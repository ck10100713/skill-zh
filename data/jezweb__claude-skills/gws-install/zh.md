---
name: gws-install
description: "用既有的 OAuth 憑證，在另一台機器上快速安裝 Google Workspace CLI（gws）。需要先前 gws-setup 產生的 client_secret.json。只要使用者想在新電腦裝 gws、重灌系統後重裝、設定第二台工作站，或說「install gws」、「gws on new machine」、「set up gws again」，就用這個 skill。"
compatibility: claude-code-only
---

# Google Workspace CLI：快速安裝

用先前設定好的 OAuth 憑證，在另一台機器上安裝 `gws`。產出一個已完成認證、所有 agent skill 都準備好的 CLI。

**前置條件**：使用者必須有先前 `gws-setup`（或 Google Cloud Console）產生的 `client_secret.json`。如果沒有，改用 `gws-setup` skill。

## 工作流程

### 步驟 1：事前檢查

```bash
which gws && gws --version
ls ~/.config/gws/client_secret.json
gws auth status
```

如果已經用正確的 scope 完成認證，直接跳到步驟 4。

### 步驟 2：安裝 CLI

```bash
npm install -g @googleworkspace/cli
gws --version
```

### 步驟 3：設定憑證

請使用者提供 `client_secret.json`。有三種方式：

**選項 A：貼上 JSON 內容**

請使用者貼上 JSON，把它寫到 `~/.config/gws/client_secret.json`：

```bash
mkdir -p ~/.config/gws
```

預期格式：

```json
{
  "installed": {
    "client_id": "...",
    "project_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "...",
    "redirect_uris": ["http://localhost"]
  }
}
```

**選項 B：檔案路徑**

如果使用者本機有這個檔案（例如在 Downloads）：

```bash
mkdir -p ~/.config/gws
cp /path/to/client_secret.json ~/.config/gws/client_secret.json
```

**選項 C：環境變數**

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID="your-client-id"
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="your-client-secret"
```

### 步驟 4：認證

**重要**：這個步驟會印出一條很長的 OAuth URL（30 個以上的 scope），使用者必須在瀏覽器打開。這條 URL 太長，從終端機輸出複製會因為換行而壞掉。一定要先把它抽到檔案裡，再用程式打開。

先問要用哪個 Google 帳號，然後：

1. **在背景執行 auth** 並擷取輸出：

```bash
gws auth login -s gmail,drive,calendar,sheets,docs,chat,tasks 2>&1 | tee /tmp/gws-auth-output.txt
```

當成背景工作執行沒問題，使用者在瀏覽器核准之後它就會完成。

2. **抽出並打開 URL**（輸出出現後另外執行）：

```bash
grep -o 'https://accounts.google.com[^ ]*' /tmp/gws-auth-output.txt > /tmp/gws-auth-url.txt
cat /tmp/gws-auth-url.txt | xargs open
```

如果 `open` 沒用，就告訴使用者：「auth URL 存在 `/tmp/gws-auth-url.txt`，打開那個檔案，從裡面複製 URL。」

3. **等使用者**在瀏覽器核准，然後驗證：

```bash
gws auth status
```

**替代方案：`--full` 取得所有 scope**

```bash
gws auth login --full
```

使用者可以在原本那台機器上用 `gws auth status` 看當初授權了哪些 scope。

### 步驟 5：安裝 Agent Skills

```bash
npx skills add googleworkspace/cli -g --agent claude-code --all
```

這會把 90 個以上的 skill 裝進 `~/.claude/skills/`。skill 已經裝過的話，重跑也安全。

### 步驟 6：驗證

```bash
gws auth status
gws calendar +agenda --today
gws gmail +triage
```

---

## 疑難排解

### 「Auth error — credentials missing or invalid」（exit code 2）

- 檢查 `~/.config/gws/client_secret.json` 存在，而且是有效的 JSON
- 重新執行 `gws auth login`

### Token 過期

- 如果 GCP app 是「Testing」狀態，token 7 天後就會過期
- 重新執行 `gws auth login` 來更新
- 想要永久 token 的話，到 GCP Console 的 OAuth consent screen 把 app 推到 Production

### Skill 沒出現在 Claude Code

- Skill 是在 session 開始時載入的，安裝後要重啟 Claude Code
- 驗證：`ls ~/.claude/skills/gws-* | wc -l` 應該會顯示 30 個以上的資料夾

## 另請參閱

- [gws-setup](../gws-setup/SKILL.md)：第一次設定，包含建立 GCP 專案
- [gws-shared](~/.claude/skills/gws-shared/SKILL.md)：認證模式與全域 flag
