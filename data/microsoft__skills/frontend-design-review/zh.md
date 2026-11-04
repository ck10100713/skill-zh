---
name: frontend-design-review
description: >
  審查並打造有辨識度、可上正式環境的前端介面，兼顧高設計品質與 design system 合規。
  用三大支柱評估：從洞察到行動毫無阻力、品質是工藝、可信賴的打造。
  USE FOR: PR reviews, design reviews, accessibility audits, design system compliance checks, creative frontend design,
  UI code review, component reviews, responsive design checks, theme testing, and creating memorable UI.
  DO NOT USE FOR: Backend API reviews, database schema reviews, infrastructure or DevOps work, pure business logic
  without UI, or non-frontend code.
acknowledgments: |
  設計審查原則與品質支柱框架由 @Quirinevwm (https://github.com/Quirinevwm) 創作。
  創意前端的指引靈感來自 Anthropic 的 frontend-design skill
  (https://github.com/anthropics/skills/tree/main/skills/frontend-design)。各自依其授權條款使用。
---

# Frontend Design Review

依據設計品質標準和你的 design system 審查 UI 實作，**或者**從零打造有辨識度、可上正式環境的前端介面。

## Two Modes

### Mode 1: Design Review
評估現有的 UI，看它是否符合 design system、三大品質支柱（Frictionless、Quality Craft、Trustworthy）、無障礙和程式碼品質。

### Mode 2: Creative Frontend Design
打造有辨識度的介面，避開千篇一律的「AI slop」美學，有清楚的概念方向，並且精準執行。

---

## Creative Frontend Design

寫程式之前，先決定一個美學方向：
- **Purpose**：這解決什麼問題？誰會用？
- **Tone**：極簡、極繁、復古未來、有機、奢華、俏皮、編輯風、野獸派、裝飾藝術、柔和/粉彩、工業風等等。
- **Constraints**：框架、效能、無障礙的要求。
- **Differentiation**：什麼讓它有辨識度，又符合情境？

### Aesthetics Guidelines

- **Typography**：選有辨識度、能提升美感的字體。把 display 字體和精緻的內文字體搭配。避開 Inter、Roboto、Arial、Space Grotesk。
- **Color & Theme**：用 CSS 變數建立一致的配色。主色加上銳利的點綴色，勝過膽怯又平均分配的色盤。
- **Motion**：優先用純 CSS。一次編排得宜、有錯落進場的頁面載入動畫，勝過零散的微互動。
- **Spatial Composition**：不對稱、重疊、對角線流向、打破網格的元素、大方的留白，**或是**有控制的高密度。
- **Backgrounds**：漸層網格、雜訊紋理、幾何圖案、多層透明、戲劇性的陰影、顆粒疊加。

**避免**：用爛的字體、老套的配色、可預測的版面、沒有針對情境設計特色的千篇一律設計。

實作的複雜度要符合願景。極繁 = 精細的程式碼。極簡 = 克制與精準。

---

## Design Review

### Design System Workflow

**實作之前：**
1. 到你的 Storybook / 元件庫看元件的 API 和用法
2. 用 Figma Dev Mode 取得精確的規格（間距、token、屬性）
3. 用 design system 的元件 + design token 來實作

**審查時：**
1. 把實作和 Figma 設計做比對
2. 確認有用 design token（不是寫死的值）
3. 檢查所有 variant/狀態都實作正確
4. 標出偏差（需要設計核准）

**如果元件不存在：**
1. 檢查現有元件能不能調整來用
2. 聯絡設計團隊建立新元件
3. 在程式碼裡記錄例外和理由

### Review Process

1. 找出使用者的任務
2. 在 design system 裡找符合的模式
3. 評估美學方向
4. 確認範圍（元件、功能或流程）
5. 逐一評估每個支柱
6. 為問題評分並排優先順序（blocking/major/minor）
7. 附上 design system 範例來提供建議

### Core Principles

- **Task completion**：點擊次數越少越好。每個畫面都要回答「我可以做什麼？」和「接下來會發生什麼？」
- **Action hierarchy**：每個 view 有 1-2 個主要動作。次要動作用漸進式揭露。
- **Onboarding**：功能出現時就解釋。預設值要聰明，勝過一堆設定。
- **Navigation**：進出點要清楚。隨時都有返回/取消。深層流程要有 breadcrumb。

---

## Quality Pillars

### 1. Frictionless Insight to Action

**評估：** 任務能在 ≤3 次互動內完成嗎？主要動作明顯而且只有一個嗎？

**警訊：** 點太多次、多個互相競爭的主要按鈕、動作藏很深、死路。

### 2. Quality is Craft

**評估：**
- Design system 合規：符合 Figma 規格，有用 design token
- 美學方向：有辨識度的字體、一致的配色、有意圖的動態
- 無障礙：最低 Grade C（WCAG 2.1 A），理想是 Grade B（WCAG 2.1 AA）

**警訊：** 千篇一律的 AI 美學、寫死的值、實作和 Figma 不符、reflow 壞掉、缺少 focus 指示。

### 3. Trustworthy Building

**評估：**
- AI 透明度：AI 生成的內容要有免責聲明
- 錯誤透明度：錯誤訊息要能讓人採取行動

**警訊：** 缺少 AI 免責聲明、錯誤訊息不透明又沒有指引。

---

## Review Output Format

完整的審查範本見 [references/review-output-format.md](references/review-output-format.md)。

## Review Type Modifiers

依情境調整審查重點（PR、Creative、Design、Accessibility）見 [references/review-type-modifiers.md](references/review-type-modifiers.md)。

## Quick Checklist

核准前的檢查清單（涵蓋 design system 合規、美學品質、frictionless、quality craft 和 trustworthy 支柱）見 [references/quick-checklist.md](references/quick-checklist.md)。

## Pattern Examples

創意前端與 design system 審查工作的好壞範例見 [references/pattern-examples.md](references/pattern-examples.md)。

---

## Acknowledgments

創意前端的原則靈感來自 [Anthropic's frontend-design skill](https://github.com/anthropics/skills/tree/main/skills/frontend-design)。設計審查原則與品質支柱框架由 [@Quirinevwm](https://github.com/Quirinevwm) 創作，用於系統化的 UI 評估。
