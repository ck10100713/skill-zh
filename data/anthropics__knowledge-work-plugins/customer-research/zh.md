---
name: customer-research
description: 針對客戶的問題或主題做多來源研究，並標明來源出處。用在客戶問了你需要查證的事、調查某個 bug 之前是否被回報過、確認之前對某個帳號說過什麼，或在起草回覆之前蒐集背景的時候。
argument-hint: "<question or topic>"
---

# /customer-research

> 如果看到不熟的佔位符，或需要確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

針對客戶問題、產品主題或帳號相關的詢問做多來源研究。把所有可用來源的發現綜合起來，附上清楚的出處和信心評分。

## 用法

```
/customer-research <question or topic>
```

## 工作流程

### 1. 解析研究需求

找出需要哪一種研究：
- **客戶問題**：客戶問了、需要有答案的事（例如「Does our product support SSO with Okta?」）
- **問題調查**：某個被回報問題的背景（例如「Has this bug been reported before? What's the known workaround?」）
- **帳號背景**：和特定客戶的歷史（例如「What did we tell Acme Corp last time they asked about this?」）
- **主題研究**：和支援工作相關的一般主題（例如「Best practices for webhook retry logic」）

搜尋之前，先釐清你實際上想找什麼：
- 這是有明確答案的事實問題嗎？
- 這是需要多種觀點的脈絡性問題嗎？
- 這是範圍還在界定中的探索性問題嗎？
- 答案的受眾是誰（內部團隊、客戶、管理層）？

### 2. 搜尋可用來源

依照下面的來源層級有系統地搜尋，並配合目前連了什麼來調整。不要在第一個結果就停下來，要在各來源之間交叉比對。

**第 1 層：官方內部來源（信心最高）：**
- ~~knowledge base（如果有連接）：產品文件、runbook、FAQ、政策文件
- ~~cloud storage：內部文件、規格、指南、過去的研究
- 產品 roadmap（內部版）：功能時程、優先順序

**第 2 層：組織背景：**
- ~~CRM 備註：帳號備註、活動歷史、先前的回答、商機細節
- ~~support platform（如果有連接）：先前的解決方式、已知問題、替代做法
- 會議筆記：先前的討論、決定、承諾

**第 3 層：團隊溝通：**
- ~~chat：在相關頻道搜尋這個主題；看看隊友有沒有討論過或回答過
- ~~email：搜尋先前關於這個主題的往來信件
- 行事曆備註：會議議程和會後筆記

**第 4 層：外部來源：**
- 網路搜尋：官方文件、部落格文章、社群論壇
- 公開的知識庫、說明中心、發行說明
- 第三方文件：整合夥伴、互補工具

**第 5 層：推論或類比（直接來源找不到答案時使用）：**
- 類似的情況：先前怎麼處理類似的問題
- 類似的客戶：對可比較的帳號什麼有效
- 一般最佳實務：業界標準和常態

### 3. 綜合發現

把結果整理成結構化的研究簡報：

```
## Research: [問題／主題]

### Answer
[對問題清楚、直接的答案，先講結論]

**Confidence:** [High / Medium / Low]
[說明是什麼決定了信心水準]

### Key Findings

**From [來源 1]:**
- [帶有具體細節的發現]
- [帶有具體細節的發現]

**From [來源 2]:**
- [帶有具體細節的發現]

### Context & Nuance
[任何重要的但書、邊角案例或額外背景]

### Sources
1. [來源名稱／連結]：[它提供了什麼]
2. [來源名稱／連結]：[它提供了什麼]
3. [來源名稱／連結]：[它提供了什麼]

### Gaps & Unknowns
- [無法確認的事]
- [可能需要請專家驗證的事]

### Recommended Next Steps
- [如果答案需要交給客戶，要做的行動]
- [如果需要進一步研究，要做的行動]
- [如果需要驗證，要請教誰]
```

### 4. 處理來源不足的情況

如果已連接的來源都沒有結果：

- 針對這個主題做網路研究
- 向使用者詢問內部背景：
  - 「I couldn't find this in connected sources. Do you have internal docs or knowledge base articles about this?」
  - 「Has your team discussed this topic before? Any ~~chat channels I should check?」
  - 「Is there a subject matter expert who would know the answer?」
- 對限制要坦白：
  - 「This answer is based on web research only — please verify against your internal documentation before sharing with the customer.」
  - 「I found a possible answer but couldn't confirm it from an authoritative internal source.」

### 5. 面向客戶時的考量

如果研究是要用來回答客戶的問題：

- 如果答案涉及產品 roadmap、定價、法律或資安議題，可能需要審閱，要標記出來
- 如果答案和先前可能溝通過的內容不同，要註明
- 為面向客戶的回覆建議適當的但書
- 提議起草客戶回覆：「Want me to draft a response to the customer based on these findings?」

### 6. 知識擷取

研究完成後，建議把知識記錄下來：

- 「Should I save these findings to your knowledge base for future reference?」
- 「Want me to create a FAQ entry based on this research?」
- 「This might be worth documenting — should I draft a runbook entry?」

這能幫忙累積組織知識，並減少團隊重複研究的工夫。

---

## 來源優先順序與信心

### 各來源層級的信心

| 層級 | 來源類型 | 信心 | 備註 |
|------|-------------|------------|-------|
| 1 | 官方內部文件、KB、政策 | **高** | 除非明顯過期，否則可信：要檢查日期 |
| 2 | CRM、支援工單、會議筆記 | **中高** | 可能帶有主觀或不完整 |
| 3 | 聊天、email、行事曆備註 | **中** | 非正式，可能脫離脈絡或只是推測 |
| 4 | 網路、論壇、第三方文件 | **低中** | 可能不符合你的具體情況 |
| 5 | 推論、類比、最佳實務 | **低** | 要清楚標示是推論，不是事實 |

### 信心等級

一定要指定並傳達信心等級：

**高信心：**
- 答案經官方文件或權威來源確認
- 多個來源互相佐證同一個答案
- 資訊是最新的（在合理的時間範圍內驗證過）
- 「I'm confident this is accurate based on [source].」

**中信心：**
- 答案出現在非正式來源（聊天、email），而不是官方文件
- 單一來源，沒有佐證
- 資訊可能稍微過時，但很可能仍然有效
- 「Based on [source], this appears to be the case, but I'd recommend confirming with [team/person].」

**低信心：**
- 答案是從相關資訊推論出來的
- 來源已過時或可能不可靠
- 各來源之間發現互相矛盾的資訊
- 「I wasn't able to find a definitive answer. Based on [context], my best assessment is [answer], but this should be verified before sharing with the customer.」

**無法判定：**
- 在任何來源都找不到相關資訊
- 問題需要來源裡沒有的專門知識
- 「I couldn't find information about this. I recommend reaching out to [suggested expert/team] for a definitive answer.」

### 處理矛盾

當來源之間意見不一致時：
1. 明確指出矛盾
2. 判斷哪個來源比較權威或比較新
3. 連同背景呈現兩種觀點
4. 建議如何解決這個差異
5. 如果要交給客戶：在解決之前，使用最保守、最謹慎的答案

## 何時升級 vs. 直接回答

### 這些情況直接回答：
- 官方文件清楚涵蓋這個問題
- 多個可靠的來源互相佐證這個答案
- 問題是事實性的，而且不敏感
- 答案不涉及承諾、時程或定價
- 你先前回答過類似的問題，而且確認過準確

### 這些情況要升級或驗證：
- 答案涉及產品 roadmap 的承諾或時程
- 定價、法律條款或合約相關的問題
- 資安、合規或資料處理的問題
- 答案可能開先例或製造期待
- 你在來源裡發現互相矛盾的資訊
- 問題涉及特定客戶的客製化設定
- 答案需要你不具備的專門知識
- 客戶處於風險中，而錯誤的答案可能讓情況惡化

### 升級路徑：
1. **專家（SME）**：技術或特定領域的問題
2. **產品團隊**：roadmap、功能或能力的問題
3. **法務／合規**：條款、隱私、資安或法規的問題
4. **帳務／財務**：定價、發票或付款相關的問題
5. **工程**：客製化設定、bug 或技術根本原因
6. **管理層**：策略決策、例外或高風險的情況

## 為團隊知識庫記錄研究

研究完成後，把知識記錄下來供未來使用。

### 何時要記錄：
- 這個問題以前出現過，或很可能會再出現
- 研究花了很大工夫才整理出來
- 答案需要綜合多個來源
- 答案糾正了常見的誤解
- 答案涉及容易搞錯的細微差異

### 記錄格式：
```
## [問題／主題]

**Last Verified:** [日期]
**Confidence:** [等級]

### Answer
[清楚、直接的答案]

### Details
[輔助細節、背景和細微差異]

### Sources
[這份資訊的來源]

### Related Questions
[這個答案可能也能幫忙回答的其他問題]

### Review Notes
[何時要重新驗證、什麼可能會改變這個答案]
```

### 知識庫整理：
- 所有條目都標註日期
- 標記引用特定產品版本或功能的條目
- 每季審閱並更新條目
- 把不再相關的條目歸檔
- 為條目加標籤方便搜尋（依主題、產品領域、客戶區隔）
