---
name: day-one-patch
description: "首日上線 patch：針對 gold master 之後發現的已知問題做集中修正。含 QA gate 和 rollback 的迷你 sprint。"
argument-hint: "[scope: known-bugs | cert-feedback | all]"
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion
model: sonnet
---

# Day-One Patch

每款上市的遊戲都有首日 patch。在上線日之前先規劃好，才不會
亂成一團。這個 skill 把 patch 的範圍限縮在安全又必要的東西，
用輕量的 QA 把關，並確保在任何東西出貨之前就有 rollback 計畫。
它是一個迷你 sprint，不是 hotfix，也不是完整的 sprint。

**何時執行：**
- gold master build 鎖定之後（cert 通過，或 launch candidate 已打 tag）
- 有已知 bug，但風險太高、不適合在 gold master 處理
- cert 回饋要求送件後做小幅修正
- 發行 gate 通過之後，上市前的 playtest 又浮出必修的問題

**首日 patch 的範圍規則：**
- 只放修起來安全的 P1/P2 bug
- 不加新功能，只修 bug
- 不重構，只做最小可行的改動
- 任何需要超過 4 小時開發時間的修正，都歸到 patch 1.1，不是首日

**輸出：** `production/releases/day-one-patch-[version].md`

---

## Phase 1: 載入發行 Context

讀：
- `project.yaml` 的 `project.stage`（退回 `production/stage.txt`）：確認專案在 Release 階段
- `production/gate-checks/` 裡最新的檔案：讀發行 gate 的 verdict
- `production/qa/bugs/*.md`：載入所有 Status 是 Open 或 Fixed — Pending Verification 的 bug
- `production/sprints/` 最新的：了解出貨了什麼
- 最新的 `production/security/security-audit-*.md`：檢查有沒有任何未解決的安全項目

如果解析出來的階段（project.yaml → stage.txt）不是 `Release` 或 `Polish`：
> "Day-one patch prep is for Release-stage projects. Current stage: [stage]. This skill is not appropriate until you are approaching launch."

**檢查前提，不要假設。** 這整個 skill 建立在「有一份已經通過發行 gate 的
gold master」之上，這個前提正是它可以用輕量 QA、
而不是完整 QA 的理由。所以要驗證，不要從階段的值去推論：

- **`production/gate-checks/` 裡沒有檔案**，或沒有任何一份記錄發行 gate 的
  verdict：回報 `Release gate: NOT ASSESSED — no gate-check record found`。
  不要默默繼續。要明白說出下面縮減的 QA 範圍，是靠一個
  沒人找得到的 gate 撐腰的，並問是要先跑 `/gate-check`，還是
  改走完整的 QA 繼續。
- **最近一份紀錄是 FAIL、CONCERNS 或 NOT ASSESSED**：點名並停下。
  在一個從沒通過 gate 的 build 上做首日 patch，就不是首日 patch；
  那是遲到的發行 gate，而且範圍框在錯的變更上。
- 光靠 `project.stage: Release` **不能**證明這件事。階段只是
  對專案在哪裡的一個宣稱；gate 紀錄才是它配得上那個位置的證據。

---

## Phase 2: 框定 Patch 範圍

### Step 2a：分類哪些開著的 bug 要放進 patch

每個開著的 bug 都要評估：

| Criterion | Include in day-one? |
|-----------|-------------------|
| S1 or S2 severity | Yes — must include if safe to fix |
| P1 priority | Yes |
| Fix estimated < 4 hours | Yes |
| Fix requires architecture change | No — defer to 1.1 |
| Fix introduces new code paths | No — too risky |
| Fix is data/config only (no code change) | Yes — very low risk |
| Cert feedback requirement | Yes — required for platform approval |
| S3/S4 severity | Only if trivial config fix; otherwise defer |

### Step 2b：把 patch 範圍呈現給使用者

用 `AskUserQuestion`：
- Prompt: "Based on open bugs and cert feedback, here is the proposed day-one patch scope. Does this look right?"
- 顯示：納入的 bug 表（ID、嚴重度、描述、預估工時）
- 顯示：延後的 bug 表（ID、嚴重度、延後的原因）
- 選項：`[A] Approve this scope` / `[B] Adjust — I want to add or remove items` / `[C] No day-one patch needed`

選 [C]：輸出 "No day-one patch required. Proceed to `/launch-checklist`." 然後停。

### Step 2c：檢查總範圍

加總預估工時。如果總計超過 1 天的工作量：
> "⚠️ Patch scope is [N hours] — this exceeds a safe day-one window. Consider deferring lower-priority items to patch 1.1. A bloated day-one patch introduces more risk than it removes."

用 `AskUserQuestion` 確認是繼續還是縮小範圍。

---

## Phase 3: Rollback 計畫

在寫任何程式碼之前，先定義 rollback 程序。這點沒得商量。

用 `Agent` spawn `release-manager`。請他們產出一份 rollback 計畫，涵蓋：
- 在每個目標平台上怎麼還原成 gold master build
- 平台特有的 rollback 限制（有些平台沒辦法回退 cert 過的 build）
- 誰負責觸發 rollback
- 如果發生 rollback，需要哪些玩家溝通

呈現 rollback 計畫。問："May I write this rollback plan to `production/releases/rollback-plan-[version].md`?"

rollback 計畫沒寫好之前，不准進 Phase 4。

---

## Phase 4: 實作修正

核准範圍內的每個程式碼修正，都 spawn 一個聚焦的實作迴圈：

1. 用 `Agent` spawn `lead-programmer`，給它：
   - bug 報告（精確的重現步驟，如果知道的話還有根本原因）
   - 限制：只做最小可行的修正，不要順手清理
   - 受影響的檔案（來自 bug 報告的 Technical Context 章節）

   它對每個 bug 回傳最小修正，以及會動到的檔案，
   不寫任何東西。

2. 對整組問一次："May I apply these fixes? [BUG-ID → files, one
   line each]"。沒有這個核准，不准改任何程式碼。

3. 回答 yes 的話，把每個核准的修正交回給 `lead-programmer`（帶著它的計畫發一個新的 `Agent` 呼叫）去實作，
   並用 `project.yaml` 的 `commands.test` 跑有針對性的測試，
   runner 允許的話縮小到受影響的 suite，絕對不要憑記憶寫 runner 指令。如果 `commands.test` 沒設定，就說出來，
   並替那個 bug 記錄 `Tests: NOT RUN — commands.test unset`。

4. 用 `Agent` spawn `qa-tester` 來驗證：修正之後 bug 還會重現嗎？

只改 config/data 的修正：直接改（不需要 programmer agent）。先問，要點名檔案和變更："May I edit `[config file]` — `[key]`: [old value] → [new value]?" 確認值有變，並重跑任何相關的 smoke test。

---

## Phase 5: Patch QA Gate

這是輕量的 QA，不是完整的 `/team-qa`。patch 在發行 gate 時已經通過 QA；我們只是重新驗證有改動的地方。

用 `Agent` spawn `qa-lead`，給它：
- 所有改動檔案的清單
- 所有修好的 bug 清單（附 Phase 4 的驗證狀態）
- 受影響系統的 smoke check 範圍

請 qa-lead 判斷：**有針對性的 smoke check 就夠了，還是有任何修正動到需要更廣泛 regression 的系統？**

執行需要的 QA 範圍：
- **有針對性的 smoke check**：跑 `/smoke-check`（它不接受系統參數）
- **更廣泛的 regression**：用 `project.yaml` 的 `commands.test`，跑引擎測試根目錄裡受影響系統的測試（Godot 是 `tests/unit/` 和 `tests/integration/`、Unity 是 `Assets/Tests/`、Unreal 是 `Source/<Module>/Private/Tests/`，見 `.claude/docs/directory-structure.md`），runner 允許的話縮小到受影響的 suite，絕對不要憑記憶寫 runner 指令。如果 `commands.test` 沒設定，更廣泛的 regression 就是 NOT ASSESSED；要說出來。

QA verdict 必須是 PASS 或 PASS WITH WARNINGS 才能繼續。如果是 FAIL：把失敗的那個修正排出首日 patch，延到 1.1。

**如果 QA verdict 是 `NOT ASSESSED`，那不算通過。** `/smoke-check` 在測試套件從沒跑過時
會回傳它：沒有 build、沒有 runner，或是沒人確認過的結果。
不要在它之上繼續，也不要把它重新解讀成 PASS WITH WARNINGS：warnings
的意思是有人看過、看到一些小問題，而這個的意思是沒人看過。
要嘛取得結果（verdict 會指出什麼能讓它可以跑），要嘛把
修正延到 1.1。首日 patch 會送到每一個首日買遊戲的玩家手上，
對沒驗證過的改動來說，那是最糟的受眾。

---

## Phase 6: 產生 Patch 紀錄

```markdown
# Day-One Patch: [Game Name] v[version]

**Date prepared**: [date]
**Target release**: [launch date or "day of launch"]
**Base build**: [gold master tag or commit]
**Patch build**: [patch tag or commit]

---

## Patch Notes (Internal)

### Bugs Fixed
| BUG-ID | Severity | Description | Fix summary |
|--------|----------|-------------|-------------|
| BUG-NNNN | S[1-4] | [description] | [one-line fix] |

### Deferred to 1.1
| BUG-ID | Severity | Description | Reason deferred |
|--------|----------|-------------|-----------------|
| BUG-NNNN | S[1-4] | [description] | [reason] |

---

## QA Sign-Off

**QA scope**: [Targeted smoke / Broader regression]
**Verdict**: [PASS / PASS WITH WARNINGS / NOT ASSESSED]
**QA lead**: qa-lead agent
**Date**: [date]
**Warnings (if any)**: [list or "None"]
**Not assessed (if any)**: [what could not be checked, and why — or "None"]

---

## Rollback Plan

See: `production/releases/rollback-plan-[version].md`

**Trigger condition**: If [N] or more S1 bugs are reported within [X] hours of launch, execute rollback.
**Rollback owner**: [user / producer]

---

## Approvals Required Before Deploy

- [ ] lead-programmer: all fixes reviewed
- [ ] qa-lead: QA gate PASS confirmed
- [ ] producer: deployment timing approved
- [ ] release-manager: platform submission confirmed

---

## Player-Facing Patch Notes

[Draft for community-manager to review before publishing]

[list player-facing changes in plain language]
```

問："May I write this patch record to `production/releases/day-one-patch-[version].md`?"

---

## Phase 7: 下一步

patch 紀錄寫好之後：

1. 跑 `/patch-notes`，產生 patch notes 的玩家版
2. patch 上線之後，每個修好的 bug 都跑 `/bug-report verify [BUG-ID]`
3. 每個驗證過的修正都跑 `/bug-report close [BUG-ID]`
4. 上線後 48–72 小時，用 `/retrospective [milestone-name]` 排一次上線後檢討，針對 `production/milestones/` 裡的上線 milestone

**如果 patch 之後仍有任何 S1 bug 還開著：**
> "⚠️ S1 bugs remain open and were not patched. These are accepted risks. Document them in the rollback plan trigger conditions — if they occur at scale, rollback may be preferable to a follow-up patch."

用 `AskUserQuestion`：
- Prompt: "Day-one patch complete. What's next?"
- 選項：
  - `[A] Run /patch-notes — generate player-facing patch notes`
  - `[B] Run /bug-report to log any issues found post-deploy`
  - `[C] Stop here`

---

## 協作協定

- **守住範圍就是一切**：抗拒 scope creep；每多加一項，風險就多一分
- **永遠先有 rollback 計畫**：沒有 rollback 計畫的 patch 就是不負責任
- **延後不等於遺忘**：每個延後的 bug 都列在紀錄的
  "Deferred to 1.1" 表裡；之後跑 `/bug-triage`，把它們排進 1.1 sprint
  （如果專案沒有 sprint 計畫，像預設的 minimal workflow，就排進 brief 的 build order）
- **玩家溝通是 patch 的一部分**：`/patch-notes` 是必要的輸出，不是選用
