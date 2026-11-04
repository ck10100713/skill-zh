---
name: strategy-document
description: "為中小企業撰寫結構化的策略文件：SWOT 分析、精實商業計畫、OKR、競爭分析。每種模式都有明確的結構和品質標準。只要企業想闡述策略、設定目標、分析競爭對手、規劃成長、做 SWOT、寫 OKR 或建立精實商業計畫，就用這個 skill。產出可執行的文件，不是泛泛的框架。"
---

# Strategy Document Writer

產出具體到可以直接行動的策略文件。品質標準：每一句陳述都要能被檢驗真偽（"We have 3 React developers with 10+ years experience"，而不是 "We have a strong team"），每一項建議都要能在明確的時間內執行完。

## 流程

### 步驟 1：決定模式

問使用者需要哪種文件：

1. **SWOT 分析**：評估目前的處境
2. **商業計畫**（精實版或完整版）：闡述商業模式
3. **OKR / 目標**：設定可衡量的目標
4. **競爭分析**：了解市場全貌

如果使用者不確定，就問他想做什麼決定，通常就能看出該用哪種模式：
- "我們該進入這個市場嗎？" -> 競爭分析 + SWOT
- "這一季我們該專注在什麼？" -> OKR
- "我們需要募資 / 合作夥伴簡報" -> 商業計畫
- "感覺哪裡不對勁，但說不出來" -> SWOT

### 步驟 2：收集背景資訊

詢問：
- 企業名稱、產業、規模（團隊人數，方便的話提供營收）
- 目前狀況（什麼事讓你想做這件事？）
- 主要競爭對手（如果知道）
- 時間範圍（這一季、今年、三年）
- 文件的讀者（內部團隊、董事會、投資人、銀行、自己想清楚）

讀者決定細節的程度。銀行要財務預測，創辦人要釐清思緒，團隊要方向。

### 步驟 3：起草並驗證

寫完文件後，每一條都用「具體性測試」檢查：這句話放到產業裡任何一家公司都成立嗎？如果是，就太模糊了。用使用者的具體情境重寫。

---

## 模式 1：SWOT 分析

### 結構

用 2x2 表格呈現，每個象限 3-5 點。每一點一句話，要具體、可執行。

```
             HELPFUL                    HARMFUL
          to achieving objectives    to achieving objectives

INTERNAL  STRENGTHS                  WEAKNESSES
(origin)  - ...                      - ...
          - ...                      - ...

EXTERNAL  OPPORTUNITIES              THREATS
(origin)  - ...                      - ...
          - ...                      - ...
```

**內部**（Strengths、Weaknesses）= 企業能掌控的事：團隊技能、流程、技術、財務、文化、智慧財產。

**外部**（Opportunities、Threats）= 企業無法掌控的事：市場趨勢、競爭對手、法規、經濟狀況、技術轉變。

### 條目的品質標準

| 太模糊 | 具體又有用 |
|-----------|-------------------|
| "Strong team" | "3 developers with 10+ years React experience; only 1 has backend skills" |
| "Good reputation" | "4.8 Google rating from 127 reviews; 94% client retention over 3 years" |
| "Growing market" | "Australian SME SaaS market growing 12% annually (IBISWorld 2025)" |
| "Competition" | "Competitor X launched a free tier in Q4 2025, capturing 200+ of our target segment" |
| "Cash flow issues" | "Average debtor days: 58; target: 30. $120K outstanding beyond 60 days" |

每個條目都要通過 "so what?" 測試：必須清楚說明這一點為什麼對策略決策重要。

### "So What?" 區塊

表格之後，加一個把發現轉成行動的區塊：

**策略意涵：**
- 哪些優勢可以用來對付哪些機會？（進攻）
- 哪些劣勢會被哪些威脅暴露出來？（防守）
- 企業該開始做什麼、停止做什麼、改變什麼？

這是 SWOT 最有價值的部分。只有表格、沒有意涵，只是在分類，不是策略。

### 反模式

- 同一點同時列在 Strengths 和 Opportunities（如果是內部的，就是優勢）
- 在 Strengths/Weaknesses 裡放企業無法影響的項目
- 放泛泛的條目，套到產業裡每家公司都成立
- 沒有意涵區塊，光有表格無法執行

---

## 模式 2：商業計畫

### 精實格式（一頁）

讀者是創辦人或需要釐清思緒的小團隊時使用。每個區塊一段，不灌水。

| 區塊 | 要寫什麼 |
|---------|--------------|
| **Problem** | 存在什麼痛點？誰感受到？他們現在怎麼應付？ |
| **Solution** | 這個事業提供什麼？一句話講完。 |
| **Key Metrics** | 3-5 個代表健康度的數字（MRR、churn、CAC、LTV、NPS） |
| **Unique Value Prop** | 為什麼選這家而不選其他替代方案？一句話。 |
| **Channels** | 顧客怎麼找到你？依成效排序。 |
| **Revenue Streams** | 錢怎麼進來？列出每個收入來源，附上大約佔總額的百分比。 |
| **Cost Structure** | 前 5 大成本類別，附上大約的月/年金額。 |
| **Unfair Advantage** | 什麼是不容易被複製的？（團隊專長、專有資料、網路效應、法規地位） |

每個區塊的測試：如果你無法用一段話講完，代表你還沒完全理解。重寫到講得出來為止。

### 完整格式

在精實格式之上加上：

- **Executive Summary**（最後寫，因為它要總結其他所有內容）
- **Market Analysis**：TAM/SAM/SOM 附來源、客群、市場趨勢
- **Financial Projections**：12 個月損益表、現金流預測、損益平衡分析
- **Team**：關鍵人物、他們的相關經驗、要補的缺口
- **Milestones**：未來 3、6、12 個月會發生什麼，附具體交付項目

### 計畫的寫作原則

- 現況用現在式，計畫用未來式。核心模式絕對不要用過去式。
- 財務預測必須明確寫出假設。"$50K MRR by month 12" 需要加上 "assuming 15% monthly growth from current $12K base and 5% churn."
- 要承認風險。投資人和貸款方信任看得到危險的創辦人，而不是假裝危險不存在的人。
- 不要空泛的願景話。"We aim to be the leading provider" 不是計畫。"We will acquire 200 paying customers in 12 months through Google Ads ($5K/month budget, target $25 CAC)" 才是計畫。

---

## 模式 3：OKR 與目標

### 結構

```
OBJECTIVE: [Qualitative, inspiring, time-bound]

  KR1: [Quantitative, measurable, has a number]
  KR2: [Quantitative, measurable, has a number]
  KR3: [Quantitative, measurable, has a number]
```

通常每季 3-5 個 Objective，每個有 3-5 個 Key Result。

### Objective

- 定性且鼓舞人心，描述期望的未來狀態
- 有時限（通常是一季）
- 有野心，但全力以赴就達得到（完成 70% 算健康）

| 太模糊 | 具體 |
|-----------|---------|
| "Improve our marketing" | "Establish a predictable inbound lead pipeline by end of Q2" |
| "Grow the business" | "Expand into the Brisbane market with a repeatable sales process by Q3" |
| "Be more efficient" | "Eliminate manual reporting bottlenecks across all client accounts by Q2" |

### Key Result

- 定量，有具體的目標數字
- 可衡量，季末可以檢查有沒有達成
- 是成果，不是任務

| 任務（錯） | 成果（對） |
|--------------|----------------|
| "Launch the new website" | "Achieve 1,000 monthly organic visitors to the new site" |
| "Hire 2 developers" | "Reduce average feature delivery time from 3 weeks to 1 week" |
| "Run Google Ads campaign" | "Generate 50 qualified leads at under $30 CAC" |
| "Write 12 blog posts" | "Grow organic traffic 40% (800 to 1,120 monthly sessions)" |

任務是你為了達成 Key Result 而做的活動，屬於專案計畫，不屬於 OKR。

### 評分

季末時，每個 KR 以 0.0 到 1.0 評分：
- 0.0-0.3：沒有任何有意義的進展
- 0.4-0.6：有進展但沒達標
- 0.7-0.9：交出了很強的成果（這是目標區間）
- 1.0：剛好達到目標（可能代表目標太容易）

如果每個 OKR 都拿 1.0，代表目標不夠有野心。如果每個 OKR 都低於 0.3，代表目標不切實際，或優先順序錯了。

---

## 模式 4：競爭分析

### 結構

先做比較矩陣，再解讀它。

**比較矩陣：**

| 因素 | 你的事業 | 競爭對手 A | 競爭對手 B | 競爭對手 C |
|--------|--------------|-------------|-------------|-------------|
| Price point | $X/mo | $Y/mo | $Z/mo | Free tier + $W/mo |
| Key feature 1 | Yes | Yes | No | Partial |
| Key feature 2 | No | Yes | Yes | Yes |
| Target market | AU SMEs | Enterprise | Startups | All segments |
| Strength | Personal service | Scale | Price | Brand recognition |
| Weakness | Small team | Impersonal | Limited features | Slow support |

### 解讀區塊

**你贏在哪：** 附證據的具體優勢。要寫 "Faster onboarding (3 days vs industry average of 2 weeks)"，不要寫 "better service"。

**你輸在哪：** 誠實的評估。"Competitor A has 10x our development team; we cannot match their feature velocity" 比假裝差距不存在有用得多。

**你的差異化在哪：** 你做得到、但別人在結構上做不到或選擇不做的事。這是策略上的金礦，會影響定位、訊息和產品決策。

**建議行動：** 根據分析，什麼該改變？要做的新功能、要主攻或避開的客群、定價調整、合作機會。

### 研究來源

- 競爭對手網站（定價頁、功能列表、案例研究）
- 評論網站（G2、Capterra、Google Reviews、ProductHunt）
- 徵才職缺（會透露他們的優先事項和缺口）
- 社群媒體和內容（定位、受眾、語氣）
- 產業報告（市場規模、成長率、趨勢）

如果使用者能接觸到競爭對手的真實客戶（透過業界人脈、論壇、社群媒體），第一手的回饋比任何公開報告都有價值。

---

## 寫作原則（所有模式）

**具體勝過模糊。** 每個論述都需要一個數字、一個名字，或一個具體例子。"Strong growth" 不是策略，"40% revenue increase from $850K to $1.19M" 才是策略。

**證據勝過意見。** 不要寫 "We believe the market is growing"，要寫 "The AU SaaS market grew 12% in 2025 (source)."。如果找不到證據，就直說，誠實的空缺比捏造的論述好。

**可執行勝過願景。** 每個區塊都要回答「我們拿這個資訊要做什麼？」如果某個 SWOT 條目或競爭洞察沒有帶出決策或行動，就不值得放進去。

**誠實面對弱點。** 只列優勢的策略文件沒有用。價值在於看見完整的全貌，包括不舒服的部分。投資人、合作夥伴和團隊都更信任誠實，而不是精緻的包裝。

**長度適中。** 精實商業計畫是一頁。SWOT 是一頁加上意涵。OKR 最多幾頁。競爭分析的長度隨競爭對手數量變化。不要為了長度灌水，每一句都要有存在的理由。

## 範例：SWOT 優勢條目

**太模糊：**
> Strong digital presence and good online reputation.

**正確做法：**
> 4.8 average Google rating from 127 reviews (highest among Newcastle web agencies). Website generates 35 qualified leads per month organically, with a 12% conversion rate to paying clients. Social media following of 2,400 across LinkedIn and Instagram, with 6.2% average engagement rate on case study posts.

第二個版本給讀者三個數據點，可以拿去跟競爭對手比較、對照產業平均、長期追蹤。
