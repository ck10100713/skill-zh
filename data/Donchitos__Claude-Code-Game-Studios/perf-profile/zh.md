---
name: perf-profile
description: "效能分析：找出瓶頸、對照預算量測，並產出依優先順序排序的最佳化建議。"
argument-hint: "[system-name or 'full']"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/perf-profile/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash "*/.claude/skills/perf-profile/../../hooks/yaml-helper.sh" get_effective_yaml_key *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys performance.enforce,automation,workflow`

上面已經解析好了，直接用。沒有這個區塊的話，用
`.claude/docs/config-resolution.md` 裡的預設值。

# Performance Profile

每一次 `AskUserQuestion` 呼叫都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

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

## Phase 0: Resolve Budget Enforcement

`performance.enforce` 決定預算違規在這次執行中*代表什麼*。它
不會改變要量測哪些預算 — `performance.target_framerate`、
`frame_budget_ms`、`draw_call_limit` 和 `memory_ceiling_mb` 在每個等級
都是用同樣的方式分析：

| Value | Effect on this profile's findings |
|-------|-----------------------------------|
| `warn` (default) | Violations are reported as findings. They do not block; CI logs them without failing. |
| `block` | Violations are **blockers**. Say so explicitly in the report — a `block` project treats an over-budget system as release-stopping, and `/gate-check` will FAIL the Polish gate on it. |
| `off` | Budgets are informational only. Still report measured values, but do not raise violations as findings or recommendations to fix. |

只有 `warn`、`block` 和 `off` 會被認得。看到任何其他值，就告訴
使用者，並退回 `warn`，不要亂猜。

> 這個值可以在本機覆蓋（`/settings --local performance.enforce=block`），
> 所以要用上面解析好的區塊，不要去讀 `project.yaml` — 隊友
> 在本機設的比較嚴格的值，本來就應該只在他的機器上生效。

## Phase 1: Determine Scope

讀參數：

- 系統名稱 → 把分析聚焦在那個特定系統
- `full` → 對所有系統跑完整的分析

---

## Phase 2: Load Performance Budgets

**先從 config 讀已提交的預算** — 它們是專案對自己同意了什麼的
紀錄，設計文件只是退路，不是來源：

```bash
bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" get_effective_yaml_key performance.target_framerate
bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" get_effective_yaml_key performance.frame_budget_ms
bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" get_effective_yaml_key performance.draw_call_limit
bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" get_effective_yaml_key performance.memory_ceiling_mb
```

每一行當成獨立的純指令執行，一次呼叫一個 key：helper 會自己切換到
專案根目錄，所以就算 session 是在子資料夾啟動的也能運作，而這個 skill 只預先核准
那種形式（用 `source` 或 `cd ... &&` 包起來，每次都會問使用者）。輸出是空的，
代表那個預算沒設。

> **要從 `project.yaml` 解析這些預算，不要從文字敘述。** 上面的 Phase 0
> 說這四個預算「在每個等級都是用同樣的方式分析」。如果預算是從設計文件或 CLAUDE.md
> 讀的，在 `project.yaml` 設了
> `performance.target_framerate: 60` 的使用者，這個設定就會被忽略。

然後對 config 沒有的東西，退回去讀設計文件或 CLAUDE.md：

- 目標 FPS（例如 60fps = 16.67ms 的 frame 預算）
- 記憶體預算（總量和每個系統）
- 載入時間目標
- Draw call 預算
- 網路頻寬上限（如果是多人遊戲）

**沒有已提交預算的指標是 `NOT ASSESSED`，不是通過。** 不要
對照範本的 `[16.67ms]` placeholder 去量測 — 沒設的預算不是
已經達標的預算，而對照一個沒人選的數字去回報 headroom，
正是這個 skill 自己的標頭警告過的那種捏造。

---

## Phase 3: Analyze Codebase

**CPU 分析目標：**
- `_process()` / `Update()` / `Tick()` 函式 — 全部列出並估算成本
- 對大型集合的巢狀迴圈
- 熱路徑上的字串運算
- 每個 frame 都執行的程式碼裡的配置模式
- 對遊戲實體做的未最佳化搜尋/排序
- 每個 frame 都做的昂貴物理查詢（raycast、overlap）

**記憶體分析目標：**
- 大型資料結構和它們的成長模式
- 貼圖/資產記憶體佔用的估計
- Object pool vs instantiate/destroy 的模式
- 洩漏的參照（應該被釋放卻沒有的物件）
- 快取大小和淘汰政策

**渲染目標（如果適用）：**
- Draw call 估計
- 重疊的透明物件造成的 overdraw
- Shader 複雜度
- 未最佳化的粒子系統
- 缺少 LOD 或 occlusion culling

**I/O 目標：**
- 存檔/讀檔效能
- 資產載入模式（同步 vs 非同步）
- 網路訊息的頻率和大小

---

## Phase 4: Generate Profiling Report

**把報告寫到 `production/polish/[scope]-report-[date].md`**，並依
Collaboration Protocol 先問：*"May I write this profiling report to
`production/polish/[scope]-report-[date].md`?"* 目錄不存在就建立。

> **要點名目的地 — 不要只把範本渲染到對話裡就算了。**
> 只存在於 transcript 裡的 profile，session 一結束就沒了，
> 而且沒辦法拿兩次執行來比較。`production/polish/`
> 刻意跟 `/team-polish` 寫入的位置相同：不管走哪條路取得的 profile，
> 都應該放在同一個地方，不然這個 skill 存在的目的，也就是比較，
> 就做不到。
>
> 如果有 `NOT ASSESSED` 章節留在報告裡，就把它保留在寫入的
> 檔案裡。在寫到磁碟的路上把缺口編輯掉的 profile，之後讀起來
> 會像一份完整的量測。


```markdown
## Performance Profile: [System or Full]
Generated: [Date]

### Performance Budgets
| Metric | Budget | Estimated Current | Status |
|--------|--------|-------------------|--------|
| Frame time | [16.67ms] | [estimate] | [OK/WARNING/OVER/NOT ASSESSED] |
| Memory | [target] | [estimate] | [OK/WARNING/OVER/NOT ASSESSED] |
| Load time | [target] | [estimate] | [OK/WARNING/OVER/NOT ASSESSED] |
| Draw calls | [target] | [estimate] | [OK/WARNING/OVER/NOT ASSESSED] |

### Hotspots Identified
| # | Location | Issue | Estimated Impact | Fix Effort |
|---|----------|-------|------------------|------------|

### Optimization Recommendations (Priority Order)
1. **[Title]** — [Description]
   - Location: [file:line]
   - Expected gain: [estimate]
   - Risk: [Low/Med/High]
   - Approach: [How to implement]

### Quick Wins (< 1 hour each)
- [Simple optimization 1]

### Requires Investigation
- [Area that needs actual runtime profiling to confirm impact]
```

輸出報告時附上摘要：前 3 個熱點、對每個已設定的預算估計的
headroom — 沒有預算的指標就寫 `no budget set — headroom not
assessed` — 以及建議的下一步動作。

---

## Phase 5: Scope and Timeline Decision

只有在任何熱點的 Fix Effort 被評為 M 或 L 時，才啟動這個階段。

呈現需要大量投入的項目，並請使用者對每一項做選擇：

- **A) 實作最佳化**（現在就做修復或排進行程 — 在沒有 sprint 的 `workflow: minimal`，加進 brief 的 build order）
- **B) 縮減功能範圍**（執行 `/scope-check [feature]` 分析取捨）
- **C) 接受效能損失，延後到 Polish 階段**（記成已知問題）
- **D) 升級給 technical-director 做架構決策**（執行 `/architecture-decision`）

如果有多個項目被延後到 Polish（選項 C），把它們記在 `### Deferred to Polish` 底下。

---

## Verdict

每個有產出報告的執行都要收尾 — 不管 Phase 5 有沒有執行 — 用：
Verdict: **COMPLETE** — performance profile generated（如果寫入有核准，
就存到 `production/polish/[scope]-report-[date].md`）。唯一的
另一種結果，就是上面的 `NOT ASSESSED — NO DATA` 路徑。

---

## Phase 6: Next Steps

- 如果瓶頸需要架構層級的改變：執行 `/architecture-decision`。
- 如果需要縮減範圍：執行 `/scope-check [feature]`。
- 要把最佳化排進行程：執行 `/sprint-plan update`（在沒有 sprint 的 `workflow: minimal`，改加進 brief 的 build order）。

### Rules
- 沒量測過就絕對不要最佳化 — 對效能的直覺不可靠
- 建議必須包含估計的影響 — 「讓它變快」是沒辦法執行的
- 要在目標硬體上分析，不只是開發機
- 靜態分析（這個 skill）找出候選項目；runtime profiling 才能確認
