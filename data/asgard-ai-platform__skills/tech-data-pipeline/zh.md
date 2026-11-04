---
name: "tech-data-pipeline"
description: "設計資料管線，涵蓋 ETL 與 ELT 架構、資料來源整合、排程、品質檢查和資料倉儲設計。當使用者需要在系統之間搬資料、建資料倉儲、自動化資料處理或提升資料可靠度時使用這個 skill，就算他們說的是「把資料從 X 搬到 Y」、「建一條 ETL pipeline」、「我們的資料一團亂」或「架一個 data warehouse」也一樣。"
metadata:
  category: "WP-11 通用技術"
  tags: ["technology", "data-pipeline", "etl", "data-engineering"]
---

# 資料管線設計

## 框架

```
IRON LAW: Data Quality Checks at Every Stage
（鐵律：每個階段都要做資料品質檢查）

一條把壞資料搬得很快的管線，比沒有管線還糟，
因為它會汙染下游的分析和決策。管線的每個階段
（extract、transform、load）都必須有資料品質檢查：
筆數、null 檢查、schema 驗證、新鮮度檢查。

「Garbage in, garbage out」不是警告，是保證。
```

### ETL vs ELT

| 面向 | ETL（Extract, Transform, Load） | ELT（Extract, Load, Transform） |
|--------|-------------------------------|-------------------------------|
| 在哪裡轉換？ | 載入前（在管線裡） | 載入後（在倉儲裡） |
| 最適合 | 結構化資料、重合規的情境 | 雲端倉儲（BigQuery、Snowflake） |
| 彈性 | 較低（轉換邏輯是固定的） | 較高（載入後用 SQL 轉換） |
| 成本 | 運算花在管線 | 運算花在倉儲 |
| 趨勢 | 傳統/地端 | 現代/雲原生 |

### 管線架構

```
[Sources] → [Extract] → [Stage] → [Transform] → [Load] → [Serve]
   ↑                                                          ↓
   |              [Quality Checks at every stage]        [Dashboard]
   |              [Monitoring & Alerting]                [API]
   └──────────────── [Orchestrator (Airflow/Prefect)] ──────┘
```

### 資料來源類型

| 來源 | 擷取方式 | 挑戰 |
|--------|-----------------|-----------|
| **資料庫** | CDC（Change Data Capture）、批次查詢、複寫 | schema 變動、對來源端的效能衝擊 |
| **API** | REST/GraphQL 輪詢、webhook | 速率限制、分頁、auth token 更新 |
| **檔案** | S3/GCS 撈取、SFTP、email 附件 | 格式不一致、編碼問題 |
| **串流** | Kafka、Kinesis、Pub/Sub | 順序、exactly-once 處理 |
| **SaaS 工具** | 現成 connector（Fivetran、Airbyte） | API 變動、資料模型複雜 |

### 排程調度工具

| 工具 | 類型 | 最適合 | 複雜度 |
|------|------|----------|-----------|
| **Airflow** | Python DAG | 複雜管線、有工程師團隊 | 高 |
| **Prefect** | Python、現代 API | 比 Airflow 簡單、開發體驗好 | 中 |
| **dbt** | 只做 SQL 轉換 | ELT 的轉換層 | 中低 |
| **Cron** | 簡單排程 | 單一腳本、低複雜度 | 低 |
| **Fivetran/Airbyte** | 託管的 connector | Extract + Load（不含轉換） | 低 |

### 資料品質框架

| 檢查 | 驗證什麼 | 時機 |
|-------|-----------------|------|
| **筆數（Row count）** | 筆數符合預期（與上次執行相差在 ±10% 以內） | extract 後、load 後 |
| **Null 檢查** | 關鍵欄位沒有非預期的 null | extract 後 |
| **Schema 驗證** | 欄位名稱、型別符合預期 | extract 後 |
| **新鮮度（Freshness）** | 資料夠新（沒有過期） | load 後 |
| **唯一性** | 沒有重複的 primary key | load 後 |
| **範圍檢查** | 數值落在預期範圍內 | transform 後 |
| **參照完整性** | foreign key 對得上父表 | load 後 |

### 管線設計步驟

1. **盤點來源與目的地**：什麼資料、從哪來、到哪去？
2. **定義新鮮度需求**：即時？每小時？每天？
3. **選架構**：依工具和團隊決定 ETL 或 ELT
4. **漸進式建置**：從一個來源、一個目的地、一個排程開始
5. **加品質檢查**：至少要有筆數 + null 檢查 + 新鮮度
6. **建立監控**：失敗、品質檢查違規、延遲都要告警
7. **寫文件**：資料字典、管線圖、SLA

## 輸出格式

```markdown
# Data Pipeline Design: {Project}

## Sources & Destinations
| Source | Type | Destination | Freshness | Volume |
|--------|------|-----------|-----------|--------|
| {source} | DB/API/File | {dest} | {daily/hourly} | {rows/day} |

## Architecture
- Pattern: ETL / ELT
- Orchestrator: {tool}
- Transform: {tool/SQL}
- Quality: {tool/custom checks}

## Pipeline Diagram
{Source} → {Extract} → {Stage} → {Transform} → {Load} → {Serve}

## Quality Checks
| Stage | Check | Threshold | Alert |
|-------|-------|-----------|-------|
| Extract | Row count | ±10% of prior | Slack alert |
| Load | Freshness | < 6 hours old | PagerDuty |

## Schedule
| Pipeline | Frequency | Start Time | SLA |
|----------|-----------|-----------|-----|
| {name} | {daily/hourly} | {time} | Data ready by {time} |
```

## 常見陷阱

- **冪等性不能少**：管線跑兩次的結果，要跟跑一次一樣。用 upsert（不是 insert）和依日期分區的載入。
- **Schema 漂移**：來源系統會在沒通知的情況下改 schema。要做 schema 偵測和告警。
- **補跑（backfill）能力**：管線壞了 3 天，能不能只重跑那 3 天而不產生重複資料？從第一天就要這樣設計。
- **買得到的就別自己做**：Fivetran/Airbyte 有 200 多種來源 connector。自己寫一個 Salesforce 擷取器，很少值得投入那些工程時間。
- **資料倉儲 vs 資料湖**：倉儲（BigQuery、Snowflake）= 結構化、可用 SQL 查詢。資料湖（S3、GCS）= 原始、任何格式都行。多數現代架構兩者並用（lakehouse 模式）。

## 參考資料

- dbt 專案結構，見 `references/dbt-guide.md`
- 資料倉儲建模（星狀 schema），見 `references/dimensional-modeling.md`
