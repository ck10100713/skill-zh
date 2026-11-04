---
name: perl-testing
description: Perl 測試模式，涵蓋 Test2::V0、Test::More、prove runner、mocking、用 Devel::Cover 量測 coverage，以及 TDD 方法論。用 Test2::V0 或 Test::More 寫 Perl 測試，或量測 coverage 時使用。
metadata:
  origin: ECC
---

# Perl 測試模式

用 Test2::V0、Test::More、prove 和 TDD 方法論，替 Perl 應用程式建立完整的測試策略。

## 何時啟用

- 撰寫新的 Perl 程式碼（走 TDD：red、green、refactor）
- 替 Perl 模組或應用程式設計測試套件
- Review Perl 的測試 coverage
- 建置 Perl 的測試基礎設施
- 把測試從 Test::More 遷移到 Test2::V0
- Debug 失敗的 Perl 測試

## TDD 工作流程

一律照 RED-GREEN-REFACTOR 的循環走。

```perl
# Step 1: RED — 先寫一個會失敗的測試
# t/unit/calculator.t
use v5.36;
use Test2::V0;

use lib 'lib';
use Calculator;

subtest 'addition' => sub {
    my $calc = Calculator->new;
    is($calc->add(2, 3), 5, 'adds two numbers');
    is($calc->add(-1, 1), 0, 'handles negatives');
};

done_testing;

# Step 2: GREEN — 寫最小的實作
# lib/Calculator.pm
package Calculator;
use v5.36;
use Moo;

sub add($self, $a, $b) {
    return $a + $b;
}

1;

# Step 3: REFACTOR — 在測試保持綠燈的情況下改善
# 執行：prove -lv t/unit/calculator.t
```

## Test::More 基礎

Perl 的標準測試模組，用得很廣，隨 core 一起附帶。

### 基本斷言

```perl
use v5.36;
use Test::More;

# 事先宣告 plan，或用 done_testing
# plan tests => 5;  # 固定的 plan（選用）

# 相等
is($result, 42, 'returns correct value');
isnt($result, 0, 'not zero');

# 布林
ok($user->is_active, 'user is active');
ok(!$user->is_banned, 'user is not banned');

# 深層比較
is_deeply(
    $got,
    { name => 'Alice', roles => ['admin'] },
    'returns expected structure'
);

# Pattern 比對
like($error, qr/not found/i, 'error mentions not found');
unlike($output, qr/password/, 'output hides password');

# 型別檢查
isa_ok($obj, 'MyApp::User');
can_ok($obj, 'save', 'delete');

done_testing;
```

### SKIP 與 TODO

```perl
use v5.36;
use Test::More;

# 有條件地跳過測試
SKIP: {
    skip 'No database configured', 2 unless $ENV{TEST_DB};

    my $db = connect_db();
    ok($db->ping, 'database is reachable');
    is($db->version, '15', 'correct PostgreSQL version');
}

# 標記預期會失敗的測試
TODO: {
    local $TODO = 'Caching not yet implemented';
    is($cache->get('key'), 'value', 'cache returns value');
}

done_testing;
```

## Test2::V0 現代框架

Test2::V0 是 Test::More 的現代替代品：斷言更豐富、診斷訊息更好、可以擴充。

### 為什麼選 Test2？

- 用 hash/array builder 做更強的深層比較
- 失敗時的診斷輸出更好
- Subtest 的作用域更乾淨
- 可透過 Test2::Tools::* plugin 擴充
- 向下相容 Test::More 的測試

### 用 Builder 做深層比較

```perl
use v5.36;
use Test2::V0;

# Hash builder，檢查部分結構
is(
    $user->to_hash,
    hash {
        field name  => 'Alice';
        field email => match(qr/\@example\.com$/);
        field age   => validator(sub { $_ >= 18 });
        # 忽略其他欄位
        etc();
    },
    'user has expected fields'
);

# Array builder
is(
    $result,
    array {
        item 'first';
        item match(qr/^second/);
        item DNE();  # Does Not Exist，確認沒有多餘的項目
    },
    'result matches expected list'
);

# Bag，不看順序的比較
is(
    $tags,
    bag {
        item 'perl';
        item 'testing';
        item 'tdd';
    },
    'has all required tags regardless of order'
);
```

### Subtests

```perl
use v5.36;
use Test2::V0;

subtest 'User creation' => sub {
    my $user = User->new(name => 'Alice', email => 'alice@example.com');
    ok($user, 'user object created');
    is($user->name, 'Alice', 'name is set');
    is($user->email, 'alice@example.com', 'email is set');
};

subtest 'User validation' => sub {
    my $warnings = warns {
        User->new(name => '', email => 'bad');
    };
    ok($warnings, 'warns on invalid data');
};

done_testing;
```

### 用 Test2 測試例外

```perl
use v5.36;
use Test2::V0;

# 測試程式碼會 die
like(
    dies { divide(10, 0) },
    qr/Division by zero/,
    'dies on division by zero'
);

# 測試程式碼不會 die
ok(lives { divide(10, 2) }, 'division succeeds') or note($@);

# 組合寫法
subtest 'error handling' => sub {
    ok(lives { parse_config('valid.json') }, 'valid config parses');
    like(
        dies { parse_config('missing.json') },
        qr/Cannot open/,
        'missing file dies with message'
    );
};

done_testing;
```

## 測試組織與 prove

### 目錄結構

```text
t/
├── 00-load.t              # 確認模組能編譯
├── 01-basic.t             # 核心功能
├── unit/
│   ├── config.t           # 依模組分的單元測試
│   ├── user.t
│   └── util.t
├── integration/
│   ├── database.t
│   └── api.t
├── lib/
│   └── TestHelper.pm      # 共用的測試工具
└── fixtures/
    ├── config.json        # 測試資料檔
    └── users.csv
```

### prove 指令

```bash
# 執行所有測試
prove -l t/

# 詳細輸出
prove -lv t/

# 執行特定測試
prove -lv t/unit/user.t

# 遞迴搜尋
prove -lr t/

# 平行執行（8 個 job）
prove -lr -j8 t/

# 只重跑上次失敗的測試
prove -l --state=failed t/

# 彩色輸出並顯示計時
prove -l --color --timer t/

# 給 CI 用的 TAP 輸出
prove -l --formatter TAP::Formatter::JUnit t/ > results.xml
```

### .proverc 設定

```text
-l
--color
--timer
-r
-j4
--state=save
```

## Fixture 與 Setup/Teardown

### Subtest 隔離

```perl
use v5.36;
use Test2::V0;
use File::Temp qw(tempdir);
use Path::Tiny;

subtest 'file processing' => sub {
    # Setup
    my $dir = tempdir(CLEANUP => 1);
    my $file = path($dir, 'input.txt');
    $file->spew_utf8("line1\nline2\nline3\n");

    # Test
    my $result = process_file("$file");
    is($result->{line_count}, 3, 'counts lines');

    # Teardown 會自動發生 (CLEANUP => 1)
};
```

### 共用的測試 Helper

把可重複使用的 helper 放在 `t/lib/TestHelper.pm`，用 `use lib 't/lib'` 載入。透過 `Exporter` 匯出像 `create_test_db()`、`create_temp_dir()` 和 `fixture_path()` 這類工廠函式。

## Mocking

### Test::MockModule

```perl
use v5.36;
use Test2::V0;
use Test::MockModule;

subtest 'mock external API' => sub {
    my $mock = Test::MockModule->new('MyApp::API');

    # Good: mock 回傳受控的資料
    $mock->mock(fetch_user => sub ($self, $id) {
        return { id => $id, name => 'Mock User', email => 'mock@test.com' };
    });

    my $api = MyApp::API->new;
    my $user = $api->fetch_user(42);
    is($user->{name}, 'Mock User', 'returns mocked user');

    # 驗證呼叫次數
    my $call_count = 0;
    $mock->mock(fetch_user => sub { $call_count++; return {} });
    $api->fetch_user(1);
    $api->fetch_user(2);
    is($call_count, 2, 'fetch_user called twice');

    # $mock 離開作用域時會自動還原
};

# Bad: monkey-patch 之後沒有還原
# *MyApp::API::fetch_user = sub { ... };  # 絕對不要，會洩漏到其他測試
```

要輕量的 mock 物件，用 `Test::MockObject` 建立可注入的 test double，用 `->mock()` 設定行為，用 `->called_ok()` 驗證呼叫。

## 用 Devel::Cover 量測 Coverage

### 執行 Coverage

```bash
# 基本的 coverage 報告
cover -test

# 或一步一步來
perl -MDevel::Cover -Ilib t/unit/user.t
cover

# HTML 報告
cover -report html
open cover_db/coverage.html

# 指定門檻
cover -test -report text | grep 'Total'

# 適合 CI：低於門檻就失敗
cover -test && cover -report text -select '^lib/' \
  | perl -ne 'if (/Total.*?(\d+\.\d+)/) { exit 1 if $1 < 80 }'
```

### 整合測試

資料庫測試用 in-memory SQLite，API 測試則 mock HTTP::Tiny。

```perl
use v5.36;
use Test2::V0;
use DBI;

subtest 'database integration' => sub {
    my $dbh = DBI->connect('dbi:SQLite:dbname=:memory:', '', '', {
        RaiseError => 1,
    });
    $dbh->do('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)');

    $dbh->prepare('INSERT INTO users (name) VALUES (?)')->execute('Alice');
    my $row = $dbh->selectrow_hashref('SELECT * FROM users WHERE name = ?', undef, 'Alice');
    is($row->{name}, 'Alice', 'inserted and retrieved user');
};

done_testing;
```

## 最佳實踐

### 要做

- **走 TDD**：先寫測試再寫實作（red-green-refactor）
- **用 Test2::V0**：斷言更現代，診斷更好
- **用 subtest**：把相關的斷言分組，隔離狀態
- **Mock 外部依賴**：網路、資料庫、檔案系統
- **用 `prove -l`**：一定要把 lib/ 加進 `@INC`
- **測試名稱要講清楚**：`'user login with invalid password fails'`
- **測試邊界情況**：空字串、undef、零、邊界值
- **目標 80% 以上的 coverage**：重點放在業務邏輯的路徑
- **讓測試保持快速**：mock I/O，用 in-memory 資料庫

### 不要做

- **不要測實作細節**：測行為和輸出，不要測內部
- **不要在 subtest 之間共用狀態**：每個 subtest 都要獨立
- **不要漏掉 `done_testing`**：它確保所有預定的測試都有跑
- **不要 over-mock**：只 mock 邊界，不要 mock 被測的程式碼
- **新專案不要用 `Test::More`**：優先選 Test2::V0
- **不要無視測試失敗**：merge 之前所有測試都必須通過
- **不要測 CPAN 模組**：相信函式庫自己會運作正確
- **不要寫脆弱的測試**：避免過度特定的字串比對

## 速查

| 任務 | 指令 / 模式 |
|---|---|
| 執行所有測試 | `prove -lr t/` |
| 詳細輸出執行單一測試 | `prove -lv t/unit/user.t` |
| 平行執行測試 | `prove -lr -j8 t/` |
| Coverage 報告 | `cover -test && cover -report html` |
| 測試相等 | `is($got, $expected, 'label')` |
| 深層比較 | `is($got, hash { field k => 'v'; etc() }, 'label')` |
| 測試例外 | `like(dies { ... }, qr/msg/, 'label')` |
| 測試沒有例外 | `ok(lives { ... }, 'label')` |
| Mock 一個 method | `Test::MockModule->new('Pkg')->mock(m => sub { ... })` |
| 跳過測試 | `SKIP: { skip 'reason', $count unless $cond; ... }` |
| TODO 測試 | `TODO: { local $TODO = 'reason'; ... }` |

## 常見陷阱

### 忘了 `done_testing`

```perl
# Bad: 測試檔會跑，但沒驗證所有測試都有執行
use Test2::V0;
is(1, 1, 'works');
# 少了 done_testing，如果測試程式碼被跳過，bug 會悄悄溜過去

# Good: 一律用 done_testing 收尾
use Test2::V0;
is(1, 1, 'works');
done_testing;
```

### 漏了 `-l` 旗標

```bash
# Bad: 找不到 lib/ 裡的模組
prove t/unit/user.t
# Can't locate MyApp/User.pm in @INC

# Good: 把 lib/ 加進 @INC
prove -l t/unit/user.t
```

### Over-Mocking

要 mock 的是*依賴*，不是被測的程式碼。如果你的測試只是在驗證 mock 回傳你叫它回傳的東西，那就等於什麼都沒測。

### 測試污染

在 subtest 裡面用 `my` 變數，絕對不要用 `our`，避免狀態在測試之間洩漏。

**記住**：測試是你的安全網。要讓它們保持快速、聚焦、互相獨立。新專案用 Test2::V0，執行用 prove，要對 coverage 負責就用 Devel::Cover。
