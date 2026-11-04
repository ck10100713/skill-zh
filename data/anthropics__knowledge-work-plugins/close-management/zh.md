---
name: close-management
description: 管理月底結帳流程，包含任務排序、相依關係和狀態追蹤。用於規劃結帳日曆、追蹤結帳進度、找出阻礙，或依天數安排結帳活動的順序時。
user-invocable: false
---

# 結帳管理

**重要**：這個 skill 協助結帳管理的工作流程，但不提供財務建議。所有結帳活動都應該由合格的財務專業人員審閱。

月底結帳檢查清單、任務排序與相依關係、狀態追蹤，以及依天數整理的常見結帳活動。

## 月底結帳檢查清單

### 結帳前（月底最後 2 到 3 個工作日）

- [ ] 把結帳日曆和期限提醒寄給所有參與者
- [ ] 跟 AP、AR、薪資和資金部門確認截止（cut-off）程序
- [ ] 確認所有子系統運作正常（ERP、薪資、銀行）
- [ ] 完成初步銀行調節（除了最後一天的活動以外都處理）
- [ ] 檢視未結採購單，看有沒有需要估列的項目
- [ ] 確認薪資處理時程跟結帳時程一致
- [ ] 蒐集任何已知特殊交易的資訊

### 結帳第 1 天（T+1：月底後第一個工作日）

- [ ] 確認所有子帳模組都已完成期末處理
- [ ] 對已收貨／已收到服務但未開發票的項目，跑 AP 應計
- [ ] 過薪資分錄和薪資應計（如果薪資期間橫跨月底）
- [ ] 記錄到月底為止的現金收入與支出
- [ ] 過集團內部往來交易，並跟對方確認
- [ ] 用最終的銀行對帳單完成銀行調節
- [ ] 跑固定資產折舊
- [ ] 過預付費用攤銷

### 結帳第 2 天（T+2）

- [ ] 完成收入認列分錄和遞延收入調整
- [ ] 過所有剩餘的應計日記帳分錄
- [ ] 完成 AR 子帳對帳
- [ ] 完成 AP 子帳對帳
- [ ] 記錄存貨調整（如適用）
- [ ] 對外幣餘額過匯率重估分錄
- [ ] 開始做資產負債表科目對帳

### 結帳第 3 天（T+3）

- [ ] 完成所有資產負債表對帳
- [ ] 過對帳時發現的任何調整日記帳分錄
- [ ] 完成集團內部往來對帳和沖銷分錄
- [ ] 跑初步試算表和損益表
- [ ] 對損益表做初步 flux 分析
- [ ] 調查並解決重大差異

### 結帳第 4 天（T+4）

- [ ] 過稅務提列分錄（所得稅、銷售稅、財產稅）
- [ ] 完成權益變動表（股票報酬、庫藏股）
- [ ] 定案所有日記帳分錄（soft close）
- [ ] 產出財務報表草稿（損益表、資產負債表、現金流量表）
- [ ] 做詳細的 flux 分析並準備差異說明
- [ ] 管理階層審閱財務報表和關鍵指標

### 結帳第 5 天（T+5）

- [ ] 過管理階層審閱後的任何最終調整
- [ ] 定案財務報表（hard close）
- [ ] 在 ERP/GL 系統鎖定該期間
- [ ] 把財務報告資料包發給利害關係人
- [ ] 依實際結果更新預測／預估
- [ ] 進行結帳檢討會議，找出流程可改進之處

## 任務排序與相依關係

### 相依關係圖

任務依「前一項要先完成，後一項才能開始」來組織：

```
LEVEL 1 (No dependencies — can start immediately at T+1):
├── Cash receipts/disbursements recording
├── Bank statement retrieval
├── Payroll processing/accrual
├── Fixed asset depreciation run
├── Prepaid amortization
├── AP accrual preparation
└── Intercompany transaction posting

LEVEL 2 (Depends on Level 1 completion):
├── Bank reconciliation (needs: cash entries + bank statement)
├── Revenue recognition (needs: billing/delivery data finalized)
├── AR subledger reconciliation (needs: all revenue/cash entries)
├── AP subledger reconciliation (needs: all AP entries/accruals)
├── FX revaluation (needs: all foreign currency entries posted)
└── Remaining accrual JEs (needs: review of all source data)

LEVEL 3 (Depends on Level 2 completion):
├── All balance sheet reconciliations (needs: all JEs posted)
├── Intercompany reconciliation (needs: both sides posted)
├── Adjusting entries from reconciliations
└── Preliminary trial balance

LEVEL 4 (Depends on Level 3 completion):
├── Tax provision (needs: pre-tax income finalized)
├── Equity roll-forward
├── Consolidation and eliminations
├── Draft financial statements
└── Preliminary flux analysis

LEVEL 5 (Depends on Level 4 completion):
├── Management review
├── Final adjustments
├── Hard close / period lock
├── Financial reporting package
└── Forecast updates
```

### 關鍵路徑

關鍵路徑決定結帳最短需要多久。典型的關鍵路徑：

```
Cash/AP/AR entries → Subledger reconciliations → Balance sheet recs →
  Tax provision → Draft financials → Management review → Hard close
```

要縮短結帳時間：
- 把 Level 1 的分錄自動化（折舊、預付攤銷、標準應計）
- 在當月就先對帳（持續對帳）
- 把彼此獨立的對帳平行處理
- 訂清楚的期限，遲交要有後果
- 用標準化範本，減少對帳的準備時間

## 狀態追蹤與回報

### 結帳狀態儀表板

用下列屬性追蹤每個結帳任務：

| Task | Owner | Deadline | Status | Blocker | Notes |
|------|-------|----------|--------|---------|-------|
| [Task name] | [Person/role] | [Day T+N] | Not Started / In Progress / Complete / Blocked | [If blocked, what's blocking] | [Any notes] |

### 狀態定義

- **Not Started：** 任務還沒開始（可能在等相依的項目）
- **In Progress：** 任務正在進行
- **Complete：** 任務已完成，並且經過覆核／核准
- **Blocked：** 任務因為相依項目、缺資料或問題而無法繼續
- **At Risk：** 任務進行中，但可能趕不上期限

### 每日結帳狀態會議（建議）

結帳期間，每天開一場簡短（15 分鐘）的 standup：

1. **檢視狀態看板：** 逐一過未完成的任務，標出落後的
2. **找出阻礙：** 提出任何妨礙任務完成的問題
3. **重新分配或升級：** 調整負責人，或把阻礙升級處理以便盡快解決
4. **更新時程：** 如果有任務處於風險中，評估對整體結帳時程的影響

### 長期追蹤的結帳指標

| 指標 | 定義 | 目標 |
|--------|-----------|--------|
| 結帳天數 | 從期末到 hard close 的工作日數 | 逐步縮短 |
| soft close 之後的調整分錄數 | 管理階層審閱期間過的分錄 | 越少越好 |
| 遲交任務數 | 超過期限才完成的任務 | 零 |
| 對帳例外數 | 需要調查的調節項目 | 逐步減少 |
| 重編／更正數 | 結帳後才發現的錯誤 | 零 |

## 依天數整理的常見結帳活動

### 典型的 5 天結帳日曆

| 天數 | 主要活動 | 負責人 |
|-----|---------------|-------------|
| **T+1** | 現金分錄、薪資、AP 應計、折舊、預付攤銷、集團內部往來過帳 | staff accountant、薪資 |
| **T+2** | 收入認列、剩餘應計、子帳對帳（AR、AP、FA）、匯率重估 | 收入會計、AP/AR、資金部門 |
| **T+3** | 資產負債表對帳、集團內部往來對帳、沖銷、初步試算表、初步 flux | 會計團隊、合併報表 |
| **T+4** | 稅務提列、權益變動表、財務報表草稿、詳細 flux 分析、管理階層審閱 | 稅務、Controller、FP&A |
| **T+5** | 最終調整、hard close、期間鎖定、發送報告資料包、更新預測、檢討會議 | Controller、FP&A、財務主管 |

### 加速結帳（目標 3 天）

給想更快結帳的組織：

| 天數 | 主要活動 |
|-----|---------------|
| **T+1** | 所有 JE 過帳（自動加手動）、所有子帳對帳、銀行調節、集團內部往來對帳、初步試算表 |
| **T+2** | 所有資產負債表對帳、稅務提列、合併、財務報表草稿、flux 分析、管理階層審閱 |
| **T+3** | 最終調整、hard close、報告資料包、更新預測 |

**3 天結帳的前提條件：**
- 週期性日記帳分錄自動化（折舊、攤銷、標準應計）
- 當月就持續對帳（不要全部擠到月底）
- 集團內部往來沖銷自動化
- 結帳前的活動在月底前就完成（截止、應計估計）
- 團隊被充分授權、責任歸屬清楚、交接越少越好
- 子系統即時或近即時整合

## 結帳流程改善

### 常見瓶頸與解法

| 瓶頸 | 根本原因 | 解法 |
|-----------|-----------|---------|
| AP 應計太晚 | 在等各部門確認支出 | 建立持續的應計估算；訂截止期限 |
| 手動日記帳分錄 | 週期性分錄每個月都手動準備 | 在 ERP 裡把標準週期性分錄自動化 |
| 對帳很慢 | 每個月都從零開始 | 建立持續／滾動式對帳 |
| 集團內部往來延遲 | 在等對方確認 | 把內部往來比對自動化；訂更嚴格的期限 |
| 管理階層審閱時又有變動 | 審閱時才發現大額調整 | 改善初步審閱流程；授權團隊更早抓出問題 |
| 佐證文件缺漏 | 結帳時才在趕文件 | 整個月都持續維護文件 |

### 結帳檢討問題

每次結帳後，問這幾題：
1. 這次結帳有什麼做得好、值得繼續的？
2. 什麼花的時間比預期久，為什麼？
3. 遇到了哪些阻礙，怎麼預防？
4. 財務結果裡有沒有哪些意外，是我們本來應該更早發現的？
5. 下個月有什麼可以自動化或簡化？
