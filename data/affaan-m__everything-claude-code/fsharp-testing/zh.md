---
name: fsharp-testing
description: 用 xUnit、FsUnit、Unquote、FsCheck 屬性測試、整合測試的 F# 測試模式，以及測試組織的最佳實務。用 xUnit、FsUnit、Unquote 或 FsCheck 寫 F# 測試時使用。
metadata:
  origin: ECC
---

# F# Testing Patterns

用 xUnit、FsUnit、Unquote、FsCheck 和現代 .NET 測試實務，替 F# 應用程式做測試的完整模式。

## When to Activate

- 為 F# 程式碼寫新測試
- review 測試品質與覆蓋率
- 為 F# 專案建置測試基礎設施
- 除錯 flaky 或很慢的測試

## Test Framework Stack

| Tool | Purpose |
|---|---|
| **xUnit** | 測試框架（標準 .NET 生態系的選擇） |
| **FsUnit.xUnit** | 對 F# 友善的 xUnit 斷言語法 |
| **Unquote** | 用 F# quotation 的斷言函式庫，失敗訊息很清楚 |
| **FsCheck.xUnit** | 跟 xUnit 整合的屬性測試（property-based testing） |
| **NSubstitute** | mock .NET 依賴 |
| **Testcontainers** | 整合測試用真實的基礎設施 |
| **WebApplicationFactory** | ASP.NET Core 整合測試 |

## Unit Tests with xUnit + FsUnit

### Basic Test Structure

```fsharp
module OrderServiceTests

open Xunit
open FsUnit.Xunit

[<Fact>]
let ``create sets status to Pending`` () =
    let order = Order.create "cust-1" [ validItem ]
    order.Status |> should equal Pending

[<Fact>]
let ``confirm changes status to Confirmed`` () =
    let order = Order.create "cust-1" [ validItem ]
    let confirmed = Order.confirm order
    confirmed.Status |> should be (ofCase <@ Confirmed @>)
```

### Assertions with Unquote

Unquote 用 F# quotation，所以失敗訊息會顯示失敗的完整運算式，不只是「expected X got Y」。

```fsharp
module OrderValidationTests

open Xunit
open Swensen.Unquote

[<Fact>]
let ``PlaceOrder returns success when request is valid`` () =
    let request = { CustomerId = "cust-123"; Items = [ validItem ] }
    let result = OrderService.placeOrder request
    test <@ Result.isOk result @>

[<Fact>]
let ``order total sums item prices`` () =
    let items = [ { Sku = "A"; Quantity = 2; Price = 10m }
                  { Sku = "B"; Quantity = 1; Price = 5m } ]
    let total = Order.calculateTotal items
    test <@ total = 25m @>

[<Fact>]
let ``validated email rejects empty input`` () =
    let result = ValidatedEmail.create ""
    test <@ Result.isError result @>
```

### Async Tests

```fsharp
[<Fact>]
let ``PlaceOrder returns success when request is valid`` () = task {
    let deps = createTestDeps ()
    let request = { CustomerId = "cust-123"; Items = [ validItem ] }

    let! result = OrderService.placeOrder deps request

    test <@ Result.isOk result @>
}

[<Fact>]
let ``PlaceOrder returns error when items are empty`` () = task {
    let deps = createTestDeps ()
    let request = { CustomerId = "cust-123"; Items = [] }

    let! result = OrderService.placeOrder deps request

    test <@ Result.isError result @>
}
```

### Parameterized Tests with Theory

```fsharp
[<Theory>]
[<InlineData("")>]
[<InlineData("   ")>]
let ``PlaceOrder rejects empty customer ID`` (customerId: string) =
    let request = { CustomerId = customerId; Items = [ validItem ] }
    let result = OrderService.placeOrder request
    result |> should be (ofCase <@ Error @>)

[<Theory>]
[<InlineData("", false)>]
[<InlineData("a", false)>]
[<InlineData("user@example.com", true)>]
[<InlineData("user+tag@example.co.uk", true)>]
let ``IsValidEmail returns expected result`` (email: string, expected: bool) =
    test <@ EmailValidator.isValid email = expected @>
```

## Property-Based Testing with FsCheck

### Using FsCheck.xUnit

```fsharp
open FsCheck
open FsCheck.Xunit

[<Property>]
let ``order total is always non-negative`` (items: NonEmptyList<PositiveInt * decimal>) =
    let orderItems =
        items.Get
        |> List.map (fun (qty, price) ->
            { Sku = "SKU"; Quantity = qty.Get; Price = abs price })
    let total = Order.calculateTotal orderItems
    total >= 0m

[<Property>]
let ``serialization roundtrips`` (order: Order) =
    let json = JsonSerializer.Serialize order
    let deserialized = JsonSerializer.Deserialize<Order> json
    deserialized = order
```

### Custom Generators

```fsharp
type OrderGenerators =
    static member ValidEmail () =
        gen {
            let! user = Gen.elements [ "alice"; "bob"; "carol" ]
            let! domain = Gen.elements [ "example.com"; "test.org" ]
            return $"{user}@{domain}"
        }
        |> Arb.fromGen

[<Property(Arbitrary = [| typeof<OrderGenerators> |])>]
let ``valid emails pass validation`` (email: string) =
    EmailValidator.isValid email
```

## Mocking Dependencies

### Function Stubs (Preferred)

```fsharp
let createTestDeps () =
    let mutable savedOrders = []
    { FindOrder = fun id -> task { return Map.tryFind id testData }
      SaveOrder = fun order -> task { savedOrders <- order :: savedOrders }
      SendNotification = fun _ -> Task.CompletedTask }

[<Fact>]
let ``PlaceOrder saves the confirmed order`` () = task {
    let mutable saved = []
    let deps =
        { createTestDeps () with
            SaveOrder = fun order -> task { saved <- order :: saved } }

    let! _ = OrderService.placeOrder deps validRequest

    test <@ saved.Length = 1 @>
}
```

### NSubstitute for .NET Interfaces

```fsharp
open NSubstitute

[<Fact>]
let ``calls repository with correct ID`` () = task {
    let repo = Substitute.For<IOrderRepository>()
    repo.FindByIdAsync(Arg.Any<Guid>(), Arg.Any<CancellationToken>())
        .Returns(Task.FromResult(Some testOrder))

    let service = OrderService(repo)
    let! _ = service.GetOrder(testOrder.Id, CancellationToken.None)

    do! repo.Received(1).FindByIdAsync(testOrder.Id, Arg.Any<CancellationToken>())
}
```

## ASP.NET Core Integration Tests

```fsharp
type OrderApiTests (factory: WebApplicationFactory<Program>) =
    interface IClassFixture<WebApplicationFactory<Program>>

    let client =
        factory.WithWebHostBuilder(fun builder ->
            builder.ConfigureServices(fun services ->
                services.RemoveAll<DbContextOptions<AppDbContext>>() |> ignore
                services.AddDbContext<AppDbContext>(fun options ->
                    options.UseInMemoryDatabase("TestDb") |> ignore) |> ignore))
            .CreateClient()

    [<Fact>]
    member _.``GET order returns 404 when not found`` () = task {
        let! response = client.GetAsync($"/api/orders/{Guid.NewGuid()}")
        test <@ response.StatusCode = HttpStatusCode.NotFound @>
    }
```

## Test Organization

```
tests/
  MyApp.Tests/
    Unit/
      OrderServiceTests.fs
      PaymentServiceTests.fs
    Integration/
      OrderApiTests.fs
      OrderRepositoryTests.fs
    Properties/
      OrderPropertyTests.fs
    Helpers/
      TestData.fs
      TestDeps.fs
```

## Common Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| 測試實作細節 | 測行為和結果 |
| 共用可變的測試狀態 | 每個測試用全新的狀態 |
| 非同步測試裡用 `Thread.Sleep` | 用帶 timeout 的 `Task.Delay`，或 polling 輔助函式 |
| 對 `sprintf` 的輸出做斷言 | 對有型別的值和 pattern match 做斷言 |
| 忽略 `CancellationToken` | 一律傳入並驗證取消行為 |
| 跳過屬性測試 | 任何有明確不變量的函式都用 FsCheck |

## Related Skills

- `dotnet-patterns`：慣用的 .NET 模式、依賴注入與架構
- `csharp-testing`：C# 測試模式（WebApplicationFactory 和 Testcontainers 這類共用的基礎設施，也適用於 F#）

## Running Tests

```bash
# 跑所有測試
dotnet test

# 跑覆蓋率
dotnet test --collect:"XPlat Code Coverage"

# 跑特定專案
dotnet test tests/MyApp.Tests/

# 依測試名稱過濾
dotnet test --filter "FullyQualifiedName~OrderService"

# 開發時用 watch 模式
dotnet watch test --project tests/MyApp.Tests/
```
