---
name: foundation-models-on-device
description: Apple FoundationModels 框架的裝置端 LLM 用法，包含文字生成、搭配 @Generable 的引導式生成、tool calling，以及 iOS 26+ 的 snapshot streaming。要在 iOS 26+ 用 Apple FoundationModels 加入裝置端 LLM 功能時使用。
---

# FoundationModels: On-Device LLM (iOS 26)

用 FoundationModels 框架把 Apple 的裝置端語言模型整合進 app 的做法。涵蓋文字生成、用 `@Generable` 產生結構化輸出、自訂 tool calling 和 snapshot streaming，全部都在裝置上執行，保護隱私也支援離線。

## When to Activate

- 用 Apple Intelligence 在裝置端打造 AI 功能
- 不依賴雲端來生成或摘要文字
- 從自然語言輸入中擷取結構化資料
- 為特定領域的 AI 動作實作自訂 tool calling
- 串流結構化回應，讓 UI 即時更新
- 需要保護隱私的 AI（資料不會離開裝置）

## Core Pattern — Availability Check

建立 session 之前，一定要先檢查模型是否可用：

```swift
struct GenerativeView: View {
    private var model = SystemLanguageModel.default

    var body: some View {
        switch model.availability {
        case .available:
            ContentView()
        case .unavailable(.deviceNotEligible):
            Text("Device not eligible for Apple Intelligence")
        case .unavailable(.appleIntelligenceNotEnabled):
            Text("Please enable Apple Intelligence in Settings")
        case .unavailable(.modelNotReady):
            Text("Model is downloading or not ready")
        case .unavailable(let other):
            Text("Model unavailable: \(other)")
        }
    }
}
```

## Core Pattern — Basic Session

```swift
// 單輪：每次都建立新的 session
let session = LanguageModelSession()
let response = try await session.respond(to: "What's a good month to visit Paris?")
print(response.content)

// 多輪：重用 session 以保留對話脈絡
let session = LanguageModelSession(instructions: """
    You are a cooking assistant.
    Provide recipe suggestions based on ingredients.
    Keep suggestions brief and practical.
    """)

let first = try await session.respond(to: "I have chicken and rice")
let followUp = try await session.respond(to: "What about a vegetarian option?")
```

寫 instructions 的重點：
- 定義模型的角色（「You are a mentor」）
- 說明要做什麼（「Help extract calendar events」）
- 設定風格偏好（「Respond as briefly as possible」）
- 加上安全措施（遇到危險請求就回「I can't help with that」）

## Core Pattern — Guided Generation with @Generable

生成結構化的 Swift 型別，不要拿原始字串：

### 1. Define a Generable Type

```swift
@Generable(description: "Basic profile information about a cat")
struct CatProfile {
    var name: String

    @Guide(description: "The age of the cat", .range(0...20))
    var age: Int

    @Guide(description: "A one sentence profile about the cat's personality")
    var profile: String
}
```

### 2. Request Structured Output

```swift
let response = try await session.respond(
    to: "Generate a cute rescue cat",
    generating: CatProfile.self
)

// 直接存取結構化欄位
print("Name: \(response.content.name)")
print("Age: \(response.content.age)")
print("Profile: \(response.content.profile)")
```

### Supported @Guide Constraints

- `.range(0...20)`：數值範圍
- `.count(3)`：陣列元素個數
- `description:`：給生成過程的語意引導

## Core Pattern — Tool Calling

讓模型呼叫自訂程式碼，處理特定領域的任務：

### 1. Define a Tool

```swift
struct RecipeSearchTool: Tool {
    let name = "recipe_search"
    let description = "Search for recipes matching a given term and return a list of results."

    @Generable
    struct Arguments {
        var searchTerm: String
        var numberOfResults: Int
    }

    func call(arguments: Arguments) async throws -> ToolOutput {
        let recipes = await searchRecipes(
            term: arguments.searchTerm,
            limit: arguments.numberOfResults
        )
        return .string(recipes.map { "- \($0.name): \($0.description)" }.joined(separator: "\n"))
    }
}
```

### 2. Create Session with Tools

```swift
let session = LanguageModelSession(tools: [RecipeSearchTool()])
let response = try await session.respond(to: "Find me some pasta recipes")
```

### 3. Handle Tool Errors

```swift
do {
    let answer = try await session.respond(to: "Find a recipe for tomato soup.")
} catch let error as LanguageModelSession.ToolCallError {
    print(error.tool.name)
    if case .databaseIsEmpty = error.underlyingError as? RecipeSearchToolError {
        // 處理特定的 tool 錯誤
    }
}
```

## Core Pattern — Snapshot Streaming

用 `PartiallyGenerated` 型別串流結構化回應，讓 UI 即時更新：

```swift
@Generable
struct TripIdeas {
    @Guide(description: "Ideas for upcoming trips")
    var ideas: [String]
}

let stream = session.streamResponse(
    to: "What are some exciting trip ideas?",
    generating: TripIdeas.self
)

for try await partial in stream {
    // partial: TripIdeas.PartiallyGenerated（所有屬性都是 Optional）
    print(partial)
}
```

### SwiftUI Integration

```swift
@State private var partialResult: TripIdeas.PartiallyGenerated?
@State private var errorMessage: String?

var body: some View {
    List {
        ForEach(partialResult?.ideas ?? [], id: \.self) { idea in
            Text(idea)
        }
    }
    .overlay {
        if let errorMessage { Text(errorMessage).foregroundStyle(.red) }
    }
    .task {
        do {
            let stream = session.streamResponse(to: prompt, generating: TripIdeas.self)
            for try await partial in stream {
                partialResult = partial
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| 在裝置端執行 | 隱私：資料不會離開裝置，離線也能用 |
| 4,096 token 上限 | 裝置端模型的限制；大量資料要拆成多個 session 分批處理 |
| Snapshot streaming（不是 delta） | 對結構化輸出友善；每個 snapshot 都是一個完整的部分狀態 |
| `@Generable` macro | 結構化生成有編譯期安全；自動產生 `PartiallyGenerated` 型別 |
| 每個 session 同時只處理一個請求 | `isResponding` 會阻止並行請求；需要的話就建多個 session |
| `response.content`（不是 `.output`） | 這才是正確的 API，一律透過 `.content` 屬性取結果 |

## Best Practices

- **一定要檢查 `model.availability`**，建立 session 前先做，所有不可用的情況都要處理
- **用 `instructions`** 引導模型行為，它的優先順序高於 prompt
- **送新請求前先檢查 `isResponding`**，session 一次只處理一個請求
- **用 `response.content`** 取結果，不要用 `.output`
- **大型輸入要切成小塊**，4,096 token 的上限是 instructions + prompt + 輸出加起來算
- **結構化輸出用 `@Generable`**，比解析原始字串更有保障
- **用 `GenerationOptions(temperature:)`** 調整創意程度（越高越有創意）
- **用 Instruments 監控**，用 Xcode Instruments 分析請求效能

## Anti-Patterns to Avoid

- 沒先檢查 `model.availability` 就建立 session
- 送出超過 4,096 token context window 的輸入
- 在同一個 session 上嘗試並行請求
- 用 `.output` 而不是 `.content` 來取回應資料
- 明明可以用 `@Generable` 結構化輸出，卻去解析原始字串回應
- 把複雜的多步驟邏輯塞在單一個 prompt 裡，應該拆成多個各有重點的 prompt
- 假設模型永遠可用，裝置資格和設定各有不同

## When to Use

- 對隱私敏感的 app，在裝置端生成文字
- 從使用者輸入擷取結構化資料（表單、自然語言指令）
- 一定要能離線運作的 AI 輔助功能
- 逐步顯示生成內容的串流 UI
- 透過 tool calling 執行特定領域的 AI 動作（搜尋、運算、查詢）
