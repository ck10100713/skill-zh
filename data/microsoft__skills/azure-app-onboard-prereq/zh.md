---
name: azure-app-onboard-prereq
description: "評估原始碼是否準備好部署到 Azure，也就是在做 infrastructure 工作之前的檢查。評估 build 健康度、app 完整度、dependency 和本機服務、技術棧相容性，以及部署可行性。回答你的 app 在部署前需要什麼，包括 framework、dependency 和設定。檢查 dependency 是否相容，找出部署阻礙和不支援的 framework。WHEN: \"evaluate my repo\", \"is my app ready to deploy\", \"what does my app need to deploy\", \"what do I need before deploying\", \"does my app need\", \"can I ship this to Azure\", \"scan my repo for issues\", \"is this app deployable\", \"check if my app is ready for Azure\", \"do I need a Dockerfile\", \"what's blocking my deployment\", \"are there any blockers\", \"are my dependencies compatible\", \"does Azure support my framework\", \"what needs to change before deploying\", \"check my app configuration\"."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.3"
---

# Azure App Onboard Prereq — Repository Evaluation

在做 infrastructure 規劃之前，先評估使用者的 repository 的 build 健康度、app 完整度和 Azure 部署可行性。產出每個 component 的判定（PASS/WARN/FAIL），供下游 phase 使用。

> **和 orchestrator 的關係：** 由 `azure-app-onboard` 在 Step 3 呼叫，也可以單獨用來做程式碼就緒度檢查。被 orchestrator 呼叫時，寫完 artifact 之後要把控制權還給 `azure-app-onboard`，絕對不要直接呼叫下游 phase。

AppOnboard pipeline 四個 phase 裡的第 1 個。Session：`.copilot-azure/sessions/{session-id}/`。讀取 `context.json`。寫入 `components[]`、`repo{}`、`detectedInfra[]`。產出 `prereq-output.json`。Schema：[`prereq-schemas.ts`](references/prereq-schemas.ts)，包含 `PrereqOutput`、`BuildRequirements`。支援直接進入。

## When NOT to Use

| Signal | Redirect |
|--------|----------|
| 驗證 infrastructure（Bicep/TF/azure.yaml） | **azure-validate** |
| 產生 IaC | **azure-prepare** |
| 從點子到 production 的端到端流程 | **azure-app-onboard** |
| 執行 `azd up` 或部署 | **azure-deploy** |

## Rules

> ⛔ **絕對禁止：`npm install`、`npm test`、`npx jest`、`pytest`，以及所有 install/build/test 指令一律不准跑。**
> 在 prereq phase，無論如何都不准執行 `npm install`、`npm test`、`npx jest`、`pip install`、`pytest`、`dotnet build`、`dotnet restore`、`dotnet test`、`go mod download`、`cargo build`，或任何套件管理器的 install、build、test 指令。不要用跑測試套件的方式驗證程式碼，改成用靜態方式檢查測試設定檔。prereq phase 只做唯讀評估和純靜態驗證。
> **唯一例外，兩種情境，而且都要先取得同意：** (a) agent 在 migration/remediation 期間**修改過**的程式碼（見 [remediation-protocol.md](references/remediation-protocol.md) step 6），或 (b) agent 在 zero-code 路徑上**從頭寫**的程式碼（見 [zero-code-path.md](references/zero-code-path.md)）。這兩種情況，install/build/test 都只能透過使用者確認的 build-validation 關卡（[build-check.md](references/build-check.md) Step 3）執行，而且要使用者回答過那個針對特定指令的同意提示才行。事先給過的一般同意不算數。

1. ⛔ **完整 pipeline（Step 1–8），沒有例外。** 所有 prompt 都直接進 Step 1。針對特定問題的回答要放在發現結果（Step 5）裡，不要放在這之前。
2. ⛔ **評估不准用 sub-agent。** 三軸評估都在同一個 context 內完成。**例外**：zero-code 路徑的 scaffolding（Step 2）。
3. 修改程式碼或做破壞性修改都需要 `ask_user`。出結果之前最多問 3 個問題。直接進入時，不要重問 orchestrator 已經問過的意圖問題。

## MCP Tools

| Tool | Purpose |
|------|---------|
| `mcp_azure_mcp_get_azure_bestpractices` | 用 Azure best practice 驗證偵測到的技術棧模式 |
| `mcp_azure_mcp_extension_cli_install` | 檢查/安裝需要的 CLI 工具（az、azd、func） |

## Workflow

### Step 1: Session Check

**從 orchestrator 進入：** Session 已經存在，讀 `context.json`，進到 Step 2。

**直接進入：** 檢查 `.copilot-azure/sessions/active-session.json`：
- **存在** → ⛔ 讀 [session-protocol.md](references/session-protocol.md) 取得恢復/重新開始的關卡。使用者回答之前不准繼續。
- **不存在** → 建立 session：產生 UUID，執行 `New-Item -ItemType Directory -Path ".copilot-azure/sessions/{uuid}" -Force`，用 `create` tool 寫入 `context.json` 和 `active-session.json`。

接著：`az account show` → 把 `{id, name, tenantId}` 合併進 `context.json.azure`。⛔ 在任何掃描之前，session 一定要先存在磁碟上。

### Step 2: Scan Workspace

掃描專案檔案。偵測 component、`repo{}`、`detectedInfra[]`、`detectedServices[]`。對 Terraform provider 分類。檢查 CLI 是否可用。技術棧偵測衝突時：使用者明確講的優先（寫進 `context.json`，把這次掃描標為 override）；只有掃描結果的話 → 跟使用者確認；有多個技術棧 → 全部列出來問（見 [component-mapping.md](references/component-mapping.md)）；沒有程式碼 → [zero-code-path.md](references/zero-code-path.md)。

> 如果沒有專案檔案、沒有 Dockerfile，而且沒有 index.html → ⛔ 讀 [zero-code-path.md](references/zero-code-path.md)。

> ⛔ **Cloud SDK 提早關卡。** grep `aws-sdk|@aws-sdk|boto3|google-cloud|@google-cloud|firebase`。如果找到實際在用的 dependency → 讀 [cloud-sdk-migration.md](references/cloud-sdk-migration.md)，然後 `ask_user`：**"Redirect to Azure Cloud Migrate"**（設定 `routeToSkill: "azure-cloud-migrate"`）· **"Continue evaluation anyway"**（完成就緒度評估和 SDK→Azure 對應，然後在 Step 8 停下來，dependency 換掉之前不出規劃）· **"Cancel"**。

### Step 3: Per-Component Evaluation

| Sub-step | Action | Reference |
|----------|--------|-----------|
| 3.1 | **Build check** | ⛔ **你一定要讀 [build-check.md](references/build-check.md)** |
| 3.2 | **Completeness check** | ⛔ **你一定要讀 [completeness-check.md](references/completeness-check.md)** |
| 3.3 | **Deployability check** | ⛔ **你一定要讀 [deployability-check.md](references/deployability-check.md)** |
| 3.3a | **Component mapping**（有條件） | 只有在找到超過 1 個專案 manifest（monorepo）時才讀 [component-mapping.md](references/component-mapping.md) |

評估完之後，為每個 component 填入 `buildRequirements`。判定的傳遞、tier 規則和 f1Viable 的彙總，都在 [readiness-gate.md](references/readiness-gate.md) 和各個檢查 reference 裡。

### Step 4: Write Artifacts + Readiness Gate

⛔ 確認 `context.json` 存在磁碟上。先讀 [readiness-gate.md](references/readiness-gate.md)（判定、tier、batch-then-approve、fast-track），再讀 [prereq-artifacts.md](references/prereq-artifacts.md)（寫入流程、schema）。

### Step 5: Present Findings

依照 [readiness-gate.md § Present Findings](references/readiness-gate.md)，先依嚴重度分組顯示判定，再繼續。

### Step 6: Remediation (conditional)

⛔ 如果有任何 ❌ FAIL 判定、🔧 Recommended Fix，或帶有 `fixPhase: "prereq"` 的 ⚠️ WARN，**你一定要讀 [remediation-protocol.md](references/remediation-protocol.md)**。裡面包含修復迴圈、靜態驗證、強制重新評估、修復後的 artifact 更新，以及 build-validation 同意關卡。如果所有判定都是 ✅ PASS，或是沒有 `fixPhase: "prereq"` 的 ⚠️ WARN，就跳到 Step 7。

### Step 7: Write Final State

`completedPhases` 已經有 `"prereq"` 而且 `currentPhase: null`（來自 Step 4）。然後：

> ⛔ **寫入 `lastScanCommit`。** 執行 `git rev-parse HEAD`，把完整的 40 字元 SHA 存進 `context.json.repo.lastScanCommit`。這是必填：Step 1 的過期防護會在恢復 session 時拿它和 HEAD 比對，偵測有沒有變動。

### Step 8: Route

⛔ **必做，不准跳過這一步。**

> **路由欄位：** 所有路由都會把 `routeToSkill` 和 `routeReason` 寫進 `context.json`。

> **修復後的 context：** 如果 Step 6 有跑，路由提示一開頭要先說：「修復完成：已修好 {N} 個問題，你的 app 現在是 {overallHealth}。」

> ⛔ **由上到下比對每一列，第一個符合的就用。**

| # | Condition | Action |
|---|-----------|--------|
| 1 | 有設定 `routeToSkill`（任何一筆） | `ask_user`："Redirect to {routeToSkill}" / "Not now"。⛔ Pipeline 到此為止，不准繼續做架構規劃。 |
| 2 | `cloudSdkFindings[]` 非空（使用者選了 "Continue evaluation anyway"） | 把 cloud-SDK → Azure 的替換對應當作 🔶 blocker 呈現，然後用這段原封不動的 prompt 做 `ask_user`：**"🔶 Cloud SDK migration required — these dependencies must be swapped before this app can deploy to Azure. (Redirect to azure-cloud-migrate / Stop — swap manually and re-run)"** — Redirect 會設定 `routeToSkill: "azure-cloud-migrate"`，Stop 就停下來。⛔ Pipeline 到此為止，不准繼續做架構規劃，也不准提供「繼續到 prepare」的選項，dependency 沒換掉之前這個 app 不能部署。 |
| 3 | Orchestrator + 沒有 `routeToSkill` | 告訴使用者：「✅ 你的 app 已經評估完而且準備好了，我們來規劃你的 Azure 部署。」然後呼叫 `azure-app-onboard`。⛔ 不准停下來、不准等使用者輸入、不准旁白內部的交接。使用者在 scope triage 時就已經同意走完整條 pipeline。 |
| 4 | 直接進入 + ready/readyWithCaveats + 沒有 Azure infra | `ask_user`："Deploy to Azure (full pipeline)" → 呼叫 `azure-app-onboard` / "Not now" |
| 5 | 直接進入 + ready/readyWithCaveats + 已有 Azure infra | `ask_user`："Start fresh" → 呼叫 `azure-app-onboard` / "Use existing infra" → 呼叫 `azure-prepare` / "Not now" |
| 6 | 直接進入 + blocked | 回報 blocker 摘要，並說「修好之後重跑。」 |

嚴重度 tier（🛑🔶❌🔧⚠️✅）定義在 [readiness-gate.md](references/readiness-gate.md)。

## Outputs

| Artifact | Location | Consumer |
|----------|----------|----------|
| Session context | `context.json` → `components[]`、`repo{}`、`detectedInfra[]`、`detectedServices[]` | 所有下游 phase |
| Prereq output | `prereq-output.json` | prepare phase（透過 `azure-app-onboard`） |
| Readiness report | `.copilot-azure/sessions/{uuid}/readiness-report.md` | 使用者（離線參考） |
