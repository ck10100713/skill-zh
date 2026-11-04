---
name: "grad-is-success"
description: "用 DeLone 和 McLean 的資訊系統成功模型，透過六個相互依賴的面向評估 IS 的效益。當使用者需要評估資訊系統的系統品質、資訊品質或服務品質、診斷使用者為什麼不滿意、衡量系統投資的淨效益，或問到「怎麼衡量 IS 成功」「為什麼使用者對這個系統不滿」「我們的系統有帶來價值嗎」時，就用這個 skill。"
metadata:
  category: "WP-30 資訊管理"
  tags: ["IS-success", "DeLone-McLean", "system-quality", "information-quality", "service-quality", "user-satisfaction", "net-benefits"]
---

# IS Success Model (DeLone & McLean)

## Overview

DeLone 和 McLean 的 IS 成功模型（1992，2003 年更新）找出 IS 成功的六個相互依賴的面向：系統品質（System Quality）、資訊品質（Information Quality）、服務品質（Service Quality）、使用意圖 / 使用（Intention to Use/Use）、使用者滿意度（User Satisfaction）和淨效益（Net Benefits）。這些面向形成一條帶有回饋迴圈的因果鏈，淨效益會強化（或削弱）後續的使用與滿意度。

## When to Use

- 評估資訊系統的整體效益
- 診斷使用者不滿意或系統使用率低的原因
- 為 IS 專案上線後的檢討建立衡量框架
- 跨多個品質面向比較替代系統

## When NOT to Use

- 開發前的需求蒐集（用需求工程方法）
- 部署前預測技術接受度（用 TAM/UTAUT）
- 只衡量個別任務的表現（用 Task-Technology Fit）

## Assumptions

```
IRON LAW: IS success is MULTIDIMENSIONAL — measuring only one dimension
(e.g., usage) gives an incomplete and potentially misleading picture.
```

關鍵假設：
1. 六個面向是相互依賴的，不是獨立的指標
2. 系統品質、資訊品質和服務品質，在因果上先於使用與滿意度
3. 淨效益會回饋，影響未來的使用和使用者滿意度
4. 脈絡決定哪些面向最重要，沒有通用的權重

## Methodology

### Step 1 — Identify the IS and stakeholder groups

指明要評估的資訊系統、它的目的，以及相關的利害關係人群體（終端使用者、主管、IT 人員、客戶）。為每個群體定義「淨效益」是什麼意思。

### Step 2 — Measure quality dimensions

| Dimension | Representative Measures |
|-----------|------------------------|
| System Quality | 可靠度、回應時間、易用性、彈性、安全性 |
| Information Quality | 正確性、完整性、及時性、相關性、一致性 |
| Service Quality | IT 支援的回應性、保證性、同理心（改編自 SERVQUAL） |

### Step 3 — Assess use and satisfaction

衡量實際使用（頻率、時間長度、廣度），或使用意圖（部署前）。用整體滿意度量表和特定功能的滿意度來衡量使用者滿意度。

### Step 4 — Evaluate net benefits and feedback loops

在適當的層級量化淨效益（個人生產力、工作小組效率、組織績效）。追蹤回饋：正向的淨效益應該提高未來的使用和滿意度；負向的效益則是惡化迴圈的訊號。

## Output Format

```markdown
## IS Success Assessment: [System Name]

### Quality Dimensions
| Dimension | Rating (1-7) | Strengths | Weaknesses |
|-----------|-------------|-----------|------------|
| System Quality | | | |
| Information Quality | | | |
| Service Quality | | | |

### Use & Satisfaction
- Usage level: [high/moderate/low] — [evidence]
- User Satisfaction: [score] — [key drivers/detractors]

### Net Benefits
| Stakeholder Group | Benefit Type | Assessment |
|-------------------|-------------|------------|
| | | |

### Feedback Loop Diagnosis
- Virtuous cycle present? [yes/no] — [evidence]
- Deterioration risks: ...

### Recommendations
1. [Target dimension]: [action]
2. ...
```

## Gotchas

- 當系統使用是強制的，使用量就不適合當成功指標，這時滿意度是更好的指標
- 這個模型是分類架構，不是因果理論，它指出該衡量什麼，不提供精確的因果權重
- 服務品質是在 2003 年更新時加入的，使用 1992 年模型的研究會漏掉它
- 淨效益取代了原本的「個人影響」和「組織影響」，要明確定義分析的層級
- 資訊品質和系統品質在實務上高度相關，要做區辨效度檢驗
- 脈絡影響極大，ERP 的評估和消費性 App 的評估，各面向的權重不一樣

## References

- DeLone, W. H., & McLean, E. R. (1992). Information systems success: The quest for the dependent variable. *Information Systems Research*, 3(1), 60-95.
- DeLone, W. H., & McLean, E. R. (2003). The DeLone and McLean model of information systems success: A ten-year update. *Journal of Management Information Systems*, 19(4), 9-30.
- Petter, S., DeLone, W., & McLean, E. (2008). Measuring information systems success: Models, dimensions, measures, and interrelationships. *European Journal of Information Systems*, 17(3), 236-263.
