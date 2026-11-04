---
name: slides
description: 用 Chart.js、design token、響應式版面、文案公式和情境化的投影片策略，製作有策略的 HTML 簡報。
argument-hint: "[topic] [slide-count]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# Slides

結合資料視覺化的策略性 HTML 簡報設計。

## 何時使用

- 行銷簡報和 pitch deck
- 用 Chart.js 做資料驅動的投影片
- 搭配版面模式的策略性投影片設計
- 針對文案優化的簡報內容

## 子指令

| 子指令 | 說明 | 參考 |
|------------|-------------|-----------|
| `create` | 建立有策略的簡報投影片 | `references/create.md` |

## Script 路徑

這個 skill 及其 `references/` 裡的 script 路徑，都是相對於包含這個 SKILL.md 的目錄，不是相對於專案：`scripts/<file>` 指這個 skill 自己的 `scripts/` 資料夾，`../<skill>/scripts/<file>` 指跟它一起安裝的同層子 skill。請從那個目錄組出完整路徑（skill 載入時 Claude Code 會回報它的 base directory），而且工作目錄要維持在專案根目錄，因為 script 會讀寫相對於它的專案檔案，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`。

## 參考資料（知識庫）

| 主題 | 檔案 |
|-------|------|
| 版面模式 | `references/layout-patterns.md` |
| HTML 範本 | `references/html-template.md` |
| 文案公式 | `references/copywriting-formulas.md` |
| 投影片策略 | `references/slide-strategies.md` |

## 路由

1. 從 `$ARGUMENTS` 解析子指令（第一個字）
2. 載入對應的 `references/{subcommand}.md`
3. 用剩下的參數執行
