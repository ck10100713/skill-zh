---
name: architecture-decision
description: "建立 ADR 來記錄一項技術決策：背景、考慮過的替代方案、後果。"
argument-hint: "[title | retrofit <path> | accept <ADR-id>] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(wc -c *), Bash(bash "*/.claude/skills/architecture-decision/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/registry.sh *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow,docs.density,team.size`

上面已解析完成，直接使用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，
就用 `.claude/docs/config-resolution.md` 裡的預設值。

# Architecture Decision

呼叫這個 skill 時：

## 0. 解析參數：偵測 Retrofit / Acceptance 模式

完整的檢查模式請見 `.claude/docs/director-gates.md`。個別 gate 的定義放在 `.claude/docs/director-gates/[gate-id].md`，被派出的 agent 自己會讀自己的 gate 檔案；不要在父 session 裡讀它。

每次呼叫 `AskUserQuestion` 都要遵循 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
`automation_always_ask` 的類別一律會詢問）。

**`team.size`**：由哪些 agent 來驗證這份 ADR（和 review_mode/workflow 互不相干）。
- **`individual`**（預設）：`technical-director`（TD-ADR）+ 引擎專家。
- **`small`** 和 **`studio`**：同樣這兩個。這個 skill 在任何規模下，都不會派出引擎
  子專家，也不會派出對抗式 reviewer。

**`docs.density`**：它控制的是 ADR 文字章節的*深度*，不是骨架產出哪些章節
（那是固定的）。`modes.rigor` 會和 `workflow` 一起設定它；要單獨調整 ADR 的詳細程度，
就明確設定 `docs.density`：
`terse`（預設，透過 `rigor: minimal`）= 決策 + 替代方案用條列，每項一行理由；
`balanced` = 每個章節一段，附簡短理由（`rigor: standard`）；`thorough` =
完整的文字，在 Decision、Alternatives 和 Consequences 裡附上取捨和完整的理由推導。
套用在文字章節上；Engine Compatibility、ADR
Dependencies 和 GDD Requirements 的表格是結構性的，在任何密度下都保持完整。

**`workflow`**（見 `.claude/docs/workflow-modes.md`）：
- `full` — 必要 ADR 清單上的所有 ADR 都必須完成。
- `standard` — 只需要關鍵的 ADR（Foundation 層的系統）。
- `minimal` — 不需要。但仍然可以自願執行。

**如果參數以 `retrofit` 開頭，後面接一個檔案路徑**

**現在就讀 `references/0-retrofit.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

**如果參數以 `accept` 開頭，後面接一個 ADR id**

**現在就讀 `references/0-accept.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

如果不是 retrofit 或 acceptance 模式，就進行下面的步驟 1（一般的 ADR 撰寫）。

**沒有參數的防護**：如果沒有提供參數（title 是空的），在執行第 0 階段之前，先問：

> 「你要記錄的是什麼技術決策？請給一個簡短的標題
> （例如 `event-system-architecture`、`physics-engine-choice`）。」

把使用者的回答當成 title，然後進行步驟 1。

---

## 1. 載入引擎 Context（永遠先做）

**現在就讀 `references/1-engine-context.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 2. 決定下一個 ADR 編號

掃描 `docs/architecture/` 裡既有的 ADR，找出下一個編號。

---

## 3. 蒐集 context

**現在就讀 `references/3-gather-context.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 4. 協作引導決策

**現在就讀 `references/4-decide.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 5. 產生 ADR

**現在就讀 `references/5-generate.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 6. 收尾的下一步

ADR 寫好之後（registry 也視需要更新了），用 `AskUserQuestion` 收尾。

產生 widget 之前：
1. 讀 `docs/architecture/architecture.md` 的 `## Required ADRs` 章節（依章節讀），並列出 `docs/architecture/adr-*.md`：必要的 ADR 沒有檔案，就是還沒寫。沒有 `architecture.md` 的話，就找 technical-preferences.md 或 systems-index.md 裡標為前置條件的 ADR
2. 檢查所有前置的 ADR 現在是否都寫好了。如果是，就加入「開始寫 GDD」的選項。
3. 把**所有**剩下的優先 ADR 都列成獨立的選項，不要只列下一兩個。

Widget 格式：
```
ADR-[NNNN] written and registry updated. What would you like to do next?
[1] Write [next-priority-adr-name] — [brief description from prerequisites list]
[2] Write [another-priority-adr] — [brief description]  (include ALL remaining ones)
[N] Start writing GDDs — run `/design-system [first-undesigned-system]` (only show if all prerequisite ADRs are written)
[N+1] Stop here for this session
```

如果沒有剩下的優先 ADR，也沒有還沒設計的 GDD 系統，就只提供「Stop here」，並建議在新的 session 裡執行 `/architecture-review`。

**收尾的輸出裡，一定要附上這則固定的提醒（不准省略）：**

> 要對照你的 GDD 驗證 ADR 的涵蓋範圍，請開一個**全新的 Claude Code session**，
> 然後執行 `/architecture-review`。
>
> **絕對不要在和 `/architecture-decision` 同一個 session 裡執行 `/architecture-review`。**
> 做審查的 agent 必須獨立於撰寫時的 context，才能給出不偏頗的
> 評估。在這裡執行，會讓審查失去效力。

**這裡不要解除 story 的阻擋。** 這份 ADR 是 `Proposed`，步驟 5 保證了這一點，
而被阻擋、等待這項決策的 story，仍然在等這項決策。寫完就解除阻擋，
會在這道防護最該發揮作用的時候把它廢掉：流程看起來順暢運轉，
實際上卻是建立在沒人接受過的決策上。

改成告訴使用者，現在有什麼在等待被接受：

> 「ADR-NNNN 已寫好，狀態是 `Proposed`。還有 [N] 個 story 因它而維持 `Blocked`。
> 等決策確定後，再執行 `/architecture-decision accept ADR-NNNN`，
> 那樣才會把它們移到 `Ready`。」

要依路徑列出被阻擋的 story，讓維持 Proposed 的代價看得見。
（接受一份 ADR 的後果，會在很多 skill 裡被強制執行，但授權
只記錄在少數幾個地方，所以兩者之間的路徑必須保持明確。）
