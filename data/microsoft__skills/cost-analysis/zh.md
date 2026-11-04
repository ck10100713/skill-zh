---
name: cost-analysis
description: "分析 Azure 實際支出、帳單變化，以及 AKS 或 AI 的成本。WHEN: \"Azure cost breakdown\", \"most expensive resources\", \"why did my bill increase\", \"cost spike\", \"unexpected charge\", \"Cosmos DB charges\", \"Foundry model costs\", \"AKS cluster cost\", \"namespace cost\", \"enable AKS cost analysis\", \"idle AKS capacity\". DO NOT USE FOR: forecasts, pricing estimates, rightsizing, commitments, or budgets."
license: MIT
metadata:
  author: Microsoft
  version: "1.1.2"
---

# Azure Cost Analysis

## Quick Reference

| Intent | Workflow | Primary tools |
|--------|----------|---------------|
| 查詢歷史支出 | [Cost query](references/cost-query/workflow.md) | `query_costs` |
| 解釋成本暴增 | [Cost investigation](references/cost-investigation.md) | `query_costs`, Resource Graph |
| 分析 AKS 支出 | [AKS cost analysis](references/aks-cost-analysis.md) | `query_aks_costs`, Resource Graph |
| 分析 AI 服務支出 | [AI cost analysis](references/ai-cost-analysis.md) | `query_costs` |

## When to Use This Skill

用在支出、異常，以及 AKS 或 AI 的成本分攤。

## MCP Tools

先用成本工具和 Resource Graph。如果某個操作不能用，照
[fallback and safety](references/tools-and-safety.md) 處理。

## Workflow

1. 確認範圍、期間、幣別和拆分方式。
2. 只載入上面對應的那個 workflow。
3. 絕對不要在 shell 或 interpreter 裡轉換 MCP 的結果；要總計、分組、
   排序或有範圍限制的後續查詢，請在工具那邊做。
4. 遵守資料列上限，資料不完整要標示出來。
5. 把實測成本、推論出來的原因和建議分開講。

## Error Handling

| Error | Action |
|-------|--------|
| Access denied | 說出需要哪個 scope 和角色。 |
| Empty result | 區分「沒有資料」和「資料拿不到」。 |
| Multiple currencies | 每種幣別分開回報。 |
| Server error | 重試一次；還是失敗就停下來，附上 trace ID。 |
