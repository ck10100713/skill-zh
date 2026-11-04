---
name: launch-checklist
description: "橫跨所有部門的上線就緒檢查：程式碼、內容、商店、行銷、社群、基礎設施、法務，以及 go/no-go 簽核。"
argument-hint: "[launch-date or 'dry-run']"
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(bash "*/.claude/skills/launch-checklist/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys rigor,workflow,project.stage,cert_tier,automation`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次檔案寫入，都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

上面已經解析好了，直接用。沒有這個區塊的話，用 `.claude/docs/config-resolution.md` 裡的預設值。

# Launch Checklist

**把這份 checklist 的範圍限縮到這個專案。** 每個平台的每個項目都列出來，
會訓練讀的人跳過整份清單，這就讓 gate 失去意義：

- **`project.stage`** — 專案還沒走到的階段，它的項目不在範圍內；
  要講出來，不要列成未勾選。
- **`modes.rigor`** — 在 `minimal`，把「唯一理由是流程成本」而且這個專案已經選擇不要那種流程的項目拿掉。
- **`platform.cert_tier`** — **只**列出專案目標 tier 的認證項目。如果
  **沒設**，就**問哪些平台在範圍內**，
  不要全部列出 — 沒設的值是一個問題，不是可以
  把所有認證軌道都列出來的許可。把答案對應到下面四個值，
  就是這次執行的 tier。如果判斷不出來，就把這個章節標成
  **`NOT ASSESSED — cert tier unknown`**。**沒設不等於 `none`：** `none` 是
  一個決定，沒設是缺了決定，兩者不能產生相同的輸出。
  要依這個 key 的**四個值**分支 — `none | itch | steam | console` —
  不要依平台名稱。完整的需求表是 `.claude/docs/effects-map.md` 的 `## platform.cert_tier`
  章節 — **只讀那個章節**（用 Grep 找它的標題，再做有範圍的 Read）；整個檔案不是 runtime 的輸入。
  - `none` — **完全不列認證章節。** 內部 release、alpha 或 jam 遊戲。
    要說這個章節被省略了以及原因；不要留空白。
  - `itch` — 只列 itch.io 上傳需求：build 大小、頁面設定、年齡標籤。
    **沒有 console，也沒有 Steamworks 的項目。**
  - `steam` — Steamworks：商店頁面、depot build、成就、系統
    需求、通用內容規則。**沒有 console 認證項目。**
  - `console` — 完整的平台認證（TRC / XR / Lotcheck）、存檔資料
    規則、手把按鍵對應規則、年齡分級機構。最重的 tier。

  > **要依上面的 `cert_tier` 值分支，不要依平台名稱。** 用目標平台來判斷，
  > 會把 `itch` 專案和 `steam` 專案一視同仁、把 `none` 和沒設混為一談，
  > 還會用 `mobile` 當 key，而它根本不是 `cert_tier` 的
  > 值。用 config 定義的詞彙。

如果某個項目因為沒有 config 而無法界定範圍，就標成
**`NOT ASSESSED — platform/stage unknown`**。不要默默把它放進去：不然一個
`rigor: standard`、單一平台的專案會拿到大約 150 項的
checklist，要求 PC **和** console **和** mobile 認證加上年齡
分級，其中大約 140 項根本無法評估。

---


## Phase 1: Parse Arguments

讀參數取得上線日期或 `dry-run` 模式。Dry-run 模式會產生 checklist，但不建立簽核項目，也不寫檔。沒有參數時就是一般執行，目標日期不設定（`Target Launch: not set`）— 只有參數寫 `dry-run` 時才是 dry-run。

---

## Phase 2: Gather Project Context

- 讀 `CLAUDE.md` 取得技術堆疊、目標平台和團隊結構
- 讀 `production/milestones/` 裡最新的 milestone
- 讀 `production/releases/` 裡任何既有的 release checklist
- 如果 `design/live-ops/content-calendar.md` 的內容行事曆存在，就讀它

---

## Phase 3: Scan Codebase Health

> **這個階段的每個掃描都是在找壞東西，所以零命中的結果
> 在結構上就是模糊的：它可能代表「搜過了，沒找到」，也可能代表
> 「根本沒東西可搜」。在上線 gate 上，這是兩個相反的發現，
> 而綠色勾選框會把它們呈現得一模一樣。**
>
> **在下面每個掃描之前，先確立分母，並且回報。** 每一行
> 要嘛寫 `scanned [N] files, [M] hits`，要嘛寫
> `NOT ASSESSED — [code root unresolved | no source files | no asset folder | directory empty]`。
> 絕對不准只畫一個勾。code root 依 engine 而定，是 `src/`、`Assets/` 或 `Source/`
> （依 `.claude/docs/code-root-resolution.md` 解析）；資產放在
> `assets/`、`Assets/` 或 `Content/`。
>
> 下面四個項目都適用這點：每個都用同樣的方式搜尋，找
> placeholder 資產、TODO、debug 輸出和寫死的測試值，而且在空的或
> 不存在的 root 上都會回傳零命中。舉例來說，沒有 `assets/` 目錄時，
> placeholder 掃描會回傳零命中，而只畫勾的話就會讓
> 「All placeholder art replaced」變成綠色。

- 計算 `TODO`、`FIXME`、`HACK` 註解的數量和位置
- 檢查 production 程式碼裡有沒有留下 `console.log`、`print()` 或 debug 輸出
- 檢查 placeholder 資產（搜尋 `placeholder`、`temp_`、`WIP_`）
- 檢查寫死的測試/開發值（localhost、測試憑證、debug 旗標）

**把這個區別帶進 checklist 本身。** 掃描結果是 `NOT ASSESSED` 的項目，寫成 `- [?]`，
不是 `- [ ]`。沒勾的框代表*還有工作要做*；`[?]` 代表*沒人能檢查*，
而兩者之中只有一種能靠做完工作來關閉。凡是出現 `[?]` 的地方都要附上圖例：
`[?] = not assessed — the input to this check was absent`。

---

## Phase 4: Generate the Launch Checklist

```markdown
# Launch Checklist: [Game Title]
Target Launch: [Date or DRY RUN]
Generated: [Date]

---

## 1. Code Readiness

### Build Health
- [ ] Clean build on all target platforms
- [ ] Zero compiler warnings
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Performance benchmarks within targets
- [ ] No memory leaks (verified via extended soak test)
- [ ] Build size within platform limits
- [ ] Build version correctly set and tagged in source control

### Code Quality
- [ ] TODO count: [N] (zero required for launch, or documented exceptions)
- [ ] FIXME count: [N] (zero required)
- [ ] HACK count: [N] (each must have documented justification)
- [ ] No debug output in production code
- [ ] No hardcoded dev/test values
- [ ] All feature flags set to production values
- [ ] Error handling covers all critical paths
- [ ] Crash reporting integrated and verified

### Security
- [ ] No exposed API keys or credentials in source
- [ ] Save data encrypted
- [ ] Network communication secured (TLS/DTLS)
- [ ] Anti-cheat measures active (if multiplayer)
- [ ] Input validation on all server endpoints (if multiplayer)
- [ ] Privacy policy compliance verified

---

## 2. Content Readiness

### Assets
- [ ] All placeholder art replaced with final assets
- [ ] All placeholder audio replaced with final audio
- [ ] Audio mix finalized and approved by audio director
- [ ] All VFX polished and performance-verified
- [ ] No missing or broken asset references
- [ ] Asset naming conventions enforced

### Text and Localization
- [ ] All player-facing text proofread
- [ ] No hardcoded strings (all externalized for localization)
- [ ] All supported languages translated and verified
- [ ] Text fits UI in all languages (text fitting pass complete)
- [ ] Font coverage verified for all supported languages
- [ ] Credits complete, accurate, and up to date

### Game Content
- [ ] All levels/maps playable from start to finish
- [ ] Tutorial flow complete and tested with new players
- [ ] All achievements/trophies implemented and tested
- [ ] Save/load works correctly for all game states
- [ ] Difficulty settings balanced and tested
- [ ] End-game/credits sequence complete

---

## 3. Quality Assurance

### Testing
- [ ] Full regression test suite passed
- [ ] Zero S1 (Critical) bugs open
- [ ] Zero S2 (High) bugs open (or documented exceptions) — at `workflow: full` instead: zero S2 (High) and S3 (Medium) bugs open, no exceptions
- [ ] Soak test passed (the longest soak `/soak-test` runs, or longer by hand if a play session lasts longer)
- [ ] Multiplayer stress test passed (if applicable)
- [ ] All critical user paths tested on every platform
- [ ] Edge cases tested (full storage, no network, suspend/resume)

### Platform Certification

**Emit ONLY the block matching `platform.cert_tier`** (resolved in the resolved-config block at the top of this skill — see
the `platform.cert_tier` rule above). Do not emit this section's other blocks, and
do not fall back to emitting all of them.

**At `none`** — omit the section and say so in one line:
`Platform Certification: omitted — cert_tier is 'none' (internal/jam release).`

**At `itch`:**
- [ ] Build size within itch.io upload limits
- [ ] itch.io page complete (cover art, screenshots, description, tags)
- [ ] Age/content tags set honestly
- [ ] Downloadable vs browser build decided and tested

**At `steam`:**
- [ ] Steamworks SDK integrated and tested
- [ ] Store page complete (capsule art, trailer, description, system requirements)
- [ ] Depot build uploaded and installs cleanly from a fresh account
- [ ] Achievements functional
- [ ] Steam common content rules reviewed

**At `console`:**
- [ ] TRC/TCR/Lotcheck submission prepared
- [ ] Save-data rules compliant (corruption, full storage, user switching)
- [ ] Controller-mapping rules met, platform-correct button prompts
- [ ] Suspend/resume verified
- [ ] Age ratings obtained (ESRB, PEGI, regional)

**Every tier**, because these are not certification-gated:
- [ ] Accessibility: minimum standards met (remapping, text scaling, colorblind)

> **Emit this section gated by tier, never as one ungated list.** PC *and*
> Console *and* Mobile rows emitted at every tier contradict the `cert_tier` rule
> at the top of this skill, which says an `itch` project gets no console and no
> Steamworks items.

### Performance
- [ ] Target FPS met on minimum spec hardware
- [ ] Load times within budget on all platforms
- [ ] Memory usage within budget on all platforms
- [ ] Network bandwidth within targets (if multiplayer)
- [ ] No frame hitches in critical gameplay moments

---

## 4. Store and Distribution

### Store Pages
- [ ] Store page copy finalized and proofread
- [ ] Screenshots current and per-platform resolution
- [ ] Trailers current and approved
- [ ] Key art and capsule images finalized
- [ ] System requirements accurate (PC)
- [ ] Pricing configured for all regions
- [ ] Pre-purchase/wishlist campaigns active (if applicable)

### Legal
- [ ] EULA finalized and approved by legal
- [ ] Privacy policy published and linked
- [ ] Third-party license attributions complete
- [ ] Music/audio licensing verified
- [ ] Trademark/IP clearance confirmed
- [ ] GDPR/CCPA compliance verified (data collection, consent, deletion)

---

## 5. Infrastructure

### Servers (if multiplayer/online)
- [ ] Production servers provisioned and load-tested
- [ ] Auto-scaling configured and tested
- [ ] Database backups configured
- [ ] CDN configured for content delivery
- [ ] DDoS protection active
- [ ] Monitoring and alerting configured

### Analytics and Monitoring
- [ ] Analytics pipeline verified and receiving data
- [ ] Crash reporting active and dashboard accessible
- [ ] Server monitoring dashboards live
- [ ] Key metrics tracked: DAU, session length, retention, crashes
- [ ] Alerts configured for critical thresholds

---

## 6. Community and Marketing

### Community Readiness
- [ ] Community guidelines published
- [ ] Moderation team briefed and tools ready
- [ ] Discord/forum/social channels set up
- [ ] FAQ and known issues page prepared
- [ ] Support email/ticketing system active

### Marketing
- [ ] Launch trailer published
- [ ] Press/influencer review keys distributed
- [ ] Social media launch posts scheduled
- [ ] Launch day blog post/dev update drafted
- [ ] Patch notes for launch version published

---

## 7. Operations

### Team Readiness
- [ ] On-call schedule set for first 72 hours post-launch
- [ ] Incident response playbook reviewed by team
- [ ] Rollback plan documented and tested
- [ ] Hotfix pipeline tested (can ship emergency fix within 4 hours)
- [ ] Communication plan for launch issues (who posts, where, how fast)

### Day-One Plan
- [ ] Day-one patch prepared (if needed)
- [ ] Server unlock/go-live procedure documented
- [ ] Launch monitoring dashboard bookmarked by all leads
- [ ] War room/channel established for launch day

---

## Go / No-Go Decision

**Overall Status**: [READY / CONDITIONAL / NOT ASSESSED / NOT READY]

First match wins: **NOT READY** if Blocking Items is not empty; else **NOT
ASSESSED** if any item is `- [?]`, any section came out `NOT ASSESSED`, or any
item is still unconfirmed — neither ticked on evidence or on a Phase 4b answer,
nor marked N/A, nor listed below (name each; group by section when there are
many); else **CONDITIONAL** if Conditional
Items is not empty; else **READY**. NOT ASSESSED outranks CONDITIONAL and READY —
an item nobody could check is not a passed one — and ranks below NOT READY, so a
known blocker is never buried behind it.

### Blocking Items
[Every FAIL or unresolved finding: a check that found a problem — FIXMEs, debug
output, placeholder assets, hardcoded dev values, an open S1 bug, a failing
build or test — with no documented workaround and no explicitly accepted risk]

### Conditional Items
[Every shortfall with a documented workaround or an explicitly accepted risk —
e.g. a HACK with its documented justification, an S2 with a documented
exception (below `workflow: full`, which allows none). Name the workaround, or
who accepted the risk]

### Sign-Offs Required
- [ ] Creative Director — Content and experience quality
- [ ] Technical Director — Technical health and stability
- [ ] QA Lead — Quality and test coverage
- [ ] Producer — Schedule and overall readiness
- [ ] Release Manager — Build and deployment readiness
```

---

## Phase 4b: Confirm What Only a Person Can

上面大部分項目沒辦法從 repository 判定 — on-call 排班表、
EULA、媒體 key、定價、有人跑過的 soak test。不問的話，每一項
都會維持未確認，Overall Status 就只能是 NOT ASSESSED，所以要問。

對這七個章節各自收集沒有任何掃描或檔案能判定的項目（Phase 3 的計數和
Phase 2 讀到的東西不用再問），**每個章節問一次
`AskUserQuestion`**，把這些項目編號列出來。每個項目的
答案是 **yes / no / not yet / N/A**。Options：`Yes — all of them` /
`Not yet — none of them` / `N/A — this section does not apply` /
`Some differ — I'll answer per item`（使用者接著替每個編號項目各給
答案）。沒有東西可問的章節就跳過。

- **yes** → 勾成 `- [x]`，標註 `(confirmed by the user)`
- **no** 或 **not yet** → 算失敗項目：放在 Blocking Items 底下，
  如果使用者說出 workaround 或接受風險，就放在 Conditional Items 底下
- **N/A** → 寫成 `- N/A — [item]`，並且不計入 Overall Status
- 沒有回答的項目維持未確認，狀態裡要點名它

這些是只有使用者能回答的事實問題，所以 `collaborative` 和 `guided`
都要問，而且絕對不替使用者回答。在 `autonomous` 模式和
`dry-run`，跳過這個階段並說明：它原本會問的項目維持未確認，Overall Status 是 NOT ASSESSED。

然後根據答案填寫 Go / No-Go 章節。

---

## Phase 5: Save Checklist

把完成的 checklist 和摘要呈現給使用者（Overall Status、項目總數、blocking 項目數、conditional 項目數、not-assessed 項目數、有未完成章節的部門）。

如果不是 dry-run 模式，問：「May I write this to `production/releases/launch-checklist-[date].md`?」

使用者回答之前什麼都不要建立 — 連 `production/releases/` 目錄也不要。
如果答應，就寫檔；寫檔時會一併建立目錄。

---

## Phase 6: Next Steps

- 如果 `project.stage` 不是 `Release`（是 `Polish`、更早的階段，或沒設），先跑 `/gate-check release` — 它是上線前的就緒 gate。
- 透過 `/team-release` 協調簽核和 deploy。
