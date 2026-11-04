---
name: springboot-security
description: Java Spring Boot 服務中，Spring Security 在驗證/授權、輸入驗證、CSRF、secret、header、rate limiting 和相依套件安全上的最佳實務。Review Spring Security 的驗證/授權、輸入驗證、CSRF、secret、header 或 rate limiting 時使用。
metadata:
  origin: ECC
---

# Spring Boot 安全 Review

新增驗證、處理輸入、建立 endpoint 或處理 secret 時使用。

## 何時啟用

- 新增驗證（JWT、OAuth2、以 session 為基礎）
- 實作授權（@PreAuthorize、角色型存取）
- 驗證使用者輸入（Bean Validation、自訂 validator）
- 設定 CORS、CSRF 或安全 header
- 管理 secret（Vault、環境變數）
- 新增 rate limiting 或暴力破解防護
- 掃描相依套件的 CVE

## 驗證

- 優先用無狀態的 JWT，或帶撤銷清單的 opaque token
- session 用 `httpOnly`、`Secure`、`SameSite=Strict` 的 cookie
- 用 `OncePerRequestFilter` 或 resource server 驗證 token

```java
@Component
public class JwtAuthFilter extends OncePerRequestFilter {
  private final JwtService jwtService;

  public JwtAuthFilter(JwtService jwtService) {
    this.jwtService = jwtService;
  }

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain chain) throws ServletException, IOException {
    String header = request.getHeader(HttpHeaders.AUTHORIZATION);
    if (header != null && header.startsWith("Bearer ")) {
      String token = header.substring(7);
      Authentication auth = jwtService.authenticate(token);
      SecurityContextHolder.getContext().setAuthentication(auth);
    }
    chain.doFilter(request, response);
  }
}
```

## 授權

- 啟用方法層級的安全：`@EnableMethodSecurity`
- 用 `@PreAuthorize("hasRole('ADMIN')")` 或 `@PreAuthorize("@authz.canEdit(#id)")`
- 預設拒絕；只開放必要的 scope

```java
@RestController
@RequestMapping("/api/admin")
public class AdminController {

  @PreAuthorize("hasRole('ADMIN')")
  @GetMapping("/users")
  public List<UserDto> listUsers() {
    return userService.findAll();
  }

  @PreAuthorize("@authz.isOwner(#id, authentication)")
  @DeleteMapping("/users/{id}")
  public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
    userService.delete(id);
    return ResponseEntity.noContent().build();
  }
}
```

## 輸入驗證

- 在 controller 上用 Bean Validation 搭配 `@Valid`
- 在 DTO 上加約束：`@NotBlank`、`@Email`、`@Size`、自訂 validator
- 渲染之前，用白名單清理任何 HTML

```java
// BAD: No validation
@PostMapping("/users")
public User createUser(@RequestBody UserDto dto) {
  return userService.create(dto);
}

// GOOD: Validated DTO
public record CreateUserDto(
    @NotBlank @Size(max = 100) String name,
    @NotBlank @Email String email,
    @NotNull @Min(0) @Max(150) Integer age
) {}

@PostMapping("/users")
public ResponseEntity<UserDto> createUser(@Valid @RequestBody CreateUserDto dto) {
  return ResponseEntity.status(HttpStatus.CREATED)
      .body(userService.create(dto));
}
```

## 防止 SQL Injection

- 用 Spring Data repository 或參數化查詢
- 原生查詢用 `:param` 綁定；絕對不要串接字串

```java
// BAD: String concatenation in native query
@Query(value = "SELECT * FROM users WHERE name = '" + name + "'", nativeQuery = true)

// GOOD: Parameterized native query
@Query(value = "SELECT * FROM users WHERE name = :name", nativeQuery = true)
List<User> findByName(@Param("name") String name);

// GOOD: Spring Data derived query (auto-parameterized)
List<User> findByEmailAndActiveTrue(String email);
```

## 密碼編碼

- 密碼一律用 BCrypt 或 Argon2 做雜湊，絕對不要存明文
- 用 `PasswordEncoder` bean，不要手動做雜湊

```java
@Bean
public PasswordEncoder passwordEncoder() {
  return new BCryptPasswordEncoder(12); // cost factor 12
}

// In service
public User register(CreateUserDto dto) {
  String hashedPassword = passwordEncoder.encode(dto.password());
  return userRepository.save(new User(dto.email(), hashedPassword));
}
```

## CSRF 防護

- 瀏覽器 session 的應用程式要保持 CSRF 啟用；在表單/header 裡帶 token
- 純 API 搭配 Bearer token 時，停用 CSRF，改靠無狀態驗證

```java
http
  .csrf(csrf -> csrf.disable())
  .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
```

## Secret 管理

- 原始碼裡不放 secret；從環境變數或 vault 載入
- 讓 `application.yml` 不含憑證；用 placeholder
- 定期輪替 token 和資料庫憑證

```yaml
# BAD: Hardcoded in application.yml
spring:
  datasource:
    password: mySecretPassword123

# GOOD: Environment variable placeholder
spring:
  datasource:
    password: ${DB_PASSWORD}

# GOOD: Spring Cloud Vault integration
spring:
  cloud:
    vault:
      uri: https://vault.example.com
      token: ${VAULT_TOKEN}
```

## 安全 Header

```java
http
  .headers(headers -> headers
    .contentSecurityPolicy(csp -> csp
      .policyDirectives("default-src 'self'"))
    .frameOptions(HeadersConfigurer.FrameOptionsConfig::sameOrigin)
    .xssProtection(Customizer.withDefaults())
    .referrerPolicy(rp -> rp.policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.NO_REFERRER)));
```

## CORS 設定

- 在 security filter 層級設定 CORS，不要每個 controller 各設一次
- 限制允許的 origin，正式環境絕對不要用 `*`

```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
  CorsConfiguration config = new CorsConfiguration();
  config.setAllowedOrigins(List.of("https://app.example.com"));
  config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
  config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
  config.setAllowCredentials(true);
  config.setMaxAge(3600L);

  UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
  source.registerCorsConfiguration("/api/**", config);
  return source;
}

// In SecurityFilterChain:
http.cors(cors -> cors.configurationSource(corsConfigurationSource()));
```

## Rate Limiting

- 在昂貴的 endpoint 上套用 Bucket4j 或閘道層級的限制
- 對突發流量記錄並告警；回傳 429 並附上重試提示

```java
// Using Bucket4j for per-endpoint rate limiting
@Component
public class RateLimitFilter extends OncePerRequestFilter {
  private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

  private Bucket createBucket() {
    return Bucket.builder()
        .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
        .build();
  }

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain chain) throws ServletException, IOException {
    String clientIp = request.getRemoteAddr();
    Bucket bucket = buckets.computeIfAbsent(clientIp, k -> createBucket());

    if (bucket.tryConsume(1)) {
      chain.doFilter(request, response);
    } else {
      response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
      response.getWriter().write("{\"error\": \"Rate limit exceeded\"}");
    }
  }
}
```

## 相依套件安全

- 在 CI 裡執行 OWASP Dependency Check / Snyk
- 讓 Spring Boot 和 Spring Security 維持在受支援的版本
- 遇到已知 CVE 就讓 build 失敗

## 日誌與個資

- 絕對不要記錄 secret、token、密碼或完整的卡號（PAN）資料
- 遮蔽敏感欄位；使用結構化的 JSON 日誌

## 檔案上傳

- 驗證大小、content type 和副檔名
- 存放在 web root 之外；需要的話要掃描

## 發布前檢查清單

- [ ] 驗證 token 有被驗證，也正確過期
- [ ] 每個敏感路徑都有授權防護
- [ ] 所有輸入都經過驗證和清理
- [ ] 沒有字串串接的 SQL
- [ ] CSRF 的做法符合應用程式類型
- [ ] Secret 都外部化；沒有任何被 commit
- [ ] 已設定安全 header
- [ ] API 有 rate limiting
- [ ] 相依套件已掃描，而且是最新的
- [ ] 日誌裡沒有敏感資料

**記住**：預設拒絕、驗證輸入、最小權限，並且先以安全的設定為優先。
