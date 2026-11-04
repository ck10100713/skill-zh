---
name: brand
description: 品牌語調、視覺識別、訊息框架、素材管理、品牌一致性。處理品牌內容、語氣、行銷素材、品牌合規與風格指南時啟動。
argument-hint: "[update|review|create] [args]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# Brand

品牌識別、語調、訊息、素材管理與一致性框架。

## 何時使用

- 定義品牌語調與內容語氣指引
- 視覺識別標準與風格指南的制定
- 建立訊息框架
- 品牌一致性的審查與稽核
- 素材的整理、命名與核准
- 色彩調色盤管理與字體規格

## Script 路徑

這個 skill 及其 `references/` 裡的 script 路徑，都是相對於包含這個 SKILL.md 的目錄，不是相對於專案：`scripts/<file>` 指這個 skill 自己的 `scripts/` 資料夾，`../<skill>/scripts/<file>` 指跟它一起安裝的同層子 skill。請從那個目錄組出完整路徑（skill 載入時 Claude Code 會回報它的 base directory），而且工作目錄要維持在專案根目錄，因為 script 會讀寫相對於它的專案檔案，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`。

## 快速開始

**把品牌脈絡注入 prompt：**
```bash
node scripts/inject-brand-context.cjs
node scripts/inject-brand-context.cjs --json
```

**驗證素材：**
```bash
node scripts/validate-asset.cjs <asset-path>
```

**擷取／比較顏色：**
```bash
node scripts/extract-colors.cjs --palette
node scripts/extract-colors.cjs <image-path>
```

## 品牌同步流程

```bash
# 1. Edit docs/brand-guidelines.md (or use /brand update)
# 2. Sync to design tokens
node scripts/sync-brand-to-tokens.cjs
# 3. Verify
node scripts/inject-brand-context.cjs --json | head -20
```

如果同步時在常見的 CSS 進入點及其本地 CSS import 裡，偵測到既有的 token 檔、`:root` 自訂屬性或 Tailwind v4 `@theme` 變數，或偵測到 Tailwind 的主題色彩與 preset，同步就會停下來。繼續之前，先檢查回報的來源。如果偵測到的檔案是前一次同步產生、由工具管理的 `assets/design-tokens.*` 輸出，而且你確定要取代它們，就加上 `--force` 重跑。

**同步的檔案：**
- `docs/brand-guidelines.md` → 唯一事實來源（Source of truth）
- `assets/design-tokens.json` → Token 定義
- `assets/design-tokens.css` → CSS 變數

## 子指令

| 子指令 | 說明 | 參考 |
|------------|-------------|-----------|
| `update` | 更新品牌識別，並同步到所有設計系統 | `references/update.md` |

## 參考資料

| 主題 | 檔案 |
|-------|------|
| 語調框架 | `references/voice-framework.md` |
| 視覺識別 | `references/visual-identity.md` |
| 訊息 | `references/messaging-framework.md` |
| 一致性 | `references/consistency-checklist.md` |
| 規範範本 | `references/brand-guideline-template.md` |
| 素材整理 | `references/asset-organization.md` |
| 色彩管理 | `references/color-palette-management.md` |
| 字體 | `references/typography-specifications.md` |
| Logo 使用 | `references/logo-usage-rules.md` |
| 核准檢查表 | `references/approval-checklist.md` |

## Scripts

| Script | 用途 |
|--------|---------|
| `scripts/inject-brand-context.cjs` | 擷取品牌脈絡，用於 prompt 注入 |
| `scripts/sync-brand-to-tokens.cjs` | 把 brand-guidelines.md 同步成 design-tokens.json/css |
| `scripts/validate-asset.cjs` | 驗證素材的命名、大小、格式 |
| `scripts/extract-colors.cjs` | 擷取顏色並與調色盤比較 |

## 範本

| 範本 | 用途 |
|----------|---------|
| `templates/brand-guidelines-starter.md` | 新品牌用的完整起始範本 |

## 路由

1. 從 `$ARGUMENTS` 解析子指令（第一個字）
2. 載入對應的 `references/{subcommand}.md`
3. 用剩下的參數執行
