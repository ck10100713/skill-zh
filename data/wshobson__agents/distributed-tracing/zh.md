---
name: distributed-tracing
description: 用 Jaeger 和 Tempo 實作分散式追蹤，追蹤 microservices 之間的請求並找出效能瓶頸。適用於除錯 microservices、分析請求流程，或為分散式系統建立 observability 的時候。
---

# 分散式追蹤

用 Jaeger 和 Tempo 實作分散式追蹤，看清楚請求在 microservices 之間的流向。

## 目的

追蹤請求在分散式系統中的路徑，了解延遲、相依關係和失敗點。

## 什麼時候用

- 除錯延遲問題
- 了解服務之間的相依關係
- 找出瓶頸
- 追蹤錯誤的傳遞
- 分析請求路徑

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務

1. **適度取樣**（production 用 1-10%）
2. **加上有意義的 tag**（user_id、request_id）
3. **在所有服務邊界傳遞 context**
4. **在 span 裡記錄 exception**
5. **操作名稱要一致**
6. **監控追蹤的額外負擔**（對 CPU 的影響 <1%）
7. **設定追蹤錯誤的警報**
8. **實作分散式 context**（baggage）
9. **用 span event** 記錄重要的里程碑
10. **記錄 instrumentation** 的標準

## 與 Logging 整合

### 關聯 Log

```python
import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)

def process_request():
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id

    logger.info(
        "Processing request",
        extra={"trace_id": format(trace_id, '032x')}
    )
```

## 疑難排解

**看不到任何 trace：**

- 檢查 collector 的 endpoint
- 確認網路連線
- 檢查取樣設定
- 檢視應用程式 log

**延遲額外負擔很高：**

- 降低取樣率
- 使用 batch span processor
- 檢查 exporter 設定


## 相關 Skill

- `prometheus-configuration`：用於 metrics
- `grafana-dashboards`：用於視覺化
- `slo-implementation`：用於延遲 SLO
