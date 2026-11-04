---
name: operator-approval-loop
description: 給 agent 起草的對外訊息用的操作員核准合約，包含內部歸檔通知、有 hash 的草稿、以 epoch 為鍵的決定、持久的投遞認領和收據，以及草稿前的基準關卡。當 agent 起草訊息給外部交易對手，而且每一則在送出前都必須由人類操作員核准、駁回或引導時使用。
---

# Operator Approval Loop

和外部交易對手對話的 agent，絕不該憑自己的判斷送出訊息，
而且應該在內部持續讓操作員知情。這個 skill 定義了合約：每一份對外草稿
都歸檔成一項義務，由操作員針對確切的文字做決定，
再由投遞帳本證明實際送出了什麼。

## When to Use

- agent 在共用頻道、email 或聊天裡，起草給客戶、供應商、投資人或夥伴的回覆，
  而且送出前必須由人類核准。
- 你需要稽核軌跡，把每一則已送出的訊息，連到確切的草稿
  文字、核准它的操作員，和決定的時間。
- 你看過過期的核准放行了改寫後的草稿，或兩個 worker
  把同一則已核准的訊息送了兩次。
- 草稿一再向交易對手詢問帳本裡已經有的事實。

## How It Works

### Objects

| 物件 | 意義 |
| --- | --- |
| Obligation | 我們欠交易對手的一件事。狀態依序是 `drafted`，然後 `approved` 或 `rejected`，然後 `sent`。帶有 `direction`、`counterparty`、`channel` 和一個 `updated_at` epoch。 |
| Draft | 附屬的資料列，存放確切的草稿文字、該文字的 sha256、來源座標（平台、頻道、討論串、使用者），以及優先順序（P0 到 P3）。每個義務一份，重新歸檔時會被取代。 |
| Decision | 操作員的核准或駁回，連同操作員 id、nonce 和它所針對的草稿 epoch 一起記錄。 |
| Approval snapshot | 由已授權的決定寫入者記錄的、不可變的文字、hash、epoch 和目的地。缺少 snapshot 就不能授予投遞許可。 |
| Claim | 持久的保留，帶有隨機 token 和狀態；每個義務最多只有一個有效的 claim。 |
| Delivery | 帳本資料列，證明某一組（義務、決定）的一次送出或通知。 |

參考的 schema 在 [references/approval-ledger.sql](references/approval-ledger.sql)。

### Filing a draft

1. 清理輸入。去掉控制字元、把單行欄位裡的空白合併，並強制長度上限
   （草稿、摘要、context、交易對手）。空的或過長的欄位會被拒絕，不會默默截斷。
2. 執行基準關卡（見下）。它可能拒絕這次歸檔。
3. 用 sha256 對草稿文字做 hash。hash 的前綴會放進摘要，
   讓核准面板顯示它正在核准哪一份文字。
4. Upsert。如果同一組（交易對手、頻道）已經有一個開啟中、狀態為 drafted 的義務，
   就取代 draft 附屬資料，並推進義務的 `updated_at`。這個推進就是
   epoch 的輪替：任何綁在舊 epoch 的決定，都再也不能放行新的文字。
   否則就插入一個狀態為 `drafted` 的新義務。
5. 歸檔收據只送到已設定、已驗證的內部營運目的地。如果來源就是那個內部目的地，就在那裡確認。
   「絕不沉默」指的是內部回報，不是自動對外回覆。
   草稿 hash、核准狀態、操作員身分和工作流程 metadata，
   都不要放進交易對手看得到的頻道。未知或未分類的來源保持安靜；
   私訊不會自動算是內部。

如果沒有已驗證的內部目的地可用，就把歸檔結果留在
內部的工具結果或操作員介面裡。絕不退回到外部或未知的來源。
外人看得到的工具結果，不算內部介面。

歸檔草稿並不授權對外回應。任何政策允許的
釐清問題或中性回應，都是另外的對外決定，要受
counterparty-channel-discipline 裡既有的 mention、頻道、僅草稿、凍結和 never 限制約束。
它不能揭露內部的核准 metadata。

### Baseline gate

歸檔任何草稿之前，先查詢該交易對手目前的基準
（時序帳本、合約庫或 CRM）：

- 紀錄上有已簽署或已交付的合約：拒絕這次歸檔，並附上證據
  和建議。簽約之後還向交易對手詢問規格，正是這個關卡要阻止的
  失誤。
- 操作員覆寫：`force_despite_signed_contract` 讓歸檔通過，
  並在草稿 context 裡蓋上 `[BASELINE_OVERRIDE_SIGNED_CONTRACT]`。
- 關卡服務連不上：歸檔繼續進行，並在 context 裡蓋上
  `[BASELINE_CHECK_UNAVAILABLE]`。面板看得出防護是關著的。
  失敗絕不會默默停用關卡。
- 有事實可用時，把最新的幾筆以 `[BASELINE FACTS: ...]` 摘要的形式附到 context，
  讓草稿帶著當下的真相出現。

### Deciding

核准面板列出狀態為 `drafted`、方向為 `we_owe_them` 的義務。核准或駁回
會寫入一筆帶有草稿 epoch（`draft_updated_ts`）的決定資料列，並在同一個
交易裡翻轉義務的狀態。epoch 與目前 `updated_at` 不符的決定，
是過期的，不能放行任何東西。

對於已經授權的核准決定，同一個交易會插入一筆
不可變的 `obligation_approval_snapshots` 資料列：決定和義務的 ID、
目前的草稿 epoch、確切的文字和 SHA-256、平台/頻道/討論串，以及種類
`draft_sent`。決定的寫入者在寫入之前必須先確立授權；
參考實作絕不驗證操作員，也不憑空製造決定。
參考實作不會啟用或擴大自動核准政策。
沒有 snapshot 的舊決定，需要明確的對帳或新的
核准；絕不要根據目前可變動的草稿去補發許可。

### Delivering

SQLite 的參考實作是 [references/approval_claims.py](references/approval_claims.py)。
它授予投遞許可，但絕不呼叫傳輸層。使用從 SQL fixture 初始化好的既有本機參考
資料庫；這個模組不會套用 schema 或正式環境的 migration。只有受信任的決定寫入者才能
填入核准紀錄。所有寫入者都必須啟用 foreign key 和遞迴 trigger，
並遵守 schema 的防護；對資料庫的管理層級竄改不在這個模型的範圍內。

1. 找出已綁定的、已核准的草稿。找到不等於許可。`claim()` 會開啟
   自己的 `BEGIN IMMEDIATE` 交易，對照 snapshot 驗證目前已核准的 epoch、
   確切文字、計算出來的 SHA-256 和完整的目的地，
   並在回傳 token 之前插入一筆唯一的 claim。發生衝突時，worker
   在傳輸之前就會停下來。已完成的收據不能再被 claim。
2. `begin_dispatch()` 會重新驗證綁定，並用 token 把 `claimed`
   以原子方式改成 `dispatching`。只有贏得的那個呼叫者，在 commit 之後才會收到
   確切的 `draft_text` 和目的地。絕不要重新產生文字、為了傳輸而重讀
   可變動的附屬資料，或把這份 payload 拿去做另一次嘗試。
   巢狀的呼叫者交易會被拒絕；許可不能取決於之後呼叫者的 commit。
   傳輸期間不會有任何資料庫交易保持開啟。
3. 確認成功的結果交給 `complete()`，它會以原子方式記錄
   投遞座標、把 claim 標成已投遞，並把義務翻成
   `sent`。相同的完成是 no-op；衝突的座標會失敗。
   收據的 UNIQUE 鍵只對紀錄去重，不是對先前的外部效果去重。
4. 例外、逾時、begin-dispatch 之後 worker 死亡，或收據寫入失敗，
   都會留下被擋住的嘗試。`mark_unknown()` 記錄不確定的狀態。
   未知的 claim 永不過期、不重開、不自動重試，也不允許
   該義務的另一個決定繞過它們。受信任的呼叫者可以用 `reconcile()`，
   帶上已確認成功的座標和證據；這個模組不會驗證
   那份證據。沒有收據不代表沒有送達。

這個保證是每個已核准的決定只有一次自動投遞嘗試，不是
外部投遞恰好一次。在 begin-dispatch 之後、傳輸之前當掉，
可能留下零次送出和一個被扣住的 claim。要把未知的結果釋放出來做新的
嘗試，需要對原本的執行者做 fencing，並驗證服務商的
語意；這個參考實作刻意不提供這種重試操作。

| Claim 狀態 | 允許的下一個狀態 |
| --- | --- |
| claimed | dispatching，或在投遞之前 cancelled |
| dispatching | delivered 或 unknown |
| unknown | 只能透過受信任的對帳變成 delivered |
| delivered、cancelled | 終態；決定的鍵不能再用 |

claim 有效期間，資料庫的防護會凍結義務、草稿和決定的
寫入，包括取代。Snapshot 和 claim 不能被刪除。要重新歸檔之前，
先用 token 取消已 claim 的操作；之後那個過期的 token 就什麼都授予不了。
投遞開始之後，新的編輯或撤銷要先擱著等對帳。
這是把變更序列化，而不是假裝能收回已經在進行中的操作。

被駁回的決定，以及沒有 draft 附屬資料/snapshot 的舊資料列，絕不會進入
這條對外草稿送出的路徑。把它們回報到內部的操作員介面，交給
人工處理。內部收據的頁尾維持在內部：
`approved by <operator> · receipt <decision_id> · draft sha256 <prefix>`。
絕不要修改已核准的對外文字，去附加工作流程 metadata。

針對性的本機驗證用的是暫時的資料庫、獨立的連線和一個
模擬的嘗試計數器，不是服務商，也不是真的訊息：
`python3 -m unittest discover -s tests/skills -p 'test_approval_delivery_claims.py'`。
這些測試需要 Python 3.11+ 並支援 SQLite 序列化；參考實作
只用標準函式庫。既有的 desk-pattern 合約檢查仍然是
另外的相容性檢查。

### Time-boxed auto-approval (optional)

草稿可以帶 `auto_send_after`（epoch 秒數）。一次掃描會核准
期限已過、而且沒有任何決定的草稿，記錄操作員為 `auto-ttl`，然後
投遞走正常的路徑。操作員的動作永遠優先：決定會在
掃描看到之前就翻轉狀態，而重新歸檔會輪替
epoch，並移動或清除期限。掃描會在寫入交易裡重新檢查狀態和 epoch，
所以競爭會以 no-op 收場。沒有期限的草稿永遠維持硬性關卡。

### Signal linkage

草稿可以指名它所回應的進來的義務（`signal_obligation_id`）。
這是量測延遲（進來的訊號到起草的回應）唯一真實的連結，
也讓 SLA 掃描把那個進來的項目視為已回覆。
如果被參照的資料列不存在，就拒絕這次歸檔。

## Examples

### File a draft

```text
file_request(
  draft="Thanks, we can hold the slot until Friday. Which start date works?",
  counterparty="acme-supplier",
  context="reply to delivery window question",
  origin_platform="slack", origin_channel="#acme-shared",
  origin_thread="1712345678.000100", priority="P1",
  signal_obligation_id=412)
-> {obligation_id: 431, draft_sha256: "9f2c...", refiled: false}
```

已設定、已驗證的內部營運目的地會看到：
`Draft filed for approval (P1, sha 9f2c8a1b). Waiting on operator.`
交易對手看得到的來源頻道不會收到歸檔通知。如果沒有已驗證的
內部目的地可用，收據就留在內部的工具結果
或操作員介面裡，沒有外部的退路。

### Re-file after a steer

操作員要求更短的草稿。對同一組
（交易對手、頻道）再歸檔一次，會回傳 `refiled: true`，附屬資料的文字和 hash
改變，`updated_at` 往前推。在舊面板資料列上按下的核准，
帶的是舊 epoch，會被忽略。

### Gate refusal

```text
DeskApprovalError: baseline gate refused this draft: the ledger shows a
signed contract for 'acme-supplier'. Evidence: master agreement executed
2026-08-14. Recommendation: do not ask. Re-file with
force_despite_signed_contract=true if this is genuinely a new thread.
```

### Delivery footer in an internal channel

```text
Confirmed for Friday, start date 2026-09-08.
approved by operator-a · receipt 118 · draft sha256 9f2c8a1b2d3e4f50
```

## Invariants to test

- 歸檔收據只會送到已設定、已驗證的內部營運；來源只有在它
  就是那個已驗證的內部目的地時才會收到。
- 未知的來源保持安靜。內部目的地不可用時，使用
  內部的工具結果或操作員介面，沒有外部的退路。
- 同一組（交易對手、頻道）歸檔兩次，只會產生一個義務、兩個 epoch。
- epoch 過期的決定，絕不會產生投遞資料列。
- 兩個同時的 claim 者，只會產生一個投遞許可；輸的一方絕不嘗試傳輸。
- 未知的結果和收據寫入失敗，絕不會啟用自動重試。
- 成功完成時，會在同一個交易裡記錄收據和 sent 狀態。
- 被改動過的 epoch、文字、hash 或目的地，無法取得或開始 claim。
- 有效的 claim 會擋住重新歸檔；只有在投遞之前取消，才能解除那個扣留。
- 關卡不可用時會蓋上標記；關卡發現已簽署時，沒有 force 就拒絕。
- auto-ttl 絕不會對操作員之後已重新歸檔的文字觸發。
