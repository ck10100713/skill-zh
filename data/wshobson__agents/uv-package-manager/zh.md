---
name: uv-package-manager
description: 精通 uv 套件管理工具，用於快速的 Python 相依套件管理、虛擬環境和現代 Python 專案工作流程。設定 Python 專案、管理相依套件，或用 uv 最佳化 Python 開發流程時使用。
---

# UV Package Manager

使用 uv 的完整指南。uv 是用 Rust 寫的、極快的 Python 套件安裝與解析工具，用於現代 Python 專案管理和相依套件工作流程。

## When to Use This Skill

- 快速建立新的 Python 專案
- 比 pip 更快地管理 Python 相依套件
- 建立並管理虛擬環境
- 安裝 Python 直譯器
- 有效率地解決相依套件衝突
- 從 pip/pip-tools/poetry 遷移
- 加速 CI/CD 流水線
- 管理 monorepo 的 Python 專案
- 使用 lockfile 做可重現的建置
- 最佳化含有 Python 相依套件的 Docker 建置

## Core Concepts

### 1. What is uv?

- **Ultra-fast package installer**：比 pip 快 10-100 倍
- **Written in Rust**：善用 Rust 的效能
- **Drop-in pip replacement**：相容 pip 的工作流程
- **Virtual environment manager**：建立並管理 venv
- **Python installer**：下載並管理 Python 版本
- **Resolver**：進階的相依套件解析
- **Lockfile support**：可重現的安裝

### 2. Key Features

- 極快的安裝速度
- 靠全域快取節省磁碟空間
- 相容 pip、pip-tools、poetry
- 完整的相依套件解析
- 跨平台支援（Linux、macOS、Windows）
- 安裝時不需要有 Python
- 內建虛擬環境支援

### 3. UV vs Traditional Tools

- **vs pip**：快 10-100 倍，解析器更好
- **vs pip-tools**：更快、更簡單、使用體驗更好
- **vs poetry**：更快、限制較少、更輕量
- **vs conda**：更快、專注在 Python

## Installation

### Quick Install

```bash
# Using Homebrew (macOS or Linux)
brew install uv

# Using Cargo (if you have Rust)
cargo install --locked uv
```

在 Windows 上用 WinGet：

```powershell
winget install --id=astral-sh.uv -e
```

其他支援的安裝方式，請看[官方安裝指南](https://docs.astral.sh/uv/getting-started/installation/)。

### Verify Installation

```bash
uv --version
# uv 0.x.x
```

## Quick Start

### Create a New Project

```bash
# Create new project with virtual environment
uv init my-project
cd my-project

# Or create in current directory
uv init .

# Initialize creates:
# - .python-version (Python version)
# - pyproject.toml (project config)
# - README.md
# - .gitignore
```

### Install Dependencies

```bash
# Install packages (creates venv if needed)
uv add requests pandas

# Install dev dependencies
uv add --dev pytest black ruff

# Install from requirements.txt
uv pip install -r requirements.txt

# Install from pyproject.toml
uv sync
```

## Virtual Environment Management

### Pattern 1: Creating Virtual Environments

```bash
# Create virtual environment with uv
uv venv

# Create with specific Python version
uv venv --python 3.12

# Create with custom name
uv venv my-env

# Create with system site packages
uv venv --system-site-packages

# Specify location
uv venv /path/to/venv
```

### Pattern 2: Activating Virtual Environments

```bash
# Linux/macOS
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Or use uv run (no activation needed)
uv run python script.py
uv run pytest
```

### Pattern 3: Using uv run

```bash
# Run Python script (auto-activates venv)
uv run python app.py

# Run installed CLI tool
uv run black .
uv run pytest

# Run with specific Python version
uv run --python 3.11 python script.py

# Pass arguments
uv run python script.py --arg value
```

## Package Management

### Pattern 4: Adding Dependencies

```bash
# Add package (adds to pyproject.toml)
uv add requests

# Add with version constraint
uv add "django>=4.0,<5.0"

# Add multiple packages
uv add numpy pandas matplotlib

# Add dev dependency
uv add --dev pytest pytest-cov

# Add optional dependency group
uv add --optional docs sphinx

# Add from git
uv add git+https://github.com/user/repo.git

# Add from git with specific ref
uv add git+https://github.com/user/repo.git@v1.0.0

# Add from local path
uv add ./local-package

# Add editable local package
uv add -e ./local-package
```

### Pattern 5: Removing Dependencies

```bash
# Remove package
uv remove requests

# Remove dev dependency
uv remove --dev pytest

# Remove multiple packages
uv remove numpy pandas matplotlib
```

### Pattern 6: Upgrading Dependencies

```bash
# Upgrade specific package
uv add --upgrade requests

# Upgrade all packages
uv sync --upgrade

# Upgrade package to latest
uv add --upgrade requests

# Show what would be upgraded
uv tree --outdated
```

### Pattern 7: Locking Dependencies

```bash
# Generate uv.lock file
uv lock

# Update lock file
uv lock --upgrade

# Lock without installing
uv lock --no-install

# Lock specific package
uv lock --upgrade-package requests
```

## Python Version Management

### Pattern 8: Installing Python Versions

```bash
# Install Python version
uv python install 3.12

# Install multiple versions
uv python install 3.11 3.12 3.13

# Install latest version
uv python install

# List installed versions
uv python list

# Find available versions
uv python list --all-versions
```

### Pattern 9: Setting Python Version

```bash
# Set Python version for project
uv python pin 3.12

# This creates/updates .python-version file

# Use specific Python version for command
uv --python 3.11 run python script.py

# Create venv with specific version
uv venv --python 3.12
```

## Project Configuration

### Pattern 10: pyproject.toml with uv

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]
docs = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    # Additional dev dependencies managed by uv
]

[tool.uv.sources]
# Custom package sources
my-package = { git = "https://github.com/user/repo.git" }
```

### Pattern 11: Using uv with Existing Projects

```bash
# Migrate from requirements.txt
uv add -r requirements.txt

# Migrate from poetry
# Already have pyproject.toml, just use:
uv sync

# Export to requirements.txt
uv pip freeze > requirements.txt

# Export with hashes
uv pip freeze --require-hashes > requirements.txt
```

進階工作流程（包含 Docker 整合、lockfile 管理、效能最佳化、工具比較、常見工作流程、工具整合、疑難排解、最佳實務、遷移指南和指令參考），請看 [references/advanced-patterns.md](references/advanced-patterns.md)
