---
name: motion-foundations
description: 使用 motion/react 的 React / Next.js 的 motion token、spring 預設、效能規則、裝置適配、無障礙強制規範和 SSR 安全。基礎層，其他所有 motion skill 都依賴它。在 React 或 Next.js 裡設置 motion token、spring 預設、reduced-motion 處理或 SSR 安全的動畫時使用。
tags: [motion, animation, performance, accessibility]
category: frontend
author: jeff
metadata:
  version: 1.0.0
---

# Motion Foundations

動態系統的底層。定義下游 skill（`motion-patterns`、`motion-advanced`）會繼承的
每個值、限制和規則。
開始任何動畫工作之前，先載入這個 skill。

## When to Activate

- 從零開始做任何有動畫的元件
- 設置 token、spring 預設或 easing 值
- 實作 `prefers-reduced-motion` 支援
- 除錯動畫初始狀態造成的 hydration 不一致
- 評估某個動畫到底該不該存在

## Outputs

這個 skill 會產出：

- 共用的 `motionTokens` 物件（duration、easing、distance、scale）
- 共用的 `springs` 預設對照表（5 個具名設定）
- 所有元件都使用的 `shouldAnimate()` 關卡
- 透過 `useReducedMotion` 達成、符合無障礙規範的動畫預設值
- 零 hydration 警告的 SSR 安全初始狀態

## Principles

動態至少要做到下列其中一件事，否則就該移除：

- 引導注意力
- 傳達狀態
- 保持空間連續性

回應速度永遠優先於平滑度。一個 60 fps 卻造成輸入延遲的動畫，
比沒有動畫更糟。

## Rules

這些沒有商量餘地。它們適用於系統裡的每個元件。

1. **只用 `motion/react`。** 絕對不要從 `framer-motion` import。絕對不要在同一棵樹裡混用兩者。
2. **`initial` 必須和伺服器輸出一致。** 如果伺服器渲染的是 `opacity: 1`，`initial` prop 也必須是 `opacity: 1`。沒有例外。
3. **Reduced motion 凌駕一切。** 當 `useReducedMotion()` 回傳 `true`，或 `prefersReduced` 是 `true` 時，所有 transform 都要停用。唯一允許的退路，是 ≤ 0.2 秒、只有 opacity 的淡入淡出。
4. **絕對不要對 layout 屬性做動畫。** `width`、`height`、`top`、`left`、`margin`、`padding` 禁止出現在 `animate` 裡。只能用 `transform` 和 `opacity`。
5. **所有 token 值都來自 `motionTokens`。** 元件檔案裡禁止寫死 duration 和 easing。
6. **所有 spring 設定都來自 `springs` 對照表。** 禁止內嵌 `stiffness`/`damping` 值。
7. **每個 import `motion/react` 的檔案都必須有 `"use client"`。**
8. **絕對不要在模組層級讀 `window` 或 `navigator`。** 一律用 `typeof window !== "undefined"` 防護。

## Decision Guidance

### Choosing a duration

| Token | 使用時機 |
| --------- | -------------------------------------------- |
| `instant` | Tooltip 顯示/隱藏、focus ring、徽章更新 |
| `fast` | 按鈕回饋、圖示切換、chip 切換 |
| `normal` | Modal 開啟、卡片展開、頁面元素進場 |
| `slow` | Hero 進場、整頁轉場 |
| `crawl` | 刻意的敘事感；少用 |

### Choosing a spring

| 預設 | 使用時機 |
| --------- | ------------------------------------------ |
| `snappy` | 預設的 UI：按鈕、chip、導覽項目 |
| `gentle` | 卡片、modal、面板輕柔落下 |
| `bouncy` | 俏皮的時刻：空狀態、onboarding |
| `instant` | Tooltip、popover、下拉選單 |
| `release` | 拖曳放開：自然的物理手感 |

### When to disable animation entirely

下列情況要停用（讓 `shouldAnimate()` 回傳 `false`）：

- `prefersReduced` 是 `true`
- `isLowEnd` 是 `true`，而且動畫不是必要的
- 元素在畫面外，而且永遠不會進入 viewport
- 動畫純粹是裝飾，沒有任何 UX 目的

## Core Concepts

### Token system

```ts
// lib/motion-tokens.ts
export const motionTokens = {
  duration: {
    instant: 0.08,
    fast:    0.18,
    normal:  0.35,
    slow:    0.6,
    crawl:   1.0,
  },
  easing: {
    smooth: [0.22, 1, 0.36, 1],
    sharp:  [0.4, 0, 0.2, 1],
    bounce: [0.34, 1.56, 0.64, 1],
    linear: [0, 0, 1, 1],
  },
  distance: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 48,
  },
  scale: {
    subtle: 0.98,
    press:  0.95,
    pop:    1.04,
  },
}

export const springs = {
  snappy:  { type: "spring", stiffness: 300, damping: 30 },
  gentle:  { type: "spring", stiffness: 120, damping: 14 },
  bouncy:  { type: "spring", stiffness: 400, damping: 10 },
  instant: { type: "spring", stiffness: 600, damping: 35 },
  release: { type: "spring", stiffness: 200, damping: 20, restDelta: 0.001 },
}
```

### Runtime flags

```ts
// lib/motion-config.ts
export const motionConfig = {
  isLowEnd() {
    return (
      typeof navigator !== "undefined" &&
      navigator.hardwareConcurrency <= 4
    )
  },

  prefersReduced() {
    return (
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    )
  },

  shouldAnimate({ essential = false } = {}) {
    if (this.prefersReduced()) return false
    if (!essential && this.isLowEnd()) return false
    return true
  },

  duration() {
    return this.isLowEnd() || this.prefersReduced()
      ? motionTokens.duration.instant
      : motionTokens.duration.normal
  },
}
```

### Accessibility

**優先順序（由高到低）：**

1. `prefers-reduced-motion: reduce`：停用所有 transform，把 opacity 轉場限制在 ≤ 0.2 秒
2. 低階裝置偵測：縮短 duration，移除非必要的動畫
3. 設計偏好：其他所有情況

動態必須平順地降級。它絕不能突然消失，
造成 layout shift 或讓人搞不清方向。

```tsx
// hooks/use-reduced-motion.tsx
"use client"
import { useReducedMotion } from "motion/react"

export function useSafeMotion(fullY: number = 16) {
  const reduce = useReducedMotion()
  return {
    initial: { opacity: 0, y: reduce ? 0 : fullY },
    animate: { opacity: 1, y: 0 },
    exit:    { opacity: 0, y: reduce ? 0 : -fullY },
  }
}
```

```css
/* globals.css */
@media (prefers-reduced-motion: reduce) {
  .motion-safe-transition  { transition: opacity 0.15s; }
  .motion-reduce-transform { transform: none !important; }
}
```

```html
<!-- Tailwind -->
<div class="motion-safe:animate-fade motion-reduce:opacity-100"></div>
```

### SSR / hydration safety

**規則：`initial` 必須永遠和伺服器渲染的內容一致。**

```tsx
// 錯誤：伺服器渲染 opacity:1，但 initial 寫 0，hydration 會不一致
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} />

// 正確：用 AnimatePresence，或等到 client 掛載之後
"use client"
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])

<motion.div
  initial={{ opacity: mounted ? 0 : 1 }}
  animate={{ opacity: 1 }}
/>
```

## Code Examples

### End-to-end: tokens + springs + accessibility + SSR guard

```tsx
// components/fade-in-card.tsx
"use client"

import { useState, useEffect } from "react"
import { motion } from "motion/react"
import { motionTokens, springs } from "@/lib/motion-tokens"
import { useSafeMotion } from "@/hooks/use-reduced-motion"
import { motionConfig } from "@/lib/motion-config"

interface FadeInCardProps {
  children: React.ReactNode
  delay?: number
}

export function FadeInCard({ children, delay = 0 }: FadeInCardProps) {
  // SSR 防護：initial 必須和伺服器輸出一致（opacity: 1）
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])

  // 無障礙：偏好 reduced motion 時停用 transform
  const safeMotion = useSafeMotion(motionTokens.distance.md)

  // 裝置關卡：低階硬體上略過動畫
  if (!motionConfig.shouldAnimate() || !mounted) {
    return <div>{children}</div>
  }

  return (
    <motion.div
      initial={safeMotion.initial}
      animate={safeMotion.animate}
      exit={safeMotion.exit}
      transition={{
        ...springs.gentle,
        delay,
      }}
      whileHover={{ scale: motionTokens.scale.pop }}
      whileTap={{ scale: motionTokens.scale.press }}
    >
      {children}
    </motion.div>
  )
}
```

## Constraints / Non-Goals

這個 skill **不**涵蓋：

- UI 元件模式（按鈕、modal、stagger）→ 見 `motion-patterns`
- 拖曳、手勢、SVG、文字動畫、自訂 hook → 見 `motion-advanced`
- 純 CSS 動畫，或不透過 `motion/react` 的 Tailwind `animate-*` class
- 第三方動畫函式庫（GSAP、anime.js 等）
- 動態設計的決策（何時做動畫、要強調什麼）：那是設計的事，不是程式碼的限制

## Anti-Patterns

| Anti-pattern | 違反的規則 | 修法 |
| --------------------------------------- | ------- | ------------------------------- |
| `import { motion } from "framer-motion"` | Rule 1 | 用 `motion/react` |
| SSR 元件上寫 `initial={{ opacity: 0 }}` | Rule 2 | 加掛載防護 |
| 略過 `useReducedMotion` 檢查 | Rule 3 | 用 `useSafeMotion` hook |
| `animate={{ width: "100%" }}` | Rule 4 | 改用 `scaleX` transform |
| 內嵌寫 `transition={{ duration: 0.4 }}` | Rule 5 | 用 `motionTokens.duration.normal` |
| 內嵌寫 `{ stiffness: 300, damping: 30 }` | Rule 6 | 用 `springs.snappy` |
| 缺少 `"use client"` 指令 | Rule 7 | 加在檔案最上面 |
| 在模組層級用 `navigator.hardwareConcurrency` | Rule 8 | 用 `typeof navigator !== "undefined"` 包起來 |

## Related Skills

- **`motion-patterns`**：使用這裡定義的 token 和 spring，建出按鈕、modal、stagger、頁面轉場和捲動的模式。不會重新定義任何值。
- **`motion-advanced`**：使用這裡定義的 token 和 spring，做拖曳、SVG、文字和手勢模式。在這個基礎上加上 `useAnimate` 序列和自訂 hook。
