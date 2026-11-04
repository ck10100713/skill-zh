---
name: rpi
description: 只有在使用者明確用名稱呼叫這個 skill 時才使用。
---

# Research, Design, and Implement

幫使用者研究一個改動、把設計想清楚，然後實作出來。依照使用者要求的步驟，使用下面的各階段指示。

`$SKILLBASE` 指的是包含這個 `SKILL.md` 的目錄。

範本裡的 `<rpi-invocation>` 指的是 host 的 skill 指令：Codex 是 `$rpi`，Claude Code 是 `/rpi`，host 有提供的話則是它加上 plugin 前綴的名稱。把後續的指令用這個原生的呼叫方式輸出。

## 選擇步驟

依照使用者要求的步驟。要選擇或說明流程、或接下來是什麼的時候，讀 `$SKILLBASE/references/workflow.md`。

如果只有任務描述、沒有指定步驟，就從研究問題開始。問使用者想走哪種流程：研究後接設計討論、PRD 或 TDD，或只做研究。等他們選好再開始那個階段，然後把選擇帶進建議的下一個指令。

請使用者選擇流程時，讀 `$SKILLBASE/references/workflow-choice.md`，並把它的方框連線圖連同問題一起顯示。

Create 會寫一份新文件；iterate 則是依使用者的回饋就地更新既有文件，或是接續一份做到一半的文件的流程。

從 `$SKILLBASE/references/<step>/process.md` 載入對應的流程：

| 請求 | 步驟 |
| --- | --- |
| 研究問題 | `create-research-questions` 或 `iterate-research-questions` |
| 研究 | `create-research` 或 `iterate-research` |
| 設計討論 | `create-design-discussion` 或 `iterate-design-discussion` |
| 產品需求 / PRD | `create-prd` 或 `iterate-prd` |
| 技術設計 / TDD | `create-tdd` 或 `iterate-tdd` |
| 實作大綱 | `create-structure-outline` 或 `iterate-structure-outline` |
| 實作 | `implement-outline` |
| 實作的回饋或修正 | `iterate-implementation` |

預設更新既有文件；需要或被要求時才建新的。有多份符合時，用最新的那份，並說明選了哪個檔案。

## 使用任務目錄

使用者有給目錄就用那個。

否則，在 `.agents/artifacts/` 裡找既有的任務目錄，名稱和 workflow 檔名要跟請求或目前任務的 branch 相符。明顯符合的就直接重用，不用問。如果目錄看起來接近、但可能屬於別的任務，或有好幾個看起來都合理，寫入之前先問使用者要用哪個。檢查是否符合時，只讀所選階段允許讀的文件。

沒有符合的現有目錄時，如果 branch 能辨識出任務，就用 `.agents/artifacts/<branch-name>`，把 `/` 換成 `-`。在 `main` 上，或沒有 branch 能辨識任務時，從請求挑一個簡短的 kebab-case slug，用 `.agents/artifacts/<task-slug>`，不用問是否同意。說明選了哪個路徑，並視需要重用或建立目錄。

存在選定的路徑。如果 sandbox 擋住那裡的寫入，就請求限定範圍的寫入權限，或要一個可寫的任務目錄，然後等使用者決定。

RPI 框架的作者建議不要 commit 這些 artifact。

新的 workflow 文件，用任務目錄裡下一個可用的 `NN-` 前綴編號。更新文件時維持原有路徑。把輔助的 mockup 和圖表存在文件旁邊，當作一般的本機檔案連結。

Workflow 文件的 frontmatter 包含 `repos`，是零個或多個 repo 的清單，每個項目有 `identifier` 和 `sha`。沒有適用的就用 `repos: []`。字串值視需要加引號，確保是合法的 YAML。

## Review 文件

寫完或更新 workflow 文件之後，讀 `$SKILLBASE/references/prose.md` 和 `$SKILLBASE/references/show-me.md`，然後依這兩份來 review 文件。讓它更短、更視覺化、更容易讓人消化：砍掉沒有存在價值的字和段落，用能講清楚重點的最小視圖取代密集的文字，並讓每個視覺元素緊貼著它所支持的簡短文字。

## 建議下一步

用該階段的交接指示和 `$SKILLBASE/references/workflow.md` 來決定接下來做什麼。使用者預設每個階段都在獨立的 context window 裡執行。建議下一個指令時，要附上任務目錄和選定的流程。並說明他們可以在這裡跑、在 compaction 之後跑，或開新的 session 跑。

被問到下一步是什麼時，用 artifact 的檔名找出目前的階段，然後讀它的文件，看有什麼未完成的工作和已定案的選擇。要能辨識 `prd` 或 `product-requirements`、`tdd` 或 `tech-design`，以及 `structure-outline` 或 `outline`。

## 使用 Subagent

依各階段的指示，使用隨附的 `codebase-locator`、`codebase-analyzer`、`codebase-pattern-finder`、`web-search-researcher` 和 `outline-implementer-agent` 的 agent 指示。

<important if="you do not have an Agent() or Task() or other tool for running subagents">
  read the subagent instructions from $SKILLBASE/references/subagents/SUBAGENT_NAME.md
</important>

<important if="you have a tool for running subagents or delegated sessions, but the named subagents are not available">
  read the subagent instructions from $SKILLBASE/references/subagents/SUBAGENT_NAME.md and pass them into the subagent with your main prompt, with
<instructions>
REFERENCE_CONTENTS
</instructions>
<message>
YOUR_MESSAGE ON WHAT TO LOOK FOR OR BUILD
</message>
</important>
