---
name: angular-developer
description: 產生 Angular 程式碼並提供架構指引。建立專案、元件或 service 時觸發，也用在 reactivity（signals、linkedSignal、resource）、表單、依賴注入、路由、SSR、無障礙（ARIA）、動畫、樣式（元件樣式、Tailwind CSS）、測試或 CLI 工具的最佳實務。
metadata:
  origin: ECC
---

# Angular 開發者指南

## 何時啟用

- 在任何 Angular 專案或 codebase 裡工作
- 建立或搭建新的 Angular 專案、應用程式或函式庫
- 產生元件、service、directive、pipe、guard 或 resolver
- 用 Angular Signals、`linkedSignal` 或 `resource` 實作 reactivity
- 處理 Angular 表單（signal forms、reactive forms 或 template-driven）
- 設定依賴注入、路由、lazy loading 或路由 guard
- 加上無障礙（ARIA）、動畫或元件樣式
- 撰寫或除錯 Angular 專屬的測試（單元、component harness、E2E）
- 設定 Angular CLI 工具或 Angular MCP server

1. 提供指引之前，一定要先分析專案的 Angular 版本，因為最佳實務和可用的功能在不同版本之間差很多。如果是用 Angular CLI 建新專案，除非使用者要求，否則不要指定版本。

2. 產生程式碼時，遵循 Angular 的風格指南和最佳實務，維持可維護性和效能。用 Angular CLI 來搭建元件、service、directive、pipe 和 route，確保一致。

3. 程式碼產生完之後，執行 `ng build` 確認沒有 build 錯誤。如果有錯誤，先分析錯誤訊息並修好，再往下做。絕對不要跳過這一步，它對確保產生的程式碼正確、能運作至關重要。

## 建立新專案

如果使用者沒有提供準則，建立新的 Angular 專案時就用這些預設值：

1. 除非使用者另有指定，否則使用 Angular 最新的穩定版本。
2. 只有在目標 Angular 版本支援時，新專案才優先使用 Signal Forms。[了解更多](references/signal-forms.md)。

**`ng new` 的執行規則：**
被要求建立新的 Angular 專案時，你必須依照下面這些嚴格的步驟，決定正確的執行指令：

**步驟 1：檢查使用者有沒有明確指定版本。**

- **如果**使用者要求特定版本（例如 Angular 15），就繞過本機安裝，一律使用 `npx`。
- **指令：** `npx @angular/cli@<requested_version> new <project-name>`

**步驟 2：檢查是否已經安裝 Angular。**

- **如果**沒有要求特定版本，就在終端機執行 `ng version`，檢查系統上是否已經安裝 Angular CLI。
- **如果**指令成功並回傳已安裝的版本，就直接使用本機或全域的安裝。
- **指令：** `ng new <project-name>`

**步驟 3：退而使用最新版。**

- **如果**沒有要求特定版本，而且 `ng version` 指令失敗（表示系統上沒有 Angular），你就必須用 `npx` 去抓最新版。
- **指令：** `npx @angular/cli@latest new <project-name>`

## 元件

處理 Angular 元件時，依任務參考下面的文件：

- **基礎**：結構、metadata、核心概念，以及 template 控制流程（@if、@for、@switch）。請讀 [components.md](references/components.md)
- **Inputs**：以 signal 為基礎的 input、transform 和 model input。請讀 [inputs.md](references/inputs.md)
- **Outputs**：以 signal 為基礎的 output 和自訂事件的最佳實務。請讀 [outputs.md](references/outputs.md)
- **Host Elements**：Host binding 和 attribute 注入。請讀 [host-elements.md](references/host-elements.md)

如果你需要比上面的文件更深入的資料，請讀 `https://angular.dev/guide/components` 的文件。

## Reactivity 與資料管理

管理狀態和資料的 reactivity 時，使用 Angular Signals，並參考下面的文件：

- **Signals 概覽**：核心 signal 概念（`signal`、`computed`）、reactive context 和 `untracked`。請讀 [signals-overview.md](references/signals-overview.md)
- **相依狀態（`linkedSignal`）**：建立連結到來源 signal 的可寫入狀態。請讀 [linked-signal.md](references/linked-signal.md)
- **非同步 Reactivity（`resource`）**：把非同步資料直接抓進 signal 狀態。請讀 [resource.md](references/resource.md)
- **副作用（`effect`）**：記錄、第三方 DOM 操作（`afterRenderEffect`），以及什麼時候「不」該用 effect。請讀 [effects.md](references/effects.md)

## 表單

新應用程式大多數情況下，**優先用 signal forms**。做表單決策時，先分析專案，並考慮下面的準則：

- 如果應用程式的版本支援 Signal Forms，而且是新表單，**優先用 signal forms**。
- 對舊的應用程式或既有的表單，配合應用程式目前的表單策略。

- **Signal Forms**：用 signal 管理表單狀態。請讀 [signal-forms.md](references/signal-forms.md)
- **Template-driven forms**：用在簡單的表單。請讀 [template-driven-forms.md](references/template-driven-forms.md)
- **Reactive forms**：用在複雜的表單。請讀 [reactive-forms.md](references/reactive-forms.md)

## 依賴注入

在 Angular 實作依賴注入時，遵循這些準則：

- **基礎**：依賴注入、service 和 `inject()` 函式的概覽。請讀 [di-fundamentals.md](references/di-fundamentals.md)
- **建立與使用 Service**：建立 service、`providedIn: 'root'` 選項，以及注入到元件或其他 service。請讀 [creating-services.md](references/creating-services.md)
- **定義相依 Provider**：自動與手動提供、`InjectionToken`、`useClass`、`useValue`、`useFactory` 和 scope。請讀 [defining-providers.md](references/defining-providers.md)
- **Injection Context**：`inject()` 可以用在哪裡、`runInInjectionContext` 和 `assertInInjectionContext`。請讀 [injection-context.md](references/injection-context.md)
- **階層式 Injector**：`EnvironmentInjector` 對 `ElementInjector`、解析規則、modifier（`optional`、`skipSelf`），以及 `providers` 對 `viewProviders`。請讀 [hierarchical-injectors.md](references/hierarchical-injectors.md)

## Angular Aria

要為下列任何模式建構無障礙的自訂元件時：Accordion、Listbox、Combobox、Menu、Tabs、Toolbar、Tree、Grid，請參考下面的文件：

- **Angular Aria 元件**：建構 headless、無障礙的元件（Accordion、Listbox、Combobox、Menu、Tabs、Toolbar、Tree、Grid），以及為 ARIA attribute 設定樣式。請讀 [angular-aria.md](references/angular-aria.md)

## 路由

在 Angular 實作導覽時，參考下面的文件：

- **定義路由**：URL 路徑、靜態與動態區段、萬用字元和 redirect。請讀 [define-routes.md](references/define-routes.md)
- **路由載入策略**：Eager 與 lazy loading，以及感知 context 的載入。請讀 [loading-strategies.md](references/loading-strategies.md)
- **用 Outlet 顯示路由**：使用 `<router-outlet>`、巢狀 outlet 和具名 outlet。請讀 [show-routes-with-outlets.md](references/show-routes-with-outlets.md)
- **導覽到路由**：用 `RouterLink` 做宣告式導覽，用 `Router` 做程式化導覽。請讀 [navigate-to-routes.md](references/navigate-to-routes.md)
- **用 Guard 控制路由存取**：實作 `CanActivate`、`CanMatch` 和其他安全用的 guard。請讀 [route-guards.md](references/route-guards.md)
- **資料 Resolver**：用 `ResolveFn` 在路由啟用前預先抓資料。請讀 [data-resolvers.md](references/data-resolvers.md)
- **Router 生命週期與事件**：導覽事件的時間順序，以及除錯。請讀 [router-lifecycle.md](references/router-lifecycle.md)
- **渲染策略**：CSR、SSG（預先渲染）和帶 hydration 的 SSR。請讀 [rendering-strategies.md](references/rendering-strategies.md)
- **路由轉場動畫**：啟用並自訂 View Transitions API。請讀 [route-animations.md](references/route-animations.md)

如果你需要更深入的文件或更多 context，請看[官方 Angular 路由指南](https://angular.dev/guide/routing)。

## 樣式與動畫

在 Angular 實作樣式和動畫時，參考下面的文件：

- **在 Angular 使用 Tailwind CSS**：把 Tailwind CSS 整合進 Angular 專案。請讀 [tailwind-css.md](references/tailwind-css.md)
- **Angular 動畫**：使用原生 CSS（建議）或舊的 DSL 來做動態效果。請讀 [angular-animations.md](references/angular-animations.md)
- **元件樣式**：元件樣式和封裝的最佳實務。請讀 [component-styling.md](references/component-styling.md)

## 測試

撰寫或更新測試時，依任務參考下面的文件：

- **基礎**：單元測試的最佳實務、非同步模式和 `TestBed`。請讀 [testing-fundamentals.md](references/testing-fundamentals.md)
- **Component Harness**：穩健的元件互動標準模式。請讀 [component-harnesses.md](references/component-harnesses.md)
- **Router 測試**：用 `RouterTestingHarness` 做可靠的導覽測試。請讀 [router-testing.md](references/router-testing.md)
- **端對端（E2E）測試**：用 Cypress 或 Playwright 做 E2E 測試的最佳實務。請讀 [e2e-testing.md](references/e2e-testing.md)

## 工具

處理 Angular 工具時，參考下面的文件：

- **Angular CLI**：建立應用程式、產生程式碼（元件、route、service）、serve 和 build。請讀 [cli.md](references/cli.md)
- **Angular MCP Server**：可用的工具、設定和實驗性功能。請讀 [mcp.md](references/mcp.md)

## 反面模式

- 把 `null` 或 `undefined` 當成 signal form 欄位的初始值：改用 `''`、`0` 或 `[]`
- 沒先呼叫欄位就存取表單欄位的狀態旗標：`form.field.valid()`，要用 `form.field().valid()`
- 目標 Angular 版本支援 Signal Forms，卻用舊的表單 API 開新表單
- 在 `[formField]` 的 input 上設定 `min`、`max`、`value`、`disabled` 或 `readonly` HTML attribute：這些要改成 schema 規則來定義
- 在 injection context 之外呼叫 `inject()`：需要時用 `runInInjectionContext`
- 把應該用 `computed()` 的衍生狀態拿去用 `effect()`
- 在巢狀的 `@for` 迴圈裡參照 `$parent.$index`：Angular 不支援 `$parent`；請改用 `let outerIdx = $index`

## 相關 Skill

- `tdd-workflow`：適用於 Angular 元件和 service 的測試驅動開發工作流程
- `security-review`：web 應用程式的安全 checklist，包含 Angular 專屬的問題
- `frontend-patterns`：一般的前端模式，提供 React/Next.js 做法的背景
