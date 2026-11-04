---
name: architecture-decision-records
description: 依技術決策文件化的最佳實務，撰寫並維護 Architecture Decision Record（ADR）。在記錄重大的技術決策、回顧過去的架構選擇，或建立決策流程時使用。
---

# Architecture Decision Records

建立、維護和管理 Architecture Decision Record（ADR）的完整模式，用來記下重大技術決策背後的脈絡和理由。

## 何時使用這個 Skill

- 做出重大的架構決策
- 記錄技術選型
- 記下設計上的取捨
- 帶新進團隊成員上手
- 回顧歷史決策
- 建立決策流程

## 核心概念

### 1. 什麼是 ADR？

Architecture Decision Record 記錄的是：

- **Context（脈絡）**：為什麼我們需要做這個決定
- **Decision（決策）**：我們決定了什麼
- **Consequences（後果）**：因此會發生什麼

### 2. 何時該寫 ADR

| 該寫 ADR                  | 不用寫 ADR               |
| -------------------------- | ---------------------- |
| 採用新框架     | 小版本升級 |
| 資料庫技術選擇 | 修 bug              |
| API 設計模式        | 實作細節 |
| 安全架構      | 例行維護    |
| 整合模式       | 設定變更  |

### 3. ADR 的生命週期

```
Proposed → Accepted → Deprecated → Superseded
              ↓
           Rejected
```

起草標準、輕量或 Y-statement 的 ADR 之前，先讀[決策範本](references/decision-templates.md)。

起草棄用 ADR 或 RFC 之前，先讀[棄用與 RFC 範本](references/deprecation-rfc-templates.md)。

## ADR 管理

### 目錄結構

```
docs/
├── adr/
│   ├── README.md           # Index and guidelines
│   ├── template.md         # Team's ADR template
│   ├── 0001-use-postgresql.md
│   ├── 0002-caching-strategy.md
│   ├── 0003-mongodb-user-profiles.md  # [DEPRECATED]
│   └── 0020-deprecate-mongodb.md      # Supersedes 0003
```

### ADR 索引（README.md）

```markdown
# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for [Project Name].

## Index

| ADR                                   | Title                              | Status     | Date       |
| ------------------------------------- | ---------------------------------- | ---------- | ---------- |
| [0001](0001-use-postgresql.md)        | Use PostgreSQL as Primary Database | Accepted   | 2024-01-10 |
| [0002](0002-caching-strategy.md)      | Caching Strategy with Redis        | Accepted   | 2024-01-12 |
| [0003](0003-mongodb-user-profiles.md) | MongoDB for User Profiles          | Deprecated | 2023-06-15 |
| [0020](0020-deprecate-mongodb.md)     | Deprecate MongoDB                  | Accepted   | 2024-01-15 |

## Creating a New ADR

1. Copy `template.md` to `NNNN-title-with-dashes.md`
2. Fill in the template
3. Submit PR for review
4. Update this index after approval

## ADR Status

- **Proposed**: Under discussion
- **Accepted**: Decision made, implementing
- **Deprecated**: No longer relevant
- **Superseded**: Replaced by another ADR
- **Rejected**: Considered but not adopted
```

### 自動化（adr-tools）

```bash
# Install adr-tools
brew install adr-tools

# Initialize ADR directory
adr init docs/adr

# Create new ADR
adr new "Use PostgreSQL as Primary Database"

# Supersede an ADR
adr new -s 3 "Deprecate MongoDB in Favor of PostgreSQL"

# Generate table of contents (to a separate file, so the hand-written
# index and guidelines in README.md are not overwritten)
adr generate toc > docs/adr/toc.md

# Link related ADRs
adr link 2 "Complements" 1 "Is complemented by"
```

## 審查流程

```markdown
## ADR Review Checklist

### Before Submission

- [ ] Context clearly explains the problem
- [ ] All viable options considered
- [ ] Pros/cons balanced and honest
- [ ] Consequences (positive and negative) documented
- [ ] Related ADRs linked

### During Review

- [ ] At least 2 senior engineers reviewed
- [ ] Affected teams consulted
- [ ] Security implications considered
- [ ] Cost implications documented
- [ ] Reversibility assessed

### After Acceptance

- [ ] ADR index updated
- [ ] Team notified
- [ ] Implementation tickets created
- [ ] Related documentation updated
```

## 最佳實務

### 該做的

- **早點寫 ADR** - 在開始實作之前
- **保持簡短** - 最多 1 到 2 頁
- **誠實面對取捨** - 要寫出真正的缺點
- **連結相關的決策** - 建立決策圖
- **更新狀態** - 被取代時標成 deprecated

### 不該做的

- **不要改已經 accepted 的 ADR** - 寫新的去取代它
- **不要省略 context** - 未來的讀者需要背景
- **不要隱藏失敗** - 被否決的決策很有價值
- **不要含糊** - 具體的決策、具體的後果
- **不要忘了實作** - 有 ADR 卻沒有行動，是浪費
