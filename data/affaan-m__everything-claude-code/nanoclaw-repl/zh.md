---
name: nanoclaw-repl
description: 操作與擴充 NanoClaw，ECC 零相依、具備 session 感知的 REPL，有以 markdown 為底的持久 session，以及用於切換模型、載入 skill、session 分支、跨 session 搜尋、歷史壓縮和匯出的 slash command。執行或擴充 scripts/claw.js，或要恢復、分支、壓縮、搜尋、匯出 NanoClaw session 時使用。
metadata:
  origin: ECC
---

# NanoClaw REPL

執行或擴充 `scripts/claw.js` 時，用這個 skill。

## Capabilities

- 以 markdown 為底的持久 session
- 用 `/model` 切換模型
- 用 `/load` 動態載入 skill
- 用 `/branch` 做 session 分支
- 用 `/search` 做跨 session 搜尋
- 用 `/compact` 壓縮歷史
- 用 `/export` 匯出成 md/json/txt
- 用 `/metrics` 看 session 指標

## Operating Guidance

1. 讓 session 專注在單一任務。
2. 高風險變更之前先分支。
3. 重大里程碑之後做壓縮。
4. 分享或封存之前先匯出。

## Extension Rules

- 維持零外部執行期相依
- 保持「markdown 即資料庫」的相容性
- 讓指令處理函式保持確定性，而且只在本機執行
