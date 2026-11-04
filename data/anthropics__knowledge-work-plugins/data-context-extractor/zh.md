---
name: data-context-extractor
description: >
  從分析師身上萃取只存在於團隊口耳相傳的知識，產生或改進公司專屬的資料分析 skill。

  BOOTSTRAP MODE - Triggers: "Create a data context skill", "Set up data analysis for our warehouse",
  "Help me create a skill for our database", "Generate a data skill for [company]"
  → 探索 schema、提出關鍵問題，並產生含參考檔案的初版 skill

  ITERATION MODE - Triggers: "Add context about [domain]", "The skill needs more info about [topic]",
  "Update the data skill with [metrics/tables/terminology]", "Improve the [domain] reference"
  → 載入既有的 skill、提出針對性的問題，並附加／更新參考檔案

  用在資料分析師希望 Claude 了解他們公司專屬的資料倉儲、術語、指標定義和常見查詢模式的時候。
---

# 資料背景萃取器（Data Context Extractor）

一個 meta-skill，從分析師身上萃取公司專屬的資料知識，並產生量身打造的資料分析 skill。

## 運作方式

這個 skill 有兩種模式：

1. **Bootstrap 模式**：從零開始建立新的資料分析 skill
2. **Iteration 模式**：加入特定領域的參考檔案，改進既有的 skill

---

## Bootstrap 模式

使用時機：使用者想為他們的資料倉儲建立新的資料背景 skill。

### 階段 1：資料庫連線與探索

**步驟 1：確認資料庫類型**

問：「What data warehouse are you using?」

常見的選項：
- **BigQuery**
- **Snowflake**
- **PostgreSQL/Redshift**
- **Databricks**

用 `~~data warehouse` 工具（查詢和 schema）來連線。如果不清楚，就檢查目前 session 裡有哪些可用的 MCP 工具。

**步驟 2：探索 schema**

用 `~~data warehouse` 的 schema 工具來：
1. 列出可用的 dataset／schema
2. 找出最重要的資料表（問使用者：「Which 3-5 tables do analysts query most often?」）
3. 拉出那些關鍵資料表的 schema 細節

各 SQL 方言的探索查詢範例：
```sql
-- BigQuery：列出 dataset
SELECT schema_name FROM INFORMATION_SCHEMA.SCHEMATA

-- BigQuery：列出某個 dataset 裡的資料表
SELECT table_name FROM `project.dataset.INFORMATION_SCHEMA.TABLES`

-- Snowflake：列出 schema
SHOW SCHEMAS IN DATABASE my_database

-- Snowflake：列出資料表
SHOW TABLES IN SCHEMA my_schema
```

### 階段 2：核心問題（要問這些）

schema 探索完之後，用對話的方式問這些問題（不要一次全部丟出來）：

**實體釐清（關鍵）**
> 「When people here say 'user' or 'customer', what exactly do they mean? Are there different types?」

要聽出：
- 多種實體類型（user vs account vs organization）
- 它們之間的關係（1:1、1:多、多:多）
- 哪些 ID 欄位把它們串起來

**主要識別碼**
> 「What's the main identifier for a [customer/user/account]? Are there multiple IDs for the same entity?」

要聽出：
- 主鍵 vs 業務鍵
- UUID vs 整數 ID
- 舊的 ID 系統

**關鍵指標**
> 「What are the 2-3 metrics people ask about most? How is each one calculated?」

要聽出：
- 確切的公式（ARR = monthly_revenue × 12）
- 每個指標由哪些資料表／欄位餵進來
- 時間區間的慣例（近 7 天、日曆月等）

**資料整潔**
> 「What should ALWAYS be filtered out of queries? (test data, fraud, internal users, etc.)」

要聽出：
- 一定要加的標準 WHERE 條件
- 標示排除對象的旗標欄位（is_test、is_internal、is_fraud）
- 要排除的特定值（status = 'deleted'）

**常見的坑**
> 「What mistakes do new analysts typically make with this data?」

要聽出：
- 容易搞混的欄位名稱
- 時區問題
- NULL 處理的怪癖
- 歷史狀態 vs 目前狀態的資料表

### 階段 3：產生 Skill

用這個結構建立 skill：

```
[company]-data-analyst/
├── SKILL.md
└── references/
    ├── entities.md          # 實體定義與關係
    ├── metrics.md           # KPI 計算方式
    ├── tables/              # 每個領域一個檔案
    │   ├── [domain1].md
    │   └── [domain2].md
    └── dashboards.json      # 選填：既有儀表板的目錄
```

**SKILL.md 範本**：見 `references/skill-template.md`

**SQL 方言段落**：見 `references/sql-dialects.md`，並放進適當的方言備註。

**參考檔案範本**：見 `references/domain-template.md`

### 階段 4：打包與交付

1. 在 skill 目錄裡建立所有檔案
2. 打包成 zip 檔
3. 呈現給使用者，並附上摘要說明擷取了什麼

---

## Iteration 模式

使用時機：使用者已經有一個 skill，但需要補充更多背景。

### 步驟 1：載入既有的 Skill

請使用者上傳他們現有的 skill（zip 或資料夾），如果已經在 session 裡就直接找出來。

讀取目前的 SKILL.md 和參考檔案，了解已經記錄了什麼。

### 步驟 2：找出缺口

問：「What domain or topic needs more context? What queries are failing or producing wrong results?」

常見的缺口：
- 新的資料領域（行銷、財務、產品等）
- 缺少的指標定義
- 沒記錄的資料表關係
- 新的術語

### 步驟 3：針對性探索

針對已經確認的領域：

1. **探索相關的資料表**：用 `~~data warehouse` 的 schema 工具找出那個領域的資料表
2. **問針對該領域的問題**：
   - 「What tables are used for [domain] analysis?」
   - 「What are the key metrics for [domain]?」
   - 「Any special filters or gotchas for [domain] data?」

3. **產生新的參考檔案**：用領域範本建立 `references/[domain].md`

### 步驟 4：更新與重新打包

1. 加入新的參考檔案
2. 更新 SKILL.md 的「Knowledge Base Navigation」段落，把新的領域放進去
3. 重新打包 skill
4. 把更新後的 skill 呈現給使用者

---

## 參考檔案標準

每個參考檔案應該包含：

### 資料表文件
- **位置**：完整的資料表路徑
- **說明**：這張表包含什麼、何時使用
- **主鍵**：如何唯一識別每一列
- **更新頻率**：資料多久重新整理一次
- **關鍵欄位**：一張表，列出欄位名稱、型別、說明、備註
- **關聯**：這張表如何和其他表 join
- **範例查詢**：2-3 個常見的查詢模式

### 指標文件
- **指標名稱**：人看得懂的名稱
- **定義**：白話的解釋
- **公式**：附欄位參照的確切算法
- **來源資料表**：資料從哪裡來
- **注意事項**：邊角案例、排除項目、坑

### 實體文件
- **實體名稱**：它叫什麼
- **定義**：它在業務上代表什麼
- **主要資料表**：在哪裡找到這個實體
- **ID 欄位**：如何識別它
- **關聯**：它和其他實體的關係
- **常用篩選**：標準的排除項目（內部、測試等）

---

## 品質檢查清單

交付產生的 skill 之前，確認：

- [ ] SKILL.md 有完整的 frontmatter（name、description）
- [ ] 實體釐清的段落很清楚
- [ ] 關鍵術語都有定義
- [ ] 標準篩選／排除項目都有記錄
- [ ] 每個領域至少有 2-3 個範例查詢
- [ ] SQL 使用正確的方言語法
- [ ] 參考檔案都從 SKILL.md 的導覽段落連結出去
