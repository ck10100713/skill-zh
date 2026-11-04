---
name: call-list
description: 建立今天的通話清單。執行 lead-triage 排出最值得打電話的前 5 名 lead，從 email 往來紀錄提供談話重點，在行事曆上排出時間，並草擬後續訊息。當出現「call list」「who am I calling today」「top five to call today」或「block time for calls」時觸發。只想要 lead 評分或排名、不需要排行事曆的老闆，直接導向 lead-triage。可接受選用的數量與日期參數。
allowed-tools: Read, WebFetch
---

執行 lead 優先排序。掃描 pipeline，依急迫性和機會排名，拉出相關的 email 脈絡，讓老闆準備好開始打電話。

解析參數：
- `--n`（預設：`5`）— 要列出的 lead 數量（1–10）
- `--date`（預設：今天）— 要建立通話清單的日期（`YYYY-MM-DD`）

## Step 1 — 掃描 pipeline（lead-triage）

拉資料和評分都執行 `lead-triage` skill 的工作流程，它掌管 HubSpot 欄位清單、四維度模型、從備註內文抓急迫性、分數過於平均的防護，以及補強資料這一段（連了 Apollo 或 Clay 時，替沒有公司資料的 lead 補上公司適配度，這是計量收費的，所以 lead-triage 會問一次點數成本；把那個問題原樣轉給老闆，不要自己回答）。這些都不要在這裡重做。然後從 Mail 替每個留下來的 lead 拉 email 對話串（每個聯絡人最近 3 封），用來做談話重點。

## Step 2 — 排名並挑出前 N 名

採用 lead-triage 的排名並選出前 `--n` 個，只要 lead 數量夠，就一定剛好是 `--n` 個，不管 pipeline 多大。同分時，優先選有未回覆的進線訊號的 lead。如果 lead-triage 回報分數過於平均，就改呈現它依 CRM 事實排的順序，並說明這點。

為每個選出的 lead 產生一張通話卡：

```
{Rank}. {Contact Name} — {Company}
Deal: {currency code} {amount} | Stage: {stage} | Last contact: {X days ago}
Signal: {most recent activity}

TALKING POINTS
• {point from email/deal context}
• {point from email/deal context}
• {open question to ask}

GOAL FOR THIS CALL: {one sentence — advance to next stage / re-engage / close}
```

## Step 3 — 行事曆排時段

清單上的每個 lead，都提議在老闆行事曆的目標日期排 20 分鐘。

顯示提議的行事曆項目：
```
{time slot} — Call: {Contact Name} ({Company})
```

建立行事曆事件之前，要等老闆確認要排哪些通話。

## Step 4 — 草擬後續訊息

對於任何有未回覆 email 超過 3 天的 lead，草擬一封簡短的後續訊息：
```
Subject: Re: {thread subject}

Hi {first name},

{One sentence referencing prior conversation}. {One sentence with a clear next step or question}.

{Sign-off}
```

## Connector 失敗

如果連不到 HubSpot，就停下來告訴老闆，因為 lead 評分需要 CRM 資料。如果連不到 Mail，就跳過 Step 1 的 email 脈絡擷取和 Step 4 的後續草稿，並在輸出裡註明「Mail not connected — email context and follow-up drafts skipped」；Step 3 的行事曆排時段照樣執行。如果連不到 Google Calendar，就跳過行事曆排時段並註明。如果 lead 資料的 connector 連不到，或老闆拒絕補強資料的花費，沒有公司資料的 lead 其公司適配度就維持平均，要在輸出裡說明，不要把那個順序當成依適配度排的呈現。

## 核准關卡

- **絕對不要自動寄 email。** 草稿只能交給老闆核准。
- **沒有老闆確認，絕對不要建立行事曆時段**，要先顯示提議的清單。
- **絕對不要自動更新 HubSpot 的 deal 階段。**

## 輸出

呈現排好名的通話清單和談話腳本。然後顯示提議的行事曆時段並請老闆確認。接著顯示後續草稿，並問要寄哪些。

在聊天摘要之外（絕對不是取代它），用 house style（`../../shared/artifact-style.md`）把清單渲染成一份 CALL SHEET artifact：讓老闆印出來、邊撥號邊用的東西。版面要適合列印，每個 lead 一列，各帶通話目標和兩三個簡短的談話重點，再加一條空白的結果欄可以隨手寫。這是工作用的表單，不是 dashboard，不要放數字卡，也不要放圖表。

## 收尾提議

收尾用一行說明建了什麼，然後給一個最相關的下一步和它的觸發說法，通常是替需要寫 email 而不是打電話的 lead 用「write this outreach」（`outreach-composer`）。最多再加兩個：「fill my funnel」（`/grow-pipeline`）或「update the CRM」（`crm-autopilot`）。最多三個，這個 session 稍早老闆拒絕過的就跳過。

## 使用沒列出的工具

這個 skill 裡提到的 connector 是測試過的路徑，不是一道牆。如果老闆想讓這個流程用某個沒連線或沒列出的工具，就提議 `build-connector`，它會先查 connector 目錄，沒有的話再透過 Zapier 連接，絕對不手工對著原始 API 硬幹。連線建好之後，這個工具就像其他任何可選的 connector 一樣加入這個 skill，受同樣的核准關卡約束。
