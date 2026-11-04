---
name: kotlin-coroutines-flows
description: Android 與 KMP 的 Kotlin Coroutines 和 Flow 模式，涵蓋結構化並行、Flow 運算子、StateFlow、錯誤處理與測試。在 Android 或 KMP 上撰寫 coroutine 或 Flow 程式碼，或除錯取消與並行問題時使用。
metadata:
  origin: ECC
---

# Kotlin Coroutines & Flows

Android 與 Kotlin Multiplatform 專案中，結構化並行、以 Flow 為基礎的 reactive stream，以及 coroutine 測試的模式。

## When to Activate

- 用 Kotlin coroutine 撰寫非同步程式碼
- 用 Flow、StateFlow 或 SharedFlow 處理 reactive 資料
- 處理並行操作（平行載入、debounce、retry）
- 測試 coroutine 和 Flow
- 管理 coroutine scope 與取消

## Structured Concurrency

### Scope Hierarchy

```
Application
  └── viewModelScope (ViewModel)
        └── coroutineScope { } (structured child)
              ├── async { } (concurrent task)
              └── async { } (concurrent task)
```

一律使用結構化並行，絕對不要用 `GlobalScope`：

```kotlin
// BAD
GlobalScope.launch { fetchData() }

// GOOD — 範圍限定在 ViewModel 的生命週期
viewModelScope.launch { fetchData() }

// GOOD — 範圍限定在 composable 的生命週期
LaunchedEffect(key) { fetchData() }
```

### Parallel Decomposition

平行的工作用 `coroutineScope` + `async`：

```kotlin
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val items = async { itemRepository.getRecent() }
    val stats = async { statsRepository.getToday() }
    val profile = async { userRepository.getCurrent() }
    Dashboard(
        items = items.await(),
        stats = stats.await(),
        profile = profile.await()
    )
}
```

### SupervisorScope

當子任務失敗不該取消其他兄弟任務時，用 `supervisorScope`：

```kotlin
suspend fun syncAll() = supervisorScope {
    launch { syncItems() }       // 這裡失敗不會取消 syncStats
    launch { syncStats() }
    launch { syncSettings() }
}
```

## Flow Patterns

### Cold Flow — One-Shot to Stream Conversion

```kotlin
fun observeItems(): Flow<List<Item>> = flow {
    // 資料庫每次變動都會重新發送
    itemDao.observeAll()
        .map { entities -> entities.map { it.toDomain() } }
        .collect { emit(it) }
}
```

### StateFlow for UI State

```kotlin
class DashboardViewModel(
    observeProgress: ObserveUserProgressUseCase
) : ViewModel() {
    val progress: StateFlow<UserProgress> = observeProgress()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = UserProgress.EMPTY
        )
}
```

`WhileSubscribed(5_000)` 會在最後一個訂閱者離開後，讓上游再保持運作 5 秒，所以設定變更（例如螢幕旋轉）時不會重新啟動。

### Combining Multiple Flows

```kotlin
val uiState: StateFlow<HomeState> = combine(
    itemRepository.observeItems(),
    settingsRepository.observeTheme(),
    userRepository.observeProfile()
) { items, theme, profile ->
    HomeState(items = items, theme = theme, profile = profile)
}.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), HomeState())
```

### Flow Operators

```kotlin
// 搜尋輸入做 debounce
searchQuery
    .debounce(300)
    .distinctUntilChanged()
    .flatMapLatest { query -> repository.search(query) }
    .catch { emit(emptyList()) }
    .collect { results -> _state.update { it.copy(results = results) } }

// 用指數退避做 retry
fun fetchWithRetry(): Flow<Data> = flow { emit(api.fetch()) }
    .retryWhen { cause, attempt ->
        if (cause is IOException && attempt < 3) {
            delay(1000L * (1 shl attempt.toInt()))
            true
        } else {
            false
        }
    }
```

### SharedFlow for One-Time Events

```kotlin
class ItemListViewModel : ViewModel() {
    private val _effects = MutableSharedFlow<Effect>()
    val effects: SharedFlow<Effect> = _effects.asSharedFlow()

    sealed interface Effect {
        data class ShowSnackbar(val message: String) : Effect
        data class NavigateTo(val route: String) : Effect
    }

    private fun deleteItem(id: String) {
        viewModelScope.launch {
            repository.delete(id)
            _effects.emit(Effect.ShowSnackbar("Item deleted"))
        }
    }
}

// 在 Composable 裡收集
LaunchedEffect(Unit) {
    viewModel.effects.collect { effect ->
        when (effect) {
            is Effect.ShowSnackbar -> snackbarHostState.showSnackbar(effect.message)
            is Effect.NavigateTo -> navController.navigate(effect.route)
        }
    }
}
```

## Dispatchers

```kotlin
// CPU 密集的工作
withContext(Dispatchers.Default) { parseJson(largePayload) }

// IO 密集的工作
withContext(Dispatchers.IO) { database.query() }

// 主執行緒（UI）— viewModelScope 的預設值
withContext(Dispatchers.Main) { updateUi() }
```

在 KMP 裡，使用 `Dispatchers.Default` 和 `Dispatchers.Main`（所有平台都有）。`Dispatchers.IO` 只有 JVM/Android 才有，其他平台用 `Dispatchers.Default`，或透過 DI 提供。

## Cancellation

### Cooperative Cancellation

長時間執行的迴圈必須檢查是否已取消：

```kotlin
suspend fun processItems(items: List<Item>) = coroutineScope {
    for (item in items) {
        ensureActive()  // 如果已取消，會丟出 CancellationException
        process(item)
    }
}
```

### Cleanup with try/finally

```kotlin
viewModelScope.launch {
    try {
        _state.update { it.copy(isLoading = true) }
        val data = repository.fetch()
        _state.update { it.copy(data = data) }
    } finally {
        _state.update { it.copy(isLoading = false) }  // 一定會執行，即使被取消也一樣
    }
}
```

## Testing

### Testing StateFlow with Turbine

```kotlin
@Test
fun `search updates item list`() = runTest {
    val fakeRepository = FakeItemRepository().apply { emit(testItems) }
    val viewModel = ItemListViewModel(GetItemsUseCase(fakeRepository))

    viewModel.state.test {
        assertEquals(ItemListState(), awaitItem())  // 初始值

        viewModel.onSearch("query")
        val loading = awaitItem()
        assertTrue(loading.isLoading)

        val loaded = awaitItem()
        assertFalse(loaded.isLoading)
        assertEquals(1, loaded.items.size)
    }
}
```

### Testing with TestDispatcher

```kotlin
@Test
fun `parallel load completes correctly`() = runTest {
    val viewModel = DashboardViewModel(
        itemRepo = FakeItemRepo(),
        statsRepo = FakeStatsRepo()
    )

    viewModel.load()
    advanceUntilIdle()

    val state = viewModel.state.value
    assertNotNull(state.items)
    assertNotNull(state.stats)
}
```

### Faking Flows

```kotlin
class FakeItemRepository : ItemRepository {
    private val _items = MutableStateFlow<List<Item>>(emptyList())

    override fun observeItems(): Flow<List<Item>> = _items

    fun emit(items: List<Item>) { _items.value = items }

    override suspend fun getItemsByCategory(category: String): Result<List<Item>> {
        return Result.success(_items.value.filter { it.category == category })
    }
}
```

## Anti-Patterns to Avoid

- 使用 `GlobalScope`：會洩漏 coroutine，沒有結構化的取消
- 在 `init {}` 裡沒有 scope 就收集 Flow，要用 `viewModelScope.launch`
- 對可變集合使用 `MutableStateFlow`，一律使用不可變的複本：`_state.update { it.copy(list = it.list + newItem) }`
- 攔截 `CancellationException`，要讓它往上傳遞，才能正確取消
- 用 `flowOn(Dispatchers.Main)` 來收集，收集時的 dispatcher 是呼叫端的 dispatcher
- 在 `@Composable` 裡不加 `remember` 就建立 `Flow`，每次 recomposition 都會重新建立 flow

## References

UI 如何消費 Flow，請見 skill：`compose-multiplatform-patterns`。
Coroutine 在各層裡該放哪裡，請見 skill：`android-clean-architecture`。
