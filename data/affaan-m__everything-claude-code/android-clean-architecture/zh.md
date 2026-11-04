---
name: android-clean-architecture
description: 給 Android 和 Kotlin Multiplatform 專案用的 Clean Architecture 模式：模組結構、相依規則、UseCase、Repository 和資料層模式。在 Android 或 KMP 專案裡規劃模組、分層或資料流時使用。
metadata:
  origin: ECC
---

# Android Clean Architecture

給 Android 和 KMP 專案用的 Clean Architecture 模式。涵蓋模組邊界、依賴反轉、UseCase/Repository 模式，以及搭配 Room、SQLDelight 和 Ktor 的資料層設計。

## 何時啟用

- 規劃 Android 或 KMP 專案的模組
- 實作 UseCase、Repository 或 DataSource
- 設計各層之間的資料流（domain、data、presentation）
- 用 Koin 或 Hilt 設定依賴注入
- 在分層架構裡使用 Room、SQLDelight 或 Ktor

## 模組結構

### 建議的配置

```
project/
├── app/                  # Android 進入點、DI 接線、Application class
├── core/                 # 共用工具、base class、錯誤型別
├── domain/               # UseCase、領域模型、repository 介面（純 Kotlin）
├── data/                 # Repository 實作、DataSource、DB、網路
├── presentation/         # 畫面、ViewModel、UI 模型、導覽
├── design-system/        # 可重複使用的 Compose 元件、主題、字型
└── feature/              # Feature 模組（選用，給較大的專案）
    ├── auth/
    ├── settings/
    └── profile/
```

### 相依規則

```
app → presentation, domain, data, core
presentation → domain, design-system, core
data → domain, core
domain → core (or no dependencies)
core → (nothing)
```

**關鍵**：`domain` 絕對不能依賴 `data`、`presentation` 或任何框架。它只含純 Kotlin。

## Domain 層

### UseCase 模式

每個 UseCase 代表一個商業操作。用 `operator fun invoke` 讓呼叫端更乾淨：

```kotlin
class GetItemsByCategoryUseCase(
    private val repository: ItemRepository
) {
    suspend operator fun invoke(category: String): Result<List<Item>> {
        return repository.getItemsByCategory(category)
    }
}

// 給反應式串流用的、以 Flow 為基礎的 UseCase
class ObserveUserProgressUseCase(
    private val repository: UserRepository
) {
    operator fun invoke(userId: String): Flow<UserProgress> {
        return repository.observeProgress(userId)
    }
}
```

### 領域模型

領域模型是單純的 Kotlin data class，沒有框架的 annotation：

```kotlin
data class Item(
    val id: String,
    val title: String,
    val description: String,
    val tags: List<String>,
    val status: Status,
    val category: String
)

enum class Status { DRAFT, ACTIVE, ARCHIVED }
```

### Repository 介面

在 domain 定義，在 data 實作：

```kotlin
interface ItemRepository {
    suspend fun getItemsByCategory(category: String): Result<List<Item>>
    suspend fun saveItem(item: Item): Result<Unit>
    fun observeItems(): Flow<List<Item>>
}
```

## Data 層

### Repository 實作

協調本地和遠端資料來源：

```kotlin
class ItemRepositoryImpl(
    private val localDataSource: ItemLocalDataSource,
    private val remoteDataSource: ItemRemoteDataSource
) : ItemRepository {

    override suspend fun getItemsByCategory(category: String): Result<List<Item>> {
        return runCatching {
            val remote = remoteDataSource.fetchItems(category)
            localDataSource.insertItems(remote.map { it.toEntity() })
            localDataSource.getItemsByCategory(category).map { it.toDomain() }
        }
    }

    override suspend fun saveItem(item: Item): Result<Unit> {
        return runCatching {
            localDataSource.insertItems(listOf(item.toEntity()))
        }
    }

    override fun observeItems(): Flow<List<Item>> {
        return localDataSource.observeAll().map { entities ->
            entities.map { it.toDomain() }
        }
    }
}
```

### Mapper 模式

把 mapper 寫成 extension function，放在資料模型附近：

```kotlin
// 在 data 層
fun ItemEntity.toDomain() = Item(
    id = id,
    title = title,
    description = description,
    tags = tags.split("|"),
    status = Status.valueOf(status),
    category = category
)

fun ItemDto.toEntity() = ItemEntity(
    id = id,
    title = title,
    description = description,
    tags = tags.joinToString("|"),
    status = status,
    category = category
)
```

### Room Database（Android）

```kotlin
@Entity(tableName = "items")
data class ItemEntity(
    @PrimaryKey val id: String,
    val title: String,
    val description: String,
    val tags: String,
    val status: String,
    val category: String
)

@Dao
interface ItemDao {
    @Query("SELECT * FROM items WHERE category = :category")
    suspend fun getByCategory(category: String): List<ItemEntity>

    @Upsert
    suspend fun upsert(items: List<ItemEntity>)

    @Query("SELECT * FROM items")
    fun observeAll(): Flow<List<ItemEntity>>
}
```

### SQLDelight（KMP）

```sql
-- Item.sq
CREATE TABLE ItemEntity (
    id TEXT NOT NULL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    tags TEXT NOT NULL,
    status TEXT NOT NULL,
    category TEXT NOT NULL
);

getByCategory:
SELECT * FROM ItemEntity WHERE category = ?;

upsert:
INSERT OR REPLACE INTO ItemEntity (id, title, description, tags, status, category)
VALUES (?, ?, ?, ?, ?, ?);

observeAll:
SELECT * FROM ItemEntity;
```

### Ktor Network Client（KMP）

```kotlin
class ItemRemoteDataSource(private val client: HttpClient) {

    suspend fun fetchItems(category: String): List<ItemDto> {
        return client.get("api/items") {
            parameter("category", category)
        }.body()
    }
}

// 設定帶有 content negotiation 的 HttpClient
val httpClient = HttpClient {
    install(ContentNegotiation) { json(Json { ignoreUnknownKeys = true }) }
    install(Logging) { level = LogLevel.HEADERS }
    defaultRequest { url("https://api.example.com/") }
}
```

## 依賴注入

### Koin（對 KMP 友善）

```kotlin
// Domain module
val domainModule = module {
    factory { GetItemsByCategoryUseCase(get()) }
    factory { ObserveUserProgressUseCase(get()) }
}

// Data module
val dataModule = module {
    single<ItemRepository> { ItemRepositoryImpl(get(), get()) }
    single { ItemLocalDataSource(get()) }
    single { ItemRemoteDataSource(get()) }
}

// Presentation module
val presentationModule = module {
    viewModelOf(::ItemListViewModel)
    viewModelOf(::DashboardViewModel)
}
```

### Hilt（只限 Android）

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindItemRepository(impl: ItemRepositoryImpl): ItemRepository
}

@HiltViewModel
class ItemListViewModel @Inject constructor(
    private val getItems: GetItemsByCategoryUseCase
) : ViewModel()
```

## 錯誤處理

### Result/Try 模式

用 `Result<T>` 或自訂的 sealed type 來傳遞錯誤：

```kotlin
sealed interface Try<out T> {
    data class Success<T>(val value: T) : Try<T>
    data class Failure(val error: AppError) : Try<Nothing>
}

sealed interface AppError {
    data class Network(val message: String) : AppError
    data class Database(val message: String) : AppError
    data object Unauthorized : AppError
}

// 在 ViewModel 裡：對應成 UI 狀態
viewModelScope.launch {
    when (val result = getItems(category)) {
        is Try.Success -> _state.update { it.copy(items = result.value, isLoading = false) }
        is Try.Failure -> _state.update { it.copy(error = result.error.toMessage(), isLoading = false) }
    }
}
```

## Convention Plugin（Gradle）

KMP 專案可以用 convention plugin 減少 build 檔案的重複：

```kotlin
// build-logic/src/main/kotlin/kmp-library.gradle.kts
plugins {
    id("org.jetbrains.kotlin.multiplatform")
}

kotlin {
    androidTarget()
    iosX64(); iosArm64(); iosSimulatorArm64()
    sourceSets {
        commonMain.dependencies { /* 共用相依套件 */ }
        commonTest.dependencies { implementation(kotlin("test")) }
    }
}
```

在各模組裡套用：

```kotlin
// domain/build.gradle.kts
plugins { id("kmp-library") }
```

## 要避免的反面模式

- 在 `domain` 裡 import Android 框架的 class：保持純 Kotlin
- 把資料庫 entity 或 DTO 直接暴露給 UI 層：一律對應成領域模型
- 把商業邏輯放在 ViewModel：抽到 UseCase
- 使用 `GlobalScope` 或非結構化的 coroutine：用 `viewModelScope` 或結構化並行
- 肥大的 repository 實作：拆成各有專責的 DataSource
- 模組之間循環相依：如果 A 依賴 B，B 就不能依賴 A

## 參考資料

UI 模式請見 skill：`compose-multiplatform-patterns`。
非同步模式請見 skill：`kotlin-coroutines-flows`。
