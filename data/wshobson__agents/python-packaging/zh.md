---
name: python-packaging
description: 用適當的專案結構、setup.py/pyproject.toml 建立可發布的 Python 套件，並發布到 PyPI。在打包 Python 函式庫、建立 CLI 工具或散布 Python 程式碼時使用。
---

# Python Packaging

用現代的打包工具、pyproject.toml 建立、組織並散布 Python 套件，以及發布到 PyPI 的完整指南。

## When to Use This Skill

- 建立要散布的 Python 函式庫
- 建構帶有 entry point 的命令列工具
- 把套件發布到 PyPI 或私有 repository
- 建立 Python 專案結構
- 建立帶有相依套件、可安裝的套件
- 建置 wheel 與原始碼發行版
- Python 套件的版本控管與發布
- 建立 namespace package
- 實作套件 metadata 與 classifier

## Core Concepts

### 1. Package Structure

- **Source layout**：`src/package_name/`（推薦）
- **Flat layout**：`package_name/`（較簡單，但彈性較差）
- **套件 metadata**：pyproject.toml、setup.py 或 setup.cfg
- **發行格式**：wheel (.whl) 與原始碼發行版 (.tar.gz)

### 2. Modern Packaging Standards

- **PEP 517/518**：建置系統的需求
- **PEP 621**：pyproject.toml 中的 metadata
- **PEP 660**：可編輯安裝
- **pyproject.toml**：單一的設定來源

### 3. Build Backends

- **setuptools**：傳統、廣泛使用
- **hatchling**：現代、有明確主張
- **flit**：輕量，適用於純 Python
- **poetry**：相依管理 + 打包

### 4. Distribution

- **PyPI**：Python Package Index（公開）
- **TestPyPI**：正式發布前的測試
- **私有 repository**：JFrog、AWS CodeArtifact 等

## Quick Start

### Minimal Package Structure

```
my-package/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── module.py
└── tests/
    └── test_module.py
```

### Minimal pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "0.1.0"
description = "A short description"
authors = [{name = "Your Name", email = "you@example.com"}]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=22.0",
]
```

## Package Structure Patterns

### Pattern 1: Source Layout (Recommended)

```
my-package/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       ├── utils.py
│       └── py.typed          # For type hints
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_utils.py
└── docs/
    └── index.md
```

**優點：**

- 避免不小心從原始碼 import
- 測試的 import 更乾淨
- 隔離性更好

**source layout 用的 pyproject.toml：**

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

### Pattern 2: Flat Layout

```
my-package/
├── pyproject.toml
├── README.md
├── my_package/
│   ├── __init__.py
│   └── module.py
└── tests/
    └── test_module.py
```

**比較簡單，但：**

- 不用安裝就能 import 套件
- 對函式庫來說比較不專業

### Pattern 3: Multi-Package Project

```
project/
├── pyproject.toml
├── packages/
│   ├── package-a/
│   │   └── src/
│   │       └── package_a/
│   └── package-b/
│       └── src/
│           └── package_b/
└── tests/
```

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。
