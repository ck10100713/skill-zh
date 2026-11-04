---
name: skillopt-sleep
description: "當使用者想讓他的 Claude agent 從過去的使用中自我改進、問到夜間/離線的「睡眠」或「做夢」週期、記憶/skill 整合，或說出像是「讓我的 agent 越用越好」、「回顧我過去的 session」、「學習我的偏好」、「整合你學到的東西」、「執行 sleep 週期」，或想排程背景的自我最佳化時使用。驅動 skillopt_sleep 引擎：收集過去的 session -> 挖出重複的任務 -> 透過選定的 backend 重播 -> 在 held-out 關卡後面整合經過驗證的 CLAUDE.md/SKILL.md。"
---

# SkillOpt-Sleep：由使用驅動、讓本機 Claude agent 自我演化

SkillOpt-Sleep 給使用者的 agent 一個**睡眠週期**。依需求或每晚排程，它會回顧真實的 Claude Code 過往 session，把重複出現的任務透過選定的 backend 重新跑一遍，並把學到的東西整合進**記憶**（`CLAUDE.md`）和 **skill**（`SKILL.md`）。啟用預設的驗證關卡時，它只保留能提升 held-out 分數的變更。只有透過明確的採用，或使用者要求的 `--auto-adopt`，線上使用的檔案才會被改動。它的目標是改進這位使用者重複出現的工作，同時讓每個被接受的提案，都能在該次執行的 held-out 任務上量測出來，而且不需要訓練模型權重。它是訓練在部署階段的類比：短期經驗 → 長期能力。

它綜合了三個想法：
- **SkillOpt**：skill/記憶文件是可訓練的文字；有上限的新增/刪除/取代編輯；只透過 held-out 關卡才會被接受；被拒絕的編輯會記錄在執行報告裡供檢視。
- **Claude Dreams**：讀過去的 session，在受保護的學習區塊內提出變更的整合方式；輸入永遠不會被修改，輸出在採用前會先被檢視。
- **Agent sleep**：定期的背景重播，把一段段經歷變成持久的 skill。

## 什麼時候使用這個 skill

當使用者想要下列任何一種時觸發：
- "make my agent learn from how I use it" / "get better the more I use it" / "remember my preferences across sessions"
- 夜間/排程或隨選的**離線自我改進 / dream / sleep** 執行
- **回顧過去的 session/軌跡**，並提煉出重複出現的任務
- 把回饋**整合**進 `CLAUDE.md` 或受管理的 skill
- **排程**這個週期（cron），或**採用**已 staged 的提案

## 週期（六個階段）

1. **Harvest**：讀取 `~/.claude/projects/*/<session>.jsonl` + `~/.claude/history.jsonl`（唯讀）→ session digest。
2. **Mine**：digest → `TaskRecord`（重複出現的意圖 + 結果標籤 + 可能的話附上可檢查的參照）。
3. **Replay**：在*目前*的 skill+記憶下，透過選定的 backend 重新跑任務 → (hard, soft) 分數。
4. **Consolidate**：反思失敗 → 提出有上限的編輯 → 在 held-out 的切片上設**關卡**；啟用預設關卡時，只有嚴格改善才接受。
5. **Stage**：把被接受的 `proposed_CLAUDE.md` 和/或 `proposed_SKILL.md`，加上 `report.md`、`report.json`、`manifest.json` 和 `diagnostics.json`，寫到 `<project>/.skillopt-sleep/staging/<timestamp>/`。**線上使用的東西一律不動。** 被拒絕的執行仍然會有報告，但沒有要取代線上檔案的提案。
6. **Adopt**：明確的（或選擇啟用的自動）：把 staged 的檔案複製覆蓋線上檔案，先備份。

## 怎麼驅動它

優先使用 `/skillopt-sleep` 指令。底層它會呼叫附帶的 runner：

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/sleep.sh" status                       # what's happened
"${CLAUDE_PLUGIN_ROOT}/scripts/sleep.sh" dry-run --project "$(pwd)"    # no-staging preview
"${CLAUDE_PLUGIN_ROOT}/scripts/sleep.sh" run --project "$(pwd)"        # full cycle, stages a proposal
"${CLAUDE_PLUGIN_ROOT}/scripts/sleep.sh" adopt --project "$(pwd)"      # apply staged proposal (with backup)
```

- 預設的 backend 是 `mock`（確定性的，**不花 API 費用**），適合用來試管線。
- 加上 `--backend claude` 或 `--backend codex` 會花使用者真實的預算，做由模型驅動的最佳化。held-out 的進步是該次執行專屬的證據，不是更廣泛改進的保證；結果取決於任務、模型和檢查。
- 範圍預設是被呼叫的專案；`--scope all` 會把每個 Claude 專案都收集到目前這次執行所設定的目標裡。
- 真實的 backend 會把截斷後的 transcript/任務內容送給它的提供者。用在敏感的 session 之前，先看下面的資料界線規則。

### 排程

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/sleep.sh" schedule --project "$(pwd)" --hour 3 --minute 17
"${CLAUDE_PLUGIN_ROOT}/scripts/sleep.sh" unschedule --project "$(pwd)"
```

會安裝一個每晚執行的 cron 項目。`unschedule --all` 會移除所有受管理的項目。

## 常用的 CLI flag

| Flag | 預設 | 說明 |
|------|---------|-------------|
| `--project PATH` | cwd | 要演化的專案目錄 |
| `--scope all\|invoked` | invoked | 收集範圍 |
| `--backend mock\|claude\|codex\|copilot\|handoff\|azure_openai` | mock | Backend（mock = 不呼叫提供者） |
| `--model NAME` | backend 預設 | 覆寫重播所用的模型 |
| `--source claude\|codex\|auto` | claude | Transcript 來源 |
| `--lookback-hours N` | 72 | 收集的時間範圍 |
| `--max-sessions N` | 推算出來 | 收集的 session 上限；預設是 3 × 最大任務數（目前預設是 120） |
| `--max-tasks N` | 40 | 挖出的任務上限 |
| `--target-skill-path PATH` | `~/.claude/skills/skillopt-sleep-learned/SKILL.md` | 明確指定要演化的 SKILL.md |
| `--tasks-file PATH` | — | 已審查過的 TaskRecord JSON（跳過 harvest） |
| `--progress` | off | 把階段進度印到 stderr |
| `--auto-adopt` | off | 關卡通過時自動採用 |
| `--edit-budget N` | 4 | 每晚最多有上限的編輯數 |
| `--preferences TEXT` | 空 | 把家規加到最佳化器的反思先驗 |
| `--json` | off | 機器可讀的 JSON 輸出 |

CLI 還有來源/runtime 路徑的覆寫（`--claude-home`、`--codex-home` 和 `--codex-path`），以及各動作專屬的 flag。以 `python -m skillopt_sleep <action> --help` 為權威的介面。

## 設定 key（`~/.skillopt-sleep/config.json`）

除了 CLI flag 之外，進階行為由設定控制：

- **`preferences`**：注入最佳化器反思步驟的自由文字家規（例如 "Always use async/await"、"Answers in `\boxed{}`"）。
- **`gate_mode`**：`on`（預設，有驗證關卡）或 `off`（貪婪，接受所有編輯）。
- **`gate_metric`**：`hard`、`soft` 或 `mixed`（預設）。控制 held-out 關卡如何計分。
- **`gate_no_regression`**：預設是 `false`。設成 `true` 時，只要有任何驗證任務所設定的關卡分數下降，就拒絕該候選。
- **`dream_rollouts`**：>1 會對每個任務啟用多次 rollout 的對比式反思。
- **`recall_k`**：>0 會把 K 個相似的過去任務召回進 dream（長期記憶）。
- **`evolve_memory`** / **`evolve_skill`**：獨立切換 CLAUDE.md 與 SKILL.md 的整合。

## 記憶整合

睡眠週期可以整合兩者：
- **SKILL.md**：受管理的 skill 檔案（有上限的編輯：新增/刪除/取代）
- **CLAUDE.md**：專案記憶（同樣有上限的編輯）

啟用預設關卡時，兩者都用同一個 held-out 分數評估。設定 `evolve_memory: false` 就只整合 skill，設定 `evolve_skill: false` 就只整合記憶。

## 硬性規則

- **絕對不要**在這個 skill 裡手動編輯使用者的 `CLAUDE.md` / `SKILL.md`。讓引擎明確的 `adopt`，或使用者要求的 `--auto-adopt` 路徑去套用 staging manifest，並先備份既有的線上檔案。
- Harvest 是唯讀的。`mock` 重播沒有副作用。
- 真實的 backend 會把截斷後的 transcript 摘錄和推導出的任務，送給選定的提供者，用於挖掘、重播、評判和反思。Claude transcript 的路徑不保證在這些呼叫之前移除每一個 secret。請先檢視提供者的政策和 session 內容。對敏感資料，使用 `mock`，或執行 `harvest --output <file>`，檢查/遮蔽那份 JSON，設定 `"reviewed": true`，再用 `--tasks-file` 重播；真實的 backend 會拒絕未經審查的任務檔。
- 在建議採用之前，一定要給使用者看 **held-out 的 baseline → 候選**分數，以及確切的提案編輯。採用之前要先有證據。
- 如果被要求在不呼叫提供者的情況下示範這個機制，就執行 `python -m skillopt_sleep.experiments.run_experiment --persona researcher --json`：這是一個確定性的合成 demo，展示 held-out 的提升和關卡的拒絕。它驗證的是機制，不是在使用者自己的任務上的成效。

## 驗證 / demo

```bash
# deterministic synthetic demo (no API): score rises and the gate blocks a regression
python -m skillopt_sleep.experiments.run_experiment --persona researcher --assert-improves
python -m skillopt_sleep.experiments.run_experiment --persona programmer  --assert-improves
```

已記錄的結果、限制和受支援的整合範圍，見 [SkillOpt-Sleep 文件](https://github.com/microsoft/SkillOpt/tree/main/docs/sleep)。
