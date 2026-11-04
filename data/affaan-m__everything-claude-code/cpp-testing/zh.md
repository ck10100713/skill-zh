---
name: cpp-testing
description: 只在撰寫/更新/修復 C++ 測試、設定 GoogleTest/CTest、診斷失敗或 flaky 的測試，或加入 coverage/sanitizer 時使用。
metadata:
  origin: ECC
---

# C++ 測試（Agent Skill）

以 agent 為中心的現代 C++（C++17/20）測試工作流程，使用 GoogleTest/GoogleMock 搭配 CMake/CTest。

## 何時使用

- 撰寫新的 C++ 測試，或修復既有測試
- 為 C++ 元件設計單元/整合測試的涵蓋範圍
- 加入測試涵蓋率、CI 閘門或回歸保護
- 設定 CMake/CTest 工作流程，讓執行方式一致
- 調查測試失敗或 flaky 的行為
- 開啟 sanitizer 來診斷記憶體/race 問題

### 何時不要用

- 實作新的產品功能，但沒有改到測試
- 跟測試涵蓋率或失敗無關的大規模重構
- 沒有測試回歸可以驗證的效能調校
- 非 C++ 專案，或非測試的任務

## 核心概念

- **TDD 循環**：red → green → refactor（先寫測試，做最小修改，再整理）。
- **隔離**：優先用依賴注入和 fake，不要用全域狀態。
- **測試目錄結構**：`tests/unit`、`tests/integration`、`tests/testdata`。
- **Mock vs fake**：互動用 mock，有狀態的行為用 fake。
- **CTest 探索**：用 `gtest_discover_tests()` 取得穩定的測試探索。
- **CI 訊號**：先跑子集，再用 `--output-on-failure` 跑完整套件。

## TDD 工作流程

照 RED → GREEN → REFACTOR 的循環：

1. **RED**：寫一個會失敗的測試，抓住新的行為
2. **GREEN**：做出能通過的最小改動
3. **REFACTOR**：在測試維持綠燈的狀態下整理

```cpp
// tests/add_test.cpp
#include <gtest/gtest.h>

int Add(int a, int b); // Provided by production code.

TEST(AddTest, AddsTwoNumbers) { // RED
  EXPECT_EQ(Add(2, 3), 5);
}

// src/add.cpp
int Add(int a, int b) { // GREEN
  return a + b;
}

// REFACTOR: simplify/rename once tests pass
```

## 程式碼範例

### 基本單元測試（gtest）

```cpp
// tests/calculator_test.cpp
#include <gtest/gtest.h>

int Add(int a, int b); // Provided by production code.

TEST(CalculatorTest, AddsTwoNumbers) {
    EXPECT_EQ(Add(2, 3), 5);
}
```

### Fixture（gtest）

```cpp
// tests/user_store_test.cpp
// Pseudocode stub: replace UserStore/User with project types.
#include <gtest/gtest.h>
#include <memory>
#include <optional>
#include <string>

struct User { std::string name; };
class UserStore {
public:
    explicit UserStore(std::string /*path*/) {}
    void Seed(std::initializer_list<User> /*users*/) {}
    std::optional<User> Find(const std::string &/*name*/) { return User{"alice"}; }
};

class UserStoreTest : public ::testing::Test {
protected:
    void SetUp() override {
        store = std::make_unique<UserStore>(":memory:");
        store->Seed({{"alice"}, {"bob"}});
    }

    std::unique_ptr<UserStore> store;
};

TEST_F(UserStoreTest, FindsExistingUser) {
    auto user = store->Find("alice");
    ASSERT_TRUE(user.has_value());
    EXPECT_EQ(user->name, "alice");
}
```

### Mock（gmock）

```cpp
// tests/notifier_test.cpp
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <string>

class Notifier {
public:
    virtual ~Notifier() = default;
    virtual void Send(const std::string &message) = 0;
};

class MockNotifier : public Notifier {
public:
    MOCK_METHOD(void, Send, (const std::string &message), (override));
};

class Service {
public:
    explicit Service(Notifier &notifier) : notifier_(notifier) {}
    void Publish(const std::string &message) { notifier_.Send(message); }

private:
    Notifier &notifier_;
};

TEST(ServiceTest, SendsNotifications) {
    MockNotifier notifier;
    Service service(notifier);

    EXPECT_CALL(notifier, Send("hello")).Times(1);
    service.Publish("hello");
}
```

### CMake/CTest 快速上手

```cmake
# CMakeLists.txt (excerpt)
cmake_minimum_required(VERSION 3.20)
project(example LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
# Prefer project-locked versions. If using a tag, use a pinned version per project policy.
set(GTEST_VERSION v1.17.0) # Adjust to project policy.
FetchContent_Declare(
  googletest
  # Google Test framework (official repository)
  URL https://github.com/google/googletest/archive/refs/tags/${GTEST_VERSION}.zip
)
FetchContent_MakeAvailable(googletest)

add_executable(example_tests
  tests/calculator_test.cpp
  src/calculator.cpp
)
target_link_libraries(example_tests GTest::gtest GTest::gmock GTest::gtest_main)

enable_testing()
include(GoogleTest)
gtest_discover_tests(example_tests)
```

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j
ctest --test-dir build --output-on-failure
```

## 執行測試

```bash
ctest --test-dir build --output-on-failure
ctest --test-dir build -R ClampTest
ctest --test-dir build -R "UserStoreTest.*" --output-on-failure
```

```bash
./build/example_tests --gtest_filter=ClampTest.*
./build/example_tests --gtest_filter=UserStoreTest.FindsExistingUser
```

## 除錯失敗的測試

1. 用 gtest filter 單獨重跑那個失敗的測試。
2. 在失敗的 assertion 周圍加上範圍限定的 log。
3. 開啟 sanitizer 再重跑一次。
4. 找到根本原因並修好之後，再擴大到完整套件。

## 涵蓋率

優先用 target 層級的設定，不要用全域 flag。

```cmake
option(ENABLE_COVERAGE "Enable coverage flags" OFF)

if(ENABLE_COVERAGE)
  if(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    target_compile_options(example_tests PRIVATE --coverage)
    target_link_options(example_tests PRIVATE --coverage)
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    target_compile_options(example_tests PRIVATE -fprofile-instr-generate -fcoverage-mapping)
    target_link_options(example_tests PRIVATE -fprofile-instr-generate)
  endif()
endif()
```

GCC + gcov + lcov：

```bash
cmake -S . -B build-cov -DENABLE_COVERAGE=ON
cmake --build build-cov -j
ctest --test-dir build-cov
lcov --capture --directory build-cov --output-file coverage.info
lcov --remove coverage.info '/usr/*' --output-file coverage.info
genhtml coverage.info --output-directory coverage
```

Clang + llvm-cov：

```bash
cmake -S . -B build-llvm -DENABLE_COVERAGE=ON -DCMAKE_CXX_COMPILER=clang++
cmake --build build-llvm -j
LLVM_PROFILE_FILE="build-llvm/default.profraw" ctest --test-dir build-llvm
llvm-profdata merge -sparse build-llvm/default.profraw -o build-llvm/default.profdata
llvm-cov report build-llvm/example_tests -instr-profile=build-llvm/default.profdata
```

## Sanitizer

```cmake
option(ENABLE_ASAN "Enable AddressSanitizer" OFF)
option(ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer" OFF)
option(ENABLE_TSAN "Enable ThreadSanitizer" OFF)

if(ENABLE_ASAN)
  add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
  add_link_options(-fsanitize=address)
endif()
if(ENABLE_UBSAN)
  add_compile_options(-fsanitize=undefined -fno-omit-frame-pointer)
  add_link_options(-fsanitize=undefined)
endif()
if(ENABLE_TSAN)
  add_compile_options(-fsanitize=thread)
  add_link_options(-fsanitize=thread)
endif()
```

## Flaky 測試的護欄

- 絕對不要用 `sleep` 做同步；用 condition variable 或 latch。
- 讓每個測試的暫存目錄都是獨一無二的，而且一定要清掉。
- 單元測試避免依賴真實時間、網路或檔案系統。
- 隨機輸入要用固定的種子，讓結果可重現。

## 最佳實務

### 該做

- 讓測試保持確定性而且彼此隔離
- 優先用依賴注入，不要用全域
- 前置條件用 `ASSERT_*`，多個檢查用 `EXPECT_*`
- 用 CTest 的 label 或目錄把單元測試和整合測試分開
- 在 CI 裡跑 sanitizer 來偵測記憶體和 race 問題

### 不要做

- 單元測試不要依賴真實時間或網路
- 能用 condition variable 的時候，不要用 sleep 做同步
- 不要對簡單的值物件過度 mock
- 對不重要的 log 不要用脆弱的字串比對

### 常見陷阱

- **使用固定的暫存路徑** → 每個測試產生獨一無二的暫存目錄，並且清掉。
- **倚賴實際時鐘時間** → 注入一個 clock，或使用假的時間來源。
- **flaky 的並行測試** → 用 condition variable/latch 和有上限的等待。
- **隱藏的全域狀態** → 在 fixture 裡重設全域狀態，或乾脆移除全域變數。
- **過度 mock** → 有狀態的行為優先用 fake，只對互動用 mock。
- **沒有跑 sanitizer** → 在 CI 加入 ASan/UBSan/TSan 的 build。
- **只在 debug build 上量涵蓋率** → 確保涵蓋率的 target 使用一致的 flag。

## 選用附錄：Fuzzing / Property Testing

只有專案已經支援 LLVM/libFuzzer 或 property-testing 函式庫時才用。

- **libFuzzer**：最適合 I/O 很少的純函式。
- **RapidCheck**：用 property-based 測試來驗證不變式。

最小的 libFuzzer harness（偽碼：把 ParseConfig 換成你的）：

```cpp
#include <cstddef>
#include <cstdint>
#include <string>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string input(reinterpret_cast<const char *>(data), size);
    // ParseConfig(input); // project function
    return 0;
}
```

## GoogleTest 的替代方案

- **Catch2**：header-only，matcher 很有表達力
- **doctest**：輕量，編譯開銷最小
