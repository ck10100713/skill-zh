---
name: springboot-patterns
description: Spring Boot 架構模式、REST API 設計、分層 service、資料存取、快取、非同步處理和日誌。用於 Java Spring Boot 後端工作。打造或 review Spring Boot 後端（REST 層、service、資料存取、快取或非同步工作）時使用。
metadata:
  origin: ECC
---

# Spring Boot 開發模式

用於可擴展、正式環境等級服務的 Spring Boot 架構與 API 模式。

## 何時啟用

- 用 Spring MVC 或 WebFlux 建構 REST API
- 規劃 controller → service → repository 的分層
- 設定 Spring Data JPA、快取或非同步處理
- 加入驗證、例外處理或分頁
- 為 dev/staging/production 環境設定 profile
- 用 Spring Events 或 Kafka 實作事件驅動模式

## REST API 結構

```java
@RestController
@RequestMapping("/api/markets")
@Validated
class MarketController {
  private final MarketService marketService;

  MarketController(MarketService marketService) {
    this.marketService = marketService;
  }

  @GetMapping
  ResponseEntity<Page<MarketResponse>> list(
      @RequestParam(defaultValue = "0") int page,
      @RequestParam(defaultValue = "20") int size) {
    Page<Market> markets = marketService.list(PageRequest.of(page, size));
    return ResponseEntity.ok(markets.map(MarketResponse::from));
  }

  @PostMapping
  ResponseEntity<MarketResponse> create(@Valid @RequestBody CreateMarketRequest request) {
    Market market = marketService.create(request);
    return ResponseEntity.status(HttpStatus.CREATED).body(MarketResponse.from(market));
  }
}
```

## Repository 模式（Spring Data JPA）

```java
public interface MarketRepository extends JpaRepository<MarketEntity, Long> {
  @Query("select m from MarketEntity m where m.status = :status order by m.volume desc")
  List<MarketEntity> findActive(@Param("status") MarketStatus status, Pageable pageable);
}
```

## 帶交易的 Service 層

```java
@Service
public class MarketService {
  private final MarketRepository repo;

  public MarketService(MarketRepository repo) {
    this.repo = repo;
  }

  @Transactional
  public Market create(CreateMarketRequest request) {
    MarketEntity entity = MarketEntity.from(request);
    MarketEntity saved = repo.save(entity);
    return Market.from(saved);
  }
}
```

## DTO 與驗證

```java
public record CreateMarketRequest(
    @NotBlank @Size(max = 200) String name,
    @NotBlank @Size(max = 2000) String description,
    @NotNull @FutureOrPresent Instant endDate,
    @NotEmpty List<@NotBlank String> categories) {}

public record MarketResponse(Long id, String name, MarketStatus status) {
  static MarketResponse from(Market market) {
    return new MarketResponse(market.id(), market.name(), market.status());
  }
}
```

## 例外處理

```java
@ControllerAdvice
class GlobalExceptionHandler {
  @ExceptionHandler(MethodArgumentNotValidException.class)
  ResponseEntity<ApiError> handleValidation(MethodArgumentNotValidException ex) {
    String message = ex.getBindingResult().getFieldErrors().stream()
        .map(e -> e.getField() + ": " + e.getDefaultMessage())
        .collect(Collectors.joining(", "));
    return ResponseEntity.badRequest().body(ApiError.validation(message));
  }

  @ExceptionHandler(AccessDeniedException.class)
  ResponseEntity<ApiError> handleAccessDenied() {
    return ResponseEntity.status(HttpStatus.FORBIDDEN).body(ApiError.of("Forbidden"));
  }

  @ExceptionHandler(Exception.class)
  ResponseEntity<ApiError> handleGeneric(Exception ex) {
    // Log unexpected errors with stack traces
    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
        .body(ApiError.of("Internal server error"));
  }
}
```

## 快取

需要在設定類別上加 `@EnableCaching`。

```java
@Service
public class MarketCacheService {
  private final MarketRepository repo;

  public MarketCacheService(MarketRepository repo) {
    this.repo = repo;
  }

  @Cacheable(value = "market", key = "#id")
  public Market getById(Long id) {
    return repo.findById(id)
        .map(Market::from)
        .orElseThrow(() -> new EntityNotFoundException("Market not found"));
  }

  @CacheEvict(value = "market", key = "#id")
  public void evict(Long id) {}
}
```

## 非同步處理

需要在設定類別上加 `@EnableAsync`。

```java
@Service
public class NotificationService {
  @Async
  public CompletableFuture<Void> sendAsync(Notification notification) {
    // send email/SMS
    return CompletableFuture.completedFuture(null);
  }
}
```

## 日誌（SLF4J）

```java
@Service
public class ReportService {
  private static final Logger log = LoggerFactory.getLogger(ReportService.class);

  public Report generate(Long marketId) {
    log.info("generate_report marketId={}", marketId);
    try {
      // logic
    } catch (Exception ex) {
      log.error("generate_report_failed marketId={}", marketId, ex);
      throw ex;
    }
    return new Report();
  }
}
```

## Middleware / Filter

```java
@Component
public class RequestLoggingFilter extends OncePerRequestFilter {
  private static final Logger log = LoggerFactory.getLogger(RequestLoggingFilter.class);

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain filterChain) throws ServletException, IOException {
    long start = System.currentTimeMillis();
    try {
      filterChain.doFilter(request, response);
    } finally {
      long duration = System.currentTimeMillis() - start;
      log.info("req method={} uri={} status={} durationMs={}",
          request.getMethod(), request.getRequestURI(), response.getStatus(), duration);
    }
  }
}
```

## 分頁與排序

```java
PageRequest page = PageRequest.of(pageNumber, pageSize, Sort.by("createdAt").descending());
Page<Market> results = marketService.list(page);
```

## 容錯的外部呼叫

```java
public <T> T withRetry(Supplier<T> supplier, int maxRetries) {
  int attempts = 0;
  while (true) {
    try {
      return supplier.get();
    } catch (Exception ex) {
      attempts++;
      if (attempts >= maxRetries) {
        throw ex;
      }
      try {
        Thread.sleep((long) Math.pow(2, attempts) * 100L);
      } catch (InterruptedException ie) {
        Thread.currentThread().interrupt();
        throw ex;
      }
    }
  }
}
```

## Rate Limiting（Filter + Bucket4j）

**安全注意事項**：`X-Forwarded-For` header 預設是不可信的，因為客戶端可以偽造。
只有在符合下面這些條件時，才使用 forwarded header：
1. 你的應用程式位在可信任的反向代理後面（nginx、AWS ALB 等）
2. 你已經把 `ForwardedHeaderFilter` 註冊成 bean
3. 你已在 application properties 中設定 `server.forward-headers-strategy=NATIVE` 或 `FRAMEWORK`
4. 你的代理已設定成覆寫（而不是附加）`X-Forwarded-For` header

`ForwardedHeaderFilter` 設定正確時，`request.getRemoteAddr()` 會自動從 forwarded header 回傳正確的客戶端 IP。沒有這個設定的話，直接用 `request.getRemoteAddr()`，它回傳的是直接連線的 IP，這是唯一可信的值。

```java
@Component
public class RateLimitFilter extends OncePerRequestFilter {
  private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

  /*
   * SECURITY: This filter uses request.getRemoteAddr() to identify clients for rate limiting.
   *
   * If your application is behind a reverse proxy (nginx, AWS ALB, etc.), you MUST configure
   * Spring to handle forwarded headers properly for accurate client IP detection:
   *
   * 1. Set server.forward-headers-strategy=NATIVE (for cloud platforms) or FRAMEWORK in
   *    application.properties/yaml
   * 2. If using FRAMEWORK strategy, register ForwardedHeaderFilter:
   *
   *    @Bean
   *    ForwardedHeaderFilter forwardedHeaderFilter() {
   *        return new ForwardedHeaderFilter();
   *    }
   *
   * 3. Ensure your proxy overwrites (not appends) the X-Forwarded-For header to prevent spoofing
   * 4. Configure server.tomcat.remoteip.trusted-proxies or equivalent for your container
   *
   * Without this configuration, request.getRemoteAddr() returns the proxy IP, not the client IP.
   * Do NOT read X-Forwarded-For directly—it is trivially spoofable without trusted proxy handling.
   */
  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain filterChain) throws ServletException, IOException {
    // Use getRemoteAddr() which returns the correct client IP when ForwardedHeaderFilter
    // is configured, or the direct connection IP otherwise. Never trust X-Forwarded-For
    // headers directly without proper proxy configuration.
    String clientIp = request.getRemoteAddr();

    Bucket bucket = buckets.computeIfAbsent(clientIp,
        k -> Bucket.builder()
            .addLimit(Bandwidth.classic(100, Refill.greedy(100, Duration.ofMinutes(1))))
            .build());

    if (bucket.tryConsume(1)) {
      filterChain.doFilter(request, response);
    } else {
      response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
    }
  }
}
```

## 背景工作

使用 Spring 的 `@Scheduled`，或整合佇列（例如 Kafka、SQS、RabbitMQ）。讓 handler 保持冪等而且可觀測。

## 可觀測性

- 透過 Logback encoder 輸出結構化日誌（JSON）
- Metrics：Micrometer + Prometheus/OTel
- Tracing：Micrometer Tracing 搭配 OpenTelemetry 或 Brave 後端

## 正式環境預設值

- 優先用建構子注入，避免欄位注入
- 啟用 `spring.mvc.problemdetails.enabled=true`，輸出符合 RFC 7807 的錯誤（Spring Boot 3+）
- 依工作負載設定 HikariCP 連線池大小，並設定 timeout
- 查詢用 `@Transactional(readOnly = true)`
- 適當的地方用 `@NonNull` 和 `Optional` 強化 null 安全

**記住**：controller 要薄、service 要專注、repository 要簡單、錯誤要集中處理。以好維護和好測試為最佳化目標。
