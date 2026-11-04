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
