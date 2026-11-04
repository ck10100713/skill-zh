---
name: design-system
description: 稽核、記錄或擴充你的 design system。檢查元件之間命名不一致或寫死的數值、為元件的 variant、狀態和無障礙備註寫文件，或設計一個符合現有系統的新 pattern 時使用。
argument-hint: "[audit | document | extend] <component or system>"
---

# /design-system

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

管理你的 design system：稽核一致性、為元件寫文件，或設計新的 pattern。

## 用法

```
/design-system audit                    # Full system audit
/design-system document [component]     # Document a component
/design-system extend [pattern]         # Design a new component or pattern
```

## Design System 的組成

### Design Tokens
定義視覺語言的原子值：
- 顏色（品牌、語意、中性）
- 字體排印（字級、字重、行高）
- 間距（級距、元件 padding）
- 邊框（圓角、寬度）
- 陰影（elevation 層級）
- 動態（時長、easing）

### 元件
可重複使用的 UI 元素，並且定義了：
- Variant（primary、secondary、ghost）
- 狀態（default、hover、active、disabled、loading、error）
- 尺寸（sm、md、lg）
- 行為（互動、動畫）
- 無障礙（ARIA、鍵盤）

### Pattern
結合多個元件的常見 UI 解法：
- 表單（輸入群組、驗證、送出）
- 導覽（側邊欄、分頁籤、麵包屑）
- 資料呈現（表格、卡片、清單）
- 回饋（toast、modal、行內訊息）

## 原則

1. **一致性勝過創意**：系統存在的目的，就是讓團隊不用重新發明輪子
2. **在限制內保持彈性**：元件應該能組合，不該僵硬
3. **每件事都要寫文件**：沒有文件的東西，就等於不存在
4. **做版本管理和遷移**：破壞相容性的變更需要遷移路徑

## 輸出：Audit

```markdown
## Design System Audit

### Summary
**Components reviewed:** [X] | **Issues found:** [X] | **Score:** [X/100]

### Naming Consistency
| Issue | Components | Recommendation |
|-------|------------|----------------|
| [Inconsistent naming] | [List] | [Standard to adopt] |

### Token Coverage
| Category | Defined | Hardcoded Values Found |
|----------|---------|----------------------|
| Colors | [X] | [X] instances of hardcoded hex |
| Spacing | [X] | [X] instances of arbitrary values |
| Typography | [X] | [X] instances of custom fonts/sizes |

### Component Completeness
| Component | States | Variants | Docs | Score |
|-----------|--------|----------|------|-------|
| Button | ✅ | ✅ | ⚠️ | 8/10 |
| Input | ✅ | ⚠️ | ❌ | 5/10 |

### Priority Actions
1. [Most impactful improvement]
2. [Second priority]
3. [Third priority]
```

## 輸出：Document

```markdown
## Component: [Name]

### Description
[What this component is and when to use it]

### Variants
| Variant | Use When |
|---------|----------|
| [Primary] | [Main actions] |
| [Secondary] | [Supporting actions] |

### Props / Properties
| Property | Type | Default | Description |
|----------|------|---------|-------------|
| [prop] | [type] | [default] | [description] |

### States
| State | Visual | Behavior |
|-------|--------|----------|
| Default | [description] | — |
| Hover | [description] | [interaction] |
| Active | [description] | [interaction] |
| Disabled | [description] | Non-interactive |
| Loading | [description] | [animation] |

### Accessibility
- **Role**: [ARIA role]
- **Keyboard**: [Tab, Enter, Escape behavior]
- **Screen reader**: [Announced as...]

### Do's and Don'ts
| ✅ Do | ❌ Don't |
|------|---------|
| [Best practice] | [Anti-pattern] |

### Code Example
[Framework-appropriate code snippet]
```

## 輸出：Extend

```markdown
## New Component: [Name]

### Problem
[What user need or gap this component addresses]

### Existing Patterns
| Related Component | Similarity | Why It's Not Enough |
|-------------------|-----------|---------------------|
| [Component] | [What's shared] | [What's missing] |

### Proposed Design

#### API / Props
| Property | Type | Default | Description |
|----------|------|---------|-------------|
| [prop] | [type] | [default] | [description] |

#### Variants
| Variant | Use When | Visual |
|---------|----------|--------|
| [Variant] | [Scenario] | [Description] |

#### States
| State | Behavior | Notes |
|-------|----------|-------|
| Default | [Description] | — |
| Hover | [Description] | [Interaction] |
| Disabled | [Description] | Non-interactive |
| Loading | [Description] | [Animation] |

#### Tokens Used
- Colors: [Which tokens]
- Spacing: [Which tokens]
- Typography: [Which tokens]

### Accessibility
- **Role**: [ARIA role]
- **Keyboard**: [Expected interactions]
- **Screen reader**: [Announced as...]

### Open Questions
- [Decision that needs design review]
- [Edge case to resolve]
```

## 如果有連接 connector

如果有連接 **~~design tool**：
- 直接在 Figma 稽核元件：檢查命名、variant 和 token 的使用
- 拉出元件屬性和圖層結構來寫文件

如果有連接 **~~knowledge base**：
- 搜尋現有的元件文件和使用指南
- 把更新後的文件發布到你的 wiki

## 小提醒

1. **先從稽核開始**：先知道自己在哪，再決定要往哪走。
2. **邊做邊寫文件**：設計元件的同時寫文件最輕鬆。
3. **覆蓋率比完美重要**：80% 的元件都有文件，勝過只把 10 個元件做到 100%。
