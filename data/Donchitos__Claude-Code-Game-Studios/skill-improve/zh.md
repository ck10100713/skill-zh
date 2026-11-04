---
name: skill-improve
description: "用測試、修正、重測的循環改善 skill：靜態檢查、針對性修正，分數有進步就保留、沒進步就還原。"
argument-hint: "[skill-name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/skill-improve/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

**自動化模式**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次寫檔，都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
屬於 `automation_always_ask` 的類別一律要詢問）。

# Skill Improve

對單一個 skill 跑改善循環：
測試 → 修正 → 重測 → 保留或還原。

它的分數來自 `/skill-test` 的靜態與類別檢查，這些檢查是去讀
skill 而不是去執行它：分數變高代表 skill 寫得比較好，不是
證明它的行為比較好。要檢查行為，要在修改前後，各拿一個真實的需求去跑這個 skill。

---

## Phase 1: Parse Argument

從第一個參數讀 skill 名稱。如果沒有，輸出用法然後停下來：

```
Usage: /skill-improve [skill-name]
Example: /skill-improve tech-debt
```

確認 `.claude/skills/[name]/SKILL.md` 存在。如果不存在，就停下來並說：
"Skill '[name]' not found."

Glob `CCGS Skill Testing Framework/catalog.yaml`。如果它存在，先說：
"`CCGS Skill Testing Framework/` was renamed `studio-tests/` in 1.2.0, and this
skill reads only `studio-tests/`. Move any specs you wrote there; UPGRADING.md
(v1.1.3 → v1.2.0, `studio-tests/`) says how." 然後繼續。

---

## Phase 2: Baseline Test

跑 `/skill-test static [name]` 並記錄基準分數：
- FAIL 的數量
- WARN 的數量
- 哪些具體的檢查失敗（Check 1–7）

顯示給使用者：
```
Static baseline:   [N] failures, [M] warnings
Failing: Check 4 (no ask-before-write), Check 5 (no handoff)
```

如果靜態結果是 **NOT ASSESSED**（skill 檔案讀不到或無法解析），
就停下來並回報它和它的原因：沒有分數可以改善，
而一份沒人讀得了的檔案得到 0 個 FAIL，不是乾淨的結果。

如果基準是 0 個 FAIL 和 0 個 WARN，記下來，然後進 Phase 2b。

### Phase 2b: Category Baseline

在 `studio-tests/catalog.yaml` 裡查這個 skill 的 `category:` 欄位。

如果找不到 `category:` 欄位，顯示：
"Category: not yet assigned — skipping category checks."
然後跳到 Phase 3。

如果找到類別，跑 `/skill-test category [name]` 並記錄類別基準：
- FAIL 的數量
- WARN 的數量
- 哪些具體的類別評分標準指標失敗

顯示給使用者：
```
Category baseline: [N] failures, [M] warnings  ([category] rubric)
```

類別結果如果是 **NOT ASSESSED**（skill-test 找不到或無法套用某個評分標準段落），
要連同原因一起回報，而且它不是零：這時
類別這個維度就從下面的「已經通過」判斷中排除。

如果靜態和類別兩個基準都是 0 個 FAIL 和 0 個 WARN，而且兩者都不是
NOT ASSESSED，就停下來：
"This skill already passes all static and category checks. No improvements needed."

---

## Phase 3: Diagnose

讀完整個 skill：`.claude/skills/[name]/SKILL.md`，以及它 `references/` 資料夾裡的每個檔案
（如果有的話）：最長的 skill 會把每個階段放在那裡。要點名
每個缺口在哪個檔案。

對每個失敗或警告的**靜態**檢查，找出確切的缺口：

- **Check 1 fail** → 缺少哪個 frontmatter 欄位
- **Check 2 fail** → 找到幾個 phase，對比最低要求
- **Check 3 fail** → skill 內文裡完全沒有結論關鍵字
- **Check 4 fail** → allowed-tools 有 Write 或 Edit，卻沒有寫入前先詢問的用語
- **Check 5 warn** → 結尾沒有後續或下一步的段落
- **Check 6 warn** → 設了 `context: fork`，但找到的 phase 少於 5 個
- **Check 7 warn** → argument-hint 是空的，或跟文件裡寫的模式不符

對每個失敗或警告的**類別**檢查（如果在 Phase 2b 已指派類別），
找出 skill 文字裡確切的缺口。例如：
- 如果 G2 失敗（gate 模式，director 面板寬度）：skill 內文沒有依 `modes.workflow`
  來決定 PHASE-GATE 面板的大小（`minimal` 時是 PR，`standard` 時是 TD + PR，
  `full` 時是全部 4 個）
- 如果 A2 失敗（authoring，沒有逐段的 May-I-write）：skill 只在最後問一次，而不是
  在每一段寫入前問
- 如果 T3 失敗（team，BLOCKED 沒有被提出）：skill 沒有因為被 blocked 的 agent 而停下依賴它的工作

在提出任何修改之前，先把合併後的完整診斷顯示給使用者。

---

## Phase 4: Propose Fix

針對每個失敗和警告寫一個有針對性的修正。把提議的修改
用標示清楚的修改前/修改後區塊顯示。只改有問題的地方，不要
重寫已經通過的段落。在有 `references/` 資料夾的 skill 裡，
對某個階段步驟的修正要放在那個階段的 `references/` 檔案，不要放回
`SKILL.md`；下面的詢問就要點名這次修正改動的每一個檔案。

詢問："May I write this improved version to `.claude/skills/[name]/SKILL.md`?"

如果使用者說不要，就在這裡停下來。

---

## Phase 5: Write and Retest

記錄這次修正要改動的每個檔案目前的內容（確切的文字，保留在
這段對話裡），讓 Phase 6 可以還原。

把改善後的 skill 寫入 `.claude/skills/[name]/SKILL.md`，以及
這次修正改動的每個 `references/` 檔案。

重跑 `/skill-test static [name]` 並記錄新的靜態分數：要以那次執行量到的為準，絕對不要憑編輯的內容自己宣稱。
如果有指派類別，也重跑 `/skill-test category [name]` 並記錄新的類別分數。

顯示比較：
```
Static:   Before [N] failures, [M] warnings  →  After [N'] failures, [M'] warnings
Category: Before [N] failures, [M] warnings  →  After [N'] failures, [M'] warnings  (if applicable)
Combined: [before] → [after] (improved / no change / worse)
```

`[before]` 和 `[after]` 是 Phase 6 的合併計數：失敗加上警告，
兩個維度都算，例如 `Combined: 3 → 0 (improved)`。

---

## Phase 6: Verdict

計算合併的失敗總數：靜態 FAIL + 類別 FAIL + 靜態 WARN + 類別 WARN。
**重測結果如果是 NOT ASSESSED**（例如編輯弄壞了
frontmatter，導致檔案無法再被解析），不管它的計數是多少，絕對不算改善：
走下面「沒有進步」的分支。

**如果合併分數有進步（合併的失敗計數比基準低）：**
回報："Score improved. Changes kept."
顯示每個維度修了什麼的摘要。

**如果合併分數一樣或更差：**
回報："Combined score did not improve."
顯示改了什麼，以及它為什麼可能沒有幫助。
詢問："May I restore `.claude/skills/[name]/SKILL.md` to the content it had before this run?"
要點名 Phase 5 寫過的每個檔案。
如果同意：用 Write 把 Phase 5 記錄的內容寫回每個檔案；如果不同意，就讓檔案維持寫入後的樣子。絕對不要
`git checkout` 它：那會回到上一個*已 commit* 的版本，並且丟掉
這次執行之前做過、還沒 commit 的任何編輯。

---

## Phase 7: Next Steps

- 跑 `/skill-test static all` 找下一個有失敗的 skill。
- 跑 `/skill-improve [next-name]` 繼續對另一個 skill 跑這個循環。
- 跑 `/skill-test audit` 看整體涵蓋率的進度。
