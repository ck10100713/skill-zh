---
name: grafana-dashboards
description: 建立並管理可上 production 的 Grafana dashboard，用於即時視覺化系統與應用程式的指標。適用於建構監控 dashboard、視覺化指標，或建立營運 observability 介面的時候。
---

# Grafana Dashboard

為完整的系統 observability 建立並管理可上 production 的 Grafana dashboard。

## 目的

設計有效的 Grafana dashboard，用來監控應用程式、基礎設施與業務指標。

## 什麼時候用

- 視覺化 Prometheus 指標
- 建立自訂 dashboard
- 實作 SLO dashboard
- 監控基礎設施
- 追蹤業務 KPI

## Dashboard 設計原則

### 1. 資訊的階層

```
┌─────────────────────────────────────┐
│  關鍵指標（大數字）                 │
├─────────────────────────────────────┤
│  主要趨勢（時間序列）               │
├─────────────────────────────────────┤
│  詳細指標（表格/熱圖）              │
└─────────────────────────────────────┘
```

### 2. RED 方法（服務）

- **Rate**：每秒請求數
- **Errors**：錯誤率
- **Duration**：延遲/回應時間

### 3. USE 方法（資源）

- **Utilization**：資源忙碌的時間百分比
- **Saturation**：佇列長度/等待時間
- **Errors**：錯誤數量

## Dashboard 結構

### API 監控 Dashboard

```json
{
  "dashboard": {
    "title": "API Monitoring",
    "tags": ["api", "production"],
    "timezone": "browser",
    "refresh": "30s",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (service)",
            "legendFormat": "{{service}}"
          }
        ],
        "gridPos": { "x": 0, "y": 0, "w": 12, "h": 8 }
      },
      {
        "title": "Error Rate %",
        "type": "graph",
        "targets": [
          {
            "expr": "(sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))) * 100",
            "legendFormat": "Error Rate"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": { "params": [5], "type": "gt" },
              "operator": { "type": "and" },
              "query": { "params": ["A", "5m", "now"] },
              "type": "query"
            }
          ]
        },
        "gridPos": { "x": 12, "y": 0, "w": 12, "h": 8 }
      },
      {
        "title": "P95 Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))",
            "legendFormat": "{{service}}"
          }
        ],
        "gridPos": { "x": 0, "y": 8, "w": 24, "h": 8 }
      }
    ]
  }
}
```

## 面板類型

### 1. Stat 面板（單一數值）

```json
{
  "type": "stat",
  "title": "Total Requests",
  "targets": [
    {
      "expr": "sum(http_requests_total)"
    }
  ],
  "options": {
    "reduceOptions": {
      "values": false,
      "calcs": ["lastNotNull"]
    },
    "orientation": "auto",
    "textMode": "auto",
    "colorMode": "value"
  },
  "fieldConfig": {
    "defaults": {
      "thresholds": {
        "mode": "absolute",
        "steps": [
          { "value": 0, "color": "green" },
          { "value": 80, "color": "yellow" },
          { "value": 90, "color": "red" }
        ]
      }
    }
  }
}
```

### 2. 時間序列圖

```json
{
  "type": "graph",
  "title": "CPU Usage",
  "targets": [
    {
      "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
    }
  ],
  "yaxes": [
    { "format": "percent", "max": 100, "min": 0 },
    { "format": "short" }
  ]
}
```

### 3. 表格面板

```json
{
  "type": "table",
  "title": "Service Status",
  "targets": [
    {
      "expr": "up",
      "format": "table",
      "instant": true
    }
  ],
  "transformations": [
    {
      "id": "organize",
      "options": {
        "excludeByName": { "Time": true },
        "indexByName": {},
        "renameByName": {
          "instance": "Instance",
          "job": "Service",
          "Value": "Status"
        }
      }
    }
  ]
}
```

### 4. 熱圖

```json
{
  "type": "heatmap",
  "title": "Latency Heatmap",
  "targets": [
    {
      "expr": "sum(rate(http_request_duration_seconds_bucket[5m])) by (le)",
      "format": "heatmap"
    }
  ],
  "dataFormat": "tsbuckets",
  "yAxis": {
    "format": "s"
  }
}
```

## 變數

### Query 變數

```json
{
  "templating": {
    "list": [
      {
        "name": "namespace",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(kube_pod_info, namespace)",
        "refresh": 1,
        "multi": false
      },
      {
        "name": "service",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(kube_service_info{namespace=\"$namespace\"}, service)",
        "refresh": 1,
        "multi": true
      }
    ]
  }
}
```

### 在查詢中使用變數

```
sum(rate(http_requests_total{namespace="$namespace", service=~"$service"}[5m]))
```

## Dashboard 中的警報

```json
{
  "alert": {
    "name": "High Error Rate",
    "conditions": [
      {
        "evaluator": {
          "params": [5],
          "type": "gt"
        },
        "operator": { "type": "and" },
        "query": {
          "params": ["A", "5m", "now"]
        },
        "reducer": { "type": "avg" },
        "type": "query"
      }
    ],
    "executionErrorState": "alerting",
    "for": "5m",
    "frequency": "1m",
    "message": "Error rate is above 5%",
    "noDataState": "no_data",
    "notifications": [{ "uid": "slack-channel" }]
  }
}
```

## Dashboard Provisioning

**dashboards.yml：**

```yaml
apiVersion: 1

providers:
  - name: "default"
    orgId: 1
    folder: "General"
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/dashboards
```

## 常見的 Dashboard 模式

### 基礎設施 Dashboard

**主要面板：**

- 每個節點的 CPU 使用率
- 每個節點的記憶體用量
- 磁碟 I/O
- 網路流量
- 依 namespace 區分的 Pod 數量
- 節點狀態

### 資料庫 Dashboard

**主要面板：**

- 每秒查詢數
- Connection pool 使用量
- 查詢延遲（P50、P95、P99）
- 活躍連線數
- 資料庫大小
- 複寫延遲
- 慢查詢

### 應用程式 Dashboard

**主要面板：**

- 請求速率
- 錯誤率
- 回應時間（百分位數）
- 活躍使用者/session
- 快取命中率
- 佇列長度

## 最佳實務

1. **從範本開始**（Grafana 社群的 dashboard）
2. **面板與變數的命名要一致**
3. **把相關的指標放在同一個 row**
4. **設定適當的時間範圍**（預設：最近 6 小時）
5. **使用變數**增加彈性
6. **加上面板描述**提供脈絡
7. **正確設定單位**
8. **為顏色設定有意義的門檻**
9. **跨 dashboard 使用一致的顏色**
10. **用不同的時間範圍測試**

## Dashboard as Code

### Terraform Provisioning

```hcl
resource "grafana_dashboard" "api_monitoring" {
  config_json = file("${path.module}/dashboards/api-monitoring.json")
  folder      = grafana_folder.monitoring.id
}

resource "grafana_folder" "monitoring" {
  title = "Production Monitoring"
}
```

### Ansible Provisioning

```yaml
- name: Deploy Grafana dashboards
  copy:
    src: "{{ item }}"
    dest: /etc/grafana/dashboards/
  with_fileglob:
    - "dashboards/*.json"
  notify: restart grafana
```


## 相關 Skill

- `prometheus-configuration`：用於指標收集
- `slo-implementation`：用於 SLO dashboard
