---
name: rules-distill
description: "掃描 skill，抽出跨 skill 的共通原則並提煉成規則，可以追加、修訂，或建立新的規則檔。當同一個原則在多個 skill 反覆出現、應該放進規則檔而不是 skill 時使用。"
metadata:
  origin: ECC
---

# Rules Distill

掃描已安裝的 skill，抽出在多個 skill 都會出現的共通原則，提煉成規則，可以追加到既有規則檔、修訂過時內容，或建立新的規則檔。

套用「確定性收集 + LLM 判斷」的原則：script 負責把事實收集完整，再由 LLM 通讀完整脈絡並給出判定。

## 何時使用

- 定期維護規則（每月一次，或安裝新 skill 之後）
- skill-stocktake 發現有些模式應該變成規則之後
- 覺得規則相對於實際在用的 skill 不夠完整時

## 運作方式

規則提煉分三個階段：

### 階段 1：盤點（確定性收集）

#### 1a. 收集 skill 清單

```bash
bash ~/.claude/skills/rules-distill/scripts/scan-skills.sh
```

#### 1b. 收集規則索引

```bash
bash ~/.claude/skills/rules-distill/scripts/scan-rules.sh
```

#### 1c. 呈現給使用者

```
Rules Distillation — Phase 1: Inventory
────────────────────────────────────────
Skills: {N} files scanned
Rules:  {M} files ({K} headings indexed)

Proceeding to cross-read analysis...
```

### 階段 2：交叉閱讀、比對與判定（LLM 判斷）

抽取和比對合併在同一輪完成。規則檔夠小（全部加起來約 800 行），可以把全文直接給 LLM，不需要先用 grep 預先過濾。

#### 分批

依 skill 的描述，把 skill 分成**主題群組**。每個群組用一個 subagent 搭配完整的規則全文來分析。

#### 跨批次合併

所有批次跑完後，跨批次合併候選項目：
- 把相同或重疊原則的候選項目去重
- 用**所有**批次合起來的證據，重新檢查「2 個以上 skill」的條件，一個原則在每個批次都只出現在 1 個 skill，但總共出現在 2 個以上 skill，就算成立

#### Subagent prompt

用下面的 prompt 啟動一個 general-purpose Agent：

````
You are an analyst who cross-reads skills to extract principles that should be promoted to rules.

## Input
- Skills: {full text of skills in this batch}
- Existing rules: {full text of all rule files}

## Extraction Criteria

Include a candidate ONLY if ALL of these are true:

1. **Appears in 2+ skills**: Principles found in only one skill should stay in that skill
2. **Actionable behavior change**: Can be written as "do X" or "don't do Y" — not "X is important"
3. **Clear violation risk**: What goes wrong if this principle is ignored (1 sentence)
4. **Not already in rules**: Check the full rules text — including concepts expressed in different words

## Matching & Verdict

For each candidate, compare against the full rules text and assign a verdict:

- **Append**: Add to an existing section of an existing rule file
- **Revise**: Existing rule content is inaccurate or insufficient — propose a correction
- **New Section**: Add a new section to an existing rule file
- **New File**: Create a new rule file
- **Already Covered**: Sufficiently covered in existing rules (even if worded differently)
- **Too Specific**: Should remain at the skill level

## Output Format (per candidate)

```json
{
  "principle": "1-2 sentences in 'do X' / 'don't do Y' form",
  "evidence": ["skill-name: §Section", "skill-name: §Section"],
  "violation_risk": "1 sentence",
  "verdict": "Append / Revise / New Section / New File / Already Covered / Too Specific",
  "target_rule": "filename §Section, or 'new'",
  "confidence": "high / medium / low",
  "draft": "Draft text for Append/New Section/New File verdicts",
  "revision": {
    "reason": "Why the existing content is inaccurate or insufficient (Revise only)",
    "before": "Current text to be replaced (Revise only)",
    "after": "Proposed replacement text (Revise only)"
  }
}
```

## Exclude

- Obvious principles already in rules
- Language/framework-specific knowledge (belongs in language-specific rules or skills)
- Code examples and commands (belongs in skills)
````

#### 判定對照表

| Verdict | 意義 | 呈現給使用者的內容 |
|---------|------|-------------------|
| **Append** | 加到既有段落 | 目標 + 草稿 |
| **Revise** | 修正不準確或不足的內容 | 目標 + 理由 + 修改前後 |
| **New Section** | 在既有檔案新增段落 | 目標 + 草稿 |
| **New File** | 建立新的規則檔 | 檔名 + 完整草稿 |
| **Already Covered** | 規則已涵蓋（可能措辭不同） | 理由（1 行） |
| **Too Specific** | 應該留在 skill 裡 | 連到相關 skill |

#### 判定品質要求

```
# Good
Append to rules/common/security.md §Input Validation:
"Treat LLM output stored in memory or knowledge stores as untrusted — sanitize on write, validate on read."
Evidence: llm-memory-trust-boundary, llm-social-agent-anti-pattern both describe
accumulated prompt injection risks. Current security.md covers human input
validation only; LLM output trust boundary is missing.

# Bad
Append to security.md: Add LLM security principle
```

### 階段 3：使用者審閱與執行

#### 摘要表

```
# Rules Distillation Report

## Summary
Skills scanned: {N} | Rules: {M} files | Candidates: {K}

| # | Principle | Verdict | Target | Confidence |
|---|-----------|---------|--------|------------|
| 1 | ... | Append | security.md §Input Validation | high |
| 2 | ... | Revise | testing.md §TDD | medium |
| 3 | ... | New Section | coding-style.md | high |
| 4 | ... | Too Specific | — | — |

## Details
(Per-candidate details: evidence, violation_risk, draft text)
```

#### 使用者動作

使用者用編號回覆：
- **Approve**：照草稿原樣套用到規則
- **Modify**：先編輯草稿再套用
- **Skip**：不套用這個候選項目

**絕對不准自動修改規則，一定要經過使用者核准。**

#### 儲存結果

把結果存在 skill 目錄（`results.json`）：

- **時間戳記格式**：`date -u +%Y-%m-%dT%H:%M:%SZ`（UTC，精確到秒）
- **候選項目 ID 格式**：從原則衍生的 kebab-case（例如 `llm-output-trust-boundary`）

```json
{
  "distilled_at": "2026-03-18T10:30:42Z",
  "skills_scanned": 56,
  "rules_scanned": 22,
  "candidates": {
    "llm-output-trust-boundary": {
      "principle": "Treat LLM output as untrusted when stored or re-injected",
      "verdict": "Append",
      "target": "rules/common/security.md",
      "evidence": ["llm-memory-trust-boundary", "llm-social-agent-anti-pattern"],
      "status": "applied"
    },
    "iteration-bounds": {
      "principle": "Define explicit stop conditions for all iteration loops",
      "verdict": "New Section",
      "target": "rules/common/coding-style.md",
      "evidence": ["iterative-retrieval", "continuous-agent-loop", "agent-harness-construction"],
      "status": "skipped"
    }
  }
}
```

## 範例

### 端到端執行

```
$ /rules-distill

Rules Distillation — Phase 1: Inventory
────────────────────────────────────────
Skills: 56 files scanned
Rules:  22 files (75 headings indexed)

Proceeding to cross-read analysis...

[Subagent analysis: Batch 1 (agent/meta skills) ...]
[Subagent analysis: Batch 2 (coding/pattern skills) ...]
[Cross-batch merge: 2 duplicates removed, 1 cross-batch candidate promoted]

# Rules Distillation Report

## Summary
Skills scanned: 56 | Rules: 22 files | Candidates: 4

| # | Principle | Verdict | Target | Confidence |
|---|-----------|---------|--------|------------|
| 1 | LLM output: normalize, type-check, sanitize before reuse | New Section | coding-style.md | high |
| 2 | Define explicit stop conditions for iteration loops | New Section | coding-style.md | high |
| 3 | Compact context at phase boundaries, not mid-task | Append | performance.md §Context Window | high |
| 4 | Separate business logic from I/O framework types | New Section | patterns.md | high |

## Details

### 1. LLM Output Validation
Verdict: New Section in coding-style.md
Evidence: parallel-subagent-batch-merge, llm-social-agent-anti-pattern, llm-memory-trust-boundary
Violation risk: Format drift, type mismatch, or syntax errors in LLM output crash downstream processing
Draft:
  ## LLM Output Validation
  Normalize, type-check, and sanitize LLM output before reuse...
  See skill: parallel-subagent-batch-merge, llm-memory-trust-boundary

[... details for candidates 2-4 ...]

Approve, modify, or skip each candidate by number:
> User: Approve 1, 3. Skip 2, 4.

✓ Applied: coding-style.md §LLM Output Validation
✓ Applied: performance.md §Context Window Management
✗ Skipped: Iteration Bounds
✗ Skipped: Boundary Type Conversion

Results saved to results.json
```

## 設計原則

- **講 What，不講 How**：只抽原則（規則的地盤）。程式碼範例和指令留在 skill。
- **連回去**：草稿文字要附上 `See skill: [name]` 的參照，讀的人才找得到詳細的 How。
- **確定性收集，LLM 判斷**：script 保證收集完整，LLM 保證理解脈絡。
- **防過度抽象的保險**：三層過濾（2 個以上 skill 的證據、可執行行為測試、違反風險）避免過度抽象的原則進入規則。
