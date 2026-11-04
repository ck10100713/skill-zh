---
name: visual-pr
description: 只有在使用者明確用名稱呼叫這個 skill 時才使用。
---

# Describe a Pull Request

替目前任務建立或更新 pull request，寫一份精簡的描述，幫 reviewer 理解這個改動為什麼存在，以及實作的整體形狀。

## 工作流程

1. 讀描述範本：

   `Read({SKILLBASE}/references/pr_description_template.md)`

2. 找出或建立 pull request：
   - 用 `gh pr view --json url,number,title,state,baseRefName,headRefName 2>/dev/null` 檢查目前的 branch 有沒有 PR。
   - 如果沒有 PR，檢查 `git status --short --branch` 和目前 branch 上的 commit。
   - 需要的話先 commit 跟任務相關的改動，把 branch 連同 upstream 一起 push，並為它建立 PR。遵循該 repo 的 git 安全守則。
   - 只有在目前的 branch 上沒有相關的工作、而且沒有可以安全建立的目前 branch PR 時，才請使用者選一個 PR。

3. 只蒐集解釋這個改動所需的 context：
   - 讀 ticket 和任何相關的任務 artifact。
   - 讀完整的 PR diff，以及足夠的周邊程式碼來理解行為和歸屬。
   - 用 `gh pr view` 取得 PR 的 metadata 和改動的檔案。
   - 讀 `{SKILLBASE}/references/show-me.md`，了解 PR 內文所用的視覺化大綱慣例。

4. 用範本寫 PR 描述：
   - **Why the change** 剛好一句話。
   - **Special things to note** 1 到 3 個重點。優先放 reviewer 要注意的警告、migration、相容性限制、刻意省略的東西，或令人意外的決定。沒有特別要考慮的事項時，寫 `- None.`。
   - 讓 **Change outline** 是精簡的、受 `/show-me` 啟發的結構化視圖，不是散文，也不是逐檔案的 changelog。
   - 只放有助於解釋這個 PR 的視圖：
     - SQL table 和 endpoint 契約的改動，加上商業邏輯的 pseudocode。
     - 重要的資料結構 / 型別改動
     - 一棵淺層的檔案樹，呈現改動後的職責。
     - React 元件樹的改動，包含重要的 hook、state 和 package 邊界。
     - Call tree、call stack、控制流程或資料流的改動。
   - 呈現對既有形狀的改動時，優先用 `diff` 區塊。大部分內容都是新的，或 diff 的寫法會讓歸屬或順序變模糊時，呈現完整的目標形狀。
   - 每個視圖都聚焦在 reviewer 需要的東西。沒有改動的類別就省略。
   - 選用：如果你知道 ticket id/url、humanlayer 任務 url、相關的計畫/文件 url，或其他相關連結，就放在標頭；否則省略標頭

5. 儲存並發布描述：
   - 任務目錄存在的話，用 `.humanlayer/tasks/{task-slug}/pr-description.md`；否則用 `.humanlayer/tasks/pr-{number}/description.md`。
   - 用 `gh pr edit {number} --body-file {output-path}` 更新 PR。
   - 確認更新成功。

6. 回報完成：
   - 讀 `{SKILLBASE}/references/describe_pr_final_answer.md`。
   - 用那份最終回答範本回應，附上 PR URL、儲存的描述 URL，以及精簡的改動檔案清單。

一定要讀並遵守 `{SKILLBASE}/references/pr_description_template.md`。PR 內文不要超出那份範本的範圍。

像一個人對另一個人說話那樣寫：避免行話和俚語，用簡單、連貫、精簡的語言。
