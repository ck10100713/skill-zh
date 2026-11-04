---
name: browser-qa
description: "用瀏覽器自動化 MCP（claude-in-chrome、Playwright 或 Puppeteer）執行部署後的 UI 自動驗證：console 錯誤與 Core Web Vitals 冒煙檢查、表單與登入流程的互動測試、三個斷點的截圖視覺回歸，以及 axe-core 無障礙稽核，最後給出 SHIP / DO-NOT-SHIP 的結論。適用於測試 staging 或 preview 上已部署的功能、前端變更上線前、審查前端 PR，或檢查響應式版面與無障礙。"
metadata:
  origin: ECC
---

# Browser QA — Automated Visual Testing & Interaction

## When to Use

- 功能部署到 staging/preview 之後
- 需要驗證跨頁面的 UI 行為時
- 上線前，確認版面、表單、互動真的能用
- 審查動到前端程式碼的 PR 時
- 無障礙稽核與響應式測試

## How It Works

用瀏覽器自動化 MCP（claude-in-chrome、Playwright 或 Puppeteer），像真實使用者一樣操作線上頁面。

### Safety first — blast radius (run read-only by default)

Browser QA 會動用真實的登入和真實的使用者旅程，所以要明確控制影響範圍。
預設是**唯讀**：絕對不要對 production URL 跑會**變更資料**的旅程（結帳、付款、刪除、
大量更新），一定要有明確的 opt-in **而且**是 staging/preview
URL 才行。用事先建好的**測試帳號**，絕對不用真實的 production 登入，
儲存任何截圖之前，要先把憑證、token、個資**遮蔽**掉。

### Phase 1: Smoke Test
```
1. Navigate to target URL
2. Check for console errors (filter noise: analytics, third-party)
3. Verify no 4xx/5xx in network requests
4. Screenshot above-the-fold on desktop + mobile viewport
5. Check Core Web Vitals: LCP < 2.5s, CLS < 0.1, INP < 200ms
   (INP replaced FID in March 2024; thresholds per web.dev)
```

### Phase 2: Interaction Test
```
1. Click every nav link — verify no dead links
2. Submit forms with valid data — verify success state
3. Submit forms with invalid data — verify error state
4. Test auth flow: login → protected page → logout (test creds only, never prod)
5. Test critical user journeys (checkout, onboarding, search)
   — read-only by default; only exercise mutating journeys against staging
     with explicit opt-in (see "Safety first" above)
```

### Phase 3: Visual Regression
```
1. Screenshot key pages at 3 breakpoints (375px, 768px, 1440px)
2. Compare against committed baseline screenshots
   — no baseline ⇒ report INCONCLUSIVE, never a silent PASS
3. Flag layout shifts > 5px, missing elements, overflow
4. Check dark mode if applicable
```

### Phase 4: Accessibility
```
1. Run axe-core or equivalent on each page
2. Flag WCAG 2.2 AA violations (contrast, labels, focus order)
3. Verify keyboard navigation works end-to-end
4. Check screen reader landmarks
```

> 注意：axe-core 自動涵蓋的範圍大約只有 WCAG 的 30–40%。跑出乾淨的結果是**必要條件，
> 但不充分**，鍵盤導覽、焦點順序和螢幕閱讀器的檢查仍然需要手動
> 確認。不要只憑自動化通過就回報「無障礙沒問題」。

## Output Format

```markdown
## QA Report — [URL] — [timestamp]

### Smoke Test
- Console errors: 0 critical, 2 warnings (analytics noise)
- Network: all 200/304, no failures
- Core Web Vitals: LCP 1.2s ✓, CLS 0.02 ✓, INP 89ms ✓

### Interactions
- [✓] Nav links: 12/12 working
- [✗] Contact form: missing error state for invalid email
- [✓] Auth flow: login/logout working

### Visual
- [✗] Hero section overflows on 375px viewport
- [✓] Dark mode: all pages consistent

### Accessibility
- 2 AA violations: missing alt text on hero image, low contrast on footer links

### Verdict: SHIP WITH FIXES (2 issues, 0 blockers)
# verdict ∈ SHIP / SHIP WITH FIXES / DO NOT SHIP; use INCONCLUSIVE if no visual baseline
```

## Integration

可搭配任何瀏覽器 MCP：
- `mChild__claude-in-chrome__*` 工具（首選，用的是你實際的 Chrome）
- 透過 `mcp__browserbase__*` 使用 Playwright
- 直接寫 Puppeteer script

搭配 `/canary-watch` 做部署後的監控。
