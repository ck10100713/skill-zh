---
name: compose-multiplatform-patterns
description: KMP 專案用的 Compose Multiplatform 與 Jetpack Compose 模式：狀態管理、導覽、主題、效能，以及平台專屬的 UI。適用於在 KMP 專案中建構 Compose 或 Jetpack Compose 的 UI、狀態、導覽或主題。
metadata:
  origin: ECC
---

# Compose Multiplatform Patterns

用 Compose Multiplatform 和 Jetpack Compose，在 Android、iOS、Desktop 和 Web 之間建構共用 UI 的模式。涵蓋狀態管理、導覽、主題和效能。

## When to Activate

- 建構 Compose UI（Jetpack Compose 或 Compose Multiplatform）
- 用 ViewModel 和 Compose state 管理 UI 狀態
- 在 KMP 或 Android 專案裡實作導覽
- 設計可重複使用的 composable 和設計系統
- 最佳化 recomposition 與渲染效能

## State Management

### ViewModel + Single State Object

每個畫面的狀態用單一個 data class。以 `StateFlow` 對外公開，並在 Compose 裡收集：

```kotlin
data class ItemListState(
    val items: List<Item> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val searchQuery: String = ""
)

class ItemListViewModel(
    private val getItems: GetItemsUseCase
) : ViewModel() {
    private val _state = MutableStateFlow(ItemListState())
    val state: StateFlow<ItemListState> = _state.asStateFlow()

    fun onSearch(query: String) {
        _state.update { it.copy(searchQuery = query) }
        loadItems(query)
    }

    private fun loadItems(query: String) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            getItems(query).fold(
                onSuccess = { items -> _state.update { it.copy(items = items, isLoading = false) } },
                onFailure = { e -> _state.update { it.copy(error = e.message, isLoading = false) } }
            )
        }
    }
}
```

### Collecting State in Compose

```kotlin
@Composable
fun ItemListScreen(viewModel: ItemListViewModel = koinViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    ItemListContent(
        state = state,
        onSearch = viewModel::onSearch
    )
}

@Composable
private fun ItemListContent(
    state: ItemListState,
    onSearch: (String) -> Unit
) {
    // 無狀態的 composable，容易預覽和測試
}
```

### Event Sink Pattern

複雜的畫面用 sealed interface 表示事件，不要用多個 callback lambda：

```kotlin
sealed interface ItemListEvent {
    data class Search(val query: String) : ItemListEvent
    data class Delete(val itemId: String) : ItemListEvent
    data object Refresh : ItemListEvent
}

// 在 ViewModel 裡
fun onEvent(event: ItemListEvent) {
    when (event) {
        is ItemListEvent.Search -> onSearch(event.query)
        is ItemListEvent.Delete -> deleteItem(event.itemId)
        is ItemListEvent.Refresh -> loadItems(_state.value.searchQuery)
    }
}

// 在 Composable 裡，用單一 lambda 取代很多個
ItemListContent(
    state = state,
    onEvent = viewModel::onEvent
)
```

## Navigation

### Type-Safe Navigation (Compose Navigation 2.8+)

把路由定義成 `@Serializable` 物件：

```kotlin
@Serializable data object HomeRoute
@Serializable data class DetailRoute(val id: String)
@Serializable data object SettingsRoute

@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController, startDestination = HomeRoute) {
        composable<HomeRoute> {
            HomeScreen(onNavigateToDetail = { id -> navController.navigate(DetailRoute(id)) })
        }
        composable<DetailRoute> { backStackEntry ->
            val route = backStackEntry.toRoute<DetailRoute>()
            DetailScreen(id = route.id)
        }
        composable<SettingsRoute> { SettingsScreen() }
    }
}
```

### Dialog and Bottom Sheet Navigation

用 `dialog()` 和 overlay 的模式，不要用命令式的 show/hide：

```kotlin
NavHost(navController, startDestination = HomeRoute) {
    composable<HomeRoute> { /* ... */ }
    dialog<ConfirmDeleteRoute> { backStackEntry ->
        val route = backStackEntry.toRoute<ConfirmDeleteRoute>()
        ConfirmDeleteDialog(
            itemId = route.itemId,
            onConfirm = { navController.popBackStack() },
            onDismiss = { navController.popBackStack() }
        )
    }
}
```

## Composable Design

### Slot-Based APIs

設計 composable 時用 slot 參數來保留彈性：

```kotlin
@Composable
fun AppCard(
    modifier: Modifier = Modifier,
    header: @Composable () -> Unit = {},
    content: @Composable ColumnScope.() -> Unit,
    actions: @Composable RowScope.() -> Unit = {}
) {
    Card(modifier = modifier) {
        Column {
            header()
            Column(content = content)
            Row(horizontalArrangement = Arrangement.End, content = actions)
        }
    }
}
```

### Modifier Ordering

Modifier 的順序很重要，照這個順序套用：

```kotlin
Text(
    text = "Hello",
    modifier = Modifier
        .padding(16.dp)          // 1. Layout (padding, size)
        .clip(RoundedCornerShape(8.dp))  // 2. Shape
        .background(Color.White) // 3. Drawing (background, border)
        .clickable { }           // 4. Interaction
)
```

## KMP Platform-Specific UI

### expect/actual for Platform Composables

```kotlin
// commonMain
@Composable
expect fun PlatformStatusBar(darkIcons: Boolean)

// androidMain
@Composable
actual fun PlatformStatusBar(darkIcons: Boolean) {
    val systemUiController = rememberSystemUiController()
    SideEffect { systemUiController.setStatusBarColor(Color.Transparent, darkIcons) }
}

// iosMain
@Composable
actual fun PlatformStatusBar(darkIcons: Boolean) {
    // iOS 透過 UIKit interop 或 Info.plist 處理這個
}
```

## Performance

### Stable Types for Skippable Recomposition

當所有屬性都是 stable 時，把類別標記成 `@Stable` 或 `@Immutable`：

```kotlin
@Immutable
data class ItemUiModel(
    val id: String,
    val title: String,
    val description: String,
    val progress: Float
)
```

### Use `key()` and Lazy Lists Correctly

```kotlin
LazyColumn {
    items(
        items = items,
        key = { it.id }  // 穩定的 key 才能讓項目重複使用，也才能有動畫
    ) { item ->
        ItemRow(item = item)
    }
}
```

### Defer Reads with `derivedStateOf`

```kotlin
val listState = rememberLazyListState()
val showScrollToTop by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 5 }
}
```

### Avoid Allocations in Recomposition

```kotlin
// BAD — 每次 recomposition 都產生新的 lambda 和 list
items.filter { it.isActive }.forEach { ActiveItem(it, onClick = { handle(it) }) }

// GOOD — 幫每個項目加 key，讓 callback 保持綁在正確的那一列
val activeItems = remember(items) { items.filter { it.isActive } }
activeItems.forEach { item ->
    key(item.id) {
        ActiveItem(item, onClick = { handle(item) })
    }
}
```

## Theming

### Material 3 Dynamic Theming

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(LocalContext.current)
            else dynamicLightColorScheme(LocalContext.current)
        }
        darkTheme -> darkColorScheme()
        else -> lightColorScheme()
    }

    MaterialTheme(colorScheme = colorScheme, content = content)
}
```

## Anti-Patterns to Avoid

- 在 ViewModel 裡用 `mutableStateOf`，其實搭配 `collectAsStateWithLifecycle` 的 `MutableStateFlow` 對生命週期更安全
- 把 `NavController` 一路傳進很深的 composable，要改傳 lambda callback
- 在 `@Composable` 函式裡做大量運算，要搬到 ViewModel 或 `remember {}`
- 用 `LaunchedEffect(Unit)` 取代 ViewModel 的 init，在某些設定下，它會在設定變更時重新執行
- 在 composable 參數裡建立新的物件實例，會造成不必要的 recomposition

## References

模組結構與分層請見 skill：`android-clean-architecture`。
coroutine 和 Flow 的模式請見 skill：`kotlin-coroutines-flows`。
