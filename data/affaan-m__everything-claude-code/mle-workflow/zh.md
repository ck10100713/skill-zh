---
name: mle-workflow
description: 正式環境的機器學習工程流程，涵蓋 data contract、可重現的訓練、模型評估、deploy、監控和回滾。建置、審查或強化超出一次性 notebook 的 ML 系統時使用。
license: MIT
metadata:
  origin: ECC
---

# Machine Learning Engineering Workflow

用這個 skill 把模型的工作變成正式環境的 ML 系統：有明確的 data contract、可重複的訓練、可量測的品質關卡、可 deploy 的成品，以及營運監控。

## When to Activate

- 規劃或審查正式環境的 ML 功能、模型更新、排序系統、推薦系統、分類器、embedding 流程或預測 pipeline
- 把 notebook 程式碼轉成可重複使用的訓練、評估、批次推論或線上推論 pipeline
- 設計模型升級標準、離線/線上評估、實驗追蹤或回滾路徑
- 除錯由資料漂移、label 洩漏、過期特徵、成品不一致，或訓練與服務邏輯不一致造成的失敗
- 加入模型監控、canary 上線、shadow 流量或 deploy 後的品質檢查

## Scope Calibration

只用適合眼前這個系統的那幾條路線。這個 skill 適用於排序、搜尋、推薦、分類器、預測、embedding、LLM 流程、異常偵測和批次分析，但不應該把同一種架構硬套在它們身上。

- 不要假設每個模型都有監督式 label、線上服務、feature store、PyTorch、GPU、人工審查、A/B 測試或即時回饋。
- 如果有 data contract、baseline、評估腳本和回滾說明，就足以讓這個變更可被審查，就不要加沉重的 MLOps 機制。
- 專案缺少 label、延遲的結果、slice 定義、正式流量或監控負責人時，要把假設明確寫出來。
- 把範例當作可替換的鷹架。把指標、服務模式、資料儲存和上線機制，換成專案原生的對應物。

## Related Skills

- `python-patterns` 和 `python-testing`：Python 實作和 pytest 覆蓋
- `pytorch-patterns`：深度學習模型、data loader、裝置處理和訓練迴圈
- `eval-harness` 和 `ai-regression-testing`：升級關卡和 agent 輔助的回歸檢查
- `database-migrations`、`postgres-patterns` 和 `clickhouse-io`：資料儲存和分析介面
- `deployment-patterns`、`docker-patterns` 和 `security-review`：服務、機密、容器和正式環境強化

## Reuse the SWE Surface

不要把 MLE 當成和軟體工程分開的東西。大多數 ECC 的 SWE 流程可以直接套用在 ML 系統上，而且失敗模式往往更嚴格：

建議的 `minimal --with capability:machine-learning` 安裝方式，會讓核心 agent 介面和這個 skill 並存。對於只有 skill 或 agent 受限的 harness，如果目標支援 agent，就把 `skill:mle-workflow` 和 `agent:mle-reviewer` 搭配使用。

| SWE 介面 | MLE 用法 |
|-------------|---------|
| `product-capability` / `architecture-decision-records` | 把模型工作變成明確的產品合約，並記錄無法回頭的資料、模型和上線決定 |
| `repo-scan` / `codebase-onboarding` / `code-tour` | 在引入平行的 ML 堆疊之前，先找出既有的訓練、特徵、服務、評估和監控路徑 |
| `plan` / `feature-dev` | 把模型變更當成產品能力來界定範圍，分成資料、評估、服務和回滾幾個階段 |
| `tdd-workflow` / `python-testing` | 實作之前先測試特徵轉換、切分邏輯、指標計算、成品載入和推論 schema |
| `code-reviewer` / `mle-reviewer` | 審查程式碼品質，以及 ML 特有的洩漏、可重現性、升級和監控風險 |
| `build-fix` / `pr-test-analyzer` | 診斷壞掉的 CI、不穩定的評估、缺少的 fixture，以及特定環境的模型或相依性失敗 |
| `quality-gate` / `test-coverage` | 要求轉換、指標、推論合約、升級關卡和回滾行為都有自動化證據 |
| `eval-harness` / `verification-loop` | 把離線指標、slice 檢查、延遲預算和回滾演練變成可重複的關卡 |
| `ai-regression-testing` | 把每個正式環境的 bug 保存成回歸測試：缺特徵、過期 label、壞成品、schema 漂移或服務不一致 |
| `api-design` / `backend-patterns` | 設計預測 API、批次工作、idempotent 的重新訓練端點和回應 envelope |
| `database-migrations` / `postgres-patterns` / `clickhouse-io` | 為 label、特徵快照、預測紀錄、實驗指標和 drift 分析做版本管理 |
| `deployment-patterns` / `docker-patterns` | 把可重現的訓練和服務 image 打包起來，附健康檢查、資源限制和回滾 |
| `canary-watch` / `dashboard-builder` | 用模型版本、slice、drift、延遲、成本和延遲 label 的儀表板，讓上線健康度看得見 |
| `security-review` / `security-scan` | 檢查模型成品、notebook、prompt、資料集和紀錄裡有沒有機密、PII、不安全的反序列化和供應鏈風險 |
| `e2e-testing` / `browser-qa` / `accessibility` | 測試使用預測結果的關鍵產品流程，包括可解釋性和 fallback 的 UI 狀態 |
| `benchmark` / `performance-optimizer` | 量測吞吐量、p95 延遲、記憶體、GPU 使用率，以及每次預測或重新訓練的成本 |
| `cost-aware-llm-pipeline` / `token-budget-advisor` | 依品質、延遲和預算來分流 LLM/embedding 工作負載，而不是預設用最大的模型 |
| `documentation-lookup` / `search-first` | 寫程式前，先確認模型服務、feature store、向量資料庫和評估工具目前的函式庫行為 |
| `git-workflow` / `github-ops` / `opensource-pipeline` | 把 MLE 變更打包成可審查的形式：範圍清楚、排除產生的成品、有可重現的測試證據 |
| `strategic-compact` / `dmux-workflows` | 把長的 ML 工作拆成平行的軌道：data contract、評估 harness、服務路徑、監控和文件 |

## Ten MLE Task Simulations

規劃或審查 MLE 工作時，把這些模擬當作覆蓋度檢查。一個強的 MLE 流程，應該能把每個任務化簡成明確的合約、可重用的 SWE 介面、自動化的證據，以及可審查的成品。

| ID | 常見的 MLE 任務 | 精簡的 ECC 路徑 | 必要輸出 | 涵蓋的 pipeline 路線 |
|----|-----------------|----------------------|-----------------|------------------------|
| MLE-01 | 釐清模糊的預測、排序、推薦、分類、embedding 或預測能力 | `product-capability`、`plan`、`architecture-decision-records`、`mle-workflow` | Iteration Compact，寫明誰在乎、決策負責人、成功指標、不可接受的錯誤、假設、限制和第一個實驗 | 產品合約、利害關係人損失、風險、上線 |
| MLE-02 | 定義指標目標、label、資料來源和錯誤預算 | `repo-scan`、`database-reviewer`、`database-migrations`、`postgres-patterns`、`clickhouse-io` | 資料與指標合約，含實體粒度、label 時間、label 信心、特徵時間、point-in-time join、切分政策和資料集快照 | data contract、指標設計、洩漏、可重現性 |
| MLE-03 | 加複雜度之前，先建 baseline 模型和評分路徑 | `tdd-workflow`、`python-testing`、`python-patterns`、`code-reviewer` | Baseline 評分器，附 confusion matrix、校準說明、延遲/成本估計、已知弱點，以及針對分數形狀和確定性的測試 | baseline、評分、測試、服務一致性 |
| MLE-04 | 依「什麼能區分結果」的假設來產生特徵 | `python-patterns`、`pytorch-patterns`、`docker-patterns`、`deployment-patterns` | 特徵計畫和轉換模組，涵蓋訊號來源、缺值、離群值、相關性、洩漏檢查，以及訓練/服務一致 | 特徵 pipeline、洩漏、訓練、成品 |
| MLE-05 | 在取捨之下調整閾值、設定和模型複雜度 | `eval-harness`、`ai-regression-testing`、`quality-gate`、`test-coverage` | 閾值/設定報告，比較 precision、recall、F1、AUC、校準、分群 slice、延遲、成本、複雜度和可接受的錯誤類別 | 評估、閾值、升級、回歸 |
| MLE-06 | 做錯誤分析，把錯誤變成下一個實驗 | `eval-harness`、`ai-regression-testing`、`mle-reviewer`、`silent-failure-hunter` | 錯誤群集報告，涵蓋 false positive、false negative、模糊的 label、過期特徵、缺少的訊號和 bug 追蹤，並記下學到的教訓 | 錯誤分析、bug 追蹤、迭代、回歸 |
| MLE-07 | 把模型成品打包，供批次或線上推論使用 | `api-design`、`backend-patterns`、`security-review`、`security-scan` | 有版本的成品包，含前處理、設定、相依性限制、schema 驗證、安全載入和不含 PII 的紀錄 | 成品、安全、推論合約 |
| MLE-08 | 上線線上服務或批次評分，並收集回饋 | `api-design`、`backend-patterns`、`e2e-testing`、`browser-qa`、`accessibility` | 預測端點或批次工作，含回應 envelope、逾時、批次處理、fallback、模型版本、信心、回饋紀錄和產品流程測試 | 服務、批次推論、fallback、使用者流程 |
| MLE-09 | 用 shadow 流量、canary、A/B 測試或回滾來上線模型 | `canary-watch`、`dashboard-builder`、`verification-loop`、`performance-optimizer` | 上線計畫，寫明流量切分、儀表板、p95 延遲、成本、品質護欄、回滾成品和回滾觸發條件 | deploy、canary、回滾 |
| MLE-10 | 上線後營運、除錯並更新正式環境的模型 | `silent-failure-hunter`、`dashboard-builder`、`mle-reviewer`、`doc-updater`、`github-ops` | 觀察紀錄和更新計畫，含 drift 檢查、延遲 label 健康度、告警負責人、runbook 更新、重新訓練的標準和 PR 證據 | 監控、事件應變、重新訓練 |

## Iteration Compact

動模型程式碼之前，先把工作壓縮成一份可審查的成品。它要短到放得進 PR 描述，又精確到讓別的工程師可以質疑裡面的取捨。

```text
Goal:
Who cares:
Decision owner:
User or system action changed by the model:
Success metric:
Guardrail metrics:
Mistake budget:
Unacceptable mistakes:
Acceptable mistakes:
Assumptions:
Constraints:
Labels and data snapshot:
Baseline:
Candidate signals:
Threshold or config plan:
Eval slices:
Known risks:
Next experiment:
Rollback or fallback:
```

這份 compact 相當於 SWE 裡一份好的設計筆記。它避免團隊去最佳化一個沒人信任的指標、加了對不上真正錯誤模式的特徵，或是在沒有回滾方案的情況下把複雜度上線。

## Decision Brain

任務模糊、影響大或指標很重的時候，就跑這個迴圈：

1. 從決策出發，不要從模型出發。講出會改變下游行為的那個動作。
2. 講出誰在乎、為什麼。不同的利害關係人，對 false positive、false negative、延遲、運算花費、不透明或錯失機會，付出的成本不一樣。
3. 把模糊轉成假設。問什麼訊號能區分結果、什麼證據能推翻它，以及什麼簡單的 baseline 應該很難被超越。
4. 在發明客製系統之前，先研究前人做法或鄰近的已知問題。
5. 用 `(probability, confidence) x (cost, severity, importance, impact)` 替各選項打分數。
6. 考慮對抗行為、誘因、選擇性揭露、分布漂移和回饋迴圈。
7. 偏好能減少最重要錯誤的最簡單變更。簡單不是偷懶；它是在保住迭代速度的同時，把大失誤降到最低的方法。
8. 記下決策、證據、反方論點和下一個可回頭的步驟。

## Metric and Mistake Economics

依失敗的成本選指標，不要憑習慣：

- 儘早使用 confusion matrix，讓團隊討論具體的 false positive 和 false negative，而不是抽象的 accuracy。
- 錯誤的正向決策成本最高時，偏重 precision。
- 漏掉正例的成本最高時，偏重 recall。
- 只有在 precision/recall 的取捨真的平衡又說得清楚時，才用 F1。
- 排序品質比單一閾值更重要時，用 AUC 或排序指標。
- 把延遲、吞吐量、記憶體和成本當成一等指標來追蹤，因為它們決定了可行的模型複雜度。
- 慶祝離線進步之前，先和 baseline 以及目前正式環境的模型比較。
- 把真實世界的回饋訊號當作有偏差、有延遲、有覆蓋缺口的延遲 label；沒分析過，就不要當成基準真相。

每個指標選擇都要說明：它讓哪種錯誤變便宜、讓哪種錯誤更可能發生，以及誰來承擔那個成本。

## Data and Feature Hypotheses

特徵應該來自一套「為什麼能區分」的理論：

- 文字、類別欄位、數值歷史、圖關係、近期性、頻率和聚合值，是候選的訊號家族，不是自動就能當特徵。
- 每個特徵家族都要說明為什麼它該能區分結果，以及它可能怎麼洩漏未來資訊。
- label 有雜訊時，考慮仲裁、label 信心、soft target 或信心加權。
- 類別不平衡時，比較加權損失、重新取樣、閾值移動和校準過的決策規則。
- 有缺值時，判斷「缺少」本身是否帶有資訊、能不能補值，或是該棄權的理由。
- 有離群值時，判斷該截斷、分桶、調查，還是當作罕見但重要的訊號保留下來。
- 特徵之間有相關時，檢查它們是冗餘、不穩定，還是用來代理拿不到的未來狀態。

錯誤分析還沒顯示 baseline 是因為額外訊號或容量能合理修好的原因而失敗，就不要增加模型複雜度。

## Error Analysis Loop

每次 baseline、訓練、閾值變更或設定變更之後：

1. 把錯誤分成 false positive、false negative、棄權、低信心案例和系統失敗。
2. 依共同特徵把錯誤分群：語言、實體類型、來源、時間、地區、裝置、稀疏度、近期性、特徵新鮮度、label 來源或模型版本。
3. 把模型的錯誤，和資料 bug、label 模糊、產品需求模糊、埋點缺口、服務不一致分開。
4. 把每個主要的群集追到四個動作之一：更好的 label、更好的特徵、更好的閾值/設定，或更好的產品 fallback。
5. 把每個重要的錯誤保存成回歸測試、評估 slice、儀表板面板或 runbook 條目。
6. 把下一次迭代寫成可證偽的實驗，不要寫成模糊的「改善模型」任務。

最強的 MLE 迴圈不是訓練 -> 指標 -> 上線，而是錯誤 -> 分群 -> 假設 -> 實驗 -> 證據 -> 更簡單的系統。

## Observation Ledger

在程式碼、PR、實驗報告或 runbook 旁邊，留一份精簡的決策與證據紀錄：

```text
Iteration:
Change:
Why this mattered:
Metric movement:
Slice movement:
False positives:
False negatives:
Unexpected errors:
Decision:
Tradeoff accepted:
Lesson captured:
Regression added:
Debt created:
Next iteration:
```

用這份紀錄讓模型的工作能累積。目標是讓每次迭代都讓下一個決策更容易，而不只是再多產出一個成品。

## Core Workflow

### 1. Define the Prediction Contract

寫模型程式碼之前，先把產品層級的合約記下來：

- 預測目標和決策負責人
- 輸入實體、輸出 schema、信心/校準欄位，以及允許的延遲
- 批次、線上、串流或混合的服務模式
- 模型、feature store 或相依服務無法使用時的 fallback 行為
- 高影響決策的人工審查或覆寫路徑
- 輸入、預測和 label 的隱私、保留和稽核要求

不要接受「改善模型」當作需求。要把模型連到可觀察的產品行為，和可量測的驗收關卡。

### 2. Lock the Data Contract

每個 ML 任務都需要明確的 data contract：

- 實體粒度和主鍵
- label 定義、label 時間戳記和 label 可取得的延遲
- 特徵時間戳記、新鮮度 SLA 和 point-in-time join 規則
- 訓練、驗證、測試和回測的切分政策
- 必要欄位、允許的 null、範圍、類別和單位
- 不得進入訓練成品或紀錄的 PII 或敏感欄位
- 為了可重現性而設的資料集版本或快照 ID

先防洩漏。如果某個特徵在預測時拿不到，或是用未來資訊 join 出來的，就移除它，或移到只供分析的路徑。

### 3. Build a Reproducible Pipeline

訓練程式碼要讓別的工程師不靠隱藏的 notebook 狀態就能跑：

- 所有超參數和路徑都用有型別的設定檔或 dataclass
- 釘住套件和模型的相依性
- 設定隨機種子，並記錄任何不確定的 GPU 行為
- 記錄資料集版本、程式碼 SHA、設定 hash、指標和成品 URI
- 前處理邏輯跟模型成品存在一起，不要另外放在 notebook 裡
- 訓練、評估和推論的轉換共用同一份，或從同一個來源產生
- 每個步驟都做成 idempotent，這樣重試才不會弄壞成品或指標

偏好不可變的值和純轉換函式。產生特徵時，避免修改共用的 data frame 或全域設定。

```python
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainingConfig:
    dataset_uri: str
    model_dir: Path
    seed: int
    learning_rate: float
    batch_size: int


def artifact_name(config: TrainingConfig, code_sha: str) -> str:
    config_key = f"{config.dataset_uri}:{config.seed}:{config.learning_rate}:{config.batch_size}"
    config_hash = hashlib.sha256(config_key.encode("utf-8")).hexdigest()[:12]
    return f"{code_sha[:12]}-{config_hash}"
```

### 4. Evaluate Before Promotion

升級標準要在訓練結束前就宣告好：

- 和 baseline 模型、目前正式環境的模型做比較
- 對齊產品行為的主要指標
- 延遲、校準、公平性 slice、成本和錯誤集中度的護欄指標
- 重要族群、地區、裝置、語言或資料來源的 slice 指標
- 指標有雜訊時，要有信賴區間或重複執行的變異
- 高影響模型要有人工審查失敗範例
- 明確的「不准上線」閾值

```python
PROMOTION_GATES = {
    "auc": ("min", 0.82),
    "calibration_error": ("max", 0.04),
    "p95_latency_ms": ("max", 80),
}


def assert_promotion_ready(metrics: dict[str, float]) -> None:
    missing = sorted(name for name in PROMOTION_GATES if name not in metrics)
    if missing:
        raise ValueError(f"Model promotion metrics missing required gates: {missing}")

    failures = {
        name: value
        for name, (direction, threshold) in PROMOTION_GATES.items()
        for value in [metrics[name]]
        if (direction == "min" and value < threshold)
        or (direction == "max" and value > threshold)
    }
    if failures:
        raise ValueError(f"Model failed promotion gates: {failures}")
```

離線指標拿來當關卡，不是保證。模型會改變產品行為時，全面上線前要規劃 shadow 評估、canary 上線或 A/B 測試。

### 5. Package for Serving

ML 成品要在服務合約可測試時，才算準備好上正式環境：

- 模型成品包含版本、訓練資料參照、設定和前處理
- 輸入 schema 會拒絕無效、過期或超出範圍的特徵
- 輸出 schema 在有用時包含模型版本、信心或解釋欄位
- 服務路徑有逾時、批次處理、資源限制和 fallback 行為
- CPU/GPU 需求要明確寫出並經過測試
- 預測紀錄避開 PII，同時留下足夠的識別碼，供除錯和 label join 使用
- 整合測試涵蓋缺特徵、過期特徵、型別錯誤、空批次和 fallback 路徑

沒有測試證明兩者等價，就不准讓只在訓練用的特徵程式碼，和服務用的特徵程式碼分岔。

### 6. Operate the Model

模型監控需要系統和品質兩種訊號：

- 可用性、錯誤率、逾時率、佇列深度，以及 p50/p95/p99 延遲
- 特徵 null 比率、範圍漂移、類別漂移和新鮮度漂移
- 預測分布漂移和信心分布漂移
- label 到達的健康度和延遲的品質指標
- 商業 KPI 護欄和回滾觸發條件
- 為 canary 和回滾準備的每版本儀表板

每次 deploy 都要有回滾計畫，寫明前一版的成品、設定、資料相依性和流量切換機制。

## Review Checklist

- [ ] 預測合約明確且可測試
- [ ] data contract 定義了實體粒度、label 時間、特徵時間和快照/版本
- [ ] 洩漏風險已對照預測時可取得的資料檢查過
- [ ] 訓練能從程式碼、設定、資料版本和種子重現
- [ ] 指標有和 baseline 以及目前正式環境的模型比較
- [ ] 高風險族群有包含 slice 指標和護欄
- [ ] 升級關卡是自動化的，而且 fail closed
- [ ] 訓練和服務的轉換是共用的，或有等價性測試
- [ ] 模型成品帶有版本、設定、資料集參照和前處理
- [ ] 服務路徑會驗證輸入，並有逾時、fallback 和回滾行為
- [ ] 監控涵蓋系統健康、特徵漂移、預測漂移和延遲的 label
- [ ] 成品、紀錄、prompt 和範例都排除了敏感資料

## Anti-Patterns

- 需要 notebook 狀態才能重現模型
- 隨機切分把未來資料洩漏進驗證集或測試集
- 特徵 join 忽略事件時間和 label 可取得時間
- 離線指標進步，但重要 slice 退步
- 反覆在測試集上調整閾值
- 把訓練前處理手動複製到服務程式碼裡
- 預測紀錄裡缺少模型版本
- 監控只檢查服務存活，不看資料或預測品質
- 回滾得靠重新訓練，而不是切回已知良好的成品

## Output Expectations

用這個 skill 時，要回傳具體的成品：data contract、升級關卡、pipeline 步驟、測試計畫、deploy 計畫或審查發現。把擋住正式環境就緒的未知項目點出來，不要用假設去填。
