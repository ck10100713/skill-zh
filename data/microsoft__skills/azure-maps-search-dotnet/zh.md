---
name: azure-maps-search-dotnet
description: |
  Azure Maps SDK for .NET。位置服務，包括地理編碼、路線規劃、地圖渲染、地理定位和天氣。用於地址搜尋、導航路線、地圖圖磚、IP 地理定位和天氣資料。Triggers: "Azure Maps", "MapsSearchClient", "MapsRoutingClient", "MapsRenderingClient", "geocoding .NET", "route directions", "map tiles", "geolocation".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.Maps.Search
---

# Azure Maps (.NET)

Azure Maps SDK for .NET，提供位置服務：地理編碼、路線規劃、地圖渲染、地理定位和天氣。

## 安裝

```bash
# Search（地理編碼、反向地理編碼）
dotnet add package Azure.Maps.Search --prerelease

# Routing（導航路線、路線矩陣）
dotnet add package Azure.Maps.Routing --prerelease

# Rendering（地圖圖磚、靜態圖片）
dotnet add package Azure.Maps.Rendering --prerelease

# Geolocation（IP 轉位置）
dotnet add package Azure.Maps.Geolocation --prerelease

# Weather
dotnet add package Azure.Maps.Weather --prerelease

# Resource Management（帳號管理、SAS token）
dotnet add package Azure.ResourceManager.Maps --prerelease

# 認證需要
dotnet add package Azure.Identity
```

**目前版本**：
- `Azure.Maps.Search`: v2.0.0-beta.5
- `Azure.Maps.Routing`: v1.0.0-beta.4
- `Azure.Maps.Rendering`: v2.0.0-beta.1
- `Azure.Maps.Geolocation`: v1.0.0-beta.3
- `Azure.ResourceManager.Maps`: v1.1.0-beta.2

## 環境變數

```bash
AZURE_MAPS_SUBSCRIPTION_KEY=<your-subscription-key>  # 只有用 AzureKeyCredential 認證時才需要
AZURE_MAPS_CLIENT_ID=<your-client-id>  # 必填：Azure Maps client ID
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

### Subscription Key（共用金鑰）

```csharp
using Azure;
using Azure.Maps.Search;

var subscriptionKey = Environment.GetEnvironmentVariable("AZURE_MAPS_SUBSCRIPTION_KEY");
var credential = new AzureKeyCredential(subscriptionKey);

var client = new MapsSearchClient(credential);
```

### Microsoft Entra Token Credential

```csharp
using Azure.Identity;
using Azure.Maps.Search;

// 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接用特定的 credential：
// 見 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
var clientId = Environment.GetEnvironmentVariable("AZURE_MAPS_CLIENT_ID");

var client = new MapsSearchClient(credential, clientId);
```

### Shared Access Signature (SAS)

```csharp
using Azure;
using Azure.Core;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.Maps;
using Azure.ResourceManager.Maps.Models;
using Azure.Maps.Search;

// 用 Azure Resource Manager 認證
ArmClient armClient = new ArmClient(new DefaultAzureCredential());

// 取得 Maps 帳號資源
ResourceIdentifier mapsAccountResourceId = MapsAccountResource.CreateResourceIdentifier(
    subscriptionId, resourceGroupName, accountName);
MapsAccountResource mapsAccount = armClient.GetMapsAccountResource(mapsAccountResourceId);

// 產生 SAS token
MapsAccountSasContent sasContent = new MapsAccountSasContent(
    MapsSigningKey.PrimaryKey, 
    principalId, 
    maxRatePerSecond: 500, 
    start: DateTime.UtcNow.ToString("O"), 
    expiry: DateTime.UtcNow.AddDays(1).ToString("O"));

Response<MapsAccountSasToken> sas = mapsAccount.GetSas(sasContent);

// 用 SAS token 建立 client
var sasCredential = new AzureSasCredential(sas.Value.AccountSasToken);
var client = new MapsSearchClient(sasCredential);
```

## Client 階層

```
Azure.Maps.Search
└── MapsSearchClient
    ├── GetGeocoding()                    → 地址轉座標
    ├── GetGeocodingBatch()               → 批次地理編碼
    ├── GetReverseGeocoding()             → 座標轉地址
    ├── GetReverseGeocodingBatch()        → 批次反向地理編碼
    └── GetPolygon()                      → 取得邊界多邊形

Azure.Maps.Routing
└── MapsRoutingClient
    ├── GetDirections()                   → 導航路線
    ├── GetImmediateRouteMatrix()         → 路線矩陣（同步，≤100）
    ├── GetRouteMatrix()                  → 路線矩陣（非同步，≤700）
    └── GetRouteRange()                   → 等時線/可達範圍

Azure.Maps.Rendering
└── MapsRenderingClient
    ├── GetMapTile()                      → 地圖圖磚
    ├── GetMapStaticImage()               → 靜態地圖圖片
    └── GetCopyrightCaption()             → 著作權資訊

Azure.Maps.Geolocation
└── MapsGeolocationClient
    └── GetCountryCode()                  → IP 轉國家/地區

Azure.Maps.Weather
└── MapsWeatherClient
    ├── GetCurrentWeatherConditions()     → 目前天氣
    ├── GetDailyForecast()                → 每日預報
    ├── GetHourlyForecast()               → 每小時預報
    └── GetSevereWeatherAlerts()          → 天氣警報
```

## 核心工作流程

### 1. 地理編碼（地址轉座標）

```csharp
using Azure;
using Azure.Maps.Search;

var credential = new AzureKeyCredential(subscriptionKey);
var client = new MapsSearchClient(credential);

Response<GeocodingResponse> result = client.GetGeocoding("1 Microsoft Way, Redmond, WA 98052");

foreach (var feature in result.Value.Features)
{
    Console.WriteLine($"Coordinates: {string.Join(",", feature.Geometry.Coordinates)}");
    Console.WriteLine($"Address: {feature.Properties.Address.FormattedAddress}");
    Console.WriteLine($"Confidence: {feature.Properties.Confidence}");
}
```

### 2. 批次地理編碼

```csharp
using Azure.Maps.Search.Models.Queries;

List<GeocodingQuery> queries = new List<GeocodingQuery>
{
    new GeocodingQuery() { Query = "400 Broad St, Seattle, WA" },
    new GeocodingQuery() { Query = "1 Microsoft Way, Redmond, WA" },
    new GeocodingQuery() { AddressLine = "Space Needle", Top = 1 },
};

Response<GeocodingBatchResponse> results = client.GetGeocodingBatch(queries);

foreach (var batchItem in results.Value.BatchItems)
{
    foreach (var feature in batchItem.Features)
    {
        Console.WriteLine($"Coordinates: {string.Join(",", feature.Geometry.Coordinates)}");
    }
}
```

### 3. 反向地理編碼（座標轉地址）

```csharp
using Azure.Core.GeoJson;

GeoPosition coordinates = new GeoPosition(-122.138685, 47.6305637);
Response<GeocodingResponse> result = client.GetReverseGeocoding(coordinates);

foreach (var feature in result.Value.Features)
{
    Console.WriteLine($"Address: {feature.Properties.Address.FormattedAddress}");
    Console.WriteLine($"Locality: {feature.Properties.Address.Locality}");
}
```

### 4. 取得邊界多邊形

```csharp
using Azure.Maps.Search.Models;

GetPolygonOptions options = new GetPolygonOptions()
{
    Coordinates = new GeoPosition(-122.204141, 47.61256),
    ResultType = BoundaryResultTypeEnum.Locality,
    Resolution = ResolutionEnum.Small,
};

Response<Boundary> result = client.GetPolygon(options);

Console.WriteLine($"Boundary copyright: {result.Value.Properties?.Copyright}");
Console.WriteLine($"Polygon count: {result.Value.Geometry.Count}");
```

### 5. 導航路線

```csharp
using Azure;
using Azure.Core.GeoJson;
using Azure.Maps.Routing;
using Azure.Maps.Routing.Models;

var client = new MapsRoutingClient(new AzureKeyCredential(subscriptionKey));

List<GeoPosition> routePoints = new List<GeoPosition>()
{
    new GeoPosition(-122.34, 47.61),  // 西雅圖
    new GeoPosition(-122.13, 47.64)   // 雷德蒙
};

RouteDirectionQuery query = new RouteDirectionQuery(routePoints);
Response<RouteDirections> result = client.GetDirections(query);

foreach (var route in result.Value.Routes)
{
    Console.WriteLine($"Distance: {route.Summary.LengthInMeters} meters");
    Console.WriteLine($"Duration: {route.Summary.TravelTimeDuration}");
    
    foreach (RouteLeg leg in route.Legs)
    {
        Console.WriteLine($"Leg points: {leg.Points.Count}");
    }
}
```

### 6. 帶選項的導航路線

```csharp
RouteDirectionOptions options = new RouteDirectionOptions()
{
    RouteType = RouteType.Fastest,
    UseTrafficData = true,
    TravelMode = TravelMode.Bicycle,
    Language = RoutingLanguage.EnglishUsa,
    InstructionsType = RouteInstructionsType.Text,
};

RouteDirectionQuery query = new RouteDirectionQuery(routePoints)
{
    RouteDirectionOptions = options
};

Response<RouteDirections> result = client.GetDirections(query);
```

### 7. 路線矩陣

```csharp
RouteMatrixQuery routeMatrixQuery = new RouteMatrixQuery
{
    Origins = new List<GeoPosition>()
    {
        new GeoPosition(-122.34, 47.61),
        new GeoPosition(-122.13, 47.64)
    },
    Destinations = new List<GeoPosition>() 
    { 
        new GeoPosition(-122.20, 47.62),
        new GeoPosition(-122.40, 47.65)
    },
};

// 同步（最多 100 種路線組合）
Response<RouteMatrixResult> result = client.GetImmediateRouteMatrix(routeMatrixQuery);

foreach (var cell in result.Value.Matrix.SelectMany(row => row))
{
    Console.WriteLine($"Distance: {cell.Response?.RouteSummary?.LengthInMeters}");
    Console.WriteLine($"Duration: {cell.Response?.RouteSummary?.TravelTimeDuration}");
}

// 非同步（最多 700 種路線組合）
RouteMatrixOptions routeMatrixOptions = new RouteMatrixOptions(routeMatrixQuery)
{
    TravelTimeType = TravelTimeType.All,
};
GetRouteMatrixOperation asyncResult = client.GetRouteMatrix(WaitUntil.Completed, routeMatrixOptions);
```

### 8. 路線範圍（等時線）

```csharp
RouteRangeOptions options = new RouteRangeOptions(-122.34, 47.61)
{
    TimeBudget = new TimeSpan(0, 20, 0)  // 20 分鐘
};

Response<RouteRangeResult> result = client.GetRouteRange(options);

// result.Value.ReachableRange 裡有多邊形
Console.WriteLine($"Boundary points: {result.Value.ReachableRange.Boundary.Count}");
```

### 9. 取得地圖圖磚

```csharp
using Azure;
using Azure.Maps.Rendering;

var client = new MapsRenderingClient(new AzureKeyCredential(subscriptionKey));

int zoom = 10;
int tileSize = 256;

// 把座標轉成圖磚索引
MapTileIndex tileIndex = MapsRenderingClient.PositionToTileXY(
    new GeoPosition(13.3854, 52.517), zoom, tileSize);

// 抓取地圖圖磚
GetMapTileOptions options = new GetMapTileOptions(
    MapTileSetId.MicrosoftImagery,
    new MapTileIndex(tileIndex.X, tileIndex.Y, zoom)
);

Response<Stream> mapTile = client.GetMapTile(options);

// 存成檔案
using (FileStream fileStream = File.Create("./MapTile.png"))
{
    mapTile.Value.CopyTo(fileStream);
}
```

### 10. IP 地理定位

```csharp
using System.Net;
using Azure;
using Azure.Maps.Geolocation;

var client = new MapsGeolocationClient(new AzureKeyCredential(subscriptionKey));

IPAddress ipAddress = IPAddress.Parse("2001:4898:80e8:b::189");
Response<CountryRegionResult> result = client.GetCountryCode(ipAddress);

Console.WriteLine($"Country ISO Code: {result.Value.IsoCode}");
```

### 11. 目前天氣

```csharp
using Azure;
using Azure.Core.GeoJson;
using Azure.Maps.Weather;

var client = new MapsWeatherClient(new AzureKeyCredential(subscriptionKey));

var position = new GeoPosition(-122.13071, 47.64011);
var options = new GetCurrentWeatherConditionsOptions(position);

Response<CurrentConditionsResult> result = client.GetCurrentWeatherConditions(options);

foreach (var condition in result.Value.Results)
{
    Console.WriteLine($"Temperature: {condition.Temperature.Value} {condition.Temperature.Unit}");
    Console.WriteLine($"Weather: {condition.Phrase}");
    Console.WriteLine($"Humidity: {condition.RelativeHumidity}%");
}
```

## 主要型別參考

### Search 套件

| 型別 | 用途 |
|------|---------|
| `MapsSearchClient` | 搜尋操作的主要 client |
| `GeocodingResponse` | 地理編碼結果 |
| `GeocodingBatchResponse` | 批次地理編碼結果 |
| `GeocodingQuery` | 批次地理編碼的查詢 |
| `ReverseGeocodingQuery` | 批次反向地理編碼的查詢 |
| `GetPolygonOptions` | 取得多邊形的選項 |
| `Boundary` | 邊界多邊形結果 |
| `BoundaryResultTypeEnum` | 邊界類型（Locality、AdminDistrict 等） |
| `ResolutionEnum` | 多邊形解析度（Small、Medium、Large） |

### Routing 套件

| 型別 | 用途 |
|------|---------|
| `MapsRoutingClient` | 路線操作的主要 client |
| `RouteDirectionQuery` | 導航路線的查詢 |
| `RouteDirectionOptions` | 路線計算選項 |
| `RouteDirections` | 導航路線結果 |
| `RouteLeg` | 路線的一個路段 |
| `RouteMatrixQuery` | 路線矩陣的查詢 |
| `RouteMatrixResult` | 路線矩陣結果 |
| `RouteRangeOptions` | 等時線的選項 |
| `RouteRangeResult` | 等時線結果 |
| `RouteType` | 路線類型（Fastest、Shortest、Eco、Thrilling） |
| `TravelMode` | 交通方式（Car、Truck、Bicycle、Pedestrian） |

### Rendering 套件

| 型別 | 用途 |
|------|---------|
| `MapsRenderingClient` | 渲染的主要 client |
| `GetMapTileOptions` | 地圖圖磚選項 |
| `MapTileIndex` | 圖磚座標（X、Y、Zoom） |
| `MapTileSetId` | 圖磚集識別碼 |

### 通用型別

| 型別 | 用途 |
|------|---------|
| `GeoPosition` | 地理位置（經度、緯度） |
| `GeoBoundingBox` | 地理區域的邊界框 |

## 最佳實務

1. **正式環境用 Entra ID**：比 subscription key 更好
2. **批次操作**：多個地址就用批次地理編碼
3. **快取結果**：地理編碼結果不常變
4. **選合適的圖磚大小**：依顯示需求用 256 或 512 像素
5. **處理速率限制**：實作 exponential backoff
6. **用非同步路線矩陣**：計算大型矩陣（>100）時
7. **考慮交通資料**：設 `UseTrafficData = true` 才能得到準確的預估抵達時間

## 錯誤處理

```csharp
try
{
    Response<GeocodingResponse> result = client.GetGeocoding(address);
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Status: {ex.Status}");
    Console.WriteLine($"Error: {ex.Message}");
    
    switch (ex.Status)
    {
        case 400:
            // 請求參數無效
            break;
        case 401:
            // 認證失敗
            break;
        case 429:
            // 被限流，要實作 backoff
            break;
    }
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.Maps.Search` | 地理編碼、搜尋 | `dotnet add package Azure.Maps.Search --prerelease` |
| `Azure.Maps.Routing` | 導航路線、矩陣 | `dotnet add package Azure.Maps.Routing --prerelease` |
| `Azure.Maps.Rendering` | 地圖圖磚、圖片 | `dotnet add package Azure.Maps.Rendering --prerelease` |
| `Azure.Maps.Geolocation` | IP 地理定位 | `dotnet add package Azure.Maps.Geolocation --prerelease` |
| `Azure.Maps.Weather` | 天氣資料 | `dotnet add package Azure.Maps.Weather --prerelease` |
| `Azure.ResourceManager.Maps` | 帳號管理 | `dotnet add package Azure.ResourceManager.Maps --prerelease` |

## 參考連結

| 資源 | URL |
|----------|-----|
| Azure Maps 文件 | https://learn.microsoft.com/azure/azure-maps/ |
| Search API 參考 | https://learn.microsoft.com/dotnet/api/azure.maps.search |
| Routing API 參考 | https://learn.microsoft.com/dotnet/api/azure.maps.routing |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/maps |
| 定價 | https://azure.microsoft.com/pricing/details/azure-maps/ |
