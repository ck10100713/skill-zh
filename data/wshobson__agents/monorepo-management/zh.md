---
name: monorepo-management
description: 精通用 Turborepo、Nx 和 pnpm workspaces 管理 monorepo，建構高效、可擴展的多 package repository，並優化建置與相依性管理。在建立 monorepo、優化建置或管理共用相依套件時使用。
---

# Monorepo Management

建構高效、可擴展的 monorepo，讓多個 package 和應用程式之間能共用程式碼、使用一致的工具，並做到原子性的變更。

## When to Use This Skill

- 建立新的 monorepo 專案
- 從 multi-repo 遷移到 monorepo
- 優化建置與測試效能
- 管理共用的相依套件
- 實作程式碼共用策略
- 為 monorepo 設定 CI/CD
- 套件的版本控管與發布
- 除錯 monorepo 特有的問題

## Core Concepts

### 1. Why Monorepos?

**優點：**

- 共用程式碼與相依套件
- 跨專案的原子性 commit
- 一致的工具與標準
- 重構更容易
- 簡化相依性管理
- 程式碼可見度更高

**挑戰：**

- 大規模時的建置效能
- CI/CD 的複雜度
- 存取控制
- Git repository 變得很大

### 2. Monorepo Tools

**套件管理工具：**

- pnpm workspaces（推薦）
- npm workspaces
- Yarn workspaces

**建置系統：**

- Turborepo（大多數情況推薦）
- Nx（功能豐富，但較複雜）
- Lerna（較舊，已進入維護模式）

## Turborepo Setup

### Initial Setup

```bash
# Create new monorepo
npx create-turbo@latest my-monorepo
cd my-monorepo

# Structure:
# apps/
#   web/          - Next.js app
#   docs/         - Documentation site
# packages/
#   ui/           - Shared UI components
#   config/       - Shared configurations
#   tsconfig/     - Shared TypeScript configs
# turbo.json      - Turborepo configuration
# package.json    - Root package.json
```

### Configuration

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "type-check": {
      "dependsOn": ["^build"],
      "outputs": []
    }
  }
}
```

```json
// package.json (root)
{
  "name": "my-monorepo",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "format": "prettier --write \"**/*.{ts,tsx,md}\"",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0"
  },
  "packageManager": "pnpm@8.0.0"
}
```

pnpm 只會從 `pnpm-workspace.yaml` 讀取 workspace package，所以要在那裡宣告（見 `references/details.md`）。Turborepo 2 把 `pipeline` 改名為 `tasks`，仍使用 `pipeline` 的 `turbo.json` 會被拒絕；要升級 1.x 的設定請執行 `npx @turbo/codemod migrate`。

### Package Structure

```json
// packages/ui/package.json
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./button": {
      "import": "./dist/button.js",
      "types": "./dist/button.d.ts"
    }
  },
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "dev": "tsup src/index.ts --format esm,cjs --dts --watch",
    "lint": "eslint src/",
    "type-check": "tsc --noEmit"
  },
  "devDependencies": {
    "@repo/tsconfig": "workspace:*",
    "tsup": "^7.0.0",
    "typescript": "^5.0.0"
  },
  "dependencies": {
    "react": "^18.2.0"
  }
}
```

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Best Practices

1. **版本一致**：在整個 workspace 鎖定相依套件的版本
2. **共用設定**：集中管理 ESLint、TypeScript、Prettier 設定
3. **相依圖**：保持無環，避免循環相依
4. **有效快取**：正確設定 inputs/outputs
5. **型別安全**：在前端/後端之間共用型別
6. **測試策略**：單元測試放在 package，E2E 放在 app
7. **文件**：每個 package 都要有 README
8. **發布策略**：用 changesets 做版本控管

## Common Pitfalls

- **循環相依**：A 依賴 B，B 又依賴 A
- **幽靈相依**：用了沒寫在 package.json 的套件
- **快取 inputs 不正確**：Turborepo 的 inputs 漏掉檔案
- **過度共用**：共用了本來應該分開的程式碼
- **共用不足**：在多個 package 之間重複程式碼
- **Monorepo 太大**：沒有適當的工具，建置會變慢

## Publishing Packages

```bash
# Using Changesets
pnpm add -Dw @changesets/cli
pnpm changeset init

# Create changeset
pnpm changeset

# Version packages
pnpm changeset version

# Publish
pnpm changeset publish
```

```yaml
# .github/workflows/release.yml
- name: Create Release Pull Request or Publish
  uses: changesets/action@v1
  with:
    publish: pnpm release
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```
