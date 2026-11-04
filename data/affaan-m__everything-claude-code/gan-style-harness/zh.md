---
name: gan-style-harness
description: "受 GAN 啟發的 Generator-Evaluator agent harness，用來自主打造高品質的應用程式。依據 Anthropic 2026 年 3 月的 harness 設計論文。當某個功能應該透過 generator 和 evaluator 反覆迭代、直到通過品質門檻為止，並由 agent 自主完成時使用。"
metadata:
  origin: ECC-community
tools: Read, Write, Edit, Bash, Grep, Glob, Task
---

# GAN-Style Harness Skill

> 靈感來自 [Anthropic 的 Harness Design for Long-Running Application Development](https://www.anthropic.com/engineering/harness-design-long-running-apps)（2026 年 3 月 24 日）

一個把**生成**和**評估**分開的多 agent harness，建立一個對抗式的回饋迴圈，把品質推到遠超過單一 agent 能做到的程度。

## Core Insight

> 叫 agent 評估自己的作品時，它們是病態的樂觀主義者：會稱讚平庸的產出，還會說服自己放過真正的問題。但是設計一個**獨立的 evaluator**，讓它嚴格到毫不留情，比教 generator 自我批評容易得多。

這跟 GAN（生成對抗網路）是同一種動態：Generator 負責產出，Evaluator 負責批評，而這份回饋會驅動下一輪迭代。

## When to Use

- 從一行 prompt 開始建構完整的應用程式
- 需要高視覺品質的前端設計任務
- 需要真正能用的功能、而不只是程式碼的 full-stack 專案
- 任何無法接受「AI slop」美學的任務
- 願意投入 50 到 200 美元換取 production 品質產出的專案

## When NOT to Use

- 快速的單檔修正（用標準的 `claude -p`）
- 預算很緊的任務（低於 10 美元）
- 簡單的重構（改用 de-sloppify 模式）
- 已經有測試、規格很明確的任務（用 TDD 工作流程）

## Architecture

```
                    ┌─────────────┐
                    │   PLANNER   │
                    │  (Sonnet)   │
                    └──────┬──────┘
                           │ Product Spec
                           │ (features, sprints, design direction)
                           ▼
              ┌────────────────────────┐
              │                        │
              │   GENERATOR-EVALUATOR  │
              │      FEEDBACK LOOP     │
              │                        │
              │  ┌──────────┐          │
              │  │GENERATOR │--build-->│──┐
              │  │ (Sonnet) │          │  │
              │  └────▲─────┘          │  │
              │       │                │  │ live app
              │    feedback             │  │
              │       │                │  │
              │  ┌────┴─────┐          │  │
              │  │EVALUATOR │<-test----│──┘
              │  │ (Sonnet) │          │
              │  │+Playwright│         │
              │  └──────────┘          │
              │                        │
              │   5-15 iterations      │
              └────────────────────────┘
```

## The Three Agents

### 1. Planner Agent

**角色：** 產品經理，把簡短的 prompt 擴充成完整的產品規格。

**關鍵行為：**
- 接收一行 prompt，產出一份包含 16 個功能、分多個 sprint 的規格
- 定義使用者故事、技術需求和視覺設計方向
- 刻意走**野心勃勃**的路線，保守的規劃只會帶來令人失望的結果
- 產出 Evaluator 之後會用到的評估準則

**Model：** 預設 Sonnet；想要更深入的規格擴充，可以用 `GAN_PLANNER_MODEL=opus` 提升

### 2. Generator Agent

**角色：** 開發者，照規格實作功能。

**關鍵行為：**
- 以結構化的 sprint 運作（較新的模型可以用連續模式）
- 在寫程式碼之前，先跟 Evaluator 協商一份「sprint contract」
- 使用完整的 full-stack 工具：React、FastAPI/Express、資料庫、CSS
- 在迭代之間用 git 管理版本控制
- 讀取 Evaluator 的回饋，並納入下一輪迭代

**Model：** 預設 Sonnet；想要最強的寫程式能力，可以用 `GAN_GENERATOR_MODEL=opus` 提升

### 3. Evaluator Agent

**角色：** QA 工程師，測試正在執行的真實應用程式，不只是看程式碼。

**關鍵行為：**
- 用 **Playwright MCP** 跟執行中的應用程式互動
- 點過每個功能、填表單、測試 API endpoint
- 依四項準則打分（可設定）：
  1. **Design Quality**：整體感覺是不是一個連貫的整體？
  2. **Originality**：是自訂的決策，還是範本/AI 的慣用模式？
  3. **Craft**：字體、間距、動畫、微互動做得怎樣？
  4. **Functionality**：所有功能真的都能用嗎？
- 回傳結構化的回饋，包含分數和具體的問題
- 被設計成**嚴格到毫不留情**，絕對不稱讚平庸的作品

**Model：** 預設 Sonnet；想要更強的判斷力加工具使用能力，可以用 `GAN_EVALUATOR_MODEL=opus` 提升

## Evaluation Criteria

預設的四項準則，每項 1 到 10 分：

```markdown
## Evaluation Rubric

### Design Quality (weight: 0.3)
- 1-3: Generic, template-like, "AI slop" aesthetics
- 4-6: Competent but unremarkable, follows conventions
- 7-8: Distinctive, cohesive visual identity
- 9-10: Could pass for a professional designer's work

### Originality (weight: 0.2)
- 1-3: Default colors, stock layouts, no personality
- 4-6: Some custom choices, mostly standard patterns
- 7-8: Clear creative vision, unique approach
- 9-10: Surprising, delightful, genuinely novel

### Craft (weight: 0.3)
- 1-3: Broken layouts, missing states, no animations
- 4-6: Works but feels rough, inconsistent spacing
- 7-8: Polished, smooth transitions, responsive
- 9-10: Pixel-perfect, delightful micro-interactions

### Functionality (weight: 0.2)
- 1-3: Core features broken or missing
- 4-6: Happy path works, edge cases fail
- 7-8: All features work, good error handling
- 9-10: Bulletproof, handles every edge case
```

### Scoring

- **加權分數** = (各準則分數 * 權重) 的總和
- **通過門檻** = 7.0（可設定）
- **最大迭代次數** = 15（可設定，通常 5 到 15 次就夠）

## Usage

### Via Command

```bash
# 完整的三 agent harness
/project:gan-build "Build a project management app with Kanban boards, team collaboration, and dark mode"

# 搭配自訂設定
/project:gan-build "Build a recipe sharing platform" --max-iterations 10 --pass-threshold 7.5

# 前端設計模式（只有 generator + evaluator，沒有 planner）
/project:gan-design "Create a landing page for a crypto portfolio tracker"
```

### Via Shell Script

```bash
# 基本用法
./scripts/gan-harness.sh "Build a music streaming dashboard"

# 帶選項
GAN_MAX_ITERATIONS=10 \
GAN_PASS_THRESHOLD=7.5 \
GAN_EVAL_CRITERIA="functionality,performance,security" \
./scripts/gan-harness.sh "Build a REST API for task management"
```

### Via Claude Code (Manual)

```bash
# Step 1: Plan
claude -p --model sonnet "You are a Product Planner. Read PLANNER_PROMPT.md. Expand this brief into a full product spec: 'Build a Kanban board app'. Write spec to spec.md"

# Step 2: Generate (iteration 1)
claude -p --model sonnet "You are a Generator. Read spec.md. Implement Sprint 1. Start the dev server on port 3000."

# Step 3: Evaluate (iteration 1)
claude -p --model sonnet --allowedTools "Read,Bash,mcp__playwright__*" "You are an Evaluator. Read EVALUATOR_PROMPT.md. Test the live app at http://localhost:3000. Score against the rubric. Write feedback to feedback-001.md"

# Step 4: Generate (iteration 2 — reads feedback)
claude -p --model sonnet "You are a Generator. Read spec.md and feedback-001.md. Address all issues. Improve the scores."

# 重複步驟 3 到 4，直到達到通過門檻
```

## Evolution Across Model Capabilities

模型越來越強，harness 就該越來越精簡。以下依循 Anthropic 的演進：

### Stage 1 — Weaker Models (Sonnet-class)
- 需要完整的 sprint 拆解
- sprint 之間要重設 context（避免 context 焦慮）
- 最少 2 個 agent：Initializer + Coding Agent
- 用大量的鷹架（scaffolding）彌補模型的不足

### Stage 2 — Capable Models (Opus 4.5-class)
- 完整的 3 agent harness：Planner + Generator + Evaluator
- 每個實作階段之前先訂 sprint contract
- 複雜的 app 拆成 10 個 sprint
- 重設 context 仍然有用，但沒那麼關鍵

### Stage 3 — Frontier Models (Opus 4.6-class)
- 簡化的 harness：單次規劃，連續生成
- 評估簡化成最後單次收尾的檢查（模型更聰明了）
- 不需要 sprint 結構
- 自動 compaction 處理 context 的成長

> **關鍵原則：** harness 的每個元件，都編碼了一個「模型自己做不到什麼」的假設。模型進步時，要重新測試這些假設，把不再需要的部分拿掉。

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GAN_MAX_ITERATIONS` | `15` | generator-evaluator 的最大循環次數 |
| `GAN_PASS_THRESHOLD` | `7.0` | 通過所需的加權分數（1-10） |
| `GAN_PLANNER_MODEL` | `sonnet` | planning agent 用的 model |
| `GAN_GENERATOR_MODEL` | `sonnet` | generator agent 用的 model |
| `GAN_EVALUATOR_MODEL` | `sonnet` | evaluator agent 用的 model |
| `GAN_EVAL_CRITERIA` | `design,originality,craft,functionality` | 以逗號分隔的準則 |
| `GAN_DEV_SERVER_PORT` | `3000` | 執行中 app 的 port |
| `GAN_DEV_SERVER_CMD` | `npm run dev` | 啟動 dev server 的指令 |
| `GAN_PROJECT_DIR` | `.` | 專案的工作目錄 |
| `GAN_SKIP_PLANNER` | `false` | 跳過 planner，直接用現成的規格 |
| `GAN_EVAL_MODE` | `playwright` | `playwright`、`screenshot` 或 `code-only` |

### Evaluation Modes

| Mode | Tools | Best For |
|------|-------|----------|
| `playwright` | Browser MCP + 即時互動 | 有 UI 的 full-stack 應用 |
| `screenshot` | 截圖 + 視覺分析 | 靜態網站、只做設計 |
| `code-only` | 測試 + linting + build | API、函式庫、CLI 工具 |

## Anti-Patterns

1. **Evaluator 太寬鬆**：如果 evaluator 在第一輪迭代就全部放行，代表你的評分標準太寬鬆。把評分準則收緊，並針對常見的 AI 慣用模式加上明確的扣分。

2. **Generator 無視回饋**：確保回饋是用檔案傳遞，不是 inline。Generator 應該在每輪迭代一開始就讀 `feedback-NNN.md`。

3. **無限迴圈**：一定要設定 `GAN_MAX_ITERATIONS`。如果 generator 連續 3 輪迭代都無法突破某個分數的高原，就停下來，標記給人類 review。

4. **Evaluator 只做表面測試**：evaluator 必須用 Playwright 跟執行中的 app **互動**，不能只截圖。要點按鈕、填表單、測試錯誤狀態。

5. **Evaluator 稱讚自己提的修正**：絕對不要讓 evaluator 提出修正方案之後，又去評估那些修正。evaluator 只負責批評，修正是 generator 的事。

6. **Context 耗盡**：長時間的 session 要用 Claude Agent SDK 的自動 compaction，或是在主要階段之間重設 context。

## Results: What to Expect

根據 Anthropic 公開的結果：

| Metric | Solo Agent | GAN Harness | Improvement |
|--------|-----------|-------------|-------------|
| Time | 20 分鐘 | 4-6 小時 | 久 12-18 倍 |
| Cost | $9 | $125-200 | 貴 14-22 倍 |
| Quality | 勉強能用 | 可上 production | 質變 |
| Core features | 壞掉 | 全部能用 | N/A |
| Design | 千篇一律的 AI slop | 有辨識度、精緻 | N/A |

**取捨很明確：** 花大約 20 倍的時間和成本，換來產出品質的質變。適合品質很重要的專案。

## References

- [Anthropic: Harness Design for Long-Running Apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)：原始論文，作者是 Prithvi Rajasekaran
- [Epsilla: The GAN-Style Agent Loop](https://www.epsilla.com/blogs/anthropic-harness-engineering-multi-agent-gan-architecture)：架構解構
- [Martin Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)：更廣的業界脈絡
- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)：OpenAI 的平行研究
