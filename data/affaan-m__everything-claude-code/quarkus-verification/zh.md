---
name: quarkus-verification
description: "Quarkus 專案的驗證迴圈：建置、靜態分析（Checkstyle、PMD、SpotBugs）、搭配 JaCoCo 覆蓋率的測試、OWASP 依賴與容器安全掃描、GraalVM native 編譯、健康檢查，以及設定驗證。在 PR 之前、大型重構或依賴升級之後、部署前，驗證 Quarkus 服務時使用。"
metadata:
  origin: ECC
---

# Quarkus 驗證迴圈

在開 PR 前、大幅修改後和部署前執行。

## 何時啟用

- 為 Quarkus 服務開 pull request 之前
- 大型重構或依賴升級之後
- staging 或 production 部署前的驗證
- 跑完整的 build → lint → test → 安全掃描 → native 編譯 pipeline
- 驗證測試覆蓋率達到門檻（80% 以上）
- 測試 native image 相容性

## 階段 1：建置

```bash
# Maven
mvn clean verify -DskipTests

# Gradle
./gradlew clean assemble -x test
```

建置失敗就停下來，先修掉編譯錯誤。

## 階段 2：靜態分析

### Checkstyle、PMD、SpotBugs（Maven）

```bash
mvn checkstyle:check pmd:check spotbugs:check
```

### SonarQube（如果有設定）

```bash
mvn sonar:sonar \
  -Dsonar.projectKey=my-quarkus-project \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=${SONAR_TOKEN}
```

### 常見要處理的問題

- 沒用到的 import 或變數
- 複雜的方法（循環複雜度高）
- 潛在的 null pointer dereference
- SpotBugs 標出的安全問題

## 階段 3：測試加覆蓋率

```bash
# 跑所有測試
mvn clean test

# 產生覆蓋率報告
mvn jacoco:report

# 強制覆蓋率門檻（80%）
mvn jacoco:check

# 或用 Gradle
./gradlew test jacocoTestReport jacocoTestCoverageVerification
```

### 測試類別

#### 單元測試
用 mock 的依賴測試 service 邏輯：

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
  @Mock UserRepository userRepository;
  @InjectMocks UserService userService;

  @Test
  void createUser_validInput_returnsUser() {
    var dto = new CreateUserDto("Alice", "alice@example.com");

    // Panache 的 persist() 是 void，用 doNothing 加 verify
    doNothing().when(userRepository).persist(any(User.class));

    User result = userService.create(dto);

    assertThat(result.name).isEqualTo("Alice");
    verify(userRepository).persist(any(User.class));
  }
}
```

#### 整合測試
用真實資料庫測試（Testcontainers）：

```java
@QuarkusTest
@QuarkusTestResource(PostgresTestResource.class)
class UserRepositoryIntegrationTest {

  @Inject
  UserRepository userRepository;

  @Test
  @Transactional
  void findByEmail_existingUser_returnsUser() {
    User user = new User();
    user.name = "Alice";
    user.email = "alice@example.com";
    userRepository.persist(user);

    Optional<User> found = userRepository.findByEmail("alice@example.com");

    assertThat(found).isPresent();
    assertThat(found.get().name).isEqualTo("Alice");
  }
}
```

#### API 測試
用 REST Assured 測試 REST endpoint：

```java
@QuarkusTest
class UserResourceTest {

  @Test
  void createUser_validInput_returns201() {
    given()
        .contentType(ContentType.JSON)
        .body("""
            {"name": "Alice", "email": "alice@example.com"}
            """)
        .when().post("/api/users")
        .then()
        .statusCode(201)
        .body("name", equalTo("Alice"));
  }

  @Test
  void createUser_invalidEmail_returns400() {
    given()
        .contentType(ContentType.JSON)
        .body("""
            {"name": "Alice", "email": "invalid"}
            """)
        .when().post("/api/users")
        .then()
        .statusCode(400);
  }
}
```

### 覆蓋率報告

看 `target/site/jacoco/index.html` 的詳細覆蓋率：
- 整體行覆蓋率（目標：80% 以上）
- 分支覆蓋率（目標：70% 以上）
- 找出沒被覆蓋的關鍵路徑

## 階段 4：安全掃描

### 依賴漏洞（Maven）

```bash
mvn org.owasp:dependency-check-maven:check
```

看 `target/dependency-check-report.html` 的 CVE。

### Quarkus 安全稽核

```bash
# 檢查有漏洞的 extension
mvn quarkus:audit

# 列出所有 extension
mvn quarkus:list-extensions
```

### OWASP ZAP（API 安全測試）

```bash
docker run -t ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py \
  -t http://localhost:8080/q/openapi \
  -f openapi
```

### 常見安全檢查

- [ ] 所有 secret 都在環境變數裡（不在程式碼中）
- [ ] 所有 endpoint 都有輸入驗證
- [ ] 已設定驗證／授權
- [ ] CORS 設定正確
- [ ] 已設定安全標頭
- [ ] 密碼用 BCrypt 雜湊
- [ ] 防止 SQL injection（參數化查詢）
- [ ] 公開 endpoint 有 rate limiting

## 階段 5：Native 編譯

測試 GraalVM native image 相容性：

```bash
# 建置 native 執行檔
mvn package -Dnative

# 或用容器
mvn package -Dnative -Dquarkus.native.container-build=true

# 測試 native 執行檔
./target/*-runner

# 跑基本的 smoke test
curl http://localhost:8080/q/health/live
curl http://localhost:8080/q/health/ready
```

### Native Image 疑難排解

常見問題：
- **Reflection**：為動態載入的類別加 reflection 設定
- **Resources**：用 `quarkus.native.resources.includes` 把資源納入
- **JNI**：如果用 native 函式庫，要註冊 JNI 類別

reflection 設定範例：
```java
@RegisterForReflection(targets = {MyDynamicClass.class})
public class ReflectionConfiguration {}
```

## 階段 6：效能測試

### 用 K6 做負載測試

```javascript
// load-test.js
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const res = http.get('http://localhost:8080/api/markets');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
}
```

執行：
```bash
k6 run load-test.js
```

### 要監控的指標

- 回應時間（p50、p95、p99）
- 吞吐量（requests/sec）
- 錯誤率
- 記憶體使用量
- CPU 使用量

## 階段 7：健康檢查

```bash
# Liveness
curl http://localhost:8080/q/health/live

# Readiness
curl http://localhost:8080/q/health/ready

# 所有健康檢查
curl http://localhost:8080/q/health

# Metrics（如果有啟用）
curl http://localhost:8080/q/metrics
```

預期回應：
```json
{
  "status": "UP",
  "checks": [
    {
      "name": "Database connection",
      "status": "UP"
    }
  ]
}
```

## 階段 8：容器映像建置

```bash
# 建置容器映像
mvn package -Dquarkus.container-image.build=true

# 或指定 registry
mvn package \
  -Dquarkus.container-image.build=true \
  -Dquarkus.container-image.registry=docker.io \
  -Dquarkus.container-image.group=myorg \
  -Dquarkus.container-image.tag=1.0.0

# 測試容器
docker run -p 8080:8080 myorg/my-quarkus-app:1.0.0
```

### 容器安全掃描

```bash
# Trivy
trivy image myorg/my-quarkus-app:1.0.0

# Grype
grype myorg/my-quarkus-app:1.0.0
```

## 階段 9：設定驗證

```bash
# 檢查所有設定屬性
mvn quarkus:info

# 列出所有設定來源
curl http://localhost:8080/q/dev/io.quarkus.quarkus-vertx-http/config
```

### 各環境專屬檢查

- [ ] 每個環境都設定了資料庫 URL
- [ ] secret 已外部化（Vault、環境變數）
- [ ] logging 等級適當
- [ ] CORS origin 設定正確
- [ ] 已設定 rate limiting
- [ ] 已啟用監控／tracing

## 階段 10：文件審查

- [ ] OpenAPI/Swagger 文件是最新的（`/q/swagger-ui`）
- [ ] README 有安裝設定說明
- [ ] API 變更都有文件
- [ ] 破壞性變更有遷移指南
- [ ] 設定屬性都有文件

產生 OpenAPI spec：
```bash
curl http://localhost:8080/q/openapi -o openapi.json
```

## 驗證檢查清單

### 程式碼品質
- [ ] 建置通過，沒有警告
- [ ] 靜態分析乾淨（沒有高／中等級問題）
- [ ] 程式碼符合團隊慣例
- [ ] PR 裡沒有被註解掉的程式碼或 TODO

### 測試
- [ ] 所有測試通過
- [ ] 程式碼覆蓋率 ≥ 80%
- [ ] 有用真實資料庫的整合測試
- [ ] 安全測試通過
- [ ] 效能在可接受範圍內

### 安全
- [ ] 沒有依賴漏洞
- [ ] 驗證／授權已測試
- [ ] 輸入驗證完整
- [ ] 原始碼裡沒有 secret
- [ ] 已設定安全標頭

### 部署
- [ ] Native 編譯成功
- [ ] 容器映像能建置
- [ ] 健康檢查回應正確
- [ ] 設定對目標環境有效

### Native Image
- [ ] Native 執行檔能建置
- [ ] Native 測試通過
- [ ] 啟動時間 < 100ms
- [ ] 記憶體佔用可接受

## 自動化驗證腳本

```bash
#!/bin/bash
set -e

echo "=== 階段 1：建置 ==="
mvn clean verify -DskipTests

echo "=== 階段 2：靜態分析 ==="
mvn checkstyle:check pmd:check spotbugs:check

echo "=== 階段 3：測試加覆蓋率 ==="
mvn test jacoco:report jacoco:check

echo "=== 階段 4：安全掃描 ==="
mvn org.owasp:dependency-check-maven:check

echo "=== 階段 5：Native 編譯 ==="
mvn package -Dnative -Dquarkus.native.container-build=true

echo "=== 所有階段完成 ==="
echo "請檢視報告："
echo "  - 覆蓋率：target/site/jacoco/index.html"
echo "  - 安全性：target/dependency-check-report.html"
echo "  - Native：target/*-runner"
```

## CI/CD 整合

### GitHub Actions 範例

```yaml
name: Verification

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - name: Set up JDK 21
        uses: actions/setup-java@v5
        with:
          java-version: '21'
          distribution: 'temurin'

      - name: Cache Maven packages
        uses: actions/cache@v6
        with:
          path: ~/.m2
          key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}

      - name: Build
        run: mvn clean verify -DskipTests

      - name: Test with Coverage
        run: mvn test jacoco:report jacoco:check

      - name: Security Scan
        run: mvn org.owasp:dependency-check-maven:check

      - name: Upload Coverage
        uses: codecov/codecov-action@v7
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: target/site/jacoco/jacoco.xml
```

## 最佳實踐

- 每個 PR 之前都跑驗證迴圈
- 在 CI/CD pipeline 中自動化
- 問題馬上修，不要累積技術債
- 覆蓋率維持在 80% 以上
- 定期更新依賴
- 定期測試 native 編譯
- 監控效能趨勢
- 文件化破壞性變更
- 檢視安全掃描結果
- 驗證每個環境的設定
