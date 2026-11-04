---
name: orch-change-feature
description: 統籌把既有、運作中的功能改成新的期望行為：把它的測試更新成新規格、修改實作去符合、審查，再做有關卡的 commit。行為沒壞，但應該不一樣時使用。
metadata:
  origin: ECC
---

# orch-change-feature

Actor · action · target：**orch · change · feature**。包在
[`orch-pipeline`](../orch-pipeline/SKILL.md) 共用引擎外面的薄包裝。

## When to Use

- 既有的功能**能用**，但期望的行為不同（「改」、
  「調整」、「讓它也……」、「不要 X，改成 Y」）。
- 和同系列的其他 skill 區分：
  - **沒**壞，所以不是 `orch-fix-defect`（沒有 bug 要重現）。
  - **不是**新的，所以不是 `orch-add-feature`（能力已經存在）。

## Operation settings

- **預設的大小下限：** small，大多數微調只涉及一兩個函式。
- **階段遮罩：** 0 →（只有新行為需要研究時才跑 1）→ 輕量的 2 →
  4 → 5 → 6。
- **第一步（階段 4）：** 把*既有的*測試更新成表達新的
  期望行為，然後修改實作，直到它們通過。先改
  測試，才是微調和修 bug 的區別。

## How It Works

1. 用上面的設定執行 `orch-pipeline` 引擎。
2. 計畫保持輕量，只有 `standard` 以上的大小才值得跑完整的 `planner`。
3. 停在 **Gate 1**（計畫 / 修改過的測試的核准）和 **Gate 2**（commit 前）。
4. 如果變更碰到安全觸發條件，就加上 `security-reviewer`。

## Example

```
orch-change-feature: make nws-poller alert at 2 warnings instead of 3
→ update threshold tests to new spec → change impl to green
→ code-review → commit  [GATE 2: confirm]
```
