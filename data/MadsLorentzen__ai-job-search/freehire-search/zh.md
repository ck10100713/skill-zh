---
name: freehire-search
version: 1.0.0
description: >
  用這個 skill，透過 freehire.me 聚合服務的公開 API，搜尋多個國家和市場（以及遠端）的即時軟體／科技／資料／工程職缺，或查詢某一則特定職缺。它把約 50 個 ATS 平台的職缺整合成同一個 schema，所以一個 skill 就涵蓋很多市場，但它的分面篩選（技能、類別、資歷）目前以科技職缺為優先調校，所以觸發範圍要限定在技術類職缺。觸發詞：find a tech job、software job search、developer jobs、engineering vacancies、data/ML jobs、DevOps roles、remote developer jobs、
  "are there any <tech role> jobs in <place>"、look up this freehire job posting。
context: fork
enabled: true  # set to false to keep this portal installed but have /scrape skip it
allowed-tools: Bash(bun run .agents/skills/freehire-search/cli/src/cli.ts *)
---

# freehire Search Skill

搜尋 **[freehire.me](https://freehire.me)** 職缺聚合服務的即時職缺，它是一個開源的 IT 求職板，把許多國家約 50 個 ATS 平台的職缺正規化成同一個 schema。不需要驗證、不需要 API key，而且**執行期零依賴**，只要有 `bun` 就能跑。市場是在每次查詢時用分面旗標（`--region`、`--country`）選的，所以同一個 skill 在任何市場的 fork 使用者手上都能直接用。

> 這是 repo 的求職入口 skill 模式的一個不分國家的實作範例，和 `linkedin-search` 類似。和爬 HTML 的入口網站不同，它查詢的是 freehire 的公開 JSON API，所以結果是結構化的（技能、資歷、地區分面），不是從 markup 解析出來的。

## ⚠️ Scope: tech-focused

freehire 的語料庫已經包含一些非科技職缺（它會爬整個公司的徵才頁面），**但它的分面篩選（技能、類別和資歷字典）目前是以科技職缺優先調校的**，所以這個 skill 把觸發範圍限定在軟體／資料／工程／科技職缺，那裡的篩選效果很好。非科技的涵蓋範圍存在，但還在成熟中；現在不要依賴這個 skill 來涵蓋一般（非技術）職缺。

## ℹ️ Hosted-service dependency (best-effort, no SLA)

這個 skill 依賴第三方託管服務 freehire.me。讀取是**公開且不需驗證**的，和 `linkedin-search` 一樣是零註冊門檻。

**freehire.me 是個人專案，但有在積極維護；它以盡力而為的方式運作（沒有正式的 SLA）。** 如果 API 連不上，CLI 會優雅地失敗：以非零的 exit code 結束並附上清楚的錯誤訊息，所以服務中斷只會讓這個來源降級，不會弄壞周圍的工作流程。

**自行架設／可替換的 base URL。** freehire 後端是獨立的 MIT 授權 repo：[`strelov1/freehire`](https://github.com/strelov1/freehire)（Go + PostgreSQL + Meilisearch），用 Docker Compose 一個指令就能架起來（`make up` → API 在 `:8080`，路徑一樣是 `/api/v1/...`）。這個 skill 支援 base-URL 環境變數 `FREEHIRE_API_URL`（預設 `https://freehire.me`），所以指向本機實例只要改一行：

```bash
FREEHIRE_API_URL=http://localhost:8080 bun run .agents/skills/freehire-search/cli/src/cli.ts search -q "go"
```

注意：架起 *API* 很輕，但要維持一份*完整、持續更新*的鏡像（約 50 個平台、數百萬筆職缺）就很吃資源。自行架設的人要嘛只爬一個範圍有限的來源子集，要嘛把環境變數指回託管的 API。

## When to use this skill

- 依關鍵字搜尋科技職缺，限定在某個地區／國家或遠端，每筆結果都會帶回**完整的描述**，不用每一筆再另外追查
- 依資歷、類別、技能或時效（N 天內刊登）篩選
- 用 slug 查詢單一 freehire 職缺（包含已經關閉的）

## Commands

### Search job listings

```bash
bun run .agents/skills/freehire-search/cli/src/cli.ts search [-q "<keywords>"] [facet flags]
```

主要旗標：
- `--query <text>` / `-q <text>`：關鍵字搜尋（職稱、技能、角色）。全文檢索；選填。
  支援 `OR` 和 `title:`（見下方「Query operators」）。
- `--jobage <days>`：N 天內刊登（對應到 `posted_within_days`）。
- `--page <n>`：從 1 開始的頁碼。預設 1。
- `--limit <n>` / `-n <n>`：每頁結果數（API 的上限）。預設 25。
- `--format json|table|plain`：預設 `json`。
- `--description-format markdown|text|html`：每筆結果的完整描述怎麼 render。預設 `markdown`，會保留職缺的標題和需求清單。僅限 `json` 輸出。

**Query operators。** `-q` 看得懂兩個運算子；CLI 會把文字原封不動傳過去，由 API 解析：

- 在幾個選項之間放 `OR`，會回傳符合其中**任何一個**的職缺，例如 `-q "golang OR rust"`。只能用大寫：小寫的 `or` 就是一般的搜尋字。純粹用空格分隔的字**不是**聯集（`-q "golang rust"` 回傳的職缺比單獨 `-q golang` 還少），所以同義詞和替代技術棧要用 `OR`，不要每個關鍵字各跑一次搜尋。最多 5 個選項；第 6 個會被拒絕並回傳錯誤。雙引號裡的 `OR` 是字面文字。
- 開頭的 `title:` 會把那個選項限定在職缺**職稱**，例如 `-q "title:staff engineer"` 會跳過只是在描述裡提到這些字的職缺。它是逐個選項套用的，所以每個選項都要重複寫：`-q "title:staff engineer OR title:principal engineer"`。它只在選項的開頭才算；中間的 `title:` 會被當成文字搜尋。裡面可以用引號：`-q 'title:"staff engineer"'` 會比對整個片語。

分面旗標、`--jobage`、`--page` 和 `--limit` 作用在合併後的結果：每個選項都以同樣方式過濾，符合多個選項的職缺只會出現一次。

**搜尋結果已經帶有完整描述。** 這個 skill 查詢的是 freehire 的 agent 搜尋端點，它把索引裡被截斷的預覽，換成每則職缺的完整文字，所以搜 20 個職缺只要 1 個 request，不是 1 + 20 個。**不要**對搜尋結果逐一跑 `detail` 去讀描述，`detail` 只用在用 slug 查單一職缺（例如從 tracker 來的，或已經關閉因此不在搜尋裡的職缺）。完整描述很冗長：`--limit` 要保守，讀內文之前先用職稱／公司預先過濾，或是傳 `--no-description` 做便宜的探索：它會保留其他所有欄位，只把內文整個拿掉（要抓入選名單裡某個職缺的內文，用 `detail`，或是不帶這個旗標重跑搜尋）。

分面篩選（值來自 freehire 的受控詞彙；同一個分面內用逗號分隔代表 OR）：
- `--region <codes>`：大區域：`global`、`eu`、`uk`、`north_america`、`latam`、`apac`、`mena`、`africa`、`cis`。`--region eu,uk`。`eu` 不包含英國；要涵蓋整個歐洲要加 `uk`。單一國家請改用 `--country`：`us` 是國家代碼，不是地區，`--region us` 什麼都比對不到。`--region`、`--country` 和 `--city` 構成同一個 OR 群組，所以單獨用 `--country us` 就會限定在美國。用 `none` 來比對地區**無法**解析的職缺（見下方「Partial data」）。
- `--country <codes>`：ISO-3166 alpha-2，例如 `--country DE,GB`
- `--city <names>`：城市名稱，例如 `--city Berlin`
- `--seniority <levels>`：`junior`、`middle`、`senior`、`staff`、`principal`、`lead`……
- `--category <cats>`：`backend`、`frontend`、`fullstack`、`devops`、`ml_ai`、`qa`……
- `--skill <names>`：標準技能名稱，例如 `--skill go,kubernetes`
- `--company <slug>`：公司 slug（來自結果裡的 `company_slug`）
- `--remote <mode>`：`remote` | `hybrid` | `onsite`（`work_mode` 分面）。單獨一個 `--remote` 代表 `remote`。用逗號分隔代表 OR（`remote,hybrid`；`on-site` 會正規化成 `onsite`）。不認識的項目會以 exit 1 結束，回傳 `BAD_ARG`。
- `--facet <key=value>`：任何其他分面參數（可重複），例如 `--facet salary_min=100000`

> **地點是分面，不是自由文字。** 和 `linkedin-search` 的 `--location` 不同，freehire 是透過結構化的 `--region`/`--country`/`--city` 分面來過濾地理位置。某個市場目前有哪些值，到 [`/api/v1/jobs/facets`](https://freehire.me/api/v1/jobs/facets) 查（加上 `?q=<role>` 來縮小範圍），絕對不要自己編造分面值。

### Fetch full job detail

```bash
bun run .agents/skills/freehire-search/cli/src/cli.ts detail <slug|url> [--format json|plain]
```

`slug` 是 `search` 結果裡的 `id`（例如 `golang-zensar-2bxu6dxm`）。你也可以傳完整的 `https://freehire.me/jobs/<slug>` URL。其他任何主機的 URL，包含搜尋結果的 `url` 欄位帶的雇主應徵連結，都會在發出任何 request 之前以 `BAD_ID` 被拒絕。回傳完整的（已去除 HTML 的）描述、技能、地區／國家，以及（當職缺有被補充資料時）資歷、類別、僱用類型和薪資。如果 freehire 有記錄薪資的週期，`salary` 就會保留它（`INR 300000–300000/year`、`INR 12000/month`）；比較薪資時只能在同一個週期下比。

用在你已經有 slug 的職缺：追蹤中的應徵、分享的連結，或是搜尋已經不再列出的已關閉職缺。重新抓取 `search` 剛回傳的那一筆，只是重讀一份你已經有的描述。

## Usage examples

```bash
# Senior backend roles, table view
bun run .agents/skills/freehire-search/cli/src/cli.ts search -q "backend engineer" --seniority senior --limit 10 --format table

# Go or Rust roles, one search (OR must be uppercase)
bun run .agents/skills/freehire-search/cli/src/cli.ts search -q "golang OR rust" --remote remote --format table

# Staff or principal titles only, not postings that mention them in passing
bun run .agents/skills/freehire-search/cli/src/cli.ts search -q "title:staff engineer OR title:principal engineer" --format table

# Remote React roles in the EU
bun run .agents/skills/freehire-search/cli/src/cli.ts search -q "react" --remote remote --region eu --format table

# DevOps roles in Germany posted in the last 14 days
bun run .agents/skills/freehire-search/cli/src/cli.ts search --category devops --country DE --jobage 14 --format table

# ML/AI roles anywhere, fully remote
bun run .agents/skills/freehire-search/cli/src/cli.ts search -q "machine learning" --category ml_ai --remote remote --format table

# Descriptions as plain text instead of Markdown
bun run .agents/skills/freehire-search/cli/src/cli.ts search -q "platform engineer" --limit 5 --description-format text

# Full details for a specific job
bun run .agents/skills/freehire-search/cli/src/cli.ts detail golang-zensar-2bxu6dxm --format plain
```

## Output formats

| Format | 最適合 |
|--------|----------|
| `json` | 預設：給程式使用；唯一帶有每筆結果描述的格式 |
| `table` | 快速讓人掃過 |
| `plain` | 閱讀單一職缺的完整細節（`detail` 指令） |

搜尋的 JSON 是 `{ "meta": { "count", "page", "total" }, "results": [...] }`；每筆結果至少帶有 `id`（freehire 的 slug）、`title`、`company`、`location`、`date`、`url` 和 `description`（缺的值是 `null`）。`table` 和 `plain` 會省略描述，因為它會淹沒原本方便掃讀的清單。所有錯誤都以 `{ "error": "...", "code": "..." }` 寫到 **stderr**，行程以 exit code `1` 結束。

有一種診斷訊息不算錯誤：`--region`（或 `--facet regions=`）的值不在文件記載的詞彙裡（`us` 是國家代碼，不是地區），會在結果之後把 `{ "warning": "...", "code": "REGION_VALUE_UNKNOWN" }` 印到 **stderr**，行程仍以 exit `0` 結束，stdout 是合法的 JSON 文件。

## Partial data

分面是逐筆職缺推導出來的，可能**不完整**，地理位置尤其如此。一個職缺可能解析得出它的 `work_mode`（例如 `remote`），但當來源的地點文字有歧義時，**地區或國家仍然無法確定**（freehire 的字典絕不亂猜）。所以：

- 缺少地區／國家代表「沒解析出來」，**不是**「不適用」：用 `--region eu` 篩選，會默默丟掉地區沒解析出來的職缺，即使它們實際上在歐盟。如果你需要這些職缺，就放寬或拿掉這個分面。
- 未解析的那一桶有專用的分面值：`--region none` 會比對**沒有**解析出地區的職缺，適合用來撈出那些從沒釘住地理位置的遠端職缺。它可以和真正的地區做 OR，例如 `--region eu,none`。
- 基於同樣的原因，`result.regions` / `countries` / `cities` 可能是空陣列；空的要當成未知，不是「以上皆非」。

## Notes

- 資料來自 freehire.me 的公開 API，不需要憑證。只有每個使用者的追蹤（apply/save）需要 key，而這個 skill 刻意不碰它：它**只做搜尋 + detail**。
- 搜尋結果裡的 `id` 是 freehire 的 `public_slug`，原封不動傳給 `detail` 即可。
- `date` 是 `YYYY-MM-DD` 格式的刊登日期（API 的 `posted_at` 時間戳的日期部分，每個入口網站 CLI 都輸出這個形狀）；沒有日期的職缺可能是 `null`。
- 分面值是受控詞彙。篩選之前，先用 `/api/v1/jobs/facets` 看某個查詢目前有哪些值（附計數）。
- API 會對 429/5xx 以指數退避重試；連不上 API 時以非零 exit code 結束並附上清楚的訊息（盡力而為的服務，見上面的依賴說明）。
- `search` 呼叫的是 `/api/v1/agent/jobs/search`（和其他的一樣是公開的）；`--no-description` 呼叫比較輕量的 `/api/v1/jobs/search`，它不提供完整內文。比這個端點更舊的自行架設實例會回 404，CLI 會把它回報成指名該端點的錯誤，絕不會當成空的結果集。
