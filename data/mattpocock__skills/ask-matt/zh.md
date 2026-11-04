---
name: ask-matt
description: 問問哪個 skill 或流程適合你的情況。這個 repo 裡所有 skill 的路由器。
disable-model-invocation: true
---

# 問 Matt

你不可能記得每個 skill，所以直接問。

在說明某個 skill 做什麼、或建議跳過某個步驟之前，先讀那個 skill 的 SKILL.md：這裡的摘要只是讓你抓個方向。

**流程（flow）** 是穿過這些 skill 的一條路徑。大多數路徑都沿著同一條**主流程**走，另外有兩個**匯入匝道（on-ramp）** 匯進來。其他的要嘛是獨立的，要嘛是在底下運作的詞彙層。

## 主流程：想法 → 上線

大部分工作走的路線。你有個想法，想把它做出來。

1. **`/grill-with-docs`** 用訪談把想法磨利。只要你是**在工作目錄裡工作**，就從這裡開始：它是有狀態的，會把學到的東西留在 `GLOSSARY.md` 和 ADR 裡。（沒有工作目錄？改用 `/grill-me`，在獨立項目裡有介紹。兩者跑的是同一個 `/grilling` 基本元件；`grill-with-docs` 是會留下紙本紀錄的那個，所以只要有 repo 可以放，它就是兩者中比較好的。）
2. **分支：每個問題都能在對話裡解決嗎？** 如果某個問題需要一個可以跑的答案（狀態、商業邏輯、一個你得親眼看的 UI），就繞道做 prototype，兩個方向都用 **`/handoff`** 搭橋（prototype 住在它自己的目錄，這正是 `/handoff` 的用途；見階段邊界）：
   - 用 **`/handoff`** 交出去，然後針對那個檔案開一個全新的 session，
   - 用 **`/prototype`** 以用完即丟的程式碼來回答問題，
   - 用 **`/handoff`** 把你學到的東西交回來，並從原本的想法討論串參照它。
3. **分支：這是需要多個 session 的建置嗎？**
   - **是** → **`/to-spec`**（把討論串變成 spec），然後 **`/to-tickets`** 把它拆成 tracer-bullet ticket，每張都宣告它的 **blocking 關係**。接著用兩種方式之一處理這些 ticket：
     - 每張 ticket 用 **`/implement`**，而且**每張之間都 `/clear` context**。在本地 tracker 上，那是 `.scratch/<feature>/issues/` 底下每張 ticket 一個檔案，手動依 blocker 優先的順序處理；在真正的 tracker 上，這些關係會變成原生的 blocking 連結，所以任何 blocker 都已完成的 ticket 都可以被接手。每張 ticket 都是獨立完整的，所以上一張的 context 是可以丟掉的。
     - 整份 spec 用 **`/implement-spec`** 一次跑完。它把 ticket 當成**任務圖（task graph）** 來讀，對準備好的**前線（frontier）** 平行執行 implementer subagent，並把所有東西落在一個**整合 branch（integration branch）** 上。當你寧可統籌整個建置，而不想自己一張張推動時，就用它。
   - **否** → 就在這裡、同一個 context window 直接 **`/implement`**。

   不管哪種，程式碼都是靠驅動 **`/tdd`**（一次一個 red-green 切片）建出來的，最後以 **`/code-review`** 收尾，這是對 diff 做的兩個面向（Standards + Spec）的 review。`/implement` 每張 ticket 都會跑這兩個；`/implement-spec` 的 implementer 各自驅動 `/tdd`，並對整合 branch 跑一次 `/code-review`。當你只是想用測試先行的方式建出某個具體行為、不需要完整 spec 時，單獨用 **`/tdd`**；當你想針對某個固定點 review 一個 branch 或 PR 時，單獨用 **`/code-review`**。

   當工作以 pull request 的形式提交時，**`/pr`** 負責塑造本文：能顯示這次改動的最小視覺化、證明它能運作的前後對照證據，以及一個單向門或雙向門的判斷。它是模型呼叫的，所以 agent 每次寫 PR 時都會去用它。

4. **`/retro`** 把迴圈收起來。建置完之後，尤其是出了狀況的那次，它會回顧整個 session，並建議對 agent 的**環境**做哪些改變，而不是程式碼：導覽指標、自動化檢查、`/code-review` 強制執行的編碼標準、引導檔案、工具。機械式的錯誤變成 deterministic 的檢查；需要判斷的變成編碼標準。下一次建置就從更好的環境開始。

### Context 衛生

第 1 到 3 步要待在**同一個沒有中斷的 context window**（在 `/to-tickets` 之後才 compact 或 clear），這樣 grilling、spec 和 ticket 才會建立在同一套思考之上。之後每個 `/implement` 都從全新的狀態開始，照著 ticket 工作。`/retro` 要在它所回顧的那個 session 裡執行，在你 clear 之前；clear 之後，就改成把它指向那個 session 的紀錄。

這件事的限制是**[smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)**：模型還能清楚推理的那個 window（在最先進的模型上約 150k token）。如果在 `/to-tickets` 之前 session 就接近它，不要在退化的狀態下硬撐；在最近的階段邊界 `/compact` 然後繼續（見階段邊界）。

## 匯入匝道

產生工作的起始情境，然後匯進主流程。

- **Bug 和需求一直堆積** → **`/triage`**。它讓 issue 依著 triage 角色流轉，並產出 agent 可以直接接手的 issue，之後由 **`/implement`** 撿起來做。

  triage 只用在**不是你自己建立的** issue：bug 回報、進來的功能需求、任何未經加工直接送來的東西。`/to-tickets` 產出的 ticket 已經是 agent 可以直接接手的，所以**不要 triage 它們**。

- **有東西壞了** → **`/diagnosing-bugs`**。給難搞的 bug：第一眼看不出來的、時有時無的 flake、在兩個已知良好狀態之間悄悄混進來的退步。它在擁有**緊湊的回饋迴圈**（一個已經會在*這個* bug 上變紅的指令）之前，拒絕建立理論，然後用回歸測試來修。修好之後，在同一個 session 執行 **`/retro`**，問問什麼本來可以防止這個 bug；如果真正的發現是沒有好的 seam 可以把它鎖住，那就是 **`/improve-codebase-architecture`** 的工作。

- **一個龐大、模糊的投入：全新的專案或龐大的功能建置，大到一個 session 裝不下** → **`/wayfinder`**，這裡最吃認知力的流程。當從這裡到目的地的路還看不見時，它會在 issue tracker 上畫出由**決策 ticket** 組成的**共享地圖**，一次解決一張，產出的是**決策，不是成品**，直到迷霧被推開、路清楚為止。**`/grill-with-docs`** 磨利的是你一個 session 抓得住的想法，wayfinder 則是給你抓不住的想法，它比較慢也比較密，所以只留給那種情況用，絕對不要用在範圍明確的功能上。

  當地圖清楚了，**它是交接，不是建置**：在 **`/to-spec`** 匯進主流程，它會把地圖裡連結的決策塌縮成可以建置的計畫，然後照常走 `/to-tickets` 和 `/implement`。把地圖直接接到 `/implement` 會跳過那個塌縮，把連結的細節丟掉，所以只有在這個投入結果真的很小時，才直接走 `/implement`。

## Codebase 健康

不是功能工作，只是維護。

- **`/improve-codebase-architecture`** 在你有空檔時就跑，讓 codebase 保持對 agent 好操作的狀態。它會浮現**加深的機會**；選一個就是_產生一個想法_，你可以在 `/grill-with-docs` 把它帶進主流程。它是找出候選項的勘查；**`/codebase-design`**（見下面）則是你設計選定的那一個時所用的工作台。

## 底層的詞彙

兩個由模型呼叫的參考，在其他 skill *底下*運作，各自是它那套詞彙的單一事實來源。當問題出在**用字**而不是流程時，直接用它們；或者讓上面的 skill 把它們拉進來。

- **`/domain-modeling`**：磨利專案的*領域*語言：挑戰模糊的術語、解決一詞多義的字（「account」身兼三職）、把難以回頭的決策記錄成 ADR。這是 `/grill-with-docs` 為了讓 `GLOSSARY.md` 維持乾淨的詞彙表而推動的主動紀律。
- **`/codebase-design`** 是深模組的詞彙（module、interface、depth、seam、adapter、leverage、locality），用來設計 module 的*形狀*：在乾淨的 seam 上，小介面背後藏著大量行為。`/tdd` 和 `/improve-codebase-architecture` 都用這套詞彙。

## 階段邊界

**階段（phase）** 是 session 裡的一塊工作：grilling、實作、QA。在兩個階段之間的**邊界**，你有五個選項，而在它們之間做選擇，是這整張地圖裡最模糊的決策：

- **Continue**：留在原地。不花成本，也不損失任何東西。
- **`/clear`**：清空 window，當這裡的任何東西都跟接下來無關時。
- **`/handoff`** 寫一份可攜的 markdown 檔。範圍很窄：只用在**新的 harness**、**新的目錄**、**同事**，或是**階段中途**分岔出去做的支線任務。它買到的是可攜性。
- **Subagent**：把範圍緊縮的任務送到它自己的 window，並拿回一份報告。
- **`/compact`** 壓縮這個 context，並用它當種子開一個全新的 session。這是**預設**，在決策樹的底部，而不是第一個該伸手去拿的。

讀 [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) 了解有順序的決策樹：五個問題、每個分支背後的推理，以及為什麼第一手來源的成本讓 **Continue** 是第一個該排除的選項。要在邊界**上**做決定；階段中途，就繼續，或把剩下的拆給 subagent。

## 獨立項目

完全不在主流程上。

- **`/grill-me`**：跟 `/grill-with-docs` 一樣毫不留情的訪談，但是**無狀態**：它不在本地儲存任何東西，也不建立 `GLOSSARY.md`。當你**不是在工作目錄裡工作**時用它（磨利計畫、設計、一篇文章，任何底下沒有 repo 的東西）。如果你在工作目錄裡，就改用 `/grill-with-docs`：它跑同樣的訪談，還會留下紙本紀錄，所以嚴格來說它比較好。
- **`/grilling`** 是訪談的基本元件本身：回合、前線、事實是 agent 的工作而決策是你的。`/grill-me` 和 `/grill-with-docs` 是兩個有名字的入口，而 `/triage`、`/wayfinder` 和 `/improve-codebase-architecture` 內部都會跑它。只有在你想要完全沒有外包裝的訪談時，才直接用它。
- **`/prototype`** 是個小小的、用完即丟的程式，回答一個設計問題：這個狀態模型感覺對嗎，或這個 UI 該長什麼樣子。用完即丟是對程式碼寫法的限制，不是承諾要銷毀它：答案會併進真正的程式碼，而 prototype 本身會被留存成**第一手來源**，放在 main 以外的 `prototype/<name>` branch 上，並從實作的 issue 指向它。它就是主流程第 2 步的繞道，但任何時候設計問題很難在紙上解決，都可以用它。
- **`/research`**：把查資料的苦工委派給**背景 agent**：它對照**第一手來源**調查一個問題，然後在 repo 裡留下一份附出處的 Markdown 檔。它在讀的時候你可以繼續工作。它產出的檔案是你可以在 `/grill-with-docs` 帶*進*主流程的東西，因為研究是餵養思考，而不是取代它。
- **`/to-questionnaire`** 用在擋住你的東西不在你的腦袋或 codebase 裡，而是在**別人**那裡的時候，它會寫一份問卷讓對方填。它是 `/grill-me` 的反面：它不是針對主題訪談你，而是針對**寄送**（寄給誰、你需要對方回什麼）訪談你，再把問題對準那個落差。回來的東西是 `/grill-with-docs` 或 `/to-spec` 的素材。
- **`/wizard`** 用在只有**人類**才能做的步驟：佈建基礎設施、設定憑證或 CI secret、點過不熟悉的第三方 dashboard、執行一次性的遷移或切換。它會產生一支互動式 bash 腳本，打開每個 URL、擷取每個值，並寫進 `.env` 和 GitHub secrets，這樣這套流程就不再是你每次都要向 agent 重新解釋的東西。由模型呼叫，所以 agent 一撞上只有你能通過的牆就會去用它。如果 agent 自己就能做，它就該自己做；這是給人類真的在迴圈裡的情況。
- **`/wait-what`** 是對沒講到點上的訊息的補救。在對話中途、在任何其他 skill 裡面使用它，agent 就會把它剛才說的重新 pitch 一次，補上你缺少的 context，用白話英文，並使用 `GLOSSARY.md` 的詞彙。它是事後補救；`/grill-with-docs` 才是事前的解法，因為早期就談好的共用語言，才能讓行話一開始就不會出現。
- **`/teach`**：把目前的目錄當成有狀態的 workspace，跨好幾個 session 學習一個概念。
- **`/writing-for-agents`** 是撰寫 agent 會讀取的文件的參考：skill、AGENTS.md、被指標指到的文件。

## 前置條件

**`/setup-matt-pocock-skills`**：在你的第一個工程流程之前先跑，設定其他 skill 預設存在的 issue tracker、triage 標籤和文件版面配置。自訂的 issue tracker 也行。
