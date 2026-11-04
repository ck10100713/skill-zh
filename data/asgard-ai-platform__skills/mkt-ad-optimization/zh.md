---
name: "mkt-ad-optimization"
description: "最佳化 Google Ads、Meta Ads 和 LINE LAP 上的數位廣告活動，包含出價策略、受眾鎖定、素材測試和 ROAS 最佳化。使用者需要改善廣告成效、降低 CPA、選擇出價策略，或在各平台之間分配預算時使用，就算他們說的是「我們的廣告沒效果」、「降低我們的單次獲客成本」、「Google 廣告還是 Facebook 廣告」或「提高我們的 ROAS」也一樣。"
metadata:
  category: "WP-09 數位行銷"
  tags: ["digital-marketing", "advertising", "google-ads", "meta-ads"]
---

# 數位廣告最佳化

## 框架

```
IRON LAW: Optimize for the Business Metric, Not the Ad Metric

High CTR with low conversion = wasted clicks (attracting curiosity, not buyers).
Low CPC with no sales = cheap traffic that doesn't convert.

The only metrics that matter: CPA (Cost Per Acquisition), ROAS (Return On Ad Spend),
and ultimately: profit per ad dollar. Optimize the funnel, not the ad.
```

### 平台比較

| 平台 | 最適合 | 受眾 | 平均 CPC（台灣） | 鎖定能力 |
|----------|---------|---------|-----------------|-------------------|
| **Google 搜尋** | 高意圖的查詢、直接回應 | 主動搜尋的人 | NT$5-30 | 關鍵字意圖（最強） |
| **Google 多媒體廣告聯播網** | 知名度、再行銷、廣泛觸及 | 被動瀏覽 | NT$1-5 | 情境、受眾 |
| **Meta（FB/IG）** | 社群探索、視覺型產品、相似受眾 | 社群用戶 | NT$3-15 | 興趣、行為、相似受眾 |
| **LINE LAP** | 台灣專屬、廣泛觸及 | LINE 用戶（台灣 95%） | NT$3-20 | 人口統計、興趣 |
| **YouTube** | 影片品牌建立、考慮階段 | 影片觀看者 | NT$1-5（CPV） | 意圖、興趣相似、有購買意向 |
| **TikTok** | Z 世代、爆款產品、短影音 | 年輕族群 | NT$2-10 | 興趣、行為 |

### 出價策略

| 策略 | 運作方式 | 何時使用 |
|----------|-------------|------------|
| **手動 CPC** | 你自己設定最高 CPC | 學習期、小預算、要完全掌控 |
| **目標 CPA** | 演算法針對目標單次獲客成本做最佳化 | 每月 30 次以上轉換、有已知的 CPA 目標 |
| **目標 ROAS** | 演算法針對目標廣告投資報酬率做最佳化 | 電商、已知每次轉換的營收 |
| **最大化轉換** | 花完全部預算取得最多轉換 | 成長期、比較不在意 CPA |
| **最大化點擊** | 用預算換最多的點擊 | 流量活動、知名度 |

### 最佳化工作流程

**Phase 1：稽核目前的成效**
- 依活動、廣告群組、關鍵字／受眾看 CPA
- 品質分數（Google）或相關性分數（Meta）
- 依登陸頁看轉換率
- 浪費的支出：有點擊但沒有轉換的搜尋字詞

**Phase 2：速贏（第 1-2 週）**
- 加入否定關鍵字（Google 搜尋）
- 暫停表現不佳的廣告群組／受眾
- 降低高 CPA 關鍵字的出價
- 修正登陸頁不一致的問題（廣告的承諾 ≠ 登陸頁的內容）

**Phase 3：結構性改善（第 3-4 週）**
- 受眾分群：把冷、溫、熱受眾分開
- 素材更新：新的廣告文案／圖片（2-4 週後就會出現疲乏）
- 登陸頁最佳化：速度、行動版、清楚的 CTA

**Phase 4：擴大規模（第 2 個月起）**
- 對表現好的活動增加預算（漸進式，每週 +20%）
- 擴展到新的受眾（相似受眾、新的興趣）
- 測試新的平台
- 建立再行銷漏斗：知名度 → 考慮 → 轉換

### 素材測試（A/B）

| 元素 | 該測什麼 | 最少樣本 |
|---------|-------------|---------------|
| 標題 | 效益 vs 功能、問句 vs 陳述句 | 各 1,000 次曝光 |
| 圖片／影片 | 產品照 vs 生活風格、靜態 vs 影片 | 各 1,000 次曝光 |
| CTA | 「立即購買」vs「了解更多」vs「領取優惠」 | 各 500 次點擊 |
| 優惠 | 免運費 vs 折扣 % vs 贈品 | 各 100 次轉換 |

## 輸出格式

```markdown
# Ad Optimization Report: {Campaign/Account}

## Performance Summary
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Spend | NT${X}/month | — | — |
| CPA | NT${X} | NT${X} | 🟢/🟡/🔴 |
| ROAS | {X}x | {X}x | 🟢/🟡/🔴 |
| CVR | {%} | {%} | 🟢/🟡/🔴 |

## Top Performing
| Campaign/Ad | CPA | ROAS | Action |
|------------|-----|------|--------|
| {name} | NT${X} | {X}x | Scale +20% |

## Underperforming
| Campaign/Ad | CPA | Issue | Action |
|------------|-----|-------|--------|
| {name} | NT${X} | {diagnosis} | Pause/Optimize/Restructure |

## Optimization Plan
| Priority | Action | Expected Impact | Timeline |
|----------|--------|----------------|----------|
| 1 | {action} | CPA -{X%} | {weeks} |
```

## 注意事項

- **學習期需要耐心**：Google/Meta 的演算法每個廣告群組每週需要 50 次以上的轉換才能最佳化。太頻繁重組結構會讓學習重來。
- **歸因不完美**：Google 把功勞算給 Google，Meta 把功勞算給 Meta。跨平台歸因要用 UTM 參數和中立的分析工具（GA4）。
- **素材疲乏是真的**：就算是表現最好的廣告，同一批受眾一再看到，2-4 週後也會衰退。要定期更新素材。
- **台灣廣告市場的特殊性**：LINE LAP 能觸及 Facebook 正在流失的族群（年紀較大的用戶）。Google 在搜尋意圖上占主導。要依你的受眾混搭平台。
- **iOS 隱私（ATT）**：自 iOS 14.5 起，Meta 的追蹤受到限制。預期 iOS 用戶的報表會比較不準。要使用 Conversion API 和以模型為基礎的歸因。

## 參考資料

- Google Ads 帳戶結構的最佳實務請看 `references/google-ads-structure.md`
- Meta Ads 素材指南請看 `references/meta-creative.md`
