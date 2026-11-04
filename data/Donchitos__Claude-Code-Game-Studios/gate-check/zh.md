---
name: gate-check
description: "準備好從一個開發階段進到下一個了嗎？給出 PASS/CONCERNS/NOT ASSESSED/FAIL 的判定，附上阻礙項目和必備產出物。「我們可以進 production 了嗎？」"
argument-hint: "[target-phase: systems-design | technical-setup | pre-production | production | polish | release] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/gate-check/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/artifact-check.sh *), Bash(bash .claude/scripts/gdd-structure-check.sh*), Bash(bash .claude/scripts/adr-dep-graph.sh*), Bash(bash .claude/scripts/set-stage.sh *)
model: opus
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,workflow,qa.level,testing.strict,performance.enforce,team.size,project.stage,system_overrides`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，
用 `.claude/docs/config-resolution.md` 裡的預設值。

# Phase Gate Validation

這個 skill 負責驗證專案是否準備好進入下一個開發階段。它會檢查必備產出物、品質標準和阻礙項目。

**跟 `/project-stage-detect` 不一樣**：那個 skill 是診斷性的（「我們現在在哪？」）。
這個 skill 是規範性的（「我們準備好前進了嗎？」，並給出正式的判定）。

## Production Stages (7)

專案會依序走過這些階段：

1. **Concept** — 腦力激盪、遊戲概念文件
2. **Systems Design** — 梳理各系統、撰寫 GDD
3. **Technical Setup** — 引擎設定、架構決策
4. **Pre-Production** — 做原型、驗證 vertical slice
5. **Production** — 功能開發（Epic/Feature/Task 追蹤啟動）
6. **Polish** — 效能、playtest、修 bug
7. **Release** — 上線準備、認證

**當 gate 通過時**（或使用者明確接受 CONCERNS 判定的風險 — Section 6），要同時更新 `project.yaml` 裡的 stage（設定 `project.stage: <new-stage>`），也要把新的 stage 名稱寫進 `production/stage.txt`（單獨一行，例如 `Production`）。雙寫是為了向後相容還沒遷移的 hook。這樣狀態列會立刻更新。

---

## 1. Parse Arguments

**目標階段：** `$ARGUMENTS` 去掉任何 `--review <mode>` 這組之後剩下的部分（留白 = 自動偵測目前階段，再驗證下一個轉換）。`/gate-check --review full` 沒有指定任何階段。

注意：在 `solo` 模式下，director 的派生（CD-PHASE-GATE、TD-PHASE-GATE、PR-PHASE-GATE、AD-PHASE-GATE）都會跳過 — gate-check 變成只檢查產出物存不存在。在 `lean` 模式下，phase-gate 的 director 還是會跑（phase gate 正是 lean 模式的用途）；跑幾個，由下面的 `workflow` 決定。

**`workflow`**（依 `.claude/docs/workflow-modes.md`）：

`gate-check` 是整個專案範圍的，所以 gate 整體的產出物清單（載入的 gate 檔）用專案層級的 `workflow`，
**而且**在驗證 MVP GDD 時，會逐個 system 去查
`workflow_overrides.system_overrides.<system>` — 被釘在較高 tier 的 system，
在 gate 通過之前一定要達到那個 tier 的章節數，不管專案層級的 workflow 是什麼（見 Section 2b，
「Per-system overrides」）。

> **gate-check 遵守 `workflow`，但不受 `automation` 約束。** 產出物
> 清單會依 tier 改變；協作式的提問協定（Collaborative
> Protocol 那一節）一律適用 — phase gate 是刻意設計的人工檢查點，絕對不會自動執行。

**`qa.level`**：控制 phase gate 上的測試強制程度，而 `workflow`
控制需要哪些產出物。`modes.rigor` 會兩個一起設；想只調整強制程度，就明確設定
`qa.level`。在 `minimal`，不套用任何測試 gate — 測試證據和單元測試產出物項目變成非必備，
Section 3 的 `testing.strict` 檢查是 no-op；smoke check 不會放寬（Section 2b）—
不過在這個等級 `/smoke-check` 是不跑遊戲測試的（它的自動化那一列會顯示
WAIVED），所以 build 檢查（有設的話是 `commands.smoke`，否則 `commands.build`）加上
啟動和關鍵路徑檢查就是底線 — 沒人啟動過的 build 就是
NOT ASSESSED — 而沒有測試的專案還是可以通過。在 `standard`，
Logic + Integration 測試必須通過。在 `full`，需要完整的覆蓋率檢查 + regression suite
（覆蓋率下限取 `qa.coverage_minimum`，如果有設的話）。UI 和 Visual/Feel
story 需要保留的截圖不算測試項目：沒有任何 `qa.level` 能放寬它們
（Section 2b）。

**`team.size`**：不會改變 phase gate 派出幾個 director — 小組的寬度
是 `workflow` 這條軸的事（Section 4b）。這個值只影響每個 director 審查裡的
**specialist 深度**。
`individual` 用核心 specialist 組；`small` 用標準組；`studio`
再加上 engine 子 specialist。它絕對不會跳過 director — 跳過 director 是
`review_mode` 的工作。`review_mode` 和 `team.size` 都是由
`modes.rigor` 設定 — 選一個 rigor 就兩個一起設 — 兩者在明確設定時
各自仍會覆蓋那條軸（full-rigor 的專案拿到 `studio` 組；較輕的 tier
拿到 `individual`）。

- **有帶參數**：`/gate-check production` — 驗證是否準備好進入那個特定階段
- **沒帶參數**：用跟
  `/project-stage-detect` 同樣的啟發式自動偵測目前階段，然後**執行前先跟使用者確認**：

  使用 `AskUserQuestion`：
  - Prompt: "Detected stage: **[current stage]**. Running gate for [Current] → [Next] transition. Is this correct?"
  - Options:
    - `[A] Yes — run this gate`
    - `[B] No — pick a different gate`（如果選這個，就顯示第二個選單，列出所有 gate 選項：Concept → Systems Design、Systems Design → Technical Setup、Technical Setup → Pre-Production、Pre-Production → Production、Production → Polish、Polish → Release）
  
  沒帶參數時，不准跳過這個確認步驟。

---

## 2. Phase Gate Definitions

每個 gate 的清單 — 必備產出物、品質檢查，以及它依 workflow tier 的精簡版 —
都放在各自的檔案裡。**只讀目標階段轉換對應的那一列；絕對不要載入其他的。**

| Gate | Definition file |
|------|-----------------|
| Concept → Systems Design | `references/gate-systems-design.md` |
| Systems Design → Technical Setup | `references/gate-technical-setup.md` |
| Technical Setup → Pre-Production | `references/gate-pre-production.md` |
| Pre-Production → Production | `references/gate-production.md` |
| Production → Polish | `references/gate-polish.md` |
| Polish → Release | `references/gate-release.md` |

每個檔案先寫 `full` 的基準，再寫那個 gate 的 `standard` 和 `minimal`
精簡版。套用 Section 1 解析出來的 tier。

## 2b. Workflow Tier Adjustment

**現在就讀 `references/2b-workflow-tier.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## 3. Run the Gate Check

**現在就讀 `references/3-run-gate-check.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## 4. Collaborative Assessment

**現在就讀 `references/4-assessment.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## 5. Output the Verdict

**現在就讀 `references/5-verdict.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## 6. Update Stage on PASS

**現在就讀 `references/6-update-stage.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## 7. Closing Next-Step Widget

**現在就讀 `references/7-next-steps.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Collaborative Protocol

這個 skill 遵循協作式設計原則：

1. **先掃描**：檢查所有產出物和品質 gate
2. **不確定的就問**：沒辦法驗證的東西，不要假設是 PASS
3. **呈現發現**：秀出完整清單和各項狀態
4. **使用者決定**：判定只是建議 — 接下來怎麼做由使用者做最後決定；
   只有 stage 的寫入會受判定約束（Section 6）
5. **取得核准**：「May I write this gate check report to production/gate-checks/?」
6. **絕對不自動修**：必備產出物缺了，就回報 FAIL 判定，
   並指出要跑哪個 skill（例如「run `/test-setup`」）。不准建立缺少的檔案，也不准
   自動重跑 gate。為了製造 PASS 而建立檔案，等於讓
   gate 失去意義。

**絕對不要**擋住使用者做事 — 判定只決定這個 skill 要不要
寫入新的 stage。CONCERNS 時，使用者可以明確接受所列風險來往前走，
報告會記錄這件事（Section 6）；FAIL 或 NOT ASSESSED 時，
stage 維持原樣，直到重跑通過，期間沒有任何東西會阻止使用者
去處理那些阻礙項目。
