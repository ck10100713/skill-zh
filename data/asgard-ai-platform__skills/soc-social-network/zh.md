---
name: "soc-social-network"
description: "運用社會網絡分析的概念（節點、連結、中心性、結構洞、強弱連結）來描繪並分析關係結構。使用者需要了解組織內的影響力模式、找出關鍵的連結者、分析資訊流動，或描繪利害關係人的關係時使用，就算他們說的是「誰是意見領袖」、「資訊在這裡是怎麼傳開的」或「畫出我們團隊裡的關係」也一樣。"
metadata:
  category: "WP-18 社會科學院"
  tags: ["social-science", "social-network-analysis", "organizational-behavior"]
---

# 社會網絡分析

## 概述

社會網絡分析檢視行動者（節點）之間的關係（連結），揭露組織圖上看不見的結構。它能找出誰真正握有影響力、資訊瓶頸在哪裡，以及想法如何在社群中擴散。

## 框架

```
IRON LAW: Structure Determines Influence, Not Just Position

A mid-level manager who bridges two disconnected departments may have more
real influence than a VP who sits in a dense, well-connected cluster.
Network position (centrality, brokerage) determines influence more than
formal hierarchy.
```

### 核心概念

| 概念 | 定義 | 為什麼重要 |
|---------|-----------|---------------|
| **節點（Node）** | 一個行動者（人、組織、實體） | 誰在網絡裡 |
| **連結（Tie）** | 節點之間的關係 | 節點是怎麼連在一起的 |
| **強連結（Strong tie）** | 頻繁、有情感、互惠的關係 | 信任、支持、可靠的資訊 |
| **弱連結（Weak tie）**（Granovetter） | 不頻繁、隨意、橋接的關係 | 取得「新」資訊和機會的管道 |
| **度中心性（Degree centrality）** | 直接連結的數量 | 受歡迎程度、活躍度 |
| **中介中心性（Betweenness centrality）** | 一個節點出現在其他節點之間最短路徑上的頻率 | 經紀角色、把關、資訊控制 |
| **接近中心性（Closeness centrality）** | 到所有其他節點的平均距離 | 資訊觸及的速度 |
| **結構洞（Structural hole）**（Burt） | 兩個群集之間的缺口，由一位經紀人搭橋 | 競爭優勢的來源：經紀人控制資訊流動 |

### 分析步驟

1. **定義網絡**：節點是誰？什麼算是連結？（溝通、信任、諮詢、合作）
2. **蒐集資料**：問卷（「你會找誰討論意見？」）、email／Slack 資料、會議共同出席
3. **描繪網絡**：把節點和連結視覺化
4. **計算中心性指標**：每個節點的度、中介、接近中心性
5. **找出結構模式**：群集、橋接、孤立者、結構洞
6. **詮釋並轉為行動**：誰是關鍵連結者？瓶頸在哪裡？

## 輸出格式

```markdown
# Network Analysis: {Context}

## Network Definition
- Nodes: {who} (N = {count})
- Tie definition: {what constitutes a connection}
- Data source: {survey / communication data / observation}

## Key Metrics
| Node | Degree | Betweenness | Role |
|------|--------|-------------|------|
| {person} | {N connections} | {score} | Hub / Bridge / Isolate |

## Structural Findings
- Clusters: {identified groups}
- Bridges: {who connects clusters}
- Structural holes: {where gaps exist}
- Isolates: {disconnected nodes}

## Implications
1. {finding → action}
```

## 範例

### 正確的應用
**情境：** 一家 50 人新創的諮詢網絡
- 中介中心性最高的節點：產品經理（不是 CEO），她橋接了工程、設計和商務團隊
- 結構洞：行銷團隊跟工程完全沒有直接連結，所有溝通都經過產品經理
- 影響：如果產品經理離職，三個團隊之間的資訊流動就會崩潰。需要建立直接的跨職能連結 ✓

### 錯誤的應用
- 「CEO 的連結最多，所以他最有影響力」→ CEO 的度中心性高（連結多），但中介中心性可能很低（每個人彼此之間也有連結，不需要經過 CEO）。違反鐵律：決定影響力的是結構，不只是連結的數量。

## 注意事項

- **Granovetter 的弱連結的力量**：弱連結對於取得新資訊和機會「更」有價值，因為它們橋接了不同的社交圈。強連結分享的是重複的資訊。
- **網絡資料很敏感**：畫出誰跟誰說話，可能讓人覺得像監控。要對目的保持透明，並盡可能匿名化。
- **網絡會改變**：關係會演變。網絡圖只是一張快照。要定期重新量測。
- **中心性依賴情境**：在諮詢網絡裡中心性高，不等於在友誼網絡裡中心性高。要小心定義連結的類型。
- **不要把相關當成因果**：中心的人可能因為所處的位置而表現更好，也可能因為表現好而變成中心。要分清楚很困難。

## 參考資料

- 網絡視覺化的工具與方法請看 `references/network-tools.md`
