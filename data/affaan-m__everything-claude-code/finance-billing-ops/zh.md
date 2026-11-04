---
name: finance-billing-ops
description: 以證據為先的營收、定價、退款、團隊計費與計費模型真相工作流，用於 ECC。在使用者想要銷售快照、定價比較、重複扣款診斷，或有程式碼支撐的計費實況，而不是通用的支付建議時使用。
metadata:
  origin: ECC
---

# Finance Billing Ops

當使用者想了解金錢、定價、退款、團隊席位邏輯，或產品的實際行為是否真的像網站與銷售文案所暗示的那樣時使用。

這比 `customer-billing-ops` 的範圍更廣。那個 skill 是用來處理客戶補救。這個 skill 是用來取得操作者所需的真相：營收狀態、定價決策、團隊計費，以及有程式碼支撐的計費行為。

## Skill 組合

相關時，把這些 ECC 原生 skill 拉進工作流：

- `customer-billing-ops`：針對特定客戶的補救與後續跟進
- `research-ops`：競爭對手定價或當前市場證據很重要時
- `market-research`：答案應該以定價建議收尾時
- `github-ops`：計費真相取決於兄弟 repo 的程式碼、backlog 或發布狀態時
- `verification-loop`：答案取決於證明 checkout、席位處理或 entitlement 行為時

## 何時使用

- 使用者問 Stripe 的銷售、退款、MRR，或最近的客戶活動
- 使用者問團隊計費、按席位計費或配額疊加，在程式碼裡是不是真的存在
- 使用者想要競爭對手的定價比較或定價模型的 benchmark
- 問題把營收事實和產品實作的真相混在一起

## 護欄

- 區分即時資料和已儲存的快照
- 分開：
  - 營收事實
  - 客戶影響
  - 有程式碼支撐的產品真相
  - 建議
- 除非實際的 entitlement 路徑真的強制執行，否則不要說「按席位」
- 不要假設重複訂閱就代表重複的價值

## 工作流

### 1. 從最新的計費證據開始

優先使用即時的計費資料。如果資料不是即時的，要明確寫出快照的時間戳。

把整體狀況正規化：

- 已付款的銷售
- 有效的訂閱
- 失敗或未完成的 checkout
- 退款
- 爭議
- 重複的訂閱

### 2. 把客戶事件和產品真相分開

如果問題是針對特定客戶，先分類：

- 重複 checkout
- 真實的團隊意圖
- 壞掉的自助控制
- 未達成的產品價值
- 失敗的付款或未完成的設定

然後把它和更廣泛的產品問題分開：

- 團隊計費真的存在嗎？
- 席位真的有被計算嗎？
- checkout 的數量會改變 entitlement 嗎？
- 網站有誇大目前的行為嗎？

### 3. 檢查有程式碼支撐的計費行為

如果答案取決於實作的真相，就檢查程式碼路徑：

- checkout
- 定價頁
- entitlement 計算
- 席位或配額處理
- installation 與 user 使用量的邏輯對比
- 計費入口或自助管理的支援

### 4. 以決策和產品缺口收尾

回報：

- 銷售快照
- 問題診斷
- 產品真相
- 建議的操作者行動
- 產品或 backlog 的缺口

## 輸出格式

```text
SNAPSHOT
- timestamp
- revenue / subscriptions / anomalies

CUSTOMER IMPACT
- who is affected
- what happened

PRODUCT TRUTH
- what the code actually does
- what the website or sales copy claims

DECISION
- refund / preserve / convert / no-op

PRODUCT GAP
- exact follow-up item to build or fix
```

## 常見陷阱

- 不要把失敗的嘗試和淨營收混為一談
- 不要只憑行銷用語就推斷有團隊計費
- 有當前證據時，不要憑記憶比較競爭對手的定價
- 不要從診斷直接跳到退款，而沒有先分類問題

## 驗證

- 答案包含即時資料的聲明或快照時間戳
- 產品真相的主張要有程式碼支撐
- 客戶影響和更廣泛的定價/產品結論要清楚分開
