---
name: kotlin-exposed-patterns
description: JetBrains Exposed ORM 的使用模式，包含 DSL 查詢、DAO 模式、transaction、HikariCP 連線池、Flyway migration 與 repository 模式。在使用 Exposed ORM 時（DSL 或 DAO 查詢、transaction、連線池、migration）使用。
metadata:
  origin: ECC
---

# Kotlin Exposed Patterns

用 JetBrains Exposed ORM 存取資料庫的完整模式，包含 DSL 查詢、DAO、transaction，以及可直接上 production 的設定。

## 何時使用

- 用 Exposed 建立資料庫存取層
- 用 Exposed DSL 或 DAO 寫 SQL 查詢
- 用 HikariCP 設定連線池
- 用 Flyway 建立資料庫 migration
- 用 Exposed 實作 repository 模式
- 處理 JSON 欄位與複雜查詢

## 運作方式

Exposed 提供兩種查詢風格：DSL 直接寫類似 SQL 的運算式，DAO 則管理 entity 的生命週期。HikariCP 管理一個可重複使用的資料庫連線池，透過 `HikariConfig` 設定。Flyway 在啟動時執行有版本號的 SQL migration 腳本，讓 schema 保持同步。所有資料庫操作都包在 `newSuspendedTransaction` 區塊裡，確保 coroutine 安全與原子性。repository 模式把 Exposed 查詢藏在介面後面，讓商業邏輯跟資料層解耦，測試時也能改用記憶體內的 H2 資料庫。

## 範例

### DSL 查詢

```kotlin
suspend fun findUserById(id: UUID): UserRow? =
    newSuspendedTransaction {
        UsersTable.selectAll()
            .where { UsersTable.id eq id }
            .map { it.toUser() }
            .singleOrNull()
    }
```

### DAO Entity 用法

```kotlin
suspend fun createUser(request: CreateUserRequest): User =
    newSuspendedTransaction {
        UserEntity.new {
            name = request.name
            email = request.email
            role = request.role
        }.toModel()
    }
```

### HikariCP 設定

```kotlin
val hikariConfig = HikariConfig().apply {
    driverClassName = config.driver
    jdbcUrl = config.url
    username = config.username
    password = config.password
    maximumPoolSize = config.maxPoolSize
    isAutoCommit = false
    transactionIsolation = "TRANSACTION_READ_COMMITTED"
    validate()
}
```

## 資料庫設定

### HikariCP 連線池

```kotlin
// DatabaseFactory.kt
object DatabaseFactory {
    fun create(config: DatabaseConfig): Database {
        val hikariConfig = HikariConfig().apply {
            driverClassName = config.driver
            jdbcUrl = config.url
            username = config.username
            password = config.password
            maximumPoolSize = config.maxPoolSize
            isAutoCommit = false
            transactionIsolation = "TRANSACTION_READ_COMMITTED"
            validate()
        }

        return Database.connect(HikariDataSource(hikariConfig))
    }
}

data class DatabaseConfig(
    val url: String,
    val driver: String = "org.postgresql.Driver",
    val username: String = "",
    val password: String = "",
    val maxPoolSize: Int = 10,
)
```

### Flyway Migration

```kotlin
// FlywayMigration.kt
fun runMigrations(config: DatabaseConfig) {
    Flyway.configure()
        .dataSource(config.url, config.username, config.password)
        .locations("classpath:db/migration")
        .baselineOnMigrate(true)
        .load()
        .migrate()
}

// Application startup
fun Application.module() {
    val config = DatabaseConfig(
        url = environment.config.property("database.url").getString(),
        username = environment.config.property("database.username").getString(),
        password = environment.config.property("database.password").getString(),
    )
    runMigrations(config)
    val database = DatabaseFactory.create(config)
    // ...
}
```

### Migration 檔案

```sql
-- src/main/resources/db/migration/V1__create_users.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'USER',
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

## 資料表定義

### DSL 風格的資料表

```kotlin
// tables/UsersTable.kt
object UsersTable : UUIDTable("users") {
    val name = varchar("name", 100)
    val email = varchar("email", 255).uniqueIndex()
    val role = enumerationByName<Role>("role", 20)
    val metadata = jsonb<UserMetadata>("metadata", Json.Default).nullable()
    val createdAt = timestampWithTimeZone("created_at").defaultExpression(CurrentTimestampWithTimeZone)
    val updatedAt = timestampWithTimeZone("updated_at").defaultExpression(CurrentTimestampWithTimeZone)
}

object OrdersTable : UUIDTable("orders") {
    val userId = uuid("user_id").references(UsersTable.id)
    val status = enumerationByName<OrderStatus>("status", 20)
    val totalAmount = long("total_amount")
    val currency = varchar("currency", 3)
    val createdAt = timestampWithTimeZone("created_at").defaultExpression(CurrentTimestampWithTimeZone)
}

object OrderItemsTable : UUIDTable("order_items") {
    val orderId = uuid("order_id").references(OrdersTable.id, onDelete = ReferenceOption.CASCADE)
    val productId = uuid("product_id")
    val quantity = integer("quantity")
    val unitPrice = long("unit_price")
}
```

### 複合資料表

```kotlin
object UserRolesTable : Table("user_roles") {
    val userId = uuid("user_id").references(UsersTable.id, onDelete = ReferenceOption.CASCADE)
    val roleId = uuid("role_id").references(RolesTable.id, onDelete = ReferenceOption.CASCADE)
    override val primaryKey = PrimaryKey(userId, roleId)
}
```

## DSL 查詢

### 基本 CRUD

```kotlin
// Insert
suspend fun insertUser(name: String, email: String, role: Role): UUID =
    newSuspendedTransaction {
        UsersTable.insertAndGetId {
            it[UsersTable.name] = name
            it[UsersTable.email] = email
            it[UsersTable.role] = role
        }.value
    }

// Select by ID
suspend fun findUserById(id: UUID): UserRow? =
    newSuspendedTransaction {
        UsersTable.selectAll()
            .where { UsersTable.id eq id }
            .map { it.toUser() }
            .singleOrNull()
    }

// Select with conditions
suspend fun findActiveAdmins(): List<UserRow> =
    newSuspendedTransaction {
        UsersTable.selectAll()
            .where { (UsersTable.role eq Role.ADMIN) }
            .orderBy(UsersTable.name)
            .map { it.toUser() }
    }

// Update
suspend fun updateUserEmail(id: UUID, newEmail: String): Boolean =
    newSuspendedTransaction {
        UsersTable.update({ UsersTable.id eq id }) {
            it[email] = newEmail
            it[updatedAt] = CurrentTimestampWithTimeZone
        } > 0
    }

// Delete
suspend fun deleteUser(id: UUID): Boolean =
    newSuspendedTransaction {
        UsersTable.deleteWhere { UsersTable.id eq id } > 0
    }

// Row mapping
private fun ResultRow.toUser() = UserRow(
    id = this[UsersTable.id].value,
    name = this[UsersTable.name],
    email = this[UsersTable.email],
    role = this[UsersTable.role],
    metadata = this[UsersTable.metadata],
    createdAt = this[UsersTable.createdAt],
    updatedAt = this[UsersTable.updatedAt],
)
```

### 進階查詢

```kotlin
// Join queries
suspend fun findOrdersWithUser(userId: UUID): List<OrderWithUser> =
    newSuspendedTransaction {
        (OrdersTable innerJoin UsersTable)
            .selectAll()
            .where { OrdersTable.userId eq userId }
            .orderBy(OrdersTable.createdAt, SortOrder.DESC)
            .map { row ->
                OrderWithUser(
                    orderId = row[OrdersTable.id].value,
                    status = row[OrdersTable.status],
                    totalAmount = row[OrdersTable.totalAmount],
                    userName = row[UsersTable.name],
                )
            }
    }

// Aggregation
suspend fun countUsersByRole(): Map<Role, Long> =
    newSuspendedTransaction {
        UsersTable
            .select(UsersTable.role, UsersTable.id.count())
            .groupBy(UsersTable.role)
            .associate { row ->
                row[UsersTable.role] to row[UsersTable.id.count()]
            }
    }

// Subqueries
suspend fun findUsersWithOrders(): List<UserRow> =
    newSuspendedTransaction {
        UsersTable.selectAll()
            .where {
                UsersTable.id inSubQuery
                    OrdersTable.select(OrdersTable.userId).withDistinct()
            }
            .map { it.toUser() }
    }

// LIKE and pattern matching — always escape user input to prevent wildcard injection
private fun escapeLikePattern(input: String): String =
    input.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

suspend fun searchUsers(query: String): List<UserRow> =
    newSuspendedTransaction {
        val sanitized = escapeLikePattern(query.lowercase())
        UsersTable.selectAll()
            .where {
                (UsersTable.name.lowerCase() like "%${sanitized}%") or
                    (UsersTable.email.lowerCase() like "%${sanitized}%")
            }
            .map { it.toUser() }
    }
```

### 分頁

```kotlin
data class Page<T>(
    val data: List<T>,
    val total: Long,
    val page: Int,
    val limit: Int,
) {
    val totalPages: Int get() = ((total + limit - 1) / limit).toInt()
    val hasNext: Boolean get() = page < totalPages
    val hasPrevious: Boolean get() = page > 1
}

suspend fun findUsersPaginated(page: Int, limit: Int): Page<UserRow> =
    newSuspendedTransaction {
        val total = UsersTable.selectAll().count()
        val data = UsersTable.selectAll()
            .orderBy(UsersTable.createdAt, SortOrder.DESC)
            .limit(limit)
            .offset(((page - 1) * limit).toLong())
            .map { it.toUser() }

        Page(data = data, total = total, page = page, limit = limit)
    }
```

### 批次操作

```kotlin
// Batch insert
suspend fun insertUsers(users: List<CreateUserRequest>): List<UUID> =
    newSuspendedTransaction {
        UsersTable.batchInsert(users) { user ->
            this[UsersTable.name] = user.name
            this[UsersTable.email] = user.email
            this[UsersTable.role] = user.role
        }.map { it[UsersTable.id].value }
    }

// Upsert (insert or update on conflict)
suspend fun upsertUser(id: UUID, name: String, email: String) {
    newSuspendedTransaction {
        UsersTable.upsert(UsersTable.email) {
            it[UsersTable.id] = EntityID(id, UsersTable)
            it[UsersTable.name] = name
            it[UsersTable.email] = email
            it[updatedAt] = CurrentTimestampWithTimeZone
        }
    }
}
```

## DAO 模式

### Entity 定義

```kotlin
// entities/UserEntity.kt
class UserEntity(id: EntityID<UUID>) : UUIDEntity(id) {
    companion object : UUIDEntityClass<UserEntity>(UsersTable)

    var name by UsersTable.name
    var email by UsersTable.email
    var role by UsersTable.role
    var metadata by UsersTable.metadata
    var createdAt by UsersTable.createdAt
    var updatedAt by UsersTable.updatedAt

    val orders by OrderEntity referrersOn OrdersTable.userId

    fun toModel(): User = User(
        id = id.value,
        name = name,
        email = email,
        role = role,
        metadata = metadata,
        createdAt = createdAt,
        updatedAt = updatedAt,
    )
}

class OrderEntity(id: EntityID<UUID>) : UUIDEntity(id) {
    companion object : UUIDEntityClass<OrderEntity>(OrdersTable)

    var user by UserEntity referencedOn OrdersTable.userId
    var status by OrdersTable.status
    var totalAmount by OrdersTable.totalAmount
    var currency by OrdersTable.currency
    var createdAt by OrdersTable.createdAt

    val items by OrderItemEntity referrersOn OrderItemsTable.orderId
}
```

### DAO 操作

```kotlin
suspend fun findUserByEmail(email: String): User? =
    newSuspendedTransaction {
        UserEntity.find { UsersTable.email eq email }
            .firstOrNull()
            ?.toModel()
    }

suspend fun createUser(request: CreateUserRequest): User =
    newSuspendedTransaction {
        UserEntity.new {
            name = request.name
            email = request.email
            role = request.role
        }.toModel()
    }

suspend fun updateUser(id: UUID, request: UpdateUserRequest): User? =
    newSuspendedTransaction {
        UserEntity.findById(id)?.apply {
            request.name?.let { name = it }
            request.email?.let { email = it }
            updatedAt = OffsetDateTime.now(ZoneOffset.UTC)
        }?.toModel()
    }
```

## Transaction

### 支援 Suspend 的 Transaction

```kotlin
// Good: Use newSuspendedTransaction for coroutine support
suspend fun performDatabaseOperation(): Result<User> =
    runCatching {
        newSuspendedTransaction {
            val user = UserEntity.new {
                name = "Alice"
                email = "alice@example.com"
            }
            // All operations in this block are atomic
            user.toModel()
        }
    }

// Good: Nested transactions with savepoints
suspend fun transferFunds(fromId: UUID, toId: UUID, amount: Long) {
    newSuspendedTransaction {
        val from = UserEntity.findById(fromId) ?: throw NotFoundException("User $fromId not found")
        val to = UserEntity.findById(toId) ?: throw NotFoundException("User $toId not found")

        // Debit
        from.balance -= amount
        // Credit
        to.balance += amount

        // Both succeed or both fail
    }
}
```

### Transaction 隔離等級

```kotlin
suspend fun readCommittedQuery(): List<User> =
    newSuspendedTransaction(transactionIsolation = Connection.TRANSACTION_READ_COMMITTED) {
        UserEntity.all().map { it.toModel() }
    }

suspend fun serializableOperation() {
    newSuspendedTransaction(transactionIsolation = Connection.TRANSACTION_SERIALIZABLE) {
        // Strictest isolation level for critical operations
    }
}
```

## Repository 模式

### 介面定義

```kotlin
interface UserRepository {
    suspend fun findById(id: UUID): User?
    suspend fun findByEmail(email: String): User?
    suspend fun findAll(page: Int, limit: Int): Page<User>
    suspend fun search(query: String): List<User>
    suspend fun create(request: CreateUserRequest): User
    suspend fun update(id: UUID, request: UpdateUserRequest): User?
    suspend fun delete(id: UUID): Boolean
    suspend fun count(): Long
}
```

### Exposed 實作

```kotlin
class ExposedUserRepository(
    private val database: Database,
) : UserRepository {

    override suspend fun findById(id: UUID): User? =
        newSuspendedTransaction(db = database) {
            UsersTable.selectAll()
                .where { UsersTable.id eq id }
                .map { it.toUser() }
                .singleOrNull()
        }

    override suspend fun findByEmail(email: String): User? =
        newSuspendedTransaction(db = database) {
            UsersTable.selectAll()
                .where { UsersTable.email eq email }
                .map { it.toUser() }
                .singleOrNull()
        }

    override suspend fun findAll(page: Int, limit: Int): Page<User> =
        newSuspendedTransaction(db = database) {
            val total = UsersTable.selectAll().count()
            val data = UsersTable.selectAll()
                .orderBy(UsersTable.createdAt, SortOrder.DESC)
                .limit(limit)
                .offset(((page - 1) * limit).toLong())
                .map { it.toUser() }
            Page(data = data, total = total, page = page, limit = limit)
        }

    override suspend fun search(query: String): List<User> =
        newSuspendedTransaction(db = database) {
            val sanitized = escapeLikePattern(query.lowercase())
            UsersTable.selectAll()
                .where {
                    (UsersTable.name.lowerCase() like "%${sanitized}%") or
                        (UsersTable.email.lowerCase() like "%${sanitized}%")
                }
                .orderBy(UsersTable.name)
                .map { it.toUser() }
        }

    override suspend fun create(request: CreateUserRequest): User =
        newSuspendedTransaction(db = database) {
            UsersTable.insert {
                it[name] = request.name
                it[email] = request.email
                it[role] = request.role
            }.resultedValues!!.first().toUser()
        }

    override suspend fun update(id: UUID, request: UpdateUserRequest): User? =
        newSuspendedTransaction(db = database) {
            val updated = UsersTable.update({ UsersTable.id eq id }) {
                request.name?.let { name -> it[UsersTable.name] = name }
                request.email?.let { email -> it[UsersTable.email] = email }
                it[updatedAt] = CurrentTimestampWithTimeZone
            }
            if (updated > 0) findById(id) else null
        }

    override suspend fun delete(id: UUID): Boolean =
        newSuspendedTransaction(db = database) {
            UsersTable.deleteWhere { UsersTable.id eq id } > 0
        }

    override suspend fun count(): Long =
        newSuspendedTransaction(db = database) {
            UsersTable.selectAll().count()
        }

    private fun ResultRow.toUser() = User(
        id = this[UsersTable.id].value,
        name = this[UsersTable.name],
        email = this[UsersTable.email],
        role = this[UsersTable.role],
        metadata = this[UsersTable.metadata],
        createdAt = this[UsersTable.createdAt],
        updatedAt = this[UsersTable.updatedAt],
    )
}
```

## JSON 欄位

### 搭配 kotlinx.serialization 的 JSONB

```kotlin
// Custom column type for JSONB
inline fun <reified T : Any> Table.jsonb(
    name: String,
    json: Json,
): Column<T> = registerColumn(name, object : ColumnType<T>() {
    override fun sqlType() = "JSONB"

    override fun valueFromDB(value: Any): T = when (value) {
        is String -> json.decodeFromString(value)
        is PGobject -> {
            val jsonString = value.value
                ?: throw IllegalArgumentException("PGobject value is null for column '$name'")
            json.decodeFromString(jsonString)
        }
        else -> throw IllegalArgumentException("Unexpected value: $value")
    }

    override fun notNullValueToDB(value: T): Any =
        PGobject().apply {
            type = "jsonb"
            this.value = json.encodeToString(value)
        }
})

// Usage in table
@Serializable
data class UserMetadata(
    val preferences: Map<String, String> = emptyMap(),
    val tags: List<String> = emptyList(),
)

object UsersTable : UUIDTable("users") {
    val metadata = jsonb<UserMetadata>("metadata", Json.Default).nullable()
}
```

## 用 Exposed 做測試

### 測試用的記憶體資料庫

```kotlin
class UserRepositoryTest : FunSpec({
    lateinit var database: Database
    lateinit var repository: UserRepository

    beforeSpec {
        database = Database.connect(
            url = "jdbc:h2:mem:test;DB_CLOSE_DELAY=-1;MODE=PostgreSQL",
            driver = "org.h2.Driver",
        )
        transaction(database) {
            SchemaUtils.create(UsersTable)
        }
        repository = ExposedUserRepository(database)
    }

    beforeTest {
        transaction(database) {
            UsersTable.deleteAll()
        }
    }

    test("create and find user") {
        val user = repository.create(CreateUserRequest("Alice", "alice@example.com"))

        user.name shouldBe "Alice"
        user.email shouldBe "alice@example.com"

        val found = repository.findById(user.id)
        found shouldBe user
    }

    test("findByEmail returns null for unknown email") {
        val result = repository.findByEmail("unknown@example.com")
        result.shouldBeNull()
    }

    test("pagination works correctly") {
        repeat(25) { i ->
            repository.create(CreateUserRequest("User $i", "user$i@example.com"))
        }

        val page1 = repository.findAll(page = 1, limit = 10)
        page1.data shouldHaveSize 10
        page1.total shouldBe 25
        page1.hasNext shouldBe true

        val page3 = repository.findAll(page = 3, limit = 10)
        page3.data shouldHaveSize 5
        page3.hasNext shouldBe false
    }
})
```

## Gradle 依賴

```kotlin
// build.gradle.kts
dependencies {
    // Exposed
    implementation("org.jetbrains.exposed:exposed-core:1.0.0")
    implementation("org.jetbrains.exposed:exposed-dao:1.0.0")
    implementation("org.jetbrains.exposed:exposed-jdbc:1.0.0")
    implementation("org.jetbrains.exposed:exposed-kotlin-datetime:1.0.0")
    implementation("org.jetbrains.exposed:exposed-json:1.0.0")

    // Database driver
    implementation("org.postgresql:postgresql:42.7.5")

    // Connection pooling
    implementation("com.zaxxer:HikariCP:6.2.1")

    // Migrations
    implementation("org.flywaydb:flyway-core:10.22.0")
    implementation("org.flywaydb:flyway-database-postgresql:10.22.0")

    // Testing
    testImplementation("com.h2database:h2:2.3.232")
}
```

## 速查：Exposed 模式

| 模式 | 說明 |
|---------|-------------|
| `object Table : UUIDTable("name")` | 定義以 UUID 為主鍵的資料表 |
| `newSuspendedTransaction { }` | coroutine 安全的 transaction 區塊 |
| `Table.selectAll().where { }` | 帶條件的查詢 |
| `Table.insertAndGetId { }` | 新增並回傳產生的 ID |
| `Table.update({ condition }) { }` | 更新符合條件的資料列 |
| `Table.deleteWhere { }` | 刪除符合條件的資料列 |
| `Table.batchInsert(items) { }` | 高效率的批次新增 |
| `innerJoin` / `leftJoin` | 資料表 join |
| `orderBy` / `limit` / `offset` | 排序與分頁 |
| `count()` / `sum()` / `avg()` | 聚合函式 |

**記住**：簡單查詢用 DSL 風格，需要 entity 生命週期管理時用 DAO 風格。一律使用 `newSuspendedTransaction` 以支援 coroutine，並把資料庫操作包在 repository 介面後面，方便測試。
