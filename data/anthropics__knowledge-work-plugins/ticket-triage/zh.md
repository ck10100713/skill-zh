---
name: ticket-triage
description: 對客服 ticket 或客戶問題做分流與排優先順序。新 ticket 進來需要分類、指派 P1-P4 優先順序、決定該由哪個團隊處理，或在轉派前確認是不是重複或已知問題時使用。
argument-hint: "<ticket 或問題描述>"
---

# /ticket-triage

> 如果看到不認識的 placeholder，或想確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

替進來的客服 ticket 或客戶問題做分類、排優先順序、決定轉派對象。產出一份結構化的 triage 評估，並附上建議的初步回覆。

## 用法

```
/ticket-triage <ticket 內容、客戶訊息，或問題描述>
```

範例：
- `/ticket-triage Customer says their dashboard has been showing a blank page since this morning`
- `/ticket-triage "I was charged twice for my subscription this month"`
- `/ticket-triage User can't connect their SSO — getting a 403 error on the callback URL`
- `/ticket-triage Feature request: they want to export reports as PDF`

## 工作流程

### 1. 解析問題

讀輸入內容，抽出：

- **核心問題**：客戶實際遇到什麼狀況？
- **症狀**：他們看到的具體行為或錯誤是什麼？
- **客戶背景**：這是誰？有沒有帳號資料、方案等級或歷史紀錄可以參考？
- **緊急訊號**：他們被卡住了嗎？是 production 嗎？影響多少使用者？
- **情緒狀態**：沮喪、困惑、就事論事，還是正在升級？

### 2. 分類並排優先順序

依照下面的分類表和優先順序框架：

- 指定一個**主要分類**（bug、how-to、feature request、billing、account、integration、security、data、performance），可再加一個次要分類
- 依影響範圍和緊急程度指定**優先順序**（P1–P4）
- 找出問題對應的**產品區域**

### 3. 檢查重複和已知問題

轉派前，先查現有的資料來源：

- **~~support platform**：搜尋類似的未結或最近已解決的 ticket
- **~~knowledge base**：看有沒有已知問題或現成文件
- **~~project tracker**：看有沒有現成的 bug 回報或 feature request

套用下面的重複偵測流程。

### 4. 決定轉派對象

依照下面的轉派規則，根據分類和複雜度，建議該由哪個團隊或佇列處理。

### 5. 產出 Triage 結果

```
## Triage: [一句話的問題摘要]

**Category:** [主要] / [次要，如適用]
**Priority:** [P1-P4] — [簡短理由]
**Product area:** [區域/團隊]

### Issue Summary
[2-3 句話，說明客戶遇到什麼狀況]

### Key Details
- **Customer:** [已知的話寫名稱/帳號]
- **Impact:** [誰、什麼受到影響]
- **Workaround:** [有 / 沒有 / 不確定]
- **Related tickets:** [找到類似問題的話附連結]
- **Known issue:** [Yes — 連結 / No / Checking]

### Routing Recommendation
**Route to:** [團隊或佇列]
**Why:** [簡短理由]

### Suggested Initial Response
[草擬給客戶的第一則回覆：承認問題、
設定預期、有 workaround 就附上。
可以用下面的自動回覆範本當起點。]

### Internal Notes
- [接手的 agent 需要的其他背景]
- [如果是 bug，附上重現提示]
- [需要留意的升級觸發條件]
```

### 6. 提供下一步選項

呈現完 triage 之後：
- 「要我草擬完整的客戶回覆嗎？」
- 「要我再搜尋更多這個問題的背景嗎？」
- 「要我到 tracker 查這是不是已知 bug 嗎？」
- 「要升級處理嗎？我可以用 /customer-escalation 把它打包。」

---

## 分類表

每張 ticket 都要有一個**主要分類**，也可以有一個**次要分類**：

| 分類 | 說明 | 訊號詞 |
|----------|-------------|-------------|
| **Bug** | 產品行為不正確或不如預期 | Error, broken, crash, not working, unexpected, wrong, failing |
| **How-to** | 客戶需要產品使用上的指引 | How do I, can I, where is, setting up, configure, help with |
| **Feature request** | 客戶想要一個目前不存在的功能 | Would be great if, wish I could, any plans to, requesting |
| **Billing** | 付款、訂閱、發票或定價問題 | Charge, invoice, payment, subscription, refund, upgrade, downgrade |
| **Account** | 帳號存取、權限、設定或使用者管理 | Login, password, access, permission, SSO, locked out, can't sign in |
| **Integration** | 連接第三方工具或 API 的問題 | API, webhook, integration, connect, OAuth, sync, third-party |
| **Security** | 資安疑慮、資料存取或合規問題 | Data breach, unauthorized, compliance, GDPR, SOC 2, vulnerability |
| **Data** | 資料品質、遷移、匯入/匯出問題 | Missing data, export, import, migration, incorrect data, duplicates |
| **Performance** | 速度、可靠度或可用性問題 | Slow, timeout, latency, down, unavailable, degraded |

### 判斷分類的訣竅

- 如果客戶**同時**回報 bug 和 feature request，bug 是主要分類
- 如果客戶因為 bug 而無法登入，分類是 **Bug**（不是 Account），由根本原因決定分類
- 「以前可以用，現在不行」= **Bug**
- 「我希望它用不一樣的方式運作」= **Feature request**
- 「我要怎麼讓它動起來？」= **How-to**
- 拿不準的時候，傾向判成 **Bug**，寧可調查也不要直接打發掉

## 優先順序框架

### P1 — Critical
**標準：** production 系統掛掉、資料遺失或損毀、資安事件、全部或大部分使用者受影響。

- 客戶完全無法使用產品
- 資料正在遺失、損毀或外洩
- 資安事件正在發生
- 問題正在惡化，或影響範圍正在擴大

**SLA 預期：** 1 小時內回覆。持續處理，直到解決或緩解。每 1-2 小時更新一次。

### P2 — High
**標準：** 主要功能壞掉、重要工作流程被卡住、很多使用者受影響、沒有 workaround。

- 核心工作流程壞了，但產品還能部分使用
- 多位使用者受影響，或重要客戶受到衝擊
- 問題卡住了有時限的工作
- 沒有合理的 workaround

**SLA 預期：** 4 小時內回覆。當天開始積極調查。每 4 小時更新一次。

### P3 — Medium
**標準：** 功能部分壞掉、有 workaround、單一使用者或小團隊受影響。

- 功能運作不正常，但有 workaround
- 問題造成不便，但沒有卡住關鍵工作
- 單一使用者或小團隊受影響
- 客戶沒有緊急升級

**SLA 預期：** 1 個工作天內回覆。3 個工作天內解決或更新進度。

### P4 — Low
**標準：** 小不便、外觀問題、一般提問、feature request。

- 不影響功能的外觀或 UI 問題
- Feature request 和改進想法
- 一般提問或 how-to 詢問
- 有簡單、已有文件說明的解法的問題

**SLA 預期：** 2 個工作天內回覆。照正常步調解決。

### 優先順序升級觸發條件

遇到以下情況，自動調高優先順序：
- 客戶等待的時間已經超過 SLA 允許的範圍
- 多位客戶回報同一個問題（偵測到 pattern）
- 客戶明確要求升級，或提到高階主管介入
- 原本在用的 workaround 失效了
- 問題範圍擴大（更多使用者、更多資料、新的症狀）

## 轉派規則

依分類和複雜度轉派 ticket：

| 轉派給 | 時機 |
|----------|------|
| **Tier 1（第一線客服）** | How-to 問題、有文件化解法的已知問題、帳務詢問、重設密碼 |
| **Tier 2（資深客服）** | 需要調查的 bug、複雜的設定、integration 疑難排解、帳號問題 |
| **Engineering** | 已確認、需要改程式碼的 bug、基礎設施問題、效能下降 |
| **Product** | 需求量大的 feature request、設計決策、工作流程缺口 |
| **Security** | 資料存取疑慮、弱點回報、合規問題 |
| **Billing/Finance** | 退款請求、合約爭議、複雜的帳務調整 |

## 重複偵測

建立新 ticket 或轉派之前，先檢查有沒有重複：

1. **用症狀搜尋**：找錯誤訊息或描述類似的 ticket
2. **用客戶搜尋**：看這位客戶有沒有針對同一個問題的未結 ticket
3. **用產品區域搜尋**：找同一個功能區域最近的 ticket
4. **檢查已知問題**：跟已文件化的已知問題比對

**如果找到重複：**
- 把新 ticket 連結到既有的那張
- 通知客戶這是已知問題，正在追蹤中
- 把新回報裡的任何新資訊補進既有 ticket
- 如果新回報增加了急迫性（更多客戶受影響等），就調高優先順序

## 各分類的自動回覆範本

### Bug — 初步回覆
```
Thank you for reporting this. I can see how [specific impact]
would be disruptive for your work.

I've logged this as a [priority] issue and our team is
investigating. [If workaround exists: "In the meantime, you
can [workaround]."]

I'll update you within [SLA timeframe] with what we find.
```

### How-to — 初步回覆
```
Great question! [Direct answer or link to documentation]

[If more complex: "Let me walk you through the steps:"]
[Steps or guidance]

Let me know if that helps, or if you have any follow-up
questions.
```

### Feature Request — 初步回覆
```
Thank you for this suggestion — I can see why [capability]
would be valuable for your workflow.

I've documented this and shared it with our product team.
While I can't commit to a specific timeline, your feedback
directly informs our roadmap priorities.

[If alternative exists: "In the meantime, you might find
[alternative] helpful for achieving something similar."]
```

### Billing — 初步回覆
```
I understand billing issues need prompt attention. Let me
look into this for you.

[If straightforward: resolution details]
[If complex: "I'm reviewing your account now and will have
an answer for you within [timeframe]."]
```

### Security — 初步回覆
```
Thank you for flagging this — we take security concerns
seriously and are reviewing this immediately.

I've escalated this to our security team for investigation.
We'll follow up with you within [timeframe] with our findings.

[If action is needed: "In the meantime, we recommend
[protective action]."]
```

## Triage 最佳實務

1. 分類前先把整張 ticket 讀完，後面訊息裡的脈絡常常會改變評估
2. 依**根本原因**分類，不要只看客戶描述的症狀
3. 優先順序拿不準時，寧可往高的方向判，降級比錯過 SLA 後補救容易
4. 轉派前一定要檢查重複和已知問題
5. 寫內部備註，讓下一個接手的人能快速掌握脈絡
6. 把你已經查過或排除的東西寫進去，避免重複調查
7. 注意 pattern：如果同一個問題一直出現，即使個別 ticket 優先順序低，也要把這個 pattern 往上升級
