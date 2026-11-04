---
name: ponytail-gain
description: >
  顯示 ponytail 在 benchmark 中量測到的節省幅度（程式碼、成本、速度）。
  一次性顯示。用於 /ponytail-gain、「what does ponytail save」、
  「ponytail impact」。
---

# Ponytail Gain

被呼叫時，顯示這張計分板。一次性：**不要**改模式、寫旗標
檔案，或保存任何東西。

這些數字來自 Ponytail 5 公開的 agentic benchmark：無頭模式的 Claude
Code（Opus 5.5，預設 effort），跑 39 個任務（真實 FastAPI +
React repo 裡的功能 ticket、bug 修復、安全與隱私案例、小型 app），每個跑 5 次，
對照沒有這個 skill 的同一個 agent。其中 18 個任務有隱藏的檢查，
驗證正確性和安全性。每個數字是各任務中位數的幾何平均。
它們是量測出來的，不是從目前的 repo 算出來的。
來源：`benchmarks/results/2026-10-07-agentic.md` 和 README。

## 計分板

用純 ASCII 畫長條。長條長度表示 ponytail 佔
沒有 skill 基準線的比例；標籤帶有精確的數字：

```
  ponytail gain           benchmark · 39 tasks × 5 runs · Opus 5.5

  no-skill        ████████████████████  100%
  Lines of code   █████████···········   47%   ▼ 53%
  Output tokens   ███████████·········   55%   ▼ 45%
  Cost            ███████████████·····   74%   ▼ 26%
  Time            ████████████········   59%   ▼ 41%
  Hidden checks passed   97%  (no-skill 96%)
  Tests where the logic needs one   98%  (no-skill 68%)

  This repo:  /ponytail-debt  (shortcuts you deferred)
              /ponytail-audit (what's still cuttable)
```

## 誠實的界線

這些是 benchmark 的平均值，不是這個 repo 的數字。**絕對不要**印出針對單一 repo 的節省
數字（「你在這裡省了 X 行/token」）：沒蓋出來的那個版本從來沒寫過，
所以在真實的 repo 裡，沒有真正的基準線可以拿來相減。
唯一真正針對單一 repo 的數字，來自 `/ponytail-debt`（有計數的帳本），
而這張卡片是指向那裡，不是自己編一個。

## 範圍界線

一次性顯示。不編輯任何東西，不改任何模式。
