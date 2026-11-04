---
name: quarkus-tdd
description: 用 JUnit 5、Mockito、REST Assured、Camel 測試和 JaCoCo，對 Quarkus 3.x LTS 做測試驅動開發。新增功能、修 bug 或重構事件驅動服務時使用。
metadata:
  origin: ECC
---

# Quarkus TDD 工作流程

適用 Quarkus 3.x 服務的 TDD 指南，覆蓋率 80% 以上（單元加整合）。針對 Apache Camel 的事件驅動架構做過最佳化。

## 何時使用

- 新功能或 REST endpoint
- 修 bug 或重構
- 新增資料存取邏輯、安全規則或 reactive stream
- 測試 Apache Camel route 和事件處理器
- 測試用到 RabbitMQ 的事件驅動服務
- 測試條件式流程邏輯
- 驗證 CompletableFuture 非同步操作
- 測試 LogContext 的傳遞

## 工作流程

1. 先寫測試（應該會失敗）
2. 寫出剛好能通過的最少程式碼
3. 在測試全綠的狀態下重構
4. 用 JaCoCo 強制覆蓋率（目標 80% 以上）

## 用 @Nested 組織的單元測試

照這個結構化做法，寫出完整又好讀的測試：

```java
@ExtendWith(MockitoExtension.class)
@DisplayName("OrderService Unit Tests")
class OrderServiceTest {

  @Mock
  private OrderRepository orderRepository;

  @Mock
  private EventService eventService;

  @Mock
  private FulfillmentPublisher fulfillmentPublisher;

  @InjectMocks
  private OrderService orderService;

  private CreateOrderCommand validCommand;

  @BeforeEach
  void setUp() {
    validCommand = new CreateOrderCommand(
        "customer-123",
        List.of(new OrderLine("sku-123", 2))
    );
  }

  @Nested
  @DisplayName("Tests for createOrder")
  class CreateOrder {

    @Test
    @DisplayName("Should persist order and publish fulfillment event")
    void givenValidCommand_whenCreateOrder_thenPersistsAndPublishes() {
      // ARRANGE
      doNothing().when(orderRepository).persist(any(Order.class));

      // ACT
      OrderReceipt receipt = orderService.createOrder(validCommand);

      // ASSERT
      assertThat(receipt).isNotNull();
      assertThat(receipt.customerId()).isEqualTo("customer-123");
      verify(orderRepository).persist(any(Order.class));
      verify(fulfillmentPublisher).publishAsync(receipt);
      verify(eventService).createSuccessEvent(receipt, "ORDER_CREATED");
    }

    @Test
    @DisplayName("Should reject missing customer id")
    void givenMissingCustomerId_whenCreateOrder_thenThrowsBadRequest() {
      // ARRANGE
      CreateOrderCommand invalid = new CreateOrderCommand("", validCommand.lines());

      // ACT & ASSERT
      WebApplicationException exception = assertThrows(
          WebApplicationException.class,
          () -> orderService.createOrder(invalid)
      );

      assertThat(exception.getResponse().getStatus()).isEqualTo(400);
      verify(orderRepository, never()).persist(any(Order.class));
      verify(fulfillmentPublisher, never()).publishAsync(any());
    }

    @Test
    @DisplayName("Should record error event when persistence fails")
    void givenPersistenceFailure_whenCreateOrder_thenRecordsErrorEvent() {
      // ARRANGE
      doThrow(new PersistenceException("database unavailable"))
          .when(orderRepository).persist(any(Order.class));

      // ACT & ASSERT
      PersistenceException exception = assertThrows(
          PersistenceException.class,
          () -> orderService.createOrder(validCommand)
      );

      assertThat(exception.getMessage()).contains("database unavailable");
      verify(eventService).createErrorEvent(
          eq(validCommand),
          eq("ORDER_CREATE_FAILED"),
          contains("database unavailable")
      );
      verify(fulfillmentPublisher, never()).publishAsync(any());
    }

    @Test
    @DisplayName("Should reject null commands")
    void givenNullCommand_whenCreateOrder_thenThrowsNullPointerException() {
      // ACT & ASSERT
      assertThrows(
          NullPointerException.class,
          () -> orderService.createOrder(null)
      );

      verify(orderRepository, never()).persist(any(Order.class));
    }
  }
}
```

### 關鍵測試模式

1. **@Nested 類別**：依被測試的方法分組
2. **@DisplayName**：為測試報告提供好讀的測試描述
3. **命名慣例**：用 `givenX_whenY_thenZ`，讀起來清楚
4. **AAA 模式**：明確寫出 `// ARRANGE`、`// ACT`、`// ASSERT` 註解
5. **@BeforeEach**：準備共用的測試資料，減少重複
6. **assertDoesNotThrow**：測試成功情境時，不必自己 catch 例外
7. **assertThrows**：測試例外情境，並用 AssertJ 驗證訊息
8. **完整覆蓋**：測試正常路徑、null 輸入、邊界情況、例外
9. **驗證互動**：用 Mockito 的 `verify()` 確認方法有被正確呼叫
10. **Never Verify**：用 `never()` 確認錯誤情境下方法沒有被呼叫

## 測試 Camel Route

```java
@QuarkusTest
@DisplayName("Business Rules Camel Route Tests")
class BusinessRulesRouteTest {

  @Inject
  CamelContext camelContext;

  @Inject
  ProducerTemplate producerTemplate;

  @InjectMock
  EventService eventService;

  @InjectMock
  DocumentValidator documentValidator;

  private BusinessRulesPayload testPayload;

  @BeforeEach
  void setUp() {
    // ARRANGE - 測試資料
    testPayload = new BusinessRulesPayload();
    testPayload.setDocumentId(1L);
    testPayload.setFlowProfile(FlowProfile.BASIC);
  }

  @Nested
  @DisplayName("Tests for business-rules-publisher route")
  class BusinessRulesPublisher {

    @Test
    @DisplayName("Should successfully publish message to RabbitMQ")
    void givenValidPayload_whenPublish_thenMessageSentToQueue() throws Exception {
      // ARRANGE
      MockEndpoint mockRabbitMQ = camelContext.getEndpoint("mock:rabbitmq", MockEndpoint.class);
      mockRabbitMQ.expectedMessageCount(1);

      // 用 mock 取代真實 endpoint 來做測試
      camelContext.getRouteController().stopRoute("business-rules-publisher");
      AdviceWith.adviceWith(camelContext, "business-rules-publisher", advice -> {
        advice.replaceFromWith("direct:business-rules-publisher");
        advice.weaveByToString(".*spring-rabbitmq.*").replace().to("mock:rabbitmq");
      });
      camelContext.getRouteController().startRoute("business-rules-publisher");

      // ACT
      producerTemplate.sendBody("direct:business-rules-publisher", testPayload);

      // ASSERT — body 經過 .marshal().json(JsonLibrary.Jackson) 之後是 JSON String
      mockRabbitMQ.assertIsSatisfied(5000);

      assertThat(mockRabbitMQ.getExchanges()).hasSize(1);
      String body = mockRabbitMQ.getExchanges().get(0).getIn().getBody(String.class);
      assertThat(body).contains("\"documentId\":1");
    }

    @Test
    @DisplayName("Should handle marshalling to JSON")
    void givenPayload_whenPublish_thenMarshalledToJson() throws Exception {
      // ARRANGE
      MockEndpoint mockMarshal = new MockEndpoint("mock:marshal");
      camelContext.addEndpoint("mock:marshal", mockMarshal);
      mockMarshal.expectedMessageCount(1);

      camelContext.getRouteController().stopRoute("business-rules-publisher");
      AdviceWith.adviceWith(camelContext, "business-rules-publisher", advice -> {
        advice.weaveAddLast().to("mock:marshal");
      });
      camelContext.getRouteController().startRoute("business-rules-publisher");

      // ACT
      producerTemplate.sendBody("direct:business-rules-publisher", testPayload);

      // ASSERT
      mockMarshal.assertIsSatisfied(5000);

      String body = mockMarshal.getExchanges().get(0).getIn().getBody(String.class);
      assertThat(body).contains("\"documentId\":1");
      assertThat(body).contains("\"flowProfile\":\"BASIC\"");
    }
  }

  @Nested
  @DisplayName("Tests for document-processing route")
  class DocumentProcessing {

    @Test
    @DisplayName("Should route invoice to correct processor")
    void givenInvoiceType_whenProcess_thenRoutesToInvoiceProcessor() throws Exception {
      // ARRANGE
      MockEndpoint mockInvoice = camelContext.getEndpoint("mock:invoice", MockEndpoint.class);
      mockInvoice.expectedMessageCount(1);

      camelContext.getRouteController().stopRoute("document-processing");
      AdviceWith.adviceWith(camelContext, "document-processing", advice -> {
        advice.weaveByToString(".*direct:process-invoice.*").replace().to("mock:invoice");
      });
      camelContext.getRouteController().startRoute("document-processing");

      // ACT
      producerTemplate.sendBodyAndHeader("direct:process-document",
          testPayload, "documentType", "INVOICE");

      // ASSERT
      mockInvoice.assertIsSatisfied(5000);
    }

    @Test
    @DisplayName("Should handle validation errors gracefully")
    void givenValidationError_whenProcess_thenRoutesToErrorHandler() throws Exception {
      // ARRANGE
      MockEndpoint mockError = camelContext.getEndpoint("mock:error", MockEndpoint.class);
      mockError.expectedMessageCount(1);

      camelContext.getRouteController().stopRoute("document-processing");
      AdviceWith.adviceWith(camelContext, "document-processing", advice -> {
        advice.weaveByToString(".*direct:validation-error-handler.*")
            .replace().to("mock:error");
      });
      camelContext.getRouteController().startRoute("document-processing");

      // Mock validator bean 讓它丟出例外
      when(documentValidator.validate(any())).thenThrow(new ValidationException("Invalid document"));

      // ACT
      producerTemplate.sendBody("direct:process-document", testPayload);

      // ASSERT
      mockError.assertIsSatisfied(5000);

      Exception exception = mockError.getExchanges().get(0).getException();
      assertThat(exception).isInstanceOf(ValidationException.class);
      assertThat(exception.getMessage()).contains("Invalid document");
    }
  }
}
```

## 測試 Event Service

```java
@ExtendWith(MockitoExtension.class)
@DisplayName("EventService Unit Tests")
class EventServiceTest {

  @Mock
  private EventRepository eventRepository;

  @Mock
  private ObjectMapper objectMapper;

  @InjectMocks
  private EventService eventService;

  private BusinessRulesPayload testPayload;

  @BeforeEach
  void setUp() {
    // ARRANGE
    testPayload = new BusinessRulesPayload();
    testPayload.setDocumentId(1L);
  }

  @Nested
  @DisplayName("Tests for createSuccessEvent")
  class CreateSuccessEvent {

    @Test
    @DisplayName("Should create success event with correct attributes")
    void givenValidPayload_whenCreateSuccessEvent_thenEventPersisted() throws Exception {
      // ARRANGE
      when(objectMapper.writeValueAsString(testPayload)).thenReturn("{\"documentId\":1}");

      // ACT
      assertDoesNotThrow(() ->
          eventService.createSuccessEvent(testPayload, "DOCUMENT_PROCESSED"));

      // ASSERT
      verify(eventRepository).persist(argThat(event ->
          event.getType().equals("DOCUMENT_PROCESSED") &&
          event.getStatus() == EventStatus.SUCCESS &&
          event.getPayload().equals("{\"documentId\":1}") &&
          event.getTimestamp() != null
      ));
    }

    @Test
    @DisplayName("Should throw exception when payload is null")
    void givenNullPayload_whenCreateSuccessEvent_thenThrowsException() {
      // ARRANGE
      Object nullPayload = null;

      // ACT & ASSERT
      NullPointerException exception = assertThrows(
          NullPointerException.class,
          () -> eventService.createSuccessEvent(nullPayload, "EVENT_TYPE")
      );

      assertThat(exception.getMessage()).isEqualTo("Payload cannot be null");
      verify(eventRepository, never()).persist(any());
    }
  }

  @Nested
  @DisplayName("Tests for createErrorEvent")
  class CreateErrorEvent {

    @Test
    @DisplayName("Should create error event with error message")
    void givenError_whenCreateErrorEvent_thenEventPersistedWithMessage() throws Exception {
      // ARRANGE
      String errorMessage = "Processing failed";
      when(objectMapper.writeValueAsString(testPayload)).thenReturn("{\"documentId\":1}");

      // ACT
      assertDoesNotThrow(() ->
          eventService.createErrorEvent(testPayload, "PROCESSING_ERROR", errorMessage));

      // ASSERT
      verify(eventRepository).persist(argThat(event ->
          event.getType().equals("PROCESSING_ERROR") &&
          event.getStatus() == EventStatus.ERROR &&
          event.getErrorMessage().equals(errorMessage) &&
          event.getPayload().equals("{\"documentId\":1}")
      ));
    }

    @ParameterizedTest
    @DisplayName("Should reject invalid error messages")
    @ValueSource(strings = {"", " "})
    void givenBlankErrorMessage_whenCreateErrorEvent_thenThrowsException(String blankMessage) {
      // ACT & ASSERT
      IllegalArgumentException exception = assertThrows(
          IllegalArgumentException.class,
          () -> eventService.createErrorEvent(testPayload, "ERROR", blankMessage)
      );

      assertThat(exception.getMessage()).contains("Error message cannot be blank");
    }
  }
}
```

## 測試 CompletableFuture

```java
@ExtendWith(MockitoExtension.class)
@DisplayName("FileStorageService Unit Tests")
class FileStorageServiceTest {

  @Mock
  private S3Client s3Client;

  @Mock
  private ExecutorService executorService;

  @InjectMocks
  private FileStorageService fileStorageService;

  private InputStream testInputStream;
  private LogContext testLogContext;

  @BeforeEach
  void setUp() {
    // ARRANGE
    testInputStream = new ByteArrayInputStream("test content".getBytes());
    testLogContext = new LogContext();
    testLogContext.put("traceId", "trace-123");
  }

  @Nested
  @DisplayName("Tests for uploadOriginalFile")
  class UploadOriginalFile {

    @Test
    @DisplayName("Should successfully upload file and return document info")
    void givenValidFile_whenUpload_thenReturnsDocumentInfo() throws Exception {
      // ARRANGE
      doAnswer(invocation -> {
        ((Runnable) invocation.getArgument(0)).run();
        return null;
      }).when(executorService).execute(any(Runnable.class));

      when(s3Client.putObject(any(PutObjectRequest.class), any(RequestBody.class)))
          .thenReturn(PutObjectResponse.builder().build());

      // ACT
      CompletableFuture<StoredDocumentInfo> future =
          fileStorageService.uploadOriginalFile(testInputStream, 1024L,
              testLogContext, InvoiceFormat.UBL);

      StoredDocumentInfo result = future.join();

      // ASSERT
      assertThat(result).isNotNull();
      assertThat(result.getPath()).isNotBlank();
      assertThat(result.getSize()).isEqualTo(1024L);
      assertThat(result.getUploadedAt()).isNotNull();

      verify(s3Client).putObject(any(PutObjectRequest.class), any(RequestBody.class));
    }

    @Test
    @DisplayName("Should handle S3 upload failure")
    void givenS3Failure_whenUpload_thenCompletableFutureFails() {
      // ARRANGE — 同步執行，讓例外能透過 future 傳遞出來
      doAnswer(invocation -> {
        ((Runnable) invocation.getArgument(0)).run();
        return null;
      }).when(executorService).execute(any(Runnable.class));

      when(s3Client.putObject(any(PutObjectRequest.class), any(RequestBody.class)))
          .thenThrow(new StorageException("S3 unavailable"));

      // ACT
      CompletableFuture<StoredDocumentInfo> future =
          fileStorageService.uploadOriginalFile(testInputStream, 1024L,
              testLogContext, InvoiceFormat.UBL);

      // ASSERT
      assertThatThrownBy(() -> future.join())
          .isInstanceOf(CompletionException.class)
          .hasCauseInstanceOf(StorageException.class)
          .hasMessageContaining("S3 unavailable");
    }

    @Test
    @DisplayName("Should propagate LogContext to async operation")
    void givenLogContext_whenUpload_thenContextPropagated() throws Exception {
      // ARRANGE
      AtomicReference<LogContext> capturedContext = new AtomicReference<>();

      doAnswer(invocation -> {
        capturedContext.set(CustomLog.getCurrentContext());
        ((Runnable) invocation.getArgument(0)).run();
        return null;
      }).when(executorService).execute(any(Runnable.class));

      // ACT
      fileStorageService.uploadOriginalFile(testInputStream, 1024L,
          testLogContext, InvoiceFormat.UBL).join();

      // ASSERT
      assertThat(capturedContext.get()).isNotNull();
      assertThat(capturedContext.get().get("traceId")).isEqualTo("trace-123");
    }
  }
}
```

## Resource 層測試（REST Assured）

```java
@QuarkusTest
@DisplayName("DocumentResource API Tests")
class DocumentResourceTest {

  @InjectMock
  DocumentService documentService;

  @Nested
  @DisplayName("Tests for GET /api/documents")
  class ListDocuments {

    @Test
    @DisplayName("Should return list of documents")
    void givenDocumentsExist_whenList_thenReturnsOk() {
      // ARRANGE
      List<Document> documents = List.of(createDocument(1L, "DOC-001"));
      when(documentService.list(0, 20)).thenReturn(documents);

      // ACT & ASSERT
      given()
          .when().get("/api/documents")
          .then()
          .statusCode(200)
          .body("$.size()", is(1))
          .body("[0].referenceNumber", equalTo("DOC-001"));
    }
  }

  @Nested
  @DisplayName("Tests for POST /api/documents")
  class CreateDocument {

    @Test
    @DisplayName("Should create document and return 201")
    void givenValidRequest_whenCreate_thenReturns201() {
      // ARRANGE
      Document document = createDocument(1L, "DOC-001");
      when(documentService.create(any())).thenReturn(document);

      // ACT & ASSERT
      given()
          .contentType(ContentType.JSON)
          .body("""
              {
                "referenceNumber": "DOC-001",
                "description": "Test document",
                "validUntil": "2030-01-01T00:00:00Z",
                "categories": ["test"]
              }
              """)
          .when().post("/api/documents")
          .then()
          .statusCode(201)
          .header("Location", containsString("/api/documents/1"))
          .body("referenceNumber", equalTo("DOC-001"));
    }

    @Test
    @DisplayName("Should return 400 for invalid input")
    void givenInvalidRequest_whenCreate_thenReturns400() {
      // ACT & ASSERT
      given()
          .contentType(ContentType.JSON)
          .body("""
              {
                "referenceNumber": "",
                "description": "Test"
              }
              """)
          .when().post("/api/documents")
          .then()
          .statusCode(400);
    }
  }

  private Document createDocument(Long id, String referenceNumber) {
    Document document = new Document();
    document.setId(id);
    document.setReferenceNumber(referenceNumber);
    document.setStatus(DocumentStatus.PENDING);
    return document;
  }
}
```

## 搭配真實資料庫的整合測試

```java
@QuarkusTest
@TestProfile(IntegrationTestProfile.class)
@DisplayName("Document Integration Tests")
class DocumentIntegrationTest {

  @Test
  @Transactional
  @DisplayName("Should create and retrieve document via API")
  void givenNewDocument_whenCreateAndRetrieve_thenSuccessful() {
    // ACT - 透過 API 建立
    Long id = given()
        .contentType(ContentType.JSON)
        .body("""
            {
              "referenceNumber": "INT-001",
              "description": "Integration test",
              "validUntil": "2030-01-01T00:00:00Z",
              "categories": ["test"]
            }
            """)
        .when().post("/api/documents")
        .then()
        .statusCode(201)
        .extract().path("id");

    // ASSERT - 透過 API 取回
    given()
        .when().get("/api/documents/" + id)
        .then()
        .statusCode(200)
        .body("referenceNumber", equalTo("INT-001"));
  }
}
```

## 用 JaCoCo 算覆蓋率

### Maven 設定（完整）

```xml
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <version>0.8.13</version>
  <executions>
    <!-- 準備測試執行用的 agent -->
    <execution>
      <id>prepare-agent</id>
      <goals>
        <goal>prepare-agent</goal>
      </goals>
    </execution>

    <!-- 產生覆蓋率報告 -->
    <execution>
      <id>report</id>
      <phase>verify</phase>
      <goals>
        <goal>report</goal>
      </goals>
    </execution>

    <!-- 強制執行覆蓋率門檻 -->
    <execution>
      <id>check</id>
      <goals>
        <goal>check</goal>
      </goals>
      <configuration>
        <rules>
          <rule>
            <element>BUNDLE</element>
            <limits>
              <limit>
                <counter>LINE</counter>
                <value>COVEREDRATIO</value>
                <minimum>0.80</minimum>
              </limit>
              <limit>
                <counter>BRANCH</counter>
                <value>COVEREDRATIO</value>
                <minimum>0.70</minimum>
              </limit>
            </limits>
          </rule>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>
```

用覆蓋率跑測試：
```bash
mvn clean test
mvn jacoco:report
mvn jacoco:check

# 報告位置：target/site/jacoco/index.html
```

## 測試依賴

```xml
<dependencies>
    <!-- Quarkus 測試 -->
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-junit5</artifactId>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-junit5-mockito</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- Mockito -->
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- AssertJ（優先於 JUnit 斷言） -->
    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <version>3.24.2</version>
        <scope>test</scope>
    </dependency>

    <!-- REST Assured -->
    <dependency>
        <groupId>io.rest-assured</groupId>
        <artifactId>rest-assured</artifactId>
        <scope>test</scope>
    </dependency>

    <!-- Camel 測試 -->
    <dependency>
        <groupId>org.apache.camel.quarkus</groupId>
        <artifactId>camel-quarkus-junit5</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

## 最佳實踐

### 測試組織
- 用 `@Nested` 類別依被測試的方法分組
- 用 `@DisplayName` 提供報告裡看得到的好讀測試描述
- 測試方法照 `givenX_whenY_thenZ` 命名
- 共用測試資料用 `@BeforeEach` 準備，減少重複

### 測試結構
- 照 AAA 模式，明確寫註解（`// ARRANGE`、`// ACT`、`// ASSERT`）
- 成功情境用 `assertDoesNotThrow`
- 例外情境用 `assertThrows`，並驗證訊息
- 用 AssertJ 的 `contains()` 或 `isEqualTo()` 驗證例外訊息符合預期

### 測試覆蓋
- 測試所有 public 方法的正常路徑
- 測試 null 輸入的處理
- 測試邊界情況（空集合、邊界值、負數 ID、空白字串）
- 完整測試例外情境
- Mock 所有外部依賴（repository、service、Camel endpoint）
- 目標是行覆蓋率 80% 以上、分支覆蓋率 70% 以上

### 斷言
- 值的檢查**優先用 AssertJ**（`assertThat`），不要用 JUnit 斷言
- 用 AssertJ 的 fluent API 提升可讀性：`assertThat(list).hasSize(3).contains(item)`
- 例外：用 JUnit 的 `assertThrows` 捕捉，再用 AssertJ 驗證訊息
- 不會丟例外的成功路徑：用 JUnit 的 `assertDoesNotThrow`
- 集合：`extracting()`、`filteredOn()`、`containsExactly()`

### 整合測試
- 整合測試用 `@QuarkusTest`
- 在 Quarkus 測試裡用 `@InjectMock` mock 依賴
- API 測試優先用 REST Assured
- 測試專用設定用 `@TestProfile`

### 事件驅動測試
- 用 `AdviceWith` 和 `MockEndpoint` 測試 Camel route
- 用 `@CamelQuarkusTest` 註解（如果用獨立的 Camel 測試）
- 驗證訊息內容、header 和路由邏輯
- 錯誤處理的 route 要另外測
- 單元測試裡 mock 外部系統（RabbitMQ、S3、資料庫）

### Camel Route 測試
- 用 `MockEndpoint` 斷言訊息流
- 用 `AdviceWith` 修改 route 以便測試（把 endpoint 換成 mock）
- 測試訊息轉換和 marshalling
- 測試例外處理和 dead letter queue

### 測試非同步操作
- 測試 CompletableFuture 的成功與失敗情境
- 測試中用 `.join()` 等非同步完成
- 測試 CompletableFuture 的例外傳遞
- 驗證 LogContext 有傳遞到非同步操作

### 效能
- 測試要快，而且彼此隔離
- 用持續模式跑測試：`mvn quarkus:test`
- 輸入有多種變化時，用參數化測試（`@ParameterizedTest`）
- 建立可重用的測試資料 builder 或 factory 方法

### Quarkus 專屬
- 維持在最新的 LTS 版本（Quarkus 3.x）
- 定期測試 native 編譯的相容性
- 不同情境用 Quarkus test profile
- 善用 Quarkus dev services 做本機測試
- 用 `@InjectMock`，不要用 `@MockBean`（Quarkus 專屬）

### 驗證最佳實踐
- 一律驗證 mock 依賴上的互動
- 用 `verify(mock, never())` 確認錯誤情境下方法沒有被呼叫
- 複雜的參數比對用 `argThat()`
- 呼叫順序重要時要驗證順序：Mockito 的 `InOrder`
