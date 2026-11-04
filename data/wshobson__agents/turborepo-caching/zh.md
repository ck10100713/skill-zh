---
name: turborepo-caching
description: 設定 Turborepo，用本機與遠端快取讓 monorepo 建置更有效率。設定 Turborepo、最佳化建置流水線，或實作分散式快取時使用。
---

# Turborepo Caching

Turborepo 建置最佳化的 production 模式。

## When to Use This Skill

- 設定新的 Turborepo 專案
- 設定建置流水線
- 實作遠端快取
- 最佳化 CI/CD 效能
- 從其他 monorepo 工具遷移
- 除錯 cache miss

## Core Concepts

### 1. Turborepo Architecture

```
Workspace Root/
├── apps/
│   ├── web/
│   │   └── package.json
│   └── docs/
│       └── package.json
├── packages/
│   ├── ui/
│   │   └── package.json
│   └── config/
│       └── package.json
├── turbo.json
└── package.json
```

### 2. Pipeline Concepts

| Concept        | Description                      |
| -------------- | -------------------------------- |
| **dependsOn**  | 必須先完成的任務   |
| **cache**      | 是否快取輸出         |
| **outputs**    | 要快取的檔案               |
| **inputs**     | 會影響 cache key 的檔案      |
| **persistent** | 長時間執行的任務（dev server） |

## Templates

### Template 1: turbo.json Configuration

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": [".env", ".env.local"],
  "globalEnv": ["NODE_ENV", "VERCEL_URL"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"],
      "env": ["API_URL", "NEXT_PUBLIC_*"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "inputs": ["src/**/*.tsx", "src/**/*.ts", "test/**/*.ts"]
    },
    "lint": {
      "outputs": [],
      "cache": true
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "clean": {
      "cache": false
    }
  }
}
```

### Template 2: Package-Specific Pipeline

```json
// apps/web/turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "extends": ["//"],
  "pipeline": {
    "build": {
      "outputs": [".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_ANALYTICS_ID"]
    },
    "test": {
      "outputs": ["coverage/**"],
      "inputs": ["src/**", "tests/**", "jest.config.js"]
    }
  }
}
```

### Template 3: Remote Caching with Vercel

```bash
# 登入 Vercel
npx turbo login

# 連結到 Vercel 專案
npx turbo link

# 使用遠端快取執行
turbo build --remote-only

# CI 環境變數
TURBO_TOKEN=your-token
TURBO_TEAM=your-team
```

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

env:
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
  TURBO_TEAM: ${{ vars.TURBO_TEAM }}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npx turbo build --filter='...[origin/main]'

      - name: Test
        run: npx turbo test --filter='...[origin/main]'
```

### Template 4: Self-Hosted Remote Cache

```typescript
// 自訂遠端快取伺服器（Express）
import express from "express";
import { createReadStream, createWriteStream } from "fs";
import { mkdir } from "fs/promises";
import { join } from "path";

const app = express();
const CACHE_DIR = "./cache";

// 取得 artifact
app.get("/v8/artifacts/:hash", async (req, res) => {
  const { hash } = req.params;
  const team = req.query.teamId || "default";
  const filePath = join(CACHE_DIR, team, hash);

  try {
    const stream = createReadStream(filePath);
    stream.pipe(res);
  } catch {
    res.status(404).send("Not found");
  }
});

// 存入 artifact
app.put("/v8/artifacts/:hash", async (req, res) => {
  const { hash } = req.params;
  const team = req.query.teamId || "default";
  const dir = join(CACHE_DIR, team);
  const filePath = join(dir, hash);

  await mkdir(dir, { recursive: true });

  const stream = createWriteStream(filePath);
  req.pipe(stream);

  stream.on("finish", () => {
    res.json({
      urls: [`${req.protocol}://${req.get("host")}/v8/artifacts/${hash}`],
    });
  });
});

// 檢查 artifact 是否存在
app.head("/v8/artifacts/:hash", async (req, res) => {
  const { hash } = req.params;
  const team = req.query.teamId || "default";
  const filePath = join(CACHE_DIR, team, hash);

  try {
    await fs.access(filePath);
    res.status(200).end();
  } catch {
    res.status(404).end();
  }
});

app.listen(3000, "127.0.0.1");
```

```json
// 本機快取 demo 用的 turbo.json
{
  "remoteCache": {
    "signature": false
  }
}
```

```bash
# 這個本機 demo 不會驗證假的 token。
# 只能在受信任的機器上使用可丟棄的 artifact，不要把 server 暴露出去。
turbo build --api="http://127.0.0.1:3000" --token="my-token" --team="my-team"
```

### Template 5: Filtering and Scoping

```bash
# 建置特定 package
turbo build --filter=@myorg/web

# 建置該 package 和它的相依套件
turbo build --filter=@myorg/web...

# 建置該 package 和依賴它的套件
turbo build --filter=...@myorg/ui

# 建置自 main 以來有變動的 package
turbo build --filter='...[origin/main]'

# 建置某目錄下的 package
turbo build --filter='./apps/*'

# 組合多個 filter
turbo build --filter=@myorg/web --filter=@myorg/docs

# 排除某個 package
turbo build --filter='!@myorg/docs'

# 包含有變動套件的相依套件
turbo build --filter='...[HEAD^1]...'
```

### Template 6: Advanced Pipeline Configuration

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"],
      "inputs": ["$TURBO_DEFAULT$", "!**/*.md", "!**/*.test.*"]
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"],
      "inputs": ["src/**", "tests/**", "*.config.*"],
      "env": ["CI", "NODE_ENV"]
    },
    "test:e2e": {
      "dependsOn": ["build"],
      "outputs": [],
      "cache": false
    },
    "deploy": {
      "dependsOn": ["build", "test", "lint"],
      "outputs": [],
      "cache": false
    },
    "db:generate": {
      "cache": false
    },
    "db:push": {
      "cache": false,
      "dependsOn": ["db:generate"]
    },
    "@myorg/web#build": {
      "dependsOn": ["^build", "@myorg/db#db:generate"],
      "outputs": [".next/**"],
      "env": ["NEXT_PUBLIC_*"]
    }
  }
}
```

### Template 7: Root package.json Setup

```json
{
  "name": "my-turborepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "build": "turbo build",
    "dev": "turbo dev",
    "lint": "turbo lint",
    "test": "turbo test",
    "clean": "turbo clean && rm -rf node_modules",
    "format": "prettier --write \"**/*.{ts,tsx,md}\"",
    "changeset": "changeset",
    "version-packages": "changeset version",
    "release": "turbo build --filter=./packages/* && changeset publish"
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "prettier": "^3.0.0",
    "@changesets/cli": "^2.26.0"
  },
  "packageManager": "npm@10.0.0"
}
```

## Debugging Cache

```bash
# 乾跑，看哪些任務會執行
turbo build --dry-run

# 顯示 hash 的詳細輸出
turbo build --verbosity=2

# 顯示 task graph
turbo build --graph

# 強制不使用快取
turbo build --force

# 顯示快取狀態
turbo build --summarize

# 除錯特定任務
TURBO_LOG_VERBOSITY=debug turbo build --filter=@myorg/web
```

## Best Practices

### Do's

- **Define explicit inputs** - 避免快取失效
- **Use workspace protocol** - `"@myorg/ui": "workspace:*"`
- **Enable remote caching** - 在 CI 和本機之間共用
- **Filter in CI** - 只建置受影響的 package
- **Cache build outputs** - 快取建置輸出，不要快取原始碼

### Don'ts

- **Don't cache dev servers** - 用 `persistent: true`
- **Don't include secrets in env** - 用執行期環境變數
- **Don't ignore dependsOn** - 會造成 race condition
- **Don't over-filter** - 可能會漏掉相依套件
