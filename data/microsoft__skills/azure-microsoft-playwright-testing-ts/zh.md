---
name: azure-microsoft-playwright-testing-ts
description: 使用 Azure Playwright Workspaces（前身為 Microsoft Playwright Testing）大規模執行 Playwright 測試。用於在雲端託管的瀏覽器上擴展瀏覽器測試、整合 CI/CD pipeline，或把測試結果發佈到 Azure portal。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/playwright'
---

# Azure Playwright Workspaces SDK for TypeScript

用雲端託管的瀏覽器大規模執行 Playwright 測試，並整合 Azure portal 報告。

> **遷移通知：** `@azure/microsoft-playwright-testing` 將於 **2026 年 3 月 8 日**退役。請改用 `@azure/playwright`。詳見[遷移指南](https://aka.ms/mpt/migration-guidance)。

## 安裝

```bash
# 建議：自動產生設定檔
npm init @azure/playwright@latest

# 手動安裝
npm install @azure/playwright --save-dev
npm install @playwright/test@^1.47 --save-dev
npm install @azure/identity --save-dev
```

**需求：**
- Playwright 1.47+（基本用法）
- Playwright 1.57+（Azure reporter 功能）

## 環境變數

```bash
PLAYWRIGHT_SERVICE_URL=wss://eastus.api.playwright.microsoft.com/playwrightworkspaces/{workspace-id}/browsers
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證

### Microsoft Entra Token Credential（建議）

```bash
# 用 Azure CLI 登入
az login
```

```typescript
// playwright.service.config.ts
import { defineConfig } from "@playwright/test";
import { createAzurePlaywrightConfig, ServiceOS } from "@azure/playwright";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";
import config from "./playwright.config";

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在正式環境直接使用特定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

export default defineConfig(
  config,
  createAzurePlaywrightConfig(config, {
    os: ServiceOS.LINUX,
    credential,
  })
);
```

### 自訂 Credential

```typescript
import { ManagedIdentityCredential } from "@azure/identity";
import { createAzurePlaywrightConfig } from "@azure/playwright";

export default defineConfig(
  config,
  createAzurePlaywrightConfig(config, {
    credential: new ManagedIdentityCredential(),
  })
);
```

## 核心流程

### 服務設定

```typescript
// playwright.service.config.ts
import { defineConfig } from "@playwright/test";
import { createAzurePlaywrightConfig, ServiceOS } from "@azure/playwright";
import { DefaultAzureCredential } from "@azure/identity";
import config from "./playwright.config";

export default defineConfig(
  config,
  createAzurePlaywrightConfig(config, {
    os: ServiceOS.LINUX,
    connectTimeout: 30000,
    exposeNetwork: "<loopback>",
    credential: new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]}),
  })
);
```

### 執行測試

```bash
npx playwright test --config=playwright.service.config.ts --workers=20
```

### 搭配 Azure Reporter

```typescript
import { defineConfig } from "@playwright/test";
import { createAzurePlaywrightConfig, ServiceOS } from "@azure/playwright";
import { DefaultAzureCredential } from "@azure/identity";
import config from "./playwright.config";

export default defineConfig(
  config,
  createAzurePlaywrightConfig(config, {
    os: ServiceOS.LINUX,
    credential: new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]}),
  }),
  {
    reporter: [
      ["html", { open: "never" }],
      ["@azure/playwright/reporter"],
    ],
  }
);
```

### 手動連接瀏覽器

```typescript
import playwright, { test, expect, BrowserType } from "@playwright/test";
import { getConnectOptions } from "@azure/playwright";

test("manual connection", async ({ browserName }) => {
  const { wsEndpoint, options } = await getConnectOptions();
  const browser = await (playwright[browserName] as BrowserType).connect(wsEndpoint, options);
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto("https://example.com");
  await expect(page).toHaveTitle(/Example/);

  await browser.close();
});
```

## 設定選項

```typescript
type PlaywrightServiceAdditionalOptions = {
  serviceAuthType?: "ENTRA_ID" | "ACCESS_TOKEN";  // 預設：ENTRA_ID
  os?: "linux" | "windows";                        // 預設：linux
  runName?: string;                                // 在 portal 顯示的自訂 run 名稱
  connectTimeout?: number;                         // 預設：30000ms
  exposeNetwork?: string;                          // 預設：<loopback>
  credential?: TokenCredential;                    // Entra ID 必填
};
```

### ServiceOS Enum

```typescript
import { ServiceOS } from "@azure/playwright";

// 可用的值
ServiceOS.LINUX   // "linux"，預設值
ServiceOS.WINDOWS // "windows"
```

### ServiceAuth Enum

```typescript
import { ServiceAuth } from "@azure/playwright";

// 可用的值
ServiceAuth.ENTRA_ID      // 建議使用，採用 credential
ServiceAuth.ACCESS_TOKEN  // 使用 PLAYWRIGHT_SERVICE_ACCESS_TOKEN 環境變數
```

## CI/CD 整合

### GitHub Actions

```yaml
name: playwright-ts
on: [push, pull_request]

permissions:
  id-token: write
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - run: npm ci
      
      - name: Run Tests
        env:
          PLAYWRIGHT_SERVICE_URL: ${{ secrets.PLAYWRIGHT_SERVICE_URL }}
        run: npx playwright test -c playwright.service.config.ts --workers=20
```

### Azure Pipelines

```yaml
- task: AzureCLI@2
  displayName: Run Playwright Tests
  env:
    PLAYWRIGHT_SERVICE_URL: $(PLAYWRIGHT_SERVICE_URL)
  inputs:
    azureSubscription: My_Service_Connection
    scriptType: pscore
    inlineScript: |
      npx playwright test -c playwright.service.config.ts --workers=20
    addSpnToEnvironment: true
```

## 主要型別

```typescript
import {
  createAzurePlaywrightConfig,
  getConnectOptions,
  ServiceOS,
  ServiceAuth,
  ServiceEnvironmentVariable,
} from "@azure/playwright";

import type {
  OsType,
  AuthenticationType,
  BrowserConnectOptions,
  PlaywrightServiceAdditionalOptions,
} from "@azure/playwright";
```

## 從舊套件遷移

| 舊（`@azure/microsoft-playwright-testing`） | 新（`@azure/playwright`） |
|---------------------------------------------|---------------------------|
| `getServiceConfig()` | `createAzurePlaywrightConfig()` |
| `timeout` 選項 | `connectTimeout` 選項 |
| `runId` 選項 | `runName` 選項 |
| `useCloudHostedBrowsers` 選項 | 已移除（永遠啟用） |
| `@azure/microsoft-playwright-testing/reporter` | `@azure/playwright/reporter` |
| 隱含的 credential | 明確的 `credential` 參數 |

### 之前（舊）

```typescript
import { getServiceConfig, ServiceOS } from "@azure/microsoft-playwright-testing";

export default defineConfig(
  config,
  getServiceConfig(config, {
    os: ServiceOS.LINUX,
    timeout: 30000,
    useCloudHostedBrowsers: true,
  }),
  {
    reporter: [["@azure/microsoft-playwright-testing/reporter"]],
  }
);
```

### 之後（新）

```typescript
import { createAzurePlaywrightConfig, ServiceOS } from "@azure/playwright";
import { DefaultAzureCredential } from "@azure/identity";

export default defineConfig(
  config,
  createAzurePlaywrightConfig(config, {
    os: ServiceOS.LINUX,
    connectTimeout: 30000,
    credential: new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]}),
  }),
  {
    reporter: [
      ["html", { open: "never" }],
      ["@azure/playwright/reporter"],
    ],
  }
);
```

## 最佳實務

1. **使用 Microsoft Entra Token Credential**：比 access token 更安全
2. **本機開發用 `DefaultAzureCredential`；正式環境用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`**
3. **啟用 artifacts**：在設定裡加上 `trace: "on-first-retry"`、`video: "retain-on-failure"`
4. **擴充 worker 數量**：平行執行時用 `--workers=20` 或更高
5. **選擇 region**：選離你的測試目標最近的 region
6. **HTML reporter 排前面**：用 Azure reporter 時，HTML reporter 要列在 Azure reporter 之前
