---
name: evaluation-methodology
description: "PluginEval quality methodology, covering dimensions, rubrics, and scoring formulas. Use this skill when understanding how plugin quality is measured, when interpreting a low score on a specific dimension, when deciding how to improve a skill's triggering accuracy or orchestration fitness, when setting score thresholds for your marketplace, or when explaining quality badges to external partners like Neon."
---

# 評估方法論

PluginEval 結合最多三層，替 skill 或 plugin 打 0 到 100 分。Static 層是 lint，速度快又具確定性，適合用來檢查結構。LLM judge 層和 Monte Carlo 層是實驗性質，沒有拿人工標註驗證過，所以它們的數字只能當作粗略的訊號。以 trace 為基礎的 eval 計畫，請看 repo 根目錄的 `evals/README.md`。

Judge rubric 的錨點在 [references/rubrics.md](references/rubrics.md)。每個 anti-pattern 的修法和每個維度的提升技巧，在 [references/improving-scores.md](references/improving-scores.md)。

## 評估深度

| 深度 | 層 | 信心標籤 |
|---|---|---|
| `quick` | static | Estimated |
| `standard`（`score` 的預設） | static 與 judge | Assessed |
| `deep`（`certify` 使用） | static、judge，以及跑 50 次的 Monte Carlo | Certified |
| `thorough` | static、judge，以及跑 100 次的 Monte Carlo | Certified+ |

這個標籤代表實際跑了哪個深度，不代表有跟人工判斷對照過。Plugin 目錄不管你要求哪個深度，都只會跑 static 層。

## Static 層（lint）

Static 層讀取 SKILL.md，不呼叫任何模型。它計算七個子分數，前六個會餵進複合維度：

- `frontmatter_quality`（餵進 `triggering_accuracy`）
- `orchestration_wiring`（餵進 `orchestration_fitness`）
- `progressive_disclosure`, `structural_completeness`, `token_efficiency`, `ecosystem_coherence`
- `harness_portability`

`harness_portability` 不對應任何維度，所以不會改變 skill 的複合分數。不過它占 static 層自身分數的 6%。Plugin 的分數是由這層分數算出來的，所以 portability 的發現可能會稍微拉低 plugin 的分數。它的發現不會被算作 anti-pattern。

Static 層會標出六種 anti-pattern：`OVER_CONSTRAINED`、`EMPTY_DESCRIPTION`、`MISSING_TRIGGER`、`BLOATED_SKILL`、`ORPHAN_REFERENCE` 和 `DEAD_CROSS_REF`。每個標記會讓分數扣 5%，最低扣到 50% 為止：

```text
penalty = max(0.5, 1.0 - 0.05 * anti_pattern_count)
```

報告會為每個標記印出嚴重程度，但扣分只算標記的數量，不看嚴重程度。

## LLM judge 層（實驗性質）

Judge 層會呼叫模型四次，回傳四個 0 到 1 的整體分數：

- `triggering_accuracy`：Haiku 讀 description 並寫 10 個測試 prompt，5 個應該觸發、5 個不應該。它預測每個 prompt 的結果，並回報自己算出的 F1。沒有任何東西會拿這些預測去對照真實的觸發情況。
- `orchestration_fitness` 和 `scope_calibration`：Sonnet 用五級的 rubric 替 skill 評分。
- `output_quality`：Sonnet 想像三個任務，並評估它預期會得到的輸出。

這三次 Sonnet 呼叫只看得到 SKILL.md 的前 3,000 個字元。只會跑一個 judge，因為沒有任何東西會讀 `judges` 設定。

## Monte Carlo 層（實驗性質）

Haiku 寫 15 個應該觸發這個 skill 的 prompt，這一層重複使用它們，湊到 50 次執行（`thorough` 是 100 次）。每次執行會把 SKILL.md 的文字和一個 prompt 送給模型，這一層記錄四個量測值：

- Activation rate 是有任何非空回覆的執行所占的比例，所以它顯示的是模型有沒有回答，不是 skill 該不該被觸發。
- Output quality 是回覆長度除以 500，上限 1.0。
- Failure rate 是出錯的執行所占的比例。
- Token efficiency 是 `1 - median_tokens / 8000`。

每個 prompt 都是應該觸發的，所以這一層從來不會檢查 skill 有沒有在不相關的請求中保持安靜。這一層的 JSON 包含針對它自己量測值的 Wilson、bootstrap 和 Clopper-Pearson 區間。複合分數的 `ci_lower` 和 `ci_upper` 欄位永遠是 null。

## 複合分數

第一步，每個維度會把存在的各層分數混合起來，並把混合權重在這些層之間重新正規化。第二步，把加權後的維度分數加總，並把維度權重在有分數的維度之間重新正規化。第三步，把總和乘以 100，再乘以 anti-pattern 的扣分係數。

| 維度 | 權重 | Static | Judge | Monte Carlo |
|---|---|---|---|---|
| `triggering_accuracy` | 0.25 | 0.15 | 0.25 | 0.60 |
| `orchestration_fitness` | 0.20 | 0.10 | 0.70 | 無 |
| `output_quality` | 0.15 | 無 | 0.40 | 0.60 |
| `scope_calibration` | 0.12 | 無 | 0.55 | 無 |
| `progressive_disclosure` | 0.10 | 0.80 | 無 | 無 |
| `token_efficiency` | 0.06 | 0.40 | 無 | 0.50 |
| `robustness` | 0.05 | 無 | 無 | 0.80 |
| `structural_completeness` | 0.03 | 0.90 | 無 | 無 |
| `code_template_quality` | 0.02 | 無 | 無 | 無 |
| `ecosystem_coherence` | 0.02 | 0.85 | 無 | 無 |

某個格子寫「無」，代表那一層對該維度不產生分數，即使 `LAYER_BLENDS` 列了權重也一樣。沒有任何一層會產生 `code_template_quality`，所以它永遠是未量測。對 plugin 目錄來說，複合分數是 static 層在這個 plugin 所有 skill 和 agent 上的平均分數，乘以 100，再乘以 plugin 的 anti-pattern 數量對應的扣分係數。

## 徽章與等級

徽章只由複合分數決定。Platinum 要至少 90，Gold 至少 80，Silver 至少 70，Bronze 至少 60。`Badge.from_scores` 接受 Elo 評分，但沒有任何指令會算出 Elo。Plugin 層級的徽章，包含每週 CI 報告裡的那些，只來自 static 層。`standard` 深度以上的 skill 層級徽章，也會納入實驗性質的那幾層。

每個有量測的維度，會在 0 到 100 的量表上得到一個字母等級，從 97 的 A+ 一路到 60 的 D-，低於 60 就是 F。

## 用法

```bash
plugin-eval score ./path/to/skill --depth quick     # 只做 static lint
plugin-eval score ./path/to/skill                   # static 與 judge
plugin-eval certify ./path/to/skill                 # deep 深度
plugin-eval compare ./skill-a ./skill-b             # 預設為 quick 深度
plugin-eval score ./path/to/skill --depth quick --output json --threshold 70
```

在 `standard` 深度以上，`score`、`certify` 和 `compare` 會在 stderr 印出提示，說明 judge 層和 Monte Carlo 層是實驗性質。對 plugin 目錄，CLI 則改為印出警告，說明只會跑 static 層。有指定 `--threshold` 時，只要複合分數低於該值，指令就會以 exit code 1 結束。`plugin-eval init` 會寫出 corpus index，但沒有其他指令會讀它。
reads it.

## 範例

下面是 JSON 輸出的節錄範例。腳本可以從中讀取 `composite.score`：

```json
{
  "layers": [{"layer": "static", "score": 0.75, "sub_scores": {}, "anti_patterns": []}],
  "composite": {"score": 76.9, "ci_lower": null, "ci_upper": null, "badge": "silver",
                "confidence_label": "Estimated", "dimensions": []},
  "elo": null
}
```

## 疑難排解

- 加了內容之後分數下降的話，檢查 JSON 裡的 `layers[0].anti_patterns`。
- 如果 quick 深度下 `triggering_accuracy` 偏低，在 description 加上觸發用語，例如「Use this skill when」，後面接幾個以逗號分隔的使用情境。
- Judge 分數在每次執行之間會變動，因為模型每次都會寫新的測試 prompt 和任務。需要可重複比較的時候，請用 static 層。
- 如果 stderr 說 judge 無法量測某些維度，請用 `uv sync --extra llm` 安裝 LLM extra。

## 相關

`eval-judge` agent 在 Claude Code 內替四個 judge 維度評分，`eval-orchestrator` agent 則負責執行 CLI 並合併結果。
