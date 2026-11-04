---
name: wiki-vitepress
description: 把產生好的 wiki Markdown 打包成 VitePress 靜態網站，含深色主題、深色模式 Mermaid 圖（可點擊放大），並輸出正式 build 結果。當使用者想把產生好的 wiki 頁面做成可瀏覽的網站時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Wiki VitePress Packager

把產生好的 wiki Markdown 檔，轉成精緻的 VitePress 靜態網站，有深色主題和可互動的 Mermaid 圖。

## 何時啟動

- 使用者要求「build a site」或「package as VitePress」
- 使用者執行 `/deep-wiki:build` 指令
- 使用者想從產生好的 wiki 頁面得到可瀏覽的 HTML 輸出

## VitePress 腳手架

在 `wiki-site/` 目錄下產生以下結構：

```
wiki-site/
├── .vitepress/
│   ├── config.mts
│   └── theme/
│       ├── index.ts
│       └── custom.css
├── public/
├── [generated .md pages]
├── package.json
└── index.md
```

## Config 需求（`config.mts`）

- 使用 `vitepress-plugin-mermaid` 的 `withMermaid` wrapper
- 設定 `appearance: 'dark'`，只用深色主題
- 依據目錄（catalogue）結構設定 `themeConfig.nav` 和 `themeConfig.sidebar`
- Mermaid config 一定要設定深色主題變數：

```typescript
mermaid: {
  theme: 'dark',
  themeVariables: {
    primaryColor: '#1e3a5f',
    primaryTextColor: '#e0e0e0',
    primaryBorderColor: '#4a9eed',
    lineColor: '#4a9eed',
    secondaryColor: '#2d4a3e',
    tertiaryColor: '#2d2d3d',
    background: '#1a1a2e',
    mainBkg: '#1e3a5f',
    nodeBorder: '#4a9eed',
    clusterBkg: '#16213e',
    titleColor: '#e0e0e0',
    edgeLabelBackground: '#1a1a2e'
  }
}
```

## 深色模式 Mermaid：三層修正

### 第 1 層：主題變數（在 config.mts 裡）
如上所示，透過 `mermaid.themeVariables` 設定。

### 第 2 層：CSS 覆寫（`custom.css`）
用 `!important` 針對 Mermaid 的 SVG 元素：

```css
.mermaid .node rect,
.mermaid .node circle,
.mermaid .node polygon { fill: #1e3a5f !important; stroke: #4a9eed !important; }
.mermaid .edgeLabel { background-color: #1a1a2e !important; color: #e0e0e0 !important; }
.mermaid text { fill: #e0e0e0 !important; }
.mermaid .label { color: #e0e0e0 !important; }
```

### 第 3 層：取代 inline style（`theme/index.ts`）
Mermaid 的 inline `style` 屬性會蓋過所有東西。用 `onMounted` 加輪詢（polling）去取代它們：

```typescript
import { onMounted } from 'vue'

// In setup()
onMounted(() => {
  let attempts = 0
  const fix = setInterval(() => {
    document.querySelectorAll('.mermaid svg [style]').forEach(el => {
      const s = (el as HTMLElement).style
      if (s.fill && !s.fill.includes('#1e3a5f')) s.fill = '#1e3a5f'
      if (s.stroke && !s.stroke.includes('#4a9eed')) s.stroke = '#4a9eed'
      if (s.color) s.color = '#e0e0e0'
    })
    if (++attempts >= 20) clearInterval(fix)
  }, 500)
})
```

要用 `setup()` 搭配 `onMounted`，不要用 `enhanceApp()`，因為 SSR 期間 DOM 不存在。

## Mermaid 圖點擊放大

把每個 `.mermaid` 容器包進可點擊的 wrapper，點下去開啟全螢幕 modal：

```typescript
document.querySelectorAll('.mermaid').forEach(el => {
  el.style.cursor = 'zoom-in'
  el.addEventListener('click', () => {
    const modal = document.createElement('div')
    modal.className = 'mermaid-zoom-modal'
    modal.innerHTML = el.outerHTML
    modal.addEventListener('click', () => modal.remove())
    document.body.appendChild(modal)
  })
})
```

Modal 的 CSS：
```css
.mermaid-zoom-modal {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.9);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999; cursor: zoom-out;
}
.mermaid-zoom-modal .mermaid { transform: scale(1.5); }
```

## 後處理規則

在 VitePress build 之前，掃描所有 `.md` 檔並修正：
- 把 `<br/>` 換成 `<br>`（為了相容 Vue 的 template compiler）
- code fence 以外的裸 `<T>` 泛型參數，用反引號包起來
- 確保每一頁都有 YAML frontmatter，而且有 `title` 和 `description`

## Build

```bash
cd wiki-site && npm install && npm run docs:build
```

輸出會在 `wiki-site/.vitepress/dist/`。

## 已知的坑

- Mermaid 是非同步渲染，`onMounted` 觸發時 SVG 還不存在，所以一定要輪詢。
- 為了裸 `<T>` 而設 `isCustomElement` compiler 選項，會造成更嚴重的當機，絕對不要用
- Mermaid 的節點文字用的是 inline `style`，優先權最高，只靠 CSS 修不掉
- `enhanceApp()` 會在 SSR 期間執行，那時 `document` 不存在，所以只能用 `setup()`
