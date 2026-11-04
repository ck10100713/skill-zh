---
layout: "default"
skill: "setup-matt-pocock-skills"
author: "Matt Pocock"
category: "設定與維護"
summary: "設定 issue tracker、triage 標籤和文件版面"
source: "https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: setup-matt-pocock-skills
description: "為這個 repo 設定工程類 skill：設定它的 issue tracker、triage 標籤詞彙和領域文件的版面配置。第一次使用其他工程類 skill 之前，先跑一次。"
disable-model-invocation: true
---

# 設定 Matt Pocock 的 Skills

建立工程類 skill 預設存在的每個 repo 設定：

- **Issue tracker**：issue 放在哪（預設是 GitHub；也內建支援本地 markdown）
- **Triage labels**：五個標準 triage 角色所使用的字串
- **Domain docs**：`GLOSSARY.md` 和 ADR 放在哪，以及讀取它們的使用端規則

這是 prompt 驅動的 skill，不是 deterministic 的腳本。先探索，呈現你找到的東西，跟使用者確認，再寫入。

## 流程

### 1. 探索

看目前的 repo，了解它的起始狀態。有什麼就讀什麼，不要假設：

- `git remote -v` 和 `.git/config`：這是 GitHub repo 嗎？哪一個？
- repo 根目錄的 `AGENTS.md` 和 `CLAUDE.md`：兩者有沒有存在？其中一個是否已經有 `## Agent skills` 這一節？
- repo 根目錄的 `GLOSSARY.md` 和 `GLOSSARY-MAP.md`，以及舊版的 `CONTEXT.md` / `CONTEXT-MAP.md`。如果有舊版檔案，就提議用 `git mv` 改成 `GLOSSARY` 的名稱，並改寫 `docs/agents/domain.md` 裡的那些名稱。
- `docs/adr/` 和任何 `src/*/docs/adr/` 目錄
- `docs/agents/`：這個 skill 先前的產出是不是已經存在？
- `.scratch/`：這是本地 markdown issue tracker 慣例已經在使用的跡象
- 有沒有安裝 `triage` skill？（這個 skill 旁邊有 `triage` skill 資料夾，或你可用的 skill 裡有 `triage`。）這決定 B 節要不要跑。
- Monorepo 的跡象：`pnpm-workspace.yaml`、`package.json` 裡的 `workspaces` 欄位，或是有自己 `src/` 且內容豐富的 `packages/*`。這些只會出現在真正的大型多 package repo；沒有就是單一 context，幾乎所有 repo 都是這樣。

### 2. 呈現發現並詢問

總結現有的和缺少的東西。然後依序處理各節。一節一個答案，再下一節。

每一節都先給建議答案，讓使用者一個字就能接受。只有在選擇真的有分岔時，才附上一行說明；如果探索已經決定了答案，就整節跳過（`triage` 沒安裝時跳過 B 節，沒有 monorepo 時跳過 C 節）。

**A 節：Issue tracker。**

> 說明：「issue tracker」就是這個 repo 的 issue 放的地方。像 `to-tickets`、`triage` 和 `to-spec` 這些 skill 會從它讀取、也會寫入。它們需要知道該呼叫 `gh issue create`、在 `.scratch/` 底下寫 markdown 檔，還是照你描述的其他流程。選你實際上為這個 repo 追蹤工作的地方。

預設立場：這些 skill 是為 GitHub 設計的。如果 `git remote` 指向 GitHub，就提議 GitHub。如果 `git remote` 指向 GitLab（`gitlab.com` 或自架的主機），就提議 GitLab。否則（或使用者偏好其他的話），提供：

- **GitHub**：issue 放在 repo 的 GitHub Issues（使用 `gh` CLI）
- **GitLab**：issue 放在 repo 的 GitLab Issues（使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI）
- **Local markdown**：issue 以檔案形式放在這個 repo 的 `.scratch/<feature>/` 底下（適合個人專案或沒有 remote 的 repo）
- **Other**（Jira、Linear 等）：請使用者用一段話描述工作流程；skill 會把它當成自由格式的文字記錄下來

把選擇記錄在 `docs/agents/issue-tracker.md`。GitHub 和 GitLab 的範本帶有一個「PRs as a request surface」旗標，預設**關閉**。保持關閉，也不要主動提起：想把外部 PR 放進 triage 佇列的使用者，之後可以自己去檔案裡把旗標打開。

GitHub 或 GitLab 的 tracker 需要一個連得到的 repo。當使用者選了其中一個、而沒有 `git remote` 指向那個主機時，向他們要 repo URL 並接好（需要的話先 `git init`，再 `git remote add origin <url>`），然後才繼續。完成的標準是在這個目錄裡跑 `gh repo view` / `glab repo view` 能印出專案；如果不行，就停下來告訴使用者缺了什麼。

**B 節：Triage 標籤詞彙。** 如果沒有安裝 `triage` skill（探索時會知道），就整節跳過，因為沒安裝的 skill 不需要標籤。

如果有安裝，只問剛好一個問題：

> 你要保留預設的 triage 標籤嗎？（建議：**要**）

預設是五個標準角色，每個標籤字串都等於它的名字：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。如果答**要**，原樣寫入。只有在使用者說不要時（通常是因為他們的 tracker 已經在用其他名稱，例如用 `bug:triage` 取代 `needs-triage`），才蒐集覆寫的設定，讓 `triage` 套用既有的標籤，而不是建立重複的。

**C 節：Domain docs。** 預設為**單一 context**（repo 根目錄一份 `GLOSSARY.md` + `docs/adr/`）。這適合幾乎所有 repo；不用問，直接寫。

只有探索發現 monorepo 的跡象時，才提供**多 context**（根目錄的 `GLOSSARY-MAP.md` 指向各 context 自己的 `GLOSSARY.md`）。然後確認他們要哪一種版面配置。

### 3. 確認並編輯

給使用者看以下內容的草稿：

- 要加到 `CLAUDE.md` / `AGENTS.md`（看哪個正在被編輯，選擇規則見第 4 步）的 `## Agent skills` 區塊
- `docs/agents/issue-tracker.md`、`docs/agents/domain.md` 和 `docs/agents/triage-labels.md` 的內容（最後一個只有在安裝了 `triage` 時才有）

寫入之前讓他們先編輯。

### 4. 寫入

**選要編輯的檔案：**

- 如果 `CLAUDE.md` 存在，就編輯它。
- 否則如果 `AGENTS.md` 存在，就編輯它。
- 如果兩個都不存在，問使用者要建哪一個；不要替他們選。

當 `CLAUDE.md` 已經存在時，絕對不要建立 `AGENTS.md`（反過來也一樣）；一律編輯已經存在的那一個。

如果選定的檔案裡已經有 `## Agent skills` 區塊，就直接原地更新內容，不要再附加一份重複的。不要覆蓋使用者對周圍各節的編輯。

區塊內容：

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```

只有在安裝了 `triage` 而且 B 節有跑的時候，才包含 `### Triage labels` 子區塊並寫入 `docs/agents/triage-labels.md`。沒有的話，兩者都省略。

當 B 節在 GitHub 或 GitLab 上跑過時，把 tracker 上缺少的每個設定好的標籤都建立起來（`gh label create` / `glab label create`）。

然後用這個 skill 資料夾裡的種子範本當起點，寫入文件檔：

- [issue-tracker-github.md](./issue-tracker-github.md)：GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md)：GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md)：本地 markdown issue tracker
- [triage-labels.md](./triage-labels.md)：標籤對應（只有安裝了 `triage` 時才有）
- [domain.md](./domain.md)：領域文件的使用端規則 + 版面配置

對於「other」的 issue tracker，用使用者的描述從頭寫 `docs/agents/issue-tracker.md`。

### 5. 完成

告訴使用者設定完成了，以及哪些工程類 skill 現在會讀這些檔案。提醒他們之後可以直接編輯 `docs/agents/*.md`；只有在想換 issue tracker 或想從頭重來時，才需要重跑這個 skill。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: setup-matt-pocock-skills
description: "Configure this repo for the engineering skills: set up its issue tracker, triage label vocabulary, and domain doc layout. Run once before first use of the other engineering skills."
disable-model-invocation: true
---

# Setup Matt Pocock's Skills

Scaffold the per-repo configuration that the engineering skills assume:

- **Issue tracker**: where issues live (GitHub by default; local markdown is also supported out of the box)
- **Triage labels**: the strings used for the five canonical triage roles
- **Domain docs**: where `GLOSSARY.md` and ADRs live, and the consumer rules for reading them

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config`: is this a GitHub repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root: does either exist? Is there already an `## Agent skills` section in either?
- `GLOSSARY.md` and `GLOSSARY-MAP.md` at the repo root, and the legacy `CONTEXT.md` / `CONTEXT-MAP.md`. If a legacy file exists, offer to `git mv` it to its `GLOSSARY` name and rewrite those names in `docs/agents/domain.md`.
- `docs/adr/` and any `src/*/docs/adr/` directories
- `docs/agents/`: does this skill's prior output already exist?
- `.scratch/`: a sign that a local-markdown issue tracker convention is already in use
- Is the `triage` skill installed? (a `triage` skill folder alongside this one, or `triage` in your available skills.) This decides whether Section B runs at all.
- Monorepo signals: a `pnpm-workspace.yaml`, a `workspaces` field in `package.json`, or a populated `packages/*` with its own `src/`. These are present only in a genuinely large multi-package repo; their absence means single-context, which is almost every repo.

### 2. Present findings and ask

Summarise what's present and what's missing. Then take the sections in order. One section, one answer, then the next.

Lead each section with the recommended answer so the user can accept it in a word. Give a one-line explainer only when the choice genuinely branches; skip the section entirely when exploration already settled it (Section B when `triage` isn't installed, Section C when there's no monorepo).

**Section A: Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-tickets`, `triage`, and `to-spec` read from and write to it. They need to know whether to call `gh issue create`, write a markdown file under `.scratch/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.

Default posture: these skills were designed for GitHub. If a `git remote` points at GitHub, propose that. If a `git remote` points at GitLab (`gitlab.com` or a self-hosted host), propose GitLab. Otherwise (or if the user prefers), offer:

- **GitHub**: issues live in the repo's GitHub Issues (uses the `gh` CLI)
- **GitLab**: issues live in the repo's GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Local markdown**: issues live as files under `.scratch/<feature>/` in this repo (good for solo projects or repos without a remote)
- **Other** (Jira, Linear, etc.): ask the user to describe the workflow in one paragraph; the skill will record it as freeform prose

Record the choice in `docs/agents/issue-tracker.md`. The GitHub and GitLab templates carry a "PRs as a request surface" flag, defaulted **off**. Leave it off and don't raise it: a user who wants external PRs in the triage queue can flip the flag in the file later.

A GitHub or GitLab tracker needs a reachable repo. When the user picks one and no `git remote` points at that host, get the repo URL from them and wire it up (`git init` if needed, `git remote add origin <url>`) before going further. Done when `gh repo view` / `glab repo view` prints the project from inside this directory; if it can't, stop and tell the user what's missing.

**Section B: Triage label vocabulary.** Skip this section entirely if the `triage` skill isn't installed (exploration told you), since an uninstalled skill needs no labels.

If it is installed, ask exactly one question:

> Do you want to keep the default triage labels? (recommended: **yes**)

The defaults are the five canonical roles, each label string equal to its name: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On **yes**, write them as-is. Only if the user says no, usually because their tracker already uses other names (e.g. `bug:triage` for `needs-triage`), collect the overrides so `triage` applies existing labels instead of creating duplicates.

**Section C: Domain docs.** Default to **single-context** (one `GLOSSARY.md` + `docs/adr/` at the repo root). This fits almost every repo; write it without asking.

Offer **multi-context** (a root `GLOSSARY-MAP.md` pointing to per-context `GLOSSARY.md` files) only when exploration found monorepo signals. Then confirm which layout they want.

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` block to add to whichever of `CLAUDE.md` / `AGENTS.md` is being edited (see step 4 for selection rules)
- The contents of `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, and `docs/agents/triage-labels.md` (the last only when `triage` is installed)

Let them edit before writing.

### 4. Write

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create; don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa); always edit the one that's already there.

If an `## Agent skills` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```

Include the `### Triage labels` sub-block, and write `docs/agents/triage-labels.md`, only when `triage` is installed and Section B ran. When it isn't, both are omitted.

When Section B ran on GitHub or GitLab, create each configured label the tracker lacks (`gh label create` / `glab label create`).

Then write the docs files using the seed templates in this skill folder as a starting point:

- [issue-tracker-github.md](./issue-tracker-github.md): GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md): GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md): local-markdown issue tracker
- [triage-labels.md](./triage-labels.md): label mapping (only if `triage` is installed)
- [domain.md](./domain.md): domain doc consumer rules + layout

For "other" issue trackers, write `docs/agents/issue-tracker.md` from scratch using the user's description.

### 5. Done

Tell the user the setup is complete and which engineering skills will now read from these files. Mention they can edit `docs/agents/*.md` directly later; re-running this skill is only necessary if they want to switch issue trackers or restart from scratch.
~~~~~
{% endraw %}

</section>
</div>
