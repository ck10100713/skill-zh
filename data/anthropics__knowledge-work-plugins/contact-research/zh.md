---
name: contact-research
description: "用 Common Room 的資料研究特定的人。當使用者說『who is [name]』『look up [email]』『research [contact]』『is [name] a warm lead』，或任何聯絡人層級的問題時觸發。"
---

# 聯絡人研究（Contact Research）

從 Common Room 取得完整的聯絡人檔案。支援用 email、社群帳號，或姓名加公司查詢。回傳的是豐富化後的資料，包括活動歷史、Spark、分數、網站造訪紀錄和 CRM 欄位。

## 步驟 1：找到聯絡人

Common Room 支援多種查詢方式，使用者給什麼就用什麼：

| 使用者提供的資訊 | 查詢方式 |
|---------------------|--------------|
| Email 位址 | 用 email 查詢（最可靠） |
| LinkedIn、Twitter/X 或 GitHub 帳號 | 用社群帳號查詢，要明確指定帳號類型 |
| 姓名 + 公司 | 用姓名加組織網域做身分比對；如果有歧義，列出符合的對象 |
| 只有姓名 | 用姓名搜尋；如果有多個符合，顯示簡短清單，請使用者確認 |

如果找不到符合的對象，就回覆：「Common Room doesn't have a record for this person.」不要猜測，也不要捏造檔案資料。

## 步驟 2：取得聯絡人欄位

用 Common Room 的物件目錄查看有哪些欄位群組以及裡面的內容。要完整檔案就請求所有群組；針對性的問題就只請求相關的部分。

**要知道的關鍵欄位群組：**
- **分數（Scores）**：一律回傳原始值或百分位，絕對不要用標籤
- **近期活動**：用 `Contact Initiated` 篩選（近 60 天），看的是對方自己的行動，不是你們團隊的
- **網站造訪**：總次數加上具體頁面（近 12 週）
- **Spark**：要追蹤互動隨時間的演變時，取回所有的 Spark

## 步驟 3：執行 Spark enrichment（如果有的話）

如果有 Spark 就用。Spark 提供：
- 專業背景和工作經歷
- 社群存在感和影響力訊號
- 人物類型分類：Champion、Economic Buyer、Technical Evaluator、End User 或 Gatekeeper
- 推測在採購流程中的角色

如果沒有 Spark，但有真實的活動資料（近期行動、網站造訪、社群互動），就從這些訊號推測人物類型。如果 Spark 和活動資料都沒有，就歸類為 Unknown，不要只憑職稱去猜人物類型。

當使用者想了解這位聯絡人的互動如何隨時間演變時，要取回**所有 Spark**（不只最新的）。

## 步驟 4：評估帳號背景

針對這位聯絡人所屬的公司，拉一份精簡的帳號快照。要記下：
- 帳號層級的未結商機、擴展訊號或流失風險
- 這家公司其他聯絡人是否也很活躍
- 這個人的互動程度和同事相比如何

## 步驟 5：找出對話切入角度

根據活動和訊號，挑出最強的 2 到 3 個切入點：
- 最近一次 `Contact Initiated` 的活動（社群貼文、產品事件、支援單）
- 他們最近造訪的特定網頁，特別是帶有評估意圖的
- 換工作、升職或公司新聞
- 他們的 Spark 人物類型，以及這代表的溝通風格
- 他們在已知進行中 deal 裡的角色

## 輸出格式

只放實際有回傳資料的段落。沒有資料的段落直接省略，不要用猜測去填。

**資料豐富時：**

```
## [Contact Name] — Profile

**Overview**
[2 sentences: who they are, their role, and relationship status]

**Details**
- Title: [title]
- Company: [company]
- Email: [email]
- LinkedIn: [URL]
- Other profiles: [Twitter/X, GitHub, CRM link if available]

**Scores** [If scores returned]
[All scores as raw values or percentiles]

**Recent Activity** (last 60 days) [If activity returned]
[3–5 bullets with dates]

**Website Visits** (last 12 weeks) [If visit data exists]
[Total visit count + list of pages visited]

**Spark Profile** [If Spark data is non-null]
[Persona type, background summary, influence signals]

**Segments** [If segments returned]
[List of segment names this contact belongs to]

**Account Context**
[1–2 sentences on their company's status]

**Conversation Starters**
[2–3 specific, signal-backed openers]
```

**資料稀少時（例如只回傳姓名、職稱、email、標籤；sparkSummary 是 null）：**

```
## [Contact Name] — Profile (Limited Data)

**Data available:** [List exactly what Common Room returned]

[Present only the returned fields]

**Web Search**
[Any findings from searching their name + company]

**Note:** Common Room has limited data on this contact. No activity history, scores, or Spark profile available. I can run deeper web searches or look up their company for additional context.
```

不要用稀少的資料去產生對話切入點、人物類型推論或互動評估。這些都需要真實的訊號。

## 品質標準

- 查詢必須針對輸入類型使用正確的方法，不要在 email 和帳號之間亂猜
- 分數只用原始值／百分位，絕對不要用標籤
- `Contact Initiated` 的活動（近 60 天）是主要的互動訊號，要放在最前面
- 如果沒有 Spark，就直接說沒有，不要只憑職稱捏造人物類型
- 只要聯絡人最近一次活動超過 30 天，就要標註出來

## 參考檔案

- **`references/contact-signals-guide.md`**：完整的欄位說明、Spark 人物類型指南，以及對話切入點的原則
