---
name: product-capability
description: 把 PRD 的意圖、roadmap 的需求或產品討論，轉成可以直接實作的 capability 計畫，在多服務的工作開始之前，把限制、不變式、介面和尚未解決的決策攤開來。使用者需要 ECC 原生的 PRD 轉 SRS 流程，而不是含糊的規劃文字時使用。
metadata:
  origin: ECC
---

# Product Capability

這個 skill 把產品意圖轉成明確的工程限制。

當缺口不是「我們該做什麼？」，而是「實作開始之前，到底哪些事情必須成立？」的時候，就用它。

## 何時使用

- 已經有 PRD、roadmap 項目、討論或創辦人的筆記，但實作上的限制還是隱性的
- 某個功能橫跨多個服務、repo 或團隊，寫程式之前需要一份 capability 契約
- 產品意圖很清楚，但架構、資料、生命週期或政策上的影響還很模糊
- 資深工程師在 review 時，一直在重複講同樣那些隱藏的假設
- 你需要一份能跨 harness 和 session 留存、可重複使用的產出物

## 標準產出物

如果 repo 裡有長期維護的產品背景檔案，例如 `PRODUCT.md`、`docs/product/` 或 program-spec 目錄，就更新在那裡。

如果還沒有 capability manifest，就用下面這個範本建立一份：

- `docs/examples/product-capability-template.md`

目標不是再建立另一套規劃機制。目標是讓隱藏的 capability 限制變成長期留存、可重複使用的東西。

## 不可妥協的規則

- 不要發明產品事實。未解決的問題要明確標出來。
- 把使用者看得到的承諾，跟實作細節分開。
- 要點出哪些是固定的政策、哪些是架構偏好、哪些還沒決定。
- 如果需求跟 repo 現有的限制衝突，要清楚講出來，不要含糊帶過。
- 優先用一份可重複使用的 capability 產出物，不要用散落各處的臨時筆記。

## 輸入

只讀需要的東西：

1. 產品意圖
   - issue、討論、PRD、roadmap 筆記、創辦人的訊息
2. 目前的架構
   - 相關的 repo 文件、契約、schema、路由、既有的工作流程
3. 既有的 capability 背景
   - `PRODUCT.md`、設計文件、RFC、migration 筆記、營運模式文件
4. 交付上的限制
   - 認證、計費、合規、上線推出、向下相容、效能、review 政策

## 核心工作流程

### 1. 重新陳述這個 capability

把需求壓縮成一句精確的話：

- 使用者或操作者是誰
- 這個功能上線之後，多了什麼新能力
- 因為它，哪個結果會改變

如果這句話很弱，實作就會跑偏。

### 2. 釐清 capability 的限制

把實作之前必須成立的限制抽出來：

- 業務規則
- 範圍邊界
- 不變式
- 信任邊界
- 資料所有權
- 生命週期的轉換
- 上線推出 / migration 的要求
- 失敗與復原的預期

這些東西往往只存在於資深工程師的記憶裡。

### 3. 定義面向實作的契約

產出一份 SRS 風格的 capability 計畫，包含：

- capability 摘要
- 明確的非目標
- 參與者與介面
- 必要的狀態與轉換
- 介面 / 輸入 / 輸出
- 對資料模型的影響
- 安全 / 計費 / 政策的限制
- 可觀測性與操作者的需求
- 卡住實作的未解決問題

### 4. 轉成執行

用確切的交接收尾：

- 可以直接實作
- 需要先做架構 review
- 需要先釐清產品問題

有用的話，指向下一條 ECC 原生的流程：

- `project-flow-ops`
- `workspace-surface-audit`
- `api-connector-builder`
- `dashboard-builder`
- `tdd-workflow`
- `verification-loop`

## 輸出格式

依下面的順序回傳結果：

```text
CAPABILITY
- one-paragraph restatement

CONSTRAINTS
- fixed rules, invariants, and boundaries

IMPLEMENTATION CONTRACT
- actors
- surfaces
- states and transitions
- interface/data implications

NON-GOALS
- what this lane explicitly does not own

OPEN QUESTIONS
- blockers or product decisions still required

HANDOFF
- what should happen next and which ECC lane should take it
```

## 好的結果

- 產品意圖現在已經具體到可以實作，不必在 PR 中途才重新發現隱藏的限制。
- 工程 review 有一份長期留存的產出物，不用靠記憶或 Slack 的上下文。
- 產出的計畫可以跨 Claude Code、Codex、Cursor、OpenCode 和 ECC 2.0 的規劃介面重複使用。
