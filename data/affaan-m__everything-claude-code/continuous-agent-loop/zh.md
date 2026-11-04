---
name: continuous-agent-loop
description: 持續自主 agent 迴圈的模式，附帶品質關卡、評估和復原控制。適用於執行必須自我檢查、以評估把關，並能從失敗中復原的 agent 迴圈。
metadata:
  origin: ECC
---

# Continuous Agent Loop

這是 v1.8+ 標準的迴圈 skill 名稱。它取代 `autonomous-loops`，並保留一個版本的相容性。

## Loop Selection Flow

```text
Start
  |
  +-- Need strict CI/PR control? -- yes --> continuous-pr
  |
  +-- Need RFC decomposition? -- yes --> rfc-dag
  |
  +-- Need exploratory parallel generation? -- yes --> infinite
  |
  +-- default --> sequential
```

## Combined Pattern

建議的 production 堆疊：
1. RFC 分解（`ralphinho-rfc-pipeline`）
2. 品質關卡（`plankton-code-quality` + `/quality-gate`）
3. 評估迴圈（`eval-harness`）
4. session 持久化（`nanoclaw-repl`）

## Failure Modes

- 迴圈空轉，沒有可衡量的進展
- 同一個根本原因反覆重試
- merge 佇列停滯
- 無上限的升級造成成本漂移

## Recovery

- 凍結迴圈
- 執行 `/harness-audit`
- 把範圍縮小到失敗的單元
- 用明確的驗收標準重播
