---
name: token-budget-advisor
description: 回答之前，先提供回應深度的選項（25%/50%/75%/100%）並附上 token 估計，再依選擇的層級回答。當使用者想控制回應長度或 token 預算時使用，例如 'token budget'、'short version'、'brief answer'、'respuesta corta vs larga'、'cuántos tokens'、'ahorrar tokens'、'responde al 50%'、'dame la versión corta'、'quiero controlar cuánto usas'。如果這個 session 已經設定過深度，或「token」指的是認證/付款 token，就跳過。
metadata:
  origin: community
---

# Token Budget Advisor (TBA)

攔截回應流程，在 Claude 回答**之前**，讓使用者選擇回應的深度。

## 何時使用

- 使用者想控制回應要多長或多詳細
- 使用者提到 token、預算、深度或回應長度
- 使用者說「short version」、「tldr」、「brief」、「al 25%」、「exhaustive」等等
- 任何使用者想事先選擇深度/細節層級的時候

**不要觸發**的情況：使用者在這個 session 已經設定過層級（默默維持它），或答案簡單到只有一行。

## 運作方式

### 步驟 1：估計輸入的 token

用 repo 標準的 context-budget 啟發式，在心裡估計 prompt 的 token 數。

使用跟 [context-budget](../context-budget/SKILL.md) 相同的校準指引：

- 純文字：`words × 1.3`
- 程式碼為主，或混合/程式碼區塊：`chars / 4`

混合內容就用佔多數的內容類型，並維持這是啟發式的估計。

### 步驟 2：依複雜度估計回應大小

先把 prompt 分類，再套用倍數範圍，得到完整的回應區間：

| 複雜度   | 倍數範圍 | 範例 prompt                                      |
|--------------|------------------|------------------------------------------------------|
| Simple       | 3× – 8×          | "What is X?"、是非題、單一事實                   |
| Medium       | 8× – 20×         | "How does X work?"                                  |
| Medium-High  | 10× – 25×        | 附帶 context 的程式碼請求                           |
| Complex      | 15× – 40×        | 多部分的分析、比較、架構      |
| Creative     | 10× – 30×        | 故事、文章、敘事寫作                  |

回應區間 = `input_tokens × mult_min` 到 `input_tokens × mult_max`（但不要超過你模型設定的輸出 token 上限）。

### 步驟 3：呈現深度選項

在回答**之前**呈現這個區塊，使用實際估計出來的數字：

```
Analyzing your prompt...

Input: ~[N] tokens  |  Type: [type]  |  Complexity: [level]  |  Language: [lang]

Choose your depth level:

[1] Essential   (25%)  ->  ~[tokens]   Direct answer only, no preamble
[2] Moderate    (50%)  ->  ~[tokens]   Answer + context + 1 example
[3] Detailed    (75%)  ->  ~[tokens]   Full answer with alternatives
[4] Exhaustive (100%)  ->  ~[tokens]   Everything, no limits

Which level? (1-4 or say "25% depth", "50% depth", "75% depth", "100% depth")

Precision: heuristic estimate ~85-90% accuracy (±15%).
```

各層級的 token 估計（在回應區間之內）：
- 25%  → `min + (max - min) × 0.25`
- 50%  → `min + (max - min) × 0.50`
- 75%  → `min + (max - min) × 0.75`
- 100% → `max`

### 步驟 4：依選擇的層級回應

| 層級            | 目標長度       | 包含                                             | 省略                                              |
|------------------|---------------------|-----------------------------------------------------|---------------------------------------------------|
| 25% Essential    | 最多 2-4 句   | 直接的答案、關鍵結論                       | Context、範例、細微差異、替代方案           |
| 50% Moderate     | 1-3 段      | 答案 + 必要的 context + 1 個範例              | 深入分析、邊界情況、參考資料             |
| 75% Detailed     | 結構化的回應 | 多個範例、優缺點、替代方案          | 極端的邊界情況、窮盡的參考資料         |
| 100% Exhaustive  | 不設限      | 全部：完整分析、所有程式碼、所有觀點 | 沒有                                        |

## 捷徑：跳過提問

如果使用者已經表明層級，就直接用那個層級回應，不用問：

| 他們說的話                                      | 層級 |
|----------------------------------------------------|-------|
| "1" / "25% depth" / "short version" / "brief answer" / "tldr"  | 25%   |
| "2" / "50% depth" / "moderate depth" / "balanced answer"        | 50%   |
| "3" / "75% depth" / "detailed answer" / "thorough answer"       | 75%   |
| "4" / "100% depth" / "exhaustive answer" / "full deep dive"     | 100%  |

如果使用者在 session 稍早設定過層級，後續的回應要**默默維持它**，除非他們改變。

## 精確度說明

這個 skill 使用啟發式估計，沒有真正的 tokenizer。準確度約 85-90%，變異 ±15%。一定要顯示免責聲明。

## 範例

### 會觸發

- "Give me the short version first."
- "How many tokens will your answer use?"
- "Respond at 50% depth."
- "I want the exhaustive answer, not the summary."
- "Dame la version corta y luego la detallada."

### 不會觸發

- "What is a JWT token?"
- "The checkout flow uses a payment token."
- "Is this normal?"
- "Complete the refactor."
- 使用者已經為這個 session 選好深度之後的後續問題

## 來源

獨立的 skill，來自 [TBA — Token Budget Advisor for Claude Code](https://github.com/Xabilimon1/Token-Budget-Advisor-Claude-Code-)。
原專案還附了一個 Python 估計器 script，但這個 repo 讓這個 skill 保持自成一體，而且只用啟發式。
