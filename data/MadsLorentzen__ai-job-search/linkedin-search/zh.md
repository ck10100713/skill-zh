---
name: linkedin-search
version: 1.0.0
description: >
  只要使用者想在任何地點或市場搜尋工作、找職缺列表，或是查詢特定職缺，
  不管是任何國家、城市，或遠端，都要用這個 skill。適用於任何產業或職位的開放職位、
  職缺和招募（軟體、資料、設計、行銷、金融、法務、營運等）。地點一律由使用者明確提供。觸發詞：
  find a job, job search, search for jobs, job openings, vacancies, hiring,
  positions open, remote jobs, "are there any X jobs in <place>", look up this
  job posting.
context: fork
enabled: true  # set to false to keep this portal installed but have /scrape skip it
allowed-tools: Bash(bun run .agents/skills/linkedin-search/cli/src/cli.ts *)
---

# LinkedIn Search Skill

搜尋 LinkedIn 公開求職板的即時職缺，適用於**任何國家／地區**（以及遠端）。不需要驗證、不需要 API key，而且**執行期零依賴**，只要有 `bun` 就能跑。地點一律明確傳入，所以同一個 skill 在任何市場的 fork 使用者手上都能直接用。

> 這是 repo 的求職入口 skill 模式的一個不分國家的實作範例。LinkedIn 的 `jobs-guest` 端點是全球通用的，HTML 解析也與國家無關；每個市場只有你傳入的 `--location` 會不同。

## ⚠️ Personal use only

這會用到 LinkedIn 的公開職缺頁面；自動化存取違反 LinkedIn 的服務條款，所以**請保持低流量，不要用於商業用途或大量收集資料。** 使用風險自負。

## When to use this skill

- 搜尋某個地點（任何國家／城市）或遠端的職缺
- 依時效（今天／最近 7／14／30 天刊登）或工作地點類型（remote/hybrid/onsite）篩選
- 取得某個特定職缺的完整描述

## Commands

### Search job listings

```bash
bun run .agents/skills/linkedin-search/cli/src/cli.ts search --location "<place>" [flags]
```

主要旗標：
- `--location <text>` / `-l <text>`：**必填。** LinkedIn 的地點字串，例如 `"Mumbai, Maharashtra, India"`、`"Berlin, Germany"`、`"London, United Kingdom"`，或 `"Remote"`。
- `--query <text>` / `-q <text>`：關鍵字搜尋（職稱、技能、角色）。建議使用。
- `--jobage <days>`：N 天內刊登：`1`、`7`、`14`、`30`。省略就是所有職缺。
- `--jobage-minutes <n>`：N 分鐘內刊登（精確到不足一天，例如 `30`）。和 `--jobage` 衝突，只能傳其中一個。
- `--remote <mode>`：`remote`、`hybrid` 或 `onsite`（工作地點類型篩選）。
- `--page <n>`：頁碼（從 1 開始，每頁 10 筆結果）。
- `--limit <n>` / `-n <n>`：限制輸出的結果總數（用戶端）。
- `--format json|table|plain`：預設 `json`。

### Fetch full job detail

```bash
bun run .agents/skills/linkedin-search/cli/src/cli.ts detail <id|url> [--format json|plain]
```

`id` 是 `search` 結果裡的職缺 ID（例如 `4426311357`）。你也可以傳完整的 LinkedIn `jobs/view/...` URL，或是 `urn:li:jobPosting:...` URN。回傳完整描述、資歷、僱用類型、職務職能和產業。

## Usage examples

```bash
# Data engineer roles in Bengaluru, last 30 days
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "data engineer" -l "Bengaluru, Karnataka, India" --jobage 30 --format table

# Product manager roles in Berlin, remote
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "product manager" -l "Berlin, Germany" --remote remote --format table

# Any role, fully remote
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "paralegal" -l "Remote" --format table

# Engineer roles, remote, posted in the last 30 minutes
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "engineer" -l "Remote" --jobage-minutes 30 --format table

# Full details for a specific job
bun run .agents/skills/linkedin-search/cli/src/cli.ts detail 4426311357 --format plain
```

## Output formats

| Format | 最適合 |
|--------|----------|
| `json` | 預設：給程式使用，把 ID 傳給 `detail` |
| `table` | 快速、人類好讀的瀏覽 |
| `plain` | 閱讀單一職缺的完整細節（`detail` 指令） |

所有錯誤都以 `{ "error": "...", "code": "..." }` 寫到 **stderr**，行程以 exit code `1` 結束。

## Notes

- 資料來自 LinkedIn 公開的 `jobs-guest` 端點，不需要憑證。
- 每頁大小固定為 10 筆結果。
- LinkedIn 可能會限流；CLI 對 429/5xx 以指數退避重試。保持低流量（見上面的服務條款說明）。
- 職缺 ID 是數字（例如 `4426311357`），原封不動傳給 `detail` 即可。
