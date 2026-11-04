---
name: csharp-testing
description: C# 與 .NET 的測試模式，涵蓋 xUnit、FluentAssertions、mocking、整合測試，以及測試組織的最佳實務。在 C# / .NET 專案裡撰寫或審查 xUnit 測試、mock 或整合測試時使用。
metadata:
  origin: ECC
---

# C# 測試模式

用 xUnit、FluentAssertions 和現代測試實務，為 .NET 應用程式整理的完整測試模式。

## 何時啟用

- 為 C# 程式碼撰寫新的測試
- 審查測試品質和涵蓋率
- 為 .NET 專案建立測試基礎設施
- 除錯 flaky 或很慢的測試

## 測試框架組合

| 工具 | 用途 |
|---|---|
| **xUnit** | 測試框架（.NET 首選） |
| **FluentAssertions** | 好讀的 assertion 語法 |
| **NSubstitute** 或 **Moq** | mock 依賴 |
| **Testcontainers** | 整合測試裡使用真實的基礎設施 |
| **WebApplicationFactory** | ASP.NET Core 整合測試 |
| **Bogus** | 產生擬真的測試資料 |

## 單元測試結構

### Arrange-Act-Assert

```csharp
public sealed class OrderServiceTests
{
    private readonly IOrderRepository _repository = Substitute.For<IOrderRepository>();
    private readonly ILogger<OrderService> _logger = Substitute.For<ILogger<OrderService>>();
    private readonly OrderService _sut;

    public OrderServiceTests()
    {
        _sut = new OrderService(_repository, _logger);
    }

    [Fact]
    public async Task PlaceOrderAsync_ReturnsSuccess_WhenRequestIsValid()
    {
        // Arrange
        var request = new CreateOrderRequest
        {
            CustomerId = "cust-123",
            Items = [new OrderItem("SKU-001", 2, 29.99m)]
        };

        // Act
        var result = await _sut.PlaceOrderAsync(request, CancellationToken.None);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.Value.Should().NotBeNull();
        result.Value!.CustomerId.Should().Be("cust-123");
    }

    [Fact]
    public async Task PlaceOrderAsync_ReturnsFailure_WhenNoItems()
    {
        // Arrange
        var request = new CreateOrderRequest
        {
            CustomerId = "cust-123",
            Items = []
        };

        // Act
        var result = await _sut.PlaceOrderAsync(request, CancellationToken.None);

        // Assert
        result.IsSuccess.Should().BeFalse();
        result.Error.Should().Contain("at least one item");
    }
}
```

### 用 Theory 寫參數化測試

```csharp
[Theory]
[InlineData("", false)]
[InlineData("a", false)]
[InlineData("ab@c.d", false)]
[InlineData("user@example.com", true)]
[InlineData("user+tag@example.co.uk", true)]
public void IsValidEmail_ReturnsExpected(string email, bool expected)
{
    EmailValidator.IsValid(email).Should().Be(expected);
}

[Theory]
[MemberData(nameof(InvalidOrderCases))]
public async Task PlaceOrderAsync_RejectsInvalidOrders(CreateOrderRequest request, string expectedError)
{
    var result = await _sut.PlaceOrderAsync(request, CancellationToken.None);

    result.IsSuccess.Should().BeFalse();
    result.Error.Should().Contain(expectedError);
}

public static TheoryData<CreateOrderRequest, string> InvalidOrderCases => new()
{
    { new() { CustomerId = "", Items = [ValidItem()] }, "CustomerId" },
    { new() { CustomerId = "c1", Items = [] }, "at least one item" },
    { new() { CustomerId = "c1", Items = [new("", 1, 10m)] }, "SKU" },
};
```

## 用 NSubstitute 做 Mocking

```csharp
[Fact]
public async Task GetOrderAsync_ReturnsNull_WhenNotFound()
{
    // Arrange
    var orderId = Guid.NewGuid();
    _repository.FindByIdAsync(orderId, Arg.Any<CancellationToken>())
        .Returns((Order?)null);

    // Act
    var result = await _sut.GetOrderAsync(orderId, CancellationToken.None);

    // Assert
    result.Should().BeNull();
}

[Fact]
public async Task PlaceOrderAsync_PersistsOrder()
{
    // Arrange
    var request = ValidOrderRequest();

    // Act
    await _sut.PlaceOrderAsync(request, CancellationToken.None);

    // Assert — verify the repository was called
    await _repository.Received(1).AddAsync(
        Arg.Is<Order>(o => o.CustomerId == request.CustomerId),
        Arg.Any<CancellationToken>());
}
```

## ASP.NET Core 整合測試

### WebApplicationFactory 設定

```csharp
public sealed class OrderApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public OrderApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace real DB with in-memory for tests
                services.RemoveAll<DbContextOptions<AppDbContext>>();
                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));
            });
        }).CreateClient();
    }

    [Fact]
    public async Task GetOrder_Returns404_WhenNotFound()
    {
        var response = await _client.GetAsync($"/api/orders/{Guid.NewGuid()}");

        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task CreateOrder_Returns201_WithValidRequest()
    {
        var request = new CreateOrderRequest
        {
            CustomerId = "cust-1",
            Items = [new("SKU-001", 1, 19.99m)]
        };

        var response = await _client.PostAsJsonAsync("/api/orders", request);

        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();
    }
}
```

### 用 Testcontainers 測試

```csharp
public sealed class PostgresOrderRepositoryTests : IAsyncLifetime
{
    private readonly PostgreSqlContainer _postgres = new PostgreSqlBuilder()
        .WithImage("postgres:16-alpine")
        .Build();

    private AppDbContext _db = null!;

    public async Task InitializeAsync()
    {
        await _postgres.StartAsync();
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseNpgsql(_postgres.GetConnectionString())
            .Options;
        _db = new AppDbContext(options);
        await _db.Database.MigrateAsync();
    }

    public async Task DisposeAsync()
    {
        await _db.DisposeAsync();
        await _postgres.DisposeAsync();
    }

    [Fact]
    public async Task AddAsync_PersistsOrder()
    {
        var repo = new SqlOrderRepository(_db);
        var order = Order.Create("cust-1", [new OrderItem("SKU-001", 2, 10m)]);

        await repo.AddAsync(order, CancellationToken.None);

        var found = await repo.FindByIdAsync(order.Id, CancellationToken.None);
        found.Should().NotBeNull();
        found!.Items.Should().HaveCount(1);
    }
}
```

## 測試組織

```
tests/
  MyApp.UnitTests/
    Services/
      OrderServiceTests.cs
      PaymentServiceTests.cs
    Validators/
      EmailValidatorTests.cs
  MyApp.IntegrationTests/
    Api/
      OrderApiTests.cs
    Repositories/
      OrderRepositoryTests.cs
  MyApp.TestHelpers/
    Builders/
      OrderBuilder.cs
    Fixtures/
      DatabaseFixture.cs
```

## 測試資料 Builder

```csharp
public sealed class OrderBuilder
{
    private string _customerId = "cust-default";
    private readonly List<OrderItem> _items = [new("SKU-001", 1, 10m)];

    public OrderBuilder WithCustomer(string customerId)
    {
        _customerId = customerId;
        return this;
    }

    public OrderBuilder WithItem(string sku, int quantity, decimal price)
    {
        _items.Add(new OrderItem(sku, quantity, price));
        return this;
    }

    public Order Build() => Order.Create(_customerId, _items);
}

// Usage in tests
var order = new OrderBuilder()
    .WithCustomer("cust-vip")
    .WithItem("SKU-PREMIUM", 3, 99.99m)
    .Build();
```

## 常見反模式

| 反模式 | 修正方式 |
|---|---|
| 測試實作細節 | 測試行為和結果 |
| 共用的可變測試狀態 | 每個測試用全新的實例（xUnit 透過建構函式就做到了） |
| 在 async 測試裡用 `Thread.Sleep` | 用帶 timeout 的 `Task.Delay`，或 polling helper |
| 對 `ToString()` 的輸出做 assertion | 對有型別的屬性做 assertion |
| 每個測試一個巨大的 assertion | 每個測試一個邏輯上的 assertion |
| 測試名稱描述實作 | 用行為命名：`Method_ExpectedResult_WhenCondition` |
| 忽略 `CancellationToken` | 一律傳入並驗證取消行為 |

## 執行測試

```bash
# Run all tests
dotnet test

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"

# Run specific project
dotnet test tests/MyApp.UnitTests/

# Filter by test name
dotnet test --filter "FullyQualifiedName~OrderService"

# Watch mode during development
dotnet watch test --project tests/MyApp.UnitTests/
```
