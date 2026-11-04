---
name: onboard
description: "替新的貢獻者或 agent 產生 onboarding 文件：專案現況、慣例，以及跟指定角色相關的優先事項。"
argument-hint: "[role|area]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/onboard/../../hooks/yaml-helper.sh" resolve_config *)
model: haiku
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次檔案寫入，都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

# Onboard

## Insufficient input — check this before producing any report

**如果這個 skill 需要的輸入不存在，答案就是「跑不起來」，
不是一份填好的報告。** 先檢查，檢查沒過就停下來。

1. 列出這個 skill 會讀的輸入（資料檔、先前的報告、profiler 輸出、
   測試結果、registry、原始碼）。
2. 對每一項，記錄 `FOUND` 或 `ABSENT` — 不是「假設存在」。
3. 如果某個章節需要的任何輸入是 ABSENT，那個章節就是
   **`NOT ASSESSED — NO DATA`**。不要估算它、不要從
   相鄰的產出物去推斷它，也不要把一個強制要填的格子留給
   下一個讀範本的人去填。
4. 如果**每一個**必要的輸入都是 ABSENT，就停下來，並把
   **`NOT ASSESSED — NO DATA`** 當成整份判定回報，點名缺了什麼，
   以及哪個 skill 會產生它。

**`NOT ASSESSED` 的判定是一種成功。** 當沒有資料時，它就是對
「資料怎麼說？」正確又有用的答案。這條規定要防的失誤很具體：
判定列舉裡沒有「跑不起來」狀態的報告，會產生
**假的乾淨通過** — 在沒有資產也沒有標準的專案上，資產稽核回傳 COMPLIANT；
或者效能分析在零 profiler 資料、也從來沒設過預算的情況下，回報「>99% headroom against
a 16.67ms budget」。

**沒有證據，不等於證據不存在。** 因為沒有檔案可掃，所以沒找到任何
符合項目的掃描，什麼都沒驗證。要說清楚到底是這兩者中的哪一個 — 讀的人
光看綠色結果是分辨不出來的。

---

## Phase 1: Load Project Context

讀 CLAUDE.md 取得專案概覽和標準。

如果有指定特定角色，就從 `.claude/agents/` 讀對應的 agent 定義。

`CLAUDE.md` 和 `.claude/agents/` 是框架內附的 — 沒有任何 skill 會建立它們。如果其中一個不見了，就回報它在安裝時就缺了。

---

## Phase 2: Scan Relevant Area

- 給 programmer：掃描 code root（依 `.claude/docs/code-root-resolution.md` 解析），找架構、模式、關鍵檔案。root 解析不出來，代表掃描沒有執行：它所餵給的章節要寫 `NOT ASSESSED — code root unresolved`，絕對不要猜是 `src/`
- 給 designer：掃描 `design/`，找既有的設計文件
- 給敘事：掃描 `design/narrative/`，找世界觀和故事文件
- 給 QA：掃描 `tests/`，找既有的測試覆蓋（`/test-setup` 會建立它）
- 給 production：掃描 `production/`，找目前的 sprint 和 milestone
- **沒有給角色或區域**：做一般性的導覽 — 列出 `design/`、
  `docs/architecture/`、`production/` 和 code root 的頂層，如果
  `production/session-state/active.md` 存在就讀它，並說明
  給個角色可以讓下一輪更聚焦（例如 `/onboard programmer`）

讀最近的變更（有 git 的話用 git log），了解目前的動能。

---

## Phase 3: Generate Onboarding Document

```markdown
# Onboarding: [Role/Area]

## Project Summary
[2-3 sentence summary of what this game is and its current state]

## Your Role
[What this role does on this project, key responsibilities, who you report to]

## Project Architecture
[Relevant architectural overview for this role]

### Key Directories
| Directory | Contents | Your Interaction |
|-----------|----------|-----------------|

### Key Files
| File | Purpose | Read Priority |
|------|---------|--------------|

## Current Standards and Conventions
[Summary of conventions relevant to this role from CLAUDE.md and agent definition]

## Current State of Your Area
[What has been built, what is in progress, what is planned next. Name what
Phase 2 found by path — for a designer, each existing GDD and design doc — or
say it found none]

## Current Sprint Context
[What the team is working on now and what is expected of this role]

## Key Dependencies
[What other roles/systems this role interacts with most]

## Common Pitfalls
[Things that trip up new contributors in this area]

## First Tasks
[Suggested first tasks to get oriented and productive]

1. [Read these documents first]
2. [Review this code/content]
3. [Start with this small task]

## Questions to Ask
[Questions the new contributor should ask to get fully oriented]
```

---

## Phase 4: Save Document

把 onboarding 文件呈現給使用者。

問：「May I write this to `production/onboarding/onboard-[role]-[date].md`?」

使用者答應就寫檔，目錄不存在的話先建立。

---

## Phase 5: Next Steps

Verdict: **COMPLETE** — onboarding document generated.

- 在新貢獻者的第一個 session 之前，把 onboarding 文件分享給他。
- 執行 `/sprint-status`，讓新貢獻者看到目前的進度。
- 如果貢獻者需要指引，不知道接下來該做什麼，就執行 `/help`。
