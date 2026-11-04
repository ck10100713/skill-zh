---
name: perl-security
description: 全面的 Perl 安全指南，涵蓋 taint mode、輸入驗證、安全的程序執行、DBI 參數化查詢、web 安全（XSS/SQLi/CSRF），以及 perlcritic 安全規則。Review Perl 的輸入處理、程序執行、DBI 查詢或面向網路的程式碼時使用。
metadata:
  origin: ECC
---

# Perl 安全模式

給 Perl 應用程式的完整安全指南，涵蓋輸入驗證、injection 防護和安全的寫法。

## 何時啟用

- 在 Perl 應用程式中處理使用者輸入
- 開發 Perl web 應用程式（CGI、Mojolicious、Dancer2、Catalyst）
- Review Perl 程式碼有沒有安全漏洞
- 用使用者提供的路徑做檔案操作
- 從 Perl 執行系統指令
- 撰寫 DBI 資料庫查詢

## 運作方式

先從會追蹤 taint 的輸入邊界開始，再往外擴：驗證並 untaint 輸入，把檔案系統和程序執行限制住，所有地方都用參數化的 DBI 查詢。下面的範例列出的是安全的預設做法，只要你的 Perl 程式碼會碰到使用者輸入、shell 或網路，出貨前都要先套用。

## Taint Mode

Perl 的 taint mode (`-T`) 會追蹤來自外部來源的資料，沒有經過明確驗證就不准拿去做不安全的操作。

### 啟用 Taint Mode

```perl
#!/usr/bin/perl -T
use v5.36;

# Tainted：任何來自程式外部的東西
my $input    = $ARGV[0];        # Tainted
my $env_path = $ENV{PATH};      # Tainted
my $form     = <STDIN>;         # Tainted
my $query    = $ENV{QUERY_STRING}; # Tainted

# 儘早清理 PATH（taint mode 下必須做）
$ENV{PATH} = '/usr/local/bin:/usr/bin:/bin';
delete @ENV{qw(IFS CDPATH ENV BASH_ENV)};
```

### Untaint 模式

```perl
use v5.36;

# Good: 用明確的 regex 驗證並 untaint
sub untaint_username($input) {
    if ($input =~ /^([a-zA-Z0-9_]{3,30})$/) {
        return $1;  # $1 已經 untainted
    }
    die "Invalid username: must be 3-30 alphanumeric characters\n";
}

# Good: 驗證並 untaint 檔案路徑
sub untaint_filename($input) {
    if ($input =~ m{^([a-zA-Z0-9._-]+)$}) {
        return $1;
    }
    die "Invalid filename: contains unsafe characters\n";
}

# Bad: 太寬鬆的 untaint（等於白做）
sub bad_untaint($input) {
    $input =~ /^(.*)$/s;
    return $1;  # 什麼都收，沒有意義
}
```

## 輸入驗證

### 用 Allowlist，不要用 Blocklist

```perl
use v5.36;

# Good: Allowlist，明確定義什麼才允許
sub validate_sort_field($field) {
    my %allowed = map { $_ => 1 } qw(name email created_at updated_at);
    die "Invalid sort field: $field\n" unless $allowed{$field};
    return $field;
}

# Good: 用明確的 pattern 驗證
sub validate_email($email) {
    if ($email =~ /^([a-zA-Z0-9._%+-]+\@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$/) {
        return $1;
    }
    die "Invalid email address\n";
}

sub validate_integer($input) {
    if ($input =~ /^(-?\d{1,10})$/) {
        return $1 + 0;  # 轉成數字
    }
    die "Invalid integer\n";
}

# Bad: Blocklist，永遠列不完
sub bad_validate($input) {
    die "Invalid" if $input =~ /[<>"';&|]/;  # 擋不住編碼過的攻擊
    return $input;
}
```

### 長度限制

```perl
use v5.36;

sub validate_comment($text) {
    die "Comment is required\n"        unless length($text) > 0;
    die "Comment exceeds 10000 chars\n" if length($text) > 10_000;
    return $text;
}
```

## 安全的正規表達式

### 防範 ReDoS

在互相重疊的 pattern 上使用巢狀量詞，會造成災難性的 backtracking。

```perl
use v5.36;

# Bad: 有 ReDoS 風險（指數級 backtracking）
my $bad_re = qr/^(a+)+$/;           # 巢狀量詞
my $bad_re2 = qr/^([a-zA-Z]+)*$/;   # 字元類別上的巢狀量詞
my $bad_re3 = qr/^(.*?,){10,}$/;    # 重複的 greedy/lazy 組合

# Good: 改寫成不巢狀
my $good_re = qr/^a+$/;             # 單一量詞
my $good_re2 = qr/^[a-zA-Z]+$/;     # 字元類別上只有單一量詞

# Good: 用 possessive 量詞或 atomic group 避免 backtracking
my $safe_re = qr/^[a-zA-Z]++$/;             # Possessive (5.10+)
my $safe_re2 = qr/^(?>a+)$/;                # Atomic group

# Good: 對不受信任的 pattern 強制設 timeout
use POSIX qw(alarm);
sub safe_match($string, $pattern, $timeout = 2) {
    my $matched;
    eval {
        local $SIG{ALRM} = sub { die "Regex timeout\n" };
        alarm($timeout);
        $matched = $string =~ $pattern;
        alarm(0);
    };
    alarm(0);
    die $@ if $@;
    return $matched;
}
```

## 安全的檔案操作

### 三參數 open

```perl
use v5.36;

# Good: 三參數 open、lexical filehandle、檢查回傳值
sub read_file($path) {
    open my $fh, '<:encoding(UTF-8)', $path
        or die "Cannot open '$path': $!\n";
    local $/;
    my $content = <$fh>;
    close $fh;
    return $content;
}

# Bad: 兩參數 open 搭配使用者資料（command injection）
sub bad_read($path) {
    open my $fh, $path;        # 如果 $path = "|rm -rf /"，會直接執行指令！
    open my $fh, "< $path";   # Shell metacharacter injection
}
```

### 防範 TOCTOU 與 Path Traversal

```perl
use v5.36;
use Fcntl qw(:DEFAULT :flock);
use File::Spec;
use Cwd qw(realpath);

# 原子性地建立檔案
sub create_file_safe($path) {
    sysopen(my $fh, $path, O_WRONLY | O_CREAT | O_EXCL, 0600)
        or die "Cannot create '$path': $!\n";
    return $fh;
}

# 驗證路徑沒有跑出允許的目錄
sub safe_path($base_dir, $user_path) {
    my $real = realpath(File::Spec->catfile($base_dir, $user_path))
        // die "Path does not exist\n";
    my $base_real = realpath($base_dir)
        // die "Base dir does not exist\n";
    die "Path traversal blocked\n" unless $real =~ /^\Q$base_real\E(?:\/|\z)/;
    return $real;
}
```

暫存檔用 `File::Temp`（`tempfile(UNLINK => 1)`），並用 `flock(LOCK_EX)` 防止 race condition。

## 安全的程序執行

### List 形式的 system 與 exec

```perl
use v5.36;

# Good: List 形式，不會經過 shell 展開
sub run_command(@cmd) {
    system(@cmd) == 0
        or die "Command failed: @cmd\n";
}

run_command('grep', '-r', $user_pattern, '/var/log/app/');

# Good: 用 IPC::Run3 安全地擷取輸出
use IPC::Run3;
sub capture_output(@cmd) {
    my ($stdout, $stderr);
    run3(\@cmd, \undef, \$stdout, \$stderr);
    if ($?) {
        die "Command failed (exit $?): $stderr\n";
    }
    return $stdout;
}

# Bad: 字串形式，會有 shell injection！
sub bad_search($pattern) {
    system("grep -r '$pattern' /var/log/app/");  # 如果 $pattern = "'; rm -rf / #"
}

# Bad: 在 backticks 裡做變數插值
my $output = `ls $user_dir`;   # 有 shell injection 風險
```

另外也可以用 `Capture::Tiny`，安全地擷取外部指令的 stdout/stderr。

## 防範 SQL Injection

### DBI Placeholders

```perl
use v5.36;
use DBI;

my $dbh = DBI->connect($dsn, $user, $pass, {
    RaiseError => 1,
    PrintError => 0,
    AutoCommit => 1,
});

# Good: 參數化查詢，一律使用 placeholder
sub find_user($dbh, $email) {
    my $sth = $dbh->prepare('SELECT * FROM users WHERE email = ?');
    $sth->execute($email);
    return $sth->fetchrow_hashref;
}

sub search_users($dbh, $name, $status) {
    my $sth = $dbh->prepare(
        'SELECT * FROM users WHERE name LIKE ? AND status = ? ORDER BY name'
    );
    $sth->execute("%$name%", $status);
    return $sth->fetchall_arrayref({});
}

# Bad: 在 SQL 裡做字串插值（SQLi 漏洞！）
sub bad_find($dbh, $email) {
    my $sth = $dbh->prepare("SELECT * FROM users WHERE email = '$email'");
    # 如果 $email = "' OR 1=1 --"，會回傳所有使用者
    $sth->execute;
    return $sth->fetchrow_hashref;
}
```

### 動態欄位的 Allowlist

```perl
use v5.36;

# Good: 拿欄位名稱對照 allowlist 驗證
sub order_by($dbh, $column, $direction) {
    my %allowed_cols = map { $_ => 1 } qw(name email created_at);
    my %allowed_dirs = map { $_ => 1 } qw(ASC DESC);

    die "Invalid column: $column\n"    unless $allowed_cols{$column};
    die "Invalid direction: $direction\n" unless $allowed_dirs{uc $direction};

    my $sth = $dbh->prepare("SELECT * FROM users ORDER BY $column $direction");
    $sth->execute;
    return $sth->fetchall_arrayref({});
}

# Bad: 直接把使用者選的欄位插進去
sub bad_order($dbh, $column) {
    $dbh->prepare("SELECT * FROM users ORDER BY $column");  # SQLi！
}
```

### DBIx::Class（ORM 的安全性）

```perl
use v5.36;

# DBIx::Class 會產生安全的參數化查詢
my @users = $schema->resultset('User')->search({
    status => 'active',
    email  => { -like => '%@example.com' },
}, {
    order_by => { -asc => 'name' },
    rows     => 50,
});
```

## Web 安全

### 防範 XSS

```perl
use v5.36;
use HTML::Entities qw(encode_entities);
use URI::Escape qw(uri_escape_utf8);

# Good: 針對 HTML context 編碼輸出
sub safe_html($user_input) {
    return encode_entities($user_input);
}

# Good: 針對 URL context 編碼
sub safe_url_param($value) {
    return uri_escape_utf8($value);
}

# Good: 針對 JSON context 編碼
use JSON::MaybeXS qw(encode_json);
sub safe_json($data) {
    return encode_json($data);  # 會處理 escape
}

# 樣板自動 escape（Mojolicious）
# <%= $user_input %>   — 自動 escape（安全）
# <%== $raw_html %>    — 原樣輸出（危險，只能用在受信任的內容）

# 樣板自動 escape（Template Toolkit）
# [% user_input | html %]  — 明確的 HTML 編碼

# Bad: 在 HTML 裡原樣輸出
sub bad_html($input) {
    print "<div>$input</div>";  # 如果 $input 含有 <script> 就是 XSS
}
```

### CSRF 防護

```perl
use v5.36;
use Crypt::URandom qw(urandom);
use MIME::Base64 qw(encode_base64url);

sub generate_csrf_token() {
    return encode_base64url(urandom(32));
}
```

驗證 token 時要用 constant-time 比較。大多數 web framework（Mojolicious、Dancer2、Catalyst）都內建 CSRF 防護，優先用內建的，不要自己手刻。

### Session 與 Header 安全

```perl
use v5.36;

# Mojolicious session + headers
$app->secrets(['long-random-secret-rotated-regularly']);
$app->sessions->secure(1);          # 只走 HTTPS
$app->sessions->samesite('Lax');

$app->hook(after_dispatch => sub ($c) {
    $c->res->headers->header('X-Content-Type-Options' => 'nosniff');
    $c->res->headers->header('X-Frame-Options'        => 'DENY');
    $c->res->headers->header('Content-Security-Policy' => "default-src 'self'");
    $c->res->headers->header('Strict-Transport-Security' => 'max-age=31536000; includeSubDomains');
});
```

## 輸出編碼

輸出一定要依照它的 context 編碼：HTML 用 `HTML::Entities::encode_entities()`，URL 用 `URI::Escape::uri_escape_utf8()`，JSON 用 `JSON::MaybeXS::encode_json()`。

## CPAN 模組安全

- **釘住版本**，寫在 cpanfile：`requires 'DBI', '== 1.643';`
- **優先選有在維護的模組**：到 MetaCPAN 看最近有沒有發佈新版
- **減少依賴**：每多一個依賴就多一個攻擊面

## 安全工具

### perlcritic 安全規則

```ini
# .perlcriticrc — 以安全為主的設定
severity = 3
theme = security + core

# 要求檢查 system call 的回傳值
[InputOutput::RequireCheckedSyscalls]
functions = :builtins
severity = 4

# 禁止 string eval
[BuiltinFunctions::ProhibitStringyEval]
severity = 5

# 禁止 backtick 運算子
[InputOutput::ProhibitBacktickOperators]
severity = 4

# 禁止兩參數 open
[InputOutput::ProhibitTwoArgOpen]
severity = 5

# 禁止 bare-word filehandle
[InputOutput::ProhibitBarewordFileHandles]
severity = 5
```

### 執行 perlcritic

```bash
# 檢查單一檔案
perlcritic --severity 3 --theme security lib/MyApp/Handler.pm

# 檢查整個專案
perlcritic --severity 3 --theme security lib/

# 整合進 CI
perlcritic --severity 4 --theme security --quiet lib/ || exit 1
```

## 安全檢查清單

| 檢查項目 | 要確認什麼 |
|---|---|
| Taint mode | CGI/web script 有加 `-T` 旗標 |
| 輸入驗證 | Allowlist pattern、長度限制 |
| 檔案操作 | 三參數 open、path traversal 檢查 |
| 程序執行 | List 形式的 system，不做 shell 插值 |
| SQL 查詢 | DBI placeholder，絕不做字串插值 |
| HTML 輸出 | `encode_entities()`、樣板自動 escape |
| CSRF token | 有產生，且在會改變狀態的請求上有驗證 |
| Session 設定 | Secure、HttpOnly、SameSite cookie |
| HTTP header | CSP、X-Frame-Options、HSTS |
| 依賴套件 | 釘住版本、模組有審查過 |
| Regex 安全 | 沒有巢狀量詞、pattern 有加錨點 |
| 錯誤訊息 | 沒有把 stack trace 或路徑洩漏給使用者 |

## 反模式

```perl
# 1. 兩參數 open 搭配使用者資料（command injection）
open my $fh, $user_input;               # CRITICAL 漏洞

# 2. 字串形式的 system（shell injection）
system("convert $user_file output.png"); # CRITICAL 漏洞

# 3. SQL 字串插值
$dbh->do("DELETE FROM users WHERE id = $id");  # SQLi

# 4. 對使用者輸入做 eval（code injection）
eval $user_code;                         # 遠端程式碼執行

# 5. 沒清理就信任 $ENV
my $path = $ENV{UPLOAD_DIR};             # 可能被竄改
system("ls $path");                      # 雙重漏洞

# 6. 沒驗證就關掉 taint
($input) = $input =~ /(.*)/s;           # 偷懶的 untaint，等於白做

# 7. 在 HTML 裡放原始的使用者資料
print "<div>Welcome, $username!</div>";  # XSS

# 8. 沒驗證的 redirect
print $cgi->redirect($user_url);         # Open redirect
```

**記住**：Perl 的彈性很強，但需要紀律。面向網路的程式碼要開 taint mode，所有輸入用 allowlist 驗證，每個查詢都用 DBI placeholder，所有輸出都依 context 編碼。要做縱深防禦，絕對不要只靠單一層。
