---
name: santa-method
description: "多 agent 對抗式驗證：兩位獨立的 reviewer 用同一份評分標準，兩人都通過產出才能發布，並有修正後重新 review 的收斂迴圈，以及升級給人處理的次數上限。在發布、正式環境 deploy、合規或品牌敏感內容，或容易產生幻覺的說法出貨前把關時使用。"
metadata:
  origin: "Ronald Skelton - Founder, RapportScore.ai"
---

# Santa Method

多 agent 對抗式驗證框架。列好清單，檢查兩次。如果是淘氣名單，就修到變乖為止。

核心洞察：單一 agent 檢查自己的產出，會帶著產出當初那些相同的偏見、知識缺口和系統性錯誤。兩位沒有共用 context 的獨立 reviewer，可以打破這種失效模式。

## 何時啟用

在這些情況使用這個 skill：
- 產出會被發布、deploy，或由終端使用者使用
- 必須落實合規、法規或品牌限制
- 程式碼沒經過人工 review 就上正式環境
- 內容正確性很重要（技術文件、教材、面向客戶的文案）
- 大規模批次產生，抽查會漏掉系統性模式
- 幻覺風險偏高（說法、統計數字、API 參照、法律用語）

**不要**用在內部草稿、探索性研究，或可以用確定性方式驗證的任務（那些用 build/test/lint pipeline）。

## 架構

```
┌─────────────┐
│  GENERATOR   │  Phase 1: Make a List
│  (Agent A)   │  Produce the deliverable
└──────┬───────┘
       │ output
       ▼
┌──────────────────────────────┐
│     DUAL INDEPENDENT REVIEW   │  Phase 2: Check It Twice
│                                │
│  ┌───────────┐ ┌───────────┐  │  Two agents, same rubric,
│  │ Reviewer B │ │ Reviewer C │  │  no shared context
│  └─────┬─────┘ └─────┬─────┘  │
│        │              │        │
└────────┼──────────────┼────────┘
         │              │
         ▼              ▼
┌──────────────────────────────┐
│        VERDICT GATE           │  Phase 3: Naughty or Nice
│                                │
│  B passes AND C passes → NICE  │  Both must pass.
│  Otherwise → NAUGHTY           │  No exceptions.
└──────┬──────────────┬─────────┘
       │              │
    NICE           NAUGHTY
       │              │
       ▼              ▼
   [ SHIP ]    ┌─────────────┐
               │  FIX CYCLE   │  Phase 4: Fix Until Nice
               │              │
               │ iteration++  │  Collect all flags.
               │ if i > MAX:  │  Fix all issues.
               │   escalate   │  Re-run both reviewers.
               │ else:        │  Loop until convergence.
               │   goto Ph.2  │
               └──────────────┘
```

## 各階段細節

### 階段 1：列好清單（Generate）

執行主要任務。你平常的產生流程不用改。Santa Method 是產生之後的驗證層，不是產生策略。

```python
# The generator runs as normal
output = generate(task_spec)
```

### 階段 2：檢查兩次（獨立雙重 Review）

並行啟動兩個 review agent。關鍵的不變條件：

1. **Context 隔離**：兩位 reviewer 都看不到對方的評估
2. **相同的評分標準**：兩人拿到一樣的評估準則
3. **相同的輸入**：兩人都拿到原始規格**和**產生的產出
4. **結構化輸出**：各自回傳有型別的判定，不是散文

```python
REVIEWER_PROMPT = """
You are an independent quality reviewer. You have NOT seen any other review of this output.

## Task Specification
{task_spec}

## Output Under Review
{output}

## Evaluation Rubric
{rubric}

## Instructions
Evaluate the output against EACH rubric criterion. For each:
- PASS: criterion fully met, no issues
- FAIL: specific issue found (cite the exact problem)

Return your assessment as structured JSON:
{
  "verdict": "PASS" | "FAIL",
  "checks": [
    {"criterion": "...", "result": "PASS|FAIL", "detail": "..."}
  ],
  "critical_issues": ["..."],   // blockers that must be fixed
  "suggestions": ["..."]         // non-blocking improvements
}

Be rigorous. Your job is to find problems, not to approve.
"""
```

```python
# Spawn reviewers in parallel (Claude Code subagents)
review_b = Agent(prompt=REVIEWER_PROMPT.format(...), description="Santa Reviewer B")
review_c = Agent(prompt=REVIEWER_PROMPT.format(...), description="Santa Reviewer C")

# Both run concurrently — neither sees the other
```

### 評分標準設計

評分標準是最重要的輸入。模糊的標準只會得到模糊的 review。每一條準則都必須有客觀的通過/失敗條件。

| 準則 | 通過條件 | 失敗訊號 |
|-----------|---------------|----------------|
| 事實正確 | 所有說法都能對照來源資料或常識查證 | 捏造的統計數字、錯誤的版本號、不存在的 API |
| 沒有幻覺 | 沒有捏造的實體、引言、URL 或參照 | 連到不存在的頁面、引言標了出處卻查無來源 |
| 完整性 | 規格裡的每個需求都有處理 | 缺少段落、跳過邊緣案例、涵蓋不完整 |
| 合規 | 通過所有專案特定的限制 | 用了禁用詞、語氣違規、不符法規 |
| 內部一致 | 產出內部沒有矛盾 | A 段說 X，B 段說不是 X |
| 技術正確 | 程式碼能編譯/執行，演算法合理 | 語法錯誤、邏輯 bug、錯誤的複雜度說法 |

#### 各領域的評分標準擴充

**內容/行銷：**
- 符合品牌語氣
- 符合 SEO 要求（關鍵字密度、meta 標籤、結構）
- 沒有誤用競爭對手商標
- 有 CTA 而且連結正確

**程式碼：**
- 型別安全（沒有 `any` 外洩、null 處理得當）
- 錯誤處理涵蓋度
- 安全性（程式碼裡沒有 secret、有輸入驗證、有防注入）
- 新路徑有測試覆蓋

**合規敏感（受監管、法律、金融）：**
- 沒有保證結果或無根據的說法
- 有必要的免責聲明
- 只用核准的術語
- 用語符合所在司法管轄區

### 階段 3：淘氣還是乖（判定關卡）

```python
def santa_verdict(review_b, review_c):
    """Both reviewers must pass. No partial credit."""
    if review_b.verdict == "PASS" and review_c.verdict == "PASS":
        return "NICE"  # Ship it

    # Merge flags from both reviewers, deduplicate
    all_issues = dedupe(review_b.critical_issues + review_c.critical_issues)
    all_suggestions = dedupe(review_b.suggestions + review_c.suggestions)

    return "NAUGHTY", all_issues, all_suggestions
```

為什麼兩人都得通過：只要有一位 reviewer 抓到問題，那個問題就是真的。另一位 reviewer 的盲點，正是 Santa Method 要消滅的失效模式。

### 階段 4：修到變乖（收斂迴圈）

```python
MAX_ITERATIONS = 3

for iteration in range(MAX_ITERATIONS):
    verdict, issues, suggestions = santa_verdict(review_b, review_c)

    if verdict == "NICE":
        log_santa_result(output, iteration, "passed")
        return ship(output)

    # Fix all critical issues (suggestions are optional)
    output = fix_agent.execute(
        output=output,
        issues=issues,
        instruction="Fix ONLY the flagged issues. Do not refactor or add unrequested changes."
    )

    # Re-run BOTH reviewers on fixed output (fresh agents, no memory of previous round)
    review_b = Agent(prompt=REVIEWER_PROMPT.format(output=output, ...))
    review_c = Agent(prompt=REVIEWER_PROMPT.format(output=output, ...))

# Exhausted iterations — escalate
log_santa_result(output, MAX_ITERATIONS, "escalated")
escalate_to_human(output, issues)
```

重點：每一輪 review 都要用**全新的 agent**。Reviewer 不能帶著前幾輪的記憶，因為先前的 context 會造成錨定偏誤。

## 實作模式

### 模式 A：Claude Code Subagent（建議）

Subagent 提供真正的 context 隔離。每位 reviewer 都是獨立的 process，沒有共用狀態。

```bash
# In a Claude Code session, use the Agent tool to spawn reviewers
# Both agents run in parallel for speed
```

```python
# Pseudocode for Agent tool invocation
reviewer_b = Agent(
    description="Santa Review B",
    prompt=f"Review this output for quality...\n\nRUBRIC:\n{rubric}\n\nOUTPUT:\n{output}"
)
reviewer_c = Agent(
    description="Santa Review C",
    prompt=f"Review this output for quality...\n\nRUBRIC:\n{rubric}\n\nOUTPUT:\n{output}"
)
```

### 模式 B：依序內聯（備案）

沒有 subagent 可用時，用明確的 context 重置來模擬隔離：

1. 產生產出
2. 新 context：「You are Reviewer 1. Evaluate ONLY against this rubric. Find problems.」
3. 逐字記錄發現
4. 完全清掉 context
5. 新 context：「You are Reviewer 2. Evaluate ONLY against this rubric. Find problems.」
6. 比較兩份 review，修正，重複

Subagent 模式完全勝出，內聯模擬有 reviewer 之間 context 外洩的風險。

### 模式 C：批次抽樣

大批次（100 筆以上）每一筆都跑完整的 Santa，成本太高。改用分層抽樣：

1. 對隨機樣本跑 Santa（批次的 10% 到 15%，至少 5 筆）
2. 依類型把失敗分類（幻覺、合規、完整性等）
3. 如果出現系統性模式，對整個批次套用針對性的修正
4. 重新抽樣，重新驗證修正後的批次
5. 持續到乾淨的樣本通過為止

```python
import random

def santa_batch(items, rubric, sample_rate=0.15):
    sample = random.sample(items, max(5, int(len(items) * sample_rate)))

    for item in sample:
        result = santa_full(item, rubric)
        if result.verdict == "NAUGHTY":
            pattern = classify_failure(result.issues)
            items = batch_fix(items, pattern)  # Fix all items matching pattern
            return santa_batch(items, rubric)   # Re-sample

    return items  # Clean sample → ship batch
```

## 失效模式與對策

| 失效模式 | 症狀 | 對策 |
|-------------|---------|------------|
| 無限迴圈 | 修正之後 reviewer 還是一直找到新問題 | 設定最大迭代次數（3）。升級處理。 |
| 橡皮圖章 | 兩位 reviewer 什麼都放行 | 對抗式 prompt：「Your job is to find problems, not approve.」 |
| 主觀漂移 | Reviewer 標記的是風格偏好，不是錯誤 | 評分標準要嚴格，只用客觀的通過/失敗準則 |
| 修正造成退步 | 修掉問題 A 卻引入問題 B | 每一輪都用全新的 reviewer，才抓得到退步 |
| Reviewer 一致性偏誤 | 兩位 reviewer 漏掉同一件事 | 靠獨立性降低，但無法消除。關鍵產出就加第三位 reviewer 或人工抽查。 |
| 成本爆炸 | 大型產出的迭代次數太多 | 用批次抽樣模式。每個驗證週期設預算上限。 |

## 與其他 skill 的整合

| Skill | 關係 |
|-------|-------------|
| Verification Loop | 用在確定性檢查（build、lint、test）。Santa 用在語意檢查（正確性、幻覺）。先跑 verification-loop，再跑 Santa。 |
| Eval Harness | Santa Method 的結果餵給 eval 指標。追蹤多次 Santa 執行的 pass@k，衡量產生器品質隨時間的變化。 |
| Continuous Learning v2 | Santa 的發現變成 instinct。同一條準則反覆失敗，就學成避開該模式的行為。 |
| Strategic Compact | 在 compact 之前跑 Santa。不要在驗證進行到一半時丟掉 review 的 context。 |

## 指標

追蹤這些指標，衡量 Santa Method 的成效：

- **首輪通過率**：第 1 輪就通過 Santa 的產出比例（目標：>70%）
- **平均收斂迭代數**：平均要幾輪才到 NICE（目標：<1.5）
- **問題分類**：失敗類型的分布（幻覺 vs. 完整性 vs. 合規）
- **Reviewer 一致度**：兩位 reviewer 都標記的問題 vs. 只有一位標記的比例（一致度低代表評分標準要收緊）
- **漏網率**：出貨後才發現、本該被 Santa 抓到的問題（目標：0）

## 成本分析

每個驗證週期，Santa Method 的 token 成本大約是單純產生的 2 到 3 倍。對大多數高風險的產出來說，這很划算：

```
Cost of Santa = (generation tokens) + 2×(review tokens per round) × (avg rounds)
Cost of NOT Santa = (reputation damage) + (correction effort) + (trust erosion)
```

批次作業用抽樣模式，成本可降到完整驗證的 15% 到 20%，同時還能抓到 90% 以上的系統性問題。
