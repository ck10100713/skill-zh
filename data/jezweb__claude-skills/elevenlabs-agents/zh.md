---
name: elevenlabs-agents
description: "在 ElevenLabs 平台上建構對話式 AI 語音 agent。設定 agent + 工具 + 知識庫、整合 SDK（React / React Native / Swift / JS / 伺服器端）、測試、部署。只要使用者提到 ElevenLabs、建構語音 agent、AI 電話系統、AI 櫃台接待、對話式 AI，或排查已棄用的 @11labs 套件、webhook 錯誤、CSP 違規、localhost allowlist 或工具解析錯誤，就使用。"
compatibility: claude-code-only
---

# ElevenLabs Agent Builder

建構可上線的對話式 AI 語音 agent。產出一個設定好工具、知識庫和 SDK 整合的 agent。

## 套件

```bash
npm install @elevenlabs/react           # React SDK
npm install @elevenlabs/client          # JavaScript SDK (browser + server)
npm install @elevenlabs/react-native    # React Native SDK
npm install @elevenlabs/elevenlabs-js   # Full API (server only)
npm install -g @elevenlabs/agents-cli   # CLI ("Agents as Code")
```

**已棄用：**`@11labs/react`、`@11labs/client`，如果有裝就解除安裝。

**僅限伺服器端的警告：**`@elevenlabs/elevenlabs-js` 用到 Node.js 的 `child_process`，在瀏覽器裡無法運作。瀏覽器環境用 `@elevenlabs/client`，或自己架一台 proxy 伺服器。

## 工作流程

### Step 1：透過 Dashboard 或 CLI 建立 Agent

**Dashboard：** https://elevenlabs.io/app/conversational-ai -> Create Agent

**CLI（Agents as Code）：**
```bash
elevenlabs agents init
elevenlabs agents add "Support Bot" --template customer-service
# Edit agent_configs/support-bot.json
elevenlabs agents push --env dev
```

範本：`default`、`minimal`、`voice-only`、`text-only`、`customer-service`、`assistant`。

設定項目：
- **聲音**：從 5000 多種聲音中選，或複製聲音
- **LLM**：GPT、Claude、Gemini 或自訂
- **System prompt**：使用下面的 6 要素框架
- **第一句話**：對話開始時 agent 說的話

### Step 2：寫 System Prompt

用 6 要素框架寫出有效的 agent prompt：

**1. Personality**：agent 是誰：
```
You are [NAME], a [ROLE] at [COMPANY].
You have [EXPERIENCE]. Your traits: [LIST TRAITS].
```

**2. Environment**：溝通的脈絡：
```
You're communicating via [phone/chat/video].
Consider [environmental factors]. Adapt to [context].
```

**3. Tone**：說話模式和正式程度：
```
Tone: Professional yet warm. Use contractions for natural speech.
Avoid jargon. Keep responses to 2-3 sentences. Ask one question at a time.
```

**4. Goal**：目標和成功標準：
```
Primary Goal: Resolve customer issues on the first call.
Success: Customer verbally confirms issue is resolved.
```

**5. Guardrails**：界線和倫理：
```
Never: provide medical/legal/financial advice, share confidential info.
Always: verify identity before account access, document interactions.
Escalation: customer requests manager, issue beyond knowledge base.
```

**6. Tools**：可用的函式，以及什麼時候用：
```
1. lookup_order(order_id) -- Use when customer mentions an order.
2. transfer_to_supervisor() -- Use when issue requires manager approval.
Always explain what you're doing before calling a tool.
```

### Step 3：加入工具

**用戶端工具（在瀏覽器執行）：**

```typescript
const clientTools = {
  updateCart: {
    description: "Add or remove items from the shopping cart",
    parameters: z.object({
      action: z.enum(['add', 'remove']),
      item: z.string(),
      quantity: z.number().min(1)
    }),
    handler: async ({ action, item, quantity }) => {
      const cart = getCart();
      action === 'add' ? cart.add(item, quantity) : cart.remove(item, quantity);
      return { success: true, total: cart.total, items: cart.items.length };
    }
  },
  navigate: {
    description: "Navigate user to a different page",
    parameters: z.object({ url: z.string().url() }),
    handler: async ({ url }) => { window.location.href = url; return { success: true }; }
  }
};
```

**伺服器端工具（webhook）：**

```json
{
  "name": "get_weather",
  "description": "Fetch current weather for a city",
  "url": "https://api.weather.com/v1/current",
  "method": "GET",
  "parameters": {
    "type": "object",
    "properties": {
      "city": { "type": "string", "description": "City name" }
    },
    "required": ["city"]
  },
  "headers": {
    "Authorization": "Bearer {{secret__weather_api_key}}"
  }
}
```

webhook header 裡的 API key 用 `{{secret__key_name}}`，絕對不要寫死。

**MCP 工具：關鍵的相容性注意事項：**

ElevenLabs 把它的 MCP 整合標示為「Streamable HTTP」，但**不支援**真正的 MCP 2025-03-26 Streamable HTTP 規格（SSE 回應）。ElevenLabs 要的是：

- 純 JSON 回應（`application/json`），不是 SSE（`text/event-stream`）
- 協定版本 `2024-11-05`，不是 `2025-03-26`
- 透過 HTTP 傳送的簡單 JSON-RPC，直接回傳 JSON

**不能用**的東西：
- 官方 MCP SDK 的 `createMcpHandler`（回傳 SSE）
- Cloudflare Agents SDK 的 `McpServer.serve()`（回傳 SSE）
- 任何回傳 `Content-Type: text/event-stream` 的伺服器

適用於 ElevenLabs 的 MCP 伺服器寫法：

```typescript
import { Hono } from 'hono';
import { cors } from 'hono/cors';

const tools = [{
  name: "my_tool",
  description: "Tool description",
  inputSchema: {
    type: "object",
    properties: { param1: { type: "string", description: "Description" } },
    required: ["param1"]
  }
}];

async function handleMCPRequest(request, env) {
  const { id, method, params } = request;
  switch (method) {
    case 'initialize':
      return {
        jsonrpc: '2.0', id,
        result: {
          protocolVersion: '2024-11-05',  // MUST be 2024-11-05
          serverInfo: { name: 'my-mcp', version: '1.0.0' },
          capabilities: { tools: {} }
        }
      };
    case 'tools/list':
      return { jsonrpc: '2.0', id, result: { tools } };
    case 'tools/call':
      const result = await handleTool(params.name, params.arguments, env);
      return { jsonrpc: '2.0', id, result };
    default:
      return { jsonrpc: '2.0', id, error: { code: -32601, message: `Unknown: ${method}` } };
  }
}

const app = new Hono();
app.use('/*', cors({ origin: '*', allowMethods: ['GET', 'POST', 'OPTIONS'] }));
app.post('/mcp', async (c) => {
  const body = await c.req.json();
  return c.json(await handleMCPRequest(body, c.env));  // Plain JSON, NOT SSE
});
export default app;
```

### Step 4：加入知識庫（RAG）

上傳讓 agent 參考的文件：
- PDF、文字檔、網頁 URL
- 透過 dashboard 設定：Agent -> Knowledge Base -> Upload
- 或透過 API：`POST /v1/convai/knowledge-base/upload`（multipart/form-data）
- Agent 在對話中會自動搜尋知識庫

### Step 5：整合 SDK

**React**：複製並客製化 `assets/react-sdk-boilerplate.tsx`：

```typescript
import { useConversation } from '@elevenlabs/react';

const { startConversation, stopConversation, status } = useConversation({
  agentId: 'your-agent-id',
  signedUrl: '/api/elevenlabs/auth',
  clientTools,
  dynamicVariables: {
    user_name: 'John',
    account_type: 'premium',
  },
  onEvent: (event) => { /* transcript, agent_response, tool_call */ },
});
```

System prompt 用 `{{user_name}}` 的形式參照動態變數。

**React Native**：見 `assets/react-native-boilerplate.tsx`
**嵌入 widget**：見 `assets/widget-embed-template.html`
**Swift**：見 `assets/swift-sdk-boilerplate.swift`

### Step 6：測試

**CLI 測試：**

```bash
# Run all tests for an agent
elevenlabs agents test "Support Agent"

# Add a test scenario
elevenlabs tests add "Refund Request" --template basic-llm
```

**測試設定：**

```json
{
  "name": "Refund Request Test",
  "scenario": "Customer requests refund for defective product",
  "user_input": "I want a refund for order #12345. The product arrived broken.",
  "success_criteria": [
    "Agent acknowledges the issue empathetically",
    "Agent asks for or uses provided order number",
    "Agent verifies order details",
    "Agent provides clear next steps or refund timeline"
  ],
  "evaluation_type": "llm"
}
```

**工具呼叫測試：**

```json
{
  "name": "Order Lookup Test",
  "scenario": "Customer asks about order status",
  "user_input": "What's the status of order ORD-12345?",
  "expected_tool_call": {
    "tool_name": "lookup_order",
    "parameters": { "order_id": "ORD-12345" }
  }
}
```

**API 模擬：**

```typescript
const simulation = await client.agents.simulate({
  agent_id: 'agent_123',
  scenario: 'Customer requests refund',
  user_messages: [
    "I want a refund for order #12345",
    "It arrived broken",
    "Yes, process the refund"
  ],
  success_criteria: [
    "Agent shows empathy",
    "Agent verifies order",
    "Agent provides timeline"
  ]
});
console.log('Passed:', simulation.passed);
```

**CI/CD 整合：**

```yaml
name: Test Agent
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install -g @elevenlabs/cli
      - run: elevenlabs tests push
        env:
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
      - run: elevenlabs agents test "Support Agent"
        env:
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
```

### Step 7：部署

```bash
# Dry run first (always)
elevenlabs agents push --env prod --dry-run

# Deploy to production
elevenlabs agents push --env prod
```

多環境的工作流程：
```bash
elevenlabs agents push --env dev       # Development
elevenlabs agents push --env staging   # Staging
elevenlabs agents test "Agent Name"    # Test in staging
elevenlabs agents push --env prod      # Production
```

---

## 關鍵寫法

### Signed URL（安全性）

絕對不要在用戶端程式碼裡暴露 API key。用一個伺服器端點：

```typescript
app.get('/api/elevenlabs/auth', async (req, res) => {
  const response = await fetch(
    'https://api.elevenlabs.io/v1/convai/conversation/get-signed-url',
    {
      headers: { 'xi-api-key': process.env.ELEVENLABS_API_KEY },
      body: JSON.stringify({ agent_id: 'your-agent-id' }),
      method: 'POST'
    }
  );
  const { signed_url } = await response.json();
  res.json({ signed_url });
});
```

### Agent 版本管理（A/B 測試）

Dashboard：Agent -> Versions -> Create Branch。比較指標，讓勝出的版本上線。

### 通話後 Webhook

```json
{
  "type": "post_call_transcription",
  "data": {
    "conversation_id": "conv_xyz789",
    "transcript": "...",
    "duration_seconds": 120,
    "analysis": { "sentiment": "positive", "resolution": true }
  }
}
```

用 HMAC SHA-256 驗證：
```typescript
const hmac = crypto.createHmac('sha256', process.env.WEBHOOK_SECRET)
  .update(JSON.stringify(request.body)).digest('hex');
if (signature !== hmac) { /* reject */ }
```

---

## 成本最佳化

模型陣容和價格過時得很快，挑選之前，先到 ElevenLabs dashboard（Agent → LLM 下拉選單）或文件查看最新的清單，不要寫死一個你在這個 session 裡沒驗證過的模型 id。比較持久的選法是：大多數 agent 用目前便宜又快的模型（只有品質需要時才升級），知識庫很大時用長 context 的模型。

主要的省錢方式：
- **LLM 快取**：重複的 prompt 最多可省 90%（在設定裡啟用）
- **Prompt 長度**：同樣的指示，150 個 token 比 500 個 token 好
- **用 RAG，不要塞 context**：用知識庫，不要把 system prompt 塞滿
- **時長限制**：設定 `max_duration_seconds`，避免對話失控
- **輪流模式**：「patient」模式 = 較少 LLM 呼叫 = 成本較低

---

## CLI 快速參考

```bash
elevenlabs auth login                              # Authenticate
elevenlabs agents init                             # Init project
elevenlabs agents add "Name" --template default    # Add agent
elevenlabs agents push --env dev                   # Deploy to dev
elevenlabs agents push --env prod --dry-run        # Preview prod deploy
elevenlabs agents push --env prod                  # Deploy to prod
elevenlabs agents pull                             # Pull from platform
elevenlabs agents test "Name"                      # Run tests
elevenlabs agents list                             # List agents
elevenlabs agents status                           # Check sync status
elevenlabs agents widget "Name"                    # Generate widget
elevenlabs tools add-webhook "Name" --config-path tool.json  # Add tool
elevenlabs tests add "Name" --template basic-llm   # Add test
```

環境變數：CI/CD 用 `ELEVENLABS_API_KEY`。

---

## 選用參考資料

特殊用途請見：
- `references/api-reference.md`：以程式管理 agent 的完整 REST API
- `references/compliance-guide.md`：GDPR、HIPAA、PCI DSS、資料落地
- `references/workflow-examples.md`：多 agent 路由、轉接升級、多語言

---

## 資源檔

- `assets/react-sdk-boilerplate.tsx`：React 整合範本
- `assets/react-native-boilerplate.tsx`：React Native 範本
- `assets/swift-sdk-boilerplate.swift`：Swift/iOS 範本
- `assets/javascript-sdk-boilerplate.js`：純 JS 範本
- `assets/widget-embed-template.html`：可嵌入的 widget
- `assets/system-prompt-template.md`：System prompt 指南
- `assets/agent-config-schema.json`：設定 schema 參考
- `assets/ci-cd-example.yml`：CI/CD pipeline 範本
