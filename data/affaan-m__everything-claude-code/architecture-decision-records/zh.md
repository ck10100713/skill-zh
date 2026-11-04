---
name: architecture-decision-records
description: 把架構決策記錄成 docs/adr/ 裡編號的 ADR markdown 檔案，內容有背景、考慮過的替代方案和後果，並附一份索引 README。使用者說「記錄這個決策」或「幫這個寫 ADR」、在框架或資料庫之間做選擇、討論取捨，或問為什麼 codebase 長這樣時使用。
metadata:
  origin: ECC
---

# Architecture Decision Records

在 coding session 當下，就把架構決策記錄下來。與其讓決策只存在於 Slack 討論串、PR 留言或某個人的記憶裡，這個 skill 會產出結構化的 ADR 文件，跟程式碼放在一起。

## 何時啟用

- 使用者明確說「我們來記錄這個決策」或「幫這個寫 ADR」
- 使用者在重大的替代方案之間做選擇（框架、函式庫、模式、資料庫、API 設計）
- 使用者說「我們決定要...」或「我們選 X 而不選 Y 的原因是...」
- 使用者問「我們為什麼選 X？」（去讀既有的 ADR）
- 規劃階段討論到架構取捨的時候

## ADR 格式

使用 Michael Nygard 提出的輕量 ADR 格式，並針對 AI 輔助開發做了調整：

```markdown
# ADR-NNNN: [決策標題]

**Date**: YYYY-MM-DD
**Status**: proposed | accepted | deprecated | superseded by ADR-NNNN
**Deciders**: [有哪些人參與]

## Context

我們看到什麼問題，促使了這個決策或變更？

[用 2 到 5 句話描述情況、限制和作用中的各種力量]

## Decision

我們提議和/或正在做的變更是什麼？

[用 1 到 3 句話清楚陳述決策]

## Alternatives Considered

### Alternative 1: [名稱]
- **Pros**: [好處]
- **Cons**: [缺點]
- **Why not**: [這個方案被否決的具體原因]

### Alternative 2: [名稱]
- **Pros**: [好處]
- **Cons**: [缺點]
- **Why not**: [這個方案被否決的具體原因]

## Consequences

因為這個變更，哪些事會變得比較容易或比較困難？

### Positive
- [好處 1]
- [好處 2]

### Negative
- [取捨 1]
- [取捨 2]

### Risks
- [風險與緩解方式]
```

## 工作流程

### 記錄新的 ADR

偵測到決策時刻時：

1. **初始化（只有第一次）**：如果 `docs/adr/` 不存在，要先請使用者確認，再建立這個目錄、一份帶有索引表頭的 `README.md`（見下面的 ADR 索引格式），以及一份供手動使用的空白 `template.md`。沒有明確同意，不要建立檔案。
2. **找出決策**：擷取正在做的核心架構選擇
3. **蒐集背景**：是什麼問題促成的？有哪些限制？
4. **記錄替代方案**：還考慮過哪些選項？為什麼被否決？
5. **陳述後果**：取捨是什麼？哪些事變得比較容易或比較難？
6. **指定編號**：掃描 `docs/adr/` 裡既有的 ADR，然後遞增
7. **確認並寫入**：把 ADR 草稿拿給使用者 review。明確核准之後，才寫入 `docs/adr/NNNN-decision-title.md`。如果使用者拒絕，就丟掉草稿，不要寫任何檔案。
8. **更新索引**：附加到 `docs/adr/README.md`

### 讀取既有的 ADR

當使用者問「我們為什麼選 X？」時：

1. 檢查 `docs/adr/` 是否存在，如果不存在，就回答：「這個專案裡找不到任何 ADR。要不要開始記錄架構決策？」
2. 如果存在，掃描 `docs/adr/README.md` 索引找相關的項目
3. 讀符合的 ADR 檔案，呈現 Context 和 Decision 兩個段落
4. 如果找不到符合的，就回答：「找不到這個決策的 ADR。要不要現在記錄一份？」

### ADR 目錄結構

```
docs/
└── adr/
    ├── README.md              ← 所有 ADR 的索引
    ├── 0001-use-nextjs.md
    ├── 0002-postgres-over-mongo.md
    ├── 0003-rest-over-graphql.md
    └── template.md            ← 供手動使用的空白範本
```

### ADR 索引格式

```markdown
# Architecture Decision Records

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-use-nextjs.md) | Use Next.js as frontend framework | accepted | 2026-01-15 |
| [0002](0002-postgres-over-mongo.md) | PostgreSQL over MongoDB for primary datastore | accepted | 2026-01-20 |
| [0003](0003-rest-over-graphql.md) | REST API over GraphQL | accepted | 2026-02-01 |
```

## 決策偵測訊號

留意對話裡這些代表架構決策的模式：

**明確的訊號**
- "Let's go with X"
- "We should use X instead of Y"
- "The trade-off is worth it because..."
- "Record this as an ADR"

**隱含的訊號**（建議記錄 ADR，沒有使用者確認不要自動建立）
- 比較兩個框架或函式庫，並得出結論
- 做資料庫 schema 的設計選擇，並說明理由
- 在架構模式之間選擇（monolith 對 microservices、REST 對 GraphQL）
- 決定驗證/授權策略
- 評估過替代方案之後，選定部署基礎設施

## 好的 ADR 長什麼樣子

### 該做
- **要具體**：寫「使用 Prisma ORM」，不要寫「用一個 ORM」
- **記錄原因**：理由比做了什麼更重要
- **包含被否決的替代方案**：未來的開發者需要知道考慮過什麼
- **誠實陳述後果**：每個決策都有取捨
- **保持簡短**：ADR 應該 2 分鐘內讀得完
- **用現在式**：寫「我們使用 X」，不要寫「我們將使用 X」

### 不該做
- 記錄瑣碎的決策：變數命名或格式的選擇不需要 ADR
- 寫成長篇大論：如果 context 段落超過 10 行，就太長了
- 省略替代方案：「我們就隨便挑一個」不是有效的理由
- 補寫卻不標註：如果記錄的是過去的決策，要註明原本的日期
- 讓 ADR 過時：被取代的決策應該參照取代它的那一份

## ADR 生命週期

```
proposed → accepted → [deprecated | superseded by ADR-NNNN]
```

- **proposed**：決策還在討論，尚未定案
- **accepted**：決策已生效，也正在被遵循
- **deprecated**：決策不再適用（例如功能被移除）
- **superseded**：有較新的 ADR 取代了這一份（一定要連結到取代它的那份）

## 值得記錄的決策類別

| 類別 | 範例 |
|----------|---------|
| **技術選擇** | 框架、語言、資料庫、雲端服務商 |
| **架構模式** | Monolith 對 microservices、事件驅動、CQRS |
| **API 設計** | REST 對 GraphQL、版本策略、驗證機制 |
| **資料建模** | Schema 設計、正規化的決定、快取策略 |
| **基礎設施** | 部署模型、CI/CD pipeline、監控堆疊 |
| **安全** | 驗證策略、加密做法、secret 管理 |
| **測試** | 測試框架、覆蓋率目標、E2E 與整合測試的平衡 |
| **流程** | 分支策略、review 流程、發布節奏 |

## 與其他 Skill 的整合

- **Planner agent**：當 planner 提議架構變更時，建議建立 ADR
- **Code reviewer agent**：標出引入架構變更、卻沒有對應 ADR 的 PR
