---
name: wiki-changelog
description: 分析 git commit 歷史，產生依變更類型分類的結構化 changelog。適用於使用者問最近改了什麼、想要 changelog，或需要了解 repository 有什麼變動時。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Wiki Changelog

從 git 歷史產生結構化的 changelog。

## 解析來源 Repository（一定要先做）

產生任何 changelog 之前，你一定要先確定來源 repository 的背景：

1. **檢查 git remote**：執行 `git remote get-url origin` 偵測是否有 remote
2. **問使用者**：_"這是只在本機的 repository，還是你有來源 repository 的 URL（例如 GitHub、Azure DevOps）？"_
   - 有提供遠端 URL → 存成 `REPO_URL`，對 commit hash 和檔案參照使用**帶連結的引用**
   - 只在本機 → 使用純文字的 commit hash 和檔案參照
3. 來源 repo 的背景沒解析清楚之前，**不准繼續**

## 什麼時候啟動

- 使用者問「what changed recently」、「generate a changelog」、「summarize commits」
- 使用者想了解最近的開發活動

## 步驟

1. 檢視 git log（commit、日期、作者、訊息）
2. 依時間區間分組：每天（最近 7 天）、每週（更早的）
3. 分類每個 commit：Features（🆕）、Fixes（🐛）、Refactoring（🔄）、Docs（📝）、Config（🔧）、Dependencies（📦）、Breaking（⚠️）
4. 用專案的術語，產生簡潔、面向使用者的描述

## 限制

- 聚焦在面向使用者的變更
- 把相關的 commit 合併成連貫的描述
- 使用 README 裡的專案術語
- 醒目標示 breaking change，並附上遷移說明
- 有 `REPO_URL` 時，要幫 commit hash 加連結：`[abc1234](REPO_URL/commit/abc1234)`，變更的檔案也要：`[file_path](REPO_URL/blob/BRANCH/file_path)`
