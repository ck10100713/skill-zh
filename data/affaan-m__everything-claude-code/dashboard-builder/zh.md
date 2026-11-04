---
name: dashboard-builder
description: 為 Grafana、SigNoz 和類似平台建立能回答操作者真實問題的監控 dashboard。當要把 metrics 變成真正能用的 dashboard，而不是好看卻沒用的板子時使用。
metadata:
  version: "1.0.0"
  origin: ECC direct-port adaptation
---

# Dashboard Builder

當任務是要建一個讓人可以拿來操作的 dashboard 時使用。

目標不是「把每個指標都秀出來」。目標是回答：

- 它健康嗎？
- 瓶頸在哪？
- 什麼變了？
- 有人該採取什麼行動？

## 何時使用

- 「建一個 Kafka 監控 dashboard」
- 「幫 Elasticsearch 做一個 Grafana dashboard」
- 「幫這個服務做一個 SigNoz dashboard」
- 「把這份 metrics 清單變成真正能營運用的 dashboard」

## 護欄

- 不要從視覺版面開始，要從操作者的問題開始
- 不要因為某個指標存在，就把所有可用的指標都放進去
- 不要在沒有結構的情況下，把健康、吞吐量和資源的 panel 混在一起
- 不要出貨沒有標題、單位和合理門檻的 panel

## 工作流程

### 1. 定義營運上的問題

圍繞這些來組織：

- 健康 / 可用性
- 延遲 / 效能
- 吞吐量 / 流量
- 飽和度 / 資源
- 該服務特有的風險

### 2. 研究目標平台的 schema

先檢查既有的 dashboard：

- JSON 結構
- 查詢語言
- 變數
- 門檻值的樣式
- 區塊版面

### 3. 建出最小但有用的板子

建議的結構：

1. 總覽
2. 效能
3. 資源
4. 該服務特有的區塊

### 4. 砍掉好看沒用的 panel

每個 panel 都應該回答一個真實的問題。回答不了，就移除。

## Panel 組合範例

### Elasticsearch

- cluster 健康
- shard 配置
- 搜尋延遲
- 索引速率
- JVM heap / GC

### Kafka

- broker 數量
- 副本不足的 partition
- 訊息流入 / 流出
- consumer lag
- 磁碟和網路壓力

### API gateway / ingress

- 請求速率
- p50 / p95 / p99 延遲
- 錯誤率
- upstream 健康
- 活躍連線數

## 品質檢查清單

- [ ] 有效的 dashboard JSON
- [ ] 清楚的區塊分組
- [ ] 有標題和單位
- [ ] 門檻/狀態顏色有意義
- [ ] 常用的篩選有對應的變數
- [ ] 預設的時間範圍和刷新頻率合理
- [ ] 沒有對操作者沒價值的好看 panel

## 相關 Skills

- `research-ops`
- `backend-patterns`
- `terminal-ops`
