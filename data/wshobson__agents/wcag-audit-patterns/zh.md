---
name: wcag-audit-patterns
description: 以自動化測試、人工驗證和修正指引，進行 WCAG 2.2 無障礙稽核。稽核網站無障礙性、修正 WCAG 違規，或實作無障礙設計模式時使用。
---

# WCAG Audit Patterns

依 WCAG 2.2 準則稽核網頁內容的完整指南，附可執行的修正策略。

## When to Use This Skill

- 進行無障礙稽核
- 修正 WCAG 違規
- 實作無障礙元件
- 為無障礙相關訴訟做準備
- 符合 ADA/Section 508 要求
- 取得 VPAT 合規

## Core Concepts

### 1. WCAG Conformance Levels

| Level   | Description            | Required For      |
| ------- | ---------------------- | ----------------- |
| **A**   | 最低限度的無障礙  | 法律底線    |
| **AA**  | 標準符合度   | 多數法規  |
| **AAA** | 加強版無障礙 | 特殊需求 |

### 2. POUR Principles

```
Perceivable:  Can users perceive the content?
Operable:     Can users operate the interface?
Understandable: Can users understand the content?
Robust:       Does it work with assistive tech?
```

### 3. Common Violations by Impact

```
Critical (Blockers):
├── Missing alt text for functional images
├── No keyboard access to interactive elements
├── Missing form labels
└── Auto-playing media without controls

Serious:
├── Insufficient color contrast
├── Missing skip links
├── Inaccessible custom widgets
└── Missing page titles

Moderate:
├── Missing language attribute
├── Unclear link text
├── Missing landmarks
└── Improper heading hierarchy
```

## Detailed patterns and worked examples

詳細的模式說明放在 `references/details.md`。上面的導覽層不夠用的時候，再去讀那個檔案。

## Best Practices

### Do's

- **Start early** - 從設計階段就考慮無障礙
- **Test with real users** - 身心障礙使用者的回饋最有價值
- **Automate what you can** - 30-50% 的問題可以自動偵測
- **Use semantic HTML** - 減少對 ARIA 的需求
- **Document patterns** - 建立無障礙的元件庫

### Don'ts

- **Don't rely only on automated testing** - 一定要有人工測試
- **Don't use ARIA as first solution** - 先用原生 HTML
- **Don't hide focus outlines** - 鍵盤使用者需要它們
- **Don't disable zoom** - 使用者需要能縮放
- **Don't use color alone** - 需要多重指示
