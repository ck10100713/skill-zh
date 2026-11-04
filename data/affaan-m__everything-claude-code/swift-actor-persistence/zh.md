---
name: swift-actor-persistence
description: 在 Swift 裡用 actor 做執行緒安全的資料持久化：以檔案為底的記憶體快取，從設計上消除資料競爭。在 Swift 裡持久化資料，而且需要從設計上排除資料競爭或執行緒安全問題時使用。
metadata:
  origin: ECC
---

# 用 Swift Actor 做執行緒安全的持久化

用 Swift actor 打造執行緒安全資料持久層的模式。結合記憶體快取與檔案儲存，利用 actor 模型在編譯期消除資料競爭。

## 何時啟用

- 在 Swift 5.5+ 中建構資料持久層
- 需要以執行緒安全的方式存取共享的可變狀態
- 想消除手動同步（lock、DispatchQueue）
- 建構採用本地儲存的 offline-first 應用程式

## 核心模式

### 以 Actor 為基礎的 Repository

Actor 模型保證序列化存取，沒有資料競爭，由編譯器強制執行。

```swift
public actor LocalRepository<T: Codable & Identifiable> where T.ID == String {
    private var cache: [String: T] = [:]
    private let fileURL: URL

    public init(directory: URL = .documentsDirectory, filename: String = "data.json") {
        self.fileURL = directory.appendingPathComponent(filename)
        // Synchronous load during init (actor isolation not yet active)
        self.cache = Self.loadSynchronously(from: fileURL)
    }

    // MARK: - Public API

    public func save(_ item: T) throws {
        cache[item.id] = item
        try persistToFile()
    }

    public func delete(_ id: String) throws {
        cache[id] = nil
        try persistToFile()
    }

    public func find(by id: String) -> T? {
        cache[id]
    }

    public func loadAll() -> [T] {
        Array(cache.values)
    }

    // MARK: - Private

    private func persistToFile() throws {
        let data = try JSONEncoder().encode(Array(cache.values))
        try data.write(to: fileURL, options: .atomic)
    }

    private static func loadSynchronously(from url: URL) -> [String: T] {
        guard let data = try? Data(contentsOf: url),
              let items = try? JSONDecoder().decode([T].self, from: data) else {
            return [:]
        }
        return Dictionary(uniqueKeysWithValues: items.map { ($0.id, $0) })
    }
}
```

### 使用方式

因為 actor 隔離，所有呼叫都會自動變成 async：

```swift
let repository = LocalRepository<Question>()

// Read — fast O(1) lookup from in-memory cache
let question = await repository.find(by: "q-001")
let allQuestions = await repository.loadAll()

// Write — updates cache and persists to file atomically
try await repository.save(newQuestion)
try await repository.delete("q-001")
```

### 搭配 @Observable ViewModel

```swift
@Observable
final class QuestionListViewModel {
    private(set) var questions: [Question] = []
    private let repository: LocalRepository<Question>

    init(repository: LocalRepository<Question> = LocalRepository()) {
        self.repository = repository
    }

    func load() async {
        questions = await repository.loadAll()
    }

    func add(_ question: Question) async throws {
        try await repository.save(question)
        questions = await repository.loadAll()
    }
}
```

## 關鍵設計決策

| 決策 | 理由 |
|----------|-----------|
| 用 Actor（不是 class + lock） | 由編譯器強制執行緒安全，不需要手動同步 |
| 記憶體快取 + 檔案持久化 | 從快取快速讀取，寫入磁碟確保持久 |
| 同步載入的 init | 避開非同步初始化的複雜度 |
| 以 ID 為 key 的 Dictionary | 以識別碼做 O(1) 查找 |
| 對 `Codable & Identifiable` 泛型化 | 可重複用於任何模型型別 |
| 原子檔案寫入（`.atomic`） | 避免當機時只寫入一半 |

## 最佳實務

- 所有跨越 actor 邊界的資料都**使用 `Sendable` 型別**
- **讓 actor 的公開 API 保持最小**：只公開領域操作，不要公開持久化細節
- **用 `.atomic` 寫入**，避免 app 在寫入中途當機造成資料損毀
- **在 `init` 裡同步載入**：對本地檔案來說，async 初始化只增加複雜度，好處很小
- **搭配 `@Observable`** ViewModel，做回應式的 UI 更新

## 要避免的反模式

- 新的 Swift concurrency 程式碼，卻用 `DispatchQueue` 或 `NSLock` 取代 actor
- 把內部的快取 dictionary 暴露給外部呼叫者
- 讓檔案 URL 可設定，卻沒有驗證
- 忘了所有 actor 方法呼叫都是 `await`：呼叫者必須處理 async context
- 用 `nonisolated` 繞過 actor 隔離（這就失去了意義）

## 何時使用

- iOS/macOS app 的本地資料儲存（使用者資料、設定、快取內容）
- 之後才同步到伺服器的 offline-first 架構
- app 中多個部分並行存取的任何共享可變狀態
- 把舊式以 `DispatchQueue` 為基礎的執行緒安全，換成現代的 Swift concurrency
