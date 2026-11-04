---
name: springboot-verification
description: 執行完整的 Spring Boot 驗證迴圈：Maven 或 Gradle build、SpotBugs、PMD 和 Checkstyle 靜態分析、搭配 JaCoCo 覆蓋率的單元與 Testcontainers 整合測試、OWASP 相依套件和 secret 掃描，以及 diff review，最後產出通過/失敗的就緒報告。準備 Spring Boot pull request、驗證覆蓋率門檻，或做部署前驗證時使用。
metadata:
  origin: ECC
---

# Spring Boot 驗證迴圈

在開 PR 之前、重大變更之後，以及部署前執行。

## 何時啟用

- 為 Spring Boot 服務開 pull request 之前
- 大規模重構或升級相依套件之後
- 部署到 staging 或正式環境前的驗證
- 執行完整的 build → lint → test → 安全掃描 pipeline
- 驗證測試覆蓋率有達到門檻

## 階段 1：Build

```bash
mvn -T 4 clean verify -DskipTests
# or
./gradlew clean assemble -x test
```

Build 失敗就停下來修。

## 階段 2：靜態分析

Maven（常見外掛）：
```bash
mvn -T 4 spotbugs:check pmd:check checkstyle:check
```

Gradle（如果有設定）：
```bash
./gradlew checkstyleMain pmdMain spotbugsMain
```

## 階段 3：測試 + 覆蓋率

```bash
mvn -T 4 test
mvn jacoco:report   # verify 80%+ coverage
# or
./gradlew test jacocoTestReport
```

回報：
- 測試總數、通過/失敗
- 覆蓋率 %（行/分支）

### 單元測試

用 mock 的相依項，單獨測試 service 邏輯：

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

  @Mock private UserRepository userRepository;
  @InjectMocks private UserService userService;

  @Test
  void createUser_validInput_returnsUser() {
    var dto = new CreateUserDto("Alice", "alice@example.com");
    var expected = new User(1L, "Alice", "alice@example.com");
    when(userRepository.save(any(User.class))).thenReturn(expected);

    var result = userService.create(dto);

    assertThat(result.name()).isEqualTo("Alice");
    verify(userRepository).save(any(User.class));
  }

  @Test
  void createUser_duplicateEmail_throwsException() {
    var dto = new CreateUserDto("Alice", "existing@example.com");
    when(userRepository.existsByEmail(dto.email())).thenReturn(true);

    assertThatThrownBy(() -> userService.create(dto))
        .isInstanceOf(DuplicateEmailException.class);
  }
}
```

### 搭配 Testcontainers 的整合測試

對真實資料庫測試，不要用 H2：

```java
@SpringBootTest
@Testcontainers
class UserRepositoryIntegrationTest {

  @Container
  static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
      .withDatabaseName("testdb");

  @DynamicPropertySource
  static void configureProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", postgres::getJdbcUrl);
    registry.add("spring.datasource.username", postgres::getUsername);
    registry.add("spring.datasource.password", postgres::getPassword);
  }

  @Autowired private UserRepository userRepository;

  @Test
  void findByEmail_existingUser_returnsUser() {
    userRepository.save(new User("Alice", "alice@example.com"));

    var found = userRepository.findByEmail("alice@example.com");

    assertThat(found).isPresent();
    assertThat(found.get().getName()).isEqualTo("Alice");
  }
}
```

### 搭配 MockMvc 的 API 測試

用完整的 Spring context 測試 controller 層：

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

  @Autowired private MockMvc mockMvc;
  @MockBean private UserService userService;

  @Test
  void createUser_validInput_returns201() throws Exception {
    var user = new UserDto(1L, "Alice", "alice@example.com");
    when(userService.create(any())).thenReturn(user);

    mockMvc.perform(post("/api/users")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""
                {"name": "Alice", "email": "alice@example.com"}
                """))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.name").value("Alice"));
  }

  @Test
  void createUser_invalidEmail_returns400() throws Exception {
    mockMvc.perform(post("/api/users")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""
                {"name": "Alice", "email": "not-an-email"}
                """))
        .andExpect(status().isBadRequest());
  }
}
```

## 階段 4：安全掃描

```bash
# Dependency CVEs
mvn org.owasp:dependency-check-maven:check
# or
./gradlew dependencyCheckAnalyze

# Secrets in source
grep -rn "password\s*=\s*\"" src/ --include="*.java" --include="*.yml" --include="*.properties"
grep -rn "sk-\|api_key\|secret" src/ --include="*.java" --include="*.yml"

# Secrets (git history)
git secrets --scan  # if configured
```

### 常見的安全發現

```
# Check for System.out.println (use logger instead)
grep -rn "System\.out\.print" src/main/ --include="*.java"

# Check for raw exception messages in responses
grep -rn "e\.getMessage()" src/main/ --include="*.java"

# Check for wildcard CORS
grep -rn "allowedOrigins.*\*" src/main/ --include="*.java"
```

## 階段 5：Lint/格式化（選用關卡）

```bash
mvn spotless:apply   # if using Spotless plugin
./gradlew spotlessApply
```

## 階段 6：Diff Review

```bash
git diff --stat
git diff
```

檢查清單：
- 沒有遺留除錯日誌（`System.out`、沒有 guard 的 `log.debug`）
- 錯誤訊息和 HTTP 狀態碼有意義
- 需要的地方有交易和驗證
- 設定變更有記錄文件

## 輸出範本

```
VERIFICATION REPORT
===================
Build:     [PASS/FAIL]
Static:    [PASS/FAIL] (spotbugs/pmd/checkstyle)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (CVE findings: N)
Diff:      [X files changed]

Overall:   [READY / NOT READY]

Issues to Fix:
1. ...
2. ...
```

## 持續模式

- 有重大變更時重新執行各階段，長時間的 session 則每 30 到 60 分鐘執行一次
- 保持短迴圈：`mvn -T 4 test` 加 spotbugs，快速取得回饋

**記住**：快速回饋勝過遲來的驚嚇。關卡要嚴格，在正式環境的系統裡，警告就當成缺陷處理。
