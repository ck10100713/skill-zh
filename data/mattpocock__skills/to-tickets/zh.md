---
name: to-tickets
description: 把計畫、spec 或目前的對話拆成一組 tracer-bullet ticket，每張都宣告自己的 blocking 關係，發佈到設定好的 tracker（在本地是每張 ticket 一個檔案，把關係寫成文字；在真正的 tracker 上則用原生的 blocking 連結）。
disable-model-invocation: true
---

# 拆成 Ticket

把計畫、spec 或對話拆成一組 **ticket**：tracer-bullet 的垂直切片，每張都宣告**擋住**它的 ticket。

issue tracker 和 triage 標籤詞彙應該已經提供給你了。如果沒有，叫使用者去跑 `/setup-matt-pocock-skills`。

## 流程

### 1. 蒐集 context

從對話 context 裡已經有的東西著手。如果使用者傳了參照（spec 路徑、issue 編號或 URL）當參數，就抓下來，讀完整的內容和留言。

### 2. 探索 codebase（選用）

如果還沒探索過 codebase，就探索一下，了解程式碼的現況。ticket 的標題和說明要用專案領域詞彙表的詞彙，並尊重你要動的那一區的 ADR。

找找有沒有機會先對程式碼做 prefactor，讓實作更容易。「先讓改動變容易，再做那個容易的改動。」

### 3. 擬定垂直切片

把工作拆成 **tracer bullet** ticket。

<vertical-slice-rules>

- 每個切片都切出一條窄但**完整**的路徑，穿過每一層（schema、API、UI、測試）：是垂直的，**不是**只切其中一層的水平切片
- 完成的切片可以單獨 demo 或驗證
- 每個切片的大小要能放進單一個全新的 context window
- 任何 prefactor 都要先做

</vertical-slice-rules>

幫每張 ticket 標出它的 **blocking 關係**：必須先完成才能開始它的其他 ticket。沒有 blocker 的 ticket 可以立刻開始。

**大範圍重構是垂直切片的例外。** **大範圍重構（wide refactor）** 是指單一機械式的改動（重新命名欄位、替共用符號改型別），它的**波及範圍**散布到整個 codebase，所以一次編輯就會同時弄壞數千個呼叫點，沒有任何垂直切片能讓它維持綠燈。不要硬塞成 tracer bullet；把它排成 **expand–contract**。先 expand：把新的形式加在舊的旁邊，什麼都不會壞。接著依波及範圍的大小分批（每個 package、每個目錄）把呼叫點遷移過去，每一批自己是一張 ticket，被 expand 那張擋住，因為舊的形式還在，所以 CI 能一批接一批保持綠燈。最後 contract：等沒有任何呼叫端了，就把舊的形式刪掉，放在一張被所有 migrate 批次擋住的 ticket 裡。如果連分批都沒辦法單獨保持綠燈，就維持這個順序，但讓它們共用一個整合 branch，並讓它們全部擋住最後一張整合與驗證的 ticket；只有在那裡才保證是綠燈。

### 4. 考考使用者

把提議的拆解結果用編號清單呈現。每張 ticket 都顯示：

- **Title**：簡短的描述性名稱
- **Blocked by**：哪些其他 ticket（如果有的話）必須先完成
- **What it delivers**：這張 ticket 讓什麼端到端的行為可以運作

問使用者：

- 粒度感覺對嗎？（太粗 / 太細）
- blocking 關係對嗎：每張 ticket 只依賴真正會擋住它的 ticket 嗎？
- 有沒有哪些 ticket 該合併或再拆細？

反覆調整，直到使用者同意這個拆解。

### 5. 把 ticket 發佈到設定好的 tracker

發佈核准的 ticket。**怎麼發**取決於 `/setup-matt-pocock-skills` 設定的 tracker；兩種情況的 ticket 都一樣，只有 blocking 關係的形式不同：

- **本地檔案** → 每張 ticket 寫一個檔案，放在 `.scratch/<feature-slug>/issues/<NN>-<slug>.md`，依依賴順序（blocker 在前）從 `01` 開始編號。每個檔案的「Blocked by」列出它依賴的編號/標題。使用下面每張 ticket 的檔案範本：一張 ticket 一個檔案，絕對不要合併成單一檔案。
- **真正的 issue tracker（GitHub、Linear 等）** → 依依賴順序（blocker 在前）每張 ticket 發佈一個 issue，這樣每張 ticket 的 blocking 關係才能參照真正的識別碼。平台有原生的 blocking 關係就用它；沒有的話，就把每張 ticket 的「Blocked by」設成擋住它的 issue。如果來源是既有的 issue，就讓每張 ticket 成為它的 sub-issue（用 tracker 文件裡的操作）。除非另有指示，否則套上 `ready-for-agent` triage 標籤；這些 ticket 從設計上就是 agent 可以接手的。

處理**前線（frontier）**：所有 blocker 都已完成的 ticket。對純線性的鏈來說，就是從上到下。

**不要**關閉或修改任何 parent issue。

<local-ticket-template>

# <NN>: <Ticket 標題>

**What to build（要做什麼）：** 這張 ticket 讓什麼端到端的行為可以運作，從使用者的角度來寫，不是逐層列出的實作清單。

**Blocked by（被誰擋住）：** 擋住這張的 ticket 的編號/標題，或是「None (can start immediately)」。

**Status（狀態）：** ready-for-agent

- [ ] 驗收條件 1
- [ ] 驗收條件 2

</local-ticket-template>

<issue-template>

## Parent

tracker 上 parent issue 的參照（如果來源是既有的 issue；否則省略這一節）。

## What to build

這張 ticket 讓什麼端到端的行為可以運作，從使用者的角度來寫，不是逐層的實作。

## Acceptance criteria

- [ ] 條件 1
- [ ] 條件 2

## Blocked by

- 每張擋住它的 ticket 的參照，或是「None (can start immediately)」。如果 blocker 已經設成原生的關係，就省略這一節。

</issue-template>

不管哪種形式，都要避開具體的檔案路徑或程式碼片段：它們很快就會過時。例外：如果 prototype 產生了某個片段，它比文字更精確地編碼了一項決策（state machine、reducer、schema、型別形狀），就 inline 放進去，並簡短註明它來自 prototype。只留下決策含量高的部分，不要放可以跑的 demo，只放重要的那幾段。
