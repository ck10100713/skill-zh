---
name: recsys-pipeline-architect
description: 用 xAI 開源的 X For You 演算法所推廣的六階段 Source→Hydrator→Filter→Scorer→Selector→SideEffect 框架，設計可組合的推薦、排序和 feed pipeline。在建構任何「幫 (user, context) 挑出前 K 個項目」的系統時使用，例如內容 feed、搜尋排序、RAG reranker、任務優先排序、通知分流、廣告選擇。
---

# Recsys Pipeline Architect

一個用來建構可組合的推薦、排序和 feed pipeline 的規格與 scaffold skill。它把 xAI 開源的 [For You algorithm](https://github.com/xai-org/x-algorithm)（Apache 2.0）所推廣的六階段模式編碼進來，套用到任何「幫 (user, context) 挑前 K 個」的問題。

## Overview

正式環境裡大多數的「推薦系統」都不是什麼特殊的 ML，而是 *pipeline*：從一個或多個來源取得候選項目、用 metadata 補充資訊、剔除不合格的、替剩下的打分、排序後挑出前 K 個，最後觸發非同步的 side effect。這個模式放諸四海皆準。變的是打分函式和項目本身，pipeline 的形狀不會變。

這個 skill 是這個模式的獨立重新實作（MIT），沒有複製原始碼。

## When to Use This Skill

- 建構任何會回傳「某個 user/context 的前 K 個項目」的系統
- 設計或重構個人化 feed（內容、搜尋結果、通知）
- 把 LLM/ML 打分器包進完整的 pipeline 管線（來源、hydration、filter、side effect）
- 加入可調權重的多動作預測（取代單一相關性分數）
- 建構 RAG 檢索的 reranker（便宜的檢索 → 昂貴的 rerank）
- 設計任務優先排序或警報分流系統

## The Six-Stage Framework

| # | Stage | Job | Parallel? |
|---|---|---|---|
| 1 | **Source** | 從一個或多個來源取得候選項目 | Yes — 多個 source 平行執行 |
| 2 | **Hydrator** | 用 filter 和打分需要的 metadata 補充候選項目 | Yes — 彼此獨立的 hydrator 平行執行 |
| 3 | **Filter** | 剔除不合格的候選項目（被封鎖、過期、重複、不符資格） | Sequential — 每個 filter 看到的項目越來越少 |
| 4 | **Scorer** | 替每個留下來的候選項目指派一個或多個分數 | Sequential — 後面的 scorer 看得到前面的分數 |
| 5 | **Selector** | 依最終分數排序，回傳前 K 個 | Single op |
| 6 | **SideEffect** | 快取、記 log、發事件、更新已推送的歷史 | Async — 絕對不能擋住回應 |

### Why this exact order

- Source 在 hydration 之前：先知道有哪些候選項目，再花成本去補充資訊
- Hydration 在 filter 之前：很多 filter 需要 source 沒提供的 metadata
- Filter 在打分之前：打分是最昂貴的階段，先把不合格的剔掉
- Scorer 做成鏈（不是單一 scorer）：真實系統會組合 ML 打分 + 多樣性 rerank + 業務規則
- Selector 在打分之後：讓打分維持確定性、可快取
- SideEffect 放最後而且要非同步：side effect 絕對不能擋住使用者的回應

## Workflow When Invoked

帶使用者走過八個步驟：

1. **釐清使用情境**（一輪就好，缺資訊時才問這三個問題）：要排序的項目、輸入的 context、語言/runtime
2. **找出候選項目的來源**（通常是 in-network + out-of-network，單一來源也可以）
3. **列出需要的 hydration**：對每個 filter 和 scorer，它需要哪些 source 沒提供的資料？
4. **列出 filter**：便宜的在前、昂貴的在後，通用的在前、針對使用者的在後（重複、自己、年代、封鎖/靜音、先前推送過、資格）
5. **設計 scorer 鏈**：主要的 ML/啟發式 → combiner（帶權重的多動作）→ 多樣性 → 業務規則
6. **Selector**：依最終分數由高到低排序，取前 K 個（或分層混合）
7. **SideEffects**：快取已推送的 ID、發出 impression 事件、更新計數器、記錄分析資料；全部都是 fire-and-forget
8. **用使用者的技術棧產生 scaffold**

## Key Trade-offs to Surface

這些絕對不要悶著頭用預設值，它們是偽裝成技術問題的產品決策。

### 1. Single score vs multi-action prediction

- **Single score：** 訓練一個模型來預測相關性。要改變行為 → 重新訓練。
- **Multi-action：** 對很多動作預測 `P(action)`（`P(read)`、`P(like)`、`P(share)`、`P(skip)`、`P(report)`），在 serving 時用權重組合。要改變行為 → 改權重，不用重新訓練。

X For You 演算法用的是 multi-action，同時有正權重和負權重。使用者預期會常常調整時，推薦用 multi-action。

### 2. Candidate isolation vs joint scoring

- **Isolated：** 每個候選項目獨立打分。確定性、可快取。
- **Joint：** 打分時候選項目彼此互相 attend（例如對整批資料跑 transformer）。表達力更強，但不同批次之間不具確定性。

預設用 isolation。只有在有明確理由時才用 joint（例如明確需要感知整批資料的多樣性）。

### 3. Online vs offline batch

- **Request-time（online）：** 每次請求都跑一次 pipeline。延遲預算：100–300ms。
- **Pre-computed（offline batch）：** pipeline 定期跑，結果快取起來。延遲更低，新鮮度更低。
- **Hybrid：** 候選項目的檢索離線做，排序線上做。

## Hard Rules

1. **不要編造 benchmark 數字。** 「這有多快？」→「看工作負載，自己跑跑看」。
2. **標明出處要守規矩。** 把這個模式標註為「由 xAI 開源的 For You algorithm 推廣」/ `github.com/xai-org/x-algorithm`（Apache 2.0）。
3. **不要使用商標。** 不要把使用者的產出命名成「X-like」，也不要用「For You」品牌。用中性名稱：「candidate pipeline」、「feed pipeline」、「ranking pipeline」。
4. **把取捨攤開來講。** Multi-action vs single、isolation vs joint、online vs offline，絕對不要悶著頭用預設值。
5. **產生的 scaffold 一定要能跑。** 不准拿偽程式碼冒充程式碼。
6. **Filter 的順序很重要。** 便宜的在前，昂貴的在後。通用的在前，針對使用者的在後。
7. **Side effect 絕對不能擋住回應。** 包成 fire-and-forget 的寫法（goroutine / 不 await 的 promise / asyncio task）。

## Anti-Patterns

- ❌ 先打分再 filter（把算力浪費在注定會被剔掉的候選項目上）
- ❌ 同步的 side effect（快取寫入/impression 發送擋住了回應）
- ❌ 產品需要多目標調整，卻只用單一「相關性」分數
- ❌ 預設用 joint scoring（不具確定性、無法快取、跟 rerank 組合不起來）
- ❌ 「為了說明」而寫的偽程式碼，scaffold 一定要真的能跑

## Common Use Cases

### Content feed (Strapi v5 plugin, TypeScript)

使用者有一個 50k 篇文章的 CMS，想要個人化的「for you」feed。走完 8 個步驟 → 產生 Strapi plugin 的 scaffold，包含 multi-action 打分、作者多樣性、標準 filter，以及非同步的 side effect 通道。

### RAG retrieval reranker (Python async)

使用者的 RAG 從向量資料庫回傳前 50 個 chunk，想用更昂貴的 scorer 重新排序，再回傳前 5 個。單一 source 的 pipeline 加上一條 scorer 鏈（便宜的檢索 + 昂貴的 rerank）。

### Task prioritizer (FastAPI service)

使用者有一個不斷進來的任務建議佇列，想依照「這個使用者接下來該做什麼」來排序，並考慮他過去的行為模式。項目換成任務而不是內容，同樣的形狀照樣適用。

### Notification triage (offline-batch job)

使用者想要每天一份摘要，從過去 24 小時的佇列中挑出前 10 個。這是 offline-batch 的 pipeline。Source = 佇列，filter = 年代/去重/資格，scorer = 緊急度 × 使用者親和度，selector = 前 10 個，side effect = 寄 email（一樣是非同步）。

## Upstream

這個 skill 是上游 repo 的單檔轉接層，上游附有 5 份隨需載入的參考文件和 3 個可執行的範例 scaffold（Strapi v5 / Go / Python，每一個的測試套件都是綠燈，共 9/9 個測試）。

- **Upstream：** https://github.com/mturac/recsys-pipeline-architect
- **Release：** v0.1.0（MIT）
- **References：** 4 種語言（TS/Go/Python/Rust）的介面、multi-action 打分、candidate isolation、filter 食譜（12 種 pattern）、scorer 食譜
- **跨平台安裝：** `npx skills add mturac/recsys-pipeline-architect`
