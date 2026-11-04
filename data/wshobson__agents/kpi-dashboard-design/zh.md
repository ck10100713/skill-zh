---
name: kpi-dashboard-design
description: 設計有效的 KPI dashboard，涵蓋指標選擇、視覺化最佳實務與即時監控模式。在建立追蹤 MRR、churn、LTV/CAC 的高階主管 SaaS 指標 dashboard、設計有即時服務健康度與請求吞吐量的營運中心、為產品團隊做 cohort 留存分析檢視，或排查因計算方法不一致而互相矛盾的指標時使用。
---

# KPI Dashboard Design

設計有效的 Key Performance Indicator (KPI) dashboard 的完整模式，目標是能推動商業決策。

## When to Use This Skill

- 設計高階主管 dashboard
- 挑選有意義的 KPI
- 建立即時監控畫面
- 建立各部門專屬的指標檢視
- 改善現有 dashboard 的版面
- 建立指標治理機制

## Core Concepts

### 1. KPI Framework

| Level           | Focus            | Update Frequency  | Audience   |
| --------------- | ---------------- | ----------------- | ---------- |
| **Strategic**   | 長期目標  | 每月/每季 | 高階主管 |
| **Tactical**    | 部門目標 | 每週/每月    | 主管 |
| **Operational** | 日常營運       | 即時/每日   | 團隊 |

### 2. SMART KPIs

```
Specific: Clear definition
Measurable: Quantifiable
Achievable: Realistic targets
Relevant: Aligned to goals
Time-bound: Defined period
```

### 3. Dashboard Hierarchy

```
├── Executive Summary (1 page)
│   ├── 4-6 headline KPIs
│   ├── Trend indicators
│   └── Key alerts
├── Department Views
│   ├── Sales Dashboard
│   ├── Marketing Dashboard
│   ├── Operations Dashboard
│   └── Finance Dashboard
└── Detailed Drilldowns
    ├── Individual metrics
    └── Root cause analysis
```

## Detailed worked examples and patterns

詳細章節（從 `## Common KPIs by Department` 開始）放在 `references/details.md`。上面的導覽摘要不夠用時，再去讀那個檔案。

## Best Practices

### Do's

- **KPI 限制在 5 到 7 個** - 專注在真正重要的
- **提供脈絡** - 比較、趨勢、目標
- **顏色保持一致** - 紅色代表差，綠色代表好
- **支援 drilldown** - 從摘要往下鑽到細節
- **更新頻率要適當** - 配合指標本身的頻率

### Don'ts

- **不要放虛榮指標** - 專注在能採取行動的資料
- **不要塞太滿** - 留白有助於理解
- **不要用 3D 圖表** - 會扭曲視覺判斷
- **不要隱藏計算方法** - 要把計算方式寫下來
- **不要忽略行動裝置** - 確保版面能響應式調整

## Troubleshooting

### Dashboard 上的 MRR 跟財務部的數字對不上

最常見的原因是年繳方案的處理方式不一致。財務可能按日攤提，而 dashboard 是正規化成月。統一成同一個公式，並直接寫在 dashboard 的卡片上：

```sql
-- Explicit formula shown in tooltip / data dictionary
-- Annual plans: divide total contract value by 12
-- Quarterly plans: divide by 3
-- Monthly plans: use as-is
CASE subscription_interval
    WHEN 'monthly'   THEN amount
    WHEN 'quarterly' THEN amount / 3.0
    WHEN 'yearly'    THEN amount / 12.0
END AS normalized_mrr
```

### Dashboard 一片綠，但產品團隊說用戶一直在抱怨

Dashboard 很可能只追蹤系統 uptime（落後指標），沒有追蹤使用者實際感受到的品質。在基礎設施指標旁邊加上使用者感知的指標：

| Infrastructure (green) | User-perceived (add these) |
|---|---|
| API uptime 99.9% | P95 page load time |
| Error rate 0.1% | Task completion rate |
| Queue depth normal | Support ticket volume |

### 留存 cohort 看起來是平的，各 cohort 之間沒有差異

檢查 cohort 查詢有沒有正確按註冊月份分組。常見的 bug 是用了 `created_at::date` 而不是 `DATE_TRUNC('month', created_at)`，這樣會按天分組，cohort 太小，看不出趨勢：

```sql
-- Wrong: too granular, cohorts are too small
DATE_TRUNC('day', created_at) AS cohort_date

-- Correct: monthly cohorts
DATE_TRUNC('month', created_at) AS cohort_month
```

### 即時 dashboard 把資料庫打爆

每 10 秒刷新一次、又跑複雜 cohort SQL 的即時 dashboard，會拖垮正式環境的查詢效能。把 OLAP 負載跟 OLTP 分開：用排程 job 把預先聚合好的指標寫進摘要表，dashboard 改讀那張表：

```python
# Scheduled every 5 minutes via cron/Celery
def refresh_mrr_summary():
    conn.execute("""
        INSERT INTO kpi_snapshot (metric, value, snapshot_at)
        SELECT 'mrr', SUM(...), NOW()
        FROM subscriptions WHERE status = 'active'
        ON CONFLICT (metric) DO UPDATE SET value = EXCLUDED.value
    """)
```

### 警報閾值一直觸發，團隊都不理了

靜態閾值設了就沒再檢視，會造成 alert fatigue。改用依滾動平均計算的動態閾值，只有指標明顯偏離自己的基準線時才觸發警報：

```python
# Alert if current value is > 2 standard deviations from 30-day rolling mean
def is_anomalous(current: float, history: list[float]) -> bool:
    mean = statistics.mean(history)
    stdev = statistics.stdev(history)
    return abs(current - mean) > 2 * stdev
```

## Related Skills

- `data-storytelling` - 把 dashboard 的發現變成能推動高階主管決策的敘事
