---
name: quarkus-security
description: "Quarkus 安全實作模式：JWT 與 OIDC 驗證、@RolesAllowed RBAC 與 SecurityIdentity 檢查、Bean Validation 與自訂 validator、參數化 Panache 查詢、BCrypt 密碼雜湊、CORS 與安全標頭、rate limiting、稽核 logging、Vault 或環境變數管理 secret，以及依賴套件 CVE 掃描。新增驗證或授權、驗證輸入、管理 secret 或加固 Quarkus 應用程式時使用。"
metadata:
  origin: ECC
---

# Quarkus 安全審查

用驗證、授權和輸入驗證來保護 Quarkus 應用程式的最佳實踐。

## 何時啟用

- 新增驗證（JWT、OIDC、Basic Auth）
- 用 @RolesAllowed 或 SecurityIdentity 實作授權
- 驗證使用者輸入（Bean Validation、自訂 validator）
- 設定 CORS 或安全標頭
- 管理 secret（Vault、環境變數、config source）
- 新增 rate limiting 或暴力破解防護
- 掃描依賴套件的 CVE
- 處理 MicroProfile JWT 或 SmallRye JWT

## 驗證

### JWT 驗證

```java
// 用 JWT 保護的 resource
@Path("/api/protected")
@Authenticated
public class ProtectedResource {

  @Inject
  JsonWebToken jwt;

  @Inject
  SecurityIdentity securityIdentity;

  @GET
  public Response getData() {
    String username = jwt.getName();
    Set<String> roles = jwt.getGroups();
    return Response.ok(Map.of(
        "username", username,
        "roles", roles,
        "principal", securityIdentity.getPrincipal().getName()
    )).build();
  }
}
```

設定（application.properties）：
```properties
mp.jwt.verify.publickey.location=publicKey.pem
mp.jwt.verify.issuer=https://auth.example.com

# OIDC
quarkus.oidc.auth-server-url=https://auth.example.com/realms/myrealm
quarkus.oidc.client-id=backend-service
quarkus.oidc.credentials.secret=${OIDC_SECRET}
```

### 自訂驗證 Filter

```java
@Provider
@Priority(Priorities.AUTHENTICATION)
public class CustomAuthFilter implements ContainerRequestFilter {

  @Inject
  SecurityIdentity identity;

  @Override
  public void filter(ContainerRequestContext requestContext) {
    String authHeader = requestContext.getHeaderString(HttpHeaders.AUTHORIZATION);

    // header 不存在或格式錯誤就立刻拒絕
    if (authHeader == null || !authHeader.startsWith("Bearer ")) {
      requestContext.abortWith(Response.status(Response.Status.UNAUTHORIZED).build());
      return;
    }

    String token = authHeader.substring(7);
    if (!validateToken(token)) {
      requestContext.abortWith(Response.status(Response.Status.UNAUTHORIZED).build());
    }
  }

  private boolean validateToken(String token) {
    // Token 驗證邏輯
    return true;
  }
}
```

## 授權

### 角色式存取控制

```java
@Path("/api/admin")
@RolesAllowed("ADMIN")
public class AdminResource {

  @GET
  @Path("/users")
  public List<UserDto> listUsers() {
    return userService.findAll();
  }

  @DELETE
  @Path("/users/{id}")
  @RolesAllowed({"ADMIN", "SUPER_ADMIN"})
  public Response deleteUser(@PathParam("id") Long id) {
    userService.delete(id);
    return Response.noContent().build();
  }
}

@Path("/api/users")
public class UserResource {

  @Inject
  SecurityIdentity securityIdentity;

  @GET
  @Path("/{id}")
  @RolesAllowed("USER")
  public Response getUser(@PathParam("id") Long id) {
    // 檢查擁有者
    if (!securityIdentity.hasRole("ADMIN") &&
        !isOwner(id, securityIdentity.getPrincipal().getName())) {
      return Response.status(Response.Status.FORBIDDEN).build();
    }
    return Response.ok(userService.findById(id)).build();
  }

  private boolean isOwner(Long userId, String username) {
    return userService.isOwner(userId, username);
  }
}
```

### 程式化安全

```java
@ApplicationScoped
public class SecurityService {

  @Inject
  SecurityIdentity securityIdentity;

  public boolean canAccessResource(Long resourceId) {
    if (securityIdentity.isAnonymous()) {
      return false;
    }

    if (securityIdentity.hasRole("ADMIN")) {
      return true;
    }

    String userId = securityIdentity.getPrincipal().getName();
    return resourceRepository.isOwner(resourceId, userId);
  }
}
```

## 輸入驗證

### Bean Validation

```java
// BAD: 沒有驗證
@POST
public Response createUser(UserDto dto) {
  return Response.ok(userService.create(dto)).build();
}

// GOOD: 有驗證的 DTO
public record CreateUserDto(
    @NotBlank @Size(max = 100) String name,
    @NotBlank @Email String email,
    @NotNull @Min(18) @Max(150) Integer age,
    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$") String phone
) {}

@POST
@Path("/users")
public Response createUser(@Valid CreateUserDto dto) {
  User user = userService.create(dto);
  return Response.status(Response.Status.CREATED).entity(user).build();
}
```

### 自訂 Validator

```java
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = UsernameValidator.class)
public @interface ValidUsername {
  String message() default "Invalid username format";
  Class<?>[] groups() default {};
  Class<? extends Payload>[] payload() default {};
}

public class UsernameValidator implements ConstraintValidator<ValidUsername, String> {
  @Override
  public boolean isValid(String value, ConstraintValidatorContext context) {
    if (value == null) return false;
    return value.matches("^[a-zA-Z0-9_-]{3,20}$");
  }
}

// 使用方式
public record CreateUserDto(
    @ValidUsername String username,
    @NotBlank @Email String email
) {}
```

## 防止 SQL Injection

### Panache Active Record（預設安全）

```java
// GOOD: 用 Panache 做參數化查詢
List<User> users = User.list("email = ?1 and active = ?2", email, true);

Optional<User> user = User.find("username", username).firstResultOptional();

// GOOD: 具名參數
List<User> users = User.list("email = :email and age > :minAge",
    Parameters.with("email", email).and("minAge", 18));
```

### Native Query（要用參數）

```java
// BAD: 字串串接
@Query(value = "SELECT * FROM users WHERE name = '" + name + "'", nativeQuery = true)

// GOOD: 參數化的 native query
@Entity
public class User extends PanacheEntity {
  public static List<User> findByEmailNative(String email) {
    return getEntityManager()
        .createNativeQuery("SELECT * FROM users WHERE email = :email", User.class)
        .setParameter("email", email)
        .getResultList();
  }
}
```

## 密碼雜湊

```java
@ApplicationScoped
public class PasswordService {

  public String hash(String plainPassword) {
    return BcryptUtil.bcryptHash(plainPassword);
  }

  public boolean verify(String plainPassword, String hashedPassword) {
    return BcryptUtil.matches(plainPassword, hashedPassword);
  }
}

// 在 service 裡
@ApplicationScoped
public class UserService {
  @Inject
  PasswordService passwordService;

  @Transactional
  public User register(CreateUserDto dto) {
    String hashedPassword = passwordService.hash(dto.password());
    User user = new User();
    user.email = dto.email();
    user.password = hashedPassword;
    user.persist();
    return user;
  }

  public boolean authenticate(String email, String password) {
    return User.find("email", email)
        .firstResultOptional()
        .map(u -> passwordService.verify(password, u.password))
        .orElse(false);
  }
}
```

## CORS 設定

```properties
# application.properties
quarkus.http.cors=true
quarkus.http.cors.origins=https://app.example.com,https://admin.example.com
quarkus.http.cors.methods=GET,POST,PUT,DELETE
quarkus.http.cors.headers=accept,authorization,content-type,x-requested-with
quarkus.http.cors.exposed-headers=Content-Disposition
quarkus.http.cors.access-control-max-age=24H
quarkus.http.cors.access-control-allow-credentials=true
```

## Secret 管理

```properties
# application.properties - 這裡不放任何 secret

# 使用環境變數
quarkus.datasource.username=${DB_USER}
quarkus.datasource.password=${DB_PASSWORD}
quarkus.oidc.credentials.secret=${OIDC_CLIENT_SECRET}

# 或使用 Vault
quarkus.vault.url=https://vault.example.com
quarkus.vault.authentication.kubernetes.role=my-role
```

### HashiCorp Vault 整合

```java
@ApplicationScoped
public class SecretService {

  @ConfigProperty(name = "api-key")
  String apiKey; // 從 Vault 取得

  public String getSecret(String key) {
    return ConfigProvider.getConfig().getValue(key, String.class);
  }
}
```

## Rate Limiting

**安全注意事項**：絕對不要直接使用 `X-Forwarded-For`，客戶端可以偽造它。
可以的話，用 servlet request 取得的實際遠端位址，
或已驗證的身分（API key、JWT subject）。

```java
@ApplicationScoped
public class RateLimitFilter implements ContainerRequestFilter {
  private final Map<String, RateLimiter> limiters = new ConcurrentHashMap<>();

  @Inject
  HttpServletRequest servletRequest;

  @Override
  public void filter(ContainerRequestContext requestContext) {
    String clientId = getClientIdentifier();
    RateLimiter limiter = limiters.computeIfAbsent(clientId,
        k -> RateLimiter.create(100.0)); // 每秒 100 個請求

    if (!limiter.tryAcquire()) {
      requestContext.abortWith(
          Response.status(429)
              .entity(Map.of("error", "Too many requests"))
              .build()
      );
    }
  }

  private String getClientIdentifier() {
    // 使用容器提供的遠端位址（不是 X-Forwarded-For）。
    // 如果在可信任的 proxy 後面，設定 quarkus.http.proxy.proxy-address-forwarding=true
    // 這樣 getRemoteAddr() 才會回傳真正的客戶端 IP。
    return servletRequest.getRemoteAddr();
  }
}
```

## 安全標頭

```java
@Provider
public class SecurityHeadersFilter implements ContainerResponseFilter {

  @Override
  public void filter(ContainerRequestContext request, ContainerResponseContext response) {
    MultivaluedMap<String, Object> headers = response.getHeaders();

    // 防止 clickjacking
    headers.putSingle("X-Frame-Options", "DENY");

    // XSS 防護
    headers.putSingle("X-Content-Type-Options", "nosniff");
    headers.putSingle("X-XSS-Protection", "1; mode=block");

    // HSTS
    headers.putSingle("Strict-Transport-Security", "max-age=31536000; includeSubDomains");

    // CSP：script-src 避免用 'unsafe-inline'，因為它會抵銷 XSS 防護；
    // 改用 nonce 或 hash。CSS 框架需要時，style-src 可以接受 'unsafe-inline'，
    // 但能用 nonce 就優先用 nonce。
    headers.putSingle("Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'");
  }
}
```

## 稽核 Logging

```java
@ApplicationScoped
public class AuditService {
  private static final Logger LOG = Logger.getLogger(AuditService.class);

  @Inject
  SecurityIdentity securityIdentity;

  public void logAccess(String resource, String action) {
    String user = securityIdentity.isAnonymous()
        ? "anonymous"
        : securityIdentity.getPrincipal().getName();

    LOG.infof("AUDIT: user=%s action=%s resource=%s timestamp=%s",
        user, action, resource, Instant.now());
  }
}

// 在 resource 裡使用
@Path("/api/sensitive")
public class SensitiveResource {
  @Inject
  AuditService auditService;

  @GET
  @RolesAllowed("ADMIN")
  public Response getData() {
    auditService.logAccess("sensitive-data", "READ");
    return Response.ok(data).build();
  }
}
```

## 依賴套件安全掃描

```bash
# Maven
mvn org.owasp:dependency-check-maven:check

# Gradle
./gradlew dependencyCheckAnalyze

# 檢查 Quarkus extension
quarkus extension list --installable
```

## 最佳實踐

- production 一律用 HTTPS
- 無狀態驗證啟用 JWT 或 OIDC
- 宣告式授權用 `@RolesAllowed`
- 用 Bean Validation 驗證所有輸入
- 密碼用 BCrypt 雜湊（絕對不要存明文）
- secret 存放在 Vault 或環境變數
- 用參數化查詢防止 SQL injection
- 所有回應都加上安全標頭
- 對公開 endpoint 實作 rate limiting
- 稽核敏感操作
- 依賴套件保持更新，並掃描 CVE
- 程式化檢查用 SecurityIdentity
- 設定適當的 CORS 政策
- 測試驗證和授權的路徑
