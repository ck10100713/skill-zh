---
name: teams-app-developer
description: "建置、測試並 deploy 給 Teams 和 Copilot 用的 Microsoft 365 應用程式與 agent。包含專案建立、本機測試、雲端 deploy、疑難排解，以及 Slack 轉 Teams 遷移的子 skill。USE FOR: Teams agent、bot、tab、message extension、Declarative Agents、Custom Engine Agents、local testing、Agents Playground、Azure resource provision、remote deployment、Slack to Teams migration、cross-platform bot development、Block Kit to Adaptive Cards conversion。DO NOT USE FOR: 一般網頁開發、非 bot / 非 Teams 專案。"
---

# Microsoft 365 Agents Toolkit Skill

用 ATK CLI 建置 Microsoft 365 agent 和 Teams 應用程式。

## AI 行為準則

1. **測試策略：** 先推薦 Agents Playground（比較快，不需要 M365）。只有使用者明確要求時，才用 Teams 流程。

2. **環境變數：** 絕對不要寫死 secret，也不要編造 placeholder 值。一定要向使用者要真實的值。

3. **錯誤處理：** 仔細讀錯誤訊息。檢查 `env/.env.local`、`.localConfigs` 和 `atk auth list`。常見的坑：
   - **`AADSTS7000229`** → `aadApp/create` 在 YAML 裡缺少 `generateServicePrincipal: true`，加上去然後重新 provision
   - `.localConfigs` 裡**缺少 `TENANT_ID`** → SDK 用了錯的 token authority → Bot Connector 回 401
   - **修好驗證後還是 401** → devtunnel URL 可能被列入黑名單，重建一個新的 tunnel
   - 完整的診斷步驟請看 [troubleshoot/troubleshoot.md](troubleshoot/troubleshoot.md)

4. **長時間執行的指令：要等它跑完：**
   - `atk new`、`atk provision`、`atk deploy` 可能要好幾分鐘
   - 一定要等它完成才能跑下一步（timeout 120000ms 以上）

5. **啟動本機服務：會卡住終端機（這是正常的）：**
   - `npm run dev`、`npm start`、`python app.py`、`devtunnel host` 等等都會卡住，因為程序會一直跑下去
   - 一定要當背景程序跑（`isBackground=true`），這些指令絕對不要用 `isBackground=false`
   - 不要等它「結束」，改成檢查輸出有沒有「listening on port」或 tunnel URL 來確認啟動
   - 如果出現錯誤，讀 log、診斷、修正、重啟
   - 用**新的終端機**來啟動 Agents Playground 或開啟 Teams sideloading URL

6. **監看 App Log：** 定期檢查背景終端機的輸出有沒有執行期錯誤。如果 app 當掉，讀錯誤、修掉根本原因，然後重啟。

7. **Telemetry 標記：** 跑任何 `atk` CLI 指令之前，先設定 session 環境變數，讓所有 CLI 呼叫都標記成由 skill 發起：
   ```bash
   export ATK_CLI_SKILL=true
   ```
   在 session 開頭執行一次。同一個終端機裡之後所有的 `atk` 指令都會繼承它。

## ATK CLI 設定

```bash
atk --version  # Must be > 1.1.5-beta
```

如果找不到 ATK 或版本太舊：

```bash
npm i -g @microsoft/m365agentstoolkit-cli@beta
```

## CLI 全域選項

| 選項 | 意思          | 建議                                                                                                                                                                   |
| ------ | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-i`   | 互動模式 | 自動化時一律用 `-i false`，避免卡住                                                                                                                             |
| `-f`   | 專案資料夾   | 預設是目前目錄，要指定自訂資料夾時才用。建立新專案時，這是專案資料夾要建立在底下的父資料夾。 |
| `-h`   | 指令說明    | 用 `atk <command> -h` 快速確認語法                                                                                                                                   |

## 子 Skills

| 子 Skill            | 什麼時候用                                                                      | 參考                                                                    |
| -------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **create-project**   | 用範本建立新專案、選範本、`atk new`                   | [create-project/create-project.md](create-project/create-project.md)         |
| **test-playground**  | 用 Agents Playground 在本機測試、`agentsplayground`、快速測試           | [test-playground/test-playground.md](test-playground/test-playground.md)     |
| **test-teams**       | 在 Teams 上跑、devtunnel、sideload、Teams 測試、在 Copilot 測試                | [test-teams/test-teams.md](test-teams/test-teams.md)                         |
| **provision-deploy** | provision Azure 資源、deploy 到雲端、`atk provision`、`atk deploy`        | [provision-deploy/provision-deploy.md](provision-deploy/provision-deploy.md) |
| **troubleshoot**     | 修錯誤、401、port 衝突、YAML 錯誤、過時的 bot                         | [troubleshoot/troubleshoot.md](troubleshoot/troubleshoot.md)                 |
| **slack-to-teams**   | 把 Slack bot 遷移到 Teams、跨平台橋接、Block Kit 轉 Adaptive Cards | [slack-to-teams/SKILL.md](slack-to-teams/SKILL.md)                           |

> **強制規定：** 執行任何流程之前，先讀對應的子 skill 文件。

## 共用參考資料

- [manifest-and-yaml.md](toolkit/manifest-and-yaml.md)：專案檔案、YAML 設定、環境變數、.localConfigs 流程
- [commands.md](toolkit/commands.md)：ATK CLI 指令：package、validate、share、collaborate
- [templates.md](toolkit/templates.md)：完整的範本目錄與語言支援
- [experts/](experts/index.md)：100 多個微型專家檔案：Teams SDK、Slack SDK、跨平台橋接、deploy、AI 模型、安全、語言轉換
- [docs/](docs/README.md)：平台比較指南：UI、訊息、身分、基礎設施、功能缺口

## 流程鏈

把使用者的意圖對應到最小可行的流程。

| 使用者意圖                   | 流程（依序讀）                    |
| ----------------------------- | ------------------------------------------- |
| 從零開始建新 app    | create-project → test-playground            |
| 在本機測試現有專案 | test-playground（建議）或 test-teams |
| Deploy 到 Azure               | provision-deploy                            |
| 修壞掉的 bot                | troubleshoot → 重新測試                      |
| 把 Slack bot 遷移到 Teams    | slack-to-teams                              |

> **強制規定：** 執行任何 slack-to-teams 流程之前，先讀 [slack-to-teams/SKILL.md](slack-to-teams/SKILL.md)。這個子 skill 裡有一套路由式專家系統，包含 100 多個微型專家檔案，用於跨平台 bot 開發。

## ATK 專案 Context 解析

只在缺少時才解析設定值。如果 session 裡已經知道某個值，就重複使用。

### 步驟 1：偵測 ATK 專案

如果目前資料夾裡有 `m365agentstoolkit*.yml`，就視為 ATK 專案並解析設定。

### 步驟 2：解析常見設定

解析 `m365agentstoolkit*.yml` 裡引用的變數。常見變數：
AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT_NAME

### 步驟 3：收集缺少的值

如果缺少必要的值，只問使用者缺少的那幾個。

完整的設定檔細節請參考 [manifest-and-yaml.md](toolkit/manifest-and-yaml.md)。
