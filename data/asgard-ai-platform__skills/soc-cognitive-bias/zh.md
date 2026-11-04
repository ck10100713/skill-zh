---
name: "soc-cognitive-bias"
description: "在決策情境中辨識並分析認知偏誤，包含確認偏誤、錨定、可得性捷思和沉沒成本謬誤。使用者需要稽核某個決策有沒有偏誤、了解團隊為什麼一再犯同樣的錯、設計去偏誤的介入措施，或評估某個結論是根據證據還是認知捷徑時使用，就算他們說的是「我們是不是在自欺欺人」、「為什麼我們一直搞錯這件事」或「這份分析有偏誤嗎」也一樣。"
metadata:
  category: "WP-18 社會科學院"
  tags: ["social-science", "cognitive-bias", "decision-making"]
---

# 認知偏誤分析

## 概述

認知偏誤是對理性判斷的系統性偏離。它們不是隨機的錯誤，而是可預測的模式，會影響每一個人，包括專家。這個 skill 幫你找出特定決策情境中有哪些偏誤在作用，並設計對策。

## 框架

```
IRON LAW: Name the Specific Bias, Not Just "Bias"

"This decision might be biased" is not analysis. Identify the SPECIFIC
bias by name, explain its mechanism, and show how it applies to this
particular situation. Different biases require different countermeasures.
```

### 偏誤稽核流程

1. **描述決策**：要決定的是什麼？由誰決定？根據什麼證據？
2. **用名稱找出可能的偏誤**：哪些特定的偏誤（確認偏誤、錨定、沉沒成本、團體迷思、過度自信、可得性等）可能正在影響這個決策？
3. **找證據**：哪些具體的行為或推理模式顯示了這個偏誤？
4. **評估影響**：這個偏誤對決策品質的影響有多大？（高／中／低）
5. **設計對策**：每個找出來的偏誤，要用哪個具體的去偏誤技巧來處理？

完整的偏誤目錄（12 種偏誤 × 機制 × 範例）以及每種偏誤的去偏誤技巧，請看 [`references/debiasing-protocols.md`](references/debiasing-protocols.md)。

## 輸出格式

```markdown
# Cognitive Bias Audit: {Decision Context}

## Decision Under Review
- Decision: {what is being decided}
- Decision-makers: {who}
- Current leaning: {which way they're leaning}

## Biases Identified
| Bias | Evidence | Impact | Countermeasure |
|------|----------|--------|---------------|
| {name} | {specific behavior/reasoning} | H/M/L | {debiasing technique} |

## Debiased Recommendation
{What the decision looks like after accounting for identified biases}
```

## 範例

### 正確的應用
**情境：** 公司在決定要不要繼續一個失敗的產品上市（已經 6 個月、花了 NT$5M）

| 偏誤 | 證據 | 影響 |
|------|----------|--------|
| **沉沒成本** | 「我們已經投資了 NT$5M，現在不能停」 | 高：過去的花費拿不回來，而且跟往後的決策無關 |
| **過度自信** | 「我們修正後的預測顯示 Q3 會翻轉」，但先前 3 次的預測也都錯了 | 中：團隊系統性地高估成功機率 |
| **確認偏誤** | 團隊只引用那 2 則正面的客戶評價，卻忽略 50 則負面的 | 高：選擇性地過濾資訊 |

**去偏誤的問題**：「如果有個競爭對手免費把這條產品線送給我們，我們會接嗎？」如果答案是不會，不管沉沒成本多少，這個產品都應該停掉 ✓

### 錯誤的應用
- 只說「團隊有偏誤」，卻沒說是哪一種偏誤 → 沒辦法行動。違反鐵律：要指名特定的偏誤。

## 注意事項

- **每個人都有偏誤，包括你**：做偏誤稽核的分析者自己也有偏誤。要用結構化的流程（檢查表、紅隊），不要只靠自我覺察。
- **辨識偏誤 ≠ 消除偏誤**：知道某個偏誤會減弱它的影響，但不會消除。去偏誤需要結構性的介入（流程、誘因），不只是意識到。
- **動機性推理看起來像分析**：當有人心裡有想要的結果，就會不自覺地為它建構聽起來合邏輯的論點。要檢查：結論是在分析之前還是之後出現的？
- **虛假的平衡**：不是每個決策都有偏誤。有時候團隊的傾向是對的。不要在沒有偏誤的地方硬套偏誤。
- **文化脈絡**：有些偏誤在不同文化中的表現不同。權威偏誤在階層分明的文化中更強。團體迷思在集體主義與個人主義的環境中表現也不一樣。

## 參考資料

- 偏誤在行為經濟學上的應用請看 econ-behavioral skill
- 團體決策的去偏誤流程請看 `references/debiasing-protocols.md`
