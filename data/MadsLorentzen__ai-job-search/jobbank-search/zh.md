---
name: jobbank-search
version: 1.0.0
description: >
  只要使用者提到任何和 Akademikernes Jobbank、jobbank.dk 上找工作有關的事，或是在丹麥找學術或高學歷職位，
  一定要用這個 skill，即使他們沒有明講 jobbank.dk。關於丹麥職缺列表、畢業生儲備幹部（graduate trainee）職位、
  Ph.d. 職缺，或是在丹麥特定產業或地區找工作的問題，也要呼叫這個 skill。觸發詞包括：
  jobbank, akademikernes jobbank, jobs denmark, academic jobs denmark, find job
  denmark, highly educated jobs, graduate job denmark, trainee position denmark,
  ph.d. position denmark, postdoc denmark, studiejob, fuldtidsjob, deltidsjob,
  vikariat, freelance job, praktikplads, job søgning, jobsøgning, søg job,
  ledige stillinger, nye jobs, it jobs denmark, engineering jobs denmark,
  marketing jobs denmark, finance jobs denmark, healthcare jobs denmark,
  remote job denmark, fjernarbejde, job københavn, job aarhus, job odense,
  nyuddannede job, job til nyuddannede, international job denmark,
  jobbank søgning, find stilling, data scientist job, software developer job,
  projektleder stilling, konsulent job, data analyse job.
context: fork
enabled: false  # Danish demo portal - ships opt-in; /setup enables it when your market is Denmark, or set true here yourself
allowed-tools: Bash(bun run .agents/skills/jobbank-search/cli/src/cli.ts *)
---

# Jobbank Search Skill

搜尋 [Akademikernes Jobbank](https://jobbank.dk) 的即時丹麥職缺，它是丹麥針對高學歷求職者的主要求職入口。搜尋用 RSS feed（最多 100 筆結果），詳細職缺資訊則解析 JSON-LD。Jobbank 可能會用 Cloudflare 的 bot 防護擋掉自動化請求；如果發生這種情況，就回報該入口網站不可用，改用 WebSearch 備案，不要重試。

## When to use this skill

當使用者想要：

- 在丹麥搜尋工作、職位或職涯機會
- 找學術、畢業生、儲備幹部、Ph.d. 或博士後職位
- 依關鍵字、產業、地點、學歷背景或工作職能找工作
- 找丹麥的遠端或混合辦公職位
- 取得 jobbank.dk 上某個特定職缺的完整細節
- 查看某家特定公司在 jobbank.dk 上有哪些職位
- 瀏覽適合應屆畢業生或有國際背景者的職缺

## Commands

### Search jobs

```bash
bun run .agents/skills/jobbank-search/cli/src/cli.ts search [flags]
```

主要旗標：
- `--key <text>`：關鍵字搜尋（職稱、公司、關鍵字）
- `--exclude <text>`：從結果中排除關鍵字
- `--type <code>`：職缺類型：`3`=Fuldtidsjob，`6`=Graduate/trainee，`13`=Deltidsjob，`8`=Vikariat，`12`=Ph.d. & Postdoc，`11`=Freelance，`9`=Praktikplads，`4`=Studiejob（可重複）
- `--location <code>`：地區：`2`=Storkøbenhavn，`8`=Østjylland (Aarhus)，`7`=Midtjylland，`6`=Nordjylland，`13`=Fyn（可重複）
- `--work-area <code>`：職能：`31`=IT-Software，`43`=Data & Analyse，`26`=Ledelse，`29`=Marketing（可重複）
- `--industry <code>`：產業：`10331`=IT & Tele，`10442`=Forskning & Uddannelse，`10358`=Finans（可重複）
- `--education <code>`：學歷領域：`24`=IT，`21`=Økonomi & Revision，`34`=Samfundsvidenskab（可重複）
- `--remote <value>`：`helt`（完全遠端）或 `delvist`（部分遠端）
- `--suitable-for <code>`：`2`=Nyuddannede，`4`=International baggrund，`5`=Erfarne
- `--company <id>`：依公司 ID 篩選
- `--since <YYYY-MM-DD>`：在這個日期當天或之後刊登的職缺
- `--limit <n>`：限制 CLI 回傳的結果數
- `--format json|table|plain`

> **RSS 限制：** RSS feed 每次 request 最多回傳 100 筆。RSS 沒有分頁功能。`meta.total` 顯示真實的總數；`results` 上限是 100。

### Full job detail

```bash
bun run .agents/skills/jobbank-search/cli/src/cli.ts detail <id> [--format json|plain]
```

`id` 是 `search` 結果裡的數字職缺 ID。會抓取職缺頁面，並解析內嵌的 Schema.org `JobPosting` JSON-LD 取得結構化資料。

---

## How to use effectively

**先用 `search`，再用 `detail` 取得完整描述。**

1. 用 `search` 搭配 `--key` 和／或篩選條件，找出符合的職缺和它們的 ID
2. 呼叫 `detail <id>` 取得完整的 HTML 職缺描述、確切的截止日和公司細節

**多值篩選用可重複的旗標。** 大部分篩選旗標都可以重複使用，來比對任何一個值：

```bash
# IT or Finance industry, Copenhagen or Aarhus
bun run .agents/skills/jobbank-search/cli/src/cli.ts search \
  --industry 10331 --industry 10358 \
  --location 2 --location 8
```

**篩選代碼記載在 README 裡**，位置是 `skills/jobbank-search/cli/README.md`。

---

## Usage examples

### Find data scientist jobs in Copenhagen

```bash
bun run .agents/skills/jobbank-search/cli/src/cli.ts search \
  --key "data scientist" \
  --location 2 \
  --format table
```

### Graduate trainee positions for new graduates

```bash
bun run .agents/skills/jobbank-search/cli/src/cli.ts search \
  --type 6 \
  --suitable-for 2 \
  --format table
```

### Remote IT software jobs

```bash
bun run .agents/skills/jobbank-search/cli/src/cli.ts search \
  --work-area 31 \
  --remote helt \
  --format table
```

### Ph.d. and postdoc positions in research

```bash
bun run .agents/skills/jobbank-search/cli/src/cli.ts search \
  --type 12 \
  --industry 10442 \
  --format table
```

### Recent full-time jobs posted since March 1

```bash
bun run .agents/skills/jobbank-search/cli/src/cli.ts search \
  --type 3 \
  --since 2026-03-01 \
  --format table
```

### Full details for a specific job

```bash
bun run .agents/skills/jobbank-search/cli/src/cli.ts detail 1234567 --format plain
```

### IT jobs in Aarhus or Copenhagen

```bash
bun run .agents/skills/jobbank-search/cli/src/cli.ts search \
  --key developer \
  --location 2 --location 8 \
  --work-area 31 \
  --format table
```

---

## Output formats

| Format | 最適合 |
|--------|----------|
| `json` | 預設：給程式使用，把 ID 傳給 `detail` |
| `table` | 快速、人類好讀的結果清單 |
| `plain` | 單一職缺的細節檢視（`detail` 指令） |

所有錯誤都以 `{ "error": "...", "code": "..." }` 寫到 **stderr**，行程以 exit code `1` 結束。

---

## Notes

- 資料來自公開的 jobbank.dk RSS feed 和 HTML 頁面。Jobbank 仍可能用 Cloudflare bot 防護擋掉自動化的 CLI 請求；把它當成入口網站可用性的失敗，並退回用 WebSearch。
- RSS feed 每次查詢最多回傳 100 筆結果。要看更高的數量，`meta.total` 顯示真實的總數。
- `detail` 指令會抓取完整的職缺頁面，並擷取 JSON-LD 結構化資料區塊。
- `location` 的值是地區代碼（例如 `2` = Storkøbenhavn），不是城市名稱。
- 所有篩選代碼記載在 `skills/jobbank-search/cli/README.md`。
