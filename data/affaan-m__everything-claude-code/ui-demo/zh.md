---
name: ui-demo
description: 用 Playwright 錄製精緻的 UI demo 影片。當使用者要求為網頁應用程式製作 demo、導覽、螢幕錄影或教學影片時使用。產出 WebM 影片，有看得見的游標、自然的節奏和專業的質感。
metadata:
  origin: ECC
---

# UI Demo 影片錄製

用 Playwright 的影片錄製功能，搭配注入的游標覆蓋層、自然的節奏和說故事的流程，錄製網頁應用程式的精緻 demo 影片。

## 何時使用

- 使用者要「demo video」、「screen recording」、「walkthrough」或「tutorial」
- 使用者想用視覺方式展示某個功能或工作流程
- 使用者需要一支用於文件、onboarding 或向利害關係人簡報的影片

## 三階段流程

每個 demo 都要經過三個階段：**Discover -> Rehearse -> Record**。絕對不要跳過去直接錄。

---

## 階段 1：Discover

在寫任何腳本之前，先探索目標頁面，了解實際上有什麼。

### 為什麼

你沒看過的東西，就沒辦法寫成腳本。欄位可能是 `<input>` 而不是 `<textarea>`，下拉選單可能是自訂元件而不是 `<select>`，留言框可能支援 `@mentions` 或 `#tags`。假設會悄悄地讓錄影壞掉。

### 怎麼做

走到流程中的每一頁，把它的互動元素傾印出來：

```javascript
// Run this for each page in the flow BEFORE writing the demo script
const fields = await page.evaluate(() => {
  const els = [];
  document.querySelectorAll('input, select, textarea, button, [contenteditable]').forEach(el => {
    if (el.offsetParent !== null) {
      els.push({
        tag: el.tagName,
        type: el.type || '',
        name: el.name || '',
        placeholder: el.placeholder || '',
        text: el.textContent?.trim().substring(0, 40) || '',
        contentEditable: el.contentEditable === 'true',
        role: el.getAttribute('role') || '',
      });
    }
  });
  return els;
});
console.log(JSON.stringify(fields, null, 2));
```

### 要看什麼

- **表單欄位**：它們是 `<select>`、`<input>`、自訂下拉選單，還是 combobox？
- **Select 選項**：把 option 的 value 和文字都傾印出來。佔位選項常常有 `value="0"` 或 `value=""`，看起來像非空。用 `Array.from(el.options).map(o => ({ value: o.value, text: o.text }))`。略過文字包含 "Select" 或 value 是 `"0"` 的選項。
- **富文字**：留言框支援 `@mentions`、`#tags`、markdown 或 emoji 嗎？檢查 placeholder 文字。
- **必填欄位**：哪些欄位會擋住表單送出？檢查 `required`、標籤裡的 `*`，並試著空白送出，看有沒有驗證錯誤。
- **動態內容**：欄位是不是在填完其他欄位之後才出現？
- **按鈕標籤**：確切的文字，例如 `"Submit"`、`"Submit Request"` 或 `"Send"`。
- **表格欄位標題**：對以表格驅動的 modal，要把每個 `input[type="number"]` 對應到它的欄位標題，不要假設所有數字輸入的意義都一樣。

### 輸出

每一頁的欄位對照表，用來在腳本裡寫出正確的 selector。範例：

```text
/purchase-requests/new:
  - Budget Code: <select> (first select on page, 4 options)
  - Desired Delivery: <input type="date">
  - Context: <textarea> (not input)
  - BOM table: inline-editable cells with span.cursor-pointer -> input pattern
  - Submit: <button> text="Submit"

/purchase-requests/N (detail):
  - Comment: <input placeholder="Type a message..."> supports @user and #PR tags
  - Send: <button> text="Send" (disabled until input has content)
```

---

## 階段 2：Rehearse

不錄影，把所有步驟跑一遍。確認每個 selector 都解析得到。

### 為什麼

靜默的 selector 失敗，是 demo 錄影壞掉的主要原因。彩排可以在你浪費一次錄影之前就抓到它們。

### 怎麼做

用 `ensureVisible`，這是一個會記錄並大聲失敗的包裝函式：

```javascript
async function ensureVisible(page, locator, label) {
  const el = typeof locator === 'string' ? page.locator(locator).first() : locator;
  const visible = await el.isVisible().catch(() => false);
  if (!visible) {
    const msg = `REHEARSAL FAIL: "${label}" not found - selector: ${typeof locator === 'string' ? locator : '(locator object)'}`;
    console.error(msg);
    const found = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('button, input, select, textarea, a'))
        .filter(el => el.offsetParent !== null)
        .map(el => `${el.tagName}[${el.type || ''}] "${el.textContent?.trim().substring(0, 30)}"`)
        .join('\n  ');
    });
    console.error('  Visible elements:\n  ' + found);
    return false;
  }
  console.log(`REHEARSAL OK: "${label}"`);
  return true;
}
```

### 彩排腳本的結構

```javascript
const steps = [
  { label: 'Login email field', selector: '#email' },
  { label: 'Login submit', selector: 'button[type="submit"]' },
  { label: 'New Request button', selector: 'button:has-text("New Request")' },
  { label: 'Budget Code select', selector: 'select' },
  { label: 'Delivery date', selector: 'input[type="date"]:visible' },
  { label: 'Description field', selector: 'textarea:visible' },
  { label: 'Add Item button', selector: 'button:has-text("Add Item")' },
  { label: 'Submit button', selector: 'button:has-text("Submit")' },
];

let allOk = true;
for (const step of steps) {
  if (!await ensureVisible(page, step.selector, step.label)) {
    allOk = false;
  }
}
if (!allOk) {
  console.error('REHEARSAL FAILED - fix selectors before recording');
  process.exit(1);
}
console.log('REHEARSAL PASSED - all selectors verified');
```

### 彩排失敗時

1. 讀可見元素的傾印結果。
2. 找出正確的 selector。
3. 更新腳本。
4. 重新跑彩排。
5. 每個 selector 都通過了才繼續。

---

## 階段 3：Record

要等 discovery 和 rehearsal 都通過之後，才可以建立錄影。

### 錄影原則

#### 1. 說故事的流程

把影片規劃成一個故事。照使用者指定的順序，或用這個預設：

- **Entry**：登入，或導覽到起點
- **Context**：掃過周圍的畫面，讓觀看者先有方向感
- **Action**：執行主要的工作流程步驟
- **Variation**：展示次要功能，例如設定、主題或在地化
- **Result**：展示結果、確認畫面，或新的狀態

#### 2. 節奏

- 登入之後：`4s`
- 導覽之後：`3s`
- 點擊按鈕之後：`2s`
- 主要步驟之間：`1.5-2s`
- 最後一個動作之後：`3s`
- 打字延遲：每個字元 `25-40ms`

#### 3. 游標覆蓋層

注入一個會跟著滑鼠移動的 SVG 箭頭游標：

```javascript
async function injectCursor(page) {
  await page.evaluate(() => {
    if (document.getElementById('demo-cursor')) return;
    const cursor = document.createElement('div');
    cursor.id = 'demo-cursor';
    cursor.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M5 3L19 12L12 13L9 20L5 3Z" fill="white" stroke="black" stroke-width="1.5" stroke-linejoin="round"/>
    </svg>`;
    cursor.style.cssText = `
      position: fixed; z-index: 999999; pointer-events: none;
      width: 24px; height: 24px;
      transition: left 0.1s, top 0.1s;
      filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.3));
    `;
    cursor.style.left = '0px';
    cursor.style.top = '0px';
    document.body.appendChild(cursor);
    document.addEventListener('mousemove', (e) => {
      cursor.style.left = e.clientX + 'px';
      cursor.style.top = e.clientY + 'px';
    });
  });
}
```

每次頁面導覽之後都要呼叫 `injectCursor(page)`，因為覆蓋層在導覽時會被銷毀。

#### 4. 滑鼠移動

絕對不要讓游標瞬間移動。點擊前要先移到目標上：

```javascript
async function moveAndClick(page, locator, label, opts = {}) {
  const { postClickDelay = 800, ...clickOpts } = opts;
  const el = typeof locator === 'string' ? page.locator(locator).first() : locator;
  const visible = await el.isVisible().catch(() => false);
  if (!visible) {
    console.error(`WARNING: moveAndClick skipped - "${label}" not visible`);
    return false;
  }
  try {
    await el.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    const box = await el.boundingBox();
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 10 });
      await page.waitForTimeout(400);
    }
    await el.click(clickOpts);
  } catch (e) {
    console.error(`WARNING: moveAndClick failed on "${label}": ${e.message}`);
    return false;
  }
  await page.waitForTimeout(postClickDelay);
  return true;
}
```

每次呼叫都應該帶一個有描述性的 `label`，方便除錯。

#### 5. 打字

要讓打字看得見，不要瞬間填入：

```javascript
async function typeSlowly(page, locator, text, label, charDelay = 35) {
  const el = typeof locator === 'string' ? page.locator(locator).first() : locator;
  const visible = await el.isVisible().catch(() => false);
  if (!visible) {
    console.error(`WARNING: typeSlowly skipped - "${label}" not visible`);
    return false;
  }
  await moveAndClick(page, el, label);
  await el.fill('');
  await el.pressSequentially(text, { delay: charDelay });
  await page.waitForTimeout(500);
  return true;
}
```

#### 6. 捲動

用平滑捲動，不要跳來跳去：

```javascript
await page.evaluate(() => window.scrollTo({ top: 400, behavior: 'smooth' }));
await page.waitForTimeout(1500);
```

#### 7. Dashboard 掃視

展示 dashboard 或總覽頁面時，讓游標掃過關鍵元素：

```javascript
async function panElements(page, selector, maxCount = 6) {
  const elements = await page.locator(selector).all();
  for (let i = 0; i < Math.min(elements.length, maxCount); i++) {
    try {
      const box = await elements[i].boundingBox();
      if (box && box.y < 700) {
        await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 8 });
        await page.waitForTimeout(600);
      }
    } catch (e) {
      console.warn(`WARNING: panElements skipped element ${i} (selector: "${selector}"): ${e.message}`);
    }
  }
}
```

#### 8. 字幕

在 viewport 底部注入一條字幕列：

```javascript
async function injectSubtitleBar(page) {
  await page.evaluate(() => {
    if (document.getElementById('demo-subtitle')) return;
    const bar = document.createElement('div');
    bar.id = 'demo-subtitle';
    bar.style.cssText = `
      position: fixed; bottom: 0; left: 0; right: 0; z-index: 999998;
      text-align: center; padding: 12px 24px;
      background: rgba(0, 0, 0, 0.75);
      color: white; font-family: -apple-system, "Segoe UI", sans-serif;
      font-size: 16px; font-weight: 500; letter-spacing: 0.3px;
      transition: opacity 0.3s;
      pointer-events: none;
    `;
    bar.textContent = '';
    bar.style.opacity = '0';
    document.body.appendChild(bar);
  });
}

async function showSubtitle(page, text) {
  await page.evaluate((t) => {
    const bar = document.getElementById('demo-subtitle');
    if (!bar) return;
    if (t) {
      bar.textContent = t;
      bar.style.opacity = '1';
    } else {
      bar.style.opacity = '0';
    }
  }, text);
  if (text) await page.waitForTimeout(800);
}
```

每次導覽之後，要把 `injectSubtitleBar(page)` 跟 `injectCursor(page)` 一起呼叫。

使用模式：

```javascript
await showSubtitle(page, 'Step 1 - Logging in');
await showSubtitle(page, 'Step 2 - Dashboard overview');
await showSubtitle(page, '');
```

準則：

- 字幕文字要短，最好在 60 個字元以內。
- 用 `Step N - Action` 的格式保持一致。
- 在 UI 自己就能說明的長停頓期間，把字幕清掉。

## 腳本範本

```javascript
'use strict';
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE_URL = process.env.QA_BASE_URL || 'http://localhost:3000';
const VIDEO_DIR = path.join(__dirname, 'screenshots');
const OUTPUT_NAME = 'demo-FEATURE.webm';
const REHEARSAL = process.argv.includes('--rehearse');

// Paste injectCursor, injectSubtitleBar, showSubtitle, moveAndClick,
// typeSlowly, ensureVisible, and panElements here.

(async () => {
  const browser = await chromium.launch({ headless: true });

  if (REHEARSAL) {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    // Navigate through the flow and run ensureVisible for each selector.
    await browser.close();
    return;
  }

  const context = await browser.newContext({
    recordVideo: { dir: VIDEO_DIR, size: { width: 1280, height: 720 } },
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();

  try {
    await injectCursor(page);
    await injectSubtitleBar(page);

    await showSubtitle(page, 'Step 1 - Logging in');
    // login actions

    await page.goto(`${BASE_URL}/dashboard`);
    await injectCursor(page);
    await injectSubtitleBar(page);
    await showSubtitle(page, 'Step 2 - Dashboard overview');
    // pan dashboard

    await showSubtitle(page, 'Step 3 - Main workflow');
    // action sequence

    await showSubtitle(page, 'Step 4 - Result');
    // final reveal
    await showSubtitle(page, '');
  } catch (err) {
    console.error('DEMO ERROR:', err.message);
  } finally {
    await context.close();
    const video = page.video();
    if (video) {
      const src = await video.path();
      const dest = path.join(VIDEO_DIR, OUTPUT_NAME);
      try {
        fs.copyFileSync(src, dest);
        console.log('Video saved:', dest);
      } catch (e) {
        console.error('ERROR: Failed to copy video:', e.message);
        console.error('  Source:', src);
        console.error('  Destination:', dest);
      }
    }
    await browser.close();
  }
})();
```

用法：

```bash
# Phase 2: Rehearse
node demo-script.cjs --rehearse

# Phase 3: Record
node demo-script.cjs
```

## 錄影前檢查清單

- [ ] Discovery 階段已完成
- [ ] Rehearsal 通過，所有 selector 都 OK
- [ ] 已啟用 headless 模式
- [ ] 解析度設為 `1280x720`
- [ ] 每次導覽之後都重新注入游標和字幕覆蓋層
- [ ] 在主要的轉場使用 `showSubtitle(page, 'Step N - ...')`
- [ ] 所有點擊都用 `moveAndClick`，並附有描述性的 label
- [ ] 看得見的輸入使用 `typeSlowly`
- [ ] 沒有靜默的 catch；helper 都會記錄警告
- [ ] 內容的呈現使用平滑捲動
- [ ] 關鍵的停頓，人類觀看者看得出來
- [ ] 流程符合要求的故事順序
- [ ] 腳本反映的是階段 1 實際發現的 UI

## 常見陷阱

1. 導覽之後游標消失：重新注入它。
2. 影片太快：加上停頓。
3. 游標是個圓點而不是箭頭：使用 SVG 覆蓋層。
4. 游標瞬間移動：點擊前先移過去。
5. Select 下拉選單看起來怪怪的：先展示移動，再選選項。
6. Modal 感覺很突兀：確認之前加一段閱讀的停頓。
7. 影片檔路徑是隨機的：複製成固定的輸出名稱。
8. Selector 失敗被吞掉：絕對不要用靜默的 catch 區塊。
9. 欄位型別是假設的：先去探索它們。
10. 功能是假設的：寫腳本之前先檢查實際的 UI。
11. 佔位的 select 值看起來像真的：留意 `"0"` 和 `"Select..."`。
12. 彈出視窗會產生獨立的影片：明確擷取彈出頁面，必要時再合併。
