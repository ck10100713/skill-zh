---
name: orch-refine-code
description: 統籌保持行為不變的重構：確認測試是綠的、在不改變行為的前提下重新整理結構、讓測試維持綠燈、審查，再做有關卡的 commit。結構該改善但行為絕不能變時使用。
metadata:
  origin: ECC
---

# orch-refine-code

Actor · action · target：**orch · refine · code**。包在
[`orch-pipeline`](../orch-pipeline/SKILL.md) 共用引擎外面的薄包裝。

## When to Use

- 行為相同，**結構更好**：抽出模組、移除重複、清掉
  死碼、減少巢狀、為了清楚而改名。
- 和同系列的其他 skill 區分：如果行為有任何要改變的打算，這就是
  錯的 skill（該用 `orch-change-feature` / `orch-fix-defect`）。

## Operation settings

- **預設的大小下限：** standard，重新整理結構會動到多個檔案。
- **階段遮罩：** 0 → 2（規劃重新整理）→ 4（保持綠燈）→ 5 → 6。不會寫
  新行為的測試，既有的測試套件就是安全網。
- **第一步（階段 4）：** 在動程式碼**之前**，確認相關的測試存在而且是**綠的**；
  如果覆蓋率很薄，先補 characterization test。
  然後小步重新整理結構，每一步之後重跑測試。

## How It Works

1. 用上面的設定執行 `orch-pipeline` 引擎。
2. 對死碼 / 重複的清掃，委派給 `refactor-cleaner` agent
   （它會跑 knip / depcheck / ts-prune 並安全地移除）。
3. 停在 **Gate 1**（重新整理的計畫）和 **Gate 2**（commit 前）。
4. 用 `refactor:` 作為 commit 類型，diff 必須是行為中性的。

## Example

```
orch-refine-code: extract the NWS HTTP client out of poller.py
→ confirm tests green → plan extraction  [GATE 1: approve]
→ move in small steps, tests green throughout → code-review
→ commit refactor:  [GATE 2: confirm]
```
