---
name: email-sequence
description: 設計並起草多封 email 的 sequence，包含完整文案、時機、分支邏輯、退出條件和成效基準。建構 onboarding、lead nurture、re-engagement、win-back 或產品發表的流程、需要附 A/B 測試建議的完整 drip campaign，或要用流程圖把 sequence 從頭到尾畫出來時使用。
argument-hint: "[sequence type]"
---

# Email Sequence

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

為任何生命週期或 campaign 的使用情境，設計並起草完整的 email sequence，包含完整文案、時機、分支邏輯和成效基準。

## 觸發

使用者執行 `/email-sequence`，或要求建立、設計、建構或起草 email sequence、drip campaign、nurture 流程或 onboarding 系列。

## 輸入

向使用者蒐集以下資訊。沒有提供的話，先問再繼續：

1. **Sequence 類型**：下列之一：
   - Onboarding
   - Lead nurture
   - Re-engagement
   - 產品發表
   - 活動後跟進
   - 升級／upsell
   - Win-back
   - 教育型 drip

2. **目標**：這個 sequence 要達成什麼（例如：啟用新使用者、把 lead 轉成客戶、降低流失、帶動活動出席、upsell 到更高的方案）

3. **受眾**：誰會收到這個 sequence、他們在哪個階段，以及任何相關的分眾細節（職務、產業、行為觸發、生命週期階段）

4. **Email 封數**（選填）：沒指定的話，依 sequence 類型，使用下面「Sequence 類型範本」段落的範本推薦封數

5. **時機／頻率偏好**（選填）：希望的寄信間隔（例如「每 3 天」「每週」「第一週密集，之後逐漸放緩」）

6. **品牌語氣**：如果本機設定有設定，就自動套用並告知使用者。如果沒設定，就問：「Do you have brand voice guidelines I should follow? If not, I'll use a clear, conversational professional tone.」

7. **其他脈絡**（選填）：
   - 要包含的特定優惠、折扣或誘因
   - 要連結的 CTA 或 landing page
   - 可用的內容素材（部落格文章、案例研究、影片、指南）
   - 要突顯的產品功能
   - 要引用的競品差異點

## 流程

### 1. Sequence 策略

起草任何 email 之前，先定義整體的 sequence 架構：

- **敘事弧線**：這個 sequence 在所有 email 中說了什麼故事？從第一封到最後一封，情感和邏輯上怎麼推進？
- **旅程對應**：把每封 email 對應到買家或使用者旅程的某個階段（awareness、consideration、decision、activation、expansion）
- **升級邏輯**：每封 email 的強度、急迫性或價值，怎麼在前一封的基礎上往上疊？
- **成功定義**：什麼具體行動代表這個 sequence 完成任務、收件人該退出了？

### 2. 單封 Email 設計

為 sequence 中的每封 email，產出：

#### 主旨行
- 每封提供 2 到 3 個選項
- 變換手法：好奇、以效益為主、急迫、個人化、問句式
- 盡量控制在 50 個字元以內；註明在手機上的預覽行為

#### 預覽文字
- 40 到 90 個字元，補充（不是重複）主旨行
- 要增加脈絡或懸念，提高開信的可能性

#### Email 目的
- 一句話說明這封 email 為什麼存在，以及它要把收件人推向哪裡

#### 內文
- 可以直接使用的完整草稿
- 層級清楚：hook、內文、CTA
- 短段落（最多 2 到 3 句）
- 好掃讀的排版，適當時用粗體標出關鍵片語
- 相關的地方放個人化 token（例如名字、公司名稱、使用的產品）

#### 主要 CTA
- 按鈕文字和目的地
- 每封 email 一個主要 CTA（只有在適合該 sequence 階段時才加次要 CTA）

#### 時機
- 觸發事件後或前一封 email 後的第幾天
- 如果時機該依互動調整，要註明（例如「如果他們有開信但沒點擊，就提早寄」）

#### 分眾／條件備註
- 誰會收到這封 email、誰會跳過
- 任何依行為或屬性的條件（例如「只寄給還沒完成設定的使用者」）

### 3. Sequence 邏輯

定義這個 sequence 的流程控制：

- **分支條件**：依互動走不同路徑。例如：
  - 「如果開了第 2 封但沒點 CTA，就寄第 2b 封（較溫和的再次邀請），取代第 3 封」
  - 「如果點了第 1 封的 CTA，就跳過第 2 封，直接寄第 3 封」
- **退出條件**：收件人轉換（完成期望的行動）時，就把他們移出 sequence。要定義在這個 sequence 裡「轉換」是什麼意思。
- **重新進入規則**：有人可以重新進入這個 sequence 嗎？在什麼條件下？（例如「如果使用者 90 天後再次流失，就重新進入 win-back sequence」）
- **抑制規則**：如果收件人已經在另一個進行中的 sequence、已退訂行銷信，或過去 48 小時內聯絡過客服，就不要寄

### 4. 成效基準

依 sequence 類型提供預期的基準，讓使用者可以設定目標：

| 指標 | Onboarding | Lead Nurture | Re-engagement | Win-back |
|--------|-----------|--------------|---------------|----------|
| 開信率 | 50-70% | 20-30% | 15-25% | 15-20% |
| 點擊率 | 10-20% | 3-7% | 2-5% | 2-4% |
| 轉換率 | 15-30% | 2-5% | 3-8% | 1-3% |
| 退訂率 | <0.5% | <0.5% | 1-2% | 1-3% |

如果使用者有提供產業和受眾的脈絡，就依此調整基準。

## Sequence 類型範本

把這些當作起步的框架。依使用者的目標和受眾調整長度和內容。

**Onboarding（14 到 21 天內 5 到 7 封）：**
歡迎並設定預期 -- 快速成功案例展現價值 -- 核心功能深入介紹 -- 進階功能或整合 -- 社會認證和社群 -- 關心近況並徵求回饋 -- 升級提示或後續步驟

**Lead Nurture（3 到 4 週內 4 到 6 封）：**
以價值為先的教育內容 -- 找出痛點 -- 搭配佐證的解決方案定位 -- 社會認證和成果 -- 軟性 CTA（試用、demo、資源） -- 直接 CTA（購買、預約、註冊）

**Re-engagement（10 到 14 天內 3 到 4 封）：**
「We miss you」並附上有說服力的回來理由 -- 提醒價值，強調他們錯過了什麼 -- 誘因或專屬優惠 -- 附明確期限的最後機會

**Win-back（30 天內 3 到 5 封）：**
友善地關心，問哪裡出了問題 -- 他們離開後有什麼新東西 -- 特別優惠或回來的誘因 -- 徵求回饋（即使他們不回來） -- 最後的道別，並留一扇門

**產品發表（2 到 3 週內 4 到 6 封）：**
預告或預先公告 -- 附完整細節的發表公告 -- 功能亮點或使用案例 -- 社會認證和早期成果 -- 限時優惠或加碼 -- 最後機會或提醒

**活動後跟進（7 到 10 天內 3 到 4 封）：**
感謝並附上重點心得或錄影 -- 活動資源整理 -- 相關優惠或下一步 -- 意見調查

**升級／Upsell（2 到 3 週內 3 到 5 封）：**
使用量里程碑或成功的慶祝 -- 他們碰到的功能缺口或限制 -- 附佐證的升級效益 -- 限時誘因 -- 方案的直接比較

**教育型 Drip（4 到 6 週內 5 到 8 封）：**
介紹以及他們會學到什麼 -- 第 1 課：基礎概念 -- 第 2 課：中階概念 -- 第 3 課：進階概念 -- 實際應用或練習 -- 資源整理 -- 結業和後續步驟

## 工具整合

### 如果有連接 ~~email marketing（例如 Klaviyo、Mailchimp、Customer.io）
- 說明如何在該平台把 sequence 設成 flow 或自動化
- 註明可以使用的平台專屬功能（例如 smart send time、條件分流、A/B 測試）
- 把分支邏輯對應到該平台視覺化 flow builder 的概念

### 如果有連接 ~~marketing automation 或 ~~CRM（例如 HubSpot、Marketo）
- 參考 lead scoring 資料，來決定分眾和退出條件
- 用生命週期階段資料，為各分眾調整訊息
- 註明如何依 CRM 屬性或名單成員身分設定加入觸發條件

### 如果沒有連接任何工具
- 以可以直接複製貼上的格式交付所有 email 內容
- 附上一份使用者在任何 email 平台都能照著做的設定檢查清單：
  1. 建立自動化或 flow
  2. 設定加入觸發條件
  3. 依指定的延遲加入每封 email
  4. 設定分支和退出條件
  5. 為建議的指標設定追蹤

## 輸出

用以下段落呈現完整的 sequence：

### Sequence 總覽表

| # | Subject Line | Purpose | Timing | Primary CTA | Condition |
|---|-------------|---------|--------|-------------|-----------|

### 完整 Email 草稿
每封 email 都附主旨行選項、預覽文字、目的、內文、CTA、時機和分眾備註。

### Sequence 流程圖
用純文字畫出 email 流程、分支路徑和退出點的圖。使用清楚的格式，例如：

```
[Trigger] --> Email 1 (Day 0)
                |
          Opened? --Yes--> Email 2 (Day 3)
                |              |
                No        Clicked CTA? --Yes--> [EXIT: Converted]
                |              |
                v              No
          Email 1b (Day 2)     |
                |              v
                +--------> Email 3 (Day 7)
                               |
                               v
                          Email 4 (Day 10)
                               |
                          [EXIT: Sequence complete]
```

### 分支邏輯備註
把所有條件、退出和抑制，整理成一份參考清單。

### A/B 測試建議
- 2 到 3 個建議的 A/B 測試（主旨行、CTA 文字、寄送時間、email 長度）
- 要測什麼、怎麼分流，以及怎麼衡量勝出者

### 要追蹤的指標
- 這個 sequence 的主要轉換指標
- 每封 email 的指標：開信率、CTR、退訂率
- Sequence 層級的指標：整體轉換率、轉換所需時間、流失點
- 建議的檢視頻率（例如「第一個月每週檢視成效，之後每月」）

## Sequence 結束之後

問：「Would you like me to:
- Revise the copy or tone for any specific email?
- Add a branching path for a specific scenario?
- Create a variation of this sequence for a different audience segment?
- Draft the A/B test variants for the subject lines?
- Build a companion sequence (e.g., a post-purchase follow-up after this lead nurture converts)?」
