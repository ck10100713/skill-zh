---
name: mcp-builder
description: 建立高品質 MCP（Model Context Protocol）server 的指南，讓 LLM 能透過設計良好的工具與外部服務互動。在建置 MCP server 來整合外部 API 或服務時使用，不論是用 Python（FastMCP）還是 Node/TypeScript（MCP SDK）。
license: Complete terms in LICENSE.txt
---

# MCP Server 開發指南

## 概述

建立 MCP（Model Context Protocol）server，讓 LLM 能透過設計良好的工具與外部服務互動。MCP server 的品質，要看它能不能讓 LLM 完成真實世界的任務。

---

# 流程

## 🚀 高階工作流程

建立高品質的 MCP server 包含四個主要階段：

### 階段 1：深入研究與規劃

#### 1.1 了解現代 MCP 設計

**API 涵蓋範圍 vs. 工作流程工具：**
在完整涵蓋 API endpoint 和專門的工作流程工具之間取得平衡。工作流程工具對特定任務比較方便，而完整的涵蓋範圍讓 agent 能彈性組合操作。表現會因 client 而異：有些 client 受益於把基本工具組合起來的程式碼執行，有些則搭配更高階的工作流程效果更好。不確定的時候，優先選完整的 API 涵蓋範圍。

**工具命名與可發現性：**
清楚、有描述性的工具名稱能幫 agent 快速找到對的工具。使用一致的前綴（例如 `github_create_issue`、`github_list_repos`），並用以動作為導向的命名。

**Context 管理：**
簡潔的工具描述，加上能過濾／分頁結果的能力，對 agent 有幫助。設計出回傳資料聚焦、相關的工具。有些 client 支援程式碼執行，可以幫 agent 有效率地過濾和處理資料。

**可以直接照做的錯誤訊息：**
錯誤訊息應該用具體的建議和下一步，引導 agent 找到解法。

#### 1.2 研讀 MCP 協定文件

**瀏覽 MCP 規格：**

先從 sitemap 找相關頁面：`https://modelcontextprotocol.io/sitemap.xml`

然後抓特定頁面，加上 `.md` 後綴就能拿到 markdown 格式（例如 `https://modelcontextprotocol.io/specification/draft.md`）。

要看的重點頁面：
- 規格概述與架構
- 傳輸機制（streamable HTTP、stdio）
- 工具、resource 和 prompt 的定義

#### 1.3 研讀框架文件

**建議的技術組合：**
- **語言**：TypeScript（SDK 支援品質高，在許多執行環境，例如 MCPB，相容性也好。而且 AI 模型擅長產生 TypeScript 程式碼，受益於它廣泛的使用、靜態型別和好用的 linting 工具）
- **傳輸**：遠端 server 用 Streamable HTTP，並使用無狀態的 JSON（比起有狀態的 session 和串流回應，更容易擴展和維護）。本地 server 用 stdio。

**載入框架文件：**

- **MCP 最佳實務**：[📋 View Best Practices](./reference/mcp_best_practices.md) - 核心準則

**TypeScript（建議）：**

TypeScript SDK 有兩個主要版本。寫程式之前先選一個：
- **v2**（`@modelcontextprotocol/server`）：目前的穩定版。新的 server 用它。
- **v1**（`@modelcontextprotocol/sdk`）：只會收到 bug 和安全性修正。只有在專案的 `package.json` 已經依賴 `@modelcontextprotocol/sdk` 時才用它，或是用 `npx @modelcontextprotocol/codemod@latest v1-to-v2 .` 把那個專案遷移過去

如果專案已經在用 v1，要跟使用者說一次，用一兩句話就好：v2（`@modelcontextprotocol/server`）是目前的穩定版，v1 只會收到 bug 和安全性修正，而 `npx @modelcontextprotocol/codemod@latest v1-to-v2 .` 可以遷移專案。然後繼續用 v1，除非使用者要求遷移。

不要在同一個專案裡混用兩個版本：v1 的程式碼範例（從 `@modelcontextprotocol/sdk/...` import）不適用於 v2。

- **TypeScript SDK (v2)**：用 WebFetch 載入 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`；完整文件索引在 `https://ts.sdk.modelcontextprotocol.io/v2/llms.txt`
- [⚡ TypeScript Guide (v2)](./reference/node_mcp_server_v2.md) - TypeScript 的寫法與範例
- 只限 v1 專案：`https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/v1.x/README.md` 和 [TypeScript Guide (v1)](./reference/node_mcp_server.md)

**Python：**
- **Python SDK**：用 WebFetch 載入 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Python Guide](./reference/python_mcp_server.md) - Python 的寫法與範例

#### 1.4 規劃你的實作

**了解 API：**
檢視服務的 API 文件，找出關鍵的 endpoint、認證需求和資料模型。需要時使用網路搜尋和 WebFetch。

**工具選擇：**
優先選完整的 API 涵蓋範圍。列出要實作的 endpoint，從最常見的操作開始。

---

### 階段 2：實作

#### 2.1 建立專案結構

專案設定請見各語言的指南：
- [⚡ TypeScript Guide (v2)](./reference/node_mcp_server_v2.md) - 專案結構、package.json、tsconfig.json（既有的 v1 專案看 [v1](./reference/node_mcp_server.md)）
- [🐍 Python Guide](./reference/python_mcp_server.md) - 模組組織、相依套件

#### 2.2 實作核心基礎設施

建立共用的工具：
- 附認證的 API client
- 錯誤處理的 helper
- 回應格式化（JSON/Markdown）
- 分頁支援

#### 2.3 實作工具

每個工具都要有：

**輸入 Schema：**
- 使用 Zod（TypeScript）或 Pydantic（Python）
- 包含限制條件和清楚的描述
- 在欄位描述裡加範例

**輸出 Schema：**
- 結構化資料盡量定義 `outputSchema`
- 工具回應使用 `structuredContent`（TypeScript SDK 的功能）
- 幫助 client 理解和處理工具的輸出

**工具描述：**
- 功能的簡潔摘要
- 參數描述
- 回傳型別的 schema

**實作：**
- I/O 操作使用 async/await
- 適當的錯誤處理，訊息要能直接照著做
- 適用時支援分頁
- 使用現代 SDK 時，同時回傳文字內容和結構化資料

**Annotation：**
- `readOnlyHint`：true/false
- `destructiveHint`：true/false
- `idempotentHint`：true/false
- `openWorldHint`：true/false

---

### 階段 3：審查與測試

#### 3.1 程式碼品質

檢查：
- 沒有重複的程式碼（DRY 原則）
- 一致的錯誤處理
- 完整的型別涵蓋
- 清楚的工具描述

#### 3.2 建置與測試

**TypeScript：**
- 跑 `npm run build` 確認編譯通過
- v2 專案：對建置好的 server 執行 [v2 指南](./reference/node_mcp_server_v2.md#verify-your-server) 裡的自我檢查 script
- 用 MCP Inspector 測試：`npx @modelcontextprotocol/inspector`

**Python：**
- 驗證語法：`python -m py_compile your_server.py`
- 用 MCP Inspector 測試

詳細的測試方法和品質檢查清單，請見各語言的指南。

---

### 階段 4：建立評測

實作完 MCP server 之後，建立完整的評測來測試它的成效。

**載入 [✅ Evaluation Guide](./reference/evaluation.md) 取得完整的評測準則。**

#### 4.1 了解評測的目的

用評測來測試 LLM 能不能有效地使用你的 MCP server，回答真實又複雜的問題。

#### 4.2 建立 10 個評測問題

要建立有效的評測，照評測指南裡列的流程：

1. **檢視工具**：列出可用的工具，了解它們的能力
2. **探索內容**：用唯讀操作探索現有的資料
3. **產生問題**：建立 10 個複雜又貼近現實的問題
4. **驗證答案**：自己解每一題，驗證答案

#### 4.3 評測要求

確保每個問題都是：
- **獨立的**：不依賴其他問題
- **唯讀的**：只需要不具破壞性的操作
- **複雜的**：需要多次呼叫工具和深入探索
- **貼近現實的**：根據人們真正在意的真實使用情境
- **可驗證的**：只有單一、明確、可以用字串比對驗證的答案
- **穩定的**：答案不會隨時間改變

#### 4.4 輸出格式

建立一個 XML 檔，結構如下：

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

# 參考檔案

## 📚 文件庫

開發過程中依需要載入這些資源：

### 核心 MCP 文件（先載入）
- **MCP 協定**：從 `https://modelcontextprotocol.io/sitemap.xml` 的 sitemap 開始，然後抓加上 `.md` 後綴的特定頁面
- [📋 MCP Best Practices](./reference/mcp_best_practices.md) - 通用的 MCP 準則，包括：
  - Server 和工具的命名慣例
  - 回應格式準則（JSON vs Markdown）
  - 分頁的最佳實務
  - 傳輸方式的選擇（streamable HTTP vs stdio）
  - 安全性和錯誤處理的標準

### SDK 文件（階段 1/2 載入）
- **Python SDK**：從 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` 抓取
- **TypeScript SDK (v2)**：從 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` 抓取；完整文件索引在 `https://ts.sdk.modelcontextprotocol.io/v2/llms.txt`
- **TypeScript SDK (v1，只限既有的 v1 專案)**：從 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/v1.x/README.md` 抓取

### 各語言實作指南（階段 2 載入）
- [🐍 Python Implementation Guide](./reference/python_mcp_server.md) - 完整的 Python/FastMCP 指南，包含：
  - Server 初始化的寫法
  - Pydantic model 範例
  - 用 `@mcp.tool` 註冊工具
  - 完整可執行的範例
  - 品質檢查清單

- [⚡ TypeScript Implementation Guide (SDK v2)](./reference/node_mcp_server_v2.md) - `@modelcontextprotocol/server` 的完整 TypeScript 指南，包含：
  - 專案設定和 server factory
  - 工具設計：Zod 4 schema、輸出格式、分頁、錯誤
  - 同時支援 stdio 和 Streamable HTTP 的完整範例，加上 bearer 認證
  - Resource、prompt 和通知
  - 驗證建置好的 server 的自我檢查 script
  - 進階功能的 SDK 範例連結
  - v1 → v2 的對照表、遷移步驟和品質檢查清單

- [⚡ TypeScript Implementation Guide (SDK v1)](./reference/node_mcp_server.md) - 給既有 `@modelcontextprotocol/sdk` 專案的對應指南

### 評測指南（階段 4 載入）
- [✅ Evaluation Guide](./reference/evaluation.md) - 完整的評測建立指南，包含：
  - 問題的建立準則
  - 答案的驗證策略
  - XML 格式規範
  - 範例問題和答案
  - 用提供的 script 執行評測
