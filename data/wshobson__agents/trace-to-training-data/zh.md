---
name: trace-to-training-data
description: 把評估 trace 和 production log 轉成 SFT 範例與偏好配對（preference pair）。已有評分過的 trace 或失敗範例、需要變成訓練資料時，對模型輸出做 rejection sampling 時，或要從通過與失敗的執行結果建立 DPO pair 時使用。
---

# Trace To Training Data

這個 skill 假設 `eval-harness-first` 已經替要在這裡轉換的 trace 評過分了：golden、grader 和 `runs/<run-id>/results.json` 在轉換開始前都已經存在。這就是那個 skill 在自己的流程裡提到的 flywheel 銜接點：「同一批標好的 trace 就變成訓練集」。轉換在這裡做，評分已經在上游做完了。

**Input：** 評過分的 trace，也就是 `eval/goldens.jsonl` 加上 `runs/<run-id>/results.json`。每一列都有 `task_id`、grader 給的 `verdict`，任務支援純量分數（judge 分數、執行結果的部分得分，或 RLVR verifier）時還會有 `reward`：

```json
{"task_id": "t-042", "trace_id": "t-042-a3",
 "messages": [{"role": "user", "content": "..."}],
 "verdict": "pass", "reward": 0.91,
 "grader": "exact_match"}
```

**Output format：** 格式要跟 `dataset-curation` 的 Format Selection 表完全一樣，也就是 SFT 的 `messages` 列，或 DPO 的 `prompt`/`chosen`/`rejected` pair，這樣這個 skill 的輸出就是那個 skill 的輸入，中間不用再重塑。

## The Principle

標記的工作 eval harness 已經做完了：`results.json` 裡的每個 trace，在這個 skill 碰到之前就帶有 verdict，通常還有 reward。把評過分的 trace 轉成訓練資料列是機械式的工作：從 `dataset-curation` 的表裡挑一種格式、對應欄位、寫成 JSONL。**剩下要做的是篩選（curation）**：哪些 trace 達到品質門檻、哪些 pair 有資訊量、哪些資料列絕對不能進訓練集。

如果某個轉換步驟需要重新判斷一個 trace，那表示 harness 少了 grader，不是這個 skill 該去硬補的缺口。沒有 verdict 或 reward 的 trace 還不能轉換，先退回 `eval-harness-first`，不要為了讓轉換往下走就在這裡手動標。

## SFT From Traces

- **只留成功軌跡中 reward 最高的那一部分**，不是每個通過的都留。把通過的 trace 依 reward 排序，取前面一部分（Agent-lightning 的做法），不要把每個剛好過門檻的 trace 都收進來。勉強過關的 trace，SFT 訊號比分數遠高於門檻的弱。
- **經專家修正的失敗案例直接成為 gold SFT 範例**（Langfuse 的做法）：當人類把失敗 trace 的輸出改成正確版本，這個修正不需要 reward 門檻，因為人已經驗證過了。修正結果直接進 SFT 集。
- **多步驟 trace 用 step 層級的 masking，比整條軌跡丟掉更好。** 多步驟軌跡裡只有部分步驟有問題時，把壞步驟的 loss mask 掉、保留好的步驟，不要整條軌跡丟掉。SRFT 回報在 SWE-bench 上，step 層級的 critic masking 是 32.2%，整條軌跡丟棄是 30.9%，切得更細確實有差距，雖然不大。

## Preference Pairs From Traces

- **用同一個任務**上通過與失敗的軌跡來建 pair，絕對不要從不同任務中隨便抓最高分和最低分的 trace 湊在一起。跨任務的 pair 會教模型偏好某個任務，而不是偏好某個回應。
- **rejected 的那一筆，挑該任務 reward 分布的 μ−2σ 位置，絕對不要挑絕對最小值。** 完整的挑選公式在 `preference-optimization` 的 Pair Construction 章節；這個 skill 負責提供它要吃的、評過分的軌跡。
- **用 judge 分數差來挑 pair，可以減少 pair 數量又不減訊號。** 每個候選 pair 用 chosen 減 rejected 的 judge 分數差來打分，只留差距最大的那一群：16.5k 候選裡的前 5k，下游結果跟整個候選池相當。要先建完整的候選集，再用分數差篩選，不要一開始就把生成上限設在 5k。

## Hygiene

- **任何資料列出貨前都要掃描機密和 PII，找到就遮蔽。** 從 production log 來的 trace 可能帶有憑證、API key、token 或客戶資料：對每一筆 SFT 和 DPO 資料列跑機密/PII 掃描並遮蔽命中的內容；遮蔽後如果敏感欄位還在，轉換就要 fail closed（這筆資料丟掉，不帶著原始內容出貨）。絕對不要 commit 機密。
- **Eval golden 絕對不能洩漏到訓練資料。** 每一個 `eval/goldens.jsonl` 的 ID 都要從所有轉換出來的 SFT 和 DPO 集中排除：同時也是 golden 的 trace 會讓模型去訓練之後要拿來評分的那個題目，悄悄把之後每一次 eval 的成績灌水。
- **對照既有訓練集去重**，不能只在新轉出來的資料列之間去重：用精確比對或 embedding 相似度，配合 `dataset-curation` 的 dedup method 欄位，在這批資料併進去之前，先跟現有的訓練資料比過。
- **來源紀錄（provenance）要寫進 dataset card。** 每一筆轉換出來的資料列都要能追溯到它的來源 `run_id` 和 `trace_id`：`dataset-curation` 的 Provenance 欄位檢查的，正是這條回到 `trace-to-training-data` 輸出的連結；找不到來源的資料列還不能併入。

## Related Skills

- `eval-harness-first` — 產出這個 skill 要轉換的、評過分的 trace；沒有 verdict 或 reward 的 trace 還不能轉換，轉換前先退回那邊。
- `dataset-curation` — 負責目標格式和 dataset card，這個 skill 的來源紀錄資料會餵進去；轉換出來的資料列必須和它的 Format Selection 表欄位名稱完全一致，不是差不多就好。
- `preference-optimization` — 使用這個 skill 建好的 DPO pair，並負責上面提到的完整 μ−2σ rejected 挑選公式。

把 JSONL 轉成 JSONL 的完整範例，包括評過分的 trace 轉成 SFT 列、trace pair 轉成 DPO pair、修正轉成 SFT 列、rejection sampling 迴圈，以及 golden holdout 檢查，都放在 `references/conversion-recipes.md`。
