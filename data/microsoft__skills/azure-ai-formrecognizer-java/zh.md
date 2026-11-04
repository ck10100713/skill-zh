---
name: azure-ai-formrecognizer-java
description: |
  Azure AI Document Intelligence SDK（Java 版，com.azure:azure-ai-documentintelligence）。
  用於從文件、收據、發票、身分證件擷取文字、表格、key-value 配對，或建立自訂文件模型。
  Triggers: "document intelligence java", "form recognizer java", "extract text from PDF java", "OCR document java",
  "analyze invoice receipt java", "custom document model java", "document classification java"。
---

# Azure AI Document Intelligence SDK（Java）

> **更名：** Azure AI Form Recognizer 現在叫做 **Azure AI Document Intelligence**。
> 新專案應該用 `com.azure:azure-ai-documentintelligence`。舊的 `azure-ai-formrecognizer` 套件只支援 API 版本 2023-07-31。
> 請看[遷移指南](https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/MIGRATION_GUIDE.md)。

## 實作之前

先用 `microsoft-docs` MCP 搜尋目前的 API 用法：
- 查詢：`"azure-ai-documentintelligence Java SDK"`
- 驗證：參數要和已安裝的 SDK 版本相符（最新 GA：1.0.7）

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-documentintelligence</artifactId>
    <version>1.0.0</version>
</dependency>

<!-- 使用 DefaultAzureCredential 時需要 -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.14.2</version>
</dependency>
```

## 環境變數

```bash
DOCUMENT_INTELLIGENCE_ENDPOINT=https://<resource>.cognitiveservices.azure.com/ # 所有認證方式都必填
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

### DefaultAzureCredential（建議）

```java
import com.azure.ai.documentintelligence.DocumentIntelligenceClient;
import com.azure.ai.documentintelligence.DocumentIntelligenceClientBuilder;
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

DocumentIntelligenceClient client = new DocumentIntelligenceClientBuilder()
    .endpoint(System.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"))
    .credential(credential)
    .buildClient();
```

### API Key

```java
import com.azure.core.credential.AzureKeyCredential;

DocumentIntelligenceClient client = new DocumentIntelligenceClientBuilder()
    .endpoint(System.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"))
    .credential(new AzureKeyCredential(System.getenv("DOCUMENT_INTELLIGENCE_KEY")))
    .buildClient();
```

### Administration Client

```java
import com.azure.ai.documentintelligence.DocumentIntelligenceAdministrationClient;
import com.azure.ai.documentintelligence.DocumentIntelligenceAdministrationClientBuilder;
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

DocumentIntelligenceAdministrationClient adminClient = new DocumentIntelligenceAdministrationClientBuilder()
    .endpoint(System.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"))
    .credential(credential)
    .buildClient();
```

### 非同步 Client

```java
import com.azure.ai.documentintelligence.DocumentIntelligenceAsyncClient;
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

DocumentIntelligenceAsyncClient asyncClient = new DocumentIntelligenceClientBuilder()
    .endpoint(System.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"))
    .credential(credential)
    .buildAsyncClient();
```

## 預建模型

| Model ID | 用途 |
|----------|---------|
| `prebuilt-read` | 擷取文字、行、字、語言 |
| `prebuilt-layout` | 文字、表格、勾選標記、結構 |
| `prebuilt-receipt` | 收據資料擷取 |
| `prebuilt-invoice` | 發票欄位擷取 |
| `prebuilt-idDocument` | 身分文件（護照、駕照） |
| `prebuilt-tax.us.w2` | 美國 W2 稅務表單 |
| `prebuilt-healthInsuranceCard.us` | 美國健康保險卡 |
| `prebuilt-contract` | 合約欄位擷取 |

> **已退役的模型：** `prebuilt-businessCard` 和 `prebuilt-document` 在 API 版本 2024-11-30 已退役。這些請改用舊的 `azure-ai-formrecognizer` 套件。

## 核心模式

### 從檔案分析

```java
import com.azure.ai.documentintelligence.models.*;
import com.azure.core.util.BinaryData;
import com.azure.core.util.polling.SyncPoller;
import java.io.File;

File document = new File("document.pdf");
BinaryData documentData = BinaryData.fromFile(document.toPath(), (int) document.length());

SyncPoller<AnalyzeOperationDetails, AnalyzeResult> poller =
    client.beginAnalyzeDocument("prebuilt-layout",
        new AnalyzeDocumentOptions(documentData));

AnalyzeResult result = poller.getFinalResult();
```

### 從 URL 分析

```java
String documentUrl = "https://example.com/invoice.pdf";

SyncPoller<AnalyzeOperationDetails, AnalyzeResult> poller =
    client.beginAnalyzeDocument("prebuilt-invoice",
        new AnalyzeDocumentOptions(documentUrl));

AnalyzeResult result = poller.getFinalResult();
```

### 擷取版面配置

```java
AnalyzeResult result = poller.getFinalResult();

for (DocumentPage page : result.getPages()) {
    System.out.printf("Page has width: %.2f and height: %.2f, measured with unit: %s%n",
        page.getWidth(), page.getHeight(), page.getUnit());

    // 行
    for (DocumentLine line : page.getLines()) {
        System.out.printf("Line '%s' is within bounding box %s.%n",
            line.getContent(), line.getPolygon());
    }

    // 勾選標記
    for (DocumentSelectionMark mark : page.getSelectionMarks()) {
        System.out.printf("Selection mark is '%s' with confidence %.2f.%n",
            mark.getState(), mark.getConfidence());
    }
}

// 表格
for (DocumentTable table : result.getTables()) {
    System.out.printf("Table: %d rows x %d columns%n",
        table.getRowCount(), table.getColumnCount());
    for (DocumentTableCell cell : table.getCells()) {
        System.out.printf("Cell[%d,%d]: %s%n",
            cell.getRowIndex(), cell.getColumnIndex(), cell.getContent());
    }
}
```

### 擷取文件欄位

```java
SyncPoller<AnalyzeOperationDetails, AnalyzeResult> poller =
    client.beginAnalyzeDocument("prebuilt-receipt",
        new AnalyzeDocumentOptions(receiptUrl));

AnalyzeResult result = poller.getFinalResult();

for (AnalyzedDocument doc : result.getDocuments()) {
    Map<String, DocumentField> fields = doc.getFields();

    DocumentField merchantName = fields.get("MerchantName");
    if (merchantName != null && merchantName.getType() == DocumentFieldType.STRING) {
        System.out.printf("Merchant: %s (confidence: %.2f)%n",
            merchantName.getValueString(), merchantName.getConfidence());
    }

    DocumentField transactionDate = fields.get("TransactionDate");
    if (transactionDate != null && transactionDate.getType() == DocumentFieldType.DATE) {
        System.out.printf("Date: %s%n", transactionDate.getValueDate());
    }
}
```

### 帶選項分析

```java
SyncPoller<AnalyzeOperationDetails, AnalyzeResult> poller =
    client.beginAnalyzeDocument("my-custom-model",
        new AnalyzeDocumentOptions(documentUrl)
            .setPages(Collections.singletonList("1-3"))
            .setLocale("en-US")
            .setDocumentAnalysisFeatures(Arrays.asList(DocumentAnalysisFeature.LANGUAGES))
            .setOutputContentFormat(DocumentContentFormat.TEXT));
```

## 自訂模型

### 建立自訂模型

```java
String blobContainerUrl = "{SAS_URL_of_training_data}";

SyncPoller<DocumentModelBuildOperationDetails, DocumentModelDetails> poller =
    adminClient.beginBuildDocumentModel(
        new BuildDocumentModelOptions("my-custom-model", DocumentBuildMode.TEMPLATE)
            .setAzureBlobSource(new AzureBlobContentSource(blobContainerUrl)));

DocumentModelDetails model = poller.getFinalResult();
System.out.printf("Model ID: %s%n", model.getModelId());
System.out.printf("Created: %s%n", model.getCreatedOn());

model.getDocumentTypes().forEach((docType, details) -> {
    details.getFieldSchema().forEach((field, schema) -> {
        System.out.printf("Field: %s (%s)%n", field, schema.getType());
    });
});
```

### 管理模型

```java
// 資源上限
DocumentIntelligenceResourceDetails resourceDetails = adminClient.getResourceDetails();
System.out.printf("Models: %d / %d%n",
    resourceDetails.getCustomDocumentModels().getCount(),
    resourceDetails.getCustomDocumentModels().getLimit());

// 列出模型
PagedIterable<DocumentModelDetails> models = adminClient.listModels();
for (DocumentModelDetails model : models) {
    System.out.printf("Model: %s, Created: %s%n",
        model.getModelId(), model.getCreatedOn());
}

// 取得模型
DocumentModelDetails model = adminClient.getModel("model-id");

// 刪除模型
adminClient.deleteModel("model-id");
```

## 文件分類

### 建立分類器

```java
Map<String, ClassifierDocumentTypeDetails> docTypes = new HashMap<>();
docTypes.put("invoice", new ClassifierDocumentTypeDetails()
    .setAzureBlobSource(new AzureBlobContentSource(containerUrl).setPrefix("invoices/")));
docTypes.put("receipt", new ClassifierDocumentTypeDetails()
    .setAzureBlobSource(new AzureBlobContentSource(containerUrl).setPrefix("receipts/")));

SyncPoller<DocumentClassifierBuildOperationDetails, DocumentClassifierDetails> poller =
    adminClient.beginBuildClassifier(
        new BuildDocumentClassifierOptions("my-classifier", docTypes));

DocumentClassifierDetails classifier = poller.getFinalResult();
```

### 分類文件

```java
SyncPoller<AnalyzeOperationDetails, AnalyzeResult> poller =
    client.beginClassifyDocument("my-classifier",
        new ClassifyDocumentOptions(documentUrl));

AnalyzeResult result = poller.getFinalResult();
for (AnalyzedDocument doc : result.getDocuments()) {
    System.out.printf("Classified as: %s (confidence: %.2f)%n",
        doc.getDocumentType(), doc.getConfidence());
}
```

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;

try {
    client.beginAnalyzeDocument("prebuilt-receipt",
        new AnalyzeDocumentOptions("invalid-url"));
} catch (HttpResponseException e) {
    System.out.printf("Status: %d, Error: %s%n",
        e.getResponse().getStatusCode(), e.getMessage());
}
```

## 從 azure-ai-formrecognizer 遷移

| 舊（formrecognizer v4.x） | 新（documentintelligence v1.x） |
|---|---|
| `DocumentAnalysisClient` | `DocumentIntelligenceClient` |
| `DocumentAnalysisClientBuilder` | `DocumentIntelligenceClientBuilder` |
| `DocumentModelAdministrationClient` | `DocumentIntelligenceAdministrationClient` |
| `beginAnalyzeDocumentFromUrl(modelId, url)` | `beginAnalyzeDocument(modelId, new AnalyzeDocumentOptions(url))` |
| `beginAnalyzeDocument(modelId, data)` | `beginAnalyzeDocument(modelId, new AnalyzeDocumentOptions(data))` |
| `SyncPoller<OperationResult, AnalyzeResult>` | `SyncPoller<AnalyzeOperationDetails, AnalyzeResult>` |
| `field.getValueAsString()` | `field.getValueString()` |
| `field.getValueAsDate()` | `field.getValueDate()` |
| `field.getValueAsDouble()` | `field.getValueNumber()` |
| `field.getValueAsList()` | `field.getValueList()` |
| `field.getValueAsMap()` | `field.getValueObject()` |
| `mark.getSelectionMarkState()` | `mark.getState()` |
| `adminClient.beginBuildDocumentModel(url, mode, prefix, options, ctx)` | `adminClient.beginBuildDocumentModel(new BuildDocumentModelOptions(id, mode).setAzureBlobSource(...))` |
| `adminClient.getResourceDetails()` → `.getCustomDocumentModelCount()` | `adminClient.getResourceDetails()` → `.getCustomDocumentModels().getCount()` |
| `FORM_RECOGNIZER_ENDPOINT` | `DOCUMENT_INTELLIGENCE_ENDPOINT` |

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/examples.md](references/examples.md) | 所有情境的完整程式碼範例 |
