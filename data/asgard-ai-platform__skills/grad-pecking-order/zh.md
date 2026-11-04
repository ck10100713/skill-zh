---
name: "grad-pecking-order"
description: "用啄食順序理論（Myers 和 Majluf，1984）分析資訊不對稱如何驅動融資的層級決策。當使用者需要解釋為什麼公司偏好內部融資勝過外部融資、把發行股票解讀成負面訊號、評估籌資決策，或問到「為什麼增資消息一出股價就跌」「我們該用負債還是股權」「為什麼公司囤現金」時，就用這個 skill。"
metadata:
  category: "WP-26 財務理論"
  tags: ["pecking-order", "information-asymmetry", "Myers-Majluf", "financing-hierarchy", "adverse-selection"]
---

# Pecking Order Theory

## Overview

啄食順序理論（Myers & Majluf，1984）主張，公司遵循嚴格的融資層級，先用內部資金，再用負債，最後才用股權，這由經理人和外部投資人之間的資訊不對稱所驅動。和抵換理論不同，這個理論沒有目標槓桿比率。

## When to Use

- 解釋為什麼公司囤積現金，而不是還給股東
- 解讀市場對融資公告的反應
- 根據資訊環境預測融資選擇
- 分析為什麼高獲利的公司常常槓桿很低

## When NOT to Use

- 公司的資訊不對稱很小（例如透明的受管制公用事業）
- 積極鎖定槓桿比率的公司（抵換理論更適合）
- 稅務考量明顯主導融資選擇

## Assumptions

```
IRON LAW: Firms prefer internal financing first because external
financing signals negative private information. Equity issuance is
the most informationally sensitive — and therefore most costly — source.
```

關鍵假設：
1. 經理人比外部投資人更了解公司價值
2. 經理人依既有股東的利益行事
3. 投資人會理性地折價資訊較充分的內部人所發行的證券
4. 交易成本從內部資金、負債到股權依序增加

## Methodology

### Step 1 — Assess Information Asymmetry

- 公司的業務有多透明？（研發密集 = 高不對稱）
- 管理層溝通的過往紀錄如何？
- 公司的資產要從外部評價有多複雜？

### Step 2 — Identify Available Financing Sources

| Source | Adverse Selection Cost | Pecking Order Rank |
|--------|----------------------|-------------------|
| Retained earnings | 無 | 第 1 順位（首選） |
| Bank debt (secured) | 低 | 第 2 |
| Public debt (bonds) | 中 | 第 3 |
| Convertible debt | 中高 | 第 4 |
| Equity issuance | 最高 | 最後手段 |

### Step 3 — Predict or Explain Financing Choice

- 內部資金足夠：不需要外部融資
- 內部資金不足：先發行最安全的證券（負債先於股權）
- 發行股票：表示管理層認為股價被高估

### Step 4 — Evaluate Market Reaction

- 發行股票的公告：預期股價有負面反應（典型為 -2% 到 -3%）
- 發行負債：反應溫和或中性
- 內部融資：沒有訊號效果

## Output Format

```markdown
## Pecking Order Analysis: [Firm / Decision]

### Information Environment
- Asymmetry level: [High / Medium / Low]
- Key drivers: [R&D intensity, asset complexity, etc.]

### Financing Decision
| Option | Available | Adverse Selection Cost | Chosen? |
|--------|-----------|----------------------|---------|
| Internal funds | [Y/N] | None | [Y/N] |
| Debt | [Y/N] | [Low/Medium] | [Y/N] |
| Equity | [Y/N] | [High] | [Y/N] |

### Signaling Implications
- [Expected market reaction and rationale]

### Assessment
- [Consistent with pecking order? If not, why?]
```

## Gotchas

- 啄食順序預測沒有目標槓桿，槓桿是過去融資需求的累積結果
- 這個理論比較能解釋大型、成熟的公司，新創常常不得不發行股票
- 實證證據不一，有些公司明顯鎖定槓桿比率
- 資訊不對稱會隨時間變化，財報公布後或審計後的時間窗口會降低它
- 無法解釋為什麼有些公司明明有現金還發行股票（帝國建構、擇時）
- 混合型證券（可轉債、特別股）會模糊層級的邊界

## References

- Myers, S. & Majluf, N. (1984). Corporate financing and investment decisions when firms have information that investors do not have. *Journal of Financial Economics*, 13(2), 187-221.
- Myers, S. (1984). The capital structure puzzle. *Journal of Finance*, 39(3), 575-592.
- Frank, M. & Goyal, V. (2003). Testing the pecking order theory of capital structure. *Journal of Financial Economics*, 67(2), 217-248.
