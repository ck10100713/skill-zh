---
name: agent-architecture-audit
description: 針對 agent 和 LLM 應用的全棧診斷。稽核 12 層的 agent stack，找出 wrapper 退化、記憶污染、工具紀律失敗、隱藏的修復迴圈，以及渲染損壞。產出依嚴重程度排序、以程式碼為先的修復建議。對建構 agent 應用、自主迴圈，或任何 LLM 驅動功能的開發者來說很重要。當 agent 或 LLM 功能行為異常、又不知道是哪一層出問題時，或是在出貨 agent stack 之前使用。
metadata:
  origin: oh-my-agent-check
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Agent Architecture Audit

針對 agent 系統的診斷工作流程，這類系統會把失敗藏在 wrapper 層、過時的記憶、重試迴圈，或傳輸／渲染的變異後面。

## When to Activate

**以下情況一定要用：**
- 把任何 agent 或 LLM 驅動的應用發布到 production
- 出貨帶有工具呼叫、記憶或多步驟工作流程的功能
- 加了 wrapper 層之後 agent 的行為退化
- 使用者回報「agent 越來越差」或「工具不穩」
- 同一個 model 在 playground 裡正常，放進你的 wrapper 裡就壞掉
- 除錯 agent 行為超過 15 分鐘還找不到根本原因

**特別關鍵的情況：**
- 你加了新的 prompt 層、工具定義或記憶系統
- 你系統裡不同的 agent 行為不一致
- model 昨天還好好的，今天卻在幻覺
- 你懷疑隱藏的修復／重試迴圈在默默改動回應

**不要用在：**
- 一般的程式碼除錯：用 `agent-introspection-debugging`
- Code review：用各語言專屬的 reviewer agent
- 資安掃描：用 `security-review` 或 `security-review/scan`
- Agent 效能 benchmark：用 `agent-eval`
- 寫新功能：用合適的工作流程 skill

## The 12-Layer Stack

每個 agent 系統都有這些層。其中任何一層都可能弄壞答案：

| # | 層 | 會出什麼問題 |
|---|-------|----------------|
| 1 | System prompt | 指示衝突、指示膨脹 |
| 2 | Session history | 從先前的回合注入過時的 context |
| 3 | 長期記憶 | 跨 session 污染、新對話裡出現舊話題 |
| 4 | 蒸餾（Distillation） | 壓縮後的產物以偽事實的形式重新進入 |
| 5 | 主動回想（Active recall） | 多餘的重新摘要層浪費 context |
| 6 | 工具選擇 | 工具路由錯誤、model 跳過必要的工具 |
| 7 | 工具執行 | 幻覺執行：聲稱呼叫了卻沒有呼叫 |
| 8 | 工具結果詮釋 | 誤讀或忽略工具輸出 |
| 9 | 答案塑形 | 最終回應的格式損壞 |
| 10 | 平台渲染 | 傳輸層變異（UI、API、CLI 改動了有效的答案） |
| 11 | 隱藏的修復迴圈 | 默默的 fallback／重試 agent 跑第二次 LLM 處理 |
| 12 | 持久化 | 過期的狀態或快取的產物被當成即時證據重複使用 |

## Common Failure Patterns

### 1. Wrapper Regression

基礎 model 產出正確的答案，但 wrapper 層讓它變差。

**症狀：**
- Model 在 playground 或直接呼叫 API 時沒問題，放進你的 agent 就壞掉
- 加了新的 prompt 層，既有的行為退化
- Agent 聽起來很有自信，但自信地錯了
- 「上次更新之前明明是好的」

### 2. Memory Contamination

舊的話題透過歷史、記憶檢索或蒸餾，洩漏到新的對話裡。

**症狀：**
- Agent 提起不相關的過去話題
- 使用者的更正留不住（舊記憶覆蓋新的）
- 同一個 session 的產物以偽事實的形式重新進入
- 記憶無限成長，隨著時間降低回應品質

### 3. Tool Discipline Failure

工具在 prompt 裡宣告了，卻沒有在程式碼裡強制執行。Model 跳過它們，或是幻覺出執行結果。

**症狀：**
- Prompt 裡寫「Must use tool X」，但 model 沒呼叫它就回答
- 工具結果看起來正確，但其實從來沒真的執行過
- 不同的工具爭搶同一個職責
- Model 在不該用工具時用了，或是在必須用時跳過

### 4. Rendering/Transport Corruption

Agent 內部的答案是正確的，但平台層在傳遞過程中把它改壞了。

**症狀：**
- 日誌顯示答案正確，使用者看到的卻是壞掉的輸出
- Markdown 渲染、JSON 解析或串流片段弄壞了有效的回應
- 隱藏的 fallback agent 在交付之前悄悄換掉答案
- 終端機和 UI 的輸出不一樣

### 5. Hidden Agent Layers

默默的修復、重試、摘要或回想 agent，在沒有明確契約的情況下運行。

**症狀：**
- 輸出在內部產生和交付給使用者之間改變了
- 「Auto-fix」迴圈跑了使用者不知道的第二次 LLM 處理
- 多個 agent 在沒有協調的情況下修改同一份輸出
- 答案被看不見的層「修順」或「更正」

## Audit Workflow

### Phase 1: Scope

定義你要稽核什麼：

- **目標系統**：是哪個 agent 應用？
- **入口點**：使用者怎麼和它互動？
- **Model stack**：用哪些 LLM 和供應商？
- **症狀**：使用者回報了什麼？
- **時間區間**：什麼時候開始的？
- **要稽核的層**：12 層中哪些適用？

### Phase 2: Evidence Collection

從 codebase 蒐集證據：

- **原始碼**：agent 迴圈、工具路由器、記憶准入、prompt 組裝
- **日誌**：歷史 session 的追蹤、工具呼叫記錄
- **設定**：prompt 範本、工具 schema、供應商設定
- **記憶檔案**：SOP、知識庫、session 封存

用 `rg` 搜尋 anti-pattern：

```bash
# 只寫在 prompt 文字裡（不在程式碼裡）的工具要求
rg "must.*tool|必须.*工具|required.*call" --type md

# 沒有驗證的工具執行
rg "tool_call|toolCall|tool_use" --type py --type ts

# 主要 agent 迴圈之外隱藏的 LLM 呼叫
rg "completion|chat\.create|messages\.create|llm\.invoke"

# 沒有使用者更正優先權的記憶准入
rg "memory.*admit|long.*term.*update|persist.*memory" --type py --type ts

# 會額外執行 LLM 呼叫的 fallback 迴圈
rg "fallback|retry.*llm|repair.*prompt|re-?prompt" --type py --type ts

# 默默的輸出變異
rg "mutate|rewrite.*response|transform.*output|shap" --type py --type ts
```

### Phase 3: Failure Mapping

對每個發現，記錄：

- **症狀**：使用者看到什麼
- **機制**：wrapper 怎麼造成它
- **來源層**：12 層中的哪一層
- **根本原因**：最深層的原因
- **證據**：file:line 或 log:row 的參照
- **信心度**：0.0 到 1.0

### Phase 4: Fix Strategy

預設的修復順序（程式碼為先，不是 prompt 為先）：

1. **用程式碼把關工具要求**：在程式碼裡強制執行，不要只寫在 prompt 文字裡
2. **移除或縮小隱藏的修復 agent**：用契約讓 fallback 變明確
3. **減少 context 重複**：同樣的資訊同時經過 prompt + history + memory + distillation
4. **收緊記憶准入**：使用者更正 > agent 的斷言
5. **收緊蒸餾的觸發條件**：不該壓縮的東西就不要壓縮
6. **減少渲染變異**：直接穿透，不要轉換
7. **改成有型別的 JSON envelope**：內部流程用結構化資料，不要用自由格式的文字

## Severity Model

| 等級 | 意義 | 動作 |
|-------|---------|--------|
| `critical` | Agent 可能有信心地產出錯誤的營運行為 | 下次發布前修好 |
| `high` | Agent 經常降低正確性或穩定性 | 這個 sprint 修好 |
| `medium` | 正確性通常還在，但輸出脆弱或浪費 | 排進下個週期 |
| `low` | 大多是外觀或可維護性的問題 | 放 backlog |

## Output Format

依這個順序向使用者呈現發現：

1. **依嚴重程度排序的發現**（最關鍵的在前）
2. **架構診斷**（哪一層弄壞了什麼，為什麼）
3. **排好順序的修復計畫**（程式碼為先，不是 prompt 為先）

不要用稱讚或摘要開頭。如果系統壞了，就直接說。

## Quick Diagnostic Questions

稽核 agent 系統時，回答這些問題：

| # | 問題 | 如果是 → |
|---|----------|----------|
| 1 | Model 能不能跳過必要的工具還照樣回答？ | 工具沒有被程式碼把關 |
| 2 | 舊的對話內容會不會出現在新的回合？ | 記憶污染 |
| 3 | 同樣的資訊是不是同時在 system prompt、記憶和 history 裡？ | Context 重複 |
| 4 | 平台在交付之前會不會跑第二次 LLM 處理？ | 隱藏的修復迴圈 |
| 5 | 輸出在內部產生和交付給使用者之間有沒有不同？ | 渲染損壞 |
| 6 | 「must use tool X」的規則是不是只在 prompt 文字裡？ | 工具紀律失敗 |
| 7 | Agent 自己的獨白會不會變成持久記憶？ | 記憶中毒 |

## Anti-Patterns to Avoid

- 在證偽 wrapper 層的退化之前，不要先怪 model。
- 沒有展示污染路徑，就不要怪記憶。
- 不要讓目前乾淨的狀態，抹掉一次髒的歷史事件。
- 不要把 markdown 文字當成可信的內部協定。
- 當程式碼從沒強制執行時，不要接受 prompt 文字裡的「must use tool」。
- 發現要直接、有證據支持，而且依嚴重程度排序。

## Report Schema

稽核應該產出符合這個形狀的結構化報告：

```json
{
  "schema_version": "ecc.agent-architecture-audit.report.v1",
  "executive_verdict": {
    "overall_health": "high_risk",
    "primary_failure_mode": "string",
    "most_urgent_fix": "string"
  },
  "scope": {
    "target_name": "string",
    "model_stack": ["string"],
    "layers_to_audit": ["string"]
  },
  "findings": [
    {
      "severity": "critical|high|medium|low",
      "title": "string",
      "mechanism": "string",
      "source_layer": "string",
      "root_cause": "string",
      "evidence_refs": ["file:line"],
      "confidence": 0.0,
      "recommended_fix": "string"
    }
  ],
  "ordered_fix_plan": [
    { "order": 1, "goal": "string", "why_now": "string", "expected_effect": "string" }
  ]
}
```

## Related Skills

- `agent-introspection-debugging`：除錯 agent 執行期的失敗（迴圈、逾時、狀態錯誤）
- `agent-eval`：正面對決式地 benchmark agent 效能
- `security-review`：程式碼和設定的資安稽核
- `autonomous-agent-harness`：設定自主 agent 的運作
- `agent-harness-construction`：從零開始建構 agent harness
