---
name: shadcn-ui
description: "為 React 專案安裝並設定 shadcn/ui 元件。引導元件選擇、安裝順序、相依套件管理、用語意 token 客製化，以及常見的 UI 配方（表單、資料表格、導覽、modal）。在 tailwind-theme-builder 把主題基礎建設設好之後使用，適用於新增元件、做表單、建資料表格或設定導覽列。"
compatibility: claude-code-only
---

# shadcn/ui 元件

把 shadcn/ui 元件加進已經有主題的 React 專案。這個 skill 在 `tailwind-theme-builder` 把 CSS 變數、ThemeProvider 和 dark mode 設好**之後**才執行。它負責元件安裝、客製化，以及把元件組合成可用的模式。

**前置條件**：主題基礎建設要先存在（CSS 變數、components.json、cn() 工具函式）。還沒設的話先用 `tailwind-theme-builder`。

## 安裝順序

照相依順序安裝元件。先裝基礎元件，再裝功能元件：

### 基礎元件（先裝）

```bash
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add input label
pnpm dlx shadcn@latest add card
```

### 功能元件（需要時再裝）

```bash
# Forms
pnpm dlx shadcn@latest add form        # needs: react-hook-form, zod, @hookform/resolvers
pnpm dlx shadcn@latest add textarea select checkbox switch

# Feedback
pnpm dlx shadcn@latest add toast        # needs: sonner
pnpm dlx shadcn@latest add alert badge

# Overlay
pnpm dlx shadcn@latest add dialog sheet popover dropdown-menu

# Data Display
pnpm dlx shadcn@latest add table        # for data tables, also: @tanstack/react-table
pnpm dlx shadcn@latest add tabs separator avatar

# Navigation
pnpm dlx shadcn@latest add navigation-menu command
```

### 外部相依套件

| 元件 | 需要 |
|-----------|----------|
| Form | `react-hook-form`、`zod`、`@hookform/resolvers` |
| Toast | `sonner` |
| Data Table | `@tanstack/react-table` |
| Command | `cmdk` |
| Date Picker | `date-fns`（選用） |

外部套件另外裝：`pnpm add react-hook-form zod @hookform/resolvers`

## 已知陷阱

以下是已經確認過的修正方式，可以避開常見的 bug：

### Radix Select：不能用空字串

```tsx
// Don't use empty string values
<SelectItem value="">All</SelectItem>           // BREAKS

// Use sentinel value
<SelectItem value="__any__">All</SelectItem>    // WORKS
const actual = value === "__any__" ? "" : value
```

### React Hook Form：null 值

```tsx
// Don't spread {...field} — it passes null which Input rejects
<Input
  value={field.value ?? ''}
  onChange={field.onChange}
  onBlur={field.onBlur}
  name={field.name}
  ref={field.ref}
/>
```

### Lucide Icons：tree-shaking

```tsx
// Don't use dynamic import — icons get tree-shaken in production
import * as LucideIcons from 'lucide-react'
const Icon = LucideIcons[iconName]  // BREAKS in prod

// Use explicit map
import { Home, Users, Settings, type LucideIcon } from 'lucide-react'
const ICON_MAP: Record<string, LucideIcon> = { Home, Users, Settings }
const Icon = ICON_MAP[iconName]
```

### Dialog 寬度覆寫

```tsx
// Default sm:max-w-lg won't be overridden by max-w-6xl
<DialogContent className="max-w-6xl">       // DOESN'T WORK

// Use same breakpoint prefix
<DialogContent className="sm:max-w-6xl">    // WORKS
```

## 客製化元件

shadcn 元件用的是你主題裡的語意 CSS token。要客製化的話：

### 擴充 variant

編輯 `src/components/ui/` 裡的元件檔案來加自訂 variant：

```tsx
// button.tsx — add a "brand" variant
const buttonVariants = cva("...", {
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground",
      brand: "bg-brand text-brand-foreground hover:bg-brand/90",
      // ... existing variants
    },
  },
})
```

### 顏色覆寫

用主題裡的語意 token，絕對不要直接用 Tailwind 原始顏色：

```tsx
// Don't use raw colours
<Button className="bg-blue-500">             // WRONG

// Use semantic tokens
<Button className="bg-primary">              // RIGHT
<Card className="bg-card text-card-foreground">  // RIGHT
```

## 工作流程

### 步驟 1：評估需求

判斷專案需要哪些 UI 模式：

| 需求 | 元件 |
|------|-----------|
| 有驗證的表單 | Form、Input、Label、Select、Textarea、Button、Toast |
| 可排序的資料顯示 | Table、Badge、Pagination |
| 後台 CRUD 介面 | Dialog、Form、Table、Button、Toast |
| 行銷/landing page | Card、Button、Badge、Separator |
| 設定/偏好 | Tabs、Form、Switch、Select、Toast |
| 導覽 | NavigationMenu（桌面版）、Sheet（行動版）、ModeToggle |

### 步驟 2：安裝元件

先裝基礎元件，再依上面判斷出的需求裝功能元件。用上面的指令。

### 步驟 3：組出配方

把元件組合成可用的模式。完整的可用範例看 [references/recipes.md](references/recipes.md)：

- **聯絡表單**：Form + Input + Textarea + Button + Toast
- **資料表格**：Table + 欄位排序 + Pagination + 搜尋
- **Modal CRUD**：Dialog + Form + Button
- **導覽**：Sheet + NavigationMenu + ModeToggle
- **設定頁**：Tabs + Form + Switch + Select + Toast

### 步驟 4：客製化

用主題裡的語意 token 套用專案專屬的顏色和 variant。

## 參考檔案

| 時機 | 讀這個 |
|------|------|
| 選元件、安裝指令、props | [references/component-catalogue.md](references/component-catalogue.md) |
| 建立完整的 UI 模式 | [references/recipes.md](references/recipes.md) |
