---
name: agent-eval
description: 在自訂任務上，正面比較 coding agent（Claude Code、Aider、Codex 等），指標包含通過率、成本、時間和一致性。在 coding agent 之間做選擇時，或是 agent 設定的改動需要量測過的通過率、成本和時間，而不是憑印象時使用。
license: MIT
metadata:
  origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Agent Eval Skill

一個輕量的 CLI 工具，在可重現的任務上正面比較 coding agent。每一次「哪個 coding agent 最好？」的比較都是憑感覺在跑，這個工具把它系統化。

## When to Activate

- 在你自己的 codebase 上比較 coding agent（Claude Code、Aider、Codex 等）
- 在採用新工具或新 model 之前，量測 agent 的表現
- 當 agent 更新它的 model 或工具時，跑迴歸檢查
- 為團隊產出有資料支持的 agent 選擇決策

## Installation

> **注意：** 審閱原始碼之後，再從它的 repository 安裝 agent-eval。

## Core Concepts

### YAML Task Definitions

用宣告的方式定義任務。每個任務指定要做什麼、要動哪些檔案，以及怎麼判斷成功：

```yaml
name: add-retry-logic
description: Add exponential backoff retry to the HTTP client
repo: ./my-project
files:
  - src/http_client.py
prompt: |
  Add retry logic with exponential backoff to all HTTP requests.
  Max 3 retries. Initial delay 1s, max delay 30s.
judge:
  - type: pytest
    command: pytest tests/test_http_client.py -v
  - type: grep
    pattern: "exponential_backoff|retry"
    files: src/http_client.py
commit: "abc1234"  # 釘在特定的 commit，確保可重現
```

### Git Worktree Isolation

每次 agent 執行都有自己的 git worktree，不需要 Docker。這提供了可重現性的隔離，所以 agent 不會互相干擾，也不會弄壞基底 repo。

### Metrics Collected

| 指標 | 量測什麼 |
|--------|-----------------|
| 通過率 | Agent 產出的程式碼有沒有通過 judge？ |
| 成本 | 每個任務的 API 花費（如果有資料的話） |
| 時間 | 到完成為止的實際經過秒數 |
| 一致性 | 重複執行的通過率（例如 3/3 = 100%） |

## Workflow

### 1. Define Tasks

建立 `tasks/` 目錄放 YAML 檔案，一個任務一個檔案：

```bash
mkdir tasks
# 寫任務定義（見上面的範本）
```

### 2. Run Agents

對你的任務執行 agent：

```bash
agent-eval run --task tasks/add-retry-logic.yaml --agent claude-code --agent aider --runs 3
```

每次執行：
1. 從指定的 commit 建立全新的 git worktree
2. 把 prompt 交給 agent
3. 執行 judge 準則
4. 記錄通過／失敗、成本和時間

### 3. Compare Results

產生比較報告：

```bash
agent-eval report --format table
```

```
Task: add-retry-logic (3 runs each)
┌──────────────┬───────────┬────────┬────────┬─────────────┐
│ Agent        │ Pass Rate │ Cost   │ Time   │ Consistency │
├──────────────┼───────────┼────────┼────────┼─────────────┤
│ claude-code  │ 3/3       │ $0.12  │ 45s    │ 100%        │
│ aider        │ 2/3       │ $0.08  │ 38s    │  67%        │
└──────────────┴───────────┴────────┴────────┴─────────────┘
```

## Judge Types

### Code-Based (deterministic)

```yaml
judge:
  - type: pytest
    command: pytest tests/ -v
  - type: command
    command: npm run build
```

### Pattern-Based

```yaml
judge:
  - type: grep
    pattern: "class.*Retry"
    files: src/**/*.py
```

### Model-Based (LLM-as-judge)

```yaml
judge:
  - type: llm
    prompt: |
      Does this implementation correctly handle exponential backoff?
      Check for: max retries, increasing delays, jitter.
```

## Best Practices

- **從 3 到 5 個任務開始**，要能代表你真實的工作負載，不要用玩具範例
- **每個 agent 至少跑 3 次**以捕捉變異：agent 是非確定性的
- **在任務 YAML 裡釘住 commit**，讓結果在幾天／幾週之後都可以重現
- **每個任務至少放一個確定性的 judge**（測試、build）：LLM judge 會增加雜訊
- **把成本和通過率一起追蹤**：成本是 10 倍的 95% agent，可能不是對的選擇
- **替你的任務定義做版本控制**：它們是測試 fixture，當作程式碼對待

## Links

- Repository: [github.com/joaquinhuigomez/agent-eval](https://github.com/joaquinhuigomez/agent-eval)
