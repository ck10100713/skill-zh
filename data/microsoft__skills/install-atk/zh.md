---
name: install-atk
description: >
  安裝或更新 M365 Agents Toolkit (ATK) 的 CLI 和 VS Code extension。
  Triggers: "install atk", "update atk", "install agents toolkit", "update agents toolkit",
  "install the toolkit", "setup atk", "get atk", "install atk cli", "install atk extension",
  "install atk vsix", "update the vs code extension", "install latest atk", "upgrade atk"
---

# Install ATK

安裝或更新 M365 Agents Toolkit (ATK) 的 CLI 和/或 VS Code extension。

## Telemetry Tagging

執行任何 `atk` CLI 指令之前，先設定 session 環境變數，讓所有 CLI 呼叫都被標記為 skill 發起的：
```bash
export ATK_CLI_SKILL=true
```
在 session 開頭跑一次就好。同一個終端機之後所有的 `atk` 指令都會繼承它。

## Triggers

使用者要求下列事項時，這個 skill 會啟動：
- 安裝或更新 ATK / Agents Toolkit / the toolkit
- 安裝或更新 ATK CLI
- 安裝或更新 ATK 的 VS Code extension / VSIX
- 設定 ATK / 開始使用 ATK

## Behavior

ATK CLI 指令使用 `npx -y --package @microsoft/m365agentstoolkit-cli atk`，它會自動下載並執行最新版，不需要全域安裝。

被觸發時，先判斷使用者要什麼：

| User intent | Action |
|-------------|--------|
| 安裝/更新**全部**，或只說「ATK」 | 確認 CLI 能用 + 安裝 VSIX |
| 只安裝/更新 **CLI** | 確認 CLI 能用（npx 會自動處理） |
| 只安裝/更新 **extension** / **VSIX** | 只安裝 VSIX |
| 不明確 | 確認 CLI 能用 + 安裝 VSIX |

## Commands

### Step 1: Verify ATK CLI works

```bash
npx -y --package @microsoft/m365agentstoolkit-cli atk --version
```

- **如果成功**（印出版本號）：ATK CLI 可以用。`npx` 前綴會在第一次使用時自動下載最新的套件，並快取起來給之後的執行用。
- **如果失敗**：檢查有沒有安裝 Node.js 18+ 和 npm。`npx` 指令需要能正常運作的 Node.js 環境。

### Step 2: ATK VS Code Extension (if requested)

```bash
code --install-extension TeamsDevApp.ms-teams-vscode-extension
```

## Execution

1. **驗證** ATK CLI 能用：執行 `npx -y --package @microsoft/m365agentstoolkit-cli atk --version`
2. 回報結果（版本號/失敗）
3. 如果使用者要求，安裝 VS Code extension
4. 說明所有 ATK 指令都使用 `npx -y --package @microsoft/m365agentstoolkit-cli atk` 前綴，不需要全域安裝

## Safety Rules

- **絕對不准**略過錯誤，失敗要清楚回報給使用者
- **一定要**使用上面的確切套件名稱和 extension ID，不要換成其他名稱或連結
