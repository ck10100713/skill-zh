---
name: flutter-dart-code-review
description: 不綁特定函式庫的 Flutter/Dart code review 檢查清單，涵蓋 widget 最佳實務、狀態管理模式（BLoC、Riverpod、Provider、GetX、MobX、Signals）、Dart 慣用寫法、效能、無障礙、安全性與 clean architecture。review Flutter 或 Dart 程式碼時使用，不論專案用哪種狀態管理函式庫。
metadata:
  origin: ECC
---

# Flutter/Dart Code Review Best Practices

一份完整、不綁特定函式庫的 Flutter/Dart 應用程式 review 檢查清單。不管用哪種狀態管理方案、路由函式庫或 DI 框架，這些原則都適用。

---

## 1. General Project Health

- [ ] 專案的資料夾結構一致（feature-first 或 layer-first）
- [ ] 關注點分離得當：UI、商業邏輯、資料層各自獨立
- [ ] widget 裡沒有商業邏輯，widget 純粹負責呈現
- [ ] `pubspec.yaml` 很乾淨：沒有用不到的依賴，版本鎖得適當
- [ ] `analysis_options.yaml` 包含嚴格的 lint 規則集，並開啟嚴格的 analyzer 設定
- [ ] production 程式碼裡沒有 `print()`，改用 `dart:developer` 的 `log()` 或 logging 套件
- [ ] 產生出來的檔案（`.g.dart`、`.freezed.dart`、`.gr.dart`）是最新的，或已加進 `.gitignore`
- [ ] 平台專屬的程式碼隔離在抽象層後面

---

## 2. Dart Language Pitfalls

- [ ] **隱含的 dynamic**：缺少型別標註導致變成 `dynamic`，要開啟 `strict-casts`、`strict-inference`、`strict-raw-types`
- [ ] **濫用 null safety**：過度使用 `!`（bang operator），而不是做正確的 null 檢查或用 Dart 3 的 pattern matching（`if (value case var v?)`）
- [ ] **型別提升失敗**：用了 `this.field`，其實改用區域變數就能做型別提升
- [ ] **catch 範圍太廣**：`catch (e)` 沒有 `on` 子句，一律要指定例外型別
- [ ] **去 catch `Error`**：`Error` 的子型別代表 bug，不應該被 catch
- [ ] **沒必要的 `async`**：標了 `async` 卻從沒 `await`，白白增加開銷
- [ ] **`late` 用太多**：該用 nullable 或建構子初始化比較安全的地方卻用了 `late`，會把錯誤延後到 runtime
- [ ] **迴圈裡做字串串接**：反覆組字串要用 `StringBuffer`，不要用 `+`
- [ ] **`const` 情境下有可變狀態**：`const` 建構子類別的欄位不應該是可變的
- [ ] **忽略 `Future` 的回傳值**：要用 `await`，或明確呼叫 `unawaited()` 表明是故意的
- [ ] **能用 `final` 卻用 `var`**：區域變數優先用 `final`，編譯期常數用 `const`
- [ ] **相對 import**：為了一致，用 `package:` 形式的 import
- [ ] **對外暴露可變集合**：public API 應該回傳不可修改的 view，不要直接回傳原始的 `List`/`Map`
- [ ] **沒用到 Dart 3 pattern matching**：優先用 switch expression 和 `if-case`，不要寫囉嗦的 `is` 檢查加手動轉型
- [ ] **為了回傳多個值而建的拋棄式類別**：用 Dart 3 的 record `(String, int)`，不要建只用一次的 DTO
- [ ] **production 程式碼裡的 `print()`**：用 `dart:developer` 的 `log()` 或專案的 logging 套件；`print()` 沒有 log level，也沒辦法過濾

---

## 3. Widget Best Practices

### Widget decomposition:
- [ ] 沒有任何 widget 的 `build()` 方法超過約 80 到 100 行
- [ ] widget 的拆分同時考慮封裝，以及它們變動的方式（rebuild 邊界）
- [ ] 回傳 widget 的私有 `_build*()` 輔助方法，要抽成獨立的 widget 類別（這樣才能重用 element、傳遞 const，也能吃到框架的最佳化）
- [ ] 不需要可變區域狀態的地方，優先用 Stateless widget 而不是 Stateful
- [ ] 可重用的 widget 抽出來放在獨立檔案

### Const usage:
- [ ] 能用 `const` 建構子就用，避免不必要的 rebuild
- [ ] 不會變的集合用 `const` 字面值（`const []`、`const {}`）
- [ ] 所有欄位都是 final 時，建構子要宣告成 `const`

### Key usage:
- [ ] list/grid 裡用 `ValueKey`，重新排序時才能保留狀態
- [ ] `GlobalKey` 要節制使用，只在真的需要跨整棵 tree 存取狀態時才用
- [ ] `build()` 裡避免用 `UniqueKey`，它會讓每個 frame 都強制 rebuild
- [ ] 身分是由資料物件而不是單一值決定時，用 `ObjectKey`

### Theming & design system:
- [ ] 顏色來自 `Theme.of(context).colorScheme`，沒有寫死 `Colors.red` 或 hex 值
- [ ] 文字樣式來自 `Theme.of(context).textTheme`，沒有直接寫帶原始字級的 inline `TextStyle`
- [ ] 確認過深色模式相容，沒有預設背景是淺色
- [ ] 間距和尺寸用一致的 design token 或常數，不用 magic number

### Build method complexity:
- [ ] `build()` 裡沒有網路呼叫、檔案 I/O 或繁重的運算
- [ ] `build()` 裡沒有 `Future.then()` 或 `async` 工作
- [ ] `build()` 裡沒有建立訂閱（`.listen()`）
- [ ] `setState()` 限縮在盡可能小的子樹

---

## 4. State Management (Library-Agnostic)

這些原則適用於所有 Flutter 狀態管理方案（BLoC、Riverpod、Provider、GetX、MobX、Signals、ValueNotifier 等等）。

### Architecture:
- [ ] 商業邏輯放在 widget 層之外，放在狀態管理元件裡（BLoC、Notifier、Controller、Store、ViewModel 等）
- [ ] 狀態管理元件透過注入取得依賴，不是在內部自己建構
- [ ] 由 service 或 repository 層抽象化資料來源，widget 和狀態管理元件不該直接呼叫 API 或資料庫
- [ ] 每個狀態管理元件只負責單一職責，不要有處理不相干事情的「上帝」管理器
- [ ] 跨元件的依賴要遵循該方案的慣例：
  - 在 **Riverpod**：provider 透過 `ref.watch` 依賴其他 provider 是正常的，只有循環或過度糾纏的鏈才需要標出來
  - 在 **BLoC**：bloc 不應該直接依賴其他 bloc，優先用共用的 repository 或在 presentation 層協調
  - 在其他方案：照官方文件記載的元件間溝通慣例來做

### Immutability & value equality (for immutable-state solutions: BLoC, Riverpod, Redux):
- [ ] state 物件是不可變的，用 `copyWith()` 或建構子產生新實例，不要原地修改
- [ ] state 類別有正確實作 `==` 和 `hashCode`（所有欄位都納入比較）
- [ ] 整個專案的機制要一致：手動 override、`Equatable`、`freezed`、Dart record 或其他都行，但要統一
- [ ] state 物件裡的集合不要以原始的可變 `List`/`Map` 暴露出去

### Reactivity discipline (for reactive-mutation solutions: MobX, GetX, Signals):
- [ ] state 只能透過該方案的 reactive API 修改（MobX 的 `@action`、signal 的 `.value`、GetX 的 `.obs`），直接改欄位會繞過變更追蹤
- [ ] 衍生值用該方案的 computed 機制，不要重複儲存
- [ ] reaction 和 disposer 都有正確清理（MobX 的 `ReactionDisposer`、Signals 的 effect 清理）

### State shape design:
- [ ] 互斥的狀態用 sealed type、union variant，或該方案內建的非同步狀態型別（例如 Riverpod 的 `AsyncValue`），不要用布林旗標（`isLoading`、`isError`、`hasData`）
- [ ] 每個非同步操作都把 loading、success、error 建模成各自獨立的狀態
- [ ] UI 窮舉處理所有 state variant，沒有被默默忽略的情況
- [ ] error 狀態帶著可以顯示的錯誤資訊；loading 狀態不要帶著過期的資料
- [ ] 不要拿 nullable 資料當作 loading 指標，狀態要明確

```dart
// BAD：一堆布林旗標會允許不可能的狀態
class UserState {
  bool isLoading = false;
  bool hasError = false; // isLoading && hasError 竟然表示得出來！
  User? user;
}

// GOOD（不可變做法）：sealed type 讓不可能的狀態根本無法表示
sealed class UserState {}
class UserInitial extends UserState {}
class UserLoading extends UserState {}
class UserLoaded extends UserState {
  final User user;
  const UserLoaded(this.user);
}
class UserError extends UserState {
  final String message;
  const UserError(this.message);
}

// GOOD（reactive 做法）：observable enum 加資料，透過 reactivity API 修改
// enum UserStatus { initial, loading, loaded, error }
// 用你的方案提供的 observable/signal，把 status 和 data 分開包起來
```

### Rebuild optimization:
- [ ] 狀態消費端 widget（Builder、Consumer、Observer、Obx、Watch 等）的範圍盡可能縮小
- [ ] 用 selector 讓只有特定欄位變動時才 rebuild，而不是每次 state 發出就 rebuild
- [ ] 用 `const` widget 擋住 rebuild 沿著 tree 往下傳
- [ ] 計算出來的／衍生的狀態用 reactive 方式算，不要重複儲存

### Subscriptions & disposal:
- [ ] 所有手動訂閱（`.listen()`）都在 `dispose()` / `close()` 裡取消
- [ ] 不再需要的 stream controller 都關掉
- [ ] timer 在 dispose 生命週期裡取消
- [ ] 優先用框架管理的生命週期，不要手動訂閱（用宣告式的 builder，不要用 `.listen()`）
- [ ] 非同步 callback 裡呼叫 `setState` 前，先檢查 `mounted`
- [ ] `await` 之後要用 `BuildContext` 時，先檢查 `context.mounted`（Flutter 3.7+），過期的 context 會造成 crash
- [ ] 非同步空檔之後，沒確認 widget 還在 mounted 狀態就不要做導覽、跳 dialog 或顯示 scaffold 訊息
- [ ] `BuildContext` 絕對不要存在 singleton、狀態管理元件或 static 欄位裡

### Local vs global state:
- [ ] 暫時性的 UI 狀態（checkbox、slider、動畫）用區域狀態（`setState`、`ValueNotifier`）
- [ ] 共享狀態只往上提到剛好需要的高度，不要過度全域化
- [ ] 功能範圍的狀態在該功能不再使用時要正確 dispose

---

## 5. Performance

### Unnecessary rebuilds:
- [ ] 不要在根 widget 層級呼叫 `setState()`，把狀態變動限縮在區域
- [ ] 用 `const` widget 擋住 rebuild 傳遞
- [ ] 會獨立重繪的複雜子樹外面包 `RepaintBoundary`
- [ ] 跟動畫無關的子樹，用 `AnimatedBuilder` 的 child 參數

### Expensive operations in build():
- [ ] `build()` 裡不要對大型集合做排序、過濾或 map，這些要放在狀態管理層算
- [ ] `build()` 裡不要編譯 regex
- [ ] `MediaQuery.of(context)` 的用法要具體（例如 `MediaQuery.sizeOf(context)`）

### Image optimization:
- [ ] 網路圖片有做快取（用專案適合的任何快取方案）
- [ ] 圖片解析度適合目標裝置（縮圖不要載 4K 圖）
- [ ] `Image.asset` 搭配 `cacheWidth`/`cacheHeight`，以顯示尺寸解碼
- [ ] 網路圖片提供 placeholder 和 error widget

### Lazy loading:
- [ ] 大型或動態清單用 `ListView.builder` / `GridView.builder`，不要用 `ListView(children: [...])`（小型靜態清單用具體建構子沒問題）
- [ ] 大型資料集有實作分頁
- [ ] web build 裡的重型函式庫用延遲載入（`deferred as`）

### Other:
- [ ] 動畫裡避免用 `Opacity` widget，改用 `AnimatedOpacity` 或 `FadeTransition`
- [ ] 動畫裡避免做裁切，圖片事先裁好
- [ ] 不要在 widget 上覆寫 `operator ==`，改用 `const` 建構子
- [ ] 節制使用 intrinsic dimension widget（`IntrinsicHeight`、`IntrinsicWidth`），它們會多一次 layout pass

---

## 6. Testing

### Test types and expectations:
- [ ] **單元測試**：涵蓋所有商業邏輯（狀態管理元件、repository、工具函式）
- [ ] **Widget 測試**：涵蓋單一 widget 的行為、互動和視覺輸出
- [ ] **整合測試**：涵蓋端到端的關鍵使用者流程
- [ ] **Golden 測試**：對設計關鍵的 UI 元件做像素等級的比對

### Coverage targets:
- [ ] 商業邏輯的行覆蓋率目標 80% 以上
- [ ] 所有狀態轉換都有對應的測試（loading → success、loading → error、retry 等）
- [ ] 測過邊界情況：空狀態、錯誤狀態、載入狀態、邊界值

### Test isolation:
- [ ] 外部依賴（API client、資料庫、service）都用 mock 或 fake
- [ ] 每個測試檔剛好只測一個類別/單元
- [ ] 測試驗證的是行為，不是實作細節
- [ ] stub 只定義每個測試需要的行為（最小化 stub）
- [ ] 測試案例之間沒有共享的可變狀態

### Widget test quality:
- [ ] 非同步操作正確使用 `pumpWidget` 和 `pump`
- [ ] 適當使用 `find.byType`、`find.text`、`find.byKey`
- [ ] 沒有依賴時間的 flaky 測試，改用 `pumpAndSettle` 或明確的 `pump(Duration)`
- [ ] 測試在 CI 裡跑，失敗就擋住 merge

---

## 7. Accessibility

### Semantic widgets:
- [ ] 自動產生的標籤不夠用時，用 `Semantics` widget 提供螢幕閱讀器的標籤
- [ ] 純裝飾性的元素用 `ExcludeSemantics`
- [ ] 用 `MergeSemantics` 把相關的 widget 合併成單一個無障礙元素
- [ ] 圖片有設 `semanticLabel` 屬性

### Screen reader support:
- [ ] 所有互動元素都能取得焦點，而且有有意義的描述
- [ ] 焦點順序合乎邏輯（跟視覺閱讀順序一致）

### Visual accessibility:
- [ ] 文字與背景的對比度 >= 4.5:1
- [ ] 可點擊目標至少 48x48 像素
- [ ] 不要只靠顏色表示狀態（要搭配圖示或文字）
- [ ] 文字會跟著系統字級設定縮放

### Interaction accessibility:
- [ ] 沒有什麼都不做的 `onPressed` callback，每個按鈕不是有作用就是被停用
- [ ] 錯誤欄位會建議如何修正
- [ ] 使用者輸入資料時，情境不會無預警地改變

---

## 8. Platform-Specific Concerns

### iOS/Android differences:
- [ ] 適當的地方使用平台自適應的 widget
- [ ] 正確處理返回導覽（Android 返回鍵、iOS 滑動返回）
- [ ] 狀態列和安全區域用 `SafeArea` widget 處理
- [ ] 平台專屬的權限已在 `AndroidManifest.xml` 和 `Info.plist` 宣告

### Responsive design:
- [ ] 響應式版面用 `LayoutBuilder` 或 `MediaQuery`
- [ ] breakpoint 定義一致（手機、平板、桌面）
- [ ] 小螢幕上文字不會溢出，用 `Flexible`、`Expanded`、`FittedBox`
- [ ] 橫向模式有測過，或明確鎖定
- [ ] Web 專屬：支援滑鼠/鍵盤互動，有 hover 狀態

---

## 9. Security

### Secure storage:
- [ ] 敏感資料（token、憑證）存在平台的安全儲存空間（iOS 的 Keychain、Android 的 EncryptedSharedPreferences）
- [ ] 絕對不要把 secret 存在明文儲存空間
- [ ] 敏感操作考慮用生物辨識驗證把關

### API key handling:
- [ ] API key 沒有寫死在 Dart 原始碼裡，用 `--dart-define`、排除在版控之外的 `.env` 檔，或編譯期設定
- [ ] secret 沒有 commit 進 git，檢查 `.gitignore`
- [ ] 真正機密的 key 用後端 proxy（client 絕不該持有伺服器端的 secret）

### Input validation:
- [ ] 所有使用者輸入在送到 API 前都經過驗證
- [ ] 表單驗證採用正確的驗證模式
- [ ] 沒有原始 SQL，也沒有把使用者輸入做字串插值
- [ ] deep link URL 在導覽前先驗證並清理

### Network security:
- [ ] 所有 API 呼叫都強制使用 HTTPS
- [ ] 高安全性的 app 考慮做憑證綁定（certificate pinning）
- [ ] 驗證 token 有正確更新並過期
- [ ] 沒有把敏感資料寫進 log 或印出來

---

## 10. Package/Dependency Review

### Evaluating pub.dev packages:
- [ ] 檢查 **pub points 分數**（目標 130 以上，滿分 160）
- [ ] 以 **likes** 和 **popularity** 當作社群訊號
- [ ] 確認發佈者在 pub.dev 上是 **verified**
- [ ] 檢查最後發佈日期，久未更新（超過 1 年）的套件有風險
- [ ] 看開放中的 issue 和維護者的回應速度
- [ ] 檢查授權跟你的專案相不相容
- [ ] 確認支援的平台涵蓋你的目標

### Version constraints:
- [ ] 依賴用 caret 語法（`^1.2.3`），允許相容的更新
- [ ] 只有在絕對必要時才鎖死精確版本
- [ ] 定期跑 `flutter pub outdated` 追蹤過期的依賴
- [ ] production 的 `pubspec.yaml` 不要有 dependency override，只在暫時修補時用，並附上註解或 issue 連結
- [ ] 盡量減少間接依賴的數量，每個依賴都是一個攻擊面

### Monorepo-specific (melos/workspace):
- [ ] 內部套件只從 public API import，不要用 `package:other/src/internal.dart`（這會破壞 Dart 套件的封裝）
- [ ] 內部套件的依賴用 workspace 解析，不要寫死 `path: ../../` 這種相對路徑字串
- [ ] 所有子套件共用或繼承根目錄的 `analysis_options.yaml`

---

## 11. Navigation and Routing

### General principles (apply to any routing solution):
- [ ] 一致使用同一種路由做法，不要把命令式的 `Navigator.push` 和宣告式 router 混著用
- [ ] 路由參數有型別，不要用 `Map<String, dynamic>` 或對 `Object?` 做轉型
- [ ] 路由路徑用常數、enum 或自動產生的方式定義，不要在程式碼裡散落 magic string
- [ ] 驗證 guard/redirect 集中管理，不要在各個畫面重複寫
- [ ] Android 和 iOS 都設定了 deep link
- [ ] deep link URL 在導覽前先驗證並清理
- [ ] 導覽狀態可測試，路由切換可以在測試裡驗證
- [ ] 所有平台上的返回行為都正確

---

## 12. Error Handling

### Framework error handling:
- [ ] 覆寫 `FlutterError.onError` 來捕捉框架錯誤（build、layout、paint）
- [ ] 設定 `PlatformDispatcher.instance.onError`，處理 Flutter 沒攔到的非同步錯誤
- [ ] 針對 release 模式客製 `ErrorWidget.builder`（顯示對使用者友善的畫面，不要紅屏）
- [ ] `runApp` 外面包一層全域錯誤捕捉（例如 `runZonedGuarded`、Sentry/Crashlytics 的包裝）

### Error reporting:
- [ ] 整合了錯誤回報服務（Firebase Crashlytics、Sentry 或同等的服務）
- [ ] 非致命錯誤連同 stack trace 一起回報
- [ ] 狀態管理的錯誤 observer 接上錯誤回報（例如 BlocObserver、ProviderObserver，或你所用方案的對應機制）
- [ ] 錯誤回報附上可識別使用者的資訊（user ID），方便除錯

### Graceful degradation:
- [ ] API 錯誤會顯示對使用者友善的錯誤 UI，不會 crash
- [ ] 暫時性的網路失敗有重試機制
- [ ] 離線狀態有妥善處理
- [ ] 狀態管理裡的 error 狀態帶有可顯示的錯誤資訊
- [ ] 原始例外（網路、解析）在到達 UI 之前，先對應成對使用者友善、已本地化的訊息，絕對不要把原始例外字串顯示給使用者

---

## 13. Internationalization (l10n)

### Setup:
- [ ] 設定好在地化方案（Flutter 內建的 ARB/l10n、easy_localization 或同等方案）
- [ ] 在 app 設定中宣告支援的 locale

### Content:
- [ ] 所有使用者看得到的字串都走在地化系統，widget 裡沒有寫死的字串
- [ ] 範本檔包含給翻譯人員看的說明/脈絡
- [ ] 複數、性別、選項用 ICU 訊息語法
- [ ] placeholder 有定義型別
- [ ] 各 locale 之間沒有缺漏的 key

### Code review:
- [ ] 整個專案一致使用同一種在地化存取方式
- [ ] 日期、時間、數字、貨幣的格式化會依 locale 調整
- [ ] 如果目標市場包含阿拉伯文、希伯來文等，要支援文字方向（RTL）
- [ ] 在地化文字不要用字串串接，用帶參數的訊息

---

## 14. Dependency Injection

### Principles (apply to any DI approach):
- [ ] 在層級邊界上，類別依賴的是抽象（介面），不是具體實作
- [ ] 依賴由外部透過建構子、DI 框架或 provider graph 提供，不是在內部自己建立
- [ ] 註冊時區分生命週期：singleton、factory、lazy singleton
- [ ] 環境專屬的綁定（dev/staging/prod）用設定處理，不要用 runtime 的 `if` 檢查
- [ ] DI graph 裡沒有循環依賴
- [ ] service locator 的呼叫（如果有用）不要散落在商業邏輯各處

---

## 15. Static Analysis

### Configuration:
- [ ] 有 `analysis_options.yaml`，並開啟嚴格設定
- [ ] 嚴格的 analyzer 設定：`strict-casts: true`、`strict-inference: true`、`strict-raw-types: true`
- [ ] 納入完整的 lint 規則集（very_good_analysis、flutter_lints 或自訂的嚴格規則）
- [ ] monorepo 裡所有子套件都繼承或共用根目錄的 analysis 選項

### Enforcement:
- [ ] 已 commit 的程式碼沒有未解決的 analyzer 警告
- [ ] lint 抑制（`// ignore:`）都有註解說明理由
- [ ] `flutter analyze` 在 CI 裡跑，失敗就擋住 merge

### Key rules to verify regardless of lint package:
- [ ] `prefer_const_constructors`：對 widget tree 的效能有幫助
- [ ] `avoid_print`：改用正式的 logging
- [ ] `unawaited_futures`：避免 fire-and-forget 的非同步 bug
- [ ] `prefer_final_locals`：變數層級的不可變性
- [ ] `always_declare_return_types`：明確的契約
- [ ] `avoid_catches_without_on_clauses`：針對特定錯誤處理
- [ ] `always_use_package_imports`：一致的 import 風格

---

## State Management Quick Reference

下表把通用原則對應到各主流方案的實作。用它來把 review 規則套用到專案所用的方案上。

| Principle | BLoC/Cubit | Riverpod | Provider | GetX | MobX | Signals | Built-in |
|-----------|-----------|----------|----------|------|------|---------|----------|
| State container | `Bloc`/`Cubit` | `Notifier`/`AsyncNotifier` | `ChangeNotifier` | `GetxController` | `Store` | `signal()` | `StatefulWidget` |
| UI consumer | `BlocBuilder` | `ConsumerWidget` | `Consumer` | `Obx`/`GetBuilder` | `Observer` | `Watch` | `setState` |
| Selector | `BlocSelector`/`buildWhen` | `ref.watch(p.select(...))` | `Selector` | N/A | computed | `computed()` | N/A |
| Side effects | `BlocListener` | `ref.listen` | `Consumer` callback | `ever()`/`once()` | `reaction` | `effect()` | callbacks |
| Disposal | auto via `BlocProvider` | `.autoDispose` | auto via `Provider` | `onClose()` | `ReactionDisposer` | manual | `dispose()` |
| Testing | `blocTest()` | `ProviderContainer` | `ChangeNotifier` directly | `Get.put` in test | store directly | signal directly | widget test |

---

## Sources

- [Effective Dart: Style](https://dart.dev/effective-dart/style)
- [Effective Dart: Usage](https://dart.dev/effective-dart/usage)
- [Effective Dart: Design](https://dart.dev/effective-dart/design)
- [Flutter Performance Best Practices](https://docs.flutter.dev/perf/best-practices)
- [Flutter Testing Overview](https://docs.flutter.dev/testing/overview)
- [Flutter Accessibility](https://docs.flutter.dev/ui/accessibility-and-internationalization/accessibility)
- [Flutter Internationalization](https://docs.flutter.dev/ui/accessibility-and-internationalization/internationalization)
- [Flutter Navigation and Routing](https://docs.flutter.dev/ui/navigation)
- [Flutter Error Handling](https://docs.flutter.dev/testing/errors)
- [Flutter State Management Options](https://docs.flutter.dev/data-and-backend/state-mgmt/options)
