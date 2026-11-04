---
name: "meta-structured-problem"
description: "用 MECE 原則、議題樹、假設驅動法和金字塔原理做結構化解題。使用者面對複雜又模糊的問題，需要有系統地拆解、整理成顧問式的分析，或要把建議整理得清楚時使用，就算他們說的是「我要從哪裡開始」、「這個問題太大了」、「幫我拆解一下」或「幫我整理思路」也一樣。"
metadata:
  category: "WP-22 跨學科"
  tags: ["meta-thinking", "structured-problem-solving", "mece", "mckinsey"]
---

# 結構化解題

## 框架

```
IRON LAW: MECE or It's Not Structured

Every decomposition must be MECE:
- Mutually Exclusive: No overlap between categories
- Collectively Exhaustive: No gaps — all possibilities covered

"Revenue = New customers + Existing customers" is MECE ✓
"Revenue = Online + Enterprise + Growth" is NOT MECE ✗ (overlapping)
```

### 核心工具

**議題樹（Issue Tree）**：把一個問題拆成子問題，每一層都要 MECE
```
"Why is profit declining?"
├── Revenue declining?
│   ├── Volume down?
│   │   ├── New customer acquisition down?
│   │   └── Existing customer churn up?
│   └── Price down?
│       ├── Discounting increased?
│       └── Mix shift to lower-priced products?
└── Costs increasing?
    ├── COGS up?
    └── OpEx up?
```

**假設驅動法**：不要什麼都去探索，而是先提出一個假設，然後去驗證它
1. 形成初始假設（「利潤下滑是因為流失率上升」）
2. 找出什麼證據可以證明／推翻它
3. 蒐集那個特定的證據
4. 修正或否定這個假設
5. 重複

**金字塔原理**（Barbara Minto）：由上而下組織溝通內容
1. **先講答案**：從建議開始，不要從分析開始
2. **把支持的論點分組**：3-5 個支持論點，MECE
3. **有邏輯地排序**：依論點強度、時間順序或結構順序
4. **被問了才講細節**：每一層都為想看更多的人提供更多細節

**80/20 法則**：把力氣放在驅動 80% 答案的那 20% 分析上。不要過度分析議題樹上次要的分支。

### 解題流程

1. **定義問題**：「客戶的利潤年減 15%。為什麼？他們該怎麼做？」
2. **用議題樹建立結構**：把可能的原因做 MECE 拆解
3. **排分支的優先順序**：哪些分支最有可能包含答案？（80/20）
4. **形成假設**：「我認為主要的原因是…」
5. **蒐集證據**：用資料測試每個假設
6. **綜合發現**：證據說了什麼？
7. **提出建議**：用金字塔原理呈現（答案先行）

## 輸出格式

```markdown
# Structured Analysis: {Problem}

## Problem Statement
{One sentence, specific and measurable}

## Issue Tree
{MECE decomposition — text or visual}

## Hypothesis
{Initial hypothesis with rationale}

## Evidence
| Branch | Hypothesis | Evidence | Verdict |
|--------|-----------|---------|---------|
| {branch} | {sub-hypothesis} | {data found} | Confirmed/Rejected |

## Synthesis (Pyramid Structure)
**Recommendation**: {answer first}

**Supporting Arguments**:
1. {argument 1 with evidence}
2. {argument 2 with evidence}
3. {argument 3 with evidence}

## Next Steps
1. {action item}
```

## 範例

### 正確的應用
**情境：**「為什麼我們的外送 app 在流失市占率？」

議題樹（MECE）：
```
Market share declining
├── Our growth slowing?
│   ├── New user acquisition down?
│   │   ├── Marketing spend reduced?
│   │   └── Conversion rate dropped?
│   └── Existing user activity down?
│       ├── Order frequency declining?
│       └── Users churning?
└── Competitors growing faster?
    ├── New entrant capturing share?
    └── Existing competitor accelerating?
```

假設：「現有用戶的活躍度下降，是因為外送費調漲後，訂單頻率降低。」
證據：外送費調漲後那個月，訂單頻率下降了 22%。✓

金字塔：「取消對高頻用戶的外送費調漲。調漲後訂單頻率下降 22%，而且流失的訂單有 60% 來自每週訂 3 次以上的用戶。針對高頻用戶推出免外送費的忠誠度層級，預估能用每月 NT$X 的成本，挽回約 15% 流失的市占率。」

### 錯誤的應用
- 議題樹：「營收問題：線上、行銷、客服」→ 不是 MECE（類別重疊，也沒有涵蓋全部）。違反鐵律。

## 注意事項

- **MECE 在實務上很難**：完美的 MECE 是理想。盡量做到接近，並註明哪裡的類別界線模糊。「夠好的 MECE」勝過「完美但花了 3 天」。
- **假設驅動 ≠ 確認偏誤**：假設是用來引導調查的起點，不是要捍衛的結論。如果證據推翻它，就改假設。
- **金字塔原理感覺很反直覺**：人自然會想照時間順序講故事（問題 → 分析 → 結論）。聽眾要的是答案「先」講，再講支持的證據。先講建議。
- **結構化 ≠ 慢**：花 30 分鐘把問題結構化，能省下好幾個小時沒有焦點的分析。結構本身就是速度。
- **知道什麼時候停**：分析有邊際效益遞減。如果你手上的證據已經夠做出有信心的建議，就停止分析、直接建議。

## 參考資料

- 依問題類型分類的議題樹範本請看 `references/issue-tree-templates.md`
- 金字塔原理寫作指南請看 `references/pyramid-principle.md`
