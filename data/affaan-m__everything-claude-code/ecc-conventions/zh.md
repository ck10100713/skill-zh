---
name: ecc-conventions
description: ECC 的開發慣例與模式。JavaScript 專案，採用 conventional commits。
license: MIT
---

# ECC Conventions

> 由 [affaan-m/ECC](https://github.com/affaan-m/ECC) 於 2026-03-20 產生

## 概覽

這個 skill 教 Claude ECC 所採用的開發模式與慣例。

## 技術棧

- **主要語言**：JavaScript
- **架構**：混合式模組組織
- **測試位置**：獨立存放

## 何時使用這個 Skill

在下列情況啟用這個 skill：
- 修改這個 repo
- 依既有模式新增功能
- 撰寫符合專案慣例的測試
- 用正確的訊息格式建立 commit

## Commit 慣例

依據分析過的 500 個 commit，遵循以下 commit 訊息慣例。

### Commit 風格：Conventional Commits

### 使用的前綴

- `fix`
- `test`
- `feat`
- `docs`

### 訊息準則

- 訊息平均長度：約 65 個字元
- 第一行要精簡又有描述性
- 用祈使語氣（"Add feature" 而不是 "Added feature"）


*Commit 訊息範例*

```text
feat(rules): add C# language support
```

*Commit 訊息範例*

```text
chore(deps-dev): bump flatted (#675)
```

*Commit 訊息範例*

```text
fix: auto-detect ECC root from plugin cache when CLAUDE_PLUGIN_ROOT is unset (#547) (#691)
```

*Commit 訊息範例*

```text
docs: add Antigravity setup and usage guide (#552)
```

*Commit 訊息範例*

```text
merge: PR #529 — feat(skills): add documentation-lookup, bun-runtime, nextjs-turbopack; feat(agents): add rust-reviewer
```

*Commit 訊息範例*

```text
Revert "Add Kiro IDE support (.kiro/) (#548)"
```

*Commit 訊息範例*

```text
Add Kiro IDE support (.kiro/) (#548)
```

*Commit 訊息範例*

```text
feat: add block-no-verify hook for Claude Code and Cursor (#649)
```

## 架構

### 專案結構：單一套件

這個專案採用**混合式**模組組織。

### 設定檔

- `.github/workflows/ci.yml`
- `.github/workflows/maintenance.yml`
- `.github/workflows/monthly-metrics.yml`
- `.github/workflows/release.yml`
- `.github/workflows/reusable-release.yml`
- `.github/workflows/reusable-test.yml`
- `.github/workflows/reusable-validate.yml`
- `.opencode/package.json`
- `.opencode/tsconfig.json`
- `.prettierrc`
- `eslint.config.js`
- `package.json`

### 準則

- 這個專案採用混合式組織
- 新增程式碼時，依循既有模式

## 程式碼風格

### 語言：JavaScript

### 命名慣例

| 元素 | 慣例 |
|---------|------------|
| 檔案 | camelCase |
| 函式 | camelCase |
| 類別 | PascalCase |
| 常數 | SCREAMING_SNAKE_CASE |

### Import 風格：相對路徑 Import

### Export 風格：混合風格


*偏好的 import 風格*

```typescript
// Use relative imports
import { Button } from '../components/Button'
import { useAuth } from './hooks/useAuth'
```

## 測試

### 測試框架

沒有偵測到特定的測試框架，沿用這個 repo 既有的測試模式。

### 檔案模式：`*.test.js`

### 測試類型

- **單元測試**：隔離測試個別的函式與元件
- **整合測試**：測試多個元件/服務之間的互動

### Coverage

這個專案已設定 coverage 報告。目標是 80% 以上的 coverage。


## 錯誤處理

### 錯誤處理風格：Try-Catch 區塊


*標準的錯誤處理模式*

```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  throw new Error('User-friendly message')
}
```

## 常見工作流

這些工作流是分析 commit 模式後偵測出來的。

### 資料庫 Migration

用 migration 檔案做資料庫 schema 變更

**頻率**：每月約 2 次

**步驟**：
1. 建立 migration 檔案
2. 更新 schema 定義
3. 產生/更新型別

**通常會牽涉的檔案**：
- `**/schema.*`
- `migrations/*`

**Commit 序列範例**：
```
feat: implement --with/--without selective install flags (#679)
fix: sync catalog counts with filesystem (27 agents, 113 skills, 58 commands) (#693)
feat(rules): add Rust language rules (rebased #660) (#686)
```

### 功能開發

標準的功能實作流程

**頻率**：每月約 22 次

**步驟**：
1. 新增功能實作
2. 為功能新增測試
3. 更新文件

**通常會牽涉的檔案**：
- `manifests/*`
- `schemas/*`
- `**/*.test.*`
- `**/api/**`

**Commit 序列範例**：
```
feat(skills): add documentation-lookup, bun-runtime, nextjs-turbopack; feat(agents): add rust-reviewer
docs(skills): align documentation-lookup with CONTRIBUTING template; add cross-harness (Codex/Cursor) skill copies
fix: address PR review — skill template (When to use, How it works, Examples), bun.lock, next build note, rust-reviewer CI note, doc-lookup privacy/uncertainty
```

### 新增語言規則

在規則系統中新增一個程式語言，包含 coding style、hook、模式、安全與測試準則。

**頻率**：每月約 2 次

**步驟**：
1. 在 rules/{language}/ 底下建立新目錄
2. 新增 coding-style.md、hooks.md、patterns.md、security.md 和 testing.md，內容針對該語言
3. 視需要引用或連結相關的 skill

**通常會牽涉的檔案**：
- `rules/*/coding-style.md`
- `rules/*/hooks.md`
- `rules/*/patterns.md`
- `rules/*/security.md`
- `rules/*/testing.md`

**Commit 序列範例**：
```
Create a new directory under rules/{language}/
Add coding-style.md, hooks.md, patterns.md, security.md, and testing.md files with language-specific content
Optionally reference or link to related skills
```

### 新增 Skill

在系統中新增一個 skill，記錄它的工作流、觸發條件與用法，通常還附輔助 script。

**頻率**：每月約 4 次

**步驟**：
1. 在 skills/{skill-name}/ 底下建立新目錄
2. 新增 SKILL.md 並寫好文件（何時使用、運作方式、範例等）
3. 視需要在 skills/{skill-name}/scripts/ 底下新增 script 或輔助檔案
4. 處理 review 回饋並反覆修訂文件

**通常會牽涉的檔案**：
- `skills/*/SKILL.md`
- `skills/*/scripts/*.sh`
- `skills/*/scripts/*.js`

**Commit 序列範例**：
```
Create a new directory under skills/{skill-name}/
Add SKILL.md with documentation (When to Use, How It Works, Examples, etc.)
Optionally add scripts or supporting files under skills/{skill-name}/scripts/
Address review feedback and iterate on documentation
```

### 新增 Agent

在系統中新增一個 agent，用於 code review、解決 build 問題或其他自動化任務。

**頻率**：每月約 2 次

**步驟**：
1. 在 agents/{agent-name}.md 建立新的 agent markdown 檔
2. 在 AGENTS.md 註冊這個 agent
3. 視需要更新 README.md 和 docs/COMMAND-AGENT-MAP.md

**通常會牽涉的檔案**：
- `agents/*.md`
- `AGENTS.md`
- `README.md`
- `docs/COMMAND-AGENT-MAP.md`

**Commit 序列範例**：
```
Create a new agent markdown file under agents/{agent-name}.md
Register the agent in AGENTS.md
Optionally update README.md and docs/COMMAND-AGENT-MAP.md
```

### 新增 Workflow 入口

新增或更新工作流入口。預設以 skill 優先；只有在仍需要舊式 slash 相容性時才加 command shim。

**頻率**：每月約 1 次

**步驟**：
1. 在 skills/{skill-name}/SKILL.md 建立或更新正式的工作流
2. 只在需要時，才新增或更新 commands/{command-name}.md 當作相容性 shim

**通常會牽涉的檔案**：
- `skills/*/SKILL.md`
- `commands/*.md`（只有在刻意保留舊式 shim 時）

**Commit 序列範例**：
```
Create or update the canonical skill under skills/{skill-name}/SKILL.md
Only if needed, add or update commands/{command-name}.md as a compatibility shim
```

### 同步目錄數量

讓 AGENTS.md 和 README.md 裡記載的 agent、skill、command 數量，跟 repo 實際狀態一致。

**頻率**：每月約 3 次

**步驟**：
1. 更新 AGENTS.md 裡的 agent、skill、command 數量
2. 更新 README.md 裡同樣的數量（quick-start、比較表等）
3. 視需要更新其他文件檔案

**通常會牽涉的檔案**：
- `AGENTS.md`
- `README.md`

**Commit 序列範例**：
```
Update agent, skill, and command counts in AGENTS.md
Update the same counts in README.md (quick-start, comparison table, etc.)
Optionally update other documentation files
```

### 新增跨 Harness 的 Skill 副本

為不同的 agent harness（例如 Codex、Cursor、Antigravity）新增 skill 副本，確保跨平台相容。

**頻率**：每月約 2 次

**步驟**：
1. 把 SKILL.md 複製或改編到 .agents/skills/{skill}/SKILL.md 和/或 .cursor/skills/{skill}/SKILL.md
2. 視需要新增各 harness 專屬的 openai.yaml 或設定檔
3. 處理 review 回饋，對齊 CONTRIBUTING 範本

**通常會牽涉的檔案**：
- `.agents/skills/*/SKILL.md`
- `.cursor/skills/*/SKILL.md`
- `.agents/skills/*/agents/openai.yaml`

**Commit 序列範例**：
```
Copy or adapt SKILL.md to .agents/skills/{skill}/SKILL.md and/or .cursor/skills/{skill}/SKILL.md
Optionally add harness-specific openai.yaml or config files
Address review feedback to align with CONTRIBUTING template
```

### 新增或更新 Hook

新增或更新 git 或 bash hook，用來落實工作流、品質或安全政策。

**頻率**：每月約 1 次

**步驟**：
1. 在 hooks/ 或 scripts/hooks/ 新增或更新 hook script
2. 在 hooks/hooks.json 或類似的設定檔註冊 hook
3. 視需要在 tests/hooks/ 新增或更新測試

**通常會牽涉的檔案**：
- `hooks/*.hook`
- `hooks/hooks.json`
- `scripts/hooks/*.js`
- `tests/hooks/*.test.js`
- `.cursor/hooks.json`

**Commit 序列範例**：
```
Add or update hook scripts in hooks/ or scripts/hooks/
Register the hook in hooks/hooks.json or similar config
Optionally add or update tests in tests/hooks/
```

### 處理 Review 回饋

依 code review 的回饋更新文件、script 或設定，讓它更清楚、更正確或更符合慣例。

**頻率**：每月約 4 次

**步驟**：
1. 編輯 SKILL.md、agent 或 command 檔案，回應 reviewer 的意見
2. 依要求更新範例、標題或設定
3. 反覆修改直到所有 review 回饋都解決

**通常會牽涉的檔案**：
- `skills/*/SKILL.md`
- `agents/*.md`
- `commands/*.md`
- `.agents/skills/*/SKILL.md`
- `.cursor/skills/*/SKILL.md`

**Commit 序列範例**：
```
Edit SKILL.md, agent, or command files to address reviewer comments
Update examples, headings, or configuration as requested
Iterate until all review feedback is resolved
```


## 最佳實務

依據對 codebase 的分析，遵循這些做法：

### 該做

- 用 conventional commit 格式（feat:、fix: 等）
- 遵循 *.test.js 的命名模式
- 檔名用 camelCase
- 偏好混合式 export

### 不該做

- 不要寫含糊的 commit 訊息
- 新功能不要跳過測試
- 沒討論過就不要偏離既有模式

---

*這個 skill 由 [ECC Tools](https://ecc.tools) 自動產生。請依團隊需求自行檢視並客製化。*
