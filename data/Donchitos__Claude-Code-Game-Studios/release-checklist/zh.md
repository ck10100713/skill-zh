---
name: release-checklist
description: "發布前檢查清單：build 驗證、認證要求、商店 metadata、上線就緒度。"
argument-hint: "[platform: pc|console|mobile|all]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/release-checklist/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys rigor,workflow,project.stage,cert_tier,automation`

**自動化模式**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次寫檔，都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
屬於 `automation_always_ask` 的類別一律要詢問）。

上面已經解析完畢，直接用。沒有這個區塊的話，預設值看 `.claude/docs/config-resolution.md`。

# Release Checklist

**把這份檢查清單的範圍限縮到這個專案。** 每個平台的每個項目都全部列出來，
會讓讀的人養成跳過整份清單的習慣，關卡就形同虛設：

- **`project.stage`**：這個專案還沒走到的階段，對應的項目不在範圍內；
  直接說明這點，不要列出來然後全部沒勾。
- **`modes.rigor`**：在 `minimal` 時，把唯一理由是「流程負擔」的項目拿掉，
  這個專案已經選擇不要這些流程了。
- **`platform.cert_tier`**：認證項目**只**列出專案鎖定的那一級。如果它**沒設定**，
  就**先問哪些平台在範圍內**，不要全部列出來。沒設定是一個問題，
  不是把所有認證路線都列出來的許可。如果無法判斷，就把該段標成
  **`NOT ASSESSED — cert tier unknown`**。**沒設定不等於 `none`：** `none` 是一個決定，
  沒設定是缺少決定，兩者不能產出同樣的結果。
  依這個 key 的**四個值**分支，`none | itch | steam | console`，
  不要依平台名稱分支。完整的要求表在 `.claude/docs/effects-map.md` 的
  `## platform.cert_tier` 那一節，**只讀那一節**（先用 Grep 找標題，再做有範圍的 Read）；
  整個檔案不是執行時的輸入。
  - `none`：**完全不要輸出認證段落。** 內部發布、alpha 或 game jam 的遊戲。
    說明這段被省略以及原因，不要留空白。
  - `itch`：只列 itch.io 上傳要求：build 大小、頁面設定、年齡標籤。
    **不要有主機和 Steamworks 項目。**
  - `steam`：Steamworks：商店頁面、depot build、成就、系統需求、一般內容規範。
    **不要有主機認證項目。**
  - `console`：完整的平台認證（TRC / XR / Lotcheck）、存檔資料規則、
    手把按鍵對應規則、年齡分級機構。最重的一級。

  > **依上面的 `cert_tier` 值分支，不要依平台名稱。** 如果拿目標平台來判斷，
  > `itch` 專案和 `steam` 專案會被一視同仁，`none` 會跟沒設定混在一起，
  > 還會去比對 `mobile`，而 `mobile` 根本不是 `cert_tier` 的值。
  > 用設定檔定義的那套詞彙。

如果因為設定檔不存在而無法界定某個項目的範圍，就把它標成
**`NOT ASSESSED — platform/stage unknown`**。不要默默把它放進去：
否則一個 `rigor: standard`、單一平台的專案，會拿到約 150 項的檢查清單，
要求 PC **和**主機**和**手機的認證加上年齡分級，其中約 140 項根本無法評估。

---


## Phase 1: Parse Arguments

讀取參數取得目標平台（`pc`、`console`、`mobile` 或 `all`）。沒指定平台就預設 `all`。

**參數決定的是「裝置」要求，絕對不決定認證路線。** 認證由 `platform.cert_tier` 決定，
它在本 skill 最上面的解析設定區塊裡已解析好，
見上面的 `platform.cert_tier` 規則。這兩條軸是不同的清單，只是剛好用了同一個字：
`pc`/`console`/`mobile` 是硬體形態，`none|itch|steam|console` 是認證體系。
它們只在 `console` 上重疊，其他地方完全不相干：
`itch` 和 `none` 根本沒有裝置區塊，`mobile` 也不是 `cert_tier` 的值。
所以輸出某個裝置區塊，不代表該輸出哪個認證區塊，
而且 `all` **不是**輸出所有認證路線的許可。

---

## Phase 2: Load Project Context

- 讀 `CLAUDE.md`，取得專案背景、版本資訊和平台目標。
- 讀 `production/milestones/` 裡目前的 milestone，了解這次發布應該包含哪些功能和內容。
- 讀 `production/qa/bugs/` 裡尚未關閉的 bug：對 `production/qa/bugs/*.md` grep `**Severity**` 和 `**Status**` 這幾行，做法跟 `/bug-triage` 一樣。除非 Status 是 `Closed` 或 `Verified Fixed`，否則這個 bug 就算未關閉。bug 相關項目採用 `/gate-check release` 針對解析出來的 `workflow` 所用的門檻：在 `full` 時，只要有未關閉的 S1、S2 或 S3 bug，該項目就不通過；在 `standard` 和 `minimal` 時只有未關閉的 S1 會不通過，未關閉的 S2 或 S3 則當成風險列在 Rationale 裡。每一個造成不通過的 bug，都要在 Rationale 裡點名為阻擋項目。**如果 `production/qa/bugs/` 裡沒有 bug 檔案** → bug 項目寫 `NOT ASSESSED — no bug records`，絕對不要寫零，也不要打勾，因為「沒有紀錄」和「紀錄是乾淨的」不能產出同一份清單；bug 用 `/bug-report` 開單。

---

## Phase 3: Scan Codebase

> **每個數字都要註明分母。** 這些掃描是在找壞東西，
> 所以 `0` 可能是「搜過了，沒找到」，也可能是「根本沒東西可搜」，
> 在發布關卡上這兩個是相反的結論。要這樣回報：
> `scanned [N] source files: [M] TODO, [M] FIXME, [M] HACK`；或者在程式碼根目錄
> （`src/`、`Assets/` 或 `Source/`；依
> `.claude/docs/code-root-resolution.md` 解析）無法解析時，寫
> **`NOT ASSESSED — code root unresolved`**；在目錄不存在或裡面沒有
> 原始碼檔案時，寫 **`NOT ASSESSED — no source files found to scan`**。光寫一個 `0`
> 不算結果。

掃描尚未解決的問題：

- 計算 `TODO` 註解數量
- 計算 `FIXME` 註解數量
- 計算 `HACK` 註解數量
- 記下它們的位置和嚴重程度

如果有測試輸出目錄或 CI log，檢查裡面的測試結果。
**如果都找不到，要明講**：`Test results: NOT ASSESSED — no test output or
CI logs found`，不要把這一行省掉。「沒有測試結果」和「測試通過」
不能產出同一份發布檢查清單。

---

## Phase 4: Generate the Release Checklist

```markdown
## Release Checklist: [Version] -- [Platform]
Generated: [Date]

### Codebase Health
- Scanned: [N] source files (or `NOT ASSESSED — [reason]`, per Phase 3)
- TODO count: [N] ([list top 5 if many])
- FIXME count: [N] ([list all -- these are potential blockers])
- HACK count: [N] ([list all -- these need review])

### Build Verification
- [ ] Clean build succeeds on all target platforms
- [ ] No compiler warnings (zero-warning policy)
- [ ] All assets included and loading correctly
- [ ] Build size within budget ([target size])
- [ ] Build version number correctly set ([version])
- [ ] Build is reproducible from tagged commit

### Quality Gates
- Open bugs (`production/qa/bugs/`): [N] S1, [N] S2, [N] S3 -- or `NOT ASSESSED — no bug records`
- [ ] Zero open S1 (Critical) bugs
- [ ] Zero open S2 (High) and S3 (Medium) bugs, no exceptions -- this row at `workflow: full` only; at `standard`/`minimal` open S2/S3 bugs go in the Rationale as risks
- [ ] All critical path features tested and signed off by QA
- [ ] Performance within budgets:
  - [ ] Target FPS met on minimum spec hardware
  - [ ] Memory usage within budget
  - [ ] Load times within budget
  - [ ] No memory leaks over extended play sessions
- [ ] No regression from previous build
- [ ] Soak test passed (4+ hours continuous play)

### Content Complete
- [ ] All placeholder assets replaced with final versions
- [ ] All TODO/FIXME in content files resolved or documented
- [ ] All player-facing text proofread
- [ ] All text localization-ready (no hardcoded strings)
- [ ] Audio mix finalized and approved
- [ ] Credits complete and accurate
```

依參數加上**裝置**區塊。這些區塊不含認證或商店 SDK 項目，
那些放在下一小節，由 `platform.cert_tier` 控制；在這裡重複會讓 `itch` 專案拿到 Steamworks 的項目。

**`pc` 的情況：**
```markdown
### Platform Requirements: PC
- [ ] Minimum and recommended specs verified and documented
- [ ] Keyboard+mouse controls fully functional
- [ ] Controller support tested (Xbox, PlayStation, generic)
- [ ] Resolution scaling tested (1080p, 1440p, 4K, ultrawide)
- [ ] Windowed, borderless, and fullscreen modes working
- [ ] Graphics settings save and load correctly
```

**`console` 的情況：**
```markdown
### Platform Requirements: Console
- [ ] Platform-specific controller prompts display correctly
- [ ] Suspend/resume works correctly
- [ ] User switching handled properly
- [ ] Network connectivity loss handled gracefully
- [ ] Storage full scenario handled
```

**`mobile` 的情況：**
```markdown
### Platform Requirements: Mobile
- [ ] App store guidelines compliance verified
- [ ] All required device permissions justified and documented
- [ ] Privacy policy linked and accurate
- [ ] Data safety/nutrition labels completed
- [ ] Touch controls tested on multiple screen sizes
- [ ] Battery usage within acceptable range
- [ ] Background behavior correct (pause, resume, terminate)
- [ ] Push notification permissions handled correctly
- [ ] In-app purchase flow tested (if applicable)
- [ ] App size within store limits
```

> **手機的商店項目刻意留在這裡。** `platform.cert_tier` 的值是
> `none|itch|steam|console`，沒有手機這個體系，
> 所以 App Store / Play Store 的合規不能掛在它底下。把這些項目留在裝置區塊
> 是刻意的選擇，不是疏漏。不要去「修正」它，也不要發明一個 `mobile`
> 等級，那正是 `cert_tier` 規則警告過的錯誤詞彙。

**認證：只輸出符合 `platform.cert_tier` 的那一個區塊**（在本 skill 最上面的
解析設定區塊中已解析）。不要輸出這一小節的其他區塊，
也不要因為平台參數是 `all` 就退回去全部輸出。

**`none` 時**：完全不輸出認證區塊。改為只輸出下面這一行，
讓省略是看得見的，而不是看起來像漏掉一段：
```markdown
Certification: omitted — cert_tier is 'none' (internal build, alpha or jam release).
```

**`itch` 時：**
```markdown
### Certification: itch.io
- [ ] Build size within itch.io upload limits
- [ ] itch.io page complete (cover art, screenshots, description)
- [ ] Age/content tags set honestly
- [ ] Downloadable vs browser build decided and tested
- [ ] Butler channel names correct for each platform uploaded
```

**`steam` 時：**
```markdown
### Certification: Steamworks
- [ ] Steamworks SDK integrated and tested
- [ ] Depot build uploaded and installs cleanly from a fresh account
- [ ] Achievements functional
- [ ] Cloud saves functional
- [ ] Steam Deck compatibility verified (if targeting)
- [ ] Steam common content rules reviewed
```

**`console` 時：**
```markdown
### Certification: Console
- [ ] TRC/TCR/Lotcheck requirements checklist complete
- [ ] First-party certification submission prepared
- [ ] Platform-specific achievement/trophy integration tested
- [ ] Parental controls respected
- [ ] Save-data rules compliant (corruption, full storage, user switching)
- [ ] Age ratings obtained (ESRB, PEGI, regional)
```

如果 `cert_tier` **沒設定**，就問哪些平台在範圍內，不要
把每條路線都列出來；如果無法判斷，就輸出
`### Certification: NOT ASSESSED — cert tier unknown` 並說明原因。**沒設定不等於
`none`**：`none` 是一個決定，沒設定是缺少決定。

> **認證項目屬於這裡，放在同一個由 `cert_tier` 控制的小節。** 不要把它們
> 放進 PC、主機和手機的裝置區塊：那些區塊是由指令參數選的，
> 而且預設是 `all`，所以一個 `itch` 專案不帶參數跑
> `/release-checklist`，就會拿到 Steamworks SDK 的項目
> *和* Lotcheck 的項目，這違反本 skill 最上面的 `cert_tier` 規則。
>
> **`console` 在這個檔案裡有兩種意思。** 它既是裝置區塊的參數值，
> *也是* `cert_tier` 的值，四個字裡有一個撞名。
> `**For \`console\`:**` 這種標題是依參數控制，不是依等級控制，不要把它
> 當成認證範圍已經由等級界定的證據。

**商店與上線區段（所有平台）：**
```markdown
### Store / Distribution
- [ ] Store page metadata complete and proofread
  - [ ] Short description
  - [ ] Long description
  - [ ] Feature list
  - [ ] System requirements (PC)
- [ ] Screenshots up to date and per-platform resolution requirements met
- [ ] Trailers up to date
- [ ] Key art and capsule images current
- [ ] Age rating obtained and configured:
  - [ ] ESRB
  - [ ] PEGI
  - [ ] Other regional ratings as required
- [ ] Legal notices, EULA, and privacy policy in place
- [ ] Third-party license attributions complete
- [ ] Pricing configured for all regions

### Launch Readiness
- [ ] Analytics / telemetry verified and receiving data
- [ ] Crash reporting configured and dashboard accessible
- [ ] Day-one patch prepared and tested (if needed)
- [ ] On-call team schedule set for first 72 hours
- [ ] Community launch announcements drafted
- [ ] Press/influencer keys prepared for distribution
- [ ] Support team briefed on known issues and FAQ
- [ ] Rollback plan documented (if critical issues found post-launch)

### Go / No-Go: [READY / NOT ASSESSED / NOT READY]

First match wins: **NOT READY** if any blocking item fails; else **NOT ASSESSED**
if any section or item came out `NOT ASSESSED` (name each one); else **READY**. NOT
ASSESSED outranks READY — an unassessed section is not a passed one — and ranks
below NOT READY, so a known blocker is never buried behind it.

**Rationale:**
[Summary of readiness assessment. List any blocking items that must be
resolved before launch. If NOT READY, list the specific items that need
resolution and estimated time to address them.]

**Sign-offs Required:**
- [ ] QA Lead
- [ ] Technical Director
- [ ] Producer
- [ ] Creative Director
```

---

## Phase 5: Save Checklist

把檢查清單呈現給使用者，附上：檢查項目總數、已知阻擋項目數量（FIXME/HACK 數量、已知 bug）。

詢問："May I write this to `production/releases/release-checklist-[version].md`?"

如果使用者同意，就寫檔，目錄不存在的話先建立。

---

## Phase 6: Next Steps

- 如果還沒做，先起草 changelog 或 patch notes（`/changelog`、`/patch-notes`），發布關卡會檢查它們。
- 跑 `/gate-check release`，Polish → Release 關卡會讀這份檢查清單。
- 通過之後：跑 `/launch-checklist`，然後用 `/team-release` 協調發布。
