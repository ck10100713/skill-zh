---
name: orch-build-mvp
description: 統籌從設計或規格文件起步一個可運作的 MVP：讀入 SDD/PRD、規劃薄的垂直切片、搭出第一個端到端切片的骨架，再以 generator-evaluator 的建置迴圈推進，搭配審查和有關卡的 feat commit。設計或規格文件必須透過規劃好的垂直切片變成跑得起來的 MVP 時使用。
metadata:
  origin: ECC
---

# orch-build-mvp

Actor · action · target：**orch · build · mvp**。包在
[`orch-pipeline`](../orch-pipeline/SKILL.md) 共用引擎外面的薄包裝。

## When to Use

- 使用者有一份**設計 / 規格文件**（SDD、PRD、system_design），想從它
  起步一個可運作的垂直切片。
- 以文件路徑當參數，例如 `civicpulse/docs/SDD-v0.6.md`。

## Operation settings

- **預設的大小下限：** large，這是包含 Scaffold 的完整 pipeline。
- **階段遮罩：** 0（讀規格）→ 1 → 2（重度）→ 3（scaffold）→ 4 → 5 → 6。
- **第一步（階段 0 → 2）：** 讀文件；擷取範圍、已鎖定的決定
  和功能清單；把它排成**薄的垂直切片**（先做一條端到端
  的路徑，不是先做完所有 model 再做所有 view）。階段 3 負責立起第一個切片。

## How It Works

1. 用上面的設定執行 `orch-pipeline` 引擎。
2. **重用既有的 GAN harness**，不要自己手刻迭代迴圈：
   - 把 SDD 轉成 `gan-harness/spec.md` + `gan-harness/eval-rubric.md`
     （這取代了 `gan-planner` 本來會產生的東西，因為你已經有規格了）。
   - 用 `/gan-build "<one-line brief>" --skip-planner` 推動建置
     （預設值：`--max-iterations 15`、`--pass-threshold 7.0`、
     `--eval-mode playwright`；非 UI 的切片用 `--eval-mode code-only`）。
   - 那個指令會跑 `gan-generator` → `gan-evaluator` 迴圈，並寫出
     `gan-harness/feedback/feedback-NNN.md`，直到分數通過或停滯。
3. 停在 **Gate 1**（切片計畫）和 **Gate 2**（commit 前）。把
   骨架和每個切片分別作為獨立的 `feat:` commit。
4. 任何碰到安全觸發條件的切片，都要加上 `security-reviewer`。

## Example

```
orch-build-mvp: civicpulse/docs/SDD-v0.6.md
→ read SDD → slice list (vertical) → scaffold slice 1  [GATE 1: approve]
→ /gan-build --skip-planner (generator → evaluator loop) scores vs spec → review
→ commit feat:  [GATE 2: confirm] → next slice
```
