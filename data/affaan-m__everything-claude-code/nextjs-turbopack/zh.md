---
name: nextjs-turbopack
description: Next.js 16+ 與 Turbopack 的指引：增量式 Rust 打包、檔案系統快取、更快的 dev 啟動和 HMR、Turbopack 對 webpack 的取捨，以及 middleware.ts 改名為 proxy.ts 的檔名變更。開發或除錯 Next.js 16+ 應用、診斷 dev 啟動或熱更新太慢、在打包工具之間做選擇，或審查 middleware/proxy 檔案命名時使用。
metadata:
  origin: ECC
---

# Next.js and Turbopack

Next.js 16+ 在本機開發時預設使用 Turbopack：一個用 Rust 寫的增量式打包工具，大幅加快 dev 啟動和熱更新。

## When to Use

- **Turbopack（預設的 dev）**：日常開發用。冷啟動和 HMR 更快，在大型應用上尤其明顯。
- **Webpack（舊版 dev）**：只有在碰到 Turbopack 的 bug，或 dev 時依賴只有 webpack 才有的 plugin 時才用。用 `--webpack` 停用 Turbopack（依你的 Next.js 版本也可能是 `--no-turbopack`；請查你那個版本的文件）。
- **正式環境**：正式環境的建置行為（`next build`）依 Next.js 版本，可能用 Turbopack 或 webpack；請查你那個版本的官方 Next.js 文件。

使用時機：開發或除錯 Next.js 16+ 應用、診斷 dev 啟動或 HMR 太慢，或最佳化正式環境的 bundle。

## How It Works

- **Turbopack**：Next.js dev 用的增量式打包工具。使用檔案系統快取，重啟快很多（例如在大型專案上快 5 到 14 倍）。
- **dev 的預設值**：從 Next.js 16 開始，除非停用，否則 `next dev` 會用 Turbopack 執行。
- **檔案系統快取**：重啟時重用先前的工作；快取通常在 `.next` 底下；基本使用不需要額外設定。
- **Bundle Analyzer（Next.js 16.1+）**：實驗性的 Bundle Analyzer，用來檢查輸出並找出很重的相依；透過設定或實驗性旗標啟用（請查你那個版本的 Next.js 文件）。

## Examples

### Commands

```bash
next dev
next build
next start
```

### Usage

用 `next dev` 搭配 Turbopack 做本機開發。用 Bundle Analyzer（見 Next.js 文件）來最佳化 code-splitting 並削減很大的相依。盡量偏好 App Router 和 server component。

## Middleware File Naming

Next.js 16 引入 `proxy.ts` 作為 middleware 的檔名，取代舊的 `middleware.ts` 慣例：

- **Next.js 16+**：在專案根目錄用 `proxy.ts`
- **Next.js 16 之前**：在專案根目錄用 `middleware.ts`

檔名的變更和 **Next.js 版本**有關，和用哪個打包工具（Turbopack 還是 webpack）無關。一定要查你正在審查的那個版本的官方文件。

**不要在 Next.js 16 專案裡，把 `proxy.ts` 標成命名錯誤或遺失的 middleware 檔案。** 那個檔案是正確而且刻意這樣取的。建議改名成 `middleware.ts` 會讓 middleware 無法執行。

參考：[Next.js proxy 文件](https://nextjs.org/docs/app/getting-started/proxy)

## Best Practices

- 維持在較新的 Next.js 16.x，才能有穩定的 Turbopack 和快取行為。
- 如果 dev 很慢，確認你用的是 Turbopack（預設），而且快取沒有被不必要地清掉。
- 正式環境的 bundle 大小有問題時，用你那個版本的官方 Next.js bundle 分析工具。
