---
name: "algo-sc-routing"
description: "解車輛路徑問題（vehicle routing problem），在載重與時間限制下最佳化配送路線。當使用者需要規劃配送路線、降低運輸成本或提高車隊使用率時就用這個 skill，即使他們說的是「配送路線最佳化」「車隊排程」或「最小化行駛距離」。"
metadata:
  category: "WP-41 供應鏈演算法"
  tags: ["supply-chain", "vrp", "routing", "logistics"]
---

# Vehicle Routing Problem (VRP)

## Overview

VRP 要幫一整個車隊決定最佳路線，從倉庫（depot）出發服務一批客戶，讓總距離或總成本最小。它是 NP-hard，精確解只有在小規模時（< 25 個節點）才做得到。實務上用啟發式演算法（Clarke-Wright savings、sweep）或元啟發式演算法（模擬退火、基因演算法）。

## When to Use

**觸發條件：**
- 為一整個車隊規劃每日配送路線
- 在載重限制下，最小化總行駛距離／時間
- 在多輛車之間最佳化路線分配

**不適用的情況：**
- 單一車輛的路線最佳化（用 TSP solver）
- 訂單持續進來的即時動態路徑規劃（用 online algorithm）

## Algorithm

```
IRON LAW: VRP Is NP-Hard — Exact Solutions Don't Scale
For n customers, the solution space grows factorially. Exact methods
(branch and bound) work for n < 25. For real-world problems (50-1000+
customers), heuristics are REQUIRED. A good heuristic solution within
5% of optimal is far more valuable than an optimal solution that takes
hours to compute.
```

### Phase 1: Input Validation
收集：倉庫位置、客戶位置與需求量、車輛載重、車輛數量、時間窗（如果有）、距離／時間矩陣。
**Gate：** 所有位置都已經地理編碼（geocode），單一客戶的需求量不超過車輛載重。

### Phase 2: Core Algorithm
**Clarke-Wright Savings 啟發式演算法：**
1. 一開始每個客戶各自一條路線（depot → customer → depot）
2. 計算合併每一對路線的節省量：s(i,j) = d(depot,i) + d(depot,j) - d(i,j)
3. 把節省量由大到小排序
4. 在載重限制允許的前提下，貪婪地合併路線
5. 用 2-opt（交換路線內的邊）和 or-opt（在路線之間移動客戶）做改善

### Phase 3: Verification
檢查：每個客戶剛好被訪問一次、沒有車輛超載、所有路線都從 depot 出發並回到 depot。把總距離和下界（lower bound）比較。
**Gate：** 所有限制都滿足，解在下界的 10% 以內。

### Phase 4: Output
回傳各條路線，包含順序、距離和載重。

## Output Format

```json
{
  "routes": [{"vehicle": 1, "sequence": ["depot", "C3", "C7", "C1", "depot"], "distance_km": 45, "load": 850, "capacity": 1000}],
  "summary": {"total_distance_km": 180, "vehicles_used": 4, "utilization_avg": 0.82},
  "metadata": {"customers": 30, "method": "clarke_wright_2opt", "computation_ms": 150}
}
```

## Examples

### Sample I/O
**輸入：** 10 個客戶，2 輛車（載重 = 500），depot 在中心
**預期結果：** 2 條路線，各服務約 5 個客戶，用地理分群把總距離降到最小。

### Edge Cases
| 輸入 | 預期結果 | 原因 |
|-------|----------|-----|
| 某個客戶的需求量 > 載重 | 無解，或拆分配送 | 需要用拆分配送的 VRP 變體 |
| 所有客戶都在同一個地點 | 路線極簡，趟數受載重限制 | 距離可以忽略，趟數由載重決定 |
| 時間窗很緊 | 需要更多車輛 | 時間限制可能讓路線無法滿載 |

## Gotchas

- **距離矩陣的品質**：道路距離 ≠ 歐幾里得距離。實務上的路徑規劃要用真實道路網路的距離（Google Maps、OSRM）。
- **時間窗會增加複雜度**：VRPTW（帶時間窗的 VRP）難很多。客戶要求特定配送時段，會把路線切碎。
- **動態 vs 靜態**：真實世界會有取消、加單和路況變化。先規劃靜態路線，但要允許動態重新最佳化。
- **司機限制**：最長駕駛時數、休息規定和加班成本，都是基本模型裡沒有的實務限制。
- **回到 depot**：標準 VRP 假設路線最後要回到 depot。開放式 VRP（路線結束在最後一個客戶）需要不同的建模方式。

## References

- Clarke-Wright 演算法的實作，請見 `references/clarke-wright.md`
- 元啟發式方法（SA、GA），請見 `references/metaheuristics.md`
