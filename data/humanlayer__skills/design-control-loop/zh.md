---
name: design-control-loop
description: 訪談使用者，設計一個貼合他們 codebase 的 agentic 控制迴圈（在干擾之下運作的 sensor、controller、actuator），再把它建成可在本機執行的元件，加上排程執行的 coding-agent workflow
---

# Design Control Loop

使用者想用排程的方式，靠小而低風險、可 review 的改動，把 codebase 的某個屬性逐步推向目標，就用這個 skill，這就是 **agentic 控制迴圈**。

你的工作是**訪談使用者、_跟他一起_設計這個迴圈，然後幫他建出來**。設計必須貼合*他們的* codebase 和他們已經在用的工具。沒有固定的工具組合，也沒有範本可以照抄：根據你在 repo 裡找到的東西提出選項、討論取捨、談定設計，然後實作。

## 心智模型

借用控制理論。codebase 是一個一直在被改動的動態系統（改動來自隊友、相依套件和產生出來的程式碼，這些就是**干擾**）。控制迴圈是一步步把它推向想要的狀態，而不是一次到位：

- **Set point**：codebase 某個屬性想要達到的最終狀態。
- **Sensor**：量測目前的狀態，得出跟 set point 之間的差距。
- **Controller**：根據量測結果，決定下一個小而低風險的改動。
- **Actuator**：套用改動並開 PR 的 coding agent。
- 結果會回饋到下一次執行。人要待在迴圈*之上*，負責導航。

在設計任何東西之前，先讀 `references/control-loop-taxonomy.md`，並帶使用者過一遍這些概念。有一個完整的實例見 `references/example-control-loop.md`，把它當作說明，不是藍圖。

## 怎麼使用這個 skill

- **先讀 repo 再問**（Phase A）。帶著提案去訪談，不要丟一張空白表單。
- **每個元件都要客製。**適合的 sensor、controller 和 actuator，完全取決於使用者的問題和技術棧。參考檔裡的清單是用來激發討論的範例，絕對不是要硬推的 checklist。
- **在接進 CI 之前，每個元件都要能在本機獨立執行**（Phase D）。workflow 只該負責把使用者已經能手動執行的幾塊串起來。
- **在動手建之前，先把談定的設計寫下來**，使用者才能用很低的成本糾正。

## 產出

依照談定的設計，在目標 repo 建立或更新這些東西：

- **Sensor** 和 **controller**：納入版本控制、使用者能在本機執行的指令/腳本。
- `.claude/skills/<skill-name>/SKILL.md`：**actuator** skill，記錄 agent 的判斷方式（依 repo 慣例，路徑也可以是 `.agents/skills/...`）。
- 定期執行迴圈並開 PR 的 **workflow**（預設用 GitHub Actions，repo 用什麼 CI 就用什麼）。
- 一個 **memory/feedback 檔案**，在每次執行之間帶著長期回饋。
- 選用：**dampener**（回歸閘門），在迴圈改善問題的同時，防止問題變得更糟。

## 工作流程

### Phase A — 了解這個系統

**讀這些參考檔：**`references/example-control-loop.md`。

在問設定問題之前，先讀：

- 現有的 CI：`.github/workflows/*.yml`、`.github/actions/**`，或 repo 非 GitHub 的 CI 設定：runner、checkout、安裝相依套件、cache 和 PR 的慣例。
- 套件管理相關的檔案（`package.json`、`bun.lock`、`pnpm-lock.yaml`、`yarn.lock`、`package-lock.json`、`pyproject.toml`、`go.mod`、`Cargo.toml` 等）。
- 現有的驗證腳本：typecheck、lint、test、quality、format，以及以 package 為範圍的指令。
- 現有的 `.claude/skills` / `.agents/skills`，以及任何現有的 agent 迴圈（workflow、`agent-memory`、膠水腳本放哪裡），照著它們的慣例走，不要自己發明新的。
- repo 裡已有的靜態分析、linting、codegen 和測試工具，這些最有可能成為 sensor 的原料。
- 大致摸清楚有哪些 package、服務，以及這個 repo 的用途。

完成標準：你能說出這個 repo 的套件管理工具、安裝指令、可能的驗證指令、CI 平台，以及任何現有的迴圈慣例。你大致了解它包含的 package/服務/應用程式。

### Phase B — 跟使用者一起設計迴圈

**讀這些參考檔：**`references/control-loop-taxonomy.md`、`references/example-control-loop.md`、`references/agent-runner-templates.md`。

這是一場訪談。逐一過下面每個元件。從問使用者 set point 的問題開始。根據 Phase A 提出選項並攤開取捨，不要硬性指定任何選擇。邊談邊記錄決定。

1. **Set point。**我們要推動什麼屬性，推到什麼目標？例如：一個不變式（「沒有 procedure 使用舊的寫法」）、一個門檻（「這些 package 的測試覆蓋率 ≥ X」），或一個方向（「每次執行都減少出現次數」）。同時要釘死**範圍**：這個迴圈可以改哪些目錄/package，哪些只能讀。

2. **Sensor。**迴圈要怎麼量測跟 set point 之間的差距？檢查 codebase 和使用者現有的工具，提出適合*他們*技術棧的選項：靜態分析或 lint 工具、結構/AST 搜尋、測試套件、型別檢查器、telemetry 或錯誤查詢、自訂腳本，甚至是以 agent 為基礎的檢查。討論對他們重要的取捨（穩定性、成本、可重複性，以及量測會不會被悄悄關掉），不要硬性規定任何屬性。目標是做出 controller 能重複拿來行動的量測。

3. **Controller。**迴圈要怎麼從量測結果挑出下一個增量，大小要維持低風險、可 review？這個要*跟*使用者一起設計：怎麼排目標的優先順序、一個增量有多大，以及在這裡「一個可 review 的工作單位」是什麼意思。controller 可以是完全確定性的（挑下一個目標的腳本），也可以是完全 agentic 的（agent 依自然語言標準決定），也可以跟 sensor 或 actuator **融合**。controller 是你會根據迴圈的輸出**長期調校**的部分，先從簡單的開始，預期之後要修改。

4. **Actuator。**由 coding agent 加上 repo 專用的 skill 來套用改動。
   - **Agent + 憑證。**從 `references/agent-runner-templates.md` 挑 CLI coding agent（Claude Code、Codex、OpenCode、CodeLayer 等）、它的 secret 和它的 headless 指令。
   - **先找黃金範式。**在自動化之前，先確立什麼樣的改動算好：問使用者 codebase 裡現有的範式要不要遵循，並檢查程式碼把它們找出來。把這些記進 actuator skill（Phase C）。
   - **驗證。**決定 agent 在 commit 之前必須通過哪些指令（根據 Phase A 提出建議並確認）。

5. **干擾 + dampener（提出來讓使用者選）。**說出迴圈之外還有什麼會改變系統（隊友同時在發版、相依套件升版、產生出來的程式碼）。然後**提出** dampener 這個選項：一個檢查，在排程迴圈一點一點削減問題的同時，防止被量測的問題變得更糟，例如一個 PR 檢查，把 sensor 的輸出跟基準線比對，把新引入的偏差揭露出來（或最終直接擋掉）。這是選用的；有些迴圈不需要。

完成標準：一份簡短的書面設計，寫出 set point、sensor、controller、actuator（agent + skill + 驗證），以及干擾/dampener，而且每個元件都是使用者能在本機執行的東西。

### Phase C — 建 actuator skill

**讀這些參考檔：**`references/skill-template.md`、`references/example-skill.md`、`references/response-template.md`。

寫一個 repo 專用的 skill，記錄 actuator 在這個任務上的判斷方式。因為它放在 repo 裡，可以用 repo 專屬的路徑、package 名稱和慣例。

- 有順序的行為放在 `SKILL.md`，寫成附帶可檢查完成標準的步驟；長的範本和範例搬到旁邊的參考檔。
- 把 Phase B4 的黃金範式編進去，讓 agent 遵循既有慣例。
- 每條規則只留一個來源；不要在 skill、prompt 和 memory 檔案裡重複同樣的指引。
- 放一份回應範本（例如 `references/response-template.md`），定義 agent 最終輸出的格式，這會變成 PR 內文。要在 skill 裡指示 agent 讀它並照著做。
- 用 `references/skill-template.md` 當骨架，`references/example-skill.md` 當具體範例。skill 規格見 https://agentskills.io/specification 。

**IMPORTANT：**skill frontmatter 裡的 `name` 必須跟它的目錄 slug 一致，名稱是 `migrate-foo` 的 skill 就放在 `.claude/skills/migrate-foo/SKILL.md`（或 `.agents/skills/migrate-foo/SKILL.md`）。

完成標準：skill 把這份工作講得夠清楚，agent 能無人值守地完成，包括怎麼格式化最終回應。

### Phase D — 讓每個元件都能在本機執行

**讀這些參考檔：**`references/agent-runner-templates.md`。

在任何 CI 出現之前，先把 sensor 和 controller 做成納入版本控制的指令或腳本（腳本放哪裡，照 repo 的慣例），然後手動驗證整個迴圈能運作：

- 單獨執行 **sensor**，確認它產出穩定、可用的量測。
- 對真實的 sensor 輸出執行 **controller**，確認它挑出合理的下一個增量。
- 用 headless CLI 指令，在 controller 挑出的目標上於本機執行 **actuator**，確認它做出改動並通過驗證。

每一塊都能在本機各自跑起來之後，才往 CI 走。這樣迴圈才好除錯，workflow 也只是把使用者已經能執行的東西串起來的薄薄一層。

完成標準：使用者能在本機獨立執行 sensor、controller 和 actuator。

### Phase E — 把迴圈接進 CI

**讀這些參考檔：**`references/workflow-template.yml`、`references/prompt-template.md`、`references/agent-runner-templates.md`。

把各元件組裝成一個定期執行的 job。預設用 GitHub Actions，因為它本來就有程式碼、secret、版本控制和排程/手動觸發，但 repo 用什麼 CI 就用什麼。

- 把迴圈拆成**分開的步驟：sensor → controller → actuator**，然後 commit 並開 PR，用 agent 的最後一則訊息當內文。（如果元件是融合的，例如 sensor 本來就會排優先順序，或同一個 agent 既挑目標又做改動，就合成單一步驟，不要硬做出設計裡沒有的切分。）
- 可重用的邏輯可以放在自訂的 composite action 裡。
- 依任務風險和 review 負擔決定**執行頻率**（每天、平日、每週、每月、只能手動，或自訂 cron）。
- 把 memory 檔案（Phase F）內插進 actuator 的 context。
- 用 `references/workflow-template.yml` 當基底，`references/prompt-template.md` 當內嵌 prompt。agent 執行加上擷取回應的步驟，從 `references/agent-runner-templates.md` 取用（每個 agent 的輸出方式不同；要把最終回應存到 `/tmp/pr-body.md`）。

完成標準：workflow 可以從 `workflow_dispatch` 執行，而且不依賴任何不存在的檔案。

### Phase F — 讓人待在迴圈之上

**讀這些參考檔：**`references/memory-template.md`、`references/agent-iteration.ts`。

排程的迴圈沒人導航就會漂移。給人兩個管道，兩個都該改變未來的行為，而不只是目前這個 PR：

- **Memory/feedback 檔案。**一個納入版本控制的 markdown 檔案（例如 `.github/agent-memory/<task-slug>.md`），每次執行時，在 **controller 之後**以確定性的方式載入 actuator 的 context。用 `references/memory-template.md`。好的項目：永久的範圍排除、已知的誤報區域，以及應該改變未來挑選目標的 reviewer 回饋，不要放一次性的指示或單次執行的 log。
- **PR 上的 `/iterate`。**替每個迴圈的 PR 加 label，並嵌入隱藏標記，讓每個 workflow 只處理它自己建立的 PR 上的留言。maintainer 留言 `/iterate` 時，對應的 workflow 會載入 PR 的 context（diff、留言）和回饋，由 agent 更新它的 memory 和 PR。把 `references/agent-iteration.ts`（模式：`footer` 和 `prompt`）裝在 repo 放 CI 腳本的地方。

跟使用者說明時，把這件事講成**你怎麼長期調校 controller 和 skill**：迴圈會變好，是因為有人持續在糾正它。

完成標準：長期回饋能跨執行保留，而且 `/iterate`（如果啟用）會更新既有的 PR。

### Phase G — 流量控制

**讀這些參考檔：**`references/workflow-template.yml`。

限制在製品（WIP）的數量，讓迴圈產出 PR 的速度永遠不會超過 review 的速度。**建議的預設：每個迴圈一個開著的 PR。**

- workflow 會檢查有沒有帶這個迴圈 label 而且開著的 PR，達到上限時，排程執行就 no-op；手動的 `workflow_dispatch` 執行會繞過這個檢查。
- 決定 PR 的 metadata：label 名稱、PR 標題前綴、branch 前綴。

沒有這個機制的話，每天跑的迴圈會堆出一堆重複或互相衝突的 PR，卻沒人在 review。完成標準：這個迴圈開著的 PR 已達上限時，排程執行會 no-op。

### Phase H — 驗證、試跑，然後加速迭代

**讀這些參考檔：**`references/workflow-template.yml`。

**驗證** workflow YAML（`bunx js-yaml file.yml`、`python -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" file.yml`，或 `yq`），並確認 skill、workflow 和 memory 檔案裡提到的每個路徑，不是已經存在，就是這次任務會建立。

**試跑。**workflow 要先跑過一次，才能用 `workflow_dispatch` 觸發。暫時為目前的 branch 加上 `push` trigger，push，看它跑完，然後把 trigger 移掉。review 它開出來的任何 PR，確認迴圈的行為。

**準備好加速迭代**（迴圈調校好、開始穩定產出高品質結果之後）：提高排程頻率；加大 controller 的批次（例如每次執行挑 N 個目標）；每次 workflow 執行跑 N 輪 sense→control→actuate 循環；或把 workflow 跑多次，一個 PR 分給一位隊友。

完成標準：workflow YAML 能 parse、所有被引用的檔案都存在，而且迴圈至少產出過一個經過 review 的 PR。

## 參考檔案

上面每個 phase 都有點名相關的參考檔，走到那個 phase 時再讀。完整索引：

- `references/control-loop-taxonomy.md`：控制迴圈的各個元件，以及該問的設計問題；先讀這份，並用它來教使用者。
- `references/example-control-loop.md`：一個完整的迴圈實例，逐元件加註解。是說明，不是範本。
- `references/agent-runner-templates.md`：Claude Code、Codex、OpenCode 和 CodeLayer 在本機 + CI 的 headless 指令和 secret，附回應擷取方式。
- `references/workflow-template.yml`：定期執行的迴圈 workflow 骨架，sensor/controller/actuator 分成獨立步驟。
- `references/prompt-template.md`：actuator 步驟的內嵌 prompt 結構。
- `references/memory-template.md`：memory/feedback 檔案的骨架。
- `references/skill-template.md`：產生出來的 actuator skill 的骨架。
- `references/response-template.md`：agent 該怎麼格式化最終回應（PR 內文）的範例。
- `references/example-skill.md`：一個結構良好的任務 skill 的具體範例。
- `references/agent-iteration.ts`：支援 `/iterate` 的輔助腳本（PR footer 標記 + 迭代 prompt 的組裝）。
