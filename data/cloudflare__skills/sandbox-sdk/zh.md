---
name: sandbox-sdk
description: 建置能安全執行程式碼的沙箱應用程式。在建置 AI 程式碼執行、code interpreter、CI/CD 系統、互動式開發環境，或要執行不受信任的程式碼時載入。涵蓋 Sandbox SDK 的生命週期、指令、檔案、code interpreter 和 preview URL。檢索 Cloudflare 文件優先於預訓練知識。
---

# Cloudflare Sandbox SDK

在 Cloudflare Workers 上建置安全、隔離的程式碼執行環境。

## FIRST: Verify Installation

```bash
npm install @cloudflare/sandbox
docker info  # 必須成功，本機開發需要 Docker
```

## Retrieval Sources

你對 Sandbox SDK 的知識可能已經過時。任何 Sandbox SDK 的任務，都要**優先用檢索，不要靠預訓練記憶**。

| 資源 | URL |
|----------|-----|
| Docs | https://developers.cloudflare.com/sandbox/ |
| API Reference | https://developers.cloudflare.com/sandbox/api/ |
| Examples | https://github.com/cloudflare/sandbox-sdk/tree/main/examples |
| Get Started | https://developers.cloudflare.com/sandbox/get-started/ |

實作功能時，先抓對應的文件頁面或範例。

## Required Configuration

**wrangler.jsonc**（要照抄，不要改結構）：

```jsonc
{
  "containers": [{
    "class_name": "Sandbox",
    "image": "./Dockerfile",
    "instance_type": "lite",
    "max_instances": 1
  }],
  "durable_objects": {
    "bindings": [{ "class_name": "Sandbox", "name": "Sandbox" }]
  },
  "migrations": [{ "new_sqlite_classes": ["Sandbox"], "tag": "v1" }]
}
```

**Worker entry**：必須重新 export Sandbox class：

```typescript
import { getSandbox } from '@cloudflare/sandbox';
export { Sandbox } from '@cloudflare/sandbox';  // 必要的 export
```

## Quick Reference

| 任務 | Method |
|------|--------|
| 取得 sandbox | `getSandbox(env.Sandbox, 'user-123')` |
| 執行指令 | `await sandbox.exec('python script.py')` |
| 執行程式碼（interpreter） | `await sandbox.runCode(code, { language: 'python' })` |
| 寫檔案 | `await sandbox.writeFile('/workspace/app.py', content)` |
| 讀檔案 | `await sandbox.readFile('/workspace/app.py')` |
| 建立目錄 | `await sandbox.mkdir('/workspace/src', { recursive: true })` |
| 列出檔案 | `await sandbox.listFiles('/workspace')` |
| 開放 port | `await sandbox.exposePort(8080)` |
| 銷毀 | `await sandbox.destroy()` |

## Core Patterns

### Execute Commands

```typescript
const sandbox = getSandbox(env.Sandbox, 'user-123');
const result = await sandbox.exec('python --version');
// result: { stdout, stderr, exitCode, success }
```

### Code Interpreter (Recommended for AI)

要執行 LLM 產生的程式碼並取得豐富的輸出，用 `runCode()`：

```typescript
const ctx = await sandbox.createCodeContext({ language: 'python' });

await sandbox.runCode('import pandas as pd; data = [1,2,3]', { context: ctx });
const result = await sandbox.runCode('sum(data)', { context: ctx });
// result.results[0].text = "6"
```

**支援的語言**：`python`、`javascript`、`typescript`

狀態會在同一個 context 內保留。正式環境要明確建立 context。

### File Operations

```typescript
await sandbox.mkdir('/workspace/project', { recursive: true });
await sandbox.writeFile('/workspace/project/main.py', code);
const file = await sandbox.readFile('/workspace/project/main.py');
const files = await sandbox.listFiles('/workspace/project');
```

## When to Use What

| 需求 | 用什麼 | 原因 |
|------|-----|-----|
| Shell 指令、腳本 | `exec()` | 直接控制、streaming |
| LLM 產生的程式碼 | `runCode()` | 豐富的輸出、狀態保留 |
| Build／測試 pipeline | `exec()` | exit code、stderr 擷取 |
| 資料分析 | `runCode()` | 圖表、表格、pandas |

## Extending the Dockerfile

基底映像檔（`docker.io/cloudflare/sandbox:0.7.0`）包含 Python 3.11、Node.js 20 和常用工具。

要加依賴，就擴充 Dockerfile：

```dockerfile
FROM docker.io/cloudflare/sandbox:0.7.0

# Python 套件
RUN pip install requests beautifulsoup4

# Node 套件（全域）
RUN npm install -g typescript

# 系統套件
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

EXPOSE 8080  # 本機開發要開放 port 就必須有這行
```

映像檔要保持精簡，會影響 cold start 時間。

## Preview URLs (Port Exposure)

開放在 sandbox 裡執行的 HTTP 服務：

```typescript
const { url } = await sandbox.exposePort(8080);
// 回傳該服務的 preview URL
```

**正式環境的要求**：Preview URL 需要有 wildcard DNS（`*.yourdomain.com`）的自訂網域。`.workers.dev` 網域不支援 preview URL 的子網域。

參見：https://developers.cloudflare.com/sandbox/guides/expose-services/

## OpenAI Agents SDK Integration

SDK 在 `@cloudflare/sandbox/openai` 提供給 OpenAI Agents 用的 helper：

```typescript
import { Shell, Editor } from '@cloudflare/sandbox/openai';
```

完整的整合模式見 `examples/openai-agents`。

## Sandbox Lifecycle

- `getSandbox()` 會立刻回傳，container 在第一次操作時才會延遲啟動
- Container 閒置 10 分鐘後會休眠（可透過 `sleepAfter` 設定）
- 用 `destroy()` 立刻釋放資源
- 同一個 `sandboxId` 一定會回傳同一個 sandbox instance

## Anti-Patterns

- **不要用內部 client**（`CommandClient`、`FileClient`），用 `sandbox.*` method
- **不要漏掉 Sandbox 的 export**：沒有 `export { Sandbox }`，Worker 就部署不了
- **多使用者的情況，不要寫死 sandbox ID**，用使用者／session 的識別碼
- **不要忘了清理**：臨時的 sandbox 要呼叫 `destroy()`

## Detailed References

- **[references/api-quick-ref.md](references/api-quick-ref.md)** - 完整 API，含選項和回傳型別
- **[references/examples.md](references/examples.md)** - 範例索引和使用情境
