---
name: screen-reader-testing
description: 用螢幕閱讀器（包含 VoiceOver、NVDA 和 JAWS）測試網頁應用。在驗證螢幕閱讀器相容性、除錯無障礙問題，或確保輔助科技的支援時使用。
---

# Screen Reader Testing

用螢幕閱讀器測試網頁應用的實用指南，做完整的無障礙驗證。

## When to Use This Skill

- 驗證螢幕閱讀器的相容性
- 測試 ARIA 的實作
- 除錯輔助科技的問題
- 驗證表單的無障礙
- 測試動態內容的語音播報
- 確保 navigation 的無障礙

## Core Concepts

### 1. Major Screen Readers

| Screen Reader | Platform  | Browser        | Usage |
| ------------- | --------- | -------------- | ----- |
| **VoiceOver** | macOS/iOS | Safari         | ~15%  |
| **NVDA**      | Windows   | Firefox/Chrome | ~31%  |
| **JAWS**      | Windows   | Chrome/IE      | ~40%  |
| **TalkBack**  | Android   | Chrome         | ~10%  |
| **Narrator**  | Windows   | Edge           | ~4%   |

### 2. Testing Priority

```
Minimum Coverage:
1. NVDA + Firefox (Windows)
2. VoiceOver + Safari (macOS)
3. VoiceOver + Safari (iOS)

Comprehensive Coverage:
+ JAWS + Chrome (Windows)
+ TalkBack + Chrome (Android)
+ Narrator + Edge (Windows)
```

### 3. Screen Reader Modes

| Mode               | Purpose                | When Used         |
| ------------------ | ---------------------- | ----------------- |
| **Browse/Virtual** | 閱讀內容           | 預設的閱讀模式   |
| **Focus/Forms**    | 跟控制項互動 | 填寫表單     |
| **Application**    | 自訂 widget         | ARIA 應用程式 |

在 macOS 上測試之前，先讀 [VoiceOver 的設定、指令和檢查清單](references/voiceover.md)。

iOS Safari 的覆蓋是必要的，請讀 [VoiceOver 觸控的設定和手勢](references/voiceover-ios.md)。

用 NVDA 測試之前，先讀 [NVDA 的設定、模式、指令和測試腳本](references/nvda.md)。

用 JAWS 或 TalkBack 測試之前，先讀 [各平台的設定和指令](references/jaws-talkback.md)。

## Common Test Scenarios

### 1. Modal Dialog

```html
<!-- Accessible modal structure -->
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-desc"
>
  <h2 id="dialog-title">Confirm Delete</h2>
  <p id="dialog-desc">This action cannot be undone.</p>
  <button>Cancel</button>
  <button>Delete</button>
</div>
```

```javascript
// Focus management
function openModal(modal) {
  // Store last focused element
  lastFocus = document.activeElement;

  // Move focus to modal
  modal.querySelector("h2").focus();

  // Trap focus
  modal.addEventListener("keydown", trapFocus);
}

function closeModal(modal) {
  // Return focus
  lastFocus.focus();
}

function trapFocus(e) {
  if (e.key === "Tab") {
    const focusable = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      last.focus();
      e.preventDefault();
    } else if (!e.shiftKey && document.activeElement === last) {
      first.focus();
      e.preventDefault();
    }
  }

  if (e.key === "Escape") {
    closeModal(modal);
  }
}
```

### 2. Live Regions

```html
<!-- Status messages (polite) -->
<div role="status" aria-live="polite" aria-atomic="true">
  <!-- Content updates will be announced after current speech -->
</div>

<!-- Alerts (assertive) -->
<div role="alert" aria-live="assertive">
  <!-- Content updates interrupt current speech -->
</div>

<!-- Progress updates -->
<div
  role="progressbar"
  aria-valuenow="75"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-label="Upload progress"
></div>

<!-- Log (additions only) -->
<div role="log" aria-live="polite" aria-relevant="additions">
  <!-- New messages announced, removals not -->
</div>
```

### 3. Tab Interface

```html
<div role="tablist" aria-label="Product information">
  <button role="tab" id="tab-1" aria-selected="true" aria-controls="panel-1">
    Description
  </button>
  <button
    role="tab"
    id="tab-2"
    aria-selected="false"
    aria-controls="panel-2"
    tabindex="-1"
  >
    Reviews
  </button>
</div>

<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
  Product description content...
</div>

<div role="tabpanel" id="panel-2" aria-labelledby="tab-2" hidden>
  Reviews content...
</div>
```

```javascript
// Tab keyboard navigation
tablist.addEventListener("keydown", (e) => {
  const tabs = [...tablist.querySelectorAll('[role="tab"]')];
  const index = tabs.indexOf(document.activeElement);

  let newIndex;
  switch (e.key) {
    case "ArrowRight":
      newIndex = (index + 1) % tabs.length;
      break;
    case "ArrowLeft":
      newIndex = (index - 1 + tabs.length) % tabs.length;
      break;
    case "Home":
      newIndex = 0;
      break;
    case "End":
      newIndex = tabs.length - 1;
      break;
    default:
      return;
  }

  tabs[newIndex].focus();
  activateTab(tabs[newIndex]);
  e.preventDefault();
});
```

## Debugging Tips

```javascript
// Log what screen reader sees
function logAccessibleName(element) {
  const computed = window.getComputedStyle(element);
  console.log({
    role: element.getAttribute("role") || element.tagName,
    name:
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby") ||
      element.textContent,
    state: {
      expanded: element.getAttribute("aria-expanded"),
      selected: element.getAttribute("aria-selected"),
      checked: element.getAttribute("aria-checked"),
      disabled: element.disabled,
    },
    visible: computed.display !== "none" && computed.visibility !== "hidden",
  });
}
```

## Best Practices

### Do's

- **用真正的螢幕閱讀器測試** - 不要只用模擬器
- **先用語意化 HTML** - ARIA 只是補充
- **在 browse 和 focus 模式都測** - 體驗不一樣
- **驗證 focus 管理** - 尤其是 SPA
- **先只用鍵盤測試** - 這是螢幕閱讀器測試的基礎

### Don'ts

- **不要以為一種螢幕閱讀器就夠了** - 要測多種
- **不要忽略行動裝置** - 使用者正在成長
- **不要只測 happy path** - 也要測錯誤狀態
- **不要跳過動態內容** - 最常出問題的地方
- **不要只靠視覺測試** - 體驗不一樣
