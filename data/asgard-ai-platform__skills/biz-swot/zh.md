---
name: "biz-swot"
description: "用 SWOT 搭配 TOWS 矩陣做策略規劃分析。當使用者需要盤點優勢、劣勢、機會、威脅來評估公司、產品或專案，或想從內部與外部因素推導出策略選項時使用。就算使用者沒有明講 SWOT，只要提到競爭定位、策略評估，或問「我們的優勢和風險是什麼」，也要使用這個 skill。"
metadata:
  category: "WP-13 商學院—策略"
  tags: ["business-strategy", "swot", "tows"]
---

# SWOT 分析與 TOWS 矩陣

## 概述

SWOT 把策略評估拆成內部因素（優勢、劣勢）和外部因素（機會、威脅）。接著 TOWS 矩陣把這四個象限兩兩交叉，產出具體的策略選項。這個 skill 帶你走完整個流程：從找出因素、排優先順序，到擬定可執行的策略。

## 何時使用

**觸發條件：**
- 使用者要評估公司、產品、團隊或專案的策略位置
- 使用者需要找出優勢、風險或競爭因素
- 使用者想把情勢分析轉成策略選項
- 使用者提到「SWOT」、「優劣勢」或「策略評估」

**何時不要用：**
- 要看產業層級的競爭態勢 → 用 Porter 五力
- 要掃描總體環境 → 用 PESTEL
- 要做產品組合決策 → 用 BCG 矩陣
- 使用者只需要財務分析，不需要策略定位

## 框架

```
IRON LAW: Internal vs External Classification

Strengths and Weaknesses are INTERNAL — they originate from within the
organization and the organization can directly control or change them.
Examples: proprietary technology, brand reputation, team expertise, cost
structure, operational processes.

Opportunities and Threats are EXTERNAL — they originate from the environment
and the organization cannot directly control them.
Examples: market trends, regulatory changes, competitor actions, economic
conditions, technological shifts.

NEVER classify an external trend as a Strength or Weakness.
NEVER classify an internal capability as an Opportunity or Threat.

Test: "Can the organization decide to change this tomorrow?"
  YES → Internal (S or W)
  NO  → External (O or T)
```

```
IRON LAW: Completeness Before Synthesis

Complete ALL four quadrants before generating strategies.
Do NOT jump to recommendations after identifying only strengths and
opportunities. Skipping W or T produces dangerously optimistic strategies.
```

### 步驟 1：找出內部因素（S 和 W）

檢視組織的資源、能力和績效：

- **有形**：財務資源、實體資產、技術、專利
- **無形**：品牌資產、文化、專業知識、關係、聲譽
- **能力**：流程、技能、管理品質、創新紀錄

每個因素都要跟競爭對手比，分類成優勢（競爭優勢）或劣勢（競爭劣勢）。要講具體：「團隊很好」太籠統；「工程團隊有 5 年以上 ML 部署經驗」才有辦法行動。

### 步驟 2：找出外部因素（O 和 T）

從以下面向掃描環境：

- **市場**：成長趨勢、客戶需求轉變、新的客群
- **競爭**：競爭對手動向、新進者、替代品
- **總體**：法規、經濟、技術、社會的變化
- **產業特有**：供應鏈轉移、通路演變、標準變動

每個因素分類成機會（有利）或威脅（不利）。每個因素都要有證據支撐，盡量引用資料、趨勢或具體事件。

### 步驟 3：排優先順序

不是每個因素分量都一樣。每個象限內，依下列項目排序：

1. **影響**：對組織的影響有多大？（高 / 中 / 低）
2. **可能性**（只針對 O 和 T）：發生的機率多高？（高 / 中 / 低）
3. **急迫性**：有沒有時間壓力？

每個象限留前 3 到 5 個因素進 TOWS 矩陣。放太多會稀釋分析。

### 步驟 4：建立 TOWS 矩陣

把四個象限交叉，產出四種策略：

| | **機會** | **威脅** |
|---|---|---|
| **優勢** | **SO 策略**：用優勢抓住機會 | **ST 策略**：用優勢抵禦威脅 |
| **劣勢** | **WO 策略**：補強劣勢以抓住機會 | **WT 策略**：把劣勢降到最低以避開威脅 |

每個格子產出 1 到 3 個具體的策略選項。每個策略必須至少引用兩條軸各一個因素（例如 SO 策略一定要點名一個具體的優勢「和」一個具體的機會）。

### 步驟 5：擬定行動計畫

把最有希望的 TOWS 策略轉成可執行的建議：

1. 從四個格子裡挑出影響最大的 3 到 5 個策略
2. 每個策略都要定義：目標、負責人、時程、所需資源、成功指標
3. 標出策略之間的相依關係和可能的衝突

## 輸出格式

```markdown
# SWOT Analysis: {Subject}

## Internal Factors

### Strengths
| # | Factor | Evidence | Impact |
|---|--------|----------|--------|
| S1 | {specific strength} | {supporting data} | High/Med/Low |
| S2 | ... | ... | ... |

### Weaknesses
| # | Factor | Evidence | Impact |
|---|--------|----------|--------|
| W1 | {specific weakness} | {supporting data} | High/Med/Low |
| W2 | ... | ... | ... |

## External Factors

### Opportunities
| # | Factor | Evidence | Likelihood |
|---|--------|----------|-----------|
| O1 | {specific opportunity} | {supporting data} | High/Med/Low |
| O2 | ... | ... | ... |

### Threats
| # | Factor | Evidence | Likelihood |
|---|--------|----------|-----------|
| T1 | {specific threat} | {supporting data} | High/Med/Low |
| T2 | ... | ... | ... |

## TOWS Strategy Matrix

| | Opportunities (O1, O2...) | Threats (T1, T2...) |
|---|---|---|
| **Strengths** | SO: {strategy using S to capture O} | ST: {strategy using S to counter T} |
| **Weaknesses** | WO: {strategy to fix W and capture O} | WT: {strategy to minimize W and avoid T} |

## Recommended Actions
1. **{Strategy name}** — {description} (from: {SO/ST/WO/WT})
   - Timeline: ...
   - Success metric: ...
2. ...
```

## 範例

### 正確的做法

**情境：** 一家台灣中型珍珠奶茶連鎖品牌，考慮擴展到日本，替它做 SWOT

**分析：**

| 象限 | 因素 | 分類 | 理由 |
|----------|--------|---------------|-----------|
| **S** | 獨家珍珠配方，口感獨特 | 內部 ✓ | 公司自己的研發成果 |
| **S** | 台灣 50 間門市，SOP 已驗證 | 內部 ✓ | 公司的營運資產 |
| **W** | 沒有會日文的管理團隊 | 內部 ✓ | 公司自己的資源缺口 |
| **W** | 海外擴張資金有限 | 內部 ✓ | 公司自己的財務限制 |
| **O** | 日本珍奶市場年增 15% | 外部 ✓ | 市場趨勢，公司控制不了 |
| **O** | 疫後日台觀光回溫 | 外部 ✓ | 總體環境因素 |
| **T** | 日本已有成熟的競爭者（貢茶、CoCo） | 外部 ✓ | 競爭態勢 |
| **T** | 日圓貶值推高進口成本 | 外部 ✓ | 經濟條件 |

**TOWS 策略範例：**
- **SO**：運用獨家配方（S1）在成長中的日本市場（O1）做出差異化，定位成「道地的台灣職人茶飲」
- **WT**：處理資金受限（W2）的問題，並把匯率風險（T2）降到最低，原料盡量在日本當地採購

### 錯誤的做法

**情境：** 同一家珍奶連鎖品牌

**哪裡做錯了：**

| 因素 | 被放在 | 應該是 | 原因 |
|--------|-----------|-----------|-----|
| 「日本珍奶市場年增 15%」 | **優勢** ❌ | **機會** | 市場成長是外部趨勢，公司控制不了。違反 Iron Law：S/W 只能放內部因素。 |
| 「我們的團隊缺乏經驗」 | **威脅** ❌ | **劣勢** | 團隊組成是內部的，要請誰公司自己決定。違反 Iron Law：O/T 只能放外部因素。 |
| 「品牌很好」 | **優勢** ⚠️ | 需要更具體 | 太籠統，沒辦法行動。品牌好在哪？在台灣的知名度？社群追蹤數？還是具體的獎項？ |

## 常見陷阱

- **把「市場地位」搞混內外部**：「我們是第 3 名」感覺像內部因素，但排名本身是市場動態決定的。要拆開：「北台灣有強大的配銷網絡」（S，內部能力）對「市場整併讓競爭者變少」（O 或 T，外部趨勢）。
- **把基本門檻當優勢**：如果每個競爭對手都有網站，「我們有網站」就不是優勢。優勢一定是相對競爭對手的優勢。
- **把「沒有威脅」誤認成機會**：「這個利基市場沒有大型競爭者」不是機會，可能代表這個利基根本做不起來。機會需要一個正面的外部趨勢或事件。
- **TOWS 策略只參照單一軸**：「擴展到日本」不是 TOWS 策略。它必須跨象限：「運用獨家配方（S1）進入成長中的日本市場（O1）」。
- **範圍失控**：對「整間公司」做 SWOT 太廣。要把範圍縮到一個具體決策：「擴展到日本的 SWOT」或「推出新產品線的 SWOT」。
- **近因偏誤**：近期事件會主導整個分析。要刻意把結構性的長期因素跟當前事件一起考慮。

## 參考資料

- TOWS 矩陣的詳細案例研究，見 `references/tows-case-studies.md`
- 與其他策略框架（Porter、PESTEL、BCG）的比較，見 `references/framework-comparison.md`
