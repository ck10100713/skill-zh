---
layout: "default"
skill: "web-perf"
author: "Cloudflare"
category: "Cloudflare 平台"
summary: "用 Chrome DevTools MCP 稽核網站效能與 Core Web Vitals"
source: "https://github.com/cloudflare/skills/blob/main/skills/web-perf/SKILL.md"
license: "Apache-2.0"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: web-perf
description: 稽核、診斷或優化網站的載入與互動效能、Core Web Vitals 和 Lighthouse 效能分數。
---

# Web Performance Audit

你對網頁效能指標、門檻值和工具 API 的知識可能已經過時。引用具體數字或建議時，**優先用檢索，不要靠預訓練記憶**。

## Retrieval Sources

| 來源 | 怎麼檢索 | 用途 |
|--------|----------------|---------|
| web.dev | `https://web.dev/articles/vitals` | Core Web Vitals 的門檻值、定義 |
| Chrome DevTools docs | `https://developer.chrome.com/docs/devtools/performance` | 工具 API、trace 分析 |
| Lighthouse scoring | `https://developer.chrome.com/docs/lighthouse/performance/performance-scoring` | 分數權重、指標門檻 |

## FIRST: Verify MCP Tools Available

開始之前，先確認有哪些可用的瀏覽器和效能工具。針對要求的稽核，用手上有的能力。如果沒有 trace 工具，就繼續做任何有用的原始碼或網路分析，並說明哪些量測沒辦法收集。

如果使用者要設定 Chrome DevTools MCP，參考它的[安裝指南](https://github.com/ChromeDevTools/chrome-devtools-mcp#quick-start)，並使用最新的套件版本。只有在設定屬於使用者授權的範圍內才去改 MCP 設定，否則先問。對使用 `command` 和 `args` 的 client，server 項目的範例如下：

```json
"chrome-devtools": {
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest"]
}
```

## Key Guidelines

- **要有把握**：先檢查 network request、DOM 或程式碼庫來驗證說法，再明確地講出發現。
- **建議之前先驗證**：確認某個東西沒被用到，才建議移除。
- **量化影響**：用 insight 估算的節省量。影響是 0ms 的改動不要排優先。
- **跳過不是問題的項目**：如果 render-blocking 資源估算的影響是 0ms，記一筆就好，不要建議處理。
- **要具體**：講「把 hero.png（450KB）壓成 WebP」，不要講「優化圖片」。
- **毫不留情地排優先順序**：LCP 200ms、CLS 為 0 的網站已經很優秀了，直接講。

## Quick Reference

| 任務 | 工具呼叫 |
|------|-----------|
| 載入頁面 | `navigate_page(url: "...")` |
| 開始 trace | `performance_start_trace(autoStop: true, reload: true)` |
| 分析 insight | `performance_analyze_insight(insightSetId: "...", insightName: "...")` |
| 列出 request | `list_network_requests(resourceTypes: ["Script", "Stylesheet", ...])` |
| Request 細節 | `get_network_request(reqid: <id>)` |
| 無障礙 snapshot | `take_snapshot(verbose: true)` |

## Workflow

複製這份 checklist 來追蹤進度：

```
Audit Progress:
- [ ] Phase 1: Performance trace (navigate + record)
- [ ] Phase 2: Core Web Vitals analysis (includes CLS culprits)
- [ ] Phase 3: Network analysis
- [ ] Phase 4: Accessibility snapshot
- [ ] Phase 5: Codebase analysis (skip if third-party site)
```

### Phase 1: Performance Trace

1. 導覽到目標 URL：
   ```
   navigate_page(url: "<target-url>")
   ```

2. 開始 performance trace 並重新載入，以擷取 cold-load 的指標：
   ```
   performance_start_trace(autoStop: true, reload: true)
   ```

3. 等 trace 完成，再取得結果。

**排查：**
- 如果 trace 回傳空的或失敗，先用 `navigate_page` 確認頁面有正確載入
- 如果 insight 名稱對不上，檢查 trace 的回應，列出可用的 insight

### Phase 2: Core Web Vitals Analysis

用 `performance_analyze_insight` 取出關鍵指標。

**注意：** insight 名稱可能因 Chrome DevTools 版本而異。如果某個 insight 名稱不能用，就看 trace 回應裡的 `insightSetId`，找出可用的 insight。

常見的 insight 名稱：

| 指標 | Insight 名稱 | 要看什麼 |
|--------|--------------|------------------|
| LCP | `LCPBreakdown` | 到最大內容繪製（LCP）的時間；TTFB、資源載入、render 延遲的拆解 |
| CLS | `CLSCulprits` | 造成 layout shift 的元素（沒有尺寸的圖片、注入的內容、字型替換） |
| Render Blocking | `RenderBlocking` | 擋住第一次繪製的 CSS/JS |
| Document Latency | `DocumentLatency` | 伺服器回應時間的問題 |
| Network Dependencies | `NetworkRequestsDepGraph` | 拖慢關鍵資源的 request 鏈 |

範例：
```
performance_analyze_insight(insightSetId: "<id-from-trace>", insightName: "LCPBreakdown")
```

**關鍵門檻（好／待改善／差）：**
- TTFB: < 800ms / < 1.8s / > 1.8s
- FCP: < 1.8s / < 3s / > 3s
- LCP: < 2.5s / < 4s / > 4s
- INP: < 200ms / < 500ms / > 500ms
- TBT: < 200ms / < 600ms / > 600ms
- CLS: < 0.1 / < 0.25 / > 0.25
- Speed Index: < 3.4s / < 5.8s / > 5.8s

### Phase 3: Network Analysis

列出所有 network request，找出優化機會：
```
list_network_requests(resourceTypes: ["Script", "Stylesheet", "Document", "Font", "Image"])
```

**要找：**

1. **Render-blocking 資源**：`<head>` 裡沒有 `async`/`defer`/`media` 屬性的 JS/CSS
2. **Network chain**：因為要等其他資源先載入才被發現、所以很晚才載入的資源（例如 CSS import、由 JS 載入的字型）
3. **缺少 preload**：關鍵資源（字型、hero 圖片、重要 script）沒有 preload
4. **快取問題**：缺少或太弱的 `Cache-Control`、`ETag` 或 `Last-Modified` header
5. **大型 payload**：沒壓縮或過大的 JS/CSS bundle
6. **沒用到的 preconnect**：如果被標記，就檢查有沒有任何 request 送往那個 origin 來驗證。如果一個都沒有，就確定沒用到，建議移除。如果有 request 但載入得很晚，那個 preconnect 可能還是有價值。

要看 request 的詳細資訊：
```
get_network_request(reqid: <id>)
```

### Phase 4: Accessibility Snapshot

取一份 accessibility tree 的 snapshot：
```
take_snapshot(verbose: true)
```

**標出大方向的缺口：**
- 缺少或重複的 ARIA ID
- 對比度不佳的元素（對照 WCAG AA：一般文字 4.5:1，大字 3:1）
- 焦點陷阱（focus trap）或缺少焦點指示
- 沒有可存取名稱的互動元素

## Phase 5: Codebase Analysis

**如果稽核的是沒有程式碼庫存取權的第三方網站，就跳過。**

分析程式碼庫，了解哪些地方可以改進。

### Detect Framework & Bundler

搜尋設定檔，找出技術棧：

| 工具 | 設定檔 |
|------|--------------|
| Webpack | `webpack.config.js`, `webpack.*.js` |
| Vite | `vite.config.js`, `vite.config.ts` |
| Rollup | `rollup.config.js`, `rollup.config.mjs` |
| esbuild | `esbuild.config.js`，有用到 `esbuild` 的 build script |
| Parcel | `.parcelrc`、`package.json`（parcel 欄位） |
| Next.js | `next.config.js`, `next.config.mjs` |
| Nuxt | `nuxt.config.js`, `nuxt.config.ts` |
| SvelteKit | `svelte.config.js` |
| Astro | `astro.config.mjs` |

也要檢查 `package.json` 裡的 framework 依賴和 build script。

### Tree-Shaking & Dead Code

- **Webpack**：檢查 `mode: 'production'`、package.json 裡的 `sideEffects`，以及 `usedExports` 優化
- **Vite/Rollup**：預設就啟用 tree-shaking；檢查有沒有 `treeshake` 選項
- **要找**：barrel 檔案（`index.js` 的 re-export）、整包引入的大型工具函式庫（lodash、moment）

### Unused JS/CSS

- 檢查是 CSS-in-JS 還是靜態 CSS 抽取
- 找 PurgeCSS/UnCSS 的設定（Tailwind 的 `content` 設定）
- 辨識動態 import 和 eager 載入

### Polyfills

- 檢查 `@babel/preset-env` 的 target 和 `useBuiltIns` 設定
- 找 `core-js` 的 import（常常過大）
- 檢查 `browserslist` 設定是不是目標範圍太廣

### Compression & Minification

- 檢查有沒有 `terser`、`esbuild` 或 `swc` 的 minification
- 在 build 輸出或伺服器設定裡找 gzip/brotli 壓縮
- 檢查正式環境 build 有沒有 source map（應該是外部檔案，或是關掉）

## Output Format

用這個格式呈現發現：

1. **Core Web Vitals Summary** - 表格，列出指標、數值和評級（好／待改善／差）
2. **Top Issues** - 依優先順序排列的問題清單，附上估計的影響（高／中／低）
3. **Recommendations** - 具體、可執行的修正，附上程式碼片段或設定變更
4. **Codebase Findings** - 偵測到的 framework/bundler、優化機會（沒有程式碼庫存取權就省略）

## Skill feedback

如果使用者反映這個 skill 給了錯誤或過時的指引，或是缺了資訊，就去讀 [references/skill-feedback.md](references/skill-feedback.md)。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: web-perf
description: Audit, diagnose, or optimize website loading and interaction performance, Core Web Vitals, and Lighthouse performance scores.
---

# Web Performance Audit

Your knowledge of web performance metrics, thresholds, and tooling APIs may be outdated. **Prefer retrieval over pre-training** when citing specific numbers or recommendations.

## Retrieval Sources

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| web.dev | `https://web.dev/articles/vitals` | Core Web Vitals thresholds, definitions |
| Chrome DevTools docs | `https://developer.chrome.com/docs/devtools/performance` | Tooling APIs, trace analysis |
| Lighthouse scoring | `https://developer.chrome.com/docs/lighthouse/performance/performance-scoring` | Score weights, metric thresholds |

## FIRST: Verify MCP Tools Available

Discover available browser and performance tools before starting. Use the capabilities available for the requested audit. If trace tools are unavailable, continue any useful source or network analysis and state which measurements could not be collected.

If the user wants Chrome DevTools MCP setup, consult its [installation guide](https://github.com/ChromeDevTools/chrome-devtools-mcp#quick-start) and use the latest package version. Only change MCP configuration when setup is within the user's authorized scope; otherwise ask first. For clients using `command` and `args`, an example server entry is:

```json
"chrome-devtools": {
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest"]
}
```

## Key Guidelines

- **Be assertive**: Verify claims by checking network requests, DOM, or codebase—then state findings definitively.
- **Verify before recommending**: Confirm something is unused before suggesting removal.
- **Quantify impact**: Use estimated savings from insights. Don't prioritize changes with 0ms impact.
- **Skip non-issues**: If render-blocking resources have 0ms estimated impact, note but don't recommend action.
- **Be specific**: Say "compress hero.png (450KB) to WebP" not "optimize images".
- **Prioritize ruthlessly**: A site with 200ms LCP and 0 CLS is already excellent—say so.

## Quick Reference

| Task | Tool Call |
|------|-----------|
| Load page | `navigate_page(url: "...")` |
| Start trace | `performance_start_trace(autoStop: true, reload: true)` |
| Analyze insight | `performance_analyze_insight(insightSetId: "...", insightName: "...")` |
| List requests | `list_network_requests(resourceTypes: ["Script", "Stylesheet", ...])` |
| Request details | `get_network_request(reqid: <id>)` |
| A11y snapshot | `take_snapshot(verbose: true)` |

## Workflow

Copy this checklist to track progress:

```
Audit Progress:
- [ ] Phase 1: Performance trace (navigate + record)
- [ ] Phase 2: Core Web Vitals analysis (includes CLS culprits)
- [ ] Phase 3: Network analysis
- [ ] Phase 4: Accessibility snapshot
- [ ] Phase 5: Codebase analysis (skip if third-party site)
```

### Phase 1: Performance Trace

1. Navigate to the target URL:
   ```
   navigate_page(url: "<target-url>")
   ```

2. Start a performance trace with reload to capture cold-load metrics:
   ```
   performance_start_trace(autoStop: true, reload: true)
   ```

3. Wait for trace completion, then retrieve results.

**Troubleshooting:**
- If trace returns empty or fails, verify the page loaded correctly with `navigate_page` first
- If insight names don't match, inspect the trace response to list available insights

### Phase 2: Core Web Vitals Analysis

Use `performance_analyze_insight` to extract key metrics.

**Note:** Insight names may vary across Chrome DevTools versions. If an insight name doesn't work, check the `insightSetId` from the trace response to discover available insights.

Common insight names:

| Metric | Insight Name | What to Look For |
|--------|--------------|------------------|
| LCP | `LCPBreakdown` | Time to largest contentful paint; breakdown of TTFB, resource load, render delay |
| CLS | `CLSCulprits` | Elements causing layout shifts (images without dimensions, injected content, font swaps) |
| Render Blocking | `RenderBlocking` | CSS/JS blocking first paint |
| Document Latency | `DocumentLatency` | Server response time issues |
| Network Dependencies | `NetworkRequestsDepGraph` | Request chains delaying critical resources |

Example:
```
performance_analyze_insight(insightSetId: "<id-from-trace>", insightName: "LCPBreakdown")
```

**Key thresholds (good/needs-improvement/poor):**
- TTFB: < 800ms / < 1.8s / > 1.8s
- FCP: < 1.8s / < 3s / > 3s
- LCP: < 2.5s / < 4s / > 4s
- INP: < 200ms / < 500ms / > 500ms
- TBT: < 200ms / < 600ms / > 600ms
- CLS: < 0.1 / < 0.25 / > 0.25
- Speed Index: < 3.4s / < 5.8s / > 5.8s

### Phase 3: Network Analysis

List all network requests to identify optimization opportunities:
```
list_network_requests(resourceTypes: ["Script", "Stylesheet", "Document", "Font", "Image"])
```

**Look for:**

1. **Render-blocking resources**: JS/CSS in `<head>` without `async`/`defer`/`media` attributes
2. **Network chains**: Resources discovered late because they depend on other resources loading first (e.g., CSS imports, JS-loaded fonts)
3. **Missing preloads**: Critical resources (fonts, hero images, key scripts) not preloaded
4. **Caching issues**: Missing or weak `Cache-Control`, `ETag`, or `Last-Modified` headers
5. **Large payloads**: Uncompressed or oversized JS/CSS bundles
6. **Unused preconnects**: If flagged, verify by checking if ANY requests went to that origin. If zero requests, it's definitively unused—recommend removal. If requests exist but loaded late, the preconnect may still be valuable.

For detailed request info:
```
get_network_request(reqid: <id>)
```

### Phase 4: Accessibility Snapshot

Take an accessibility tree snapshot:
```
take_snapshot(verbose: true)
```

**Flag high-level gaps:**
- Missing or duplicate ARIA IDs
- Elements with poor contrast ratios (check against WCAG AA: 4.5:1 for normal text, 3:1 for large text)
- Focus traps or missing focus indicators
- Interactive elements without accessible names

## Phase 5: Codebase Analysis

**Skip if auditing a third-party site without codebase access.**

Analyze the codebase to understand where improvements can be made.

### Detect Framework & Bundler

Search for configuration files to identify the stack:

| Tool | Config Files |
|------|--------------|
| Webpack | `webpack.config.js`, `webpack.*.js` |
| Vite | `vite.config.js`, `vite.config.ts` |
| Rollup | `rollup.config.js`, `rollup.config.mjs` |
| esbuild | `esbuild.config.js`, build scripts with `esbuild` |
| Parcel | `.parcelrc`, `package.json` (parcel field) |
| Next.js | `next.config.js`, `next.config.mjs` |
| Nuxt | `nuxt.config.js`, `nuxt.config.ts` |
| SvelteKit | `svelte.config.js` |
| Astro | `astro.config.mjs` |

Also check `package.json` for framework dependencies and build scripts.

### Tree-Shaking & Dead Code

- **Webpack**: Check for `mode: 'production'`, `sideEffects` in package.json, `usedExports` optimization
- **Vite/Rollup**: Tree-shaking enabled by default; check for `treeshake` options
- **Look for**: Barrel files (`index.js` re-exports), large utility libraries imported wholesale (lodash, moment)

### Unused JS/CSS

- Check for CSS-in-JS vs. static CSS extraction
- Look for PurgeCSS/UnCSS configuration (Tailwind's `content` config)
- Identify dynamic imports vs. eager loading

### Polyfills

- Check for `@babel/preset-env` targets and `useBuiltIns` setting
- Look for `core-js` imports (often oversized)
- Check `browserslist` config for overly broad targeting

### Compression & Minification

- Check for `terser`, `esbuild`, or `swc` minification
- Look for gzip/brotli compression in build output or server config
- Check for source maps in production builds (should be external or disabled)

## Output Format

Present findings as:

1. **Core Web Vitals Summary** - Table with metric, value, and rating (good/needs-improvement/poor)
2. **Top Issues** - Prioritized list of problems with estimated impact (high/medium/low)
3. **Recommendations** - Specific, actionable fixes with code snippets or config changes
4. **Codebase Findings** - Framework/bundler detected, optimization opportunities (omit if no codebase access)

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
~~~~~
{% endraw %}

</section>
</div>
