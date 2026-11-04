---
name: design-handoff
description: 從設計稿產生給開發者的 handoff 規格。當設計已經可以交給工程，需要一份涵蓋版面、design token、元件 props、互動狀態、responsive 斷點、邊界情況和動畫細節的規格表時使用。
argument-hint: "<Figma URL or design description>"
---

# /design-handoff

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

從設計稿產生完整的開發者 handoff 文件。

## 用法

```
/design-handoff $ARGUMENTS
```

為這個產生 handoff 規格：@$1

如果有給 Figma URL，就從 Figma 把設計拉下來。否則就根據提供的描述或截圖來做。

## 要包含什麼

### 視覺規格
- 精確的尺寸（padding、margin、寬度）
- Design token 參照（顏色、字體排印、間距）
- Responsive 斷點和行為
- 元件的 variant 和狀態

### 互動規格
- 點擊／輕觸的行為
- Hover 狀態
- 轉場和動畫（時長、easing）
- 手勢支援（滑動、縮放、長按）

### 內容規格
- 字數上限
- 截斷行為
- 空狀態
- 載入狀態
- 錯誤狀態

### 邊界情況
- 內容的最小／最大量
- 國際化文字（字串比較長）
- 網路很慢
- 資料缺漏

### 無障礙
- Focus 順序
- ARIA label 和 role
- 鍵盤互動
- 螢幕閱讀器的朗讀內容

## 原則

1. **不要假設**：沒寫清楚的東西，開發者就會用猜的。每件事都要講清楚。
2. **用 token，不要用數值**：參照 `spacing-md`，不要寫 `16px`。
3. **每個狀態都要列**：default、hover、active、disabled、loading、error、empty。
4. **說明為什麼**：「這在 mobile 會收合，因為使用者主要單手操作」這種說明，能幫開發者做出好的判斷。

## 輸出

```markdown
## Handoff Spec: [Feature/Screen Name]

### Overview
[What this screen/feature does, user context]

### Layout
[Grid system, breakpoints, responsive behavior]

### Design Tokens Used
| Token | Value | Usage |
|-------|-------|-------|
| `color-primary` | #[hex] | CTA buttons, links |
| `spacing-md` | [X]px | Between sections |
| `font-heading-lg` | [size/weight/family] | Page title |

### Components
| Component | Variant | Props | Notes |
|-----------|---------|-------|-------|
| [Component] | [Variant] | [Props] | [Special behavior] |

### States and Interactions
| Element | State | Behavior |
|---------|-------|----------|
| [CTA Button] | Hover | [Background darken 10%] |
| [CTA Button] | Loading | [Spinner, disabled] |
| [Form] | Error | [Red border, error message below] |

### Responsive Behavior
| Breakpoint | Changes |
|------------|---------|
| Desktop (>1024px) | [Default layout] |
| Tablet (768-1024px) | [What changes] |
| Mobile (<768px) | [What changes] |

### Edge Cases
- **Empty state**: [What to show when no data]
- **Long text**: [Truncation rules]
- **Loading**: [Skeleton or spinner]
- **Error**: [Error state appearance]

### Animation / Motion
| Element | Trigger | Animation | Duration | Easing |
|---------|---------|-----------|----------|--------|
| [Element] | [Trigger] | [Description] | [ms] | [easing] |

### Accessibility Notes
- [Focus order]
- [ARIA labels needed]
- [Keyboard interactions]
```

## 如果有連接 connector

如果有連接 **~~design tool**：
- 從 Figma 拉精確的尺寸、token 和元件規格
- 匯出素材並產生完整的規格表

如果有連接 **~~project tracker**：
- 把 handoff 連到實作的 ticket
- 為規格的每個段落建立子任務

## 小提醒

1. **貼上 Figma 連結**：我就能拉到精確的尺寸、token 和元件資訊。
2. **提到邊界情況**：問「有 100 個項目時會怎樣？」，我就能把邊界條件寫進規格。
3. **說明技術棧**：說「我們用 React + Tailwind」，我就能給更貼切的實作備註。
