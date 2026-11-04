---
name: zoom-cobrowse-sdk
description: "Zoom Cobrowse SDK 的參考 skill。在導向協作式客服的工作流程之後，實作瀏覽器共同瀏覽、標註工具、隱私遮罩、遠端協助或以 PIN 碼分享 session 時使用。"
user-invocable: false
triggers:
  - "cobrowse"
  - "co-browse"
  - "collaborative browsing"
  - "agent assist"
  - "customer support screen share"
  - "zoom cobrowse"
---

# Zoom Cobrowse SDK：網頁開發

用 Zoom Cobrowse SDK 做網頁協作瀏覽的背景參考。在客服工作流程已經清楚、需要實作細節時使用。

**官方文件**：https://developers.zoom.us/docs/cobrowse-sdk/  
**API 參考**：https://marketplacefront.zoom.us/sdk/cobrowse/  
**Quickstart Repository**：https://github.com/zoom/CobrowseSDK-Quickstart  
**Auth Endpoint 範例**：https://github.com/zoom/cobrowsesdk-auth-endpoint-sample

## 快速連結

**剛接觸 Cobrowse SDK？照這個順序走：**

1. **[Get Started Guide](get-started.md)** - 從憑證到第一次 session 的完整設定
2. **[Session Lifecycle](concepts/session-lifecycle.md)** - 理解客戶和客服的流程
3. **[JWT Authentication](concepts/jwt-authentication.md)** - Token 產生與安全性
4. **[Customer Integration](examples/customer-integration.md)** - 把 SDK 整合進你的網站
5. **[Agent Integration](examples/agent-integration.md)** - 設定客服入口（iframe 或 npm）

**核心概念：**
- **[Two Roles Pattern](concepts/two-roles-pattern.md)** - 客戶 vs 客服的架構
- **[Session Lifecycle](concepts/session-lifecycle.md)** - PIN 碼產生、連線、重新連線
- **[JWT Authentication](concepts/jwt-authentication.md)** - SDK Key vs API Key、role_type、claim
- **[Distribution Methods](concepts/distribution-methods.md)** - CDN vs npm（BYOP）

**功能：**
- **[Annotation Tools](examples/annotations.md)** - 繪圖、螢光標示、指標工具
- **[Privacy Masking](examples/privacy-masking.md)** - 對客服隱藏敏感欄位
- **[Remote Assist](examples/remote-assist.md)** - 客服可以捲動客戶的頁面
- **[Multi-Tab Persistence](examples/multi-tab-persistence.md)** - Session 跨分頁持續
- **[BYOP Mode](examples/byop-custom-pin.md)** - 搭配 npm 整合的 Bring Your Own PIN

**疑難排解：**
- **[Common Issues](troubleshooting/common-issues.md)** - 快速診斷和解法
- **[Error Codes](troubleshooting/error-codes.md)** - 完整的錯誤參考
- **[CORS and CSP](troubleshooting/cors-csp.md)** - 跨來源和安全政策設定
- **[Browser Compatibility](troubleshooting/browser-compatibility.md)** - 支援的瀏覽器和限制
- **[5-Minute Runbook](RUNBOOK.md)** - 深入除錯之前的快速 preflight 檢查

**參考：**
- **[API Reference](references/api-reference.md)** - 完整的 SDK 方法和事件
- **[Settings Reference](references/settings-reference.md)** - 所有初始化設定
- **Integrated Index** - 見本檔案下方的區段

## SDK 概覽

Zoom Cobrowse SDK 是一個 JavaScript 函式庫，提供：

- **即時共同瀏覽**：客服能即時看到客戶的瀏覽器活動
- **以 PIN 碼為基礎的 session**：用安全的 6 位數 PIN 碼連接客戶和客服
- **標註工具**：繪圖、螢光標示、消失筆、矩形、顏色選擇器
- **隱私遮罩**：用 CSS selector 遮蔽敏感的表單欄位
- **遠端協助**：客服可以捲動客戶的頁面（需經同意）
- **多分頁持續性**：客戶開新分頁時 session 會繼續
- **自動重新連線**：session 能從頁面重新整理中恢復（2 分鐘的時間窗口）
- **Session 事件**：session 狀態變化的即時事件
- **需要 HTTPS**：安全連線（HTTP 只在 loopback／本地開發主機上可用）
- **不需要外掛**：純 JavaScript，不需要瀏覽器擴充功能

## 雙角色架構

Cobrowse 有**兩個不同的角色**，各自有不同的整合模式：

| 角色 | role_type | 整合方式 | 需要 JWT | 用途 |
|------|-----------|-------------|--------------|---------|
| **Customer** | 1 | 網站整合（CDN 或 npm） | 是 | 分享自己瀏覽器 session 的使用者 |
| **Agent** | 2 | Iframe（CDN）或 npm（僅 BYOP） | 是 | 查看／協助客戶的客服人員 |

**重點**：客戶和客服用**不同的整合方式**，但用同一個 JWT 認證模式。

## 先讀這段（關鍵）

做客戶／客服的 demo 時，把客戶端 SDK 事件 `pincode_updated` 給出的 PIN 碼，當作唯一對使用者顯示的 PIN 碼。

- 在 UI 裡顯示一個有清楚標示的值（例如 **Support PIN**）。
- 客服加入時用同一個 PIN 碼。
- 不要把後端預先啟動紀錄裡暫時的／除錯用的 PIN 碼暴露給使用者。

如果忽略這些規則，客服台常常會失敗，出現 `Pincode is not found` / 代碼 `30308`。

### 典型的正式環境流程（最常見）

這是大多數團隊最先實作的流程，也是使用者在 demo 中通常期待的：

1. **客戶先開始 session**（`role_type=1`）
   - 後端建立／記錄 session
   - 後端回傳客戶的 JWT
   - 客戶端 SDK 啟動並取得一個 PIN 碼
2. **客服第二個加入**（`role_type=2`）
   - 客服輸入客戶的 PIN 碼
   - 後端驗證 PIN 碼和 session 狀態
   - 後端回傳客服的 JWT
   - 客服開啟 Zoom 代管的客服台 iframe（BYOP 時則是自訂的 npm 客服 UI）

如果 demo 只有一個通用的「session」使用者，對真正的 cobrowse 運作來說就是不完整的。

## 先決條件

### 平台需求

- **支援的瀏覽器**：
  - Chrome 80+ ✓
  - Firefox 78+ ✓
  - Safari 14+ ✓
  - Edge 80+ ✓
  - Internet Explorer ✗（不支援）

- **網路需求**：
  - 需要 HTTPS（HTTP 只在 loopback／本地開發主機上可用）
  - 允許對 `*.zoom.us` 的跨來源請求
  - CSP header 必須允許 Zoom 網域（見 [CORS and CSP guide](troubleshooting/cors-csp.md)）

- **第三方 Cookie**：
  - 必須啟用第三方 cookie，重新整理後才能重新連線
  - 隱私模式可能會限制某些功能

### Zoom 帳號需求

1. 有 SDK Universal Credit 的 **Zoom Workplace 帳號**
2. 在 Zoom Marketplace 建立的 **Video SDK App**
3. 從該 app 的 Cobrowse 分頁取得的 **Cobrowse SDK 憑證**

**注意**：Cobrowse SDK 是 **Video SDK 的一項功能**（不是獨立的產品）。

### 憑證概覽

你會從 Zoom Marketplace → Video SDK App → Cobrowse 分頁拿到 **4 組憑證**：

| 憑證 | 類型 | 用途 | 可以公開嗎？ |
|------------|------|----------|----------------|
| **SDK Key** | 公開 | CDN URL、JWT `app_key` claim | ✓ 可以（client 端） |
| **SDK Secret** | 私密 | 簽署 JWT | ✗ 不行（只能在伺服器端） |
| **API Key** | 私密 | REST API 呼叫（選用） | ✗ 不行（只能在伺服器端） |
| **API Secret** | 私密 | REST API 呼叫（選用） | ✗ 不行（只能在伺服器端） |

**關鍵**：SDK Key 是**公開的**（嵌在 CDN URL 裡），但 SDK Secret **絕對不能**在 client 端暴露。

## 快速開始

### Step 1：取得 SDK 憑證

1. 前往 [Zoom Marketplace](https://marketplace.zoom.us/)
2. 打開你的 **Video SDK App**（或建立一個）
3. 前往 **Cobrowse** 分頁
4. 複製你的憑證：
   - SDK Key
   - SDK Secret
   - API Key（選用）
   - API Secret（選用）

### Step 2：設定 Token 伺服器

部署一個伺服器端 endpoint 來產生 JWT。使用官方範例：

```bash
git clone https://github.com/zoom/cobrowsesdk-auth-endpoint-sample.git
cd cobrowsesdk-auth-endpoint-sample
npm install

# Create .env file
cat > .env << EOF
ZOOM_SDK_KEY=your_sdk_key_here
ZOOM_SDK_SECRET=your_sdk_secret_here
PORT=4000
EOF

npm start
```

**Token endpoint：**
```javascript
// POST https://YOUR_TOKEN_SERVICE_BASE_URL
{
  "role": 1,           // 1 = customer, 2 = agent
  "userId": "user123",
  "userName": "John Doe"
}

// Response
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Step 3：客戶端整合（CDN）

```html
<!DOCTYPE html>
<html>
<head>
  <title>Customer - Cobrowse Demo</title>
  <script type="module">
    const ZOOM_SDK_KEY = 'YOUR_SDK_KEY';
    
    // Load SDK from CDN
    (function(r, a, b, f, c, d) {
      r[f] = r[f] || { init: function() { r.ZoomCobrowseSDKInitArgs = arguments }};
      var fragment = a.createDocumentFragment();
      function loadJs(url) {
        c = a.createElement(b);
        d = a.getElementsByTagName(b)[0];
        c["async"] = false;
        c.src = url;
        fragment.appendChild(c);
      }
      loadJs(`https://us01-zcb.zoom.us/static/resource/sdk/${ZOOM_SDK_KEY}/js/2.13.2`);
      d.parentNode.insertBefore(fragment, d);
    })(window, document, "script", "ZoomCobrowseSDK");
  </script>
</head>
<body>
  <h1>Customer Support</h1>
  <button id="cobrowse-btn" disabled>Loading...</button>
  
  <!-- Sensitive fields - will be masked from agent -->
  <label>SSN: <input type="text" class="pii-mask" placeholder="XXX-XX-XXXX"></label>
  <label>Credit Card: <input type="text" class="pii-mask" placeholder="XXXX-XXXX-XXXX-XXXX"></label>
  
  <script type="module">
    let sessionRef = null;
    
    const settings = {
      allowAgentAnnotation: true,
      allowCustomerAnnotation: true,
      piiMask: {
        maskCssSelectors: ".pii-mask",
        maskType: "custom_input"
      }
    };
    
    ZoomCobrowseSDK.init(settings, function({ success, session, error }) {
      if (success) {
        sessionRef = session;
        
        // Listen for PIN code
        session.on("pincode_updated", (payload) => {
          console.log("PIN Code:", payload.pincode);
          // IMPORTANT: this is the PIN agent should use
          alert(`Share this PIN with agent: ${payload.pincode}`);
        });
        
        // Listen for session events
        session.on("session_started", () => console.log("Session started"));
        session.on("agent_joined", () => console.log("Agent joined"));
        session.on("agent_left", () => console.log("Agent left"));
        session.on("session_ended", () => console.log("Session ended"));
        
        document.getElementById("cobrowse-btn").disabled = false;
        document.getElementById("cobrowse-btn").innerText = "Start Cobrowse Session";
      } else {
        console.error("SDK init failed:", error);
      }
    });
    
    document.getElementById("cobrowse-btn").addEventListener("click", async () => {
      // Fetch JWT from your server
      const response = await fetch("https://YOUR_TOKEN_SERVICE_BASE_URL", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: 1,
          userId: "customer_" + Date.now(),
          userName: "Customer"
        })
      });
      const { token } = await response.json();
      
      // Start cobrowse session
      sessionRef.start({ sdkToken: token });
    });
  </script>
</body>
</html>
```

### Step 4：客服端整合（Iframe）

```html
<!DOCTYPE html>
<html>
<head>
  <title>Agent Portal</title>
</head>
<body>
  <h1>Agent Portal</h1>
  <iframe 
    id="agent-iframe"
    width="1024" 
    height="768"
    allow="autoplay *; camera *; microphone *; display-capture *; geolocation *;"
  ></iframe>
  
  <script>
    async function connectAgent() {
      // Fetch JWT from your server
      const response = await fetch("https://YOUR_TOKEN_SERVICE_BASE_URL", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: 2,
          userId: "agent_" + Date.now(),
          userName: "Support Agent"
        })
      });
      const { token } = await response.json();
      
      // Load Zoom agent portal
      const iframe = document.getElementById("agent-iframe");
      iframe.src = `https://us01-zcb.zoom.us/sdkapi/zcb/frame-templates/desk?access_token=${token}`;
    }
    
    connectAgent();
  </script>
</body>
</html>
```

### Step 5：測試整合

1. 開**兩個獨立的瀏覽器**（或無痕視窗 + 一般視窗）
2. **客戶瀏覽器**：打開客戶頁面，點「Start Cobrowse Session」
3. **客戶瀏覽器**：記下顯示的 6 位數 PIN 碼
4. **客服瀏覽器**：打開客服頁面，輸入 PIN 碼
5. **兩個瀏覽器**：session 連線，客服能看到客戶的頁面
6. **測試功能**：標註、資料遮罩、遠端協助

## 主要功能

### 1. 標註工具

客戶和客服都可以在共享的畫面上繪圖：

```javascript
const settings = {
  allowAgentAnnotation: true,      // Agent can draw
  allowCustomerAnnotation: true    // Customer can draw
};
```

**可用的工具**：
- 筆（持久）
- 消失筆（4 秒後消失）
- 矩形
- 顏色選擇器
- 橡皮擦
- 復原／重做

### 2. 隱私遮罩

用 CSS selector 對客服隱藏敏感欄位：

```javascript
const settings = {
  piiMask: {
    maskType: "custom_input",           // Mask specific fields
    maskCssSelectors: ".pii-mask, #ssn", // CSS selectors
    maskHTMLAttributes: "data-sensitive=true" // HTML attributes
  }
};
```

**支援的遮罩**：
- 文字節點 ✓
- 表單輸入 ✓
- Select 元素 ✓
- 圖片 ✗（不支援）
- 連結 ✗（不支援）

### 3. 遠端協助

客服可以捲動客戶的頁面：

```javascript
const settings = {
  remoteAssist: {
    enable: true,
    enableCustomerConsent: true,        // Customer must approve
    remoteAssistTypes: ['scroll_page'], // Only scroll supported
    requireStopConfirmation: false      // Confirmation when stopping
  }
};
```

### 4. 多分頁 Session 持續性

客戶開新分頁時，session 會繼續：

```javascript
const settings = {
  multiTabSessionPersistence: {
    enable: true,
    stateCookieKey: '$$ZCB_SESSION$$'  // Cookie key (base64 encoded)
  }
};
```

## Session 生命週期

### 客戶流程

1. **載入 SDK** → CDN 腳本載入 `ZoomCobrowseSDK`
2. **初始化** → `ZoomCobrowseSDK.init(settings, callback)`
3. **取得 JWT** → 向你的伺服器請求 token（role_type=1）
4. **開始 Session** → `session.start({ sdkToken })`
5. **產生 PIN 碼** → 觸發 `pincode_updated` 事件
6. **分享 PIN 碼** → 客戶把 6 位數 PIN 碼給客服
7. **客服加入** → 觸發 `agent_joined` 事件
8. **Session 啟用** → 開始即時同步
9. **結束 Session** → `session.end()` 或客服離開

### 客服流程

1. **取得 JWT** → 向你的伺服器請求 token（role_type=2）
2. **載入 Iframe** → 帶著 token 指向 Zoom 客服入口
3. **輸入 PIN 碼** → 客服輸入客戶的 6 位數 PIN 碼
4. **連線** → 觸發 `session_joined` 事件
5. **查看 Session** → 客服看到客戶的瀏覽器
6. **使用工具** → 標註、遠端協助、縮放
7. **離開 Session** → 點「Leave Cobrowse」按鈕

### Session 恢復（自動重新連線）

當客戶重新整理頁面時：

```javascript
ZoomCobrowseSDK.init(settings, function({ success, session, error }) {
  if (success) {
    const sessionInfo = session.getSessionInfo();
    
    // Check if session is recoverable
    if (sessionInfo.sessionStatus === 'session_recoverable') {
      session.join();  // Auto-rejoin previous session
    } else {
      // Start new session
      session.start({ sdkToken });
    }
  }
});
```

**恢復時間窗口**：2 分鐘。超過 2 分鐘，session 就會結束。

## 關鍵陷阱與最佳實務

### ⚠️ 關鍵：SDK Secret 必須留在伺服器端

**問題**：開發者常常不小心把 SDK Secret 嵌進前端程式碼。

**解法**：
- ✓ **SDK Key** → 可以公開（嵌在 CDN URL 裡）
- ✗ **SDK Secret** → 絕對不能公開（只在伺服器端用來簽署 JWT）

```javascript
// ❌ WRONG - Secret exposed in frontend
const jwt = signJWT(payload, 'YOUR_SDK_SECRET');  // Security risk!

// ✅ CORRECT - Secret stays on server
const response = await fetch('/api/token', {
  method: 'POST',
  body: JSON.stringify({ role: 1, userId, userName })
});
const { token } = await response.json();
```

### SDK Key vs API Key（用途不同！）

| 憑證 | 用途 | JWT Claim |
|------------|----------|-----------|
| **SDK Key** | CDN URL、JWT `app_key` | `app_key: "SDK_KEY"` |
| **API Key** | REST API 呼叫（選用） | 不用在 JWT 裡 |

**常見錯誤**：在 JWT 的 `app_key` claim 裡用了 API Key，而不是 SDK Key。

### Session 限制

| 限制 | 值 | 發生什麼事 |
|-------|-------|--------------|
| 每個 session 的客戶數 | 1 | 錯誤 1012：`SESSION_CUSTOMER_COUNT_LIMIT` |
| 每個 session 的客服數 | 5 | 錯誤 1013：`SESSION_AGENT_COUNT_LIMIT` |
| 每個瀏覽器的活躍 session 數 | 1 | 錯誤 1004：`SESSION_COUNT_LIMIT` |
| PIN 碼長度 | 最多 10 個字元 | 錯誤 1008：`SESSION_PIN_INVALID_FORMAT` |

### Session 逾時行為

| 事件 | 逾時 | 發生什麼事 |
|-------|---------|--------------|
| 客服等待客戶 | 3 分鐘 | Session 自動結束 |
| 頁面重新整理後的重新連線 | 2 分鐘 | 沒重新連上就結束 session |
| 重新連線嘗試 | 最多 2 次 | 失敗 2 次後 session 結束 |

### HTTPS 需求

**問題**：SDK 在 HTTP 網站上載入不了。

**解法**：
- 正式環境：用 HTTPS ✓
- 開發環境：本地 HTTP 測試時用 loopback 主機 ✓
- 開發環境：如果需要，用本地 HTTPS endpoint 搭配受信任／自簽的憑證 ✓

### 需要第三方 Cookie

**問題**：重新整理後的重新連線沒作用。

**解法**：在瀏覽器設定裡啟用第三方 cookie。

**受影響的情境**：
- 瀏覽器隱私模式
- 啟用了「Prevent cross-site tracking」的 Safari
- 啟用了「Block third-party cookies」的 Chrome

### 發布方式的混淆

| 方式 | 使用情境 | 客服端整合 | 是否需要 BYOP |
|--------|----------|-------------------|---------------|
| **CDN** | 大多數使用情境 | Zoom 代管的 iframe | 否（自動產生 PIN 碼） |
| **npm** | 自訂客服 UI、完整掌控 | 自訂的 npm 整合 | 是（必要） |

**重點**：如果你想用 **npm** 整合，就**必須**使用 BYOP（Bring Your Own PIN）模式。

### 跨來源 Iframe 的處理

**問題**：Cobrowse 在跨來源的 iframe 裡不能用。

**解法**：把 SDK 片段注入到跨來源的 iframe 裡：

```html
<script>
const ZOOM_SDK_KEY = "YOUR_SDK_KEY_HERE";

(function(r,a,b,f,c,d){r[f]=r[f]||{init:function(){r.ZoomCobrowseSDKInitArgs=arguments}};
var fragment=a.createDocumentFragment();function loadJs(url) {c=a.createElement(b);d=a.getElementsByTagName(b)[0];c.async=false;c.src=url;fragment.appendChild(c);};
loadJs('https://us01-zcb.zoom.us/static/resource/sdk/${ZOOM_SDK_KEY}/js');d.parentNode.insertBefore(fragment,d);})(window,document,'script','ZoomCobrowseSDK');
</script>
```

**同源的 iframe**：不需要額外設定。

## 已知限制

### 同步限制

**不會同步**：
- HTML5 Canvas 元素
- WebGL 內容
- Audio 和 Video 元素
- Shadow DOM
- 用 Canvas 渲染的 PDF
- Web Components

**部分同步**：
- 下拉選單（只有選取的結果）
- 日期選擇器（只有選取的結果）
- 顏色選擇器（只有選取的結果）

### 渲染限制

- 高解析度圖片可能會被壓縮
- 不同的螢幕尺寸可能造成 CSS media query 的差異
- 跨來源的圖片可能無法渲染（CORS 限制）
- 跨來源的字型可能無法渲染（CORS 限制）

### 遮罩限制

**支援**：
- 文字節點 ✓
- 表單輸入 ✓
- Select 元素 ✓

**不支援**：
- `<img>` 元素 ✗
- 連結 ✗

## 完整文件庫

這個 skill 包含依類別整理的完整指南：

### 核心概念
- **[Two Roles Pattern](concepts/two-roles-pattern.md)** - 客戶 vs 客服的架構
- **[Session Lifecycle](concepts/session-lifecycle.md)** - 從開始到結束的完整流程
- **[JWT Authentication](concepts/jwt-authentication.md)** - Token 結構與簽署
- **[Distribution Methods](concepts/distribution-methods.md)** - CDN vs npm（BYOP）

### 範例
- **[Customer Integration](examples/customer-integration.md)** - 完整的客戶端設定
- **[Agent Integration](examples/agent-integration.md)** - Iframe 和 npm 的客服端設定
- **[Annotations](examples/annotations.md)** - 繪圖工具設定
- **[Privacy Masking](examples/privacy-masking.md)** - 欄位遮罩模式
- **[Remote Assist](examples/remote-assist.md)** - 客服控制頁面
- **[Multi-Tab Persistence](examples/multi-tab-persistence.md)** - 跨分頁的 session
- **[BYOP Custom PIN](examples/byop-custom-pin.md)** - 自訂 PIN 碼

### 參考
- **[API Reference](references/api-reference.md)** - 完整的 SDK 方法和事件
- **[Settings Reference](references/settings-reference.md)** - 所有初始化設定
- **[Error Codes](references/error-codes.md)** - 完整的錯誤參考
- **[Session Events](references/session-events.md)** - 所有事件類型

### 疑難排解
- **[Common Issues](troubleshooting/common-issues.md)** - 快速診斷
- **[Error Codes](troubleshooting/error-codes.md)** - 錯誤碼參考
- **[CORS and CSP](troubleshooting/cors-csp.md)** - 跨來源設定
- **[Browser Compatibility](troubleshooting/browser-compatibility.md)** - 瀏覽器支援

## 資源

- **官方文件**：https://developers.zoom.us/docs/cobrowse-sdk/
- **API 參考**：https://marketplacefront.zoom.us/sdk/cobrowse/
- **Quickstart Repo**：https://github.com/zoom/CobrowseSDK-Quickstart
- **Auth Endpoint 範例**：https://github.com/zoom/cobrowsesdk-auth-endpoint-sample
- **開發者論壇**：https://devforum.zoom.us/
- **開發者部落格**：https://developers.zoom.us/blog/?category=zoom-cobrowse-sdk

---

**需要協助？** 先看下面的 Integrated Index 區段，裡面有完整的導覽。

---

## Integrated Index

_這個區段是從 `SKILL.md` 搬過來的。_

**Cobrowse SDK 所有文件的完整導覽。**

## 開始上手（從這裡開始！）

如果你剛接觸 Zoom Cobrowse SDK，照這條學習路徑走：

1. **[SKILL.md](SKILL.md)** - 主要概覽和快速開始
2. **[5-Minute Runbook](RUNBOOK.md)** - 針對常見失敗的 preflight 檢查
3. **[Get Started Guide](get-started.md)** - 從憑證到第一次 session 的逐步設定
4. **[Session Lifecycle](concepts/session-lifecycle.md)** - 理解完整的客戶和客服流程
5. **[Customer Integration](examples/customer-integration.md)** - 把 SDK 整合進你的網站
6. **[Agent Integration](examples/agent-integration.md)** - 設定客服入口

## 核心概念

你需要理解的基礎概念：

- **[Two Roles Pattern](concepts/two-roles-pattern.md)** - 客戶（role_type=1）vs 客服（role_type=2）的架構
- **[Session Lifecycle](concepts/session-lifecycle.md)** - 完整流程：init → start → PIN → connect → end
- **[JWT Authentication](concepts/jwt-authentication.md)** - Token 結構、簽署、SDK Key vs API Key
- **[Distribution Methods](concepts/distribution-methods.md)** - CDN vs npm（BYOP 模式）

## 範例與模式

常見情境的完整可運作範例：

### Session 管理
- **[Customer Integration](examples/customer-integration.md)** - 完整的客戶端實作（CDN 和 npm）
- **[Agent Integration](examples/agent-integration.md)** - Iframe 和 npm 的客服端設定模式
- **[Session Events](examples/session-events.md)** - 處理所有 session 生命週期事件
- **[Auto-Reconnection](examples/auto-reconnection.md)** - 頁面重新整理與 session 恢復

### 功能
- **[Annotation Tools](examples/annotations.md)** - 啟用繪圖、螢光標示、消失筆
- **[Privacy Masking](examples/privacy-masking.md)** - 用 CSS selector 遮蔽敏感欄位
- **[Remote Assist](examples/remote-assist.md)** - 客服可以捲動客戶的頁面
- **[Multi-Tab Persistence](examples/multi-tab-persistence.md)** - Session 跨瀏覽器分頁持續
- **[BYOP Custom PIN](examples/byop-custom-pin.md)** - 搭配 npm 整合的 Bring Your Own PIN

## 參考

完整的 API 和設定參考：

### SDK 參考
- **[API Reference](references/api-reference.md)** - 所有 SDK 方法和介面
  - ZoomCobrowseSDK.init()
  - session.start()
  - session.join()
  - session.end()
  - session.on()
  - session.getSessionInfo()
  
- **[Settings Reference](references/settings-reference.md)** - 所有初始化設定
  - allowAgentAnnotation
  - allowCustomerAnnotation
  - piiMask
  - remoteAssist
  - multiTabSessionPersistence

- **[Session Events Reference](references/session-events.md)** - 所有事件類型
  - pincode_updated
  - session_started
  - session_ended
  - agent_joined
  - agent_left
  - session_error
  - session_reconnecting
  - remote_assist_started
  - remote_assist_stopped

### 錯誤參考
- **[Error Codes](references/error-codes.md)** - 完整的錯誤碼參考
  - 1001-1017：Session 錯誤
  - 2001：Token 錯誤
  - 9999：服務錯誤

### 官方文件
- **[Get Started](references/get-started.md)** - 官方 get started 文件（爬取的）
- **[Features](references/features.md)** - 官方功能文件（爬取的）
- **[Authorization](references/authorization.md)** - 官方 JWT 授權文件（爬取的）
- **[API Documentation](references/api.md)** - 爬取的 API 參考文件

## 疑難排解

快速診斷與常見問題的解決：

- **[Common Issues](troubleshooting/common-issues.md)** - 常見問題的快速修正
  - SDK 沒載入
  - Token 產生失敗
  - 客服連不上
  - 欄位沒被遮蔽
  - 重新整理後 session 沒有重新連線

- **[Error Codes](troubleshooting/error-codes.md)** - 錯誤碼查找與解法
  - Session 開始／加入失敗（1001、1011、1016）
  - Session 數量限制錯誤（1002、1004、1012、1013、1015）
  - PIN 碼錯誤（1006、1008、1009、1010）
  - Token 錯誤（2001）

- **[CORS and CSP](troubleshooting/cors-csp.md)** - 跨來源和 Content Security Policy 設定
  - Access-Control-Allow-Origin header
  - Content-Security-Policy header
  - 跨來源 iframe 的處理
  - 同源 iframe 的處理

- **[Browser Compatibility](troubleshooting/browser-compatibility.md)** - 瀏覽器需求與限制
  - 支援的瀏覽器（Chrome 80+、Firefox 78+、Safari 14+、Edge 80+）
  - 不支援 Internet Explorer
  - 隱私模式的限制
  - 第三方 cookie 的需求

## 依使用情境

依你想做的事找文件：

### 我想要...

**第一次設定 cobrowse：**
- [Get Started Guide](get-started.md)
- [JWT Authentication](concepts/jwt-authentication.md)
- [Customer Integration](examples/customer-integration.md)
- [Agent Integration](examples/agent-integration.md)

**加入標註工具：**
- [Annotation Tools Example](examples/annotations.md)
- [Settings Reference - allowAgentAnnotation](references/settings-reference.md#allowa gentannotation)
- [Settings Reference - allowCustomerAnnotation](references/settings-reference.md#allowcustomerannotation)

**對客服隱藏敏感資料：**
- [Privacy Masking Example](examples/privacy-masking.md)
- [Settings Reference - piiMask](references/settings-reference.md#piimask)

**讓客服控制客戶的頁面：**
- [Remote Assist Example](examples/remote-assist.md)
- [Settings Reference - remoteAssist](references/settings-reference.md#remoteassist)

**使用自訂 PIN 碼：**
- [BYOP Custom PIN Example](examples/byop-custom-pin.md)
- [JWT Authentication - enable_byop](concepts/jwt-authentication.md#enable-byop)

**處理頁面重新整理：**
- [Auto-Reconnection Example](examples/auto-reconnection.md)
- [Session Lifecycle - Recovery](concepts/session-lifecycle.md#session-recovery)

**用 npm 整合（不用 CDN）：**
- [BYOP Custom PIN Example](examples/byop-custom-pin.md)
- [Distribution Methods](concepts/distribution-methods.md#npm-integration)

**除錯 session 連線問題：**
- [Common Issues](troubleshooting/common-issues.md)
- [Error Codes](troubleshooting/error-codes.md)
- [Session Events - session_error](examples/session-events.md#session-error)

**設定 CORS 和 CSP header：**
- [CORS and CSP Guide](troubleshooting/cors-csp.md)
- [Browser Compatibility](troubleshooting/browser-compatibility.md)

## 依錯誤碼

快速查找錯誤碼的解法：

### Session 錯誤
- **1001**（SESSION_START_FAILED）→ [Error Codes](troubleshooting/error-codes.md#1001-session-start-failed)
- **1002**（SESSION_CONNECTING_IN_PROGRESS）→ [Error Codes](troubleshooting/error-codes.md#1002-session-connecting-in-progress)
- **1004**（SESSION_COUNT_LIMIT）→ [Error Codes](troubleshooting/error-codes.md#1004-session-count-limit)
- **1011**（SESSION_JOIN_FAILED）→ [Error Codes](troubleshooting/error-codes.md#1011-session-join-failed)
- **1012**（SESSION_CUSTOMER_COUNT_LIMIT）→ [Error Codes](troubleshooting/error-codes.md#1012-session-customer-count-limit)
- **1013**（SESSION_AGENT_COUNT_LIMIT）→ [Error Codes](troubleshooting/error-codes.md#1013-session-agent-count-limit)
- **1015**（SESSION_DUPLICATE_USER）→ [Error Codes](troubleshooting/error-codes.md#1015-session-duplicate-user)
- **1016**（NETWORK_ERROR）→ [Error Codes](troubleshooting/error-codes.md#1016-network-error)
- **1017**（SESSION_CANCELING_IN_PROGRESS）→ [Error Codes](troubleshooting/error-codes.md#1017-session-canceling-in-progress)

### PIN 碼錯誤
- **1006**（SESSION_JOIN_PIN_NOT_FOUND）→ [Error Codes](troubleshooting/error-codes.md#1006-session-join-pin-not-found)
- **1008**（SESSION_PIN_INVALID_FORMAT）→ [Error Codes](troubleshooting/error-codes.md#1008-session-pin-invalid-format)
- **1009**（SESSION_START_PIN_REQUIRED）→ [Error Codes](troubleshooting/error-codes.md#1009-session-start-pin-required)
- **1010**（SESSION_START_PIN_CONFLICT）→ [Error Codes](troubleshooting/error-codes.md#1010-session-start-pin-conflict)

### 認證錯誤
- **2001**（TOKEN_INVALID）→ [Error Codes](troubleshooting/error-codes.md#2001-token-invalid)

### 服務錯誤
- **9999**（UNDEFINED）→ [Error Codes](troubleshooting/error-codes.md#9999-undefined)

## 官方資源

外部的文件和範例：

- **官方文件**：https://developers.zoom.us/docs/cobrowse-sdk/
- **API 參考**：https://marketplacefront.zoom.us/sdk/cobrowse/
- **Quickstart Repo**：https://github.com/zoom/CobrowseSDK-Quickstart
- **Auth Endpoint 範例**：https://github.com/zoom/cobrowsesdk-auth-endpoint-sample
- **開發者論壇**：https://devforum.zoom.us/
- **開發者部落格**：https://developers.zoom.us/blog/?category=zoom-cobrowse-sdk

## 文件結構

```
cobrowse-sdk/
├── SKILL.md                    # Main skill entry point
├── SKILL.md                    # This file - complete navigation
├── get-started.md              # Step-by-step setup guide
│
├── concepts/                   # Core concepts
│   ├── two-roles-pattern.md
│   ├── session-lifecycle.md
│   ├── jwt-authentication.md
│   └── distribution-methods.md
│
├── examples/                   # Working examples
│   ├── customer-integration.md
│   ├── agent-integration.md
│   ├── annotations.md
│   ├── privacy-masking.md
│   ├── remote-assist.md
│   ├── multi-tab-persistence.md
│   ├── byop-custom-pin.md
│   ├── session-events.md
│   └── auto-reconnection.md
│
├── references/                 # API and config references
│   ├── api-reference.md        # SDK methods
│   ├── settings-reference.md   # Init settings
│   ├── session-events.md       # Event types
│   ├── error-codes.md          # Error reference
│   ├── get-started.md          # Official docs (crawled)
│   ├── features.md             # Official docs (crawled)
│   ├── authorization.md        # Official docs (crawled)
│   └── api.md                  # API docs (crawled)
│
└── troubleshooting/            # Problem resolution
    ├── common-issues.md
    ├── error-codes.md
    ├── cors-csp.md
    └── browser-compatibility.md
```

## 搜尋提示

**依關鍵字找：**
- 「annotation」→ [Annotation Tools](examples/annotations.md)
- 「mask」或「privacy」→ [Privacy Masking](examples/privacy-masking.md)
- 「PIN」或「custom PIN」→ [BYOP Custom PIN](examples/byop-custom-pin.md)
- 「JWT」或「token」→ [JWT Authentication](concepts/jwt-authentication.md)
- 「error」→ [Error Codes](troubleshooting/error-codes.md)
- 「CORS」或「CSP」→ [CORS and CSP](troubleshooting/cors-csp.md)
- 「iframe」→ [Agent Integration](examples/agent-integration.md)
- 「npm」→ [Distribution Methods](concepts/distribution-methods.md)、[BYOP](examples/byop-custom-pin.md)
- 「refresh」或「reconnect」→ [Auto-Reconnection](examples/auto-reconnection.md)
- 「agent」→ [Agent Integration](examples/agent-integration.md)、[Two Roles Pattern](concepts/two-roles-pattern.md)
- 「customer」→ [Customer Integration](examples/customer-integration.md)、[Two Roles Pattern](concepts/two-roles-pattern.md)

---

**找不到你需要的？** 請看[官方文件](https://developers.zoom.us/docs/cobrowse-sdk/)，或到[開發者論壇](https://devforum.zoom.us/)問。

## 環境變數

- 標準化的 `.env` key，以及各個值要去哪裡找，請看 [references/environment-variables.md](references/environment-variables.md)。
