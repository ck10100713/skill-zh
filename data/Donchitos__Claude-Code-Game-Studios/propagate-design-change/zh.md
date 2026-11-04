---
name: propagate-design-change
description: "找出因為 GDD 變動而過時的架構決策（ADR），並逐一帶著解決。當使用者改了 GDD 裡的某個數字或規則，問哪些 ADR 或架構決策現在已經過期時使用。"
argument-hint: "[path/to/changed-gdd.md] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/propagate-design-change/../../hooks/yaml-helper.sh" resolve_config *), Bash(git diff *), Bash(git log *), Bash(bash .claude/scripts/adr-status.sh*), Bash(bash .claude/scripts/md-section.sh *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,review_gate,automation,automation_always_ask,workflow,system_overrides`

上面已經解析好了，直接用；`--review` 在這次執行會覆蓋 `review_mode`。沒有
這個區塊的話，用 `.claude/docs/config-resolution.md` 裡的預設值。

要提問就用提問工具。沒有提問工具的話，把選項編號列出來，然後結束這一輪等使用者回覆。
被跳過或被關掉的問題不算回答：改用純文字再問一次。

# Propagate Design Change

當 GDD 改了，依它寫成的架構決策可能就不再成立。這個 skill 會找出
這次變更碰到的每一個 ADR，比較 ADR 當初的假設
和 GDD 現在說的，並帶著使用者逐一處理。

**範例：** `/propagate-design-change design/gdd/combat-system.md`

提問方式依照 `.claude/docs/automation-modes.md`（collaborative 一律問，guided
重大選擇才問，autonomous 只記錄然後繼續；`automation_always_ask`
裡的類別一律要問：這裡 ADR 受到的影響屬於 `schema_changes` 和
`architecture_decisions`）。

**Tier。** 取變動的 GDD 所屬 system 的 `workflow`：如果它在 `system_overrides` 有一列
就用那一列，否則用專案的值。被釘在 `minimal` 的 system 就算在 `standard` 專案裡也沒有 ADR。
`full` 檢查每個 ADR；`standard` 檢查關鍵（Foundation 層）的 ADR，以及任何點名了變動 GDD 的 ADR；
`minimal` 沒有東西要檢查（Phase 4）。

## Phase 1: The GDD path

skill 名稱後面打的文字，去掉任何 `--review <mode>` 那組之後，就是
變動的 GDD。它是必要的。缺少時：「Usage: `/propagate-design-change
design/gdd/[system].md` — give the path to the GDD that changed.」不是檔案時：
「[path] not found. Check the path and try again.」

## Phase 2: What changed

問 git，絕對不要用肉眼比對兩份完整的文件：

```bash
git diff HEAD -- design/gdd/[filename].md
```

空的：變更可能已經 commit 了，所以擴大到最後一次碰過它的 commit：
`git diff HEAD~1 HEAD -- design/gdd/[filename].md`。

- 完全沒有歷史（`git log --oneline -1 -- design/gdd/[filename].md` 什麼
  都沒印）：「No previous version in git — this is a new GDD, not a revision.
  Nothing to propagate.」停下來。
- 有歷史，但兩個 diff 都是空的：回報「no uncommitted or last-commit changes to
  `[file]`」，並問要對哪個 revision 做傳遞。空的 diff 代表*這裡*沒有東西變，
  不代表沒有東西受影響。

從 hunk 取得：`@@` 標頭會點出每個變更所在的章節，所以
變動章節的清單直接來自 diff 本身。沒有 hunk 的章節，依定義就是沒變。
只有在 hunk 單獨看不懂的時候（一個數字的變更，它的意義取決於
上面的規則），才去讀周圍的章節，而且只讀那一個章節：`bash .claude/scripts/md-section.sh extract design/gdd/[file].md "[Section]"`。

## Phase 3: The change summary

```
## Change Summary: [GDD filename]
Date of revision: [today]

Changed sections:
- [Section]: [what changed — new rule, removed rule, formula modified, …]

Unchanged sections:
- [Section]

Key changes affecting architecture:
- [change likely to affect ADRs]
```

**其他用到這些事實的 GDD。** 當 `design/registry/entities.yaml` 不存在或沒有條目
（在 `/design-system` 填入之前，它是一個空的 stub），
就跳過這步；下面的 ADR 檢查仍然會執行。否則它會記錄哪些 GDD 依賴
這個 system 的事實：搜尋 `source: design/gdd/[filename]`。對這個 GDD 擁有的、
而且 diff 改了值的每個實體、常數或公式，
它的 `referenced_by:` 清單會點名現在可能不一致的 GDD。把它們列在「Downstream GDDs to re-check」底下。

## Phase 4: The ADRs in scope

`bash .claude/scripts/adr-status.sh` 會列出每個 ADR 的 status、layer 和
缺少的章節。

- **`full`：** 每個 ADR。
- **`standard`：** 關鍵的（`layer` 欄寫 Foundation，或沒有
  layer：有疑問就當成關鍵）以及任何點名了變動 GDD 的 ADR。
- **`minimal`：** 回報「No ADR check at minimal workflow — design change recorded;
  no architecture impact analysis.」停下來。

先確立分母：它們的數量是 **N**。N 是 0：「No ADRs found in `docs/architecture/` — nothing to
check.」停下來。

**哪些參照了這個 GDD。** 不用讀整份 ADR：

1. 每個 ADR 的 GDD Requirements Addressed 章節
   （`bash .claude/scripts/md-section.sh extract <adr> "GDD Requirements Addressed"`），
   找點名變動 GDD 的列；
2. 在 ADR 裡搜尋變動 GDD 的檔名，這樣能抓到在文字敘述裡引用它、
   卻沒有表格列的 ADR。

兩者的聯集就是受影響的集合 **M**。

| Result | Meaning | Action |
|---|---|---|
| **M ≥ 1** | Normal. | Go on. The N − M others are out of scope for this check: never describe them as verified unaffected. |
| **M = 0**, and every in-scope ADR lacks GDD Requirements Addressed (`missing` column) | Traceability cannot be computed. | "[N] ADRs found, none has a 'GDD Requirements Addressed' section — traceability cannot be computed (a pre-production gate blocker). Run `/architecture-decision retrofit [adr]`." Stop. |
| **M = 0**, the sections exist | No ADR references this GDD. | "No ADR references [gdd] — no architecture impact." Stop. |

如果 `docs/architecture/requirements-traceability.md` 存在，就讀它。

回報：「Checked [N] ADRs. [M] reference [gdd filename] ([X] in a requirements
table, [Y] in prose only).」

## Phase 5: Impact analysis

對 **M** 裡的每個 ADR，用 `md-section.sh extract` 讀它的 Context、Decision 和 Consequences 章節：
要判斷一個決策是否還成立，需要它的推理，
絕對不能只看它的表格列。然後，對它列出的、來自變動 GDD 的每個需求：

1. 這個需求在目前的 GDD 裡還存在嗎？
2. ADR 寫成時，GDD 是怎麼說的，現在又是怎麼說的？
3. 這個決策還成立嗎？

替每個 ADR 分類：

| Status | Meaning |
|--------|---------|
| ✅ **Still Valid** | The change does not touch what this ADR decided |
| ⚠️ **Needs Review** | The change may affect it; human judgement needed |
| 🔴 **Likely Superseded** | The change contradicts what this ADR assumed |

```
### ADR-NNNN: [title]
Status: [Still Valid | Needs Review | Likely Superseded]

What the ADR assumed about this GDD:
  "[quote from its GDD Requirements Addressed or Context]"

What the GDD now says:
  "[quote from the current GDD]"

Assessment:
  [whether the decision still holds, and why]

Recommended action:
  [Keep as-is | Review and update | Mark Superseded and write a new ADR]
```

## Phase 6: The impact report, then the review

在要求任何動作之前，先把整份報告秀出來：

```
## Design Change Impact Report
GDD: [filename]
Date: [today]
Changes detected: [N sections changed]
ADRs referencing this GDD: [M]

### Not Affected
[ADRs whose decisions still hold]

### Needs Review ([count])
[ADRs that may need updating]

### Likely Superseded ([count])
[ADRs whose assumptions the change contradicts]
```

**技術審查。** 讀上面的 `review_gate` 那行。`skill-gates=skip`
（solo 或 lean）：不派 agent；註明 `TD-CHANGE-IMPACT skipped — [Solo | Lean] mode`。
`skill-gates=run`：把審查交給 `technical-director` agent，使用 gate
**TD-CHANGE-IMPACT**（`.claude/docs/director-gates/td-change-impact.md`；agent
自己會讀它）。Brief：

- **Objective：** 在使用者根據影響報告採取行動之前，先檢查它。
- **給它：** 上面的整份報告：變更摘要、每個受影響的 ADR，連同
  它的分類和建議動作。
- **檢查：** 沒有 ADR 被分得太輕；建議的動作是合理的；沒有漏掉
  對其他 ADR 或系統的連鎖影響。
- **回傳：** APPROVE、CONCERNS、REJECT，或點名缺少輸入的 NOT ASSESSED。
- **Boundaries：** 它不編輯任何檔案。

依判定行動：

- **APPROVE：** 進 Phase 7。
- **CONCERNS：** 顯示被標記的 ADR 或動作，並問：「How do you want to go
  on?」Options：Revise the impact assessment / Accept with the noted concerns /
  Discuss further。
- **REJECT：** 不要進 Phase 7；先重新分析影響。
- **NOT ASSESSED：** 它不是核准（`.claude/docs/director-gates.md`）。點名
  缺了什麼，然後補上並重新執行審查；或者，當使用者
  選擇不補就繼續時，進 Phase 7，並在報告和最後的判定行裡寫上 `TD-CHANGE-IMPACT: NOT
  ASSESSED — [input]`。

## Phase 7: Resolve each ADR

對每個被標成 Needs Review 或 Likely Superseded 的 ADR，一次一個，問：「ADR-NNNN
([title]) — [status]. What would you like to do?」Options：

- Mark it Superseded (I'll write the new ADR)
- Update it in place (a small revision): note what to revise; the user edits it
- Keep it as it is (the change does not affect this decision)
- Skip it for now (revisit later)

**Mark Superseded。** 問「May I set the Status of [ADR file] to Superseded?」使用者答應就
只取代它 `## Status` 章節的內容：

```
bash .claude/scripts/md-section.sh replace docs/architecture/[adr-file].md "Status" <<'EOF'
Superseded — replacement pending (see docs/architecture/change-impact-[date]-[system-slug].md)
EOF
```

這是這個 skill 唯一會寫的形式。`adr-status.sh` 會把它讀成 Superseded，所以
`/dev-story` 和 `/create-stories` 會擋住仍然指向它的 story。新的 ADR 寫好之後，
會記錄它取代的是哪一個。ADR 裡其他東西都不要改：它的內容保持原樣。

## Phase 8: The traceability index

當 `docs/architecture/requirements-traceability.md` 存在時，問「May I add the
changed requirements to the traceability index?」使用者答應就替每個變動的需求加一列：

```markdown
## Superseded Requirements
| Date | GDD | Requirement | Changed To | ADRs Affected | Resolution |
|------|-----|-------------|------------|---------------|------------|
| [date] | [gdd] | [old requirement text] | [new requirement text] | ADR-NNNN | [Superseded/Updated/Valid] |
```

## Phase 9: The change impact document

問「May I write the change impact report to
`docs/architecture/change-impact-[date]-[system-slug].md`?」它包含變更
摘要、影響分析、為每個 ADR 選擇的處理方式，以及
需要撰寫或更新的 ADR。

## Phase 10: Follow-up

依各項處理結果：

- 被標成 Superseded 的 ADR：「Run `/architecture-decision [title]` to write the
  replacement, then `/propagate-design-change` again to check coverage.」
- 要就地更新的 ADR：每個 ADR 要改的欄位。
- 受影響的 ADR 很多：「Run `/architecture-review` once they are updated, to check
  the traceability matrix still holds together.」

Phase 9 寫入之後，以 `Verdict: COMPLETE — change impact report saved` 結尾，
被拒絕的話則以 `Verdict: BLOCKED — user declined the write` 結尾。
