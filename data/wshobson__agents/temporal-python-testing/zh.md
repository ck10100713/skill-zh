---
name: temporal-python-testing
description: 用 pytest、時間跳躍（time-skipping）和 mock 策略測試 Temporal workflow。涵蓋單元測試、整合測試、replay 測試和本機開發環境設定。實作 Temporal workflow 測試或除錯測試失敗時使用。
---

# Temporal Python Testing Strategies

用 pytest 測試 Temporal workflow 的完整做法，並以漸進式揭露（progressive disclosure）的資源檔對應各種測試情境。

## When to Use This Skill

- **Unit testing workflows** - 用時間跳躍做快速測試
- **Integration testing** - 搭配 mock activity 的 workflow 測試
- **Replay testing** - 對照 production 歷史驗證決定性（determinism）
- **Local development** - 架設 Temporal server 和 pytest
- **CI/CD integration** - 自動化測試流水線
- **Coverage strategies** - 達到 ≥80% 的測試覆蓋率

## Testing Philosophy

**建議做法**（來源：docs.temporal.io/develop/python/testing-suite）：

- 大部分寫成整合測試
- 用 pytest 搭配 async fixture
- 時間跳躍能讓回饋變快（跑一個月的 workflow 只要幾秒）
- Mock activity 來隔離 workflow 邏輯
- 用 replay 測試驗證決定性

**三種測試類型**：

1. **Unit**：用時間跳躍測 workflow，用 ActivityEnvironment 測 activity
2. **Integration**：Worker 搭配 mock activity
3. **End-to-end**：完整的 Temporal server 加真實 activity（少用）

## Available Resources

這個 skill 以漸進式揭露提供詳細指引。依測試需求載入對應的資源：

### Unit Testing Resources

**File**：`resources/unit-testing.md`
**When to load**：單獨測試個別 workflow 或 activity
**Contains**：

- 有時間跳躍的 WorkflowEnvironment
- 測 activity 用的 ActivityEnvironment
- 快速執行長時間的 workflow
- 手動推進時間的模式
- pytest fixture 與模式

### Integration Testing Resources

**File**：`resources/integration-testing.md`
**When to load**：測試外部依賴被 mock 的 workflow
**Contains**：

- Activity mock 策略
- 錯誤注入模式
- 多 activity workflow 測試
- Signal 與 query 測試
- 覆蓋率策略

### Replay Testing Resources

**File**：`resources/replay-testing.md`
**When to load**：驗證決定性或要部署 workflow 變更時
**Contains**：

- 決定性驗證
- Production 歷史 replay
- CI/CD 整合模式
- 版本相容性測試

### Local Development Resources

**File**：`resources/local-setup.md`
**When to load**：架設開發環境時
**Contains**：

- Docker Compose 設定
- pytest 安裝與設定
- 覆蓋率工具整合
- 開發流程

## Quick Start Guide

### Basic Workflow Test

```python
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

@pytest.fixture
async def workflow_env():
    env = await WorkflowEnvironment.start_time_skipping()
    yield env
    await env.shutdown()

@pytest.mark.asyncio
async def test_workflow(workflow_env):
    async with Worker(
        workflow_env.client,
        task_queue="test-queue",
        workflows=[YourWorkflow],
        activities=[your_activity],
    ):
        result = await workflow_env.client.execute_workflow(
            YourWorkflow.run,
            args,
            id="test-wf-id",
            task_queue="test-queue",
        )
        assert result == expected
```

### Basic Activity Test

```python
from temporalio.testing import ActivityEnvironment

async def test_activity():
    env = ActivityEnvironment()
    result = await env.run(your_activity, "test-input")
    assert result == expected_output
```

## Coverage Targets

**建議覆蓋率**（來源：docs.temporal.io best practices）：

- **Workflows**：≥80% 邏輯覆蓋
- **Activities**：≥80% 邏輯覆蓋
- **Integration**：關鍵路徑搭配 mock activity
- **Replay**：部署前涵蓋所有 workflow 版本

## Key Testing Principles

1. **Time-Skipping** - 跑一個月的 workflow 幾秒就測完
2. **Mock Activities** - 讓 workflow 邏輯和外部依賴隔離
3. **Replay Testing** - 部署前驗證決定性
4. **High Coverage** - production workflow 以 ≥80% 為目標
5. **Fast Feedback** - 單元測試在毫秒內跑完

## How to Use Resources

**需要時再載入對應的資源**：

- 「Show me unit testing patterns」→ 載入 `resources/unit-testing.md`
- 「How do I mock activities?」→ 載入 `resources/integration-testing.md`
- 「Setup local Temporal server」→ 載入 `resources/local-setup.md`
- 「Validate determinism」→ 載入 `resources/replay-testing.md`

## Additional References

- Python SDK Testing: docs.temporal.io/develop/python/testing-suite
- Testing Patterns: github.com/temporalio/temporal/blob/main/docs/development/testing.md
- Python Samples: github.com/temporalio/samples-python
