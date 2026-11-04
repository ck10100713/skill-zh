---
name: react-native
description: "打造高效能行動 app 的 React Native 與 Expo 模式。涵蓋列表效能、用 Reanimated 做動畫、導覽、UI 模式、狀態管理、平台專屬程式碼和 Expo 工作流程。在建置或審查 React Native 程式碼時使用。觸發詞：'react native'、'expo'、'mobile app'、'react native performance'、'flatlist'、'reanimated'、'expo router'、'mobile development'、'ios app'、'android app'。"
compatibility: claude-code-only
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# React Native 模式

React Native + Expo app 的效能與架構模式。規則依影響程度排序：先修 CRITICAL，再碰 MEDIUM。

這只是個起點。你做越多行動 app，這個 skill 就會越長越多。

## 什麼時候套用

- 建立新的 React Native 或 Expo app
- 優化列表和捲動效能
- 實作動畫
- 審查行動端程式碼的效能問題
- 設定新的 Expo 專案

## 1. 列表效能（CRITICAL）

列表是 React Native 的第一大效能問題。捲動一卡，整個 app 的體驗就毀了。

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **用 ScrollView 放資料** | `<ScrollView>` 會一次渲染所有項目 | 用 `<FlatList>` 或 `<FlashList>`，它們有虛擬化，只渲染看得到的項目 |
| **缺少 keyExtractor** | FlatList 沒有 `keyExtractor` → 不必要的重新渲染 | `keyExtractor={(item) => item.id}`，每個項目一個穩定且唯一的 key |
| **複雜的 renderItem** | renderItem 裡昂貴的元件每次捲動都重新渲染 | 包在 `React.memo` 裡，抽成獨立元件 |
| **renderItem 裡的 inline 函式** | `renderItem={({ item }) => <Row onPress={() => nav(item.id)} />}` | 抽出 handler：`const handlePress = useCallback(...)` |
| **沒有 getItemLayout** | FlatList 捲動時要量測每個項目（很昂貴） | 對固定高度的項目提供 `getItemLayout`：`(data, index) => ({ length: 80, offset: 80 * index, index })` |
| **FlashList** | FlatList 不錯，大型列表用 FlashList 更好 | `@shopify/flash-list`：可直接替換，採用回收機制架構 |
| **列表中的大圖片** | 全解析度圖片在主執行緒解碼 | 用 `expo-image`，加上 placeholder + transition，並指定尺寸 |

### FlatList 檢查清單

每個 FlatList 都應該有：
```tsx
<FlatList
  data={items}
  keyExtractor={(item) => item.id}
  renderItem={renderItem}           // Memoised component
  getItemLayout={getItemLayout}     // If items are fixed height
  initialNumToRender={10}           // Don't render 100 items on mount
  maxToRenderPerBatch={10}          // Batch size for off-screen rendering
  windowSize={5}                    // How many screens to keep in memory
  removeClippedSubviews={true}      // Unmount off-screen items (Android)
/>
```

## 2. 動畫（HIGH）

原生動畫在 UI 執行緒上跑。JS 動畫會卡住 JS 執行緒，造成卡頓。

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **用 Animated API 做複雜動畫** | `Animated` 在 JS 執行緒上跑，會阻擋互動 | 用 `react-native-reanimated`，它在 UI 執行緒上跑 |
| **版面動畫** | 項目出現/消失時沒有轉場 | `LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut)` |
| **共享元素轉場** | 在畫面之間導覽時，元素瞬間跳過去 | `react-native-reanimated` 的共享轉場，或 `expo-router` 的共享元素 |
| **手勢 + 動畫** | 拖曳/滑動感覺卡頓 | `react-native-gesture-handler` + `reanimated` worklet，全部在 UI 執行緒上 |
| **量測版面** | `onLayout` 觸發太晚，造成閃爍 | 用 `useAnimatedStyle` 搭配 shared value 即時回應 |

### Reanimated 基礎

```tsx
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';

function AnimatedBox() {
  const offset = useSharedValue(0);
  const style = useAnimatedStyle(() => ({
    transform: [{ translateX: withSpring(offset.value) }],
  }));

  return (
    <GestureDetector gesture={panGesture}>
      <Animated.View style={[styles.box, style]} />
    </GestureDetector>
  );
}
```

## 3. 導覽（HIGH）

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **Expo Router** | React Native 用的檔案式路由（像 Next.js） | 用 `app/` 目錄搭配 `_layout.tsx` 檔案。新的 Expo 專案優先用這個。 |
| **堆疊裡的重型畫面** | 每個畫面都一直掛載在堆疊裡 | 對不需要保留的畫面用 `unmountOnBlur: true` |
| **Deep linking** | App 對 URL 沒反應 | Expo Router 會自動處理。純 RN 則設定 `Linking` API |
| **分頁徽章更新** | 切到該分頁時，徽章數字沒更新 | 用 `useIsFocused()`，或在 focus 時重新取資料：`useFocusEffect(useCallback(...))` |
| **導覽狀態持久化** | App 進背景/被關掉後，位置就丟了 | `onStateChange` + 搭配 AsyncStorage 的 `initialState` |

### Expo Router 結構

```
app/
├── _layout.tsx          # Root layout (tab navigator)
├── index.tsx            # Home tab
├── (tabs)/
│   ├── _layout.tsx      # Tab bar config
│   ├── home.tsx
│   ├── search.tsx
│   └── profile.tsx
├── [id].tsx             # Dynamic route
└── modal.tsx            # Modal route
```

## 4. UI 模式（HIGH）

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **Safe area** | 內容被瀏海或 home indicator 蓋住 | 用 `<SafeAreaView>`，或 `react-native-safe-area-context` 的 `useSafeAreaInsets()` |
| **避開鍵盤** | 表單欄位被鍵盤擋住 | `<KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>` |
| **平台專屬程式碼** | iOS 和 Android 需要不同行為 | `Platform.select({ ios: ..., android: ... })`，或 `.ios.tsx` / `.android.tsx` 檔案 |
| **狀態列** | 狀態列蓋住內容，或顏色不對 | 在 root layout 用 `expo-status-bar` 的 `<StatusBar style="auto" />` |
| **觸控目標** | 按鈕太小點不到 | 最小 44x44pt。用 `hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}` |
| **觸覺回饋** | 點擊感覺死板 | `expo-haptics`：重要動作上用 `Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)` |

## 5. 圖片與媒體（MEDIUM）

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **Image 元件** | react-native 的 `<Image>` 功能很基本 | 用 `expo-image`：有快取、placeholder、轉場、blurhash |
| **遠端圖片沒有尺寸** | 圖片載入時版面位移 | 一定要指定 `width` 和 `height`，或用 `aspectRatio` |
| **大圖片** | Android 上 OOM 當掉 | 在伺服器端縮圖，或用會處理記憶體的 `expo-image` |
| **SVG** | SVG 支援不是原生的 | `react-native-svg` + `react-native-svg-transformer` 來 import SVG |
| **影片** | 影片播放 | `expo-av` 或 `expo-video`（較新的 API） |

## 6. 狀態與資料（MEDIUM）

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **用 AsyncStorage 存複雜資料** | 每次讀取都要 JSON parse/stringify | 用 MMKV（`react-native-mmkv`），比 AsyncStorage 快 30 倍 |
| **全域狀態** | 簡單的狀態卻要 Redux/MobX 的一堆樣板程式碼 | Zustand：極簡，跟 React Native 搭配得很好 |
| **伺服器狀態** | 手動 fetch + loading + error + cache | TanStack Query：跟 web 一樣，在 React Native 也能用 |
| **離線優先** | 沒網路 app 就不能用 | TanStack Query 的 `persistQueryClient` + MMKV，複雜的離線需求用 WatermelonDB |
| **深層狀態更新** | 巢狀物件展開運算子地獄 | 透過 Zustand 用 Immer：`set(produce(state => { state.user.name = 'new' }))` |

## 7. Expo 工作流程（MEDIUM）

| 模式 | 什麼時候 | 怎麼做 |
|---------|------|-----|
| **Development build** | 需要原生模組 | `npx expo run:ios` 或 `eas build --profile development` |
| **Expo Go** | 快速做原型，沒有原生模組 | `npx expo start`：掃 QR code |
| **EAS Build** | CI/CD、app store 的 build | `eas build --platform ios --profile production` |
| **EAS Update** | 不經 app store 審核的 hot fix | `eas update --branch production --message "Fix bug"` |
| **Config plugin** | 不用 eject 就能修改原生設定 | 用 `app.config.ts` 搭配 `expo-build-properties` 或自訂 config plugin |
| **環境變數** | 每個 build 用不同設定 | `eas.json` 的 build profile + `expo-constants` |

### 新專案設定

```bash
npx create-expo-app my-app --template tabs
cd my-app
npx expo install expo-image react-native-reanimated react-native-gesture-handler react-native-safe-area-context
```

## 8. 測試（LOW-MEDIUM）

| 工具 | 用途 | 設定 |
|------|-----|-------|
| **Jest** | 單元測試、hook 測試 | Expo 預設就內建 |
| **React Native Testing Library** | 元件測試 | `@testing-library/react-native` |
| **Detox** | 在真機/模擬器上做 E2E 測試 | `detox`：Wix 的測試框架 |
| **Maestro** | 用 YAML 流程做 E2E | `maestro test flow.yaml`：比 Detox 簡單 |

## 常見陷阱

| 陷阱 | 修法 |
|--------|-----|
| Metro bundler 快取 | `npx expo start --clear` |
| Pod install 問題（iOS） | `cd ios && pod install --repo-update` |
| Reanimated 沒作用 | 必須是第一個 import：在 root 裡 `import 'react-native-reanimated'` |
| Expo SDK 升級 | 更新 SDK 版本後執行 `npx expo install --fix` |
| Android build 失敗 | 檢查 `gradle.properties` 的記憶體設定：`org.gradle.jvmargs=-Xmx4g` |
| iOS 模擬器很慢 | 效能測試要用實體裝置，模擬器不能反映真實效能 |
