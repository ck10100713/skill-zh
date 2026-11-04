---
name: accessibility-review
description: 對設計稿或頁面做 WCAG 2.1 AA 無障礙稽核。用 "audit accessibility"、"check a11y"、"is this accessible?" 觸發，或在交付前審查設計稿的色彩對比、鍵盤操作、觸控目標大小或螢幕閱讀器行為時使用。
argument-hint: "<Figma URL, URL, or description>"
---

# /accessibility-review

> 如果看到不熟悉的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

稽核設計稿或頁面是否符合 WCAG 2.1 AA 無障礙規範。

## 用法

```
/accessibility-review $ARGUMENTS
```

Audit for accessibility: @$1

## WCAG 2.1 AA 速查

### 可感知（Perceivable）
- **1.1.1** 非文字內容要有替代文字（alt text）
- **1.3.1** 資訊與結構要以語意方式傳達
- **1.4.3** 對比度 >= 4.5:1（一般文字）、>= 3:1（大型文字）
- **1.4.11** 非文字對比 >= 3:1（UI 元件、圖形）

### 可操作（Operable）
- **2.1.1** 所有功能都能用鍵盤操作
- **2.4.3** 焦點順序合乎邏輯
- **2.4.7** 有看得見的焦點指示
- **2.5.5** 觸控目標 >= 44x44 CSS pixels

### 可理解（Understandable）
- **3.2.1** 取得焦點時行為可預期（不會有意外的變化）
- **3.3.1** 錯誤辨識（要描述錯誤）
- **3.3.2** 輸入欄位要有標籤或說明

### 穩健（Robust）
- **4.1.2** 所有 UI 元件都要有名稱、角色、值

## 常見問題

1. 色彩對比不足
2. 缺少表單標籤
3. 互動元素無法用鍵盤操作
4. 有意義的圖片缺少替代文字
5. Modal 內的焦點陷阱
6. 缺少 ARIA landmark
7. 自動播放的媒體沒有控制項
8. 有時間限制但沒有延長選項

## 測試方法

1. 自動化掃描（大約只能抓到 30% 的問題）
2. 純鍵盤操作
3. 螢幕閱讀器測試（VoiceOver、NVDA）
4. 驗證色彩對比
5. 放大到 200%，版面會壞掉嗎？

## 輸出

```markdown
## Accessibility Audit: [Design/Page Name]
**Standard:** WCAG 2.1 AA | **Date:** [Date]

### Summary
**Issues found:** [X] | **Critical:** [X] | **Major:** [X] | **Minor:** [X]

### Findings

#### Perceivable
| # | Issue | WCAG Criterion | Severity | Recommendation |
|---|-------|---------------|----------|----------------|
| 1 | [Issue] | [1.4.3 Contrast] | 🔴 Critical | [Fix] |

#### Operable
| # | Issue | WCAG Criterion | Severity | Recommendation |
|---|-------|---------------|----------|----------------|
| 1 | [Issue] | [2.1.1 Keyboard] | 🟡 Major | [Fix] |

#### Understandable
| # | Issue | WCAG Criterion | Severity | Recommendation |
|---|-------|---------------|----------|----------------|
| 1 | [Issue] | [3.3.2 Labels] | 🟢 Minor | [Fix] |

#### Robust
| # | Issue | WCAG Criterion | Severity | Recommendation |
|---|-------|---------------|----------|----------------|
| 1 | [Issue] | [4.1.2 Name, Role, Value] | 🟡 Major | [Fix] |

### Color Contrast Check
| Element | Foreground | Background | Ratio | Required | Pass? |
|---------|-----------|------------|-------|----------|-------|
| [Body text] | [color] | [color] | [X]:1 | 4.5:1 | ✅/❌ |

### Keyboard Navigation
| Element | Tab Order | Enter/Space | Escape | Arrow Keys |
|---------|-----------|-------------|--------|------------|
| [Element] | [Order] | [Behavior] | [Behavior] | [Behavior] |

### Screen Reader
| Element | Announced As | Issue |
|---------|-------------|-------|
| [Element] | [What SR says] | [Problem if any] |

### Priority Fixes
1. **[Critical fix]** — Affects [who] and blocks [what]
2. **[Major fix]** — Improves [what] for [who]
3. **[Minor fix]** — Nice to have
```

## 如果有連接器可用

如果有連接 **~~design tool**：
- 直接從 Figma 檢查色彩值、字體大小和觸控目標
- 在設計規格中檢查元件的 ARIA 角色和鍵盤行為

如果有連接 **~~project tracker**：
- 為每個無障礙發現建立工單，附上嚴重程度和 WCAG 準則
- 把發現連結到既有的無障礙修復 epic

## 小技巧

1. **先從對比和鍵盤下手**：這兩項能抓到最常見、影響最大的問題。
2. **用真正的輔助技術測試**：我的稽核是很好的起點，但用 VoiceOver/NVDA 手動測試能抓到我抓不到的東西。
3. **依影響排優先順序**：先修會擋住使用者的問題，之後再潤飾。
