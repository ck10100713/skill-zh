---
name: roll-forward
description: 為資產負債表科目建立 roll-forward 明細表：期初餘額加上本期活動、減去迴轉，等於期末餘額，且每個組成項目都對應到總帳（GL）。適用於月結套件和稽核支援。
---

# Roll-forward

給定一個科目（或科目群組）、實體和期間，產出一份從期初連到期末的 roll-forward。

## 結構

```
Beginning balance (per prior-period close)      X
  + Additions / new activity                    A
  + Accruals booked this period                 B
  − Reversals of prior accruals                (C)
  − Payments / settlements                     (D)
  ± Reclasses / adjustments                     E
  ± FX translation                              F
Ending balance (per GL at period end)           Y
```

## 每一行都要對得上

- **期初**：上一期的結帳套件，或上一期期末日的 GL 餘額。
- **每一條活動項目**：透過 internal-gl MCP 做 GL 查詢（科目 + 日期區間 + 傳票來源篩選）。要引用該查詢。
- **期末**：期末日的 GL 餘額。

這份明細表**一定要能加總**：`X + A + B − C − D + E + F = Y`。如果加不起來，差額就是未解釋項目，要攤出來講，不准硬塞數字把它補平。

## 輸出

roll-forward 表要附一欄「對應來源（ties to）」，每一行都引用 GL 查詢或文件，再加上加總檢查（通過／未通過，有未解釋差額的話要列出金額）。
