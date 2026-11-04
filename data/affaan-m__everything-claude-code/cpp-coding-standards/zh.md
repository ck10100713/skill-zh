---
name: cpp-coding-standards
description: 以 C++ Core Guidelines（isocpp.github.io）為基礎的 C++ 撰寫規範。在撰寫、審查或重構 C++ 程式碼時使用，確保寫法現代、安全、符合慣用法。
metadata:
  origin: ECC
---

# C++ 撰寫規範（C++ Core Guidelines）

針對現代 C++（C++17/20/23）的完整撰寫規範，來自 [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)。強調型別安全、資源安全、不可變性和清晰度。

## 何時使用

- 撰寫新的 C++ 程式碼（類別、函式、template）
- 審查或重構既有的 C++ 程式碼
- 在 C++ 專案中做架構決策
- 在 C++ codebase 中維持一致的風格
- 在語言功能之間做選擇（例如 `enum` vs `enum class`、raw pointer vs smart pointer）

### 何時不要用

- 非 C++ 專案
- 無法採用現代 C++ 功能的舊 C codebase
- 特定準則和硬體限制衝突的嵌入式/bare-metal 環境（要有選擇地調整）

## 貫穿全文的原則

這些主題在整份準則裡反覆出現，是所有規則的基礎：

1. **到處用 RAII**（P.8、R.1、E.6、CP.20）：把資源的生命週期綁在物件的生命週期上
2. **預設不可變**（P.10、Con.1-5、ES.25）：先從 `const`/`constexpr` 開始；可變是例外
3. **型別安全**（P.4、I.4、ES.46-49、Enum.3）：用型別系統在編譯期就擋掉錯誤
4. **表達意圖**（P.3、F.1、NL.1-2、T.10）：名稱、型別和 concept 都要能傳達目的
5. **把複雜度降到最低**（F.2-3、ES.5、Per.4-5）：簡單的程式碼才是正確的程式碼
6. **值語意優先於指標語意**（C.10、R.3-5、F.20、CP.31）：優先用 by value 回傳和 scoped 物件

## 哲學與介面（P.*、I.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **P.1** | 直接在程式碼裡表達想法 |
| **P.3** | 表達意圖 |
| **P.4** | 理想上，程式應該是靜態型別安全的 |
| **P.5** | 編譯期檢查優先於執行期檢查 |
| **P.8** | 不要洩漏任何資源 |
| **P.10** | 不可變資料優先於可變資料 |
| **I.1** | 讓介面明確 |
| **I.2** | 避免非 const 的全域變數 |
| **I.4** | 讓介面的型別精確且強型別 |
| **I.11** | 絕不透過 raw pointer 或 reference 轉移所有權 |
| **I.23** | 保持函式參數的數量少 |

### 該這樣做

```cpp
// P.10 + I.4: Immutable, strongly typed interface
struct Temperature {
    double kelvin;
};

Temperature boil(const Temperature& water);
```

### 不要這樣做

```cpp
// Weak interface: unclear ownership, unclear units
double boil(double* temp);

// Non-const global variable
int g_counter = 0;  // I.2 violation
```

## 函式（F.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **F.1** | 把有意義的操作包成名稱取得好的函式 |
| **F.2** | 一個函式應該只做一個邏輯操作 |
| **F.3** | 讓函式保持簡短、簡單 |
| **F.4** | 如果函式可能在編譯期求值，就宣告成 `constexpr` |
| **F.6** | 如果你的函式一定不能 throw，就宣告成 `noexcept` |
| **F.8** | 優先用純函式 |
| **F.16** | 「in」參數，便宜複製的型別用 by value 傳，其他用 `const&` |
| **F.20** | 「out」值，優先用回傳值，不要用輸出參數 |
| **F.21** | 要回傳多個「out」值，優先回傳一個 struct |
| **F.43** | 絕不回傳指向區域物件的指標或 reference |

### 參數傳遞

```cpp
// F.16: Cheap types by value, others by const&
void print(int x);                           // cheap: by value
void analyze(const std::string& data);       // expensive: by const&
void transform(std::string s);               // sink: by value (will move)

// F.20 + F.21: Return values, not output parameters
struct ParseResult {
    std::string token;
    int position;
};

ParseResult parse(std::string_view input);   // GOOD: return struct

// BAD: output parameters
void parse(std::string_view input,
           std::string& token, int& pos);    // avoid this
```

### 純函式與 constexpr

```cpp
// F.4 + F.8: Pure, constexpr where possible
constexpr int factorial(int n) noexcept {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

static_assert(factorial(5) == 120);
```

### 反模式

- 函式回傳 `T&&`（F.45）
- 使用 `va_arg` / C 風格的 variadic（F.55）
- 在傳給其他 thread 的 lambda 裡用 reference 捕獲（F.53）
- 回傳 `const T`，這會妨礙 move 語意（F.49）

## 類別與類別階層（C.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **C.2** | 有不變式（invariant）就用 `class`；資料成員各自獨立變動就用 `struct` |
| **C.9** | 盡量減少成員的暴露 |
| **C.20** | 能不定義預設操作就不要定義（Rule of Zero） |
| **C.21** | 只要定義或 `=delete` 了任何 copy/move/解構函式，就要全部處理（Rule of Five） |
| **C.35** | 基底類別的解構函式：public virtual 或 protected non-virtual |
| **C.41** | 建構函式應該建立出完全初始化的物件 |
| **C.46** | 單一參數的建構函式要宣告成 `explicit` |
| **C.67** | 多型類別應該抑制 public 的 copy/move |
| **C.128** | 虛擬函式：`virtual`、`override`、`final` 三選一，只指定一個 |

### Rule of Zero

```cpp
// C.20: Let the compiler generate special members
struct Employee {
    std::string name;
    std::string department;
    int id;
    // No destructor, copy/move constructors, or assignment operators needed
};
```

### Rule of Five

```cpp
// C.21: If you must manage a resource, define all five
class Buffer {
public:
    explicit Buffer(std::size_t size)
        : data_(std::make_unique<char[]>(size)), size_(size) {}

    ~Buffer() = default;

    Buffer(const Buffer& other)
        : data_(std::make_unique<char[]>(other.size_)), size_(other.size_) {
        std::copy_n(other.data_.get(), size_, data_.get());
    }

    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            auto new_data = std::make_unique<char[]>(other.size_);
            std::copy_n(other.data_.get(), other.size_, new_data.get());
            data_ = std::move(new_data);
            size_ = other.size_;
        }
        return *this;
    }

    Buffer(Buffer&&) noexcept = default;
    Buffer& operator=(Buffer&&) noexcept = default;

private:
    std::unique_ptr<char[]> data_;
    std::size_t size_;
};
```

### 類別階層

```cpp
// C.35 + C.128: Virtual destructor, use override
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;  // C.121: pure interface
};

class Circle : public Shape {
public:
    explicit Circle(double r) : radius_(r) {}
    double area() const override { return 3.14159 * radius_ * radius_; }

private:
    double radius_;
};
```

### 反模式

- 在建構函式/解構函式裡呼叫虛擬函式（C.82）
- 對非 trivial 的型別使用 `memset`/`memcpy`（C.90）
- 虛擬函式和覆寫它的函式提供不同的預設引數（C.140）
- 把資料成員宣告成 `const` 或 reference，這會抑制 move/copy（C.12）

## 資源管理（R.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **R.1** | 用 RAII 自動管理資源 |
| **R.3** | raw pointer（`T*`）不擁有資源 |
| **R.5** | 優先用 scoped 物件；不要不必要地在 heap 上配置 |
| **R.10** | 避免 `malloc()`/`free()` |
| **R.11** | 避免明確呼叫 `new` 和 `delete` |
| **R.20** | 用 `unique_ptr` 或 `shared_ptr` 表示所有權 |
| **R.21** | 除非要共享所有權，否則優先用 `unique_ptr` 而不是 `shared_ptr` |
| **R.22** | 用 `make_shared()` 來建立 `shared_ptr` |

### Smart Pointer 的用法

```cpp
// R.11 + R.20 + R.21: RAII with smart pointers
auto widget = std::make_unique<Widget>("config");  // unique ownership
auto cache  = std::make_shared<Cache>(1024);        // shared ownership

// R.3: Raw pointer = non-owning observer
void render(const Widget* w) {  // does NOT own w
    if (w) w->draw();
}

render(widget.get());
```

### RAII 模式

```cpp
// R.1: Resource acquisition is initialization
class FileHandle {
public:
    explicit FileHandle(const std::string& path)
        : handle_(std::fopen(path.c_str(), "r")) {
        if (!handle_) throw std::runtime_error("Failed to open: " + path);
    }

    ~FileHandle() {
        if (handle_) std::fclose(handle_);
    }

    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& other) noexcept
        : handle_(std::exchange(other.handle_, nullptr)) {}
    FileHandle& operator=(FileHandle&& other) noexcept {
        if (this != &other) {
            if (handle_) std::fclose(handle_);
            handle_ = std::exchange(other.handle_, nullptr);
        }
        return *this;
    }

private:
    std::FILE* handle_;
};
```

### 反模式

- 裸的 `new`/`delete`（R.11）
- 在 C++ 程式碼裡用 `malloc()`/`free()`（R.10）
- 在單一運算式裡做多個資源配置（R.13，有 exception safety 的風險）
- 用 `unique_ptr` 就夠的地方卻用 `shared_ptr`（R.21）

## 運算式與陳述式（ES.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **ES.5** | 讓作用域保持小 |
| **ES.20** | 物件一律要初始化 |
| **ES.23** | 優先用 `{}` 初始化語法 |
| **ES.25** | 除非打算修改，否則把物件宣告成 `const` 或 `constexpr` |
| **ES.28** | 對 `const` 變數的複雜初始化，用 lambda |
| **ES.45** | 避免 magic constant；用有名字的常數 |
| **ES.46** | 避免窄化/有損的算術轉換 |
| **ES.47** | 用 `nullptr`，不要用 `0` 或 `NULL` |
| **ES.48** | 避免轉型 |
| **ES.50** | 不要把 `const` 轉掉 |

### 初始化

```cpp
// ES.20 + ES.23 + ES.25: Always initialize, prefer {}, default to const
const int max_retries{3};
const std::string name{"widget"};
const std::vector<int> primes{2, 3, 5, 7, 11};

// ES.28: Lambda for complex const initialization
const auto config = [&] {
    Config c;
    c.timeout = std::chrono::seconds{30};
    c.retries = max_retries;
    c.verbose = debug_mode;
    return c;
}();
```

### 反模式

- 沒初始化的變數（ES.20）
- 用 `0` 或 `NULL` 當指標（ES.47，要用 `nullptr`）
- C 風格轉型（ES.48，要用 `static_cast`、`const_cast` 等）
- 把 `const` 轉掉（ES.50）
- 沒有命名常數的 magic number（ES.45）
- 混用有號和無號的算術（ES.100）
- 在巢狀作用域裡重複使用名稱（ES.12）

## 錯誤處理（E.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **E.1** | 在設計初期就制定錯誤處理策略 |
| **E.2** | 用 throw exception 來表示函式無法完成它被指派的任務 |
| **E.6** | 用 RAII 防止洩漏 |
| **E.12** | 當 throw 不可能或不可接受時，用 `noexcept` |
| **E.14** | 用專門設計的自訂型別當 exception |
| **E.15** | by value 丟出，by reference 接住 |
| **E.16** | 解構函式、釋放操作和 swap 絕不能失敗 |
| **E.17** | 不要試圖在每個函式裡接住所有 exception |

### Exception 階層

```cpp
// E.14 + E.15: Custom exception types, throw by value, catch by reference
class AppError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class NetworkError : public AppError {
public:
    NetworkError(const std::string& msg, int code)
        : AppError(msg), status_code(code) {}
    int status_code;
};

void fetch_data(const std::string& url) {
    // E.2: Throw to signal failure
    throw NetworkError("connection refused", 503);
}

void run() {
    try {
        fetch_data("https://api.example.com");
    } catch (const NetworkError& e) {
        log_error(e.what(), e.status_code);
    } catch (const AppError& e) {
        log_error(e.what());
    }
    // E.17: Don't catch everything here -- let unexpected errors propagate
}
```

### 反模式

- 丟出 `int` 或字串字面值這類內建型別（E.14）
- by value 接住（有 slicing 的風險）（E.15）
- 默默吞掉錯誤的空 catch 區塊
- 把 exception 拿來控制流程（E.3）
- 依賴 `errno` 這類全域狀態的錯誤處理（E.28）

## 常數與不可變性（Con.*）

### 全部規則

| 規則 | 摘要 |
|------|---------|
| **Con.1** | 預設讓物件不可變 |
| **Con.2** | 預設讓成員函式是 `const` |
| **Con.3** | 預設把指標和 reference 傳成指向 `const` |
| **Con.4** | 建構之後就不會變的值要用 `const` |
| **Con.5** | 編譯期就能算出來的值要用 `constexpr` |

```cpp
// Con.1 through Con.5: Immutability by default
class Sensor {
public:
    explicit Sensor(std::string id) : id_(std::move(id)) {}

    // Con.2: const member functions by default
    const std::string& id() const { return id_; }
    double last_reading() const { return reading_; }

    // Only non-const when mutation is required
    void record(double value) { reading_ = value; }

private:
    const std::string id_;  // Con.4: never changes after construction
    double reading_{0.0};
};

// Con.3: Pass by const reference
void display(const Sensor& s) {
    std::cout << s.id() << ": " << s.last_reading() << '\n';
}

// Con.5: Compile-time constants
constexpr double PI = 3.14159265358979;
constexpr int MAX_SENSORS = 256;
```

## 並行與平行（CP.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **CP.2** | 避免 data race |
| **CP.3** | 盡量減少可寫資料的明確共享 |
| **CP.4** | 用 task 的角度思考，不要用 thread |
| **CP.8** | 不要用 `volatile` 做同步 |
| **CP.20** | 用 RAII，絕不直接用 `lock()`/`unlock()` |
| **CP.21** | 要取得多個 mutex 時，用 `std::scoped_lock` |
| **CP.22** | 持有 lock 時，絕不呼叫未知的程式碼 |
| **CP.42** | 不要不帶條件就 wait |
| **CP.44** | 記得替你的 `lock_guard` 和 `unique_lock` 取名字 |
| **CP.100** | 除非萬不得已，不要用 lock-free 程式設計 |

### 安全的上鎖

```cpp
// CP.20 + CP.44: RAII locks, always named
class ThreadSafeQueue {
public:
    void push(int value) {
        std::lock_guard<std::mutex> lock(mutex_);  // CP.44: named!
        queue_.push(value);
        cv_.notify_one();
    }

    int pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        // CP.42: Always wait with a condition
        cv_.wait(lock, [this] { return !queue_.empty(); });
        const int value = queue_.front();
        queue_.pop();
        return value;
    }

private:
    std::mutex mutex_;             // CP.50: mutex with its data
    std::condition_variable cv_;
    std::queue<int> queue_;
};
```

### 多個 Mutex

```cpp
// CP.21: std::scoped_lock for multiple mutexes (deadlock-free)
void transfer(Account& from, Account& to, double amount) {
    std::scoped_lock lock(from.mutex_, to.mutex_);
    from.balance_ -= amount;
    to.balance_ += amount;
}
```

### 反模式

- 用 `volatile` 做同步（CP.8，它只用在硬體 I/O）
- detach thread（CP.26，生命週期幾乎沒辦法管理）
- 沒命名的 lock guard：`std::lock_guard<std::mutex>(m);` 會立刻被銷毀（CP.44）
- 持有 lock 的同時呼叫 callback（CP.22，有 deadlock 的風險）
- 沒有深厚專業知識就用 lock-free 程式設計（CP.100）

## Template 與泛型程式設計（T.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **T.1** | 用 template 來提高抽象層次 |
| **T.2** | 用 template 來表達適用於多種引數型別的演算法 |
| **T.10** | 為所有 template 引數指定 concept |
| **T.11** | 盡可能使用標準的 concept |
| **T.13** | 簡單的 concept 優先用簡寫語法 |
| **T.43** | 優先用 `using`，不要用 `typedef` |
| **T.120** | 只有真的需要時才用 template metaprogramming |
| **T.144** | 不要特化函式 template（改用 overload） |

### Concepts（C++20）

```cpp
#include <concepts>

// T.10 + T.11: Constrain templates with standard concepts
template<std::integral T>
T gcd(T a, T b) {
    while (b != 0) {
        a = std::exchange(b, a % b);
    }
    return a;
}

// T.13: Shorthand concept syntax
void sort(std::ranges::random_access_range auto& range) {
    std::ranges::sort(range);
}

// Custom concept for domain-specific constraints
template<typename T>
concept Serializable = requires(const T& t) {
    { t.serialize() } -> std::convertible_to<std::string>;
};

template<Serializable T>
void save(const T& obj, const std::string& path);
```

### 反模式

- 在看得到的 namespace 裡放沒有約束的 template（T.47）
- 特化函式 template，而不是用 overload（T.144）
- `constexpr` 就夠的地方卻用 template metaprogramming（T.120）
- 用 `typedef` 而不是 `using`（T.43）

## 標準函式庫（SL.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **SL.1** | 盡可能使用函式庫 |
| **SL.2** | 標準函式庫優先於其他函式庫 |
| **SL.con.1** | `std::array` 或 `std::vector` 優先於 C 陣列 |
| **SL.con.2** | 預設優先用 `std::vector` |
| **SL.str.1** | 用 `std::string` 來擁有字元序列 |
| **SL.str.2** | 用 `std::string_view` 來參照字元序列 |
| **SL.io.50** | 避免 `endl`（用 `'\n'`，`endl` 會強制 flush） |

```cpp
// SL.con.1 + SL.con.2: Prefer vector/array over C arrays
const std::array<int, 4> fixed_data{1, 2, 3, 4};
std::vector<std::string> dynamic_data;

// SL.str.1 + SL.str.2: string owns, string_view observes
std::string build_greeting(std::string_view name) {
    return "Hello, " + std::string(name) + "!";
}

// SL.io.50: Use '\n' not endl
std::cout << "result: " << value << '\n';
```

## 列舉（Enum.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **Enum.1** | 列舉優先於巨集 |
| **Enum.3** | `enum class` 優先於一般的 `enum` |
| **Enum.5** | enumerator 不要用全大寫 |
| **Enum.6** | 避免沒有名字的列舉 |

```cpp
// Enum.3 + Enum.5: Scoped enum, no ALL_CAPS
enum class Color { red, green, blue };
enum class LogLevel { debug, info, warning, error };

// BAD: plain enum leaks names, ALL_CAPS clashes with macros
enum { RED, GREEN, BLUE };           // Enum.3 + Enum.5 + Enum.6 violation
#define MAX_SIZE 100                  // Enum.1 violation -- use constexpr
```

## 原始檔與命名（SF.*、NL.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **SF.1** | 程式碼檔用 `.cpp`，介面檔用 `.h` |
| **SF.7** | 不要在 header 的全域作用域寫 `using namespace` |
| **SF.8** | 所有 `.h` 檔都要有 `#include` guard |
| **SF.11** | header 檔應該是自足的（self-contained） |
| **NL.5** | 避免把型別資訊編進名稱（不要用匈牙利命名法） |
| **NL.8** | 使用一致的命名風格 |
| **NL.9** | 只有巨集名稱用全大寫 |
| **NL.10** | 優先用 `underscore_style` 的名稱 |

### Header Guard

```cpp
// SF.8: Include guard (or #pragma once)
#ifndef PROJECT_MODULE_WIDGET_H
#define PROJECT_MODULE_WIDGET_H

// SF.11: Self-contained -- include everything this header needs
#include <string>
#include <vector>

namespace project::module {

class Widget {
public:
    explicit Widget(std::string name);
    const std::string& name() const;

private:
    std::string name_;
};

}  // namespace project::module

#endif  // PROJECT_MODULE_WIDGET_H
```

### 命名慣例

```cpp
// NL.8 + NL.10: Consistent underscore_style
namespace my_project {

constexpr int max_buffer_size = 4096;  // NL.9: not ALL_CAPS (it's not a macro)

class tcp_connection {                 // underscore_style class
public:
    void send_message(std::string_view msg);
    bool is_connected() const;

private:
    std::string host_;                 // trailing underscore for members
    int port_;
};

}  // namespace my_project
```

### 反模式

- 在 header 的全域作用域寫 `using namespace std;`（SF.7）
- 依賴 include 順序的 header（SF.10、SF.11）
- `strName`、`iCount` 這類匈牙利命名法（NL.5）
- 巨集以外的東西用全大寫（NL.9）

## 效能（Per.*）

### 關鍵規則

| 規則 | 摘要 |
|------|---------|
| **Per.1** | 沒有理由就不要最佳化 |
| **Per.2** | 不要過早最佳化 |
| **Per.6** | 沒有量測就不要對效能下斷言 |
| **Per.7** | 設計時要保留最佳化的空間 |
| **Per.10** | 倚賴靜態型別系統 |
| **Per.11** | 把運算從執行期搬到編譯期 |
| **Per.19** | 以可預測的方式存取記憶體 |

### 準則

```cpp
// Per.11: Compile-time computation where possible
constexpr auto lookup_table = [] {
    std::array<int, 256> table{};
    for (int i = 0; i < 256; ++i) {
        table[i] = i * i;
    }
    return table;
}();

// Per.19: Prefer contiguous data for cache-friendliness
std::vector<Point> points;           // GOOD: contiguous
std::vector<std::unique_ptr<Point>> indirect_points; // BAD: pointer chasing
```

### 反模式

- 沒有 profiling 資料就最佳化（Per.1、Per.6）
- 選了「很聰明」的低階程式碼，而不是清楚的抽象（Per.4、Per.5）
- 忽略資料配置和 cache 行為（Per.19）

## 快速參考檢查清單

標記 C++ 工作完成之前：

- [ ] 沒有 raw `new`/`delete`，用 smart pointer 或 RAII（R.11）
- [ ] 物件在宣告時就初始化（ES.20）
- [ ] 變數預設是 `const`/`constexpr`（Con.1、ES.25）
- [ ] 成員函式盡可能是 `const`（Con.2）
- [ ] 用 `enum class`，不用一般的 `enum`（Enum.3）
- [ ] 用 `nullptr`，不用 `0`/`NULL`（ES.47）
- [ ] 沒有窄化轉換（ES.46）
- [ ] 沒有 C 風格轉型（ES.48）
- [ ] 單一參數的建構函式是 `explicit`（C.46）
- [ ] 套用了 Rule of Zero 或 Rule of Five（C.20、C.21）
- [ ] 基底類別的解構函式是 public virtual 或 protected non-virtual（C.35）
- [ ] template 用 concept 做了約束（T.10）
- [ ] header 的全域作用域沒有 `using namespace`（SF.7）
- [ ] header 有 include guard 而且是自足的（SF.8、SF.11）
- [ ] lock 使用 RAII（`scoped_lock`/`lock_guard`）（CP.20）
- [ ] exception 是自訂型別，by value 丟出，by reference 接住（E.14、E.15）
- [ ] 用 `'\n'`，不用 `std::endl`（SL.io.50）
- [ ] 沒有 magic number（ES.45）
