---
name: cost-optimization
description: "最佳化現有的 Azure 資源，並分析 Reservation 或 Savings Plan。WHEN: \"optimize Azure costs\", \"reduce cloud spending\", \"rightsize resources\", \"find idle resources\", \"orphaned disk\", \"deleted VM still charged\", \"public IP still charging\", \"reservation utilization\", \"Savings Plan coverage\", \"commitment recommendation\", \"why is pay-as-you-go still charged\". DO NOT USE FOR: cost spikes, forecasts, pricing estimates, budgets, or governance."
license: MIT
metadata:
  author: Microsoft
  version: "1.0.2"
---

# Azure Cost Optimization

## Quick Reference

| Intent | Workflow | Primary tools |
|--------|----------|---------------|
| 減少浪費或 rightsize | [Optimization](references/optimization.md) | Cost and Resource Graph tools |
| 檢視 commitment | [Commitments](references/commitments.md) | `list_benefit_utilization`, `list_reservation_transactions`, `get_benefit_recommendations` |

## When to Use This Skill

用在浪費、rightsizing 和 commitment。

## MCP Tools

最佳化用成本工具和 Resource Graph 工具，commitment 用 benefit 工具。
查詢要先驗證。Fallback：[API mappings](references/tool-fallback.md)。

## Workflow

1. 確認 scope、期間、幣別和 commitment 的意圖。
2. 只載入上面對應的那個 workflow。
3. 絕對不要在 shell 或 interpreter 裡轉換 MCP 的結果；要經過驗證的
   伺服器端投影、聚合或有範圍限制的後續查詢，請在工具那邊做。
4. 把實測成本、回報的節省金額和定性的改善機會分開講。
5. 只提出建議；不要刪除、調整大小、購買或部署任何資源。

## Error Handling

| Error | Action |
|-------|--------|
| Access denied | 說出 scope 和權限。 |
| Multiple currencies | 依幣別分組，每種幣別分開回報。 |
| Missing evidence | 說明缺口；不要編造數值。 |
| Server error | 重試一次；還是失敗就回報 trace ID。 |
