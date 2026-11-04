---
name: checkpoint-promotion
description: 在 promote 之前，用 drift budget、成對比較和遺忘檢查，把關 fine-tune 出來的 checkpoint。訓練跑完產出 checkpoint 之後、判斷調整後的模型要不要上線時，或已 promote 的模型需要對更新後的 golden 重新把關時使用。
---

# Checkpoint Promotion

整個 plugin 的 Phase 5 關卡：一個訓練得很順利、task 指標也贏過基準的 checkpoint，沒有通過下面四個階段，仍然不能上線。`eval-harness-first` 建好了這裡要重跑的 suite，這個 skill 就是用那個 suite 的 baseline 來做決定的地方。

**輸入：** 一個訓練好的 checkpoint、`eval-harness-first` 產生的 `eval/baseline-<model>.json`，以及凍結的 `eval/drift-suite.yaml`。
**輸出格式：** `promotion-report.md`，包含四個階段的證據，以及最後的 `PROMOTE` 或 `REJECT` 結論，`/finetune` 的 Phase 5 和 `/promote-checkpoint` 會直接使用這個結論。

## 四階段關卡

每個階段都把關下一個階段：階段 2 失敗，階段 3 就不會跑。階段 2 和 3 共用一次昂貴的推論 pass，所以在**確定性（deterministic）**的 arena 上，可以讓它們同時執行，到做出結論時再套用關卡順序（序列化也省不了什麼）；以 judge 為基礎的 arena 仍然應該先等階段 2，那裡才是真正省下成本的地方。

1. **資料品質關卡。** 在任何評估碰到 checkpoint 之前：把訓練集去重、檢查是否有 eval golden 洩漏（這正是 `trace-to-training-data` 的 Hygiene 章節要預防的失敗），並掃描標籤雜訊。用洩漏的 golden 訓練出來的 checkpoint，會讓後面每個階段都失效。
2. **Held-out + 凍結的能力漂移 suite。** 對 checkpoint 重新跑 `eval-harness-first` 的 `eval/drift-suite.yaml`（MMLU/GSM8K/IFEval 加上 200 到 500 個領域相鄰的題目），並逐個 benchmark 跟 `baseline-<model>.json` 比對，對照下面的 Drift Budget 表。
3. **跟 base 的成對 arena。** 位置隨機化的 judge，checkpoint 對 base model，同樣的 prompt。或者，當 harness 裡每個評分器都是確定性的（沒有 LLM judge，位置隨機化不適用）時，使用 `references/gate-templates.md` 裡確定性的成對比較變體。**在 holdout 上贏、卻輸掉即時 arena 的，不能上線**：階段 2 的數字和階段 3 的判斷必須一致；在凍結的 golden 上贏、成對比較卻輸，是真實的訊號，不是要想辦法解釋掉的差異。
4. **Canary。** 任何要進到正式流量的 checkpoint，都要做 5 到 10% 分層抽樣的 rollout，並帶自動 rollback。**只在本機使用的人，到階段 3 就停止**：本機部署跳過階段 4，是正確的停止點，不是走捷徑。

### Drift Budget

| Drift（百分點） | 結論 |
|---|---|
| ≤1 | 雜訊，繼續 |
| 2–5 | 決定之前，先用不同的 seed 重跑 |
| >5 | **HARD FAIL**，不因 task 的進步而例外 |

不管其他列怎麼說，>5 個百分點那一列都優先生效：一個在目標 task 上進步 8 分、卻掉了 6 分通用能力的 checkpoint，在這裡仍然是失敗，task 的進步永遠買不回違反 drift budget 的代價。

**題目數量來自預算，不是來自方便：** 要讓半寬度小於 5 個百分點 hard-fail 門檻的一半，嚴格的 n 在典型準確率（p≈0.7）下約是 1,300；n=200 是務實的下限（同樣的 p 下半寬度約 ±6 個百分點，n=50 則是 ±13 個百分點）。每個結論都要回報半寬度，而且當差距小於半寬度時，要當成 `REJECT (uncertain)`，不是 PASS/HARD FAIL。完整的算式和一個跑了 5 次的警示範例見：`references/gate-templates.md`。

**RERUN 不是結論。** 2 到 5 個百分點的 drift，必須在不同 seed 的重跑完成之後，才會產生 `PROMOTE` 或 `REJECT`：`PROMOTE` 要求回到 ≤1 個百分點（雜訊）；任何重跑後仍然 >1 個百分點的情況，不論是在 2 到 5 的區間還是 >5 的違規，階段 2 都會判成硬性的 `REJECT`。任何報告在到達 Verdict 區段時，階段 2 都不能還顯示 `RERUN`。

## 災難性遺忘

沒有管理的 LoRA fine-tuning 會喪失真正的通用能力，而階段 2 就是用來抓這個的：

- **沒管理時約損失 43% 的知識**：沒有 replay、沒有 regularization。
- **有基本管理時約 10%**：有一些 replay 或保守的 LR。
- **replay + EWC 時約 3%**：有紀律的情況。
- **10 到 30% 的通用資料 replay 混合是標準的緩解方式**：訓練時混入通用領域的資料，不要只用目標 task 的資料。

如果 checkpoint 在階段 2 碰到 >5 個百分點的 hard fail，依序走這個升級階梯，這是這個 skill 和 `references/gate-templates.md` 共同指向的唯一標準順序：

1. **調整 replay 混合的比例：用換的，不要用加的**（加上去會讓比例和總 optimizer step 數混在一起）。在小規模的執行（<~100 step）下，劑量不是單調的：任何調換之後都要重新檢查 drift。
2. **降低 learning rate。**
3. **減少 epoch。**
4. **更小的 LoRA rank**：就是 `lora-qlora-recipes` 和 `preference-optimization` 為訓練執行調整的同一組 rank/LR 槓桿，只是在這裡反向套用。

這個順序是預設，不是定律：**只靠一組前後對照的執行得到的補救建議，只是假設**：一旦任何槓桿造成反轉，就把它標成低信心，而且要偏向做不同 seed 的重複實驗，不要盲目相信下一階。如果某個槓桿解決了 drift 違規，卻讓某個成功標準指標掉到目標以下，這是要交給人去判斷的雙面取捨，不是繼續往階梯下面走的理由。這兩個但書背後完整的推理和 5 次執行的軌跡見：`references/gate-templates.md`。

**要揭露 drift suite 的指令重複使用。** 如果某一列 replay 複製了 drift harness 完全相同的指令措辭（不只是來源題目不重疊），那個 benchmark replay 之後的分數就只是上限：在把接近預算的通過當成乾淨之前，要標示它對指令熟悉，或是用改寫過的說法重新探測。

## 結論

`promotion-report.md` 要把四個階段都當成區段涵蓋，而且**必須以最終結論結尾：`PROMOTE` 或 `REJECT`**，附上產生這個結論的證據，以及當結論是 `REJECT` 時，恰好一個最優先的補救建議。範本：`references/gate-templates.md`。其他 skill 會解析的最終格式：

```
## Verdict

REJECT

Evidence: domain-adjacent drift
suite dropped 6.2pt (threshold:
>5pt hard fail) despite +8pt on
the target task.

Top remediation: swap the
replay-mix fraction from 10%
toward 20%, holding step count
constant.
```

- **REJECT 是結果，不是錯誤。** 一個沒通過階段 2 的 drift budget 或階段 3 的 arena 比較的 checkpoint，已經做到它該做的事。不要把 REJECT 當成需要重跑這個 skill 的失敗；它是運作正常的關卡該有的正確輸出。
- **一個補救建議，不是一份選單。** 證據區段可以列出所有觀察到的東西；結論區段要依上面的升級階梯，指出單一槓桿最大的修法。一份在三種可能的修法之間猶豫不決的報告，沒有做到這個 skill 存在的目的：排出優先順序。
- **不自動重新訓練。** 這個 skill 產出的是結論和報告，不是重新觸發的訓練執行。`REJECT` 會把補救交還給人，在 `finetuning-method-selection` 或相關的訓練 skill 那裡做決定。

## 相關 Skill

- `eval-harness-first`：擁有這個 skill 重新執行並對照比較的 drift suite 和 baseline；沒有 `baseline-<model>.json`，就沒有東西可以拿來把關。
- `quantized-export`：`PROMOTE` 結論之後唯一有效的下一步。
- `preference-optimization` 和 `lora-qlora-recipes`：擁有災難性遺忘升級路徑中的 LR 和 rank 槓桿；這個 skill 診斷違規，那些 skill 擁有造成違規的設定。
- `dataset-curation`：擁有 replay 混合的建構做法，也就是升級階梯第一階所套用的。

完整的 `promotion-report.md` 範本，包含四個階段、drift suite 的評分表、成對 arena 的協定（題目數、位置隨機化、勝率門檻），以及 replay 混合的設定範例：`references/gate-templates.md`。
