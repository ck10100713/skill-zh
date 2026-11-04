---
name: nuxt4-patterns
description: Nuxt 4 應用的模式，涵蓋 hydration 安全、效能、route rules、延遲載入，以及用 useFetch 和 useAsyncData 做 SSR 安全的資料取得。建置或審查 Nuxt 4 應用，或除錯 hydration 不一致和 SSR 安全的資料取得時使用。
metadata:
  origin: ECC
---

# Nuxt 4 Patterns

建置或除錯使用 SSR、混合 rendering、route rules 或頁面層級資料取得的 Nuxt 4 應用時使用。

## When to Activate

- 伺服器 HTML 和 client 狀態之間的 hydration 不一致
- 路由層級的 rendering 決策，例如 prerender、SWR、ISR 或 client-only 區塊
- 圍繞延遲載入、延遲 hydration 或 payload 大小的效能工作
- 用 `useFetch`、`useAsyncData` 或 `$fetch` 取得頁面或元件的資料
- 和路由參數、middleware 或 SSR/client 差異有關的 Nuxt 路由問題

## Hydration Safety

- 讓第一次 render 保持確定性。不要把 `Date.now()`、`Math.random()`、只有瀏覽器才有的 API，或 storage 的讀取，直接放進 SSR 渲染的樣板狀態裡。
- 伺服器產生不出同樣的 markup 時，把只有瀏覽器才會跑的邏輯放到 `onMounted()`、`import.meta.client`、`ClientOnly` 或 `.client.vue` 元件後面。
- 用 Nuxt 的 `useRoute()` composable，不要用 `vue-router` 的那個。
- 不要用 `route.fullPath` 來驅動 SSR 渲染的 markup。URL 的 fragment 只存在於 client，會造成 hydration 不一致。
- 把 `ssr: false` 當成真正只有瀏覽器才有的區域的逃生口，不要當成不一致的預設解法。

## Data Fetching

- 在頁面和元件裡做 SSR 安全的 API 讀取，偏好用 `await useFetch()`。它會把伺服器取得的資料轉進 Nuxt 的 payload，避免 hydration 時再取一次。
- 當 fetcher 不是單純的 `$fetch()` 呼叫、需要自訂 key，或要組合多個非同步來源時，用 `useAsyncData()`。
- 給 `useAsyncData()` 一個穩定的 key，才能重用快取，refresh 的行為也才可預期。
- 讓 `useAsyncData()` 的 handler 沒有副作用。它們可能在 SSR 和 hydration 期間執行。
- 使用者觸發的寫入或只在 client 的動作，用 `$fetch()`，不要用在應該從 SSR hydrate 的頂層頁面資料上。
- 不重要、不該擋住導覽的資料，用 `lazy: true`、`useLazyFetch()` 或 `useLazyAsyncData()`。在 UI 裡要處理 `status === 'pending'`。
- 只有對 SEO 或首次繪製不需要的資料，才用 `server: false`。
- 用 `pick` 精簡 payload 大小，不需要深層響應性時，偏好比較淺的 payload。

```ts
const route = useRoute()

const { data: article, status, error, refresh } = await useAsyncData(
  () => `article:${route.params.slug}`,
  () => $fetch(`/api/articles/${route.params.slug}`),
)

const { data: comments } = await useFetch(`/api/articles/${route.params.slug}/comments`, {
  lazy: true,
  server: false,
})
```

## Route Rules

rendering 和快取策略，偏好在 `nuxt.config.ts` 裡用 `routeRules`：

```ts
export default defineNuxtConfig({
  routeRules: {
    '/': { prerender: true },
    '/products/**': { swr: 3600 },
    '/blog/**': { isr: true },
    '/admin/**': { ssr: false },
    '/api/**': { cache: { maxAge: 60 * 60 } },
  },
})
```

- `prerender`：建置時產生靜態 HTML
- `swr`：提供快取的內容，並在背景重新驗證
- `isr`：在支援的平台上做增量靜態再生
- `ssr: false`：由 client 渲染的路由
- `cache` 或 `redirect`：Nitro 層級的回應行為

route rules 要依路由群組挑，不要全域套用。行銷頁面、商品目錄、儀表板和 API 通常需要不同的策略。

## Lazy Loading and Performance

- Nuxt 已經依路由對頁面做 code-split。在微調元件的切分之前，先讓路由邊界有意義。
- 用 `Lazy` 前綴動態 import 不重要的元件。
- 用 `v-if` 有條件地渲染延遲元件，這樣在 UI 真的需要之前，不會載入那個 chunk。
- 對首屏以下或不重要的互動式 UI，用延遲 hydration。

```vue
<template>
  <LazyRecommendations v-if="showRecommendations" />
  <LazyProductGallery hydrate-on-visible />
</template>
```

- 要自訂策略，用 `defineLazyHydrationComponent()` 搭配 visibility 或 idle 策略。
- Nuxt 的延遲 hydration 作用在單一檔案元件上。傳新的 props 給延遲 hydrate 的元件，會立刻觸發 hydration。
- 內部導覽用 `NuxtLink`，這樣 Nuxt 才能預先載入路由元件和產生出來的 payload。

## Review Checklist

- 第一次 SSR render 和 hydrate 後的 client render 產生相同的 markup
- 頁面資料用 `useFetch` 或 `useAsyncData`，不是頂層的 `$fetch`
- 不重要的資料是延遲載入的，而且有明確的載入 UI
- route rules 符合頁面對 SEO 和新鮮度的要求
- 很重的互動式 island 是延遲載入或延遲 hydrate 的
