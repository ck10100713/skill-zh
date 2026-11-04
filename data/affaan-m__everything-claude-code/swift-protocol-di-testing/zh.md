---
name: swift-protocol-di-testing
description: 以 protocol 為基礎的依賴注入，讓 Swift 程式碼可測試：用聚焦的 protocol 和 Swift Testing 來 mock 檔案系統、網路和外部 API。Swift 程式碼需要測試，而且檔案系統、網路或外部 API 必須被 mock 時使用。
metadata:
  origin: ECC
---

# 用 Swift Protocol 依賴注入做測試

把外部相依項（檔案系統、網路、iCloud）抽象到小而聚焦的 protocol 後面，讓 Swift 程式碼可以測試的模式。讓測試不用 I/O 也能保持確定性。

## 何時啟用

- 撰寫會存取檔案系統、網路或外部 API 的 Swift 程式碼
- 需要測試錯誤處理路徑，又不想觸發真正的失敗
- 建構要能跨環境運作的模組（app、測試、SwiftUI preview）
- 搭配 Swift concurrency（actor、Sendable）設計可測試的架構

## 核心模式

### 1. 定義小而聚焦的 Protocol

每個 protocol 只處理一個外部關注點。

```swift
// File system access
public protocol FileSystemProviding: Sendable {
    func containerURL(for purpose: Purpose) -> URL?
}

// File read/write operations
public protocol FileAccessorProviding: Sendable {
    func read(from url: URL) throws -> Data
    func write(_ data: Data, to url: URL) throws
    func fileExists(at url: URL) -> Bool
}

// Bookmark storage (e.g., for sandboxed apps)
public protocol BookmarkStorageProviding: Sendable {
    func saveBookmark(_ data: Data, for key: String) throws
    func loadBookmark(for key: String) throws -> Data?
}
```

### 2. 建立預設（正式環境）實作

```swift
public struct DefaultFileSystemProvider: FileSystemProviding {
    public init() {}

    public func containerURL(for purpose: Purpose) -> URL? {
        FileManager.default.url(forUbiquityContainerIdentifier: nil)
    }
}

public struct DefaultFileAccessor: FileAccessorProviding {
    public init() {}

    public func read(from url: URL) throws -> Data {
        try Data(contentsOf: url)
    }

    public func write(_ data: Data, to url: URL) throws {
        try data.write(to: url, options: .atomic)
    }

    public func fileExists(at url: URL) -> Bool {
        FileManager.default.fileExists(atPath: url.path)
    }
}
```

### 3. 建立測試用的 Mock 實作

```swift
public final class MockFileAccessor: FileAccessorProviding, @unchecked Sendable {
    public var files: [URL: Data] = [:]
    public var readError: Error?
    public var writeError: Error?

    public init() {}

    public func read(from url: URL) throws -> Data {
        if let error = readError { throw error }
        guard let data = files[url] else {
            throw CocoaError(.fileReadNoSuchFile)
        }
        return data
    }

    public func write(_ data: Data, to url: URL) throws {
        if let error = writeError { throw error }
        files[url] = data
    }

    public func fileExists(at url: URL) -> Bool {
        files[url] != nil
    }
}
```

### 4. 用預設參數注入相依項

正式環境的程式碼用預設值；測試則注入 mock。

```swift
public actor SyncManager {
    private let fileSystem: FileSystemProviding
    private let fileAccessor: FileAccessorProviding

    public init(
        fileSystem: FileSystemProviding = DefaultFileSystemProvider(),
        fileAccessor: FileAccessorProviding = DefaultFileAccessor()
    ) {
        self.fileSystem = fileSystem
        self.fileAccessor = fileAccessor
    }

    public func sync() async throws {
        guard let containerURL = fileSystem.containerURL(for: .sync) else {
            throw SyncError.containerNotAvailable
        }
        let data = try fileAccessor.read(
            from: containerURL.appendingPathComponent("data.json")
        )
        // Process data...
    }
}
```

### 5. 用 Swift Testing 寫測試

```swift
import Testing

@Test("Sync manager handles missing container")
func testMissingContainer() async {
    let mockFileSystem = MockFileSystemProvider(containerURL: nil)
    let manager = SyncManager(fileSystem: mockFileSystem)

    await #expect(throws: SyncError.containerNotAvailable) {
        try await manager.sync()
    }
}

@Test("Sync manager reads data correctly")
func testReadData() async throws {
    let mockFileAccessor = MockFileAccessor()
    mockFileAccessor.files[testURL] = testData

    let manager = SyncManager(fileAccessor: mockFileAccessor)
    let result = try await manager.loadData()

    #expect(result == expectedData)
}

@Test("Sync manager handles read errors gracefully")
func testReadError() async {
    let mockFileAccessor = MockFileAccessor()
    mockFileAccessor.readError = CocoaError(.fileReadCorruptFile)

    let manager = SyncManager(fileAccessor: mockFileAccessor)

    await #expect(throws: SyncError.self) {
        try await manager.sync()
    }
}
```

## 最佳實務

- **單一職責**：每個 protocol 只處理一個關注點，不要建立方法一大堆的「上帝 protocol」
- **Sendable conformance**：protocol 跨 actor 邊界使用時必須有
- **預設參數**：讓正式環境的程式碼預設使用真實實作；只有測試需要指定 mock
- **錯誤模擬**：設計 mock 時，要有可設定的錯誤屬性，用來測試失敗路徑
- **只 mock 邊界**：mock 外部相依項（檔案系統、網路、API），不要 mock 內部型別

## 要避免的反模式

- 建立涵蓋所有外部存取的單一巨大 protocol
- Mock 沒有外部相依項的內部型別
- 用 `#if DEBUG` 條件編譯，取代正確的依賴注入
- 搭配 actor 使用時，忘了 `Sendable` conformance
- 過度設計：如果某個型別沒有外部相依項，就不需要 protocol

## 何時使用

- 任何會碰到檔案系統、網路或外部 API 的 Swift 程式碼
- 測試在真實環境很難觸發的錯誤處理路徑
- 建構需要在 app、測試和 SwiftUI preview 情境下都能運作的模組
- 使用 Swift concurrency（actor、結構化並行）、需要可測試架構的 app
