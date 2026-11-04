---
name: postmortem-writing
description: 撰寫有效的 blameless postmortem，包含根因分析、時間軸與行動項目。在進行事件檢討、撰寫 postmortem 文件或改善事件應變流程時使用。
---

# Postmortem Writing

撰寫有效的 blameless postmortem 的完整指南，用來推動組織學習並防止事件再次發生。

## When to Use This Skill

- 進行事後事件檢討
- 撰寫 postmortem 文件
- 主持 blameless postmortem 會議
- 找出根因與促成因素
- 建立可執行的後續項目
- 建立組織的學習文化

## Core Concepts

### 1. Blameless Culture

| Blame-Focused            | Blameless                         |
| ------------------------ | --------------------------------- |
| 「這是誰造成的？」       | 「是什麼條件讓這件事會發生？」   |
| 「有人犯了錯」 | 「系統允許了這個錯誤」 |
| 懲罰個人       | 改善系統                   |
| 隱藏資訊         | 分享學到的事                   |
| 不敢發言      | 心理安全感              |

### 2. Postmortem Triggers

- SEV1 或 SEV2 事件
- 影響客戶、超過 15 分鐘的停機
- 資料遺失或資安事件
- 差點釀成嚴重後果的 near-miss
- 全新的失效模式
- 需要非常規介入的事件

## Quick Start

### Postmortem Timeline

```
Day 0: Incident occurs
Day 1-2: Draft postmortem document
Day 3-5: Postmortem meeting
Day 5-7: Finalize document, create tickets
Week 2+: Action item completion
Quarterly: Review patterns across incidents
```

## Templates and detailed worked examples

完整的範本庫與詳細的範例放在 `references/details.md`。需要具體範本時，再去讀那個檔案。

### Template 2: 5 Whys Analysis

```markdown
# 5 Whys Analysis: [Incident]

## Problem Statement

Payment service experienced 47-minute outage due to database connection exhaustion.

## Analysis

### Why #1: Why did the service fail?

**Answer**: Database connections were exhausted, causing all new requests to fail.

**Evidence**: Metrics showed connection count at 100/100 (max), with 500+ pending requests.

---

### Why #2: Why were database connections exhausted?

**Answer**: Each incoming request opened a new database connection instead of using the connection pool.

**Evidence**: Code diff shows direct `DriverManager.getConnection()` instead of pooled `DataSource`.

---

### Why #3: Why did the code bypass the connection pool?

**Answer**: A developer refactored the repository class and inadvertently changed the connection acquisition method.

**Evidence**: PR #1234 shows the change, made while fixing a different bug.

---

### Why #4: Why wasn't this caught in code review?

**Answer**: The reviewer focused on the functional change (the bug fix) and didn't notice the infrastructure change.

**Evidence**: Review comments only discuss business logic.

---

### Why #5: Why isn't there a safety net for this type of change?

**Answer**: We lack automated tests that verify connection pool behavior and lack documentation about our connection patterns.

**Evidence**: Test suite has no tests for connection handling; wiki has no article on database connections.

## Root Causes Identified

1. **Primary**: Missing automated tests for infrastructure behavior
2. **Secondary**: Insufficient documentation of architectural patterns
3. **Tertiary**: Code review checklist doesn't include infrastructure considerations

## Systemic Improvements

| Root Cause    | Improvement                       | Type       |
| ------------- | --------------------------------- | ---------- |
| Missing tests | Add infrastructure behavior tests | Prevention |
| Missing docs  | Document connection patterns      | Prevention |
| Review gaps   | Update review checklist           | Detection  |
| No canary     | Implement canary deployments      | Mitigation |
```

### Template 3: Quick Postmortem (Minor Incidents)

```markdown
# Quick Postmortem: [Brief Title]

**Date**: 2024-01-15 | **Duration**: 12 min | **Severity**: SEV3

## What Happened

API latency spiked to 5s due to cache miss storm after cache flush.

## Timeline

- 10:00 - Cache flush initiated for config update
- 10:02 - Latency alerts fire
- 10:05 - Identified as cache miss storm
- 10:08 - Enabled cache warming
- 10:12 - Latency normalized

## Root Cause

Full cache flush for minor config update caused thundering herd.

## Fix

- Immediate: Enabled cache warming
- Long-term: Implement partial cache invalidation (ENG-999)

## Lessons

Don't full-flush cache in production; use targeted invalidation.
```

## Facilitation Guide

### Running a Postmortem Meeting

```markdown
## Meeting Structure (60 minutes)

### 1. Opening (5 min)

- Remind everyone of blameless culture
- "We're here to learn, not to blame"
- Review meeting norms

### 2. Timeline Review (15 min)

- Walk through events chronologically
- Ask clarifying questions
- Identify gaps in timeline

### 3. Analysis Discussion (20 min)

- What failed?
- Why did it fail?
- What conditions allowed this?
- What would have prevented it?

### 4. Action Items (15 min)

- Brainstorm improvements
- Prioritize by impact and effort
- Assign owners and due dates

### 5. Closing (5 min)

- Summarize key learnings
- Confirm action item owners
- Schedule follow-up if needed

## Facilitation Tips

- Keep discussion on track
- Redirect blame to systems
- Encourage quiet participants
- Document dissenting views
- Time-box tangents
```

## Anti-Patterns to Avoid

| Anti-Pattern            | Problem                    | Better Approach                 |
| ----------------------- | -------------------------- | ------------------------------- |
| **Blame game**          | 讓學習停擺        | 專注在系統                |
| **Shallow analysis**    | 無法防止再次發生 | 問五次「為什麼」               |
| **No action items**     | 浪費時間              | 一定要有具體的下一步 |
| **Unrealistic actions** | 永遠做不完            | 把範圍縮到做得到的任務       |
| **No follow-up**        | 行動項目被遺忘          | 在工單系統裡追蹤       |

## Best Practices

### Do's

- **立刻開始** - 記憶消退得很快
- **要具體** - 精確的時間、精確的錯誤
- **附上圖表** - 視覺化的證據
- **指定負責人** - 不要有沒人認領的行動項目
- **廣泛分享** - 組織學習

### Don'ts

- **不要點名羞辱** - 絕對不要
- **不要跳過小事件** - 它們會揭露模式
- **不要把它寫成究責文件** - 那會扼殺學習
- **不要製造瑣事** - 行動項目要有意義
- **不要跳過後續追蹤** - 驗證行動項目有完成
