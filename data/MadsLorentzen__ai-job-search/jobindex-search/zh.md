---
name: jobindex-search
version: 1.0.0
description: >
  只要使用者想在丹麥找工作、找丹麥職缺列表、查詢特定職缺，或是問任何和丹麥就業市場有關的事，
  一定要用這個 skill，即使他們沒有明講 jobindex.dk。關於開放職位、職缺、在丹麥招募、丹麥城市或產業的工作機會，
  或是使用者想在丹麥找工作時，都要呼叫這個 skill。在脈絡是丹麥的情況下，像「find me a job」、
  「are there any jobs for X in Copenhagen」或「what jobs are available in Aarhus」這類說法也要觸發。
  觸發詞包括：jobindex, jobsøgning, job i Danmark, ledige stillinger,
  job opslag, find job, stillingopslag, jobannonce, job vacancy denmark, danish jobs,
  jobs in denmark, job search denmark, work in denmark, find work denmark, IT jobs
  denmark, engineer jobs denmark, developer jobs copenhagen, marketing jobs aarhus,
  jobs aarhus, jobs copenhagen, jobs odense, jobs aalborg, job openings denmark,
  hiring denmark, job listings denmark, python jobs denmark, grafisk designer job,
  data engineer job, softwareudvikler job, full stack developer job danmark.
context: fork
enabled: false  # Danish demo portal - ships opt-in; /setup enables it when your market is Denmark, or set true here yourself
allowed-tools: Bash(bun run .agents/skills/jobindex-search/cli/src/cli.ts *)
---

# Jobindex Search Skill

搜尋 Jobindex.dk 的即時丹麥職缺。不需要驗證。涵蓋所有產業的數千筆職缺，即時更新。

## When to use this skill

當使用者想要：

- 依關鍵字、職稱或技術，搜尋丹麥的職缺
- 找特定丹麥城市的工作（把城市名稱放進關鍵字，例如 `python aarhus`）
- 依時效篩選職缺（今天刊登、最近 7 天、最近 30 天）
- 取得某個特定職缺的完整描述
- 針對某個職業或技能組合，探索丹麥的就業市場

## Commands

### Search job listings

```bash
bun run .agents/skills/jobindex-search/cli/src/cli.ts search --query "<text>" [flags]
```

主要旗標：
- `--query <text>` / `-q <text>`：關鍵字搜尋（職稱、技能、公司、城市）。**必填。** 沒有 query 的搜尋會以 `MISSING_REQUIRED` 結束。
- `--jobage <days>`：依刊登時間篩選：`1`（今天）、`7`、`14`、`30`，或 `9999`（全部，預設）
- `--sort <order>`：`score`（相關度，預設）或 `date`（最新的在前）
- `--page <n>`：頁碼（從 1 開始，每頁固定 20 筆結果）
- `--limit <n>`：限制 CLI 輸出的結果總數（用戶端）
- `--format json|table|plain`

> **地區注意事項**：Jobindex API 不支援用參數做地區篩選。要找特定城市的工作，把城市放進 `--query`（例如 `--query "data engineer københavn"` 或 `--query "python aarhus"`）。

### Fetch full job detail

```bash
bun run .agents/skills/jobindex-search/cli/src/cli.ts detail <id> [--format json|plain]
```

`id` 是 `search` 結果裡的職缺 ID（例如 `h1647303`）。你也可以傳完整的 Jobindex URL。回傳完整的職缺描述、截止日、僱用類型、工時和應徵連結。

---

## How to use effectively

**一律從 `search` 開始。** 把職稱、技能或職業當作 `--query` 傳入。在 query 裡搭配城市名稱來縮小地點範圍（例如 `--query "frontend developer odense"`）。

**要看最新的職缺，用 `--jobage 7` 或 `--jobage 1`。** 沒有它的話，結果會包含所有歷史職缺。

**用 `--sort date` 先看最近刊登的職缺。** 預設的 `score` 是依相關度排序。

**自然的流程：`search` → `detail`。**
1. 用 `search` 找出符合的職缺和它們的 `id` 值。
2. 呼叫 `detail <id>` 取得完整描述、截止日和應徵連結。

**快速瀏覽用 `--format table`**，資料處理用 `--format json`，閱讀單一職缺的完整細節用 `--format plain`。

**分頁**：API 一律每頁回傳 20 筆結果。用 `--page` 切換頁面。用 `--limit` 限制單次抓一頁時的結果數。

---

## Usage examples

### Find Python jobs posted in the last 7 days

```bash
bun run .agents/skills/jobindex-search/cli/src/cli.ts search \
  --query python \
  --jobage 7 \
  --sort date \
  --format table
```

### Data engineer jobs in Copenhagen

```bash
bun run .agents/skills/jobindex-search/cli/src/cli.ts search \
  --query "data engineer københavn" \
  --sort score \
  --format table
```

### Graphic designer jobs — all time, by relevance

```bash
bun run .agents/skills/jobindex-search/cli/src/cli.ts search \
  --query "grafisk designer" \
  --limit 10 \
  --format table
```

### Full-stack developer jobs, page 2

```bash
bun run .agents/skills/jobindex-search/cli/src/cli.ts search \
  --query "full stack developer" \
  --page 2 \
  --format json
```

### Jobs posted today for a keyword

```bash
bun run .agents/skills/jobindex-search/cli/src/cli.ts search \
  --query python \
  --jobage 1 \
  --sort date \
  --limit 20 \
  --format table
```

### Get full details for a specific job

```bash
bun run .agents/skills/jobindex-search/cli/src/cli.ts detail h1647303 --format plain
```

### Marketing jobs in Aarhus

```bash
bun run .agents/skills/jobindex-search/cli/src/cli.ts search \
  --query "marketing aarhus" \
  --jobage 30 \
  --sort date \
  --format table
```

---

## Output formats

| Format | 最適合 |
|--------|----------|
| `json` | 預設：給程式使用、資料處理、把 ID 傳給 `detail` |
| `table` | 快速、人類好讀的概覽和瀏覽 |
| `plain` | 閱讀單一職缺的完整細節（`detail` 指令） |

所有錯誤都以 `{ "error": "...", "code": "..." }` 寫到 **stderr**，行程以 exit code `1` 結束。

---

## Notes

- 所有資料都來自公開的 `jobindex.dk` API，不需要憑證。
- 每頁大小固定為 20 筆結果（Jobindex API 的限制）。
- 透過 API 參數做地區篩選行不通，請改把城市名稱放進 `--query`。
- `--jobage 9999` 是預設值，會包含所有職缺，不管刊登多久。
- `meta.total` 的總數來自搜尋頁面內嵌的數字 `searchResponse.hitcount`。
- 職缺 ID 帶有字串前綴（例如 `h1647303`），原封不動傳給 `detail` 即可。
