---
name: azure-appconfiguration-ts
description: 用 Azure App Configuration SDK for JavaScript（@azure/app-configuration）建構應用程式。適用於處理設定值、feature flag、Key Vault reference、動態重新整理，或集中式設定管理。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/app-configuration'
---

# Azure App Configuration SDK for TypeScript

集中管理設定，支援 feature flag 和動態重新整理。

## Installation

```bash
# 低階 CRUD SDK
npm install @azure/app-configuration @azure/identity

# 高階 provider（應用程式建議用這個）
npm install @azure/app-configuration-provider @azure/identity

# Feature flag 管理
npm install @microsoft/feature-management
```

## Environment Variables

```bash
AZURE_APPCONFIG_ENDPOINT=https://<your-resource>.azconfig.io
# 或
AZURE_APPCONFIG_CONNECTION_STRING=Endpoint=https://...;Id=...;Secret=...
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Authentication

```typescript
import { AppConfigurationClient } from "@azure/app-configuration";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在 production 直接用指定的 credential：
// 參考 https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const client = new AppConfigurationClient(
  process.env.AZURE_APPCONFIG_ENDPOINT!,
  credential
);

// Connection string
const client2 = new AppConfigurationClient(
  process.env.AZURE_APPCONFIG_CONNECTION_STRING!
);
```

## CRUD Operations

### Create/Update Settings

```typescript
// 新增（已存在就會失敗）
await client.addConfigurationSetting({
  key: "app:settings:message",
  value: "Hello World",
  label: "production",
  contentType: "text/plain",
  tags: { environment: "prod" },
});

// Set（建立或更新）
await client.setConfigurationSetting({
  key: "app:settings:message",
  value: "Updated value",
  label: "production",
});

// 用 optimistic concurrency 更新
const existing = await client.getConfigurationSetting({ key: "myKey" });
existing.value = "new value";
await client.setConfigurationSetting(existing, { onlyIfUnchanged: true });
```

### Read Settings

```typescript
// 取得單一設定
const setting = await client.getConfigurationSetting({
  key: "app:settings:message",
  label: "production",  // 選填
});
console.log(setting.value);

// 搭配 filter 列出
const settings = client.listConfigurationSettings({
  keyFilter: "app:*",
  labelFilter: "production",
});

for await (const setting of settings) {
  console.log(`${setting.key}: ${setting.value}`);
}
```

### Delete Settings

```typescript
await client.deleteConfigurationSetting({
  key: "app:settings:message",
  label: "production",
});
```

### Lock/Unlock (Read-Only)

```typescript
// 鎖定
await client.setReadOnly({ key: "myKey", label: "prod" }, true);

// 解鎖
await client.setReadOnly({ key: "myKey", label: "prod" }, false);
```

## App Configuration Provider

### Load Configuration

```typescript
import { load } from "@azure/app-configuration-provider";
import { DefaultAzureCredential } from "@azure/identity";

const appConfig = await load(
  process.env.AZURE_APPCONFIG_ENDPOINT!,
  new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]}),
  {
    selectors: [
      { keyFilter: "app:*", labelFilter: "production" },
    ],
    trimKeyPrefixes: ["app:"],
  }
);

// Map 風格的存取
const value = appConfig.get("settings:message");

// Object 風格的存取
const config = appConfig.constructConfigurationObject({ separator: ":" });
console.log(config.settings.message);
```

### Dynamic Refresh

```typescript
const appConfig = await load(endpoint, credential, {
  selectors: [{ keyFilter: "app:*" }],
  refreshOptions: {
    enabled: true,
    refreshIntervalInMs: 30_000,  // 30 秒
  },
});

// 觸發重新整理（不會阻塞）
appConfig.refresh();

// 監聽重新整理事件
const disposer = appConfig.onRefresh(() => {
  console.log("Configuration refreshed!");
});

// Express middleware 模式
app.use((req, res, next) => {
  appConfig.refresh();
  next();
});
```

### Key Vault References

```typescript
const appConfig = await load(endpoint, credential, {
  selectors: [{ keyFilter: "app:*" }],
  keyVaultOptions: {
    credential: new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]}),
    secretRefreshIntervalInMs: 7200_000,  // 2 小時
  },
});

// Secret 會自動解析
const dbPassword = appConfig.get("database:password");
```

## Feature Flags

### Create Feature Flag (Low-Level)

```typescript
import {
  featureFlagPrefix,
  featureFlagContentType,
  FeatureFlagValue,
  ConfigurationSetting,
} from "@azure/app-configuration";

const flag: ConfigurationSetting<FeatureFlagValue> = {
  key: `${featureFlagPrefix}Beta`,
  contentType: featureFlagContentType,
  value: {
    id: "Beta",
    enabled: true,
    description: "Beta feature",
    conditions: {
      clientFilters: [
        {
          name: "Microsoft.Targeting",
          parameters: {
            Audience: {
              Users: ["user@example.com"],
              Groups: [{ Name: "beta-testers", RolloutPercentage: 50 }],
              DefaultRolloutPercentage: 0,
            },
          },
        },
      ],
    },
  },
};

await client.addConfigurationSetting(flag);
```

### Load and Evaluate Feature Flags

```typescript
import { load } from "@azure/app-configuration-provider";
import {
  ConfigurationMapFeatureFlagProvider,
  FeatureManager,
} from "@microsoft/feature-management";

const appConfig = await load(endpoint, credential, {
  featureFlagOptions: {
    enabled: true,
    selectors: [{ keyFilter: "*" }],
    refresh: {
      enabled: true,
      refreshIntervalInMs: 30_000,
    },
  },
});

const featureProvider = new ConfigurationMapFeatureFlagProvider(appConfig);
const featureManager = new FeatureManager(featureProvider);

// 簡單檢查
const isEnabled = await featureManager.isEnabled("Beta");

// 搭配 targeting context
const isEnabledForUser = await featureManager.isEnabled("Beta", {
  userId: "user@example.com",
  groups: ["beta-testers"],
});
```

## Snapshots

```typescript
// 建立 snapshot
const snapshot = await client.beginCreateSnapshotAndWait({
  name: "release-v1.0",
  retentionPeriod: 2592000,  // 30 天
  filters: [{ keyFilter: "app:*", labelFilter: "production" }],
});

// 取得 snapshot
const snap = await client.getSnapshot("release-v1.0");

// 列出 snapshot 裡的設定
const settings = client.listConfigurationSettingsForSnapshot("release-v1.0");
for await (const setting of settings) {
  console.log(`${setting.key}: ${setting.value}`);
}

// 封存/復原
await client.archiveSnapshot("release-v1.0");
await client.recoverSnapshot("release-v1.0");

// 從 snapshot 載入（provider）
const config = await load(endpoint, credential, {
  selectors: [{ snapshotName: "release-v1.0" }],
});
```

## Labels

```typescript
// 建立帶 label 的設定
await client.setConfigurationSetting({
  key: "database:host",
  value: "dev-db.example.com",
  label: "development",
});

await client.setConfigurationSetting({
  key: "database:host",
  value: "prod-db.example.com",
  label: "production",
});

// 用 label 過濾
const prodSettings = client.listConfigurationSettings({
  keyFilter: "*",
  labelFilter: "production",
});

// 沒有 label（null label）
const noLabelSettings = client.listConfigurationSettings({
  labelFilter: "\0",
});

// 列出可用的 label
for await (const label of client.listLabels()) {
  console.log(label.name);
}
```

## Key Types

```typescript
import {
  AppConfigurationClient,
  ConfigurationSetting,
  FeatureFlagValue,
  SecretReferenceValue,
  featureFlagPrefix,
  featureFlagContentType,
  secretReferenceContentType,
  ListConfigurationSettingsOptions,
} from "@azure/app-configuration";

import { load } from "@azure/app-configuration-provider";

import {
  FeatureManager,
  ConfigurationMapFeatureFlagProvider,
} from "@microsoft/feature-management";
```

## Best Practices

1. **應用程式用 provider**：執行階段設定用 `@azure/app-configuration-provider`
2. **管理用低階 SDK**：CRUD 操作用 `@azure/app-configuration`
3. **開啟 refresh**：用於動態更新設定
4. **用 label**：依環境區分設定
5. **用 snapshot**：用於不可變的 release 設定
6. **Sentinel 模式**：用一個 sentinel key 觸發完整重新整理
7. **RBAC 角色**：唯讀存取用 `App Configuration Data Reader`
