---
name: "algo-net-community"
description: "實作 Louvain 社群偵測，找出網路中連結緊密的群體。當使用者需要在社群 / 組織網路中找出社群或叢集、依互動模式區隔客戶，或分析網路的模組化結構時使用，即使他們說的是『find groups in this network』『community detection』或『network clustering』。"
metadata:
  category: "WP-46 網絡演算法"
  tags: ["network", "community-detection", "louvain", "modularity"]
---

# Louvain 社群偵測

## 概述

Louvain 演算法透過最佳化 modularity（模組度）來偵測社群，模組度是社群內部邊的比例，減去邊隨機分布時預期的比例。這是貪婪的階層式演算法，在稀疏圖上複雜度為 O(n log n)。會產生多種解析度下的社群階層。

## 何時使用

**觸發條件：**
- 在社群、組織或互動網路中找出自然的分群
- 依行為相似度區隔使用者 / 客戶
- 分析複雜網路的模組化結構

**不該使用的情況：**
- 重疊社群（用 DEMON 或 BigCLAM）
- 社群已預先定義、你只是在對節點分類時（用 label propagation）

## 演算法

```
IRON LAW: Modularity Has a RESOLUTION LIMIT
Louvain optimizes modularity, which has a known resolution limit
(Fortunato & Barthélemy, 2007): it cannot detect communities smaller
than √(2E) where E = total edges. In large networks, small but real
communities may be merged. Use multi-resolution methods or Leiden
algorithm (improved Louvain) for better results.
```

### 階段 1：輸入驗證
從互動資料建立無向加權圖。邊的權重代表互動強度（頻率、時間長度、量）。
**關卡：** 圖已載入，沒有孤立節點（或已決定怎麼處理它們）。

### 階段 2：核心演算法
**第一階段：局部移動**
1. 每個節點先各自一個社群
2. 對每個節點，計算移到各個鄰居的社群所帶來的模組度增益
3. 把節點移到增益為正且最大的社群
4. 重複，直到沒有任何有利的移動

**第二階段：聚合**
5. 建立新圖，其中節點 = 社群，邊 = 社群之間的邊的加總
6. 在聚合後的圖上重複第一階段
7. 持續到模組度不再提升為止

### 階段 3：驗證
檢查：模組度 Q > 0（非平凡的劃分）、社群大小合理（不是一個巨大的加上許多單點）、人工檢視抽樣的社群。
**關卡：** 模組度為正，社群大小呈類似冪律的分布。

### 階段 4：輸出
回傳社群歸屬，附上模組度分數。

## 輸出格式

```json
{
  "communities": [{"id": 0, "size": 45, "top_members": ["Alice", "Bob"], "internal_density": 0.35}],
  "summary": {"num_communities": 12, "modularity": 0.65, "largest": 120, "smallest": 5},
  "metadata": {"algorithm": "louvain", "nodes": 500, "edges": 2000}
}
```

## 範例

### 輸入輸出範例
**輸入：** 200 位員工的 email 網路，以 email 頻率加權
**預期：** 社群大致對應部門 / 團隊，模組度約 0.5-0.7。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 完全圖 | 一個社群或隨機切分 | 沒有模組化結構 |
| 不連通的分量 | 每個分量 = 一個社群 | 自然分離 |
| 加權 vs 不加權 | 社群不同 | 權重會改變模組度的計算 |

## 注意事項

- **非確定性**：節點處理的順序會影響結果。跑多次，選模組度最高的劃分，或改用 Leiden 演算法（更穩定）。
- **解析度參數**：標準 Louvain 在模組度裡用 γ=1。調整 γ 可以看到不同尺度的社群。γ>1 找到較小的社群；γ<1 找到較大的。
- **Leiden > Louvain**：Louvain 可能產生連通性很差的社群（移除一個節點就讓社群斷開）。Leiden 演算法修正了這點，並提供保證。
- **時間穩定性**：在動態網路中，即使網路變化很小，社群歸屬也可能在不同快照之間劇烈改變。要用時間平滑。
- **詮釋**：社群偵測找出結構，但要解讀節點「為什麼」聚在一起，需要領域知識。不要過度詮釋自動偵測出來的社群。

## 參考資料

- Leiden 演算法（改良的 Louvain），見 `references/leiden.md`
- 多解析度社群偵測，見 `references/multi-resolution.md`
