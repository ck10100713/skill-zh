---
name: kotlin-testing
description: 用 Kotest、MockK、coroutine 測試、property-based testing 與 Kover 覆蓋率的 Kotlin 測試模式，遵循 TDD 方法論與慣用的 Kotlin 寫法。在用 Kotest 或 MockK 寫 Kotlin 測試，或測試 coroutines、檢查覆蓋率時使用。
metadata:
  origin: ECC
---

# Kotlin Testing Patterns

用 Kotest 與 MockK、依 TDD 方法論撰寫可靠、好維護的 Kotlin 測試的完整模式。

## 何時使用

- 撰寫新的 Kotlin 函式或 class
- 為既有的 Kotlin 程式碼補測試覆蓋
- 實作 property-based test
- 在 Kotlin 專案中遵循 TDD 流程
- 設定 Kover 來量測程式碼覆蓋率

## 運作方式

1. **找出目標程式碼**：找到要測試的函式、class 或 module
2. **寫 Kotest spec**：依測試範圍選擇 spec 風格（StringSpec、FunSpec、BehaviorSpec）
3. **mock 依賴**：用 MockK 隔離被測單元
4. **跑測試（RED）**：確認測試以預期的錯誤失敗
5. **實作程式碼（GREEN）**：寫最少的程式碼讓測試通過
6. **Refactor**：在測試維持綠燈的前提下改善實作
7. **檢查覆蓋率**：執行 `./gradlew koverHtmlReport`，確認覆蓋率 80% 以上

## 範例

以下各節針對每種測試模式提供詳細、可執行的範例：

### 速查

- **Kotest spec**：StringSpec、FunSpec、BehaviorSpec、DescribeSpec 的範例在 [Kotest Spec Styles](#kotest-spec-styles)
- **Mock**：MockK 設定、coroutine mock、參數捕捉在 [MockK](#mockk)
- **TDD 逐步示範**：用 EmailValidator 走完整的 RED/GREEN/REFACTOR 循環，在 [TDD Workflow for Kotlin](#tdd-workflow-for-kotlin)
- **覆蓋率**：Kover 設定與指令在 [Kover Coverage](#kover-coverage)
- **Ktor 測試**：testApplication 設定在 [Ktor testApplication Testing](#ktor-testapplication-testing)

### TDD Workflow for Kotlin

#### RED-GREEN-REFACTOR 循環

```
RED     -> Write a failing test first
GREEN   -> Write minimal code to pass the test
REFACTOR -> Improve code while keeping tests green
REPEAT  -> Continue with next requirement
```

#### 在 Kotlin 中逐步做 TDD

```kotlin
// Step 1: Define the interface/signature
// EmailValidator.kt
package com.example.validator

fun validateEmail(email: String): Result<String> {
    TODO("not implemented")
}

// Step 2: Write failing test (RED)
// EmailValidatorTest.kt
package com.example.validator

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.result.shouldBeFailure
import io.kotest.matchers.result.shouldBeSuccess

class EmailValidatorTest : StringSpec({
    "valid email returns success" {
        validateEmail("user@example.com").shouldBeSuccess("user@example.com")
    }

    "empty email returns failure" {
        validateEmail("").shouldBeFailure()
    }

    "email without @ returns failure" {
        validateEmail("userexample.com").shouldBeFailure()
    }
})

// Step 3: Run tests - verify FAIL
// $ ./gradlew test
// EmailValidatorTest > valid email returns success FAILED
//   kotlin.NotImplementedError: An operation is not implemented

// Step 4: Implement minimal code (GREEN)
fun validateEmail(email: String): Result<String> {
    if (email.isBlank()) return Result.failure(IllegalArgumentException("Email cannot be blank"))
    if ('@' !in email) return Result.failure(IllegalArgumentException("Email must contain @"))
    val regex = Regex("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")
    if (!regex.matches(email)) return Result.failure(IllegalArgumentException("Invalid email format"))
    return Result.success(email)
}

// Step 5: Run tests - verify PASS
// $ ./gradlew test
// EmailValidatorTest > valid email returns success PASSED
// EmailValidatorTest > empty email returns failure PASSED
// EmailValidatorTest > email without @ returns failure PASSED

// Step 6: Refactor if needed, verify tests still pass
```

### Kotest Spec Styles

#### StringSpec（最簡單）

```kotlin
class CalculatorTest : StringSpec({
    "add two positive numbers" {
        Calculator.add(2, 3) shouldBe 5
    }

    "add negative numbers" {
        Calculator.add(-1, -2) shouldBe -3
    }

    "add zero" {
        Calculator.add(0, 5) shouldBe 5
    }
})
```

#### FunSpec（類 JUnit）

```kotlin
class UserServiceTest : FunSpec({
    val repository = mockk<UserRepository>()
    val service = UserService(repository)

    test("getUser returns user when found") {
        val expected = User(id = "1", name = "Alice")
        coEvery { repository.findById("1") } returns expected

        val result = service.getUser("1")

        result shouldBe expected
    }

    test("getUser throws when not found") {
        coEvery { repository.findById("999") } returns null

        shouldThrow<UserNotFoundException> {
            service.getUser("999")
        }
    }
})
```

#### BehaviorSpec（BDD 風格）

```kotlin
class OrderServiceTest : BehaviorSpec({
    val repository = mockk<OrderRepository>()
    val paymentService = mockk<PaymentService>()
    val service = OrderService(repository, paymentService)

    Given("a valid order request") {
        val request = CreateOrderRequest(
            userId = "user-1",
            items = listOf(OrderItem("product-1", quantity = 2)),
        )

        When("the order is placed") {
            coEvery { paymentService.charge(any()) } returns PaymentResult.Success
            coEvery { repository.save(any()) } answers { firstArg() }

            val result = service.placeOrder(request)

            Then("it should return a confirmed order") {
                result.status shouldBe OrderStatus.CONFIRMED
            }

            Then("it should charge payment") {
                coVerify(exactly = 1) { paymentService.charge(any()) }
            }
        }

        When("payment fails") {
            coEvery { paymentService.charge(any()) } returns PaymentResult.Declined

            Then("it should throw PaymentException") {
                shouldThrow<PaymentException> {
                    service.placeOrder(request)
                }
            }
        }
    }
})
```

#### DescribeSpec（RSpec 風格）

```kotlin
class UserValidatorTest : DescribeSpec({
    describe("validateUser") {
        val validator = UserValidator()

        context("with valid input") {
            it("accepts a normal user") {
                val user = CreateUserRequest("Alice", "alice@example.com")
                validator.validate(user).shouldBeValid()
            }
        }

        context("with invalid name") {
            it("rejects blank name") {
                val user = CreateUserRequest("", "alice@example.com")
                validator.validate(user).shouldBeInvalid()
            }

            it("rejects name exceeding max length") {
                val user = CreateUserRequest("A".repeat(256), "alice@example.com")
                validator.validate(user).shouldBeInvalid()
            }
        }
    }
})
```

### Kotest Matchers

#### 核心 Matcher

```kotlin
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import io.kotest.matchers.string.*
import io.kotest.matchers.collections.*
import io.kotest.matchers.nulls.*

// Equality
result shouldBe expected
result shouldNotBe unexpected

// Strings
name shouldStartWith "Al"
name shouldEndWith "ice"
name shouldContain "lic"
name shouldMatch Regex("[A-Z][a-z]+")
name.shouldBeBlank()

// Collections
list shouldContain "item"
list shouldHaveSize 3
list.shouldBeSorted()
list.shouldContainAll("a", "b", "c")
list.shouldBeEmpty()

// Nulls
result.shouldNotBeNull()
result.shouldBeNull()

// Types
result.shouldBeInstanceOf<User>()

// Numbers
count shouldBeGreaterThan 0
price shouldBeInRange 1.0..100.0

// Exceptions
shouldThrow<IllegalArgumentException> {
    validateAge(-1)
}.message shouldBe "Age must be positive"

shouldNotThrow<Exception> {
    validateAge(25)
}
```

#### 自訂 Matcher

```kotlin
fun beActiveUser() = object : Matcher<User> {
    override fun test(value: User) = MatcherResult(
        value.isActive && value.lastLogin != null,
        { "User ${value.id} should be active with a last login" },
        { "User ${value.id} should not be active" },
    )
}

// Usage
user should beActiveUser()
```

### MockK

#### 基本 Mock

```kotlin
class UserServiceTest : FunSpec({
    val repository = mockk<UserRepository>()
    val logger = mockk<Logger>(relaxed = true) // Relaxed: returns defaults
    val service = UserService(repository, logger)

    beforeTest {
        clearMocks(repository, logger)
    }

    test("findUser delegates to repository") {
        val expected = User(id = "1", name = "Alice")
        every { repository.findById("1") } returns expected

        val result = service.findUser("1")

        result shouldBe expected
        verify(exactly = 1) { repository.findById("1") }
    }

    test("findUser returns null for unknown id") {
        every { repository.findById(any()) } returns null

        val result = service.findUser("unknown")

        result.shouldBeNull()
    }
})
```

#### Coroutine Mock

```kotlin
class AsyncUserServiceTest : FunSpec({
    val repository = mockk<UserRepository>()
    val service = UserService(repository)

    test("getUser suspending function") {
        coEvery { repository.findById("1") } returns User(id = "1", name = "Alice")

        val result = service.getUser("1")

        result.name shouldBe "Alice"
        coVerify { repository.findById("1") }
    }

    test("getUser with delay") {
        coEvery { repository.findById("1") } coAnswers {
            delay(100) // Simulate async work
            User(id = "1", name = "Alice")
        }

        val result = service.getUser("1")
        result.name shouldBe "Alice"
    }
})
```

#### 參數捕捉

```kotlin
test("save captures the user argument") {
    val slot = slot<User>()
    coEvery { repository.save(capture(slot)) } returns Unit

    service.createUser(CreateUserRequest("Alice", "alice@example.com"))

    slot.captured.name shouldBe "Alice"
    slot.captured.email shouldBe "alice@example.com"
    slot.captured.id.shouldNotBeNull()
}
```

#### Spy 與部分 Mock

```kotlin
test("spy on real object") {
    val realService = UserService(repository)
    val spy = spyk(realService)

    every { spy.generateId() } returns "fixed-id"

    spy.createUser(request)

    verify { spy.generateId() } // Overridden
    // Other methods use real implementation
}
```

### Coroutine 測試

#### 用 runTest 測 Suspend 函式

```kotlin
import kotlinx.coroutines.test.runTest

class CoroutineServiceTest : FunSpec({
    test("concurrent fetches complete together") {
        runTest {
            val service = DataService(testScope = this)

            val result = service.fetchAllData()

            result.users.shouldNotBeEmpty()
            result.products.shouldNotBeEmpty()
        }
    }

    test("timeout after delay") {
        runTest {
            val service = SlowService()

            shouldThrow<TimeoutCancellationException> {
                withTimeout(100) {
                    service.slowOperation() // Takes > 100ms
                }
            }
        }
    }
})
```

#### 測試 Flow

```kotlin
import io.kotest.matchers.collections.shouldContainInOrder
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runTest

class FlowServiceTest : FunSpec({
    test("observeUsers emits updates") {
        runTest {
            val service = UserFlowService()

            val emissions = service.observeUsers()
                .take(3)
                .toList()

            emissions shouldHaveSize 3
            emissions.last().shouldNotBeEmpty()
        }
    }

    test("searchUsers debounces input") {
        runTest {
            val service = SearchService()
            val queries = MutableSharedFlow<String>()

            val results = mutableListOf<List<User>>()
            val job = launch {
                service.searchUsers(queries).collect { results.add(it) }
            }

            queries.emit("a")
            queries.emit("ab")
            queries.emit("abc") // Only this should trigger search
            advanceTimeBy(500)

            results shouldHaveSize 1
            job.cancel()
        }
    }
})
```

#### TestDispatcher

```kotlin
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle

class DispatcherTest : FunSpec({
    test("uses test dispatcher for controlled execution") {
        val dispatcher = StandardTestDispatcher()

        runTest(dispatcher) {
            var completed = false

            launch {
                delay(1000)
                completed = true
            }

            completed shouldBe false
            advanceTimeBy(1000)
            completed shouldBe true
        }
    }
})
```

### Property-Based Testing

#### Kotest Property Testing

```kotlin
import io.kotest.core.spec.style.FunSpec
import io.kotest.property.Arb
import io.kotest.property.arbitrary.*
import io.kotest.property.forAll
import io.kotest.property.checkAll
import kotlinx.serialization.json.Json
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString

// Note: The serialization roundtrip test below requires the User data class
// to be annotated with @Serializable (from kotlinx.serialization).

class PropertyTest : FunSpec({
    test("string reverse is involutory") {
        forAll<String> { s ->
            s.reversed().reversed() == s
        }
    }

    test("list sort is idempotent") {
        forAll(Arb.list(Arb.int())) { list ->
            list.sorted() == list.sorted().sorted()
        }
    }

    test("serialization roundtrip preserves data") {
        checkAll(Arb.bind(Arb.string(1..50), Arb.string(5..100)) { name, email ->
            User(name = name, email = "$email@test.com")
        }) { user ->
            val json = Json.encodeToString(user)
            val decoded = Json.decodeFromString<User>(json)
            decoded shouldBe user
        }
    }
})
```

#### 自訂 Generator

```kotlin
val userArb: Arb<User> = Arb.bind(
    Arb.string(minSize = 1, maxSize = 50),
    Arb.email(),
    Arb.enum<Role>(),
) { name, email, role ->
    User(
        id = UserId(UUID.randomUUID().toString()),
        name = name,
        email = Email(email),
        role = role,
    )
}

val moneyArb: Arb<Money> = Arb.bind(
    Arb.long(1L..1_000_000L),
    Arb.enum<Currency>(),
) { amount, currency ->
    Money(amount, currency)
}
```

### 資料驅動測試

#### Kotest 的 withData

```kotlin
class ParserTest : FunSpec({
    context("parsing valid dates") {
        withData(
            "2026-01-15" to LocalDate(2026, 1, 15),
            "2026-12-31" to LocalDate(2026, 12, 31),
            "2000-01-01" to LocalDate(2000, 1, 1),
        ) { (input, expected) ->
            parseDate(input) shouldBe expected
        }
    }

    context("rejecting invalid dates") {
        withData(
            nameFn = { "rejects '$it'" },
            "not-a-date",
            "2026-13-01",
            "2026-00-15",
            "",
        ) { input ->
            shouldThrow<DateParseException> {
                parseDate(input)
            }
        }
    }
})
```

### 測試生命週期與 Fixture

#### BeforeTest / AfterTest

```kotlin
class DatabaseTest : FunSpec({
    lateinit var db: Database

    beforeSpec {
        db = Database.connect("jdbc:h2:mem:test;DB_CLOSE_DELAY=-1")
        transaction(db) {
            SchemaUtils.create(UsersTable)
        }
    }

    afterSpec {
        transaction(db) {
            SchemaUtils.drop(UsersTable)
        }
    }

    beforeTest {
        transaction(db) {
            UsersTable.deleteAll()
        }
    }

    test("insert and retrieve user") {
        transaction(db) {
            UsersTable.insert {
                it[name] = "Alice"
                it[email] = "alice@example.com"
            }
        }

        val users = transaction(db) {
            UsersTable.selectAll().map { it[UsersTable.name] }
        }

        users shouldContain "Alice"
    }
})
```

#### Kotest Extension

```kotlin
// Reusable test extension
class DatabaseExtension : BeforeSpecListener, AfterSpecListener {
    lateinit var db: Database

    override suspend fun beforeSpec(spec: Spec) {
        db = Database.connect("jdbc:h2:mem:test;DB_CLOSE_DELAY=-1")
    }

    override suspend fun afterSpec(spec: Spec) {
        // cleanup
    }
}

class UserRepositoryTest : FunSpec({
    val dbExt = DatabaseExtension()
    register(dbExt)

    test("save and find user") {
        val repo = UserRepository(dbExt.db)
        // ...
    }
})
```

### Kover Coverage

#### Gradle 設定

```kotlin
// build.gradle.kts
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.9.7"
}

kover {
    reports {
        total {
            html { onCheck = true }
            xml { onCheck = true }
        }
        filters {
            excludes {
                classes("*.generated.*", "*.config.*")
            }
        }
        verify {
            rule {
                minBound(80) // Fail build below 80% coverage
            }
        }
    }
}
```

#### 覆蓋率指令

```bash
# Run tests with coverage
./gradlew koverHtmlReport

# Verify coverage thresholds
./gradlew koverVerify

# XML report for CI
./gradlew koverXmlReport

# View HTML report (use the command for your OS)
# macOS:   open build/reports/kover/html/index.html
# Linux:   xdg-open build/reports/kover/html/index.html
# Windows: start build/reports/kover/html/index.html
```

#### 覆蓋率目標

| 程式碼類型 | 目標 |
|-----------|--------|
| 關鍵商業邏輯 | 100% |
| 公開 API | 90%+ |
| 一般程式碼 | 80%+ |
| 產生的程式碼 / 設定檔 | 排除 |

### Ktor testApplication Testing

```kotlin
class ApiRoutesTest : FunSpec({
    test("GET /users returns list") {
        testApplication {
            application {
                configureRouting()
                configureSerialization()
            }

            val response = client.get("/users")

            response.status shouldBe HttpStatusCode.OK
            val users = response.body<List<UserResponse>>()
            users.shouldNotBeEmpty()
        }
    }

    test("POST /users creates user") {
        testApplication {
            application {
                configureRouting()
                configureSerialization()
            }

            val response = client.post("/users") {
                contentType(ContentType.Application.Json)
                setBody(CreateUserRequest("Alice", "alice@example.com"))
            }

            response.status shouldBe HttpStatusCode.Created
        }
    }
})
```

### 測試指令

```bash
# Run all tests
./gradlew test

# Run specific test class
./gradlew test --tests "com.example.UserServiceTest"

# Run specific test
./gradlew test --tests "com.example.UserServiceTest.getUser returns user when found"

# Run with verbose output
./gradlew test --info

# Run with coverage
./gradlew koverHtmlReport

# Run detekt (static analysis)
./gradlew detekt

# Run ktlint (formatting check)
./gradlew ktlintCheck

# Continuous testing
./gradlew test --continuous
```

### 最佳實務

**要做：**
- 測試要先寫（TDD）
- 整個專案一致使用 Kotest 的 spec 風格
- suspend 函式用 MockK 的 `coEvery`/`coVerify`
- coroutine 測試用 `runTest`
- 測行為，不要測實作
- 純函式用 property-based testing
- 用 `data class` 當測試 fixture，比較清楚

**不要做：**
- 混用測試框架（選定 Kotest 就一路用下去）
- mock data class（用真實的實例）
- 在 coroutine 測試裡用 `Thread.sleep()`（改用 `advanceTimeBy`）
- 跳過 TDD 的 RED 階段
- 直接測 private 函式
- 忽略不穩定（flaky）的測試

### 整合 CI/CD

```yaml
# GitHub Actions example
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '21'

    - name: Run tests with coverage
      run: ./gradlew test koverXmlReport

    - name: Verify coverage
      run: ./gradlew koverVerify

    - name: Upload coverage
      uses: codecov/codecov-action@v5
      with:
        files: build/reports/kover/report.xml
        token: ${{ secrets.CODECOV_TOKEN }}
```

**記住**：測試就是文件，它們展示你的 Kotlin 程式碼該怎麼用。用 Kotest 有表達力的 matcher 讓測試好讀，用 MockK 乾淨地 mock 依賴。
