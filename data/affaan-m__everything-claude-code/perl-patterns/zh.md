---
name: perl-patterns
description: 現代 Perl 5.36+ 的慣用寫法、最佳實踐與慣例，用來建構穩健、好維護的 Perl 應用程式。撰寫或 review 現代 Perl 5.36+ 程式碼時使用。
metadata:
  origin: ECC
---

# 現代 Perl 開發模式

Perl 5.36+ 的慣用模式與最佳實踐，用來建構穩健、好維護的應用程式。

## 何時啟用

- 撰寫新的 Perl 程式碼或模組
- Review Perl 程式碼是否符合慣用寫法
- 把舊的 Perl 重構成現代標準
- 設計 Perl 模組架構
- 把 5.36 以前的程式碼遷移到現代 Perl

## 運作方式

套用這些模式時，以現代 Perl 5.36+ 的預設值為偏好：signatures、明確的模組、聚焦的錯誤處理，以及可測試的邊界。下面的範例是拿來複製當起點的，之後再針對你眼前實際的應用程式、依賴套件和部署模型收緊。

## 核心原則

### 1. 使用 `v5.36` Pragma

只要一行 `use v5.36`，就能取代舊的樣板，並啟用 strict、warnings 和 subroutine signatures。

```perl
# Good: 現代的開頭
use v5.36;

sub greet($name) {
    say "Hello, $name!";
}

# Bad: 舊式樣板
use strict;
use warnings;
use feature 'say', 'signatures';
no warnings 'experimental::signatures';

sub greet {
    my ($name) = @_;
    say "Hello, $name!";
}
```

### 2. Subroutine Signatures

用 signatures 讓程式更清楚，還能自動檢查參數數量。

```perl
use v5.36;

# Good: 帶預設值的 signatures
sub connect_db($host, $port = 5432, $timeout = 30) {
    # $host 必填，其他都有預設值
    return DBI->connect("dbi:Pg:host=$host;port=$port", undef, undef, {
        RaiseError => 1,
        PrintError => 0,
    });
}

# Good: 用 slurpy 參數接收不定數量的引數
sub log_message($level, @details) {
    say "[$level] " . join(' ', @details);
}

# Bad: 手動拆解引數
sub connect_db {
    my ($host, $port, $timeout) = @_;
    $port    //= 5432;
    $timeout //= 30;
    # ...
}
```

### 3. Context 敏感性

要搞懂 scalar context 和 list context 的差別，這是 Perl 的核心概念。

```perl
use v5.36;

my @items = (1, 2, 3, 4, 5);

my @copy  = @items;            # List context：所有元素
my $count = @items;            # Scalar context：元素個數 (5)
say "Items: " . scalar @items; # 強制 scalar context
```

### 4. Postfix Dereferencing

處理巢狀結構時，用 postfix dereference 語法比較好讀。

```perl
use v5.36;

my $data = {
    users => [
        { name => 'Alice', roles => ['admin', 'user'] },
        { name => 'Bob',   roles => ['user'] },
    ],
};

# Good: Postfix dereferencing
my @users = $data->{users}->@*;
my @roles = $data->{users}[0]{roles}->@*;
my %first = $data->{users}[0]->%*;

# Bad: Circumfix dereferencing（串起來時比較難讀）
my @users = @{ $data->{users} };
my @roles = @{ $data->{users}[0]{roles} };
```

### 5. `isa` 運算子 (5.32+)

中綴的型別檢查，取代 `blessed($o) && $o->isa('X')`。

```perl
use v5.36;
if ($obj isa 'My::Class') { $obj->do_something }
```

## 錯誤處理

### eval/die 模式

```perl
use v5.36;

sub parse_config($path) {
    my $content = eval { path($path)->slurp_utf8 };
    die "Config error: $@" if $@;
    return decode_json($content);
}
```

### Try::Tiny（可靠的例外處理）

```perl
use v5.36;
use Try::Tiny;

sub fetch_user($id) {
    my $user = try {
        $db->resultset('User')->find($id)
            // die "User $id not found\n";
    }
    catch {
        warn "Failed to fetch user $id: $_";
        undef;
    };
    return $user;
}
```

### 原生 try/catch (5.40+)

```perl
use v5.40;

sub divide($x, $y) {
    try {
        die "Division by zero" if $y == 0;
        return $x / $y;
    }
    catch ($e) {
        warn "Error: $e";
        return;
    }
}
```

## 用 Moo 寫現代 OO

輕量、現代的 OO 優先用 Moo。只有真的需要 Moose 的 metaprotocol 時才用 Moose。

```perl
# Good: Moo class
package User;
use Moo;
use Types::Standard qw(Str Int ArrayRef);
use namespace::autoclean;

has name  => (is => 'ro', isa => Str, required => 1);
has email => (is => 'ro', isa => Str, required => 1);
has age   => (is => 'ro', isa => Int, default  => sub { 0 });
has roles => (is => 'ro', isa => ArrayRef[Str], default => sub { [] });

sub is_admin($self) {
    return grep { $_ eq 'admin' } $self->roles->@*;
}

sub greet($self) {
    return "Hello, I'm " . $self->name;
}

1;

# 用法
my $user = User->new(
    name  => 'Alice',
    email => 'alice@example.com',
    roles => ['admin', 'user'],
);

# Bad: blessed hashref（沒有驗證，也沒有 accessor）
package User;
sub new {
    my ($class, %args) = @_;
    return bless \%args, $class;
}
sub name { return $_[0]->{name} }
1;
```

### Moo Roles

```perl
package Role::Serializable;
use Moo::Role;
use JSON::MaybeXS qw(encode_json);
requires 'TO_HASH';
sub to_json($self) { encode_json($self->TO_HASH) }
1;

package User;
use Moo;
with 'Role::Serializable';
has name  => (is => 'ro', required => 1);
has email => (is => 'ro', required => 1);
sub TO_HASH($self) { { name => $self->name, email => $self->email } }
1;
```

### 原生 `class` 關鍵字 (5.38+, Corinna)

```perl
use v5.38;
use feature 'class';
no warnings 'experimental::class';

class Point {
    field $x :param;
    field $y :param;
    method magnitude() { sqrt($x**2 + $y**2) }
}

my $p = Point->new(x => 3, y => 4);
say $p->magnitude;  # 5
```

## 正規表達式

### Named Captures 與 `/x` 旗標

```perl
use v5.36;

# Good: 用 named captures 加 /x，可讀性高
my $log_re = qr{
    ^ (?<timestamp> \d{4}-\d{2}-\d{2} \s \d{2}:\d{2}:\d{2} )
    \s+ \[ (?<level> \w+ ) \]
    \s+ (?<message> .+ ) $
}x;

if ($line =~ $log_re) {
    say "Time: $+{timestamp}, Level: $+{level}";
    say "Message: $+{message}";
}

# Bad: 位置式 captures（難維護）
if ($line =~ /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.+)$/) {
    say "Time: $1, Level: $2";
}
```

### 預先編譯的 Pattern

```perl
use v5.36;

# Good: 編譯一次，重複使用
my $email_re = qr/^[A-Za-z0-9._%+-]+\@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

sub validate_emails(@emails) {
    return grep { $_ =~ $email_re } @emails;
}
```

## 資料結構

### Reference 與安全的深層存取

```perl
use v5.36;

# Hash 與 array reference
my $config = {
    database => {
        host => 'localhost',
        port => 5432,
        options => ['utf8', 'sslmode=require'],
    },
};

# 安全的深層存取（任何一層不存在就回傳 undef）
my $port = $config->{database}{port};           # 5432
my $missing = $config->{cache}{host};           # undef，不會報錯

# Hash slices
my %subset;
@subset{qw(host port)} = @{$config->{database}}{qw(host port)};

# Array slices
my @first_two = $config->{database}{options}->@[0, 1];

# 多變數 for 迴圈（5.36 是 experimental，5.40 已穩定）
use feature 'for_list';
no warnings 'experimental::for_list';
for my ($key, $val) (%$config) {
    say "$key => $val";
}
```

## 檔案 I/O

### 三參數 open

```perl
use v5.36;

# Good: 三參數 open 搭配 autodie（core module，不用再寫 'or die'）
use autodie;

sub read_file($path) {
    open my $fh, '<:encoding(UTF-8)', $path;
    local $/;
    my $content = <$fh>;
    close $fh;
    return $content;
}

# Bad: 兩參數 open（有 shell injection 風險，見 perl-security）
open FH, $path;            # 絕對不要這樣寫
open FH, "< $path";        # 一樣不行，使用者資料出現在 mode 字串裡
```

### 用 Path::Tiny 處理檔案操作

```perl
use v5.36;
use Path::Tiny;

my $file = path('config', 'app.json');
my $content = $file->slurp_utf8;
$file->spew_utf8($new_content);

# 走訪目錄
for my $child (path('src')->children(qr/\.pl$/)) {
    say $child->basename;
}
```

## 模組組織

### 標準專案結構

```text
MyApp/
├── lib/
│   └── MyApp/
│       ├── App.pm           # 主模組
│       ├── Config.pm        # 設定
│       ├── DB.pm            # 資料庫層
│       └── Util.pm          # 工具函式
├── bin/
│   └── myapp                # 進入點 script
├── t/
│   ├── 00-load.t            # 編譯測試
│   ├── unit/                # 單元測試
│   └── integration/         # 整合測試
├── cpanfile                 # 依賴套件
├── Makefile.PL              # Build 系統
└── .perlcriticrc            # Lint 設定
```

### Exporter 模式

```perl
package MyApp::Util;
use v5.36;
use Exporter 'import';

our @EXPORT_OK   = qw(trim);
our %EXPORT_TAGS = (all => \@EXPORT_OK);

sub trim($str) { $str =~ s/^\s+|\s+$//gr }

1;
```

## 工具

### perltidy 設定 (.perltidyrc)

```text
-i=4        # 4-space indent
-l=100      # 100-char line length
-ci=4       # continuation indent
-ce         # cuddled else
-bar        # opening brace on same line
-nolq       # don't outdent long quoted strings
```

### perlcritic 設定 (.perlcriticrc)

```ini
severity = 3
theme = core + pbp + security

[InputOutput::RequireCheckedSyscalls]
functions = :builtins
exclude_functions = say print

[Subroutines::ProhibitExplicitReturnUndef]
severity = 4

[ValuesAndExpressions::ProhibitMagicNumbers]
allowed_values = 0 1 2 -1
```

### 依賴管理 (cpanfile + carton)

```bash
cpanm App::cpanminus Carton   # 安裝工具
carton install                 # 依 cpanfile 安裝依賴
carton exec -- perl bin/myapp  # 用本地依賴執行
```

```perl
# cpanfile
requires 'Moo', '>= 2.005';
requires 'Path::Tiny';
requires 'JSON::MaybeXS';
requires 'Try::Tiny';

on test => sub {
    requires 'Test2::V0';
    requires 'Test::MockModule';
};
```

## 速查：現代 Perl 慣用寫法

| 舊式寫法 | 現代替代寫法 |
|---|---|
| `use strict; use warnings;` | `use v5.36;` |
| `my ($x, $y) = @_;` | `sub foo($x, $y) { ... }` |
| `@{ $ref }` | `$ref->@*` |
| `%{ $ref }` | `$ref->%*` |
| `open FH, "< $file"` | `open my $fh, '<:encoding(UTF-8)', $file` |
| `blessed hashref` | 帶型別的 `Moo` class |
| `$1, $2, $3` | `$+{name}`（named captures） |
| `eval { }; if ($@)` | `Try::Tiny` 或原生 `try/catch` (5.40+) |
| `BEGIN { require Exporter; }` | `use Exporter 'import';` |
| 手動處理檔案 | `Path::Tiny` |
| `blessed($o) && $o->isa('X')` | `$o isa 'X'` (5.32+) |
| `builtin::true / false` | `use builtin 'true', 'false';` (5.36+, experimental) |

## 反模式

```perl
# 1. 兩參數 open（有安全風險）
open FH, $filename;                     # 絕對不要

# 2. Indirect object 語法（解析有歧義）
my $obj = new Foo(bar => 1);            # Bad
my $obj = Foo->new(bar => 1);           # Good

# 3. 過度依賴 $_
map { process($_) } grep { validate($_) } @items;  # 難以閱讀
my @valid = grep { validate($_) } @items;           # 比較好：拆開來寫
my @results = map { process($_) } @valid;

# 4. 關掉 strict refs
no strict 'refs';                        # 幾乎一定是錯的
${"My::Package::$var"} = $value;         # 改用 hash

# 5. 用全域變數當設定
our $TIMEOUT = 30;                       # Bad：可變的全域變數
use constant TIMEOUT => 30;              # 比較好：常數
# 最好：帶預設值的 Moo attribute

# 6. 用字串 eval 載入模組
eval "require $module";                  # Bad：有 code injection 風險
eval "use $module";                      # Bad
use Module::Runtime 'require_module';    # Good：安全的模組載入
require_module($module);
```

**記住**：現代 Perl 乾淨、好讀、又安全。樣板交給 `use v5.36` 處理，物件用 Moo，優先選 CPAN 上久經考驗的模組，不要自己手刻。
