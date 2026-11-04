---
name: "mkt-seo-audit"
description: "進行技術面與頁面內（on-page）的 SEO 稽核，涵蓋可爬取性、網站速度、行動裝置友善度和內容最佳化。使用者需要改善搜尋排名、診斷流量下滑、稽核網站的 SEO 問題，或規劃 SEO 策略時使用，就算他們說的是「為什麼我們的流量在掉」、「稽核我們的 SEO」、「我們怎麼在 Google 排得更前面」或「我們的網站很慢」也一樣。"
metadata:
  category: "WP-09 數位行銷"
  tags: ["digital-marketing", "seo", "technical-seo", "audit"]
---

# SEO 稽核

## 框架

```
IRON LAW: Technical Foundation Before Content Optimization

A site with brilliant content but broken crawlability, slow speed, or
no mobile support will not rank. Fix technical issues FIRST, then optimize
content. A technically sound site with mediocre content outranks a
technically broken site with great content.

Priority: Crawlability → Speed → Mobile → On-Page → Content → Links
```

### 稽核檢查表

**1. 可爬取性與索引**
| 檢查項目 | 工具 | 警訊 |
|-------|------|----------|
| robots.txt 擋住重要頁面 | robots.txt 測試工具 | 在關鍵頁面上設了 Disallow |
| Sitemap.xml 存在且有效 | XML sitemap 驗證工具 | 缺少或有錯誤 |
| 索引涵蓋範圍 | Google Search Console | 被排除的頁面持續增加 |
| Canonical 標籤正確 | 人工檢查 | 缺少或指向錯誤的 URL |
| 404 錯誤 | Screaming Frog / GSC | 超過 5% 的 URL 回傳 404 |
| 轉址鏈 | Screaming Frog | 鏈長超過 2 跳 |

**2. 網站速度（Core Web Vitals）**
| 指標 | 目標 | 工具 |
|--------|--------|------|
| LCP（Largest Contentful Paint） | < 2.5s | PageSpeed Insights |
| INP（Interaction to Next Paint） | < 200ms | PageSpeed Insights |
| CLS（Cumulative Layout Shift） | < 0.1 | PageSpeed Insights |

**3. 行動裝置友善度**
- 響應式設計（通過 Google 行動裝置友善測試）
- 觸控目標 > 48px
- 沒有水平捲動
- 不用縮放就能讀的文字

**4. 頁面內 SEO（每一頁）**
| 元素 | 最佳實務 |
|---------|-------------|
| Title 標籤 | 主要關鍵字 + 品牌，< 60 字元 |
| Meta description | 有吸引力、包含關鍵字，< 155 字元 |
| H1 | 每頁一個，包含主要關鍵字 |
| URL 結構 | 簡短、有描述性、包含關鍵字 |
| 圖片 alt 文字 | 有描述性，自然地包含關鍵字 |
| 內部連結 | 連到相關頁面，並使用有描述性的錨點文字 |

**5. 內容品質**
- 關鍵字鎖定：每個重要頁面都鎖定一個主要關鍵字
- 內容深度：全面涵蓋主題（不是薄弱內容）
- E-E-A-T 訊號：經驗（Experience）、專業（Expertise）、權威（Authoritativeness）、可信度（Trustworthiness）
- 新鮮度：關鍵內容在過去 12 個月內有更新

**6. 反向連結概況**
- 參照網域總數（Ahrefs、Moz）
- 網域權威／網域評級
- 有毒連結（垃圾、不相關）
- 錨點文字分布（自然 vs 過度最佳化）

## 輸出格式

```markdown
# SEO Audit: {Website}

## Summary
| Category | Score | Priority Issues |
|----------|-------|----------------|
| Crawlability | 🟢/🟡/🔴 | {top issue} |
| Speed | 🟢/🟡/🔴 | {top issue} |
| Mobile | 🟢/🟡/🔴 | {top issue} |
| On-Page | 🟢/🟡/🔴 | {top issue} |
| Content | 🟢/🟡/🔴 | {top issue} |
| Backlinks | 🟢/🟡/🔴 | {top issue} |

## Critical Issues (fix immediately)
1. {issue + impact + fix}

## High Priority (fix within 30 days)
1. {issue + fix}

## Opportunities
1. {keyword/content opportunity}

## Action Plan
| Priority | Action | Impact | Effort | Timeline |
|----------|--------|--------|--------|----------|
| 1 | {action} | H/M/L | H/M/L | {weeks} |
```

## 注意事項

- **SEO 成效要 3-6 個月才會顯現**：不要期待幾週內就看到排名變化。要以季為單位衡量，不是以天。
- **Google Search Console 才是事實來源**：第三方工具是估算。GSC 顯示的是 Google 實際的資料（點擊、曝光、索引狀態）。
- **Core Web Vitals 是排名因素**：自 2021 年起，Google 把頁面體驗（速度、互動性、視覺穩定性）當作排名訊號。不是可有可無。
- **AI 生成的內容**：Google 本身不會因為是 AI 內容就懲罰，但不管內容是怎麼產生的，低品質、沒幫助的內容都會被懲罰。E-E-A-T 很重要。
- **台灣的在地 SEO**：對在地商家來說，Google 我的商家（Google Business Profile）至關重要。先把 GBP 最佳化，再去煩惱自然搜尋排名。

## 參考資料

- 關鍵字研究方法論請看 `references/keyword-research.md`
- 內容最佳化指南請看 `references/content-seo.md`
