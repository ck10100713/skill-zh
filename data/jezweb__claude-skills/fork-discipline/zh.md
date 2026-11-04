---
name: fork-discipline
description: "稽核並落實多客戶專案中 core 與 client 的界線。偵測共用平台程式碼和客戶專屬程式碼糾纏的地方，找出寫死的客戶判斷、用取代而不是合併的設定檔、散落各處的客戶程式碼、migration 衝突，以及缺少的擴充點。產出界線地圖、違規報告和重構計畫，也可以選擇產生 FORK.md 文件和重整用的 script。觸發詞：'fork discipline'、'check the boundary'、'is this core or client'、'platform audit'、'client separation'、'fork test'、'refactor for multi-client'、'clean up the fork'。"
compatibility: claude-code-only
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Fork Discipline

稽核多客戶 codebase 裡 core 與 client 的界線。每個多客戶專案都應該把共用的平台程式碼（core）和每個部署專屬的程式碼（client）切乾淨。這個 skill 會找出界線模糊的地方，並告訴你怎麼修。

## 原則

```
project/
  src/            ← CORE: shared platform code. Never modified per client.
  config/         ← DEFAULTS: base config, feature flags, sensible defaults.
  clients/
    client-name/  ← CLIENT: everything that varies per deployment.
      config      ← overrides merged over defaults
      content     ← seed data, KB articles, templates
      schema      ← domain tables, migrations (numbered 0100+)
      custom/     ← bespoke features (routes, pages, tools)
```

**Fork test**：改任何檔案之前，先問「這是 core 還是 client？」如果答不出來，代表界線切得不夠乾淨。

## 什麼時候用

- 要在既有專案加第二個或第三個客戶之前
- 專案自然長大、界線變模糊之後
- 發現共用程式碼裡開始冒出 `if (client === 'acme')` 這類判斷
- 大型重構之前，想搞清楚哪些是真的共用、哪些是專屬
- 新進開發者需要了解架構時
- 定期替多客戶專案做健康檢查

## 模式

| 模式 | 觸發 | 產出 |
|------|---------|-----------------|
| **audit** | "fork discipline"、"check the boundary" | 界線地圖 + 違規報告 |
| **document** | "write FORK.md"、"document the boundary" | 專案的 FORK.md 檔 |
| **refactor** | "clean up the fork"、"enforce the boundary" | 重構計畫 + migration script |

預設：**audit**

---

## Audit 模式

### 步驟 1：偵測專案類型

判斷這是不是多客戶專案，以及它用哪種模式：

| 訊號 | 模式 |
|--------|---------|
| 有 `clients/` 或 `tenants/` 目錄 | 明確的多客戶 |
| 多個以客戶名稱命名的設定檔 | 設定驅動的多客戶 |
| `packages/` 裡有共用套件和各客戶套件 | Monorepo 多客戶 |
| 有 `CLIENT_NAME` 或 `TENANT_ID` 這類環境變數 | 執行期多客戶 |
| 只有一個部署、沒有客戶目錄 | 單一客戶（可能正在走向多客戶） |

如果是單一客戶：看專案的 CLAUDE.md 或 codebase 有沒有跡象顯示之後會變多客戶。有的話，就稽核它準備好了沒。如果真的永遠只有一個客戶，就不需要這個 skill。

### 步驟 2：畫出界線

掃過 codebase，建立界線地圖：

```
CORE (shared by all clients):
  src/server/          → API routes, middleware, auth
  src/client/          → React components, hooks, pages
  src/db/schema.ts     → Shared database schema
  migrations/0001-0050 → Core migrations

CLIENT (per-deployment):
  clients/acme/config.ts    → Client overrides
  clients/acme/kb/          → Knowledge base articles
  clients/acme/seed.sql     → Seed data
  migrations/0100+          → Client schema extensions

BLURRED (needs attention):
  src/server/routes/acme-custom.ts  → Client code in core!
  src/config/defaults.ts line 47    → Hardcoded client domain
```

### 步驟 3：找出違規

掃描這些特定的反模式：

#### Core 程式碼裡出現客戶名稱

```bash
# Search for hardcoded client identifiers in shared code
grep -rn "acme\|smith\|client_name_here" src/ --include="*.ts" --include="*.tsx"

# Search for client-specific conditionals
grep -rn "if.*client.*===\|switch.*client\|case.*['\"]acme" src/ --include="*.ts" --include="*.tsx"

# Search for environment-based client checks in shared code
grep -rn "CLIENT_NAME\|TENANT_ID\|process.env.*CLIENT" src/ --include="*.ts" --include="*.tsx"
```

**嚴重度**：高。core 程式碼裡每多一個寫死的客戶判斷，下一個客戶就得改共用程式碼。

#### 設定用取代而不是合併

檢查客戶設定是整份取代，還是合併在預設值之上：

```typescript
// BAD — client config is a complete replacement
// clients/acme/config.ts
export default {
  theme: { primary: '#1E40AF' },
  features: { emailOutbox: true },
  // Missing all other defaults — they're lost
}

// GOOD — client config is a delta merged over defaults
// clients/acme/config.ts
export default {
  theme: { primary: '#1E40AF' },  // Only overrides what's different
}
// config/defaults.ts has everything else
```

要找的是：大小可疑地接近預設檔的客戶設定檔，或是客戶設定裡定義了預設值本來就處理好的欄位。

**嚴重度**：中。過時的客戶設定會漏掉新的預設值和功能。

#### 散落各處的客戶程式碼

檢查客戶專屬的程式碼是不是放在客戶目錄之外：

```bash
# Files with client names in their path but inside src/
find src/ -name "*acme*" -o -name "*smith*" -o -name "*client-name*"

# Routes or pages that serve a single client
grep -rn "// only for\|// acme only\|// client-specific" src/ --include="*.ts" --include="*.tsx"
```

**嚴重度**：高。`src/` 裡有客戶程式碼，代表 core 不是真的共用。

#### 缺少擴充點

檢查 core 有沒有機制讓客戶不用改 core 就能客製：

| 擴充點 | 怎麼檢查 | 能做到什麼 |
|----------------|-------------|-----------------|
| 設定合併 | `config/` 有 merge 函式嗎？ | 客戶覆寫但不用整份取代 |
| 動態 import | core 會找 `clients/{name}/custom/` 嗎？ | 客戶專屬的 route/page |
| Feature flag | 功能是靠設定開關，而不是改程式碼？ | 每個客戶各自啟用/停用 |
| 主題 token | 顏色/樣式是放在變數裡，不是寫死？ | 視覺客製 |
| 內容注入 | 客戶能提供種子資料、範本嗎？ | 每個客戶專屬的內容 |
| Hook/事件系統 | 客戶能不用 patch 就擴充行為嗎？ | 自訂商業邏輯 |

**嚴重度**：中。缺少擴充點會逼得客戶程式碼被塞進 core。

#### Migration 編號衝突

```bash
# List all migration files with their numbers
ls migrations/ | sort | head -20

# Check if client migrations are in the reserved ranges
# Core: 0001-0099, Client domain: 0100-0199, Client custom: 0200+
```

**嚴重度**：在真的衝突之前是低，衝突之後就是嚴重。

#### Feature flag 與客戶判斷

```typescript
// BAD — client name check
if (clientName === 'acme') {
  showEmailOutbox = true;
}

// GOOD — feature flag in config
if (config.features.emailOutbox) {
  showEmailOutbox = true;
}
```

找出行為是依客戶身分分支、而不是依設定分支的寫法。

### 步驟 4：產出報告

寫到 `.jez/artifacts/fork-discipline-audit.md`：

```markdown
# Fork Discipline Audit: [Project Name]
**Date**: YYYY-MM-DD
**Pattern**: [explicit multi-client / config-driven / monorepo / single-heading-multi]
**Clients**: [list of client deployments]

## Boundary Map

### Core (shared)
| Path | Purpose | Clean? |
|------|---------|--------|
| src/server/ | API routes | Yes / No — [issue] |

### Client (per-deployment)
| Client | Config | Content | Schema | Custom |
|--------|--------|---------|--------|--------|
| acme | config.ts | kb/ | 0100-0120 | custom/routes/ |

### Blurred (needs attention)
| Path | Problem | Suggested fix |
|------|---------|--------------|
| src/routes/acme-custom.ts | Client code in core | Move to clients/acme/custom/ |

## Violations

### High Severity
[List with file:line, description, fix]

### Medium Severity
[List with file:line, description, fix]

### Low Severity
[List]

## Extension Points
| Point | Present? | Notes |
|-------|----------|-------|
| Config merge | Yes/No | |
| Dynamic imports | Yes/No | |
| Feature flags | Yes/No | |

## Health Score
[1-10] — [explanation]

## Top 3 Recommendations
1. [Highest impact fix]
2. [Second priority]
3. [Third priority]
```

---

## Document 模式

替專案根目錄產生 `FORK.md`，記錄界線：

```markdown
# Fork Discipline

## Architecture

This project serves multiple clients from a shared codebase.

### What's Core (don't modify per client)
[List of directories and their purpose]

### What's Client (varies per deployment)
[Client directory structure with explanation]

### How to Add a New Client
1. Copy `clients/_template/` to `clients/new-client/`
2. Edit `config.ts` with client overrides
3. Add seed data to `content/`
4. Create migrations numbered 0100+
5. Deploy with `CLIENT=new-client wrangler deploy`

### The Fork Test
Before modifying any file: is this core or client?
- Core → change in `src/`, all clients benefit
- Client → change in `clients/name/`, no other client affected
- Can't tell → the boundary needs fixing first

### Migration Numbering
| Range | Owner |
|-------|-------|
| 0001-0099 | Core platform |
| 0100-0199 | Client domain schema |
| 0200+ | Client custom features |

### Config Merge Pattern
Client configs are shallow-merged over defaults:
[Show the actual merge code from the project]
```

---

## Refactor 模式

稽核完之後，產生落實界線的具體步驟：

### 1. 把客戶程式碼搬出 core

對每個客戶程式碼放在 `src/` 裡的違規：

```bash
# Create client directory if it doesn't exist
mkdir -p clients/acme/custom/routes

# Move the file
git mv src/routes/acme-custom.ts clients/acme/custom/routes/

# Update imports in core to use dynamic discovery
```

### 2. 用 feature flag 取代客戶判斷

對 core 裡每個 `if (client === ...)`：

```typescript
// Before (in src/)
if (clientName === 'acme') {
  app.route('/email-outbox', emailRoutes);
}

// After (in src/) — feature flag
if (config.features.emailOutbox) {
  app.route('/email-outbox', emailRoutes);
}

// After (in clients/acme/config.ts) — client enables it
export default {
  features: { emailOutbox: true }
}
```

### 3. 實作設定合併

如果專案是用取代而不是合併來處理設定：

```typescript
// config/resolve.ts
import defaults from './defaults';

export function resolveConfig(clientConfig: Partial<Config>): Config {
  return {
    ...defaults,
    ...clientConfig,
    features: { ...defaults.features, ...clientConfig.features },
    theme: { ...defaults.theme, ...clientConfig.theme },
  };
}
```

### 4. 為自訂 route 加上擴充點

如果客戶需要自訂 route，但目前是靠改 core 做到的：

```typescript
// src/server/index.ts — auto-discover client routes
const clientRoutes = await import(`../../clients/${clientName}/custom/routes`)
  .catch(() => null);
if (clientRoutes?.default) {
  app.route('/custom', clientRoutes.default);
}
```

### 5. 產生重構 script

寫一個 script 到 `.jez/scripts/fork-refactor.sh`，它要：
- 建立客戶目錄結構
- 搬移找出來的檔案
- 更新 import 路徑
- 產生 FORK.md

---

## 什麼時候該跑這個

| 客戶數量 | 該做什麼 |
|-------------|-----------|
| 1 | 不要重構。只要把界線記錄下來（FORK.md），讓自己知道界線在哪。 |
| 2 | 跑 audit。修掉高嚴重度的違規。開始用設定合併模式。 |
| 3+ | 完整 refactor 模式。界線一定要乾淨，因為你現在已經有證據知道哪些東西會變。 |

**這套紀律的第 5 條規則**：沒有第 3 個客戶之前不要抽象化。只有 1 個客戶時你是在猜，2 個時你是在比對模式，3 個以上你才真的知道什麼會變。

## 小提醒

- 在加新客戶「之前」跑，不要等加完才跑
- 設定合併是投資報酬率最高的重構，先做這個
- 就算只有一個客戶，feature flag 也比 `if (client)` 好。*「這個大致一樣，只是……」* 就是 feature flag，不是 fork。
- FORK.md 是寫給團隊看的，不只是給 Claude，所以要寫成人會想讀的樣子
