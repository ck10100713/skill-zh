---
name: "ops-okr-planning"
description: "設計並導入 OKR（目標與關鍵成果），用於設定目標，並讓各組織層級對齊策略。使用者需要設定團隊或公司的目標、讓各部門對齊策略、追蹤每季進度，或要從 KPI 轉換到 OKR 制度時使用，就算他們說的是「設定我們的季度目標」、「OKR 是怎麼運作的」、「讓團隊目標對齊公司願景」或「我們的目標感覺互相脫節」也一樣。"
metadata:
  category: "WP-10 通用商業"
  tags: ["business", "okr", "goal-setting", "performance"]
---

# OKR 規劃

## 框架

```
IRON LAW: Objectives Are Ambitious, Key Results Are Measurable

Objective: Qualitative, inspiring, directional. "Become the #1 choice
for SMB accounting in Taiwan."

Key Result: Quantitative, measurable, time-bound. "Increase NPS from
32 to 50 by Q4."

If you can't measure it, it's not a Key Result. If it's not ambitious,
it's not an Objective.
```

### OKR vs KPI

| 面向 | OKR | KPI |
|--------|-----|-----|
| 目的 | 推動改變、設定方向 | 監控持續的績效 |
| 企圖心 | 挑戰性目標（達成 70% 就算成功） | 目標值（預期達成 100%） |
| 週期 | 每季 | 持續進行 |
| 範圍 | 策略優先事項（每個層級 3-5 個） | 營運指標（很多） |
| 評分 | 0.0 - 1.0 的尺度 | 以門檻值為基礎 |

### OKR 結構

```
Objective: {Inspiring, qualitative goal}
├── KR1: {Measurable result} — baseline: X → target: Y
├── KR2: {Measurable result} — baseline: X → target: Y
└── KR3: {Measurable result} — baseline: X → target: Y
```

規則：
- 每個層級（公司、團隊、個人）3-5 個 Objective
- 每個 Objective 2-5 個 Key Result
- 至少有一個 KR 應該是領先指標（不能全是落後指標）
- 挑戰性目標達成 70% 是「甜蜜點」

### 對齊（逐層展開）

```
Company OKR: "Become the market leader in Taiwan SMB accounting"
    ↓
Product Team: "Make onboarding effortless"
  KR: Reduce time-to-first-value from 7 days to 1 day
    ↓
Engineering: "Ship self-serve onboarding flow"
  KR: Launch wizard by March 15, 80% completion rate
```

每一層的 OKR 都應該「貢獻」給上一層，但不應該是複製貼上。團隊要把公司的目標轉譯成自己領域的目標。

### OKR 節奏

| 活動 | 頻率 | 參與者 |
|----------|-----------|-------------|
| **設定 OKR** | 季初 | 領導層 + 團隊主管 |
| **每週檢視** | 每週（15 分鐘） | 團隊站會 |
| **季中檢討** | 季中 | 團隊 + 主管 |
| **季末評分** | 季末 | 所有人 |
| **回顧** | 評分之後 | 團隊 |

### 評分指南

| 分數 | 意義 |
|-------|---------|
| 0.0-0.3 | 沒能做出有意義的進展 |
| 0.4-0.6 | 有進展但沒達標 |
| 0.7-0.8 | 甜蜜點：有企圖心的目標，加上扎實的執行 |
| 0.9-1.0 | 要嘛完美達成（太棒了！），要嘛目標不夠有企圖心 |

## 輸出格式

```markdown
# OKR Plan: {Team/Company} — {Quarter}

## Company Objectives
### O1: {Objective}
- KR1: {metric} — {baseline} → {target}
- KR2: {metric} — {baseline} → {target}
- KR3: {metric} — {baseline} → {target}

## Team OKRs (aligned to company)
### {Team Name}
#### O1: {Team objective} (supports Company O{N})
- KR1: {metric} — {baseline} → {target}
- KR2: ...

## Check-in Template
| KR | Target | Current | Confidence | Blocker |
|-----|--------|---------|-----------|---------|
| KR1 | {target} | {current} | 🟢/🟡/🔴 | {if any} |
```

## 注意事項

- **OKR 不是待辦清單**：「3 月前上線功能 X」是一項任務，不是 KR。要改寫成：「把用戶啟用率從 30% 提高到 50%」，KR 衡量的是「成果」，不是產出。
- **達成 100% 代表不夠有企圖心**：如果每個 OKR 都拿 1.0，代表目標太容易。要鼓勵挑戰。
- **不要把 OKR 直接跟薪酬綁在一起**：這會讓人設定安全、做得到的目標，而不是有企圖心的目標。OKR 用來對齊和學習，不是用來發獎金。
- **先從公司 OKR 開始**：沒有公司 OKR 就先訂團隊 OKR，會導致沒有對齊。方向由上而下，怎麼達成則由下而上提供意見。
- **目標最多 3-5 個**：目標越多，焦點越少。如果什麼都是優先，就沒有什麼是優先。

## 參考資料

- OKR 評分範本請看 `references/okr-templates.md`
- 與 BSC 的比較請看 biz-bsc skill
