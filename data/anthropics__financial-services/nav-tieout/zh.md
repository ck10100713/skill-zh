---
name: nav-tieout
description: 把 LP 對帳單核對到基金的 NAV 資料包：用 NAV 組成項目重新計算該 LP 的資本帳戶，並標出任何對不上的項目。在發送 LP 對帳單之前使用。
---

# NAV 核對

給定一份產生出來的 LP 對帳單和該期間的 NAV 資料包（透過 nav MCP），獨立重新計算該 LP 的資本帳戶，並逐項比較。

> **產生出來的對帳單是被測試的對象。** NAV 資料包才是真實的來源。

## 重新計算 LP 資本帳戶

```
Beginning capital (prior statement ending)
  + Contributions (capital calls paid this period)
  − Distributions (cash + in-kind)
  + Allocated net income / (loss)
      = LP% × (realized + unrealized P&L − management fee − fund expenses)
  − Carried interest allocation (if crystallized this period)
Ending capital
```

每個輸入都從 NAV 資料包取得：LP 出資承諾比例、基金層級的損益組成、費用合計、waterfall 輸出。

## 比較

對對帳單上的每一項，與你重新計算的值比較。容許範圍：`0.01`。每一筆不吻合的項目，都要註明是哪個輸入造成的（例如「allocated P&L differs — statement used 12.40% ownership, NAV pack shows 12.38% after the Q1 transfer」）。

## 額外檢查

- 這份對帳單的期末資本 = 下一期草稿的期初資本（如果有的話）。
- 所有 LP 的期末資本加總 = 基金 NAV（四捨五入內）。
- 出資承諾、未出資和可召回的數字，與出資承諾登記冊一致。

## 輸出

每一項的通過／不通過、重新計算的值與對帳單上的值並列，以及一份標記清單。不要編輯對帳單，由發布人員在審閱後依標記處理。
