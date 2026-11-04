---
name: azure-ai-document-intelligence-ts
description: 用 Azure Document Intelligence（@azure-rest/ai-document-intelligence）從文件擷取文字、表格和結構化資料。在處理發票、收據、身分證件、表單，或建立自訂文件模型時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure-rest/ai-document-intelligence'
---

# Azure Document Intelligence REST SDK（TypeScript）

用預建和自訂模型從文件擷取文字、表格和結構化資料。

## 安裝

```bash
npm install @azure-rest/ai-document-intelligence @azure/identity
```

## 環境變數

```bash
DOCUMENT_INTELLIGENCE_ENDPOINT=https://<resource>.cognitiveservices.azure.com
DOCUMENT_INTELLIGENCE_API_KEY=<api-key>
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

**重要**：這是 REST client。`DocumentIntelligence` 是**函式**，不是 class。

### DefaultAzureCredential

```typescript
import DocumentIntelligence from "@azure-rest/ai-document-intelligence";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const client = DocumentIntelligence(
  process.env.DOCUMENT_INTELLIGENCE_ENDPOINT!,
  credential
);
```

### API Key

```typescript
import DocumentIntelligence from "@azure-rest/ai-document-intelligence";

const client = DocumentIntelligence(
  process.env.DOCUMENT_INTELLIGENCE_ENDPOINT!,
  { key: process.env.DOCUMENT_INTELLIGENCE_API_KEY! }
);
```

## 分析文件（URL）

```typescript
import DocumentIntelligence, {
  isUnexpected,
  getLongRunningPoller,
  AnalyzeOperationOutput
} from "@azure-rest/ai-document-intelligence";

const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-layout")
  .post({
    contentType: "application/json",
    body: {
      urlSource: "https://example.com/document.pdf"
    },
    queryParameters: { locale: "en-US" }
  });

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const result = (await poller.pollUntilDone()).body as AnalyzeOperationOutput;

console.log("Pages:", result.analyzeResult?.pages?.length);
console.log("Tables:", result.analyzeResult?.tables?.length);
```

## 分析文件（本機檔案）

```typescript
import { readFile } from "node:fs/promises";

const fileBuffer = await readFile("./document.pdf");
const base64Source = fileBuffer.toString("base64");

const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-invoice")
  .post({
    contentType: "application/json",
    body: { base64Source }
  });

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const result = (await poller.pollUntilDone()).body as AnalyzeOperationOutput;
```

## 預建模型

| Model ID | 說明 |
|----------|-------------|
| `prebuilt-read` | OCR：擷取文字和語言 |
| `prebuilt-layout` | 文字、表格、勾選標記、結構 |
| `prebuilt-invoice` | 發票欄位 |
| `prebuilt-receipt` | 收據欄位 |
| `prebuilt-idDocument` | 身分文件欄位 |
| `prebuilt-tax.us.w2` | W-2 稅務表單欄位 |
| `prebuilt-healthInsuranceCard.us` | 健康保險卡欄位 |
| `prebuilt-contract` | 合約欄位 |
| `prebuilt-bankStatement.us` | 銀行對帳單欄位 |

## 擷取發票欄位

```typescript
const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-invoice")
  .post({
    contentType: "application/json",
    body: { urlSource: invoiceUrl }
  });

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const result = (await poller.pollUntilDone()).body as AnalyzeOperationOutput;

const invoice = result.analyzeResult?.documents?.[0];
if (invoice) {
  console.log("Vendor:", invoice.fields?.VendorName?.content);
  console.log("Total:", invoice.fields?.InvoiceTotal?.content);
  console.log("Due Date:", invoice.fields?.DueDate?.content);
}
```

## 擷取收據欄位

```typescript
const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-receipt")
  .post({
    contentType: "application/json",
    body: { urlSource: receiptUrl }
  });

const poller = getLongRunningPoller(client, initialResponse);
const result = (await poller.pollUntilDone()).body as AnalyzeOperationOutput;

const receipt = result.analyzeResult?.documents?.[0];
if (receipt) {
  console.log("Merchant:", receipt.fields?.MerchantName?.content);
  console.log("Total:", receipt.fields?.Total?.content);
  
  for (const item of receipt.fields?.Items?.values || []) {
    console.log("Item:", item.properties?.Description?.content);
    console.log("Price:", item.properties?.TotalPrice?.content);
  }
}
```

## 列出文件模型

```typescript
import DocumentIntelligence, { isUnexpected, paginate } from "@azure-rest/ai-document-intelligence";

const response = await client.path("/documentModels").get();

if (isUnexpected(response)) {
  throw response.body.error;
}

for await (const model of paginate(client, response)) {
  console.log(model.modelId);
}
```

## 建立自訂模型

```typescript
const initialResponse = await client.path("/documentModels:build").post({
  body: {
    modelId: "my-custom-model",
    description: "Custom model for purchase orders",
    buildMode: "template",  // 或 "neural"
    azureBlobSource: {
      containerUrl: process.env.TRAINING_CONTAINER_SAS_URL!,
      prefix: "training-data/"
    }
  }
});

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const result = await poller.pollUntilDone();
console.log("Model built:", result.body);
```

## 建立文件分類器

```typescript
import { DocumentClassifierBuildOperationDetailsOutput } from "@azure-rest/ai-document-intelligence";

const containerSasUrl = process.env.TRAINING_CONTAINER_SAS_URL!;

const initialResponse = await client.path("/documentClassifiers:build").post({
  body: {
    classifierId: "my-classifier",
    description: "Invoice vs Receipt classifier",
    docTypes: {
      invoices: {
        azureBlobSource: { containerUrl: containerSasUrl, prefix: "invoices/" }
      },
      receipts: {
        azureBlobSource: { containerUrl: containerSasUrl, prefix: "receipts/" }
      }
    }
  }
});

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const result = (await poller.pollUntilDone()).body as DocumentClassifierBuildOperationDetailsOutput;
console.log("Classifier:", result.result?.classifierId);
```

## 分類文件

```typescript
const initialResponse = await client
  .path("/documentClassifiers/{classifierId}:analyze", "my-classifier")
  .post({
    contentType: "application/json",
    body: { urlSource: documentUrl },
    queryParameters: { split: "auto" }
  });

if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

const poller = getLongRunningPoller(client, initialResponse);
const result = await poller.pollUntilDone();
console.log("Classification:", result.body.analyzeResult?.documents);
```

## 取得服務資訊

```typescript
const response = await client.path("/info").get();

if (isUnexpected(response)) {
  throw response.body.error;
}

console.log("Custom model limit:", response.body.customDocumentModels.limit);
console.log("Custom model count:", response.body.customDocumentModels.count);
```

## 輪詢模式

```typescript
import DocumentIntelligence, {
  isUnexpected,
  getLongRunningPoller,
  AnalyzeOperationOutput
} from "@azure-rest/ai-document-intelligence";

// 1. 啟動操作
const initialResponse = await client
  .path("/documentModels/{modelId}:analyze", "prebuilt-layout")
  .post({ contentType: "application/json", body: { urlSource } });

// 2. 檢查錯誤
if (isUnexpected(initialResponse)) {
  throw initialResponse.body.error;
}

// 3. 建立 poller
const poller = getLongRunningPoller(client, initialResponse);

// 4. 選用：監看進度
poller.onProgress((state) => {
  console.log("Status:", state.status);
});

// 5. 等待完成
const result = (await poller.pollUntilDone()).body as AnalyzeOperationOutput;
```

## 主要型別

```typescript
import DocumentIntelligence, {
  isUnexpected,
  getLongRunningPoller,
  paginate,
  parseResultIdFromResponse,
  AnalyzeOperationOutput,
  DocumentClassifierBuildOperationDetailsOutput
} from "@azure-rest/ai-document-intelligence";
```

## 最佳實務

1. **使用 getLongRunningPoller()**：文件分析是非同步的，一定要輪詢結果
2. **檢查 isUnexpected()**：正確處理錯誤用的 type guard
3. **選對模型**：盡量用預建模型，特殊文件才用自訂的
4. **處理信心分數**：欄位都有信心值，依使用情境設定門檻
5. **使用分頁**：列出模型時用 `paginate()` 輔助函式
6. **優先用 neural 模式**：自訂模型時，neural 比 template 更能處理版面變化
