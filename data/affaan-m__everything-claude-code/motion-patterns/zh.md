---
name: motion-patterns
description: React / Next.js 可直接上正式環境的動畫模式：按鈕、modal、toast、stagger、頁面轉場、離場動畫、捲動和 layout，建立在 motion-foundations 的 token 和 spring 之上。在 React 或 Next.js 裡替特定 UI 元素做動畫（按鈕、modal、toast、stagger、頁面轉場或捲動）時使用。
tags: [motion, animation, ui-patterns]
category: frontend
author: jeff
metadata:
  version: 1.0.0
---

# Motion Patterns

最常見的 UI 動畫需求，可以直接複製貼上的模式。
這裡每個模式都建立在 `motion-foundations` 的 token 和 spring 之上。
不要在這裡定義新的 duration 或 easing 值，用 import 的。

## When to Activate

- 替按鈕、卡片、modal 或 toast 通知做動畫
- 用 stagger 做清單進場
- 在 Next.js App Router 設置頁面轉場
- 替條件式顯示的內容加進場或離場動畫
- 實作捲動顯現、與捲動連動的進度，或 sticky 的故事區塊
- 做展開的卡片、accordion 或共享元素轉場

## Outputs

這個 skill 會產出：

- 所有標準 UI 元件的無障礙、SSR 安全的動畫
- 用 `AnimatePresence` 包住、離場行為正確的條件式 render
- Next.js App Router 用的頁面轉場包裝元件
- 使用 `useScroll` + `useTransform` 的捲動顯現和捲動連動模式
- 用於展開和交叉淡入淡出元素的 layout 動畫模式（`layout`、`layoutId`）

## Principles

- 每個模式都從 `motion-foundations` import。不寫裸數字。
- 每個條件式 render 都用帶有 `key` 的 `AnimatePresence` 包起來。
- 離場動畫永遠和進場動畫一起定義，不是事後才補。
- `layout` 只用在小的、獨立的位移。大的子樹要用明確的 transform。

## Rules

1. **條件式 render 一律用 `AnimatePresence` 包起來，而且直接子元素要有 `key`。** 沒有 key，離場動畫永遠不會觸發。
2. **定義 `initial` + `animate` 時，一律同時定義 `exit`。** 沒有離場的動畫是不完整的。
3. **頁面轉場要用 `mode="wait"`。** 離場完成之前，進場不能開始。
4. **絕對不要在子元素超過約 5 個，或 DOM 巢狀很深的子樹上用 `layout`。** 改用明確的 `x`/`y` transform。
5. **Stagger 間隔必須維持在 `0.05s` 到 `0.10s` 之間。** 低於這個感覺機械；高於這個感覺遲鈍。
6. **Modal 一定要包含：** focus trap、按 Escape 關閉、scroll lock、`role="dialog"`、`aria-modal="true"`。
7. **捲動顯現要用 `viewport={{ once: true }}`。** 捲出去又重播，只會干擾，沒有資訊價值。
8. **所有 token 值都從 `motion-foundations` import。** 不准寫死數字。

## Decision Guidance

### Choosing the right pattern

| 情境 | 模式 |
| ---------------------------------------- | ---------------------- |
| 元素出現 / 消失                          | `AnimatePresence`      |
| 清單項目依序載入                         | Stagger variants       |
| 在路由之間導覽                           | 頁面轉場包裝元件       |
| 元素原地改變大小                         | `layout` prop          |
| 同一個元素在不同頁面情境之間移動         | `layoutId`             |
| 元素捲進視野時進場                       | `whileInView`          |
| 數值綁定捲動位置                         | `useScroll` + `useTransform` |

### When to use `mode="wait"` vs `mode="sync"`

| Mode | 使用時機 |
| ------- | --------------------------------------- |
| `wait` | 頁面轉場、內容替換（一次一個） |
| `sync` | 堆疊的通知、清單項目（重疊沒關係） |
| `popLayout` | 從會 reflow 的清單中移除項目 |

## Core Concepts

### AnimatePresence contract

下面三件事必須永遠成立：

1. `AnimatePresence` 包住那個條件式
2. 直接子元素有 `key`
3. 子元素有 `exit` prop

漏掉任何一項，離場動畫就會悄悄失效。

### layout vs layoutId

- `layout`：讓元素自己的大小/位置變化，原地做動畫
- `layoutId`：把兩個獨立的元素連起來，在不同次 render 之間做交叉淡入淡出

在會展開的容器裡的文字上用 `layout="position"`，避免文字 reflow 也被拿去做動畫。

## Code Examples

### Button feedback

```tsx
"use client"
import { motion } from "motion/react"
import { springs, motionTokens } from "@/lib/motion-tokens"

<motion.button
  whileHover={{ scale: motionTokens.scale.pop }}
  whileTap={{ scale: motionTokens.scale.press }}
  transition={springs.snappy}
/>
```

### Stagger list

```tsx
"use client"
import { motion } from "motion/react"
import { motionTokens, springs } from "@/lib/motion-tokens"

const container = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.08,   // 落在 0.05–0.10 的規則內
      delayChildren: 0.1,
    },
  },
}

const item = {
  hidden:  { opacity: 0, y: motionTokens.distance.md },
  visible: { opacity: 1, y: 0, transition: springs.gentle },
}

<motion.ul variants={container} initial="hidden" animate="visible">
  {items.map((i) => (
    <motion.li key={i.id} variants={item} />
  ))}
</motion.ul>
```

### Modal

```tsx
"use client"
import { motion, AnimatePresence } from "motion/react"
import { motionTokens, springs } from "@/lib/motion-tokens"

// 在呼叫端包起來：
// <AnimatePresence>{isOpen && <Modal key="modal" />}</AnimatePresence>

export function Modal({ onClose }: { onClose: () => void }) {
  return (
    <>
      {/* 遮罩 */}
      <motion.div
        className="fixed inset-0 bg-black/50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      />

      {/* 面板：無障礙要求：focus trap、按 Escape 關閉、
          scroll lock、role="dialog"、aria-modal="true" */}
      <motion.div
        role="dialog"
        aria-modal="true"
        className="fixed inset-x-4 top-1/2 -translate-y-1/2 rounded-xl bg-white p-6"
        initial={{
          opacity: 0,
          scale: motionTokens.scale.press,
          y: motionTokens.distance.sm,
        }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{
          opacity: 0,
          scale: motionTokens.scale.press,
          y: motionTokens.distance.sm,
        }}
        transition={springs.gentle}
      />
    </>
  )
}
```

### Toast stack

```tsx
"use client"
import { motion, AnimatePresence } from "motion/react"
import { motionTokens, springs } from "@/lib/motion-tokens"

<AnimatePresence mode="sync">
  {toasts.map((t) => (
    <motion.div
      key={t.id}
      layout
      initial={{
        opacity: 0,
        x: motionTokens.distance.xl,
        scale: motionTokens.scale.subtle,
      }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{
        opacity: 0,
        x: motionTokens.distance.xl,
        scale: motionTokens.scale.subtle,
      }}
      transition={springs.snappy}
    />
  ))}
</AnimatePresence>
```

### Page transition (Next.js App Router)

```tsx
// components/page-transition.tsx
"use client"
import { motion, AnimatePresence } from "motion/react"
import { usePathname } from "next/navigation"
import { motionTokens } from "@/lib/motion-tokens"

const variants = {
  initial: { opacity: 0, y: motionTokens.distance.sm },
  enter:   { opacity: 1, y: 0 },
  exit:    { opacity: 0, y: -motionTokens.distance.sm },
}

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        variants={variants}
        initial="initial"
        animate="enter"
        exit="exit"
        transition={{
          duration: motionTokens.duration.normal,
          ease: motionTokens.easing.smooth,
        }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### Scroll reveal

```tsx
"use client"
import { motion } from "motion/react"
import { motionTokens, springs } from "@/lib/motion-tokens"

<motion.div
  initial={{ opacity: 0, y: motionTokens.distance.lg }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: "-80px" }}   // once: true，規則 7
  transition={{ duration: motionTokens.duration.slow, ease: motionTokens.easing.smooth }}
/>
```

### Scroll progress bar

```tsx
"use client"
import { motion, useScroll } from "motion/react"

export function ScrollProgress() {
  const { scrollYProgress } = useScroll()
  return (
    <motion.div
      className="fixed top-0 left-0 h-1 bg-indigo-500 origin-left w-full"
      style={{ scaleX: scrollYProgress }}
    />
  )
}
```

### Expanding card

```tsx
"use client"
import { useState } from "react"
import { motion, AnimatePresence } from "motion/react"
import { springs, motionTokens } from "@/lib/motion-tokens"

export function ExpandingCard({ title, body }: { title: string; body: string }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <motion.div layout onClick={() => setExpanded(!expanded)} className="cursor-pointer">
      {/* layout="position" 避免文字 reflow 也被拿去做動畫 */}
      <motion.h2 layout="position" className="font-semibold">
        {title}
      </motion.h2>

      <AnimatePresence>
        {expanded && (
          <motion.p
            key="body"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: motionTokens.duration.fast }}
          >
            {body}
          </motion.p>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
```

### Shared-element crossfade

```tsx
// 來源情境
<motion.img layoutId="hero-image" src={src} className="w-16 h-16 rounded" />

// 目的地情境（同一個 layoutId，轉場交給 motion 處理）
<motion.img layoutId="hero-image" src={src} className="w-full rounded-xl" />
```

### Accordion

```tsx
<motion.div
  initial={false}
  animate={{ opacity: open ? 1 : 0, scaleY: open ? 1 : 0 }}
  style={{ transformOrigin: "top", overflow: "hidden" }}
  transition={{
    duration: motionTokens.duration.normal,
    ease: motionTokens.easing.smooth,
  }}
> {children}
</motion.div>
```

## End-to-End Example

一個在掛載時進場、處理條件式顯示，並且
尊重 reduced motion 的 stagger 清單，結合了 token、spring、AnimatePresence 和
來自 `motion-foundations` 的無障礙 hook：

```tsx
"use client"
import { useState } from "react"
import { motion, AnimatePresence } from "motion/react"
import { motionTokens, springs } from "@/lib/motion-tokens"
import { useSafeMotion } from "@/hooks/use-reduced-motion"

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
}

function ListItem({ label, onRemove }: { label: string; onRemove: () => void }) {
  const safe = useSafeMotion(motionTokens.distance.sm)
  return (
    <motion.li
      variants={{
        hidden:  safe.initial,
        visible: safe.animate,
      }}
      exit={safe.exit}
      transition={springs.gentle}
      className="flex items-center justify-between p-3 rounded-lg bg-white shadow-sm"
    >
      <span>{label}</span>
      <button onClick={onRemove}>Remove</button>
    </motion.li>
  )
}

export function AnimatedList({ items, onRemove }: {
  items: { id: string; label: string }[]
  onRemove: (id: string) => void
}) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-2"
    >
      <AnimatePresence mode="popLayout">
        {items.map((item) => (
          <ListItem
            key={item.id}
            label={item.label}
            onRemove={() => onRemove(item.id)}
          />
        ))}
      </AnimatePresence>
    </motion.ul>
  )
}
```

## Constraints / Non-Goals

這個 skill **不**涵蓋：

- token 和 spring 的定義 → 見 `motion-foundations`
- 拖曳互動、滑動手勢、可重新排序的清單 → 見 `motion-advanced`
- 文字動畫（逐字詞/逐字元顯現、計數器）→ 見 `motion-advanced`
- SVG 路徑繪製或變形 → 見 `motion-advanced`
- 自訂動畫 hook → 見 `motion-advanced`
- 不使用 `motion/react` 的純 CSS 轉場

## Anti-Patterns

| Anti-pattern | 違反的規則 | 修法 |
| -------------------------------------------- | ------- | ------------------------------------------ |
| `AnimatePresence` 的子元素缺少 `key` | Rule 1 | 替直接子元素加上穩定的 `key` |
| 有 `initial` + `animate` 卻沒有 `exit` | Rule 2 | 三個一律一起定義 |
| 頁面轉場沒有 `mode="wait"` | Rule 3 | 在 `AnimatePresence` 加 `mode="wait"` |
| 在 50 個項目的清單上用 `layout` | Rule 4 | 用 `mode="popLayout"` 或明確的 transform |
| 10 個項目的清單用 `staggerChildren: 0.2` | Rule 5 | 上限壓在 `0.08–0.10` |
| Modal 沒有 focus trap | Rule 6 | 加 `focus-trap-react` 或 Radix Dialog |
| `whileInView` 沒有 `viewport={{ once: true }}` | Rule 7 | 重複進場只會干擾，沒有資訊價值 |
| 內嵌寫 `transition={{ duration: 0.3 }}` | Rule 8 | 用 `motionTokens.duration.normal` |

## Related Skills

- **`motion-foundations`**：定義這裡每個模式都會 import 的所有 token、spring、`useSafeMotion` hook 和 SSR 防護。必須先設置好。
- **`motion-advanced`**：用拖曳、手勢、SVG、文字、自訂 hook 和命令式序列，擴充這些模式。不會重新定義這個 skill 裡的任何模式。
