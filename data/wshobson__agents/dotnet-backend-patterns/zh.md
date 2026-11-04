---
name: dotnet-backend-patterns
description: 精通 C#/.NET 後端開發模式，用來建構穩健的 API、MCP server 與企業級應用。涵蓋 async/await、dependency injection、Entity Framework Core、Dapper、設定、快取，以及用 xUnit 做測試。適用於開發 .NET 後端、review C# 程式碼，或設計 API 架構的時候。
---

# .NET 後端開發模式

精通 C#/.NET 模式，用現代最佳實務（2024/2025）建構 production 等級的 API、MCP server 與企業後端。

## 什麼時候用這個 Skill

- 開發新的 .NET Web API 或 MCP server
- Review C# 程式碼的品質與效能
- 用 dependency injection 設計服務架構
- 用 Redis 實作快取策略
- 撰寫單元測試與整合測試
- 用 EF Core 或 Dapper 最佳化資料庫存取
- 用 IOptions 模式設定應用程式
- 處理錯誤並實作 resilience 模式

## 核心概念

### 1. 專案結構（Clean Architecture）

```
src/
├── Domain/                     # 核心商業邏輯（無相依）
│   ├── Entities/
│   ├── Interfaces/
│   ├── Exceptions/
│   └── ValueObjects/
├── Application/                # Use case、DTO、驗證
│   ├── Services/
│   ├── DTOs/
│   ├── Validators/
│   └── Interfaces/
├── Infrastructure/             # 外部實作
│   ├── Data/                   # EF Core、Dapper repository
│   ├── Caching/                # Redis、Memory cache
│   ├── External/               # HTTP client、第三方 API
│   └── DependencyInjection/    # 服務註冊
└── Api/                        # 進入點
    ├── Controllers/            # 或 MinimalAPI endpoint
    ├── Middleware/
    ├── Filters/
    └── Program.cs
```

### 2. Dependency Injection 模式

```csharp
// 依生命週期註冊服務
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        // Scoped：每個 HTTP 請求一個實例
        services.AddScoped<IProductService, ProductService>();
        services.AddScoped<IOrderService, OrderService>();

        // Singleton：整個應用程式生命週期一個實例
        services.AddSingleton<ICacheService, RedisCacheService>();
        services.AddSingleton<IConnectionMultiplexer>(_ =>
            ConnectionMultiplexer.Connect(configuration["Redis:Connection"]!));

        // Transient：每次都建立新實例
        services.AddTransient<IValidator<CreateOrderRequest>, CreateOrderValidator>();

        // 用 Options 模式處理設定
        services.Configure<CatalogOptions>(configuration.GetSection("Catalog"));
        services.Configure<RedisOptions>(configuration.GetSection("Redis"));

        // 用 Factory 模式做條件式建立
        services.AddScoped<IPriceCalculator>(sp =>
        {
            var options = sp.GetRequiredService<IOptions<PricingOptions>>().Value;
            return options.UseNewEngine
                ? sp.GetRequiredService<NewPriceCalculator>()
                : sp.GetRequiredService<LegacyPriceCalculator>();
        });

        // Keyed service（.NET 8+）
        services.AddKeyedScoped<IPaymentProcessor, StripeProcessor>("stripe");
        services.AddKeyedScoped<IPaymentProcessor, PayPalProcessor>("paypal");

        return services;
    }
}

// 使用 keyed service
public class CheckoutService
{
    public CheckoutService(
        [FromKeyedServices("stripe")] IPaymentProcessor stripeProcessor)
    {
        _processor = stripeProcessor;
    }
}
```

### 3. Async/Await 模式

```csharp
// ✅ 正確：從頭到尾都用 async
public async Task<Product> GetProductAsync(string id, CancellationToken ct = default)
{
    return await _repository.GetByIdAsync(id, ct);
}

// ✅ 正確：用 WhenAll 平行執行
public async Task<(Stock, Price)> GetStockAndPriceAsync(
    string productId,
    CancellationToken ct = default)
{
    var stockTask = _stockService.GetAsync(productId, ct);
    var priceTask = _priceService.GetAsync(productId, ct);

    await Task.WhenAll(stockTask, priceTask);

    return (await stockTask, await priceTask);
}

// ✅ 正確：在函式庫中用 ConfigureAwait
public async Task<T> LibraryMethodAsync<T>(CancellationToken ct = default)
{
    var result = await _httpClient.GetAsync(url, ct).ConfigureAwait(false);
    return await result.Content.ReadFromJsonAsync<T>(ct).ConfigureAwait(false);
}

// ✅ 正確：有快取的熱路徑用 ValueTask
public ValueTask<Product?> GetCachedProductAsync(string id)
{
    if (_cache.TryGetValue(id, out Product? product))
        return ValueTask.FromResult(product);

    return new ValueTask<Product?>(GetFromDatabaseAsync(id));
}

// ❌ 錯誤：對 async 做阻塞（有 deadlock 風險）
var result = GetProductAsync(id).Result;  // 絕對不要這樣做
var result2 = GetProductAsync(id).GetAwaiter().GetResult(); // 一樣很糟

// ❌ 錯誤：async void（event handler 除外）
public async void ProcessOrder() { }  // Exception 會遺失

// ❌ 錯誤：對已經是 async 的程式碼多包一層不必要的 Task.Run
await Task.Run(async () => await GetDataAsync());  // 浪費 thread
```

### 4. 用 IOptions 做設定

```csharp
// 設定類別
public class CatalogOptions
{
    public const string SectionName = "Catalog";

    public int DefaultPageSize { get; set; } = 50;
    public int MaxPageSize { get; set; } = 200;
    public TimeSpan CacheDuration { get; set; } = TimeSpan.FromMinutes(15);
    public bool EnableEnrichment { get; set; } = true;
}

public class RedisOptions
{
    public const string SectionName = "Redis";

    public string Connection { get; set; } = "localhost:6379";
    public string KeyPrefix { get; set; } = "mcp:";
    public int Database { get; set; } = 0;
}

// appsettings.json
{
    "Catalog": {
        "DefaultPageSize": 50,
        "MaxPageSize": 200,
        "CacheDuration": "00:15:00",
        "EnableEnrichment": true
    },
    "Redis": {
        "Connection": "localhost:6379",
        "KeyPrefix": "mcp:",
        "Database": 0
    }
}

// 註冊
services.Configure<CatalogOptions>(configuration.GetSection(CatalogOptions.SectionName));
services.Configure<RedisOptions>(configuration.GetSection(RedisOptions.SectionName));

// 搭配 IOptions 使用（singleton，啟動時只讀一次）
public class CatalogService
{
    private readonly CatalogOptions _options;

    public CatalogService(IOptions<CatalogOptions> options)
    {
        _options = options.Value;
    }
}

// 搭配 IOptionsSnapshot 使用（scoped，每次請求重新讀取）
public class DynamicService
{
    private readonly CatalogOptions _options;

    public DynamicService(IOptionsSnapshot<CatalogOptions> options)
    {
        _options = options.Value;  // 每次請求都是最新的值
    }
}

// 搭配 IOptionsMonitor 使用（singleton，有變更時會收到通知）
public class MonitoredService
{
    private CatalogOptions _options;

    public MonitoredService(IOptionsMonitor<CatalogOptions> monitor)
    {
        _options = monitor.CurrentValue;
        monitor.OnChange(newOptions => _options = newOptions);
    }
}
```

### 5. Result 模式（避免用 Exception 控制流程）

```csharp
// 泛型 Result 型別
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }
    public string? ErrorCode { get; }

    private Result(bool isSuccess, T? value, string? error, string? errorCode)
    {
        IsSuccess = isSuccess;
        Value = value;
        Error = error;
        ErrorCode = errorCode;
    }

    public static Result<T> Success(T value) => new(true, value, null, null);
    public static Result<T> Failure(string error, string? code = null) => new(false, default, error, code);

    public Result<TNew> Map<TNew>(Func<T, TNew> mapper) =>
        IsSuccess ? Result<TNew>.Success(mapper(Value!)) : Result<TNew>.Failure(Error!, ErrorCode);

    public async Task<Result<TNew>> MapAsync<TNew>(Func<T, Task<TNew>> mapper) =>
        IsSuccess ? Result<TNew>.Success(await mapper(Value!)) : Result<TNew>.Failure(Error!, ErrorCode);
}

// 在 service 中使用
public async Task<Result<Order>> CreateOrderAsync(CreateOrderRequest request, CancellationToken ct)
{
    // 驗證
    var validation = await _validator.ValidateAsync(request, ct);
    if (!validation.IsValid)
        return Result<Order>.Failure(
            validation.Errors.First().ErrorMessage,
            "VALIDATION_ERROR");

    // 商業規則檢查
    var stock = await _stockService.CheckAsync(request.ProductId, request.Quantity, ct);
    if (!stock.IsAvailable)
        return Result<Order>.Failure(
            $"Insufficient stock: {stock.Available} available, {request.Quantity} requested",
            "INSUFFICIENT_STOCK");

    // 建立訂單
    var order = await _repository.CreateAsync(request.ToEntity(), ct);

    return Result<Order>.Success(order);
}

// 在 controller/endpoint 中使用
app.MapPost("/orders", async (
    CreateOrderRequest request,
    IOrderService orderService,
    CancellationToken ct) =>
{
    var result = await orderService.CreateOrderAsync(request, ct);

    return result.IsSuccess
        ? Results.Created($"/orders/{result.Value!.Id}", result.Value)
        : Results.BadRequest(new { error = result.Error, code = result.ErrorCode });
});
```

## 資料存取模式

### Entity Framework Core

```csharp
// DbContext 設定
public class AppDbContext : DbContext
{
    public DbSet<Product> Products => Set<Product>();
    public DbSet<Order> Orders => Set<Order>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // 套用 assembly 中所有的設定
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);

        // 全域 query filter
        modelBuilder.Entity<Product>().HasQueryFilter(p => !p.IsDeleted);
    }
}

// Entity 設定
public class ProductConfiguration : IEntityTypeConfiguration<Product>
{
    public void Configure(EntityTypeBuilder<Product> builder)
    {
        builder.ToTable("Products");

        builder.HasKey(p => p.Id);
        builder.Property(p => p.Id).HasMaxLength(40);
        builder.Property(p => p.Name).HasMaxLength(200).IsRequired();
        builder.Property(p => p.Price).HasPrecision(18, 2);

        builder.HasIndex(p => p.Sku).IsUnique();
        builder.HasIndex(p => new { p.CategoryId, p.Name });

        builder.HasMany(p => p.OrderItems)
            .WithOne(oi => oi.Product)
            .HasForeignKey(oi => oi.ProductId);
    }
}

// 搭配 EF Core 的 Repository
public class ProductRepository : IProductRepository
{
    private readonly AppDbContext _context;

    public async Task<Product?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        return await _context.Products
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Id == id, ct);
    }

    public async Task<IReadOnlyList<Product>> SearchAsync(
        ProductSearchCriteria criteria,
        CancellationToken ct = default)
    {
        var query = _context.Products.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(criteria.SearchTerm))
            query = query.Where(p => EF.Functions.Like(p.Name, $"%{criteria.SearchTerm}%"));

        if (criteria.CategoryId.HasValue)
            query = query.Where(p => p.CategoryId == criteria.CategoryId);

        if (criteria.MinPrice.HasValue)
            query = query.Where(p => p.Price >= criteria.MinPrice);

        if (criteria.MaxPrice.HasValue)
            query = query.Where(p => p.Price <= criteria.MaxPrice);

        return await query
            .OrderBy(p => p.Name)
            .Skip((criteria.Page - 1) * criteria.PageSize)
            .Take(criteria.PageSize)
            .ToListAsync(ct);
    }
}
```

### 用 Dapper 追求效能

```csharp
public class DapperProductRepository : IProductRepository
{
    private readonly IDbConnection _connection;

    public async Task<Product?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        const string sql = """
            SELECT Id, Name, Sku, Price, CategoryId, Stock, CreatedAt
            FROM Products
            WHERE Id = @Id AND IsDeleted = 0
            """;

        return await _connection.QueryFirstOrDefaultAsync<Product>(
            new CommandDefinition(sql, new { Id = id }, cancellationToken: ct));
    }

    public async Task<IReadOnlyList<Product>> SearchAsync(
        ProductSearchCriteria criteria,
        CancellationToken ct = default)
    {
        var sql = new StringBuilder("""
            SELECT Id, Name, Sku, Price, CategoryId, Stock, CreatedAt
            FROM Products
            WHERE IsDeleted = 0
            """);

        var parameters = new DynamicParameters();

        if (!string.IsNullOrWhiteSpace(criteria.SearchTerm))
        {
            sql.Append(" AND Name LIKE @SearchTerm");
            parameters.Add("SearchTerm", $"%{criteria.SearchTerm}%");
        }

        if (criteria.CategoryId.HasValue)
        {
            sql.Append(" AND CategoryId = @CategoryId");
            parameters.Add("CategoryId", criteria.CategoryId);
        }

        if (criteria.MinPrice.HasValue)
        {
            sql.Append(" AND Price >= @MinPrice");
            parameters.Add("MinPrice", criteria.MinPrice);
        }

        if (criteria.MaxPrice.HasValue)
        {
            sql.Append(" AND Price <= @MaxPrice");
            parameters.Add("MaxPrice", criteria.MaxPrice);
        }

        sql.Append(" ORDER BY Name OFFSET @Offset ROWS FETCH NEXT @PageSize ROWS ONLY");
        parameters.Add("Offset", (criteria.Page - 1) * criteria.PageSize);
        parameters.Add("PageSize", criteria.PageSize);

        var results = await _connection.QueryAsync<Product>(
            new CommandDefinition(sql.ToString(), parameters, cancellationToken: ct));

        return results.ToList();
    }

    // 對關聯資料做 multi-mapping
    public async Task<Order?> GetOrderWithItemsAsync(int orderId, CancellationToken ct = default)
    {
        const string sql = """
            SELECT o.*, oi.*, p.*
            FROM Orders o
            LEFT JOIN OrderItems oi ON o.Id = oi.OrderId
            LEFT JOIN Products p ON oi.ProductId = p.Id
            WHERE o.Id = @OrderId
            """;

        var orderDictionary = new Dictionary<int, Order>();

        await _connection.QueryAsync<Order, OrderItem, Product, Order>(
            new CommandDefinition(sql, new { OrderId = orderId }, cancellationToken: ct),
            (order, item, product) =>
            {
                if (!orderDictionary.TryGetValue(order.Id, out var existingOrder))
                {
                    existingOrder = order;
                    existingOrder.Items = new List<OrderItem>();
                    orderDictionary.Add(order.Id, existingOrder);
                }

                if (item != null)
                {
                    item.Product = product;
                    existingOrder.Items.Add(item);
                }

                return existingOrder;
            },
            splitOn: "Id,Id");

        return orderDictionary.Values.FirstOrDefault();
    }
}
```

## 快取模式

### 搭配 Redis 的多層快取

```csharp
public class CachedProductService : IProductService
{
    private readonly IProductRepository _repository;
    private readonly IMemoryCache _memoryCache;
    private readonly IDistributedCache _distributedCache;
    private readonly ILogger<CachedProductService> _logger;

    private static readonly TimeSpan MemoryCacheDuration = TimeSpan.FromMinutes(1);
    private static readonly TimeSpan DistributedCacheDuration = TimeSpan.FromMinutes(15);

    public async Task<Product?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        var cacheKey = $"product:{id}";

        // L1：Memory cache（行程內，最快）
        if (_memoryCache.TryGetValue(cacheKey, out Product? cached))
        {
            _logger.LogDebug("L1 cache hit for {CacheKey}", cacheKey);
            return cached;
        }

        // L2：分散式快取（Redis）
        var distributed = await _distributedCache.GetStringAsync(cacheKey, ct);
        if (distributed != null)
        {
            _logger.LogDebug("L2 cache hit for {CacheKey}", cacheKey);
            var product = JsonSerializer.Deserialize<Product>(distributed);

            // 填入 L1
            _memoryCache.Set(cacheKey, product, MemoryCacheDuration);
            return product;
        }

        // L3：資料庫
        _logger.LogDebug("Cache miss for {CacheKey}, fetching from database", cacheKey);
        var fromDb = await _repository.GetByIdAsync(id, ct);

        if (fromDb != null)
        {
            var serialized = JsonSerializer.Serialize(fromDb);

            // 兩層快取都填入
            await _distributedCache.SetStringAsync(
                cacheKey,
                serialized,
                new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = DistributedCacheDuration
                },
                ct);

            _memoryCache.Set(cacheKey, fromDb, MemoryCacheDuration);
        }

        return fromDb;
    }

    public async Task InvalidateAsync(string id, CancellationToken ct = default)
    {
        var cacheKey = $"product:{id}";

        _memoryCache.Remove(cacheKey);
        await _distributedCache.RemoveAsync(cacheKey, ct);

        _logger.LogInformation("Invalidated cache for {CacheKey}", cacheKey);
    }
}

// Stale-while-revalidate 模式
public class StaleWhileRevalidateCache<T>
{
    private readonly IDistributedCache _cache;
    private readonly TimeSpan _freshDuration;
    private readonly TimeSpan _staleDuration;

    public async Task<T?> GetOrCreateAsync(
        string key,
        Func<CancellationToken, Task<T>> factory,
        CancellationToken ct = default)
    {
        var cached = await _cache.GetStringAsync(key, ct);

        if (cached != null)
        {
            var entry = JsonSerializer.Deserialize<CacheEntry<T>>(cached)!;

            if (entry.IsStale && !entry.IsExpired)
            {
                // 立即回傳過期資料，同時在背景重新整理
                _ = Task.Run(async () =>
                {
                    var fresh = await factory(CancellationToken.None);
                    await SetAsync(key, fresh, CancellationToken.None);
                });
            }

            if (!entry.IsExpired)
                return entry.Value;
        }

        // 快取未命中或已過期
        var value = await factory(ct);
        await SetAsync(key, value, ct);
        return value;
    }

    private record CacheEntry<TValue>(TValue Value, DateTime CreatedAt)
    {
        public bool IsStale => DateTime.UtcNow - CreatedAt > _freshDuration;
        public bool IsExpired => DateTime.UtcNow - CreatedAt > _staleDuration;
    }
}
```

## 測試模式

### 用 xUnit 和 Moq 做單元測試

```csharp
public class OrderServiceTests
{
    private readonly Mock<IOrderRepository> _mockRepository;
    private readonly Mock<IStockService> _mockStockService;
    private readonly Mock<IValidator<CreateOrderRequest>> _mockValidator;
    private readonly OrderService _sut; // 受測系統（System Under Test）

    public OrderServiceTests()
    {
        _mockRepository = new Mock<IOrderRepository>();
        _mockStockService = new Mock<IStockService>();
        _mockValidator = new Mock<IValidator<CreateOrderRequest>>();

        // 預設：驗證通過
        _mockValidator
            .Setup(v => v.ValidateAsync(It.IsAny<CreateOrderRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new ValidationResult());

        _sut = new OrderService(
            _mockRepository.Object,
            _mockStockService.Object,
            _mockValidator.Object);
    }

    [Fact]
    public async Task CreateOrderAsync_WithValidRequest_ReturnsSuccess()
    {
        // Arrange（準備）
        var request = new CreateOrderRequest
        {
            ProductId = "PROD-001",
            Quantity = 5,
            CustomerOrderCode = "ORD-2024-001"
        };

        _mockStockService
            .Setup(s => s.CheckAsync("PROD-001", 5, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new StockResult { IsAvailable = true, Available = 10 });

        _mockRepository
            .Setup(r => r.CreateAsync(It.IsAny<Order>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new Order { Id = 1, CustomerOrderCode = "ORD-2024-001" });

        // Act（執行）
        var result = await _sut.CreateOrderAsync(request);

        // Assert（驗證）
        Assert.True(result.IsSuccess);
        Assert.NotNull(result.Value);
        Assert.Equal(1, result.Value.Id);

        _mockRepository.Verify(
            r => r.CreateAsync(It.Is<Order>(o => o.CustomerOrderCode == "ORD-2024-001"),
            It.IsAny<CancellationToken>()),
            Times.Once);
    }

    [Fact]
    public async Task CreateOrderAsync_WithInsufficientStock_ReturnsFailure()
    {
        // Arrange（準備）
        var request = new CreateOrderRequest { ProductId = "PROD-001", Quantity = 100 };

        _mockStockService
            .Setup(s => s.CheckAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new StockResult { IsAvailable = false, Available = 5 });

        // Act（執行）
        var result = await _sut.CreateOrderAsync(request);

        // Assert（驗證）
        Assert.False(result.IsSuccess);
        Assert.Equal("INSUFFICIENT_STOCK", result.ErrorCode);
        Assert.Contains("5 available", result.Error);

        _mockRepository.Verify(
            r => r.CreateAsync(It.IsAny<Order>(), It.IsAny<CancellationToken>()),
            Times.Never);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    [InlineData(-100)]
    public async Task CreateOrderAsync_WithInvalidQuantity_ReturnsValidationError(int quantity)
    {
        // Arrange（準備）
        var request = new CreateOrderRequest { ProductId = "PROD-001", Quantity = quantity };

        _mockValidator
            .Setup(v => v.ValidateAsync(request, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new ValidationResult(new[]
            {
                new ValidationFailure("Quantity", "Quantity must be greater than 0")
            }));

        // Act（執行）
        var result = await _sut.CreateOrderAsync(request);

        // Assert（驗證）
        Assert.False(result.IsSuccess);
        Assert.Equal("VALIDATION_ERROR", result.ErrorCode);
    }
}
```

### 用 WebApplicationFactory 做整合測試

```csharp
public class ProductsApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;

    public ProductsApiTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // 用 in-memory 取代真實資料庫
                services.RemoveAll<DbContextOptions<AppDbContext>>();
                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));

                // 用 memory cache 取代 Redis
                services.RemoveAll<IDistributedCache>();
                services.AddDistributedMemoryCache();
            });
        });

        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task GetProduct_WithValidId_ReturnsProduct()
    {
        // Arrange（準備）
        using var scope = _factory.Services.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

        context.Products.Add(new Product
        {
            Id = "TEST-001",
            Name = "Test Product",
            Price = 99.99m
        });
        await context.SaveChangesAsync();

        // Act（執行）
        var response = await _client.GetAsync("/api/products/TEST-001");

        // Assert（驗證）
        response.EnsureSuccessStatusCode();
        var product = await response.Content.ReadFromJsonAsync<Product>();
        Assert.Equal("Test Product", product!.Name);
    }

    [Fact]
    public async Task GetProduct_WithInvalidId_Returns404()
    {
        // Act（執行）
        var response = await _client.GetAsync("/api/products/NONEXISTENT");

        // Assert（驗證）
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}
```

## 最佳實務

### 該做的

1. **全面使用 async/await**：整條 call stack 都用
2. **注入相依項目**：用 constructor injection
3. **用 IOptions<T>** 處理具型別的設定
4. **回傳 Result 型別**，不要在商業邏輯中丟 exception
5. **所有 async 方法都用 CancellationToken**
6. **讀取量大、對效能要求高的查詢優先用 Dapper**
7. **複雜的 domain model 需要 change tracking 時用 EF Core**
8. **積極快取**，並搭配適當的失效策略
9. **商業邏輯寫單元測試，API 寫整合測試**
10. **DTO 與不可變資料用 record 型別**

### 不該做的

1. **不要對 async 做阻塞**，例如 `.Result` 或 `.Wait()`
2. **不要用 async void**，event handler 除外
3. **不要捕捉泛型 Exception**，除非會重新丟出或記錄
4. **不要寫死**設定值
5. **不要直接在 API 暴露 EF entity**（用 DTO）
6. **不要忘記**在唯讀查詢用 `AsNoTracking()`
7. **不要忽略** CancellationToken 參數
8. **不要手動** `new HttpClient()`（用 IHttpClientFactory）
9. **不要沒必要地混用**同步與非同步程式碼
10. **不要跳過** API 邊界的驗證

## 常見陷阱

- **N+1 Query**：用 `.Include()` 或明確的 join
- **記憶體洩漏**：釋放 IDisposable 資源，用 `using`
- **Deadlock**：不要混用同步與非同步，函式庫中用 ConfigureAwait(false)
- **過度撈取**：只 select 需要的欄位，用 projection
- **缺少索引**：看 query plan，為常見的 filter 加索引
- **Timeout 問題**：為 HTTP client 設定適當的 timeout
- **Cache Stampede**：快取填入時用分散式鎖
