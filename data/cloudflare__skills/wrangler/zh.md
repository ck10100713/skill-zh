---
name: wrangler
description: 在有 wrangler.jsonc、wrangler.json 或 wrangler.toml 的專案裡執行或排查 Wrangler CLI 指令，包含本機開發、Previews、部署和資源管理。新專案以及沒有 Wrangler 設定檔的專案，請改用 cf CLI。
---

# Wrangler CLI

只有在專案有 `wrangler.jsonc`、`wrangler.json` 或 `wrangler.toml`、而且沒有 `cloudflare.config.ts` 時，或是使用者明確要求 Wrangler 時，才用這個 skill。新專案、有 `cloudflare.config.ts` 的專案、沒有任何 Cloudflare 設定的專案，一律改用 Cloudflare CLI（`cf`）：有裝 `cf-cli` skill 就載入它，沒有就照 [Use cf with coding agents](https://developers.cloudflare.com/cf/agents/index.md) 做。不要在這些專案裡加 Wrangler。

用專案自己的 Wrangler 版本，寫指令或設定之前先檢索相關文件。CLI 的 flag 和設定欄位會變，不要靠記憶中的範例。

## Inspect the Project

- 找出 package manager、已安裝的 Wrangler 版本、package scripts、framework 和 Wrangler 設定。指令要透過專案的 script 或 package manager 執行，這樣才會用本地版本。需要時依現有的 lockfile 安裝依賴，不要為了配合最新文件就偷偷升級 Wrangler。如果專案有 Wrangler 設定檔但 Wrangler 不在依賴裡，照[安裝指南](https://developers.cloudflare.com/workers/wrangler/install-and-update/index.md)把它加成本地依賴。
- 找出 build 或 deploy 指令實際使用的設定，包含 framework 產生的設定。要改的是它的來源，不要改產生出來的輸出。
- 在執行會改動東西的指令之前，先確定目標的帳號、Worker、環境和資源。做資料操作時，要確定目標是本機還是遠端。

## Retrieve What the Task Needs

有 Cloudflare MCP 的 `docs` 工具就用它，沒有就直接抓對應的連結頁面。順著連結到實際用到的指令或產品頁面，不要把整份 reference 都載進來。如果頁面搬家了，從 [Wrangler command index](https://developers.cloudflare.com/workers/wrangler/commands/index.md) 或 Cloudflare 文件搜尋重新找。

| 任務 | 來源 |
| --- | --- |
| 查指令和 flag，包含資源管理、部署、rollback 和診斷 | 專案本地的 `wrangler --help` 和 `wrangler <command> --help`；[指令參考](https://developers.cloudflare.com/workers/wrangler/commands/index.md) |
| 編輯設定或新增 binding | 已安裝的 `wrangler/config-schema.json`（通常在 `node_modules` 底下）；[設定參考](https://developers.cloudflare.com/workers/wrangler/configuration/index.md) |
| 部署 framework 應用程式 | [Framework guides](https://developers.cloudflare.com/workers/framework-guides/index.md)；照專案現有 framework 和 adapter 的指南做 |
| 被要求時，把應用程式遷移到 Workers | [Pages to Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/index.md)；[Vercel to Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/vercel-to-workers/index.md) |
| 設定 staging 或 production | [Environments](https://developers.cloudflare.com/workers/wrangler/environments/index.md) |
| 在本機、CI 或已部署的 Worker 上設定 secret | [Secrets](https://developers.cloudflare.com/workers/configuration/secrets/index.md) |
| 產生 binding 和 runtime 型別 | [TypeScript](https://developers.cloudflare.com/workers/languages/typescript/index.md) |
| 本機執行或選擇測試方式 | [Local development](https://developers.cloudflare.com/workers/local-development/index.md)；[testing](https://developers.cloudflare.com/workers/testing/index.md) |
| 為 Wrangler 選擇角色、scope 或 API token 權限 | [Roles and permissions](https://developers.cloudflare.com/workers/authorization/index.md)；[Workers roles and permissions](https://developers.cloudflare.com/workers/authorization/workers/index.md#wrangler) |
| 建立或管理 branch 或 pull request 環境 | [Previews overview](https://developers.cloudflare.com/workers/previews/index.md)；[get started](https://developers.cloudflare.com/workers/previews/get-started/index.md)；[configuration](https://developers.cloudflare.com/workers/previews/configuration/index.md) |
| 判斷 Preview 資源是隔離還是共用 | [Resources and isolation](https://developers.cloudflare.com/workers/previews/resources/index.md)，包含目前的限制 |
| 設定 Preview URL、存取、除錯或 CI | [Custom domains](https://developers.cloudflare.com/workers/previews/custom-domains/index.md)；[test and debug](https://developers.cloudflare.com/workers/previews/test-and-debug/index.md)；[examples](https://developers.cloudflare.com/workers/previews/examples/index.md) |
| 在 Previews、Version URL 和 Wrangler environments 之間做選擇 | [Compare workflows](https://developers.cloudflare.com/workers/previews/compare-workflows/index.md) |
| 診斷驗證問題或選擇帳號 | [General commands](https://developers.cloudflare.com/workers/wrangler/commands/general/index.md)，包含 `whoami`；[authentication profiles](https://developers.cloudflare.com/workers/wrangler/profiles/index.md) |
| 部署未驗證的原型 | [Claim deployments](https://developers.cloudflare.com/workers/platform/claim-deployments/index.md)，看資格、到期和 claim URL 的處理；正式環境或 CI 要用永久帳號 |

用已安裝的 help 和 schema 確認文件裡的功能在專案的版本裡是否存在。如果需要的功能得升級，要把這個依賴變更講清楚。如果沒辦法檢索，就明講缺了什麼，用手上的本地證據，不要自己編語法。

## Apply the Change

- 新的設定優先用 `wrangler.jsonc`。新專案的[相容性日期](https://developers.cloudflare.com/workers/configuration/compatibility-dates/index.md)設成今天；既有專案要往前推日期時，要檢視 runtime 變更並測試。沿用專案現有的慣例，不要順手做格式遷移。
- 新增 binding 或變數之前，先檢查環境繼承。有些欄位每個環境都得分別指定；預設設定能跑，不代表 staging 也設好了。
- 用 Cloudflare Vite plugin 時，透過 dev 或 build 時的 `CLOUDFLARE_ENV` 來選環境。部署的是產出的 build；在部署時才指定環境，並不會讓它攤平後的設定換目標。見 [Vite environments](https://developers.cloudflare.com/workers/vite-plugin/reference/cloudflare-environments/index.md)。
- 部署前先把 dashboard 上的變更和設定檔對齊：Wrangler 可能會覆蓋 dashboard 上的變數和 route。綁定既有資源時，要確認它們的 identifier；省略 identifier 可能會觸發[自動 provisioning](https://developers.cloudflare.com/workers/wrangler/configuration/index.md#automatic-provisioning)。
- 開發時要分清楚本機模擬和遠端 binding。本機跑的 Worker 仍然可能存取真實資源，測試寫入之前先檢查選到的 binding。
- 執行遠端指令之前，先確認已驗證的成員或 API token 是誰，並檢索該操作目前需要的角色和 scope。優先用能滿足使用者意圖的最小 scope。`wrangler login` 的 OAuth 流程不支援細粒度授權；需要細粒度存取時，用帳號擁有的 API token，而且絕對不要請使用者把它的值貼到對話裡。
- secret 的值不要出現在指令參數、原始碼和 log 裡。用該指令文件記載的互動式輸入，或受保護的檔案／stdin 機制。本地的 secret 檔必須被版本控制忽略，而且不會自動上傳成已部署的 secret。本地 secret 缺少時，到 secrets 文件查檔案優先順序和 `secrets.required` 宣告。
- 把 `wrangler secret put` 和 `secret delete` 當成部署：它們會建立一個版本並立刻部署。變更需要分階段上線時，用文件記載的 `wrangler versions secret` 流程。
- rollback 之前，先看 [rollback 限制](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/index.md)：連接的資源和它們的資料不會跟著 Worker 程式碼一起 rollback。

## Work with Workers Previews

- Workers Previews 需要專案本地的 Wrangler 4.135.0 或更新版本；專案指令不會用比較新的全域安裝版本。檢查專案固定的版本，需要升級依賴就要講清楚。
- Previews 用在同一個 Worker 底下的 branch 和 pull request 環境。要用正式環境的資源檢查某個已上傳的特定版本，用 Version URL；需要持久、各自獨立部署的 Worker，用 Wrangler environments。照 [Compare workflows](https://developers.cloudflare.com/workers/previews/compare-workflows/index.md) 做，不要套用舊的、有 alias 的 Version URL 流程。
- 先看使用者怎麼管理 production 設定和部署。Preview 網域要透過跟 production 同一套設定系統來設定，例如 Wrangler、dashboard 或 Terraform。Preview 部署走使用者現有的路徑，例如本地 CLI、Workers Builds 或外部 CI，除非使用者要求用別的流程。要照搬的是管理方式，不是 production 資源的 binding 或資料。
- 部署前，照目前的[設定位置對照表](https://developers.cloudflare.com/workers/previews/configuration/index.md#what-goes-in-the-previews-block)和[資源矩陣與限制](https://developers.cloudflare.com/workers/previews/resources/index.md)做。不要從 Preview 的名稱推斷它是隔離的，也不要允許寫入 production 資源，除非使用者明確打算共用。
- 要告訴使用者：除非設了存取控制，Preview URL 是公開的，然後讓他們決定要不要保護這些 URL。依選定的做法，照[自訂網域和存取指引](https://developers.cloudflare.com/workers/previews/custom-domains/index.md)做。
- 確認使用者要指向哪個 Worker 或 Wrangler 環境。指向 Wrangler 環境時，每個 Preview 指令都要帶同一個 `--env` 值；省略的話會指向最上層的 Worker。

## Validate

在 TypeScript 專案裡改了設定或 binding 之後，用專案的 `wrangler types` 指令重新產生型別，不要手改產生出來的宣告檔。再跑相關的既有 typecheck 或測試。

部署相關的變更，用專案的 build 流程，並在支援時用 `wrangler deploy --dry-run`，帶上預定的設定和環境。dry run 成功只代表 build 和打包沒問題，不能證明遠端資源或執行期行為正常。依要求的工作內容，再做對應的本機或遠端檢查。

Previews 的部分，回傳了 URL 並不能驗證依賴 binding 的行為，因為 Wrangler 可能報告這些 binding 缺失。要驗證使用者要求的行為，必要時用 Preview 專屬的 log 和設定。寫入 production 資源、破壞性測試、刪除具名 Preview，都必須符合使用者的明確意圖。

回報時要寫：改了什麼、目標環境、做過哪些檢查、還有哪些驗證缺口沒補。如果結果取決於目前的指令或設定行為，要附上用到的文件連結。

## Skill feedback

如果使用者反映這個 skill 給了錯誤或過時的指引，或是缺了資訊，就去讀 [references/skill-feedback.md](references/skill-feedback.md)。
