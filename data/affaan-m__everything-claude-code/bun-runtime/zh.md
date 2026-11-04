---
name: bun-runtime
description: Bun 當作 runtime、套件管理器、bundler 和測試執行器。什麼時候選 Bun、什麼時候選 Node、migration 注意事項，以及 Vercel 支援。
metadata:
  origin: ECC
---

# Bun Runtime

Bun 是一個快速的一站式 JavaScript runtime 與工具組：runtime、套件管理器、bundler 和測試執行器。

## When to Use

- **選 Bun** 的情況：新的 JS/TS 專案、安裝/執行速度很重要的 script、使用 Bun runtime 的 Vercel 部署，以及想用單一工具鏈（執行 + 安裝 + 測試 + build）的時候。
- **選 Node** 的情況：要最大的生態系相容性、舊工具鏈預設是 Node，或是某個依賴已知跟 Bun 有問題。

適用時機：導入 Bun、從 Node migration、撰寫或除錯 Bun script/測試，或是在 Vercel 或其他平台上設定 Bun。

## How It Works

- **版本基準**：下面的指引以 Bun 1.4.x 為目標。依賴 flag 名稱之前，先用 `bun --version` 確認實際版本，因為 CLI flag 在不同版本之間可能會變。
- **Runtime**：可直接取代 Node 的相容 runtime，建構在 JavaScriptCore 上。從 Bun 1.4 開始，runtime 本身改用 Rust 實作（從 Zig migration 過來）。並非 100% 相容 Node，有些原生 addon、較少用的 `node:` 內部 API，以及依賴 Node 特有內部機制的套件仍可能失敗，在 production 依賴它之前先驗證。
- **套件管理器**：Bun 內建套件管理器；安裝效能取決於專案、網路狀況和 cache 狀態。目前的 Bun 預設 lockfile 是 `bun.lock`（文字檔）；舊版用 `bun.lockb`（二進位），Bun 為了 migration 仍然讀得了那種格式，但新專案應該用 `bun.lock`。
- **Bundler**：內建的 bundler 和 transpiler，可用於應用程式和函式庫。
- **測試執行器**：內建的 `bun test`，API 類似 Jest。

**從 Node migration**：把 `node script.js` 換成 `bun run script.js` 或 `bun script.js`。用 `bun install` 取代 `npm install`，大部分套件都能用。npm script 用 `bun run`；一次性執行的 npx 風格用 `bun x`。Node 內建模組都有支援；有 Bun API 的地方優先用 Bun API，效能比較好。

**套件與 workspace 指令**：`bun add <pkg>` / `bun remove <pkg>` / `bun update [pkg]` 管理依賴；`bun outdated` 列出過期的依賴。`bun pm ls` 用 lockfile 列出專案的依賴和解析後的版本；加 `--all` 會包含間接依賴。它不是對已安裝檔案內容做完整性檢查。[`bun audit`](https://bun.com/docs/pm/cli/audit) 用 `bun.lock` 裡的套件名稱和版本去查 registry 的安全公告；它不會修改 `package.json`、`bun.lock` 或 `node_modules`。送出私有套件的 metadata 之前，先檢查已核准的目的地。scoped registry 沒有 advisory endpoint 的套件會被略過，不影響 exit code。`bun audit fix` 會升級並安裝依賴，改動 lockfile 和已安裝的套件，有時還會改直接依賴的版本釘選，要把它當成會修改內容的安裝操作來審查，包括適用的生命週期 script。`bun dedupe` 會合併重複的安裝，`bun prune` 會移除不再被引用的套件。Monorepo 在 `package.json` 用根層的 `workspaces` 陣列（跟 npm/yarn 同一個慣例）；要在單一 workspace 裡跑 script，用 `bun run --filter <pkg-name> <script>`。

**內建 API**：加依賴之前先看這些：`Bun.file` / `Bun.write` 做檔案 I/O、`bun:sqlite` 提供內嵌 SQLite 資料庫、`Bun.serve` 做 HTTP/WebSocket 伺服器、[`Bun.sql`](https://bun.com/docs/runtime/sql) 連 SQL 資料庫、[`Bun.redis`](https://bun.com/docs/runtime/redis) 連 Redis，以及 [`Bun.S3Client`](https://bun.com/docs/runtime/s3) 存取 S3 相容的物件儲存。其餘新功能請看 [1.4 release notes](https://bun.com/blog/bun-v1.4)。

**Vercel**：在 `vercel.json` 設定 `bunVersion: "1.4.x"` 就能用 Bun 1.4（Rust runtime）。參考 [Vercel 的 Bun runtime 文件](https://vercel.com/docs/functions/runtimes/bun)。Build：`bun run build` 或 `bun build ./src/index.ts --outdir=dist`。安裝：用 `bun install --frozen-lockfile` 讓部署可重現。

**參考資料**：[Bun 1.4 release notes](https://bun.com/blog/bun-v1.4)。

## Examples

### Run and install

```bash
# Install dependencies (creates/updates bun.lock)
bun install

# Run a script or file
bun run dev
bun run src/index.ts
bun src/index.ts
```

### Scripts and env

```bash
bun run --env-file=.env dev
FOO=bar bun run script.ts
```

### Testing

```bash
bun test
bun test --watch
```

在 Bun 1.4 上跑 CI，可用的選項包括：`bun test --changed[=<ref>]` 只跑受影響的測試、`bun test --isolate` 讓每個檔案有自己的全域環境、`bun test --parallel[=<n>]` 用 worker process 平行跑、`bun test --shard=<n>/<count>` 做 CI 分片。`--isolate` 會在同一個 process 裡為每個檔案建立全新的 JavaScript global，並清掉文件上記載的各檔案資源；它不是 process 或安全沙箱。`--parallel` 預設會啟用它。`--timings=<file>` 讀取先前的執行時間來排程；`--update-timings` 會記錄執行時間。範例：`bun test --parallel --timings=./test-timings.json --update-timings`。多分片的工作流程要選 timing 檔案路徑之前，先查所裝版本的 help 和文件。

```typescript
// test/example.test.ts
import { expect, test } from "bun:test";

test("add", () => {
  expect(1 + 2).toBe(3);
});
```

### Runtime API

```typescript
const file = Bun.file("package.json");
const json = await file.json();

Bun.serve({
  port: 3000,
  fetch(req) {
    return new Response("Hello");
  },
});
```

## Best Practices

- 把 lockfile（`bun.lock`）commit 進去，讓安裝可重現。
- script 優先用 `bun run`。TypeScript 的話，Bun 原生就能跑 `.ts`。
- 依賴要保持更新，Bun 和生態系演進很快。
