---
name: java-coding-standards
description: "Spring Boot 與 Quarkus 服務的 Java 程式碼規範：命名、不可變性、Optional 的用法、stream、例外、泛型、CDI、reactive 模式，以及專案結構。會自動套用各框架專屬的慣例。在 Spring Boot 或 Quarkus 服務裡撰寫或審查 Java 時使用。"
metadata:
  origin: ECC
---

# Java Coding Standards

讓 Spring Boot 與 Quarkus 服務裡的 Java（17+）程式碼可讀、好維護的規範。

## When to Use

- 在 Spring Boot 或 Quarkus 專案裡撰寫或審查 Java 程式碼
- 落實命名、不可變性或例外處理的慣例
- 使用 record、sealed class 或 pattern matching（Java 17+）
- 檢查 Optional、stream 或泛型的使用
- 規劃 package 和專案結構
- **[QUARKUS]**：處理 CDI scope、Panache entity 或 reactive pipeline

## How It Works

### Framework Detection

套用規範之前，先從建置檔判斷框架：

- 建置檔包含 `quarkus` → 套用 **[QUARKUS]** 慣例
- 建置檔包含 `spring-boot` → 套用 **[SPRING]** 慣例
- 兩者都沒偵測到 → 只套用共通的慣例

## Core Principles

- 清楚優先於取巧
- 預設不可變；盡量減少共享的可變狀態
- 用有意義的例外儘早失敗（fail fast）
- 命名和 package 結構要一致
- **[QUARKUS]**：優先在建置期處理，而不是 runtime；盡量避免 runtime reflection

## Examples

下面各節展示具體的 Spring Boot、Quarkus 和共通的 Java 範例，
涵蓋命名、不可變性、依賴注入、reactive 程式碼、例外、
專案結構、logging、設定和測試。

## Naming

```java
// PASS: 類別/Record：PascalCase
public class MarketService {}
public record Money(BigDecimal amount, Currency currency) {}

// PASS: 方法/欄位：camelCase
private final MarketRepository marketRepository;
public Market findBySlug(String slug) {}

// PASS: 常數：UPPER_SNAKE_CASE
private static final int MAX_PAGE_SIZE = 100;

// PASS: [QUARKUS] JAX-RS resource 命名為 *Resource，不是 *Controller
public class MarketResource {}

// PASS: [SPRING] REST controller 命名為 *Controller
public class MarketController {}
```

## Immutability

```java
// PASS: 優先用 record 和 final 欄位
public record MarketDto(Long id, String name, MarketStatus status) {}

public class Market {
  private final Long id;
  private final String name;
  // 只有 getter，沒有 setter
}

// PASS: [QUARKUS] Panache active-record entity 使用 public 欄位（Quarkus 慣例）
@Entity
public class Market extends PanacheEntity {
  public String name;
  public MarketStatus status;
  // Panache 會在建置期產生 accessor；public 欄位在這裡是慣用寫法
}

// PASS: [QUARKUS] Panache MongoDB entity
@MongoEntity(collection = "markets")
public class Market extends PanacheMongoEntity {
  public String name;
  public MarketStatus status;
}
```

## Optional Usage

```java
// PASS: find* 方法回傳 Optional
// [SPRING]
Optional<Market> market = marketRepository.findBySlug(slug);

// [QUARKUS] Panache
Optional<Market> market = Market.find("slug", slug).firstResultOptional();

// PASS: 用 map/flatMap，不要用 get()
return market
    .map(MarketResponse::from)
    .orElseThrow(() -> new EntityNotFoundException("Market not found"));
```

## Streams Best Practices

```java
// PASS: 用 stream 做轉換，pipeline 保持簡短
List<String> names = markets.stream()
    .map(Market::name)
    .filter(Objects::nonNull)
    .toList();

// FAIL: 避免複雜的巢狀 stream；為了清楚，改用迴圈
```

## Dependency Injection

```java
// PASS: [SPRING] Constructor injection（優先於欄位上的 @Autowired）
@Service
public class MarketService {
  private final MarketRepository marketRepository;

  public MarketService(MarketRepository marketRepository) {
    this.marketRepository = marketRepository;
  }
}

// PASS: [QUARKUS] Constructor injection
@ApplicationScoped
public class MarketService {
  private final MarketRepository marketRepository;

  @Inject
  public MarketService(MarketRepository marketRepository) {
    this.marketRepository = marketRepository;
  }
}

// PASS: [QUARKUS] Package-private 欄位注入（在 Quarkus 可接受，能避開 proxy 問題）
@ApplicationScoped
public class MarketService {
  @Inject
  MarketRepository marketRepository;
}

// FAIL: [SPRING] 用 @Autowired 做欄位注入
@Autowired
private MarketRepository marketRepository; // 改用 constructor injection

// FAIL: [QUARKUS] 需要 interception 或 lazy init 時用 @Singleton
@Singleton // 無法 proxy，改用 @ApplicationScoped
public class MarketService {}
```

## Reactive Patterns [QUARKUS]

```java
// PASS: reactive endpoint 回傳 Uni/Multi
@GET
@Path("/{slug}")
public Uni<Market> findBySlug(@PathParam("slug") String slug) {
  return Market.find("slug", slug)
      .<Market>firstResult()
      .onItem().ifNull().failWith(() -> new MarketNotFoundException(slug));
}

// PASS: 非阻塞的 pipeline 組合
public Uni<OrderConfirmation> placeOrder(OrderRequest req) {
  return validateOrder(req)
      .chain(valid -> persistOrder(valid))
      .chain(order -> notifyFulfillment(order));
}

// FAIL: 在 Uni/Multi pipeline 裡做阻塞呼叫
public Uni<Market> find(String slug) {
  Market m = Market.find("slug", slug).firstResult(); // 阻塞，會卡住 event loop
  return Uni.createFrom().item(m);
}

// FAIL: 對共用的 Uni 訂閱超過一次
Uni<Market> shared = fetchMarket(slug);
shared.subscribe().with(m -> log(m));
shared.subscribe().with(m -> cache(m)); // 重複訂閱，改用 Uni.memoize()
```

## Exceptions

- 領域錯誤用 unchecked exception；技術性的例外要包上 context 再拋出
- 建立領域專屬的例外（例如 `MarketNotFoundException`）
- 避免寬泛的 `catch (Exception ex)`，除非是集中重新拋出或記錄

```java
throw new MarketNotFoundException(slug);
```

### Centralised Exception Handling

```java
// [SPRING]
@RestControllerAdvice
public class GlobalExceptionHandler {
  @ExceptionHandler(MarketNotFoundException.class)
  public ResponseEntity<ErrorResponse> handle(MarketNotFoundException ex) {
    return ResponseEntity.status(404).body(ErrorResponse.from(ex));
  }
}

// [QUARKUS] 選項 A：ExceptionMapper
@Provider
public class MarketNotFoundMapper implements ExceptionMapper<MarketNotFoundException> {
  @Override
  public Response toResponse(MarketNotFoundException ex) {
    return Response.status(404).entity(ErrorResponse.from(ex)).build();
  }
}

// [QUARKUS] 選項 B：@ServerExceptionMapper（RESTEasy Reactive）
@ServerExceptionMapper
public RestResponse<ErrorResponse> handle(MarketNotFoundException ex) {
  return RestResponse.status(Status.NOT_FOUND, ErrorResponse.from(ex));
}
```

## Generics and Type Safety

- 避免 raw type；要宣告泛型參數
- 可重用的工具優先用有界泛型

```java
public <T extends Identifiable> Map<Long, T> indexById(Collection<T> items) { ... }
```

## Project Structure

### [SPRING] Maven/Gradle

```
src/main/java/com/example/app/
  config/
  controller/
  service/
  repository/
  domain/
  dto/
  util/
src/main/resources/
  application.yml
src/test/java/... (mirrors main)
```

### [QUARKUS] Maven/Gradle

```
src/main/java/com/example/app/
  config/              # @ConfigMapping, @ConfigProperty beans, Producers
  resource/            # JAX-RS resources (not "controller")
  service/
  repository/          # PanacheRepository implementations (if not using active record)
  domain/              # JPA/Panache entities, MongoDB entities
  dto/
  util/
  mapper/              # MapStruct mappers (if used)
src/main/resources/
  application.properties   # Quarkus convention (YAML supported with quarkus-config-yaml)
  import.sql               # Hibernate auto-import for dev/test
src/test/java/... (mirrors main)
```

## Formatting and Style

- 一致地使用 2 或 4 個空格（依專案標準）
- 每個檔案只有一個 public 的頂層型別
- 方法保持簡短、專注；把輔助邏輯抽出去
- 成員順序：常數、欄位、constructor、public 方法、protected、private

## Code Smells to Avoid

- 參數列太長 → 用 DTO/builder
- 巢狀太深 → 用 early return
- Magic number → 用具名常數
- 靜態的可變狀態 → 優先用依賴注入
- 靜默的 catch 區塊 → 要記錄並處理，或重新拋出
- **[QUARKUS]**：本來該用 `@ApplicationScoped` 卻用了 `@Singleton`，會破壞 proxy 和 interception
- **[QUARKUS]**：混用 `quarkus-resteasy-reactive` 和 `quarkus-resteasy`（傳統版），要二選一
- **[QUARKUS]**：同一個 bounded context 裡同時用 Panache active-record 和 repository 模式，要二選一

## Logging

```java
// [SPRING] SLF4J
private static final Logger log = LoggerFactory.getLogger(MarketService.class);
log.info("fetch_market slug={}", slug);
log.error("failed_fetch_market slug={}", slug, ex);

// [QUARKUS] JBoss Logging（預設，建置期零成本）
private static final Logger log = Logger.getLogger(MarketService.class);
log.infof("fetch_market slug=%s", slug);
log.errorf(ex, "failed_fetch_market slug=%s", slug);

// [QUARKUS] 替代方案：用 @Inject 簡化 logging
@Inject
Logger log; // 由 CDI 注入，作用範圍是宣告它的類別
```

## Null Handling

- 只有在不可避免時才接受 `@Nullable`；否則用 `@NonNull`
- 對輸入使用 Bean Validation（`@NotNull`、`@NotBlank`）
- **[QUARKUS]**：在 `@BeanParam`、`@RestForm` 和 request body 參數上套用 `@Valid`

## Configuration

```java
// [SPRING] @ConfigurationProperties
@ConfigurationProperties(prefix = "market")
public record MarketProperties(int maxPageSize, Duration cacheTtl) {}

// [QUARKUS] @ConfigMapping（型別安全，建置期驗證）
@ConfigMapping(prefix = "market")
public interface MarketConfig {
  int maxPageSize();
  Duration cacheTtl();
}

// [QUARKUS] 簡單的值用 @ConfigProperty
@ConfigProperty(name = "market.max-page-size", defaultValue = "100")
int maxPageSize;
```

## Testing Expectations

### Shared
- 用 JUnit 5 + AssertJ 做流暢的斷言
- 用 Mockito 做 mock；盡量避免 partial mock
- 偏好確定性的測試；不要藏有 sleep

### [SPRING]
- controller 切片用 `@WebMvcTest`，repository 切片用 `@DataJpaTest`
- `@SpringBootTest` 保留給完整的整合測試
- 用 `@MockBean` 取代 Spring context 裡的 bean

### [QUARKUS]
- unit test 用單純的 JUnit 5 + Mockito（不用 `@QuarkusTest`）
- `@QuarkusTest` 保留給 CDI 整合測試
- 整合測試中用 `@InjectMock` 取代 CDI bean
- 資料庫/Kafka/Redis 用 Dev Services，Dev Services 夠用時就不要手動設定 Testcontainers
- 自訂外部服務的生命週期用 `@QuarkusTestResource`

```java
// [SPRING] Controller 測試
@WebMvcTest(MarketController.class)
class MarketControllerTest {
  @Autowired MockMvc mockMvc;
  @MockBean MarketService marketService;
}

// [QUARKUS] 整合測試
@QuarkusTest
class MarketResourceTest {
  @InjectMock
  MarketService marketService;

  @Test
  void should_return_404_when_market_not_found() {
    given().when().get("/markets/unknown").then().statusCode(404);
  }
}

// [QUARKUS] Unit test（沒有 CDI，也沒有 @QuarkusTest）
@ExtendWith(MockitoExtension.class)
class MarketServiceTest {
  @Mock MarketRepository marketRepository;
  @InjectMocks MarketService marketService;
}
```

**記住**：程式碼要有意圖、有型別、可觀察。除非證明有必要，否則維護性優先於微觀最佳化。
