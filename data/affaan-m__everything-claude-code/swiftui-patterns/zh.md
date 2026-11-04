---
name: swiftui-patterns
description: SwiftUI 架構模式、用 @Observable 管理狀態、view 組合、導航、效能最佳化，以及現代 iOS/macOS UI 的最佳實務。建構或 review SwiftUI view、@Observable 狀態、導航或渲染效能時使用。
---

# SwiftUI Patterns

在 Apple 平台上打造宣告式、高效能使用者介面的現代 SwiftUI 模式。涵蓋 Observation framework、view 組合、型別安全導航和效能最佳化。

## 何時啟用

- 建構 SwiftUI view 並管理狀態（`@State`、`@Observable`、`@Binding`）
- 用 `NavigationStack` 設計導航流程
- 規劃 view model 和資料流
- 為清單和複雜版面最佳化渲染效能
- 在 SwiftUI 中使用環境值和依賴注入

## 狀態管理

### Property Wrapper 的選擇

選最簡單、夠用的 wrapper：

| Wrapper | 使用情境 |
|---------|----------|
| `@State` | view 本地的值型別（開關、表單欄位、sheet 的呈現） |
| `@Binding` | 對父層 `@State` 的雙向參照 |
| `@Observable` class + `@State` | 擁有多個屬性、由該 view 持有的 model |
| `@Observable` class（不加 wrapper） | 從父層傳進來的唯讀參照 |
| `@Bindable` | 對 `@Observable` 屬性的雙向綁定 |
| `@Environment` | 透過 `.environment()` 注入的共享相依項 |

### @Observable ViewModel

用 `@Observable`（不要用 `ObservableObject`），它追蹤屬性層級的變更，所以 SwiftUI 只會重新渲染讀取了變更屬性的 view：

```swift
@Observable
final class ItemListViewModel {
    private(set) var items: [Item] = []
    private(set) var isLoading = false
    var searchText = ""

    private let repository: any ItemRepository

    init(repository: any ItemRepository = DefaultItemRepository()) {
        self.repository = repository
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        items = (try? await repository.fetchAll()) ?? []
    }
}
```

### 使用 ViewModel 的 View

```swift
struct ItemListView: View {
    @State private var viewModel: ItemListViewModel

    init(viewModel: ItemListViewModel = ItemListViewModel()) {
        _viewModel = State(initialValue: viewModel)
    }

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .searchable(text: $viewModel.searchText)
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.load() }
    }
}
```

### Environment 注入

用 `@Environment` 取代 `@EnvironmentObject`：

```swift
// Inject
ContentView()
    .environment(authManager)

// Consume
struct ProfileView: View {
    @Environment(AuthManager.self) private var auth

    var body: some View {
        Text(auth.currentUser?.name ?? "Guest")
    }
}
```

## View 組合

### 抽出子 view 以限制失效範圍

把 view 拆成小而聚焦的 struct。狀態改變時，只有讀取該狀態的子 view 會重新渲染：

```swift
struct OrderView: View {
    @State private var viewModel = OrderViewModel()

    var body: some View {
        VStack {
            OrderHeader(title: viewModel.title)
            OrderItemList(items: viewModel.items)
            OrderTotal(total: viewModel.total)
        }
    }
}
```

### 用 ViewModifier 重複使用樣式

```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}
```

## 導航

### 型別安全的 NavigationStack

用 `NavigationStack` 搭配 `NavigationPath`，做程式化、型別安全的路由：

```swift
@Observable
final class Router {
    var path = NavigationPath()

    func navigate(to destination: Destination) {
        path.append(destination)
    }

    func popToRoot() {
        path = NavigationPath()
    }
}

enum Destination: Hashable {
    case detail(Item.ID)
    case settings
    case profile(User.ID)
}

struct RootView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: Destination.self) { dest in
                    switch dest {
                    case .detail(let id): ItemDetailView(itemID: id)
                    case .settings: SettingsView()
                    case .profile(let id): ProfileView(userID: id)
                    }
                }
        }
        .environment(router)
    }
}
```

## 效能

### 大型集合用 Lazy 容器

`LazyVStack` 和 `LazyHStack` 只在 view 可見時才建立它們：

```swift
ScrollView {
    LazyVStack(spacing: 8) {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
}
```

### 穩定的識別碼

`ForEach` 一律使用穩定、唯一的 ID，避免使用陣列索引：

```swift
// Use Identifiable conformance or explicit id
ForEach(items, id: \.stableID) { item in
    ItemRow(item: item)
}
```

### 避免在 body 裡做昂貴的工作

- 絕對不要在 `body` 裡做 I/O、網路呼叫或繁重運算
- 非同步工作用 `.task {}`，view 消失時它會自動取消
- 在捲動 view 裡，`.sensoryFeedback()` 和 `.geometryGroup()` 要節制使用
- 清單裡盡量減少 `.shadow()`、`.blur()` 和 `.mask()`，它們會觸發離屏渲染

### Equatable Conformance

body 很昂貴的 view，讓它遵循 `Equatable`，跳過不必要的重新渲染：

```swift
struct ExpensiveChartView: View, Equatable {
    let dataPoints: [DataPoint] // DataPoint must conform to Equatable

    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.dataPoints == rhs.dataPoints
    }

    var body: some View {
        // Complex chart rendering
    }
}
```

## Preview

用 `#Preview` 巨集搭配內嵌的 mock 資料，加快迭代：

```swift
#Preview("Empty state") {
    ItemListView(viewModel: ItemListViewModel(repository: EmptyMockRepository()))
}

#Preview("Loaded") {
    ItemListView(viewModel: ItemListViewModel(repository: PopulatedMockRepository()))
}
```

## 要避免的反模式

- 在新程式碼裡用 `ObservableObject` / `@Published` / `@StateObject` / `@EnvironmentObject`：改遷移到 `@Observable`
- 直接在 `body` 或 `init` 裡做非同步工作：改用 `.task {}` 或明確的 load 方法
- 在不擁有資料的子 view 裡，用 `@State` 建立 view model：改成從父層傳入
- 使用 `AnyView` 型別抹除：條件式 view 優先用 `@ViewBuilder` 或 `Group`
- 在 actor 之間傳遞資料時，忽略 `Sendable` 的要求

## 參考

actor 為基礎的持久化模式，請見 skill：`swift-actor-persistence`。
以 protocol 為基礎的依賴注入，以及用 Swift Testing 做測試，請見 skill：`swift-protocol-di-testing`。
