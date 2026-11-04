---
name: bazel-build-optimization
description: 為大規模 monorepo 最佳化 Bazel 建置。在設定 Bazel、實作 remote execution，或為企業級程式碼庫最佳化建置效能時使用。
---

# Bazel 建置最佳化

大規模 monorepo 中使用 Bazel 的正式環境模式。

## 何時使用這個 Skill

- 為 monorepo 架設 Bazel
- 設定 remote caching/execution
- 最佳化建置時間
- 撰寫自訂的 Bazel rule
- 除錯建置問題
- 遷移到 Bazel

## 核心概念

### 1. Bazel 架構

```
workspace/
├── WORKSPACE.bazel       # External dependencies
├── .bazelrc              # Build configurations
├── .bazelversion         # Bazel version
├── BUILD.bazel           # Root build file
├── apps/
│   └── web/
│       └── BUILD.bazel
├── libs/
│   └── utils/
│       └── BUILD.bazel
└── tools/
    └── bazel/
        └── rules/
```

### 2. 關鍵概念

| 概念     | 說明                            |
| ----------- | -------------------------------------- |
| **Target**  | 可建置的單元（library、binary、test） |
| **Package** | 含有 BUILD 檔的目錄              |
| **Label**   | Target 的識別名稱 `//path/to:target`   |
| **Rule**    | 定義如何建置一個 target          |
| **Aspect**  | 橫切的建置行為           |

## 範本與詳細的實作範例

完整的範本庫和詳細的實作範例放在 `references/details.md`。需要具體的範本時，讀那個檔案。

## 最佳實務

### 該做的

- **用細粒度的 target** - 快取效果更好
- **固定相依版本** - 可重現的建置
- **啟用 remote caching** - 共享建置產物
- **明智地使用 visibility** - 強制執行架構
- **每個目錄寫一個 BUILD 檔** - 標準慣例

### 不該做的

- **不要用 glob 來列 deps** - 明確比較好
- **不要 commit bazel-\* 目錄** - 加進 .gitignore
- **不要跳過 WORKSPACE 的設定** - 它是建置的基礎
- **不要忽略建置警告** - 那是技術債
