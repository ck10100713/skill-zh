---
name: motion-advanced
description: React / Next.js 的進階動態模式：拖放、手勢、文字動畫、SVG 路徑繪製、自訂 hook、命令式序列（useAnimate）、loader，以及完整的 API 決策樹。需要先有 motion-foundations。在 React 或 Next.js 裡做拖放、手勢、文字或 SVG 動畫，或命令式動畫序列時使用。
tags: [motion, animation, advanced, gestures, svg]
category: frontend
author: jeff
metadata:
  version: 1.0.0
---

# Motion Advanced

複雜、互動式、以物理為基礎的動畫模式。
需要先設置好 `motion-foundations`。
`motion-patterns` 不夠用時再用這個。

## When to Activate

- 做拖曳關閉的 sheet、滑動手勢或可重新排序的清單
- 讓文字逐字詞、逐字元出現，或做成即時計數器
- 畫 SVG 路徑、變形圖示，或做圓形進度動畫
- 寫自訂的動畫 hook（`useScrollReveal`、磁吸按鈕、游標跟隨器）
- 用 `useAnimate` 以命令式串接多步驟動畫
- 做 spinner、shimmer 骨架、脈衝指示器或載入中的按鈕狀態

## Outputs

這個 skill 會產出：

- 拖曳互動：可拖曳的卡片、拖曳關閉的 sheet、`Reorder.Group` 清單
- 手勢 hook：滑動偵測、長按、捏合輪廓
- 文字動畫元件：逐字詞顯現、逐字元打字機、數字計數器
- SVG 動畫：路徑逐步繪製、圖示變形、描邊進度環
- 自訂 hook：`useScrollReveal`、`useHoverScale`、`useNavigationDirection`、`useInViewOnce`
- 透過 `useAnimate` 搭配可安全中斷的 `async/await` 做的命令式序列
- Loader 元件：spinner、shimmer、脈衝點、進度條、按鈕載入狀態

## Principles

- 直接操作（拖曳等）時，以物理為基礎的動態（`useSpring`、`springs.*`）永遠比以時間長度為基礎的更自然。
- `useMotionValue` + `useTransform` 計算衍生值時，不會觸發 re-render。
- `useAnimate` 序列是命令式的，而且可以安全中斷：動畫進行到一半時呼叫 `animate()`，會自動取消前一個動畫。
- Motion value（`useMotionValue`、`useSpring`）對 SSR 安全，不會造成 hydration 錯誤。

## Rules

1. **拖曳互動必須在觸控裝置上測試**，不能只測滑鼠。`drag` prop 兩者都能用，但手感和閾值不同。
2. **無限動畫在 `document.visibilityState === "hidden"` 時必須暫停。** 背景分頁不准消耗 GPU/CPU。
3. **滑動閾值必須明確。** 絕對不要只靠速度推斷意圖；要同時檢查 `offset` + `velocity`。
4. **`useAnimate` 的 scope ref 必須綁在已掛載的 DOM 元素上。** 在掛載之前呼叫 `animate()` 會悄悄丟錯。
5. **Motion value 不可以在每次 render 時重建。** 在元件本體裡用 `useMotionValue(0)` 是對的；在 render 裡寫 `new MotionValue(0)` 就不對。
6. **所有 token 值都從 `motion-foundations` import。** 不准寫死數字。
7. **自訂 hook 必須處理清理。** 每個 `window.addEventListener` 都要在 `useEffect` 的 return 裡有對應的 `removeEventListener`。
8. **SVG 變形要求路徑指令數量相同。** 指令結構不同的路徑會直接跳過去，不會補間。

## Decision Guidance

### Choosing the right advanced API

| 情境 | API |
| ------------------------------ | -------------------------------- |
| 放開後帶物理效果的拖曳 | `drag` + `dragTransition: springs.release` |
| 有順序、可拖曳重新排序的清單 | `Reorder.Group` + `Reorder.Item` |
| 依拖曳位移量關閉 | `drag="y"` + `onDragEnd` 位移檢查 |
| 左右滑動 | `drag="x"` + `onDragEnd` 位移檢查 |
| 長按 | `useLongPress` hook |
| 隨時間平滑的值 | `useSpring` |
| 由另一個值衍生的值 | `useTransform` |
| 多步驟序列 | `useAnimate` 搭配 `async/await` |
| 一次性的命令式動畫 | 來自 `motion` 的 `animate()` |
| 文字逐字詞進場 | 在 `inline-block` span 上做 stagger |
| SVG 逐步繪製 | `pathLength` 0 → 1 |
| SVG 變形 | `d` 屬性補間（指令數相同） |
| 圓形進度 | `strokeDashoffset` 補間 |

### When to use `useSpring` vs a spring transition

| | `useSpring` | `transition: springs.*` |
| -------------- | ---------------------------------------- | ----------------------- |
| 用於 | 游標跟隨器、跟著指標的值 | 離散的狀態變化 |
| 更新 | 連續的，每個 frame 都更新 | 由狀態變化觸發 |
| 中斷 | 平滑：物理從目前速度接著走 | 從目前的值重新開始 |

## Core Concepts

### useMotionValue + useTransform

不需要 re-render 的響應式計算：

```tsx
const x = useMotionValue(0)
const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0])
// x 一變，opacity 每個 frame 都會更新，沒有 setState，沒有 re-render
```

### useAnimate

回傳 `[scope, animate]`。scope ref 必須綁在 DOM 元素上。
`animate()` 呼叫可以安全中斷：進行到一半時再呼叫，會取消前一次執行。

```tsx
const [scope, animate] = useAnimate()

async function play() {
  await animate(".step-1", { opacity: 1 }, { duration: 0.3 })
  await animate(".step-2", { x: 0 },       { duration: 0.4 })
        animate(".step-3", { scale: 1 },    { duration: 0.25 })  // 發射後不管
}

return <div ref={scope}>...</div>
```

## Code Examples

### Draggable card

```tsx
"use client"
import { motion } from "motion/react"
import { springs, motionTokens } from "@/lib/motion-tokens"

<motion.div
  drag
  dragConstraints={{ left: -100, right: 100, top: -100, bottom: 100 }}
  dragElastic={0.1}
  whileDrag={{
    scale: motionTokens.scale.pop,
    boxShadow: "0 16px 40px rgba(0,0,0,0.2)",
  }}
  dragTransition={springs.release}
/>
```

### Drag-to-dismiss sheet

```tsx
"use client"
import { motion, useMotionValue, useTransform } from "motion/react"

export function BottomSheet({ onClose }: { onClose: () => void }) {
  const y = useMotionValue(0)
  const opacity = useTransform(y, [0, 200], [1, 0])

  return (
    <motion.div
      drag="y"
      dragConstraints={{ top: 0 }}
      style={{ y, opacity }}
      onDragEnd={(_, info) => {
        // Rule 3: 同時檢查 offset + velocity
        if (info.offset.y > 120 || info.velocity.y > 500) onClose()
      }}
    />
  )
}
```

### Reorderable list

```tsx
"use client"
import { Reorder } from "motion/react"

export function SortableList() {
  const [items, setItems] = useState(initialItems)
  return (
    <Reorder.Group axis="y" values={items} onReorder={setItems}>
      {items.map((item) => (
        <Reorder.Item key={item.id} value={item}>
          {item.label}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  )
}
```

### Swipe detection

```tsx
"use client"
import { motion } from "motion/react"

const OFFSET_THRESHOLD  = 50
const VELOCITY_THRESHOLD = 300

<motion.div
  drag="x"
  dragConstraints={{ left: 0, right: 0 }}
  onDragEnd={(_, info) => {
    const swipedRight = info.offset.x > OFFSET_THRESHOLD  || info.velocity.x > VELOCITY_THRESHOLD
    const swipedLeft  = info.offset.x < -OFFSET_THRESHOLD || info.velocity.x < -VELOCITY_THRESHOLD
    if (swipedRight) onSwipeRight()
    if (swipedLeft)  onSwipeLeft()
  }}
/>
```

### Long press hook

```tsx
import { useRef } from "react"

export function useLongPress(callback: () => void, ms = 600) {
  const timerRef = useRef<ReturnType<typeof setTimeout>>()
  return {
    onPointerDown:  () => { timerRef.current = setTimeout(callback, ms) },
    onPointerUp:    () => clearTimeout(timerRef.current),
    onPointerLeave: () => clearTimeout(timerRef.current),
  }
}
```

### Word-by-word reveal

```tsx
"use client"
import { motion } from "motion/react"
import { springs } from "@/lib/motion-tokens"

export function AnimatedText({ text }: { text: string }) {
  return (
    <motion.p
      variants={{ visible: { transition: { staggerChildren: 0.05 } } }}
      initial="hidden"
      animate="visible"
    >
      {text.split(" ").map((word, i) => (
        <motion.span
          key={i}
          className="inline-block mr-1"
          variants={{
            hidden:  { opacity: 0, y: 12 },
            visible: { opacity: 1, y: 0, transition: springs.gentle },
          }}
        >
          {word}
        </motion.span>
      ))}
    </motion.p>
  )
}
```

### Number counter

```tsx
"use client"
import { useRef, useEffect } from "react"
import { animate } from "motion"
import { motionTokens } from "@/lib/motion-tokens"

export function Counter({ to }: { to: number }) {
  const nodeRef = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    const controls = animate(0, to, {
      duration: motionTokens.duration.crawl,
      ease: motionTokens.easing.smooth,
      onUpdate: (v) => {
        if (nodeRef.current) nodeRef.current.textContent = Math.round(v).toString()
      },
    })
    return controls.stop   // Rule 7: 清理
  }, [to])

  return <span ref={nodeRef} />
}
```

### SVG path draw-on

```tsx
"use client"
import { motion } from "motion/react"
import { motionTokens } from "@/lib/motion-tokens"

<motion.path
  d="M 0 100 Q 50 0 100 100"
  initial={{ pathLength: 0, opacity: 0 }}
  animate={{ pathLength: 1, opacity: 1 }}
  transition={{ duration: motionTokens.duration.slow, ease: motionTokens.easing.smooth }}
/>
```

### Stroke progress ring

```tsx
"use client"
import { motion } from "motion/react"
import { motionTokens } from "@/lib/motion-tokens"

const CIRCUMFERENCE = 2 * Math.PI * 40   // r=40

export function ProgressRing({ progress }: { progress: number }) {
  return (
    <svg width="100" height="100" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" strokeWidth="8" />
      <motion.circle
        cx="50" cy="50" r="40"
        fill="none" stroke="#6366f1" strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={CIRCUMFERENCE}
        animate={{ strokeDashoffset: CIRCUMFERENCE - (progress / 100) * CIRCUMFERENCE }}
        transition={{ duration: motionTokens.duration.normal, ease: motionTokens.easing.smooth }}
        style={{ rotate: -90, transformOrigin: "center" }}
      />
    </svg>
  )
}
```

### useScrollReveal hook

```tsx
"use client"
import { useRef } from "react"
import { useScroll, useTransform } from "motion/react"
import { motionTokens } from "@/lib/motion-tokens"

export function useScrollReveal() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] })
  const opacity = useTransform(scrollYProgress, [0, 0.3], [0, 1])
  const y       = useTransform(scrollYProgress, [0, 0.3], [motionTokens.distance.lg, 0])
  return { ref, style: { opacity, y } }
}

// 用法
const { ref, style } = useScrollReveal()
<motion.section ref={ref} style={style} />
```

### Cursor follower

```tsx
"use client"
import { useEffect } from "react"
import { motion, useMotionValue, useSpring } from "motion/react"
import { springs } from "@/lib/motion-tokens"

export function CursorFollower() {
  const x = useMotionValue(-100)
  const y = useMotionValue(-100)
  const sx = useSpring(x, springs.gentle)
  const sy = useSpring(y, springs.gentle)

  useEffect(() => {
    const move = (e: MouseEvent) => { x.set(e.clientX); y.set(e.clientY) }
    window.addEventListener("mousemove", move)
    return () => window.removeEventListener("mousemove", move)   // Rule 7
  }, [])

  return (
    <motion.div
      className="fixed top-0 left-0 w-6 h-6 rounded-full bg-indigo-500
                 pointer-events-none -translate-x-1/2 -translate-y-1/2 z-50"
      style={{ x: sx, y: sy }}
    />
  )
}
```

### Shimmer skeleton

```tsx
"use client"
import { useEffect } from "react"
import { motion, useAnimation } from "motion/react"
import { motionTokens } from "@/lib/motion-tokens"

export function ShimmerSkeleton({ className = "" }: { className?: string }) {
  const controls = useAnimation()

  useEffect(() => {
    const play = () =>
      controls.start({
        x: ["-100%", "100%"],
        transition: {
          repeat: Infinity,
          duration: motionTokens.duration.crawl,
          ease: motionTokens.easing.linear,
        },
      })

    const handleVisibility = () => {
      if (document.visibilityState === "hidden") controls.stop()
      else void play()
    }

    void play()
    document.addEventListener("visibilitychange", handleVisibility)
    return () => {
      controls.stop()
      document.removeEventListener("visibilitychange", handleVisibility)
    }
  }, [controls])

  return (
    <div className={`relative overflow-hidden bg-gray-200 rounded ${className}`}>
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/60 to-transparent"
        initial={{ x: "-100%" }}
        animate={controls}
      />
    </div>
  )
}
```

### Button loading state

```tsx
"use client"
import { motion, AnimatePresence } from "motion/react"
import { motionTokens, springs } from "@/lib/motion-tokens"

export function LoadingButton({
  loading,
  label,
  onClick,
}: {
  loading: boolean
  label: string
  onClick: () => void
}) {
  return (
    <motion.button
      onClick={onClick}
      animate={{ opacity: loading ? 0.7 : 1 }}
      whileTap={loading ? {} : { scale: motionTokens.scale.press }}
      transition={springs.snappy}
      disabled={loading}
    >
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.span
            key="loading"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: motionTokens.duration.fast }}
          >
            …
          </motion.span>
        ) : (
          <motion.span
            key="label"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: motionTokens.duration.fast }}
          >
            {label}
          </motion.span>
        )}
      </AnimatePresence>
    </motion.button>
  )
}
```

### Infinite animation with visibility pause

```tsx
"use client"
import { useEffect } from "react"
import { motion, useAnimation } from "motion/react"
import { motionTokens } from "@/lib/motion-tokens"

export function PulseDot() {
  const controls = useAnimation()

  useEffect(() => {
    const pulse = () =>
      controls.start({
        scale: [1, 1.4, 1],
        opacity: [1, 0.6, 1],
        transition: { repeat: Infinity, duration: motionTokens.duration.crawl },
      })

    // Rule 2: 分頁被隱藏時暫停
    const handleVisibility = () => {
      if (document.visibilityState === "hidden") controls.stop()
      else void pulse()
    }

    void pulse()
    document.addEventListener("visibilitychange", handleVisibility)
    // Rule 7: unmount 時停掉 controls 並移除 listener。
    return () => {
      controls.stop()
      document.removeEventListener("visibilitychange", handleVisibility)
    }
  }, [controls])

  return <motion.span className="w-2 h-2 rounded-full bg-green-400" animate={controls} />
}
```

## End-to-End Example

拖曳關閉的 sheet，搭配 shimmer 內容、載入狀態和 reduced motion
支援，結合了 `useMotionValue`、`useTransform`、`useSafeMotion`、
`AnimatePresence`，以及來自 `motion-foundations` 的 token：

```tsx
"use client"
import { useState } from "react"
import { motion, AnimatePresence, useMotionValue, useTransform } from "motion/react"
import { springs, motionTokens } from "@/lib/motion-tokens"
import { useSafeMotion } from "@/hooks/use-reduced-motion"
import { ShimmerSkeleton } from "./shimmer-skeleton"

export function DismissibleSheet({
  isOpen,
  onClose,
  loading,
  children,
}: {
  isOpen: boolean
  onClose: () => void
  loading: boolean
  children: React.ReactNode
}) {
  const safe = useSafeMotion(motionTokens.distance.xl)
  const y = useMotionValue(0)
  const opacity = useTransform(y, [0, 200], [1, 0])

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* 背景遮罩 */}
          <motion.div
            key="backdrop"
            className="fixed inset-0 bg-black/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Sheet：拖曳關閉 */}
          <motion.div
            key="sheet"
            className="fixed bottom-0 inset-x-0 rounded-t-2xl bg-white p-6"
            drag="y"
            dragConstraints={{ top: 0 }}
            style={{ y, opacity }}
            onDragEnd={(_, info) => {
              if (info.offset.y > 120 || info.velocity.y > 500) onClose()
            }}
            initial={safe.initial}
            animate={safe.animate}
            exit={safe.exit}
            transition={springs.gentle}
          >
            {loading ? (
              <div className="space-y-3">
                <ShimmerSkeleton className="h-4 w-3/4" />
                <ShimmerSkeleton className="h-4 w-1/2" />
                <ShimmerSkeleton className="h-20 w-full" />
              </div>
            ) : children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

## Constraints / Non-Goals

這個 skill **不**涵蓋：

- token 和 spring 的定義 → 見 `motion-foundations`
- 標準 UI 模式（按鈕、modal、stagger、頁面轉場）→ 見 `motion-patterns`
- 純 CSS 動畫，或不透過 `motion/react` 的 Tailwind `animate-*`
- 以 Canvas 或 WebGL 為基礎的動畫（Three.js、Pixi 等）
- 搭配外部狀態管理器的完整拖放系統（dnd-kit、react-beautiful-dnd）
- 遊戲迴圈或逐 frame 動畫

## Anti-Patterns

| Anti-pattern | 違反的規則 | 修法 |
| ---------------------------------------------- | ------- | ------------------------------------------------ |
| `drag` 只在桌機上測 | Rule 1 | 用觸控模擬器和真機測試 |
| `animate={{ repeat: Infinity }}` 沒有暫停 | Rule 2 | 加 `visibilitychange` listener |
| `onDragEnd` 只檢查 offset，沒檢查 velocity | Rule 3 | 同時檢查 `info.offset` 和 `info.velocity` |
| 在 `useEffect` 之前就 `animate(scope, ...)` | Rule 4 | 只在掛載之後才呼叫 `animate()` |
| 在 render 裡寫 `const x = new MotionValue(0)` | Rule 5 | 用 `const x = useMotionValue(0)` |
| 內嵌寫 `transition={{ duration: 1.2 }}` | Rule 6 | 用 `motionTokens.duration.crawl` |
| `useEffect` 沒有清理 | Rule 7 | return `removeEventListener` / `controls.stop` |
| 在指令不同的路徑之間做 SVG 變形 | Rule 8 | 動畫前先正規化路徑指令 |

## Related Skills

- **`motion-foundations`**：定義這裡所 import 的所有 token、spring、`useSafeMotion` 和 SSR 防護。使用這個 skill 之前必須先設置好。
- **`motion-patterns`**：處理標準 UI 模式（按鈕、modal、stagger、頁面轉場、捲動顯現）。在動用這裡的進階模式之前，先用它。
