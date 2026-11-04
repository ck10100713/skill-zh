---
name: compose-outreach
description: "利用 Common Room 的訊號產生個人化的開發信與聯繫訊息。當使用者說『draft outreach to [person]』『write an email to [name]』『compose a message for [contact]』，或任何起草開發訊息的需求時觸發。"
---

# 撰寫開發訊息（Compose Outreach）

針對特定公司或聯絡人，根據 Common Room 的訊號，產生三種個人化的開發格式：電子郵件、電話腳本和 LinkedIn 訊息。

## 開發流程

### 步驟 1：查詢目標

用 Common Room MCP 工具找出並取得目標（公司和／或特定聯絡人）的資料。要拉的內容：
- 近期的產品使用活動和互動訊號
- 社群活動（貼文、提問、反應）
- 第三方意圖訊號（職缺、新聞、募資）
- 關係歷史（先前的聯繫、會議、信件開信紀錄）

如果使用者指定了某個人，就做聯絡人層級的研究。如果只給了公司，就依職稱、互動程度和角色，找出最適合接觸的聯絡人。

### 步驟 2：用網路搜尋找外部切入點（CR 訊號不足時）

如果 CR 回傳的訊號很強（近期活動、互動、產品使用），就該由這些訊號帶動個人化，跳過網路搜尋。如果 CR 訊號不足，或是潛在客戶在 CR 上幾乎沒有活動，就用網路搜尋找外部切入點：

**搜尋什麼：**
- `"[company name]" funding OR acquisition OR launch OR announcement`：近 30 天
- `"[contact full name]" "[company name]"`：找近期的文章、訪談、LinkedIn 貼文或研討會演講

**優先選這類外部切入點：**
- 非常新（< 2 週）：對方很可能還在想這件事
- 公開可見：對方知道你有可能看到
- 帶有變化訊號：成長、新職務、新產品、新市場

如果使用者明確要求網路搜尋或外部切入點，不管 CR 訊號多豐富都要搜。

### 步驟 3：Spark enrichment（如果有的話）

如果有 Spark，就對目標聯絡人做 enrichment，取得人物類型分類、背景和影響力訊號。用這些來調整語氣和訊息角度。

### 步驟 4：找出最好的切入點

從訊號資料中，找出 1 到 3 個最強的個人化切入點。排序依據：
1. **時效性**：發生在最近 7 到 14 天
2. **具體性**：對方做過的具體動作，而不是泛泛的趨勢
3. **關聯性**：直接連到你的產品能帶來的價值

好的切入點：在社群貼了關於 X 的問題、剛雇了 5 位工程師、最近開始使用 [功能]、公司剛完成 B 輪募資、試用快到期、champion 剛換工作。

不好的切入點：「我注意到你是我們的客戶」，或是泛泛的產業趨勢。

### 步驟 5：產生三種格式

用最強的切入點寫出三種格式。每種格式的限制和慣例都不一樣，請照 `references/outreach-formats-guide.md` 裡各格式的準則。

一定要三種都產出，並且清楚標示。

如果有使用者的公司背景（見 `references/my-company-context.md`），價值銜接和推銷內容就要以使用者具體的產品和定位為基礎。

### 步驟 6：註明你的選擇

三份草稿之後，附上一段簡短說明（2 到 4 句），解釋：
- 用了哪些訊號、為什麼選它們
- 做了哪些假設（例如推測的通話目的）
- 如果主要切入點沒打中，有哪些替代角度

## 輸出格式

```
## Outreach for [Name / Company]

### 📧 Email

**Subject:** [Subject line]

[Email body — 3–5 sentences]

---

### 📞 Call Script

**Opening:**
[Opening line — conversational, 1–2 sentences]

**Value Bridge:**
[Why you're calling and why now — 2–3 sentences tied to a signal]

**Ask:**
[Single, low-friction ask — e.g., 15-minute call, specific question]

---

### 💼 LinkedIn Message

[Under 300 characters. Warm, personal, no pitch.]

---

### Signal Notes
[2–4 sentences: which signals were used, why, and any alternative angles]
```

## 訊號資料稀少時

如果 Common Room 對目標只回傳很少的資料（例如只有姓名、職稱、標籤，沒有活動、沒有分數、沒有 Spark）：

1. **不要憑空起草開發訊息。** 建立在捏造訊號上的開發訊息，比不寄還糟。
2. **先做網路搜尋**：這會變成你主要的個人化來源。找近期新聞、LinkedIn 貼文、研討會演講、公司公告。
3. **如果網路搜尋也沒什麼結果**，就誠實呈現你手上有的東西，並且向使用者要背景資訊：

```
## Outreach for [Name / Company] — Limited Data

**What I found:**
[Only the real data from CR and web search]

**I don't have enough signal to draft personalized outreach yet.** To write something strong, I'd need:
- Recent activity or engagement signals
- Context you have from prior conversations
- A specific reason for reaching out now

Can you share any of the above?
```

## 品質標準

- 每則訊息都必須提到某個具體的東西：泛泛的開發訊息不能當成輸出
- 語氣要配合情境：針對 inbound／社群訊號要親切、口語；針對陌生開發／高階主管則要比較正式
- LinkedIn 訊息一定要在 300 字元以內，沒有例外
- 電話腳本必須能自然地唸出口：在腦中朗讀一遍，檢查節奏
- **絕對不要捏造訊號**：只能引用從 Common Room 或網路搜尋取得的資料

## 參考檔案

- **`references/outreach-formats-guide.md`**：每個管道的詳細格式規則、範例和語氣準則
