---
name: improve-claude-md
description: 用 <important if> 區塊改寫 CLAUDE.md，讓 agent 更確實遵守裡面的指示
---

使用者提供 CLAUDE.md 檔案（或要你改善一份）時，依照下面的原則和結構重寫它。

## 核心問題

Claude Code 每次載入 CLAUDE.md 時，都會附上一則 system reminder，內容是：

> "this context may or may not be relevant to your tasks. You should not respond to this context unless it is highly relevant to your task."

意思是 Claude 會忽略它覺得不相關的那部分 CLAUDE.md。跟目前任務無關的內容越多，Claude 就越可能整份都忽略，包括真正重要的部分。

## 解法：`<important if="condition">` 區塊

把 CLAUDE.md 裡只在特定條件下才相關的段落，包進 `<important if="condition">` XML 標籤。這利用的是 Claude Code 自己的 system prompt 所用的同一種 XML 標籤模式，給模型一個明確的相關性訊號，蓋過那句「may or may not be relevant」的框架。

## 原則

### 1. 基礎背景維持原樣，領域指引才包起來

不是所有東西都該放進 `<important if>` 區塊。幾乎每個任務都用得到的背景，像是專案身分、專案地圖、技術棧，要維持純 markdown 放在檔案最上面。這些是 agent 隨時都需要的 onboarding 背景。

只有特定任務才用得到的領域指引，像是測試模式、API 慣例、狀態管理、i18n，才用帶有針對性條件的 `<important if>` 區塊包起來。

經驗法則：90% 以上的任務都用得到，就維持原樣；只跟某種特定工作有關，就包起來。

### 2. 條件必須具體、有針對性

不好的寫法：條件太廣，什麼都符合：
```
<important if="you are writing or modifying any code">
- Use absolute imports
- Use functional components
- Use camelCase filenames
</important>
```

好的寫法：每條規則有自己狹窄的觸發條件：
```
<important if="you are adding or modifying imports">
- Use `@/` absolute imports (see tsconfig.json for path aliases)
- Avoid default exports except in route files
</important>

<important if="you are creating new components">
- Use functional components with explicit prop interfaces
</important>

<important if="you are creating new files or directories">
- Use camelCase for file and directory names
</important>
```

### 3. 保持簡短，漸進式揭露要節制使用

不要拆成一堆獨立檔案，讓 agent 得靠呼叫工具才找得到，除非額外的 context 真的非常冗長或複雜。

`<important if>` 區塊的重點就是所有東西都放在同一處，但依條件給不同權重：agent 全部都看得到，但只會注意符合條件的部分。

盡量讓檔案保持精簡。

### 4. 少即是多

- 前沿模型能穩定遵守的大概是幾百條。Claude Code 的 system prompt 和工具已經用掉約 50 條。你的 CLAUDE.md 要盡可能精簡。
- 砍掉任何 linter、formatter 或 pre-commit hook 能強制執行的指示
- 砍掉任何 agent 能從現有程式碼模式自己發現的指示。LLM 是 in-context learner，如果你的 codebase 一直都用某種模式，agent 搜尋幾次之後就會照著做。
- 砍掉程式碼片段。它們會過時，還會讓檔案變肥。改用檔案路徑參照（例如「範例見 `src/utils/example.ts`」）。

### 5. 指令全部保留

不要從原始檔案裡丟掉任何指令。指令表是基礎的參考資料，就算有些指令比較少用，agent 也需要知道有哪些可用。

## 輸出結構

重寫 CLAUDE.md 時，產出這個結構：

```
# CLAUDE.md

[one-line project identity — what it is, what it's built with]

## Project map
[directory listing with brief descriptions]

<important if="you need to run commands to build, test, lint, or generate code">
[commands table — all commands from the original]
</important>

<important if="<specific trigger for rule 1>">
[rule 1]
</important>

<important if="<specific trigger for rule 2>">
[rule 2]
</important>

... more rules, each with their own block ...

<important if="<specific trigger for domain area 1>">

[guidance]

</important>

... more domain sections ...
```

## 如何套用

拿到一份現有的 CLAUDE.md 要改善時：

1. **找出專案身分**：抽出一句話說明這是什麼。維持原樣放在最上面。
2. **抽出目錄地圖**：維持原樣（不加 `<important if>` 包裝）。這是基礎背景。
3. **抽出技術棧**：如果有，維持原樣放在靠近最上面的地方。濃縮成一兩行。
4. **抽出指令**：原始檔案的指令**全部**保留。用單一個 `<important if>` 區塊包起來。
5. **拆開規則**：把任何規則清單拆成一個個帶有具體條件的 `<important if>` 區塊。可以把規則分組，但絕對不要把不相關的規則塞進同一個寬鬆的條件下。
6. **包起領域段落**：測試、API 模式、狀態管理、i18n 等等，各自一個區塊，條件寫明這份知識在什麼時候重要。
7. **刪掉 linter 的地盤**：移除風格準則、格式規則，以及任何能靠工具強制執行的東西。建議改用 pre-push 或 pre-commit hook。
8. **刪掉程式碼片段**：換成檔案路徑參照。
9. **刪掉模糊的指示**：移除像「leverage the X agent」或「follow best practices」這種不具體、無法執行的東西。

## 範例

輸入：
```markdown
# CLAUDE.md

This is an Express API with a React frontend in a Turborepo monorepo.

## Commands

| Command | Description |
|---|---|
| `turbo build` | Build all packages |
| `turbo test` | Run all tests |
| `turbo lint` | Lint all packages |
| `turbo dev` | Start dev server |
| `turbo storybook` | Start Storybook |
| `turbo db:generate` | Generate Prisma client |
| `turbo db:migrate` | Run database migrations |
| `turbo analyze` | Bundle analyzer |

## Project Structure

- `apps/api/` - Express REST API
- `apps/web/` - React SPA
- `packages/db/` - Prisma schema and client
- `packages/ui/` - Shared component library
- `packages/config/` - Shared configuration

## Coding Standards

- Use named exports
- Use functional components with TypeScript interfaces for props
- Use camelCase for variables, PascalCase for components
- Prefer `const` over `let`
- Always use strict equality (`===`)
- Use template literals instead of string concatenation
- Write JSDoc comments for all public functions
- Use barrel exports in index.ts files

## API Development

- All routes go in `apps/api/src/routes/`
- Use Zod for request validation
- Use Prisma for database access
- Error responses follow RFC 7807 format
- Authentication via JWT middleware

## Testing

- Jest + Supertest for API tests
- Vitest + Testing Library for frontend
- Test fixtures in `__fixtures__/` directories
- Use `createTestClient()` helper for API integration tests
- Mock database with `prismaMock` from `packages/db/test`

## State Management

- Zustand for global client state
- React Query for server state
- URL state via `nuqs`
```

輸出：
```markdown
# CLAUDE.md

Express API + React frontend in a Turborepo monorepo.

## Project map

- `apps/api/` - Express REST API
- `apps/web/` - React SPA
- `packages/db/` - Prisma schema and client
- `packages/ui/` - Shared component library
- `packages/config/` - Shared configuration

<important if="you need to run commands to build, test, lint, or generate code">

Run with `turbo` from the repo root.

| Command | What it does |
|---|---|
| `turbo build` | Build all packages |
| `turbo test` | Run all tests |
| `turbo lint` | Lint all packages |
| `turbo dev` | Start dev server |
| `turbo storybook` | Start Storybook |
| `turbo db:generate` | Regenerate Prisma client after schema changes |
| `turbo db:migrate` | Run database migrations |
| `turbo analyze` | Bundle analyzer |
</important>

<important if="you are adding or modifying imports or exports">
- Use named exports (no default exports)
</important>

<important if="you are creating new components">
- Use functional components with TypeScript interfaces for props
</important>

<important if="you are adding or modifying API routes">

- All routes go in `apps/api/src/routes/`
- Use Zod for request validation
- Use Prisma for database access
- Error responses follow RFC 7807 format
- Authentication via JWT middleware
</important>

<important if="you are writing or modifying tests">

- API: Jest + Supertest
- Frontend: Vitest + Testing Library
- Test fixtures in `__fixtures__/` directories
- Use `createTestClient()` helper for API integration tests
- Mock database with `prismaMock` from `packages/db/test`
</important>

<important if="you are working with state management, stores, or URL parameters">

- Zustand for global client state
- React Query for server state
- URL state via `nuqs`
</important>
```

刪掉了什麼，為什麼：
- camelCase/PascalCase、const vs let、strict equality、template literals、JSDoc、barrel exports：屬於 linter 和 formatter 的地盤，或是能從現有程式碼模式發現
- 把 Coding Standards 當成一整個分組段落：拆成依觸發條件區分的針對性區塊

沒有刪掉的：
- 所有指令都保留（包括 dev、storybook、analyze）
- Project map 維持原樣（基礎背景，每個任務都相關）
