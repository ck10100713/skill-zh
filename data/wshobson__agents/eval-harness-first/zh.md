---
name: eval-harness-first
description: 建立能擋在每次 fine-tuning 之前的評估 harness，包含 golden 集、針對各失敗模式的 grader、judge 校準與 base-model baseline。適用於開始 fine-tuning 工作、把 trace 轉成 eval 集，或拿人工標註校準 judge 的時候。
---

# Eval Harness First

整個 plugin 的 Phase 0 關卡：`finetuning-method-selection` 和每一個下游 skill，都假設在寫訓練 config 之前，這個 harness 已經存在。這個 harness 不是跑完才附帶產生的東西，它是資料整理的引擎。用來建立 golden 的那批標註 trace，扣掉明確留出的 holdout 之後，就是訓練資料。

**輸入：** 如果有 production/agent trace 就用它，沒有就用任務規格，另外要有願意標註 ≥100 筆範例的標註者。
**輸出格式：** 下面的 `eval/` 目錄，包含 golden、grader、drift suite，以及後續階段要拿來當關卡的 base-model baseline。

## 關卡

沒有 eval harness，就不准 fine-tune。直接跳去寫訓練 config 的話，沒有東西可以量測、沒有東西能抓 regression，也沒有標註資料可以拿來訓練。整個飛輪是這樣轉的：

1. **蒐集 trace**：production/agent 的 span，如果還沒有就用合成任務。
2. **錯誤分析**：對 ≥100 筆 trace 做 open coding，再用 axial coding 歸成 4–8 個失敗 bucket。
3. **每個 bucket 一個 grader**：先用 deterministic 的；只有真正主觀的標準才用校準過的 LLM-judge。
4. **依優先順序排序**：頻率 × 嚴重度 × 價值。
5. **標註過的 trace 餵給資料整理，扣掉明確的 holdout。** 每個 `eval/goldens.jsonl` 的 ID，都要依 ID 從訓練資料中排除。
6. **訓練。**
7. **對 checkpoint 重跑同一個 harness**，不是換一個比較寬鬆的。
8. **Drift detection 回饋到步驟 2**：production 出現新的失敗模式，就重新開啟錯誤分析。

步驟 2–4 是在建 harness；步驟 5–8 說明了為什麼它必須先存在，因為它既是訓練資料的來源，也是 checkpoint 的出關閘門。

## 建立 Golden

- **有 trace 的時候，從 trace 來：** 做錯誤分析。先對 ≥100 筆真實 trace 做 open coding（去讀、用你自己的話標記失敗，還不要有固定分類），再用 axial coding 把這些標記收斂成 4–8 個有命名的失敗 bucket。少於 4 個，代表編碼做得太淺；多於 8 個，代表 bucket 需要合併。**例外：** 只有單一失敗面的任務（例如嚴格 schema 的抽取），可以只有 1–2 個 bucket，在一個 grader 裡面用各欄位的子指標，不要在沒有證據的情況下硬做人工切分。
- **還沒有 trace 的時候，用合成資料：** 以維度為基礎的生成，先列出重要的軸（任務類型、難度、邊界案例、persona），再對交叉乘積取樣；自由生成的 prompt 會集中在最容易寫的那幾類。
- **Golden 要像程式碼一樣做版本控制**：commit `eval/goldens.jsonl`、在 review 時看 diff、每次 release 打 tag。它同時也是 CI 的 regression 測試集。

## Grader

error analysis 得出的每個失敗 bucket 各配一個 grader，不是整個 eval 集只用一個。單一的混合分數會藏住是哪個 bucket 退步了。

- **先用 deterministic 的。** Regex、schema 驗證或執行檢查，比較便宜、可重現，而且不需要校準。
- **只有真正主觀的標準才用 LLM-judge**，例如語氣、忠實度、「哪個回應比較好」這類沒有 deterministic 檢查能表達的東西。
- **用二元的 pass/fail，不要用 Likert。** 1–5 或 1–10 的量表，校準起來雜訊比較大，也比較難一致地套用；收斂成 pass/fail。
- **Drift suite 的 MMLU 風格計分：優先用 logprob，不要用 generate-and-extract。** token 預算很緊的時候，generate-and-extract 對會先講一堆開場白的模型來說很容易 parse 失敗，把格式遵守度和被量測的知識混在一起。四種 grader 的範本和這個計分說明都在：`references/grader-templates.md`。

## Judge 校準是前提

任何交給 LLM-judge 的 bucket，在它的判決能算數（而不只是拿來探索）之前都需要校準，這是硬性前提，不是加分項。**沒有任何 bucket 交給 judge 的時候就不適用（N/A）**，全部都是 deterministic 的 harness 沒有東西需要校準，要把這點講清楚，不要讓這一節沒交代。

- 標註 ≥100 筆，切成 **train**/**dev**/**sealed test**（只報告一次，之後不准再碰）。
- 回報 **TPR 和 TNR**，不要只給一個混合的準確率數字，因為 judge 在偏斜的資料集上，只要一直說「pass」就能拿到 90%。
- **把 judge 釘在固定的模型 snapshot**，judge 模型一換就重新校準，不管怎樣每季也要校準一次。
- **Judge 必須來自和受測模型不同的模型家族。**
- 沒達到約定的 TPR/TNR 門檻的 judge，只能**作為參考**：標記出來給人工 review，絕對不能當作 promotion 的關卡。完整的流程、bias 修正和重新校準檢查表：`references/judge-calibration.md`。

## Baseline

在 Phase 1（方法選擇）開始之前，先對沒有修改過的 base model 跑完整個 harness，也就是 golden 加上 capability-drift suite。這個數字就是之後每個 checkpoint 要拿來比較的對象。

`eval/baseline-<model>.json` 就是關卡的憑證。沒有 baseline 檔案，`checkpoint-promotion` 就沒有比較的依據，一個對著沒量測過的東西「看起來比較好」的 checkpoint，不算是發現。

## 目錄規範

```
eval/
├── goldens.jsonl          # 標註過的 trace + 合成 golden，有版本控制
├── graders/                # 每個失敗 bucket 一個模組
│   ├── schema_compliance.py
│   ├── exact_match.py
│   └── rubric_judge.py
├── drift-suite.yaml        # 凍結的 benchmark + 200-500 筆相近領域的項目
└── baseline-<model>.json   # 關卡憑證：harness + drift suite 對 base model 的結果
runs/
└── <run-id>/
    └── results.json         # 每次執行的 harness 輸出，每個 checkpoint 一份
```

`eval/` 會跨執行保留，而且放在 `runs/` 外面，它是固定的量尺，不是某次執行的產物。`runs/` 是用完即丟的，`eval/` 不是。絕對不准讓執行腳本寫進 `eval/`。**標準位置：** 每份針對個別 trace 的 `results.json`，包含 Phase 0 的 baseline，都放在 `runs/<run-id>/results.json`，絕對不放在 `eval/runs/...` 底下；要求放後者的指示是錯的，不是這份規範有問題。

### Phase 0 離場檢查表

進入 `finetuning-method-selection` 之前，先確認：

1. ≥100 筆 trace 已做 open coding；4–8 個失敗 bucket（單一失敗面任務的合成 golden 不適用這個下限，見 Building Goldens 的例外；這時 bucket 數量改由 baseline 之後的錯誤分析決定）。
2. `eval/goldens.jsonl` 已 commit 並做版本控制。
3. 每個 bucket 一個 grader，先用 deterministic 的。
4. Judge 已校準：TPR/TNR、snapshot 已釘住、不同模型家族（**沒有 bucket 交給 LLM-judge 時不適用**，要明確寫出來）。
5. `eval/drift-suite.yaml` 已凍結。
6. `eval/baseline-<model>.json` 已寫入。

六項裡缺任何一項（或它明確標的 N/A）？那就不算 Phase 0 完成，`/finetune` 在每次執行前都會檢查 baseline 檔案。

## 相關 Skill

通用的評估指引（dashboard、A/B 測試、非 fine-tuning 的 harness）放在 `llm-application-dev` plugin 的 `llm-evaluation` skill，這個 skill 只涵蓋和 fine-tuning 耦合的部分：可兼作訓練資料的 golden，以及作為 checkpoint 關卡的 baseline。

- `finetuning-method-selection`：最先導到這裡。
- `dataset-curation`：把這些 trace 整理成訓練資料列。
- `trace-to-training-data`：把評分過的 trace 轉成訓練範例。
- `checkpoint-promotion`：使用 `baseline-<model>.json`，對每個候選 checkpoint 重跑這個 harness。

## 參考資料

- `references/grader-templates.md`：每種形狀可執行的 grader 範例，加上 `drift-suite.yaml` 範例和 MMLU logprob 計分說明。
- `references/judge-calibration.md`：校準流程，包含全部都是 deterministic 時的 N/A 路徑。
