---
name: azure-ai-translation-ts
description: 用 JavaScript 版的 Azure Translation SDK（@azure-rest/ai-translation-text、@azure-rest/ai-translation-document）建構翻譯應用程式。適用於實作文字翻譯、音譯、語言偵測或批次文件翻譯。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure-rest/ai-translation-text, @azure-rest/ai-translation-document'
---

# Azure Translation SDKs for TypeScript

用 REST 風格的 client 做文字與文件翻譯。

## Installation

```bash
# 文字翻譯
npm install @azure-rest/ai-translation-text @azure/identity

# 文件翻譯
npm install @azure-rest/ai-translation-document @azure/identity
```

## Environment Variables

```bash
TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
TRANSLATOR_SUBSCRIPTION_KEY=<your-api-key>
TRANSLATOR_REGION=<your-region>  # 例如 westus、eastus
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Text Translation Client

### Authentication

```typescript
import TextTranslationClient, { TranslatorCredential } from "@azure-rest/ai-translation-text";

// API Key + Region
const credential: TranslatorCredential = {
  key: process.env.TRANSLATOR_SUBSCRIPTION_KEY!,
  region: process.env.TRANSLATOR_REGION!,
};
const client = TextTranslationClient(process.env.TRANSLATOR_ENDPOINT!, credential);

// 或只傳 credential（使用全域 endpoint）
const client2 = TextTranslationClient(credential);
```

### Translate Text

```typescript
import TextTranslationClient, { isUnexpected } from "@azure-rest/ai-translation-text";

const response = await client.path("/translate").post({
  body: {
    inputs: [
      {
        text: "Hello, how are you?",
        language: "en",  // 來源語言（選填，不填會自動偵測）
        targets: [
          { language: "es" },
          { language: "fr" },
        ],
      },
    ],
  },
});

if (isUnexpected(response)) {
  throw response.body.error;
}

for (const result of response.body.value) {
  for (const translation of result.translations) {
    console.log(`${translation.language}: ${translation.text}`);
  }
}
```

### Translate with Options

```typescript
const response = await client.path("/translate").post({
  body: {
    inputs: [
      {
        text: "Hello world",
        language: "en",
        textType: "Plain",  // 或 "Html"
        targets: [
          {
            language: "de",
            profanityAction: "NoAction",  // "Marked" | "Deleted"
            tone: "formal",  // LLM 專用
          },
        ],
      },
    ],
  },
});
```

### Get Supported Languages

```typescript
const response = await client.path("/languages").get();

if (isUnexpected(response)) {
  throw response.body.error;
}

// 翻譯語言
for (const [code, lang] of Object.entries(response.body.translation || {})) {
  console.log(`${code}: ${lang.name} (${lang.nativeName})`);
}
```

### Transliterate

```typescript
const response = await client.path("/transliterate").post({
  body: { inputs: [{ text: "这是个测试" }] },
  queryParameters: {
    language: "zh-Hans",
    fromScript: "Hans",
    toScript: "Latn",
  },
});

if (!isUnexpected(response)) {
  for (const t of response.body.value) {
    console.log(`${t.script}: ${t.text}`);  // Latn: zhè shì gè cè shì
  }
}
```

### Detect Language

```typescript
const response = await client.path("/detect").post({
  body: { inputs: [{ text: "Bonjour le monde" }] },
});

if (!isUnexpected(response)) {
  for (const result of response.body.value) {
    console.log(`Language: ${result.language}, Score: ${result.score}`);
  }
}
```

## Document Translation Client

### Authentication

```typescript
import DocumentTranslationClient from "@azure-rest/ai-translation-document";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

const endpoint = "https://<translator>.cognitiveservices.azure.com";

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在 production 直接用指定的 credential：
// 參考 https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

// TokenCredential
const client = DocumentTranslationClient(endpoint, credential);

// API Key
const client2 = DocumentTranslationClient(endpoint, { key: "<api-key>" });
```

### Single Document Translation

```typescript
import DocumentTranslationClient from "@azure-rest/ai-translation-document";
import { writeFile } from "node:fs/promises";

const response = await client.path("/document:translate").post({
  queryParameters: {
    targetLanguage: "es",
    sourceLanguage: "en",  // 選填
  },
  contentType: "multipart/form-data",
  body: [
    {
      name: "document",
      body: "Hello, this is a test document.",
      filename: "test.txt",
      contentType: "text/plain",
    },
  ],
}).asNodeStream();

if (response.status === "200") {
  await writeFile("translated.txt", response.body);
}
```

### Batch Document Translation

```typescript
import { ContainerSASPermissions, BlobServiceClient } from "@azure/storage-blob";

// 為來源和目標 container 產生 SAS URL
const sourceSas = await sourceContainer.generateSasUrl({
  permissions: ContainerSASPermissions.parse("rl"),
  expiresOn: new Date(Date.now() + 24 * 60 * 60 * 1000),
});

const targetSas = await targetContainer.generateSasUrl({
  permissions: ContainerSASPermissions.parse("rwl"),
  expiresOn: new Date(Date.now() + 24 * 60 * 60 * 1000),
});

// 啟動批次翻譯
const response = await client.path("/document/batches").post({
  body: {
    inputs: [
      {
        source: { sourceUrl: sourceSas },
        targets: [
          { targetUrl: targetSas, language: "fr" },
        ],
      },
    ],
  },
});

// 從 header 取得 operation ID
const operationId = new URL(response.headers["operation-location"])
  .pathname.split("/").pop();
```

### Get Translation Status

```typescript
import { isUnexpected, paginate } from "@azure-rest/ai-translation-document";

const statusResponse = await client.path("/document/batches/{id}", operationId).get();

if (!isUnexpected(statusResponse)) {
  const status = statusResponse.body;
  console.log(`Status: ${status.status}`);
  console.log(`Total: ${status.summary.total}`);
  console.log(`Success: ${status.summary.success}`);
}

// 分頁列出文件
const docsResponse = await client.path("/document/batches/{id}/documents", operationId).get();
const documents = paginate(client, docsResponse);

for await (const doc of documents) {
  console.log(`${doc.id}: ${doc.status}`);
}
```

### Get Supported Formats

```typescript
const response = await client.path("/document/formats").get();

if (!isUnexpected(response)) {
  for (const format of response.body.value) {
    console.log(`${format.format}: ${format.fileExtensions.join(", ")}`);
  }
}
```

## Key Types

```typescript
// 文字翻譯
import type {
  TranslatorCredential,
  TranslatorTokenCredential,
} from "@azure-rest/ai-translation-text";

// 文件翻譯
import type {
  DocumentTranslateParameters,
  StartTranslationDetails,
  TranslationStatus,
} from "@azure-rest/ai-translation-document";
```

## Best Practices

1. **自動偵測來源語言**：省略 `language` 參數就會自動偵測
2. **批次請求**：一次呼叫翻譯多段文字比較有效率
3. **使用 SAS token**：文件翻譯請用有時效的 SAS URL
4. **處理錯誤**：存取 body 之前一定要先檢查 `isUnexpected(response)`
5. **區域 endpoint**：用區域 endpoint 可以降低延遲
