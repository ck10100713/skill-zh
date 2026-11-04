---
name: springboot-tdd
description: 用 JUnit 5、Mockito、MockMvc、Testcontainers 和 JaCoCo，對 Spring Boot 做測試驅動開發。新增功能、修 bug 或重構時使用。
metadata:
  origin: ECC
---

# Spring Boot TDD 工作流程

Spring Boot 服務的 TDD 指引，目標 80% 以上的覆蓋率（單元 + 整合）。

## 何時使用

- 新功能或 endpoint
- 修 bug 或重構
- 新增資料存取邏輯或安全規則

## 工作流程

1) 先寫測試（應該要失敗）
2) 實作最少的程式碼讓測試通過
3) 在測試維持綠燈的前提下重構
4) 落實覆蓋率（JaCoCo）

## 單元測試（JUnit 5 + Mockito）

```java
@ExtendWith(MockitoExtension.class)
class MarketServiceTest {
  @Mock MarketRepository repo;
  @InjectMocks MarketService service;

  @Test
  void createsMarket() {
    CreateMarketRequest req = new CreateMarketRequest("name", "desc", Instant.now(), List.of("cat"));
    when(repo.save(any())).thenAnswer(inv -> inv.getArgument(0));

    Market result = service.create(req);

    assertThat(result.name()).isEqualTo("name");
    verify(repo).save(any());
  }
}
```

模式：
- Arrange-Act-Assert
- 避免 partial mock；優先用明確的 stub
- 各種變體用 `@ParameterizedTest`

## Web 層測試（MockMvc）

```java
@WebMvcTest(MarketController.class)
class MarketControllerTest {
  @Autowired MockMvc mockMvc;
  @MockBean MarketService marketService;

  @Test
  void returnsMarkets() throws Exception {
    when(marketService.list(any())).thenReturn(Page.empty());

    mockMvc.perform(get("/api/markets"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.content").isArray());
  }
}
```

## 整合測試（SpringBootTest）

```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class MarketIntegrationTest {
  @Autowired MockMvc mockMvc;

  @Test
  void createsMarket() throws Exception {
    mockMvc.perform(post("/api/markets")
        .contentType(MediaType.APPLICATION_JSON)
        .content("""
          {"name":"Test","description":"Desc","endDate":"2030-01-01T00:00:00Z","categories":["general"]}
        """))
      .andExpect(status().isCreated());
  }
}
```

## 持久層測試（DataJpaTest）

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(TestContainersConfig.class)
class MarketRepositoryTest {
  @Autowired MarketRepository repo;

  @Test
  void savesAndFinds() {
    MarketEntity entity = new MarketEntity();
    entity.setName("Test");
    repo.save(entity);

    Optional<MarketEntity> found = repo.findByName("Test");
    assertThat(found).isPresent();
  }
}
```

## Testcontainers

- Postgres/Redis 用可重複使用的容器，貼近正式環境
- 透過 `@DynamicPropertySource` 把 JDBC URL 注入 Spring context

## 覆蓋率（JaCoCo）

Maven 片段：
```xml
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <version>0.8.14</version>
  <executions>
    <execution>
      <goals><goal>prepare-agent</goal></goals>
    </execution>
    <execution>
      <id>report</id>
      <phase>verify</phase>
      <goals><goal>report</goal></goals>
    </execution>
  </executions>
</plugin>
```

## 斷言

- 為了可讀性，優先用 AssertJ（`assertThat`）
- JSON 回應用 `jsonPath`
- 例外用：`assertThatThrownBy(...)`

## 測試資料 Builder

```java
class MarketBuilder {
  private String name = "Test";
  MarketBuilder withName(String name) { this.name = name; return this; }
  Market build() { return new Market(null, name, MarketStatus.ACTIVE); }
}
```

## CI 指令

- Maven：`mvn -T 4 test` 或 `mvn verify`
- Gradle：`./gradlew test jacocoTestReport`

**記住**：測試要快、要隔離、要可預測。測行為，不要測實作細節。
