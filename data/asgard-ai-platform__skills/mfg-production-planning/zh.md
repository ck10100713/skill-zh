---
name: "mfg-production-planning"
description: "用 MPS（主生產排程）、MRP（物料需求規劃）和產能規劃設計生產計畫。使用者需要排生產、規劃物料採購、讓產能和需求取得平衡，或最佳化生產排序時使用，就算他們說的是「我們趕不上訂單」、「什麼時候該訂料」、「生產排程」或「下一季的需求要怎麼規劃」也一樣。"
metadata:
  category: "WP-03 製造業"
  tags: ["manufacturing", "production-planning", "mrp", "scheduling"]
---

# 生產規劃（MPS/MRP）

## 框架

```
IRON LAW: Plan Hierarchically — Demand → MPS → MRP → Shop Floor

Production planning flows TOP-DOWN:
1. Demand forecast / customer orders → what to make, when
2. MPS → master schedule for finished goods
3. MRP → material and component requirements (what to buy, when)
4. Shop floor scheduling → which machine, which sequence

Skipping levels (going from demand forecast directly to shop floor)
creates chaos — material shortages, capacity conflicts, missed deliveries.
```

### 規劃階層

| 層級 | 計畫 | 時間範圍 | 粒度 | 決定什麼 |
|-------|------|---------|-------------|---------|
| **策略層** | S&OP（銷售與營運規劃） | 12-18 個月 | 每月、產品家族 | 產能投資、人力規劃 |
| **戰術層** | MPS（主生產排程） | 3-6 個月 | 每週、最終產品 | 每週要生產什麼 |
| **作業層** | MRP（物料需求規劃） | 4-12 週 | 每日、零組件／物料 | 要訂什麼、什麼時候、訂多少 |
| **執行層** | 現場排程（Shop Floor Scheduling） | 1-2 週 | 每小時、工作中心 | 順序、機台指派 |

### MPS 流程

1. **輸入**：需求預測 + 客戶訂單 + 目前庫存 + 安全庫存目標
2. **邏輯**：每一週都計算：需要生產量 = 需求 - 期初庫存 - 預定到貨 + 安全庫存
3. **輸出**：每個成品每週的計畫生產量
4. **限制**：不能超過可用產能（做粗略產能規劃的檢查）

### MRP 流程

1. **輸入**：MPS（要做什麼）+ BOM（物料清單，也就是它是用什麼做的）+ 庫存狀態 + 前置時間
2. **邏輯**：「展開」BOM，針對每個成品，計算每個零組件／物料必須什麼時候下單才趕得上
3. **輸出**：附有日期和數量的計畫採購單和生產單
4. **關鍵計算**：下單日期 = 需求日期 - 前置時間

### 排程演算法

| 演算法 | 規則 | 最適合 |
|-----------|------|-----------|
| **FCFS**（先到先做） | 依收到的順序處理 | 複雜度低、公平性重要 |
| **SPT**（最短加工時間） | 最短的工作先做 | 最小化平均流程時間 |
| **EDD**（最早到期日） | 到期日最急的先做 | 最小化延遲交貨 |
| **瓶頸優先** | 先排限制條件，其餘從屬於它 | 受產能限制的環境（TOC 邏輯） |

### SMED（單分鐘換模）

縮短換線時間來提高彈性：
1. 把內部設置（機器停止時）和外部設置（運轉時就能做）分開
2. 盡可能把內部轉成外部
3. 簡化剩下的內部步驟
4. 練習並標準化

## 輸出格式

```markdown
# Production Plan: {Product/Period}

## Demand vs Capacity
| Week | Demand | Available Capacity | Gap |
|------|--------|-------------------|-----|
| W1 | {units} | {units} | {+/-} |

## Master Production Schedule
| Week | Product A | Product B | Product C | Total |
|------|----------|----------|----------|-------|
| W1 | {units} | {units} | {units} | {units} |

## Material Requirements
| Material | Quantity | Order Date | Supplier | Lead Time |
|----------|---------|-----------|----------|-----------|
| {material} | {qty} | {date} | {supplier} | {days} |

## Scheduling
| Work Center | Mon | Tue | Wed | Thu | Fri |
|------------|-----|-----|-----|-----|-----|
| {center} | {job} | {job} | ... | ... | ... |
```

## 注意事項

- **預測準確度限制了一切**：MPS/MRP 的品質只會跟需求預測一樣好。要追蹤預測準確度（MAPE），並依預測誤差的比例建立安全庫存。
- **前置時間的變異會毀掉計畫**：如果供應商的前置時間是「2-6 週」（變異 4 週），你就需要為最壞的情況備安全庫存。要透過供應商管理來降低變異。
- **BOM 的準確度對 MRP 至關重要**：BOM 錯了，就會訂錯物料。每季都要稽核 BOM。
- **凍結區**：MPS 的前 1-2 週應該「凍結」（不改），讓執行保持穩定。在凍結區內改動，會讓混亂在整個系統裡連鎖擴散。
- **有限 vs 無限產能**：基本的 MRP 假設產能是無限的（忽略機台限制）。一定要在 MRP 的輸出上再疊一層產能檢查（粗略或詳細）。

## 參考資料

- S&OP 流程設計請看 `references/sop-process.md`
- 需求預測方法請看 `references/demand-forecasting.md`
