---
name: interaction-design
description: 設計並實作微互動、動態設計、轉場與使用者回饋模式。適用於為 UI 互動增添質感、實作載入狀態，或打造令人愉悅的使用者體驗的時候。
---

# 互動設計

透過動態、回饋和用心的狀態轉換，打造吸引人又直覺的互動，提升可用性並讓使用者愉悅。

## 什麼時候用這個 Skill

- 加入微互動以強化使用者回饋
- 實作流暢的頁面與元件轉場
- 設計載入狀態和 skeleton screen
- 建立以手勢為基礎的互動
- 建構通知與 toast 系統
- 實作拖放介面
- 加入捲動觸發的動畫
- 設計 hover 與 focus 狀態

## 核心原則

### 1. 有目的的動態

動態要用來溝通，不是用來裝飾：

- **回饋**：確認使用者的動作已經發生
- **方位感**：顯示元素從哪裡來、往哪裡去
- **聚焦**：把注意力導向重要的變化
- **連續性**：在轉場期間維持脈絡

### 2. 時間指引

| 時間長度  | 使用情境                                  |
| --------- | ----------------------------------------- |
| 100-150ms | 微回饋（hover、點擊）                     |
| 200-300ms | 小型轉場（開關、下拉選單）                |
| 300-500ms | 中型轉場（modal、頁面切換）               |
| 500ms+    | 複雜的編排動畫                            |

### 3. Easing 函式

```css
/* 常見的 easing */
--ease-out: cubic-bezier(0.16, 1, 0.3, 1); /* 減速：進場 */
--ease-in: cubic-bezier(0.55, 0, 1, 0.45); /* 加速：離場 */
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1); /* 兩者：在之間移動 */
--spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* 過衝：活潑 */
```

## 快速開始：按鈕微互動

```tsx
import { motion } from "framer-motion";

export function InteractiveButton({ children, onClick }) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      className="px-4 py-2 bg-blue-600 text-white rounded-lg"
    >
      {children}
    </motion.button>
  );
}
```

## 互動模式

### 1. 載入狀態

**Skeleton Screen**：載入期間保留版面

```tsx
function CardSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-48 bg-gray-200 rounded-lg" />
      <div className="mt-4 h-4 bg-gray-200 rounded w-3/4" />
      <div className="mt-2 h-4 bg-gray-200 rounded w-1/2" />
    </div>
  );
}
```

**進度指示器**：顯示確定的進度

```tsx
function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
      <motion.div
        className="h-full bg-blue-600"
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ ease: "easeOut" }}
      />
    </div>
  );
}
```

### 2. 狀態轉換

**帶有平滑轉場的 Toggle**：

```tsx
function Toggle({ checked, onChange }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`
        relative w-12 h-6 rounded-full transition-colors duration-200
        ${checked ? "bg-blue-600" : "bg-gray-300"}
      `}
    >
      <motion.span
        className="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow"
        animate={{ x: checked ? 24 : 0 }}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
      />
    </button>
  );
}
```

### 3. 頁面轉場

**Framer Motion 版面動畫**：

```tsx
import { AnimatePresence, motion } from "framer-motion";

function PageTransition({ children, key }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={key}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

### 4. 回饋模式

**點擊時的漣漪效果**：

```tsx
function RippleButton({ children, onClick }) {
  const [ripples, setRipples] = useState([]);

  const handleClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const ripple = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      id: Date.now(),
    };
    setRipples((prev) => [...prev, ripple]);
    setTimeout(() => {
      setRipples((prev) => prev.filter((r) => r.id !== ripple.id));
    }, 600);
    onClick?.(e);
  };

  return (
    <button onClick={handleClick} className="relative overflow-hidden">
      {children}
      {ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="absolute bg-white/30 rounded-full animate-ripple"
          style={{ left: ripple.x, top: ripple.y }}
        />
      ))}
    </button>
  );
}
```

### 5. 手勢互動

**滑動關閉**：

```tsx
function SwipeCard({ children, onDismiss }) {
  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={(_, info) => {
        if (Math.abs(info.offset.x) > 100) {
          onDismiss();
        }
      }}
      className="cursor-grab active:cursor-grabbing"
    >
      {children}
    </motion.div>
  );
}
```

## CSS 動畫模式

### Keyframe 動畫

```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
.animate-pulse {
  animation: pulse 2s ease-in-out infinite;
}
.animate-spin {
  animation: spin 1s linear infinite;
}
```

### CSS Transition

```css
.card {
  transition:
    transform 0.2s ease-out,
    box-shadow 0.2s ease-out;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}
```

## 無障礙考量

```css
/* 尊重使用者的動態偏好 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

```tsx
function AnimatedComponent() {
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  return (
    <motion.div
      animate={{ opacity: 1 }}
      transition={{ duration: prefersReducedMotion ? 0 : 0.3 }}
    />
  );
}
```

## 最佳實務

1. **效能優先**：用 `transform` 和 `opacity` 達到流暢的 60fps
2. **支援減少動態**：一律尊重 `prefers-reduced-motion`
3. **一致的時間**：整個應用程式使用同一套時間級距
4. **自然的物理感**：優先用 spring 動畫而不是 linear
5. **可中斷**：允許使用者取消長時間的動畫
6. **漸進增強**：沒有 JS 動畫也能運作
7. **在裝置上測試**：效能差異很大

## 常見問題

- **卡頓的動畫**：避免對 `width`、`height`、`top`、`left` 做動畫
- **過度動畫**：太多動態會造成疲勞
- **阻擋互動**：動畫期間絕對不要阻止使用者輸入
- **記憶體洩漏**：unmount 時要清理動畫的 listener
- **內容閃爍**：謹慎使用 `will-change` 做最佳化
