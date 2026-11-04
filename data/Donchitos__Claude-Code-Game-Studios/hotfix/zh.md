---
name: hotfix
description: "繞過一般 sprint 流程的緊急修復：開 hotfix branch、追蹤核准、驗證 backport、留下完整稽核軌跡。"
argument-hint: "[bug-id or description]"
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(git rev-parse *), Bash(git tag --list*), Bash(git branch --list *)
model: sonnet
---

# Hotfix

> **只能明確叫用**：這個 skill 只有在使用者明確用 `/hotfix` 要求時才能執行。不准依脈絡比對自動叫用。

## Phase 1: Assess Severity

讀 bug 描述或 ID。依 `/bug-triage` 的量表評估嚴重度：

- **S1 (Critical)**：當機、資料遺失，或整個功能失效 — 遊戲無法繼續（安全問題依其影響來評級）
- **S2 (High)**：主要功能壞了，但遊戲還能玩
- **S3 或更低**：功能降級但有 workaround，或只是外觀問題 — 適用一般 bug 修復流程

用 `AskUserQuestion` 確認：
- Prompt: "I've assessed this as **[assessed severity]** — [brief rationale]. Confirm severity to proceed:"
- Options:
  - `[A] S1 (Critical) — crash, data loss, or complete feature failure`
  - `[B] S2 (High) — major feature broken, game still playable`
  - `[C] S3 or lower — redirect to normal bug fix workflow`

選 [C]：停下來。Verdict: **REDIRECTED** — S3 以下請用一般 bug 修復流程。

---

## Phase 2: Create Hotfix Record

起草 hotfix 紀錄：

```markdown
## Hotfix: [Short Description]
Date: [Date]
Severity: [S1/S2]
Reporter: [Who found it]
Status: IN PROGRESS

### Problem
[Clear description of what is broken and the player impact]

### Root Cause
[To be filled during investigation]

### Fix
[To be filled during implementation]

### Testing
[What was tested and how]

### Approvals
- [ ] Fix reviewed by lead-programmer
- [ ] Regression test passed (qa-tester)
- [ ] Release approved (producer)

### Rollback Plan
[How to revert if the fix causes new issues]
```

問：「May I write this to `production/hotfixes/hotfix-[date]-[short-name].md`?」

使用者答應就寫檔，目錄不存在的話先建立。

---

## Phase 3: Create Hotfix Branch

檢查這是不是 git repository：

`Bash: git rev-parse --is-inside-work-tree 2>/dev/null`

如果這個指令失敗或回傳空的：註明「Not a git repository — create the branch manually.」並跳過建立 branch。

`[base-ref]` 是 bug 所在的那個 release。Release 是 `main`（trunk）上的 tag，
所以它就是那個 release 的 tag（`git tag --list`；最新的通常就是
上線中的 build）— 或者它的 `release/*` branch，如果有為了穩定那個
release 而切出來的話（`git branch --list 'release/*'`）。絕對不是 `main` 的最新 head：它可能帶有
還沒發佈的工作。

如果檢查通過，建立 branch 之前先用 `AskUserQuestion`：
- Prompt: "Ready to create hotfix branch 'hotfix/[short-name]' from [base-ref]?"
- Options:
  - `[A] Yes — create branch`
  - `[B] Use a different base ref — I'll specify it`
  - `[C] Skip — I'll create the branch myself`

只有使用者選 [A] 才執行 `git checkout -b hotfix/[short-name] [base-ref]`。選 [B]：請使用者提供 base ref，然後用那個 ref 執行指令。選 [C]：跳過建立 branch，直接進 Phase 4。

---

## Phase 4: Investigate and Propose

找出根本原因。起草最小的修復：哪些檔案要改、改了什麼、以及刻意不動什麼。不准在 hotfix 裡順便 refactor、清理或加功能。

呈現根本原因和提議的修復，然後問：「May I implement this fix?」在這個核准之前不准修改任何程式碼 — 緊急流程要靠「在變更出現*之前*就核准」來換取它的稽核軌跡，而不是事後補。

---

## Phase 4b: Implement (only after approval)

實作核准過的最小變更。驗證修復的方式，是用 `project.yaml` 裡的 `commands.test` 針對受影響的系統跑目標測試（runner 允許的話，縮小到受影響的 suite）— 絕對不要憑記憶寫 runner 指令，那樣會漏掉 engine 需要的旗標（gdUnit4 沒有 `--remote-debug tcp://127.0.0.1:0` 就會卡住）。檢查相鄰系統有沒有 regression。如果 `commands.test` 沒設，或沒有測試涵蓋受影響的系統，就講出來，並在 hotfix 紀錄的 Testing 章節記下 `Tests: NOT RUN — [reason]`；Phase 5b 的 QA gate 就負責驗證。

用根本原因、修復細節和測試結果更新 hotfix 紀錄。

---

## Phase 5: Collect Approvals

用 `Agent` 工具平行請求簽核：

- `subagent_type: lead-programmer` — 審查修復的正確性和副作用
- `subagent_type: qa-tester` — 對受影響的系統跑目標 regression 測試
- `subagent_type: producer` — 核准部署時機和溝通計畫

三個都必須回傳 APPROVE 才能繼續。只要有任何一個回傳 CONCERNS 或 REJECT，就不准 deploy — 把問題攤出來，先解決它。

---

## Phase 5b: QA Re-Entry Gate

核准之後，判斷 deploy hotfix 之前需要多大的 QA 範圍。用 `Agent` 派出 `qa-lead`，帶上：
- hotfix 描述和受影響的系統
- Phase 5 的 regression 測試結果
- 所有會碰到被改檔案的系統清單（用 Grep 找呼叫端）

問 qa-lead：**完整的 smoke check 夠了嗎？還是這個修復需要針對性的 team-qa？**

套用判定：
- **Smoke check 夠了** — 對 hotfix build 跑 `/smoke-check`。如果是 PASS 或
  PASS WITH WARNINGS，進 Phase 6（把警告帶進 hotfix 紀錄）。
  如果是 **FAIL**，不准 deploy：帶著失敗的檢查回到 Phase 4，在那裡讓
  修訂後的修復取得核准，實作它（Phase 4b），然後重跑 Phase 5 的
  核准 — 包含 qa-tester 的 regression 測試 — 以及這個 QA 步驟。讓 smoke suite 壞掉的 hotfix
  是第二次事故，不是修復。
- **需要針對性的 QA** — 跑 `/team-qa feature: [affected-system]`，範圍只限變更過的系統。如果 QA 回傳 APPROVED 或 APPROVED WITH CONDITIONS，進 Phase 6；如果是 NOT APPROVED 或 BLOCKED，就當成上面的 smoke-check FAIL 處理。
- **需要完整 QA** — 動到核心系統的 S1 修復，可能需要完整的 `/team-qa sprint`。這會延後 deploy，但能防止壞 patch。

**如果 QA 步驟回傳 `NOT ASSESSED`，代表這個 gate 沒有執行 — 視為未達成，
不是已達成。** `/smoke-check` 在 suite 從來沒執行時會回傳它，
`/team-qa` 則是在某個週期沒有產生任何已執行的證據時。**NOT ASSESSED 的結果
不是通過** — 不管是哪個 skill — 而在時間壓力下，
寬鬆的解讀會讓人覺得合理，
這正是為什麼要把它寫在這裡。要嘛取得缺少的結果 —
判定會寫出要怎樣才能跑 — 要嘛明確把決定交給
producer，當成「決定 deploy 一個未驗證的 hotfix」，而不是
當成默默放行的 gate。把那個決定記在 hotfix 紀錄的 Testing 章節 — 誰決定的、為什麼。

不准跳過這個 gate。讓別的東西壞掉的 hotfix，比原本的 bug 更糟。

---

## Phase 6: Update Bug Status and Deploy

> **STOP — deploy 一律需要明確核准，沒有例外。** 合併 hotfix 並替 patch release 打 tag，
> 是這個 skill 裡唯一不可逆的動作，所以即使建立 branch（可逆）已經有 gate，
> 這裡還是要加 gate。在任何
> merge、tag 或 deploy 之前，用 `AskUserQuestion`：
>
> - Prompt: "Hotfix validated and approved. Merge to [targets], tag [patch tag]
>   and deploy?" — `[targets]` 是 `main`，再加上該 release 的 `release/*` branch
>   （只有它有的時候）
> - Options: `[A] Yes — merge and deploy` / `[B] Merge to main only — hold
>   the release` / `[C] Stop here`
>
> 不管 `modes.automation` 是什麼都一樣，包括 `autonomous`。緊急流程
> 正是沒經過審查的不可逆步驟最容易出現、也最難挽回的地方。

選 `[A]`：把 hotfix branch merge 到 `main`，如果該 release 有 `release/*`
branch 也 merge 過去；在修好的 build 上替 patch release 打 tag（下一個 patch 版本，例如
`v1.2.0` → `v1.2.1`）— 有 `release/*` branch 的話就是它的 head，
沒有就是 hotfix branch 的 head — 然後 deploy 那個 tag，不是 `main` 的
head。選 `[B]`：只 merge 到 `main` — 不 merge release branch、不打 tag、不
deploy。選 `[C]`：停下來 — 不 merge、不打 tag、不 deploy，也不更新 bug 檔；
hotfix 紀錄的 Status 維持 IN PROGRESS，並且把這點講出來。

> **Backport 除非你去驗證，否則就是沒驗證。** frontmatter 宣稱了
> 「backport verified」。merge 之後，確認修復有出現在 `main`（trunk）上
> — 如果該 release 有 `release/*` branch，也要確認它上面有 — 並說明
> 結果。沒 backport 的 hotfix，代表這個 bug 會在下一個從 `main` 打 tag 的
> release 回來，這是最常見的 hotfix regression。

如果有原本的 bug 檔就更新它 — 用編號在 `production/qa/bugs/`
裡找，就像 `/bug-report verify` 做的那樣。先問：「May I update
`production/qa/bugs/[bug file]` with the fix record below and set its Status to
`Fixed — Pending Verification`?」

```markdown
## Fix Record
**Fixed in**: hotfix/[branch-name] — [commit hash or description]
**Fixed date**: [date]
**Status**: Fixed — Pending Verification
```

在 bug 檔的標頭設定 `**Status**: Fixed — Pending Verification`。

輸出 deploy 摘要。標題依 Phase 6 的答案而定 — 選 `[A]` 就是 `Hotfix
Deployed: [short-name]`，選 `[B]` 就是 `Hotfix Merged to main — release held:
[short-name]` — 而選 `[B]` 時結尾那行要省略 Tag，因為沒有建立：

```
## Hotfix Deployed: [short-name]

**Severity**: [S1/S2]
**Root cause**: [one line]
**Fix**: [one line]
**QA gate**: [Smoke check PASS / Team-QA APPROVED / NOT ASSESSED — [why, and whose
             explicit decision it was to deploy anyway]]
**Approvals**: lead-programmer ✓ / qa-tester ✓ / producer ✓
**Backport**: [verified present on `main` (and the `release/*` branch, if the
              release has one) — or NOT VERIFIED, with what was not checked]
**Rollback plan**: [from Phase 2 record]

Merge to: [targets] · Tag: [patch tag]
Next: /bug-report verify [BUG-ID] after deploy to confirm resolution
```

### Rules
- hotfix 必須是修這個問題的最小變更 — 不清理、不 refactor
- 每個 hotfix 在 deploy 之前都必須先寫好 rollback 計畫
- hotfix branch 從它要修的那個 release 開始 — 它的 tag，或者它的 `release/*`
  branch（如果有的話）— 並 merge 到 `main`（trunk），而且只有在
  `release/*` branch 存在時才 merge 到它；patch release 要打 tag
- 所有 hotfix 都需要在 48 小時內做事後檢討
- 如果修復複雜到需要超過 4 小時，升級給 `technical-director`

---

## Phase 7: Post-Deploy Verification

deploy 之後，跑 `/bug-report verify [BUG-ID]`，確認修復在已 deploy 的 build 中解決了問題。

如果是 VERIFIED FIXED：跑 `/bug-report close [BUG-ID]` 正式結案。
如果是 STILL PRESENT：hotfix 失敗了 — 立刻重新開啟、評估 rollback，並升級處理。
如果是 CANNOT VERIFY：修復未經確認 — 不要關閉 bug；在已 deploy 的 build 裡照它的重現步驟玩一遍，然後再跑一次 `/bug-report verify [BUG-ID]`，並回答它的手動遊玩問題來定案。

安排 48 小時內的事後檢討。`/retrospective` 檢討的是
sprint 或 milestone，不是事故：用
`.claude/docs/templates/incident-response.md` 記錄這次檢討，並在下一次
`/retrospective` 提出其中的教訓。

使用 `AskUserQuestion`：
- Prompt: "Hotfix complete. What's the next step?"
- Options:
  - `[A] Run /smoke-check to verify the fix`
  - `[B] Run /patch-notes to document this hotfix`
  - `[C] Stop here`
