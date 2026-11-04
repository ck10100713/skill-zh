---
name: "xborder-logistics"
description: "設計跨境電商的跨境物流策略，包括直郵、海外倉和保稅倉模式。當使用者需要把產品運送到國外、為跨境銷售選擇物流模式、優化運費，或在外國市場建立出貨履約時使用這個 skill，就算他們說的是「寄到東南亞」、「海外倉 vs 直接出貨」、「通關」或「縮短國際運送時間」也一樣。"
metadata:
  category: "WP-07 跨境電商"
  tags: ["cross-border", "logistics", "fulfillment", "international"]
---

# 跨境物流

## 框架

```
IRON LAW: Return Logistics Costs 3-5× More Than Outbound — Budget for It or Die
（鐵律：退貨物流的成本是出貨的 3-5 倍，不編預算就等著死）

Agent 會規劃出貨的運費，卻系統性地忽略退貨。
跨境的服飾退貨率落在 15-30%，而每次退貨的成本是出貨的 3-5 倍
（逆向通關、重新上架、再出口關稅、匯率損失）。
如果你的毛利吸收不了 4 倍成本下 20% 的退貨率，
不管正向出貨量多大，海外倉模式都是現金陷阱。
在決定履約模式「之前」，先算出損益兩平的退貨率。
```

### 三種物流模式

| 模式 | 運作方式 | 配送時間 | 每筆訂單成本 | 最低量 | 最適合 |
|-------|-------------|-------------|---------------|------------|----------|
| **直郵（Direct Mail）** | 每筆訂單從台灣直接寄給顧客 | 7-21 天 | 高（$8-25） | 1 筆訂單 | 測試市場、低量、高價商品 |
| **海外倉** | 事先把庫存放在目的國，在當地出貨 | 1-5 天 | 低（當地 $2-5）+ 倉儲費 | 每月 100 件以上 | 需求已驗證、需要有競爭力的配送速度 |
| **保稅倉** | 存放在保稅區，逐筆訂單通關 | 3-7 天 | 中（$5-10） | 每月 50 件以上 | 延後繳關稅、需求不確定 |

### 決策框架

```
Monthly orders to one country < 50 → Direct Mail
Monthly orders 50-500 → Consider Bonded Warehouse
Monthly orders > 500 → Overseas Warehouse justified
```

### 通關與關稅考量

| 因素 | 要知道什麼 |
|--------|-------------|
| **免稅額門檻（de minimis）** | 低於這個價值，免進口關稅（各國不同：多數東南亞是 $75，美國是 $400） |
| **HS Code** | 產品分類代碼決定關稅稅率。一定要弄「對」，HS code 錯了就會被罰 |
| **完稅總成本（Landed cost）** | 產品成本 + 運費 + 保險 + 關稅 + 稅金 = 顧客實際付的錢 |
| **文件** | 商業發票、裝箱單、原產地證明、特定產品的證書 |
| **禁限制品項** | 食品、化妝品、電子產品、醫療器材常常需要進口許可 |

### 履約夥伴類型

| 類型 | 服務 | 成本 | 掌控度 |
|------|---------|------|---------|
| **3PL（如 ShipBob、Boxme）** | 全方位服務：倉儲、揀貨包裝、出貨 | $$-$$$ | 低（外包） |
| **電商平台履約（Shopee/Lazada 倉庫）** | 平台處理物流 | 已含在佣金內 | 非常低 |
| **自營倉庫** | 自己的倉庫 + 人員 | 前期 $$$$ | 完全掌控 |
| **一件代發（Drop-shipping）** | 供應商直接出貨 | 最低 | 無 |

### 實作步驟

**階段 1：直郵（市場測試）**
1. 與國際快遞合作（DHL、FedEx、順豐）
2. 研究目的國的海關要求
3. 準備文件範本
4. 先用前 50 筆訂單測試

**階段 2：轉換到海外倉（擴張）**
5. 在目標市場選擇 3PL 或電商平台履約
6. 運送第一批庫存
7. 整合訂單管理：你的系統 → 倉庫 WMS
8. 監控：滿足率、配送時間、退貨率

**階段 3：優化**
9. 分析 SKU 層級的需求，優化預先備貨
10. 與物流夥伴談量大的費率
11. 評估用保稅倉做關稅優化

## 輸出格式

```markdown
# Cross-Border Logistics Plan: {Product} → {Destination}

## Current State
- Monthly orders: {N}
- Current model: {direct mail / none}
- Avg delivery time: {days}

## Recommended Model
- Model: {Direct Mail / Bonded / Overseas Warehouse}
- Rationale: {volume, speed requirement, cost}

## Cost Comparison
| Model | Per-Order Cost | Monthly Fixed | Total (at {N} orders) |
|-------|---------------|-------------|---------------------|
| Direct Mail | ${X} | $0 | ${X} |
| Overseas Warehouse | ${X} | ${X} | ${X} |

## Implementation Plan
| Phase | Action | Timeline |
|-------|--------|----------|
| 1 | {step} | {weeks} |
```

## 常見陷阱

- **退貨是隱藏的成本**：跨境退貨很貴，物流上也很複雜。要把退貨率假設（電商 5-15%）放進你的成本模型。如果用海外倉，要提供當地退貨。
- **通關延遲無法預測**：配送預估要留緩衝。對直郵來說，「7-14 個工作天」比「7 天」更誠實。
- **產品合規因國而異**：電子產品需要當地認證（例如馬來西亞的 SIRIM、台灣的 NCC）。食品需要進口許可。要在出貨「之前」查清楚。
- **匯率與關稅變動**：匯率和關稅稅率會變。計算完稅總成本時，要預留 5-10% 的毛利緩衝。
- **海外倉的庫存風險**：預先備貨賣不掉的庫存會卡住資金，還可能過時。一開始只放已驗證的暢銷品。

## 參考資料

- 各國海關要求，見 `references/customs-by-country.md`
- 3PL 業者比較，見 `references/3pl-comparison.md`
