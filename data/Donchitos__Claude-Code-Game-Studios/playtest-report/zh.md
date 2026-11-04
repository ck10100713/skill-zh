---
name: playtest-report
description: "結構化的 playtest 報告範本，或把既有的 playtest 筆記整理成結構化的回饋。"
argument-hint: "[new|analyze path-to-notes] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/playtest-report/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation`

上面已經解析好了，直接用；`--review` 在這次執行會覆蓋 `review_mode`。沒有
這個區塊的話，用 `.claude/docs/config-resolution.md` 裡的預設值。

# Playtest Report



## Phase 1: Parse Arguments


完整的檢查模式見 `.claude/docs/director-gates.md`。各個 gate 的定義放在 `.claude/docs/director-gates/[gate-id].md` — 被派出的 agent 會自己讀它的 gate 檔；不要在父 session 裡讀。


每一次 `AskUserQuestion` 呼叫都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

判斷模式：

- `new` → 產生空白的 playtest 報告範本。這個模式在
  Phase 2A 之後結束：空白範本沒有東西可以路由、審查或儲存。
- `analyze [path]` → 讀原始筆記，並用結構化的發現填進範本
- 沒有參數 → 透過 `AskUserQuestion` 問：`[A] New blank template` /
  `[B] Analyze notes — I'll give you the path`

---

## Phase 2A: New Template Mode

產生這份範本，並輸出給使用者：

```markdown
# Playtest Report

## Session Info
- **Date**: [Date]
- **Build**: [Version/Commit]
- **Duration**: [Time played]
- **Tester**: [Name/ID]
- **Platform**: [PC/Console/Mobile]
- **Input Method**: [KB+M / Gamepad / Touch]
- **Session Type**: [First time / Returning / Targeted test]

## Test Focus
[What specific features or flows were being tested]

## First Impressions (First 5 minutes)
- **Understood the goal?** [Yes/No/Partially]
- **Understood the controls?** [Yes/No/Partially]
- **Emotional response**: [Engaged/Confused/Bored/Frustrated/Excited]
- **Notes**: [Observations]

## Gameplay Flow
### What worked well
- [Observation 1]

### Pain points
- [Issue 1 -- Severity: High/Medium/Low]

### Confusion points
- [Where the player was confused and why]

### Moments of delight
- [What surprised or pleased the player]

## Bugs Encountered
| # | Description | Severity | Reproducible |
|---|-------------|----------|-------------|

## Feature-Specific Feedback
### [Feature 1]
- **Understood purpose?** [Yes/No]
- **Found engaging?** [Yes/No]
- **Suggestions**: [Tester suggestions]

## Quantitative Data (if available)
- **Deaths**: [Count and locations]
- **Time per area**: [Breakdown]
- **Items used**: [What and when]
- **Features discovered vs missed**: [List]

## Overall Assessment
- **Would play again?** [Yes/No/Maybe]
- **Difficulty**: [Too Easy / Just Right / Too Hard]
- **Pacing**: [Too Slow / Good / Too Fast]
- **Session length preference**: [Shorter / Good / Longer]

## Top 3 Priorities from this session
1. [Most important finding]
2. [Second priority]
3. [Third priority]
```

在 `new` 模式，到這裡就停下來，並給出：Verdict: **COMPLETE** — blank template output; nothing saved.

---

## Phase 2B: Analyze Mode

讀提供路徑上的原始筆記。跟既有的設計文件交叉參照，每份都依章節讀：用 Grep 工具（pattern `^#`，content mode）找出你需要的標題，再用 offset 和 limit 讀那幾段範圍。把結構化的發現填進上面的範本。標出任何跟設計意圖衝突的 playtest 觀察。

描述缺陷的觀察 — 當機、framerate 下降、softlock，
明顯是壞掉而不是玩起來不好的東西 — 要放進 **Bugs
Encountered** 表格，不是放在 Gameplay Flow → Pain points 底下，而且在 Phase 3 要當成
bug 來路由。Pain points 是給「玩起來的感覺」用的。

---

## Phase 3: Action Routing

把所有發現分成四個桶：

- **Design changes needed** — 好不好玩的問題、玩家困惑、壞掉的機制、跟 GDD 預期體驗衝突的觀察
- **Balance adjustments** — 數字感覺不對、難度起伏太大或太平
- **Bug reports** — 明確、可重現的實作缺陷
- **Polish items** — 不擋進度，但是之後要處理的摩擦或手感問題

呈現分類好的清單，然後路由：

- **Design changes：**「Run `/propagate-design-change [path]` on the affected design document to find downstream impacts before making changes.」
- **Balance adjustments：**「Run `/balance-check [system]` to verify the full balance picture before tuning values.」
- **Bugs：**「Use `/bug-report` to formally track these.」
- **Polish items：**「Add to the polish backlog in `production/` when the team reaches that phase.」

---

## Phase 3b: Creative Director Player Experience Review

**Review mode 檢查** — 在派出 CD-PLAYTEST 之前套用：
- `solo` → 跳過。註明：「CD-PLAYTEST skipped — Solo mode.」進入 Phase 4（儲存報告）。
- `lean` → 跳過（它不是 PHASE-GATE）。註明：「CD-PLAYTEST skipped — Lean mode.」進入 Phase 4（儲存報告）。
- `full` → 照常派出。

分類完發現之後，用 `Agent` 派出 `creative-director`，使用 gate **CD-PLAYTEST**（`.claude/docs/director-gates/cd-playtest.md`）。

傳入：結構化的報告內容、遊戲 pillar 和核心幻想（來自
`design/gdd/game-concept.md`）、正在驗證的具體假設。**如果
`game-concept.md` 不存在** — 在 `minimal` 是預期中的，因為
`design/game-brief.md` 取代了它 — brief 沒有 pillar：改傳它的
一句話 pitch 和「Who it's for / what they feel」那行，並說明
它們是用來代替 pillar 的。如果兩份文件都不存在，就在 prompt 裡講出來：
*「No pillars available — assess against the hypothesis alone.」* 對 pillar 保持沉默的 director gate，
會自己發明 pillar。

在儲存報告之前，先呈現 creative director 的評估。如果是 CONCERNS 或 REJECT，就在報告裡加一個 `## Creative Director Assessment` 章節，記下判定和回饋。如果是 APPROVE，就在報告裡註明核准。如果是 NOT ASSESSED（director 缺少某個輸入 — `.claude/docs/director-gates.md`），就加同樣的章節並點名缺了什麼；它不是核准。

---

## Phase 4: Save Report

問：「May I write this playtest report to `production/qa/playtests/playtest-[date]-[tester].md`?」

使用者答應就寫檔，目錄不存在的話先建立。

---

## Phase 5: Next Steps

Verdict: **COMPLETE** — playtest report generated.

- 先處理最高優先順序的發現類別。
- 處理完設計變更之後：對更新過的 GDD 重跑 `/design-review`。
- 修完 bug 之後：重跑 `/bug-triage` 來更新優先順序。
