---
name: design-system-patterns
description: 用 design token、theming 基礎設施與元件架構模式，建立可擴充的設計系統。適用於建立 design token、實作主題切換、建構元件庫，或奠定設計系統基礎的時候。
---

# 設計系統模式

精通設計系統架構，為 web 與行動應用打造一致、好維護又可擴充的 UI 基礎。

## 什麼時候用這個 Skill

- 為顏色、字型、間距和陰影建立 design token
- 用 CSS custom properties 實作亮色/暗色主題切換
- 建構多品牌的 theming 系統
- 設計 API 一致的元件庫架構
- 用 Figma token 建立設計到程式碼的工作流程
- 建立語意化的 token 階層（primitive、semantic、component）
- 建立設計系統的文件與指南

## 核心能力

### 1. Design Token

- Primitive token（原始值：顏色、尺寸、字型）
- Semantic token（有情境意義：text-primary、surface-elevated）
- Component token（特定用途：button-bg、card-border）
- Token 命名慣例與組織方式
- 多平台 token 產生（CSS、iOS、Android）

### 2. Theming 基礎設施

- CSS custom properties 架構
- React 中的 theme context provider
- 動態主題切換
- 偵測系統偏好（prefers-color-scheme）
- 持久化的主題儲存
- Reduced motion 與高對比模式

### 3. 元件架構

- Compound component 模式
- Polymorphic component（as prop）
- Variant 與 size 系統
- 以 slot 為基礎的組合
- Headless UI 模式
- Style props 與響應式 variant

### 4. Token Pipeline

- Figma 到程式碼的同步
- Style Dictionary 設定
- Token 的轉換與格式化
- 用 CI/CD 整合 token 更新

## 快速開始

```typescript
// 用 CSS custom properties 做 design token
const tokens = {
  colors: {
    // Primitive token
    gray: {
      50: "#fafafa",
      100: "#f5f5f5",
      900: "#171717",
    },
    blue: {
      500: "#3b82f6",
      600: "#2563eb",
    },
  },
  // Semantic token（參照 primitive）
  semantic: {
    light: {
      "text-primary": "var(--color-gray-900)",
      "text-secondary": "var(--color-gray-600)",
      "surface-default": "var(--color-white)",
      "surface-elevated": "var(--color-gray-50)",
      "border-default": "var(--color-gray-200)",
      "interactive-primary": "var(--color-blue-500)",
    },
    dark: {
      "text-primary": "var(--color-gray-50)",
      "text-secondary": "var(--color-gray-400)",
      "surface-default": "var(--color-gray-900)",
      "surface-elevated": "var(--color-gray-800)",
      "border-default": "var(--color-gray-700)",
      "interactive-primary": "var(--color-blue-400)",
    },
  },
};
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務

1. **依用途命名 token**：用語意化的名稱（text-primary），不要用視覺描述（dark-gray）
2. **維持 token 階層**：Primitive > Semantic > Component token
3. **記錄 token 用法**：在 token 定義旁附上使用指南
4. **為 token 版本化**：把 token 的變動當成 API 變動，用 semver
5. **測試主題組合**：確認所有主題搭配所有元件都能正常運作
6. **自動化 token pipeline**：用 CI/CD 做 Figma 到程式碼的同步
7. **提供 migration 路徑**：逐步 deprecate token，並給出明確的替代方案

## 常見問題

- **Token 氾濫**：token 太多、卻沒有清楚的階層
- **命名不一致**：混用不同慣例（camelCase vs kebab-case）
- **缺少暗色模式**：token 不會隨主題改變
- **寫死的值**：直接用原始值而不是 token
- **循環參照**：token 彼此互相參照形成迴圈
- **平台落差**：某些平台缺少 token（有 web 沒有 mobile）
