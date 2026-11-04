---
name: narrow-react-prop-types
description: 把 React 元件的 prop 型別收窄，讓它跟實際上線的程式路徑一致
---

# Narrow React Prop Types

React 元件的 props 為了 stories、mock、測試或 demo 被放寬，現在表達的是真正的應用程式根本不會進入的狀態，就用這個 skill。

目標是讓元件的型別描述真實上線程式路徑的契約，然後要求 stories/測試/mock 去配合這份契約，而不是反過來把契約放寬。

## 核心要求

- 在改型別之前，先找出實際的非測試、非 Storybook 呼叫端。
- 把上線的程式路徑當作 prop 契約的唯一依據。
- 不要只因為某個 optional prop 讓 Storybook、測試或 mock 資料比較好寫，就把它留著。
- 只有在存在非 Storybook、非測試的呼叫端沒有傳這個 prop，而且有正當理由時，才讓它維持 optional。
- 型別不該讓人能表達在非測試、非 Storybook 呼叫端從沒出現過的狀態。
- 型別要盡可能嚴格，這樣程式碼才能盡可能簡單。
- 盡可能從現有上線程式路徑的值和 API 推導、抽取型別。

## 工作流程

想看透過 CodeLayer 執行這個 skill 的定期 GitHub Actions workflow 範例，見 `references/agent-narrow-component-props.yml`。它的 agent memory 範例檔是 `references/narrow-component-props-memory.md`。CI agent 的回應格式見 `references/response-template.md`。

### 1. 找出可疑的元件

找有這些徵兆的元件：

- props 介面很大，有一堆 optional 欄位。
- 呼叫 optional callback，例如 `onSelect?.(...)` 或 `onArchive?.(...)`。
- 對上線程式碼很可能永遠會提供的值做 fallback 處理，例如 `items ?? []`、`count ?? 0`，或 `handler && ...`。
- 就算 callback 是 optional，UI 操作元件還是永遠會渲染出來。
- 看起來是為了 demo 設計的 props，例如 `defaultFoo`、另一種 handler 形狀，或上線程式碼沒用到的顯示開關。

不要只憑 story 或測試就挑目標。stories/測試只能當作「型別被放寬了」的輔助證據，不能當作某個狀態是真的存在的證據。

### 2. 找出每一個上線的使用處

搜尋這個元件、匯出的 prop 型別，以及共用的子 primitive 的所有 import/使用處。

依照呼叫端是上線程式路徑還是輔助程式碼來分類：

- 上線程式路徑：app 路由、已接線的元件、provider、hook、production 的 package 匯出，以及這些路徑用到的共用元件。
- 輔助程式碼：Storybook stories、測試檔、fixture、mock、demo 用的 harness，以及純視覺的範例。

只有上線程式路徑才能決定元件的 API 支援什麼。

### 3. 從上線程式路徑推導真實的型別

讀上線的呼叫端，替每個 prop 分類：

- Required：每個非測試、非 Storybook 的呼叫端都有提供它。
- Optional：至少有一個非測試、非 Storybook 的呼叫端沒傳它，而且這個缺少是有意義的 runtime 狀態。
- Removed：沒有任何非測試、非 Storybook 的呼叫端用到它。

Nullability 和 optionality 是兩回事。如果上線程式碼永遠會傳這個 prop，只是值可能是空的，就用 required 但可為 null 的 prop，例如 `focusedItem: FocusedItem | null`，不要用 `focusedItem?: FocusedItem | null`。

### 4. 收緊公開的 prop 型別

更新匯出的 prop 型別，讓它只符合上線程式路徑中觀察到的狀態。

型別越寬鬆、越多 optional，元件要推敲的可能狀態就越多。每多一個 optional prop，元件就多一個得處理、測試並維持正確的分支。要用嚴格的型別擋掉不可能的狀態，不要用寬鬆的型別逼出防禦性的渲染邏輯。

如果元件永遠會渲染一個可互動的操作元件，就要求提供讓它運作的 handler。不要允許無作用的狀態，例如一個看得到的選單項目卻呼叫 `onRename?.(...)`。

### 5. 盡可能推導並抽取型別

優先從上線的 API 推導型別，不要手動重述：

- 函式參數型別用 `Parameters<typeof fn>[0]`。
- 回傳型別用 `ReturnType<typeof fn>`。
- 把 union 收窄成真正存在的變體，用 `Extract<Union, Shape>`。
- React 的 state setter 用 `React.Dispatch<React.SetStateAction<T>>`，不要近似成 `(value: T) => void`。

當型別推論會放寬或模糊本來要的 state 形狀時，優先明確指定 state 的型別參數：

```ts
const [dialogState, setDialogState] = useState<DialogState>({
  id: null,
  isOpen: false,
})
```

避免依賴隱含的 `useState(...)` 推論，它可能產生寬鬆的可為 null 物件形狀、字串常值被放寬，或之後得靠手寫近似的 callback 型別。

### 6. 內部子元件的 props 也要收緊

如果匯出的元件把寬鬆的 props 傳進子 primitive，不要只收緊匯出的那一層。

如果 row/選單/按鈕這些子元件拿到 optional handler，只是因為父層的 props 太寬，就連這些內部 props 一起收緊。把像這樣的 optional 呼叫：

```ts
onRename?.(id, name)
```

換成必填的呼叫：

```ts
onRename(id, name)
```

### 7. 移除針對不支援狀態的 fallback 邏輯

props 變成 required 之後，把只是為了寬鬆型別才存在的防禦性 fallback 拿掉。

範例：

```ts
new Set(expandedIds ?? defaultExpandedIds ?? [])
```

應該變成：

```ts
new Set(expandedIds)
```

```ts
items && items.length > 0
```

應該變成：

```ts
items.length > 0
```

### 8. 更新所有共用這個 prop 型別的變體

如果有多個元件共用同一個寬鬆的 prop 型別，就一起更新，讓它們都落實同一份上線程式路徑的契約。

### 9. 讓測試和 stories 去配合上線程式碼

如果 story 或測試在收窄 props 之後壞掉，就提供貼近實際的 handler 和 state 來修。不要為了減少測試的設定工作，又把上線程式路徑的 props 改回 optional。

如果 story/測試的設定寫起來很囉嗦，就做一個 test helper 或 fixture 來滿足嚴格的上線程式路徑契約。helper 留在輔助程式碼裡，不要削弱元件的 API。

### 10. 驗證改動

對改動的 package，以及每個使用該元件的上線 app/package，執行 package 層級的 typecheck。

有 repo 專屬的驗證指令就用它。在這個 monorepo 裡，優先用：

```bash
bun --bun run typecheck --filter <package>
```

### 11. 格式化回應

以 CI agent 身分執行時，依照 `references/response-template.md` 格式化你的最終回應。這個回應會變成 PR 內文。

內容要包含：
- 收窄了幾個元件的摘要
- 附上理由的改動表格
- 支持每次收窄的上線呼叫端
- 需要更新的輔助程式碼（stories/測試）
- 驗證結果
- 風險評估

## Review 檢查清單

- 改動的 prop 型別是從非測試、非 Storybook 的呼叫端推導出來的。
- 對永遠會渲染的互動，optional callback 已移除。
- 渲染出來的選單項目和按鈕，不會因為缺少 handler 而變成無作用。
- 被移除的 props 沒有被上線程式路徑使用。
- 只有真實存在的狀態才保留 nullability，例如目前沒有 focus。
- 型別盡量用推導或抽取，不是手動重複。
- 在推論會放寬或模糊本意的 state 時，用了 `useState<T>(...)`。
- 共用的變體都針對同一份收窄後的契約編譯通過。
- 共用 package 和使用它的上線 app/package 都通過 typecheck。

## 要避免的反模式

- 為了讓 stories 可以省略，就把 callback 改成 optional。
- 渲染一個呼叫 `onAction?.(...)` 的選單項目。
- 上線程式碼是 controlled 的，卻為了 Storybook 加 `default*` props。
- 用 `?? []` 或 `?? 0` 遮掉缺少的、上線時必要的 state。
- 上線程式碼只用一種 API 形狀，卻接受多種。
- 把純元件當成 mock 元件，給它寬鬆的契約。
