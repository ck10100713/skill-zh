---
name: azure-ai-contentsafety-java
description: 用 Azure AI Content Safety SDK（Java 版）建立內容審核應用程式。在實作文字／圖片分析、blocklist 管理，或針對仇恨、暴力、性內容和自傷的有害內容偵測時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-ai-contentsafety
---

# Azure AI Content Safety SDK（Java）

用 Azure AI Content Safety SDK（Java 版）建立內容審核應用程式。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-contentsafety</artifactId>
    <version>1.1.0-beta.1</version>
</dependency>
```

## 建立 Client

### 使用 API Key

```java
import com.azure.ai.contentsafety.ContentSafetyClient;
import com.azure.ai.contentsafety.ContentSafetyClientBuilder;
import com.azure.ai.contentsafety.BlocklistClient;
import com.azure.ai.contentsafety.BlocklistClientBuilder;
import com.azure.core.credential.KeyCredential;

String endpoint = System.getenv("CONTENT_SAFETY_ENDPOINT");
String key = System.getenv("CONTENT_SAFETY_KEY");

ContentSafetyClient contentSafetyClient = new ContentSafetyClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildClient();

BlocklistClient blocklistClient = new BlocklistClientBuilder()
    .credential(new KeyCredential(key))
    .endpoint(endpoint)
    .buildClient();
```

### 使用 DefaultAzureCredential

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

ContentSafetyClient client = new ContentSafetyClientBuilder()
    .credential(credential)
    .endpoint(endpoint)
    .buildClient();
```

## 核心概念

### 有害內容類別
| 類別 | 說明 |
|----------|-------------|
| Hate | 針對身分族群的歧視性語言 |
| Sexual | 性內容、關係、行為 |
| Violence | 肢體傷害、武器、受傷 |
| Self-harm | 自傷、與自殺相關的內容 |

### 嚴重程度
- 文字：0-7 級（預設輸出 0、2、4、6）
- 圖片：0、2、4、6（精簡的級距）

## 核心模式

### 分析文字

```java
import com.azure.ai.contentsafety.models.*;

AnalyzeTextResult result = contentSafetyClient.analyzeText(
    new AnalyzeTextOptions("This is text to analyze"));

for (TextCategoriesAnalysis category : result.getCategoriesAnalysis()) {
    System.out.printf("Category: %s, Severity: %d%n",
        category.getCategory(),
        category.getSeverity());
}
```

### 帶選項分析文字

```java
AnalyzeTextOptions options = new AnalyzeTextOptions("Text to analyze")
    .setCategories(Arrays.asList(
        TextCategory.HATE,
        TextCategory.VIOLENCE))
    .setOutputType(AnalyzeTextOutputType.EIGHT_SEVERITY_LEVELS);

AnalyzeTextResult result = contentSafetyClient.analyzeText(options);
```

### 搭配 Blocklist 分析文字

```java
AnalyzeTextOptions options = new AnalyzeTextOptions("I h*te you and want to k*ll you")
    .setBlocklistNames(Arrays.asList("my-blocklist"))
    .setHaltOnBlocklistHit(true);

AnalyzeTextResult result = contentSafetyClient.analyzeText(options);

if (result.getBlocklistsMatch() != null) {
    for (TextBlocklistMatch match : result.getBlocklistsMatch()) {
        System.out.printf("Blocklist: %s, Item: %s, Text: %s%n",
            match.getBlocklistName(),
            match.getBlocklistItemId(),
            match.getBlocklistItemText());
    }
}
```

### 分析圖片

```java
import com.azure.ai.contentsafety.models.*;
import com.azure.core.util.BinaryData;
import java.nio.file.Files;
import java.nio.file.Paths;

// 從檔案讀取
byte[] imageBytes = Files.readAllBytes(Paths.get("image.png"));
ContentSafetyImageData imageData = new ContentSafetyImageData()
    .setContent(BinaryData.fromBytes(imageBytes));

AnalyzeImageResult result = contentSafetyClient.analyzeImage(
    new AnalyzeImageOptions(imageData));

for (ImageCategoriesAnalysis category : result.getCategoriesAnalysis()) {
    System.out.printf("Category: %s, Severity: %d%n",
        category.getCategory(),
        category.getSeverity());
}
```

### 分析網址上的圖片

```java
ContentSafetyImageData imageData = new ContentSafetyImageData()
    .setBlobUrl("https://example.com/image.jpg");

AnalyzeImageResult result = contentSafetyClient.analyzeImage(
    new AnalyzeImageOptions(imageData));
```

## Blocklist 管理

### 建立或更新 Blocklist

```java
import com.azure.core.http.rest.RequestOptions;
import com.azure.core.http.rest.Response;
import com.azure.core.util.BinaryData;
import java.util.Map;

Map<String, String> description = Map.of("description", "Custom blocklist");
BinaryData resource = BinaryData.fromObject(description);

Response<BinaryData> response = blocklistClient.createOrUpdateTextBlocklistWithResponse(
    "my-blocklist", resource, new RequestOptions());

if (response.getStatusCode() == 201) {
    System.out.println("Blocklist created");
} else if (response.getStatusCode() == 200) {
    System.out.println("Blocklist updated");
}
```

### 新增封鎖項目

```java
import com.azure.ai.contentsafety.models.*;
import java.util.Arrays;

List<TextBlocklistItem> items = Arrays.asList(
    new TextBlocklistItem("badword1").setDescription("Offensive term"),
    new TextBlocklistItem("badword2").setDescription("Another term")
);

AddOrUpdateTextBlocklistItemsResult result = blocklistClient.addOrUpdateBlocklistItems(
    "my-blocklist",
    new AddOrUpdateTextBlocklistItemsOptions(items));

for (TextBlocklistItem item : result.getBlocklistItems()) {
    System.out.printf("Added: %s (ID: %s)%n",
        item.getText(),
        item.getBlocklistItemId());
}
```

### 列出 Blocklist

```java
PagedIterable<TextBlocklist> blocklists = blocklistClient.listTextBlocklists();

for (TextBlocklist blocklist : blocklists) {
    System.out.printf("Blocklist: %s, Description: %s%n",
        blocklist.getName(),
        blocklist.getDescription());
}
```

### 取得 Blocklist

```java
TextBlocklist blocklist = blocklistClient.getTextBlocklist("my-blocklist");
System.out.println("Name: " + blocklist.getName());
```

### 列出封鎖項目

```java
PagedIterable<TextBlocklistItem> items = 
    blocklistClient.listTextBlocklistItems("my-blocklist");

for (TextBlocklistItem item : items) {
    System.out.printf("ID: %s, Text: %s%n",
        item.getBlocklistItemId(),
        item.getText());
}
```

### 移除封鎖項目

```java
List<String> itemIds = Arrays.asList("item-id-1", "item-id-2");

blocklistClient.removeBlocklistItems(
    "my-blocklist",
    new RemoveTextBlocklistItemsOptions(itemIds));
```

### 刪除 Blocklist

```java
blocklistClient.deleteTextBlocklist("my-blocklist");
```

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;

try {
    contentSafetyClient.analyzeText(new AnalyzeTextOptions("test"));
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
    // 常見的錯誤碼：InvalidRequestBody、ResourceNotFound、TooManyRequests
}
```

## 環境變數

```bash
CONTENT_SAFETY_ENDPOINT=https://<resource>.cognitiveservices.azure.com/ # 所有認證方式都必填
CONTENT_SAFETY_KEY=<your-api-key> # 只有用 AzureKeyCredential 認證時才需要
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 最佳實務

1. **Blocklist 有延遲**：變更大約 5 分鐘後才會生效
2. **選擇類別**：只請求需要的類別，可以降低延遲
3. **嚴重程度門檻**：嚴格審核通常會封鎖嚴重程度 >= 4 的內容
4. **批次處理**：平行處理多個項目以提高吞吐量
5. **快取**：適合的地方快取 blocklist 的結果

## 觸發詞

- "content safety Java"
- "content moderation Azure"
- "analyze text safety"
- "image moderation Java"
- "blocklist management"
- "hate speech detection"
- "harmful content filter"
