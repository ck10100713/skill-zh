---
name: ml-adoption-playbook
description: 給 AI agent 和軟體工程師的端到端方法論，把機器學習演算法加進既有的非 ML codebase。涵蓋問題定義、資料就緒、架構解耦和 baseline 模型整合。要在完全沒有 ML 的 codebase 加入機器學習能力，從問題定義做到 baseline 模型時使用。
origin: ECC
---

# ML Adoption Playbook

這個 skill 提供一套有彈性的方法論，把機器學習模型實作進既有的軟體工程專案。它補起傳統 SWE 和 MLOps 之間的落差，規範 ML 該怎麼研究、解耦、訓練和整合。

## When to Activate

- 使用者要求在既有 codebase「加 ML」或「加一個演算法」。
- 規劃把新模型（例如推薦、分類、預測）整合進非 ML 的應用程式。
- 為 agent 規劃一套流程，讓它能有彈性地建置、訓練並 deploy ML 元件。

## Phase 1: Problem Framing & Feasibility

寫模型程式碼之前，先釐清「為什麼」和「怎麼做」。
- **Heuristic Check：** 問使用者，簡單的 heuristic（例如 regex、規則式排序）是不是能更快解決問題。如果可以，就從那裡開始。
- **Metric Definition：** 定義 ML 模型想改善哪個商業指標（例如點擊率、降低延遲）。
- **Mistake Budget：** 定義什麼算「糟糕」的預測，以及系統該怎麼處理。

## Phase 2: Data Readiness

沒有乾淨、可取得的資料，ML 就沒用。
- **Audit Data Sources：** 找出訓練資料放在哪。是線上資料庫、靜態 CSV，還是 API？
- **Data Contract：** 為輸入資料建立 schema。需要哪些特徵？缺少某個特徵時會怎樣？
- **Leakage Prevention：** 確保使用者提議的資料切分，不會不小心把未來的資訊洩漏進訓練集（例如時間序列資料要依時間順序切分）。

## Phase 3: Architectural Integration & Decoupling

不要把模型推論和核心商業邏輯緊緊耦合。
- **API Boundary：** 建議把模型放在 API 端點後面（例如用 `fastapi-patterns` 或 `django-patterns`）或專用的 service class 裡。
- **Fallback Mechanisms：** 設計預設狀態。如果模型回應太久或丟出錯誤，系統必須能平順地退回寫死的規則。
- **Feature Flags：** 把新的 ML 推論呼叫包在 feature flag 裡，這樣才能安全地上線（或回滾）。

## Phase 4: Model Implementation & Training

程式碼的結構要能重現、能迭代。
- **Start Simple：** 先建 baseline 模型（例如簡單的 scikit-learn Logistic Regression，或最陽春的 PyTorch linear layer）。
- **Reproducibility：** 套用 `pytorch-patterns` 或類似的最佳實踐：固定隨機種子、讓程式碼不綁定特定裝置、明確記錄 tensor/array 的 shape。
- **Automated Evidence：** 資料轉換和推論 schema 要有測試。沒有拿它和 baseline 比較的評估腳本，就不要接受這個模型。

## Phase 5: Handoff to MLOps

baseline 模型整合完之後，重心轉到持續營運。
- **參考 `mle-workflow`：** 引導使用者設定實驗追蹤、model registry 和 drift 偵測。
- **CI/CD：** 把模型評估步驟加進既有的 CI pipeline，確保之後的 commit 不會讓模型效能變差。

## Iterative Agent Workflow

透過這份 playbook 協助使用者時，agent 應該：
1. **先問釐清問題**，把 Phase 1 做完，再提出架構。
2. 在 Phase 2 **草擬 data contract**，給使用者核准。
3. 在 Phase 3 **先寫解耦介面**（API/Service），*再*寫訓練迴圈。
4. 在 Phase 4 **交付可重現的腳本**，能訓練模型並存出成品。
