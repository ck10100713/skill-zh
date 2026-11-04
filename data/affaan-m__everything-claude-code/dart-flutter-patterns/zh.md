---
name: dart-flutter-patterns
description: 可以直接上 production 的 Dart 與 Flutter 模式，涵蓋 null safety、用 Freezed 做不可變狀態、async 組合、widget 架構、狀態管理（BLoC、Riverpod、Provider）、帶認證守衛的 GoRouter 導覽、Dio 網路請求、錯誤處理和測試。在撰寫或審查 Dart 與 Flutter 程式碼（狀態、widget、導覽、網路或架構）時使用。
metadata:
  origin: ECC
---

# Dart/Flutter 模式

## 何時使用

在這些情況使用這個 skill：
- 開始一個新的 Flutter 功能，需要狀態管理、導覽或資料存取的慣用模式
- 審查或撰寫 Dart 程式碼，需要 null safety、sealed type 或 async 組合的指引
- 建立新的 Flutter 專案，要在 BLoC、Riverpod 或 Provider 之間做選擇
- 實作安全的 HTTP client、WebView 整合或本機儲存
- 為 Flutter widget、Cubit 或 Riverpod provider 撰寫測試
- 把 GoRouter 跟認證守衛接起來

## 運作方式

這個 skill 提供依關注點整理、可以直接複製貼上的 Dart/Flutter 程式碼模式：
1. **Null safety**：避免 `!`，優先用 `?.`/`??`/pattern matching
2. **不可變狀態**：sealed class、`freezed`、`copyWith`
3. **Async 組合**：並行的 `Future.wait`、`await` 之後安全使用 `BuildContext`
4. **Widget 架構**：抽成類別（不要抽成方法）、`const` 的傳遞、範圍限定的 rebuild
5. **狀態管理**：BLoC/Cubit 事件、Riverpod 的 notifier 和衍生 provider
6. **導覽**：透過 `refreshListenable` 做出有反應式認證守衛的 GoRouter
7. **網路**：帶 interceptor 的 Dio、有一次性重試守衛的 token 刷新
8. **錯誤處理**：全域捕捉、`ErrorWidget.builder`、crashlytics 串接
9. **測試**：單元（BLoC test）、widget（ProviderScope overrides）、fake 優先於 mock

## 範例

```dart
// Sealed state — prevents impossible states
sealed class AsyncState<T> {}
final class Loading<T> extends AsyncState<T> {}
final class Success<T> extends AsyncState<T> { final T data; const Success(this.data); }
final class Failure<T> extends AsyncState<T> { final Object error; const Failure(this.error); }

// GoRouter with reactive auth redirect
final router = GoRouter(
  refreshListenable: GoRouterRefreshStream(authCubit.stream),
  redirect: (context, state) {
    final authed = context.read<AuthCubit>().state is AuthAuthenticated;
    if (!authed && !state.matchedLocation.startsWith('/login')) return '/login';
    return null;
  },
  routes: [...],
);

// Riverpod derived provider with safe firstWhereOrNull
@riverpod
double cartTotal(Ref ref) {
  final cart = ref.watch(cartNotifierProvider);
  final products = ref.watch(productsProvider).valueOrNull ?? [];
  return cart.fold(0.0, (total, item) {
    final product = products.firstWhereOrNull((p) => p.id == item.productId);
    return total + (product?.price ?? 0) * item.quantity;
  });
}
```

---

給 Dart 和 Flutter 應用程式、務實且可以直接上 production 的模式。盡可能不綁特定函式庫，同時明確涵蓋生態系裡最常見的套件。

---

## 1. Null Safety 基礎

### 優先用 Pattern，不要用 Bang 運算子

```dart
// BAD — crashes at runtime if null
final name = user!.name;

// GOOD — provide fallback
final name = user?.name ?? 'Unknown';

// GOOD — Dart 3 pattern matching (preferred for complex cases)
final display = switch (user) {
  User(:final name, :final email) => '$name <$email>',
  null => 'Guest',
};

// GOOD — guard early return
String getUserName(User? user) {
  if (user == null) return 'Unknown';
  return user.name; // promoted to non-null after check
}
```

### 避免濫用 `late`

```dart
// BAD — defers null error to runtime
late String userId;

// GOOD — nullable with explicit initialization
String? userId;

// OK — use late only when initialization is guaranteed before first access
// (e.g., in initState() before any widget interaction)
late final AnimationController _controller;

@override
void initState() {
  super.initState();
  _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 300));
}
```

---

## 2. 不可變狀態

### 用 Sealed Class 做狀態階層

```dart
sealed class UserState {}

final class UserInitial extends UserState {}

final class UserLoading extends UserState {}

final class UserLoaded extends UserState {
  const UserLoaded(this.user);
  final User user;
}

final class UserError extends UserState {
  const UserError(this.message);
  final String message;
}

// Exhaustive switch — compiler enforces all branches
Widget buildFrom(UserState state) => switch (state) {
  UserInitial() => const SizedBox.shrink(),
  UserLoading() => const CircularProgressIndicator(),
  UserLoaded(:final user) => UserCard(user: user),
  UserError(:final message) => ErrorText(message),
};
```

### 用 Freezed 免寫樣板碼就得到不可變性

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
    required String email,
    @Default(false) bool isAdmin,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

// Usage
final user = User(id: '1', name: 'Alice', email: 'alice@example.com');
final updated = user.copyWith(name: 'Alice Smith'); // immutable update
final json = user.toJson();
final fromJson = User.fromJson(json);
```

---

## 3. Async 組合

### 用 Future.wait 做結構化並行

```dart
Future<DashboardData> loadDashboard(UserRepository users, OrderRepository orders) async {
  // Run concurrently — don't await sequentially
  final (userList, orderList) = await (
    users.getAll(),
    orders.getRecent(),
  ).wait; // Dart 3 record destructuring + Future.wait extension

  return DashboardData(users: userList, orders: orderList);
}
```

### Stream 模式

```dart
// Repository exposes reactive streams for live data
Stream<List<Item>> watchCartItems() => _db
    .watchTable('cart_items')
    .map((rows) => rows.map(Item.fromRow).toList());

// In widget layer — declarative, no manual subscription
StreamBuilder<List<Item>>(
  stream: cartRepository.watchCartItems(),
  builder: (context, snapshot) => switch (snapshot) {
    AsyncSnapshot(connectionState: ConnectionState.waiting) =>
        const CircularProgressIndicator(),
    AsyncSnapshot(:final error?) => ErrorWidget(error.toString()),
    AsyncSnapshot(:final data?) => CartList(items: data),
    _ => const SizedBox.shrink(),
  },
)
```

### Await 之後的 BuildContext

```dart
// CRITICAL — always check mounted after any await in StatefulWidget
Future<void> _handleSubmit() async {
  setState(() => _isLoading = true);
  try {
    await authService.login(_email, _password);
    if (!mounted) return; // ← guard before using context
    context.go('/home');
  } on AuthException catch (e) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.message)));
  } finally {
    if (mounted) setState(() => _isLoading = false);
  }
}
```

---

## 4. Widget 架構

### 抽成類別，不要抽成方法

```dart
// BAD — private method returning widget, prevents optimization
Widget _buildHeader() {
  return Container(
    padding: const EdgeInsets.all(16),
    child: Text(title, style: Theme.of(context).textTheme.headlineMedium),
  );
}

// GOOD — separate widget class, enables const, element reuse
class _PageHeader extends StatelessWidget {
  const _PageHeader(this.title);
  final String title;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Text(title, style: Theme.of(context).textTheme.headlineMedium),
    );
  }
}
```

### const 的傳遞

```dart
// BAD — new instances every rebuild
child: Padding(
  padding: EdgeInsets.all(16.0),       // not const
  child: Icon(Icons.home, size: 24.0), // not const
)

// GOOD — const stops rebuild propagation
child: const Padding(
  padding: EdgeInsets.all(16.0),
  child: Icon(Icons.home, size: 24.0),
)
```

### 範圍限定的 Rebuild

```dart
// BAD — entire page rebuilds on every counter change
class CounterPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider); // rebuilds everything
    return Scaffold(
      body: Column(children: [
        const ExpensiveHeader(), // unnecessarily rebuilt
        Text('$count'),
        const ExpensiveFooter(), // unnecessarily rebuilt
      ]),
    );
  }
}

// GOOD — isolate the rebuilding part
class CounterPage extends StatelessWidget {
  const CounterPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Column(children: [
        ExpensiveHeader(),        // never rebuilt (const)
        _CounterDisplay(),        // only this rebuilds
        ExpensiveFooter(),        // never rebuilt (const)
      ]),
    );
  }
}

class _CounterDisplay extends ConsumerWidget {
  const _CounterDisplay();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    return Text('$count');
  }
}
```

---

## 5. 狀態管理：BLoC/Cubit

```dart
// Cubit — synchronous or simple async state
class AuthCubit extends Cubit<AuthState> {
  AuthCubit(this._authService) : super(const AuthState.initial());
  final AuthService _authService;

  Future<void> login(String email, String password) async {
    emit(const AuthState.loading());
    try {
      final user = await _authService.login(email, password);
      emit(AuthState.authenticated(user));
    } on AuthException catch (e) {
      emit(AuthState.error(e.message));
    }
  }

  void logout() {
    _authService.logout();
    emit(const AuthState.initial());
  }
}

// In widget
BlocBuilder<AuthCubit, AuthState>(
  builder: (context, state) => switch (state) {
    AuthInitial() => const LoginForm(),
    AuthLoading() => const CircularProgressIndicator(),
    AuthAuthenticated(:final user) => HomePage(user: user),
    AuthError(:final message) => ErrorView(message: message),
  },
)
```

---

## 6. 狀態管理：Riverpod

```dart
// Auto-dispose async provider
@riverpod
Future<List<Product>> products(Ref ref) async {
  final repo = ref.watch(productRepositoryProvider);
  return repo.getAll();
}

// Notifier with complex mutations
@riverpod
class CartNotifier extends _$CartNotifier {
  @override
  List<CartItem> build() => [];

  void add(Product product) {
    final existing = state.where((i) => i.productId == product.id).firstOrNull;
    if (existing != null) {
      state = [
        for (final item in state)
          if (item.productId == product.id) item.copyWith(quantity: item.quantity + 1)
          else item,
      ];
    } else {
      state = [...state, CartItem(productId: product.id, quantity: 1)];
    }
  }

  void remove(String productId) =>
      state = state.where((i) => i.productId != productId).toList();

  void clear() => state = [];
}

// Derived provider (selector pattern)
@riverpod
int cartCount(Ref ref) => ref.watch(cartNotifierProvider).length;

@riverpod
double cartTotal(Ref ref) {
  final cart = ref.watch(cartNotifierProvider);
  final products = ref.watch(productsProvider).valueOrNull ?? [];
  return cart.fold(0.0, (total, item) {
    // firstWhereOrNull (from collection package) avoids StateError when product is missing
    final product = products.firstWhereOrNull((p) => p.id == item.productId);
    return total + (product?.price ?? 0) * item.quantity;
  });
}
```

---

## 7. 用 GoRouter 做導覽

```dart
final router = GoRouter(
  initialLocation: '/',
  // refreshListenable re-evaluates redirect whenever auth state changes
  refreshListenable: GoRouterRefreshStream(authCubit.stream),
  redirect: (context, state) {
    final isLoggedIn = context.read<AuthCubit>().state is AuthAuthenticated;
    final isGoingToLogin = state.matchedLocation == '/login';
    if (!isLoggedIn && !isGoingToLogin) return '/login';
    if (isLoggedIn && isGoingToLogin) return '/';
    return null;
  },
  routes: [
    GoRoute(path: '/login', builder: (_, __) => const LoginPage()),
    ShellRoute(
      builder: (context, state, child) => AppShell(child: child),
      routes: [
        GoRoute(path: '/', builder: (_, __) => const HomePage()),
        GoRoute(
          path: '/products/:id',
          builder: (context, state) =>
              ProductDetailPage(id: state.pathParameters['id']!),
        ),
      ],
    ),
  ],
);
```

---

## 8. 用 Dio 做 HTTP

```dart
final dio = Dio(BaseOptions(
  baseUrl: const String.fromEnvironment('API_URL'),
  connectTimeout: const Duration(seconds: 10),
  receiveTimeout: const Duration(seconds: 30),
  headers: {'Content-Type': 'application/json'},
));

// Add auth interceptor
dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) async {
    final token = await secureStorage.read(key: 'auth_token');
    if (token != null) options.headers['Authorization'] = 'Bearer $token';
    handler.next(options);
  },
  onError: (error, handler) async {
    // Guard against infinite retry loops: only attempt refresh once per request
    final isRetry = error.requestOptions.extra['_isRetry'] == true;
    if (!isRetry && error.response?.statusCode == 401) {
      final refreshed = await attemptTokenRefresh();
      if (refreshed) {
        error.requestOptions.extra['_isRetry'] = true;
        return handler.resolve(await dio.fetch(error.requestOptions));
      }
    }
    handler.next(error);
  },
));

// Repository using Dio
class UserApiDataSource {
  const UserApiDataSource(this._dio);
  final Dio _dio;

  Future<User> getById(String id) async {
    final response = await _dio.get<Map<String, dynamic>>('/users/$id');
    return User.fromJson(response.data!);
  }
}
```

---

## 9. 錯誤處理架構

```dart
// Global error capture — set up in main()
void main() {
  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    crashlytics.recordFlutterFatalError(details);
  };

  PlatformDispatcher.instance.onError = (error, stack) {
    crashlytics.recordError(error, stack, fatal: true);
    return true;
  };

  runApp(const App());
}

// Custom ErrorWidget for production
class App extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    ErrorWidget.builder = (details) => ProductionErrorWidget(details);
    return MaterialApp.router(routerConfig: router);
  }
}
```

---

## 10. 測試速查

```dart
// Unit test — use case
test('GetUserUseCase returns null for missing user', () async {
  final repo = FakeUserRepository();
  final useCase = GetUserUseCase(repo);
  expect(await useCase('missing-id'), isNull);
});

// BLoC test
blocTest<AuthCubit, AuthState>(
  'emits loading then error on failed login',
  build: () => AuthCubit(FakeAuthService(throwsOn: 'login')),
  act: (cubit) => cubit.login('user@test.com', 'wrong'),
  expect: () => [const AuthState.loading(), isA<AuthError>()],
);

// Widget test
testWidgets('CartBadge shows item count', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [cartNotifierProvider.overrideWith(() => FakeCartNotifier(count: 3))],
      child: const MaterialApp(home: CartBadge()),
    ),
  );
  expect(find.text('3'), findsOneWidget);
});
```

---

## 參考資料

- [Effective Dart: Design](https://dart.dev/effective-dart/design)
- [Flutter Performance Best Practices](https://docs.flutter.dev/perf/best-practices)
- [Riverpod Documentation](https://riverpod.dev/)
- [BLoC Library](https://bloclibrary.dev/)
- [GoRouter](https://pub.dev/packages/go_router)
- [Freezed](https://pub.dev/packages/freezed)
- Skill：`flutter-dart-code-review`，完整的審查檢查清單
- Rules：`rules/dart/`，涵蓋程式風格、模式、安全、測試、hook
