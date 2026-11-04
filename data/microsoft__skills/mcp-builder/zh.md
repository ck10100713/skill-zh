---
name: mcp-builder
description: 建立高品質 MCP（Model Context Protocol）server 的指南，讓 LLM 能透過設計良好的工具和外部服務互動。要建 MCP server 來整合外部 API 或服務時使用，不論是 Python（FastMCP）、Node/TypeScript（MCP SDK）還是 C#/.NET（Microsoft MCP SDK）。
---

# MCP Server Development Guide

## Overview

建立 MCP（Model Context Protocol）server，讓 LLM 能透過設計良好的工具和外部服務互動。MCP server 的品質，看的是它能多有效地幫 LLM 完成真實世界的任務。

---

## Microsoft MCP Ecosystem

Microsoft 為 Azure 和 Foundry 服務提供了大量的 MCP 基礎設施。了解這個生態系，能幫你決定要自己建 server，還是用現成的。

### Server Types

| Type | Transport | Use Case | Example |
|------|-----------|----------|---------|
| **Local** | stdio | 桌面 app、單一使用者、本機開發 | 透過 NPM/Docker 執行的 Azure MCP Server |
| **Remote** | Streamable HTTP | 雲端服務、多租戶、Agent Service | `https://mcp.ai.azure.com` (Foundry) |

### Microsoft MCP Servers

自己建 server 之前，先檢查 Microsoft 有沒有已經提供：

| Server | Type | Description |
|--------|------|-------------|
| **Azure MCP** | Local | 48 個以上的 Azure 服務（Storage、KeyVault、Cosmos、SQL 等） |
| **Foundry MCP** | Remote | `https://mcp.ai.azure.com` - 模型、部署、eval、agent |
| **Fabric MCP** | Local | Microsoft Fabric API、OneLake、item 定義 |
| **Playwright MCP** | Local | 瀏覽器自動化與測試 |
| **GitHub MCP** | Remote | `https://api.githubcopilot.com/mcp` |

**完整生態系：** 完整的 server 目錄和模式見 [🔷 Microsoft MCP Patterns](./reference/microsoft_mcp_patterns.md)。

### When to Use Microsoft vs Custom

| Scenario | Recommendation |
|----------|----------------|
| 整合 Azure 服務 | 用 **Azure MCP Server**（涵蓋 48 個服務） |
| AI Foundry 的 agent/eval | 用 **Foundry MCP** remote server |
| 自訂的內部 API | 建**自訂 server**（本指南） |
| 整合第三方 SaaS | 建**自訂 server**（本指南） |
| 擴充 Azure MCP | 照 [Microsoft MCP Patterns](./reference/microsoft_mcp_patterns.md) 做

---

# Process

## 🚀 High-Level Workflow

建立高品質的 MCP server 有四個主要階段：

### Phase 1: Deep Research and Planning

#### 1.1 Understand Modern MCP Design

**API 涵蓋範圍 vs. workflow 工具：**
要在完整涵蓋 API endpoint 和專門的 workflow 工具之間取得平衡。Workflow 工具對特定任務比較方便，完整涵蓋則讓 agent 能彈性組合操作。效果因 client 而異：有些 client 受益於用程式碼執行去組合基本工具，有些則搭配較高階的 workflow 比較好。不確定時，優先選完整涵蓋 API。

**工具命名與可發現性：**
清楚、有描述性的工具名稱，能幫 agent 快速找到對的工具。用一致的前綴（例如 `github_create_issue`、`github_list_repos`），並採用以動作為導向的命名。

**Context 管理：**
簡潔的工具描述，加上過濾/分頁結果的能力，對 agent 很有幫助。設計出回傳聚焦、相關資料的工具。有些 client 支援程式碼執行，能幫 agent 有效率地過濾和處理資料。

**可行動的錯誤訊息：**
錯誤訊息要用具體的建議和後續步驟，引導 agent 走向解法。

#### 1.2 Study MCP Protocol Documentation

**瀏覽 MCP 規格：**

從 sitemap 開始找相關頁面：`https://modelcontextprotocol.io/sitemap.xml`

然後在特定頁面加上 `.md` 後綴，取得 markdown 格式（例如 `https://modelcontextprotocol.io/specification/draft.md`）。

要看的重點頁面：
- 規格概覽與架構
- 傳輸機制（streamable HTTP、stdio）
- Tool、resource 和 prompt 的定義

#### 1.3 Study Framework Documentation

**語言選擇：**

| Language | Best For | SDK |
|----------|----------|-----|
| **TypeScript**（建議） | 一般的 MCP server、相容性廣 | `@modelcontextprotocol/sdk` |
| **Python** | 資料/ML pipeline、整合 FastAPI | `mcp` (FastMCP) |
| **C#/.NET** | Azure/Microsoft 生態系、企業環境 | `Microsoft.Mcp.Core` |

**傳輸方式選擇：**

| Transport | Use Case | Characteristics |
|-----------|----------|-----------------|
| **Streamable HTTP** | Remote server、多租戶、Agent Service | Stateless、可擴展、需要驗證 |
| **stdio** | Local server、桌面 app | 簡單、單一使用者、不用網路 |

**載入框架文件：**

- **MCP Best Practices**：[📋 View Best Practices](./reference/mcp_best_practices.md) - 核心指引

**TypeScript（建議）：**
- **TypeScript SDK**：用 WebFetch 載入 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
- [⚡ TypeScript Guide](./reference/node_mcp_server.md) - TypeScript 的模式與範例

**Python：**
- **Python SDK**：用 WebFetch 載入 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Python Guide](./reference/python_mcp_server.md) - Python 的模式與範例

**C#/.NET（Microsoft 生態系）：**
- [🔷 Microsoft MCP Patterns](./reference/microsoft_mcp_patterns.md) - C# 模式、Azure MCP 架構、指令階層

#### 1.4 Plan Your Implementation

**了解 API：**
檢視該服務的 API 文件，找出關鍵的 endpoint、驗證需求和資料模型。需要時用網路搜尋和 WebFetch。

**工具選擇：**
優先完整涵蓋 API。列出要實作的 endpoint，從最常見的操作開始。

---

### Phase 2: Implementation

#### 2.1 Set Up Project Structure

專案設定見各語言的指南：
- [⚡ TypeScript Guide](./reference/node_mcp_server.md) - 專案結構、package.json、tsconfig.json
- [🐍 Python Guide](./reference/python_mcp_server.md) - 模組組織、相依套件
- [🔷 Microsoft MCP Patterns](./reference/microsoft_mcp_patterns.md) - C# 專案結構、指令階層

#### 2.2 Implement Core Infrastructure

建立共用的工具：
- 帶驗證的 API client
- 錯誤處理 helper
- 回應格式化（JSON/Markdown）
- 分頁支援

#### 2.3 Implement Tools

每個工具都要有：

**Input Schema：**
- 用 Zod（TypeScript）或 Pydantic（Python）
- 包含限制條件和清楚的描述
- 在欄位描述裡加上範例

**Output Schema：**
- 有結構化資料時，盡可能定義 `outputSchema`
- 在工具回應中使用 `structuredContent`（TypeScript SDK 的功能）
- 幫助 client 理解並處理工具輸出

**Tool Description：**
- 功能的簡潔摘要
- 參數描述
- 回傳型別 schema

**Implementation：**
- I/O 操作用 async/await
- 用可行動的訊息做好錯誤處理
- 適用的地方支援分頁
- 用現代 SDK 時，同時回傳文字內容和結構化資料

**Annotations：**
- `readOnlyHint`: true/false
- `destructiveHint`: true/false
- `idempotentHint`: true/false
- `openWorldHint`: true/false

---

### Phase 3: Review and Test

#### 3.1 Code Quality

檢查：
- 沒有重複的程式碼（DRY 原則）
- 一致的錯誤處理
- 完整的型別覆蓋
- 清楚的工具描述

#### 3.2 Build and Test

**TypeScript：**
- 執行 `npm run build` 驗證編譯
- 用 MCP Inspector 測試：`npx @modelcontextprotocol/inspector`

**Python：**
- 驗證語法：`python -m py_compile your_server.py`
- 用 MCP Inspector 測試

詳細的測試方法和品質檢查清單見各語言的指南。

---

### Phase 4: Create Evaluations

實作完 MCP server 之後，建立完整的 evaluation 來測試它的成效。

**載入 [✅ Evaluation Guide](./reference/evaluation.md) 取得完整的 evaluation 指引。**

#### 4.1 Understand Evaluation Purpose

用 evaluation 測試 LLM 能不能有效地使用你的 MCP server，回答真實又複雜的問題。

#### 4.2 Create 10 Evaluation Questions

要建立有效的 evaluation，照 evaluation 指南裡的流程：

1. **Tool Inspection**：列出可用的工具，了解它們的能力
2. **Content Exploration**：用唯讀操作探索可用的資料
3. **Question Generation**：建立 10 個複雜又真實的問題
4. **Answer Verification**：自己解每個問題，驗證答案

#### 4.3 Evaluation Requirements

確保每個問題都是：
- **Independent**：不依賴其他問題
- **Read-only**：只需要非破壞性的操作
- **Complex**：需要多次工具呼叫和深入探索
- **Realistic**：以人真的會在意的使用情境為基礎
- **Verifiable**：只有單一、明確的答案，可以用字串比對來驗證
- **Stable**：答案不會隨時間改變

#### 4.4 Output Format

建立一個有這種結構的 XML 檔案：

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
<!-- More qa_pairs... -->
</evaluation>
```

---

# Reference Files

## 📚 Documentation Library

開發過程中依需要載入這些資源：

### Core MCP Documentation (Load First)
- **MCP Protocol**：從 `https://modelcontextprotocol.io/sitemap.xml` 的 sitemap 開始，再用 `.md` 後綴取得特定頁面
- [📋 MCP Best Practices](./reference/mcp_best_practices.md) - 通用的 MCP 指引，包括：
  - Server 和工具的命名慣例
  - 回應格式指引（JSON vs Markdown）
  - 分頁最佳實務
  - 傳輸方式選擇（streamable HTTP vs stdio）
  - 安全與錯誤處理標準

### Microsoft MCP Documentation (For Azure/Foundry)
- [🔷 Microsoft MCP Patterns](./reference/microsoft_mcp_patterns.md) - Microsoft 專屬的模式，包括：
  - Azure MCP Server 架構（48 個以上的 Azure 服務）
  - C#/.NET 指令實作模式
  - 搭配 Foundry Agent Service 的 Remote MCP
  - 驗證（Entra ID、OBO flow、Managed Identity）
  - 用 Bicep 範本建立的測試基礎設施

### SDK Documentation (Load During Phase 1/2)
- **Python SDK**：從 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` 取得
- **TypeScript SDK**：從 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` 取得
- **Microsoft MCP SDK**：C#/.NET 見 [Microsoft MCP Patterns](./reference/microsoft_mcp_patterns.md)

### Language-Specific Implementation Guides (Load During Phase 2)
- [🐍 Python Implementation Guide](./reference/python_mcp_server.md) - 完整的 Python/FastMCP 指南，包括：
  - Server 初始化模式
  - Pydantic model 範例
  - 用 `@mcp.tool` 註冊工具
  - 完整可運作的範例
  - 品質檢查清單

- [⚡ TypeScript Implementation Guide](./reference/node_mcp_server.md) - 完整的 TypeScript 指南，包括：
  - 專案結構
  - Zod schema 模式
  - 用 `server.registerTool` 註冊工具
  - 完整可運作的範例
  - 品質檢查清單

- [🔷 Microsoft MCP Patterns](./reference/microsoft_mcp_patterns.md) - 完整的 C#/.NET 指南，包括：
  - 指令階層（BaseCommand → GlobalCommand → SubscriptionCommand）
  - 命名慣例（`{Resource}{Operation}Command`）
  - 用 `.AsRequired()` / `.AsOptional()` 處理選項
  - Azure Functions 的 remote MCP 部署
  - 用 Bicep 做的 live 測試模式

### Evaluation Guide (Load During Phase 4)
- [✅ Evaluation Guide](./reference/evaluation.md) - 完整的 evaluation 建立指南，包括：
  - 問題建立指引
  - 答案驗證策略
  - XML 格式規格
  - 範例問題與答案
  - 用提供的 script 執行 evaluation
