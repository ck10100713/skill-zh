---
name: social-graph-ranker
description: 用加權社交圖譜排名，找出 warm intro 管道、計算橋接分數，並分析 X 和 LinkedIn 上的人脈缺口。使用者要的是可重複使用的圖譜排名引擎本身，而不是疊在它上面的完整開發信或人脈維護流程時使用。
metadata:
  origin: ECC
---

# Social Graph Ranker

用於人脈導向開發聯繫的標準加權圖譜排名層。

使用者需要做這些事時，就用這個：

- 依引薦價值為現有的共同好友或人脈排名
- 把通往目標清單的 warm 路徑畫出來
- 衡量一階和二階人脈的橋接價值
- 判斷哪些目標值得請人 warm intro，哪些該直接 cold outreach
- 想獨立於 `lead-intelligence` 或 `connections-optimizer` 之外，理解圖譜的數學

## 何時單獨使用

使用者主要想要排名引擎時，選這個 skill：

- 「我的人脈裡誰最適合替我引薦？」
- 「依誰能幫我連到這些人，替我的共同好友排名」
- 「把我的圖譜對照這個 ICP」
- 「讓我看橋接的數學」

使用者真正想要的是下面這些時，不要單獨用它：

- 完整的潛在客戶開發和外送序列 -> 用 `lead-intelligence`
- 修剪、重新平衡和擴展人脈 -> 用 `connections-optimizer`

## 輸入

蒐集或推斷：

- 目標人物、公司或 ICP 定義
- 使用者目前在 X、LinkedIn 或兩者上的圖譜
- 加權的優先項目，例如職務、產業、地區和回應度
- 走訪深度和衰減容忍度

## 核心模型

給定：

- `T` = 加權的目標集合
- `M` = 你目前的共同好友 / 直接人脈
- `d(m, t)` = 從共同好友 `m` 到目標 `t` 的最短跳數距離
- `w(t)` = 由訊號評分得到的目標權重

基本橋接分數：

```text
B(m) = Σ_{t ∈ T} w(t) · λ^(d(m,t) - 1)
```

其中：

- `λ` 是衰減係數，通常是 `0.5`
- 直接路徑貢獻完整價值
- 每多一跳，貢獻減半

二階擴展：

```text
B_ext(m) = B(m) + α · Σ_{m' ∈ N(m) \\ M} Σ_{t ∈ T} w(t) · λ^(d(m',t))
```

其中：

- `N(m) \\ M` 是這位共同好友認識、但你不認識的人的集合
- `α` 是二階觸及的折扣，通常是 `0.3`

依回應度調整的最終排名：

```text
R(m) = B_ext(m) · (1 + β · engagement(m))
```

其中：

- `engagement(m)` 是正規化後的回應度或關係強度
- `β` 是互動加成，通常是 `0.2`

解讀：

- 第 1 級：`R(m)` 高而且有直接橋接路徑 -> 請對方 warm intro
- 第 2 級：`R(m)` 中等而且有一跳的橋接路徑 -> 有條件的引薦請求
- 第 3 級：`R(m)` 低，或沒有可行的橋接 -> 直接聯繫，或補上圖譜缺口

## 評分訊號

走訪圖譜之前，用對當前優先項目重要的任何因素替目標加權：

- 職務或頭銜吻合度
- 公司或產業適配度
- 目前的活躍度和近期性
- 地理相關性
- 影響力或觸及範圍
- 回應的可能性

走訪之後，用這些替共同好友加權：

- 通往目標集合的加權路徑數量
- 這些路徑的直接程度
- 回應度或過去的互動歷史
- 幫忙引薦的情境適配度

## 工作流程

1. 建立加權的目標集合。
2. 從 X、LinkedIn 或兩者拉出使用者的圖譜。
3. 計算直接橋接分數。
4. 替價值最高的共同好友展開二階候選人。
5. 依 `R(m)` 排名。
6. 回傳：
   - 最佳的 warm intro 請求
   - 有條件的橋接路徑
   - 沒有 warm 路徑的圖譜缺口

## 輸出格式

```text
SOCIAL GRAPH RANKING
====================

Priority Set:
Platforms:
Decay Model:

Top Bridges
- mutual / connection
  base_score:
  extended_score:
  best_targets:
  path_summary:
  recommended_action:

Conditional Paths
- mutual / connection
  reason:
  extra hop cost:

No Warm Path
- target
  recommendation: direct outreach / fill graph gap
```

## 相關 Skill

- `lead-intelligence` 在更廣的目標探索和開發聯繫 pipeline 裡使用這個排名模型
- `connections-optimizer` 在決定要保留、修剪或新增誰時，使用同樣的橋接邏輯
- 起草任何引薦請求或直接聯繫之前，應該先執行 `brand-voice`
- `x-api` 提供 X 圖譜的存取，以及選用的執行路徑
