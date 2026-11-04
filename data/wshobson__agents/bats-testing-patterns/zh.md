---
name: bats-testing-patterns
description: 掌握 Bash Automated Testing System（Bats），對 shell script 做完整的測試。在為 shell script、CI/CD pipeline 寫測試，或需要對 shell 工具做測試驅動開發時使用。
---

# Bats 測試模式

用 Bats（Bash Automated Testing System）為 shell script 撰寫完整單元測試的完整指引，包括測試模式、fixture，以及可上線等級的 shell 測試最佳實務。

## 何時使用這個 Skill

- 為 shell script 撰寫單元測試
- 對 script 實作測試驅動開發（TDD）
- 在 CI/CD pipeline 裡架設自動化測試
- 測試邊界情況和錯誤條件
- 驗證在不同 shell 環境下的行為
- 為 script 建構好維護的測試套件
- 為複雜的測試情境建立 fixture
- 測試多種 shell 方言（bash、sh、dash）

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。

## 測試錯誤條件

```bash
#!/usr/bin/env bats

@test "Function fails with missing file" {
    run my_function "/nonexistent/file.txt"
    [ "$status" -ne 0 ]
    [[ "$output" == *"not found"* ]]
}

@test "Function fails with invalid input" {
    run my_function ""
    [ "$status" -ne 0 ]
}

@test "Function fails with permission denied" {
    touch "$TMPDIR/readonly.txt"
    chmod 000 "$TMPDIR/readonly.txt"
    run my_function "$TMPDIR/readonly.txt"
    [ "$status" -ne 0 ]
    chmod 644 "$TMPDIR/readonly.txt"  # Cleanup
}

@test "Function provides helpful error message" {
    run my_function --invalid-option
    [ "$status" -ne 0 ]
    [[ "$output" == *"Usage:"* ]]
}
```

### 測試相依套件

```bash
#!/usr/bin/env bats

setup() {
    # Check for required tools
    if ! command -v jq &>/dev/null; then
        skip "jq is not installed"
    fi

    export SCRIPT="${BATS_TEST_DIRNAME}/../bin/script.sh"
}

@test "JSON parsing works" {
    skip_if ! command -v jq &>/dev/null
    run my_json_parser '{"key": "value"}'
    [ "$status" -eq 0 ]
}
```

### 測試 Shell 相容性

```bash
#!/usr/bin/env bats

@test "Script works in bash" {
    bash "${BATS_TEST_DIRNAME}/../bin/script.sh" arg1
}

@test "Script works in sh (POSIX)" {
    sh "${BATS_TEST_DIRNAME}/../bin/script.sh" arg1
}

@test "Script works in dash" {
    if command -v dash &>/dev/null; then
        dash "${BATS_TEST_DIRNAME}/../bin/script.sh" arg1
    else
        skip "dash not installed"
    fi
}
```

### 平行執行

```bash
#!/usr/bin/env bats

@test "Multiple independent operations" {
    run bash -c 'for i in {1..10}; do
        my_operation "$i" &
    done
    wait'
    [ "$status" -eq 0 ]
}

@test "Concurrent file operations" {
    for i in {1..5}; do
        my_function "$TMPDIR/file$i" &
    done
    wait
    [ -f "$TMPDIR/file1" ]
    [ -f "$TMPDIR/file5" ]
}
```

## 測試輔助模式

### test_helper.sh

```bash
#!/usr/bin/env bash

# Source script under test
export SCRIPT_DIR="${BATS_TEST_DIRNAME%/*}/bin"

# Common test utilities
assert_file_exists() {
    if [ ! -f "$1" ]; then
        echo "Expected file to exist: $1"
        return 1
    fi
}

assert_file_equals() {
    local file="$1"
    local expected="$2"

    if [ ! -f "$file" ]; then
        echo "File does not exist: $file"
        return 1
    fi

    local actual=$(cat "$file")
    if [ "$actual" != "$expected" ]; then
        echo "File contents do not match"
        echo "Expected: $expected"
        echo "Actual: $actual"
        return 1
    fi
}

# Create temporary test directory
setup_test_dir() {
    export TEST_DIR=$(mktemp -d)
}

cleanup_test_dir() {
    rm -rf "$TEST_DIR"
}
```

## 與 CI/CD 整合

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install Bats
        run: |
          npm install --global bats

      - name: Run Tests
        run: |
          bats tests/*.bats

      - name: Run Tests with Tap Reporter
        run: |
          bats tests/*.bats --tap | tee test_output.tap
```

### Makefile 整合

```makefile
.PHONY: test test-verbose test-tap

test:
	bats tests/*.bats

test-verbose:
	bats tests/*.bats --verbose

test-tap:
	bats tests/*.bats --tap

test-parallel:
	bats tests/*.bats --parallel 4

coverage: test
	# Optional: Generate coverage reports
```

## 最佳實務

1. **一個測試只測一件事** - 單一職責原則
2. **用描述性的測試名稱** - 清楚說明在測什麼
3. **測試後要清理** - 一律在 teardown 裡移除暫存檔
4. **成功和失敗的路徑都要測** - 不要只測 happy path
5. **Mock 外部相依** - 隔離被測的單元
6. **複雜的資料用 fixture** - 讓測試更好讀
7. **在 CI/CD 裡跑測試** - 及早抓到 regression
8. **跨 shell 方言測試** - 確保可攜性
9. **讓測試保持快速** - 可以的話平行執行
10. **記錄複雜的測試設定** - 說明不尋常的寫法
