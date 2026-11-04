---
name: continual-learning
description: 在 AI coding agent 裡實作 continual learning 的指南，包含 hook、記憶範圍、反思模式。替 agent 建立學習基礎設施時使用。
---

# Continual Learning for AI Coding Agents

你的 agent 每次換 session 就什麼都忘了。Continual learning 就是來解決這件事。

## The Loop

```
Experience → Capture → Reflect → Persist → Apply
     ↑                                       │
     └───────────────────────────────────────┘
```

## Quick Start

安裝 hook（一步就好）：
```bash
cp -r hooks/continual-learning .github/hooks/
```

第一次開 session 時會自動初始化，不用任何設定。

## Two-Tier Memory

**Global**（`~/.copilot/learnings.db`）：跟著你跑遍所有專案：
- 工具使用模式（哪些工具會失敗、哪些好用）
- 跨專案的慣例
- 一般的 coding 偏好

**Local**（`.copilot-memory/learnings.db`）：只跟著這個 repo：
- 專案專屬的慣例
- 這個 codebase 常犯的錯
- 團隊偏好

## How Learnings Get Stored

### Automatic (via hooks)
hook 會觀察工具的執行結果，偵測失敗模式：
```
Session 1: bash tool fails 4 times → learning stored: "bash frequently fails"
Session 2: hook surfaces that learning at start → agent adjusts approach
```

### Agent-native (via store_memory / SQL)
agent 可以直接寫入 learning：
```sql
INSERT INTO learnings (scope, category, content, source)
VALUES ('local', 'convention', 'This project uses Result<T> not exceptions', 'user_correction');
```

Categories: `pattern`, `mistake`, `preference`, `tool_insight`

### Manual (memory files)
給人看得懂、又能進版控的知識：
```markdown
# .copilot-memory/conventions.md
- Use DefaultAzureCredential for all Azure auth
- Parameter is semantic_configuration_name=, not semantic_configuration=
```

## Compaction

Learning 會隨時間衰退：
- 超過 60 天而且命中次數很少的項目會被清掉
- 高價值的 learning（常被參照的）會一直保留
- 工具 log 7 天後清掉

這樣既不會無限膨脹，又能留下重要的東西。

## Best Practices

1. **一步安裝**：超過 `cp -r` 就沒人會用
2. **範圍要抓對**：工具使用模式放 global，專案慣例放 local
3. **要具體**：`"Use semantic_configuration_name="` 比 `"use the right parameter"` 好
4. **讓它複利成長**：每個 session 進步一點點，幾週下來效果會是指數成長
