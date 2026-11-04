---
name: golang-testing
description: Go 的測試模式，包含 table-driven 測試、subtest、benchmark、fuzzing 和測試覆蓋率。依循 TDD 方法論與慣用的 Go 做法。寫 Go 測試時使用：table-driven 案例、subtest、benchmark、fuzzing 或覆蓋率。
metadata:
  origin: ECC
---

# Go Testing Patterns

依循 TDD 方法論，寫出可靠、好維護的測試，這是完整的 Go 測試模式。

## When to Activate

- 寫新的 Go 函式或方法
- 為既有的程式碼補測試覆蓋率
- 為效能關鍵的程式碼建立 benchmark
- 為輸入驗證實作 fuzz 測試
- 在 Go 專案中遵循 TDD 工作流程

## TDD Workflow for Go

### The RED-GREEN-REFACTOR Cycle

```
RED     → Write a failing test first
GREEN   → Write minimal code to pass the test
REFACTOR → Improve code while keeping tests green
REPEAT  → Continue with next requirement
```

### Step-by-Step TDD in Go

```go
// Step 1：定義 interface/簽章
// calculator.go
package calculator

func Add(a, b int) int {
    panic("not implemented") // 佔位用
}

// Step 2：寫會失敗的測試（RED）
// calculator_test.go
package calculator

import "testing"

func TestAdd(t *testing.T) {
    got := Add(2, 3)
    want := 5
    if got != want {
        t.Errorf("Add(2, 3) = %d; want %d", got, want)
    }
}

// Step 3：跑測試，確認 FAIL
// $ go test
// --- FAIL: TestAdd (0.00s)
// panic: not implemented

// Step 4：實作最少的程式碼（GREEN）
func Add(a, b int) int {
    return a + b
}

// Step 5：跑測試，確認 PASS
// $ go test
// PASS

// Step 6：需要的話重構，並確認測試仍然通過
```

## Table-Driven Tests

Go 測試的標準模式。用最少的程式碼就能達到完整的覆蓋。

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -1, -2, -3},
        {"zero values", 0, 0, 0},
        {"mixed signs", -1, 1, 0},
        {"large numbers", 1000000, 2000000, 3000000},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d",
                    tt.a, tt.b, got, tt.expected)
            }
        })
    }
}
```

### Table-Driven Tests with Error Cases

```go
func TestParseConfig(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    *Config
        wantErr bool
    }{
        {
            name:  "valid config",
            input: `{"host": "localhost", "port": 8080}`,
            want:  &Config{Host: "localhost", Port: 8080},
        },
        {
            name:    "invalid JSON",
            input:   `{invalid}`,
            wantErr: true,
        },
        {
            name:    "empty input",
            input:   "",
            wantErr: true,
        },
        {
            name:  "minimal config",
            input: `{}`,
            want:  &Config{}, // zero value 的 config
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ParseConfig(tt.input)

            if tt.wantErr {
                if err == nil {
                    t.Error("expected error, got nil")
                }
                return
            }

            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }

            if !reflect.DeepEqual(got, tt.want) {
                t.Errorf("got %+v; want %+v", got, tt.want)
            }
        })
    }
}
```

## Subtests and Sub-benchmarks

### Organizing Related Tests

```go
func TestUser(t *testing.T) {
    // 所有 subtest 共用的 setup
    db := setupTestDB(t)

    t.Run("Create", func(t *testing.T) {
        user := &User{Name: "Alice"}
        err := db.CreateUser(user)
        if err != nil {
            t.Fatalf("CreateUser failed: %v", err)
        }
        if user.ID == "" {
            t.Error("expected user ID to be set")
        }
    })

    t.Run("Get", func(t *testing.T) {
        user, err := db.GetUser("alice-id")
        if err != nil {
            t.Fatalf("GetUser failed: %v", err)
        }
        if user.Name != "Alice" {
            t.Errorf("got name %q; want %q", user.Name, "Alice")
        }
    })

    t.Run("Update", func(t *testing.T) {
        // ...
    })

    t.Run("Delete", func(t *testing.T) {
        // ...
    })
}
```

### Parallel Subtests

```go
func TestParallel(t *testing.T) {
    tests := []struct {
        name  string
        input string
    }{
        {"case1", "input1"},
        {"case2", "input2"},
        {"case3", "input3"},
    }

    for _, tt := range tests {
        tt := tt // 捕捉 range 變數
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel() // 讓 subtest 平行執行
            result := Process(tt.input)
            // 斷言...
            _ = result
        })
    }
}
```

## Test Helpers

### Helper Functions

```go
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper() // 標記這是 helper 函式

    db, err := sql.Open("sqlite3", ":memory:")
    if err != nil {
        t.Fatalf("failed to open database: %v", err)
    }

    // 測試結束時清理
    t.Cleanup(func() {
        db.Close()
    })

    // 執行 migration
    if _, err := db.Exec(schema); err != nil {
        t.Fatalf("failed to create schema: %v", err)
    }

    return db
}

func assertNoError(t *testing.T, err error) {
    t.Helper()
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}

func assertEqual[T comparable](t *testing.T, got, want T) {
    t.Helper()
    if got != want {
        t.Errorf("got %v; want %v", got, want)
    }
}
```

### Temporary Files and Directories

```go
func TestFileProcessing(t *testing.T) {
    // 建立暫存目錄，會自動清理
    tmpDir := t.TempDir()

    // 建立測試檔
    testFile := filepath.Join(tmpDir, "test.txt")
    err := os.WriteFile(testFile, []byte("test content"), 0644)
    if err != nil {
        t.Fatalf("failed to create test file: %v", err)
    }

    // 執行測試
    result, err := ProcessFile(testFile)
    if err != nil {
        t.Fatalf("ProcessFile failed: %v", err)
    }

    // 斷言...
    _ = result
}
```

## Golden Files

拿存在 `testdata/` 裡的預期輸出檔來做測試比對。

```go
var update = flag.Bool("update", false, "update golden files")

func TestRender(t *testing.T) {
    tests := []struct {
        name  string
        input Template
    }{
        {"simple", Template{Name: "test"}},
        {"complex", Template{Name: "test", Items: []string{"a", "b"}}},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Render(tt.input)

            golden := filepath.Join("testdata", tt.name+".golden")

            if *update {
                // 更新 golden 檔：go test -update
                err := os.WriteFile(golden, got, 0644)
                if err != nil {
                    t.Fatalf("failed to update golden file: %v", err)
                }
            }

            want, err := os.ReadFile(golden)
            if err != nil {
                t.Fatalf("failed to read golden file: %v", err)
            }

            if !bytes.Equal(got, want) {
                t.Errorf("output mismatch:\ngot:\n%s\nwant:\n%s", got, want)
            }
        })
    }
}
```

## Mocking with Interfaces

### Interface-Based Mocking

```go
// 為依賴定義 interface
type UserRepository interface {
    GetUser(id string) (*User, error)
    SaveUser(user *User) error
}

// Production 的實作
type PostgresUserRepository struct {
    db *sql.DB
}

func (r *PostgresUserRepository) GetUser(id string) (*User, error) {
    // 真實的資料庫查詢
}

// 測試用的 mock 實作
type MockUserRepository struct {
    GetUserFunc  func(id string) (*User, error)
    SaveUserFunc func(user *User) error
}

func (m *MockUserRepository) GetUser(id string) (*User, error) {
    return m.GetUserFunc(id)
}

func (m *MockUserRepository) SaveUser(user *User) error {
    return m.SaveUserFunc(user)
}

// 使用 mock 的測試
func TestUserService(t *testing.T) {
    mock := &MockUserRepository{
        GetUserFunc: func(id string) (*User, error) {
            if id == "123" {
                return &User{ID: "123", Name: "Alice"}, nil
            }
            return nil, ErrNotFound
        },
    }

    service := NewUserService(mock)

    user, err := service.GetUserProfile("123")
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if user.Name != "Alice" {
        t.Errorf("got name %q; want %q", user.Name, "Alice")
    }
}
```

## Benchmarks

### Basic Benchmarks

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData(1000)
    b.ResetTimer() // 不把 setup 的時間算進去

    for i := 0; i < b.N; i++ {
        Process(data)
    }
}

// 執行：go test -bench=BenchmarkProcess -benchmem
// 輸出：BenchmarkProcess-8   10000   105234 ns/op   4096 B/op   10 allocs/op
```

### Benchmark with Different Sizes

```go
func BenchmarkSort(b *testing.B) {
    sizes := []int{100, 1000, 10000, 100000}

    for _, size := range sizes {
        b.Run(fmt.Sprintf("size=%d", size), func(b *testing.B) {
            data := generateRandomSlice(size)
            b.ResetTimer()

            for i := 0; i < b.N; i++ {
                // 複製一份，避免去排序已經排好的資料
                tmp := make([]int, len(data))
                copy(tmp, data)
                sort.Ints(tmp)
            }
        })
    }
}
```

### Memory Allocation Benchmarks

```go
func BenchmarkStringConcat(b *testing.B) {
    parts := []string{"hello", "world", "foo", "bar", "baz"}

    b.Run("plus", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            var s string
            for _, p := range parts {
                s += p
            }
            _ = s
        }
    })

    b.Run("builder", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            var sb strings.Builder
            for _, p := range parts {
                sb.WriteString(p)
            }
            _ = sb.String()
        }
    })

    b.Run("join", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            _ = strings.Join(parts, "")
        }
    })
}
```

## Fuzzing (Go 1.18+)

### Basic Fuzz Test

```go
func FuzzParseJSON(f *testing.F) {
    // 加入種子 corpus
    f.Add(`{"name": "test"}`)
    f.Add(`{"count": 123}`)
    f.Add(`[]`)
    f.Add(`""`)

    f.Fuzz(func(t *testing.T, input string) {
        var result map[string]interface{}
        err := json.Unmarshal([]byte(input), &result)

        if err != nil {
            // 隨機輸入出現無效的 JSON 是預期中的事
            return
        }

        // 如果解析成功，重新編碼也應該要成功
        _, err = json.Marshal(result)
        if err != nil {
            t.Errorf("Marshal failed after successful Unmarshal: %v", err)
        }
    })
}

// 執行：go test -fuzz=FuzzParseJSON -fuzztime=30s
```

### Fuzz Test with Multiple Inputs

```go
func FuzzCompare(f *testing.F) {
    f.Add("hello", "world")
    f.Add("", "")
    f.Add("abc", "abc")

    f.Fuzz(func(t *testing.T, a, b string) {
        result := Compare(a, b)

        // 性質：Compare(a, a) 永遠應該等於 0
        if a == b && result != 0 {
            t.Errorf("Compare(%q, %q) = %d; want 0", a, b, result)
        }

        // 性質：Compare(a, b) 和 Compare(b, a) 的正負號應該相反
        reverse := Compare(b, a)
        if (result > 0 && reverse >= 0) || (result < 0 && reverse <= 0) {
            if result != 0 || reverse != 0 {
                t.Errorf("Compare(%q, %q) = %d, Compare(%q, %q) = %d; inconsistent",
                    a, b, result, b, a, reverse)
            }
        }
    })
}
```

## Test Coverage

### Running Coverage

```bash
# 基本覆蓋率
go test -cover ./...

# 產生覆蓋率 profile
go test -coverprofile=coverage.out ./...

# 在瀏覽器查看覆蓋率
go tool cover -html=coverage.out

# 依函式查看覆蓋率
go tool cover -func=coverage.out

# 搭配 race 偵測的覆蓋率
go test -race -coverprofile=coverage.out ./...
```

### Coverage Targets

| Code Type | Target |
|-----------|--------|
| 關鍵的商業邏輯 | 100% |
| 公開的 API | 90%+ |
| 一般程式碼 | 80%+ |
| 產生出來的程式碼 | 排除 |

### Excluding Generated Code from Coverage

```go
//go:generate mockgen -source=interface.go -destination=mock_interface.go

// 在覆蓋率 profile 裡，用 build tag 排除：
// go test -cover -tags=!generate ./...
```

## HTTP Handler Testing

```go
func TestHealthHandler(t *testing.T) {
    // 建立 request
    req := httptest.NewRequest(http.MethodGet, "/health", nil)
    w := httptest.NewRecorder()

    // 呼叫 handler
    HealthHandler(w, req)

    // 檢查 response
    resp := w.Result()
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        t.Errorf("got status %d; want %d", resp.StatusCode, http.StatusOK)
    }

    body, _ := io.ReadAll(resp.Body)
    if string(body) != "OK" {
        t.Errorf("got body %q; want %q", body, "OK")
    }
}

func TestAPIHandler(t *testing.T) {
    tests := []struct {
        name       string
        method     string
        path       string
        body       string
        wantStatus int
        wantBody   string
    }{
        {
            name:       "get user",
            method:     http.MethodGet,
            path:       "/users/123",
            wantStatus: http.StatusOK,
            wantBody:   `{"id":"123","name":"Alice"}`,
        },
        {
            name:       "not found",
            method:     http.MethodGet,
            path:       "/users/999",
            wantStatus: http.StatusNotFound,
        },
        {
            name:       "create user",
            method:     http.MethodPost,
            path:       "/users",
            body:       `{"name":"Bob"}`,
            wantStatus: http.StatusCreated,
        },
    }

    handler := NewAPIHandler()

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            var body io.Reader
            if tt.body != "" {
                body = strings.NewReader(tt.body)
            }

            req := httptest.NewRequest(tt.method, tt.path, body)
            req.Header.Set("Content-Type", "application/json")
            w := httptest.NewRecorder()

            handler.ServeHTTP(w, req)

            if w.Code != tt.wantStatus {
                t.Errorf("got status %d; want %d", w.Code, tt.wantStatus)
            }

            if tt.wantBody != "" && w.Body.String() != tt.wantBody {
                t.Errorf("got body %q; want %q", w.Body.String(), tt.wantBody)
            }
        })
    }
}
```

## Testing Commands

```bash
# 跑所有測試
go test ./...

# 跑測試並顯示詳細輸出
go test -v ./...

# 跑特定測試
go test -run TestAdd ./...

# 跑符合 pattern 的測試
go test -run "TestUser/Create" ./...

# 搭配 race detector 跑測試
go test -race ./...

# 搭配覆蓋率跑測試
go test -cover -coverprofile=coverage.out ./...

# 只跑短測試
go test -short ./...

# 設定 timeout 跑測試
go test -timeout 30s ./...

# 跑 benchmark
go test -bench=. -benchmem ./...

# 跑 fuzzing
go test -fuzz=FuzzParse -fuzztime=30s ./...

# 計算測試執行次數（用來偵測 flaky 測試）
go test -count=10 ./...
```

## Best Practices

**該做的（DO）：**
- 先寫測試（TDD）
- 用 table-driven 測試達到完整的覆蓋
- 測行為，不要測實作
- 在 helper 函式裡用 `t.Helper()`
- 對彼此獨立的測試用 `t.Parallel()`
- 用 `t.Cleanup()` 清理資源
- 用能描述情境的、有意義的測試名稱

**不該做的（DON'T）：**
- 直接測私有函式（要透過公開 API 測）
- 在測試裡用 `time.Sleep()`（改用 channel 或條件）
- 忽略 flaky 測試（修好它，或移除它）
- 什麼都 mock（可以的話優先用整合測試）
- 跳過錯誤路徑的測試

## Integration with CI/CD

```yaml
# GitHub Actions 範例
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-go@v5
      with:
        go-version: '1.22'

    - name: Run tests
      run: go test -race -coverprofile=coverage.out ./...

    - name: Check coverage
      run: |
        go tool cover -func=coverage.out | grep total | awk '{print $3}' | \
        awk -F'%' '{if ($1 < 80) exit 1}'
```

**Remember**：測試就是文件。它們示範你的程式碼該怎麼使用。要寫得清楚，並且隨時保持最新。
