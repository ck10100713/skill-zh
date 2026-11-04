---
name: ralphinho-rfc-pipeline
description: 把 RFC 拆成多 agent 執行的 DAG：分解成有依賴關係和驗收測試的工作單元，每個單元各自做研究、規劃、實作、測試和 review，再透過 merge queue（branch 先 rebase）合併，最後做整個系統的驗證。功能大到單一 agent 一次做不完、要編排 RFC 驅動的多 agent 執行，或管理多個 agent 產出單元的 merge queue 時使用。
metadata:
  origin: ECC
---

# Ralphinho RFC Pipeline

靈感來自 [humanplane](https://github.com/humanplane) 風格的 RFC 分解模式和多單元編排工作流程。

功能大到單一 agent 一次做不完，必須拆成可以獨立驗證的工作單元時，使用這個 skill。

## Pipeline 階段

1. RFC 接收
2. DAG 分解
3. 單元分派
4. 單元實作
5. 單元驗證
6. Merge queue 與整合
7. 最終系統驗證

## 單元規格範本

每個工作單元要包含：
- `id`
- `depends_on`
- `scope`
- `acceptance_tests`
- `risk_level`
- `rollback_plan`

## 複雜度分級

- Tier 1：單檔隔離的修改，測試是確定性的
- Tier 2：多檔行為變更，整合風險中等
- Tier 3：schema／auth／效能／安全相關變更

## 每個單元的品質 Pipeline

1. 研究
2. 實作計畫
3. 實作
4. 測試
5. review
6. 可合併報告

## Merge Queue 規則

- 依賴還有未解決的失敗時，絕對不要合併該單元。
- 單元 branch 一律 rebase 到最新的整合 branch 上。
- 每次排隊合併之後，都要重跑整合測試。

## 復原

單元卡住時：
- 從進行中的 queue 剔除
- 把已找到的結果做快照
- 重新產生縮小範圍的單元
- 用更新後的限制條件重試

## 輸出

- RFC 執行紀錄
- 單元計分卡
- 依賴圖快照
- 整合風險摘要
