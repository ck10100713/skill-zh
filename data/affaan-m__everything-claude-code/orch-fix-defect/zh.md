---
name: orch-fix-defect
description: 統籌修 bug：把它重現成一個失敗的回歸測試、修到全綠、審查，再做有關卡的 commit，每個階段都委派給對應的 ECC agent。既有的行為壞了或不對時使用。
metadata:
  origin: ECC
---

# orch-fix-defect

Actor · action · target：**orch · fix · defect**。包在
[`orch-pipeline`](../orch-pipeline/SKILL.md) 共用引擎外面的薄包裝。

## When to Use

- 有東西**壞了**：輸出錯誤、報錯、當機、退化。
- 和同系列的其他 skill 區分：
  - 行為是對的，只是你想要不同的行為 → `orch-change-feature`。
  - 這個能力還不存在 → `orch-add-feature`。

## Operation settings

- **預設的大小下限：** small（常常是 trivial）。
- **階段遮罩：** 0 →（只有根本原因不明顯，或是 standard 以上時才跑輕量的 2）→
  4 → 5 → 6。通常會跳過 Research（1）。
- **第一步（階段 4）：** 把 bug 重現成一個**新的失敗**測試
  （回歸測試），然後修到變綠。先證明 bug 存在，
  才是修 bug 和微調的區別。

## How It Works

1. 用上面的設定執行 `orch-pipeline` 引擎。
2. 如果根本原因不清楚，在寫紅燈測試之前，先用 `code-explorer` 界定範圍；
   建置壞掉的話，升級給 `build-error-resolver` / `/build-fix`。
3. 停在 **Gate 1**（只有在產生了計畫時）和 **Gate 2**（commit 前）。
4. 如果缺陷出在對安全敏感的路徑，就加上 `security-reviewer`。

## Example

```
orch-fix-defect: poller crashes on empty NWS response
→ write failing test reproducing the crash → fix to green
→ code-review → commit  [GATE 2: confirm]   (commit: fix:)
```
