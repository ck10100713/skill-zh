---
name: vite-patterns
description: Vite 建置工具的各種模式，包含設定、plugin、HMR、環境變數、proxy 設定、SSR、library mode、相依套件預先打包（pre-bundling）和建置最佳化。處理 vite.config.ts、Vite plugin 或以 Vite 為基礎的專案時啟用。
metadata:
  origin: ECC
---

# Vite Patterns

Vite 8+ 專案的建置工具與 dev server 模式。涵蓋設定、環境變數、proxy 設定、library mode、相依套件預先打包，以及常見的 production 陷阱。

## 何時使用

- 設定 `vite.config.ts` 或 `vite.config.js`
- 設定環境變數或 `.env` 檔案
- 為 API 後端設定 dev server proxy
- 最佳化建置輸出（chunk、minification、asset）
- 用 `build.lib` 發佈函式庫
- 排查相依套件預先打包或 CJS/ESM 互通問題
- 除錯 HMR、dev server 或建置錯誤
- 選擇 Vite plugin 或決定它們的順序

## 運作方式

- **Dev 模式**把原始碼當成原生 ESM 提供，不做打包。轉換是依每個 module 請求按需進行，所以冷啟動快、HMR 也精準。
- **Build 模式**用 Rolldown（v7+）或 Rollup（v5–v6）把 app 打包成 production 版本，包含 tree-shaking、code-splitting 和以 Oxc 為基礎的 minification。
- **相依套件預先打包**會用 esbuild 一次性把 CJS/UMD 的相依套件轉成 ESM，結果快取在 `node_modules/.vite` 底下，之後啟動就省掉這個工作。
- **Plugin** 在 dev 和 build 之間共用同一個介面，同一個 plugin 物件既能用在 dev server 的按需轉換，也能用在 production 流程。
- **環境變數**在建置時被靜態內嵌。有 `VITE_` 前綴的變數會變成 bundle 裡的公開常數；沒有前綴的，client 端程式碼完全看不到。

## 範例

### 設定結構

#### 基本設定

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': new URL('./src', import.meta.url).pathname },
  },
})
```

#### 條件式設定

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd())   // 只載入 VITE_ 前綴的（安全）

  return {
    plugins: [react()],
    server: command === 'serve' ? { port: 3000 } : undefined,
    define: {
      __API_URL__: JSON.stringify(env.VITE_API_URL),
    },
  }
})
```

#### 主要設定選項

| Key | 預設值 | 說明 |
|-----|---------|-------------|
| `root` | `'.'` | 專案根目錄（`index.html` 所在的位置） |
| `base` | `'/'` | 部署後 asset 的公開 base path |
| `envPrefix` | `'VITE_'` | 會暴露給 client 的環境變數前綴 |
| `build.outDir` | `'dist'` | 輸出目錄 |
| `build.minify` | `'oxc'` | Minifier（`'oxc'`、`'terser'` 或 `false`） |
| `build.sourcemap` | `false` | `true`、`'inline'` 或 `'hidden'` |

### Plugins

#### 必備 Plugin

大部分 plugin 需求都有幾個維護良好的套件可以涵蓋。自己寫之前先看看這些。

| Plugin | 用途 | 何時使用 |
|--------|---------|-------------|
| `@vitejs/plugin-react-swc` | 透過 SWC 提供 React HMR + Fast Refresh | React app 的預設選擇（比 Babel 版快） |
| `@vitejs/plugin-react` | 透過 Babel 提供 React HMR + Fast Refresh | 只有需要 Babel plugin（emotion、MobX decorator）時才用 |
| `@vitejs/plugin-vue` | Vue 3 SFC 支援 | Vue app |
| `vite-plugin-checker` | 在 worker thread 跑 `tsc` + ESLint，並附 HMR overlay | **任何 TypeScript app**，因為 `vite build` 期間 Vite 不會做型別檢查 |
| `vite-tsconfig-paths` | 遵循 `tsconfig.json` 的 `paths` alias | 只要 `tsconfig.json` 裡已經有 alias 就用 |
| `vite-plugin-dts` | 在 library mode 輸出 `.d.ts` 檔 | 發佈 TypeScript 函式庫 |
| `vite-plugin-svgr` | 把 SVG 當成 React component 匯入 | 把 SVG 當 component 用的 React app |
| `rollup-plugin-visualizer` | Bundle treemap/sunburst 報告 | 定期稽核 bundle 大小（用 `enforce: 'post'`） |
| `vite-plugin-pwa` | 零設定 PWA + Workbox | 要支援離線的 app |

**重要提醒：**`vite build` 只轉譯，**不會**做型別檢查。除非加上 `vite-plugin-checker` 或在 CI 跑 `tsc --noEmit`，否則型別錯誤會悄悄上到 production。

#### 撰寫自訂 Plugin

很少需要自己寫，大部分需求現成的 plugin 就能涵蓋。真的需要時，先直接寫在 `vite.config.ts` 裡，有被重複使用再抽出去。

```typescript
// vite.config.ts — 最小的 inline plugin
function myPlugin(): Plugin {
  return {
    name: 'my-plugin',                       // 必填，必須唯一
    enforce: 'pre',                           // 'pre' | 'post'（選填）
    apply: 'build',                           // 'build' | 'serve'（選填）
    transform(code, id) {
      if (!id.endsWith('.custom')) return
      return { code: transformCustom(code), map: null }
    },
  }
}
```

**主要 hook：**`transform`（修改原始碼）、`resolveId` + `load`（virtual module）、`transformIndexHtml`（注入 HTML）、`configureServer`（加入 dev middleware）、`hotUpdate`（自訂 HMR，在 v7+ 取代已棄用的 `handleHotUpdate`）。

**Virtual module** 用 `\0` 前綴慣例：`resolveId` 回傳 `'\0virtual:my-id'`，其他 plugin 看到就會跳過。使用者程式碼則是 import `'virtual:my-id'`。

完整的 plugin API 請看 [vite.dev/guide/api-plugin](https://vite.dev/guide/api-plugin)。開發時可以用 `vite-plugin-inspect` 來除錯轉換流程。

### HMR API

框架 plugin（`@vitejs/plugin-react`、`@vitejs/plugin-vue` 等）會自動處理 HMR。只有在做自訂的狀態 store、開發工具，或需要在更新之間保留狀態的框架無關工具函式時，才直接用 `import.meta.hot`。

```typescript
// src/store.ts — 為純 JS module 手動處理 HMR
if (import.meta.hot) {
  // 在更新之間保留狀態（必須修改 .data 的內容，絕對不能重新指派 .data）
  import.meta.hot.data.count = import.meta.hot.data.count ?? 0

  // 在 module 被取代之前清理副作用
  import.meta.hot.dispose((data) => clearInterval(data.intervalId))

  // 接受這個 module 自己的更新
  import.meta.hot.accept()
}
```

所有 `import.meta.hot` 的程式碼都會在 production build 被 tree-shake 掉，不需要自己拿掉 guard。

### 環境變數

Vite 依序載入 `.env`、`.env.local`、`.env.[mode]` 和 `.env.[mode].local`（後面的覆蓋前面的）；`*.local` 檔案會被 gitignore，用來放本機的 secret。

#### Client 端存取

只有 `VITE_` 前綴的變數會暴露給 client 端程式碼：

```typescript
import.meta.env.VITE_API_URL   // string
import.meta.env.MODE            // 'development' | 'production' | 自訂
import.meta.env.BASE_URL        // base 設定值
import.meta.env.DEV             // boolean
import.meta.env.PROD            // boolean
import.meta.env.SSR             // boolean
```

#### 在設定檔中使用環境變數

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())          // 只載入 VITE_ 前綴的（安全）
  return {
    define: {
      __API_URL__: JSON.stringify(env.VITE_API_URL),
    },
  }
})
```

### 安全性

#### `VITE_` 前綴**不是**安全邊界

任何有 `VITE_` 前綴的變數，都會在建置時被**靜態內嵌進 client bundle**。minification、base64 編碼、關掉 source map 都藏不住它。有心的攻擊者可以從出貨的 JavaScript 裡抽出任何 `VITE_` 變數。

**規則：**只有公開的值（API URL、feature flag、公開金鑰）才能放進 `VITE_` 變數。Secret（API token、資料庫 URL、私鑰）**一定要**留在 server 端，放在 API 或 serverless function 後面。

#### `loadEnv('')` 的陷阱

```typescript
// 錯誤：第三個參數傳 '' 會載入「所有」環境變數（包含 server 的 secret），
// 還讓它們能透過 `define` 被內嵌進 client 端程式碼。
const env = loadEnv(mode, process.cwd(), '')

// 正確：明確列出前綴
const env = loadEnv(mode, process.cwd(), ['VITE_', 'APP_'])
```

#### Production 的 Source Map

Production 的 source map 會洩漏你的原始碼。除非你要上傳到錯誤追蹤服務（Sentry、Bugsnag），而且之後會在本機刪掉，不然就關掉：

```typescript
build: {
  sourcemap: false,                                  // 預設值，維持這樣
}
```

#### `.gitignore` 檢查清單

- `.env.local`、`.env.*.local`：本機的 secret 覆蓋檔
- `dist/`：建置輸出
- `node_modules/.vite`：預先打包的快取（過期的項目會造成莫名其妙的錯誤）

### Server Proxy

```typescript
// vite.config.ts — server.proxy
server: {
  proxy: {
    '/foo': 'http://localhost:4567',                    // 字串簡寫

    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,                               // 後端是 virtual host 時需要
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

要 proxy WebSocket 的話，在該路由設定加上 `ws: true`。

### 建置最佳化

#### Manual Chunks

```typescript
// vite.config.ts — build.rolldownOptions
build: {
  rolldownOptions: {
    output: {
      // 物件寫法：把特定套件分成一組
      manualChunks: {
        'react-vendor': ['react', 'react-dom'],
        'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-popover'],
      },
    },
  },
}
```

```typescript
// 函式寫法：用啟發式規則來切分
manualChunks(id) {
  if (id.includes('node_modules/react')) return 'react-vendor'
  if (id.includes('node_modules')) return 'vendor'
}
```

### 效能

#### 避免 Barrel File

Barrel file（用 `index.ts` 把整個目錄的東西全部 re-export）會讓 Vite 即使只 import 一個 symbol，也得載入每個被 re-export 的檔案。這是官方文件點名的第一大 dev server 拖慢原因。

```typescript
// 錯誤：只 import 一個 util，卻逼 Vite 載入整個 barrel
import { slash } from '@/utils'

// 正確：直接 import，只會載入那一個檔案
import { slash } from '@/utils/slash'
```

#### Import 時明確寫出副檔名

每個省略的副檔名，最多會透過 `resolve.extensions` 觸發 6 次檔案系統檢查。在大型 codebase 裡，這會累積起來。

```typescript
// 錯誤
import Component from './Component'

// 正確
import Component from './Component.tsx'
```

把 `tsconfig.json` 的 `allowImportingTsExtensions` 和 `resolve.extensions` 縮小到只留你真正會用到的副檔名。

#### 預先熱身熱門路徑的路由

`server.warmup.clientFiles` 會在瀏覽器請求之前，先預轉換已知的熱門進入點，消除大型 app 冷載入時的請求瀑布。

```typescript
// vite.config.ts
server: {
  warmup: {
    clientFiles: ['./src/main.tsx', './src/routes/**/*.tsx'],
  },
}
```

#### 分析很慢的 Dev Server

覺得 `vite dev` 很慢時，先用 `vite --profile`，操作一下 app，然後按 `p+enter` 存成 `.cpuprofile`。把它載入 [Speedscope](https://www.speedscope.app)，找出哪些 plugin 在吃時間，通常是社群 plugin 裡的 `buildStart`、`config` 或 `configResolved` hook。

### Library Mode

發佈 npm 套件時用 `build.lib`。比起設定細節，有兩個地雷更重要：

1. **不會輸出型別**：要加 `vite-plugin-dts`，或另外跑 `tsc --emitDeclarationOnly`。
2. **Peer dependency 一定要 externalize**：沒列出來的 peer 會被打包進你的函式庫，讓使用端出現 runtime 重複的錯誤。

```typescript
// vite.config.ts
build: {
  lib: {
    entry: 'src/index.ts',
    formats: ['es', 'cjs'],
    fileName: (format) => `my-lib.${format}.js`,
  },
  rolldownOptions: {
    external: ['react', 'react-dom', 'react/jsx-runtime'],  // 每一個 peer dep
  },
}
```

### SSR Externals

單純用 `createServer({ middlewareMode: true })` 的做法是框架作者的領域。大部分 app 應該改用 Nuxt、Remix、SvelteKit、Astro 或 TanStack Start。身為框架使用者，你*真的*會去調的，是相依套件在 SSR 壞掉時的 externals 設定：

```typescript
// vite.config.ts — ssr 選項
ssr: {
  external: ['node-native-package'],           // 在 SSR bundle 裡保留成 require()
  noExternal: ['esm-only-package'],            // 強制打包進 SSR 輸出（能修好大部分 SSR 錯誤）
  target: 'node',                              // 'node' 或 'webworker'
}
```

### 相依套件預先打包

Vite 會預先打包相依套件，把 CJS/UMD 轉成 ESM，並減少請求數量。

```typescript
// vite.config.ts — optimizeDeps
optimizeDeps: {
  include: [
    'lodash-es',                              // 強制預先打包已知很大的相依套件
    'cjs-package',                            // 會造成互通問題的 CJS 相依套件
    'deep-lib/components/**',                 // 深層 import 用的 glob
  ],
  exclude: ['local-esm-package'],             // 被排除的話必須是合法的 ESM
  force: true,                                // 忽略快取、重新最佳化（只在暫時除錯時用）
}
```

### 常見陷阱

#### Dev 跟 Build 不一致

Dev 用 esbuild/Rolldown 做轉換；build 用 Rolldown 做打包。CJS 函式庫在兩者之間可能表現不同。部署前一定要用 `vite build && vite preview` 驗證。

#### 部署後的過期 Chunk

新的 build 會產生新的 chunk hash。還在使用中的 session 會請求已經不存在的舊檔名。Vite 沒有內建解法。緩解方式：

- 在一段部署期間內，讓舊的 `dist/assets/` 檔案繼續保留
- 在 router 裡捕捉 dynamic import 的錯誤，並強制重新整理頁面

#### Docker 與容器

Vite 預設綁定 `localhost`，從容器外面連不到：

```typescript
// vite.config.ts — Docker/容器設定
server: {
  host: true,                                  // 綁定 0.0.0.0
  hmr: { clientPort: 3000 },                   // 如果前面有 reverse proxy
}
```

#### Monorepo 的檔案存取

Vite 把檔案服務限制在專案根目錄內。根目錄以外的套件會被擋掉：

```typescript
// vite.config.ts — monorepo 檔案存取
server: {
  fs: {
    allow: ['..'],                             // 允許上層目錄（workspace 根目錄）
  },
}
```

### 反模式

```typescript
// 錯誤：把 envPrefix 設成 '' 會把「所有」環境變數（包含 secret）暴露給 client
envPrefix: ''

// 錯誤：以為應用程式原始碼裡 require() 能用，Vite 是 ESM 優先
const lib = require('some-lib')                // 改用 import

// 錯誤：把每個 node_module 都切成自己的 chunk，會產生數百個小檔案
manualChunks(id) {
  if (id.includes('node_modules')) {
    return id.split('node_modules/')[1].split('/')[0]   // 每個套件一個 chunk
  }
}

// 錯誤：library mode 沒有 externalize peer dep，會造成 runtime 重複的錯誤
// build.lib 但沒有 rolldownOptions.external

// 錯誤：使用已棄用的 esbuild minifier
build: { minify: 'esbuild' }                  // 改用 'oxc'（預設）或 'terser'

// 錯誤：用重新指派的方式修改 import.meta.hot.data
import.meta.hot.data = { count: 0 }           // 錯誤：必須修改屬性，不能重新指派
import.meta.hot.data.count = 0                 // 正確
```

**流程上的反模式：**

- **`vite preview` 不是 production server**：它只是對建置後的 bundle 做 smoke test。要把 `dist/` 部署到真正的靜態主機（NGINX、Cloudflare Pages、Vercel static），或用 multi-stage Dockerfile。
- **期待 `vite build` 做型別檢查**：它只轉譯。型別錯誤會悄悄上到 production。加上 `vite-plugin-checker` 或在 CI 跑 `tsc --noEmit`。
- **預設就出貨 `@vitejs/plugin-legacy`**：它會讓 bundle 膨脹約 40%、弄壞依賴 source map 的 bundle 分析工具，而且對 95% 以上使用現代瀏覽器的使用者來說根本不需要。要根據真實的分析數據決定，不要憑假設。
- **手寫 30 個以上的 `resolve.alias`，跟 `tsconfig.json` 的 paths 重複**：改用 `vite-tsconfig-paths`。Excalidraw 和 PostHog 都有這種情況，新專案要避免。
- **相依套件改動後留著過期的 `node_modules/.vite`**：預先打包的快取會造成莫名其妙的錯誤。切換 branch 或 patch 相依套件之後要清掉。

## 快速參考

| 模式 | 何時使用 |
|---------|-------------|
| `defineConfig` | 一律使用，提供型別推論 |
| `loadEnv(mode, root, ['VITE_'])` | 在設定檔中存取環境變數（明確指定前綴） |
| `vite-plugin-checker` | 任何 TypeScript app（補上型別檢查的缺口） |
| `vite-tsconfig-paths` | 取代手寫的 `resolve.alias` |
| `optimizeDeps.include` | 造成互通問題的 CJS 相依套件 |
| `server.proxy` | 在 dev 時把 API 請求導到後端 |
| `server.host: true` | Docker、容器、遠端存取 |
| `server.warmup.clientFiles` | 預先轉換熱門路徑的路由 |
| `build.lib` + `external` | 發佈 npm 套件 |
| `manualChunks`（物件） | 切分 vendor bundle |
| `vite --profile` | 除錯很慢的 dev server |
| `vite build && vite preview` | 在本機對 production bundle 做 smoke test（不是 production server） |

## 相關 Skill

- `frontend-patterns`：React component 模式
- `docker-patterns`：用 Vite 做容器化開發
- `nextjs-turbopack`：Next.js 的替代 bundler
