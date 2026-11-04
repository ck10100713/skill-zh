---
name: "soc-cialdini"
description: "運用 Cialdini 的說服六原則（互惠、承諾與一致、社會認同、喜好、權威、稀缺）來分析或設計影響策略。使用者需要讓訊息更有說服力、分析某個活動為什麼有效或無效、設計銷售或行銷文案，或想了解社會影響的手法時使用，就算他們說的是「我們怎麼說服大家」、「這支廣告為什麼有效」或「讓這個更有說服力」也一樣。"
metadata:
  category: "WP-18 社會科學院"
  tags: ["social-science", "persuasion", "cialdini", "influence"]
---

# Cialdini 的說服六原則

## 概述

Robert Cialdini 找出了六項驅動人類順從的通用原則。它們之所以有效，是因為它們是認知捷徑，人們靠它們來快速做決定。了解這些原則，既有助於設計更有說服力的溝通，也有助於認出別人何時正在對你使用它們。

## 框架

```
IRON LAW: Ethical Influence, Not Manipulation

These principles are tools. Using them to help people make decisions aligned
with their interests = ethical influence. Using them to exploit people against
their interests = manipulation. The test: would the person feel grateful or
deceived if they knew the technique was being used?
```

### 六項原則

**1. 互惠（Reciprocity）**：人們會覺得有義務回報人情
- 先給出有價值的東西（免費試用品、有用的內容、個人的幫忙）
- 這份禮物要有意義、出人意料，而且是個人化的
- 應用：免費試用、內容行銷、「引流磁鐵（lead magnet）」

**2. 承諾與一致（Commitment & Consistency）**：人們想讓自己的行為和先前的承諾一致
- 從小的請求開始，再逐步升級（得寸進尺，foot-in-the-door）
- 取得公開或書面的承諾
- 應用：免費註冊 → 付費轉換、忠誠度計畫、設定目標

**3. 社會認同（Social Proof）**：人們會跟著別人做，尤其是跟自己相似的別人
- 展示數字（「10,000 位以上的客戶」）、見證、評價
- 當「別人」跟目標受眾相似時最有效
- 應用：評價、案例研究、「最受歡迎」標籤、候補名單

**4. 喜好（Liking）**：人們會對自己喜歡的人說好
- 相似性（「我們跟你一樣」）、讚美、合作、外貌吸引力
- 透過反覆接觸產生的熟悉感
- 應用：品牌個性、網紅行銷、個人化

**5. 權威（Authority）**：人們會順從有公信力的專家
- 資歷、頭銜、制服、受認可的權威背書
- 必須是相關的權威（醫師為藥品背書，不是醫師為汽車背書）
- 應用：專家背書、認證、「曾被報導於」的標誌

**6. 稀缺（Scarcity）**：人們會看重有限或即將消失的東西
- 限量（「只剩 3 個」）、限時（「優惠今晚結束」）、專屬的取得管道
- 損失框架比獲得框架更強
- 應用：快閃特賣、限量版、搶先體驗計畫

### 分析步驟

1. **找出說服的情境**：誰在說服誰？想要的行動是什麼？
2. **稽核目前的訊息**：哪些原則已經在用？哪些還沒用到？
3. **建議補強**：對這個受眾和情境，哪些原則最有效？
4. **檢查倫理**：每個應用都通過「感激還是被欺騙？」的測試嗎？

## 輸出格式

```markdown
# Persuasion Analysis: {Context}

## Current State
- Persuader: {who}
- Target: {audience}
- Desired action: {what}
- Current conversion/compliance rate: {if known}

## Principle Audit
| Principle | Currently Used? | How | Effectiveness |
|-----------|----------------|-----|---------------|
| Reciprocity | Y/N | {description} | H/M/L |
| Commitment | Y/N | ... | ... |
| Social Proof | Y/N | ... | ... |
| Liking | Y/N | ... | ... |
| Authority | Y/N | ... | ... |
| Scarcity | Y/N | ... | ... |

## Recommendations
1. {Principle}: {specific implementation} — {expected impact}

## Ethics Check
{Does each recommendation pass the "grateful or deceived?" test?}
```

## 範例

### 正確的應用
**情境：** 提升一個台灣 SaaS 登陸頁的轉換率

| 原則 | 現況 | 建議 |
|-----------|---------|---------------|
| 互惠 | ✗ | 在要求註冊之前，先提供一個免費的 ROI 計算機工具 |
| 社會認同 | 偏弱（「受企業信賴」） | 加上具體的 logo + 「2,347 個團隊都在用」+ 附照片和公司名稱的見證 |
| 權威 | ✗ | 加上「資策會推薦」或相關的產業認證 |
| 稀缺 | ✗ | 「早鳥優惠價：NT$299/月（3 月 31 日截止）」 |

全部通過倫理檢查：免費工具確實有用、社會認同是真實的、權威是真正的認證、稀缺是真正的限時優惠 ✓

### 錯誤的應用
- 實際有 200 件庫存，卻寫「只剩 2 件！」→ 假的稀缺。客戶如果知道會覺得**被欺騙**。違反鐵律：只能做合乎倫理的影響。

## 注意事項

- **疊加原則會放大效果**：同時用 3-4 個原則，比任何單一原則都更有效。一個同時有社會認同 + 權威 + 稀缺的登陸頁，會勝過只有社會認同的。
- **文化校準**：權威在階層分明的文化（台灣、日本、韓國）分量更重。社會認同在集體主義文化裡很有力。個人主義文化可能對稀缺和獨特性反應更好。
- **邊際效益遞減**：過度使用稀缺（每封 email 都寫「限時！」）會侵蝕信任。每個原則都要真誠地、節制地使用。
- **B2B vs B2C**：B2B 的決策涉及多位利害關係人。權威和社會認同（案例研究）比稀缺或喜好更有效。
- **原則 7：一體感（Unity）**（Cialdini 在 2016 年新增）：共同的身分認同（「我們是一家人」、「校友」）會產生最強的影響力。在以社群為基礎的情境中可以考慮。

## 參考資料

- 暗黑模式與操弄的偵測請看 `references/dark-patterns.md`
- B2B 專屬的說服手法請看 `references/b2b-persuasion.md`
