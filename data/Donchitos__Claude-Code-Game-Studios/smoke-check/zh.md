---
name: smoke-check
description: "交給 QA 之前的關鍵路徑 smoke 關卡：執行自動化測試套件。檢查沒過就代表這個 build 還沒準備好給 QA。"
argument-hint: "[sprint | quick | --platform pc|console|mobile|all]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(bash "*/.claude/skills/smoke-check/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/project-coherence.sh*), Bash(command -v *), Bash(uname -s), Bash(godot --headless --path . --import), Bash(timeout 900 godot --headless *), Bash(timeout 1800 godot --headless *), Bash(grep -q 'com.unity.test-framework' Packages/manifest.json), Bash(echo present), Bash(echo ABSENT)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,qa.level,testing.strict`

# Smoke Check

這個 skill 是介於「實作完成」和「準備好交給 QA」之間的關卡。它會執行自動化測試
套件、檢查測試涵蓋的缺口、跟開發者批次驗證
關鍵路徑，並產出 PASS/FAIL 報告。

規則很簡單：**沒通過 smoke check 的 build，不准交給 QA。**
把壞掉的 build 交給 QA，只是浪費他們的時間，也打擊團隊士氣。

**輸出：** `production/qa/smoke-[date].md`

---

每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
屬於 `automation_always_ask` 的類別一律要詢問）。

**`qa.level`**：在 `minimal` 時，smoke-check 是**選用的**：如果
有跑，FAIL 只是建議，絕對不會擋住交接，而且沒有遊戲測試的專案，只靠它的 build、啟動和關鍵路徑來檢查（Phase 1 步驟 1）；在 `standard` 時，在階段轉換
之前是必要的；在 `full` 時，每次 commit 之前都要。這放在
Phase 6 `testing.strict.config` 解析的前面（那個只有在 smoke 執行
成為關卡之後才有意義）。跟 `workflow` 是不同的軸。

## Parse Arguments

參數可以組合：`/smoke-check sprint --platform console`

**基本模式**（第一個參數，預設：`sprint`）：
- `sprint`：針對目前 sprint 的 story 做完整的 smoke check
- `quick`：跳過涵蓋掃描（Phase 3）和 Batch 3；用在快速重新檢查

**平台旗標**（`--platform`，預設：無）：
- `--platform pc`：加入 PC 專屬的檢查（鍵盤、滑鼠、視窗模式）
- `--platform console`：加入主機專屬的檢查（手把、電視安全區、
  平台認證要求）
- `--platform mobile`：加入手機專屬的檢查（觸控、直式/橫式、
  電池/散熱行為）
- `--platform all`：加入所有平台的變體；輸出每個平台的結論表

如果有提供 `--platform`，Phase 4 會加入平台專屬的批次，
而 Phase 5 除了整體結論之外，還會輸出每個平台的結論表。

---

## Phase 1: Detect Test Setup

**現在讀 `references/1-detect-setup.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 2: Run Automated Tests

**現在讀 `references/2-run-tests.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 3: Check Test Coverage

**現在讀 `references/3-coverage.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 4: Run Manual Smoke Checks

**現在讀 `references/4-manual-checks.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 5: Generate Report

**現在讀 `references/5-report.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 6: Write and Gate

**現在讀 `references/6-write-gate.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Collaborative Protocol

**適用於 `collaborative` 模式（預設）。** `guided` 和
`autonomous` 模式請看 `.claude/docs/automation-modes.md`：下面的規則
描述的是 collaborative 模式的要求，不是通用的行為。

- **絕對不要把 NOT RUN 自動當成 FAIL**：把它記錄成 NOT RUN，讓
  開發者手動確認狀態。沒有確認的 NOT RUN 得到的是 **NOT
  ASSESSED**，不是 FAIL，也不是通過的結論。
- **絕對不要自動修正失敗**：回報它們，並說明必須解決什麼。
  不要嘗試編輯原始碼或測試檔案。
- **PASS WITH WARNINGS 不會擋住交給 QA**：它會為
  `/story-done` 記錄要追蹤的建議性缺口。
- **`quick` 參數**會跳過 Phase 3（涵蓋掃描）和 Phase 4 的 Batch 3。
  用在修好某個特定失敗之後的快速重新檢查。
- 所有手動 smoke check 的驗證都用 `AskUserQuestion`。
- **沒問過就絕對不要寫報告**：Phase 6 在建立任何檔案之前，
  都需要明確的核准。
