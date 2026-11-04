---
name: app-store-preflight-skills
description: >
  在送審之前，掃描 iOS/macOS Xcode 專案裡常見的 App Store 被拒模式。
  準備 App Store 審核、收到 Apple 的退件、或稽核 metadata、訂閱、privacy manifest、
  entitlement、設計合規時使用。整合 asc CLI 來檢視 metadata。
metadata:
  author: truongduy2611
  version: "1.1"
  guidelines-synced: "2026-10-16"
---

# App Store Preflight Skill

對你的 iOS/macOS 專案做送審前檢查，抓出常見的 App Store 被拒模式。

## 前置需求

- **asc CLI**：用 Homebrew 安裝：`brew install asc`（[App-Store-Connect-CLI](https://github.com/rudrankriyam/App-Store-Connect-CLI)）
- **ASC CLI Skills**：[app-store-connect-cli-skills](https://github.com/rudrankriyam/app-store-connect-cli-skills)，裡面有 `asc` 的用法
- **jq**：可選，但規則文件裡有些 JSON 檢視範例會用到

## Step 1：判斷 App 類型 → 載入檢查清單

從 `references/guidelines/by-app-type/` 載入相關的檢查清單，判斷哪些準則適用。一律先從 `all_apps.md` 開始，再加上該 App 類型專屬的那份：

| App 類型 | 檢查清單 |
|----------|-----------|
| 所有 app | `references/guidelines/by-app-type/all_apps.md` |
| 訂閱 / IAP | `references/guidelines/by-app-type/subscription_iap.md` |
| 社群 / UGC | `references/guidelines/by-app-type/social_ugc.md` |
| 兒童類別 | `references/guidelines/by-app-type/kids.md` |
| 健康與健身 | `references/guidelines/by-app-type/health_fitness.md` |
| 遊戲 | `references/guidelines/by-app-type/games.md` |
| macOS | `references/guidelines/by-app-type/macos.md` |
| AI / 生成式 AI | `references/guidelines/by-app-type/ai_apps.md` |
| 加密貨幣與金融 | `references/guidelines/by-app-type/crypto_finance.md` |
| VPN | `references/guidelines/by-app-type/vpn.md` |

完整的準則索引：`references/guidelines/README.md`

## Step 2：拉取 Metadata 來檢視

用 `asc` CLI 拉取最新的 App Store metadata：

```bash
# Pull canonical metadata JSON for the version you want to review
asc metadata pull --app "<APP_ID>" --version "<VERSION>" --dir ./metadata
```

`asc metadata pull` 會把 app info 檔寫到 `./metadata/app-info/*.json`，把版本在地化檔寫到 `./metadata/version/<VERSION>/*.json`。

下面大多數的規則範例，都假設用的是 `asc metadata pull` 寫出來的標準 JSON 版面。

創意素材（產品頁面標頭、搜尋結果素材；Guideline 2.3.14）放在 App Store Connect 的 Asset Library。如果你的 `asc` 版本拉不下來，就照 2.3.14 手動審查。

如果你的 metadata 已經是別的版面（例如 fastlane 的 `metadata/`），要嘛把檔案路徑範例改成適用你的結構，要嘛先拉一份標準的 `asc` 版面。

## Step 3：執行被拒規則檢查

每個類別都從 `references/rules/` 載入相關的規則檔來檢查。每條規則都包含：**What to Check**、**How to Detect**、**Resolution** 和 **Example Rejection**。

| 類別 | 規則檔 |
|----------|------------|
| Metadata | `references/rules/metadata/*.md` |
| 訂閱 | `references/rules/subscription/*.md` |
| 隱私 | `references/rules/privacy/*.md` |
| 設計 | `references/rules/design/*.md` |
| Entitlements | `references/rules/entitlements/*.md` |

## Step 4：回報發現

用這個範本產出摘要報告：

```markdown
## Preflight Report

### ❌ Rejections Found (N)
- [GUIDELINE X.X.X] Description of issue
  - File: path/to/offending/file
  - Fix: What to do

### ⚠️ Warnings (N)
- [GUIDELINE X.X.X] Potential issue

### ✅ Passed (N)
- [Category] All checks passed
```

依嚴重程度排序：先列被拒，再列警告，最後列通過。

## Step 5：自動修復 + 驗證

有些問題可以自動修復：
- **競品名稱** → 建議把競品名稱拿掉的替換文字
- **Metadata 字數上限** → 顯示目前長度和上限
- **缺少連結** → 產生 ToS/PP URL 的範本

套用任何自動修復之後，**重新執行受影響的檢查**，確認違規真的解決了。重新掃描通過才標記為已解決。

需要人工處理的問題（截圖、UI 重新設計），給清楚的指示，但不要自動修復。

## 常見陷阱

- **中國 storefront**：被禁的 AI 名詞（ChatGPT、Gemini 等）要在所有 locale 檢查，不只是 `zh-Hans`。Apple 會檢查中國 storefront 看得到的每個 locale。
- **Privacy manifest**：就算你的 app 沒有直接呼叫 Required Reason API，也一定要有 `PrivacyInfo.xcprivacy`。用到 `UserDefaults` 或 `NSFileManager` 的第三方 SDK（Firebase、Amplitude 等）會連帶觸發這個要求。
- **asc 驗證**：`asc metadata pull` 需要 App Store Connect 驗證。先執行 `asc auth login`，或設定 `ASC_KEY_ID`、`ASC_ISSUER_ID`，以及 `ASC_PRIVATE_KEY_PATH` / `ASC_PRIVATE_KEY` / `ASC_PRIVATE_KEY_B64` 其中之一。不確定 `asc` 抓到什麼的話，執行 `asc auth doctor`。
- **訂閱 metadata**：Apple 要求 ToS/PP 連結同時出現在 App Store 描述和 app 內的訂閱購買畫面。缺任何一個都是另外一次被拒。
- **隱藏功能（2.5.19）**：Feature flag 是允許的，但它能開啟的每個功能都必須在送審的 build 裡、審核人員找得到，而且要寫在審核備註裡。用審核環境檢查（sandbox receipt、TestFlight）來控制功能，屬於 bait-and-switch，開發者帳號可能因此被終止。
- **第三方 AI（5.1.2(i)）**：把 AI 呼叫經過自己的後端代理，並不能免責：只要 prompt 或使用者內容會送到 OpenAI、Gemini、Anthropic 等，app 就必須在第一次請求*之前*，先有指名該供應商的同意畫面。
- **Sign in with Apple relay domain**：新的 relay 地址除了 `privaterelay.appleid.com` 之外，也會使用 `private.icloud.com`（2026 年底起）。寫死網域的檢查會讓新使用者出問題。
- **SDK 最低版本**：上傳的 build 必須用 iOS 26 SDK 或更新版本（2026 年 4 月 28 日起）。太舊的 Xcode 會在上傳時失敗，不是等到審核。
- **macOS entitlements**：Apple 會要你說明每一個 temporary exception entitlement（`com.apple.security.temporary-exception.*`）的理由。用不到的 entitlement 就拿掉。

## 新增規則

在 `references/rules/` 適當的子目錄裡建一個 `.md` 檔：

```markdown
# Rule: [Short Title]
- **Guideline**: [Apple Guideline Number]
- **Severity**: REJECTION | WARNING
- **Category**: metadata | subscription | privacy | design | entitlements

## What to Check
## How to Detect
## Resolution
## Example Rejection
```
