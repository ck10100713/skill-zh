---
name: tailwind-theme-builder
description: "設定 Tailwind v4 + shadcn/ui 的主題化 UI，含 dark mode。安裝相依套件、透過 @theme inline 設定 CSS 變數、接上 dark mode 切換、驗證。只要使用者提到 Tailwind v4、設定 Tailwind 主題、shadcn/ui 顏色、dark mode，或排查顏色沒作用、tw-animate-css 錯誤、@theme inline 衝突、升級後 @apply 壞掉、v3 → v4 遷移問題，就用這個 skill。"
compatibility: claude-code-only
---

# Tailwind Theme Builder

設定一個完整主題化的 Tailwind v4 + shadcn/ui 專案，含 dark mode。產出設定好的 CSS、theme provider，以及可用的元件庫。

## 架構：四步驟模式

Tailwind v4 要做 CSS 變數式的主題，需要特定的架構。這個模式是**強制的**，跳過或改動任何步驟都會讓主題壞掉。

### 運作方式

```
CSS Variable Definition --> @theme inline Mapping --> Tailwind Utility Class
--background           --> --color-background     --> bg-background
(with hsl() wrapper)      (references variable)     (generated class)
```

Dark mode 切換：
```
ThemeProvider toggles .dark class on <html>
  --> CSS variables update automatically (.dark overrides :root)
  --> Tailwind utilities reference updated variables
  --> UI updates without re-render
```

### 最佳實踐

- **語意化命名：** 用 `--primary`，不要用 `--blue-500`
- **前景色配對：** 每個背景色都要有對應的前景色（`--primary` + `--primary-foreground`）
- **WCAG 對比：** 一般文字 4.5:1，大字 3:1，UI 元件 3:1
- **圖表顏色：** 用獨立的變數搭配 `@theme inline` 對應，在 style props 裡用 `var(--chart-1)` 引用

---

## 工作流程

### 步驟 1：安裝相依套件

```bash
pnpm add tailwindcss @tailwindcss/vite
pnpm add -D @types/node tw-animate-css
pnpm dlx shadcn@latest init

# Delete v3 config if it exists
rm -f tailwind.config.ts
```

### 步驟 2：設定 Vite

複製 `assets/vite.config.ts`，或自己加上 Tailwind plugin：

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } }
})
```

### 步驟 3：四步驟 CSS 架構（強制）

一定要照這個順序。跳過步驟會讓主題壞掉。

**src/index.css：**

```css
@import "tailwindcss";
@import "tw-animate-css";

/* 1. Define CSS variables at root (NOT inside @layer base) */
:root {
  --background: hsl(0 0% 100%);
  --foreground: hsl(222.2 84% 4.9%);
  --primary: hsl(221.2 83.2% 53.3%);
  --primary-foreground: hsl(210 40% 98%);
  /* ... all semantic tokens */
}

.dark {
  --background: hsl(222.2 84% 4.9%);
  --foreground: hsl(210 40% 98%);
  --primary: hsl(217.2 91.2% 59.8%);
  --primary-foreground: hsl(222.2 47.4% 11.2%);
}

/* 2. Map variables to Tailwind utilities */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
}

/* 3. Apply base styles (NO hsl() wrapper here) */
@layer base {
  body {
    background-color: var(--background);
    color: var(--foreground);
  }
}
```

**結果：** `bg-background`、`text-primary` 等 class 會自動生效。Dark mode 透過 `.dark` class 切換，語意化顏色不需要 `dark:` variant。

### 步驟 4：設定 Dark Mode

把 `assets/theme-provider.tsx` 複製到你的 components 目錄，然後包住你的 app：

```typescript
import { ThemeProvider } from '@/components/theme-provider'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
    <App />
  </ThemeProvider>
)
```

加上主題切換：先安裝 dropdown menu，再使用下面的 ModeToggle 元件：

```bash
pnpm dlx shadcn@latest add dropdown-menu
```

```typescript
// src/components/mode-toggle.tsx
import { Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useTheme } from "@/components/theme-provider"

export function ModeToggle() {
  const { setTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>Light</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>Dark</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>System</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### 步驟 5：設定 components.json

```json
{
  "tailwind": {
    "config": "",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true
  }
}
```

`"config": ""` 非常關鍵，v4 不使用 tailwind.config.ts。

---

## 關鍵規則

**一定要：**
- 在 `:root`/`.dark` 裡用 `hsl()` 包住顏色
- 用 `@theme inline` 對應所有 CSS 變數
- 用 `@tailwindcss/vite` plugin（不要用 PostCSS）
- 如果 `tailwind.config.ts` 存在，就把它刪掉

**絕對不要：**
- 把 `:root`/`.dark` 放進 `@layer base`
- 用 `.dark { @theme { } }`（v4 不支援巢狀 @theme）
- 重複包裝：`hsl(var(--background))`
- 對 `@layer base` 裡的 class 使用 `@apply`（改用 `@utility`）

---

## 全部 18 個陷阱

### 快速診斷

| # | 症狀 | 原因 | 解法 |
|---|---------|-------|-----|
| 1 | 變數被忽略 / 主題壞掉 | `:root` 在 `@layer base` 裡 | 把 `:root` 和 `.dark` 移到最外層 |
| 2 | Dark mode 顏色沒切換 | `.dark { @theme { } }` | 用 CSS 變數 + 單一個 `@theme inline` |
| 3 | 顏色全是黑/白 | `hsl()` 重複包裝 | 用 `var(--background)`，不要用 `hsl(var(...))` |
| 4 | `bg-primary` 沒被產生 | 顏色放在 `tailwind.config.ts` | 刪掉 config，改用 `@theme inline` |
| 5 | 缺少 `bg-background` class | 沒有 `@theme inline` 區塊 | 加上 `@theme inline` 對應變數 |
| 6 | shadcn 元件壞掉 | `components.json` 有 config 路徑 | 設成 `"config": ""`（空字串） |
| 7 | Tailwind 沒在處理 | 用了 PostCSS plugin | 換成 `@tailwindcss/vite` plugin |
| 8 | `@/` import 失敗 | 缺少 path alias | 在 `tsconfig.app.json` 加上 `paths` |
| 9 | 多餘的 `dark:` variant | 用了 `dark:bg-primary-dark` | 直接用 `bg-primary`，變數會處理 |
| 10 | 到處都是寫死的顏色 | 用了 `bg-blue-600 dark:bg-blue-400` | 用語意 token：`bg-primary` |
| 11 | Class 合併的 bug | 用字串拼接 class | 用 `@/lib/utils` 的 `cn()` |
| 12 | Radix Select 當掉 | 空字串值 `value=""` | 用 `value="placeholder"` |
| 13 | Tailwind 版本錯誤 | 裝了 `tailwindcss@^3` | 裝 `tailwindcss@^4.1.0` + `@tailwindcss/vite` |
| 14 | 缺 peer dependency | 只裝了 `tailwindcss` | 也要裝 `clsx`、`tailwind-merge`、`@types/node` |
| 15 | Dark mode 下壞掉 | 只測過 light mode | 測 light、dark、system，以及切換時的轉場 |
| 16 | 沒過 WCAG 對比 | 肉眼看起來沒問題 | 檢查比例：一般文字 4.5:1，大字/UI 3:1 |
| 17 | 動畫 import 讓 build 失敗 | 用了 `tailwindcss-animate`（已棄用） | 用 `tw-animate-css` 或原生 CSS 動畫 |
| 18 | CSS 優先順序問題 | shadcn init 之後出現重複的 `@layer base` | 合併成單一個 `@layer base` 區塊 |

### 陷阱細節與程式碼範例

**#1 -- :root 在 @layer base 裡**

Tailwind v4 會把 `@theme`/`@layer` 以外的 CSS 去掉，但 `:root` 必須在最外層才會保留。這是最常見的設定失敗原因。

錯誤：
```css
@layer base {
  :root { --background: hsl(0 0% 100%); }
}
```

正確：
```css
:root { --background: hsl(0 0% 100%); }
@layer base {
  body { background-color: var(--background); }
}
```

**#2 -- 巢狀 @theme**

Tailwind v4 不支援把 `@theme` 放在 selector 裡面。用 `:root`/`.dark` 裡的 CSS 變數，加上單一個 `@theme inline` 區塊。

錯誤：
```css
@theme { --color-primary: hsl(0 0% 0%); }
.dark { @theme { --color-primary: hsl(0 0% 100%); } }
```

正確：
```css
:root { --primary: hsl(0 0% 0%); }
.dark { --primary: hsl(0 0% 100%); }
@theme inline { --color-primary: var(--primary); }
```

**#3 -- hsl() 重複包裝**

變數本身已經含有 `hsl()`。重複包裝會變成 `hsl(hsl(...))`。

錯誤：`background-color: hsl(var(--background));`
正確：`background-color: var(--background);`

**#4 -- 顏色放在 tailwind.config.ts**

Tailwind v4 完全忽略 config 檔裡的 `theme.extend.colors`。把檔案刪掉，或留空。在 `components.json` 設 `"config": ""`。

**#5 -- 缺少 @theme inline**

沒有 `@theme inline` 的話，Tailwind 根本不知道你的 CSS 變數。像 `bg-background` 這類 utility class 就是不會被產生。

錯誤：
```css
:root { --background: hsl(0 0% 100%); }
/* No @theme inline block -- bg-background won't exist */
```

正確：
```css
:root { --background: hsl(0 0% 100%); }
@theme inline { --color-background: var(--background); }
```

**#7 -- PostCSS vs Vite plugin**

錯誤：
```typescript
export default defineConfig({
  css: { postcss: './postcss.config.js' }  // Old v3 way
})
```

正確：
```typescript
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({
  plugins: [react(), tailwindcss()]  // v4 way
})
```

**#8 -- Path alias**

加到 `tsconfig.app.json`：
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

**#11 -- 用 cn() 工具函式合併 class**

錯誤：`` className={`base ${isActive && 'active'}`} ``
正確：`className={cn("base", isActive && "active")}`

`@/lib/utils` 的 `cn()` 會正確合併並去除重複的 Tailwind class。

**#12 -- Radix Select 的空值**

Radix UI Select 不允許空字串值。用 `value="placeholder"` 取代 `value=""`。

**#14 -- 必要的相依套件**

```json
{
  "dependencies": {
    "tailwindcss": "^4.1.0",
    "@tailwindcss/vite": "^4.1.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^3.3.1"
  },
  "devDependencies": {
    "@types/node": "^24.0.0"
  }
}
```

**#17 -- tw-animate-css**

`tailwindcss-animate` 在 Tailwind v4 已經棄用。shadcn/ui 文件可能還在引用它。會造成 build 失敗和 import 錯誤。改用 `tw-animate-css` 或 `@tailwindcss/motion`。

**#18 -- shadcn init 之後重複的 @layer base**

`shadcn init` 會加上它自己的 `@layer base` 區塊。跑完 init 之後馬上檢查 `src/index.css`，把重複的區塊合併成一個。

錯誤：
```css
@layer base { body { background-color: var(--background); } }
@layer base { * { border-color: hsl(var(--border)); } }  /* duplicate from shadcn */
```

正確：
```css
@layer base {
  * { border-color: var(--border); }
  body { background-color: var(--background); color: var(--foreground); }
}
```

### 預防檢查清單

- [ ] 沒有 `tailwind.config.ts` 檔案（或它是空的）
- [ ] `components.json` 有 `"config": ""`
- [ ] `:root` 裡所有顏色都有 `hsl()` 包裝
- [ ] `@theme inline` 對應了所有變數
- [ ] `@layer base` 沒有包住 `:root`
- [ ] Theme provider 包住整個 app
- [ ] 在 light、dark、system 模式下都測過
- [ ] 所有文字都有足夠的對比

---

## Dark Mode 測試檢查清單

- [ ] Light mode 顯示正確
- [ ] Dark mode 顯示正確
- [ ] System mode 會遵循作業系統設定
- [ ] 重新整理頁面後主題仍然保留
- [ ] 切換元件顯示目前狀態
- [ ] 所有文字都有適當的對比
- [ ] 載入時沒有錯誤主題閃一下
- [ ] 在無痕模式下也能運作（優雅降級）

---

## 資產檔案

從 `assets/` 目錄複製：
- `index.css`：完整的 CSS，含所有顏色變數
- `components.json`：shadcn/ui v4 設定
- `vite.config.ts`：Vite + Tailwind plugin
- `theme-provider.tsx`：Dark mode provider
- `utils.ts`：`cn()` 工具函式

## 參考檔案

- `references/migration-guide.md`：v3 到 v4 遷移

## 官方文件

- shadcn/ui Tailwind v4 指南：https://ui.shadcn.com/docs/tailwind-v4
- shadcn/ui Dark Mode（Vite）：https://ui.shadcn.com/docs/dark-mode/vite
- shadcn/ui Theming：https://ui.shadcn.com/docs/theming
- Tailwind v4 文件：https://tailwindcss.com/docs
- Tailwind Dark Mode：https://tailwindcss.com/docs/dark-mode
