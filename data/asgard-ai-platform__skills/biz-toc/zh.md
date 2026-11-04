---
name: "biz-toc"
description: "用限制理論（TOC）找出並管理系統瓶頸。當使用者需要找出限制產出的因素、最佳化受限的流程、套用五大聚焦步驟，或導入鼓-緩衝-繩（Drum-Buffer-Rope）排程時使用。就算使用者只說「我們的產出卡住了」、「瓶頸在哪」或「為什麼產量上不去」也要用。"
metadata:
  category: "WP-16 商學院—營運"
  tags: ["operations", "toc", "bottleneck", "throughput"]
---

# 限制理論（TOC）

## 概述

TOC 主張每個系統至少有一個限制（瓶頸），它決定了整體產出的上限。改善非瓶頸的流程「不會」提升系統產出，只有改善瓶頸才會。五大聚焦步驟提供一套系統化的方法來找出並管理限制。

## 框架

```
IRON LAW: The System Is Only as Strong as Its Weakest Link

Improving a non-bottleneck process is a WASTE of resources — it produces
more work-in-progress that piles up at the bottleneck. Before optimizing
any process, verify it IS the bottleneck. If it's not, stop.
```

### 五大聚焦步驟

1. **IDENTIFY（找出）** 限制：找到瓶頸（使用率最高、佇列最長、在製品（WIP）堆積最多的地方）
2. **EXPLOIT（善用）** 限制：不增加資源的前提下，把瓶頸的產出榨到最大（減少停機、消除這個步驟的浪費、確保它絕不會缺料）
3. **SUBORDINATE（配合）** 其他一切：讓所有其他流程配合瓶頸的節奏。非瓶頸「不該」全速運轉。
4. **ELEVATE（提升）** 限制：如果善用還不夠，就投資擴大瓶頸的產能（加設備、增聘人力、外包）
5. **REPEAT（重複）**：提升之後，限制可能轉移到別的流程。回到步驟 1。

### 鼓-緩衝-繩（DBR）排程

| 元素 | 是什麼 | 目的 |
|---------|-----------|---------|
| **鼓（Drum）** | 瓶頸的節奏 | 決定整個系統的節拍 |
| **緩衝（Buffer）** | 瓶頸前面的時間緩衝 | 確保瓶頸永遠不會沒工作做 |
| **繩（Rope）** | 在起點釋出工作的訊號 | 把投料速度綁在瓶頸的節奏上，藉此控制 WIP |

### 產出會計（TOC 財務指標）

| 指標 | 定義 |
|--------|-----------|
| **產出（Throughput，T）** | 營收 - 真正的變動成本（只含原料） |
| **投資（Investment，I）** | 卡在系統裡的錢（庫存、設備） |
| **營運費用（Operating Expense，OE）** | 營運系統的所有其他成本 |
| **淨利** | T - OE |
| **ROI** | (T - OE) / I |

## 輸出格式

```markdown
# TOC Analysis: {System/Process}

## System Map
{Process A} → {Process B} → {**Process C (bottleneck)**} → {Process D} → Output

## Constraint Identification
- Bottleneck: {process step}
- Evidence: {utilization %, queue length, WIP accumulation}
- Current throughput: {units/period}

## Five Focusing Steps
| Step | Action | Expected Impact |
|------|--------|----------------|
| 1. Identify | {bottleneck location} | — |
| 2. Exploit | {optimize without investment} | +X% throughput |
| 3. Subordinate | {pace other processes} | Reduce WIP by X% |
| 4. Elevate | {investment if needed} | +X% throughput |
| 5. Repeat | {new constraint location} | — |

## DBR Implementation
- Drum: {bottleneck pace = X units/hour}
- Buffer: {X hours of WIP before bottleneck}
- Rope: {release new work every X minutes}
```

## 範例

### 正確的做法
**情境：** 一條 5 個站點的 PCB 組裝線做 TOC 分析
- 各站產能：錫膏印刷（100/hr）→ 取放（80/hr）→ **回焊爐（50/hr）** → 檢驗（90/hr）→ 包裝（120/hr）
- 瓶頸：回焊爐（50/hr），產能最低、使用率最高
- **善用**：把爐子換線時間從 30 分鐘壓到 10 分鐘，有效產能 +15%
- **配合**：把取放降到 55/hr（不要在爐前多做出一堆 WIP）
- **提升**：必要的話，再加第二台回焊爐，產能翻倍

### 錯誤的做法
- 買了更快的取放機（80→120/hr），系統產出完全沒變，因為回焊爐（50/hr）還是瓶頸。投資白花了，違反 Iron Law。

## 常見陷阱

- **限制不一定是實體的**：市場需求、政策或管理層的注意力，都可能是真正的限制。如果工廠能生產 1000 個但只賣得掉 500 個，限制就是市場。
- **瓶頸會移動**：提升一個限制之後，瓶頸會轉移。團隊常常慶祝完就忘了步驟 5（重複）。
- **「配合」很反直覺**：讓非瓶頸機器不滿載運轉，感覺很浪費。其實不是：非瓶頸過度生產只會做出一堆 WIP 把系統塞住。
- **TOC 與精實（Lean）**：精實是到處消除浪費，TOC 只專注在限制上。兩者互補：用 TOC 找出「該把力氣放在哪裡」，用精實最佳化「怎麼做」。

## 參考資料

- DBR 的實作細節，見 `references/dbr-scheduling.md`
