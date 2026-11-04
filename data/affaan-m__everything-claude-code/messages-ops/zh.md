---
name: messages-ops
description: ECC 的證據優先即時訊息流程。使用者想讀簡訊或 DM、找回最近的一次性驗證碼、回覆前先檢查對話串，或要證明實際檢查了哪個訊息來源時使用。
metadata:
  origin: ECC
---

# Messages Ops

任務是即時訊息擷取時用這個：iMessage、DM、最近的一次性驗證碼，或後續追蹤前先檢查對話串。

這不是 email 的工作。如果主要的介面是信箱，改用 `email-ops`。

## Skill Stack

相關時，把這些 ECC 原生 skill 拉進流程：

- `email-ops`：訊息任務其實是信箱的工作時
- `connections-optimizer`：DM 對話串屬於對外人脈經營時
- `lead-intelligence`：即時對話串應該影響鎖定對象或暖路徑開發時
- `knowledge-ops`：對話串內容需要存成長期 context 時

## When to Use

- 使用者說「讀我的訊息」「看一下簡訊」「看 DM」或「找那個驗證碼」
- 任務取決於即時的對話串，或送到本機訊息介面的最近驗證碼
- 使用者要證明檢查了哪個來源或對話串

## Guardrails

- 先確定來源：
  - 本機訊息
  - X / 社群 DM
  - 另一個要透過瀏覽器才能進的訊息介面
- 沒講出來源，就不要宣稱檢查過某個對話串
- 如果有查證過的 helper 或標準路徑，不要即興去直接存取原始資料庫
- 如果驗證或 MFA 擋住該介面，回報確切的阻礙

## Workflow

### 1. Resolve the exact thread

做任何事之前，先確定：

- 訊息介面
- 寄件人 / 收件人 / 服務
- 時間範圍
- 任務是擷取、檢查，還是為回覆做準備

### 2. Read before drafting

如果任務可能變成對外的後續追蹤：

- 讀最新的一則收到的訊息
- 找出還沒收尾的事
- 需要的話，再交給對應的對外 skill

### 3. Handle codes as a focused retrieval task

一次性驗證碼：

- 先搜尋本機最近時間範圍內的訊息
- 可以的話，用服務或寄件人縮小範圍
- 找到驗證碼，或聚焦搜尋已經搜完，就停

### 4. Report exact evidence

回傳：

- 使用的來源
- 可以的話，附對話串或寄件人
- 時間範圍
- 確切狀態：
  - read
  - code-found
  - blocked
  - awaiting reply draft

## Output Format

```text
SOURCE
- message surface
- sender / thread / service

RESULT
- message summary or code
- time window

STATUS
- read / code-found / blocked / awaiting reply draft
```

## Pitfalls

- 不要把信箱的工作和 DM/簡訊的工作混在一起
- 沒講出來源，就不要宣稱已經擷取
- 要求只是找最近的驗證碼時，不要花時間做大範圍搜尋
- 驗證路徑被擋住時，不要一直重試卻不把阻礙講出來

## Verification

- 回覆有指名訊息來源
- 回覆包含寄件人、服務、對話串，或明確的阻礙
- 最終狀態明確且有界線
