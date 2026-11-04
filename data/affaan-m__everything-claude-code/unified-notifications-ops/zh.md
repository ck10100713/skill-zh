---
name: unified-notifications-ops
description: 把通知當成一條 ECC 原生的工作流來運作，涵蓋 GitHub、Linear、桌面通知、hook 和已連接的通訊管道。當真正的問題是警報路由、去重、升級或收件匣太亂時使用。
metadata:
  origin: ECC
---

# Unified Notifications Ops

當真正的問題不是少了一個提醒時，就用這個 skill。真正的問題是通知系統太零碎。

工作是把散落各處的事件，變成一個操作者介面，具備：
- 清楚的嚴重程度
- 清楚的負責人
- 清楚的路由
- 清楚的後續動作

## 何時使用

- 使用者想要一條跨 GitHub、Linear、本機 hook、桌面通知、聊天或 email 的統一通知通道
- CI 失敗、review 請求、issue 更新和操作者事件，都到達彼此不相連的地方
- 目前的設定製造的是雜訊，不是行動
- 使用者想把重疊的通知 branch 或待辦提案，整合成一條 ECC 原生的通道
- workspace 已經有 hook、MCP 或已連接的工具，但沒有一致的通知政策

## 優先使用的介面

從已經存在的東西開始：
- GitHub 的 issue、PR、review、留言和 CI
- Linear 的 issue/專案動態
- 本機的 hook 事件和 session 生命週期訊號
- 桌面通知的基本元件
- 真的存在時，已連接的 email/聊天介面

優先用 ECC 原生的編排，不要叫使用者採用另一個獨立的通知產品。

## 不可妥協的規則

- 絕對不要暴露 token、祕密、webhook 祕密或內部識別碼
- 要把這幾項分開：
  - 事件來源
  - 嚴重程度
  - 路由管道
  - 操作者動作
- 打斷的成本不明確時，預設用摘要優先
- 不要把每個事件都 fan out 到每個管道
- 如果真正的解法是更好的 issue 分流、hook 政策或專案流程，就明確說出來

## 事件管線

把這條通道當成：

1. **Capture** 事件
2. **Classify** 緊急程度和負責人
3. **Route** 到正確的管道
4. **Collapse** 重複和低訊號的反覆
5. **Attach** 下一個操作者動作

目標是更少、更好的通知。

## 預設的嚴重程度模型

| 等級 | 範例 | 預設處理 |
| --- | --- | --- |
| Critical | 預設 branch 的 CI 壞了、安全問題、被擋住的 release、失敗的 deploy | 立刻打斷 |
| High | 被要求 review、PR 失敗、卡住負責人的交接 | 當天警報 |
| Medium | issue 狀態變更、值得注意的留言、待辦動態 | 摘要或佇列 |
| Low | 重複的成功、例行的反覆、多餘的生命週期標記 | 抑制或折疊 |

如果 workspace 沒有嚴重程度模型，在提出自動化之前先建一個。

## 工作流

### 1. 盤點目前的介面

列出：
- 事件來源
- 目前的管道
- 會發出警報的既有 hook/script
- 同一個事件的重複路徑
- 重要的事沒有被顯示出來的靜默失敗情況

指出 ECC 已經擁有什麼。

### 2. 決定什麼值得打斷

對每一類事件，回答：
- 誰需要知道？
- 他們需要多快知道？
- 這應該打斷、批次處理，還是只記錄？

使用這些預設：
- release、CI、安全和卡住負責人的事件要打斷
- 中等訊號的更新用摘要
- 遙測和低訊號的生命週期標記只記錄

### 3. 先收掉重複，再加管道

找出：
- 同一個 PR 事件同時出現在 GitHub、Linear 和本機 log
- 同一個失敗重複的 hook 通知
- 應該被摘要、而不是原封不動轉發的留言或狀態反覆
- 彼此重複、卻沒有提供更好行動路徑的管道

優先採用：
- 一份標準摘要
- 一個負責人
- 一個主要管道
- 一條備援路徑

### 4. 設計 ECC 原生的工作流

對每個真實的通知需求，定義：
- **source**
- **gate**
- **shape**：即時警報、摘要、佇列，或只放在 dashboard
- **channel**
- **action**

如果 ECC 已經有這個基本元件，優先用：
- skill 做操作者分流
- hook 做自動發出/強制執行
- agent 做委派的分類
- 只有在真的缺少橋接時，才用 MCP/connector

### 5. 回傳偏向行動的設計

結尾要寫：
- 要保留什麼
- 要抑制什麼
- 要合併什麼
- ECC 接下來應該包裝什麼

## 輸出格式

```text
CURRENT SURFACE
- sources
- channels
- duplicates
- gaps

EVENT MODEL
- critical
- high
- medium
- low

ROUTING PLAN
- source -> channel
- why
- operator owner

CONSOLIDATION
- suppress
- merge
- canonical summaries

NEXT ECC MOVE
- skill / hook / agent / MCP
- exact workflow to build next
```

## 建議規則

- 寧可一條強的通道，也不要很多條弱的
- 中等和低訊號的更新優先用摘要
- 訊號應該自動發出時，優先用 hook
- 工作是分流、路由和先 review 再決定時，優先用操作者 skill
- 根本原因是待辦 / PR 協調、而不是警報時，優先用 `project-flow-ops`
- 使用者首先需要來源盤點時，優先用 `workspace-surface-audit`
- 如果桌面通知就夠了，就不要發明不必要的外部橋接

## 適合的使用情境

- 「我們有 GitHub、Linear 和本機 hook 的警報，但沒有單一的操作者流程」
- 「我們的 CI 失敗很吵，大家都不理它」
- 「我想要一套橫跨 Claude、OpenCode 和 Codex 介面的通知政策」
- 「搞清楚什麼該打斷、什麼該放進摘要」
- 「把重疊的通知 PR 點子整合成一條標準的 ECC 通道」

## 相關 Skills

- `workspace-surface-audit`
- `project-flow-ops`
- `github-ops`
- `knowledge-ops`
- `customer-billing-ops`：當通知的痛點是帳務/客戶營運，而不是工程時使用
