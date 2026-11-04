---
name: product-lens
description: 在開工之前，用四種產品診斷先驗證「為什麼要做」：YC 風格的產品診斷（產出附帶 go/no-go 建議的 PRODUCT-BRIEF.md）、替 product-market-fit 訊號打分數的創辦人 review、衡量 time-to-value 的使用者旅程稽核，以及 ICE 功能優先順序。對產品方向做壓力測試、在功能之間做選擇、檢查上線前的合理性，或把模糊的點子轉成產品 brief 時使用。
metadata:
  origin: ECC
---

# Product Lens：做之前先想清楚

這條流程負責產品診斷，不負責撰寫可直接實作的規格。

如果使用者需要長期留存的 PRD 轉 SRS 或 capability 契約產出物，就交接給 `product-capability`。

## 何時使用

- 開始任何功能之前，先驗證「為什麼要做」
- 每週的產品 review，問自己：我們做的是對的東西嗎？
- 在功能之間卡住、無法選擇的時候
- 上線之前，檢查使用者旅程是否合理
- 在工程規劃開始之前，把模糊的點子轉成產品 brief

## 運作方式

### 模式 1：產品診斷

像 YC office hours，只是自動化。會問那些難回答的問題：

```
1. Who is this for? (specific person, not "developers")
2. What's the pain? (quantify: how often, how bad, what do they do today?)
3. Why now? (what changed that makes this possible/necessary?)
4. What's the 10-star version? (if money/time were unlimited)
5. What's the MVP? (smallest thing that proves the thesis)
6. What's the anti-goal? (what are you explicitly NOT building?)
7. How do you know it's working? (metric, not vibes)
```

輸出：一份 `PRODUCT-BRIEF.md`，包含答案、風險，以及 go/no-go 建議。

如果結果是「對，做這個」，下一條流程是 `product-capability`，不是更多創辦人的表演。

### 模式 2：創辦人 Review

用創辦人的視角來 review 你目前的專案：

```
1. Read README, CLAUDE.md, package.json, recent commits
2. Infer: what is this trying to be?
3. Score: product-market fit signals (0-10)
   - Usage growth trajectory
   - Retention indicators (repeat contributors, return users)
   - Revenue signals (pricing page, billing code, Stripe integration)
   - Competitive moat (what's hard to copy?)
4. Identify: the one thing that would 10x this
5. Flag: things you're building that don't matter
```

### 模式 3：使用者旅程稽核

描繪實際的使用者體驗：

```
1. Clone/install the product as a new user
2. Document every friction point (confusing steps, errors, missing docs)
3. Time each step
4. Compare to competitor onboarding
5. Score: time-to-value (how long until the user gets their first win?)
6. Recommend: top 3 fixes for onboarding
```

### 模式 4：功能優先順序

當你有 10 個點子，需要選出 2 個的時候：

```
1. List all candidate features
2. Score each on: impact (1-5) × confidence (1-5) ÷ effort (1-5)
3. Rank by ICE score
4. Apply constraints: runway, team size, dependencies
5. Output: prioritized roadmap with rationale
```

## 輸出

所有模式輸出的都是可執行的文件，不是長篇大論。每一條建議都有明確的下一步。

## 整合

搭配使用：
- `/browser-qa`：驗證使用者旅程稽核的發現
- `/design-system audit`：評估視覺上的完成度
- `/canary-watch`：上線後的監控
- `product-capability`：當產品 brief 需要變成可直接實作的 capability 計畫時
