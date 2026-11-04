---
name: dependency-upgrade
description: 管理大版本的相依套件升級，包含相容性分析、分階段 rollout 與完整測試。適用於升級 framework 版本、更新大版本相依套件，或處理函式庫 breaking change 的時候。
---

# 相依套件升級

精通大版本相依套件升級、相容性分析、分階段升級策略與完整的測試做法。

## 什麼時候用這個 Skill

- 升級 framework 大版本
- 更新有安全漏洞的相依套件
- 把老舊的相依套件現代化
- 解決相依套件衝突
- 規劃漸進式的升級路徑
- 測試相容性矩陣
- 自動化相依套件更新

## Semantic Versioning 複習

```
MAJOR.MINOR.PATCH（例如 2.3.1）

MAJOR：Breaking change
MINOR：新功能，向下相容
PATCH：Bug 修正，向下相容

^2.3.1 = >=2.3.1 <3.0.0（minor 更新）
~2.3.1 = >=2.3.1 <2.4.0（patch 更新）
2.3.1 = 固定版本
```

## 相依套件分析

### 稽核相依套件

```bash
# npm
npm outdated
npm audit
npm audit fix

# yarn
yarn outdated
yarn audit

# 檢查大版本更新
npx npm-check-updates
npx npm-check-updates -u  # 更新 package.json
```

### 分析相依樹

```bash
# 查看某個套件為什麼被安裝
npm ls package-name
yarn why package-name

# 找出重複的套件
npm dedupe
yarn dedupe

# 視覺化相依關係
npx madge --image graph.png src/
```

## 相容性矩陣

```javascript
// compatibility-matrix.js
const compatibilityMatrix = {
  react: {
    "16.x": {
      "react-dom": "^16.0.0",
      "react-router-dom": "^5.0.0",
      "@testing-library/react": "^11.0.0",
    },
    "17.x": {
      "react-dom": "^17.0.0",
      "react-router-dom": "^5.0.0 || ^6.0.0",
      "@testing-library/react": "^12.0.0",
    },
    "18.x": {
      "react-dom": "^18.0.0",
      "react-router-dom": "^6.0.0",
      "@testing-library/react": "^13.0.0",
    },
  },
};

function checkCompatibility(packages) {
  // 對照矩陣驗證套件版本
}
```

## 分階段升級策略

### 階段 1：規劃

```bash
# 1. 找出目前的版本
npm list --depth=0

# 2. 檢查 breaking change
# 讀 CHANGELOG.md 和 MIGRATION.md

# 3. 建立升級計畫
echo "升級順序：
1. TypeScript
2. React
3. React Router
4. Testing libraries
5. Build tools" > UPGRADE_PLAN.md
```

### 階段 2：漸進式更新

```bash
# 不要一次升級所有東西！

# 步驟 1：更新 TypeScript
npm install typescript@latest

# 測試
npm run test
npm run build

# 步驟 2：更新 React（一次升一個大版本）
npm install react@17 react-dom@17

# 再測試一次
npm run test

# 步驟 3：繼續處理其他套件
npm install react-router-dom@6

# 以此類推...
```

### 階段 3：驗證

```javascript
// tests/compatibility.test.js
describe("Dependency Compatibility", () => {
  it("should have compatible React versions", () => {
    const reactVersion = require("react/package.json").version;
    const reactDomVersion = require("react-dom/package.json").version;

    expect(reactVersion).toBe(reactDomVersion);
  });

  it("should not have peer dependency warnings", () => {
    // 執行 npm ls 並檢查有沒有警告
  });
});
```

## 處理 Breaking Change

### 找出 Breaking Change

```bash
# 直接查看 changelog
curl https://raw.githubusercontent.com/facebook/react/master/CHANGELOG.md
```

### 用 Codemod 自動修正

```bash
# 用 transform URL 執行 jscodeshift
npx jscodeshift -t <transform-url> <path>

# 範例：重新命名不安全的 lifecycle 方法
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js src/

# 針對 TypeScript 檔案
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js --parser=tsx src/

# Dry run，預覽變更
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js --dry src/
```

### 自訂的 Migration Script

```javascript
// migration-script.js
const fs = require("fs");
const glob = require("glob");

glob("src/**/*.tsx", (err, files) => {
  files.forEach((file) => {
    let content = fs.readFileSync(file, "utf8");

    // 把舊 API 換成新 API
    content = content.replace(
      /componentWillMount/g,
      "UNSAFE_componentWillMount",
    );

    // 更新 import
    content = content.replace(
      /import { Component } from 'react'/g,
      "import React, { Component } from 'react'",
    );

    fs.writeFileSync(file, content);
  });
});
```

## 測試策略

### 單元測試

```javascript
// 確保升級前後測試都通過
npm run test

// 需要的話更新測試工具
npm install @testing-library/react@latest
```

### 整合測試

```javascript
// tests/integration/app.test.js
describe("App Integration", () => {
  it("should render without crashing", () => {
    render(<App />);
  });

  it("should handle navigation", () => {
    const { getByText } = render(<App />);
    fireEvent.click(getByText("Navigate"));
    expect(screen.getByText("New Page")).toBeInTheDocument();
  });
});
```

### 視覺迴歸測試

```javascript
// visual-regression.test.js
describe("Visual Regression", () => {
  it("should match snapshot", () => {
    const { container } = render(<App />);
    expect(container.firstChild).toMatchSnapshot();
  });
});
```

### E2E 測試

```javascript
// cypress/e2e/app.cy.js
describe("E2E Tests", () => {
  it("should complete user flow", () => {
    cy.visit("/");
    cy.get('[data-testid="login"]').click();
    cy.get('input[name="email"]').type("user@example.com");
    cy.get('button[type="submit"]').click();
    cy.url().should("include", "/dashboard");
  });
});
```

## 自動化相依套件更新

### Renovate 設定

```json
// renovate.json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["major-update"]
    }
  ],
  "schedule": ["before 3am on Monday"],
  "timezone": "America/New_York"
}
```

### Dependabot 設定

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    reviewers:
      - "team-leads"
    commit-message:
      prefix: "chore"
      include: "scope"
```

## Rollback 計畫

```javascript
// rollback.sh
#!/bin/bash

# 保存目前狀態
git stash
git checkout -b upgrade-branch

# 嘗試升級
npm install package@latest

# 跑測試
if npm run test; then
  echo "升級成功"
  git add package.json package-lock.json
  git commit -m "chore: upgrade package"
else
  echo "升級失敗，正在 rollback"
  git checkout main
  git branch -D upgrade-branch
  npm install  # 從 package-lock.json 還原
fi
```

## 常見升級模式

### Lock File 管理

```bash
# npm
npm install --package-lock-only  # 只更新 lock file
npm ci  # 從 lock file 乾淨安裝

# yarn
yarn install --frozen-lockfile  # CI 模式
yarn upgrade-interactive  # 互動式升級
```

### Peer Dependency 處理

```bash
# npm 7+：嚴格的 peer dependency
npm install --legacy-peer-deps  # 忽略 peer dependency

# npm 8+：覆寫 peer dependency
npm install --force
```

### Workspace 升級

```bash
# 更新所有 workspace 套件
npm install --workspaces

# 更新特定 workspace
npm install package@latest --workspace=packages/app
```
