---
name: strategic-compact
description: 在邏輯上合適的時間點建議手動壓縮 context，讓 context 能撐過各個任務階段，而不是任由自動壓縮在隨機時間點觸發。session 接近 context 上限、而且任務階段剛好是壓縮的自然時機時使用。
metadata:
  origin: ECC
---

# Strategic Compact Skill

在工作流程的策略性時間點建議手動執行 `/compact`，而不是仰賴隨機觸發的自動壓縮。

## 何時啟用

- 執行長時間 session，接近 context 上限（200K+ token）
- 處理多階段任務（研究 → 規劃 → 實作 → 測試）
- 在同一個 session 裡切換不相關的任務
- 完成一個重大里程碑，要開始新工作時
- 回應變慢或變得比較不連貫時（context 壓力）

## 為什麼要策略性壓縮？

自動壓縮會在隨機的時間點觸發：
- 常常發生在任務進行到一半，丟掉重要的 context
- 不知道任務的邏輯邊界在哪
- 可能打斷複雜的多步驟操作

在邏輯邊界做策略性壓縮：
- **探索之後、執行之前**：壓縮研究的 context，保留實作計畫
- **完成一個里程碑之後**：為下一階段重新開始
- **重大 context 轉換之前**：在換到不同任務前，先清掉探索的 context

## 運作方式

`suggest-compact.js` script 在 PreToolUse（Edit/Write）時執行，並結合兩個訊號：

1. **Context 大小（主要）**：從 session transcript 讀取最新的 `usage` 紀錄（hook payload 裡的 `transcript_path`），並加總 `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`（這一輪真正的 context 大小）。在隨視窗縮放的門檻建議 `/compact`：200k 視窗是 160k token，1M 視窗是 250k（從 `[1m]` 模型標記偵測，或在觀察到的 token 已超過 200k 時推斷），之後 context 每多成長 60k token 就再提醒一次。有效的原生壓縮預算，可以把預設的提醒門檻降到該預算的 80%；模型容量百分比仍然使用解析出來的模型視窗
2. **Tool call 次數（次要）**：計算 session 中的工具呼叫次數；在可設定的門檻（預設：50 次）建議，之後每 25 次再建議一次

單靠工具呼叫次數，很難反映視窗壓力：幾次大型檔案讀取或 MCP 回應就能在很少的呼叫次數內塞滿視窗，而很多微小的呼叫即使跨過 50 次，視窗也幾乎是空的。Context 大小這個訊號，會在真正重要的時候觸發。

## Hook 設定

**用 plugin 安裝的？** 不需要任何設定。Plugin 的 `hooks/hooks.json` 已經註冊了 `suggest-compact.js`（hook id `pre:edit-write:suggest-compact`，在 `standard` 和 `strict` 的 hook profile 中啟用）。不要把下面的區塊複製到 `~/.claude/settings.json`，因為 plugin 安裝後 `~/.claude/scripts/` 並不存在，而且重複註冊 plugin 的 hook 會造成重複執行。

**手動安裝的**（`./install.sh`），加到你的 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "node ~/.claude/scripts/hooks/suggest-compact.js" }]
      },
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "command": "node ~/.claude/scripts/hooks/suggest-compact.js" }]
      }
    ]
  }
}
```

## 設定

環境變數：
- `COMPACT_THRESHOLD`：第一次建議之前的 tool call 次數（預設：50）
- `COMPACT_CONTEXT_THRESHOLD`：觸發 context 大小建議之前的 context token 數（預設：200k 視窗是 160000，1M 視窗是 250000，在原生壓縮預算有效且更早時，上限為其 80%）。明確指定的正數門檻會覆寫這個預設上限；`0` 會停用 context 訊號。
- `COMPACT_CONTEXT_INTERVAL`：建議重複出現之前，額外的 context token 數（預設：60000）
- `COMPACT_STATE_TTL_DAYS`：暫存目錄中過期的各 session 狀態檔被清掃之前的天數（預設：14）
- `ECC_CONTEXT_WINDOW_TOKENS`：明確指定 context 視窗大小（以 token 計），覆寫自動偵測。對於回報的 id 沒有 `[1m]` 標記的大視窗模型（例如 400k 的 Opus 4.x，或新的 1M 視窗模型家族）要設這個，讓門檻依真實的視窗縮放，而不是預設成 200k 而高估 context 用量。
- `CLAUDE_CODE_AUTO_COMPACT_WINDOW`：Claude Code 原生自動壓縮的觸發點，可能比模型的 context 視窗小。在解析 context 視窗時，ECC 只把它當成最後的退路，順序在明確的 ECC 覆寫、`[1m]` 模型標記、已知的大視窗模型家族，以及從觀察到的超過 200k token 推斷之後。它不是精確的模型容量宣告。

> 視窗的優先順序是：`ECC_CONTEXT_WINDOW_TOKENS`，接著是 `[1m]` 標記、已知的大視窗模型家族、觀察到的超過 200k token、原生自動壓縮的退路，最後是推斷出的 200k 預設值。當你知道實際的視窗大小、而自動偵測缺少這項資訊時，請設定 `ECC_CONTEXT_WINDOW_TOKENS`；不要把原生壓縮的觸發點當成模型容量的證明。

Stop-hook 的摘要排程器會在壓縮之前保護續接狀態。它採用已確認容量和有效原生壓縮預算兩者中較早的那個。當容量是推斷出來的，它只使用有效的原生預算，沒有提供的話，就把剩餘預算視為未知。模型容量的解析則維持獨立。預設的 `/compact` 提醒門檻，獨立採用其隨視窗縮放的預設值，和有效原生壓縮預算的 80% 兩者中較早的那個。明確指定的 `COMPACT_CONTEXT_THRESHOLD`（包含 `0`）仍然是最終依據。

## 壓縮決策指南

用這張表決定何時壓縮：

| 階段轉換 | 要壓縮嗎？ | 為什麼 |
|-----------------|----------|-----|
| 研究 → 規劃 | 要 | 研究的 context 很龐大；計畫才是提煉後的產出 |
| 規劃 → 實作 | 要 | 計畫已經寫下來（寫成檔案，或有的話寫成任務清單）；把 context 空出來給程式碼 |
| 實作 → 測試 | 看情況 | 測試會參照最近的程式碼就保留；要切換焦點就壓縮 |
| 除錯 → 下一個功能 | 要 | 除錯軌跡會污染不相關工作的 context |
| 實作進行到一半 | 不要 | 丟掉變數名稱、檔案路徑和部分狀態代價很高 |
| 某個做法失敗之後 | 要 | 在嘗試新做法之前，先清掉死胡同的推理 |

## 壓縮後留下什麼

了解什麼會留下來，能讓你放心壓縮：

| 會留下 | 會遺失 |
|----------|------|
| CLAUDE.md 的指示 | 中間的推理與分析 |
| 磁碟上的檔案 | 你先前讀過的檔案內容 |
| Memory 檔案（`~/.claude/memory/`） | 多步驟的對話 context |
| Git 狀態（commit、branch） | Tool call 歷史和次數 |
| 任務清單，**只有在你有 todo 工具時**（見下方） | 口頭說過的細微使用者偏好 |

> ### 不要指望任務清單會留下來，它可能根本不存在
>
> Claude Code **2.1.233 預設移除了 todo/task 工具**，涵蓋 Opus 4.8、Sonnet 5、
> Fable 5、Mythos 5 和更新的模型（`TodoWrite`、`TaskCreate/Get/Update/List`）。
> `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` 可以把它們帶回來，但那是每台機器各自的
> 環境設定，**不會跟著這個 skill 走**，所以你不能假設
> 讀的人有它。
>
> 這點很重要，因為「我的 todo 清單在壓縮後還在」，正是有人選擇壓縮
> *而不是*把狀態寫下來的理由。如果工具不存在，就沒有清單能留下來，
> 計畫就這樣沒了。**壓縮之前，先把計畫寫成檔案**，檔案在每個版本、每個模型上
> 都會留著。把任務清單當成可能缺席的便利功能，絕對不要把它當成你的持久紀錄。

## 最佳實務

1. **規劃之後壓縮**：計畫定案**而且寫成檔案**之後，壓縮以重新開始
2. **除錯之後壓縮**：在繼續之前，清掉排錯過程的 context
3. **實作進行到一半時不要壓縮**：保留相關變更需要的 context
4. **讀懂建議**：hook 告訴你*什麼時候*，你決定*要不要*
5. **壓縮之前先寫下來**：壓縮之前，把重要的 context 存到檔案或 memory
6. **`/compact` 搭配摘要使用**：加上自訂訊息：`/compact Focus on implementing auth middleware next`

## Token 最佳化模式

### 觸發表延遲載入
不要在 session 開始時載入完整的 skill 內容，改用觸發表把關鍵字對應到 skill 路徑。Skill 只在被觸發時才載入，可以把基準 context 減少 50% 以上：

| 觸發詞 | Skill | 載入時機 |
|---------|-------|-----------|
| "test"、"tdd"、"coverage" | tdd-workflow | 使用者提到測試 |
| "security"、"auth"、"xss" | security-review | 安全相關的工作 |
| "deploy"、"ci/cd" | deployment-patterns | 部署情境 |

### Context 組成意識
監看是什麼在吃掉你的 context 視窗：
- **CLAUDE.md 檔案**：永遠會載入，要保持精簡
- **已載入的 skill**：每個 skill 增加 1 到 5K token
- **對話歷史**：隨每次往返成長
- **工具結果**：檔案讀取、搜尋結果會增加大量體積

### 重複指示偵測
重複 context 的常見來源：
- 同樣的規則同時出現在 `~/.claude/rules/` 和專案的 `.claude/rules/`
- 重複 CLAUDE.md 指示的 skill
- 多個 skill 涵蓋重疊的領域

### Context 最佳化工具
- `token-optimizer` MCP：透過內容去重，自動減少 95% 以上的 token
- `context-mode`：Context 虛擬化（示範過從 315KB 縮到 5.4KB）

## 相關

- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352)：Token 最佳化段落
- Memory 持久化 hook：用於能撐過壓縮的狀態
- `continuous-learning` skill：在 session 結束前擷取模式
