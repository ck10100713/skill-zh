---
name: "cs-sop"
description: "設計客服營運，包含分級支援（L1/L2/L3）、回覆範本、SLA 定義、升級程序與客訴處理。當使用者需要建立客服團隊、制定服務標準、設計升級流程，或提升回覆品質時使用。就算使用者只說「我們的客服一團亂」、「客訴該怎麼處理」、「建立客服分級」或「寫客服 SOP」也要用。"
metadata:
  category: "WP-06 Agent通訊+客服"
  tags: ["customer-service", "sop", "support", "operations"]
---

# 客服 SOP

## 框架

```
IRON LAW: Tier the Support, Not the Customer

Every customer deserves quality service. But not every issue needs a
senior specialist. Route by ISSUE COMPLEXITY, not by customer "importance."

L1 handles 70-80% of volume (simple, repeatable)
L2 handles 15-20% (requires expertise)
L3 handles 5% (requires engineering or management)
```

### 三級支援模型

| 層級 | 處理範圍 | 所需技能 | 解決目標 |
|------|---------|----------------|------------------|
| **L1（基礎）** | FAQ、訂單狀態、重設密碼、簡單退貨 | 照腳本作業、產品基礎知識、同理心 | < 5 分鐘，首次接觸即解決 |
| **L2（專員）** | 技術問題、帳務爭議、複雜退貨、產品瑕疵 | 深入的產品知識、判斷力、協商能力 | < 24 小時 |
| **L3（專家）** | 系統 bug、法務/合規、高階主管層級的升級、危機 | 需要工程、法務或管理層介入 | < 72 小時，個案處理 |

### 案件分類

| 類別 | 範例 | 優先級 | SLA（首次回應） |
|----------|---------|----------|---------------------|
| **緊急（Critical）** | 服務中斷、資安事件、安全問題 | P1 | < 15 分鐘 |
| **高（High）** | 付款失敗、帳號被鎖、訂單錯誤 | P2 | < 1 小時 |
| **中（Medium）** | 產品問題、功能需求、一般客訴 | P3 | < 4 小時 |
| **低（Low）** | 意見回饋、建議、一般詢問 | P4 | < 24 小時 |

### 客訴處理：LAST 框架

1. **Listen（傾聽）**：讓客戶充分表達，不要打斷
2. **Apologize（道歉）**：誠懇地認同他們的不愉快（「很抱歉發生這種事」）
3. **Solve（解決）**：提出具體的解決方案或下一步
4. **Thank（感謝）**：謝謝他們讓我們知道這件事

### 升級規則

| 觸發條件 | 升級給誰 | 時限 |
|---------|-----------|---------|
| L1 在 15 分鐘內無法解決 | L2 | 立即 warm handoff（暖轉接） |
| 客戶要求找主管 | L2 或組長 | 5 分鐘內 |
| 問題涉及超過 NT$X 的退款 | L2（有核准權限） | 同一次互動內 |
| 法律威脅或提到媒體 | L3 + 法務 + 公關 | 立即 |
| 重複聯絡（同一問題 3 次以上） | L2 + 調查 | 第 3 次聯絡後 |

### 回覆範本結構

```
[Greeting] Hi {name}, thank you for contacting us.

[Acknowledge] I understand you're experiencing {issue}.

[Action] Here's what I've done / Here's what we'll do:
1. {specific action}
2. {timeline}

[Next steps] {what the customer should expect / do next}

[Close] Is there anything else I can help you with?
```

## 輸出格式

```markdown
# Customer Service SOP: {Business}

## Support Tiers
| Tier | Scope | Team Size | Tools |
|------|-------|----------|-------|
| L1 | {scope} | {N people} | {tools} |
| L2 | {scope} | {N} | {tools} |
| L3 | {scope} | {N} | {tools} |

## SLA Targets
| Priority | First Response | Resolution | Escalation |
|----------|--------------|-----------|-----------|
| P1 | {time} | {time} | {to whom} |
| P2 | ... | ... | ... |

## Top 10 Contact Reasons
| # | Reason | Volume % | Resolution | Template? |
|---|--------|---------|-----------|----------|
| 1 | {reason} | {%} | L1/L2 | Y/N |

## Escalation Flowchart
{Decision tree for when to escalate}

## Quality Metrics
| Metric | Target |
|--------|--------|
| First Contact Resolution | > 70% |
| CSAT | > 4.2/5 |
| Avg Response Time | < {X} hours |
| Escalation Rate | < 20% |
```

## 常見陷阱

- **SLA 一定要「可衡量」**：「快速回覆」不是 SLA。「P2 工單 1 小時內首次回應」才是。量不出來就管不了。
- **warm handoff > cold transfer**：升級時，L1 要先向 L2 說明狀況再轉接。逼客戶重講一遍經過，滿意度會直接崩掉。
- **給 L1 解決問題的權限**：如果 L1 每筆退款都要升級，70% 的量就會不必要地丟給 L2。給 L1 一個金額門檻內的退款權限（例如 NT$500）。
- **範本是起點，不是腳本**：機械式複製貼上的回覆，比不回還糟。客服人員應該針對具體情況調整範本。
- **台灣的客服期待**：台灣客戶期待 LINE 回覆要快（上班時間內幾分鐘），語氣要有禮貌且帶歉意，而且願意多走一步。「好服務」的門檻很高。

## 參考資料

- CSAT/NPS 問卷設計，見 cs-analytics skill
- 機器人轉真人的交接設計，見 cs-chatbot-design skill
