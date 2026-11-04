---
name: wordpress-setup
description: "透過 SSH 上的 WP-CLI 或 REST API 連接到 WordPress 網站。檢查 CLI、測試 SSH、設定驗證、驗證存取、儲存設定。只要使用者想連接 WordPress 網站、設定 WP-CLI 存取、建立 Application Password，或排查 WordPress 連線 / 驗證問題，就用這個 skill。"
compatibility: claude-code-only
---

# WordPress Setup

連接到 WordPress 網站，並透過 WP-CLI 或 REST API 驗證存取可用。產出一份驗證過的連線設定，可以直接拿來做內容管理和 Elementor 編輯。

## 工作流程

### 步驟 1：檢查 WP-CLI

```bash
wp --version
```

如果沒有安裝，引導使用者：

```bash
# macOS/Linux
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp
```

同時確認有 SSH 擴充功能（遠端網站需要）：

```bash
wp package install wp-cli/ssh-command
```

### 步驟 2：連接到網站

**選項 A：透過 SSH 使用 WP-CLI（建議）**

```bash
wp --ssh=user@hostname/path/to/wordpress option get siteurl
```

常見的寫法：
- Rocket.net：`wp --ssh=user@hostname/www/sitename/public option get siteurl`
- cPanel：`wp --ssh=user@hostname/public_html option get siteurl`
- 自訂：問使用者 SSH 使用者、主機和 WordPress 路徑

先用簡單的指令測試：

```bash
wp --ssh=user@host/path core version
```

**選項 B：用 Application Password 的 REST API**

如果 SSH 不可用：

1. 前往 `https://example.com/wp-admin/profile.php`（或使用瀏覽器自動化）
2. 捲到 "Application Passwords" 區塊
3. 輸入名稱（例如 "Claude Code"），點 "Add New Application Password"
4. 複製產生的密碼（空格是密碼的一部分，但在驗證時可有可無）

測試連線：

```bash
curl -s https://example.com/wp-json/wp/v2/posts?per_page=1 \
  -u "username:xxxx xxxx xxxx xxxx xxxx xxxx" | jq '.[0].title'
```

### 步驟 3：儲存憑證

**WP-CLI SSH**：在專案根目錄建立 `wp-cli.yml`：

```yaml
ssh:
  sitename:
    cmd: ssh -o StrictHostKeyChecking=no %pseudotty% user@hostname %cmd%
    url: /path/to/wordpress
```

之後這樣用：`wp @sitename option get siteurl`

**REST API**：存在 `.dev.vars`：

```
WP_SITE_URL=https://example.com
WP_USERNAME=admin
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

確認 `.dev.vars` 在 `.gitignore` 裡。跨專案使用的話，存在你慣用的 secrets 管理工具（環境變數、1Password CLI 等）。

### 步驟 4：驗證完整存取

執行完整的檢查：

```bash
# Site info
wp @sitename option get siteurl
wp @sitename option get blogname

# Content access
wp @sitename post list --post_type=page --posts_per_page=5 --fields=ID,post_title,post_status

# Plugin status (check for Elementor)
wp @sitename plugin status elementor

# Theme info
wp @sitename theme status
```

### 步驟 5：儲存網站設定

建立 `wordpress.config.json`，讓其他 skill 參考：

```json
{
  "site": "example.com",
  "siteUrl": "https://example.com",
  "accessMethod": "ssh",
  "sshAlias": "sitename",
  "wpPath": "/path/to/wordpress",
  "hasElementor": true,
  "elementorVersion": "3.x.x"
}
```

---

## 關鍵模式

### SSH 連線問題

| 症狀 | 解法 |
|---------|-----|
| `Permission denied (publickey)` | 檢查 SSH key：`ssh -v user@host` |
| 透過 SSH 出現 `wp: command not found` | WP-CLI 不在遠端的 PATH 裡，用完整路徑：`/usr/local/bin/wp` |
| `Error: This does not appear to be a WordPress installation` | 路徑錯誤，檢查 `wp-path` 參數 |
| 大型操作逾時 | 加上 `--ssh=user@host/path --allow-root`，或增加 SSH 逾時時間 |

### WP-CLI Alias

為常用的網站在 `~/.wp-cli/config.yml` 定義 alias：

```yaml
@client1:
  ssh: user@client1.example.com/www/public
@client2:
  ssh: user@client2.rocketcdn.me/www/client2/public
```

之後：`wp @client1 post list`

### REST API 陷阱

- Application password 需要 HTTPS（HTTP 不能用）
- 有些安全外掛會擋 REST API，檢查有沒有 401/403 回應
- 快取外掛可能會回傳過期的 REST 回應，用 `?_=${timestamp}` 破壞快取
- 自訂 post type 需要 `show_in_rest: true` 才會出現在 API 裡

---

## 參考檔案

- `references/wp-cli-essentials.md`：SSH alias 模式、常用 flag 和疑難排解
