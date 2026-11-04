---
name: azure-ai-document-intelligence-dotnet
description: |
  Azure AI Document Intelligence SDK（.NET 版）。用預建和自訂模型從文件擷取文字、表格和結構化資料。用於發票處理、收據擷取、身分文件分析和自訂文件模型。Triggers: "Document Intelligence", "DocumentIntelligenceClient", "form recognizer", "invoice extraction", "receipt OCR", "document analysis .NET"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.AI.DocumentIntelligence
---

# Azure.AI.DocumentIntelligence（.NET）

用預建和自訂模型從文件擷取文字、表格和結構化資料。

## 安裝

```bash
dotnet add package Azure.AI.DocumentIntelligence
dotnet add package Azure.Identity
```

**目前版本**：v1.0.0（GA）

## 環境變數

```bash
DOCUMENT_INTELLIGENCE_ENDPOINT=https://<resource-name>.cognitiveservices.azure.com/  # 必填：Document Intelligence endpoint
DOCUMENT_INTELLIGENCE_API_KEY=<your-api-key>  # 只有用 AzureKeyCredential 認證時才需要
BLOB_CONTAINER_SAS_URL=https://<storage>.blob.core.windows.net/<container>?<sas-token>  # 選填：訓練資料用的 blob container SAS URL
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

### Microsoft Entra Token Credential

```csharp
using Azure.Identity;
using Azure.AI.DocumentIntelligence;

string endpoint = Environment.GetEnvironmentVariable("DOCUMENT_INTELLIGENCE_ENDPOINT");
// 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
var client = new DocumentIntelligenceClient(new Uri(endpoint), credential);
```

> **注意**：Entra ID 需要**自訂子網域**（例如 `https://<resource-name>.cognitiveservices.azure.com/`），不能用區域 endpoint。

### API Key

```csharp
string endpoint = Environment.GetEnvironmentVariable("DOCUMENT_INTELLIGENCE_ENDPOINT");
string apiKey = Environment.GetEnvironmentVariable("DOCUMENT_INTELLIGENCE_API_KEY");
var client = new DocumentIntelligenceClient(new Uri(endpoint), new AzureKeyCredential(apiKey));
```

## Client 類型

| Client | 用途 |
|--------|---------|
| `DocumentIntelligenceClient` | 分析文件、分類文件 |
| `DocumentIntelligenceAdministrationClient` | 建立／管理自訂模型和分類器 |

## 預建模型

| Model ID | 說明 |
|----------|-------------|
| `prebuilt-read` | 擷取文字、語言、手寫內容 |
| `prebuilt-layout` | 擷取文字、表格、勾選標記、結構 |
| `prebuilt-invoice` | 擷取發票欄位（廠商、項目、總額） |
| `prebuilt-receipt` | 擷取收據欄位（商家、項目、總額） |
| `prebuilt-idDocument` | 擷取身分文件欄位（姓名、生日、地址） |
| `prebuilt-businessCard` | 擷取名片欄位 |
| `prebuilt-tax.us.w2` | 擷取 W-2 稅務表單欄位 |
| `prebuilt-healthInsuranceCard.us` | 擷取健康保險卡欄位 |

## 核心流程

### 1. 分析發票

```csharp
using Azure.AI.DocumentIntelligence;

Uri invoiceUri = new Uri("https://example.com/invoice.pdf");

Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
    WaitUntil.Completed, 
    "prebuilt-invoice", 
    invoiceUri);

AnalyzeResult result = operation.Value;

foreach (AnalyzedDocument document in result.Documents)
{
    if (document.Fields.TryGetValue("VendorName", out DocumentField vendorNameField)
        && vendorNameField.FieldType == DocumentFieldType.String)
    {
        string vendorName = vendorNameField.ValueString;
        Console.WriteLine($"Vendor Name: '{vendorName}', confidence: {vendorNameField.Confidence}");
    }

    if (document.Fields.TryGetValue("InvoiceTotal", out DocumentField invoiceTotalField)
        && invoiceTotalField.FieldType == DocumentFieldType.Currency)
    {
        CurrencyValue invoiceTotal = invoiceTotalField.ValueCurrency;
        Console.WriteLine($"Invoice Total: '{invoiceTotal.CurrencySymbol}{invoiceTotal.Amount}'");
    }
    
    // 擷取明細項目
    if (document.Fields.TryGetValue("Items", out DocumentField itemsField)
        && itemsField.FieldType == DocumentFieldType.List)
    {
        foreach (DocumentField item in itemsField.ValueList)
        {
            var itemFields = item.ValueDictionary;
            if (itemFields.TryGetValue("Description", out DocumentField descField))
                Console.WriteLine($"  Item: {descField.ValueString}");
        }
    }
}
```

### 2. 擷取版面配置（文字、表格、結構）

```csharp
Uri fileUri = new Uri("https://example.com/document.pdf");

Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
    WaitUntil.Completed, 
    "prebuilt-layout", 
    fileUri);

AnalyzeResult result = operation.Value;

// 依頁面擷取文字
foreach (DocumentPage page in result.Pages)
{
    Console.WriteLine($"Page {page.PageNumber}: {page.Lines.Count} lines, {page.Words.Count} words");
    
    foreach (DocumentLine line in page.Lines)
    {
        Console.WriteLine($"  Line: '{line.Content}'");
    }
}

// 擷取表格
foreach (DocumentTable table in result.Tables)
{
    Console.WriteLine($"Table: {table.RowCount} rows x {table.ColumnCount} columns");
    foreach (DocumentTableCell cell in table.Cells)
    {
        Console.WriteLine($"  Cell ({cell.RowIndex}, {cell.ColumnIndex}): {cell.Content}");
    }
}
```

### 3. 分析收據

```csharp
Operation<AnalyzeResult> operation = await client.AnalyzeDocumentAsync(
    WaitUntil.Completed, 
    "prebuilt-receipt", 
    receiptUri);

AnalyzeResult result = operation.Value;

foreach (AnalyzedDocument document in result.Documents)
{
    if (document.Fields.TryGetValue("MerchantName", out DocumentField merchantField))
        Console.WriteLine($"Merchant: {merchantField.ValueString}");
        
    if (document.Fields.TryGetValue("Total", out DocumentField totalField))
        Console.WriteLine($"Total: {totalField.ValueCurrency.Amount}");
        
    if (document.Fields.TryGetValue("TransactionDate", out DocumentField dateField))
        Console.WriteLine($"Date: {dateField.ValueDate}");
}
```

### 4. 建立自訂模型

```csharp
var adminClient = new DocumentIntelligenceAdministrationClient(
    new Uri(endpoint), 
    new AzureKeyCredential(apiKey));

string modelId = "my-custom-model";
Uri blobContainerUri = new Uri("<blob-container-sas-url>");

var blobSource = new BlobContentSource(blobContainerUri);
var options = new BuildDocumentModelOptions(modelId, DocumentBuildMode.Template, blobSource);

Operation<DocumentModelDetails> operation = await adminClient.BuildDocumentModelAsync(
    WaitUntil.Completed, 
    options);

DocumentModelDetails model = operation.Value;

Console.WriteLine($"Model ID: {model.ModelId}");
Console.WriteLine($"Created: {model.CreatedOn}");

foreach (var docType in model.DocumentTypes)
{
    Console.WriteLine($"Document type: {docType.Key}");
    foreach (var field in docType.Value.FieldSchema)
    {
        Console.WriteLine($"  Field: {field.Key}, Confidence: {docType.Value.FieldConfidence[field.Key]}");
    }
}
```

### 5. 建立文件分類器

```csharp
string classifierId = "my-classifier";
Uri blobContainerUri = new Uri("<blob-container-sas-url>");

var sourceA = new BlobContentSource(blobContainerUri) { Prefix = "TypeA/train" };
var sourceB = new BlobContentSource(blobContainerUri) { Prefix = "TypeB/train" };

var docTypes = new Dictionary<string, ClassifierDocumentTypeDetails>()
{
    { "TypeA", new ClassifierDocumentTypeDetails(sourceA) },
    { "TypeB", new ClassifierDocumentTypeDetails(sourceB) }
};

var options = new BuildClassifierOptions(classifierId, docTypes);

Operation<DocumentClassifierDetails> operation = await adminClient.BuildClassifierAsync(
    WaitUntil.Completed, 
    options);

DocumentClassifierDetails classifier = operation.Value;
Console.WriteLine($"Classifier ID: {classifier.ClassifierId}");
```

### 6. 分類文件

```csharp
string classifierId = "my-classifier";
Uri documentUri = new Uri("https://example.com/document.pdf");

var options = new ClassifyDocumentOptions(classifierId, documentUri);

Operation<AnalyzeResult> operation = await client.ClassifyDocumentAsync(
    WaitUntil.Completed, 
    options);

AnalyzeResult result = operation.Value;

foreach (AnalyzedDocument document in result.Documents)
{
    Console.WriteLine($"Document type: {document.DocumentType}, confidence: {document.Confidence}");
}
```

### 7. 管理模型

```csharp
// 取得資源詳細資訊
DocumentIntelligenceResourceDetails resourceDetails = await adminClient.GetResourceDetailsAsync();
Console.WriteLine($"Custom models: {resourceDetails.CustomDocumentModels.Count}/{resourceDetails.CustomDocumentModels.Limit}");

// 取得指定的模型
DocumentModelDetails model = await adminClient.GetModelAsync("my-model-id");
Console.WriteLine($"Model: {model.ModelId}, Created: {model.CreatedOn}");

// 列出模型
await foreach (DocumentModelDetails modelItem in adminClient.GetModelsAsync())
{
    Console.WriteLine($"Model: {modelItem.ModelId}");
}

// 刪除模型
await adminClient.DeleteModelAsync("my-model-id");
```

## 主要型別參考

| 型別 | 說明 |
|------|-------------|
| `DocumentIntelligenceClient` | 分析用的主要 client |
| `DocumentIntelligenceAdministrationClient` | 模型管理 |
| `AnalyzeResult` | 文件分析的結果 |
| `AnalyzedDocument` | 結果中的單一文件 |
| `DocumentField` | 擷取出的欄位，含值和信心分數 |
| `DocumentFieldType` | String、Date、Number、Currency 等 |
| `DocumentPage` | 頁面資訊（行、字、勾選標記） |
| `DocumentTable` | 擷取出的表格及其儲存格 |
| `DocumentModelDetails` | 自訂模型的 metadata |
| `BlobContentSource` | 訓練資料來源 |

## 建置模式

| 模式 | 使用情境 |
|------|----------|
| `DocumentBuildMode.Template` | 版面固定的文件（表單） |
| `DocumentBuildMode.Neural` | 版面不固定的文件 |

## 最佳實務

1. 正式環境**用 DefaultAzureCredential**
2. **重複使用 client 實例**：client 是 thread-safe 的
3. **處理長時間執行的操作**：要簡單的話用 `WaitUntil.Completed`
4. **檢查欄位信心分數**：一定要驗證 `Confidence` 屬性
5. **選對模型**：常見文件用預建的，特殊文件用自訂的
6. **用自訂子網域**：Entra ID 認證必須使用

## 錯誤處理

```csharp
using Azure;

try
{
    var operation = await client.AnalyzeDocumentAsync(
        WaitUntil.Completed, 
        "prebuilt-invoice", 
        documentUri);
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Error: {ex.Status} - {ex.Message}");
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.AI.DocumentIntelligence` | 文件分析（本 SDK） | `dotnet add package Azure.AI.DocumentIntelligence` |
| `Azure.AI.FormRecognizer` | 舊版 SDK（已棄用） | 改用 DocumentIntelligence |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.AI.DocumentIntelligence |
| API 參考 | https://learn.microsoft.com/dotnet/api/azure.ai.documentintelligence |
| GitHub 範例 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/documentintelligence/Azure.AI.DocumentIntelligence/samples |
| Document Intelligence Studio | https://documentintelligence.ai.azure.com/ |
| 預建模型 | https://aka.ms/azsdk/formrecognizer/models |
