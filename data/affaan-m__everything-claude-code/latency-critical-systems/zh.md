---
name: latency-critical-systems
description: 優化並驗證對延遲敏感的系統（即時 dashboard、市場資料 feed、streaming agent、執行 gateway、queue 與快取），做法是追蹤 p50/p95/p99 延遲、資料新鮮度（freshness age）與 queue 深度，盤點熱路徑，並做線上實測回讀。在 p95 延遲、吞吐量或資料新鮮度很重要時使用。
license: MIT
metadata:
  origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# 低延遲關鍵系統

當使用者在意即時行為、熱路徑、streaming 新鮮度或執行速度時使用這個 skill。
這也包含類 HFT 的基礎設施，但這個 skill 聚焦在工程面，
不授權實際交易，也不提供
財務建議。

## 把指標拆開

不要把一切都混成「很快」。要追蹤：

- p50、p95 與 p99 延遲；
- 吞吐量；
- 資料新鮮度（freshness age）；
- queue 深度；
- 快取命中率；
- provider/API 回應時間；
- 瀏覽器 render 時間；
- 負載下的正確性；
- 失敗與 retry 行為。

## 畫出熱路徑

把從使用者/事件到最終可見狀態的路徑寫出來：

```text
source event -> provider API -> ingest worker -> queue -> cache -> edge route
-> client stream -> browser render -> user-visible state
```

然後把每一段分開量測。

## 優化順序

1. 移除不必要的 round trip。
2. 對穩定的讀取加上快取，並附帶新鮮度 metadata。
3. 把小量的呼叫與寫入合併成 batch。
4. 把運算移到更靠近資料或使用者的地方。
5. 把熱路徑與冷路徑分開。
6. 在 queue 無限成長之前先施加 backpressure。
7. 只有在能改善新鮮度或使用者體驗時才用 streaming。
8. 為過期資料、降級的 provider 與壞掉的快取狀態加 canary。

## 驗證

已部署的介面存在時，用線上回讀（live readback）驗證：

- HTTP 計時與 response header；
- provider 的新鮮度時間戳；
- queue 或 job 狀態；
- edge/快取狀態；
- 用瀏覽器驗證實際 UI 的新鮮度；
- retry 與降級模式前後的 log。

對市場資料或接近執行端的路徑，在宣告這條路徑
就緒之前，還要驗證 orderbook 的時間年齡、VWAP
假設、provider 狀態與 kill-switch 行為。

## 護欄

- 不要靠捨棄必要的驗證來優化延遲。
- 不要把過期資料藏在快速的快取命中後面。
- 沒有量測，就不要拿 client 標籤宣稱毫秒等級的表現。
- 沒有明確的核准關卡，
  不要送出實際訂單、做破壞性 migration，或做會影響客戶的 deploy。
- 不要讓 secret 與私密 payload 出現在 log 與 benchmark 產物裡。
