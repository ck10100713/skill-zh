---
name: recsys-pipeline-architect
description: 用六階段 Source→Hydrator→Filter→Scorer→Selector→SideEffect 框架（由 xAI 開源的 For You 演算法推廣開來）設計可組合的推薦、排序和 feed pipeline。只要使用者在做任何要為「(使用者, 情境) 挑出前 K 個項目」的系統，就用這個 skill，例如社群 feed、內容 CMS、RAG reranker、任務排序、通知分流、搜尋重排、廣告排序。
metadata:
  origin: community
---

# recsys-pipeline-architect

一個用來建立可組合的推薦、排序和 feed pipeline 的規格加鷹架 skill。它把**六階段模式**（Source → Hydrator → Filter → Scorer → Selector → SideEffect）寫成規則，這個模式由 xAI 開源的 [For You 演算法](https://github.com/xai-org/x-algorithm)（Apache 2.0）推廣開來。這個 skill 是該模式的獨立重新實作（MIT），沒有複製原版任何程式碼。

上游：<https://github.com/mturac/recsys-pipeline-architect>

## 何時使用

- 使用者要建任何「為使用者／情境挑出前 K 個項目」的系統
- 使用者問「X 該怎麼排序」，或描述了 feed／個人化的問題
- 使用者已經有評分函式，需要它周圍的 pipeline 管線
- 使用者想從單一相關性分數，遷移到可調權重的多動作預測
- 使用者包了一個 LLM/ML scorer，需要 filter、hydrator、side-effect，以及他們技術堆疊（TypeScript / Go / Python）裡可執行的鷹架
- 觸發詞："recommendation system"、"feed algorithm"、"ranking pipeline"、"for you feed"、"candidate pipeline"、"content recommender"、"pipeline architecture for recsys"、"RAG retrieval reranker"

## 何時不要使用

- 模型架構工作（transformer 設計、two-tower 檢索、embedding 訓練）：這個 skill 處理的是模型*周圍*的管線，不是模型本身
- 純 ML 訓練 pipeline：評分函式是使用者自己的責任
- 營運已部署的 pipeline（監控、autoscaling）：不在範圍內

## 六階段框架

| # | 階段 | 工作 | 可平行？ |
|---|---|---|---|
| 1 | **Source** | 從一個或多個來源抓取候選項目 | 可以：多個 source 平行執行 |
| 2 | **Hydrator** | 為每個候選項目補上 filter 和 scorer 需要的 metadata | 可以：互相獨立的 hydrator 平行執行 |
| 3 | **Filter** | 丟掉永遠不該顯示的候選項目（被封鎖、過期、重複、不符資格） | 依序：每個 filter 看到的項目越來越少 |
| 4 | **Scorer** | 為每個存活的候選項目指派一個或多個分數 | 依序：後面的 scorer 看得到前面的分數 |
| 5 | **Selector** | 依最終分數排序，回傳前 K 個 | 單一操作 |
| 6 | **SideEffect** | 快取已回傳的 ID、記錄曝光、發出事件、更新計數器 | 非同步：絕對不能阻塞回應 |

### 為什麼是這個順序

- Source 在 hydration 之前：先知道有哪些候選項目，再花錢去補資料
- Hydration 在 filtering 之前：很多 filter 需要 source 沒提供的 metadata
- Filtering 在 scoring 之前：scoring 是最貴的階段，先丟掉不符資格的
- Scorer 要串成鏈（不是單一 scorer）：真實的系統會組合 ML 評分、多樣性重排和商業規則
- Selector 在 scoring 之後：讓 scoring 保持確定性、可快取
- SideEffect 放最後而且非同步：副作用絕對不能阻塞使用者的回應

## 被呼叫時的工作流程

帶使用者走過這八個步驟：

1. **釐清使用情境**（一輪、三個問題）：要排序的項目是什麼？輸入的情境是什麼？語言／執行環境是什麼？
2. **找出候選來源**：通常是網路內（追蹤的／擁有的／訂閱的）加網路外（ML 檢索／熱門／類似喜歡過的）
3. **列出需要的 hydration**：對每個 filter 和 scorer，source 沒提供但它需要什麼資料？
4. **列出 filter**：重複、自己、時間、封鎖／靜音、先前已回傳、資格。順序很重要，便宜的在貴的之前。
5. **設計 scorer 鏈**：主要（ML）→ 組合器（多動作加權重）→ 多樣性 → 商業規則
6. **Selector**：依最終分數由高到低排序，取前 K 個（或網路內／網路外分層混合）
7. **SideEffects**：快取已回傳的 ID、發出曝光事件、更新計數器、記錄分析，全部丟出去就不管（fire-and-forget）
8. **在使用者的技術堆疊中產生鷹架**

## 要主動講出來的關鍵取捨（不要默默採用預設）

### 1. 單一分數 vs 多動作預測

- **單一分數**：訓練一個模型預測相關性。要改變行為 → 重新訓練。
- **多動作**：對很多動作（讀、讚、分享、略過、檢舉）預測 `P(action)`，在服務時用權重組合。要改變行為 → 改權重。不用重新訓練。

X 的 For You 系統用的是多動作，正負權重都有。使用者預期會頻繁調整時，建議用多動作。

### 2. scoring 中的候選隔離

- **隔離**：每個候選項目獨立評分。確定性、可快取。
- **聯合**：候選項目在評分時彼此 attend（例如對整個 batch 跑 transformer）。表達力更強，但跨 batch 不具確定性。

預設用隔離。只有在有特定理由時才用聯合（例如明確需要感知 batch 的多樣性）。

### 3. 線上 vs 離線

- **請求時（線上）**：pipeline 在每次請求時執行。延遲預算：100–300ms。預設。
- **預先計算（離線批次）**：pipeline 定期執行，結果快取。延遲較低，新鮮度較低。
- **混合**：候選檢索離線，排序線上。

## 硬性規則

1. **不要編造 benchmark 數字。** 「快多少？」→「看 workload，自己跑跑看。」
2. **署名紀律。** 引用這個模式時，要署名為「由 xAI 開源的 For You 演算法推廣開來」／`github.com/xai-org/x-algorithm`（Apache 2.0）。
3. **不要使用商標。** 不要把使用者的產出物命名為「X-like」，也不要用「For You」品牌。模式是自由的，品牌不是。建議命名："candidate pipeline"、"feed pipeline"、"ranking pipeline"、"recsys pipeline"。
4. **講出取捨。** 多動作 vs 單一、隔離 vs 聯合、線上 vs 離線，絕對不要默默採用預設。
5. **產生的鷹架必須能跑。** 不准拿 pseudocode 冒充程式碼。
6. **Filter 順序很重要。** 便宜的在貴的之前。通用的在使用者專屬的之前。
7. **Side effect 絕對不阻塞。** 用 fire-and-forget 的方式包起來（goroutine／沒有 await 的 promise／asyncio task）。

## 反模式

- 先 scoring 再 filtering（把算力浪費在反正會被丟掉的候選項目上）
- 同步的 side effect（快取寫入／曝光事件發送阻塞了回應）
- 產品需要針對多個目標調整（互動 vs 安全 vs 多樣性 vs 廣告）時，卻只用單一「相關性」分數
- 預設就用聯合評分（不具確定性、更難快取、無法和重排階段組合）
- 為了「示範」而產生 pseudocode，鷹架必須真的能跑

## 上游內容

上游 repo <https://github.com/mturac/recsys-pipeline-architect> 內含：

- 完整的 `SKILL.md`，附完整的 8 步驟工作流程
- 5 份按需載入的參考文件：4 種語言（TS/Go/Python/Rust）的介面、多動作評分模式、候選隔離、filter 食譜（12 種模式）、scorer 食譜（加權和、MMR、多樣性懲罰、位置去偏）
- 3 個可執行的範例鷹架，每個的測試套件都是綠的：
  - Strapi v5 plugin（TypeScript / Jest，3/3 通過）
  - 相容 Zentra 的 pipeline（Go 泛型，3/3 通過）
  - PMAI 任務排序器（Python / FastAPI / pytest，3/3 通過）
- 已標記 v0.1.0 release
- MIT 授權；模式署名給 xAI 的 X For You 演算法（Apache 2.0）

透過 skills.sh 安裝：`npx skills add mturac/recsys-pipeline-architect`
