---
name: testing-strategy
description: 設計測試策略與測試計畫。當使用者說「how should we test」「test strategy for」「write tests for」「test plan」「what tests do we need」，或需要測試方法、覆蓋率、測試架構的協助時觸發。
---

# 測試策略

設計有效的測試策略，在覆蓋率、速度和維護成本之間取得平衡。

## 測試金字塔

```
        /  E2E  \         Few, slow, high confidence
       / Integration \     Some, medium speed
      /    Unit Tests  \   Many, fast, focused
```

## 依元件類型決定策略

- **API endpoint**：業務邏輯用 unit test，HTTP 層用整合測試，給下游消費者的用 contract test
- **資料 pipeline**：輸入驗證、轉換正確性、冪等性測試
- **前端**：元件測試、互動測試、視覺回歸、無障礙
- **基礎設施**：smoke test、chaos engineering、load test

## 該涵蓋什麼

重點放在：業務關鍵路徑、錯誤處理、邊界情況、安全邊界、資料完整性。

可以跳過：單純的 getter/setter、框架本身的程式碼、一次性腳本。

## 輸出

產出一份測試計畫，包含：要測什麼、每個範圍用哪種測試類型、覆蓋率目標，以及範例測試案例。同時指出現有覆蓋率的缺口。
