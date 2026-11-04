---
name: microsoft-docs
description: 透過查詢官方文件來理解 Microsoft 技術。只要使用者問某個東西怎麼運作、想要教學、需要設定選項、限制、配額或最佳實務（任何 Microsoft 技術，包括 Azure、.NET、M365、Windows、Power Platform 等），就用這個 skill，就算他們沒提到「文件」也一樣。如果問題是在理解某個概念而不是寫程式，這就是對的 skill。
context: fork
compatibility: 主要使用 Microsoft Learn MCP Server (https://learn.microsoft.com/api/mcp)；如果無法使用，就退回 mslearn CLI（`npx @microsoft/learn-cli`）。
---

# Microsoft Docs

## 工具

| 工具 | 用途 |
|------|------|
| `microsoft_docs_search` | 找文件，包括概念、指南、教學、設定 |
| `microsoft_docs_fetch` | 取得完整頁面內容（搜尋摘錄不夠用時） |

## 什麼時候用

- **理解概念**：「Cosmos DB 的 partitioning 是怎麼運作的？」
- **認識某個服務**：「Azure Functions 概觀」、「Container Apps 架構」
- **找教學**：「quickstart」、「getting started」、「step-by-step」
- **設定選項**：「App Service 設定值」
- **限制與配額**：「Azure OpenAI rate limits」、「Service Bus quotas」
- **最佳實務**：「Azure 安全性最佳實務」

## 查詢要怎麼寫才有效

好的查詢要具體：

```
# ❌ 太籠統
"Azure Functions"

# ✅ 具體
"Azure Functions Python v2 programming model"
"Cosmos DB partition key design best practices"
"Container Apps scaling rules KEDA"
```

加上背景資訊：
- 相關的話加上**版本**（`.NET 8`、`EF Core 8`）
- **任務意圖**（`quickstart`、`tutorial`、`overview`、`limits`）
- 多平台文件要加上**平台**（`Linux`、`Windows`）

## 什麼時候要抓完整頁面

搜尋之後在這些情況再 fetch：
- **教學**：需要完整的逐步說明
- **設定指南**：需要列出所有選項
- **深入探討**：使用者想要完整涵蓋
- **搜尋摘錄被截斷**：需要完整脈絡

## 為什麼要用這個

- **準確**：是即時的文件，不是可能已經過時的訓練資料
- **完整**：教學有全部步驟，不是片段
- **權威**：是 Microsoft 官方文件

## CLI 替代方案

如果 Learn MCP server 無法使用，就改在命令列用 `mslearn` CLI：

```sh
# Run directly (no install needed)
npx @microsoft/learn-cli search "azure functions timeout"

# Or install globally, then run
npm install -g @microsoft/learn-cli
mslearn search "azure functions timeout"
```

| MCP 工具 | CLI 指令 |
|----------|-------------|
| `microsoft_docs_search(query: "...")` | `mslearn search "..."` |
| `microsoft_docs_fetch(url: "...")` | `mslearn fetch "..."` |

`fetch` 指令也支援 `--section <heading>` 來只擷取單一段落，以及 `--max-chars <number>` 來截斷輸出。
