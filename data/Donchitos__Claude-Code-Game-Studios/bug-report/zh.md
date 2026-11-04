---
name: bug-report
description: "從描述產出結構化的 bug 報告，或分析程式碼找潛在 bug。含重現步驟與嚴重度。"
argument-hint: "[description] | analyze [path-to-file] | verify [BUG-ID] | close [BUG-ID]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(bash "*/.claude/skills/bug-report/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次檔案寫入都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。

# Bug Report

**只寫草稿。** 這個 skill 把報告寫到 `production/qa/bugs/`。如果
原因出在引擎、plugin 或其他廠商的程式碼，就在 **Notes** 底下加一份給他們
tracker 的草稿，然後到此為止：絕對不要在他們的 repository 裡
建立、開啟 issue 或 pull request，也不要在上面留言。由使用者自己送出。

## Phase 1: 解析參數

依參數判斷模式：

- 沒有關鍵字 → **Description Mode**：根據提供的描述產生結構化的 bug 報告
- `analyze [path]` → **Analyze Mode**：讀目標檔案，找出潛在 bug
- `verify [BUG-ID]` → **Verify Mode**：確認回報的修正真的解決了 bug
- `close [BUG-ID]` → **Close Mode**：把驗證過的 bug 標記為已關閉，並附上解決紀錄

如果沒有給參數，先向使用者要 bug 描述再繼續。

---

## Phase 2A: Description Mode

1. **解析描述**，找出關鍵資訊：什麼壞了、什麼時候、怎麼重現、預期行為是什麼。

2. **用 Grep/Glob 搜尋程式碼庫**裡相關的檔案，補充 context（受影響的系統、可能的檔案）。

3. **起草 bug 報告**：

```markdown
# Bug Report

## Summary
**Title**: [Concise, descriptive title]
**ID**: BUG-[NNNN]
**Severity**: [S1-Critical / S2-High / S3-Medium / S4-Low]
**Priority**: [P1-Fix this sprint / P2-Fix soon / P3-Backlog / P4-Won't fix]
**Status**: Open
**Reported**: [Date]
**Reporter**: [the reporter's name as the user gives it, else `—`; never an email address or account ID taken from the session]

## Classification
- **Category**: [Gameplay / UI / Audio / Visual / Performance / Crash / Network]
- **System**: [Which game system is affected — when the bug spans systems, the one whose code must change; the others go under Related systems]
- **Frequency**: [Always / Often (>50%) / Sometimes (10-50%) / Rare (<10%)]
- **Regression**: [Yes/No/Unknown -- was this working before?]

## Environment
- **Build**: [Version or commit hash]
- **Platform**: [OS, hardware if relevant]
- **Scene/Level**: [Where in the game]
- **Game State**: [Relevant state -- inventory, quest progress, etc.]

## Reproduction Steps
**Preconditions**: [Required state before starting]

1. [Exact step 1]
2. [Exact step 2]
3. [Exact step 3]

**Expected Result**: [What should happen]
**Actual Result**: [What actually happens]

## Technical Context
- **Likely affected files**: [List of files based on codebase search]
- **Related systems**: [What other systems might be involved]
- **Possible root cause**: [If identifiable from the description]

## Evidence
- **Logs**: [Relevant log output if available]
- **Visual**: [Description of visual evidence]

## Related Issues
- [Links to related bugs or design documents]

## Notes
[Any additional context or observations]
```

**Severity** 和 **Priority** 的標籤用的是 `/bug-triage` 的 S 和 P 編號與
名稱，它會從這個檔案裡把它們解析出來。`P4-Won't fix` 對應它的 `P4 — Won't fix /
Deferred`（接受的風險），不是願望清單。如果你改了任何一個等級表，
`.claude/skills/bug-triage/SKILL.md` 也要一起改。

---

## Phase 2B: Analyze Mode

1. **讀參數指定的目標檔案**。

2. **找出潛在 bug**：null 參照、off-by-one 錯誤、race condition、沒處理的邊界情況、資源洩漏、錯誤的狀態轉換。

3. **每個潛在 bug** 都用上面的範本產生一份 bug 報告，把可能的觸發情境和建議的修正填進去。

---

## Phase 2C: Verify Mode

**用編號找 bug 檔案**，這裡和 close 模式都一樣：Glob
`production/qa/bugs/BUG-*.md`，取編號對得上 `[BUG-ID]` 的那個檔案，
不管它補了幾個零，較舊的、三位數且帶 slug 的檔案，也是用編號找得到。如果
沒有符合的，就停："No bug [BUG-ID] in `production/qa/bugs/`." Verdict: **BLOCKED**
— no such bug.

讀那個檔案。擷取重現步驟和預期結果。

1. **重跑重現步驟**：用 Grep/Glob 檢查根本原因的程式碼路徑是否仍然像描述的那樣存在。如果修正把它移除或改掉了，記下這個變更。
2. **跑相關的測試**：如果這個 bug 的系統在引擎的測試根目錄裡有測試檔（Godot 是 `tests/`、Unity 是 `Assets/Tests/`、Unreal 是 `Source/<Module>/Private/Tests/`，見 `.claude/docs/directory-structure.md`），就用 Bash 搭配 `project.yaml` 的 `commands.test` 去跑它，runner 允許的話縮小到受影響的 suite，絕對不要憑記憶寫 runner 指令，那會漏掉引擎需要的旗標（gdUnit4 沒有 `--remote-debug tcp://127.0.0.1:0` 就會卡住），然後回報通過或失敗。`commands.test` 沒設定 → 沒有跑任何測試：點名沒設定的 key，然後繼續做步驟 3。
3. **檢查有沒有 regression**：在程式碼庫裡 grep，找有沒有任何新出現的、造成這個 bug 的同樣模式。
4. **手動驗證**：沒有跑任何相關測試時（沒有測試涵蓋這個 bug，也就是 `qa.level` 免除測試的常見情況；`commands.test` 沒設定；或是測試沒有跑完），或是 bug 的 Category 是 Visual 或 UI（它們的外觀沒有任何自動化測試會檢查），就透過 `AskUserQuestion` 問："Did you play the reproduction steps in [bug file] on a build with the fix? Which build?" ——
   `[No longer occurs]` / `[Still occurs]` / `[Not played yet]`。
   使用者怎麼回答、哪個 build，就照實記錄；程式碼路徑有變，絕對不能當成他們的答案。
   **當成 subagent 跑？** `qa-lead` 會預先載入這個 skill，而 subagent 沒有
   `AskUserQuestion`。回覆的結尾把問題和它的三個選項用短清單列出來，先不要給 verdict：
   呼叫你的那一方會去問使用者，verdict 要等答案回來。

產出驗證的 verdict：

- **VERIFIED FIXED**：所有適用的檢查都顯示 bug 已經消失：任何相關測試都跑了而且通過，而且在步驟 4 有問的情況下，使用者針對某個指名的 build 回答 `[No longer occurs]`。沒跑測試的話，那次親自玩過就是唯一的驗證，這是手動驗證，要照這樣記錄：`[user], manual, build [X]`。光是程式碼路徑有變，絕對不算通過
- **STILL PRESENT**：相關測試在 bug 的案例上失敗，或使用者回答 `[Still occurs]`；修正沒有解決問題
- **CANNOT VERIFY**：步驟 4 的回答是 `[Not played yet]`：指出缺了什麼或什麼跑不了（沒有相關測試、`commands.test` 沒設定、測試沒跑完、Visual 或 UI 的 bug），並說明親自玩過重現步驟就能定案，玩過之後再跑一次 `/bug-report verify [BUG-ID]`

問："May I update `production/qa/bugs/[bug file]` to set Status: Verified Fixed / Still Present / Cannot Verify?"，要點名上面找到的那個檔案，不管它補了幾個零或有沒有 slug。寫入 Status 的同時，在它底下寫一行 `**Verified by**:`：`[test file(s)] — ran and passed`，手動驗證的話寫 `[user], manual, build [X]`。

如果是 STILL PRESENT：重新開啟 bug，把 Status 改回 Open，並建議重跑 `/hotfix [BUG-ID]`。

---

## Phase 2D: Close Mode

讀 bug 檔案，用編號找，做法跟 verify 模式一樣。關閉之前先確認 Status 是 `Verified Fixed`。如果狀態是別的，就停："Bug [ID] must be Verified Fixed before it can be closed. Run `/bug-report verify [BUG-ID]` first."

顯示下面的關閉紀錄和 Status 的變更，然後問："May I update `production/qa/bugs/[bug file]` to mark it Closed?" 沒有 yes 之前什麼都不寫；回答 no 就停，bug 維持 Verified Fixed。

回答 yes 的話，把關閉紀錄附加到 bug 檔案後面：

```markdown
## Closure Record
**Closed**: [date]
**Resolution**: Fixed — [one-line description of what was changed]
**Fix commit / PR**: [if known]
**Verified by**: [the verify record's `**Verified by**:` line — the test that ran and passed, or "[user], manual, build [X]"]
**Closed by**: [user]
**Regression test**: [test file path, or "Manual verification" when verify recorded a manual play]
**Status**: Closed
```

然後把最上層的 `**Status**:` 欄位更新成 `**Status**: Closed`。

關閉後，檢查 `production/qa/bug-triage-*.md`，如果這個 bug 出現在還開著的 triage 報告裡，就註明："Bug [ID] is referenced in the triage report. Run `/bug-triage` to refresh the open bug count."

---

## Phase 3: 儲存報告

把完成的 bug 報告呈現給使用者。

**先配好 ID** 再問：Glob `production/qa/bugs/BUG-*.md`，取最大的
編號加 1，補零到四位數（一個都沒有就是 `BUG-0001`）。一次執行有好幾份報告
（analyze 模式），就從那裡開始依序各拿一個連續的 ID，
絕對不准同一個 ID 用兩次。

問："May I write this to `production/qa/bugs/BUG-[NNNN].md`?" 好幾份
報告的話，問一次並點名每個檔案："May I write these to
`production/qa/bugs/BUG-[NNNN].md`, `production/qa/bugs/BUG-[NNNN+1].md`, …?"

回答 yes 就寫檔案，需要的話建立目錄。Verdict: **COMPLETE** — bug report filed.

回答 no 就停在這裡。Verdict: **BLOCKED** — user declined write.

---

## Phase 4: 下一步

存檔後，依模式建議：

**建檔後（Description/Analyze 模式）：**
- 跑 `/bug-triage`，跟現有還開著的 bug 一起排優先順序
- 如果是 S1 或 S2：跑 `/hotfix [BUG-ID]` 走緊急修正流程

**修好 bug 之後（開發者確認修正已經進去）：**
- 跑 `/bug-report verify [BUG-ID]`，關閉之前先確認修正真的有效
- 沒有驗證絕對不准把 bug 標成已關閉，驗證不過的修正仍然是 Open

**verify 回傳 CANNOT VERIFY 之後：**
- 在有修正的 build 上玩一遍重現步驟，然後再跑一次 `/bug-report verify [BUG-ID]`，並回答它的問題

**verify 回傳 VERIFIED FIXED 之後：**
- 跑 `/bug-report close [BUG-ID]`，寫入關閉紀錄並更新狀態
- 跑 `/bug-triage`，更新還開著的 bug 數量，並把它從現行清單移除
