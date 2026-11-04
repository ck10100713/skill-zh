---
name: "algo-net-influence"
description: "解決影響力最大化問題，挑出最佳種子節點讓資訊擴散最廣。當使用者需要為病毒式行銷挑種子使用者、在預算限制下讓網路觸及最大化，或比較種子策略時使用，即使他們說的是『who should we seed first』『maximize viral reach』或『optimal influencer selection』。"
metadata:
  category: "WP-46 網絡演算法"
  tags: ["network", "influence-maximization", "seed-selection", "viral-marketing"]
---

# 影響力最大化

## 概述

影響力最大化是在網路中選 k 個種子節點，在某個擴散模型（Independent Cascade 或 Linear Threshold）下讓預期擴散範圍最大。這是 NP-hard 問題，但因為次模性（submodularity），貪婪演算法能達到 (1-1/e) ≈ 63% 的近似保證。搭配 CELF 最佳化，可以實際用在數百萬節點的網路。

## 何時使用

**觸發條件：**
- 選 k 個影響者 / 使用者作為病毒式行銷活動的種子
- 在固定預算（k 個種子）下讓資訊擴散最大化
- 比較種子策略（依 degree vs 貪婪 vs 隨機）

**不該使用的情況：**
- 衡量既有的影響力時（用中心性指標）
- 分析社群結構時（用社群偵測）

## 演算法

```
IRON LAW: Greedy With Lazy Evaluation (CELF) Is the Practical Standard
The naive greedy algorithm requires O(k × n × R) simulations where
R = Monte Carlo runs (10,000+). CELF exploits submodularity to skip
unnecessary evaluations, achieving 700x speedup. Always use CELF
over naive greedy. Simple heuristics (top-k by degree) are fast
but can perform 50%+ worse than greedy.
```

### 階段 1：輸入驗證
建立網路圖。選擇擴散模型：Independent Cascade（每條邊有機率）或 Linear Threshold（每個節點有門檻）。設定 k（種子數）和傳播機率。
**關卡：** 圖已載入、已選好擴散模型、已定義 k。

### 階段 2：核心演算法
**搭配 CELF 的貪婪法：**
1. 初始化：種子集合 S = ∅
2. 對每個候選節點，用 Monte Carlo 模擬（R=10,000 次）估計邊際增益：σ(S∪{v}) - σ(S)
3. 選邊際增益最高的節點，加入 S
4. CELF 最佳化：重用先前的邊際增益，只有在某節點的上界超過目前最佳值時才重新評估
5. 重複到 |S| = k

### 階段 3：驗證
把貪婪法的結果和基準比較：隨機種子、degree 前 k 名、PageRank 前 k 名。貪婪法應該明顯勝出。
**關卡：** 貪婪法的擴散量 > degree 啟發式的擴散量，且差距有意義。

### 階段 4：輸出
回傳種子集合，附上預期擴散量和比較。

## 輸出格式

```json
{
  "seeds": [{"node": "user_42", "marginal_gain": 150, "selection_order": 1}],
  "expected_spread": 2500,
  "baselines": {"random": 800, "top_degree": 1900, "greedy": 2500},
  "metadata": {"k": 10, "model": "independent_cascade", "mc_simulations": 10000, "nodes": 50000}
}
```

## 範例

### 輸入輸出範例
**輸入：** 社群網路 10K 個節點，k=5 個種子，IC 模型，每條邊 p=0.1
**預期：** 貪婪法選出分散、位置好的種子（不會全是高 degree 的），預期擴散量約 500-1000。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| k=1 | 個別擴散量最大的節點 | 只有一個種子，不用考慮重疊 |
| k > 社群數 | 每個社群一個種子最佳 | 多樣性勝過集中 |
| 非常稀疏的圖（p 低） | 不管種子怎麼選，擴散量都小 | 機率低時網路無法傳播 |

## 注意事項

- **Monte Carlo 的變異**：R=1000 時，擴散量估計有約 5% 的變異。要穩定的結果就用 R=10,000 以上，尤其在比較差不多的候選者時。
- **擴散模型的選擇很重要**：IC 和 LT 會得到不同的最佳種子集合。IC 偏好高 degree 的節點；LT 偏好能引發連鎖效應的節點。
- **傳播機率的估計**：真實世界的邊機率是未知的。常見做法：均勻（p=0.01-0.1）、依度數倒數加權（1/in-degree），或從級聯資料學習。
- **重疊的懲罰**：貪婪法天然就處理了重疊（次模性）。獨立挑選前幾名節點的啟發式，會把種子浪費在重疊的影響範圍上。
- **可擴展性**：即使有 CELF，數百萬節點仍需要進一步近似（以 sketch 為基礎的方法，例如 IMM 或 TIM+）。

## 參考資料

- CELF 與 CELF++ 的實作，見 `references/celf-implementation.md`
- 可擴展的影響力最大化（IMM），見 `references/scalable-im.md`
