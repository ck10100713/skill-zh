---
name: mcp-builder
description: "用 Python 和 FastMCP 打造 MCP server。定義 tool / resource / prompt，建置 server，在本機測試，部署到 FastMCP Cloud 或 Docker。只要使用者提到要做 MCP server、把工具開放給 LLM、FastMCP、做 Claude 整合，或在排查 FastMCP 的 module-level server、storage、lifespan、middleware、OAuth 或部署錯誤，就用這個 skill。"
compatibility: claude-code-only
---

# MCP Builder

從你需要的工具描述，打造一個能運作的 MCP server。產出可部署的 Python server，使用 FastMCP。

## 工作流程

### 步驟 1：定義要開放什麼

問 server 需要提供什麼：

- **Tools**：Claude 可以呼叫的函式（API 包裝、計算、檔案操作）
- **Resources**：Claude 可以讀取的資料（資料庫紀錄、設定、文件）
- **Prompts**：帶參數、可重複使用的 prompt 範本

像「用來查詢我們客戶資料庫的 MCP server」這樣簡短的描述就夠了。

### 步驟 2：建立 Server 骨架

```bash
pip install fastmcp
```

建立 server 檔案。server 實例**一定要**放在 module level：

```python
from fastmcp import FastMCP

# MUST be at module level for FastMCP Cloud
mcp = FastMCP("My Server")

@mcp.tool()
async def search_customers(query: str) -> str:
    """Search customers by name or email."""
    # Implementation here
    return f"Found customers matching: {query}"

@mcp.resource("customers://{customer_id}")
async def get_customer(customer_id: str) -> str:
    """Get customer details by ID."""
    return f"Customer {customer_id} details"

if __name__ == "__main__":
    mcp.run()
```

### 步驟 3：加上搭配的 CLI Script（選用）

為了在 Claude Code 終端機使用，在 MCP server 旁邊加上 script：

```
my-mcp-server/
├── src/index.ts          # MCP server (for Claude.ai)
├── scripts/
│   ├── search.ts         # CLI version of search tool
│   └── _shared.ts        # Shared auth/config
├── SCRIPTS.md            # Documents available scripts
└── package.json
```

CLI script 能做檔案 I/O、批次處理，以及 MCP 做不到的更豐富輸出。
TypeScript 範本見 `assets/SCRIPTS-TEMPLATE.md` 和 `assets/script-template.ts`。

### 步驟 4：本機測試

**快速測試，直接執行：**

```bash
python server.py
```

**帶 inspector UI 的開發模式（建議）：**

```bash
fastmcp dev server.py
# Opens inspector at http://localhost:5173
# Hot reload, detailed logging, tool/resource inspection
```

**給遠端 client 用的 HTTP 模式：**

```bash
python server.py --transport http --port 8000
```

**用 FastMCP Client 寫自動化測試 script：**

```python
import asyncio
from fastmcp import Client

async def test_server(server_path):
    async with Client(server_path) as client:
        # List everything
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        print(f"Tools: {[t.name for t in tools]}")
        print(f"Resources: {[r.uri for r in resources]}")
        print(f"Prompts: {[p.name for p in prompts]}")

        # Call first tool
        if tools:
            result = await client.call_tool(tools[0].name, {})
            print(f"Tool result: {result}")

        # Read first resource
        if resources:
            data = await client.read_resource(resources[0].uri)
            print(f"Resource data: {data}")

asyncio.run(test_server("server.py"))
```

### 步驟 5：部署前檢查清單

部署前先跑這些檢查。所有必要檢查都要通過。

**必要（沒過會導致部署失敗）：**

1. Server 檔案存在
2. Python 語法有效：`python3 -m py_compile server.py`
3. 有 module-level 的 server 物件（不能在函式裡面）：
   ```bash
   grep -q "^mcp = FastMCP\|^server = FastMCP\|^app = FastMCP" server.py
   ```
4. 有 `requirements.txt`，而且只含 PyPI 套件（不能有 `git+`、`-e`、`.whl`、`.tar.gz`）
5. 沒有寫死的 secret（檢查 `api_key = "..."` 這類寫法，排除 `os.getenv`/`os.environ`）

**建議（警告）：**

6. `requirements.txt` 裡有列 `fastmcp`
7. `.gitignore` 有包含 `.env`
8. 沒有循環 import
9. Git repository 已初始化並有 remote
10. Server 可以載入：`timeout 5 fastmcp inspect server.py`

### 步驟 6：部署

**FastMCP Cloud（最簡單）：**

```bash
git add . && git commit -m "Ready for deployment"
git push -u origin main
# Visit https://fastmcp.cloud, connect repo, add env vars, deploy
# URL: https://your-project.fastmcp.app/mcp
```

Cloud 的要求：
- Module-level 的 server 物件，名稱是 `mcp`、`server` 或 `app`
- `requirements.txt` 裡只有 PyPI 相依套件
- 公開的 GitHub repository
- secret 用環境變數（不能寫死）
- push 到 main 會自動部署，PR 有預覽部署

**Docker（自行代管）：**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "server.py", "--transport", "http", "--port", "8000"]
```

**Cloudflare Workers（edge）：**
用 TypeScript 搭配 Cloudflare 的 `agents` SDK（`McpAgent`）來做；目前的範本在 Cloudflare 的 remote MCP server 文件裡。

---

## 關鍵模式

### Module-Level 的 Server 實例

FastMCP Cloud 要求 server 實例放在 module level：

```python
# CORRECT
mcp = FastMCP("My Server")

@mcp.tool()
def my_tool(): ...

# WRONG -- Cloud can't find the server
def create_server():
    mcp = FastMCP("My Server")
    return mcp

# FIX for factory pattern -- export at module level
def create_server() -> FastMCP:
    mcp = FastMCP("server")
    return mcp
mcp = create_server()
```

### 一定要有型別標註

FastMCP 用型別標註來產生 tool 的 schema：

```python
@mcp.tool()
async def search(
    query: str,           # Required parameter
    limit: int = 10,      # Optional with default
    tags: list[str] = []  # Complex types supported
) -> str:
    """Docstring becomes the tool description."""
    ...
```

### 錯誤處理

錯誤用字串回傳，不要 raise exception：

```python
@mcp.tool()
async def get_data(id: str) -> str:
    try:
        result = await fetch_data(id)
        return json.dumps(result)
    except NotFoundError:
        return f"Error: No data found for ID {id}"
```

### 適合 Cloud 的 Server 模式

```python
import os
from fastmcp import FastMCP

mcp = FastMCP("production-server")
API_KEY = os.getenv("API_KEY")

@mcp.tool()
async def production_tool(data: str) -> dict:
    if not API_KEY:
        return {"error": "API_KEY not configured"}
    return {"status": "success", "data": data}

if __name__ == "__main__":
    mcp.run()
```

---

## 常見錯誤與修法

這些錯誤你一定會碰到。部署前先修好。

| 錯誤 | 原因 | 修法 |
|-------|-------|-----|
| `RuntimeError: No server object found at module level` | Server 放在函式裡 | 在 module level export `mcp = FastMCP(...)` |
| `RuntimeError: no running event loop` | 缺少 async/await | 非同步操作用 `async def` |
| `TypeError: missing required argument 'context'` | Context 沒有加型別提示 | 加上帶型別提示的 `context: Context` |
| `ValueError: Invalid resource URI` | 缺少 URI scheme | 用 `data://`、`file://`、`info://`、`api://` |
| Resource template 參數不一致 | 名稱不一致 | `user://{user_id}` 需要 `def get_user(user_id: str)` |
| Pydantic 驗證錯誤 | 型別提示錯誤 | 確保提示和實際資料型別一致 |
| Transport 不一致 | Client/server 協定不同 | 兩邊都設成 stdio，或兩邊都設成 http |
| Editable package 的 import 錯誤 | Package 沒有安裝 | `pip install -e .` 或加到 PYTHONPATH |
| `DeprecationWarning: mcp.settings` | 舊的 API | 改用 `os.getenv()` |
| Port 已被占用 | 殘留的 process | `lsof -ti:8000 \| xargs kill -9` |
| Schema 產生失敗 | 非 JSON 型別 | 用 JSON 相容的型別（不要用 NumPy array） |
| JSON 序列化錯誤 | 回應裡有 datetime/bytes | 轉成 `.isoformat()` 或字串 |
| 循環 import | 工廠函式放在 `__init__.py` | 用直接 import，避免工廠模式 |
| Python 3.12+ datetime 警告 | `datetime.utcnow()` 已棄用 | 用 `datetime.now(timezone.utc)` |
| Import 時就執行 | 非同步資源放在 module level | 用 lazy init 模式 |

---

## 正式環境模式

### 自成一體的 Server

把所有工具函式放在同一個檔案，避免循環 import：

```python
from fastmcp import FastMCP
import os

mcp = FastMCP("my-server")

# Config
class Config:
    API_KEY = os.getenv("API_KEY", "")
    BASE_URL = os.getenv("BASE_URL", "https://api.example.com")

# Helpers
def format_success(data): return {"status": "success", "data": data}
def format_error(msg): return {"status": "error", "message": msg}

@mcp.tool()
async def my_tool(query: str) -> dict:
    if not Config.API_KEY:
        return format_error("API_KEY not configured")
    return format_success({"query": query})
```

### 延遲初始化

不要在 module level 建立非同步資源。第一次用到時才初始化：

```python
_db = None

async def get_db():
    global _db
    if _db is None:
        _db = await create_connection(Config.DB_URL)
    return _db
```

### 健康檢查 Resource

```python
@mcp.resource("health://status")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "checks": {
            "api": "connected",
            "database": "connected"
        }
    }
```

### 連線池

```python
import httpx

_client = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=Config.BASE_URL,
            headers={"Authorization": f"Bearer {Config.API_KEY}"},
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=5),
            timeout=30.0
        )
    return _client
```

### 帶退避的重試

```python
async def retry_with_backoff(func, max_retries=3, initial_delay=1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = initial_delay * (2 ** attempt)
            await asyncio.sleep(delay)
```

---

## Context 功能（進階）

### Context 注入

```python
from fastmcp import Context

@mcp.tool()
async def tool_with_context(param: str, context: Context) -> dict:
    # Context parameter MUST have type hint
    pass
```

### 進度追蹤

```python
@mcp.tool()
async def long_task(items: list[str], context: Context) -> str:
    for i, item in enumerate(items):
        await context.report_progress(i + 1, len(items), f"Processing {item}")
        await process(item)
    return "Done"
```

### Sampling（在 tool 裡呼叫 LLM）

```python
@mcp.tool()
async def summarise(text: str, context: Context) -> str:
    result = await context.request_sampling(
        messages=[{"role": "user", "content": f"Summarise: {text}"}],
        max_tokens=200
    )
    return result
```

---

## CLI 速查

```bash
fastmcp dev server.py              # Dev mode with inspector UI
fastmcp run server.py              # Run (stdio)
fastmcp run server.py --transport http --port 8000  # Run (HTTP)
fastmcp inspect server.py          # Inspect without running
fastmcp install server.py          # Install to Claude Desktop
fastmcp deploy server.py --name my-server  # Deploy to Cloud
```

環境變數：`FASTMCP_LOG_LEVEL`（DEBUG/INFO/WARNING/ERROR）、`FASTMCP_ENV`（development/staging/production）。

---

## 整合模式（選用）

特定的整合做法見 `references/integration-patterns.md`：
- **手動 API**：用可重複使用 client 的 `httpx.AsyncClient`
- **OpenAPI 自動產生**：`FastMCP.from_openapi(spec, client, route_maps=[...])`
- **FastAPI 轉換**：`FastMCP.from_fastapi(app)`

---

## 資產檔案

- `assets/basic-server.py`：最精簡的 FastMCP server 範本
- `assets/self-contained-server.py`：含 storage 和 middleware 的 server
- `assets/tools-examples.py`：tool 模式與型別標註
- `assets/resources-examples.py`：resource URI 模式
- `assets/prompts-examples.py`：prompt 範本模式
- `assets/client-example.py`：MCP client 用法
- `assets/SCRIPTS-TEMPLATE.md`：CLI 搭配文件的範本
- `assets/script-template.ts`：TypeScript CLI script 範本
