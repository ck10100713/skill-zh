---
name: code-tour
description: 建立 CodeTour 的 `.tour` 檔案：針對特定讀者角色、逐步導覽、錨定在真實檔案與行號上的 walkthrough。適用於新人導覽、架構導覽、PR 導覽、RCA 導覽，以及結構化的「解釋這個怎麼運作」需求。當使用者要求 code tour、onboarding walkthrough、PR tour，或是解釋某個子系統怎麼運作時使用。
metadata:
  origin: ECC
---

# Code Tour

建立 **CodeTour** 的 `.tour` 檔案，用來做 codebase 的導覽，可以直接開到真實的檔案和行號範圍。Tour 放在 `.tours/` 裡，是給 CodeTour 格式用的，不是隨手寫的 Markdown 筆記。

好的 tour 是為特定讀者寫的敘事：
- 他們正在看什麼
- 為什麼重要
- 接下來該順著哪條路走

只建立 `.tour` JSON 檔案。這個 skill 不會修改原始碼。

## When to Use

在下列情況使用這個 skill：
- 使用者要求 code tour、新人導覽、架構導覽或 PR 導覽
- 使用者說「explain how X works」，而且想要一份可重複使用的導覽成品
- 使用者想為新進工程師或 reviewer 建一條上手路徑
- 這個任務用有引導的順序，比用平鋪直敘的摘要更合適

範例：
- 帶新的維護者上手
- 針對某個服務或套件的架構導覽
- 錨定在被改動檔案上的 PR review 導覽
- 展示失敗路徑的 RCA 導覽
- 針對信任邊界和關鍵檢查的安全審查導覽

## When NOT to Use

| Instead of code-tour | Use |
| --- | --- |
| 在對話裡一次性的解釋就夠了 | 直接回答 |
| 使用者要的是文字文件，不是 `.tour` 成品 | `documentation-lookup` 或編輯 repo 文件 |
| 任務是實作或重構 | 直接做實作的工作 |
| 任務是廣泛的 codebase 上手，不需要 tour 成品 | `codebase-onboarding` |

## Workflow

### 1. Discover

寫任何東西之前，先探索 repo：
- README 和套件/應用程式的進入點
- 資料夾結構
- 相關的設定檔
- 如果 tour 以 PR 為主，就看被改動的檔案

在你搞懂程式碼的樣貌之前，不要開始寫步驟。

### 2. Infer the reader

根據需求判斷讀者角色和深度。

| Request shape | Persona | Suggested depth |
| --- | --- | --- |
| "onboarding", "new joiner" | `new-joiner` | 9-13 steps |
| "quick tour", "vibe check" | `vibecoder` | 5-8 steps |
| "architecture" | `architect` | 14-18 steps |
| "tour this PR" | `pr-reviewer` | 7-11 steps |
| "why did this break" | `rca-investigator` | 7-11 steps |
| "security review" | `security-reviewer` | 7-11 steps |
| "explain how this feature works" | `feature-explainer` | 7-11 steps |
| "debug this path" | `bug-fixer` | 7-11 steps |

### 3. Read and verify anchors

每個檔案路徑和行號錨點都必須是真的：
- 確認檔案存在
- 確認行號在範圍內
- 如果用 selection，要驗證確切的區塊
- 如果檔案常常變動，優先用以 pattern 為基礎的錨點

絕對不要猜行號。

### 4. Write the `.tour`

寫到：

```text
.tours/<persona>-<focus>.tour
```

路徑要固定而且好讀。

### 5. Validate

完成之前：
- 每個引用的路徑都存在
- 每個行號或 selection 都有效
- 第一個步驟錨定在真實的檔案或目錄上
- `ref` 指向的 branch 或 commit，確實包含 tour 引用的每一個檔案（見下方）
- tour 在講一個連貫的故事，而不是羅列檔案

## The `ref` Field

`ref` 把 tour 綁在某個 git branch 或 commit 上。它比看起來更重要：當 `ref` 不是讀者目前 checkout 的 branch 時，CodeTour 會從 git 裡那個版本開啟每個步驟的檔案，而不是讀磁碟上的檔案。如果檔案不在那個版本裡，這個步驟就開不起來，讀者會看到 *"The editor could not be opened because the file was not found"*，即使檔案明明就在那裡。Tour 和它的註解仍然會顯示，所以真正的原因很容易被忽略。

依 tour 類型選 `ref`：

| Tour type | Set `ref` to |
| --- | --- |
| PR tour | PR 的 branch，絕對不要用 base branch |
| Onboarding / architecture | 讀者會在的 branch（通常是 `main`），或是不設 |
| Not sure | 不要設 `ref`，這樣 CodeTour 會直接從磁碟讀檔案 |

PR 的情況是常見的陷阱：PR 通常會新增檔案，而新檔案在 base branch 上還不存在。把 `ref` 指向 base（例如 `develop`），所有指向新檔案的步驟都會打不開。

完成之前，確認每個步驟的檔案在你選的 `ref` 上確實存在。

## Step Types

### Content

少用，通常只用在收尾步驟：

```json
{ "title": "Next Steps", "description": "You can now trace the request path end to end." }
```

不要讓第一個步驟只有內容。

### Directory

用來讓讀者對某個模組有方向感：

```json
{ "directory": "src/services", "title": "Service Layer", "description": "The core orchestration logic lives here." }
```

### File + line

這是預設的步驟類型：

```json
{ "file": "src/auth/middleware.ts", "line": 42, "title": "Auth Gate", "description": "Every protected request passes here first." }
```

### Selection

當某一段程式碼比整個檔案更重要時使用：

```json
{
  "file": "src/core/pipeline.ts",
  "selection": {
    "start": { "line": 15, "character": 0 },
    "end": { "line": 34, "character": 0 }
  },
  "title": "Request Pipeline",
  "description": "This block wires validation, auth, and downstream execution."
}
```

### Pattern

當確切的行號可能會漂移時使用：

```json
{ "file": "src/app.ts", "pattern": "export default class App", "title": "Application Entry" }
```

### URI

需要時，用來連到 PR、issue 或文件：

```json
{ "uri": "https://github.com/org/repo/pull/456", "title": "The PR" }
```

## Writing Rule: SMIG

每段描述都應該回答：
- **Situation**：讀者正在看什麼
- **Mechanism**：它怎麼運作
- **Implication**：對這個角色來說為什麼重要
- **Gotcha**：聰明的讀者可能會漏掉什麼

描述要精簡、具體，並且以實際的程式碼為根據。

## Narrative Shape

除非任務明顯需要不同的結構，否則用這個弧線：
1. 方向感（orientation）
2. 模組地圖
3. 核心執行路徑
4. 邊界情況或陷阱
5. 收尾 / 下一步

Tour 應該讀起來像一條路，不是一份清單。

## Example

```json
{
  "$schema": "https://aka.ms/codetour-schema",
  "title": "API Service Tour",
  "description": "Walkthrough of the request path for the payments service.",
  "ref": "main",
  "steps": [
    {
      "directory": "src",
      "title": "Source Root",
      "description": "All runtime code for the service starts here."
    },
    {
      "file": "src/server.ts",
      "line": 12,
      "title": "Entry Point",
      "description": "The server boots here and wires middleware before any route is reached."
    },
    {
      "file": "src/routes/payments.ts",
      "line": 8,
      "title": "Payment Routes",
      "description": "Every payments request enters through this router before hitting service logic."
    },
    {
      "title": "Next Steps",
      "description": "You can now follow any payment request end to end with the main anchors in place."
    }
  ]
}
```

## Anti-Patterns

| Anti-pattern | Fix |
| --- | --- |
| 平鋪的檔案清單 | 用步驟之間的依賴關係說一個故事 |
| 籠統的描述 | 點出具體的程式碼路徑或模式 |
| 猜出來的錨點 | 先驗證每個檔案和行號 |
| 快速導覽卻有太多步驟 | 大刀闊斧地刪 |
| 第一個步驟只有內容 | 把第一個步驟錨定在真實的檔案或目錄上 |
| 讀者角色不符 | 為實際的讀者寫，不要為一般的工程師寫 |

## Best Practices

- 步驟數量要和 repo 規模以及角色的深度成比例
- 方向感用 directory 步驟，實質內容用 file 步驟
- PR 導覽要先涵蓋被改動的檔案
- monorepo 要把範圍限縮在相關的套件，不要什麼都導覽
- 結尾講讀者現在能做什麼，不要重複摘要

## Related Skills

- `codebase-onboarding`
- `coding-standards`
- `council`
- 官方上游格式：`microsoft/codetour`
