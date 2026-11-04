---
name: azure-ai
description: "用於 Azure AI：Search、Speech、OpenAI、Document Intelligence。協助處理搜尋、向量／混合搜尋、語音轉文字、文字轉語音、轉錄、OCR。WHEN: AI Search, query search, vector search, hybrid search, semantic search, speech-to-text, text-to-speech, transcribe, OCR, convert text to speech。"
license: MIT
metadata:
  author: Microsoft
  version: "1.2.2"
---

# Azure AI 服務

## 服務

| 服務 | 使用時機 | MCP 工具 | CLI |
|---------|----------|-----------|-----|
| AI Search | 全文、向量、混合搜尋 | `azure__search` | `az search` |
| Speech | 語音轉文字、文字轉語音 | `azure__speech` | - |
| OpenAI | GPT 模型、embedding、DALL-E | - | `az cognitiveservices` |
| Document Intelligence | 表單擷取、OCR | - | - |

## MCP Server（優先）

啟用 Azure MCP 時：

### AI Search
- `azure__search` 搭配指令 `search_index_list`：列出 search index
- `azure__search` 搭配指令 `search_index_get`：取得 index 詳細資訊
- `azure__search` 搭配指令 `search_query`：查詢 search index

### Speech
- `azure__speech` 搭配指令 `speech_transcribe`：語音轉文字
- `azure__speech` 搭配指令 `speech_synthesize`：文字轉語音

**如果沒有啟用 Azure MCP：** 在 Copilot CLI 或 Claude Code 裡，請使用者執行 `/mcp` 並啟用 Azure MCP；在其他 host，請使用者透過該 host 的 MCP 設定啟用 Azure MCP。

## AI Search 能力

| 功能 | 說明 |
|---------|-------------|
| 全文搜尋 | 語言分析、詞幹還原 |
| 向量搜尋 | 用 embedding 做語意相似度 |
| 混合搜尋 | 關鍵字 + 向量並用 |
| AI 增強 | 實體擷取、OCR、情緒分析 |

## Speech 能力

| 功能 | 說明 |
|---------|-------------|
| 語音轉文字 | 即時和批次轉錄 |
| 文字轉語音 | 神經網路語音、支援 SSML |
| 說話者分離 | 辨識誰在什麼時候說話 |
| 自訂模型 | 特定領域的詞彙 |

## SDK 速查

要用程式存取這些服務，請看精簡版的 SDK 指南：

- **AI Search**：[Python](references/sdk/azure-search-documents-py.md) | [TypeScript](references/sdk/azure-search-documents-ts.md) | [.NET](references/sdk/azure-search-documents-dotnet.md)
- **OpenAI**：[.NET](references/sdk/azure-ai-openai-dotnet.md)
- **Vision**：[Python](references/sdk/azure-ai-vision-imageanalysis-py.md) | [Java](references/sdk/azure-ai-vision-imageanalysis-java.md)
- **Transcription**：[Python](references/sdk/azure-ai-transcription-py.md)
- **Translation**：[Python](references/sdk/azure-ai-translation-text-py.md) | [TypeScript](references/sdk/azure-ai-translation-ts.md)
- **Document Intelligence**：[.NET](references/sdk/azure-ai-document-intelligence-dotnet.md) | [TypeScript](references/sdk/azure-ai-document-intelligence-ts.md)
- **Content Safety**：[Python](references/sdk/azure-ai-contentsafety-py.md) | [TypeScript](references/sdk/azure-ai-contentsafety-ts.md) | [Java](references/sdk/azure-ai-contentsafety-java.md)

## 服務詳細資料

要看特定服務的深入文件：

- AI Search 的索引和查詢 -> [Azure AI Search documentation](https://learn.microsoft.com/azure/search/search-what-is-azure-search)
- Speech 轉錄的模式 -> [Azure AI Speech documentation](https://learn.microsoft.com/azure/ai-services/speech-service/overview)
