---
name: google-apps-script
description: "為 Sheets 和 Workspace 打造 Google Apps Script 自動化。包含自訂選單、trigger（onEdit / 定時 / 表單送出）、對話框、側邊欄、批次寄信、PDF 匯出、外部 API。只要使用者想自動化 Google Sheet、做 Sheets 選單 / 側邊欄 / 對話框、想從 email 或 webhook 寫入 Sheets 的某一列、想排程 Sheets 工作流程，或問「這個在 Sheets 裡要怎麼寫 script」，就用這個 skill。"
compatibility: claude-code-only
---

# Google Apps Script

為 Google Sheets 和 Workspace 應用程式打造自動化 script。Script 在 Google 的基礎設施上於伺服器端執行，免費額度相當寬鬆。

## 你會產出什麼

- 貼到 Extensions > Apps Script 的 Apps Script 程式碼
- 自訂選單、對話框、側邊欄
- 自動化 trigger（編輯時、定時、表單送出）
- Email 通知、PDF 匯出、API 整合

## 工作流程

### 步驟 1：了解要自動化什麼

問使用者想自動化什麼。常見情境：
- 帶有動作的自訂選單（產生報表、處理資料）
- 自動觸發的行為（編輯時、表單送出時、排程）
- 用來輸入資料的側邊欄 app
- 根據試算表資料寄 email 通知
- PDF 匯出與寄送

### 步驟 2：產生 script

照下面的結構範本寫。每個 script 都要有標頭註解、放在最上面的設定常數，以及用來建立選單的 `onOpen()`。

### 步驟 3：提供安裝說明

所有 script 的安裝方式都一樣：
1. 打開 Google Sheet
2. **Extensions > Apps Script**
3. 刪掉編輯器裡原有的程式碼
4. 貼上 script
5. 按 **Save**
6. 關掉 Apps Script 分頁
7. **重新載入試算表**（onOpen 是在頁面載入時執行）

### 步驟 4：第一次授權

每個使用者第一次執行時都會看到 Google OAuth 同意畫面。對於未驗證的 script（大部分內部 script 都是），使用者必須點：

**Advanced > Go to [Project Name] (unsafe) > Allow**

這個步驟每個使用者只需做一次。輸出時要提醒使用者這件事。

---

## Script 結構範本

每個 script 都要照這個模式：

```javascript
/**
 * [Project Name] - [Brief Description]
 *
 * [What it does, key features]
 *
 * INSTALL: Extensions > Apps Script > paste this > Save > Reload sheet
 */

// --- CONFIGURATION ---
const SOME_SETTING = 'value';

// --- MENU SETUP ---
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('My Menu')
    .addItem('Do Something', 'myFunction')
    .addSeparator()
    .addSubMenu(ui.createMenu('More Options')
      .addItem('Option A', 'optionA'))
    .addToUi();
}

// --- FUNCTIONS ---
function myFunction() {
  // Implementation
}
```

---

## 關鍵規則

### 公開 vs 私有函式

名稱結尾是 `_`（底線）的函式是**私有**的，**不能**從 client 端 HTML 透過 `google.script.run` 呼叫。這是靜默失敗：呼叫就是沒反應，也不會報錯。

```javascript
// WRONG - dialog can't call this, fails silently
function doWork_() { return 'done'; }

// RIGHT - dialog can call this
function doWork() { return 'done'; }
```

**同樣適用於**：選單項目所參照的函式，必須是以字串表示的公開函式名稱。

### 批次操作（對效能至關重要）

資料要整批讀寫，絕對不要一格一格來。差距是 70 倍。

```javascript
// SLOW (70 seconds on 100x100) - reads one cell at a time
for (let i = 1; i <= 100; i++) {
  const val = sheet.getRange(i, 1).getValue();
}

// FAST (1 second) - reads all at once
const allData = sheet.getRange(1, 1, 100, 1).getValues();
for (const row of allData) {
  const val = row[0];
}
```

大量讀寫一律用 `getRange().getValues()` / `setValues()`。

### V8 Runtime

V8 是**唯一**的 runtime（Rhino 已在 2026 年 1 月移除）。支援現代 JavaScript：`const`、`let`、arrow function、template literal、解構、class、async/generator。

**沒有**的東西（改用 Apps Script 的替代方案）：

| 缺少的 API | Apps Script 替代方案 |
|-------------|------------------------|
| `setTimeout` / `setInterval` | `Utilities.sleep(ms)`（會阻塞） |
| `fetch` | `UrlFetchApp.fetch()` |
| `FormData` | 手動組 payload |
| `URL` | 字串處理 |
| `crypto` | `Utilities.computeDigest()` / `Utilities.getUuid()` |

### Return 之前先 flush

在會修改試算表的函式 return 之前，要呼叫 `SpreadsheetApp.flush()`，從 HTML 對話框呼叫的函式尤其要這樣。沒呼叫的話，對話框顯示「Done」時，改動可能還看不到。

### Simple trigger vs Installable trigger

| 功能 | Simple（`onEdit`） | Installable |
|---------|-------------------|-------------|
| 需要授權 | 否 | 是 |
| 寄 email | 否 | 是 |
| 存取其他檔案 | 否 | 是 |
| URL fetch | 否 | 是 |
| 開對話框 | 否 | 是 |
| 以誰的身分執行 | 目前的使用者 | 建立 trigger 的人 |

輕量的反應用 simple trigger。需要寄 email、呼叫外部 API 或跨檔案存取時，用 installable trigger（透過 `ScriptApp.newTrigger()`）。

### 自訂試算表函式

在儲存格裡用 `=MY_FUNCTION()` 的函式有嚴格限制：

```javascript
/**
 * Calculates something custom.
 * @param {string} input The input value
 * @return {string} The result
 * @customfunction
 */
function MY_FUNCTION(input) {
  // Can use: basic JS, Utilities, CacheService
  // CANNOT use: MailApp, UrlFetchApp, SpreadsheetApp.getUi(), triggers
  return input.toUpperCase();
}
```

- 一定要有 `@customfunction` JSDoc 標籤
- 執行時間上限 30 秒（一般函式是 6 分鐘）
- 不能存取需要授權的服務

---

## 配額與限制

| 資源 | 免費帳號 | Google Workspace |
|----------|-------------|-----------------|
| Script 執行時間 | 每次執行 6 分鐘 | 每次執行 6 分鐘 |
| 定時 trigger 執行時間 | 30 分鐘 | 30 分鐘 |
| Trigger 每日總執行時間 | 90 分鐘 | 6 小時 |
| Trigger 總數 | 每個使用者每個 script 20 個 | 每個使用者每個 script 20 個 |
| 每天收件者數 | 100 | 1,500 |
| 每天 URL Fetch 次數 | 20,000 | 100,000 |
| Properties 儲存空間 | 500 KB | 500 KB |
| 自訂函式執行時間 | 30 秒 | 30 秒 |
| 同時執行數 | 30 | 30 |

---

## Modal 進度對話框

長時間操作時，用會自動關閉的 spinner 擋住使用者操作。任何超過幾秒的操作都適用。

**模式：選單函式 > showProgress() > 對話框呼叫動作函式 > 自動關閉**

```javascript
function showProgress(message, serverFn) {
  const html = HtmlService.createHtmlOutput(`
    <style>
      body { font-family: 'Google Sans', Arial, sans-serif; display: flex;
        flex-direction: column; align-items: center; justify-content: center;
        height: 100%; margin: 0; padding: 20px; box-sizing: border-box; }
      .spinner { width: 36px; height: 36px; border: 4px solid #e0e0e0;
        border-top: 4px solid #1a73e8; border-radius: 50%;
        animation: spin 0.8s linear infinite; margin-bottom: 16px; }
      @keyframes spin { to { transform: rotate(360deg); } }
      .message { font-size: 14px; color: #333; text-align: center; }
      .done { color: #1e8e3e; font-weight: 500; }
      .error { color: #d93025; font-weight: 500; }
    </style>
    <div class="spinner" id="spinner"></div>
    <div class="message" id="msg">${message}</div>
    <script>
      google.script.run
        .withSuccessHandler(function(r) {
          document.getElementById('spinner').style.display = 'none';
          var m = document.getElementById('msg');
          m.className = 'message done';
          m.innerText = 'Done! ' + (r || '');
          setTimeout(function() { google.script.host.close(); }, 1200);
        })
        .withFailureHandler(function(err) {
          document.getElementById('spinner').style.display = 'none';
          var m = document.getElementById('msg');
          m.className = 'message error';
          m.innerText = 'Error: ' + err.message;
          setTimeout(function() { google.script.host.close(); }, 3000);
        })
        .${serverFn}();
    </script>
  `).setWidth(320).setHeight(140);
  SpreadsheetApp.getUi().showModalDialog(html, 'Working...');
}

// Menu calls this wrapper
function menuDoWork() {
  showProgress('Processing data...', 'doTheWork');
}

// MUST be public (no underscore) for the dialog to call it
function doTheWork() {
  // ... do the work ...
  SpreadsheetApp.flush();
  return 'Processed 50 rows';  // shown in success message
}
```

---

## 常見模式

### Toast 通知

```javascript
SpreadsheetApp.getActiveSpreadsheet().toast('Operation complete!', 'Title', 5);
// Arguments: message, title, duration in seconds (-1 = until dismissed)
```

### Alert 與 Prompt 對話框

```javascript
const ui = SpreadsheetApp.getUi();

// Yes/No confirmation
const response = ui.alert('Delete this data?', 'This cannot be undone.',
  ui.ButtonSet.YES_NO);
if (response === ui.Button.YES) { /* proceed */ }

// Prompt for input
const result = ui.prompt('Enter your name:', ui.ButtonSet.OK_CANCEL);
if (result.getSelectedButton() === ui.Button.OK) {
  const name = result.getResponseText();
}
```

### 側邊欄 App

右側的 HTML 面板。用 `google.script.run` 呼叫伺服器端函式。

```javascript
function showSidebar() {
  const html = HtmlService.createHtmlOutput(`
    <h3>Quick Entry</h3>
    <select id="worker"><option>Craig</option><option>Steve</option></select>
    <input id="suburb" placeholder="Suburb">
    <button onclick="submit()">Add Job</button>
    <script>
      function submit() {
        google.script.run.withSuccessHandler(function() { alert('Added!'); })
          .addJob(document.getElementById('worker').value,
                  document.getElementById('suburb').value);
      }
    </script>
  `).setTitle('Job Entry').setWidth(300);
  SpreadsheetApp.getUi().showSidebar(html);
}

function addJob(worker, suburb) { // MUST be public (no underscore)
  SpreadsheetApp.getActiveSpreadsheet().getActiveSheet().appendRow([new Date(), worker, suburb]);
}
```

### Trigger

**onEdit（simple trigger）**：權限有限，但不需要授權：

```javascript
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() !== 'Data') return;
  if (e.range.getColumn() !== 3) return;
  // Auto-timestamp when column C is edited
  sheet.getRange(e.range.getRow(), 4).setValue(new Date());
}
```

**Installable trigger**：用 script 建立，並手動執行一次設定函式：

```javascript
function createTriggers() {
  // Time-driven: run every day at 8am
  ScriptApp.newTrigger('dailyReport')
    .timeBased().atHour(8).everyDays(1).create();

  // On edit with full permissions (can send email, fetch URLs)
  ScriptApp.newTrigger('onEditFull')
    .forSpreadsheet(SpreadsheetApp.getActive()).onEdit().create();

  // On form submit
  ScriptApp.newTrigger('onFormSubmit')
    .forSpreadsheet(SpreadsheetApp.getActive()).onFormSubmit().create();
}
```

### 從 Sheets 寄 Email

```javascript
function emailWeeklySchedule() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getRange('A2:E10').getDisplayValues();
  let body = '<h2>Weekly Schedule</h2><table border="1" cellpadding="8">';
  body += '<tr><th>Job</th><th>Suburb</th><th>Time</th><th>Price</th></tr>';
  for (const row of data) {
    if (row[0]) body += '<tr>' + row.map(c => '<td>' + c + '</td>').join('') + '</tr>';
  }
  body += '</table>';
  MailApp.sendEmail({ to: 'worker@example.com',
    subject: 'Schedule - Week ' + sheet.getName(), htmlBody: body });
}
```

### PDF 匯出

URL 的組法不直觀，匯出參數沒有官方文件：

```javascript
function exportSheetAsPdf() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const url = ss.getUrl().replace(/\/edit.*$/, '')
    + '/export?exportFormat=pdf&format=pdf&size=A4&portrait=true'
    + '&fitw=true&sheetnames=false&printtitle=false&gridlines=false'
    + '&gid=' + ss.getActiveSheet().getSheetId();
  const blob = UrlFetchApp.fetch(url, {
    headers: { 'Authorization': 'Bearer ' + ScriptApp.getOAuthToken() }
  }).getBlob().setName('report.pdf');
  MailApp.sendEmail({ to: 'boss@example.com', subject: 'Weekly Report PDF',
    body: 'Attached.', attachments: [blob] });
}
```

### 呼叫外部 API

```javascript
// GET
function fetchData() {
  const r = UrlFetchApp.fetch('https://api.example.com/data', {
    headers: { 'Authorization': 'Bearer ' + getApiKey() } });
  return JSON.parse(r.getContentText());
}

// POST (muteHttpExceptions to handle errors yourself)
function postData(payload) {
  const r = UrlFetchApp.fetch('https://api.example.com/submit', {
    method: 'post', contentType: 'application/json',
    payload: JSON.stringify(payload), muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) throw new Error('API error: ' + r.getContentText());
  return JSON.parse(r.getContentText());
}
```

### 資料驗證下拉選單

```javascript
// Dropdown from list
const rule = SpreadsheetApp.newDataValidation()
  .requireValueInList(['Option A', 'Option B', 'Option C'], true)
  .setAllowInvalid(false).setHelpText('Select an option').build();
sheet.getRange('C3:C50').setDataValidation(rule);

// Dropdown from range (e.g. a Lookups sheet)
const rule2 = SpreadsheetApp.newDataValidation()
  .requireValueInRange(ss.getSheetByName('Lookups').getRange('A1:A100')).build();
sheet.getRange('B3:B50').setDataValidation(rule2);
```

### Properties Service（持久儲存）

三種範圍：`PropertiesService.getScriptProperties()`（共用）、`.getUserProperties()`（每個使用者）、`.getDocumentProperties()`（每份試算表）。全部都用 `.setProperty(key, value)` / `.getProperty(key)`。上限 500 KB。

---

## 食譜

### 自動封存已完成的列

把狀態是「Complete」的列移到 Archive 工作表。由下往上處理，避免列索引位移。

```javascript
function archiveCompleted() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const source = ss.getSheetByName('Active');
  const archive = ss.getSheetByName('Archive');
  const data = source.getDataRange().getValues();
  const statusCol = 4; // column E (0-indexed)

  for (let i = data.length - 1; i >= 1; i--) {
    if (data[i][statusCol] === 'Complete') {
      archive.appendRow(data[i]);
      source.deleteRow(i + 1); // +1 for 1-indexed rows
    }
  }
  SpreadsheetApp.flush();
}
```

### 重複偵測與標示

模式：用 `getValues()` 讀出一欄，用物件記錄已出現過的值，並用 `setBackground('#f4cccc')` 把原始列和重複列都標示起來。所有資料用一次 `getValues()` 處理，再逐個設定背景色（分散的標示無法避免要逐個設定）。

### 批次寄信程式

關鍵模式：寄信前先檢查 `MailApp.getRemainingDailyQuota()`，每一列標記狀態，每次寄送都包在 try/catch 裡。

```javascript
function sendBatchEmails() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Recipients');
  const data = sheet.getRange('A2:C' + sheet.getLastRow()).getValues(); // Email, Name, Status
  const remaining = MailApp.getRemainingDailyQuota();
  if (remaining < data.length) {
    SpreadsheetApp.getUi().alert('Only ' + remaining + ' emails left. Need ' + data.length);
    return;
  }
  let sent = 0;
  for (let i = 0; i < data.length; i++) {
    const [email, name, status] = data[i];
    if (!email || status === 'Sent') continue;
    try {
      MailApp.sendEmail({ to: email, subject: 'Your Weekly Update',
        htmlBody: '<p>Hi ' + name + ',</p><p>Here is your update...</p>' });
      sheet.getRange(i + 2, 3).setValue('Sent'); sent++;
    } catch (e) { sheet.getRange(i + 2, 3).setValue('Error: ' + e.message); }
  }
  SpreadsheetApp.flush();
}
```

### 摘要儀表板產生器

模式：走訪編號的週分頁（`01`-`52`），從每個分頁讀取摘要儲存格，把彙總後的列寫進 Summary 工作表。用 `ss.getSheetByName(tabName)` 來走訪，Summary 不存在的話用 `ss.insertSheet('Summary')` 建立，最後用 `summary.autoResizeColumns()`，return 前要 `flush()`。

---

## 錯誤處理

外部呼叫一律包在 try/catch 裡。用 `muteHttpExceptions: true` 自己處理 HTTP 錯誤。要讓對話框的錯誤處理器接得到，就再 throw 出去。

```javascript
function fetchExternalData() {
  try {
    const response = UrlFetchApp.fetch('https://api.example.com/data', {
      headers: { 'Authorization': 'Bearer ' + getApiKey() },
      muteHttpExceptions: true
    });
    if (response.getResponseCode() !== 200)
      throw new Error('API returned ' + response.getResponseCode());
    return JSON.parse(response.getContentText());
  } catch (e) { Logger.log('Error: ' + e.message); throw e; }
}
```

---

## 錯誤預防

| 錯誤 | 修法 |
|---------|-----|
| 對話框呼叫不到函式 | 把函式名稱結尾的 `_` 拿掉 |
| 資料量大時 script 很慢 | 用 `getValues()`/`setValues()` 批次操作 |
| 對話框結束後看不到改動 | return 前加 `SpreadsheetApp.flush()` |
| `onEdit` 不能寄 email | 改用 installable trigger（`ScriptApp.newTrigger()`） |
| 自訂函式逾時 | 上限 30 秒，要簡化，或改成一般函式 |
| 找不到 `setTimeout` | 用 `Utilities.sleep(ms)`（會阻塞） |
| Script 超過 6 分鐘 | 切成小塊，批次處理改用定時 trigger |
| 授權視窗沒跳出來 | 使用者要點 Advanced > Go to (unsafe) > Allow |

## 除錯

- **Logger.log()** / **console.log()**：在 Apps Script 編輯器的 View > Execution Log 查看
- **手動執行**：在編輯器下拉選單選函式 > Run
- **Executions 分頁**：顯示最近所有執行紀錄，含錯誤和 stack trace
- **Trigger 失敗**：script.google.com > My Projects > Executions
- **部署前一定要先在試算表的副本上測試**

## 部署檢查清單

- [ ] 所有從 HTML 對話框呼叫的函式都是公開的（結尾沒有底線）
- [ ] 會修改資料的函式在 return 前都呼叫了 `SpreadsheetApp.flush()`
- [ ] 外部 API 呼叫和 MailApp 都有錯誤處理（try/catch）
- [ ] 設定常數放在檔案最上面
- [ ] 標頭註解裡有安裝說明
- [ ] 已在試算表副本上測試過
- [ ] 考慮過多使用者的行為（權限不同、目前啟用的工作表不同）
- [ ] 長時間操作使用 modal 進度對話框
- [ ] 沒有寫死工作表名稱，改用設定常數
- [ ] 批次寄信前檢查過 email 配額

---

## 需要時再去 Apps Script 文件重建

- **列/欄顯示/隱藏**：`sheet.hideRows()`、`showRows()`、`isRowHiddenByUser()`
- **格式設定**：`setBackground()`、`setFontWeight()`、`setBorder()`、`setNumberFormat()`、條件式格式
- **資料保護**：`range.protect()`、`setUnprotectedRanges()`、編輯者管理
- **多個工作表**：`getSheetByName()`、走訪編號分頁、`copyTo()`、`insertSheet()`
- **列自動編號**：用 `onEdit` trigger，在 B 欄被編輯時自動替 A 欄編號
- **Google Chat webhook**：用 JSON payload POST 到 `chat.googleapis.com`
