---
name: slack-to-teams
description: "microsoft-365-agents-toolkit 的子 skill。這是一套有 100 多個微型專家檔案的路由式專家系統，用於把 Slack bot 遷移到 Teams、跨平台橋接，以及雙平台 bot 開發。USE FOR: migrating Slack bot to Teams、adding Teams support to Slack bot、building dual-platform bots、converting Block Kit to Adaptive Cards、identity/OAuth bridging、deploying bots to Azure or AWS、configuring AI model providers。DO NOT USE FOR: 一般網頁開發、非 bot 專案、沒有 Slack 的獨立 Teams 開發（請改用上層 skill）。"
---

# Slack to Teams 專家系統

一套有 100 多個微型專家檔案的路由式專家系統，用於把 Slack bot 遷移到 Teams，以及建立跨平台 bot。

> **上層 skill：** ATK CLI 的設定和路由請看 [../SKILL.md](../SKILL.md)。本機測試請看 [../test-playground/test-playground.md](../test-playground/test-playground.md) 或 [../test-teams/test-teams.md](../test-teams/test-teams.md)。雲端 deploy 請看 [../provision-deploy/provision-deploy.md](../provision-deploy/provision-deploy.md)。疑難排解請看 [../troubleshoot/troubleshoot.md](../troubleshoot/troubleshoot.md)。

## 什麼時候用

- 建立新的 Slack bot、Teams bot 或雙平台 bot
- 為現有的 Slack bot 加上 Teams 支援（或反過來）
- 在平台之間遷移 bot
- 把 bot deploy 到 Azure 或 AWS
- 為 bot 設定 AI 模型供應商
- 在 Block Kit 和 Adaptive Cards 之間轉換 UI
- 橋接平台之間的身分、事件、檔案或傳輸層
- 讓 Teams bot 專案相容於 Microsoft Agents Toolkit（m365agents.yml、env/、appPackage 的 placeholder）

## 步驟

### 步驟 1：判斷專案類型

評估開發者是已經有程式碼，還是從零開始。

- **新專案** → 前往[新專案流程](#new-project-flow)
- **現有專案** → 前往[現有專案流程](#existing-project-flow)

---

### 新專案流程

#### 1a：選擇平台

問開發者要支援哪些平台：
- Slack + Teams（雙平台）
- 只要 Slack
- 只要 Teams

#### 1b：載入專家系統

1. 讀 [experts/index.md](../experts/index.md)，這是根路由器。
2. 執行該檔案裡定義的**事前訪談**。
3. 依平台選擇路由：
   - **Slack + Teams** → 讀 [experts/bridge/index.md](../experts/bridge/index.md)。載入 [cross-platform-advisor](../experts/bridge/cross-platform-advisor-ts.md)。
   - **只要 Slack** → 讀 [experts/slack/index.md](../experts/slack/index.md)。
   - **只要 Teams** → 讀 [experts/teams/index.md](../experts/teams/index.md)。

#### 1c：架構設定

1. 讀 [cross-platform-architecture](../experts/bridge/cross-platform-architecture-ts.md)（就算只做單一平台也要讀，它會建立之後加第二個平台的模式）。
2. 交給 domain router 和 advisor 接手。
3. 在目標專案根目錄寫一份 `PLAN.md`，記錄平台、功能、載入的專家。

#### 1d：實作

照 advisor 或 domain router 的輸出做。一個功能一個功能實作：
1. 從有優先順序的清單挑下一個功能。
2. 載入該功能指定的專家。
3. 用專家的模式和規則來實作。
4. 對照專家的陷阱段落做驗證。

---

### 現有專案流程

#### 2a：分析專案

**平行**跑這四個子分析：

**偵測語言**：掃描 `package.json`+`tsconfig.json`（TypeScript）、`pom.xml`/`build.gradle`（Java）、`*.csproj`/`*.sln`（C#）、`go.mod`（Go）、`requirements.txt`/`pyproject.toml`（Python）、`Gemfile`（Ruby）、`Cargo.toml`（Rust）。

**偵測目前的平台**：掃描相依套件裡的 SDK 指標：
- Slack：`@slack/bolt`、`@slack/web-api`、`slack_bolt`、`app.message`、`app.command`、`ack()`
- Teams：`@microsoft/teams-ai`、`botbuilder`、`TeamsActivityHandler`、`app.turn`、Adaptive Cards

**偵測功能**：掃描 slash command、Block Kit/Adaptive Cards、action handler、OAuth、檔案上傳/下載、排程、threading、AI/LLM 呼叫、主動訊息。

**偵測架構**：掃描 web framework（Express、Fastify 等）、hosting 目標（Azure、AWS、Docker）、雲端供應商、架構模式（單一 bot、雙 bot、monolith）。

#### 2b：語言關卡

把偵測到的語言分類到 SDK 等級：

| 等級 | 語言 | 指引 |
|---|---|---|
| **1：完整 SDK** | TypeScript / JavaScript | 有完整的專家系統可用 |
| **2：改寫** | Python | 兩邊的 SDK 都有，改寫 TS 的模式。載入 [bolt-python](../experts/slack/bolt-python.md)、[teams-python](../experts/teams/teams-python.md)、[python-cross-platform](../experts/bridge/python-cross-platform.md) |
| **3：SDK 分裂** | Java、C# | 一個平台有 SDK，另一個要走 REST。載入 [bolt-java](../experts/slack/bolt-java.md) 或 [teams-dotnet](../experts/teams/teams-dotnet.md) + [rest-only](../experts/bridge/rest-only-integration-ts.md) |
| **4：沒有 SDK** | Go、Ruby、Rust | 兩邊都只能用 REST。載入 [rest-only](../experts/bridge/rest-only-integration-ts.md) |

#### 2c：專家覆蓋缺口分析

1. 讀 [experts/analyzer.md](../experts/analyzer.md)。
2. 執行 analyzer 的流程：掃描 manifest、相依套件、原始碼。
3. 把偵測到的技術和現有專家交叉比對。
4. 提出缺口分析：哪些技術有覆蓋、哪些沒有。

#### 2d：建立缺少的專家（需要時）

1. 讀 [experts/builder.md](../experts/builder.md)。
2. 對每個缺口：分析專案的使用方式 → 讀套件原始碼 → 起草專家 → 驗證 → 接進路由。
3. 用 [experts/_expert-ts.md](../experts/_expert-ts.md) 當範本。

#### 2e：載入專家系統

1. 讀 [experts/index.md](../experts/index.md)，這是根路由器。
2. 執行事前訪談，用 2a 的分析結果預先填答案。
3. 依偵測到的平台和任務意圖路由：
   - 有 Slack、想要 Teams → **Bridge** domain
   - 有 Teams、想要 Slack → **Bridge** domain
   - 兩個都有 → 依任務路由（橋接調整、deploy、模型等）
   - 兩個都沒有 → 問要以哪些平台為目標
4. 如果是做橋接，載入 [cross-platform-advisor](../experts/bridge/cross-platform-advisor-ts.md)。把分析結果餵進 Phase 1。

#### 2f：架構與實作

1. 讀 [cross-platform-architecture](../experts/bridge/cross-platform-architecture-ts.md)。
2. 寫一份 `PLAN.md`，記錄分析結果、路由決定和功能遷移順序。
3. 依 advisor 有優先順序的清單，一個功能一個功能實作。

## Agents Toolkit 相容性

ATK 相容的專案結構（m365agents.yml、env/ 檔案、appPackage）請看上層 skill：
- **[上層 SKILL.md](../SKILL.md)**：ATK CLI 設定、子 skill 路由、流程鏈
- **[manifest-and-yaml.md](../toolkit/manifest-and-yaml.md)**：專案檔案、YAML 設定、環境變數、.localConfigs 流程
- **[commands.md](../toolkit/commands.md)**：打包、驗證、分享、協作、環境管理
- **[templates.md](../toolkit/templates.md)**：所有範本及其語言支援

Teams manifest schema 和打包請看 [runtime.manifest-ts](../experts/teams/runtime.manifest-ts.md)。

## 錯誤復原

如果專家系統沒涵蓋某個主題：
1. 讀 [experts/fallback.md](../experts/fallback.md)。
2. Phase 1：重新掃描所有 domain router，找漏掉的專家。
3. Phase 2：用網路搜尋補剩下的知識缺口。
4. 考慮用 [experts/builder.md](../experts/builder.md) 建立新專家。

## 專家 Domain

| Domain | 索引 | 說明 |
|---|---|---|
| Slack | [experts/slack/index.md](../experts/slack/index.md) | Bolt framework、事件、OAuth、指令、UI、CLI |
| Teams | [experts/teams/index.md](../experts/teams/index.md) | Teams AI SDK、Adaptive Cards、Graph、MCP、A2A、deploy |
| Bridge | [experts/bridge/index.md](../experts/bridge/index.md) | 27 個跨平台轉換專家（核心差異化所在） |
| Deploy | [experts/deploy/index.md](../experts/deploy/index.md) | Azure 與 AWS 的 deploy 逐步教學 |
| Models | [experts/models/index.md](../experts/models/index.md) | AI 模型供應商（OpenAI、Anthropic、Bedrock 等） |
| Convert | [experts/convert/index.md](../experts/convert/index.md) | 轉換成 TypeScript 的語言轉換 |
| Security | [experts/security/index.md](../experts/security/index.md) | 輸入驗證、secrets 管理 |

## 平台比較文件

並排比較兩個平台的參考指南：

- [UI Components](../docs/ui-components.md)：Block Kit 對 Adaptive Cards
- [Messaging & Commands](../docs/messaging-and-commands.md)
- [Identity & Auth](../docs/identity-and-auth.md)
- [Interactive Responses](../docs/interactive-responses.md)
- [Files & Links](../docs/files-and-links.md)
- [Middleware & Handlers](../docs/middleware-and-handlers.md)
- [Infrastructure](../docs/infrastructure.md)
- [Advanced Features](../docs/advanced-features.md)
- [Feature Gaps](../docs/feature-gaps.md)
- [Workflow Scenarios](../docs/workflows.md)：給 Teams bot 用的訊息原生工作流程模式（觸發、狀態、邏輯、AI、可見度）

