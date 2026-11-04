---
name: tinystruct-patterns
description: 用 tinystruct Java 框架開發的專家指引。在 tinystruct 程式碼庫，或任何建立在 tinystruct 之上的專案裡工作時使用，包括：專案缺少 bin/dispatcher 和 bin/dispatcher.cmd 啟動腳本時產生它們、建立 Application 類別、@Action 對應的路由、單元測試、ActionRegistry、HTTP/CLI 雙模式處理、內建 HTTP 伺服器、事件系統、用 Builder/Builders 處理 JSON、用 AbstractData 做資料庫持久化、POJO 產生、Server-Sent Events (SSE)、檔案上傳，以及對外的 HTTP 網路請求。
metadata:
  origin: ECC
  upstream: tinystruct==1.7.37
---

# tinystruct 開發模式

用 **tinystruct** Java 框架建構模組的架構與實作模式。它是輕量、高效能的框架，把 CLI 和 HTTP 當成同等公民，不需要 `main()` 方法，設定也很少。

## 核心原則

**CLI 和 HTTP 是同等公民。** 與傳輸方式無關的 `@Action` 使用 `Mode.DEFAULT`（或省略 `mode`），而且沒有只限 HTTP 的相依。這樣的 action 可以在終端機和網頁瀏覽器兩邊都跑。`Mode.DEFAULT` 只是拿掉傳輸方式的限制；它不會讓依賴 HTTP 的方法變成相容 CLI。`Request` 和 `Response` 參數來自 HTTP context 的屬性，沒有這些屬性時（例如一般的 CLI 呼叫）它們會是 null。要讓共用的邏輯不依賴 HTTP 物件、session 和上傳，需要時再從各傳輸專屬的進入點去呼叫它。這種「雙模式」能力是 tinystruct 的核心設計哲學。帶有傳輸專屬 mode（`Mode.CLI`、`Mode.HTTP_GET`、`Mode.HTTP_POST`……）的 action，是刻意綁在那個傳輸上的：框架會從另一邊拒絕它，並回報 "The action is not allowed to be executed."

## 主要開發工具：`bin/dispatcher`

**`bin/dispatcher` 是開發、執行、測試和除錯 tinystruct 應用程式的預設、最高優先順序工具，要先用它，再考慮 IDE 的執行設定、手寫的 `main()`、curl 或瀏覽器。** 因為與傳輸方式無關的 `@Action` 方法在設計上就是雙模式，`bin/dispatcher` 讓你直接從終端機驗證路由、引數綁定和業務邏輯，回饋迴圈最快，也不用開伺服器或瀏覽器。綁在 HTTP 方法上的 action（`Mode.HTTP_POST`、`Mode.HTTP_GET`……）無法從 `bin/dispatcher` 到達；這些要用 HTTP client 對執行中的伺服器測試。

```bash
# Run a CLI-compatible @Action directly to verify a new action
# (the class must be imported; see --import or default.import.applications in application.properties)
bin/dispatcher greet/James --import com.example.MyService
bin/dispatcher echo --words "Praise the Lord"

# Start the HTTP server when you need the web-facing counterpart
bin/dispatcher start --import org.tinystruct.system.HttpServer

# Import additional Application/MCP classes for the current run
# (one --import per class; a comma-separated list fails with ClassNotFoundException)
bin/dispatcher start --import org.tinystruct.system.HttpServer --import com.example.MyService

# Discover what's available
bin/dispatcher --help
bin/dispatcher --version
```

預設就走這個流程：實作一個與傳輸方式無關的 `@Action`，馬上用 `bin/dispatcher <action>` 跑，確認它在 CLI 模式下行為正確，等到需要驗證對網頁的路徑時（例如 `mode = Mode.HTTP_POST`、session、檔案上傳），才啟動 HTTP 伺服器（同樣用 `bin/dispatcher start ...`）。對只限 HTTP 的 action，跳過 CLI 那一步，直接用 HTTP 測；`Mode.CLI` 的 action 不需要伺服器。絕對不要把寫死的 `main(String[] args)` 當成應用程式的進入點，`bin/dispatcher`（Windows 上是 `bin/dispatcher.cmd`）是每個模組唯一的進入點。

### 產生 `bin/dispatcher` 和 `bin/dispatcher.cmd`

每個 tinystruct 專案的 `bin/` 都需要它的啟動器。**由框架來產生，絕對不要手寫，也不要從別的專案複製，更不要拿 `main()` 代替。** 只要工作目錄底下的 `bin/` 裡缺少，`ApplicationManager.init()` 就會依 tinystruct jar 裡的範本，把目前作業系統用的啟動器寫進去，並填入那個 jar 的版本。換行字元和可執行位元都已經是對的。

**1. 找出 tinystruct 版本**，也就是專案建置所依據的版本：`pom.xml` 裡的 `<tinystruct.version>` 屬性或 `org.tinystruct:tinystruct` 依賴。jar 必須拿得到，放在 `~/.m2/repository/org/tinystruct/tinystruct/<version>/`（沒有的話就跑 `mvn dependency:resolve`），或在專案的 `lib/` 裡。

**2. 在專案根目錄跑一次框架：**

```bash
java -cp ~/.m2/repository/org/tinystruct/tinystruct/<version>/tinystruct-<version>.jar \
     org.tinystruct.system.Dispatcher --version
```

把 `<version>` 換成步驟 1 找到的版本。在 Windows 上要用 `%USERPROFILE%\.m2\repository\org\tinystruct\tinystruct\<version>\tinystruct-<version>.jar`，類別一樣。這樣**只會建立你執行當下那個作業系統的腳本**，而且只在它還不存在時才建立：

| 執行於 | 建立 |
|---|---|
| Linux, macOS | `bin/dispatcher`（可執行、LF） |
| Windows | `bin\dispatcher.cmd`（CRLF） |

**3. 驗證。** 在專案根目錄執行 `bin/dispatcher --version`（Windows：`bin\dispatcher.cmd --version`）。它會印出 `Dispatcher (cli) (built on tinystruct-<version>)`，而且腳本裡的 `VERSION` 等於 jar 的版本。接著 `bin/dispatcher --help` 會列出各個指令和每個已 import 的 action。把你建立的檔案給使用者看。

**4. 兩個腳本都要拿到：在每個作業系統上各跑一次步驟 2**，或讓另一個作業系統上的隊友或 CI 去跑，再把結果 commit 進來。兩個都要 commit，這樣在任一個作業系統上 checkout 都能用。不要試圖用 `-Dos.name=…` 假裝成另一個作業系統：在 Windows 上它會失敗（`setPosixFilePermissions` 丟出 `UnsupportedOperationException`），還會留下一個空的 `bin/dispatcher`。建議的 `.gitattributes`，避免 checkout 時換行字元被弄壞：

```
bin/dispatcher     text eol=lf
bin/dispatcher.cmd text eol=crlf
```

**升級 tinystruct：** 改 `pom.xml` 裡的版本，把舊腳本刪掉，再用新的 jar 重做步驟 2。另一個做法是 `bin/dispatcher update`，它會到 Maven Central 檢查最新的 release、升級專案的依賴，並強制重新產生腳本；它需要網路、會改 `pom.xml`，而且是升到*最新*版，不是你挑的版本。

**它也會隱性發生。** 任何走到 `ApplicationManager.init()` 的程式碼（dispatcher 本身，或單元測試裡的 `ApplicationManager.install(app, config)`），只要*目前目錄*裡缺少腳本就會建立。如果單元測試把 `bin/dispatcher.cmd` 散落到各模組目錄，要從 build 目錄執行它們：在 surefire 設定裡加上 `<workingDirectory>${project.build.directory}</workingDirectory>`。

**腳本做了什麼**，這能解釋大部分的問題：

- 要**從專案根目錄**執行：shell 腳本把目前目錄當成根，`.cmd` 則把 `bin/` 的上一層當成根。
- classpath 是 `target/classes`、`lib/*.jar`、`WEB-INF/lib/*`、`WEB-INF/classes` 和 tinystruct jar（從 `lib/` 找，找不到就用 `~/.m2`），然後帶著你的引數執行 `org.tinystruct.system.Dispatcher`。
- 第一次執行時，如果缺少 `mvnw` / `mvnw.cmd`，它們會把 Maven Wrapper 解壓到專案根目錄（Unix 上用 `unzip`，Windows 上用 PowerShell）。要告訴使用者這件事會發生；這些檔案可以 commit 或忽略。
- 只有 shell 腳本會把 `-D…` 和 `-X…` 引數當成 JVM 選項。

**常見的坑：**

- **在 Windows 上要用 `bin\dispatcher.cmd`。** shell 腳本用 `:` 連接 classpath，所以在 Git Bash/MSYS 下會因為 `ClassNotFoundException: org.tinystruct.system.Dispatcher` 失敗。用 WSL，或用 `.cmd`。
- **classpath 上只有 tinystruct jar。** 框架預設不再附 fat jar，所以你的其他模組、JDBC driver 和函式庫（jjwt、lettuce……）都必須放在 `lib/`：`mvn dependency:copy-dependencies -DoutputDirectory=lib`（並把 `lib/` 加進 git ignore）。在多模組的建置裡，要把啟動器放在含有 `target/classes` 和 `lib/` 的目錄，並把同層模組的 jar 複製進那個 `lib/`；從一個同層模組不在它 classpath 上的模組去執行，會因為 `NoClassDefFoundError` 失敗。
- **用 `--import` 或設定來載入應用程式。** 每個類別一個 `--import`（`--import a.A,b.B` 會失敗；要寫成 `--import a.A --import b.B`），或是在 `application.properties` 裡一次列出：`default.import.applications=a.A;b.B`（用 `;` 分隔）。
- **`.cmd` 必須設定 `JAVA_HOME`**；沒設的話它會報錯後停止。
- **`bin/` 要直接放在含有 `target/classes` 和 `lib/` 的目錄底下。** `.cmd` 把 `bin/` 的上一層當成根，所以如果 `bin/` 巢狀在錯的目錄裡，`Dispatcher` 前面就會放到錯的 classpath。

## 何時啟用

### 何時使用

- 透過 `bin/dispatcher` 執行、測試或除錯任何與傳輸方式無關或 `Mode.CLI` 的 `@Action`，這是使用 tinystruct 應用程式的預設方式，要在碰 HTTP 或 IDE 執行設定之前先用。只限 HTTP 的 action 改用 HTTP 測試。
- 設定一個沒有 `bin/dispatcher` / `bin/dispatcher.cmd` 的專案，讓框架去產生它（見「產生 `bin/dispatcher` 和 `bin/dispatcher.cmd`」）。
- 繼承 `AbstractApplication` 來建立新的 `Application` 模組。
- 用 `@Action` 定義路由和命令列 action。
- 透過 `Context` 處理每個請求的狀態。
- 使用原生的 `Builder` 和 `Builders` 元件做 JSON 序列化。
- 透過 `AbstractData` POJO 做資料庫持久化。
- 用 `generate` 指令，搭配 XML 對應檔或 annotation（`--mapping annotation`），從資料庫資料表產生 POJO。
- 實作 Server-Sent Events (SSE) 做即時推送。
- 透過 multipart 資料處理檔案上傳。
- 用 `URLRequest` 和 `HTTPHandler` 發出對外的 HTTP 請求。
- 在 `application.properties` 裡設定資料庫連線或系統設定。
- 除錯路由衝突（Action）或 CLI 引數解析。

## 運作方式

tinystruct 框架把任何標了 `@Action` 的方法都當成可路由的 endpoint。沒有 `mode` 時，分派不限於某一種傳輸，但它的參數和實作仍然需要支援那個環境。一般的 CLI 呼叫不會提供 HTTP 的 `Request` 或 `Response` 物件。用 `mode = Mode.CLI` 或 `Mode.HTTP_POST` 這類 HTTP mode 時，分派就被限制在那個傳輸。應用程式是繼承 `AbstractApplication` 建立的，它提供 `init()` 這類核心生命週期 hook，也能存取請求的 `Context`。

路由由 `ActionRegistry` 處理，它會自動把路徑片段對應到方法引數，並注入相依。對只處理資料的服務，要使用原生的 `Builder` 和 `Builders` 元件做 JSON 序列化，維持零相依。資料庫層使用 `AbstractData` POJO，用 `@Table`/`@Column` annotation 或 XML 對應檔對應到資料表，不需要外部 ORM 函式庫就能做 CRUD。缺少的資料表可以用 `database.autocreate=true` 自動建立。

## 範例

### 基本應用程式 (MyService)
```java
public class MyService extends AbstractApplication {
    @Override
    public void init() {
        this.setTemplateRequired(false); // Disable .view lookup for data/API apps
    }

    @Override public String version() { return "1.0.0"; }

    @Action("greet")
    public String greet() {
        return "Hello from tinystruct!";
    }

    // Path parameter: GET /?q=greet/James  OR  bin/dispatcher greet/James
    @Action("greet")
    public String greet(String name) {
        return "Hello, " + name + "!";
    }
}
```

### HTTP Mode 消歧義 (login)

下面的限制是以 UTF-16 code unit 計算的範例應用程式政策，不是 tinystruct 的預設值。請依你的認證服務自行調整。空白的憑證要拒絕，但不要 trim 或以其他方式更動傳給認證的值。

```java
@Action(value = "login", mode = Mode.HTTP_POST)
public String doLogin(Request<?, ?> request) throws ApplicationException {
    String username = request.getParameter("username");
    String password = request.getParameter("password");

    final int maxUsernameLength = 256;
    final int maxPasswordLength = 1024;
    if (username == null || password == null
            || username.length() > maxUsernameLength || password.length() > maxPasswordLength
            || username.isBlank() || password.isBlank()) {
        throw new ApplicationException("Invalid credentials");
    }

    // AuthService is your application's own class, not part of tinystruct
    String userId = AuthService.getInstance().authenticate(username, password); // null on failure
    if (userId == null) {
        throw new ApplicationException("Invalid credentials");
    }

    // Only touch the session after a successful authentication
    request.getSession().setAttribute("userId", userId);
    return "Logged in";
}
```

### 原生 JSON 資料處理 (Builder + Builders)
```java
import org.tinystruct.data.component.Builder;
import org.tinystruct.data.component.Builders;

@Action("api/data")
public String getData() throws ApplicationException {
    Builders dataList = new Builders();
    Builder item = new Builder();
    item.put("id", 1);
    item.put("name", "James");
    dataList.add(item);

    Builder response = new Builder();
    response.put("status", "success");
    response.put("data", dataList);
    return response.toString(); // {"status":"success","data":[{"id":1,"name":"James"}]}
}
```

### SSE (Server-Sent Events)
```java
import org.tinystruct.http.SSEPushManager;

@Action("sse/connect")
public String connect() {
    return "{\"type\":\"connect\",\"message\":\"Connected to SSE\"}";
}

// Push to a specific client
String sessionId = getContext().getId();
Builder msg = new Builder();
msg.put("text", "Hello, user!");
SSEPushManager.getInstance().push(sessionId, msg);

// Broadcast to all
// Broadcast to all
SSEPushManager.getInstance().broadcast(msg);
```

### 檔案上傳
```java
import org.tinystruct.data.FileEntity;

@Action(value = "upload", mode = Mode.HTTP_POST)
public String upload(Request<?, ?> request) throws ApplicationException {
    List<FileEntity> files = request.getAttachments();
    if (files != null) {
        for (FileEntity file : files) {
            System.out.println("Uploaded: " + file.getFilename());
        }
    }
    return "Upload OK";
}
```

### 資料庫 Metadata 操作
`DatabaseOperator` 提供直接存取連線層級的 catalog、schema 和 metadata：
```java
import org.tinystruct.data.DatabaseOperator;

DatabaseOperator operator = new DatabaseOperator();
try {
    String catalog = operator.getCatalog();
    String schema = operator.getSchema();
    java.sql.DatabaseMetaData metaData = operator.getMetaData();
    System.out.println("Using catalog: " + catalog + ", schema: " + schema);
} finally {
    operator.close();
}
```

## MCP Server 與 Tools 整合

tinystruct 從 SDK 版本 **`1.7.0`** 開始原生支援 Model Context Protocol (MCP)。
MCP 的 API（例如 `org.tinystruct.mcp.MCPTool`、`org.tinystruct.mcp.MCPServer`、`org.tinystruct.mcp.MCPException`）直接包含在核心依賴裡：
```xml
<dependency>
    <groupId>org.tinystruct</groupId>
    <artifactId>tinystruct</artifactId>
    <version>1.7.37</version>
</dependency>
```

> **安全警告（Prompt Injection）：**
> 工具的回傳值會直接回灌進 AI 模型的 context window。在把呼叫端提供的引數放進工具的回傳字串之前，你**一定要**驗證並清理所有引數。沒有清理輸入，攻擊者就可能注入對抗性的指令（Prompt Injection），蓋過模型原本的行為。一定要驗證長度、字元集和是否為 null。

**建立 MCP Tool：**
1. 繼承 `org.tinystruct.mcp.MCPTool`。
2. 用 `@Action` 標註各個操作，並在 `arguments` 陣列裡用 `@Argument` 宣告參數。
3. 以明確的方法引數接收參數，名稱要對應 `@Argument` 裡的 key。（工具引數**不要**用 `getContext().getAttribute(...)`。）

```java
import org.tinystruct.mcp.MCPTool;
import org.tinystruct.mcp.MCPException;
import org.tinystruct.system.annotation.Action;
import org.tinystruct.system.annotation.Argument;

public class MyCustomTool extends MCPTool {
    public MyCustomTool() {
        super("custom", "A custom tool for demonstrating MCP");
    }

    @Action(
        value = "custom/hello",
        description = "Say hello to someone",
        arguments = {
            @Argument(key = "name", description = "The name to greet", type = "string", optional = false)
        }
    )
    public String hello(String name) throws MCPException {
        // SECURITY: Validate/sanitize tool inputs before returning to the model
        // to prevent prompt injection vulnerabilities.
        if (name == null || name.length() > 50 || !name.matches("^[a-zA-Z0-9 ]+$")) {
            throw new MCPException("Invalid name provided");
        }
        return "Hello, " + name + "!";
    }
}
```

**部署 MCP Server：**
1. 繼承 `org.tinystruct.mcp.MCPServer`。
2. 覆寫 `init()`，並用 `this.registerTool()` 註冊你的工具。框架會自動掃描並對應 `@Action` 方法。

```java
import org.tinystruct.mcp.MCPServer;

public class MyMCPServer extends MCPServer {
    @Override
    public void init() {
        super.init();
        this.registerTool(new MyCustomTool());
    }

    @Override
    public String version() {
        return "1.0.0";
    }
}
```

透過 dispatcher 執行這個 server：
```bash
bin/dispatcher start --import org.tinystruct.system.HttpServer --import com.example.MyMCPServer
```

### 多載的 Tool 方法
tinystruct 支援在 `MCPTool` 裡為同一個工具名稱使用多載的方法（共用同一個工具名稱，但接受不同的參數簽章）。
- **Schema 合併**：同名的所有多載的輸入 schema，會動態合併成一個統一的 JSON schema。屬性取聯集，必填屬性取交集（只有在*所有*多載裡都必填的欄位，才會維持標成必填）。
- **執行路由**：執行工具時，server 會依序走過可用的多載方法，嘗試執行。每個方法會先做 schema 驗證，第一個對所提供引數驗證通過的多載就會被執行。如果沒有任何簽章符合或成功，框架會丟出適當的例外。

## 設定

設定管理在 `src/main/resources/application.properties`。

```properties
# Database
driver=org.h2.Driver
database.url=jdbc:h2:~/mydb
database.user=sa
database.password=
# Optional: create missing tables from the class mapping on first use (off by default)
# database.autocreate=true

# Server
default.home.page=hello
server.port=8080
default.server.open_browser=true
# Static files are served only from these directories (comma- or semicolon-separated),
# Use real public directories without symlinked root components.
# Do not expose the working directory or its ancestors. Default: static
# server.static.dirs=static,public

# Locale
default.language=en_US

# Session (Redis for clustered environments)
# default.session.repository=org.tinystruct.http.RedisSessionRepository
# redis.host=127.0.0.1
# redis.port=6379

# Programmatic Logging Configuration
logging.enabled=true
logging.level=INFO
org.tinystruct.level=FINE
# Handlers to create (comma- or whitespace-separated). Default: ConsoleHandler only
handlers=java.util.logging.ConsoleHandler
# To also write rotating log files, append the FileHandler:
# handlers=java.util.logging.ConsoleHandler, java.util.logging.FileHandler
# java.util.logging.FileHandler.pattern=logs/tinystruct-%g.log
# java.util.logging.FileHandler.limit=10485760
# java.util.logging.FileHandler.count=5
# java.util.logging.FileHandler.level=INFO
# java.util.logging.FileHandler.formatter=org.tinystruct.system.logging.LogFormatter
# java.util.logging.FileHandler.encoding=UTF-8
```

在應用程式裡存取設定值：
```java
String port = this.getConfiguration("server.port");
```

## Logging 與診斷

框架內含一層對 `java.util.logging` (JUL) 的程式化包裝，開箱就有漂亮的主控台輸出和進階的呼叫端追蹤。

- **ANSI 主控台顏色**：主控台輸出依 log 層級上色（SEVERE 是紅色、WARNING 是黃色、INFO 是綠色、CONFIG 是青色，FINE/debug log 是灰色）。
- **精確的呼叫端追蹤**：使用 Java 的 `StackWalker` API 在執行時追蹤 call stack。它會找出並記錄發起這次 log 的呼叫端確切的類別、方法、檔名和行號（略過內部的工具層和 logging 層）。
- **套件/Logger 層級覆寫**：直接在 `application.properties` 裡設定套件專屬的覆寫（例如 `org.tinystruct.level=FINE`）。
- **開關與層級**：`logging.enabled=false` 會關掉所有 logging。`logging.level` 設定 root logger 的層級，接受 `OFF`、`SEVERE`/`ERROR`、`WARNING`/`WARN`、`INFO`、`CONFIG`、`FINE`/`DEBUG`、`FINER`、`FINEST`/`TRACE` 和 `ALL`（預設 `INFO`）。
- **可設定的 Handler**：`handlers` 屬性列出要建立的 handler（用逗號或空白分隔）；預設是 `java.util.logging.ConsoleHandler`。每個 handler 會讀取它自己的 `<handler>.level`（預設 `ALL`）、`<handler>.formatter` 和 `<handler>.encoding`。任何有 public 無參數建構子的 `java.util.logging.Handler` 或 `Formatter` 類別都可以指名；不認識的 formatter 會 fallback 到內建的 `LogFormatter`，建立不了的 handler 會在 stderr 回報，其他 handler 仍會照常啟動。
- **FileHandler**：選擇性加入。`java.util.logging.FileHandler.pattern` 是選填的（預設 `%h/java%u.log`，在使用者的家目錄裡），而且如果它的上層目錄不存在會自動建立。像 `logs/tinystruct-%g.log` 這種相對 pattern，會以應用程式啟動時所在的目錄為基準解析（在那裡執行 `bin/dispatcher` 時就是專案根目錄）。`limit`（預設 `0`，不限制；否則是每個檔案的最大位元組數）、`count`（預設 `1`，保留的檔案數）和 `append`（預設 `true`）控制輪替。pattern 裡的 `%g` 是輪替編號，所以 `count=5` 會產生 `tinystruct-0.log` 到 `tinystruct-4.log`。要啟用它：把 `java.util.logging.FileHandler` 加進 `handlers`，設定上面的屬性，然後重新啟動。ANSI 顏色只會用在主控台輸出，絕不會用在 log 檔。
- **兩道層級關卡**：一筆記錄必須同時通過 logger 層級和 handler 層級。把 handler 調到 `FINE`，在 logger 也允許之前什麼都不會顯示，例如 `logging.level=FINE`，或像 `org.tinystruct.level=FINE` 這種套件覆寫。
- **何時生效**：logging 設定是在 `ApplicationManager` 初始化時，從 `application.properties` 讀取一次；改了之後要重新啟動應用程式。

## 靜態檔案

內建的 `HttpServer` 從 `server.static.dirs`（用逗號或分號分隔）指定的根目錄提供靜態檔案，沒有的話就用 `server.static.dir`；預設是 `static`。在 1.7.37 裡，工作目錄/祖先目錄的檢查，是在解析 symlink 之前比較正規化後的路徑名稱。它會拒絕 `.` 或 `..` 這類普通的根目錄，但如果設定的根目錄是 symlink 指向專案目錄或祖先目錄，就可能通過這個檢查。工作目錄之外的同層目錄也是允許的；並沒有強制只允許子孫目錄的政策。

要使用真實、專用的公開資源目錄，例如 `static/`，裡面只放打算公開存取的檔案。要檢查設定的根目錄和它的上層路徑元件，沒有 symlink 到範圍更廣或私有的目錄。含有 `.` 或 `..` 片段、`.git` 或 `.env` 這類隱藏名稱，或以 `.` 或空格結尾的名稱的請求都會被拒絕。候選檔案必須留在設定的根目錄解析後的路徑之內。但當設定的根目錄本身就解析到專案根目錄時，這個限制並不能防止專案根目錄被暴露：handler 會在之後的 `isProjectRootFile` 檢查之前，就先提供符合的靜態檔案。設定的根目錄是 symlink 時，不要依賴對專案根目錄檔案的全面拒絕。見 [釘住版本的 v1.7.37 實作](https://github.com/tinystruct/tinystruct/blob/089ec19022f3bb5d87f1e83e30b2034b24f7e77f/src/main/java/org/tinystruct/system/HttpServer.java#L569-L720)。

## 警訊與反模式

| 症狀 | 正確的做法 |
|---|---|
| import `com.google.gson` 或 `com.fasterxml.jackson` | 用 `org.tinystruct.data.component.Builder` / `Builders`。 |
| 用 `List<Builder>` 當 JSON 陣列 | 用 `Builders`，避開泛型 type erasure 的問題。 |
| `ApplicationRuntimeException: template not found` | 純 API 的應用程式，在 `init()` 裡呼叫 `setTemplateRequired(false)`。 |
| 把 `@Action` 標在 `private` 方法上 | Action 必須是 `public`，才會被框架註冊。 |
| 在應用程式裡寫死 `main(String[] args)`，或只用 curl/瀏覽器/IDE 執行設定測試 | 用 `bin/dispatcher` 當所有模組的進入點，也是與傳輸方式無關和 CLI action 預設的開發/測試工具（只限 HTTP 的 action 要對它啟動的伺服器用 HTTP 測試）。 |
| `bin/dispatcher` 不存在，或是手寫或複製來的啟動腳本 | 讓框架產生它：在專案根目錄跑一次 `org.tinystruct.system.Dispatcher --version`（會建立目前作業系統的腳本）。 |
| `bin/dispatcher` 在 Windows 上因為 `ClassNotFoundException: org.tinystruct.system.Dispatcher` 失敗 | shell 腳本無法在 Git Bash/MSYS 下執行；改用 `bin\dispatcher.cmd` 或 WSL。 |
| `--import a.A,b.B` 造成 `ClassNotFoundException` | 每個類別一個 `--import`：`--import a.A --import b.B`。 |
| shell 腳本啟動器出現 `\r: command not found` | 檔案是 CRLF 換行；把 `bin/dispatcher` 轉成 LF。 |
| 手動註冊 `ActionRegistry` | 優先用 `@Action` annotation 做自動探索。 |
| 執行時找不到 Action | 確認類別有用 `--import` import，或列在 `application.properties` 裡。 |
| 看不到 CLI 引數 | 用 `--key value` 傳入；用 `getContext().getAttribute("--key")` 存取。 |
| 兩個方法同一個路徑，觸發到錯的那個 | 設定明確的 `mode`（例如 `HTTP_GET` 對 `HTTP_POST`）來消歧義。 |
| `bin/dispatcher` 失敗並顯示 "The action is not allowed to be executed." | 這個 action 有 HTTP 專屬的 mode；從 CLI 到不了它。要用 HTTP 測試。要同時支援兩種傳輸，先把只限 HTTP 的相依從共用邏輯裡分離出來，再用 `Mode.DEFAULT` 提供相容 CLI 的進入點。 |
| 靜態檔案明明存在卻回傳 404 | 檢查 `server.static.dirs` / `server.static.dir`（預設 `static/`）、被禁止的請求名稱，以及解析後的根目錄包含檢查。要用真實的公開目錄；設定成 symlink 的根目錄，可能在專案根目錄檢查之前就暴露專案或祖先目錄的檔案。 |
| 沒有寫出 log 檔 | `FileHandler` 是選擇性加入的：把 `java.util.logging.FileHandler` 加進 `handlers`。要設定 `java.util.logging.FileHandler.pattern`，否則檔案會落在 `%h/java%u.log`（你的家目錄）。 |
| `FINE` / debug 訊息從不出現 | 兩道關卡都必須放行：設定 `logging.level=FINE`（或像 `org.tinystruct.level=FINE` 的套件覆寫），並確保 handler 的 `.level` 沒有更嚴格。 |

## 最佳實務

1. **`bin/dispatcher` 優先**：對與傳輸方式無關和 `Mode.CLI` 的 action，在做其他事之前，先對著 `bin/dispatcher` 開發和驗證：從 CLI 執行 action、確認行為，再疊上 HTTP/mode 的考量。帶有 HTTP mode 的 action（`Mode.HTTP_POST`……）會被 CLI 拒絕，所以要啟動伺服器，改用 HTTP 測試。它是最快的內圈迴圈，也是唯一保證跟框架實際路由和綁定引數方式一致的工具。
2. **細粒度的應用程式**：把邏輯拆成較小、專注的應用程式，不要塞進一個龐大的類別。
3. **在 `init()` 裡做設定**：設定（config、DB）要靠 `init()`，不要放在建構子。不要呼叫 `setAction()`，要用 `@Action` annotation。
4. **注意 Mode**：用 `@Action` 的 `Mode` 參數，把敏感的操作限制成只能 `CLI` 或特定的 HTTP 方法。
5. **Context 優先於參數**：對選用的 CLI flag，用 `getContext().getAttribute("--flag")`，不要在方法簽章上加參數。
6. **非同步事件**：由事件觸發的繁重工作，在事件 handler 裡用 `CompletableFuture.runAsync()`。

## 技術參考

詳細指南放在 `references/` 目錄：

- [Architecture & Config](references/architecture.md) — 抽象層、套件地圖、屬性
- [Routing & @Action](references/routing.md) — Annotation 細節、Mode、參數
- [Data Handling](references/data-handling.md) — Builder、Builders、JSON 序列化與解析
- [Database Persistence](references/database.md) — AbstractData POJO、CRUD、annotation 與 XML 對應、POJO 產生、資料表自動建立
- [System & Usage](references/system-usage.md) — Context、Session、SSE、檔案上傳、事件、網路
- [Testing Patterns](references/testing.md) — JUnit 5 單元測試與 HTTP integration 測試

## 參考原始碼檔案（內部）

- `src/main/java/org/tinystruct/AbstractApplication.java` — 有生命週期 hook 的核心基底類別
- `src/main/java/org/tinystruct/system/annotation/Action.java` — Annotation 與 Mode
- `src/main/java/org/tinystruct/application/ActionRegistry.java` — 路由引擎
- `src/main/java/org/tinystruct/data/component/Builder.java` — JSON 物件序列化器
- `src/main/java/org/tinystruct/data/component/Builders.java` — JSON 陣列序列化器
- `src/main/java/org/tinystruct/data/component/AbstractData.java` — 有 CRUD 的 POJO 基底類別
- `src/main/java/org/tinystruct/data/Mapping.java` — 對應的 metadata（annotation 或 XML），依類別快取
- `src/main/java/org/tinystruct/data/annotation/Table.java` — `@Table`，旁邊還有 `@Id` 和 `@Column`
- `src/main/java/org/tinystruct/data/tools/TableCreator.java` — 建立缺少的資料表（`database.autocreate`）
- `src/main/java/org/tinystruct/data/tools/MySQLGenerator.java` — POJO 產生器參考（`MappingMode` 選擇 XML 或 annotation）
- `src/main/java/org/tinystruct/data/component/FieldType.java` — SQL 到 Java 的型別對應
- `src/main/java/org/tinystruct/data/component/Condition.java` — 流暢介面的 SQL 查詢建構器
- `src/main/java/org/tinystruct/http/SSEPushManager.java` — SSE 連線管理
- `src/main/java/org/tinystruct/system/logging/LogFormatter.java` — 有 ANSI 主控台顏色和以 StackWalker 為基礎的呼叫端追蹤的自訂 log formatter
- `src/main/java/org/tinystruct/system/logging/LoggerConfigurer.java` — 從應用程式屬性做程式化設定的 logging 設定器
- `src/test/java/org/tinystruct/application/ActionRegistryTest.java` — Registry 測試範例
- `src/test/java/org/tinystruct/system/HttpServerHttpModeTest.java` — HTTP integration 測試模式
