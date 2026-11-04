---
name: wiki-qa
description: 透過原始檔案分析來回答關於程式碼 repository 的問題。適用於使用者問某個東西怎麼運作、想理解某個元件，或需要協助瀏覽程式碼庫時。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Wiki Q&A

完全以原始碼的證據為基礎，回答關於 repository 的問題。

## 什麼時候啟動

- 使用者問關於程式碼庫的問題
- 使用者想理解特定的檔案、function 或元件
- 使用者問「how does X work」或「where is Y defined」

## 解析來源 Repository（一定要先做）

回答任何問題之前，你一定要先確定來源 repository 的背景：

1. **檢查 git remote**：執行 `git remote get-url origin` 偵測是否有 remote
2. **問使用者**：_"這是只在本機的 repository，還是你有來源 repository 的 URL（例如 GitHub、Azure DevOps）？"_
   - 有提供遠端 URL → 存成 `REPO_URL`，使用**帶連結的引用**：`[file:line](REPO_URL/blob/BRANCH/file#Lline)`
   - 只在本機 → 使用**本機引用**：`(file_path:line_number)`
3. **決定預設 branch**：執行 `git rev-parse --abbrev-ref HEAD`
4. 來源 repo 的背景沒解析清楚之前，**不准繼續**

## 步驟

1. 解析來源 repo 的背景（見上方）
2. 偵測問題的語言，用同一種語言回答
3. 在程式碼庫裡搜尋相關檔案
4. 讀那些檔案來蒐集證據
5. 綜合出答案，並附上 inline 帶連結的引用

## 回應格式

- 使用 `##` 標題、帶語言標記的 code block、表格、條列清單
- 用解析出來的格式 inline 引用來源：
  - **遠端**：`[src/path/file.ts:42](REPO_URL/blob/BRANCH/src/path/file.ts#L42)`
  - **本機**：`(src/path/file.ts:42)`
- 包含一張「Key Files」表格，把檔案對應到它們的角色（「File」欄要帶連結引用）
- 當答案涉及架構、資料流或關聯時，**至少放 1 張 Mermaid 圖**：一張圖能讓答案的用處大 10 倍
- 答案裡任何結構化的資料（元件清單、API endpoint、設定選項、比較）都**用表格**
- 如果資訊不足，就直說，並建議要檢視哪些檔案

## 規則

- **只**使用實際原始檔案裡的資訊
- **絕對不要**捏造、猜測或使用外部知識
- 回答之前要一步一步思考
