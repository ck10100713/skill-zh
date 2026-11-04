---
name: nextjs-app-router-patterns
description: 精通 Next.js 14+ App Router，涵蓋 Server Components、streaming、parallel routes 與進階資料抓取。在建構 Next.js 應用、實作 SSR/SSG 或優化 React Server Components 時使用。
---

# Next.js App Router Patterns

Next.js 14+ App Router 架構、Server Components 與現代全端 React 開發的完整模式。

## When to Use This Skill

- 用 App Router 建構新的 Next.js 應用
- 從 Pages Router 遷移到 App Router
- 實作 Server Components 與 streaming
- 設定 parallel route 與 intercepting route
- 優化資料抓取與快取
- 用 Server Actions 建構全端功能

## Core Concepts

### 1. Rendering Modes

| Mode                  | Where        | When to Use                               |
| --------------------- | ------------ | ----------------------------------------- |
| **Server Components** | 只在伺服器  | 資料抓取、大量運算、機密資料 |
| **Client Components** | 瀏覽器      | 互動、hook、瀏覽器 API        |
| **Static**            | 建置時   | 很少變動的內容               |
| **Dynamic**           | 請求時 | 個人化或即時資料            |
| **Streaming**         | 漸進式  | 大型頁面、緩慢的資料來源            |

### 2. File Conventions

```
app/
├── layout.tsx       # Shared UI wrapper
├── page.tsx         # Route UI
├── loading.tsx      # Loading UI (Suspense)
├── error.tsx        # Error boundary
├── not-found.tsx    # 404 UI
├── route.ts         # API endpoint
├── template.tsx     # Re-mounted layout
├── default.tsx      # Parallel route fallback
└── opengraph-image.tsx  # OG image generation
```

## Quick Start

```typescript
// app/layout.tsx
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: { default: 'My App', template: '%s | My App' },
  description: 'Built with Next.js App Router',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

// app/page.tsx - Server Component by default
async function getProducts() {
  const res = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 }, // ISR: revalidate every hour
  })
  return res.json()
}

export default async function HomePage() {
  const products = await getProducts()

  return (
    <main>
      <h1>Products</h1>
      <ProductGrid products={products} />
    </main>
  )
}
```

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Best Practices

### Do's

- **從 Server Components 開始** - 只在需要時才加 'use client'
- **資料抓取放在用到的地方** - 在使用資料的地方抓資料
- **使用 Suspense boundary** - 讓慢速資料也能 streaming
- **善用 parallel routes** - 各自獨立的載入狀態
- **使用 Server Actions** - 處理 mutation，並支援漸進式增強

### Don'ts

- **不要傳遞可序列化的資料** - Server → Client 邊界有限制
- **不要在 Server Components 裡用 hook** - 不能用 useState、useEffect
- **不要在 Client Components 裡抓資料** - 用 Server Components 或 React Query
- **不要把 layout 巢狀得太深** - 每個 layout 都會增加元件樹
- **不要忽略載入狀態** - 一律提供 loading.tsx 或 Suspense
