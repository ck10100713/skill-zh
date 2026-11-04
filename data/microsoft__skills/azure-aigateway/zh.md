---
name: azure-aigateway
description: "把 Azure API Management 設定成 AI Gateway，用來管理 AI 模型、MCP tools 和 agent。WHEN: semantic caching, token limit, content safety, load balancing, AI model governance, MCP rate limiting, jailbreak detection, add Azure OpenAI backend, add AI Foundry model, test AI gateway, LLM policies, configure AI backend, token metrics, AI cost control, convert API to MCP, import OpenAPI to gateway."
license: MIT
metadata:
  author: Microsoft
  version: "3.2.1"
compatibility: Requires Azure CLI (az) for configuration and testing
---

# Azure AI Gateway

把 Azure API Management（APIM）設定成 AI Gateway，用來管理 AI 模型、MCP tools 和 agent。

> **要部署 APIM**，請用 **azure-prepare** skill。見 [APIM deployment guide](https://learn.microsoft.com/azure/api-management/get-started-create-service-instance)。

## When to Use This Skill

| Category | Triggers |
|----------|----------|
| **Model Governance** | "semantic caching", "token limits", "load balance AI", "track token usage" |
| **Tool Governance** | "rate limit MCP", "protect my tools", "configure my tool", "convert API to MCP" |
| **Agent Governance** | "content safety", "jailbreak detection", "filter harmful content" |
| **Configuration** | "add Azure OpenAI backend", "configure my model", "add AI Foundry model" |
| **Testing** | "test AI gateway", "call OpenAI through gateway" |

---

## Quick Reference

| Policy | Purpose | Details |
|--------|---------|---------|
| `azure-openai-token-limit` | 成本控制 | [Model Policies](references/policies.md#token-rate-limiting) |
| `azure-openai-semantic-cache-lookup/store` | 省下 60-80% 成本 | [Model Policies](references/policies.md#semantic-caching) |
| `azure-openai-emit-token-metric` | 可觀測性 | [Model Policies](references/policies.md#token-metrics) |
| `llm-content-safety` | 安全與合規 | [Agent Policies](references/policies.md#content-safety) |
| `rate-limit-by-key` | 保護 MCP/tool | [Tool Policies](references/policies.md#request-rate-limiting) |

---

## Get Gateway Details

```bash
# 取得 gateway URL
az apim show --name <apim-name> --resource-group <rg> --query "gatewayUrl" -o tsv

# 列出 backend（AI 模型）
az apim backend list --service-name <apim-name> --resource-group <rg> \
  --query "[].{id:name, url:url}" -o table

# 取得 subscription key
az apim subscription keys list \
  --service-name <apim-name> --resource-group <rg> --subscription-id <sub-id>
```

---

## Test AI Endpoint

```bash
GATEWAY_URL=$(az apim show --name <apim-name> --resource-group <rg> --query "gatewayUrl" -o tsv)

curl -X POST "${GATEWAY_URL}/openai/deployments/<deployment>/chat/completions?api-version=2024-02-01" \
  -H "Content-Type: application/json" \
  -H "Ocp-Apim-Subscription-Key: <key>" \
  -d '{"messages": [{"role": "user", "content": "Hello"}], "max_tokens": 100}'
```

---

## Common Tasks

### Add AI Backend

完整步驟見 [references/patterns.md](references/patterns.md#pattern-1-add-ai-model-backend)。

```bash
# 找出 AI 資源
az cognitiveservices account list --query "[?kind=='OpenAI']" -o table

# 建立 backend
az apim backend create --service-name <apim> --resource-group <rg> \
  --backend-id openai-backend --protocol http --url "https://<aoai>.openai.azure.com/openai"

# 授予存取權（managed identity）
az role assignment create --assignee <apim-principal-id> \
  --role "Cognitive Services User" --scope <aoai-resource-id>
```

### Apply AI Governance Policy

`<inbound>` 裡建議的 policy 順序：

1. **Authentication** - 用 managed identity 連 backend
2. **Semantic Cache Lookup** - 呼叫 AI 之前先查 cache
3. **Token Limits** - 成本控制
4. **Content Safety** - 過濾有害內容
5. **Backend Selection** - 負載平衡
6. **Metrics** - 追蹤 token 用量

完整範例見 [references/policies.md](references/policies.md#combining-policies)。

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Token limit 429 | 調高 `tokens-per-minute` 或加上負載平衡 |
| 沒有 cache 命中 | 把 `score-threshold` 降到 0.7 |
| 內容誤判 | 調高各類別的門檻值（5-6） |
| Backend 驗證 401 | 給 APIM 授予 "Cognitive Services User" 角色 |

詳細內容見 [references/troubleshooting.md](references/troubleshooting.md)。

---

## References

- [**Detailed Policies**](references/policies.md) - 完整的 policy 範例
- [**Configuration Patterns**](references/patterns.md) - 一步一步的設定模式
- [**Troubleshooting**](references/troubleshooting.md) - 常見問題
- [AI-Gateway Samples](https://github.com/Azure-Samples/AI-Gateway)
- [GenAI Gateway Docs](https://learn.microsoft.com/azure/api-management/genai-gateway-capabilities)

## SDK Quick References

- **Content Safety**: [Python](references/sdk/azure-ai-contentsafety-py.md) | [TypeScript](references/sdk/azure-ai-contentsafety-ts.md)
- **API Management**: [Python](references/sdk/azure-mgmt-apimanagement-py.md) | [.NET](references/sdk/azure-mgmt-apimanagement-dotnet.md)
