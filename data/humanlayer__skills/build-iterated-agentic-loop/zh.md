---
name: build-iterated-agentic-loop
description: 建立一個 repo 專用的 skill，並安裝配套的迭代式 coding agent GitHub Actions workflow、prompt、memory 檔案和參考範本
---

# Build Iterated Agentic Loop

使用者想把一個可重複的 agent 任務，變成 repo 專用的 skill 加上一個 GitHub Actions workflow，讓 coding agent 定時跑、手動跑，或兩者都有，就用這個 skill。

目標的形狀是迭代式 agentic loop：一個聚焦的 skill 定義 agent 的判斷方式，一個 workflow 用 repo 專屬的 prompt 去呼叫 coding agent，一個 agent-memory 檔案在每次執行之間帶著長期的回饋，而且每個 workflow 都會替自己開的 PR 加 label，讓每個 loop 同時只會有一個開著的 PR。`narrow-react-prop-types` skill 就是具體的參考範例。

## 產出

在目標 repo 建立或更新這些檔案：

- `.claude/skills/<skill-name>/SKILL.md`：repo 專用的 agent 行為。
- `.github/workflows/agent-<task-name>.yml`：定期執行的 coding-agent 自動化。
- `.github/agent-memory/<task-name>.md`：穩定的回饋和範圍限制。
- 選用：`.claude/skills/<skill-name>/references/` 底下的參考檔，skill 需要範本、範例或較長的輔助資料時才放。

## 工作流程

### 1. 探索目標 repo

在問設定問題之前，先讀：

- 現有的 `.github/workflows/*.yml` 和 `.github/actions/**`，搞懂 runner、checkout、安裝相依套件、cache 和 PR 的慣用做法。
- 套件管理相關的檔案，像是 `package.json`、`bun.lock`、`pnpm-lock.yaml`、`yarn.lock`、`package-lock.json`、`pyproject.toml`、`go.mod` 或 `Cargo.toml`，或其他跟套件管理有關的檔案
- 現有的驗證腳本，特別是 typecheck、lint、test、quality、format，以及以 package 為範圍的指令。
- 現有的 `.claude/skills` 和 `.agents/skills`，避免重複已有的慣例。

完成標準：你能說出這個 repo 的套件管理工具、安裝指令、可能的驗證指令，以及現有的 workflow 慣例。

### 2. 問設定問題

帶使用者逐一過下面這些決定。根據 repo 裡看到的證據推薦預設值，不要丟一張空白表單給人填。

1. **Coding Agent**：Claude Code、Codex、OpenCode 或 CodeLayer。說明推薦選項需要的 secret 和 headless 指令。用 `references/agent-runner-templates.md`。CodeLayer 是 Humanlayer 的超輕量 agent harness。
2. **執行頻率**：每天、每週、平日、每月、只能手動，或自訂 cron。依任務的風險和 review 負擔推薦頻率，最可能是平日、每天或每週。
3. **任務**：這個 agent loop 要完成什麼任務？
  - 有沒有現成的 skill 可以做這件事？（問使用者之前可以先自己查）
  - 問使用者，要不要去看最近的 PR、git 歷史，或 codebase 裡某些特定的地方當參考。
4. **範圍**：這個 loop 可以改哪些目錄/package，又有哪些只能看不能改
5. **驗證**：agent 在 commit 之前必須通過哪些指令（根據你前面的調查提出建議，請使用者確認）
6. **PR 上限**：問使用者，排程執行時，如果這個 agent 已經有開著的 PR，要不要直接 no-op；如果要，允許開幾個 PR 之後就擋住新的執行。
  - **建議：要，每個 agent loop 限制 1 個開著的 PR。**這樣 agent 不會製造無限增長的工作量，讓人 review 都來不及。沒有上限的話，每天跑的 agent 一週可能產出 5 個以上沒人看的 PR，造成 review 疲勞和 merge conflict。
  - workflow 用 label（例如 `agent-<task-slug>`）來辨識每個 agent loop 開的 PR。排程執行時會檢查 `gh pr list --label <label> --state open`，數量達到或超過上限就跳過。
  - 手動的 `workflow_dispatch` 執行會繞過上限檢查，需要時可以強制執行。
7. **PR 的 metadata**：label 名稱、PR 標題前綴和 branch 前綴。
  - 建議用 `[MM/DD][Agent: <Agent Name>]: <Concise Description>` 當範本，例如 `[6/23][Agent: Effect Migrator]: Migrate XYZ module`
8. **回應格式**：CI agent 的最終回應（會變成 PR 內文）要用什麼格式？
  - 把 `references/response-template.md` 給使用者看，裡面有範例（修復/遷移、產生、重構）。
  - 問 reviewer 需要哪些資訊：摘要統計、風險等級、驗證步驟、檔案清單等。
  - 做出客製化的回應範本，放在產生出來的 skill 的 `references/` 目錄裡讓 skill 引用
9. **迭代行為**：`/iterate` 留言要不要更新既有的 PR。
  - 啟用的話，把 `references/agent-iteration.ts` 裝進 repo。問使用者偏好放哪裡：`.github/scripts/`、`ci-scripts/` 或 `scripts/`。
  - 這個腳本有兩種模式：`footer`（加上 PR 內文的標記）和 `prompt`（從 PR 的 context 組出迭代用的 prompt）。
  - 停用的話，把 `issue_comment` trigger 和只給迭代用的步驟從 workflow 移掉。

完成標準：workflow、prompt 和 memory 範本裡的每個佔位符，都有選好的值或明確的預設值。

### 3. 定義 agent 的工作

抽出 agent 該做的最小、可重複的工作。跟使用者一起過這三個問題：

**要找什麼？**agent 怎麼找出這次執行的目標？
- 會回報問題的 CLI 工具（例如 `bunx react-doctor`、`eslint --format json`）
- 搜尋模式（例如沒有 coverage 的 `*.test.ts` 檔案、用了已棄用 API 的元件）
- diff 或 changelog（例如上次發版之後的新相依套件、PR 裡改動的檔案）
- 該換成新寫法或遷移到新框架的舊寫法
- 依據先前 CI 執行紀錄判斷出來的 flaky test

**要改什麼？**agent 對每個目標做什麼轉換？
- 修復：原地解決回報出來的問題
- 遷移：把程式碼從一種寫法改成另一種
- 產生：依據現有的來源建立新檔案
- 重構：改結構但不改行為

**怎麼驗證？**什麼能證明改動是對的？
- build/typecheck 通過
- 測試通過（或某個特定子集）
- 當初找出問題的同一個工具，現在回報問題已解決
- lint 或 format 檢查通過

完成標準：你能用一句話講完這個工作，例如「找出 5 個 react-doctor 違規，修掉，並確認 typecheck 和 quality 都過」。

### 4. 寫 skill

寫一個 repo 專用的 skill，把 agent 在這個任務上的判斷方式寫進去。這個 skill 因為就放在這個 repo 裡，可以放 repo 專屬的路徑、package 名稱和慣例。

用這些寫 skill 的規則：

- 有順序的行為放在 skill 目錄裡的 `SKILL.md`（`.claude/skill-slug-here` 或 `.agents/skill-slug-here`，看 repo 的慣例和使用者偏好），步驟要附上可檢查的完成標準
- 長的範本和範例搬到旁邊的參考檔，再從 `SKILL.md` 指過去。
- 每條規則只留一個來源；不要在 skill、prompt 和 memory 檔案裡重複同樣的指引。
- 放一份回應範本當參考檔（例如 skill 目錄下的 `references/response-template.md`），定義 CI agent 最終輸出的格式。skill 要指示 agent 讀這份範本並照著格式化最終回應，這個回應會拿來當 PR 內文。
- 用 `references/skill-template.md` 的 skill 範本。範例 skill 在 `references/example-skill.md`
- 想了解 skill 規格可以參考 https://agentskills.io/specification 。

**IMPORTANT**：`SKILL.md` frontmatter 的 `name` 欄位必須跟 skill 的 slug 一致，例如名稱是 `fix-eslint-issues` 的 skill，就必須放在 `.claude/skills/fix-eslint-issues/SKILL.md` 或 `.agents/skills/fix-eslint-issues/SKILL.md`



完成標準：skill 把怎麼做這份工作講得夠清楚，agent 不用額外提示就能照做，包括怎麼格式化最終回應。

### 5. 寫 workflow 的 prompt

repo 專屬的目標設定放在 GitHub Actions 的 prompt 裡，不要放進通用的 skill。內容要包含：

- `Begin by using the <skill-name> skill.`
- 範圍：agent 可以改哪些目錄/package，可以看哪些。
- 指示：可 review 的工作單位、要避免什麼，以及怎麼驗證。
- 驗證指令（適用的話用 fenced bash 寫）
- 從 `.github/agent-memory/<task-name>.md` 內插進來的 agent memory。
- 收尾要求：驗證、commit、push，並回傳可以直接當 PR 用的摘要。

用 `references/workflow-template.yml` 當基底範本。草擬內嵌的 prompt 時用 `references/prompt-template.md`。

完成標準：prompt 包含無人值守執行所需的所有 repo 專屬限制。

### 6. 安裝 memory 檔案

用 `references/memory-template.md` 當起點，建立 `.github/agent-memory/<task-name>.md`。memory 檔案放的是會影響之後每次執行的長期回饋。保持精簡。

好的 memory 項目：

- 永久的範圍排除。
- 已知的誤報區域。
- 應該改變 agent 之後選擇目標的 review 回饋。

不好的 memory 項目：

- 一次性的任務指示。
- 單次執行的驗證輸出。
- skill 裡已經寫過的規則。

完成標準：把 memory 檔案刪掉，會失去對未來執行有用的 context，而不只是歷史紀錄。

### 7. 建立 workflow

用 `references/workflow-template.yml` 建立 `.github/workflows/agent-<task-name>.yml`，並把每個佔位符都換掉。

必須客製化的部分：

- workflow 名稱、cron、branch 前綴、workflow id、agent label、PR 標題。
- runner label 和這個 repo 的 setup 步驟。
- 安裝相依套件的指令。
- coding agent 的安裝、secret 和 headless 執行指令（來自 `references/agent-runner-templates.md`）。
- 擷取回應的步驟：每個 agent 的輸出形式不同（JSON、stream-json、純文字）。用 `references/agent-runner-templates.md` 裡各 agent 專屬的擷取方式，把最終回應存到 `/tmp/pr-body.md` 當 PR 內文。
- skill 名稱、範圍、驗證指令和 memory 路徑。
- PR 上限閘門：workflow 在執行前會檢查有沒有帶 agent label 而且開著的 PR。依使用者在第 2 步的選擇設定上限（預設：1）。閘門用 `gh pr list --label "$AGENT_LABEL" --state open` 比對數量。如果不設上限，就把這個閘門步驟整個移掉。
- 如果啟用 `/iterate`：把 `references/agent-iteration.ts` 裝到使用者偏好的位置，並更新 workflow 裡的路徑。這個腳本同時處理 PR footer 的產生和迭代 prompt 的組裝。這個檔案可以用使用者偏好的 TypeScript 工具鏈執行（支援 type-stripping 的 node、**Bun（建議）**、Deno、tsx 等），使用者要求的話也可以改寫成其他語言。

如果停用 `/iterate`，就移掉 `issue_comment` trigger 和只給迭代用的步驟，也不要安裝 `agent-iteration.ts`。

完成標準：workflow 可以從 `workflow_dispatch` 執行，而且不依賴任何不存在的檔案。

### 8. 驗證與確認

**驗證 workflow YAML：**commit 之前先 parse 一次 workflow 檔案，及早抓出語法錯誤。用下面任一種：

```bash
# Node.js / bun (js-yaml)
bunx js-yaml .github/workflows/agent-<task-name>.yml > /dev/null && echo "Valid YAML"

# Python
python -c "import yaml; yaml.safe_load(open('.github/workflows/agent-<task-name>.yml'))"

# yq (if installed)
yq eval '.name' .github/workflows/agent-<task-name>.yml
```

parser 失敗的話，先修好 YAML 語法再往下走。

**確認參考與路徑：**檢查 skill、workflow 和 memory 檔案裡提到的每個路徑，不是已經存在，就是這次任務有意要建立的。

完成標準：workflow YAML 能無錯誤地 parse，而且所有被引用的檔案都存在。

### 9. 試跑 workflow

GitHub Actions workflow 要先實際跑過至少一次，才能手動用 `workflow_dispatch` 觸發。要讓 workflow 啟動：

1. 暫時為目前的 branch 加上 `push` trigger（如果不是 main）：
   ```yaml
   on:
     push:
       branches:
         - <current-branch-name>  # Remove after first run
     schedule:
       - cron: "0 13 * * *"
     workflow_dispatch:
       # ...
   ```

2. commit 並 push 所有新檔案（workflow、skill、memory 檔案、腳本）。

3. workflow 會在 push 時觸發。到 Actions 分頁確認它有成功跑完。

4. 第一次成功執行之後，把暫時的 `push` trigger 移掉再 push 一次。之後就可以從 Actions UI 或 `gh workflow run` 手動觸發 workflow。

5. 如果試跑開出了 PR，先 review 確認 agent 的行為，再視情況關掉或 merge。

完成標準：workflow 出現在 Actions 分頁，而且可以用 `workflow_dispatch` 觸發。

## 參考檔案

- `references/workflow-template.yml`：coding-agent 的 GitHub Actions workflow 骨架。
- `references/agent-runner-templates.md`：Claude Code、Codex、OpenCode 和 CodeLayer 的 headless 指令與 secret。
- `references/agent-iteration.ts`：支援 `/iterate` 的輔助腳本（PR footer 和迭代 prompt 的組裝）。依使用者偏好裝到 `.github/scripts/`、`ci-scripts/` 或 `scripts/`。
- `references/prompt-template.md`：workflow 內嵌 prompt 的結構。
- `references/memory-template.md`：agent-memory 檔案的骨架。
- `references/skill-template.md`：產生出來的任務 skill 的骨架。
- `references/response-template.md`：CI agent 該怎麼格式化最終回應（PR 內文）的範例。
- `references/example-skill.md`：範例 skill
