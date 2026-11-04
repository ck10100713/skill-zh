---
name: azure-ai-contentsafety-ts
description: 用 Azure AI Content Safety（@azure-rest/ai-content-safety）分析文字和圖片中的有害內容。在審核使用者產生的內容、偵測仇恨言論、暴力、性內容或自傷，或管理自訂 blocklist 時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure-rest/ai-content-safety'
---

# Azure AI Content Safety REST SDK（TypeScript）

分析文字和圖片中的有害內容，並支援可自訂的 blocklist。

## 安裝

```bash
npm install @azure-rest/ai-content-safety @azure/identity @azure/core-auth
```

## 環境變數

```bash
CONTENT_SAFETY_ENDPOINT=https://<resource>.cognitiveservices.azure.com
CONTENT_SAFETY_KEY=<api-key>
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

**重要**：這是 REST client。`ContentSafetyClient` 是**函式**，不是 class。

### API Key

```typescript
import ContentSafetyClient from "@azure-rest/ai-content-safety";
import { AzureKeyCredential } from "@azure/core-auth";

const client = ContentSafetyClient(
  process.env.CONTENT_SAFETY_ENDPOINT!,
  new AzureKeyCredential(process.env.CONTENT_SAFETY_KEY!)
);
```

### DefaultAzureCredential

```typescript
import ContentSafetyClient from "@azure-rest/ai-content-safety";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const client = ContentSafetyClient(
  process.env.CONTENT_SAFETY_ENDPOINT!,
  credential
);
```

## 分析文字

```typescript
import ContentSafetyClient, { isUnexpected } from "@azure-rest/ai-content-safety";

const result = await client.path("/text:analyze").post({
  body: {
    text: "Text content to analyze",
    categories: ["Hate", "Sexual", "Violence", "SelfHarm"],
    outputType: "FourSeverityLevels"  // 或 "EightSeverityLevels"
  }
});

if (isUnexpected(result)) {
  throw result.body;
}

for (const analysis of result.body.categoriesAnalysis) {
  console.log(`${analysis.category}: severity ${analysis.severity}`);
}
```

## 分析圖片

### Base64 內容

```typescript
import { readFileSync } from "node:fs";

const imageBuffer = readFileSync("./image.png");
const base64Image = imageBuffer.toString("base64");

const result = await client.path("/image:analyze").post({
  body: {
    image: { content: base64Image }
  }
});

if (isUnexpected(result)) {
  throw result.body;
}

for (const analysis of result.body.categoriesAnalysis) {
  console.log(`${analysis.category}: severity ${analysis.severity}`);
}
```

### Blob URL

```typescript
const result = await client.path("/image:analyze").post({
  body: {
    image: { blobUrl: "https://storage.blob.core.windows.net/container/image.png" }
  }
});
```

## Blocklist 管理

### 建立 Blocklist

```typescript
const result = await client
  .path("/text/blocklists/{blocklistName}", "my-blocklist")
  .patch({
    contentType: "application/merge-patch+json",
    body: {
      description: "Custom blocklist for prohibited terms"
    }
  });

if (isUnexpected(result)) {
  throw result.body;
}

console.log(`Created: ${result.body.blocklistName}`);
```

### 新增項目到 Blocklist

```typescript
const result = await client
  .path("/text/blocklists/{blocklistName}:addOrUpdateBlocklistItems", "my-blocklist")
  .post({
    body: {
      blocklistItems: [
        { text: "prohibited-term-1", description: "First blocked term" },
        { text: "prohibited-term-2", description: "Second blocked term" }
      ]
    }
  });

if (isUnexpected(result)) {
  throw result.body;
}

for (const item of result.body.blocklistItems ?? []) {
  console.log(`Added: ${item.blocklistItemId}`);
}
```

### 搭配 Blocklist 分析

```typescript
const result = await client.path("/text:analyze").post({
  body: {
    text: "Text that might contain blocked terms",
    blocklistNames: ["my-blocklist"],
    haltOnBlocklistHit: false
  }
});

if (isUnexpected(result)) {
  throw result.body;
}

// 檢查 blocklist 命中
if (result.body.blocklistsMatch) {
  for (const match of result.body.blocklistsMatch) {
    console.log(`Blocked: "${match.blocklistItemText}" from ${match.blocklistName}`);
  }
}
```

### 列出 Blocklist

```typescript
const result = await client.path("/text/blocklists").get();

if (isUnexpected(result)) {
  throw result.body;
}

for (const blocklist of result.body.value ?? []) {
  console.log(`${blocklist.blocklistName}: ${blocklist.description}`);
}
```

### 刪除 Blocklist

```typescript
await client.path("/text/blocklists/{blocklistName}", "my-blocklist").delete();
```

## 有害內容類別

| 類別 | API 名稱 | 說明 |
|----------|----------|-------------|
| Hate and Fairness | `Hate` | 針對身分族群的歧視性語言 |
| Sexual | `Sexual` | 性內容、裸露、色情 |
| Violence | `Violence` | 肢體傷害、武器、恐怖主義 |
| Self-Harm | `SelfHarm` | 自傷、自殺、飲食失調 |

## 嚴重程度

| 級別 | 風險 | 建議動作 |
|-------|------|-------------------|
| 0 | Safe | 放行 |
| 2 | Low | 審查，或附警告後放行 |
| 4 | Medium | 封鎖，或要求人工審查 |
| 6 | High | 立即封鎖 |

**輸出類型**：
- `FourSeverityLevels`（預設）：回傳 0、2、4、6
- `EightSeverityLevels`：回傳 0-7

## 內容審核輔助函式

```typescript
import ContentSafetyClient, { 
  isUnexpected, 
  TextCategoriesAnalysisOutput 
} from "@azure-rest/ai-content-safety";

interface ModerationResult {
  isAllowed: boolean;
  flaggedCategories: string[];
  maxSeverity: number;
  blocklistMatches: string[];
}

async function moderateContent(
  client: ReturnType<typeof ContentSafetyClient>,
  text: string,
  maxAllowedSeverity = 2,
  blocklistNames: string[] = []
): Promise<ModerationResult> {
  const result = await client.path("/text:analyze").post({
    body: { text, blocklistNames, haltOnBlocklistHit: false }
  });

  if (isUnexpected(result)) {
    throw result.body;
  }

  const flaggedCategories = result.body.categoriesAnalysis
    .filter(c => (c.severity ?? 0) > maxAllowedSeverity)
    .map(c => c.category!);

  const maxSeverity = Math.max(
    ...result.body.categoriesAnalysis.map(c => c.severity ?? 0)
  );

  const blocklistMatches = (result.body.blocklistsMatch ?? [])
    .map(m => m.blocklistItemText!);

  return {
    isAllowed: flaggedCategories.length === 0 && blocklistMatches.length === 0,
    flaggedCategories,
    maxSeverity,
    blocklistMatches
  };
}
```

## API Endpoint

| 操作 | Method | 路徑 |
|-----------|--------|------|
| 分析文字 | POST | `/text:analyze` |
| 分析圖片 | POST | `/image:analyze` |
| 建立／更新 Blocklist | PATCH | `/text/blocklists/{blocklistName}` |
| 列出 Blocklist | GET | `/text/blocklists` |
| 刪除 Blocklist | DELETE | `/text/blocklists/{blocklistName}` |
| 新增 Blocklist 項目 | POST | `/text/blocklists/{blocklistName}:addOrUpdateBlocklistItems` |
| 列出 Blocklist 項目 | GET | `/text/blocklists/{blocklistName}/blocklistItems` |
| 移除 Blocklist 項目 | POST | `/text/blocklists/{blocklistName}:removeBlocklistItems` |

## 主要型別

```typescript
import ContentSafetyClient, {
  isUnexpected,
  AnalyzeTextParameters,
  AnalyzeImageParameters,
  TextCategoriesAnalysisOutput,
  ImageCategoriesAnalysisOutput,
  TextBlocklist,
  TextBlocklistItem
} from "@azure-rest/ai-content-safety";
```

## 最佳實務

1. **一律使用 isUnexpected()**：錯誤處理用的 type guard
2. **設定適當的門檻**：不同類別可能需要不同的嚴重程度門檻
3. **特定領域的詞彙用 blocklist**：用自訂規則補強 AI 偵測
4. **記錄審核決定**：留下稽核軌跡以符合法規
5. **處理邊界情況**：空白文字、超長文字、不支援的圖片格式
