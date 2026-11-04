---
name: d1-migration
description: "Cloudflare D1 的 migration 工作流程：用 Drizzle 產生、檢查 SQL 的陷阱、套用到本機和遠端、修復卡住的 migration、處理部分失敗。執行 migration、修復 migration 錯誤或設定 D1 schema 時使用。"
compatibility: claude-code-only
---

# D1 Migration Workflow

使用 Drizzle ORM 做 Cloudflare D1 資料庫 migration 的引導式工作流程。

## 標準 Migration 流程

### 1. 產生 Migration

```bash
pnpm db:generate
```

這會在 `drizzle/`（或你設定的 migration 目錄）裡建立一個新的 `.sql` 檔案。

### 2. 檢查 SQL（關鍵）

**套用之前，一定要先讀產生出來的 SQL。**對於簡單的 schema 改動，Drizzle 有時會產生具破壞性的 migration。

#### 警訊：重建資料表

如果看到這種模式，migration 很可能會失敗：

```sql
CREATE TABLE `my_table_new` (...);
INSERT INTO `my_table_new` SELECT ..., `new_column`, ... FROM `my_table`;
--                                      ^^^ This column doesn't exist in old table!
DROP TABLE `my_table`;
ALTER TABLE `my_table_new` RENAME TO `my_table`;
```

**原因**：在 Drizzle schema 裡改欄位的 `default` 值，會觸發整張資料表重建。INSERT SELECT 會從舊資料表去參照新的欄位。

**解法**：如果你只是新增欄位（沒有改到既有欄位的型別/約束），就簡化成：

```sql
ALTER TABLE `my_table` ADD COLUMN `new_column` TEXT DEFAULT 'value';
```

套用之前，直接編輯 `.sql` 檔案。

### 3. 套用到本機

```bash
pnpm db:migrate:local
# or: npx wrangler d1 migrations apply DB_NAME --local
```

### 4. 套用到遠端

```bash
pnpm db:migrate:remote
# or: npx wrangler d1 migrations apply DB_NAME --remote
```

**測試之前，本機和遠端兩邊都一定要套用。**只套用本機的 migration，會造成讓人摸不著頭緒的「本機正常、上線就壞」問題。

### 5. 驗證

```bash
# Check local
npx wrangler d1 execute DB_NAME --local --command "PRAGMA table_info(my_table)"

# Check remote
npx wrangler d1 execute DB_NAME --remote --command "PRAGMA table_info(my_table)"
```

## 修復卡住的 Migration

當 migration 只套用了一部分（例如欄位加好了，但 migration 沒被記錄），wrangler 會重試，然後因為欄位重複而失敗。

**症狀**：`pnpm db:migrate` 在一個看起來應該已經完成的 migration 上報錯。`PRAGMA table_info` 顯示欄位已經存在。

### 診斷

```bash
# 1. Verify the column/table exists
npx wrangler d1 execute DB_NAME --remote \
  --command "PRAGMA table_info(my_table)"

# 2. Check what migrations are recorded
npx wrangler d1 execute DB_NAME --remote \
  --command "SELECT * FROM d1_migrations ORDER BY id"
```

### 修復

```bash
# 3. Manually record the stuck migration
npx wrangler d1 execute DB_NAME --remote \
  --command "INSERT INTO d1_migrations (name, applied_at) VALUES ('0013_my_migration.sql', datetime('now'))"

# 4. Run remaining migrations normally
pnpm db:migrate
```

### 預防

- `CREATE TABLE IF NOT EXISTS`：重跑也安全
- `ALTER TABLE ADD COLUMN`：SQLite 沒有 `IF NOT EXISTS` 的變體；先檢查欄位是否存在，或在應用程式碼裡用 try/catch
- 套用之前**一定要檢查產生出來的 SQL**（上面的 Step 2）

## 批次 Insert 分批

D1 的參數限制會讓大型多列 INSERT 無聲地失敗。要分成小批次：

```typescript
const BATCH_SIZE = 10;
for (let i = 0; i < allRows.length; i += BATCH_SIZE) {
  const batch = allRows.slice(i, i + BATCH_SIZE);
  await db.insert(myTable).values(batch);
}
```

**原因**：列數 x 欄位數超過約 100-150 個參數時，D1 就會失敗。

## 欄位命名

| 情境 | 慣例 | 範例 |
|---------|-----------|---------|
| Drizzle schema | camelCase | `caseNumber: text('case_number')` |
| 原始 SQL 查詢 | snake_case | `UPDATE cases SET case_number = ?` |
| API 回應 | 對應 SQL 別名 | `SELECT case_number FROM cases` |

## 新專案設定

替新專案建立 D1 資料庫時，照這個順序：

1. **先部署 Worker**：`npm run build && npx wrangler deploy`
2. **建立 D1 資料庫**：`npx wrangler d1 create project-name-db`
3. **把 database_id 複製到** `wrangler.jsonc` 的 `d1_databases` binding
4. **重新部署**：`npx wrangler deploy`
5. **執行 migration**：本機和遠端都要套用
