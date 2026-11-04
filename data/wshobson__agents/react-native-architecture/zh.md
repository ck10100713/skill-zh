---
name: react-native-architecture
description: 用 Expo、navigation、原生模組、離線同步和跨平台模式，建構正式環境等級的 React Native 應用。在開發行動應用、實作原生整合或規劃 React Native 專案架構時使用。
---

# React Native Architecture

用 Expo 開發 React Native 的正式環境等級模式，包含 navigation、狀態管理、原生模組和 offline-first 架構。

## When to Use This Skill

- 開始一個新的 React Native 或 Expo 專案
- 實作複雜的 navigation 模式
- 整合原生模組和平台 API
- 建構 offline-first 的行動應用
- 優化 React Native 效能
- 為行動版發布設定 CI/CD

## Core Concepts

### 1. Project Structure

```
src/
├── app/                    # Expo Router screens
│   ├── (auth)/            # Auth group
│   ├── (tabs)/            # Tab navigation
│   └── _layout.tsx        # Root layout
├── components/
│   ├── ui/                # Reusable UI components
│   └── features/          # Feature-specific components
├── hooks/                 # Custom hooks
├── services/              # API and native services
├── stores/                # State management
├── utils/                 # Utilities
└── types/                 # TypeScript types
```

### 2. Expo vs Bare React Native

| Feature            | Expo           | Bare RN        |
| ------------------ | -------------- | -------------- |
| Setup complexity   | Low            | High           |
| Native modules     | EAS Build      | Manual linking |
| OTA updates        | Built-in       | Manual setup   |
| Build service      | EAS            | Custom CI      |
| Custom native code | Config plugins | Direct access  |

## Quick Start

```bash
# Create new Expo project
npx create-expo-app@latest my-app -t expo-template-blank-typescript

# Install essential dependencies
npx expo install expo-router expo-status-bar react-native-safe-area-context
npx expo install @react-native-async-storage/async-storage
npx expo install expo-secure-store expo-haptics
```

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router'
import { ThemeProvider } from '@/providers/ThemeProvider'
import { QueryProvider } from '@/providers/QueryProvider'

export default function RootLayout() {
  return (
    <QueryProvider>
      <ThemeProvider>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
        </Stack>
      </ThemeProvider>
    </QueryProvider>
  )
}
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Best Practices

### Do's

- **用 Expo** - 開發更快、有 OTA 更新、原生程式碼由平台代管
- **用 FlashList 取代 FlatList** - 長列表的效能更好
- **Memoize component** - 避免不必要的 re-render
- **用 Reanimated** - 在原生執行緒上跑 60fps 動畫
- **在真機上測試** - 模擬器抓不到真實世界的問題

### Don'ts

- **不要寫 inline style** - 為了效能，用 StyleSheet.create
- **不要在 render 裡抓資料** - 用 useEffect 或 React Query
- **不要忽略平台差異** - iOS 和 Android 都要測
- **不要把 secret 寫進程式碼** - 用環境變數
- **不要省略 error boundary** - 行動端當機不會留情面
