---
name: "ops-contract-review"
description: "審閱商業合約並找出風險，包含責任條款、智慧財產權歸屬、終止條款和付款條件。使用者需要針對供應商協議、合作合約或服務協議做務實的合約風險評估時使用，就算他們說的是「幫我看這份合約」、「我要注意什麼」、「這份協議公平嗎」或「談到更好的條件」也一樣。"
metadata:
  category: "WP-10 通用商業"
  tags: ["business", "contract", "legal", "risk-management"]
---

# 商業合約審閱

## 框架

```
IRON LAW: Read the Entire Contract, Not Just the Commercial Terms

Price and scope are negotiated carefully. Liability, indemnification,
termination, and IP ownership are often accepted on autopilot.
These "back-of-contract" clauses are where the real risk lives.

A great price with unlimited liability is a terrible deal.
```

### 合約審閱檢查表（商業角度）

**1. 當事人與授權**
- 法律主體名稱正確（不是你本來沒打算簽約的子公司）
- 簽署人有權代表該組織簽約

**2. 範圍與交付物**
- 定義清楚：包含什麼「以及」排除什麼
- 驗收標準：怎麼判斷交付是否令人滿意？
- 變更單流程：範圍變更怎麼處理、怎麼計價？

**3. 付款條款**
- 付款時程：里程碑、每月、交付時
- 付款條件：月結 30 天、月結 60 天、收到即付
- 延遲付款的後果
- 幣別與匯率風險（國際合約）

**4. 期限與終止**
- 合約期間：固定期限 vs 自動續約
- 無因終止：任一方可以退出嗎？要提前多久通知？
- 有因終止：什麼構成違約？
- 收尾義務：終止後會怎樣？資料返還？過渡協助？

**5. 責任與賠償**
- 責任上限：有沒有？金額多少？（理想上 = 合約金額）
- 賠償（Indemnification）：誰賠誰？為了什麼？是雙向還是單向？
- 排除項目：間接損害、利潤損失，有被排除嗎？
- 保險要求：任一方需要投保嗎？

**6. 智慧財產權**
- 合約期間產出的工作成果歸誰？
- 既有的智財：仍屬於原所有人（確認有寫明）
- 授權：各方可以使用對方智財的哪些權利？

**7. 保密**
- 機密資訊的定義（不要太廣，也不要太窄）
- 期間：終止後多久？
- 例外：公開資訊、獨立開發、依法被迫揭露

**8. 爭議解決**
- 準據法：哪個司法管轄區？
- 仲裁 vs 訴訟：仲裁比較快而且不公開，小額請求用訴訟比較便宜
- 管轄地：爭議在哪裡審理？

### 風險評等

| 風險等級 | 特徵 | 行動 |
|-----------|----------------|--------|
| 🟢 低 | 市場標準條款、義務平衡 | 簽 |
| 🟡 中 | 有些單方面的條款，風險可控 | 針對特定條款協商 |
| 🔴 高 | 無限責任、無法退出、智財單方面歸對方 | 沒有大幅修改就不要簽 |

## 輸出格式

```markdown
# Contract Review: {Agreement Type} with {Counterparty}

## Overview
- Type: {service/vendor/partnership/license}
- Value: {$X}
- Term: {duration}

## Risk Assessment
| Area | Risk | Issue | Recommendation |
|------|------|-------|---------------|
| Scope | 🟢/🟡/🔴 | {finding} | {action} |
| Payment | 🟢/🟡/🔴 | {finding} | {action} |
| Termination | 🟢/🟡/🔴 | {finding} | {action} |
| Liability | 🟢/🟡/🔴 | {finding} | {action} |
| IP | 🟢/🟡/🔴 | {finding} | {action} |
| Confidentiality | 🟢/🟡/🔴 | {finding} | {action} |

## Red Flags
1. {specific clause + why it's risky}

## Negotiation Priorities
1. {most important change to request}
2. {second priority}
3. {third priority}

## Overall Risk: 🟢/🟡/🔴
{Summary recommendation: sign / negotiate / reject}
```

## 注意事項

- **自動續約卻沒有通知期限**：很多合約會自動續約，除非你提前 30-90 天通知。簽約當下就要把通知期限排進行事曆。
- **「標準」合約並不中立**：起草人的「標準」範本是在保護起草人。每一項都可以談。
- **口頭協議有風險**：「他們說他們會處理那個」，如果沒寫進合約就毫無意義。重要的事就必須寫下來。
- **不可抗力的範圍**：COVID 之後，要檢查包含了什麼。疫情？供應鏈中斷？政府命令？太窄就是需要的時候沒有保護。
- **這是商業審閱，不是法律建議**：財務或法律風險重大的合約，最終版本要請有執照的律師審閱。

## 參考資料

- 契約法基礎請看 law-contract skill
- 談判技巧請看 ops-negotiation skill
