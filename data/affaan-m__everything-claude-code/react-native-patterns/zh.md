---
name: react-native-patterns
description: React Native 與 Expo 應用程式模式：Expo Router 導覽、狀態分離（server／client／route／form）、搭配 Zod 的 TanStack Query 資料抓取、高效能列表、NativeWind／StyleSheet 樣式、原生 API，以及安全儲存。建置或編輯 React Native / Expo 的畫面、元件、導覽或資料層時使用。
origin: ECC
---

# React Native / Expo 模式

用 Expo 打造 production React Native 應用程式的實用模式。涵蓋導覽、狀態、資料抓取、列表、樣式和原生 API。搭配 `rules/react-native/` 規則集使用：規則講*要強制什麼*，這個 skill 示範*怎麼做*。

下面提到的函式庫（NativeWind、Zustand/Jotai、TanStack Query）都是常見、成熟的選項，只是拿來示範。重點是模式，不是特定套件，任何等價的都行。用 Zod 做驗證，是為了和 ECC 現有的 `typescript/` 規則保持一致。

這些模式假設用的是 managed Expo 工作流程（Expo Router、EAS、`expo-*` 模組），而且跑在 New Architecture 上（近期 Expo SDK 的預設，SDK 55+ 起強制）。它們**不**假設有瀏覽器 DOM：React Native 沒有 `<div>`、沒有網址列，也沒有網頁那套資料抓取預設值。

## 何時啟用

在以下情況使用這個 skill：

- 建置或編輯 React Native / Expo 的畫面、元件或導覽
- 用 Expo Router 設定路由（以檔案為基礎的 `app/` 目錄）
- 決定狀態該放哪（server 快取 vs client store vs route 參數 vs 表單）
- 用 TanStack Query 串資料抓取，並用 Zod 驗證回應
- 渲染很長或很重的列表
- 選擇或套用樣式做法（NativeWind 或 StyleSheet）
- 存取原生裝置 API（相機、位置、通知）或安全儲存
- Review RN 程式碼的行動裝置專屬問題

**不要**在這裡用 web／React-DOM 的模式：URL 當狀態、`<div>`、瀏覽器用的 SWR，都不適用於 React Native。

## 核心概念

### 專案結構（Expo Router）

`app/` 底下用檔案式路由。route 檔案要保持精簡：只讀取並驗證參數，然後委派給放在 `components/` 或 `features/` 的畫面元件。

```
app/
  _layout.tsx          # 根 stack
  (tabs)/
    _layout.tsx        # tab 導覽器
    index.tsx          # 首頁
  user/[id].tsx        # 動態路由
components/
features/
  user/UserProfile.tsx
```

### 導覽：驗證 route 參數

Deep link 和動態路由送進來的是不可信任的字串。用之前先用 Zod 驗證。

```tsx
// app/user/[id].tsx
import { useLocalSearchParams, router } from 'expo-router'
import { z } from 'zod'
import { UserProfile } from '@/features/user/UserProfile'

const Params = z.object({ id: z.string().uuid() })

export default function UserRoute() {
  const parsed = Params.safeParse(useLocalSearchParams())
  if (!parsed.success) {
    router.replace('/not-found')
    return null
  }
  return <UserProfile userId={parsed.data.id} />
}
```

### 狀態：把關注點分開

不要把 server 資料複製到 client store。每種關注點都有自己的家。

| 關注點 | 常見選擇 |
|---------|------|
| Server 狀態（遠端資料） | server 快取函式庫（TanStack Query、SWR） |
| Client／UI 狀態 | 輕量 store（Zustand、Jotai）或 Context |
| Route／導覽狀態 | Expo Router 參數 |
| 表單狀態 | 表單函式庫（例如 React Hook Form）加 schema 驗證 |
| Secret／token | `expo-secure-store` |
| 非機密的持久化 | `AsyncStorage` / MMKV |

狀態真的需要共享之前，優先用區域的 `useState`。

### 資料抓取：快取函式庫加 Zod

用 server 快取函式庫（TanStack Query、SWR），不要在 `useEffect` 裡 fetch。在邊界處驗證，並從 schema 推導型別。明確處理 loading、error 和空狀態。（範例用 TanStack Query。）

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'

const User = z.object({ id: z.string(), email: z.string().email() })
type User = z.infer<typeof User>

export function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: async (): Promise<User> => User.parse(await api.getUser(id)),
  })
}

export function useUpdateEmail(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (email: string) => api.updateEmail(id, email),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['user', id] }),
  })
}
```

### 列表：要虛擬化，絕對不要在 ScrollView 裡 map 大陣列

```tsx
import { FlatList } from 'react-native'

<FlatList
  data={items}
  keyExtractor={(item) => item.id}
  renderItem={renderItem}          // 已 memoize
  initialNumToRender={10}
  windowSize={5}
/>
```

大型或異質的列表用 `FlashList`（Shopify）。

### 樣式：挑一套系統

`StyleSheet.create()` 是框架原生的選項；utility class 函式庫（例如 NativeWind）是常見的替代方案。選一個，並保持一致。絕對不要在熱點路徑的 JSX 裡內聯建立 style 物件。

```tsx
// NativeWind
<View className="p-4 rounded-2xl bg-white">
  <Text className="text-base font-semibold">Hello</Text>
</View>

// StyleSheet
const styles = StyleSheet.create({ card: { padding: 16, borderRadius: 16, backgroundColor: '#fff' } })
<View style={styles.card}>...</View>
```

### 原生 API：包進 hook，並清理 effect

Expo SDK 的呼叫和訂閱要放在 `use*` hook 裡，不要放在 JSX。一定要清理。

```tsx
import { useEffect, useState } from 'react'
import * as Location from 'expo-location'

type LocationState =
  | { status: 'loading' }
  | { status: 'denied' }
  | { status: 'granted'; coords: Location.LocationObjectCoords }

export function useCurrentLocation() {
  // 追蹤狀態，不只是座標，這樣 UI 才能分辨「還在載入」
  // 和「權限被拒」，並顯示可以採取行動的訊息。
  const [state, setState] = useState<LocationState>({ status: 'loading' })

  useEffect(() => {
    let active = true
    ;(async () => {
      const { status } = await Location.requestForegroundPermissionsAsync()
      if (status !== 'granted') {
        if (active) setState({ status: 'denied' })
        return
      }
      const pos = await Location.getCurrentPositionAsync({})
      if (active) setState({ status: 'granted', coords: pos.coords })
    })()
    return () => { active = false }   // unmount 後忽略過期的結果
  }, [])

  return state
}
```

### Token 的安全儲存

```tsx
import * as SecureStore from 'expo-secure-store'

await SecureStore.setItemAsync('auth_token', token)   // Keychain / Keystore
const token = await SecureStore.getItemAsync('auth_token')
```

## 程式碼範例

### 完整畫面：route → query → 列表 → 各種狀態

```tsx
// app/(tabs)/orders.tsx
import { memo, useCallback } from 'react'
import { FlatList, Text, View } from 'react-native'
import { useQuery } from '@tanstack/react-query'
import { z } from 'zod'

const OrderSchema = z.object({ id: z.string(), total: z.number(), status: z.string() })
const OrdersSchema = z.array(OrderSchema)
type Order = z.infer<typeof OrderSchema>

function useOrders() {
  return useQuery({
    queryKey: ['orders'],
    queryFn: async () => OrdersSchema.parse(await api.listOrders()),
  })
}

// 已 memoize，讓它的 reference 在各次 render 間穩定（見列表的說明）。
const OrderRow = memo(function OrderRow({ item }: { item: Order }) {
  return (
    <View className="px-4 py-3 border-b border-neutral-200">
      <Text className="font-medium">#{item.id}</Text>
      <Text className="text-neutral-500">{item.status} · ${item.total}</Text>
    </View>
  )
})

export default function OrdersScreen() {
  const { data, isLoading, isError, refetch, isRefetching } = useOrders()
  const renderItem = useCallback(({ item }: { item: Order }) => <OrderRow item={item} />, [])

  if (isLoading) return <Centered><Text>Loading…</Text></Centered>
  if (isError) return <Centered><Text accessibilityRole="alert">Could not load orders.</Text></Centered>
  if (!data?.length) return <Centered><Text>No orders yet.</Text></Centered>

  return (
    <FlatList
      data={data}
      keyExtractor={(o) => o.id}
      onRefresh={refetch}
      refreshing={isRefetching}
      renderItem={renderItem}
    />
  )
}
```

### 表單：React Hook Form 加 Zod resolver

```tsx
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { TextInput, Button, Text } from 'react-native'

const Schema = z.object({ email: z.string().email('Invalid email') })
type FormValues = z.infer<typeof Schema>

export function EmailForm({ onSubmit }: { onSubmit: (v: FormValues) => void }) {
  const { control, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(Schema),
    defaultValues: { email: '' },
  })

  return (
    <>
      <Controller
        control={control}
        name="email"
        render={({ field: { value, onChange, onBlur } }) => (
          <TextInput
            value={value}
            onChangeText={onChange}
            onBlur={onBlur}
            autoCapitalize="none"
            keyboardType="email-address"
            accessibilityLabel="Email address"
          />
        )}
      />
      {errors.email && <Text accessibilityRole="alert">{errors.email.message}</Text>}
      <Button title="Save" onPress={handleSubmit(onSubmit)} />
    </>
  )
}
```

## 反模式

```tsx
// WRONG: 在 ScrollView 裡 map 大陣列（沒有虛擬化、卡頓、記憶體高）
<ScrollView>{items.map((i) => <Row key={i.id} item={i} />)}</ScrollView>
// RIGHT: FlatList / FlashList

// WRONG: server 資料複製到 client store（兩個真相來源、資料過期）
const useStore = create((set) => ({ users: [], setUsers: (u) => set({ users: u }) }))
useEffect(() => { getUsers().then(setUsers) }, [])
// RIGHT: 由 useQuery 持有 server 狀態；需要的東西用推導的

// WRONG: token 放在 AsyncStorage（沒有加密）
await AsyncStorage.setItem('auth_token', token)
// RIGHT: expo-secure-store

// WRONG: 信任 deep link 的參數
const { id } = useLocalSearchParams(); fetchUser(id)
// RIGHT: 用之前先用 Zod 驗證

// WRONG: 熱點路徑上每次 render 都重建 inline style 物件
<View style={{ padding: 16, backgroundColor: '#fff' }} />
// RIGHT: 在 module 範圍用 StyleSheet.create，或用 NativeWind className

// WRONG: 真正的 secret 被打包進 bundle
const STRIPE_SECRET = 'sk_live_...'
// RIGHT: 有特權的呼叫留在 server 端；只出貨受後端規則保護的公開 key
```

## 最佳實踐

- route 檔案保持精簡；邏輯放進畫面元件和 `use*` hook。
- 每個外部輸入（API 回應、route 參數、push payload）都用 Zod 驗證。
- 讓 TanStack Query 持有 server 狀態；client store 保持小。
- 一定要渲染 loading、error 和空狀態，絕對不要只放一個沒有 fallback 的 spinner。
- 列表要虛擬化；`renderItem` 要 memoize；提供穩定的 `keyExtractor`。
- 動畫用 `react-native-reanimated`（UI thread）；避免在 JS thread 做重活。
- token 存在 `expo-secure-store`；授權絕對不要信任 client。
- 從一開始就顧到 safe area、Dynamic Type 和無障礙的 role／label。
- 每個原生依賴在發佈前，都要確認和 New Architecture 相容。

## 相關 skill

- `frontend-patterns`：React/Next.js（web）模式；共通的 React 概念可以參考，但那些是 DOM 專屬的。
- `coding-standards`：適用於 RN 程式碼的 TypeScript/JavaScript 慣用寫法。
- `tdd-workflow`、`e2e-testing`：測試流程（RN 用 Jest 加 React Native Testing Library，Maestro/Detox 做 e2e）。
- `security-review`：通用的安全檢查清單，補充上面 RN bundle／secret 的指引。
