---
name: test-setup
description: "建立測試框架與 CI 的骨架：tests/ 目錄、引擎測試執行器、GitHub Actions workflow。第一個 sprint 之前做一次就好。"
argument-hint: "[force]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(grep -q 'com.unity.test-framework' Packages/manifest.json), Bash(bash "*/.claude/skills/test-setup/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,qa.level`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和每一次檔案寫入，都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律要問 · guided 只問重大的 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 類別的一律要問）。

# Test Setup

這個 skill 為專案建立自動化測試的基礎設施骨架。它會偵測設定好的引擎、產生對應的測試執行器設定、建立標準的目錄結構，並把 CI/CD 接好，讓每次 push 都會跑測試。

在 Technical Setup 階段、任何實作開始之前，跑一次就好。在 sprint 開始時裝好測試框架，要花 30 分鐘。拖到第四個 sprint 才裝，要花 3 個 sprint。

**輸出：** `tests/` 目錄結構 + `.github/workflows/tests.yml`

---

## Phase 1: Detect Engine and Existing State

**現在就讀 `references/1-detect.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

## Phase 2: Present Plan

**現在就讀 `references/2-plan.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

## Phase 3: Create Directory Structure

**現在就讀 `references/3-directories.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

## Phase 4: Create CI/CD Workflow

**現在就讀 `references/4-ci.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

## Phase 5: Create Smoke Test Seed

**現在就讀 `references/5-smoke-seed.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

## Phase 6: Post-Setup Summary

**現在就讀 `references/6-summary.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

## Collaborative Protocol

- **絕對不要覆蓋既有的測試檔案**：只建立缺少的檔案。如果測試執行器的檔案已經存在，就保持原樣。
- **建立檔案之前一定要先問**：Phase 2 需要明確核准。
- **引擎偵測沒得商量**：如果沒有設定引擎，就停下來並導向 `/setup-engine`。不要用猜的。
- **`force` 旗標會跳過「已經存在」的提前結束，但絕對不會覆蓋。** 它的意思是「即使目錄已經存在，也把缺少的檔案建起來」。
- 對 Unity 的 CI，要註明 `UNITY_LICENSE` secret 必須手動設定。不要嘗試把授權管理自動化。
