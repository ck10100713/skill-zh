---
name: jobnet-search
version: 1.0.0
description: >
  只要使用者提到任何和丹麥找工作、職缺列表、職位空缺、在丹麥的就業機會，或是丹麥政府求職入口有關的事，
  一定要用這個 skill，即使他們沒有明講 jobnet.dk。在丹麥就業的脈絡下，關於特定職稱、職業、雇主或地區的問題，
  也要呼叫這個 skill。這個 skill 涵蓋由 STAR（Styrelsen for Arbejdsmarked og Rekruttering）營運的丹麥官方公共求職入口。
  觸發詞包括：danish jobs, danish job search, jobnet, jobnet.dk, find job
  denmark, danish employment, job i danmark, job på jobnet, offentlige job, stillinger
  i det offentlige, public sector jobs denmark, government jobs denmark, STAR jobs,
  job ledige stillinger, ledig stilling, søg job, job opslag, job vacancy denmark,
  stillingopslag, jobopslag, sygepleje job, ingeniør job, lærer job, pædagog job,
  it-job denmark, jobs in copenhagen, jobs in aarhus, jobs in odense, deltidsjob,
  fuldtidsjob, fastansættelse, tidsbegrænset ansættelse, fleksjob, sygeplejerske job,
  social worker job denmark, occupation search denmark, esco occupation, job deadline,
  ansøgningsfrist, søg efter job, full time job denmark, part time job denmark.
context: fork
enabled: false  # Danish demo portal - ships opt-in; /setup enables it when your market is Denmark, or set true here yourself
allowed-tools: Bash(bun run .agents/skills/jobnet-search/cli/src/cli.ts *)
---

# Jobnet-Search Skill

從 Jobnet.dk 的公開 API 取得即時的丹麥職缺。不需要驗證。Jobnet 由 STAR（Styrelsen for Arbejdsmarked og Rekruttering）營運，是丹麥的官方政府求職入口，涵蓋公部門職位，也涵蓋許多私部門的職缺。任何時候大約都有 21,000 筆以上的有效職缺。

## When to use this skill

當使用者想要：

- 依關鍵字、職稱或雇主，搜尋丹麥的職缺
- 依地區、工時（全職／兼職）或僱用期間（正職／約聘）篩選職缺
- 在給定半徑內，找某個特定郵遞區號附近的職缺
- 取得某個特定職缺廣告的完整細節，包含描述、聯絡人和應徵 URL
- 探索職業類型和 ESCO 類別，以便更精準地篩選職缺
- 瀏覽丹麥職稱或關鍵字的自動完成建議
- 找公部門、醫療、IT、教育，或是任何其他丹麥產業的職缺

## Commands

### Search for job ads

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts search [flags]
```

主要旗標：
- `--search-string <text>`：關鍵字搜尋，例如 `sygeplejerske`、`ingeniør`、`pædagog`
- `--region <region>`：`HovedstadenOgBornholm`、`Midtjylland`、`Syddanmark`、`OevrigeSjaelland`、`Nordjylland`
- `--postal-code <code>`：以半徑為基礎搜尋用的郵遞區號，例如 `2100`
- `--radius <km>`：離郵遞區號的半徑，單位 km（預設：`50`）
- `--work-hours <type>`：`FullTime` 或 `PartTime`
- `--duration <type>`：`Permanent` 或 `Temporary`
- `--job-type <type>`：`Ordinaert`、`Efterloenner`、`Foertidspension`
- `--occupation-area <id>`：職業領域識別碼，例如 `10000`
- `--occupation-group <id>`：職業群組識別碼，例如 `10060`
- `--occupation <uuid>`：一個 ESCO 職業：`occupations` 印出的 `conceptUriDa`，或是它結尾的 UUID
- `--order <type>`：`PublicationDate`（預設）、`BestMatch`、`ApplicationDate`
- `--page / --per-page / --limit`
- `--format json|table|plain`

### Full job ad detail

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts detail <jobAdId> [--format json|plain]
```

`jobAdId` 是 `search` 結果裡的 UUID（`jobAdId` 欄位，也會以 `id` 輸出，這是每個搜尋 CLI 共用的入口網站契約名稱）。回傳完整的職缺描述、聯絡人、申請截止日、雇主細節和直接的應徵 URL。

### Search occupation types

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts occupations --search-string <text> [--per-page <n>]
```

用這個來找出 ESCO 職業識別碼，再用 `--occupation` 傳給 `search`。數字型的 `--occupation-area` / `--occupation-group` 代碼是另一套分類：把職業 UUID 傳到那裡，不會比對到任何職缺。

### Typeahead suggestions

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts suggestions --query <text> [--limit <n>]
```

回傳丹麥職稱的自動完成字串。在組 `search` 查詢之前，用來探索有效的丹麥職稱很有用。

---

## How to use effectively

**先探索職業。** 在執行 `search` 之前，先用 `occupations` 或 `suggestions` 找出正確的丹麥文詞彙或 ESCO 識別碼：

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts suggestions --query "syge"
bun run .agents/skills/jobnet-search/cli/src/cli.ts occupations --search-string "sygeplejerske"
bun run .agents/skills/jobnet-search/cli/src/cli.ts search --occupation http://data.star.dk/esco/occupation/56f5d45c-ce48-43ac-9720-34831a1c8302
```

**自然的流程：`search` → `detail`。**
1. 用 `search` 取得符合職缺的清單，附上它們的 `jobAdId`。
2. 呼叫 `detail <jobAdId>` 取得完整的職缺描述、聯絡人和直接的應徵連結。

**比較用 `--format table`**，資料處理用 `--format json`，單筆細節檢視用 `--format plain`（會去掉職缺內文的 HTML）。

**分頁**：`--per-page` 控制伺服器端每頁的結果數。`--limit` 限制 CLI 輸出的筆數。用 `--page` + `--per-page` 逐頁走過大型結果集。

**地理搜尋模式：**
- 大範圍的地區篩選用 `--region`（例如整個 Midtjylland）
- 找特定位置附近的職缺用 `--postal-code` + `--radius`
- 不要在同一個查詢裡同時使用 `--region` 和 `--postal-code`

**排序要配合意圖：**
- `PublicationDate`：最新刊登的在前（預設，適合「有什麼新的」）
- `BestMatch`：相關度分數（提供 `--search-string` 時最好用）
- `ApplicationDate`：截止日最早的在前（適合急著要投的申請）

---

## Usage examples

### Jobs in Copenhagen area

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts search \
  --region HovedstadenOgBornholm \
  --per-page 10 \
  --format table
```

### Nurse jobs nationwide

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts search \
  --search-string "sygeplejerske" \
  --work-hours FullTime \
  --duration Permanent \
  --order BestMatch \
  --per-page 10 \
  --format table
```

### IT jobs near Aarhus within 30km

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts search \
  --search-string "udvikler" \
  --postal-code 8000 \
  --radius 30 \
  --work-hours FullTime \
  --format table
```

### Full details of a job ad

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts detail 9ef43bce-d82b-4ea1-a098-7ff6520f99be --format plain
```

### Jobs sorted by application deadline (urgent first)

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts search \
  --search-string "pædagog" \
  --region OevrigeSjaelland \
  --order ApplicationDate \
  --per-page 10
```

### Discover occupation terms

```bash
bun run .agents/skills/jobnet-search/cli/src/cli.ts suggestions --query "ingeniør" --limit 5
bun run .agents/skills/jobnet-search/cli/src/cli.ts occupations --search-string "lærer" --per-page 5
```

---

## Output formats

| Format | 最適合 |
|--------|----------|
| `json` | 預設：給程式使用、資料處理、在指令之間傳遞 ID |
| `table` | 快速、人類好讀的概覽和比較 |
| `plain` | 單筆細節檢視（`detail`），會去掉職缺描述的 HTML |

所有錯誤都以 `{ "error": "...", "code": "..." }` 寫到 **stderr**，行程以 exit code `1` 結束。

---

## Notes

- 所有資料都來自公開的 `jobnet.dk/bff` REST API，不需要憑證。
- API 需要 `x-csrf: 1` header；CLI 會自動加上。
- 分頁是從 1 開始（`--page 1` 是第一頁）。
- `search` 的結果省略了 HTML 職缺描述，要用 `detail` 取得。
- `detail --format plain` 會去掉 HTML 標籤，輸出好讀的文字。
- jobnet.dk 上的職缺廣告細節頁：`https://jobnet.dk/find-job/{jobAdId}`（非外部廣告；外部廣告用雇主的 `jobAdUrl`）。
- `suggestions` 是針對丹麥職稱調校的，英文詞彙可能會回傳空的結果。
