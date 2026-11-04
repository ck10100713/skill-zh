---
name: "algo-net-centrality"
description: "計算網路中心性指標，找出圖中的重要節點。當使用者需要找出關鍵影響者、關鍵基礎設施節點，或網路中的核心角色時使用，即使他們說的是『who is most important in this network』『key nodes』或『network influence measurement』。"
metadata:
  category: "WP-46 網絡演算法"
  tags: ["network", "centrality", "graph-analysis", "social-network"]
---

# 網路中心性指標

## 概述

中心性指標用來量化節點在網路中的重要性。四個經典指標：degree（連接數）、betweenness（橋接角色）、closeness（鄰近程度）、eigenvector（連接品質）。每個指標抓到的重要性面向都不一樣。複雜度從 degree 的 O(V+E) 到 betweenness 的 O(V×E) 都有。

## 何時使用

**觸發條件：**
- 找出社群 / 組織網路中的關鍵影響者或關鍵節點
- 分析網路弱點（哪個節點故障會造成最大損害）
- 從不同面向比較節點的重要性

**不該使用的情況：**
- 群體 / 社群偵測（用社群偵測演算法）
- 資訊擴散建模（用傳染病模型）

## 演算法

```
IRON LAW: Different Centrality Metrics Answer DIFFERENT Questions
- Degree: Who has the most connections? (popularity)
- Betweenness: Who bridges communities? (brokerage)
- Closeness: Who can reach everyone fastest? (efficiency)
- Eigenvector: Who is connected to important people? (prestige)
Using the WRONG metric answers the WRONG question. Choose based on
what "important" means in your context.
```

### 階段 1：輸入驗證
從邊清單或鄰接矩陣建立網路圖。確定：有向 vs 無向、加權 vs 不加權、連通 vs 不連通。
**關卡：** 圖的格式正確，已找出最大連通分量。

### 階段 2：核心演算法
1. **Degree 中心性：** C_D(v) = deg(v) / (N-1)。O(V+E)。
2. **Betweenness 中心性：** C_B(v) = Σ(σ_st(v) / σ_st)，對所有 s,t 配對。最短路徑中經過 v 的比例。O(V×E)。
3. **Closeness 中心性：** C_C(v) = (N-1) / Σd(v,u)。平均最短路徑的倒數。O(V×(V+E))。
4. **Eigenvector 中心性：** 分數正比於鄰居分數的總和。用 power iteration 迭代到收斂。O(k×E)。

### 階段 3：驗證
檢查：中心性數值已正規化到 [0,1]。各指標的前幾名節點可能不同，這是預期的，也有資訊價值。用領域知識對前 5 名做合理性檢查。
**關卡：** 所有指標都算出來了，前幾名節點符合直覺。

### 階段 4：輸出
回傳中心性分數，附上多指標比較。

## 輸出格式

```json
{
  "centralities": [{"node": "Alice", "degree": 0.85, "betweenness": 0.42, "closeness": 0.71, "eigenvector": 0.90}],
  "metadata": {"nodes": 500, "edges": 2000, "directed": false, "connected_components": 1}
}
```

## 範例

### 輸入輸出範例
**輸入：** 5 個節點的無向圖（橋接拓撲）：edges = {(A,B), (A,C), (B,C), (C,D), (D,E)}
```
    A --- B
     \  /
      C
      |
      D --- E
```

**預期的中心性（以 N-1 = 4 正規化）：**

| 節點 | Degree | Betweenness | Closeness | Eigenvector |
|------|--------|-------------|-----------|-------------|
| A | 0.50 (2/4) | 0.000 | 0.571 (4/7) | 0.452 |
| B | 0.50 (2/4) | 0.000 | 0.571 (4/7) | 0.452 |
| **C** | **0.75 (3/4)** | **0.667** | **0.800 (4/5)** | **0.628** |
| D | 0.50 (2/4) | 0.500 | 0.667 (4/6) | 0.386 |
| E | 0.25 (1/4) | 0.000 | 0.500 (4/8) | 0.201 |

驗證：**C 是橋**，四個指標全部最高。E 在邊緣，所有指標都最低。A 和 B 對稱（分數相同）。D 的 betweenness 不為零（橋接 C 到 E），但 degree 比 C 低。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 星狀圖 | 中心點所有中心性都最大 | 樞紐在所有指標上都占優勢 |
| 不連通的圖 | 不連通的節點對 closeness 無定義 | 改用 harmonic centrality |
| 有向圖 | 入度中心性 ≠ 出度中心性 | 受歡迎程度（入）vs 活躍程度（出） |

## 注意事項

- **不連通的圖**：節點彼此到不了時，closeness 中心性無定義。可改用 harmonic centrality：C_H(v) = Σ(1/d(v,u))。
- **尺度相依**：原始的中心性數值會依網路大小而變。跨網路比較要用正規化的版本。
- **Betweenness 很貴**：O(V×E) 讓它在非常大的網路（數百萬節點）上不實際。要用近似演算法（對最短路徑隨機抽樣）。
- **動態網路**：某個快照的中心性不一定反映長時間的影響力。時間性的中心性指標存在，但更複雜。
- **指標之間的相關性**：在很多真實網路中，中心性指標彼此相關。但「差異」往往最有資訊量（degree 高但 betweenness 低 = 局部樞紐，不是中介者）。

## 參考資料

- 中心性指標的比較框架，見 `references/metric-comparison.md`
- 近似的 betweenness 演算法，見 `references/approximate-betweenness.md`
