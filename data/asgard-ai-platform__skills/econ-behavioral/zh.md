---
name: "econ-behavioral"
description: "運用行為經濟學的概念（有限理性、展望理論、心理帳戶、推力理論）分析決策偏誤。當使用者需要理解人們為什麼做出不理性的經濟決策、設計選擇架構，或運用推力（nudge）影響行為時使用。就算使用者只說「為什麼客戶老是做出不好的選擇」、「怎麼鼓勵大家多存錢」或「設計一個更好的預設選項」也要用。"
metadata:
  category: "WP-17 經濟學院"
  tags: ["economics", "behavioral-economics", "decision-making"]
---

# 行為經濟學

## 概述

行為經濟學研究心理因素如何讓人偏離理性的經濟預測。古典經濟學假設行為者是理性的，行為經濟學則記錄系統性的偏誤，並設計介入措施（推力）來改善決策。

## 框架

```
IRON LAW: Biases Are Systematic, Not Random

Behavioral biases are PREDICTABLE patterns, not noise. Loss aversion
doesn't sometimes make people risk-seeking and sometimes not — it
consistently makes people overweight losses relative to equivalent gains
(roughly 2:1 ratio). Use specific bias names and their documented effects,
not vague "people are irrational."
```

### 核心概念

**有限理性（Bounded Rationality）**（Simon）：因為認知資源有限，人們會「滿意即可」（找「夠好」的），而不是最佳化。

**展望理論（Prospect Theory）**（Kahneman & Tversky）：
- **損失趨避**：損失帶來的痛，大約是等量獲得帶來的快樂的 2 倍
- **參考點依賴**：人們是相對於參考點來評價結果，不是用絕對值
- **邊際敏感度遞減**：從 $0 到 $100 的差別，感覺比 $1000 到 $1100 的差別大

**心理帳戶（Mental Accounting）**（Thaler）：人們會把錢分成心裡的「桶子」（房租、娛樂、儲蓄），並區別對待，違反了金錢的可替代性。

**框架效應（Framing Effect）**：同樣的資訊用不同方式呈現，會導致不同的決定。「90% 存活率」vs「10% 死亡率」，同一個事實，不同的選擇。

### 商業應用的關鍵偏誤

| 偏誤 | 定義 | 商業應用 |
|------|-----------|---------------------|
| **錨定效應（Anchoring）** | 先看到的數字會影響後續的估計 | 在折扣前先秀出較高的「原價」 |
| **預設效應（Default effect）** | 人們會堅持預先選好的選項 | 訂閱、器官捐贈用 opt-out 比 opt-in 好 |
| **社會認同（Social proof）** | 人們會跟著別人做 | 「1,000 位以上客戶選了這個方案」 |
| **稀缺性（Scarcity）** | 供應有限會提高感知價值 | 「庫存只剩 3 件」 |
| **稟賦效應（Endowment effect）** | 人們會高估自己已擁有的東西 | 免費試用讓取消感覺像損失 |
| **現時偏誤（Present bias）** | 人們會過度重視眼前的獎勵，輕忽未來的 | 「今天免費開始」> 「12 個月內幫你省錢」 |
| **沉沒成本謬誤（Sunk cost fallacy）** | 過去的投入影響未來的決定（本來不該） | 「我已經看了 2 小時，應該把電影看完」 |
| **現狀偏誤（Status quo bias）** | 偏好現狀、不喜歡改變 | 既有客戶就算有更好的選擇也很少轉換 |

### 推力設計框架（Thaler & Sunstein）

有效推力的 **EAST 框架**：
- **Easy（容易）**：降低阻力。簡化表單、預先填入資料、減少步驟。
- **Attractive（吸引人）**：讓期望的行動在視覺上醒目、有吸引力。
- **Social（社會性）**：顯示別人在做什麼。同儕比較、使用者見證。
- **Timely（及時）**：在做決定的當下送出推力，不要太早或太晚。

### 分析步驟

1. **找出決策情境**：使用者/客戶正在做什麼選擇？
2. **對應相關偏誤**：哪些系統性偏誤可能在起作用？
3. **評估目前的選擇架構**：這個決策現在是怎麼呈現的？
4. **設計介入措施**：用 EAST 框架運用推力
5. **測試**：拿介入措施跟目前的設計做 A/B 測試

## 輸出格式

```markdown
# Behavioral Analysis: {Decision Context}

## Decision Context
- Decision-maker: {who}
- Choice: {what they're deciding}
- Current behavior: {what they typically do}
- Desired behavior: {what we want them to do}

## Biases Identified
| Bias | How It Manifests | Impact |
|------|-----------------|--------|
| {bias} | {specific manifestation} | H/M/L |

## Current Choice Architecture
{How the decision is currently structured and why it triggers biases}

## Proposed Nudges
| Nudge | EAST Principle | Expected Effect |
|-------|---------------|----------------|
| {intervention} | Easy/Attractive/Social/Timely | {predicted change} |

## Testing Plan
- Control: {current design}
- Treatment: {nudged design}
- Metric: {conversion rate / opt-in rate / etc.}
- Sample size: {N}
```

## 範例

### 正確的做法
**情境：** 提高一家台灣公司的退休儲蓄參與率

**起作用的偏誤：**
- **現狀偏誤**：員工不加入，因為要主動 opt in
- **現時偏誤**：退休是幾十年後的事，現在花錢感覺比較急
- **損失趨避**：每月從薪水扣款感覺像損失

**推力設計：**
| 推力 | 原則 | 介入措施 |
|-------|-----------|-------------|
| 自動加入 | **Easy**（預設） | 從 opt-in 改成 opt-out（預設提撥 3%） |
| 逐步提高 | **Timely** | 「每次年度調薪時，提撥比例增加 1%」，時間點配合加薪，讓扣款不會感覺像損失 |
| 社會認同 | **Social** | 「你 78% 的同事都有參加退休計畫」 |

**預測效果**：光是自動加入，通常就能讓參與率從約 30% 提高到約 90%（文獻上有充分記錄）✓

### 錯誤的做法
- 「人是不理性的，所以我們應該操縱他們」→ 行為經濟學找出的是系統性模式，不是隨機的不理性。推力應該幫助人們做出符合「他們自己」所述目標的決定，不是違背他們的利益去操縱。違反 Iron Law 和倫理原則。

## 常見陷阱

- **推力是自由意志家長主義**：它保留選擇權，同時引導人走向更好的結果。如果推力把選擇拿掉了，那就不是推力，是強制命令。
- **偏誤會互相作用**：損失趨避 + 錨定 + 框架可以疊加。「省下 NT$300」（獲得框架）vs「別再每個月損失 NT$300」（損失框架 + 錨定），後者因為偏誤複合而更強。
- **文化差異**：有些偏誤因文化而異。社會認同在集體主義文化（台灣、日本）比個人主義文化強。要依情境校準。
- **推力疲勞**：同時用太多推力會降低效果。優先選影響最大的那個。
- **倫理界線**：利用偏誤賣人們不需要的東西（dark pattern）是剝削，不是推力。檢驗標準：如果對方知道這個推力，會感謝你嗎？

## 參考資料

- 展望理論的數學，見 `references/prospect-theory.md`
- dark pattern 與合乎倫理的推力，見 `references/ethics-of-nudging.md`
