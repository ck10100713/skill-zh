---
name: autonomous-loops
description: "自主 Claude Code 迴圈的模式與架構：從簡單的循序 pipeline，到由 RFC 驅動的多 agent DAG 系統。僅為相容性而保留：需要新的自主迴圈指引時，請改用 continuous-agent-loop。"
metadata:
  origin: ECC
---

# Autonomous Loops Skill

> 相容性說明（v1.8.0）：`autonomous-loops` 會保留一個版本。
> 正式的 skill 名稱現在是 `continuous-agent-loop`。新的迴圈指引
> 應該寫在那邊，而這個 skill 繼續保留，避免
> 破壞既有的工作流程。

讓 Claude Code 在迴圈中自主運作的模式、架構和參考實作。涵蓋從簡單的 `claude -p` pipeline，到完整由 RFC 驅動的多 agent DAG 編排。

## 何時使用

- 設定不需要人介入、自行運作的自主開發工作流程
- 為你的問題選對迴圈架構（簡單或複雜）
- 建構 CI/CD 風格的持續開發 pipeline
- 以 merge 協調的方式執行平行 agent
- 實作跨迴圈迭代的 context 持久化
- 為自主工作流程加上品質關卡和清理流程

## 迴圈模式光譜

從最簡單到最精密：

| 模式 | 複雜度 | 最適合 |
|---------|-----------|----------|
| [Sequential Pipeline](#1-sequential-pipeline-claude--p) | 低 | 每日開發步驟、腳本化的工作流程 |
| [NanoClaw REPL](#2-nanoclaw-repl) | 低 | 互動式的持久 session |
| [Infinite Agentic Loop](#3-infinite-agentic-loop) | 中 | 平行內容生成、規格驅動的工作 |
| [Continuous Claude PR Loop](#4-continuous-claude-pr-loop) | 中 | 有 CI 關卡、橫跨多天的迭代專案 |
| [De-Sloppify Pattern](#5-the-de-sloppify-pattern) | 附加 | 任何 Implementer 步驟之後的品質清理 |
| [Ralphinho / RFC-Driven DAG](#6-ralphinho--rfc-driven-dag-orchestration) | 高 | 大型功能、有 merge queue 的多單元平行工作 |

---

## 1. Sequential Pipeline（`claude -p`）

**最簡單的迴圈。** 把每日開發拆成一連串非互動式的 `claude -p` 呼叫。每次呼叫都是有明確 prompt 的聚焦步驟。

### 核心洞見

> 如果你想不出這樣的迴圈，代表你連在互動模式下，都沒辦法驅使 LLM 去修你的程式碼。

`claude -p` 這個旗標會以 prompt 非互動式地執行 Claude Code，做完就結束。把呼叫串起來，就是一條 pipeline：

```bash
#!/bin/bash
# daily-dev.sh — feature branch 用的循序 pipeline

set -e

# Step 1: 實作功能
claude -p "Read the spec in docs/auth-spec.md. Implement OAuth2 login in src/auth/. Write tests first (TDD). Do NOT create any new documentation files."

# Step 2: De-sloppify（清理流程）
claude -p "Review all files changed by the previous commit. Remove any unnecessary type tests, overly defensive checks, or testing of language features (e.g., testing that TypeScript generics work). Keep real business logic tests. Run the test suite after cleanup."

# Step 3: 驗證
claude -p "Run the full build, lint, type check, and test suite. Fix any failures. Do not add new features."

# Step 4: Commit
claude -p "Create a conventional commit for all staged changes. Use 'feat: add OAuth2 login flow' as the message."
```

### 關鍵設計原則

1. **每個步驟都是隔離的**：每次 `claude -p` 呼叫都是全新的 context window，所以步驟之間不會有 context 滲漏。
2. **順序很重要**：步驟依序執行。每一步都建立在前一步留下的檔案系統狀態上。
3. **否定式的指令很危險**：不要說「不要測試型別系統」。改成另外加一個清理步驟（見 [De-Sloppify Pattern](#5-the-de-sloppify-pattern)）。
4. **Exit code 會傳遞**：`set -e` 會在失敗時停下 pipeline。

### 變化版本

**搭配模型路由：**
```bash
# 用 Opus 做研究（深度推理）
claude -p --model opus "Analyze the codebase architecture and write a plan for adding caching..."

# 用 Sonnet 實作（快速、能力夠）
claude -p "Implement the caching layer according to the plan in docs/caching-plan.md..."

# 用 Opus 做 review（徹底）
claude -p --model opus "Review all changes for security issues, race conditions, and edge cases..."
```

**搭配環境 context：**
```bash
# 透過檔案傳遞 context，不要靠拉長 prompt
echo "Focus areas: auth module, API rate limiting" > .claude-context.md
claude -p "Read .claude-context.md for priorities. Work through them in order."
rm .claude-context.md
```

**搭配 `--allowedTools` 限制：**
```bash
# 唯讀的分析流程
claude -p --allowedTools "Read,Grep,Glob" "Audit this codebase for security vulnerabilities..."

# 只負責寫入的實作流程
claude -p --allowedTools "Read,Write,Edit,Bash" "Implement the fixes from security-audit.md..."
```

---

## 2. NanoClaw REPL

**ECC 內建的持久迴圈。** 一個感知 session 的 REPL，會帶著完整的對話歷史，同步呼叫 `claude -p`。

```bash
# 使用設定好的 plugin 根目錄，或獨立安裝的位置（~/.claude 或
# $CLAUDE_CONFIG_DIR）。對於經過審查並明確授權的 ECC checkout：
# export CLAUDE_PLUGIN_ROOT="/absolute/path/to/reviewed/ECC"
ECC_ROOT="${CLAUDE_PLUGIN_ROOT:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}}"
[ -f "$ECC_ROOT/scripts/claw.js" ] || { echo "ECC scripts not found in the selected root (set CLAUDE_PLUGIN_ROOT to an authorized ECC checkout)" >&2; exit 1; }

# 啟動預設的 session
node "$ECC_ROOT/scripts/claw.js"

# 帶有 skill context 的具名 session
CLAW_SESSION=my-project CLAW_SKILLS=tdd-workflow,security-review node "$ECC_ROOT/scripts/claw.js"
```

### 運作方式

1. 從 `~/.claude/claw/{session}.md` 載入對話歷史
2. 每則使用者訊息都帶著完整歷史當 context，送給 `claude -p`
3. 回應會附加到 session 檔案（把 Markdown 當資料庫）
4. Session 能撐過重啟

### 什麼時候用 NanoClaw，什麼時候用 Sequential Pipeline

| 使用情境 | NanoClaw | Sequential Pipeline |
|----------|----------|-------------------|
| 互動式探索 | 是 | 否 |
| 腳本化自動化 | 否 | 是 |
| Session 持久化 | 內建 | 手動 |
| Context 累積 | 每一輪都增長 | 每步都是全新的 |
| CI/CD 整合 | 差 | 極佳 |

完整細節請看 `/claw` 指令的文件。

---

## 3. Infinite Agentic Loop

**兩個 prompt 組成的系統**，編排平行的 sub-agent，做規格驅動的生成。由 disler 開發（credit: @disler）。

### 架構：兩個 Prompt 的系統

```
PROMPT 1 (Orchestrator)              PROMPT 2 (Sub-Agents)
┌─────────────────────┐             ┌──────────────────────┐
│ Parse spec file      │             │ Receive full context  │
│ Scan output dir      │  deploys   │ Read assigned number  │
│ Plan iteration       │────────────│ Follow spec exactly   │
│ Assign creative dirs │  N agents  │ Generate unique output │
│ Manage waves         │             │ Save to output dir    │
└─────────────────────┘             └──────────────────────┘
```

### 模式

1. **規格分析**：Orchestrator 讀一份定義要生成什麼的規格檔案（Markdown）
2. **目錄偵察**：掃描現有的輸出，找出最高的迭代編號
3. **平行部署**：啟動 N 個 sub-agent，每個都拿到：
   - 完整的規格
   - 獨一無二的創意方向
   - 特定的迭代編號（不會衝突）
   - 現有迭代的快照（確保不重複）
4. **波次管理**：無限模式下，每波部署 3 到 5 個 agent，直到 context 用完

### 透過 Claude Code Command 實作

建立 `.claude/commands/infinite.md`：

```markdown
Parse the following arguments from $ARGUMENTS:
1. spec_file — path to the specification markdown
2. output_dir — where iterations are saved
3. count — integer 1-N or "infinite"

PHASE 1: Read and deeply understand the specification.
PHASE 2: List output_dir, find highest iteration number. Start at N+1.
PHASE 3: Plan creative directions — each agent gets a DIFFERENT theme/approach.
PHASE 4: Deploy sub-agents in parallel (Task tool). Each receives:
  - Full spec text
  - Current directory snapshot
  - Their assigned iteration number
  - Their unique creative direction
PHASE 5 (infinite mode): Loop in waves of 3-5 until context is low.
```

**呼叫：**
```bash
/project:infinite specs/component-spec.md src/ 5
/project:infinite specs/component-spec.md src/ infinite
```

### 批次策略

| 數量 | 策略 |
|-------|----------|
| 1-5 | 所有 agent 同時進行 |
| 6-20 | 每批 5 個 |
| infinite | 每波 3 到 5 個，逐步提高精緻度 |

### 關鍵洞見：用指派來確保獨特性

不要指望 agent 自己做出差異。Orchestrator 要**指派**每個 agent 特定的創意方向和迭代編號。這樣才能避免平行的 agent 之間出現重複的點子。

---

## 4. Continuous Claude PR Loop

**一支正式環境等級的 shell script**，讓 Claude Code 在持續的迴圈裡執行，建立 PR、等 CI、自動 merge。由 AnandChowdhary 製作（credit: @AnandChowdhary）。

### 核心迴圈

```
┌─────────────────────────────────────────────────────┐
│  CONTINUOUS CLAUDE ITERATION                        │
│                                                     │
│  1. Create branch (continuous-claude/iteration-N)   │
│  2. Run claude -p with enhanced prompt              │
│  3. (Optional) Reviewer pass — separate claude -p   │
│  4. Commit changes (claude generates message)       │
│  5. Push + create PR (gh pr create)                 │
│  6. Wait for CI checks (poll gh pr checks)          │
│  7. CI failure? → Auto-fix pass (claude -p)         │
│  8. Merge PR (squash/merge/rebase)                  │
│  9. Return to main → repeat                         │
│                                                     │
│  Limit by: --max-runs N | --max-cost $X             │
│            --max-duration 2h | completion signal     │
└─────────────────────────────────────────────────────┘
```

### 安裝

> **警告：** 要審查過程式碼之後，再從它的 repo 安裝 continuous-claude。不要把外部的 script 直接 pipe 給 bash。

### 用法

```bash
# 基本：10 次迭代
continuous-claude --prompt "Add unit tests for all untested functions" --max-runs 10

# 限制成本
continuous-claude --prompt "Fix all linter errors" --max-cost 5.00

# 限制時間
continuous-claude --prompt "Improve test coverage" --max-duration 8h

# 搭配 code review 流程
continuous-claude \
  --prompt "Add authentication feature" \
  --max-runs 10 \
  --review-prompt "Run npm test && npm run lint, fix any failures"

# 透過 worktree 平行執行
continuous-claude --prompt "Add tests" --max-runs 5 --worktree tests-worker &
continuous-claude --prompt "Refactor code" --max-runs 5 --worktree refactor-worker &
wait
```

### 跨迭代 Context：SHARED_TASK_NOTES.md

關鍵的創新：一份 `SHARED_TASK_NOTES.md` 檔案，會跨迭代保留：

```markdown
## Progress
- [x] Added tests for auth module (iteration 1)
- [x] Fixed edge case in token refresh (iteration 2)
- [ ] Still need: rate limiting tests, error boundary tests

## Next Steps
- Focus on rate limiting module next
- The mock setup in tests/helpers.ts can be reused
```

Claude 在迭代開始時讀這份檔案，結束時更新它。這樣就補上了各自獨立的 `claude -p` 呼叫之間的 context 缺口。

### CI 失敗復原

當 PR 檢查失敗時，Continuous Claude 會自動：
1. 透過 `gh run list` 取得失敗的 run ID
2. 帶著 CI 修復的 context，啟動新的 `claude -p`
3. Claude 透過 `gh run view` 檢查 log、修程式碼、commit、push
4. 重新等待檢查（最多 `--ci-retry-max` 次）

### 完成訊號

Claude 可以輸出一句暗號，來表示「我做完了」：

```bash
continuous-claude \
  --prompt "Fix all bugs in the issue tracker" \
  --completion-signal "CONTINUOUS_CLAUDE_PROJECT_COMPLETE" \
  --completion-threshold 3  # 連續 3 次訊號後停止
```

連續三次迭代都發出完成訊號，就會停下迴圈，避免在已經做完的工作上白跑。

### 關鍵設定

| 旗標 | 用途 |
|------|---------|
| `--max-runs N` | 成功 N 次迭代後停止 |
| `--max-cost $X` | 花到 $X 後停止 |
| `--max-duration 2h` | 經過指定時間後停止 |
| `--merge-strategy squash` | squash、merge 或 rebase |
| `--worktree <name>` | 透過 git worktree 平行執行 |
| `--disable-commits` | Dry-run 模式（不做 git 操作） |
| `--review-prompt "..."` | 每次迭代加上 reviewer 流程 |
| `--ci-retry-max N` | 自動修 CI 失敗（預設：1） |

---

## 5. De-Sloppify 模式

**可以加在任何迴圈上的附加模式。** 在每個 Implementer 步驟之後，加上專門的清理/重構步驟。

### 問題

當你要求 LLM 用 TDD 實作時，它會把「寫測試」理解得太字面：
- 測試在驗證 TypeScript 的型別系統有在運作（測試 `typeof x === 'string'`）
- 對型別系統已經保證的事，做過度防禦的 runtime 檢查
- 測試的是框架的行為，不是商業邏輯
- 過多的錯誤處理，把真正的程式碼蓋住了

### 為什麼不用否定式指令？

在 Implementer 的 prompt 裡加上「不要測試型別系統」或「不要加不必要的檢查」，會有下游的副作用：
- 模型對「所有」測試都變得猶豫
- 它會跳過正當的 edge case 測試
- 品質會以無法預測的方式下降

### 解法：獨立的流程

不要限制 Implementer，讓它盡量做得徹底。然後再加一個專注於清理的 agent：

```bash
# Step 1: 實作（讓它徹底）
claude -p "Implement the feature with full TDD. Be thorough with tests."

# Step 2: De-sloppify（獨立的 context，專注清理）
claude -p "Review all changes in the working tree. Remove:
- Tests that verify language/framework behavior rather than business logic
- Redundant type checks that the type system already enforces
- Over-defensive error handling for impossible states
- Console.log statements
- Commented-out code

Keep all business logic tests. Run the test suite after cleanup to ensure nothing breaks."
```

### 在迴圈情境裡

```bash
for feature in "${features[@]}"; do
  # 實作
  claude -p "Implement $feature with TDD."

  # De-sloppify
  claude -p "Cleanup pass: review changes, remove test/code slop, run tests."

  # 驗證
  claude -p "Run build + lint + tests. Fix any failures."

  # Commit
  claude -p "Commit with message: feat: add $feature"
done
```

### 關鍵洞見

> 與其加上會影響下游品質的否定式指令，不如另外加一個 de-sloppify 流程。兩個各有專注的 agent，勝過一個被限制住的 agent。

---

## 6. Ralphinho / 由 RFC 驅動的 DAG 編排

**最精密的模式。** 由 RFC 驅動的多 agent pipeline，把規格拆解成相依性 DAG，讓每個單元跑過分級的品質 pipeline，再透過由 agent 驅動的 merge queue 落地。由 enitrat 製作（credit: @enitrat）。

### 架構概覽

```
RFC/PRD Document
       │
       ▼
  DECOMPOSITION (AI)
  Break RFC into work units with dependency DAG
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  RALPH LOOP (up to 3 passes)                         │
│                                                      │
│  For each DAG layer (sequential, by dependency):     │
│                                                      │
│  ┌── Quality Pipelines (parallel per unit) ───────┐  │
│  │  Each unit in its own worktree:                │  │
│  │  Research → Plan → Implement → Test → Review   │  │
│  │  (depth varies by complexity tier)             │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌── Merge Queue ─────────────────────────────────┐  │
│  │  Rebase onto main → Run tests → Land or evict │  │
│  │  Evicted units re-enter with conflict context  │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### RFC 拆解

AI 讀 RFC 並產出工作單元：

```typescript
interface WorkUnit {
  id: string;              // kebab-case 識別碼
  name: string;            // 人類可讀的名稱
  rfcSections: string[];   // 這個單元對應 RFC 的哪些段落
  description: string;     // 詳細描述
  deps: string[];          // 相依項目（其他單元的 ID）
  acceptance: string[];    // 具體的驗收標準
  tier: "trivial" | "small" | "medium" | "large";
}
```

**拆解規則：**
- 偏好少量、內聚的單元（把 merge 風險降到最低）
- 盡量減少單元之間的檔案重疊（避免衝突）
- 測試要「跟著」實作走（絕對不要把「實作 X」和「測試 X」拆開）
- 只有在真的存在程式碼相依時，才設定相依

相依性 DAG 決定執行順序：
```
Layer 0: [unit-a, unit-b]     ← 沒有相依，平行執行
Layer 1: [unit-c]             ← 依賴 unit-a
Layer 2: [unit-d, unit-e]     ← 依賴 unit-c
```

### 複雜度分級

不同等級有不同的 pipeline 深度：

| 等級 | Pipeline 階段 |
|------|----------------|
| **trivial** | implement → test |
| **small** | implement → test → code-review |
| **medium** | research → plan → implement → test → PRD-review + code-review → review-fix |
| **large** | research → plan → implement → test → PRD-review + code-review → review-fix → final-review |

這樣能避免在簡單的修改上做昂貴的操作，同時確保架構層級的修改受到徹底的檢視。

### 獨立的 Context Window（消除作者偏見）

每個階段都在自己的 agent process、自己的 context window 裡執行：

| 階段 | 模型 | 用途 |
|-------|-------|---------|
| Research | Sonnet | 讀 codebase + RFC，產出 context 文件 |
| Plan | Opus | 設計實作步驟 |
| Implement | Codex | 依計畫寫程式 |
| Test | Sonnet | 跑 build + 測試套件 |
| PRD Review | Sonnet | 檢查是否符合規格 |
| Code Review | Opus | 檢查品質與安全 |
| Review Fix | Codex | 處理 review 提出的問題 |
| Final Review | Opus | 品質關卡（只有 large 等級） |

**關鍵設計：** Reviewer 從來沒寫過它要 review 的程式碼。這消除了作者偏見，而這是自我 review 時最常漏掉問題的來源。

### 帶有驅逐機制的 Merge Queue

品質 pipeline 完成後，單元進入 merge queue：

```
Unit branch
    │
    ├─ Rebase onto main
    │   └─ Conflict? → EVICT (capture conflict context)
    │
    ├─ Run build + tests
    │   └─ Fail? → EVICT (capture test output)
    │
    └─ Pass → Fast-forward main, push, delete branch
```

**檔案重疊的判斷：**
- 沒有重疊的單元，會推測性地平行落地
- 有重疊的單元，一個一個落地，每次都 rebase

**驅逐後的復原：**
被驅逐時，會擷取完整的 context（衝突的檔案、diff、測試輸出），並在下一輪 Ralph 時回饋給 implementer：

```markdown
## MERGE CONFLICT — RESOLVE BEFORE NEXT LANDING

Your previous implementation conflicted with another unit that landed first.
Restructure your changes to avoid the conflicting files/lines below.

{full eviction context with diffs}
```

### 階段之間的資料流

```
research.contextFilePath ──────────────────→ plan
plan.implementationSteps ──────────────────→ implement
implement.{filesCreated, whatWasDone} ─────→ test, reviews
test.failingSummary ───────────────────────→ reviews, implement (next pass)
reviews.{feedback, issues} ────────────────→ review-fix → implement (next pass)
final-review.reasoning ────────────────────→ implement (next pass)
evictionContext ───────────────────────────→ implement (after merge conflict)
```

### Worktree 隔離

每個單元都在隔離的 worktree 裡執行（用的是 jj/Jujutsu，不是 git）：
```
/tmp/workflow-wt-{unit-id}/
```

同一個單元的各個 pipeline 階段**共用**同一個 worktree，這樣狀態（context 檔案、計畫檔案、程式碼修改）能在 research → plan → implement → test → review 之間保留下來。

### 關鍵設計原則

1. **確定性的執行**：事先拆解，就鎖定了平行度和順序
2. **在槓桿點由人 review**：工作計畫是單一槓桿最高的介入點
3. **關注點分離**：每個階段在獨立的 context window、由獨立的 agent 處理
4. **帶 context 的衝突復原**：完整的驅逐 context 讓重跑是有智慧的，不是盲目重試
5. **由等級決定深度**：trivial 的修改跳過 research/review；large 的修改接受最嚴格的檢視
6. **可恢復的工作流程**：完整狀態持久化到 SQLite；可以從任何一點恢復

### 什麼時候用 Ralphinho，什麼時候用比較簡單的模式

| 訊號 | 用 Ralphinho | 用比較簡單的模式 |
|--------|--------------|-------------------|
| 有多個相互依賴的工作單元 | 是 | 否 |
| 需要平行實作 | 是 | 否 |
| 很可能有 merge 衝突 | 是 | 否（循序就夠了） |
| 單一檔案的修改 | 否 | 是（sequential pipeline） |
| 橫跨多天的專案 | 是 | 也許（continuous-claude） |
| 規格/RFC 已經寫好 | 是 | 也許 |
| 針對單一件事快速迭代 | 否 | 是（NanoClaw 或 pipeline） |

---

## 選擇適合的模式

### 決策矩陣

```
Is the task a single focused change?
├─ Yes → Sequential Pipeline or NanoClaw
└─ No → Is there a written spec/RFC?
         ├─ Yes → Do you need parallel implementation?
         │        ├─ Yes → Ralphinho (DAG orchestration)
         │        └─ No → Continuous Claude (iterative PR loop)
         └─ No → Do you need many variations of the same thing?
                  ├─ Yes → Infinite Agentic Loop (spec-driven generation)
                  └─ No → Sequential Pipeline with de-sloppify
```

### 組合模式

這些模式很適合組合使用：

1. **Sequential Pipeline + De-Sloppify**：最常見的組合。每個 implement 步驟都跟著一個清理流程。

2. **Continuous Claude + De-Sloppify**：在每次迭代的 `--review-prompt` 裡加上 de-sloppify 的指示。

3. **任何迴圈 + 驗證**：在 commit 之前，用 ECC 的 `/verify` 指令或 `verification-loop` skill 當關卡。

4. **在比較簡單的迴圈裡用 Ralphinho 的分級做法**：即使是 sequential pipeline，也可以把簡單的任務導向 Haiku，複雜的任務導向 Opus：
   ```bash
   # 簡單的格式修正
   claude -p --model haiku "Fix the import ordering in src/utils.ts"

   # 複雜的架構修改
   claude -p --model opus "Refactor the auth module to use the strategy pattern"
   ```

---

## 反面模式

### 常見錯誤

1. **沒有結束條件的無限迴圈**：一定要有 max-runs、max-cost、max-duration 或完成訊號。

2. **迭代之間沒有 context 橋接**：每次 `claude -p` 呼叫都是從零開始。用 `SHARED_TASK_NOTES.md` 或檔案系統狀態來橋接 context。

3. **重試同一個失敗**：迭代失敗時，不要只是重試。要擷取錯誤的 context，餵給下一次嘗試。

4. **用否定式指令取代清理流程**：不要說「不要做 X」。加一個獨立的流程，把 X 移除。

5. **所有 agent 擠在同一個 context window**：複雜的工作流程，要把關注點拆到不同的 agent process。Reviewer 絕對不能是作者。

6. **平行工作時忽略檔案重疊**：如果兩個平行的 agent 可能修改同一個檔案，你就需要 merge 策略（循序落地、rebase 或衝突解決）。

---

## 參考資料

| 專案 | 作者 | 連結 |
|---------|--------|------|
| Ralphinho | enitrat | credit: @enitrat |
| Infinite Agentic Loop | disler | credit: @disler |
| Continuous Claude | AnandChowdhary | credit: @AnandChowdhary |
| NanoClaw | ECC | 這個 repo 裡的 `/claw` 指令 |
| Verification Loop | ECC | 這個 repo 裡的 `skills/verification-loop/` |
