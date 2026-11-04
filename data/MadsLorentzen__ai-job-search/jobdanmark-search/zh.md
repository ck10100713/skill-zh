---
name: jobdanmark-search
version: 1.0.0
description: >
  只要使用者提到任何和丹麥職缺列表、在丹麥找工作、在丹麥找工作機會，或是 Jobdanmark 上的職缺有關的事，
  一定要用這個 skill，即使他們沒有明講 jobdanmark.dk。在找工作的脈絡下，關於特定丹麥職缺類別、
  市鎮、僱用類型或薪資的問題，也要呼叫這個 skill。觸發詞包括：
  danish jobs, jobs in denmark, find job denmark, job search denmark, danish job listings,
  jobdanmark, job opslag, find job, jobsøgning, ledige stillinger, stillingsopslag,
  job i Danmark, fuldtidsjob, deltidsjob, studiejob, praktikplads, elev, fleksjob,
  IT job denmark, sygeplejersker job, håndværker job, ingeniør job, pædagog job,
  kontor job, leder job, salg job, hotel job, kirke job, job aarhus, job københavn,
  job odense, job aalborg, job sjælland, job jylland, job fyn, jobkategorier denmark,
  ledige job, ansøgningsfrist, søg job, job opslaget, jobopslag, danish vacancies,
  work in denmark, employment denmark, job denmark, jobs near me denmark,
  apprentice denmark, internship denmark, part-time denmark, full-time denmark.
context: fork
enabled: false  # Danish demo portal - ships opt-in; /setup enables it when your market is Denmark, or set true here yourself
allowed-tools: Bash(bun run .agents/skills/jobdanmark-search/cli/src/cli.ts *)
---

# Jobdanmark Search Skill

從 Jobdanmark.dk 的公開 API 取得即時的丹麥職缺。不需要驗證。涵蓋 10 個類別、所有丹麥市鎮，共約 15,000 筆以上的有效職缺。

## When to use this skill

當使用者想要：

- 搜尋丹麥的職缺（依關鍵字、地點、類別或職缺類型）
- 瀏覽丹麥某個特定城市、市鎮、郵遞區號或地區的可用職缺
- 依僱用類型篩選職缺（全職、兼職、學生工、學徒等）
- 查詢某個特定職缺的完整細節，包含描述和截止日
- 列出所有職缺類別和目前的即時職缺數
- 把搜尋詞轉成職稱 ID 或類別 ID，以便精準篩選
- 找出職缺搜尋篩選用的地點建議（市鎮、郵遞區號、地區）

## Commands

### Search job listings

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts search [flags]
```

主要旗標：
- `--text <keyword>`：自由文字搜尋，例如 `elektriker`、`sygeplejerske`、`softwareudvikler`
- `--category <id>`：類別 ID（見下方 Categories 表）
- `--jobtitle-id <id>`：來自 `autocomplete` 結果的職稱 ID
- `--municipality <name>`：例如 `Odense`、`København`、`Aarhus`
- `--zip <code>`：郵遞區號，例如 `5000`、`8000`、`2100`
- `--region <name>`：landsdel（`locations` 的類別 `region`），例如 `Sjælland`、`Østjylland`、`Fyn`
- `--administrative-region <name>`：五個大區之一（`locations` 的類別 `administrativeRegion`），例如 `Region Midtjylland`
- `--job-type <types>`：用逗號分隔：`fuldtid`、`deltid`、`fleksjob`、`elev`、`studiejob`、`praktik`
- `--page <n>`：頁碼（每頁 30 筆，由伺服器強制）
- `--limit <n>`：限制 CLI 回傳的結果總數
- `--format json|table|plain`

> 每頁筆數由 API 固定為 30。用 `--page` 來分頁。

### Full job detail

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts detail <slug> [--format json|plain]
```

`slug` 是 `search` 結果裡以 `slug` 回傳的 URL 路徑片段（例如 `it-chef-soeges-til-rah`）。從職缺頁面回傳完整的結構化職缺資料。有 Schema.org JSON-LD 時 CLI 優先用它，Jobdanmark 沒放 JSON-LD 時就退回解析 render 後的 HTML。

### List categories with live counts

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts categories [--format json|table|plain]
```

回傳所有 10 個職缺類別和目前的即時職缺數。用來讓使用者概覽就業市場很有用。

### Autocomplete job titles and categories

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts autocomplete --query "<text>" [--limit <n>]
```

用這個把搜尋詞轉成精確的職稱 ID（`--jobtitle-id`）或類別 ID（`--category`），給 `search` 用。結果裡的 `value` 欄位就是要傳給 `search` 的 ID。

### Suggest locations

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts locations --query "<text>" [--limit <n>]
```

回傳符合的市鎮、郵遞區號和地區。把項目的 `value` 傳給它的 `category` 所對應的 `search` 旗標：`municipality` → `--municipality`、`zip` → `--zip`、`region` → `--region`、`administrativeRegion` → `--administrative-region`。值放在錯的旗標下，不會比對到任何職缺。

---

## Categories

| ID | 丹麥文 | 英文 |
|----|--------|---------|
| 227972 | Pædagogik, Uddannelse og Forskning | Education, Research |
| 227973 | Håndværk, Industri, Transport og Landbrug | Crafts, Industry, Transport, Agriculture |
| 227974 | Salg, Kommunikation, Marketing, og Design | Sales, Communication, Marketing, Design |
| 227975 | Pleje, Social og Sundhed | Care, Social, Health |
| 227976 | Hotel, Service, Restauration og Sikkerhed | Hotel, Service, Restaurant, Security |
| 227977 | Kontor, Finans og Økonomi | Office, Finance, Economy |
| 227978 | IT, Ingeniør og Energi | IT, Engineering, Energy |
| 227979 | Ledelse, HR og projektstyring | Management, HR, Project Management |
| 543415 | Kirke, Kultur og Underholdning | Church, Culture, Entertainment |
| 227980 | Øvrige job | Other jobs |

---

## How to use effectively

**先解析地點。** 傳給 `search` 之前，先用 `locations` 找出正確的市鎮名稱或郵遞區號：

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts locations --query "Aarhus" --format plain
```

**解析職稱以求精準。** 使用者想找特定職位時，用 `autocomplete` 取得確切的職稱 ID：

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts autocomplete --query "sygeplejerske" --format plain
```

**自然的流程：`search` → `detail`。**
1. 用 `search` 取得符合職缺的清單，附上它們的 `slug`。
2. 呼叫 `detail <slug>` 取得完整的職缺內容，包含描述、截止日和組織細節。

**比較用 `--format table`**，資料處理用 `--format json`，單筆細節檢視用 `--format plain`。

**分頁**：API 每頁回傳 30 筆（由伺服器強制）。用 `--page` 瀏覽結果。用 `--limit` 限制 CLI 輸出，不管每頁大小。

**組合篩選條件**以得到精確的結果，例如 `--text` + `--job-type` + `--municipality` 可以在單一搜尋 request 裡一起使用。

---

## Usage examples

### IT jobs in Copenhagen

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts search \
  --category 227978 \
  --municipality "København" \
  --job-type fuldtid \
  --format table
```

### Nursing jobs anywhere in Denmark

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts search \
  --text "sygeplejerske" \
  --category 227975 \
  --format table
```

### Student jobs in Aarhus

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts search \
  --municipality "Aarhus" \
  --job-type studiejob \
  --format table
```

### What job categories are most active right now?

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts categories --format table
```

### Full details for a specific job posting

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts detail it-chef-soeges-til-rah --format plain
```

### Find jobs in zip code 8000

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts search --zip 8000 --format table
```

### What electrician jobs are available?

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts search \
  --text "elektriker" \
  --category 227973 \
  --job-type "fuldtid,deltid" \
  --format table
```

### Apprentice positions in all of Denmark

```bash
bun run .agents/skills/jobdanmark-search/cli/src/cli.ts search \
  --job-type elev \
  --page 1 \
  --format table
```

---

## Output formats

| Format | 最適合 |
|--------|----------|
| `json` | 預設：給程式使用、資料處理、在指令之間傳遞 ID |
| `table` | 快速、人類好讀的概覽和比較 |
| `plain` | 單筆細節檢視（`detail`） |

所有錯誤都以 `{ "error": "...", "code": "..." }` 寫到 **stderr**，行程以 exit code `1` 結束。

---

## Notes

- 所有資料都來自公開的 Jobdanmark.dk API，不需要憑證。
- 分頁是從 1 開始（`--page 1` 是第一頁）。每頁 30 筆，由伺服器強制。
- `detail` 指令會抓取 HTML 職缺頁面，有內嵌的 JSON-LD 時就解析它，沒有放結構化資料的頁面則退回解析 render 後的 HTML。它不使用另外的 JSON API。
- 搜尋結果裡的 `slug` 是從 API 的相對 `url` 欄位擷取出來的（`/job/` 之後的路徑）；它也會以 `id` 輸出，這是每個搜尋 CLI 共用的入口網站契約名稱。
- 搜尋結果裡的 `applicationDeadline` 可能是 `null`（沒有設定截止日）。
- 篩選用的職缺類型值：`fuldtid`、`deltid`、`fleksjob`、`elev`、`studiejob`、`praktik`。
