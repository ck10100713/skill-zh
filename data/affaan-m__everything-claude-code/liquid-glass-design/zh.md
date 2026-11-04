---
name: liquid-glass-design
description: iOS 26 Liquid Glass 設計系統，為 SwiftUI、UIKit 與 WidgetKit 提供帶有模糊、反射與互動式 morphing 的動態玻璃材質。在用 SwiftUI、UIKit 或 WidgetKit 打造 iOS 26 Liquid Glass UI 時使用。
---

# Liquid Glass 設計系統（iOS 26）

實作 Apple Liquid Glass 的模式。這是一種動態材質，會模糊它後面的內容，反射周圍內容的顏色與光線，並對觸控與指標互動做出反應。涵蓋 SwiftUI、UIKit 與 WidgetKit 的整合。

## 何時啟用

- 為 iOS 26+ 建構或更新採用新設計語言的 app
- 實作玻璃風格的按鈕、卡片、工具列或容器
- 在玻璃元素之間建立 morphing 轉場
- 把 Liquid Glass 效果套用在 widget 上
- 把既有的模糊/材質效果遷移到新的 Liquid Glass API

## 核心模式：SwiftUI

### 基本玻璃效果

替任何 view 加上 Liquid Glass 最簡單的方法：

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect()  // Default: regular variant, capsule shape
```

### 自訂形狀與色調

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.tint(.orange).interactive(), in: .rect(cornerRadius: 16.0))
```

主要的自訂選項：
- `.regular`：標準玻璃效果
- `.tint(Color)`：加上色調以突顯
- `.interactive()`：對觸控與指標互動做出反應
- 形狀：`.capsule`（預設）、`.rect(cornerRadius:)`、`.circle`

### 玻璃按鈕樣式

```swift
Button("Click Me") { /* action */ }
    .buttonStyle(.glass)

Button("Important") { /* action */ }
    .buttonStyle(.glassProminent)
```

### 多個元素用 GlassEffectContainer

多個玻璃 view 一定要包在容器裡，才有效能與 morphing：

```swift
GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()

        Image(systemName: "eraser.fill")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
    }
}
```

`spacing` 參數控制合併距離，元素靠得越近，玻璃形狀就越會融在一起。

### 合併玻璃效果

用 `glassEffectUnion` 把多個 view 合併成單一玻璃形狀：

```swift
@Namespace private var namespace

GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        ForEach(symbolSet.indices, id: \.self) { item in
            Image(systemName: symbolSet[item])
                .frame(width: 80.0, height: 80.0)
                .glassEffect()
                .glassEffectUnion(id: item < 2 ? "group1" : "group2", namespace: namespace)
        }
    }
}
```

### Morphing 轉場

當玻璃元素出現/消失時，建立平順的 morphing：

```swift
@State private var isExpanded = false
@Namespace private var namespace

GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .glassEffect()
            .glassEffectID("pencil", in: namespace)

        if isExpanded {
            Image(systemName: "eraser.fill")
                .frame(width: 80.0, height: 80.0)
                .glassEffect()
                .glassEffectID("eraser", in: namespace)
        }
    }
}

Button("Toggle") {
    withAnimation { isExpanded.toggle() }
}
.buttonStyle(.glass)
```

### 讓水平捲動延伸到 Sidebar 底下

要讓水平捲動的內容延伸到 sidebar 或 inspector 底下，要確保 `ScrollView` 的內容延伸到容器的前後邊緣。當版面延伸到邊緣時，系統會自動處理在 sidebar 底下捲動的行為，不需要額外的 modifier。

## 核心模式：UIKit

### 基本 UIGlassEffect

```swift
let glassEffect = UIGlassEffect()
glassEffect.tintColor = UIColor.systemBlue.withAlphaComponent(0.3)
glassEffect.isInteractive = true

let visualEffectView = UIVisualEffectView(effect: glassEffect)
visualEffectView.translatesAutoresizingMaskIntoConstraints = false
visualEffectView.layer.cornerRadius = 20
visualEffectView.clipsToBounds = true

view.addSubview(visualEffectView)
NSLayoutConstraint.activate([
    visualEffectView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    visualEffectView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
    visualEffectView.widthAnchor.constraint(equalToConstant: 200),
    visualEffectView.heightAnchor.constraint(equalToConstant: 120)
])

// Add content to contentView
let label = UILabel()
label.text = "Liquid Glass"
label.translatesAutoresizingMaskIntoConstraints = false
visualEffectView.contentView.addSubview(label)
NSLayoutConstraint.activate([
    label.centerXAnchor.constraint(equalTo: visualEffectView.contentView.centerXAnchor),
    label.centerYAnchor.constraint(equalTo: visualEffectView.contentView.centerYAnchor)
])
```

### 多個元素用 UIGlassContainerEffect

```swift
let containerEffect = UIGlassContainerEffect()
containerEffect.spacing = 40.0

let containerView = UIVisualEffectView(effect: containerEffect)

let firstGlass = UIVisualEffectView(effect: UIGlassEffect())
let secondGlass = UIVisualEffectView(effect: UIGlassEffect())

containerView.contentView.addSubview(firstGlass)
containerView.contentView.addSubview(secondGlass)
```

### 捲動邊緣效果

```swift
scrollView.topEdgeEffect.style = .automatic
scrollView.bottomEdgeEffect.style = .hard
scrollView.leftEdgeEffect.isHidden = true
```

### 工具列玻璃整合

```swift
let favoriteButton = UIBarButtonItem(image: UIImage(systemName: "heart"), style: .plain, target: self, action: #selector(favoriteAction))
favoriteButton.hidesSharedBackground = true  // Opt out of shared glass background
```

## 核心模式：WidgetKit

### 偵測 Rendering Mode

```swift
struct MyWidgetView: View {
    @Environment(\.widgetRenderingMode) var renderingMode

    var body: some View {
        if renderingMode == .accented {
            // Tinted mode: white-tinted, themed glass background
        } else {
            // Full color mode: standard appearance
        }
    }
}
```

### 用 Accent Group 建立視覺層級

```swift
HStack {
    VStack(alignment: .leading) {
        Text("Title")
            .widgetAccentable()  // Accent group
        Text("Subtitle")
            // Primary group (default)
    }
    Image(systemName: "star.fill")
        .widgetAccentable()  // Accent group
}
```

### Accented 模式下的圖片 Rendering

```swift
Image("myImage")
    .widgetAccentedRenderingMode(.monochrome)
```

### 容器背景

```swift
VStack { /* content */ }
    .containerBackground(for: .widget) {
        Color.blue.opacity(0.2)
    }
```

## 關鍵設計決策

| 決策 | 理由 |
|----------|-----------|
| 用 GlassEffectContainer 包起來 | 效能優化，並讓玻璃元素之間能 morphing |
| `spacing` 參數 | 控制合併距離，微調元素要靠多近才會融合 |
| `@Namespace` + `glassEffectID` | 讓 view 階層變動時有平順的 morphing 轉場 |
| `interactive()` modifier | 明確選擇啟用觸控/指標反應，不是所有玻璃都該有反應 |
| UIKit 中的 UIGlassContainerEffect | 與 SwiftUI 相同的容器模式，保持一致 |
| Widget 的 Accented rendering mode | 使用者選擇染色主畫面時，系統會套用染色玻璃 |

## 最佳實務

- **多個同層 view 套用玻璃時，一律使用 GlassEffectContainer**：它能啟用 morphing 並改善 rendering 效能
- **把 `.glassEffect()` 放在其他外觀 modifier 之後**（frame、font、padding）
- **只在會回應使用者互動的元素上用 `.interactive()`**（按鈕、可切換的項目）
- **仔細選擇容器裡的 spacing**，以控制玻璃效果何時合併
- **變更 view 階層時用 `withAnimation`**，才有平順的 morphing 轉場
- **跨外觀測試**：淺色模式、深色模式，以及 accented/染色模式
- **確保無障礙對比**：玻璃上的文字必須維持可讀

## 要避開的反模式

- 用多個獨立的 `.glassEffect()` view，卻沒有 GlassEffectContainer
- 巢狀堆太多玻璃效果，會降低效能與視覺清晰度
- 每個 view 都套玻璃，應只保留給互動元素、工具列與卡片
- 在 UIKit 用圓角時忘了 `clipsToBounds = true`
- 忽略 widget 的 accented rendering mode，會破壞染色主畫面的外觀
- 在玻璃後面用不透明背景，會抵銷半透明效果

## 何時使用

- 採用 iOS 26 新設計的導覽列、工具列與 tab bar
- 浮動操作按鈕與卡片式容器
- 需要視覺深度與觸控回饋的互動控制項
- 要與系統 Liquid Glass 外觀整合的 widget
- 相關 UI 狀態之間的 morphing 轉場
