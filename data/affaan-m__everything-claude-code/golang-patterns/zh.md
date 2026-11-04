---
name: golang-patterns
description: 慣用的 Go 模式、最佳實務與慣例，用來打造穩健、有效率、好維護的 Go 應用程式。寫或 review Go 程式碼，而且對慣用的結構或慣例有疑問時使用。
metadata:
  origin: ECC
---

# Go Development Patterns

慣用的 Go 模式與最佳實務，用來打造穩健、有效率、好維護的應用程式。

## When to Activate

- 寫新的 Go 程式碼
- review Go 程式碼
- 重構既有的 Go 程式碼
- 設計 Go 的 package/module

## Core Principles

### 1. Simplicity and Clarity

Go 重視簡單，不重視耍聰明。程式碼應該一目了然、容易閱讀。

```go
// Good：清楚而直接
func GetUser(id string) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return user, nil
}

// Bad：太過耍聰明
func GetUser(id string) (*User, error) {
    return func() (*User, error) {
        if u, e := db.FindUser(id); e == nil {
            return u, nil
        } else {
            return nil, e
        }
    }()
}
```

### 2. Make the Zero Value Useful

設計型別時，要讓它的 zero value 不用初始化就能直接使用。

```go
// Good：zero value 有用
type Counter struct {
    mu    sync.Mutex
    count int // zero value 是 0，可以直接用
}

func (c *Counter) Inc() {
    c.mu.Lock()
    c.count++
    c.mu.Unlock()
}

// Good：bytes.Buffer 用 zero value 就能運作
var buf bytes.Buffer
buf.WriteString("hello")

// Bad：需要初始化
type BadCounter struct {
    counts map[string]int // nil map 會 panic
}
```

### 3. Accept Interfaces, Return Structs

函式應該接受 interface 參數，並回傳具體型別。

```go
// Good：接受 interface，回傳具體型別
func ProcessData(r io.Reader) (*Result, error) {
    data, err := io.ReadAll(r)
    if err != nil {
        return nil, err
    }
    return &Result{Data: data}, nil
}

// Bad：回傳 interface（無謂地隱藏實作細節）
func ProcessData(r io.Reader) (io.Reader, error) {
    // ...
}
```

## Error Handling Patterns

### Error Wrapping with Context

```go
// Good：用 context 包裝 error
func LoadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("load config %s: %w", path, err)
    }

    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("parse config %s: %w", path, err)
    }

    return &cfg, nil
}
```

### Custom Error Types

```go
// 定義領域專屬的 error
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}

// 常見情況用 sentinel error
var (
    ErrNotFound     = errors.New("resource not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrInvalidInput = errors.New("invalid input")
)
```

### Error Checking with errors.Is and errors.As

```go
func HandleError(err error) {
    // 檢查特定的 error
    if errors.Is(err, sql.ErrNoRows) {
        log.Println("No records found")
        return
    }

    // 檢查 error 的型別
    var validationErr *ValidationError
    if errors.As(err, &validationErr) {
        log.Printf("Validation error on field %s: %s",
            validationErr.Field, validationErr.Message)
        return
    }

    // 未知的 error
    log.Printf("Unexpected error: %v", err)
}
```

### Never Ignore Errors

```go
// Bad：用空白識別字忽略 error
result, _ := doSomething()

// Good：處理它，或明確寫下為什麼可以安全地忽略
result, err := doSomething()
if err != nil {
    return err
}

// 可以接受：error 真的無關緊要時（很少見）
_ = writer.Close() // 盡力清理，error 已在別處記錄
```

## Concurrency Patterns

### Worker Pool

```go
func WorkerPool(jobs <-chan Job, results chan<- Result, numWorkers int) {
    var wg sync.WaitGroup

    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }

    wg.Wait()
    close(results)
}
```

### Context for Cancellation and Timeouts

```go
func FetchWithTimeout(ctx context.Context, url string) ([]byte, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, fmt.Errorf("create request: %w", err)
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, fmt.Errorf("fetch %s: %w", url, err)
    }
    defer resp.Body.Close()

    return io.ReadAll(resp.Body)
}
```

### Graceful Shutdown

```go
func GracefulShutdown(server *http.Server) {
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

    <-quit
    log.Println("Shutting down server...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := server.Shutdown(ctx); err != nil {
        log.Fatalf("Server forced to shutdown: %v", err)
    }

    log.Println("Server exited")
}
```

### errgroup for Coordinated Goroutines

```go
import "golang.org/x/sync/errgroup"

func FetchAll(ctx context.Context, urls []string) ([][]byte, error) {
    g, ctx := errgroup.WithContext(ctx)
    results := make([][]byte, len(urls))

    for i, url := range urls {
        i, url := i, url // 捕捉迴圈變數
        g.Go(func() error {
            data, err := FetchWithTimeout(ctx, url)
            if err != nil {
                return err
            }
            results[i] = data
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }
    return results, nil
}
```

### Avoiding Goroutine Leaks

```go
// Bad：context 被取消時 goroutine 會洩漏
func leakyFetch(ctx context.Context, url string) <-chan []byte {
    ch := make(chan []byte)
    go func() {
        data, _ := fetch(url)
        ch <- data // 沒有接收者就會永遠卡住
    }()
    return ch
}

// Good：正確處理取消
func safeFetch(ctx context.Context, url string) <-chan []byte {
    ch := make(chan []byte, 1) // 有 buffer 的 channel
    go func() {
        data, err := fetch(url)
        if err != nil {
            return
        }
        select {
        case ch <- data:
        case <-ctx.Done():
        }
    }()
    return ch
}
```

## Interface Design

### Small, Focused Interfaces

```go
// Good：單一方法的 interface
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

// 需要時再組合 interface
type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}
```

### Define Interfaces Where They're Used

```go
// 放在使用端的 package，不是提供端
package service

// UserStore 定義這個 service 需要什麼
type UserStore interface {
    GetUser(id string) (*User, error)
    SaveUser(user *User) error
}

type Service struct {
    store UserStore
}

// 具體實作可以放在另一個 package
// 它不需要知道這個 interface 的存在
```

### Optional Behavior with Type Assertions

```go
type Flusher interface {
    Flush() error
}

func WriteAndFlush(w io.Writer, data []byte) error {
    if _, err := w.Write(data); err != nil {
        return err
    }

    // 如果支援就 Flush
    if f, ok := w.(Flusher); ok {
        return f.Flush()
    }
    return nil
}
```

## Package Organization

### Standard Project Layout

```text
myproject/
├── cmd/
│   └── myapp/
│       └── main.go           # 進入點
├── internal/
│   ├── handler/              # HTTP handler
│   ├── service/              # 商業邏輯
│   ├── repository/           # 資料存取
│   └── config/               # 設定
├── pkg/
│   └── client/               # 公開的 API client
├── api/
│   └── v1/                   # API 定義（proto、OpenAPI）
├── testdata/                 # 測試 fixture
├── go.mod
├── go.sum
└── Makefile
```

### Package Naming

```go
// Good：簡短、小寫、沒有底線
package http
package json
package user

// Bad：冗長、大小寫混用，或是多餘
package httpHandler
package json_parser
package userService // 多餘的 'Service' 後綴
```

### Avoid Package-Level State

```go
// Bad：全域的可變狀態
var db *sql.DB

func init() {
    db, _ = sql.Open("postgres", os.Getenv("DATABASE_URL"))
}

// Good：依賴注入
type Server struct {
    db *sql.DB
}

func NewServer(db *sql.DB) *Server {
    return &Server{db: db}
}
```

## Struct Design

### Functional Options Pattern

```go
type Server struct {
    addr    string
    timeout time.Duration
    logger  *log.Logger
}

type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.timeout = d
    }
}

func WithLogger(l *log.Logger) Option {
    return func(s *Server) {
        s.logger = l
    }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{
        addr:    addr,
        timeout: 30 * time.Second, // 預設值
        logger:  log.Default(),    // 預設值
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// 用法
server := NewServer(":8080",
    WithTimeout(60*time.Second),
    WithLogger(customLogger),
)
```

### Embedding for Composition

```go
type Logger struct {
    prefix string
}

func (l *Logger) Log(msg string) {
    fmt.Printf("[%s] %s\n", l.prefix, msg)
}

type Server struct {
    *Logger // 嵌入：Server 會擁有 Log 方法
    addr    string
}

func NewServer(addr string) *Server {
    return &Server{
        Logger: &Logger{prefix: "SERVER"},
        addr:   addr,
    }
}

// 用法
s := NewServer(":8080")
s.Log("Starting...") // 呼叫被嵌入的 Logger.Log
```

## Memory and Performance

### Preallocate Slices When Size is Known

```go
// Bad：slice 會成長很多次
func processItems(items []Item) []Result {
    var results []Result
    for _, item := range items {
        results = append(results, process(item))
    }
    return results
}

// Good：只配置一次
func processItems(items []Item) []Result {
    results := make([]Result, 0, len(items))
    for _, item := range items {
        results = append(results, process(item))
    }
    return results
}
```

### Use sync.Pool for Frequent Allocations

```go
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func ProcessRequest(data []byte) []byte {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufferPool.Put(buf)
    }()

    buf.Write(data)
    // 處理...

    // buf.Bytes() 會別名到池裡的 buffer，而 deferred 的 Put 會把它
    // 交給下一個 Get。回傳前要先複製，否則呼叫端會跟重用產生 race。
    return bytes.Clone(buf.Bytes()) // Go 1.20+；否則用 append([]byte(nil), buf.Bytes()...)
}
```

絕對不要在 `Put` 之後，還回傳或保留池化 buffer 的 `buf.Bytes()`：要先複製，或是讓呼叫端傳入一個 `io.Writer`，這樣就不用複製。

### Avoid String Concatenation in Loops

```go
// Bad：會產生很多字串配置
func join(parts []string) string {
    var result string
    for _, p := range parts {
        result += p + ","
    }
    return result
}

// Good：用 strings.Builder 只配置一次
func join(parts []string) string {
    var sb strings.Builder
    for i, p := range parts {
        if i > 0 {
            sb.WriteString(",")
        }
        sb.WriteString(p)
    }
    return sb.String()
}

// Best：用標準函式庫
func join(parts []string) string {
    return strings.Join(parts, ",")
}
```

## Go Tooling Integration

### Essential Commands

```bash
# Build 和執行
go build ./...
go run ./cmd/myapp

# 測試
go test ./...
go test -race ./...
go test -cover ./...

# 靜態分析
go vet ./...
staticcheck ./...
golangci-lint run

# Module 管理
go mod tidy
go mod verify

# 格式化
gofmt -w .
goimports -w .
```

### Recommended Linter Configuration (.golangci.yml)

```yaml
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gofmt
    - goimports
    - misspell
    - unconvert
    - unparam

linters-settings:
  errcheck:
    check-type-assertions: true
  govet:
    enable:
      - shadow

issues:
  exclude-use-default: false
```

## Quick Reference: Go Idioms

| Idiom | Description |
|-------|-------------|
| Accept interfaces, return structs | 函式接受 interface 參數，回傳具體型別 |
| Errors are values | 把 error 當作一等公民的值，不是例外 |
| Don't communicate by sharing memory | 用 channel 協調 goroutine 之間的工作 |
| Make the zero value useful | 型別不需要明確初始化就能運作 |
| A little copying is better than a little dependency | 避免不必要的外部依賴 |
| Clear is better than clever | 可讀性優先於耍聰明 |
| gofmt is no one's favorite but everyone's friend | 一律用 gofmt/goimports 格式化 |
| Return early | 先處理 error，讓正常路徑不縮排 |

## Anti-Patterns to Avoid

```go
// Bad：長函式裡用 naked return
func process() (result int, err error) {
    // ... 50 行 ...
    return // 到底回傳了什麼？
}

// Bad：用 panic 做流程控制
func GetUser(id string) *User {
    user, err := db.Find(id)
    if err != nil {
        panic(err) // 不要這樣做
    }
    return user
}

// Bad：把 context 放進 struct 傳遞
type Request struct {
    ctx context.Context // Context 應該是第一個參數
    ID  string
}

// Good：Context 當作第一個參數
func ProcessRequest(ctx context.Context, id string) error {
    // ...
}

// Bad：混用 value receiver 和 pointer receiver
type Counter struct{ n int }
func (c Counter) Value() int { return c.n }    // Value receiver
func (c *Counter) Increment() { c.n++ }        // Pointer receiver
// 選一種風格，並保持一致
```

**Remember**：Go 程式碼應該以最好的方式保持無聊：可預測、一致、容易理解。有疑慮的時候，就保持簡單。
