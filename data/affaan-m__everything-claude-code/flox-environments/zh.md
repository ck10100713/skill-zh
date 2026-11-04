---
name: flox-environments
description: "用 Flox（以 Nix 為基礎的宣告式環境管理工具）建立可重現、跨平台（macOS/Linux）的開發環境。適用於設定專案工具鏈、安裝系統層級依賴（編譯器、資料庫、原生函式庫）、為團隊鎖定確切的套件版本、新人 onboarding、跑本機服務（PostgreSQL、Redis、Kafka），或解決「在我電腦上明明可以」的問題，也包含需要在專案範圍內裝工具、又不想用 sudo 的 agent / vibe-coding 場景。使用者提到 .flox/、manifest.toml、flox activate 或 FloxHub 時也適用。"
metadata:
  origin: Flox
---

# Flox Environments

Flox 用一份 TOML manifest 定義可重現的開發環境。團隊裡每個人拿到的套件、工具、設定都一模一樣，macOS 和 Linux 通用，不需要容器或 VM。底層是 Nix，可用的套件超過 150,000 個。

## When to Activate

使用者碰到環境管理問題就用這個 skill，就算他沒提到 Flox 也一樣。符合下面這些情況，Flox 就是對的工具：

- 專案除了語言本身的依賴，還需要**系統層級的套件**（編譯器、資料庫、CLI 工具）
- **可重現性很重要**：設定要在隊友的電腦、CI、或是剛重灌的筆電上表現一致
- 使用者需要**多個工具共存**，例如 Python 3.11 + PostgreSQL 16 + Redis + Node.js 放在同一個環境
- 需要**跨平台支援**（同一份設定同時跑 macOS 和 Linux）
- **AI agent 需要自己裝工具**：Flox 讓 agent 在專案範圍的環境裡加套件，不用 sudo、不污染系統、也不會被 sandbox 限制擋住

如果使用者只需要單一語言的 runtime、沒有系統依賴，一般的工具（單用 nvm、pyenv、rustup）可能就夠了。如果需要完整的作業系統層級隔離，容器可能更合適。Flox 卡在中間那個甜蜜點：宣告式、可重現，又沒有容器的額外負擔。

**前置條件：** 要先裝好 Flox，macOS、Linux、Docker 的安裝方式見 [flox.dev/docs](https://flox.dev/docs/install-flox/install/)。

## Core Concepts

Flox 環境定義在 `.flox/env/manifest.toml`，用 `flox activate` 啟用。manifest 會宣告套件、環境變數、設定用的 hook 和 shell 設定，也就是在任何地方重現這個環境所需的一切。

**關鍵路徑：**
- `.flox/env/manifest.toml`：環境定義（要 commit）
- `$FLOX_ENV`：已安裝套件的 runtime 路徑（像 `/usr`，裡面有 `bin/`、`lib/`、`include/`）
- `$FLOX_ENV_CACHE`：持久的本機儲存空間，放快取、venv、資料（重建環境後仍然保留）
- `$FLOX_ENV_PROJECT`：專案根目錄（`.flox/` 所在的位置）

## Essential Commands

```bash
flox init                       # 建立新環境
flox search <package> [--all]   # 搜尋套件
flox show <package>             # 顯示可用版本
flox install <package>          # 加一個套件
flox list                       # 列出已安裝的套件
flox activate                   # 進入環境
flox activate -- <cmd>          # 在環境裡跑一個指令，不開 subshell
flox edit                       # 互動式編輯 manifest
```

## Manifest Structure

```toml
# .flox/env/manifest.toml

[install]
# 要安裝的套件，環境的核心
ripgrep.pkg-path = "ripgrep"
jq.pkg-path = "jq"

[vars]
# 靜態環境變數
DATABASE_URL = "postgres://localhost:5432/myapp"

[hook]
# 非互動式的設定腳本（每次 activate 都會跑）
on-activate = """
  echo "Environment ready"
"""

[profile]
# shell function 和 alias（互動式 shell 可用）
common = """
  alias dev="npm run dev"
"""

[options]
# 支援的平台
systems = ["x86_64-linux", "aarch64-linux", "x86_64-darwin", "aarch64-darwin"]
```

## Package Installation Patterns

### Basic Installation

```toml
[install]
nodejs.pkg-path = "nodejs"
python.pkg-path = "python311"
rustup.pkg-path = "rustup"
```

### Version Pinning

```toml
[install]
nodejs.pkg-path = "nodejs"
nodejs.version = "^20.0"          # Semver 範圍：最新的 20.x

postgres.pkg-path = "postgresql"
postgres.version = "16.2"         # 精確版本
```

### Platform-Specific Packages

```toml
[install]
# 只有 Linux 用的工具
valgrind.pkg-path = "valgrind"
valgrind.systems = ["x86_64-linux", "aarch64-linux"]

# macOS frameworks
Security.pkg-path = "darwin.apple_sdk.frameworks.Security"
Security.systems = ["x86_64-darwin", "aarch64-darwin"]

# macOS 上的 GNU 工具（BSD 預設版本行為不同的地方）
coreutils.pkg-path = "coreutils"
coreutils.systems = ["x86_64-darwin", "aarch64-darwin"]
```

### Resolving Package Conflicts

兩個套件裝了同名的 binary 時，用 `priority`（數字小的贏）：

```toml
[install]
gcc.pkg-path = "gcc12"
gcc.priority = 3

clang.pkg-path = "clang_18"
clang.priority = 5               # 檔案衝突時 gcc 贏
```

用 `pkg-group` 把需要一起解析版本的套件分成一組：

```toml
[install]
python.pkg-path = "python311"
python.pkg-group = "python-stack"

pip.pkg-path = "python311Packages.pip"
pip.pkg-group = "python-stack"    # 跟 python 一起解析
```

## Language-Specific Recipes

### Python with uv

```toml
[install]
python.pkg-path = "python311"
uv.pkg-path = "uv"

[vars]
UV_CACHE_DIR = "$FLOX_ENV_CACHE/uv-cache"
PIP_CACHE_DIR = "$FLOX_ENV_CACHE/pip-cache"

[hook]
on-activate = """
  venv="$FLOX_ENV_CACHE/venv"
  if [ ! -d "$venv" ]; then
    uv venv "$venv" --python python3
  fi
  if [ -f "$venv/bin/activate" ]; then
    source "$venv/bin/activate"
  fi

  if [ -f requirements.txt ] && [ ! -f "$FLOX_ENV_CACHE/.deps_installed" ]; then
    uv pip install --python "$venv/bin/python" -r requirements.txt --quiet
    touch "$FLOX_ENV_CACHE/.deps_installed"
  fi
"""
```

### Node.js

```toml
[install]
nodejs.pkg-path = "nodejs"
nodejs.version = "^20.0"

[hook]
on-activate = """
  if [ -f package.json ] && [ ! -d node_modules ]; then
    npm install --silent
  fi
"""
```

### Rust

```toml
[install]
rustup.pkg-path = "rustup"
pkg-config.pkg-path = "pkg-config"
openssl.pkg-path = "openssl"

[vars]
RUSTUP_HOME = "$FLOX_ENV_CACHE/rustup"
CARGO_HOME = "$FLOX_ENV_CACHE/cargo"

[profile]
common = """
  export PATH="$CARGO_HOME/bin:$PATH"
"""
```

### Go

```toml
[install]
go.pkg-path = "go"
gopls.pkg-path = "gopls"
delve.pkg-path = "delve"

[vars]
GOPATH = "$FLOX_ENV_CACHE/go"
GOBIN = "$FLOX_ENV_CACHE/go/bin"

[profile]
common = """
  export PATH="$GOBIN:$PATH"
"""
```

### C/C++

```toml
[install]
gcc.pkg-path = "gcc13"
gcc.pkg-group = "compilers"

# 重要：只裝 gcc 不會提供 libstdc++ 的 header，要另外裝 gcc-unwrapped
gcc-unwrapped.pkg-path = "gcc-unwrapped"
gcc-unwrapped.pkg-group = "libraries"

cmake.pkg-path = "cmake"
cmake.pkg-group = "build"

gnumake.pkg-path = "gnumake"
gnumake.pkg-group = "build"

gdb.pkg-path = "gdb"
gdb.systems = ["x86_64-linux", "aarch64-linux"]
```

## Hooks and Profile

### Hooks — Non-Interactive Setup

Hook 每次 activate 都會跑，要保持快速而且冪等（idempotent）。經驗法則：**要自動發生的事放 `[hook]`，要讓使用者自己打指令的放 `[profile]`。**

```toml
[hook]
on-activate = """
  setup_database() {
    if [ ! -d "$FLOX_ENV_CACHE/pgdata" ]; then
      initdb -D "$FLOX_ENV_CACHE/pgdata" --no-locale --encoding=UTF8
    fi
  }
  setup_database
"""
```

### Profile — Interactive Shell Configuration

Profile 裡的程式碼在使用者的 shell session 裡可以直接用。

```toml
[profile]
common = """
  dev() { npm run dev; }
  test() { npm run test -- "$@"; }
"""
```

## Anti-Patterns

### Absolute Paths

```toml
# BAD：換一台機器就壞
[vars]
PROJECT_DIR = "/home/alice/projects/myapp"

# GOOD：用 Flox 的環境變數
[vars]
PROJECT_DIR = "$FLOX_ENV_PROJECT"
```

### Using exit in Hooks

```toml
# BAD：會把 shell 殺掉
[hook]
on-activate = """
  if [ ! -f config.json ]; then
    echo "Missing config"
    exit 1
  fi
"""

# GOOD：用 return 離開 hook，不要用 exit
[hook]
on-activate = """
  if [ ! -f config.json ]; then
    echo "Missing config — run setup first"
    return 1
  fi
"""
```

### Storing Secrets in Manifest

```toml
# BAD：manifest 會被 commit 進 git
[vars]
API_KEY = "<set-at-runtime>"

# GOOD：參照外部設定，或在執行時傳入
# 用法：API_KEY="<your-api-key>" flox activate
[vars]
API_KEY = "${API_KEY:-}"
```

### Slow Hooks Without Idempotency Guards

```toml
# BAD：每次 activate 都重裝
[hook]
on-activate = """
  pip install -r requirements.txt
"""

# GOOD：裝過就跳過
[hook]
on-activate = """
  if [ ! -f "$FLOX_ENV_CACHE/.deps_installed" ]; then
    uv pip install -r requirements.txt --quiet
    touch "$FLOX_ENV_CACHE/.deps_installed"
  fi
"""
```

### Putting User Commands in Hooks

```toml
# BAD：hook 裡的 function 在互動式 shell 裡用不到
[hook]
on-activate = """
  deploy() { kubectl apply -f k8s/; }
"""

# GOOD：給使用者呼叫的 function 用 [profile]
[profile]
common = """
  deploy() { kubectl apply -f k8s/; }
"""
```

## Full-Stack Example

一個 Python API 加 PostgreSQL 的完整環境：

```toml
[install]
python.pkg-path = "python311"
uv.pkg-path = "uv"
postgresql.pkg-path = "postgresql_16"
redis.pkg-path = "redis"
jq.pkg-path = "jq"
curl.pkg-path = "curl"

[vars]
UV_CACHE_DIR = "$FLOX_ENV_CACHE/uv-cache"
DATABASE_URL = "postgres://localhost:5432/myapp"
REDIS_URL = "redis://localhost:6379"

[hook]
on-activate = """
  if [ ! -d "$FLOX_ENV_CACHE/pgdata" ]; then
    initdb -D "$FLOX_ENV_CACHE/pgdata" --no-locale --encoding=UTF8
  fi

  venv="$FLOX_ENV_CACHE/venv"
  if [ ! -d "$venv" ]; then
    uv venv "$venv" --python python3
  fi
  if [ -f "$venv/bin/activate" ]; then
    source "$venv/bin/activate"
  fi

  if [ -f requirements.txt ] && [ ! -f "$FLOX_ENV_CACHE/.deps_installed" ]; then
    uv pip install --python "$venv/bin/python" -r requirements.txt --quiet
    touch "$FLOX_ENV_CACHE/.deps_installed"
  fi
"""

[profile]
common = """
  serve() { uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; }
  migrate() { alembic upgrade head; }
"""

[services]
postgres.command = "postgres -D $FLOX_ENV_CACHE/pgdata -k $FLOX_ENV_CACHE"
redis.command = "redis-server --port 6379 --daemonize no"

[options]
systems = ["x86_64-linux", "aarch64-linux", "x86_64-darwin", "aarch64-darwin"]
```

連同服務一起啟用：`flox activate --start-services`

## Environment Sharing

Flox 環境跟 git 是原生搭配的。把 `.flox/` 目錄 commit 進去，每個協作者拿到的環境都一樣：

```bash
git add .flox/
git commit -m "Add Flox environment"
# 隊友只要執行：
git clone <repo> && cd <repo> && flox activate
```

要在多個專案之間共用基底環境，就 push 到 FloxHub：

```bash
flox push                         # 把環境 push 到 FloxHub
flox activate -r owner/env-name   # 在任何地方啟用遠端環境
```

用 `[include]` 組合環境：

```toml
[include]
base.floxhub = "myorg/python-base"

[install]
# 在 base 之上加專案專屬的東西
fastapi.pkg-path = "python311Packages.fastapi"
```

## AI-Assisted and Vibe Coding

Flox 很適合 AI 輔助開發和 vibe coding 的工作流程。AI agent 需要目前環境裡沒有的工具（編譯器、資料庫、linter、CLI 小工具）時，可以直接加進專案的 Flox manifest，不用 sudo、不會污染系統套件，也不會撞到 sandbox 限制。

**為什麼這對 agent 很重要：**
- **不需要 sudo**：`flox install` 完全在 user space 運作，agent 不用提權就能加套件
- **限定在專案範圍**：套件只裝進專案環境，不是全域，所以不同專案可以用不同版本而不衝突
- **對 sandbox 友善**：在 sandbox 或受限環境裡跑的 agent，照樣能透過 Flox 裝到需要的工具
- **可還原**：每個改動都記錄在 `manifest.toml`，不要的套件可以乾淨移除，不留系統殘渣
- **可重現**：agent 設好的環境會 commit 進 git，每個人拿到的都一樣

**Agent 工作流程模式：**

```bash
# Agent 發現自己需要某個工具（例如處理 JSON 要用 jq）
flox search jq                    # 確認套件存在
flox install jq                   # 裝進專案環境

# 或是想要更多控制，就直接編輯 manifest
tmp_manifest="$(mktemp)"
flox list -c > "$tmp_manifest"
# 把套件加進 [install] 區段，然後套用
flox edit -f "$tmp_manifest"

# 在有該工具的環境下跑指令
flox activate -- jq '.results[]' data.json
```

所以只要是 Claude Code 或其他 AI agent 需要臨時準備專案工具的工作流程，Flox 都很合適。

## Debugging

```bash
flox list -c                      # 顯示原始 manifest
flox activate -- which python     # 檢查解析到哪個 binary
flox activate -- env | grep FLOX  # 看 Flox 的環境變數
flox search <package> --all       # 範圍更廣的套件搜尋（區分大小寫）
```

**常見問題：**
- **找不到套件：** 搜尋區分大小寫，試試 `flox search --all`
- **套件之間檔案衝突：** 在該贏的那個套件上加 `priority`
- **Hook 失敗：** 用 `return` 不要用 `exit`；用 `${FLOX_ENV_CACHE:-}` 做保護
- **依賴過期：** 刪掉 `$FLOX_ENV_CACHE/.deps_installed` 這個標記檔

## Related Skills

下面這些 skill 屬於 [Flox Claude Code plugin](https://github.com/flox/flox-skills)，整合得更深：

- **flox**：環境、服務與資料庫、build 與打包、容器、FloxHub 發佈、環境組合與分享，以及 CUDA/GPU 開發
- **floxify**：偵測既有 repo 的 runtime、服務和 build 工具，把它導入 Flox
- **flox-debug**：當套件解析不到預期版本時，診斷 catalog 解析問題

更多資訊與安裝請見 [flox.dev/docs](https://flox.dev/docs/install-flox/install/)
