---
name: azure-appconfiguration-java
description: |
  Azure App Configuration SDK for Java。集中管理應用程式設定，支援 key-value 設定、feature flag 和 snapshot。
  Triggers: "ConfigurationClient java", "app configuration java", "feature flag java", "configuration setting java", "azure config java".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-data-appconfiguration
---

# Azure App Configuration SDK for Java

Azure App Configuration 的 client library，這是一個集中管理應用程式設定的託管服務。

## Installation

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-data-appconfiguration</artifactId>
    <version>1.8.0</version>
</dependency>
```

或使用 Azure SDK BOM：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-sdk-bom</artifactId>
            <version>{bom_version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-data-appconfiguration</artifactId>
    </dependency>
</dependencies>
```

## Prerequisites

- Azure App Configuration store
- Connection string 或 Entra ID credential

## Environment Variables

```bash
AZURE_APPCONFIG_CONNECTION_STRING=Endpoint=https://<store>.azconfig.io;Id=<id>;Secret=<secret>  # Entra ID 驗證的替代方案
AZURE_APPCONFIG_ENDPOINT=https://<store>.azconfig.io  # 所有驗證方式都需要
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Client Creation

### With Connection String

```java
import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.ConfigurationClientBuilder;

ConfigurationClient configClient = new ConfigurationClientBuilder()
    .connectionString(System.getenv("AZURE_APPCONFIG_CONNECTION_STRING"))
    .buildClient();
```

### Async Client

```java
import com.azure.data.appconfiguration.ConfigurationAsyncClient;

ConfigurationAsyncClient asyncClient = new ConfigurationClientBuilder()
    .connectionString(connectionString)
    .buildAsyncClient();
```

### With Entra ID (Recommended)

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在 production 直接用指定的 credential：
// 參考 https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

ConfigurationClient configClient = new ConfigurationClientBuilder()
    .credential(credential)
    .endpoint(System.getenv("AZURE_APPCONFIG_ENDPOINT"))
    .buildClient();
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| Configuration Setting | 帶有選用 label 的 key-value 配對 |
| Label | 用來區分設定的維度（例如環境） |
| Feature Flag | 用於功能管理的特殊設定 |
| Secret Reference | 指向 Key Vault secret 的設定 |
| Snapshot | 設定在某個時間點的不可變檢視 |

## Configuration Setting Operations

### Create Setting (Add)

只有在設定不存在時才會建立：

```java
import com.azure.data.appconfiguration.models.ConfigurationSetting;

ConfigurationSetting setting = configClient.addConfigurationSetting(
    "app/database/connection", 
    "Production", 
    "Server=prod.db.com;Database=myapp"
);
```

### Create or Update Setting (Set)

建立或覆寫：

```java
ConfigurationSetting setting = configClient.setConfigurationSetting(
    "app/cache/enabled", 
    "Production", 
    "true"
);
```

### Get Setting

```java
ConfigurationSetting setting = configClient.getConfigurationSetting(
    "app/database/connection", 
    "Production"
);
System.out.println("Value: " + setting.getValue());
System.out.println("Content-Type: " + setting.getContentType());
System.out.println("Last Modified: " + setting.getLastModified());
```

### Conditional Get (If Changed)

```java
import com.azure.core.http.rest.Response;
import com.azure.core.util.Context;

Response<ConfigurationSetting> response = configClient.getConfigurationSettingWithResponse(
    setting,      // 帶有 ETag 的設定
    null,         // Accept datetime
    true,         // ifChanged：只有被修改過才取得
    Context.NONE
);

if (response.getStatusCode() == 304) {
    System.out.println("Setting not modified");
} else {
    ConfigurationSetting updated = response.getValue();
}
```

### Update Setting

```java
ConfigurationSetting updated = configClient.setConfigurationSetting(
    "app/cache/enabled", 
    "Production", 
    "false"
);
```

### Conditional Update (If Unchanged)

```java
// 只有 ETag 相符才更新（沒有並行修改）
Response<ConfigurationSetting> response = configClient.setConfigurationSettingWithResponse(
    setting,     // 帶有目前 ETag 的設定
    true,        // ifUnchanged
    Context.NONE
);
```

### Delete Setting

```java
ConfigurationSetting deleted = configClient.deleteConfigurationSetting(
    "app/cache/enabled", 
    "Production"
);
```

### Conditional Delete

```java
Response<ConfigurationSetting> response = configClient.deleteConfigurationSettingWithResponse(
    setting,     // 帶有 ETag 的設定
    true,        // ifUnchanged
    Context.NONE
);
```

## List and Filter Settings

### List by Key Pattern

```java
import com.azure.data.appconfiguration.models.SettingSelector;
import com.azure.core.http.rest.PagedIterable;

SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/*");

PagedIterable<ConfigurationSetting> settings = configClient.listConfigurationSettings(selector);
for (ConfigurationSetting s : settings) {
    System.out.println(s.getKey() + " = " + s.getValue());
}
```

### List by Label

```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("*")
    .setLabelFilter("Production");

PagedIterable<ConfigurationSetting> settings = configClient.listConfigurationSettings(selector);
```

### List by Multiple Keys

```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/database/*,app/cache/*");

PagedIterable<ConfigurationSetting> settings = configClient.listConfigurationSettings(selector);
```

### List Revisions

```java
SettingSelector selector = new SettingSelector()
    .setKeyFilter("app/database/connection");

PagedIterable<ConfigurationSetting> revisions = configClient.listRevisions(selector);
for (ConfigurationSetting revision : revisions) {
    System.out.println("Value: " + revision.getValue() + ", Modified: " + revision.getLastModified());
}
```

## Feature Flags

### Create Feature Flag

```java
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagFilter;
import java.util.Arrays;

FeatureFlagFilter percentageFilter = new FeatureFlagFilter("Microsoft.Percentage")
    .addParameter("Value", 50);

FeatureFlagConfigurationSetting featureFlag = new FeatureFlagConfigurationSetting("beta-feature", true)
    .setDescription("Beta feature rollout")
    .setClientFilters(Arrays.asList(percentageFilter));

FeatureFlagConfigurationSetting created = (FeatureFlagConfigurationSetting)
    configClient.addConfigurationSetting(featureFlag);
```

### Get Feature Flag

```java
FeatureFlagConfigurationSetting flag = (FeatureFlagConfigurationSetting)
    configClient.getConfigurationSetting(featureFlag);

System.out.println("Feature: " + flag.getFeatureId());
System.out.println("Enabled: " + flag.isEnabled());
System.out.println("Filters: " + flag.getClientFilters());
```

### Update Feature Flag

```java
featureFlag.setEnabled(false);
FeatureFlagConfigurationSetting updated = (FeatureFlagConfigurationSetting)
    configClient.setConfigurationSetting(featureFlag);
```

## Secret References

### Create Secret Reference

```java
import com.azure.data.appconfiguration.models.SecretReferenceConfigurationSetting;

SecretReferenceConfigurationSetting secretRef = new SecretReferenceConfigurationSetting(
    "app/secrets/api-key",
    "https://myvault.vault.azure.net/secrets/api-key"
);

SecretReferenceConfigurationSetting created = (SecretReferenceConfigurationSetting)
    configClient.addConfigurationSetting(secretRef);
```

### Get Secret Reference

```java
SecretReferenceConfigurationSetting ref = (SecretReferenceConfigurationSetting)
    configClient.getConfigurationSetting(secretRef);

System.out.println("Secret URI: " + ref.getSecretId());
```

## Read-Only Settings

### Set Read-Only

```java
ConfigurationSetting readOnly = configClient.setReadOnly(
    "app/critical/setting", 
    "Production", 
    true
);
```

### Clear Read-Only

```java
ConfigurationSetting writable = configClient.setReadOnly(
    "app/critical/setting", 
    "Production", 
    false
);
```

## Snapshots

### Create Snapshot

```java
import com.azure.data.appconfiguration.models.ConfigurationSnapshot;
import com.azure.data.appconfiguration.models.ConfigurationSettingsFilter;
import com.azure.core.util.polling.SyncPoller;
import com.azure.core.util.polling.PollOperationDetails;

List<ConfigurationSettingsFilter> filters = new ArrayList<>();
filters.add(new ConfigurationSettingsFilter("app/*"));

SyncPoller<PollOperationDetails, ConfigurationSnapshot> poller = configClient.beginCreateSnapshot(
    "release-v1.0",
    new ConfigurationSnapshot(filters),
    Context.NONE
);
poller.setPollInterval(Duration.ofSeconds(10));
poller.waitForCompletion();

ConfigurationSnapshot snapshot = poller.getFinalResult();
System.out.println("Snapshot: " + snapshot.getName() + ", Status: " + snapshot.getStatus());
```

### Get Snapshot

```java
ConfigurationSnapshot snapshot = configClient.getSnapshot("release-v1.0");
System.out.println("Created: " + snapshot.getCreatedAt());
System.out.println("Items: " + snapshot.getItemCount());
```

### List Settings in Snapshot

```java
PagedIterable<ConfigurationSetting> settings = 
    configClient.listConfigurationSettingsForSnapshot("release-v1.0");

for (ConfigurationSetting setting : settings) {
    System.out.println(setting.getKey() + " = " + setting.getValue());
}
```

### Archive Snapshot

```java
ConfigurationSnapshot archived = configClient.archiveSnapshot("release-v1.0");
System.out.println("Status: " + archived.getStatus()); // archived
```

### Recover Snapshot

```java
ConfigurationSnapshot recovered = configClient.recoverSnapshot("release-v1.0");
System.out.println("Status: " + recovered.getStatus()); // ready
```

### List All Snapshots

```java
import com.azure.data.appconfiguration.models.SnapshotSelector;

SnapshotSelector selector = new SnapshotSelector().setNameFilter("release-*");
PagedIterable<ConfigurationSnapshot> snapshots = configClient.listSnapshots(selector);

for (ConfigurationSnapshot snap : snapshots) {
    System.out.println(snap.getName() + " - " + snap.getStatus());
}
```

## Labels

### List Labels

```java
import com.azure.data.appconfiguration.models.SettingLabelSelector;

configClient.listLabels(new SettingLabelSelector().setNameFilter("*"))
    .forEach(label -> System.out.println("Label: " + label.getName()));
```

## Async Operations

```java
ConfigurationAsyncClient asyncClient = new ConfigurationClientBuilder()
    .connectionString(connectionString)
    .buildAsyncClient();

// 用 reactive stream 做非同步列表
asyncClient.listConfigurationSettings(new SettingSelector().setLabelFilter("Production"))
    .subscribe(
        setting -> System.out.println(setting.getKey() + " = " + setting.getValue()),
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Completed")
    );
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    configClient.getConfigurationSetting("nonexistent", null);
} catch (HttpResponseException e) {
    if (e.getResponse().getStatusCode() == 404) {
        System.err.println("Setting not found");
    } else {
        System.err.println("Error: " + e.getMessage());
    }
}
```

## Best Practices

1. **用 label**：依環境（Dev、Staging、Production）區分設定
2. **用 snapshot**：為每次 release 建立不可變的 snapshot
3. **Feature flag**：用於漸進式推出和 A/B 測試
4. **Secret reference**：把敏感值存在 Key Vault
5. **條件式請求**：用 ETag 做 optimistic concurrency
6. **唯讀保護**：鎖住關鍵的 production 設定
7. **用 Entra ID**：比 connection string 更好
8. **非同步 client**：用於高吞吐量情境

## Reference Links

| Resource | URL |
|----------|-----|
| Maven Package | https://central.sonatype.com/artifact/com.azure/azure-data-appconfiguration |
| GitHub | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/appconfiguration/azure-data-appconfiguration |
| API Documentation | https://aka.ms/java-docs |
| Product Docs | https://learn.microsoft.com/azure/azure-app-configuration |
| Samples | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/appconfiguration/azure-data-appconfiguration/src/samples |
| Troubleshooting | https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/appconfiguration/azure-data-appconfiguration/TROUBLESHOOTING.md |
