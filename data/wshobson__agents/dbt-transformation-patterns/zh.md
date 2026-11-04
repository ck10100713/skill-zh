---
name: dbt-transformation-patterns
description: 精通用 dbt（data build tool）做 analytics engineering，涵蓋 model 組織、測試、文件與 incremental 策略。適用於建立資料轉換、建立資料模型，或落實 analytics engineering 最佳實務的時候。
---

# dbt 轉換模式

可用於 production 的 dbt（data build tool）模式，包含 model 組織、測試策略、文件與 incremental 處理。

## 什麼時候用這個 Skill

- 用 dbt 建立資料轉換 pipeline
- 把 model 整理成 staging、intermediate、marts 三層
- 實作資料品質測試
- 為大型資料集建立 incremental model
- 為資料模型與 lineage 寫文件
- 設定 dbt 專案結構

## 核心概念

### 1. Model 分層（Medallion Architecture）

```
sources/          原始資料定義
    ↓
staging/          與來源 1:1，輕度清理
    ↓
intermediate/     商業邏輯、join、彙總
    ↓
marts/            最終分析用資料表
```

### 2. 命名慣例

| 層級         | 前綴           | 範例                          |
| ------------ | -------------- | ----------------------------- |
| Staging      | `stg_`         | `stg_stripe__payments`        |
| Intermediate | `int_`         | `int_payments_pivoted`        |
| Marts        | `dim_`, `fct_` | `dim_customers`, `fct_orders` |

## 快速開始

```yaml
# dbt_project.yml
name: "analytics"
version: "1.0.0"
profile: "analytics"

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

vars:
  start_date: "2020-01-01"

models:
  analytics:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
      +schema: analytics
```

```
# 專案結構
models/
├── staging/
│   ├── stripe/
│   │   ├── _stripe__sources.yml
│   │   ├── _stripe__models.yml
│   │   ├── stg_stripe__customers.sql
│   │   └── stg_stripe__payments.sql
│   └── shopify/
│       ├── _shopify__sources.yml
│       └── stg_shopify__orders.sql
├── intermediate/
│   └── finance/
│       └── int_payments_pivoted.sql
└── marts/
    ├── core/
    │   ├── _core__models.yml
    │   ├── dim_customers.sql
    │   └── fct_orders.sql
    └── finance/
        └── fct_revenue.sql
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務

### 該做的

- **使用 staging 層**：資料只清一次，到處都能用
- **積極做測試**：not null、unique、relationships
- **每樣東西都寫文件**：欄位描述、model 描述
- **使用 incremental**：資料表超過 100 萬筆時
- **版本控制**：dbt 專案放在 Git

### 不該做的

- **不要跳過 staging**：從 Raw 直接做到 mart 是技術債
- **不要寫死日期**：用 `{{ var('start_date') }}`
- **不要重複邏輯**：抽成 macro
- **不要在 prod 測試**：用 dev target
- **不要忽略 freshness**：要監控來源資料
