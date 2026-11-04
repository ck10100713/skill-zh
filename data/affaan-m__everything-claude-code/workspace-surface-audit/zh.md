---
name: workspace-surface-audit
description: 稽核目前的 repo、MCP server、plugin、connector、環境變數與 harness 設定，然後推薦最有價值的 ECC 原生 skill、hook、agent 和操作流程。使用者想要協助設定 Claude Code，或想了解自己的環境實際上有哪些能力時使用。
metadata:
  origin: ECC
---

# Workspace Surface Audit

唯讀的稽核 skill，用來回答這個問題：「這個 workspace 和這台機器現在實際上能做什麼，接下來該新增或啟用什麼？」

這是 ECC 原生對 setup-audit 類 plugin 的回應。除非使用者明確要求後續實作，否則不會修改任何檔案。

## 何時使用

- 使用者說「幫我設定 Claude Code」、「推薦自動化」、「我該用哪些 plugin 或 MCP？」或「我還缺什麼？」
- 在安裝更多 skill、hook 或 connector 之前，先稽核機器或 repo
- 拿官方 marketplace 的 plugin 跟 ECC 原生的覆蓋範圍做比較
- 檢視 `.env`、`.mcp.json`、plugin 設定或已連接 app 的介面，找出缺少的工作流程層
- 判斷某個能力該做成 skill、hook、agent、MCP，還是外部 connector

## 絕對不能違反的規則

- 絕對不要印出 secret 的值。只列出 provider 名稱、能力名稱、檔案路徑，以及 key 或設定是否存在。
- ECC 有合理能力接手的地方，優先用 ECC 原生流程，不要一直給「再裝一個 plugin」這種通用建議。
- 外部 plugin 只當作基準和靈感來源，不是權威的產品邊界。
- 清楚分成三類：
  - 現在就能用的
  - 能用但 ECC 還沒包裝好的
  - 沒有，需要新整合的

## 稽核輸入

只檢查能把問題回答好所需的檔案和設定：

1. Repo 介面
   - `package.json`、lockfile、語言標記、framework 設定、`README.md`
   - `.mcp.json`、`.lsp.json`、`.claude/settings*.json`、`.codex/*`
   - `AGENTS.md`、`CLAUDE.md`、安裝 manifest、hook 設定
2. 環境介面
   - 目前 repo 以及明顯相鄰的 ECC workspace 裡的 `.env*` 檔案
   - 只列出 key 名稱，例如 `STRIPE_API_KEY`、`TWILIO_AUTH_TOKEN`、`FAL_KEY`
3. 已連接的工具介面
   - 已安裝的 plugin、已啟用的 connector、MCP server、LSP 和 app 整合
4. ECC 介面
   - 已經涵蓋這個需求的現有 skill、command、hook、agent 和安裝模組

## 稽核流程

### 階段 1：盤點現有的東西

產出精簡的清單：

- 啟用中的 harness 目標
- 已安裝的 plugin 和已連接的 app
- 已設定的 MCP server
- 已設定的 LSP server
- 從 key 名稱推得的、靠環境變數運作的服務
- 已經跟這個 workspace 相關的 ECC skill

如果某個介面只有底層原件，要特別指出。例如：

- 「Stripe 可透過已連接的 app 使用，但 ECC 沒有 billing-operator skill」
- 「Google Drive 已連接，但沒有 ECC 原生的 Google Workspace 操作流程」

### 階段 2：對照官方與已安裝的介面做基準比較

把 workspace 拿來跟這些比較：

- 跟 setup、review、docs、design 或工作流程品質有重疊的官方 Claude plugin
- Claude 或 Codex 裡本機已安裝的 plugin
- 使用者目前已連接的 app 介面

不要只列名稱。每個比較都要回答：

1. 它們實際上做什麼
2. ECC 是否已經持平
3. ECC 是否只有底層原件
4. ECC 是否完全缺少這個流程

### 階段 3：把缺口變成 ECC 的決策

對每個真正的缺口，推薦正確的 ECC 原生形式：

| 缺口類型 | 偏好的 ECC 形式 |
|----------|---------------------|
| 可重複的操作流程 | Skill |
| 自動強制執行或副作用 | Hook |
| 專門的委派角色 | Agent |
| 外部工具橋接 | MCP server 或 connector |
| 安裝/啟動引導 | Setup 或 audit skill |

需求偏向操作面而非基礎設施面時，預設做成面向使用者、去編排現有工具的 skill。

## 輸出格式

依以下順序回傳五個段落：

1. **目前的介面**
   - 現在已經能用的東西
2. **持平項目**
   - ECC 已經跟基準相當或更好的地方
3. **只有底層原件的缺口**
   - 工具有了，但 ECC 缺少乾淨的操作 skill
4. **缺少的整合**
   - 還沒有的能力
5. **接下來的前 3-5 步**
   - 具體的 ECC 原生新增項目，依影響力排序

## 推薦規則

- 每個類別最多推薦 1-2 個最有價值的點子。
- 優先選使用者意圖明確、有商業價值的 skill：
  - setup 稽核
  - 帳務/客戶營運
  - issue/專案營運
  - Google Workspace 營運
  - 部署/營運控制
- 如果 connector 是公司專屬的，只有在它確實可用，或明顯對使用者的流程有幫助時才推薦。
- 如果 ECC 已經有很強的底層原件，就提議做一個 wrapper skill，不要硬發明全新的子系統。

## 好的結果

- 使用者能立刻看出什麼已連接、缺什麼、ECC 接下來該接手什麼。
- 推薦夠具體，在 repo 裡不用再做一輪探索就能實作。
- 最終回答是圍繞工作流程組織的，不是圍繞 API 品牌。
