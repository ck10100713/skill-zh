---
name: ui-styling
description: 用 shadcn/ui 元件（建構在 Radix UI + Tailwind 上）、Tailwind CSS 的 utility-first 樣式，以及基於 canvas 的視覺設計，打造漂亮又無障礙的使用者介面。用於建構使用者介面、實作設計系統、建立響應式版面、加入無障礙元件（dialog、dropdown、表單、表格）、客製主題與色彩、實作深色模式、產生視覺設計與海報，或在整個應用程式建立一致的樣式模式。
argument-hint: "[component or layout]"
license: MIT
metadata:
  author: claudekit
  version: "1.0.0"
---

# UI Styling Skill

結合 shadcn/ui 元件、Tailwind CSS utility 樣式和基於 canvas 的視覺設計系統，打造漂亮又無障礙使用者介面的完整 skill。

## 參考

- shadcn/ui: https://ui.shadcn.com/llms.txt
- Tailwind CSS: https://tailwindcss.com/docs

## 何時使用這個 Skill

在以下情況使用：
- 用 React 系的框架（Next.js、Vite、Remix、Astro）建構 UI
- 實作無障礙元件（dialog、表單、表格、導覽）
- 用 utility-first 的 CSS 方式寫樣式
- 建立響應式、mobile-first 的版面
- 實作深色模式與主題客製
- 用一致的 token 建構設計系統
- 產生視覺設計、海報或品牌素材
- 快速做原型並立即得到視覺回饋
- 加入複雜的 UI 模式（資料表格、圖表、command palette）

## 核心技術棧

### 元件層：shadcn/ui
- 透過 Radix UI primitive 提供預先做好的無障礙元件
- 複製貼上的發佈模式（元件就放在你的程式碼庫裡）
- TypeScript 優先，有完整的型別安全
- 可組合的 primitive，用來搭建複雜的 UI
- 以 CLI 安裝與管理

### 樣式層：Tailwind CSS
- Utility-first 的 CSS 框架
- 在 build 時處理，沒有 runtime 負擔
- Mobile-first 的響應式設計
- 一致的 design token（色彩、間距、字體）
- 自動移除沒用到的程式碼

### 視覺設計層：Canvas
- 博物館等級的視覺構圖
- 以設計哲學為導向的做法
- 精緻的視覺溝通
- 文字極少，視覺衝擊最大
- 系統化的圖案與細緻的美感

## Script 路徑

這個 skill 及其 `references/` 裡的 script 路徑，都是相對於包含這個 SKILL.md 的目錄，不是相對於專案：`scripts/<file>` 指這個 skill 自己的 `scripts/` 資料夾，`../<skill>/scripts/<file>` 指跟它一起安裝的同層子 skill。請從那個目錄組出完整路徑（skill 載入時 Claude Code 會回報它的 base directory），而且工作目錄要維持在專案根目錄，因為 script 會讀寫相對於它的專案檔案，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`。

## 快速開始

### 元件 + 樣式設定

**安裝 shadcn/ui 與 Tailwind：**
```bash
npx shadcn@latest init
```

CLI 會詢問框架、TypeScript、路徑和主題偏好。這樣會同時設定好 shadcn/ui 和 Tailwind CSS。

**加入元件：**
```bash
npx shadcn@latest add button card dialog form
```

**搭配 utility 樣式使用元件：**
```tsx
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export function Dashboard() {
  return (
    <div className="container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Analytics</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">View your metrics</p>
          <Button variant="default" className="w-full">
            View Details
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
```

### 替代方案：只用 Tailwind 的設定

**Vite 專案：**
```bash
npm install -D tailwindcss @tailwindcss/vite
```

```javascript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
export default { plugins: [tailwindcss()] }
```

```css
/* src/index.css */
@import "tailwindcss";
```

## 元件庫指南

**完整的元件目錄，含使用模式、安裝方式和組合範例。**

參見：`references/shadcn-components.md`

涵蓋：
- 表單與輸入元件（Button、Input、Select、Checkbox、Date Picker、表單驗證）
- 版面與導覽（Card、Tabs、Accordion、Navigation Menu）
- 浮層與對話框（Dialog、Drawer、Popover、Toast、Command）
- 回饋與狀態（Alert、Progress、Skeleton）
- 顯示元件（Table、Data Table、Avatar、Badge）

## 主題與客製

**主題設定、CSS 變數、深色模式實作和元件客製。**

參見：`references/shadcn-theming.md`

涵蓋：
- 用 next-themes 設定深色模式
- CSS 變數系統
- 色彩客製與調色盤
- 元件變體客製
- 主題切換的實作

## 無障礙模式

**ARIA 模式、鍵盤導覽、螢幕閱讀器支援，以及無障礙元件的使用。**

參見：`references/shadcn-accessibility.md`

涵蓋：
- Radix UI 的無障礙功能
- 鍵盤導覽模式
- 焦點管理
- 螢幕閱讀器播報
- 表單驗證的無障礙

## Tailwind Utility

**版面、間距、字體、色彩、邊框和陰影的核心 utility class。**

參見：`references/tailwind-utilities.md`

涵蓋：
- 版面 utility（Flexbox、Grid、定位）
- 間距系統（padding、margin、gap）
- 字體（字級、字重、對齊、行高）
- 色彩與背景
- 邊框與陰影
- 任意值，用於客製樣式

## 響應式設計

**Mobile-first 斷點、響應式 utility 和自適應版面。**

參見：`references/tailwind-responsive.md`

涵蓋：
- Mobile-first 做法
- 斷點系統（sm、md、lg、xl、2xl）
- 響應式 utility 模式
- Container query
- Max-width query
- 自訂斷點

## Tailwind 客製

**設定檔結構、自訂 utility、plugin 和主題擴充。**

參見：`references/tailwind-customization.md`

涵蓋：
- 用 @theme directive 定義自訂 token
- 自訂色彩與字型
- 間距與斷點的擴充
- 建立自訂 utility
- 自訂 variant
- Layer 的組織（@layer base、components、utilities）
- 用 apply directive 抽出元件

## 視覺設計系統

**基於 canvas 的設計哲學、視覺溝通原則和精緻的構圖。**

參見：`references/canvas-design-system.md`

涵蓋：
- 設計哲學的做法
- 視覺溝通重於文字
- 系統化的圖案與構圖
- 色彩、形式和空間設計
- 少量文字的整合
- 博物館等級的執行品質
- 多頁設計系統

## Utility Scripts

**用 Python 自動化元件安裝和設定檔生成。**

### shadcn_add.py
加入 shadcn/ui 元件，並處理依賴：
```bash
python scripts/shadcn_add.py button card dialog
```

### tailwind_config_gen.py
產生含自訂主題的 tailwind.config.js：
```bash
python scripts/tailwind_config_gen.py --colors brand:blue --fonts display:Inter
```

只要同層已經有任何 `tailwind.config.js`、`.cjs`、`.mjs` 或 `.ts` 檔，這個產生器就會拒絕建立或取代設定檔。先檢查回報的設定檔，確定要用另一份輸出時，才加上 `--force`：
```bash
python scripts/tailwind_config_gen.py --colors brand:blue --force
```

## 最佳實務

1. **元件組合**：用簡單、可組合的 primitive 搭建複雜的 UI
2. **Utility-First 樣式**：直接用 Tailwind class；真的有重複才抽成元件
3. **Mobile-First 響應式**：先寫手機版樣式，再疊上響應式 variant
4. **無障礙優先**：善用 Radix UI primitive、加上 focus 狀態、使用語意化 HTML
5. **Design Token**：用一致的間距級距、調色盤、字體系統
6. **深色模式一致性**：所有有主題的元素都套用 dark variant
7. **效能**：善用自動的 CSS purge，避免動態組出 class 名稱
8. **TypeScript**：用完整的型別安全，開發體驗更好
9. **視覺層級**：讓構圖引導注意力，有意識地運用間距和色彩
10. **專業工藝**：每個細節都重要，把 UI 當成一門手藝

## 參考導覽

**元件庫**
- `references/shadcn-components.md` - 完整的元件目錄
- `references/shadcn-theming.md` - 主題與客製
- `references/shadcn-accessibility.md` - 無障礙模式

**樣式系統**
- `references/tailwind-utilities.md` - 核心 utility class
- `references/tailwind-responsive.md` - 響應式設計
- `references/tailwind-customization.md` - 設定與擴充

**視覺設計**
- `references/canvas-design-system.md` - 設計哲學與 canvas 工作流程

**自動化**
- `scripts/shadcn_add.py` - 元件安裝
- `scripts/tailwind_config_gen.py` - 設定檔生成

## 常見模式

**含驗證的表單：**
```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export function LoginForm() {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" }
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-6">
        <FormField control={form.control} name="email" render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="email" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" className="w-full">Sign In</Button>
      </form>
    </Form>
  )
}
```

**支援深色模式的響應式版面：**
```tsx
<div className="min-h-screen bg-white dark:bg-gray-900">
  <div className="container mx-auto px-4 py-8">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            Content
          </h3>
        </CardContent>
      </Card>
    </div>
  </div>
</div>
```

## 資源

- shadcn/ui Docs: https://ui.shadcn.com
- Tailwind CSS Docs: https://tailwindcss.com
- Radix UI: https://radix-ui.com
- Tailwind UI: https://tailwindui.com
- Headless UI: https://headlessui.com
- v0 (AI UI Generator): https://v0.dev
