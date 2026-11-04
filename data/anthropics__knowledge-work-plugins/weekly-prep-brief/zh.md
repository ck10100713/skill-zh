---
name: weekly-prep-brief
description: "替未來 7 天所有的外部通話產出完整的每週簡報。用「weekly prep brief」「prepare my week」「what calls do I have this week」「Monday prep」觸發，或任何每週規劃的請求。"
---

# 每週準備簡報

產出一份完整的每週簡報，涵蓋未來 7 天每一場外部客戶或潛在客戶通話，並附上來自 Common Room 的每場會議的帳號與聯絡人研究。

## 簡報流程

### 步驟 1：取得本週的外部會議

**選項 A — 有連接行事曆：**
用 `~~calendar` connector 抓取未來 7 天（或使用者指定的範圍）排定的所有會議。只保留外部會議，也就是有組織外部與會者的會議。丟掉純內部的會議、與同事的一對一，以及週期性的內部同步會議。

為每場外部會議找出：
- 公司名稱
- 會議日期和時間
- 外部與會者的姓名和 email 位址

**選項 B — 沒有連接行事曆：**
問使用者：「要建立你的每週準備簡報，我需要你接下來的外部通話。請列出：公司名稱、日期/時間，以及與會者姓名。」

接受自由格式的輸入，並先把它解析成結構化的清單，再繼續。

### 步驟 2：確認會議清單

開始研究之前，先把找到的會議呈現給使用者確認：

> 「這是我找到的本週外部通話。如果有漏掉或該排除的，請告訴我：
> - [Company] — [Day], [Time] — [Attendees]
> - ...」

這樣可以避免把研究浪費在已取消或錯誤的會議上。

### 步驟 3：研究每場會議

對每場確認過的外部會議，盡可能平行執行：
1. **帳號研究**：用 account-research skill 做完整的帳號快照
2. **聯絡人研究**：用 contact-research skill 為每位外部與會者建立檔案

Common Room 的資料是主要來源。CR 研究之後，對每家公司做一次快速的**時效檢查**，這是補充，不是主要來源：
- 搜尋 `"[company name]" news`，範圍限定在最近 7 天
- 對於高階主管與會者，搜尋他們的名字，看最近的公開貼文或訪談
- 只收錄真正值得注意的發現（募資、領導層異動、重大媒體報導）。不要用一般性的新聞來湊簡報。

深度的校準：
- 高優先順序的帳號（大型帳號、有進行中的 opportunity、續約風險），產出完整深度的研究
- 優先順序較低或較短的會議，產出精簡的快照（每個 3–4 個重點）

### 步驟 4：彙整每週簡報

把每場會議的研究彙整成一份結構化的文件，依會議日期/時間排序。

以簡短的週層級概覽開頭，標出：
- 有緊急訊號的帳號（有風險、試用即將到期、有擴展機會）
- 需要特別準備或高階主管參與的會議
- 外部通話的總數和預估所需時間

## 輸出格式

```
# Weekly Prep Brief — Week of [Date]

## Week Overview
[2–4 bullets: key themes, flagged priorities, call count]

---

## [Monday / Tuesday / etc.]

### [Company Name] — [Time]
**Attendees:** [Names and titles]
**Meeting type:** [Discovery / QBR / Renewal / Expansion / etc. — inferred if possible]

**Company Snapshot**
[4–5 bullets: account status, top signals, recent activity]

**Attendee Profiles**
- **[Name]** ([Title]): [2–3 bullets on their signals, persona, conversation angle]
- [Repeat per attendee]

**Top Signals This Week**
[2–3 most relevant signals for this specific call]

**This Week's News** [If notable news found]
[Only genuinely noteworthy findings — funding, leadership changes, major press]

**Recommended Objectives**
[1–2 sentences: what to accomplish in this meeting]

---

[Repeat per meeting, sorted by date/time]
```

## 當某場會議的資料很少時

如果 Common Room 對某場會議的帳號或與會者只回傳有限的資料，那場會議就用精簡格式，不要用完整範本：

```
### [Company Name] — [Time] ⚠️ Limited Data
**Attendees:** [Names and titles if known]
**Data available:** [What Common Room actually returned]

**Web Search Results**
[Findings from web search — company news, attendee LinkedIn profiles]

**Note:** Common Room has limited data on this account. The rep may want to check directly in CR or gather context from colleagues before this call.
```

不要用稀少的資料硬產出完整的會議準備區塊（公司快照、訊號重點、談話要點、建議目標）。簡短但誠實的區塊，比捏造出來的完整區塊更有用。

## 品質標準

- 讓每場會議的區塊容易掃讀：業務通常在早上讀，而且常常是用手機
- 一律依日期/時間由早到晚排序
- 緊急狀況要醒目標出（風險、試用到期、進行中的 opp），不要把它們埋起來
- 如果某場會議的 Common Room 資料很薄，就用上面的精簡格式，絕對不要用猜的去填滿完整範本
- 一週有 4–6 場會議時，整份簡報應該能在 10–15 分鐘內讀完
- **每個事實都必須來自工具呼叫**：不准捏造 deal 背景、活動或訊號

## 參考檔案

- **`references/briefing-guide.md`** — 簡報結構的準則、優先順序的邏輯，以及如何處理 edge case（已取消的會議、沒有資料的新帳號等）
