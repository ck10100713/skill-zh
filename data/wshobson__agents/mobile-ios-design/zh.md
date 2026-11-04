---
name: mobile-ios-design
description: 精通 iOS Human Interface Guidelines 與 SwiftUI 模式，用來建構原生 iOS app。在設計 iOS 介面、實作 SwiftUI view，或確保 app 遵循 Apple 的設計原則時使用。
---

# iOS Mobile Design

精通 iOS Human Interface Guidelines（HIG）與 SwiftUI 模式，建構在 Apple 平台上渾然天成、精緻的原生 iOS 應用程式。

## When to Use This Skill

- 依 Apple HIG 設計 iOS app 介面
- 建構 SwiftUI view 與版面
- 實作 iOS 導覽模式（NavigationStack、TabView、sheet）
- 為 iPhone 與 iPad 建立自適應版面
- 使用 SF Symbols 與系統字體排版
- 建構無障礙的 iOS 介面
- 實作 iOS 專屬的手勢與互動
- 為 Dynamic Type 與深色模式做設計

## Core Concepts

### 1. Human Interface Guidelines Principles

**Clarity**：內容易讀、圖示精準、裝飾低調
**Deference**：UI 幫助使用者理解內容，但不跟內容搶風頭
**Depth**：用視覺層次與動態傳達階層並支援導覽

**平台考量：**

- **iOS**：觸控優先、小螢幕、直式
- **iPadOS**：較大的畫布、多工、支援指標
- **visionOS**：空間運算、眼睛/手部輸入

### 2. SwiftUI Layout System

**Stack-Based Layouts：**

```swift
// Vertical stack with alignment
VStack(alignment: .leading, spacing: 12) {
    Text("Title")
        .font(.headline)
    Text("Subtitle")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}

// Horizontal stack with flexible spacing
HStack {
    Image(systemName: "star.fill")
    Text("Featured")
    Spacer()
    Text("View All")
        .foregroundStyle(.blue)
}
```

**Grid Layouts：**

```swift
// Adaptive grid that fills available width
LazyVGrid(columns: [
    GridItem(.adaptive(minimum: 150, maximum: 200))
], spacing: 16) {
    ForEach(items) { item in
        ItemCard(item: item)
    }
}

// Fixed column grid
LazyVGrid(columns: [
    GridItem(.flexible()),
    GridItem(.flexible()),
    GridItem(.flexible())
], spacing: 12) {
    ForEach(items) { item in
        ItemThumbnail(item: item)
    }
}
```

### 3. Navigation Patterns

**NavigationStack（iOS 16+）：**

```swift
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List(items) { item in
                NavigationLink(value: item) {
                    ItemRow(item: item)
                }
            }
            .navigationTitle("Items")
            .navigationDestination(for: Item.self) { item in
                ItemDetailView(item: item)
            }
        }
    }
}
```

**TabView（iOS 18+）：**

```swift
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            Tab("Home", systemImage: "house", value: 0) {
                HomeView()
            }

            Tab("Search", systemImage: "magnifyingglass", value: 1) {
                SearchView()
            }

            Tab("Profile", systemImage: "person", value: 2) {
                ProfileView()
            }
        }
    }
}
```

### 4. System Integration

**SF Symbols：**

```swift
// Basic symbol
Image(systemName: "heart.fill")
    .foregroundStyle(.red)

// Symbol with rendering mode
Image(systemName: "cloud.sun.fill")
    .symbolRenderingMode(.multicolor)

// Variable symbol (iOS 16+)
Image(systemName: "speaker.wave.3.fill", variableValue: volume)

// Symbol effect (iOS 17+)
Image(systemName: "bell.fill")
    .symbolEffect(.bounce, value: notificationCount)
```

**Dynamic Type：**

```swift
// Use semantic fonts
Text("Headline")
    .font(.headline)

Text("Body text that scales with user preferences")
    .font(.body)

// Custom font that respects Dynamic Type
Text("Custom")
    .font(.custom("Avenir", size: 17, relativeTo: .body))
```

### 5. Visual Design

**Colors and Materials：**

```swift
// Semantic colors that adapt to light/dark mode
Text("Primary")
    .foregroundStyle(.primary)
Text("Secondary")
    .foregroundStyle(.secondary)

// System materials for blur effects
Rectangle()
    .fill(.ultraThinMaterial)
    .frame(height: 100)

// Vibrant materials for overlays
Text("Overlay")
    .padding()
    .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
```

**Shadows and Depth：**

```swift
// Standard card shadow
RoundedRectangle(cornerRadius: 16)
    .fill(.background)
    .shadow(color: .black.opacity(0.1), radius: 8, y: 4)

// Elevated appearance
.shadow(radius: 2, y: 1)
.shadow(radius: 8, y: 4)
```

## Quick Start Component

```swift
import SwiftUI

struct FeatureCard: View {
    let title: String
    let description: String
    let systemImage: String

    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: systemImage)
                .font(.title)
                .foregroundStyle(.blue)
                .frame(width: 44, height: 44)
                .background(.blue.opacity(0.1), in: Circle())

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(description)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }

            Spacer()

            Image(systemName: "chevron.right")
                .foregroundStyle(.tertiary)
        }
        .padding()
        .background(.background, in: RoundedRectangle(cornerRadius: 12))
        .shadow(color: .black.opacity(0.05), radius: 4, y: 2)
    }
}
```

## Best Practices

1. **使用語意色彩**：一律用 `.primary`、`.secondary`、`.background`，自動支援淺色/深色模式
2. **善用 SF Symbols**：用系統符號保持一致，也自動具備無障礙支援
3. **支援 Dynamic Type**：用語意字體（`.body`、`.headline`），不要用固定大小
4. **加入無障礙支援**：加上 `.accessibilityLabel()` 和 `.accessibilityHint()` modifier
5. **使用 Safe Area**：尊重 `safeAreaInset`，避免在螢幕邊緣寫死 padding
6. **實作狀態還原**：用 `@SceneStorage` 保留使用者狀態
7. **支援 iPad 多工**：為 split view 與 slide over 做設計
8. **在實機上測試**：模擬器無法完整呈現觸覺回饋與效能體驗

## Common Issues

- **版面跑掉**：少用 `.fixedSize()`，優先用彈性版面
- **效能問題**：長的捲動清單用 `LazyVStack`/`LazyHStack`
- **導覽 bug**：確保 `NavigationLink` 的值是 `Hashable`
- **深色模式問題**：避免寫死顏色，用語意色彩或 asset catalog 的顏色
- **無障礙失敗**：開著 VoiceOver 測試
- **記憶體洩漏**：留意 closure 裡的強參照循環
