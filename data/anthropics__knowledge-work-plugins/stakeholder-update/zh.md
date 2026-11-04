---
name: stakeholder-update
description: 依對象和頻率產生量身訂做的利害關係人更新。適用於撰寫給主管層的週報或月報、宣布上線、升級回報風險或阻礙，或把同一份進度轉成給高階主管的簡報、工程細節或對客戶的版本。
argument-hint: "<update type and audience>"
---

# 利害關係人更新

> 如果看到不熟悉的佔位符，或需要確認哪些工具已連接，請見 [CONNECTORS.md](../../CONNECTORS.md)。

依對象和頻率，產生量身訂做的利害關係人更新。

## 用法

```
/stakeholder-update $ARGUMENTS
```

## 工作流程

### 1. 判斷更新類型

問使用者是哪種更新：
- **Weekly（週報）**：固定頻率的更新，講進度、阻礙和下一步
- **Monthly（月報）**：較高層次的摘要，講趨勢、里程碑和策略一致性
- **Launch（上線）**：宣布功能或產品上線，附上細節和影響
- **Ad-hoc（臨時）**：針對特定情況的一次性更新（升級回報、轉向、重大決策）

### 2. 判斷對象

問更新是給誰的：
- **Executives / leadership（高階主管／領導層）**：高層次、以成果為焦點、策略性的框架、簡短
- **Engineering team（工程團隊）**：技術細節、實作背景、阻礙、需要的決策
- **Cross-functional partners（跨職能夥伴）**：適合他們脈絡的細節，聚焦共同目標和相依性
- **Customers / external（客戶／外部）**：以好處為焦點、清楚的時程、沒有內部術語
- **Board（董事會）**：以指標為導向、策略性、聚焦風險、非常精簡

### 3. 從已連接的工具拉脈絡

如果已連接 **~~project tracker**：
- 拉 roadmap 項目和里程碑的狀態
- 找出上次更新以來完成的項目
- 浮出有風險或被卡住的項目
- 拉 sprint 或迭代的進度

如果已連接 **~~chat**：
- 搜尋相關的團隊討論和決策
- 找出在頻道裡提出的阻礙或問題
- 找出非同步做出的關鍵決策

如果已連接 **~~meeting transcription**：
- 拉最近的會議記錄和討論摘要
- 找出相關會議的決策和待辦事項

如果已連接 **~~knowledge base**：
- 搜尋最近的會議記錄
- 找出決策文件或設計審查

如果沒有連接任何工具，請使用者提供：
- 自上次更新以來完成了什麼
- 目前的阻礙或風險
- 已做出或需要的關鍵決策
- 接下來會有什麼

### 4. 產生更新

用下面的範本和框架，為目標對象組織更新內容。

**給高階主管**：TL;DR、狀態顏色（G/Y/R）、與目標連結的關鍵進度、已做的決策、附緩解方案的風險、具體的請求，以及接下來的里程碑。控制在 300 字以內。

**給工程**：出貨了什麼（附連結）、進行中的是什麼（附負責人）、阻礙、需要的決策（附選項和建議）、接下來是什麼。

**給跨職能夥伴**：即將發生、會影響他們的事、你需要他們做什麼（附期限）、影響他們團隊的決策，以及開放給他們提供意見的地方。

**給客戶**：有什麼新東西（以好處的角度描述）、即將推出什麼、已知問題和替代做法，以及如何提供回饋。不用內部術語。

**給上線公告**：什麼上線了、為什麼重要、關鍵細節（範圍、可用性、限制）、成功指標、推出計畫，以及回饋管道。

### 5. 審閱與交付

產生更新之後：
- 問使用者要不要調整語氣、細節程度或強調的重點
- 提議依交付管道調整格式（email、聊天貼文、文件、簡報）
- 如果已連接 **~~chat**，提議起草要寄出的訊息

## 各對象的更新範本

### 高階主管／領導層更新
主管想要的是：策略脈絡、對照目標的進度、需要他們協助的風險、需要他們表態的決策。

**格式**：
```
Status: [Green / Yellow / Red]

TL;DR: [One sentence — the most important thing to know]

Progress:
- [Outcome achieved, tied to goal/OKR]
- [Milestone reached, with impact]
- [Key metric movement]

Risks:
- [Risk]: [Mitigation plan]. [Ask if needed].

Decisions needed:
- [Decision]: [Options with recommendation]. Need by [date].

Next milestones:
- [Milestone] — [Date]
```

**給主管的更新提醒**：
- 先講結論，不要講過程。主管要的是「我們出貨了 X，而且推動了 Y 指標」，不是「我們開了 14 次站會、解掉 23 張工單」。
- 控制在 200 字以內。他們想知道更多會自己問。
- 狀態顏色要反映**你**真正的判斷，不是你以為他們想聽的。Yellow 不是失敗，而是良好的風險管理。
- 只列你想要協助的風險。已經在處理的風險，除非他們需要知道，否則不要列。
- 請求要具體：「Decision on X by Friday」，不是「support needed」。

### 工程團隊更新
工程師想要的是：明確的優先順序、技術脈絡、已解決的阻礙、會影響他們工作的決策。

**格式**：
```
Shipped:
- [Feature/fix] — [Link to PR/ticket]. [Impact if notable].

In progress:
- [Item] — [Owner]. [Expected completion]. [Blockers if any].

Decisions:
- [Decision made]: [Rationale]. [Link to ADR if exists].
- [Decision needed]: [Context]. [Options]. [Recommendation].

Priority changes:
- [What changed and why]

Coming up:
- [Next items] — [Context on why these are next]
```

**給工程的更新提醒**：
- 連結到具體的工單、PR 和文件。工程師想點進去看細節。
- 優先順序變了，要說明原因。工程師搞懂理由之後，投入程度會比較高。
- 明確講出是什麼卡住他們，以及你正在做什麼來解除。
- 不要用不影響他們工作的資訊浪費他們的時間。

### 跨職能夥伴更新
夥伴（設計、行銷、業務、支援）想要的是：有什麼即將發生並影響他們、他們需要準備什麼、怎麼提供意見。

**格式**：
```
What's coming:
- [Feature/launch] — [Date]. [What this means for your team].

What we need from you:
- [Specific ask] — [Context]. By [date].

Decisions made:
- [Decision] — [How it affects your team].

Open for input:
- [Topic we'd love feedback on] — [How to provide it].
```

### 客戶／外部更新
客戶想要的是：有什麼新東西、即將推出什麼、對他們有什麼好處、怎麼開始用。

**格式**：
```
What's new:
- [Feature] — [Benefit in customer terms]. [How to use it / link].

Coming soon:
- [Feature] — [Expected timing]. [Why it matters to you].

Known issues:
- [Issue] — [Status]. [Workaround if available].

Feedback:
- [How to share feedback or request features]
```

**給客戶的更新提醒**：
- 不要內部術語、不要工單編號、不要技術實作細節。
- 一切都用客戶現在可以**做**什麼來描述，不要講你們蓋了什麼。
- 時程要誠實，但不要過度承諾。「Later this quarter」比一個可能錯過的日期好。
- 已知問題只有在影響客戶、而且你們有解決計畫時才提。

## 狀態回報框架

### Green / Yellow / Red 狀態

**Green（On Track，照計畫進行）：**
- 照計畫進展
- 沒有重大風險或阻礙
- 有望達成承諾和期限
- 事情真的順利時才用 Green，不要當預設值

**Yellow（At Risk，有風險）：**
- 進展比計畫慢，或有風險已經發生
- 緩解措施進行中，但結果不確定
- 沒有介入或調整範圍的話，可能會錯過承諾
- 要主動用 Yellow：越早標出風險，你的選擇越多

**Red（Off Track，偏離軌道）：**
- 嚴重落後計畫
- 有重大阻礙或風險，沒有明確的緩解方式
- 沒有重大介入（砍範圍、加資源、延長時程）就會錯過承諾
- 真的需要協助時用 Red。不要等到太遲。

### 何時改變狀態
- 看到風險的**第一個**跡象就轉 Yellow，不要等到確定情況很糟
- 你自己的選項都用盡、需要往上升級時，轉 Red
- 只有風險真正解決、而不是只是暫停時，才轉回 Green
- 改變狀態時要記錄變了什麼：「Moved to Yellow because [reason]」

## 風險溝通

### 風險管理的 ROAM 框架
- **Resolved（已解決）**：風險不再是問題。記錄是怎麼解決的。
- **Owned（已認領）**：風險已被確認，而且有人正在積極管理。寫出負責人和緩解計畫。
- **Accepted（已接受）**：風險已知，但我們選擇不做緩解就繼續。記錄理由。
- **Mitigated（已緩解）**：行動已把風險降到可接受的程度。記錄做了什麼。

### 有效溝通風險
1. **清楚說明風險**：「There is a risk that [thing] happens because [reason]」
2. **量化影響**：「If this happens, the consequence is [impact]」
3. **說明可能性**：「This is [likely/possible/unlikely] because [evidence]」
4. **提出緩解方案**：「We are managing this by [actions]」
5. **提出請求**：「We need [specific help] to further reduce this risk」

### 風險溝通的常見錯誤
- 把風險埋在好消息裡。風險重要時要放最前面。
- 含糊不清：「There might be some delays」，要具體講是什麼、多久、為什麼。
- 只講風險不講緩解方案。每個風險都該附一個計畫。
- 拖太久。早期溝通的風險是規劃的輸入；晚期溝通的風險是救火演習。

## 決策文件（ADR）

### Architecture Decision Record 格式
把重要決策記錄下來，供日後參考：

```
# [Decision Title]

## Status
[Proposed / Accepted / Deprecated / Superseded by ADR-XXX]

## Context
What is the situation that requires a decision? What forces are at play?

## Decision
What did we decide? State the decision clearly and directly.

## Consequences
What are the implications of this decision?
- Positive consequences
- Negative consequences or tradeoffs accepted
- What this enables or prevents in the future

## Alternatives Considered
What other options were evaluated?
For each: what was it, why was it rejected?
```

### 何時該寫 ADR
- 策略性的產品決策（要鎖定哪個市場區隔、要支援哪個平台）
- 重大的技術決策（架構選擇、廠商選擇、自建還是購買）
- 大家意見不同的爭議性決策（記錄理由供日後參考）
- 會限制未來選項的決策（選定一項技術、簽下合作夥伴關係）
- 你預期之後會有人質疑的決策（趁脈絡還新鮮時記下來）

### 決策文件的提醒
- 在做出決策的當下寫 ADR，不要拖到幾週後
- 寫下哪些人參與了決策、誰做了最終決定
- 脈絡要寫得充分：日後的讀者不會有今天的脈絡
- 事後證明是錯的決策也可以記錄，加上「superseded by」連結就好
- 保持簡短。一頁比五頁好。

## 會議主持

### Stand-up / 每日同步
**目的**：浮出阻礙、協調工作、維持動能。
**格式**：每個人分享：
- 自上次同步以來完成了什麼
- 接下來要做什麼
- 有什麼卡住他們

**主持提醒**：
- 控制在 15 分鐘內。如果出現討論，就移到會後。
- 聚焦在阻礙，這是站會裡價值最高的部分
- 追蹤阻礙，並跟進解決狀況
- 沒有東西需要同步就取消站會。尊重大家的時間。

### Sprint / 迭代規劃
**目的**：承諾下個 sprint 的工作。就優先順序和範圍取得共識。
**格式**：
1. 回顧：上個 sprint 出貨了什麼、延遞了什麼、砍掉了什麼
2. 優先順序：這個 sprint 最重要的是要完成什麼
3. 產能：團隊能承擔多少（把請假、on-call、會議算進去）
4. 承諾：從 backlog 選出符合產能和優先順序的項目
5. 相依性：標出任何跨團隊或外部的相依性

**主持提醒**：
- 帶著建議的優先順序來。不要要求團隊從零開始排優先順序。
- 對過度承諾要反駁。承諾少一點、穩穩交付比較好。
- 確保每個項目都有明確的負責人和明確的驗收標準。
- 標出範圍抓得太小或藏有隱藏複雜度的項目。

### 回顧會議（Retrospective）
**目的**：反思哪些做得好、哪些不好，以及要改變什麼。
**格式**：
1. 暖場：提醒團隊目標，並營造心理安全感
2. 蒐集資料：哪些做得好、哪些不好、哪些讓人困惑
3. 產生洞察：找出模式和根本原因
4. 決定行動：挑 1-3 個具體的改進，下個 sprint 試試看
5. 收尾：感謝大家誠實的回饋

**主持提醒**：
- 營造心理安全感。大家必須覺得可以安心說實話。
- 聚焦在系統和流程，不要針對個人。
- 行動項目限制在 1-3 個。超過就什麼都不會改變。
- 跟進上次回顧的行動項目。如果從來不跟進，大家就不再投入了。
- 偶爾換一下回顧的形式，避免僵化。

### 利害關係人審查／Demo
**目的**：展示進度、蒐集回饋、建立共識。
**格式**：
1. 背景：提醒利害關係人目標，以及他們上次看到什麼
2. Demo：展示做了什麼。用真實的產品，不要用簡報。
3. 指標：分享任何早期資料或回饋
4. 回饋：留出結構化的時間讓大家提問和給意見
5. 下一步：接下來有什麼，以及下次審查是什麼時候

**主持提醒**：
- 盡可能 demo 真實產品。簡報不是 demo。
- 框定回饋的蒐集方式：「What feedback do you have on X?」比「Any thoughts?」好
- 把回饋明顯地記錄下來，並承諾處理（或解釋為什麼不處理）
- 先說清楚，在這個階段哪類回饋是可行動的

## 輸出格式

讓更新容易掃讀。重點用粗體，清單用項目符號。給主管的更新要控制在 300 字以內。給工程的更新可以長一點，但結構仍然要方便略讀。

## 小提醒

- 利害關係人更新最常見的錯誤是把重點埋起來。從最重要的事開始。
- 狀態顏色（Green/Yellow/Red）要反映現實，不是樂觀。Yellow 不是失敗，而是良好的風險溝通。
- 請求要具體、可行動。「We need help」不是請求。「We need a decision on X by Friday」才是。
- 對主管，一切都用成果和目標來描述，不要講活動和任務。
- 有壞消息就放最前面。不要把它藏在好消息後面。
- 長度要配合對象的注意力。主管拿到幾個重點就好。工程拿到他們需要的細節。
