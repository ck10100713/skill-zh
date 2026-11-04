---
name: agent-harness-construction
description: 設計和優化 AI agent 的動作空間、工具定義和觀察結果的格式，以提高完成率。在定義或修訂 agent 的工具集、動作空間或觀察格式時使用。
metadata:
  origin: ECC
---

# Agent Harness Construction

當你要改善 agent 怎麼規劃、呼叫工具、從錯誤中恢復，以及收斂到完成時，使用這個 skill。

## Core Model

Agent 輸出的品質受這些因素限制：
1. 動作空間的品質
2. 觀察結果的品質
3. 恢復能力的品質
4. Context 預算的品質

## Action Space Design

1. 使用穩定、明確的工具名稱。
2. 輸入以 schema 為先，並保持狹窄。
3. 回傳確定性的輸出形狀。
4. 避免萬用工具，除非無法做到隔離。

## Granularity Rules

- 高風險操作（deploy、migration、權限）用微型工具。
- 常見的編輯／讀取／搜尋迴圈用中型工具。
- 只有在來回的開銷是主要成本時，才用巨型工具。

## Observation Design

每個工具回應都應該包含：
- `status`: success|warning|error
- `summary`: 一行結果
- `next_actions`: 可以執行的後續動作
- `artifacts`: 檔案路徑／ID

## Error Recovery Contract

每條錯誤路徑都要包含：
- 根本原因的提示
- 安全的重試指示
- 明確的停止條件

## Context Budgeting

1. 讓 system prompt 保持精簡且不變。
2. 把大量的指引移到按需載入的 skill 裡。
3. 優先用檔案的參照，不要把長文件塞進內文。
4. 在階段邊界壓縮，不要用任意的 token 門檻。

## Architecture Pattern Guidance

- ReAct：最適合路徑不確定的探索性任務。
- Function-calling：最適合結構化的確定性流程。
- Hybrid（建議）：ReAct 規劃 + 有型別的工具執行。

## Benchmarking

追蹤：
- 完成率
- 每個任務的重試次數
- pass@1 和 pass@3
- 每個成功任務的成本

## Anti-Patterns

- 太多語意重疊的工具。
- 不透明的工具輸出，沒有恢復提示。
- 只有錯誤、沒有下一步的輸出。
- 用不相關的參照讓 context 超載。
