---
name: to-spec
description: "把目前的對話變成一份 spec，並發佈到專案的 issue tracker：不訪談，只綜合你們已經討論過的內容。"
disable-model-invocation: true
---

這個 skill 會拿目前的對話 context 和你對 codebase 的理解，產出一份 spec。**不要**訪談使用者；只綜合你已經知道的東西。

issue tracker 和 triage 標籤詞彙應該已經提供給你了。如果沒有，叫使用者去跑 `/setup-matt-pocock-skills`。

## 流程

1. 如果還沒探索過，就先探索 repo，了解 codebase 的現況。整份 spec 都用專案領域詞彙表的詞彙，並尊重你要動的那一區的任何 ADR。

2. 勾勒出你打算測試這個功能的 seam。優先用既有的 seam，不要新建。用盡可能高的 seam。如果需要新的 seam，就在你能找到的最高點提出。整個 codebase 的 seam 越少越好，理想的數量是一個。

跟使用者確認這些 seam 符合他們的預期。

3. 用下面的範本寫 spec，然後發佈到專案的 issue tracker。套上 `ready-for-agent` triage 標籤，不需要再額外 triage。

<spec-template>

## Problem Statement（問題陳述）

使用者面臨的問題，從使用者的角度來寫。

## Solution（解決方案）

問題的解決方案，從使用者的角度來寫。

## User Stories（使用者故事）

一份很長的、有編號的 user story 清單。每個 user story 的格式如下：

1. 身為<角色>，我想要<功能>，這樣<好處>

<user-story-example>
1. 身為行動銀行的客戶，我想要看到各個帳戶的餘額，這樣我可以對自己的支出做出更有根據的決定
</user-story-example>

這份 user story 清單要極度詳盡，涵蓋這個功能的所有面向。

## Implementation Decisions（實作決策）

已經做出的實作決策清單。可以包含：

- 會建立/修改的 module
- 那些會被修改的 module 的介面
- 開發者給的技術釐清
- 架構決策
- Schema 變更
- API 契約
- 具體的互動

**不要**包含具體的檔案路徑或程式碼片段。它們很快就可能過時。

例外：如果 prototype 產生了某個片段，它比文字更精確地編碼了一項決策（state machine、reducer、schema、型別形狀），就把它 inline 放在相關的決策裡，並簡短註明它來自 prototype。只留下決策含量高的部分，不要放可以跑的 demo，只放重要的那幾段。

## Testing Decisions（測試決策）

已經做出的測試決策清單。包含：

- 說明什麼是好測試（只測外部行為，不測實作細節）
- 哪些 module 會被測試
- 測試的先例（也就是 codebase 裡類似類型的測試）

## Out of Scope（範圍外）

說明哪些事情不在這份 spec 的範圍內。

## Further Notes（補充說明）

關於這個功能的任何其他補充。

</spec-template>
