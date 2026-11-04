---
layout: "default"
skill: "setup-pre-commit"
author: "Matt Pocock"
category: "設定與維護"
summary: "設定 Husky 加 lint-staged 的 pre-commit hook"
source: "https://github.com/mattpocock/skills/blob/main/skills/misc/setup-pre-commit/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: setup-pre-commit
description: 在目前的 repo 設定 Husky pre-commit hook，搭配 lint-staged（Prettier）、型別檢查和測試。當使用者想加 pre-commit hook、設定 Husky、設定 lint-staged，或加上 commit 時的格式化/型別檢查/測試時使用。
---

# 設定 Pre-Commit Hook

## 這會設定什麼

- **Husky** pre-commit hook
- **lint-staged**，對所有 staged 的檔案跑 Prettier
- **Prettier** 設定（如果沒有的話）
- pre-commit hook 裡的 **typecheck** 和 **test** 腳本

## 步驟

### 1. 偵測套件管理器

檢查 `package-lock.json`（npm）、`pnpm-lock.yaml`（pnpm）、`yarn.lock`（yarn）、`bun.lockb`（bun）。有哪個就用哪個。不確定就預設用 npm。

### 2. 安裝依賴

以 devDependencies 安裝：

```
husky lint-staged prettier
```

### 3. 初始化 Husky

```bash
npx husky init
```

這會建立 `.husky/` 目錄，並在 package.json 加上 `prepare: "husky"`。

### 4. 建立 `.husky/pre-commit`

寫入這個檔案（Husky v9+ 不需要 shebang）：

```
npx lint-staged
npm run typecheck
npm run test
```

**調整**：把 `npm` 換成偵測到的套件管理器。如果 repo 的 package.json 沒有 `typecheck` 或 `test` 腳本，就省略那幾行，並告訴使用者。

### 5. 建立 `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. 建立 `.prettierrc`（如果沒有的話）

只有在沒有任何 Prettier 設定時才建立。使用這些預設值：

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```

### 7. 驗證

- [ ] `.husky/pre-commit` 存在而且可執行
- [ ] `.lintstagedrc` 存在
- [ ] package.json 裡的 `prepare` 腳本是 `"husky"`
- [ ] `prettier` 設定存在
- [ ] 跑 `npx lint-staged` 確認它能運作

### 8. Commit

把所有改動/新建的檔案 stage 起來，用這個訊息 commit：`Add pre-commit hooks (husky + lint-staged + prettier)`

這個 commit 會跑過新的 pre-commit hook：剛好是個不錯的 smoke test，確認一切都正常。

## 備註

- Husky v9+ 的 hook 檔不需要 shebang
- `prettier --ignore-unknown` 會跳過 Prettier 解析不了的檔案（圖片等等）
- pre-commit 先跑 lint-staged（快，只處理 staged 的檔案），再跑完整的 typecheck 和測試
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: setup-pre-commit
description: Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hooks, set up Husky, configure lint-staged, or add commit-time formatting/typechecking/testing.
---

# Setup Pre-Commit Hooks

## What This Sets Up

- **Husky** pre-commit hook
- **lint-staged** running Prettier on all staged files
- **Prettier** config (if missing)
- **typecheck** and **test** scripts in the pre-commit hook

## Steps

### 1. Detect package manager

Check for `package-lock.json` (npm), `pnpm-lock.yaml` (pnpm), `yarn.lock` (yarn), `bun.lockb` (bun). Use whichever is present. Default to npm if unclear.

### 2. Install dependencies

Install as devDependencies:

```
husky lint-staged prettier
```

### 3. Initialize Husky

```bash
npx husky init
```

This creates `.husky/` dir and adds `prepare: "husky"` to package.json.

### 4. Create `.husky/pre-commit`

Write this file (no shebang needed for Husky v9+):

```
npx lint-staged
npm run typecheck
npm run test
```

**Adapt**: Replace `npm` with detected package manager. If repo has no `typecheck` or `test` script in package.json, omit those lines and tell the user.

### 5. Create `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. Create `.prettierrc` (if missing)

Only create if no Prettier config exists. Use these defaults:

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```

### 7. Verify

- [ ] `.husky/pre-commit` exists and is executable
- [ ] `.lintstagedrc` exists
- [ ] `prepare` script in package.json is `"husky"`
- [ ] `prettier` config exists
- [ ] Run `npx lint-staged` to verify it works

### 8. Commit

Stage all changed/created files and commit with message: `Add pre-commit hooks (husky + lint-staged + prettier)`

This will run through the new pre-commit hooks: a good smoke test that everything works.

## Notes

- Husky v9+ doesn't need shebangs in hook files
- `prettier --ignore-unknown` skips files Prettier can't parse (images, etc.)
- The pre-commit runs lint-staged first (fast, staged-only), then full typecheck and tests
~~~~~
{% endraw %}

</section>
</div>
