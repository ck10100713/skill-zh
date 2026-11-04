---
name: cost-estimation
description: "預測 Azure 支出，並為規劃中的資源或工作負載估價。WHEN: \"forecast Azure spending\", \"project next month cost\", \"compare forecast to my planning target\", \"how much will Azure cost\", \"estimate VM cost\", \"compare storage tiers\", \"compare Azure regions\", \"retail price\", \"EA rate card\", \"negotiated pricesheet\". DO NOT USE FOR: configured budget health or alerts, bill analysis, cost spikes, rightsizing, or commitments."
license: MIT
metadata:
  author: Microsoft
  version: "1.1.1"
---

# Azure Cost Estimation

## Quick Reference

| Intent | Workflow | Primary tools |
|--------|----------|---------------|
| 預測現有支出 | [Cost forecast](references/cost-forecast/workflow.md) | `forecast_costs` |
| 為規劃中的資源估價 | [Pricing estimate](references/pricing-estimate.md) | Pricing tools |

## When to Use This Skill

用在預測、估價和規劃目標。

## MCP Tools

| Tool | Use |
|------|-----|
| `forecast_costs` | 預測某個 scope 的成本。 |
| `get_retail_prices` | 取得公開價格。 |
| `start_pricesheet_download`, `get_pricesheet_status` | 取得 Enterprise Agreement (EA) 或 Microsoft Customer Agreement (MCA) 的價格。 |

Fallback: [API mappings](references/tool-fallback.md)。

## Workflow

1. 區分「預測」和「假設性的估價」。
2. 確認 scope、假設、期間、region、OS 和幣別。
3. 載入對應的 workflow，並標明每個數值的類型。
4. 絕對不要在 shell 或 interpreter 裡轉換 MCP 的結果；要過濾或有範圍限制的
   後續查詢，請在工具那邊做。

## Error Handling

| Error | Action |
|-------|--------|
| Ambiguous meter | 詢問 OS、期限、tier 或用量。 |
| Forecast unavailable | 說明需要多少歷史資料。 |
| Pricesheet pending | 遵守回傳的 polling 間隔。 |
| Multiple currencies | 絕對不要把不同幣別加總。 |
| Server error | 重試一次；還是失敗就回報 trace ID。 |
