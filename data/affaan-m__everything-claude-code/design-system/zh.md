---
name: design-system
description: "從既有的 codebase 產生設計系統，或稽核視覺一致性：把 token（顏色、字體、間距、陰影）擷取到 design-tokens.json 和 CSS custom property，附上 DESIGN.md 的決策理由和可互動的 HTML 預覽，從 10 個面向替 UI 評分，並標出 AI slop 的模式。當要開始建立設計系統、在改版前稽核視覺一致性，或審查動到樣式的 PR 時使用。"
metadata:
  origin: ECC
---

# Design System：產生與稽核視覺系統

## 何時使用

- 開始一個需要設計系統的新專案
- 稽核既有 codebase 的視覺一致性
- 改版之前，先搞清楚你現有的是什麼
- UI 看起來「怪怪的」，但說不出哪裡怪
- 審查動到樣式的 PR

## 運作方式

### 模式 1：產生設計系統

分析你的 codebase，並產生一套前後一致的設計系統：

```
1. Scan CSS/Tailwind/styled-components for existing patterns
2. Extract: colors, typography, spacing, border-radius, shadows, breakpoints
3. Research 3 competitor sites for inspiration (via browser MCP)
4. Propose a design token set (JSON + CSS custom properties)
5. Generate DESIGN.md with rationale for each decision
6. Create an interactive HTML preview page (self-contained, no deps)
```

輸出：`DESIGN.md` + `design-tokens.json` + `design-preview.html`

### 模式 2：視覺稽核

從 10 個面向替你的 UI 評分（每項 0-10 分）：

```
1. Color consistency — are you using your palette or random hex values?
2. Typography hierarchy — clear h1 > h2 > h3 > body > caption?
3. Spacing rhythm — consistent scale (4px/8px/16px) or arbitrary?
4. Component consistency — do similar elements look similar?
5. Responsive behavior — fluid or broken at breakpoints?
6. Dark mode — complete or half-done?
7. Animation — purposeful or gratuitous?
8. Accessibility — contrast ratios, focus states, touch targets
9. Information density — cluttered or clean?
10. Polish — hover states, transitions, loading states, empty states
```

每個面向都會得到分數、具體的例子，以及附上精確 file:line 的修正建議。

### 模式 3：AI Slop 偵測

找出通用的 AI 生成設計模式：

```
- Gratuitous gradients on everything
- Purple-to-blue defaults
- "Glass morphism" cards with no purpose
- Rounded corners on things that shouldn't be rounded
- Excessive animations on scroll
- Generic hero with centered text over stock gradient
- Sans-serif font stack with no personality
```

## 範例

**為 SaaS 應用程式產生：**
```
/design-system generate --style minimal --palette earth-tones
```

**稽核既有的 UI：**
```
/design-system audit --url http://localhost:3000 --pages / /pricing /docs
```

**檢查 AI slop：**
```
/design-system slop-check
```
