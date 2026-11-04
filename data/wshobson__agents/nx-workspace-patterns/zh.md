---
name: nx-workspace-patterns
description: 設定並優化 Nx monorepo workspace。在建立 Nx、設定專案邊界、優化建置快取或實作 affected 指令時使用。
---

# Nx Workspace Patterns

Nx monorepo 管理的正式環境模式。

## When to Use This Skill

- 建立新的 Nx workspace
- 設定專案邊界
- 用 affected 指令優化 CI
- 實作 remote caching
- 管理專案之間的相依性
- 遷移到 Nx

## Core Concepts

### 1. Nx Architecture

```
workspace/
├── apps/              # Deployable applications
│   ├── web/
│   └── api/
├── libs/              # Shared libraries
│   ├── shared/
│   │   ├── ui/
│   │   └── utils/
│   └── feature/
│       ├── auth/
│       └── dashboard/
├── tools/             # Custom executors/generators
├── nx.json            # Nx configuration
└── workspace.json     # Project configuration
```

### 2. Library Types

| Type            | Purpose                          | Example             |
| --------------- | -------------------------------- | ------------------- |
| **feature**     | 智慧元件、業務邏輯 | `feature-auth`      |
| **ui**          | 純展示元件        | `ui-buttons`        |
| **data-access** | API 呼叫、狀態管理      | `data-access-users` |
| **util**        | 純函式、輔助工具          | `util-formatting`   |
| **shell**       | App 啟動                | `shell-web`         |

## Templates and detailed worked examples

完整的範本庫與詳細的範例放在 `references/details.md`。需要具體範本時，再去讀那個檔案。

## Best Practices

### Do's

- **一致地使用 tag** - 用 module boundaries 強制執行
- **及早啟用快取** - 能大幅節省 CI 時間
- **讓 lib 保持專注** - 單一職責
- **使用 generator** - 確保一致性
- **記錄邊界** - 幫助新進開發者

### Don'ts

- **不要建立循環相依** - 相依圖應該無環
- **不要跳過 affected** - 只測試有變動的部分
- **不要忽略邊界** - 技術債會累積
- **不要切得過細** - 在 lib 的數量上取得平衡
