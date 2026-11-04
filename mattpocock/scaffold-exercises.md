---
layout: "default"
skill: "scaffold-exercises"
author: "Matt Pocock"
category: "設定與維護"
summary: "建立能通過 lint 的練習題目錄結構"
source: "https://github.com/mattpocock/skills/blob/main/skills/misc/scaffold-exercises/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: scaffold-exercises
description: 建立能通過 lint 的練習題目錄結構，包含章節、題目、解答和講解。當使用者想 scaffold 練習題、建立練習題的空殼，或設定新的課程章節時使用。
---

# Scaffold 練習題

建立能通過 `pnpm ai-hero-cli internal lint` 的練習題目錄結構，然後用 `git commit` commit。

## 目錄命名

- **章節**：`exercises/` 裡的 `XX-section-name/`（例如 `01-retrieval-skill-building`）
- **練習題**：章節裡的 `XX.YY-exercise-name/`（例如 `01.03-retrieval-with-bm25`）
- 章節編號 = `XX`，練習題編號 = `XX.YY`
- 名稱用 dash-case（小寫、連字號）

## 練習題變體

每個練習題至少要有這幾個子資料夾的其中一個：

- `problem/` - 學生的工作區，裡面有 TODO
- `solution/` - 參考實作
- `explainer/` - 概念性教材，沒有 TODO

建立空殼時，除非計畫另有指定，預設用 `explainer/`。

## 必要的檔案

每個子資料夾（`problem/`、`solution/`、`explainer/`）都需要一個 `readme.md`，而且要：

- **不是空的**（必須有實際內容，只有一行標題也可以）
- 沒有壞掉的連結

建立空殼時，建一個最小的 readme，有標題和說明：

```md
# Exercise Title

Description here
```

如果子資料夾有程式碼，還需要一個 `main.ts`（超過 1 行）。但如果只是空殼，只有 readme 的練習題就可以了。

## 工作流程

1. **解析計畫** - 取出章節名稱、練習題名稱和變體類型
2. **建立目錄** - 對每個路徑用 `mkdir -p`
3. **建立 readme 空殼** - 每個變體資料夾一個 `readme.md`，有標題
4. **跑 lint** - 用 `pnpm ai-hero-cli internal lint` 驗證
5. **修掉所有錯誤** - 反覆做到 lint 通過

## Lint 規則摘要

linter（`pnpm ai-hero-cli internal lint`）會檢查：

- 每個練習題都有子資料夾（`problem/`、`solution/`、`explainer/`）
- `problem/`、`explainer/` 或 `explainer.1/` 至少存在一個
- 主要子資料夾裡的 `readme.md` 存在且不是空的
- 不能有 `.gitkeep` 檔
- 不能有 `speaker-notes.md` 檔
- readme 裡不能有壞掉的連結
- readme 裡不能有 `pnpm run exercise` 指令
- 每個子資料夾都需要 `main.ts`，除非它只有 readme

## 移動/重新命名練習題

重新編號或移動練習題時：

1. 用 `git mv`（不是 `mv`）重新命名目錄，這樣能保留 git 歷史
2. 更新數字前綴，維持順序
3. 移動完要重跑 lint

範例：

```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```

## 範例：從計畫建立空殼

假設有這樣的計畫：

```
Section 05: Memory Skill Building
- 05.01 Introduction to Memory
- 05.02 Short-term Memory (explainer + problem + solution)
- 05.03 Long-term Memory
```

建立：

```bash
mkdir -p exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer
mkdir -p exercises/05-memory-skill-building/05.02-short-term-memory/{explainer,problem,solution}
mkdir -p exercises/05-memory-skill-building/05.03-long-term-memory/explainer
```

然後建立 readme 空殼：

```
exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer/readme.md -> "# Introduction to Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/explainer/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/problem/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/solution/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.03-long-term-memory/explainer/readme.md -> "# Long-term Memory"
```
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: scaffold-exercises
description: Create exercise directory structures with sections, problems, solutions, and explainers that pass linting. Use when user wants to scaffold exercises, create exercise stubs, or set up a new course section.
---

# Scaffold Exercises

Create exercise directory structures that pass `pnpm ai-hero-cli internal lint`, then commit with `git commit`.

## Directory naming

- **Sections**: `XX-section-name/` inside `exercises/` (e.g., `01-retrieval-skill-building`)
- **Exercises**: `XX.YY-exercise-name/` inside a section (e.g., `01.03-retrieval-with-bm25`)
- Section number = `XX`, exercise number = `XX.YY`
- Names are dash-case (lowercase, hyphens)

## Exercise variants

Each exercise needs at least one of these subfolders:

- `problem/` - student workspace with TODOs
- `solution/` - reference implementation
- `explainer/` - conceptual material, no TODOs

When stubbing, default to `explainer/` unless the plan specifies otherwise.

## Required files

Each subfolder (`problem/`, `solution/`, `explainer/`) needs a `readme.md` that:

- Is **not empty** (must have real content, even a single title line works)
- Has no broken links

When stubbing, create a minimal readme with a title and a description:

```md
# Exercise Title

Description here
```

If the subfolder has code, it also needs a `main.ts` (>1 line). But for stubs, a readme-only exercise is fine.

## Workflow

1. **Parse the plan** - extract section names, exercise names, and variant types
2. **Create directories** - `mkdir -p` for each path
3. **Create stub readmes** - one `readme.md` per variant folder with a title
4. **Run lint** - `pnpm ai-hero-cli internal lint` to validate
5. **Fix any errors** - iterate until lint passes

## Lint rules summary

The linter (`pnpm ai-hero-cli internal lint`) checks:

- Each exercise has subfolders (`problem/`, `solution/`, `explainer/`)
- At least one of `problem/`, `explainer/`, or `explainer.1/` exists
- `readme.md` exists and is non-empty in the primary subfolder
- No `.gitkeep` files
- No `speaker-notes.md` files
- No broken links in readmes
- No `pnpm run exercise` commands in readmes
- `main.ts` required per subfolder unless it's readme-only

## Moving/renaming exercises

When renumbering or moving exercises:

1. Use `git mv` (not `mv`) to rename directories - preserves git history
2. Update the numeric prefix to maintain order
3. Re-run lint after moves

Example:

```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```

## Example: stubbing from a plan

Given a plan like:

```
Section 05: Memory Skill Building
- 05.01 Introduction to Memory
- 05.02 Short-term Memory (explainer + problem + solution)
- 05.03 Long-term Memory
```

Create:

```bash
mkdir -p exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer
mkdir -p exercises/05-memory-skill-building/05.02-short-term-memory/{explainer,problem,solution}
mkdir -p exercises/05-memory-skill-building/05.03-long-term-memory/explainer
```

Then create readme stubs:

```
exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer/readme.md -> "# Introduction to Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/explainer/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/problem/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/solution/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.03-long-term-memory/explainer/readme.md -> "# Long-term Memory"
```
~~~~~
{% endraw %}

</section>
</div>
