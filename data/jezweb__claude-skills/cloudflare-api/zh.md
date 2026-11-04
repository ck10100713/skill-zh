---
name: cloudflare-api
description: "直接呼叫 Cloudflare REST API，處理 wrangler 和 MCP 做不好的操作：批次 DNS、custom hostname、email routing、清 cache、WAF 規則、redirect 規則、zone 設定、Worker route、D1 跨資料庫查詢、R2 批次操作、KV 批次讀寫、Vectorize 查詢、Queues，以及全帳號資源盤點。產出 curl 指令或腳本。觸發詞：'cloudflare api', 'bulk dns', 'custom hostname', 'email routing', 'cache purge', 'waf rule', 'd1 query', 'r2 bucket', 'kv bulk', 'vectorize query', 'audit resources', 'fleet operation'。"
compatibility: claude-code-only
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Cloudflare API

wrangler CLI 或 MCP server 不適合時，直接呼叫 Cloudflare REST API。用於批次操作、全帳號範圍的變更，以及 wrangler 沒有提供的功能。

## 什麼時候用這個，而不是 Wrangler 或 MCP

| 使用情境 | Wrangler | MCP | 這個 skill |
|----------|---------|-----|-----------|
| 部署 Worker | 可以 | 可以 | 不用 |
| 建立 D1 資料庫 | 可以 | 可以 | 不用 |
| 批次更新 50 筆 DNS 紀錄 | 慢（一次一筆） | 慢（每筆一次工具呼叫） | 可以：批次腳本 |
| 白標用的 custom hostname | 不行 | 部分支援 | 可以 |
| Email routing 規則 | 不行 | 部分支援 | 可以 |
| WAF/防火牆規則 | 不行 | 可以但很囉嗦 | 可以：直接呼叫 API |
| 批次 redirect 規則 | 不行 | 一次一筆 | 可以：批次腳本 |
| 20 個 zone 的 zone 設定 | 不行 | 20 次獨立呼叫 | 可以：全域腳本 |
| 依 tag/prefix 清 cache | 不行 | 可以 | 可以（要寫腳本時） |
| Worker route 管理 | 有限 | 可以 | 可以（批次時） |
| 分析/log 查詢 | 不行 | 部分支援 | 可以：GraphQL |
| 跨資料庫的 D1 查詢/匯出 | 一次一個 DB | 一次一個 DB | 可以：跨 DB 腳本 |
| R2 批次物件操作 | 不行 | 一次一個 | 可以：S3 API + 批次 |
| KV 批次讀/寫/刪 | 一次一筆 | 一次一筆 | 可以：批次 endpoint |
| Vectorize 查詢/刪除 | 不行 | 只能透過 Worker | 可以：直接呼叫 API |
| 對 Queue 注入訊息 | 不行 | 只能透過 Worker | 可以：直接呼叫 API |
| 盤點帳號下的所有資源 | 不行 | 很繁瑣 | 可以：盤點腳本 |

**經驗法則**：單一操作 → MCP 或 wrangler。批次/全帳號/腳本化 → 直接呼叫 API。

## 驗證設定

### API Token（建議）

建立有範圍限制的 token：Dashboard → My Profile → API Tokens → Create Token

```bash
# Store it
export CLOUDFLARE_API_TOKEN="your-token-here"

# Test it
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.success'
```

**Token 權限範圍**：一律用最小權限。常見的預設組合：
- "Edit zone DNS"：DNS 操作
- "Edit zone settings"：zone 設定變更
- "Edit Cloudflare Workers"：Worker route 管理
- "Read analytics"：GraphQL 分析

### Account 與 Zone ID

```bash
# List your zones (find zone IDs)
curl -s "https://api.cloudflare.com/client/v4/zones?per_page=50" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.result[] | {name, id}'

# Get zone ID by domain name
ZONE_ID=$(curl -s "https://api.cloudflare.com/client/v4/zones?name=example.com" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq -r '.result[0].id')
```

ID 存在環境變數或設定檔裡，不要寫死在腳本中。

## 工作流程

### 批次 DNS 操作

**一次新增/更新很多筆紀錄**（例如遷移網域、幫新客戶設定）：

```bash
# Pattern: read records from a file, create in batch
while IFS=',' read -r type name content proxied; do
  curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"type\":\"$type\",\"name\":\"$name\",\"content\":\"$content\",\"proxied\":$proxied,\"ttl\":1}" \
    | jq '{name: .result.name, id: .result.id, success: .success}'
  sleep 0.25  # Rate limit: 1200 req/5min
done < dns-records.csv
```

**匯出 zone 的所有紀錄**（備份或遷移）：

```bash
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?per_page=100" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  | jq -r '.result[] | [.type, .name, .content, .proxied] | @csv' > dns-export.csv
```

**跨紀錄尋找並取代**（例如 IP 遷移）：

```bash
OLD_IP="203.0.113.1"
NEW_IP="198.51.100.1"

# Find records pointing to old IP
RECORDS=$(curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?content=$OLD_IP" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq -r '.result[].id')

# Update each one
for RECORD_ID in $RECORDS; do
  curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"content\":\"$NEW_IP\"}" | jq '.success'
done
```

### Custom Hostname（白標的客戶網域）

給 SaaS app 用，客戶使用自己的網域（例如 `app.clientdomain.com` → 你的 Worker）：

```bash
# Create custom hostname
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/custom_hostnames" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "app.clientdomain.com",
    "ssl": {
      "method": "http",
      "type": "dv",
      "settings": {
        "min_tls_version": "1.2"
      }
    }
  }' | jq '{id: .result.id, status: .result.status, ssl_status: .result.ssl.status}'

# List custom hostnames
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/custom_hostnames?per_page=50" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  | jq '.result[] | {hostname, status, ssl_status: .ssl.status}'

# Check status (client needs to add CNAME)
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/custom_hostnames/$HOSTNAME_ID" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.result.status'
```

**客戶端的設定**：他們要加一筆 CNAME：`app.clientdomain.com → your-worker.your-domain.com`

### Email Routing 規則

```bash
# Enable email routing on zone
curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/email/routing/enable" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"

# Create a routing rule (forward info@ to a real address)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/email/routing/rules" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Forward info@",
    "enabled": true,
    "matchers": [{"type": "literal", "field": "to", "value": "info@example.com"}],
    "actions": [{"type": "forward", "value": ["real-inbox@gmail.com"]}]
  }' | jq '.success'

# Create catch-all rule
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/email/routing/rules" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Catch-all",
    "enabled": true,
    "matchers": [{"type": "all"}],
    "actions": [{"type": "forward", "value": ["catchall@company.com"]}]
  }' | jq '.success'

# List rules
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/email/routing/rules" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.result[] | {name, enabled, matchers, actions}'
```

### 清除 Cache

```bash
# Purge everything (nuclear option)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"purge_everything": true}'

# Purge specific URLs
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"files": ["https://example.com/styles.css", "https://example.com/app.js"]}'

# Purge by cache tag (requires Enterprise or cache tag headers)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tags": ["product-123", "homepage"]}'

# Purge by prefix
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prefixes": ["https://example.com/images/"]}'
```

### Redirect 規則（批次）

```bash
# Create a redirect rule
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/rulesets/phases/http_request_dynamic_redirect/entrypoint" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [
      {
        "expression": "(http.request.uri.path eq \"/old-page\")",
        "description": "Redirect old-page to new-page",
        "action": "redirect",
        "action_parameters": {
          "from_value": {
            "target_url": {"value": "https://example.com/new-page"},
            "status_code": 301
          }
        }
      }
    ]
  }'
```

**批次 redirect**（從 CSV 產生 301）：用程式產生 rules 陣列：

```python
import json, csv

rules = []
with open('redirects.csv') as f:
    for row in csv.reader(f):
        old_path, new_url = row
        rules.append({
            "expression": f'(http.request.uri.path eq "{old_path}")',
            "description": f"Redirect {old_path}",
            "action": "redirect",
            "action_parameters": {
                "from_value": {
                    "target_url": {"value": new_url},
                    "status_code": 301
                }
            }
        })
print(json.dumps({"rules": rules}, indent=2))
```

### Zone 設定（全域）

對多個 zone 套用同樣的設定：

```bash
# Settings to apply
SETTINGS='{"value":"full"}'  # SSL mode: full (strict)

# Get all active zones
ZONES=$(curl -s "https://api.cloudflare.com/client/v4/zones?status=active&per_page=50" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq -r '.result[].id')

# Apply to each zone
for ZONE in $ZONES; do
  curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE/settings/ssl" \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$SETTINGS" | jq "{zone: .result.id, success: .success}"
  sleep 0.25
done
```

常見的全域設定：
- `ssl`："full" 或 "strict"
- `min_tls_version`："1.2"
- `always_use_https`："on"
- `security_level`："medium"
- `browser_cache_ttl`：14400

### WAF / 防火牆規則

```bash
# Create a WAF custom rule (block by country)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/rulesets/phases/http_request_firewall_custom/entrypoint" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [{
      "expression": "(ip.geoip.country in {\"RU\" \"CN\"})",
      "action": "block",
      "description": "Block traffic from RU and CN"
    }]
  }'

# Rate limiting rule
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/rulesets/phases/http_ratelimit/entrypoint" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [{
      "expression": "(http.request.uri.path contains \"/api/\")",
      "action": "block",
      "ratelimit": {
        "characteristics": ["ip.src"],
        "period": 60,
        "requests_per_period": 100
      },
      "description": "Rate limit API to 100 req/min per IP"
    }]
  }'
```

### Worker Route

```bash
# List routes
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/workers/routes" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.result[] | {pattern, id}'

# Create route
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/workers/routes" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pattern": "api.example.com/*", "script": "my-worker"}'

# Delete route
curl -s -X DELETE "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/workers/routes/$ROUTE_ID" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

### 分析（GraphQL）

```bash
# Worker analytics (requests, errors, CPU time)
curl -s -X POST "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ viewer { zones(filter: {zoneTag: \"'$ZONE_ID'\"}) { httpRequests1dGroups(limit: 7, filter: {date_gt: \"2026-03-10\"}) { dimensions { date } sum { requests pageViews } } } } }"
  }' | jq '.data.viewer.zones[0].httpRequests1dGroups'
```

## Rate Limit

| Endpoint | 限制 |
|---------|-------|
| 大部分的 API 呼叫 | 1200 requests / 5 分鐘 |
| DNS 紀錄操作 | 1200 / 5 分鐘（與上面共用額度） |
| 清 cache | 每天 1000 次 purge 呼叫 |
| 建立 zone | 每分鐘 5 個 |

**在腳本裡**：持續性的操作，呼叫之間加 `sleep 0.25`。要控制並行度就用 `p-limit` 或 `xargs -P 4`。

## 產生腳本

使用者描述需求後，在 `.jez/scripts/` 裡產生腳本，腳本要：
- 從環境變數讀 API token（絕對不要寫死）
- 處理列表操作的分頁
- 包含錯誤檢查（每次呼叫後用 `jq '.success'`）
- 呼叫之間加上 rate limit 的 sleep
- 記錄它做了什麼
- 盡可能支援 `--dry-run`

簡單的操作用 `curl` + `jq`。複雜的邏輯（分頁迴圈、錯誤處理、CSV 處理）用 Python。較大的腳本想要型別安全，就用 TypeScript 搭配 `cloudflare` npm 套件。

## API 參考

Base URL：`https://api.cloudflare.com/client/v4/`

完整文件：`https://developers.cloudflare.com/api/`

API 遵循一致的模式：
- `GET /zones`：列出
- `POST /zones`：建立
- `GET /zones/:id`：讀取
- `PATCH /zones/:id`：更新
- `DELETE /zones/:id`：刪除
- `PUT /zones/:id/settings/:name`：更新設定

每個回應都是 `{ success: bool, errors: [], messages: [], result: {} }`。

## 參考檔案

| 什麼時候 | 讀這個 |
|------|------|
| D1、R2、KV、Workers、Vectorize、Queues 的 API 用法 | [references/developer-platform-api.md](references/developer-platform-api.md) |
