---
name: draft-response
description: 針對情境和客戶關係，起草專業的對客戶回覆。回答產品問題、回應 escalation 或停機事件、傳達延遲或不修之類的壞消息、婉拒功能需求，或回覆帳務問題時使用。
argument-hint: "<situation description>"
---

# /draft-response

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

針對情境、客戶關係和溝通脈絡，起草一份專業的對客戶回覆。

## 用法

```
/draft-response <context about the customer question, issue, or request>
```

範例：
- `/draft-response Acme Corp is asking when the new dashboard feature will ship`
- `/draft-response Customer escalation — their integration has been down for 2 days`
- `/draft-response Responding to a feature request we won't be building`
- `/draft-response Customer hit a billing error and wants a resolution ASAP`

## 流程

### 1. 理解脈絡

解析使用者的輸入，判斷：

- **客戶**：這份溝通是給誰的？有的話就查帳戶脈絡。
- **情境類型**：提問、問題、escalation、公告、協商、壞消息、好消息、跟進
- **急迫性**：有時效嗎？客戶已經等了多久？
- **通路**：Email、客服 ticket、聊天或其他（依此調整正式程度）
- **關係階段**：新客戶、老客戶、沮喪／已升級的客戶
- **對象層級**：終端使用者、主管、高階主管、技術人員、業務人員

### 2. 研究脈絡

從可用的來源蒐集相關背景：

**~~email：**
- 跟這位客戶在這個主題上先前的往來信件
- 先前分享過的任何承諾或時程
- 現有對話串的語氣和風格

**~~chat：**
- 關於這位客戶或這個主題的內部討論
- 產品、工程或主管給的任何指引
- 類似情境以及當時怎麼處理

**~~CRM（如果有連接）：**
- 帳戶詳細資料和方案等級
- 聯絡資訊和關鍵利害關係人
- 先前的 escalation 或敏感問題

**~~support platform（如果有連接）：**
- 相關的 ticket 和它們的解決方式
- 已知問題或 workaround
- SLA 狀態和回應時間的承諾

**~~knowledge base：**
- 可以引用的官方文件或說明文章
- 產品 roadmap 資訊（如果可以分享）
- 政策或流程文件

### 3. 產生草稿

產出針對情境量身打造的回覆：

```
## Draft Response

**To:** [Customer contact name]
**Re:** [Subject/topic]
**Channel:** [Email / Ticket / Chat]
**Tone:** [Empathetic / Professional / Technical / Celebratory / Candid]

---

[Draft response text]

---

### Notes for You (internal — do not send)
- **Why this approach:** [Rationale for tone and content choices]
- **Things to verify:** [Any facts or commitments to confirm before sending]
- **Risk factors:** [Anything sensitive about this response]
- **Follow-up needed:** [Actions to take after sending]
- **Escalation note:** [If this should be reviewed by someone else first]
```

### 4. 執行品質檢查

呈現草稿之前，先確認：

- [ ] 語氣符合情境和關係
- [ ] 沒有超出授權範圍的承諾
- [ ] 沒有不該對外分享的產品 roadmap 細節
- [ ] 對先前對話的引用正確
- [ ] 下一步和負責人很清楚
- [ ] 適合對象的層級（對高階主管不要太技術，對工程師不要太籠統）
- [ ] 長度適合該通路（聊天要短，email 可以完整一點）

### 5. 提供後續修改

呈現草稿之後：
- 「Want me to adjust the tone? (more formal, more casual, more empathetic, more direct)」
- 「Should I add or remove any specific points?」
- 「Want me to make this shorter/longer?」
- 「Should I draft a version for a different stakeholder?」
- 「Want me to draft the internal escalation note as well?」
- 「Should I prepare a follow-up message to send after [X days] if no response?」

---

## 客戶溝通最佳實務

### 核心原則

1. **先展現同理心**：先認可客戶的處境，再跳到解法
2. **要直接**：直接講重點，客戶都很忙。結論先行。
3. **要誠實**：絕對不要過度承諾、不要誤導、不要把壞消息藏在術語裡
4. **要具體**：用具體的細節、時程和人名，避免模糊的用語
5. **要扛責任**：該負責時就負責。說「我們」，不要說「系統」或「流程」
6. **要收尾**：每封回覆都要有明確的下一步或 call to action
7. **配合對方的情緒**：對方沮喪，就先同理。對方興奮，就跟著熱情。

### 回覆結構

大部分客戶溝通都照這個結構：

```
1. Acknowledgment / Context (1-2 sentences)
   - Acknowledge what they said, asked, or are experiencing
   - Show you understand their situation

2. Core Message (1-3 paragraphs)
   - Deliver the main information, answer, or update
   - Be specific and concrete
   - Include relevant details they need

3. Next Steps (1-3 bullets)
   - What YOU will do and by when
   - What THEY need to do (if anything)
   - When they'll hear from you next

4. Closing (1 sentence)
   - Warm but professional sign-off
   - Reinforce you're available if needed
```

### 長度指引

- **聊天／即時訊息**：1 到 4 句。馬上講重點。
- **客服 ticket 回覆**：1 到 3 個短段落。有結構、好掃讀。
- **Email**：最多 3 到 5 段。尊重對方的收件匣。
- **Escalation 回覆**：要多長有多長才夠完整，但要用標題整理好結構。
- **對高階主管的溝通**：越短越好。最多 2 到 3 段。以數據為主。

## 語氣與風格指引

### 語氣光譜

| 情境 | 語氣 | 特徵 |
|-----------|------|----------------|
| 好消息／勝利 | 慶祝 | 熱情、溫暖、恭喜、著眼未來 |
| 例行更新 | 專業 | 清楚、簡潔、資訊豐富、友善 |
| 技術回覆 | 精確 | 準確、詳細、有結構、有耐心 |
| 延遲交付 | 負責 | 誠實、致歉、以行動為導向、具體 |
| 壞消息 | 坦率 | 直接、有同理心、以解法為導向、尊重 |
| 問題／停機 | 緊急 | 即時、透明、可執行、讓人安心 |
| Escalation | 高階主管 | 沉著、扛起責任、提出計畫、有信心 |
| 帳務／帳戶 | 精確 | 清楚、基於事實、有同理心、以解決為重 |

### 依關係階段調整語氣

**新客戶（0 到 3 個月）：**
- 更正式、更專業
- 多提供脈絡和說明（不要假設對方已經知道）
- 主動提供協助和資源
- 靠可靠和回應速度建立信任

**老客戶（3 個月以上）：**
- 溫暖、協作
- 可以引用共同的歷史和先前的對話
- 溝通更直接、更有效率
- 展現你了解他們的目標和優先順序

**沮喪或已升級的客戶：**
- 多一點同理心和認可
- 回應時間要有急迫感
- 具體的行動計畫，附明確的承諾
- 縮短回饋循環

### 寫作風格規則

**要做：**
- 用主動語態（「We'll investigate」，不要寫「This will be investigated」）
- 個人承諾用「I」，團隊承諾用「we」
- 指派行動時指名具體的人（「Sarah from our engineering team will...」）
- 用客戶的用語，不要用你們內部的術語
- 寫明確的日期和時間，不要用相對說法（寫「by Friday January 24」，不要寫「in a few days」）
- 長的回覆用標題或項目符號拆開

**不要做：**
- 使用企業術語或流行語（「synergy」「leverage」「paradigm shift」）
- 把責任推給其他團隊、系統或流程
- 用被動語態逃避責任（「Mistakes were made」）
- 加不必要的但書或含糊的說法，削弱信心
- 不必要地 CC 別人，只放需要參與對話的人
- 過度使用驚嘆號（每封 email 最多一個，沒有更好）

## 依情境的做法

**回答產品問題：**
- 先給直接的答案
- 附上相關的文件連結
- 需要的話，主動幫他們聯繫對的資源
- 如果你不知道答案：誠實說出來，承諾去查，並給出時程

**回應問題或 bug：**
- 認可這件事對他們工作的影響
- 說明你對這個問題及其狀態的了解
- 有 workaround 就提供
- 設定解決時程的預期
- 承諾定期更新

**處理 escalation：**
- 認可事情的嚴重性和他們的沮喪
- 扛起責任（不要推託或找藉口）
- 提供附時程的清楚行動計畫
- 指出負責解決的人
- 依嚴重程度，適當的話提議開會或通話

**傳達壞消息（功能下架、延遲、不修）：**
- 要直接，不要把消息藏起來
- 誠實解釋理由
- 認可這件事對他們個別造成的影響
- 提供替代方案或緩解措施
- 給出清楚的前進路徑

**分享好消息（功能上線、里程碑、獲得肯定）：**
- 先講正面的結果
- 連到他們具體的目標或使用情境
- 建議後續步驟，好好利用這個好消息
- 表達真誠的熱情

**婉拒請求（功能需求、折扣、例外）：**
- 認可這個請求和它背後的理由
- 對決定要誠實
- 解釋原因，但不要輕視對方
- 可以的話提供替代方案
- 為未來的對話留下餘地

## 常見情境的回覆範本

### 確認收到 bug 回報

```
Hi [Name],

Thank you for reporting this — I can see how [specific impact] would be
frustrating for your team.

I've confirmed the issue and escalated it to our engineering team as a
[priority level]. Here's what we know so far:
- [What's happening]
- [What's causing it, if known]
- [Workaround, if available]

I'll update you by [specific date/time] with a resolution timeline.
In the meantime, [workaround details if applicable].

Let me know if you have any questions or if this is impacting you in
other ways I should know about.

Best,
[Your name]
```

### 確認收到帳務或帳戶問題

```
Hi [Name],

Thank you for reaching out about this — I understand billing issues
need prompt attention, and I want to make sure this gets resolved
quickly.

I've looked into your account and here's what I'm seeing:
- [What happened — clear factual explanation]
- [Impact on their account — charges, access, etc.]

Here's what I'm doing to fix this:
- [Action 1 — with timeline]
- [Action 2 — if applicable]

[If resolution is immediate: "This has been corrected and you should
see the change reflected within [timeframe]."]
[If needs investigation: "I'm escalating this to our billing team
and will have an update for you by [specific date]."]

I'm sorry for the inconvenience. Let me know if you have any
questions about your account.

Best,
[Your name]
```

### 回覆你們不會做的功能需求

```
Hi [Name],

Thank you for sharing this request — I can see why [capability] would
be valuable for [their use case].

I discussed this with our product team, and this isn't something we're
planning to build in the near term. The primary reason is [honest,
respectful explanation — e.g., it serves a narrow use case, it conflicts
with our architecture direction, etc.].

That said, I want to make sure you can accomplish your goal. Here are
some alternatives:
- [Alternative approach 1]
- [Alternative approach 2]
- [Integration or workaround if applicable]

I've also documented your request in our feedback system, and if our
direction changes, I'll let you know.

Would any of these alternatives work for your team? Happy to dig
deeper into any of them.

Best,
[Your name]
```

### 停機或事件的溝通

```
Hi [Name],

I wanted to reach out directly to let you know about an issue affecting
[service/feature] that I know your team relies on.

**What happened:** [Clear, non-technical explanation]
**Impact:** [How it affects them specifically]
**Status:** [Current status — investigating / identified / fixing / resolved]
**ETA for resolution:** [Specific time if known, or "we'll update every X hours"]

[If applicable: "In the meantime, you can [workaround]."]

I'm personally tracking this and will update you as soon as we have a
resolution. You can also check [status page URL] for real-time updates.

I'm sorry for the disruption to your team's work. We take this seriously
and [what you're doing to prevent recurrence if known].

[Your name]
```

### 對方沒回應後的跟進

```
Hi [Name],

I wanted to check in — I sent over [what you sent] on [date] and
wanted to make sure it didn't get lost in the shuffle.

[Brief reminder of what you need from them or what you're offering]

If now isn't a good time, no worries — just let me know when would be
better, and I'm happy to reconnect then.

Best,
[Your name]
```

## 跟進與 escalation 指引

### 跟進頻率

| 情境 | 跟進時機 |
|-----------|-----------------|
| 沒被回答的問題 | 2 到 3 個工作天 |
| 還沒結案的客服問題 | 嚴重的每天跟進直到解決，一般的 2 到 3 天 |
| 會議後的待辦事項 | 24 小時內（寄出會議紀錄），然後在期限時確認 |
| 一般關心 | 持續進行中的問題視需要 |
| 傳達壞消息之後 | 1 週後確認影響和對方的感受 |

### 什麼時候要 escalate

**在這些情況 escalate 給你的主管：**
- 客戶威脅要取消或大幅降級
- 客戶要求你無權核准的政策例外
- 問題未解決的時間已超過 SLA 允許的範圍
- 客戶要求直接聯絡高層
- 你犯了錯，需要資深人員介入才能解決

**在這些情況 escalate 給產品／工程：**
- Bug 很嚴重，擋住了客戶的業務
- 功能缺口造成競爭上的損失
- 客戶有超出標準客服範圍的特殊技術需求
- 整合問題需要工程團隊調查

**Escalation 格式：**
```
ESCALATION: [Customer Name] — [One-line summary]

Urgency: [Critical / High / Medium]
Customer impact: [What's broken for them]
History: [Brief background — 2-3 sentences]
What I've tried: [Actions taken so far]
What I need: [Specific help or decision needed]
Deadline: [When this needs to be resolved by]
```
