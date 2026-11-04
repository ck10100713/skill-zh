---
name: laravel-patterns
description: 給 production 應用程式用的 Laravel 架構模式，包含路由/controller、Eloquent ORM、service 層、queue、event、快取與 API resource。在建構或 review Laravel 應用程式時使用（controller、Eloquent、service 層、queue 或 API resource）。
metadata:
  origin: ECC
---

# Laravel Development Patterns

用來打造可擴充、好維護的應用程式的 production 等級 Laravel 架構模式。

## 何時使用

- 建構 Laravel 網頁應用程式或 API
- 規劃 controller、service 與領域邏輯的結構
- 處理 Eloquent model 與關聯
- 用 resource 與分頁設計 API
- 加入 queue、event、快取與背景 job

## 運作方式

- 以清楚的邊界組織應用程式（controller -> service/action -> model）。
- 使用明確的 binding 與 scoped binding，讓路由行為可預期；存取控制仍然要做授權檢查。
- 多用有型別的 model、cast 與 scope，讓領域邏輯保持一致。
- IO 密集的工作放進 queue，昂貴的讀取加上快取。
- 設定集中放在 `config/*`，環境要明確。

## 範例

### 專案結構

用慣例的 Laravel 目錄配置，並讓各層（HTTP、service/action、model）邊界清楚。

### 建議的目錄配置

```
app/
├── Actions/            # Single-purpose use cases
├── Console/
├── Events/
├── Exceptions/
├── Http/
│   ├── Controllers/
│   ├── Middleware/
│   ├── Requests/       # Form request validation
│   └── Resources/      # API resources
├── Jobs/
├── Models/
├── Policies/
├── Providers/
├── Services/           # Coordinating domain services
└── Support/
config/
database/
├── factories/
├── migrations/
└── seeders/
resources/
├── views/
└── lang/
routes/
├── api.php
├── web.php
└── console.php
```

### Controller -> Service -> Action

Controller 保持精簡。協調流程放在 service，單一用途的邏輯放在 action。

```php
final class CreateOrderAction
{
    public function __construct(private OrderRepository $orders) {}

    public function handle(CreateOrderData $data): Order
    {
        return $this->orders->create($data);
    }
}

final class OrdersController extends Controller
{
    public function __construct(private CreateOrderAction $createOrder) {}

    public function store(StoreOrderRequest $request): JsonResponse
    {
        $order = $this->createOrder->handle($request->toDto());

        return response()->json([
            'success' => true,
            'data' => OrderResource::make($order),
            'error' => null,
            'meta' => null,
        ], 201);
    }
}
```

### 路由與 Controller

為了清楚起見，優先用 route-model binding 與 resource controller。

```php
use Illuminate\Support\Facades\Route;

Route::middleware('auth:sanctum')->group(function () {
    Route::apiResource('projects', ProjectController::class);
});
```

### Route Model Binding（Scoped）

用 scoped binding 防止跨租戶存取。

```php
Route::scopeBindings()->group(function () {
    Route::get('/accounts/{account}/projects/{project}', [ProjectController::class, 'show']);
});
```

### 巢狀路由與 Binding 名稱

- 前綴與路徑保持一致，避免重複巢狀（例如 `conversation` 與 `conversations`）。
- 使用單一參數名稱，並與綁定的 model 一致（例如 `Conversation` 用 `{conversation}`）。
- 巢狀時優先用 scoped binding，強制父子關係。

```php
use App\Http\Controllers\Api\ConversationController;
use App\Http\Controllers\Api\MessageController;
use Illuminate\Support\Facades\Route;

Route::middleware('auth:sanctum')->prefix('conversations')->group(function () {
    Route::post('/', [ConversationController::class, 'store'])->name('conversations.store');

    Route::scopeBindings()->group(function () {
        Route::get('/{conversation}', [ConversationController::class, 'show'])
            ->name('conversations.show');

        Route::post('/{conversation}/messages', [MessageController::class, 'store'])
            ->name('conversation-messages.store');

        Route::get('/{conversation}/messages/{message}', [MessageController::class, 'show'])
            ->name('conversation-messages.show');
    });
});
```

如果你想讓某個參數解析成不同的 model class，就定義明確的 binding。需要自訂 binding 邏輯時，用 `Route::bind()` 或在 model 上實作 `resolveRouteBinding()`。

```php
use App\Models\AiConversation;
use Illuminate\Support\Facades\Route;

Route::model('conversation', AiConversation::class);
```

### Service Container Binding

在 service provider 裡把介面綁到實作，讓依賴關係一目了然。

```php
use App\Repositories\EloquentOrderRepository;
use App\Repositories\OrderRepository;
use Illuminate\Support\ServiceProvider;

final class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->bind(OrderRepository::class, EloquentOrderRepository::class);
    }
}
```

### Eloquent Model 模式

### Model 設定

```php
final class Project extends Model
{
    use HasFactory;

    protected $fillable = ['name', 'owner_id', 'status'];

    protected $casts = [
        'status' => ProjectStatus::class,
        'archived_at' => 'datetime',
    ];

    public function owner(): BelongsTo
    {
        return $this->belongsTo(User::class, 'owner_id');
    }

    public function scopeActive(Builder $query): Builder
    {
        return $query->whereNull('archived_at');
    }
}
```

### 自訂 Cast 與 Value Object

用 enum 或 value object 做嚴格型別。

```php
use Illuminate\Database\Eloquent\Casts\Attribute;

protected $casts = [
    'status' => ProjectStatus::class,
];
```

```php
protected function budgetCents(): Attribute
{
    return Attribute::make(
        get: fn (int $value) => Money::fromCents($value),
        set: fn (Money $money) => $money->toCents(),
    );
}
```

### 用 Eager Loading 避免 N+1

```php
$orders = Order::query()
    ->with(['customer', 'items.product'])
    ->latest()
    ->paginate(25);
```

### 複雜篩選用 Query Object

```php
final class ProjectQuery
{
    public function __construct(private Builder $query) {}

    public function ownedBy(int $userId): self
    {
        $query = clone $this->query;

        return new self($query->where('owner_id', $userId));
    }

    public function active(): self
    {
        $query = clone $this->query;

        return new self($query->whereNull('archived_at'));
    }

    public function builder(): Builder
    {
        return $this->query;
    }
}
```

### Global Scope 與 Soft Delete

用 global scope 做預設篩選，用 `SoftDeletes` 處理可還原的資料。
同一個篩選條件，global scope 和 named scope 擇一使用就好，除非你刻意要疊加行為。

```php
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Database\Eloquent\Builder;

final class Project extends Model
{
    use SoftDeletes;

    protected static function booted(): void
    {
        static::addGlobalScope('active', function (Builder $builder): void {
            $builder->whereNull('archived_at');
        });
    }
}
```

### 可重用篩選用 Query Scope

```php
use Illuminate\Database\Eloquent\Builder;

final class Project extends Model
{
    public function scopeOwnedBy(Builder $query, int $userId): Builder
    {
        return $query->where('owner_id', $userId);
    }
}

// In service, repository etc.
$projects = Project::ownedBy($user->id)->get();
```

### 多步驟更新用 Transaction

```php
use Illuminate\Support\Facades\DB;

DB::transaction(function (): void {
    $order->update(['status' => 'paid']);
    $order->items()->update(['paid_at' => now()]);
});
```

### Migration

### 命名慣例

- 檔名使用時間戳記：`YYYY_MM_DD_HHMMSS_create_users_table.php`
- Migration 使用匿名 class（不取 class 名稱），由檔名表達意圖
- 資料表名稱預設是 `snake_case` 且用複數

### Migration 範例

```php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('orders', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('customer_id')->constrained()->cascadeOnDelete();
            $table->string('status', 32)->index();
            $table->unsignedInteger('total_cents');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('orders');
    }
};
```

### Form Request 與驗證

驗證放在 form request，並把輸入轉成 DTO。

```php
use App\Models\Order;

final class StoreOrderRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()?->can('create', Order::class) ?? false;
    }

    public function rules(): array
    {
        return [
            'customer_id' => ['required', 'integer', 'exists:customers,id'],
            'items' => ['required', 'array', 'min:1'],
            'items.*.sku' => ['required', 'string'],
            'items.*.quantity' => ['required', 'integer', 'min:1'],
        ];
    }

    public function toDto(): CreateOrderData
    {
        return new CreateOrderData(
            customerId: (int) $this->validated('customer_id'),
            items: $this->validated('items'),
        );
    }
}
```

### API Resource

用 resource 與分頁讓 API response 保持一致。

```php
$projects = Project::query()->active()->paginate(25);

return response()->json([
    'success' => true,
    'data' => ProjectResource::collection($projects->items()),
    'error' => null,
    'meta' => [
        'page' => $projects->currentPage(),
        'per_page' => $projects->perPage(),
        'total' => $projects->total(),
    ],
]);
```

### Event、Job 與 Queue

- 副作用（email、analytics）用 domain event 發出
- 慢的工作（報表、匯出、webhook）用 queued job
- 優先用冪等的 handler，搭配 retry 與 backoff

### 快取

- 快取讀取量大的 endpoint 與昂貴的查詢
- 在 model event（created/updated/deleted）時讓快取失效
- 快取相關資料時用 tag，方便一併失效

### 設定與環境

- secret 放 `.env`，設定放 `config/*.php`
- 使用各環境的設定覆寫，production 用 `config:cache`
