---
name: "ux-lean-startup"
description: "運用精實創業方法論：Build-Measure-Learn 循環、MVP、驗證式學習和轉向決策。當使用者要推出新產品或創業，需要快速驗證點子、設計 MVP、決定要轉向還是堅持，或減少花在未驗證假設上的白工時使用這個 skill，就算他們說的是「我們該做這個嗎」、「怎麼測試這個點子」、「什麼時候該轉向」或「我們一直燒錢卻沒有成長」也一樣。"
metadata:
  category: "WP-21 設計/資訊/傳播/公衛"
  tags: ["product", "lean-startup", "mvp", "validation"]
---

# 精實創業

## 框架

```
IRON LAW: Validate Before You Build
（鐵律：先驗證，再建造）

每個產品決策都是一個假設。測試假設最貴的方式，
就是把完整產品做出來。最便宜的方式，是「先」用最少的力氣，
測試風險最高的那個假設。

「只要做出來，他們就會來」不是策略，是祈禱。
```

### Build-Measure-Learn 循環

1. **Build（建造）**：做出能測試你最高風險假設的最小東西（MVP）
2. **Measure（衡量）**：蒐集資料，看假設是否成立（用可行動的指標，不是虛榮指標）
3. **Learn（學習）**：資料驗證了還是推翻了假設？
   - 驗證 → 加碼，測試下一個假設
   - 推翻 → 轉向（改策略）或堅持（精進執行）

### MVP 類型（依投入程度排序）

| MVP 類型 | 投入 | 測試什麼 |
|----------|--------|---------------|
| 登陸頁 | 數小時 | 「有人想要這個嗎？」（註冊轉換率） |
| 說明影片 | 數天 | 「人們理解並渴望這個嗎？」 |
| Concierge（管家式） | 數天 | 「我們能用手動方式交付價值嗎？」（替 10 位顧客人工處理） |
| Wizard of Oz（綠野仙蹤） | 數週 | 「完整體驗行得通嗎？」（後端造假，前端是真的） |
| 單一功能 | 數週 | 「這個核心功能能解決問題嗎？」 |
| 可運作的原型 | 數月 | 「我們做得出來，而且使用者會採用嗎？」 |

### 虛榮指標 vs 可行動指標

| 虛榮（避免） | 可行動（使用） |
|----------------|-----------------|
| 總註冊數 | 啟用率（完成 onboarding 的百分比） |
| 頁面瀏覽數 | 轉換率（採取目標行動的百分比） |
| 下載數 | 留存率（7/30 天後回來的百分比） |
| 總營收 | 每位使用者營收、LTV:CAC |

### 轉向的觸發條件

出現下列情況時，考慮轉向：
- 經過 2-3 個迭代週期後指標持平
- 顧客的回饋一再要求跟你正在做的不一樣的東西
- 單位經濟模型沒有隨規模改善
- 團隊的熱情已經轉移到另一個問題

### 轉向類型

| 轉向 | 改變什麼 |
|-------|-------------|
| 客群 | 同一個產品，不同的目標對象 |
| 問題 | 同一批顧客，不同的問題要解 |
| 解法 | 同一個問題，不同的做法 |
| 通路 | 同一個產品，不同的配銷方式 |
| 營收模式 | 同一個產品，不同的定價/商業模式 |
| 平台 | 單一產品 → 平台（或反過來） |

## 輸出格式

```markdown
# Lean Startup Plan: {Product/Idea}

## Riskiest Assumption
{The one thing that must be true for this to work}

## MVP Design
- Type: {landing page / concierge / etc.}
- What it tests: {specific assumption}
- Build time: {hours/days/weeks}
- Success metric: {specific threshold}

## Build-Measure-Learn Plan
| Cycle | Build | Measure | Learn |
|-------|-------|---------|-------|
| 1 | {MVP} | {metric + threshold} | Validate/Pivot? |
| 2 | {iteration} | {metric} | ... |

## Pivot/Persevere Criteria
- Persevere if: {specific metric threshold met}
- Pivot if: {specific metric threshold not met after N cycles}
```

## 常見陷阱

- **MVP ≠ 爛產品**：Minimum Viable Product 是為了「學習」所需的最小東西，不是你能矇混出貨的最低標準。凡是影響測試結果的地方，品質依然重要。
- **「Build」不一定是寫程式**：登陸頁、試算表、手動服務，任何能測試假設的東西都算。
- **轉向不是失敗**：轉向代表你學到了有價值的東西。真正的失敗是資料都說該轉向了卻不轉。
- **精實創業是為了不確定性**：如果你在已知市場裡做一個大家都很了解的產品，瀑布式可能就夠了。精實創業是用在你不知道該做什麼、或不知道為誰做的時候。

## 參考資料

- 實驗設計範本，見 `references/experiment-templates.md`
