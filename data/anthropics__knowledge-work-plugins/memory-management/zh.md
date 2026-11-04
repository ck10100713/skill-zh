---
name: memory-management
description: 兩層式記憶系統，讓 Claude 成為真正的職場協作夥伴。能解碼縮寫、首字母縮略詞、暱稱和內部用語，讓 Claude 像同事一樣聽懂你的需求。CLAUDE.md 放工作記憶，memory/ 目錄放完整知識庫。
user-invocable: false
---

# 記憶管理

記憶讓 Claude 成為你的職場協作夥伴，一個聽得懂你們內部用語的人。

## 目標

把縮寫變成理解：

```
User: "ask todd to do the PSR for oracle"
              ↓ Claude decodes
"Ask Todd Martinez (Finance lead) to prepare the Pipeline Status Report
 for the Oracle Systems deal ($2.3M, closing Q2)"
```

沒有記憶的話，這個請求毫無意義。有了記憶，Claude 就知道：
- **todd** → Todd Martinez，財務主管，偏好用 Slack
- **PSR** → Pipeline Status Report（每週的業務文件）
- **oracle** → Oracle Systems 這筆交易，不是那間公司

## 架構

```
CLAUDE.md          ← Hot cache（約 30 個人、常用術語）
memory/
  glossary.md      ← 完整解碼表（所有東西）
  people/          ← 完整的人物檔案
  projects/        ← 專案細節
  context/         ← 公司、團隊、工具
```

**CLAUDE.md（Hot Cache）：**
- 你互動最頻繁的前 30 個人左右
- 最常用的約 30 個縮寫／術語
- 進行中的專案（5 到 15 個）
- 你的偏好
- **目標：涵蓋 90% 的日常解碼需求**

**memory/glossary.md（完整詞彙表）：**
- 完整的解碼表，每個人、每個術語都在裡面
- CLAUDE.md 裡找不到時才去搜
- 可以無限成長

**memory/people/、projects/、context/：**
- 執行時需要的豐富細節
- 完整的檔案、歷史、背景

## 查詢流程

```
User: "ask todd about the PSR for phoenix"

1. Check CLAUDE.md (hot cache)
   → Todd? ✓ Todd Martinez, Finance
   → PSR? ✓ Pipeline Status Report
   → Phoenix? ✓ DB migration project

2. If not found → search memory/glossary.md
   → Full glossary has everyone/everything

3. If still not found → ask user
   → "What does X mean? I'll remember it."
```

這種分層做法讓 CLAUDE.md 保持精簡（約 100 行），同時 memory/ 可以無限擴充。

## 檔案位置

- **工作記憶：** 目前工作目錄下的 `CLAUDE.md`
- **深層記憶：** `memory/` 子目錄

## 工作記憶格式（CLAUDE.md）

用表格比較精簡。目標總共約 50 到 80 行。

```markdown
# Memory

## Me
[Name], [Role] on [Team]. [One sentence about what I do.]

## People
| Who | Role |
|-----|------|
| **Todd** | Todd Martinez, Finance lead |
| **Sarah** | Sarah Chen, Engineering (Platform) |
| **Greg** | Greg Wilson, Sales |
→ Full list: memory/glossary.md, profiles: memory/people/

## Terms
| Term | Meaning |
|------|---------|
| PSR | Pipeline Status Report |
| P0 | Drop everything priority |
| standup | Daily 9am sync |
→ Full glossary: memory/glossary.md

## Projects
| Name | What |
|------|------|
| **Phoenix** | DB migration, Q2 launch |
| **Horizon** | Mobile app redesign |
→ Details: memory/projects/

## Preferences
- 25-min meetings with buffers
- Async-first, Slack over email
- No meetings Friday afternoons
```

## 深層記憶格式（memory/）

**memory/glossary.md**：解碼表
```markdown
# Glossary

Workplace shorthand, acronyms, and internal language.

## Acronyms
| Term | Meaning | Context |
|------|---------|---------|
| PSR | Pipeline Status Report | Weekly sales doc |
| OKR | Objectives & Key Results | Quarterly planning |
| P0/P1/P2 | Priority levels | P0 = drop everything |

## Internal Terms
| Term | Meaning |
|------|---------|
| standup | Daily 9am sync in #engineering |
| the migration | Project Phoenix database work |
| ship it | Deploy to production |
| escalate | Loop in leadership |

## Nicknames → Full Names
| Nickname | Person |
|----------|--------|
| Todd | Todd Martinez (Finance) |
| T | Also Todd Martinez |

## Project Codenames
| Codename | Project |
|----------|---------|
| Phoenix | Database migration |
| Horizon | New mobile app |
```

**memory/people/{name}.md：**
```markdown
# Todd Martinez

**Also known as:** Todd, T
**Role:** Finance Lead
**Team:** Finance
**Reports to:** CFO (Michael Chen)

## Communication
- Prefers Slack DM
- Quick responses, very direct
- Best time: mornings

## Context
- Handles all PSRs and financial reporting
- Key contact for deal approvals over $500k
- Works closely with Sales on forecasting

## Notes
- Cubs fan, likes talking baseball
```

**memory/projects/{name}.md：**
```markdown
# Project Phoenix

**Codename:** Phoenix
**Also called:** "the migration"
**Status:** Active, launching Q2

## What It Is
Database migration from legacy Oracle to PostgreSQL.

## Key People
- Sarah - tech lead
- Todd - budget owner
- Greg - stakeholder (sales impact)

## Context
$1.2M budget, 6-month timeline. Critical path for Horizon project.
```

**memory/context/company.md：**
```markdown
# Company Context

## Tools & Systems
| Tool | Used for | Internal name |
|------|----------|---------------|
| Slack | Communication | - |
| Asana | Engineering tasks | - |
| Salesforce | CRM | "SF" or "the CRM" |
| Notion | Docs/wiki | - |

## Teams
| Team | What they do | Key people |
|------|--------------|------------|
| Platform | Infrastructure | Sarah (lead) |
| Finance | Money stuff | Todd (lead) |
| Sales | Revenue | Greg |

## Processes
| Process | What it means |
|---------|---------------|
| Weekly sync | Monday 10am all-hands |
| Ship review | Thursday deploy approval |
```

## 怎麼互動

### 解碼使用者輸入（分層查詢）

在動手處理請求之前，**一定要**先解碼縮寫：

```
1. CLAUDE.md (hot cache)     → Check first, covers 90% of cases
2. memory/glossary.md        → Full glossary if not in hot cache
3. memory/people/, projects/ → Rich detail when needed
4. Ask user                  → Unknown term? Learn it.
```

範例：
```
User: "ask todd to do the PSR for oracle"

CLAUDE.md lookup:
  "todd" → Todd Martinez, Finance ✓
  "PSR" → Pipeline Status Report ✓
  "oracle" → (not in hot cache)

memory/glossary.md lookup:
  "oracle" → Oracle Systems deal ($2.3M) ✓

Now Claude can act with full context.
```

### 新增記憶

當使用者說「remember this」或「X means Y」：

1. **詞彙項目**（縮寫、術語、簡稱）：
   - 加到 memory/glossary.md
   - 如果常用，也加到 CLAUDE.md 的 Quick Glossary

2. **人物：**
   - 建立／更新 memory/people/{name}.md
   - 如果重要，加到 CLAUDE.md 的 Key People
   - **記下暱稱**，這對解碼至關重要

3. **專案：**
   - 建立／更新 memory/projects/{name}.md
   - 如果是目前進行中的，加到 CLAUDE.md 的 Active Projects
   - **記下代號**：「Phoenix」、「the migration」等等

4. **偏好：** 加到 CLAUDE.md 的 Preferences 區段

### 回想記憶

當使用者問「who is X」或「what does X mean」：

1. 先查 CLAUDE.md
2. 再查 memory/ 的完整細節
3. 找不到就說：「I don't know what X means yet. Can you tell me?」

### 漸進式揭露

1. 載入 CLAUDE.md，快速解析任何請求
2. 需要完整背景才能執行時，再深入 memory/
3. 範例：寫一封給 todd 談 PSR 的 email
   - CLAUDE.md 告訴你 Todd = Todd Martinez、PSR = Pipeline Status Report
   - memory/people/todd-martinez.md 告訴你他偏好 Slack、講話很直接

## 初始化

用 `/productivity:start` 掃描你的聊天、行事曆、email 和文件來初始化。它會抽出人物、專案，並開始建立詞彙表。

## 慣例

- CLAUDE.md 裡的術語用**粗體**，方便掃讀
- CLAUDE.md 維持在約 100 行以內（「hot 30」法則）
- 檔名：小寫加連字號（`todd-martinez.md`、`project-phoenix.md`）
- 一定要記下暱稱和別名
- 詞彙用表格，方便查找
- 某個東西用得很頻繁時，升級到 CLAUDE.md
- 某個東西過時了，降級成只放在 memory/

## 什麼放哪裡

| 類型 | CLAUDE.md（Hot Cache） | memory/（完整儲存） |
|------|----------------------|------------------------|
| 人物 | 前 30 個左右的常聯絡對象 | glossary.md + people/{name}.md |
| 縮寫／術語 | 最常用的約 30 個 | glossary.md（完整清單） |
| 專案 | 只放進行中的專案 | glossary.md + projects/{name}.md |
| 暱稱 | 前 30 名的話放在 Key People | glossary.md（所有暱稱） |
| 公司背景 | 只放快速參考 | context/company.md |
| 偏好 | 全部偏好 | - |
| 歷史／過時 | ✗ 移除 | ✓ 保留在 memory/ |

## 升級／降級

**升級到 CLAUDE.md 的時機：**
- 你常常用到某個術語／人物
- 它是目前進行中工作的一部分

**降級成只放 memory/ 的時機：**
- 專案完成了
- 這個人不再是常聯絡對象
- 術語很少用

這樣可以讓 CLAUDE.md 保持新鮮、有用。
