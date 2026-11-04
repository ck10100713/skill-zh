---
name: sox-testing
description: 產生 SOX 抽樣選取、測試工作底稿和控制評估。適用於規劃季度或年度 SOX 404 測試、為某個控制（營收、P2P、ITGC、結帳）抽樣、建立測試工作底稿範本，或評估並分類控制缺失。
argument-hint: "<control area> [period]"
---

# SOX 合規測試

> 如果看到不熟悉的佔位符，或需要確認哪些工具已連接，請見 [CONNECTORS.md](../../CONNECTORS.md)。

**重要**：這個指令協助處理 SOX 合規流程，但不提供稽核或法律意見。所有測試工作底稿和評估，在用於稽核文件之前，都應該由合格的財務專業人員審閱。

產生抽樣選取、建立測試工作底稿、記錄控制評估，並提供 SOX 404 財務報導內部控制的測試範本。

## 用法

```
/sox <control-area> <period>
```

### 參數

- `control-area` — 要測試的控制領域：
  - `revenue-recognition` — 營收循環控制（order-to-cash）
  - `procure-to-pay` 或 `p2p` — 採購與應付帳款控制（purchase-to-pay）
  - `payroll` — 薪資處理和薪酬控制
  - `financial-close` — 期末結帳和報導控制
  - `treasury` — 現金管理和資金控制
  - `fixed-assets` — 資本資產生命週期控制
  - `inventory` — 存貨評價和管理控制
  - `itgc` — IT 一般控制（存取、變更管理、營運）
  - `entity-level` — 實體層級和監控控制
  - `journal-entries` — 日記帳分錄處理控制
  - 任何特定的控制 ID 或名稱
- `period` — 測試期間（例如 `2024-Q4`、`2024`、`2024-H2`）

## 工作流程

### 1. 找出要測試的控制

依控制領域，找出關鍵控制。呈現控制矩陣：

| Control # | Control Description | Type | Frequency | Key/Non-Key | Risk | Assertion |
|-----------|-------------------|------|-----------|-------------|------|-----------|
| [ID]      | [Description]     | Manual/Automated/IT-Dependent | Daily/Weekly/Monthly/Quarterly/Annual | Key | High/Medium/Low | [CEAVOP] |

**控制類型：**
- **Automated（自動化）：** 由系統強制執行、不需人工介入的控制
- **Manual（人工）：** 由人員運用判斷執行的控制
- **IT-dependent manual（依賴 IT 的人工）：** 依賴系統產生資料的人工控制

**認定（CEAVOP）：**
- **C**ompleteness（完整性）：所有交易都已記錄
- **E**xistence/Occurrence（存在／發生）：交易確實發生
- **A**ccuracy（正確性）：金額記錄正確
- **V**aluation（評價）：資產／負債評價適當
- **O**bligations/Rights（義務／權利）：實體對資產有權利，對負債有義務
- **P**resentation/Disclosure（表達／揭露）：分類和揭露適當

### 2. 決定樣本數

依控制頻率和風險計算樣本數：

| Control Frequency | Population Size (approx.) | Recommended Sample |
|------------------|--------------------------|-------------------|
| Annual           | 1                        | 1 (test the instance) |
| Quarterly        | 4                        | 2 |
| Monthly          | 12                       | 2-4 (based on risk) |
| Weekly           | 52                       | 5-15 (based on risk) |
| Daily            | ~250                     | 20-40 (based on risk) |
| Per-transaction  | Varies                   | 25-60 (based on risk and volume) |

依以下因素調整：
- **風險等級：** 風險越高的控制，樣本要越大
- **前一年的結果：** 前一年有缺失的控制，需要更大的樣本
- **依賴程度：** 外部稽核人員會依賴的控制，可能需要更大的樣本

### 3. 產生抽樣選取

用適當的方法從母體中選取樣本：

**隨機選取**（交易層級控制的預設做法）：
- 產生亂數，從母體中選出特定項目
- 確保涵蓋整個期間

**系統性選取**（用於週期性控制）：
- 從隨機起點開始，以固定間隔選取項目
- 確保所有子期間都有代表

**目標式選取**（隨機選取的補充，用於風險導向測試）：
- 選取具有特定風險特徵的項目（大額、異常、期末）
- 記錄目標式選取的理由

呈現樣本：

```
SAMPLE SELECTION
Control: [Control ID] — [Description]
Period: [Testing period]
Population: [Count] items, $[Total value]
Sample size: [N] items
Selection method: [Random/Systematic/Targeted]

| Sample # | Transaction Date | Reference/ID | Amount | Selection Basis |
|----------|-----------------|--------------|--------|-----------------|
| 1        | [Date]          | [Ref]        | $X,XXX | Random          |
| 2        | [Date]          | [Ref]        | $X,XXX | Random          |
| ...      | ...             | ...          | ...    | ...             |
```

### 4. 建立測試工作底稿

為每個控制產生測試範本：

```
SOX CONTROL TESTING WORKPAPER
==============================
Control #: [ID]
Control Description: [Full description of the control activity]
Control Owner: [Role/title — to be filled by tester]
Control Type: [Manual/Automated/IT-Dependent Manual]
Frequency: [How often the control operates]
Key Control: [Yes/No]
Relevant Assertion(s): [CEAVOP]
Testing Period: [Period]

TEST OBJECTIVE:
To determine whether [control description] operated effectively throughout the testing period.

TEST PROCEDURES:
1. [Step 1 — What to inspect, examine, or re-perform]
2. [Step 2 — What evidence to obtain]
3. [Step 3 — What to compare or verify]
4. [Step 4 — How to evaluate completeness of performance]
5. [Step 5 — How to assess timeliness of performance]

EXPECTED EVIDENCE:
- [Document type 1 — e.g., signed approval form]
- [Document type 2 — e.g., system screenshot showing review]
- [Document type 3 — e.g., reconciliation with preparer sign-off]

TEST RESULTS:

| Sample # | Ref | Procedure 1 | Procedure 2 | Procedure 3 | Result | Exception? | Notes |
|----------|-----|-------------|-------------|-------------|--------|------------|-------|
| 1        |     | Pass/Fail   | Pass/Fail   | Pass/Fail   | Pass/Fail | Y/N    |       |
| 2        |     | Pass/Fail   | Pass/Fail   | Pass/Fail   | Pass/Fail | Y/N    |       |

EXCEPTIONS NOTED:
| Sample # | Exception Description | Root Cause | Compensating Control | Impact |
|----------|----------------------|------------|---------------------|--------|
|          |                      |            |                     |        |

CONCLUSION:
[ ] Effective — Control operated effectively with no exceptions
[ ] Effective with exceptions — Control operated effectively; exceptions are isolated
[ ] Deficiency — Control did not operate effectively
[ ] Significant Deficiency — Deficiency is more than inconsequential
[ ] Material Weakness — Reasonable possibility of material misstatement not prevented/detected

Tested by: ________________  Date: ________
Reviewed by: _______________  Date: ________
```

### 5. 提供常見控制範本

依控制領域，提供預先建好的測試步驟範本：

**營收認列：**
- 確認銷售訂單的核准和授權
- 確認交貨／履約證據
- 對照合約條款測試營收認列時點
- 確認定價是否符合合約／價目表
- 測試貸項通知單的核准和有效性

**採購到付款：**
- 確認採購單的核准和授權額度
- 確認三方比對（採購單、收貨單、發票）
- 測試供應商主檔變更控制
- 確認付款核准和職責分離
- 測試重複付款防範控制

**財務結帳：**
- 確認帳戶調節的完整性和及時性
- 測試日記帳分錄的核准和職責分離
- 確認管理階層對財務報表的審閱
- 測試合併和沖銷分錄
- 確認揭露事項檢查表已完成

**ITGC：**
- 測試使用者存取的授予和撤銷
- 確認特權存取的審閱
- 測試變更管理的核准和測試
- 確認批次作業的監控和例外處理
- 測試備份和復原程序

### 6. 記錄控制評估

分類任何已找出的缺失：

**Deficiency（缺失）：** 控制讓管理階層或員工無法及時預防或偵測錯誤陳述。要考慮：
- 發生錯誤陳述的可能性
- 潛在錯誤陳述的金額大小
- 是否有補償性控制

**Significant Deficiency（重大缺失）：** 嚴重程度低於重大弱點，但重要到值得負責監督的人注意的缺失（或缺失的組合）。

**Material Weakness（重大弱點）：** 缺失（或缺失的組合）導致有合理的可能性，重大錯誤陳述無法被及時預防或偵測。

### 7. 輸出

提供：
1. 所選領域的控制矩陣
2. 附方法說明文件的抽樣選取
3. 預先填好測試步驟的測試工作底稿範本
4. 結果記錄範本
5. 缺失評估框架（發現例外時）
6. 針對任何已註記缺失的建議補救行動
