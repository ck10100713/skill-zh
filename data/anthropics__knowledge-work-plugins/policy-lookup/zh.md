---
name: policy-lookup
description: 用白話找出並解釋公司政策。用「what's our PTO policy」、「can I work remotely from another country」、「how do expenses work」觸發，或任何關於福利、差旅、請假或員工手冊規定的白話問題。
argument-hint: "<policy topic — PTO, benefits, travel, expenses, etc.>"
---

# /policy-lookup

> 如果看到不熟的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

用白話查詢並解釋公司政策。透過搜尋已連接的知識庫，或使用提供的員工手冊內容，回答員工關於政策、福利和流程的問題。

## 用法

```
/policy-lookup $ARGUMENTS
```

搜尋符合下列內容的政策：$ARGUMENTS

## 運作方式

```
┌─────────────────────────────────────────────────────────────────┐
│                    POLICY LOOKUP                                   │
├─────────────────────────────────────────────────────────────────┤
│  獨立模式（STANDALONE，隨時可用）                                  │
│  ✓ 用白話問任何政策問題                                          │
│  ✓ 貼上你的員工手冊，我來搜尋                                    │
│  ✓ 得到清楚、沒有行話的答案                                      │
├─────────────────────────────────────────────────────────────────┤
│  強化模式（SUPERCHARGED，連接你的工具之後）                        │
│  + 知識庫：自動搜尋員工手冊和政策文件                            │
│  + HRIS：拉取員工個人的細節（PTO 餘額、福利）                    │
└─────────────────────────────────────────────────────────────────┘
```

## 常見政策主題

- **PTO 與請假**：特休、病假、育嬰假、喪假、長期休假（sabbatical）
- **福利**：健康保險、牙科、視力、401k、HSA/FSA、健康促進
- **薪酬**：發薪時程、獎金時間、股權歸屬、費用報銷
- **遠端工作**：在家工作政策、可遠端的地點、設備津貼、共享辦公室
- **差旅**：訂位政策、每日津貼（per diem）、費用報告、核准流程
- **行為準則**：行為準則、騷擾政策、利益衝突
- **成長**：專業發展預算、研討會政策、學費補助

## 怎麼回答

1. 在 ~~knowledge base 搜尋相關的政策文件
2. 給出清楚的白話答案
3. 引用具體的政策原文
4. 註明任何例外或特殊情況
5. 指出特殊情況該找誰

**重要護欄：**
- 一律引用來源文件和章節
- 如果找不到政策，就明確說找不到，不要用猜的
- 法律或合規問題，建議直接諮詢 HR 或法務

## 輸出

```markdown
## Policy: [Topic]

### Quick Answer
[1-2 sentence direct answer to their question]

### Details
[Relevant policy details, explained in plain language]

### Exceptions / Special Cases
[Any relevant exceptions or edge cases]

### Who to Contact
[Person or team for questions beyond what's documented]

### Source
[Where this information came from — document name, page, or section]
```

## 如果有可用的 Connector

如果 **~~knowledge base** 已連接：
- 自動搜尋員工手冊和政策文件
- 引用具體的文件、章節和頁碼

如果 **~~HRIS** 已連接：
- 拉取員工個人的細節，例如 PTO 餘額、福利選擇和加保狀態

## 小技巧

1. **用白話問**：「Can I work from Europe for a month?」比「international remote work policy」好。
2. **要具體**：「PTO for part-time employees in California」比「PTO policy」更容易得到好答案。
