---
name: service-mesh-observability
description: 為 service mesh 實作完整的可觀測性，包含分散式 tracing、指標和視覺化。在設定 mesh 監控、除錯延遲問題，或為服務間通訊實作 SLO 時使用。
---

# Service Mesh Observability

Istio、Linkerd 和 service mesh 部署的可觀測性模式完整指南。

## When to Use This Skill

- 設定跨服務的分散式 tracing
- 實作 service mesh 的指標和儀表板
- 除錯延遲和錯誤問題
- 為服務間通訊定義 SLO
- 把服務依賴關係視覺化
- 排查 mesh 的連線問題

## Core Concepts

### 1. Three Pillars of Observability

```
┌─────────────────────────────────────────────────────┐
│                  Observability                       │
├─────────────────┬─────────────────┬─────────────────┤
│     Metrics     │     Traces      │      Logs       │
│                 │                 │                 │
│ • Request rate  │ • Span context  │ • Access logs   │
│ • Error rate    │ • Latency       │ • Error details │
│ • Latency P50   │ • Dependencies  │ • Debug info    │
│ • Saturation    │ • Bottlenecks   │ • Audit trail   │
└─────────────────┴─────────────────┴─────────────────┘
```

### 2. Golden Signals for Mesh

| Signal         | Description               | Alert Threshold   |
| -------------- | ------------------------- | ----------------- |
| **Latency**    | 請求耗時 P50、P99 | P99 > 500ms       |
| **Traffic**    | 每秒請求數       | 異常偵測 |
| **Errors**     | 5xx 錯誤率            | > 1%              |
| **Saturation** | 資源使用率      | > 80%             |

## Templates and detailed worked examples

完整的範本庫和詳細的實作範例放在 `references/details.md`。需要具體範本時，再去讀那個檔案。

## Best Practices

### Do's

- **適當取樣** - dev 100%，prod 1-10%
- **用 trace context** - 一致地傳遞 header
- **設定警報** - 針對 golden signals
- **關聯指標和 trace** - 用 exemplar
- **有策略地保留資料** - 熱/冷儲存分層

### Don'ts

- **不要過度取樣** - 儲存成本會累積
- **不要忽略 cardinality** - 限制 label 的值
- **不要跳過儀表板** - 把依賴關係視覺化
- **不要忘了成本** - 監控可觀測性本身的成本
