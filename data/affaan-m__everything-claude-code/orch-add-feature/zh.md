---
name: orch-add-feature
description: 統籌從頭到尾打造全新功能：研究、規劃、TDD 實作、審查、有關卡的 commit，每個階段都委派給對應的 ECC agent。要新增還不存在的能力時使用。
metadata:
  origin: ECC
---

# orch-add-feature

Actor · action · target：**orch · add · feature**。包在
[`orch-pipeline`](../orch-pipeline/SKILL.md) 共用引擎外面的薄包裝。

## When to Use

- 使用者想要一個**還不存在**的能力（「新增」「建立」
  「實作」「支援……」）。
- 這是全新的行為，不是修正（`orch-fix-defect`），也不是
  更改既有的行為（`orch-change-feature`）。

## Operation settings

- **預設的大小下限：** standard，除非明顯很小，否則要跑 Research + Plan。
- **階段遮罩：** 0 → 1 → 2 → 4 → 5 → 6（跳過 3 Scaffold；那只用於 MVP）。
- **第一步（階段 4）：** 針對新行為寫*新的*失敗測試，然後
  實作到全綠。

## How It Works

1. 用上面的設定執行 `orch-pipeline` 引擎。
2. 先分類大小；小的或瑣碎的功能會收斂成 4 → 5 → 6。
3. 停在 **Gate 1**（計畫核准）和 **Gate 2**（commit 前）。
4. 如果功能碰到安全觸發條件，就加上 `security-reviewer`。

> 相關：`/feature-dev` 是這個流程的獨立版本。`orch-add-feature`
> 的差別在於和家族其他成員共用 `orch-pipeline` 引擎，也就是大小分類器和
> 兩個關卡，所以能把瑣碎的功能縮到 4 → 5 → 6。

## Example

```
orch-add-feature: add OAuth2 login to nws-poller
→ research existing auth libs → plan task_list  [GATE 1: approve]
→ TDD each task → code-review (+ security-reviewer: auth path)
→ commit  [GATE 2: confirm]
```
