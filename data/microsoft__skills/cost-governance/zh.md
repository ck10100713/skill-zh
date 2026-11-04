---
name: cost-governance
description: "用 budget、警報、tag 和 policy 限制來管控 Azure 成本。WHEN: \"Azure budget health\", \"configured budget overrun\", \"list Azure budgets\", \"create Azure budget\", \"budget alerts\", \"budget coverage\", \"missing CostCenter tags\", \"allowed VM SKUs\", \"allowed Azure regions\", \"would this SKU be denied\", \"cost guardrails\". DO NOT USE FOR: planning-target forecasts, bill investigations, pricing, rightsizing, or commitments."
license: MIT
metadata:
  author: Microsoft
  version: "1.0.1"
---

# Cost Governance

## Quick Reference

| Intent | Workflow | Primary tools |
|--------|----------|---------------|
| 檢查 budget 狀態 | [Budget health](references/budget-health.md) | `list_budgets`, `forecast_costs`, `query_costs`, `list_alerts` |
| 設定 budget | [Budget setup](references/budget-setup.md) | Cost tools, `create_budget` |
| 檢視 guardrail | [Guardrails](references/guardrails.md) | Resource Graph, `list_budgets` |

## When to Use This Skill

用在 budget、警報、tag 和 policy。

## MCP Tools

budget 用成本工具；guardrail 用 Resource Graph。要寫入的話，
必須先確認 scope、金額、門檻和收件人。Fallback：
[API mappings](references/tool-fallback.md)。

## Workflow

1. 確認 scope，並載入對應的 workflow。
2. 絕對不要在 shell 或 interpreter 裡轉換 MCP 的結果；要過濾或有範圍限制的
   後續查詢，請在工具那邊做。
3. 區分「存取失敗」和「結果是空的」。
4. 回報缺口，但不要暗示 budget 能限制支出。

## Error Handling

| Error | Action |
|-------|--------|
| Access denied | 說出缺少的權限。 |
| No budget or forecast | 回報「資料拿不到」，不要說是零。 |
| Multiple currencies | 絕對不要跨幣別加總或比較。 |
| Write conflict | 保留原本的 budget。 |
| Server error | 重試一次；還是失敗就停下來，附上 trace ID。 |
