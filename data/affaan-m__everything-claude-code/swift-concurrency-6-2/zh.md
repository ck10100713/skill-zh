---
name: swift-concurrency-6-2
description: Swift 6.2 Approachable Concurrency：預設單執行緒、用 @concurrent 明確卸載到背景、為 main actor 型別提供 isolated conformance。採用 Swift 6.2 concurrency（用 @concurrent 卸載工作，或解決 main-actor 隔離問題）時使用。
---

# Swift 6.2 Approachable Concurrency

採用 Swift 6.2 並行模型的模式：程式碼預設單執行緒執行，並行要明確引入。在不犧牲效能的前提下，消除常見的資料競爭錯誤。

## 何時啟用

- 把 Swift 5.x 或 6.0/6.1 的專案遷移到 Swift 6.2
- 解決資料競爭安全性的編譯器錯誤
- 設計以 MainActor 為基礎的 app 架構
- 把吃 CPU 的工作卸載到背景執行緒
- 在 MainActor 隔離的型別上實作 protocol conformance
- 在 Xcode 26 啟用 Approachable Concurrency 的 build 設定

## 核心問題：隱含的背景卸載

在 Swift 6.1 和更早的版本，async 函式可能被隱含地卸載到背景執行緒，造成資料競爭錯誤，即使是看似安全的程式碼也一樣：

```swift
// Swift 6.1: ERROR
@MainActor
final class StickerModel {
    let photoProcessor = PhotoProcessor()

    func extractSticker(_ item: PhotosPickerItem) async throws -> Sticker? {
        guard let data = try await item.loadTransferable(type: Data.self) else { return nil }

        // Error: Sending 'self.photoProcessor' risks causing data races
        return await photoProcessor.extractSticker(data: data, with: item.itemIdentifier)
    }
}
```

Swift 6.2 修好了這點：async 函式預設會留在呼叫它的 actor 上。

```swift
// Swift 6.2: OK — async stays on MainActor, no data race
@MainActor
final class StickerModel {
    let photoProcessor = PhotoProcessor()

    func extractSticker(_ item: PhotosPickerItem) async throws -> Sticker? {
        guard let data = try await item.loadTransferable(type: Data.self) else { return nil }
        return await photoProcessor.extractSticker(data: data, with: item.itemIdentifier)
    }
}
```

## 核心模式：Isolated Conformance

MainActor 型別現在可以安全地遵循非隔離的 protocol：

```swift
protocol Exportable {
    func export()
}

// Swift 6.1: ERROR — crosses into main actor-isolated code
// Swift 6.2: OK with isolated conformance
extension StickerModel: @MainActor Exportable {
    func export() {
        photoProcessor.exportAsPNG()
    }
}
```

編譯器會確保這個 conformance 只在 main actor 上使用：

```swift
// OK — ImageExporter is also @MainActor
@MainActor
struct ImageExporter {
    var items: [any Exportable]

    mutating func add(_ item: StickerModel) {
        items.append(item)  // Safe: same actor isolation
    }
}

// ERROR — nonisolated context can't use MainActor conformance
nonisolated struct ImageExporter {
    var items: [any Exportable]

    mutating func add(_ item: StickerModel) {
        items.append(item)  // Error: Main actor-isolated conformance cannot be used here
    }
}
```

## 核心模式：全域與靜態變數

用 MainActor 保護全域/靜態狀態：

```swift
// Swift 6.1: ERROR — non-Sendable type may have shared mutable state
final class StickerLibrary {
    static let shared: StickerLibrary = .init()  // Error
}

// Fix: Annotate with @MainActor
@MainActor
final class StickerLibrary {
    static let shared: StickerLibrary = .init()  // OK
}
```

### MainActor 預設推斷模式

Swift 6.2 引入了預設推斷為 MainActor 的模式，不需要手動標註：

```swift
// With MainActor default inference enabled:
final class StickerLibrary {
    static let shared: StickerLibrary = .init()  // Implicitly @MainActor
}

final class StickerModel {
    let photoProcessor: PhotoProcessor
    var selection: [PhotosPickerItem]  // Implicitly @MainActor
}

extension StickerModel: Exportable {  // Implicitly @MainActor conformance
    func export() {
        photoProcessor.exportAsPNG()
    }
}
```

這個模式是選用的，建議用在 app、script 和其他可執行檔 target。

## 核心模式：用 @concurrent 做背景工作

需要真正的平行時，用 `@concurrent` 明確卸載：

> **重要：** 這個範例需要 Approachable Concurrency 的 build 設定，也就是 SE-0466（MainActor 預設隔離）和 SE-0461（NonisolatedNonsendingByDefault）。啟用這些之後，`extractSticker` 會留在呼叫端的 actor 上，讓存取可變狀態變得安全。**沒有這些設定，這段程式碼就有資料競爭**，編譯器會標示出來。

```swift
nonisolated final class PhotoProcessor {
    private var cachedStickers: [String: Sticker] = [:]

    func extractSticker(data: Data, with id: String) async -> Sticker {
        if let sticker = cachedStickers[id] {
            return sticker
        }

        let sticker = await Self.extractSubject(from: data)
        cachedStickers[id] = sticker
        return sticker
    }

    // Offload expensive work to concurrent thread pool
    @concurrent
    static func extractSubject(from data: Data) async -> Sticker { /* ... */ }
}

// Callers must await
let processor = PhotoProcessor()
processedPhotos[item.id] = await processor.extractSticker(data: data, with: item.id)
```

使用 `@concurrent` 的步驟：
1. 把包含它的型別標成 `nonisolated`
2. 在函式上加 `@concurrent`
3. 還不是非同步的話，加上 `async`
4. 在呼叫端加上 `await`

## 關鍵設計決策

| 決策 | 理由 |
|----------|-----------|
| 預設單執行緒 | 最自然的程式碼沒有資料競爭；並行是選用的 |
| Async 留在呼叫它的 actor | 消除了造成資料競爭錯誤的隱含卸載 |
| Isolated conformance | MainActor 型別不用不安全的 workaround 就能遵循 protocol |
| `@concurrent` 明確選用 | 背景執行是刻意的效能選擇，不是意外發生的 |
| MainActor 預設推斷 | 減少 app target 上冗長的 `@MainActor` 標註 |
| 選用式採用 | 不會破壞既有程式碼的遷移路徑，可以逐步啟用功能 |

## 遷移步驟

1. **在 Xcode 啟用**：Build Settings 裡的 Swift Compiler > Concurrency 區塊
2. **在 SPM 啟用**：在 package manifest 使用 `SwiftSettings` API
3. **使用遷移工具**：透過 swift.org/migration 自動修改程式碼
4. **從 MainActor 預設開始**：對 app target 啟用推斷模式
5. **需要時才加 `@concurrent`**：先做 profile，再卸載熱點路徑
6. **徹底測試**：資料競爭的問題會變成編譯期錯誤

## 最佳實務

- **從 MainActor 開始**：先寫單執行緒的程式碼，之後再最佳化
- **`@concurrent` 只用在吃 CPU 的工作**：影像處理、壓縮、複雜運算
- 對大多是單執行緒的 app target **啟用 MainActor 推斷模式**
- **卸載之前先 profile**：用 Instruments 找出真正的瓶頸
- **用 MainActor 保護全域變數**：全域/靜態的可變狀態需要 actor 隔離
- **使用 isolated conformance**，不要用 `nonisolated` 的 workaround 或 `@Sendable` 包裝
- **漸進式遷移**：在 build 設定裡一次啟用一個功能

## 要避免的反模式

- 對每個 async 函式都套用 `@concurrent`（大多數不需要背景執行）
- 沒搞懂隔離就用 `nonisolated` 壓掉編譯器錯誤
- actor 已經能提供同樣的安全性，還保留舊式的 `DispatchQueue` 寫法
- 在跟 concurrency 有關的 Foundation Models 程式碼裡，跳過 `model.availability` 檢查
- 跟編譯器對著幹：如果它回報資料競爭，程式碼就是真的有並行問題
- 假設所有 async 程式碼都在背景執行（Swift 6.2 預設：留在呼叫它的 actor）

## 何時使用

- 所有新的 Swift 6.2+ 專案（Approachable Concurrency 是建議的預設值）
- 把既有 app 從 Swift 5.x 或 6.0/6.1 的並行遷移過來
- 導入 Xcode 26 時，解決資料競爭安全性的編譯器錯誤
- 建構以 MainActor 為中心的 app 架構（大多數 UI app）
- 效能最佳化：把特定的繁重運算卸載到背景
