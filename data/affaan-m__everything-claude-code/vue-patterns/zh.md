---
name: vue-patterns
description: Vue.js 3 Composition API 的各種模式、component 架構、reactivity 最佳實務、Pinia 狀態管理、Vue Router 導覽，以及 Nuxt SSR 模式。處理 Vue、Nuxt、Vite 或 Pinia 專案時啟用。建置或 review Vue 3、Nuxt 或 Pinia 程式碼（Composition API、reactivity 或 router 導覽）時使用。
origin: ECC
---

# Vue.js 模式與最佳實務

用 Composition API（`<script setup>`）開發 Vue.js 3 的完整指南，涵蓋 component 設計、reactivity、狀態管理、路由、測試和 SSR 模式。跟原生 Vue 不同的地方，會附上 Nuxt 專屬的指引。

## 何時啟用

在以下情況啟用這個 skill：
- 專案使用 Vue.js（任何版本）、Nuxt、Vite + Vue 或 Pinia。
- 使用者詢問 Vue component 架構、composable、reactivity 或狀態管理。
- Review Vue Single-File Component（`.vue` 檔案）。
- 設定 Vue Router、Pinia store，或 Vite/Vitest 設定。
- 討論 Vue 專屬的效能、安全或 SSR 模式。

---

## 1. 專案結構

### 建議的目錄配置（Feature-First）

```
src/
├── api/              # API client 與 endpoint 定義
├── assets/           # 靜態資源（圖片、字型、圖示）
├── components/       # 共用/可重複使用的 component
│   ├── base/         # 基礎 UI 元件（Button、Input、Modal）
│   └── features/     # 特定功能共用的 component
├── composables/      # 可重複使用的 Composition API 邏輯
├── layouts/          # 頁面 layout（選用）
├── pages/            # 路由層級的頁面 component
├── router/           # Vue Router 設定
├── stores/           # Pinia store
├── types/            # TypeScript 型別定義
├── utils/            # 純工具函式
└── App.vue           # 根 component
```

### 檔案命名

| 慣例 | 何時使用 |
|-----------|-------------|
| `PascalCase.vue` | 所有 component（由 `vue/multi-word-component-names` 強制檢查） |
| `useCamelCase.ts` | Composable |
| `camelCase.ts` | 工具函式、API client、型別 |
| `kebab-case` 目錄 | 路由區段、功能資料夾 |

---

## 2. Component 架構

### Single-File Component 的順序

```vue
<script setup lang="ts">
// 1. Import（vue → 生態系套件 → 絕對路徑 → 相對路徑）
// 2. Props、Emits、Slots
// 3. Composable
// 4. 區域狀態（ref/reactive）
// 5. Computed 屬性
// 6. Method
// 7. Watcher
// 8. Lifecycle hook
</script>

<template>
  <!-- Template 內容 -->
</template>

<style scoped>
  /* Scoped 樣式 */
</style>
```

### Presentational 與 Container

- **Container component**：自己負責資料抓取、狀態和副作用，然後渲染 presentational component。
- **Presentational component**：接收 props、發出事件。不呼叫 API、不碰 store，純渲染。

### Props 最佳實務

```ts
// 以型別定義 props，並附預設值
interface Props {
  label: string;
  variant?: "primary" | "secondary";
  disabled?: boolean;
  items: Item[];
}

const props = withDefaults(defineProps<Props>(), {
  variant: "primary",
  disabled: false,
});
```

- 一定要提供 `type`，並在適當時加上 `required`/`default`。
- Boolean props 用 `isXxx`、`hasXxx`、`canXxx` 命名。
- 絕對不要修改 props，改成 emit 事件。
- v-model 綁定用 `defineModel()`（Vue 3.4+），或 `modelValue` + `update:modelValue`。

### 事件

```ts
const emit = defineEmits<{
  submit: [];
  "update:modelValue": [value: string];
  select: [id: string, index: number];
}>();
```

- Template 裡用 kebab-case（`@update:model-value`）。
- Script 裡用 camelCase（`emit("update:modelValue", val)`）。

---

## 3. Composable（可重複使用的邏輯）

### 結構

```ts
// composables/useDebounce.ts
export function useDebounce<T>(value: MaybeRef<T>, delay: number): Ref<T> {
  const debounced = ref(toValue(value)) as Ref<T>;

  let timer: ReturnType<typeof setTimeout>;
  watch(
    () => toValue(value),
    (newVal) => {
      clearTimeout(timer);
      timer = setTimeout(() => { debounced.value = newVal; }, delay);
    }
  );

  onUnmounted(() => clearTimeout(timer));
  return readonly(debounced);
}
```

### 規則

- 一定要以 `use` 開頭。
- 回傳 reactive 的值（`ref`、`computed`、`reactive`），絕對不要回傳單純的原始值。
- 透過 `MaybeRef` / `toRef()` / `toValue()` 接受 reactive 的輸入。
- 在 `onUnmounted` 或 watcher 的 `onCleanup` 裡清理副作用。
- 不要在 module 層級放副作用。

### 與 Mixin 的比較

Composable 完全取代 Vue 2 的 mixin：
- **Mixin**：資料流不透明、source-of-truth 會衝突、名稱會撞。
- **Composable**：明確 import、回傳值清楚、可組合、可 tree-shake。

---

## 4. 狀態管理

### 什麼情況用什麼

| 模式 | 使用情境 |
|---------|----------|
| `ref()` / `reactive()` | Component 區域狀態 |
| Props + Emits | 父子溝通 |
| Provide / Inject | 主題、設定、plugin API |
| Pinia store | 全域、共用、複雜的狀態 |
| Server state composable | 帶快取的 API 資料（包裝 `fetch`/TanStack Query） |

### Pinia Setup Store（首選）

```ts
// stores/useCartStore.ts
export const useCartStore = defineStore("cart", () => {
  const items = ref<CartItem[]>([]);
  const isLoading = ref(false);

  const totalPrice = computed(() =>
    items.value.reduce((sum, i) => sum + i.price * i.quantity, 0)
  );
  const itemCount = computed(() =>
    items.value.reduce((sum, i) => sum + i.quantity, 0)
  );

  async function addItem(productId: string) {
    isLoading.value = true;
    try {
      const item = await fetchProduct(productId);
      const existing = items.value.find(i => i.id === item.id);
      if (existing) existing.quantity++;
      else items.value.push({ ...item, quantity: 1 });
    } finally {
      isLoading.value = false;
    }
  }

  return { items, isLoading, totalPrice, itemCount, addItem };
});
```

- 用 Setup Store 語法（不要用 Options Store）。
- 業務層級的變更優先用 action，成組的更新用 `$patch()`。
- 每個 async action：都要處理 loading + success + error。

---

## 5. Vue Router

### 路由定義

```ts
const routes = [
  {
    path: "/users/:id",
    name: "user-detail",
    component: () => import("@/pages/UserDetail.vue"), // lazy 載入
    props: true, // 把 params 當成 props 傳入
    meta: { requiresAuth: true },
  },
];
```

### Navigation Guard

```ts
router.beforeEach((to, from) => {
  const { isLoggedIn } = useAuthStore();
  if (to.meta.requiresAuth && !isLoggedIn) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
});
```

### Reactive 的路由參數

當 component 保持掛載、但路由參數改變時：

```ts
const route = useRoute();
const id = computed(() => route.params.id as string);
watch(id, (newId) => fetchItem(newId));
```

---

## 6. Template 模式

### Template 語法

```vue
<!-- v-if/v-else-if/v-else -->
<div v-if="isLoading">Loading...</div>
<div v-else-if="error">Error: {{ error }}</div>
<div v-else>{{ content }}</div>

<!-- 頻繁切換用 v-show -->
<div v-show="isOpen">Toggled content</div>

<!-- v-for 搭配穩定的 key -->
<div v-for="item in items" :key="item.id">{{ item.name }}</div>

<!-- 用 computed 過濾後的清單（不要在同一個元素上用 v-if + v-for） -->
<div v-for="item in activeItems" :key="item.id">{{ item.name }}</div>

<!-- 事件處理 -->
<form @submit.prevent="handleSubmit">
  <button type="submit">Save</button>
</form>

<!-- v-model -->
<input v-model="name" />
<CustomInput v-model="value" v-model:title="title" />
```

---

## 7. 效能

| 技巧 | 何時使用 |
|-----------|-------------|
| `v-memo` | 很少變動的清單項目 |
| `v-once` | 只渲染一次、之後永遠靜態的內容 |
| `shallowRef()` | 整個被整批取代的大型資料結構 |
| `shallowReactive()` | 只有最上層屬性需要 reactive |
| `v-show` 優先於 `v-if` | 頻繁切換顯示狀態 |
| `<KeepAlive :max="10">` | 快取會來回切換的 view |
| Lazy 路由 | 非關鍵路由用 `() => import(...)` |
| `Suspense` | 非同步 component 載入，附 fallback |

---

## 8. 測試

### 工具組合

- **Vitest**：單元測試與 component 測試
- **Vue Test Utils**：掛載與互動
- **@pinia/testing**：store mock
- **Playwright**：E2E

### Component 測試模式

```ts
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import UserCard from "./UserCard.vue";

beforeEach(() => { setActivePinia(createPinia()); });

it("renders and emits", async () => {
  const wrapper = mount(UserCard, {
    props: { user: { id: "1", name: "Alice" } },
  });
  expect(wrapper.text()).toContain("Alice");
  await wrapper.find("button").trigger("click");
  expect(wrapper.emitted("select")![0]).toEqual(["1"]);
});
```

---

## 9. Nuxt 專屬模式

### Auto-Import

Nuxt 會自動 import `ref`、`computed`、`watch`、`useFetch`、`useAsyncData` 等，直接用就好，不用 import。非 Nuxt 專案則一律要明確 import。

### useAsyncData / useFetch

```ts
const { data: user, pending, error, refresh } = await useAsyncData(
  "user", // 快取用的唯一 key
  () => $fetch(`/api/users/${id}`),
);

const { data: posts } = await useFetch("/api/posts", {
  query: { page: 1 },
  key: "posts-page-1", // 讓請求去重
});
```

### Server Route

```ts
// server/api/users/[id].ts
export default defineEventHandler(async (event) => {
  const { id } = await getValidatedRouterParams(event, z.object({
    id: z.string().uuid(),
  }).parse);
  // ... 抓取並回傳
});
```

### Runtime Config

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    // 只在 server 端可用
    apiSecret: "",
    // 公開（會暴露給 client）
    public: {
      apiBase: "https://api.example.com",
    },
  },
});
```

---

## 10. Vue 3.5+ 新 API

### Reactive Props Destructure

Vue 3.5 把 reactive props destructure 轉為穩定功能：從 `defineProps()` 解構出來的變數會自動具備 reactivity：

```ts
// Vue 3.5+：解構出來的 props 是 reactive 的（不需要 toRefs）
const { count = 0, msg = "hello" } = defineProps<{
  count?: number;
  msg?: string;
}>();

// 限制：不能直接 watch 解構出來的 prop
watch(() => count, (newVal) => { ... }); // 正確：必須用 getter
```

### `useTemplateRef()`

Template ref 改用 `useTemplateRef()`，取代靠變數名稱對應的普通 ref：

```ts
import { useTemplateRef } from "vue";
const inputEl = useTemplateRef<HTMLInputElement>("input");
// "input" 對應的是 template 裡的 ref="input" 屬性，不是變數名稱
```

支援動態 ref ID：`useTemplateRef(dynamicRefId)`。

### `onWatcherCleanup()`

可全域 import 的 watcher 清理 API（Vue 3.5+）。必須在 watcher callback 內同步呼叫：

```ts
import { watch, onWatcherCleanup } from "vue";

watch(userId, async (newId) => {
  const controller = new AbortController();
  onWatcherCleanup(() => controller.abort());
  // ... 帶著 signal 去 fetch
});
```

### `useId()`

為表單元素和無障礙功能產生在 SSR 下穩定的唯一 ID：

```ts
import { useId } from "vue";
const id = useId();
```

### `defer` Teleport

`<Teleport defer>` 允許 teleport 到同一個渲染週期內才渲染出來的目標：

```vue
<Teleport defer to="#container">Content</Teleport>
<div id="container"></div>
```

### Lazy Hydration（SSR）

`defineAsyncComponent()` 現在支援 `hydrate` 策略：

```ts
import { defineAsyncComponent, hydrateOnVisible } from "vue";
const AsyncComp = defineAsyncComponent({
  loader: () => import("./Comp.vue"),
  hydrate: hydrateOnVisible(),
});
```

---

## 反模式

| 反模式 | 為什麼不對 | 修正方式 |
|-------------|---------------|---------|
| 解構 `defineProps()`（Vue < 3.5） | 只抓到快照，失去 reactivity | 用 `props.xxx` 存取，或用 `toRefs()` |
| 對解構出來的 prop 用 `watch()`（Vue 3.5+） | 編譯期錯誤，解構出來的 props 不能直接 watch | 用 getter 包起來：`watch(() => count, ...)` |
| 同一個元素上用 `v-if` + `v-for` | 執行順序不明確 | 用 computed 過濾後的陣列 |
| `v-for` 的 key 用 index | 重新排序時狀態會壞掉 | 用穩定的資料庫 ID |
| 修改 props | 違反單向資料流 | Emit 事件，或用 `v-model` |
| 用 `v-html` 渲染使用者內容 | XSS 漏洞 | 用 DOMPurify 清理 |
| Vue 3 裡用 mixin | 不透明、容易衝突 | 改用 composable |
| Composable 裡有 module 層級的副作用 | 會在各 instance 之間共用 | 限縮在 `onMounted` + `onUnmounted` 裡 |
| 用 `reactive()` 存會被整個取代的狀態 | 整個取代會破壞 reactivity | 改用 `ref()` |
| Watcher 沒有清理 | 記憶體洩漏、race condition | 用 `onCleanup` 或 `onWatcherCleanup()`（Vue 3.5+） |
| 新的 Vue 3 程式碼用 Options API | 生態系已經轉向 Composition API | 用 `<script setup>` |
| Template ref 用普通 ref | 不支援動態 ref，靠名稱對應很脆弱 | 用 `useTemplateRef()`（Vue 3.5+） |

## 相關 Skill

- `accessibility`：ARIA、語意化 HTML、focus 管理
- `frontend-patterns`：跨框架的前端架構
- `typescript`：套用在 Vue 專案上的 TypeScript 最佳實務
- `coding-standards`：一般程式碼品質標準
