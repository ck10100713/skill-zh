---
name: prometheus-configuration
description: 設定 Prometheus，對基礎設施與應用程式做完整的指標收集、儲存與監控。在實作指標收集、建立監控基礎設施或設定警報系統時使用。
---

# Prometheus Configuration

Prometheus 設定、指標收集、scrape 設定與 recording rule 的完整指南。

## Purpose

設定 Prometheus，對基礎設施與應用程式做完整的指標收集、警報與監控。

## When to Use

- 建立 Prometheus 監控
- 設定指標 scraping
- 建立 recording rule
- 設計警報規則
- 實作 service discovery

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Best Practices

1. 指標的**命名要一致**（prefix_name_unit）
2. **設定適當的 scrape 間隔**（一般 15 到 60 秒）
3. 對耗資源的查詢**使用 recording rule**
4. **實作高可用**（多個 Prometheus 實例）
5. 依儲存容量**設定保留期限**
6. **使用 relabeling** 清理指標
7. **監控 Prometheus 本身**
8. 大型部署**實作 federation**
9. 長期儲存**使用 Thanos/Cortex**
10. **記錄自訂指標**

## Troubleshooting

**檢查 scrape 目標：**

```bash
curl http://localhost:9090/api/v1/targets
```

**檢查設定：**

```bash
curl http://localhost:9090/api/v1/status/config
```

**測試查詢：**

```bash
curl 'http://localhost:9090/api/v1/query?query=up'
```


## Related Skills

- `grafana-dashboards` - 用於視覺化
- `slo-implementation` - 用於 SLO 監控
- `distributed-tracing` - 用於請求追蹤
