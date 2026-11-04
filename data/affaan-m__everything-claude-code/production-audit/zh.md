---
name: production-audit
description: 以本機證據為基礎的正式環境就緒稽核，適用於已出貨的應用程式、上線前 review、merge 後檢查，以及「正式環境會壞在哪？」這類問題，不會把 repo 資料送到外部稽核服務。在上線前、merge 之後稽核正式環境就緒程度，或被問到正式環境會壞在哪時使用。
metadata:
  origin: community
---

# Production Audit

當使用者問應用程式是否準備好出貨、正式環境可能壞在哪，或上線前必須修什麼的時候，使用這個 skill。這是把過時的社群 production-audit 構想，改寫成維護者可以放心用的版本：保留有用的正式環境就緒視角，移除了未釘住版本的外部執行，以及第三方的資料分享。

## 何時使用

- 使用者問「這個 production-ready 了嗎」、「正式環境會壞在哪」、「我們漏掉了什麼」、「幫我稽核這個 repo」或「可以出貨了嗎？」
- 某個功能剛 merge，需要 deploy 之前或 merge 之後的風險檢視。
- 公開上線、demo、客戶推出或投資人 walkthrough 快到了。
- CI 是綠的，但使用者想知道的是正式環境的風險，不只是測試狀態。
- 有 deploy 後的 URL、release branch、PR 或目前的 checkout 可以蒐集證據。

## 何時不要使用

- 正在積極實作，而適合的視角是逐行的安全寫法時，請先用 `security-review`。
- 純函式庫、範本、只有文件的 repo 或 scaffold，除非使用者想要的是打包/發佈的就緒度，而不是應用程式的就緒度。
- 使用者要求的是正式的合規稽核。這個 skill 是工程上的初步判斷，不是法律、財務、醫療或法規認證。
- 手上唯一的證據只是一個產品點子，沒有 repo、deployment、CI 或 runtime 介面。

## 運作方式

根據本機和使用者授權的證據來建立稽核。除非使用者明確核准特定的工具和資料流，否則不要執行未釘住版本的遠端程式碼、不要把 repo 內容上傳到第三方服務，也不要呼叫外部掃描器。

依照這個順序：

1. 確立 release 的範圍。
2. 讀最近的變更和目前的 branch 狀態。
3. 檢查 repo 裡實際存在的 runtime、認證、資料、付款、背景工作、AI 和 deployment 邊界。
4. 檢查 CI、測試、migration、環境變數文件和 rollback 路徑。
5. 給出簡短的 ship/block 建議，附上具體的修法。

## 證據檢查清單

從便宜的本機訊號開始：

```text
git status --short --branch
git log --oneline --decorate -20
git diff --stat origin/main...HEAD
```

然後檢查專案特有的範圍：

- Package script、CI workflow、release script、Docker 檔案和 deployment manifest。
- API 路由、webhook、認證 middleware、背景 worker、cron job 和資料庫 migration。
- 環境變數文件和啟動時的檢查。
- 可觀測性 hook、錯誤回報、log、health check 和儀表板。
- Rollback、seed、migration 和 backfill 的說明。
- 對最重要的使用者路徑的 E2E 涵蓋。

如果範圍內有 deploy 後的 URL，只對那個 URL 做瀏覽器或 HTTP 檢查，除非使用者提供安全的測試帳號，否則避免需要憑證的動作。

## 風險視角

### 安全與認證

- 公開路由、API 路由和管理路由是否清楚分開？
- 認證和授權是否在 server 端強制執行？
- Secret 是否都沒有出現在 client bundle、log、範例輸出和已 commit 的檔案裡？
- 在應用程式需要的地方，是否有 rate limit、CSRF 防護、CORS 政策和上傳驗證？
- AI 或 agent 的介面，是否能防禦 prompt injection、工具濫用，以及不受信任的內容跨進有特權的動作？

### 資料完整性

- Migration 能不能順利向前執行，並且有 rollback 或復原計畫？
- 破壞性的 migration、backfill 和資料匯入，是否有安全地分階段進行？
- 資料庫的 policy、授權和 service-role 邊界，是否符合應用程式的租戶模型？
- 寫入、工作和 webhook handler 的重試是否具冪等性？

### 付款與 Webhook

- 在解析可信的 payload 欄位之前，是否先驗證了 webhook 簽章？
- 每個付款、訂閱或履約的 webhook 是否具冪等性？
- 是否處理了重放、重複投遞和亂序投遞？
- 測試模式和正式模式的憑證是否分開？

### 營運

- 應用程式能不能從乾淨的 checkout，用文件記載的指令啟動？
- 必要的環境變數是否有命名、驗證，而且缺少時會立刻失敗（fail-fast）？
- 有沒有 health check 可以證明依賴的服務連得到？
- Deploy、rollback 和事故負責人的路徑是否有文件？
- Log 是否有用，又不會洩漏 secret 或個資？

### 使用者體驗

- 上線關鍵的路徑，在桌面和行動裝置上是否都有涵蓋？
- 表單在行動裝置上能不能順利使用，沒有輸入時縮放、版面重疊或送出被擋住的狀態？
- 載入中、空狀態、錯誤和權限被拒的狀態，是否有告訴使用者發生了什麼事？
- 當關鍵操作失敗時，有沒有支援或復原的路徑？

## 評分

用分數來強迫排優先順序，不是要暗示數學上的確定性。

| 等級 | 分數 | 意義 |
| --- | --- | --- |
| Blocked | 0-49 | 頂端的風險修好之前，不要出貨 |
| Risky | 50-69 | 只能搭配小規模推出或內部 beta 出貨 |
| Launchable With Caveats | 70-84 | 如果負責人接受列出的風險，就可以出貨 |
| Strong | 85-100 | 就現有證據看來，沒有明顯的上線阻礙 |

只要符合下列任何一項，分數上限就是 `69`：

- 敏感資料缺少認證或授權。
- 付款或履約的 webhook 不具冪等性。
- 必要的 migration 無法安全執行。
- Secret 暴露在 client bundle、log 或已 commit 的檔案裡。
- 高影響的 release 沒有 rollback 路徑。

如果 CI 不是綠的，或上線關鍵路徑沒有端到端測試過，分數上限就是 `84`。

## 輸出格式

先用一句話開頭：

```text
Production audit: 76/100, launchable with caveats, with webhook idempotency and rollback docs as the two risks to fix before public launch.
```

然後列出：

- `Blockers`：deploy 之前必須修的項目。
- `High-value fixes`：如果使用者想提高分數，接下來要修的項目。
- `Evidence checked`：檢查過的檔案、指令、CI、deploy 後的 URL 或 PR。
- `Evidence missing`：如果能提供，會改變信心的東西。
- `Next action`：一個具體的修復或驗證步驟。

優點要簡短帶過。使用者問的是就緒度，所以有用的答案是剩下的風險和下一步行動。

## 範例

使用者：

```text
is this ready to ship?
```

回應：

```text
Production audit: 68/100, risky, because Stripe webhooks are verified but not idempotent and there is no rollback note for the pending migration.

Blockers:
- Add idempotency for `checkout.session.completed` before fulfilling orders.
- Write and test the rollback path for `20260511_add_billing_state.sql`.

High-value fixes:
- Add a health check that verifies database and payment-provider reachability.
- Add one E2E path for upgrade, webhook fulfillment, and billing-page refresh.

Evidence checked:
- `api/stripe/webhook.ts`
- `db/migrations/20260511_add_billing_state.sql`
- GitHub Actions run for the release branch

Next action: Want me to patch webhook idempotency first?
```

## 反模式

- 把 `npx <package>@latest` 或遠端掃描器當成預設的稽核路徑。
- 沒有明確核准，就把原始碼、secret、客戶資料或私有拓撲上傳到外部稽核服務。
- 給了分數，卻沒有說明檢查過哪些證據。
- 把綠色的 CI 當成正式環境就緒。
- 用一句通用的「告訴我你想怎麼做」收尾。

## 另請參閱

- Skill：`security-review`
- Skill：`deployment-patterns`
- Skill：`e2e-testing`
- Skill：`tdd-workflow`
- Skill：`verification-loop`
