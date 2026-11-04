---
name: benchmark
description: 量測效能基準線並偵測回歸，涵蓋瀏覽器的 Core Web Vitals（LCP、INP、CLS、頁面大小）、API endpoint 的延遲百分位數，以及 build/測試的回饋時間，並把前後比較結果存在由 git 追蹤的 .ecc/benchmarks JSON 裡。檢查頁面速度、回應「感覺很慢」的回報、驗證上線的效能目標，或比較技術堆疊的替代方案時使用。
license: MIT
metadata:
  origin: ECC
---

# Benchmark：效能基準線與回歸偵測

## 何時使用

- PR 前後，量測對效能的影響
- 為專案建立效能基準線
- 使用者回報「感覺很慢」的時候
- 上線前，確認有達到效能目標
- 拿你的技術堆疊跟替代方案做比較

## 運作方式

### 模式 1：頁面效能

透過瀏覽器 MCP 量測真實的瀏覽器指標：

```
1. 導覽到每個目標 URL
2. 量測 Core Web Vitals：
   - LCP (Largest Contentful Paint) — 目標 < 2.5s
   - CLS (Cumulative Layout Shift) — 目標 < 0.1
   - INP (Interaction to Next Paint) — 目標 < 200ms
   - FCP (First Contentful Paint) — 目標 < 1.8s
   - TTFB (Time to First Byte) — 目標 < 800ms
3. 量測資源大小：
   - 頁面總大小（目標 < 1MB）
   - JS bundle 大小（目標 < 200KB，gzip 後）
   - CSS 大小
   - 圖片大小
   - 第三方 script 大小
4. 計算網路請求數
5. 檢查會阻擋渲染的資源
```

### 模式 2：API 效能

對 API endpoint 做 benchmark：

```
1. 每個 endpoint 打 100 次
2. 量測：p50、p95、p99 延遲
3. 追蹤：回應大小、狀態碼
4. 在負載下測試：10 個並行請求
5. 對照 SLA 目標比較
```

### 模式 3：Build 效能

量測開發的回饋迴圈：

```
1. 冷 build 時間
2. Hot reload 時間（HMR）
3. 測試套件的執行時間
4. TypeScript 檢查時間
5. Lint 時間
6. Docker build 時間
```

### 模式 4：前後比較

在修改前後各跑一次，量測影響：

```
/benchmark baseline    # 儲存目前的指標
# ... 進行修改 ...
/benchmark compare     # 跟基準線比較
```

輸出：
```
| Metric | Before | After | Delta | Verdict |
|--------|--------|-------|-------|---------|
| LCP | 1.2s | 1.4s | +200ms | WARNING: WARN |
| Bundle | 180KB | 175KB | -5KB | ✓ BETTER |
| Build | 12s | 14s | +2s | WARNING: WARN |
```

## 輸出

基準線以 JSON 儲存在 `.ecc/benchmarks/`。由 git 追蹤，讓團隊共用基準線。

## 整合

- CI：每個 PR 都跑 `/benchmark compare`
- 搭配 `/canary-watch` 做部署後的監控
- 搭配 `/browser-qa` 做完整的出貨前檢查表
