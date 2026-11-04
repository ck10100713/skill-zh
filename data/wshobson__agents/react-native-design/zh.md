---
name: react-native-design
description: 精通 React Native 的樣式、navigation 和 Reanimated 動畫，用於跨平台行動開發。在建構 React Native 應用、實作 navigation 模式或建立高效能動畫時使用。
---

# React Native Design

精通 React Native 的樣式模式、React Navigation 和 Reanimated 3，打造高效能、跨平台、有原生品質使用體驗的行動應用。

## When to Use This Skill

- 用 React Native 建構跨平台行動應用
- 用 React Navigation 6+ 實作 navigation
- 用 Reanimated 3 建立高效能動畫
- 用 StyleSheet 和 styled-components 設定元件樣式
- 為不同螢幕尺寸建構響應式版面
- 實作各平台專屬的設計（iOS/Android）
- 用 Gesture Handler 建立手勢驅動的互動
- 優化 React Native 效能

## Detailed section: Core Concepts

原本是這份 SKILL.md 裡一段 6471 bytes 的內容，為了符合 Codex 對 skill 本文 8 KB 的上限，已經搬到 `references/details.md`。

## Quick Start Component

```typescript
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  Image,
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

interface ItemCardProps {
  title: string;
  subtitle: string;
  imageUrl: string;
  onPress: () => void;
}

const AnimatedPressable = Animated.createAnimatedComponent(Pressable);

export function ItemCard({ title, subtitle, imageUrl, onPress }: ItemCardProps) {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <AnimatedPressable
      style={[styles.card, animatedStyle]}
      onPress={onPress}
      onPressIn={() => { scale.value = withSpring(0.97); }}
      onPressOut={() => { scale.value = withSpring(1); }}
    >
      <Image source={{ uri: imageUrl }} style={styles.image} />
      <View style={styles.content}>
        <Text style={styles.title} numberOfLines={1}>
          {title}
        </Text>
        <Text style={styles.subtitle} numberOfLines={2}>
          {subtitle}
        </Text>
      </View>
    </AnimatedPressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  image: {
    width: '100%',
    height: 160,
    backgroundColor: '#f3f4f6',
  },
  content: {
    padding: 16,
    gap: 4,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
});
```

## Best Practices

1. **用 TypeScript**：定義 navigation 和 prop 的型別，確保型別安全
2. **Memoize component**：用 `React.memo` 和 `useCallback` 避免不必要的 rerender
3. **讓動畫跑在 UI thread**：用 Reanimated worklet 跑 60fps 動畫
4. **避免 inline style**：為了效能，用 StyleSheet.create
5. **處理 safe area**：用 `SafeAreaView` 或 `useSafeAreaInsets`
6. **在真機上測試**：模擬器的效能跟真機不一樣
7. **列表用 FlatList**：長列表絕對不要用 ScrollView 加 map
8. **平台專屬程式碼**：iOS/Android 的差異用 Platform.select

## Common Issues

- **手勢衝突**：用 `GestureDetector` 包住手勢，並使用 `simultaneousHandlers`
- **Navigation 型別錯誤**：為所有 navigator 定義 `ParamList` 型別
- **動畫卡頓**：用 `runOnUI` worklet 把動畫搬到 UI thread
- **記憶體洩漏**：在 useEffect 裡取消動畫並做清理
- **字型載入**：自訂字型用 `expo-font` 或 `react-native-asset`
- **Safe area 問題**：在有瀏海的裝置上測試（iPhone、有挖孔的 Android）
