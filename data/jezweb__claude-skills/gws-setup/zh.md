---
name: gws-setup
description: "從零開始設定 Google Workspace CLI（gws）。引導完成 GCP 專案建立、OAuth 憑證、認證，並為 Claude Code 安裝 90 個以上的 agent skill。只要使用者想第一次設定 gws、設定 Google Workspace API 存取、安裝 Google Workspace CLI，或排查 gws 認證問題，就用這個 skill。"
compatibility: claude-code-only
---

# Google Workspace CLI：第一次設定

設定 `gws` CLI（@googleworkspace/cli），配上 OAuth 憑證和 Claude Code 用的 90 個以上 agent skill。產出一個完整認證好的 CLI，附帶 Gmail、Drive、Calendar、Sheets、Docs、Chat、Tasks 等服務的 skill。

## 前置條件

- Node.js 18+
- 一個 Google 帳號（個人或 Workspace 都可以）
- 能進入 Google Cloud Console（console.cloud.google.com）

## 工作流程

### 步驟 1：事前檢查

檢查哪些已經做完，做完的步驟就跳過：

```bash
# Check if gws is installed
which gws && gws --version

# Check if client_secret.json exists
ls ~/.config/gws/client_secret.json

# Check if already authenticated
gws auth status
```

如果 `gws auth status` 顯示 `"status": "success"` 而且有 scope，就跳到步驟 6（安裝 Skills）。

### 步驟 2：安裝 CLI

```bash
npm install -g @googleworkspace/cli
gws --version
```

### 步驟 3：建立 GCP 專案和 OAuth 憑證

使用者需要在 Google Cloud Console 建立 OAuth Desktop App 憑證。一步一步帶他做。

**3a. 建立或選擇 GCP 專案：**

引導使用者到：`https://console.cloud.google.com/projectcreate`

或使用既有專案。問使用者偏好哪一種。

**3b. 啟用 Google Workspace API：**

引導使用者到他那個專案的 API Library：`https://console.cloud.google.com/apis/library?project=PROJECT_ID`

啟用這些 API（逐一搜尋）：
- Gmail API
- Google Drive API
- Google Calendar API
- Google Sheets API
- Google Docs API
- Google Chat API（需要額外設定 Chat App，見下方）
- Tasks API
- People API
- Google Slides API
- Google Forms API
- Admin SDK API（選用，Workspace 管理功能才需要）

**3c. 設定 Google Chat App（Chat API 必要）：**

光啟用 Chat API 不夠，就算是使用者 context 的 OAuth 存取，Google 也要求有 Chat App 設定。沒有的話，所有 Chat API 呼叫都會回錯誤。

引導使用者到：`https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat?project=PROJECT_ID`

1. 點 **Configuration** 分頁
2. 填 app 資訊（名稱、頭像、描述，CLI 用途下填什麼都沒差）
3. 在「Functionality」下勾選 **Spaces and group conversations**
4. 在「Connection settings」選 **Apps Script** 或 **HTTP endpoint**（隨便選一個，只要讓這份設定存在就好）
5. 儲存

這樣會建立 Chat API 所需要的 app 身分。透過 `gws` 發出的訊息，看起來仍然是認證過的使用者發的（OAuth 使用者 context），不是 bot。

**3e. 設定 OAuth consent screen：**

引導使用者到：`https://console.cloud.google.com/apis/credentials/consent?project=PROJECT_ID`

設定：
- User Type：**External**（任何 Google 帳號都能用）
- App name：`gws CLI`（或任何名稱）
- User support email：他自己的 email
- Developer contact：他自己的 email
- Scope 留空（gws 會在登入時才請求 scope）
- 把他的 Google 帳號加為測試使用者（app 在「Testing」狀態時必須這樣做）
- 每個畫面都儲存並繼續

**3f. 建立 OAuth client ID：**

引導使用者到：`https://console.cloud.google.com/apis/credentials?project=PROJECT_ID`

1. 點 **Create Credentials** → **OAuth client ID**
2. Application type：**Desktop app**
3. Name：`gws CLI`
4. 點 **Create**
5. 複製 JSON，或下載 `client_secret_*.json` 檔案

**3g. 儲存憑證：**

請使用者提供 client_secret.json 的內容（貼上 JSON，或給下載檔案的路徑）。

```bash
mkdir -p ~/.config/gws
```

把 JSON 寫到 `~/.config/gws/client_secret.json`。預期格式：

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

### 步驟 4：選擇 Scope

問使用者想要哪種程度的存取：

| 選項 | 指令 | 授權範圍 |
|--------|---------|----------------|
| **完整存取**（建議） | `gws auth login --full` | 所有 Workspace scope，包含 admin、pubsub、cloud-platform |
| **核心服務** | `gws auth login -s gmail,drive,calendar,sheets,docs,chat,tasks` | 只含最常用的服務 |
| **最小** | `gws auth login -s gmail,calendar` | 只有 email 和行事曆 |

進階使用者建議用**完整存取**。OAuth consent screen 會顯示所有請求的 scope，使用者授權前可以先檢視。

> **注意**：如果 GCP app 是「Testing」狀態，scope 的選擇上限約 25 個。用 `-s service1,service2` 請求特定 scope，或是發布 app（Publish → In Production）來取得更廣的 scope 存取。

### 步驟 5：認證

**重要**：這個步驟會印出一條很長的 OAuth URL（30 個以上的 scope），使用者必須在瀏覽器打開。這條 URL 太長，從終端機輸出複製會因為換行而壞掉。一定要先把它抽到檔案裡，再用程式打開。

1. 執行登入指令並擷取輸出：

```bash
gws auth login --full 2>&1 | tee /tmp/gws-auth-output.txt
# Or with specific services:
# gws auth login -s gmail,drive,calendar,sheets,docs,chat,tasks 2>&1 | tee /tmp/gws-auth-output.txt
```

當成背景工作執行沒問題，使用者在瀏覽器核准之後它就會完成。

2. 抽出並打開 URL（輸出出現後另外執行）：

```bash
grep -o 'https://accounts.google.com[^ ]*' /tmp/gws-auth-output.txt > /tmp/gws-auth-url.txt
cat /tmp/gws-auth-url.txt | xargs open
```

如果 `open` 沒用，就告訴使用者：「auth URL 存在 `/tmp/gws-auth-url.txt`，打開那個檔案，從裡面複製 URL。」

3. 等使用者在瀏覽器核准。

瀏覽器核准之後，gws 會把加密過的憑證存在 `~/.config/gws/credentials.enc`。

驗證：

```bash
gws auth status
```

應該會顯示 `"status": "success"`，以及已認證的帳號和授權的 scope。

### 步驟 6：安裝 Agent Skills

為 Claude Code 全域安裝 90 個以上的 gws agent skill：

```bash
npx skills add googleworkspace/cli -g --agent claude-code --all
```

驗證 skill 已安裝：

```bash
ls ~/.claude/skills/gws-* | wc -l
```

應該會顯示 30 個以上的 gws skill 資料夾。

### 步驟 7：把憑證存起來給其他機器用

如果使用者還有其他機器要設定，建議匯出 client 憑證：

```bash
gws auth export
```

這會把解密後的憑證（包含 refresh token）印到 stdout。`client_secret.json` 是可攜的部分，同一個 OAuth client 可以在任何機器上使用，每台機器用 `gws auth login` 產生新的使用者 token 即可。

告訴使用者把 `client_secret.json` 的內容存在安全的地方（密碼管理器、加密筆記），之後在其他機器上搭配 `gws-install` skill 使用。

### 步驟 8：確認一切正常

跑幾個指令確認：

```bash
# Check auth
gws auth status

# Check calendar
gws calendar +agenda --today

# Check email
gws gmail +triage
```

如果任何指令因為認證錯誤失敗，就用需要的 scope 重新執行 `gws auth login`。

---

## 關鍵模式

### Testing vs Production 的 OAuth App

GCP OAuth app 一開始是「Testing」狀態，token 7 天過期，scope 上限約 25 個。長期使用的話：
- 在 OAuth consent screen 設定裡把 app 推到 **Production**
- Production 的 app 沒有 token 過期限制
- 個人/內部使用的話，Google 不要求驗證

### Scope 參考

| 服務 flag | 啟用的功能 |
|-------------|-----------------|
| `gmail` | 寄送、讀取、管理 email、標籤、篩選器 |
| `drive` | 檔案、資料夾、共用雲端硬碟 |
| `calendar` | 活動、行事曆、忙碌/空閒 |
| `sheets` | 讀寫試算表 |
| `docs` | 讀寫文件 |
| `chat` | 空間、訊息 |
| `tasks` | 任務清單與任務 |
| `slides` | 簡報 |
| `forms` | 表單與回覆 |
| `people` | 聯絡人與個人檔案 |
| `admin` | Workspace 管理（目錄、裝置、群組） |

### 環境變數替代方案

不用 `client_secret.json` 的話，也可以用環境變數提供憑證：

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID="your-client-id"
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="your-client-secret"
gws auth login
```

### 設定資料夾

所有 gws 設定都放在 `~/.config/gws/`：

| 檔案 | 用途 |
|------|---------|
| `client_secret.json` | OAuth client 憑證（可攜） |
| `credentials.enc` | 加密的使用者 token（每台機器各自一份） |
| `token_cache.json` | Token 更新的快取 |
| `cache/` | API discovery schema 快取 |

## 另請參閱

- [gws-install](../gws-install/SKILL.md)：用既有憑證在其他機器上快速設定
- [gws-shared](~/.claude/skills/gws-shared/SKILL.md)：gws 指令的認證模式與全域 flag
