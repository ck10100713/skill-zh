---
name: dev-story
description: "依照 story 的 ADR，把一個 story 實作成程式碼並附上測試。當使用者說要建置、實作或開始做某個 story 時使用。不適用於事前檢查是否就緒，也不適用於事後結案。"
argument-hint: "[story-path]"
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/dev-story/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/story-facts.sh *), Bash(bash .claude/scripts/adr-status.sh *), Bash(bash .claude/scripts/md-section.sh *), Bash(bash .claude/scripts/session-state.sh *), Bash(bash .claude/scripts/review-receipts.sh hash *), Bash(godot *), Bash(mkdir -p production/qa/evidence/*)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,qa.level,gate_level,engine_values,specialists,perf_budgets,system_overrides`

上面已經解析好了，直接用。沒有這個區塊的話，改用
`.claude/docs/config-resolution.md` 裡的預設值。

要提問就用提問工具。沒有提問工具的話，把選項編號列出來，然後結束這一輪等使用者回覆。
被跳過或被關掉的問題不算回答：改用純文字再問一次。

# Dev Story

實作一個 story：先確認它可以開工，標成 In Progress，用 story 組出來的 brief 把程式碼交給
適合的 programmer agent，再檢查結果能不能 parse、看起來對不對，最後交接。

**寫入的東西**（每一項都要先問、而且問題要點名它）：story 的 `Status`、`Last Updated`
和 `## Files`，還有它在 `production/sprint-status.yaml` 裡的條目。programmer agent
負責在 code root 和 test root 底下寫程式碼和測試
（`.claude/docs/code-root-resolution.md`）。session checkpoint 和 evidence stamp
不用問就直接寫。
**下一步：** `/story-done [story-path]`；在 `standard` 和 `full` 要先跑 `/code-review
[files]`。

提問方式依照 `.claude/docs/automation-modes.md`（collaborative 一律問，guided
重大選擇才問，autonomous 只記錄然後繼續；`automation_always_ask`
裡的類別一律要問）。

Checklist（複製下來，做完一項就勾一項）：

```
- [ ] Phase 1: story found, tier resolved
- [ ] Phase 2: prerequisites checked (ADR, manifest, dependencies)
- [ ] Phase 3: story marked In Progress (one ask)
- [ ] Phase 4: programmer and engine specialist chosen
- [ ] Phase 5: work handed out with a full brief
- [ ] Phase 6: finished? parse check, run and look, one Run result line
- [ ] Phase 7: summary, ## Files, checkpoint, closing block
```

## Phase 1: The story

skill 名稱後面打的文字就是 story 路徑。什麼都沒打的話，就拿 `production/session-state/active.md`
裡 checkpoint 指的那個 story，並跟使用者確認：
「Continuing work on [title] — is that correct?」那裡也沒有：就問「Which story are we
implementing?」，選項用 `bash .claude/scripts/story-facts.sh --all` 輸出裡的 `TODO` 列。
`production/epics/` 底下連一個 story 檔都沒有：停下來，說
「No stories found in `production/epics/` — run `/create-stories [epic-slug]` to make them (at `standard` and `full`, run `/create-epics` first if there is no epic yet).」

`bash .claude/scripts/story-facts.sh <story-path>` 會給出它的 type、layer、TR-ID、
ADR 和相依項目。然後把 story 完整讀一遍。

**Tier。** 取這個 story 所屬 system 的 `workflow`，以它 `GDD:` 路徑的 GDD 檔名主幹為鍵
（`design/gdd/<stem>.md` → `<stem>`；只有在沒有 GDD 路徑時，才用它 TR-ID 的 `[system]`）：
如果該 system 在 `system_overrides` 有一列就用那一列，否則用專案的值。在你第一次回覆時就說出來：
`Tier: workflow [value]`。Phase 2 要看哪一欄、結尾的 Next step 是什麼，都由這個值決定，
絕對不是 `rigor` 或 `qa.level`。

## Phase 2: Can it start?

| Input | `full` | `standard` | `minimal` |
|---|---|---|---|
| TR registry `docs/architecture/tr-registry.yaml` | missing: **stop**, "Run `/architecture-review` to bootstrap it" | optional | not expected |
| The ADR the story names | missing, `Proposed`, `Deprecated` or `Superseded`: **stop** | the same, only when the story names one | the same, only when the story names one |
| Control manifest `docs/architecture/control-manifest.md` | missing: warn, go on | missing: warn, go on | not expected |

ADR 欄位寫成 `N/A — [reason]` 的 story，就是沒有指定任何 ADR。

**ADR。** `bash .claude/scripts/adr-status.sh <ADR id>` 會給出它的 status 和
`version`。停止時的訊息：`Proposed` —「ADR-NNNN is still Proposed. Accept it with
`/architecture-decision accept ADR-NNNN` before implementing.」`Deprecated` 或
`Superseded` —「ADR-NNNN is [status]; point the story at [successor] (edit its ADR
field; `/create-stories` never rewrites an existing story) before implementing.」
`NOT_FOUND` —「ADR file not found. Run `/architecture-decision`, or correct the
story's ADR field.」

**不要打開 ADR。** programmer 讀的是 story 裡的 ADR Decision Summary 和 Implementation Notes，
不是 ADR 本身。把 ADR 的 `version` 跟 story 的
`ADR Version` 比對：

- 兩者相同，或 story 沒有 `ADR Version`（寫在蓋章機制出現之前），或兩邊都是
  `unversioned`：相信 story。後兩種情況要在摘要裡註明（「summary
  trusted unverified」）。
- 兩者不同，或 ADR 是 `unversioned` 但 story 寫了日期：去讀
  `references/version-mismatch.md`。吻合的時候就不要載入它。

絕對不要把「沒有 stamp」當成「stamp 過期」：不知道的話就退回採信 story，
之後的漂移由 `/story-readiness` 和 `/code-review` 來抓。

**Manifest。** 它存在的話，拿它的 `Manifest Version` 那行跟 story 的比對。
不一樣：去讀 `references/version-mismatch.md`。

**相依項目。** 對 story 的 Depends on 那行裡的每個路徑，執行
`bash .claude/scripts/story-facts.sh <path>`。不是 `COMPLETE` 的話，問：
「[this story]
depends on [dependency], which is [status], not Complete. How do you want to go
on?」選項：Proceed anyway — I accept the risk / Stop — I'll finish the
dependency first / It is done, the status was never updated — mark it Complete。
選 Stop：這個 story 就是 BLOCKED（Phase 7），不派 agent。選標成 Complete：先問
「May I set [path]
Status to Complete?」。選 Proceed：記在 Deviations 底下。`NOT_FOUND`：警告
「Dependency story not found: [path]」。

上面任何一個停止條件成立：都不跑 agent。直接進 Phase 7，寫 BLOCKED checkpoint。

## Phase 3: Mark it In Progress

派任何 agent 之前，先問一次：「May I mark this story In Progress? This sets `Status`
and `Last Updated` in [story path] and its entry in `production/sprint-status.yaml`,
and at the end lists the files changed under its `## Files`.」如果 sprint 檔不存在，
問題裡就不要提它。先把你接下來要做什麼寫在問題前面：
問題要放在這則回覆的最後。使用者答應後：

- `bash .claude/scripts/md-section.sh set-field <story> Status "In Progress"`，然後
  `set-field <story> "Last Updated" <YYYY-MM-DD> --after Status`。在 `minimal`，
  story 檔是唯一的進度紀錄。
- `production/sprint-status.yaml`：這個 story 的條目改成 `status: in-progress`，
  最上層的 `updated` 改成今天。沒有這個檔：就說 `Sprint status not updated:
  production/sprint-status.yaml absent`。

使用者拒絕：兩個都不改，在摘要裡印出 `Story not marked In Progress — declined`，
然後繼續。

## Phase 4: Who implements it

**Config/Data 類的 story 不需要 agent。** 把每個值的變更用 from → to 秀出來，問「May
I write [data file]?」，然後直接編輯。跳到 Phase 6。

| Story | Programmer agent |
|---|---|
| Foundation layer, any type | `engine-programmer` |
| Type UI | `ui-programmer` |
| Type Visual/Feel | `gameplay-programmer` |
| Core or Feature, gameplay | `gameplay-programmer` |
| Core or Feature, AI or pathfinding | `ai-programmer` |
| Core or Feature, networking | `network-programmer` |

**Engine specialist，每個程式碼 story 都要。** 從上面的 `specialists` 那行取：
`code`（`specialists.code`，語言 specialist：它分得出 Godot C# 專案和 GDScript 專案，
`engine.name` 做不到），加上 story 碰到 shader 或 material 時的 `shader`，
UI story 的 `ui`；當 `code` 是 `unset` 時，用 `primary`（通用的 engine
specialist）。不要憑記憶指定任何 specialist：那一行是專案自己的選擇。
每個值都是 `unset` 又沒有 `primary`：就說「No engine specialist configured」，
不帶 specialist 繼續做。

## Phase 5: Hand out the work

把實作交給 programmer agent。brief 只指向檔案；絕對不要把整份文件貼進去。

- **Objective：** 依照驗收條件實作 [story path]，並且守在它的
  Out of Scope 邊界內。
- **Sources：**
  1. story 檔。它帶有驗收條件、邊界和 QA 測試案例。
  2. 每個要查的 TR-ID（`TR-[system]-NNN`）：在
     `docs/architecture/tr-registry.yaml` 裡，找符合 `id: <TR-ID>\s*$` 的那幾行。
     它的 `requirement` 文字才是唯一依據，story 裡引用的文字不算。
  3. ADR 的指引，**直接內嵌**：story 裡的 ADR Decision Summary 和
     Implementation Notes。絕對不要給 ADR 路徑。
  4. control manifest 的 [Layer] Layer Rules，依章節取。
  5. `project.yaml` 裡的 `naming.*` 和上面的 `perf_budgets` 那行。
  6. story 的 Test Evidence 章節裡的測試檔路徑。
- **Tests，** 依 `qa.level`，針對 Logic 和 Integration 的 story：
  - `minimal`：「Do not write a test file for this story — test evidence is waived at
    `qa.level: minimal`.」要明說：少寫一行跟忘了寫一行，對 agent 來說看起來一樣。
  - `standard`：「Write the test at [path] with the code. Each acceptance criterion
    needs at least one test function.」命名規則依各 engine，見
    `.claude/rules/test-standards.md`。不用 random seed、不做跟時間有關的
    斷言、不碰外部 I/O。
  - `full`：同上，再加「every criterion must be covered: `/story-done` blocks on
    any untested one.」
- **Output：** 建立或修改的檔案、寫了哪些測試函式、任何
  問題或阻礙，以及有沒有做完。
- **Boundaries：** 程式碼只寫在解析出來的 code root 底下，測試只寫在
  test root 底下。code root 解析不出來：什麼都不寫，並回報這件事。不准碰
  story 範圍外的檔案：改成回報有這個需求。公開 API 要寫 doc comment。
  ADR 沒涵蓋到的架構選擇：回報你的計畫，不要自己決定。
  只用一次的東西不要做 helper 或抽象，不可能發生的情況不要寫錯誤處理（只在輸入和資料檔邊界做驗證），
  邏輯要通用，絕對不准為了讓測試過就把某個值特例處理。

**把 brief 漏掉的東西講清楚，兩邊都要講。** Phase 2 發現缺少的輸入
（TR registry、ADR、manifest）就不放進 brief：告訴 agent「No [input] is
passed — it does not exist at this tier; do not go looking for it」，並在派工前
用一行告訴使用者：`Briefing omits: [inputs] — implementing against
the acceptance criteria and the [GDD | brief].`

**programmer 回報之後，再把 engine 檢查交給 specialist。**
Brief：針對 [engine + version]，對照 `docs/engine-reference/<engine>/`，檢查有改動的檔案裡
有沒有用錯或已變動的 engine API；回傳一份清單，每項包含
檔案、行號、問題、修法；什麼都不准改。會破壞某條驗收條件的問題，退回
programmer 一次；其餘的寫進摘要。

## Phase 6: Check the result

**agent 做完了嗎？** 它提早停了、撞到上限，或它的回報停在
做到一半：這個 story 就是 **INCOMPLETE**。把這點當標題講，列出現有的東西，
指出壞在哪，並提議恢復那個 agent。絕對不要在它上面印「Implementation Complete」，
status 也維持原樣。

**它寫的跟它說的一樣嗎？** 先驗證產出物：agent 的回報裡點名的檔案如果
不在磁碟上，這一步就是失敗，不管回報寫得多流暢：恢復 agent 並點名缺的
檔案。回報是 BLOCKED、錯誤，或「cannot complete」：馬上說出來，被擋住的部分就不再往下做，
並給一份部分完成的報告
（`.claude/docs/error-recovery-protocol.md`）。範圍太大：用
`/create-stories` 拆開。ADR 和 story 互相矛盾：回報衝突；絕對不要猜。

**測試在嗎？** 在 `qa.level: standard` 和 `full`，對 Logic 或 Integration
story，去 Test Evidence 路徑找那個檔案。沒有：如果是 `gate_level` 那行裡該 type 的 BLOCKING
等級，標記「story unverifiable — test required before
`/story-done`」；如果是 ADVISORY，就當建議記下來。在 `minimal` 沒什麼好查的：
測試是豁免的。

**能 parse 嗎？** 跑一個用 exit code 就能回答的檢查，並回報
指令、exit code 和任何錯誤行：

- **Godot：** 先跑一次 `godot --headless --path . --import`，再跑
  `godot --headless --path . -s res://.claude/scripts/godot-parse-check.gd -- res://<each changed .gd>`。
  Exit 1 代表有 script 沒載入成功；它的 `PARSE FAIL:` 那行會點名。絕對不要用
  `--check-only`，單跑 `--import` 也不算 parse 檢查。可執行檔的選擇：`commands.test`
  指定的那個（當它的檔名看得出是 godot 時；像 `bash
  run-tests.sh` 這種 wrapper 不是 editor），否則 `engine.path`，再否則 `godot`。絕對不要在磁碟上
  搜尋：三個都跑不起來的話，這個檢查就是 not verified。
- **Unity、Unreal：** 去讀 `references/engine-checks.md`。
- **沒有 engine 可執行檔：** `parse NOT VERIFIED — engine binary not available`。
  絕對不要靠讀程式碼就推斷它能 parse。

**跑起來看看**（`.claude/docs/run-and-observe.md`）。對每個玩家看得到的 story
（每個 Visual/Feel 和 UI story，還有其他任何有畫面表現的）：直接啟動到這個 story 碰到的 scene，
把截圖直接存到 `production/qa/evidence/[story-slug]/`（`[story-slug]` 是 story 檔去掉 `.md` 的檔名；
先 `mkdir -p` 建資料夾），再用
`bash .claude/scripts/review-receipts.sh hash <each changed file> > production/qa/evidence/[story-slug]/stamp.txt`
蓋章，然後打開圖片，跟驗收條件比對。在 `qa.level:
minimal` 也不豁免。只回報一行，純文字、以 `Run result:` 開頭（不要加粗：
`/story-done` 是照原樣讀的）：

- `Run result: OBSERVED — <what was on screen>`，附上保留下來的路徑；
- `Run result: NOT VERIFIED — <reason>`（沒有 engine、沒抓到任何東西）；在
  預設的 gate level，這會讓 Visual/Feel 或 UI story 在 `/story-done` 被擋住；
- `Run result: N/A — <reason>`，給沒有任何可觀察內容的 story；理由要說清楚
  為什麼沒有（`/story-done` 不接受「it's a Logic story」）。

只有 Visual/Feel 條件裡「手感」那一半（時機、重量）會延後到
`/team-qa`：靜態圖看不出來。

這個 skill 預先核准了 PATH 上的 `godot`。透過 `engine.path` 或
`commands.test` 指定的可執行檔去跑 engine，要先問：使用者核准一次，或
把 `Bash(<that executable> *)` 加進 `.claude/settings.local.json`。

## Phase 7: Summary, files, checkpoint

```
## Implementation Complete: [title]

**Files changed**:
- `[code root path]` — created / modified ([what])
- `[test path]` — [N] test functions
**Test evidence**: waived at `qa.level: minimal` — no test was required or written   (Logic/Integration at minimal, instead of the test line)
**Verification**: [command] — [exit code and result | parse NOT VERIFIED — <reason>]

**Acceptance criteria**:
- [x] [criterion] — [file:function | test name | OBSERVED in <image path>]
- [ ] [criterion] — DEFERRED: feel, needs a playtest
**Deviations**: [None | files outside scope, an accepted dependency or version risk]
**Engine risks**: [None | the specialist's findings]
**Blockers**: [None | each]
```

在 `qa.level: standard` 和 `full`，加上：「Run your test suite and confirm the new
tests pass before `/story-done`: it checks that the test file exists, and runs
nothing.」在 `minimal` 就省略這句：沒有測試可跑。對沒有保留圖片的 Visual/Feel
或 UI story，加上：「A retained screenshot under
`production/qa/evidence/[story-slug]/` is required before `/story-done`」（Visual/Feel 另外要加，
`production/qa/evidence/[story-slug]-evidence.md` 裡的 sign-off）。

**`## Files`。** 把這個章節的內容換成改過的程式碼和測試檔清單，
一行一個，就像 Phase 3 的提問所說的：
`bash .claude/scripts/md-section.sh replace <story> "Files"`，清單從 stdin 傳入。
story 沒有這個章節：在它的結尾加上 `## Files` 和清單，用
檔案編輯的方式，絕對不要用 shell 指令（shell 寫入會跳過專案的寫入檢查）。
Phase 3 的提問被拒絕的話，這步就跳過。

**Checkpoint**，每種結果都要寫。把這個區塊 pipe 給
`bash .claude/scripts/session-state.sh checkpoint`，它會取代舊的：

```
**Updated:** [date]
**Branch:** `[current git branch]`
**Current task:** /dev-story — [story path] ([title])
**Next step:** [the Next step below]
**Blocked on:** [nothing, or the blocker]
**Files in progress:** [changed files, comma-separated]
**Run result:** [OBSERVED — … | NOT VERIFIED — … | N/A — …, as in the closing block: /story-done reads it here]
**Open questions:** [none, or one line each]
```

**這次執行的最後一則回覆要以這個區塊結尾**，這是唯一會印出 `Run result:` 那行的地方：
回覆裡其他地方都不要印。Next step 依你在 Phase 1 說出的 tier 決定（看 `workflow` 那行，
絕對不是 `rigor` 或 `qa.level`）。Next step：在 `minimal`，`/story-done [path]`。在 `standard` 和 `full`，
`/code-review [files]`，然後 `/story-done [path]`。INCOMPLETE：`/dev-story [path]`
來恢復。BLOCKED：能解除阻礙的動作（`/architecture-decision accept
ADR-NNNN`、要先完成的相依項目、要 review 的 diff）。

```
Story: [path] — [Implemented | INCOMPLETE — <breakage> | BLOCKED — <reason>]
Run result: [OBSERVED — … | NOT VERIFIED — … | N/A — …]
Next step: [Implemented, Tier: workflow minimal → /story-done [path] | Implemented, Tier: workflow standard or full → /code-review [changed files], then /story-done [path] | INCOMPLETE → /dev-story [path] to resume | BLOCKED → the unblocking action]
```
