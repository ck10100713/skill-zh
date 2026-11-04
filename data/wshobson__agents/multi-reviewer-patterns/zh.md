---
name: multi-reviewer-patterns
description: 協調跨多個品質面向的平行 code review，包含發現的去重、嚴重度校準與彙整報告。在組織多 reviewer 的 code review、校準發現的嚴重度或彙整 review 結果時使用。
version: 1.0.2
---

# Multi-Reviewer Patterns

協調跨多個品質面向的平行 code review、替發現去重、校準嚴重度，並產出彙整報告的模式。

## When to Use This Skill

- 組織多面向的 code review
- 決定要指派哪些 review 面向
- 替多位 reviewer 的發現去重
- 一致地校準嚴重度評級
- 產出彙整的 review 報告

## Review Dimension Allocation

### Available Dimensions

| Dimension         | Focus                                   | When to Include                             |
| ----------------- | --------------------------------------- | ------------------------------------------- |
| **Security**      | 漏洞、驗證授權、輸入驗證 | 只要程式碼處理使用者輸入或驗證授權就一定要加 |
| **Performance**   | 查詢效率、記憶體、快取       | 變更資料存取或熱點路徑時      |
| **Architecture**  | SOLID、耦合、模式               | 結構性變更或新模組       |
| **Testing**       | 覆蓋率、品質、邊界案例           | 新增功能時               |
| **Accessibility** | WCAG、ARIA、鍵盤導覽                | UI/前端變更             |

### Recommended Combinations

| Scenario               | Dimensions                                   |
| ---------------------- | -------------------------------------------- |
| API endpoint changes   | Security, Performance, Architecture          |
| Frontend component     | Architecture, Testing, Accessibility         |
| Database migration     | Performance, Architecture                    |
| Authentication changes | Security, Testing                            |
| Full feature review    | Security, Performance, Architecture, Testing |

## Finding Deduplication

當多位 reviewer 在同一個位置回報問題時：

### Merge Rules

1. **同一個 file:line、同一個問題**：合併成一個 finding，並標示所有 reviewer 的貢獻
2. **同一個 file:line、不同問題**：保持為獨立的 finding
3. **同一個問題、不同位置**：保持獨立，但互相交叉參照
4. **嚴重度衝突**：採用較高的嚴重度
5. **建議衝突**：兩個都保留，並標明各自是哪位 reviewer 提的

### Deduplication Process

```
For each finding in all reviewer reports:
  1. Check if another finding references the same file:line
  2. If yes, check if they describe the same issue
  3. If same issue: merge, keeping the more detailed description
  4. If different issue: keep both, tag as "co-located"
  5. Use highest severity among merged findings
```

## Severity Calibration

### Severity Criteria

| Severity     | Impact                                        | Likelihood             | Examples                                     |
| ------------ | --------------------------------------------- | ---------------------- | -------------------------------------------- |
| **Critical** | 資料遺失、資安事件、完全失效  | 確定或極可能 | SQL injection、驗證繞過、資料損毀  |
| **High**     | 對功能有重大影響、效能下降 | 可能                 | 記憶體洩漏、缺少驗證、流程壞掉 |
| **Medium**   | 部分影響、有替代做法             | 有機會                | N+1 查詢、漏掉邊界案例、錯誤訊息不清楚  |
| **Low**      | 影響極小、屬於外觀問題                      | 不太可能               | 風格問題、小幅優化、命名      |

### Calibration Rules

- 外部使用者可利用的安全漏洞：一律是 Critical 或 High
- 熱點路徑上的效能問題：至少是 Medium
- 關鍵路徑缺少測試：至少是 Medium
- 核心功能的無障礙違規：至少是 Medium
- 對功能沒有影響的程式碼風格問題：Low

## Consolidated Report Template

```markdown
## Code Review Report

**Target**: {files/PR/directory}
**Reviewers**: {dimension-1}, {dimension-2}, {dimension-3}
**Date**: {date}
**Files Reviewed**: {count}

### Critical Findings ({count})

#### [CR-001] {Title}

**Location**: `{file}:{line}`
**Dimension**: {Security/Performance/etc.}
**Description**: {what was found}
**Impact**: {what could happen}
**Fix**: {recommended remediation}

### High Findings ({count})

...

### Medium Findings ({count})

...

### Low Findings ({count})

...

### Summary

| Dimension    | Critical | High  | Medium | Low   | Total  |
| ------------ | -------- | ----- | ------ | ----- | ------ |
| Security     | 1        | 2     | 3      | 0     | 6      |
| Performance  | 0        | 1     | 4      | 2     | 7      |
| Architecture | 0        | 0     | 2      | 3     | 5      |
| **Total**    | **1**    | **3** | **9**  | **5** | **18** |

### Recommendation

{Overall assessment and prioritized action items}
```
