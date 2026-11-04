---
name: "algo-mfg-cpk"
description: "計算 Cpk 製程能力指數，評估製程是否符合規格要求。當使用者需要評估製程能力、比較不同製程，或判斷品質目標能不能達成時使用，即使他們說的是『can our process meet spec』『process capability』或『Cpk calculation』。"
metadata:
  category: "WP-48 製造演算法"
  tags: ["manufacturing", "cpk", "process-capability", "quality"]
---

# Cpk 製程能力指數

## 概述

Cpk 衡量製程落在規格界限內的程度，同時考慮變異（散布）和置中程度。Cpk = min((USL - μ) / 3σ, (μ - LSL) / 3σ)。通常要求 Cpk ≥ 1.33，關鍵特性要求 Cpk ≥ 1.67。和 Cp 不同，Cpk 會懲罰偏離中心的製程。

## 何時使用

**觸發條件：**
- 評估製造製程能不能符合客戶規格
- 比較不同製程、機台或時間區間的能力
- 為量產就緒做製程驗證

**不該使用的情況：**
- 製程沒有處於統計管制狀態時（先用 SPC 穩定下來）
- 非常態分布又沒有做轉換時

## 演算法

```
IRON LAW: Cpk Is Only Valid for a STABLE, IN-CONTROL Process
Computing Cpk on an unstable process gives a meaningless number.
The process MUST be in statistical control (per SPC charts) before
capability analysis. An unstable process with Cpk=2.0 today may
produce defects tomorrow when it shifts.
```

### 階段 1：輸入驗證
收集：來自穩定製程的 100 筆以上量測值。確定：USL、LSL（客戶規格）。確認製程在管制狀態（SPC 管制圖顯示穩定）。
**關卡：** 製程在管制中、規格已定義、有 100 筆以上資料。

### 階段 2：核心演算法
1. 計算製程平均：μ = Σxᵢ / n
2. 計算製程標準差：σ 用 R-bar/d₂ 或 S-bar/c₄（組內）估計，不是整體標準差
3. Cp = (USL - LSL) / 6σ（潛在能力，不考慮置中）
4. Cpk = min((USL - μ) / 3σ, (μ - LSL) / 3σ)（實際能力）
5. 從 Cpk 估計不良 PPM（例如 Cpk=1.33 → 約 63 PPM）

### 階段 3：驗證
檢查：Cp 和 Cpk 的差距代表置中問題（Cp >> Cpk = 偏離中心）。分布大致呈常態（直方圖、常態性檢定）。
**關卡：** 已算出能力指數、已評估置中程度、已驗證常態性。

### 階段 4：輸出
回傳能力指數，附上不良率估計。

## 輸出格式

```json
{
  "capability": {"cp": 1.8, "cpk": 1.45, "ppm_defective": 27},
  "centering": {"mean": 50.2, "target": 50.0, "offset_pct": 0.4},
  "specs": {"usl": 55, "lsl": 45, "target": 50},
  "metadata": {"samples": 200, "sigma_method": "rbar_d2", "normality_p": 0.35}
}
```

## 範例

### 輸入輸出範例
**輸入：** USL=55、LSL=45、μ=50.2、σ=1.5
**預期：** Cp = (55-45)/(6×1.5) = 1.11。Cpk = min((55-50.2)/4.5, (50.2-45)/4.5) = min(1.07, 1.16) = 1.07。低於 1.33 的目標。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| μ 剛好在目標值 | Cp = Cpk | 完美置中 |
| μ 超出規格 | Cpk < 0 | 製程平均已超過規格界限 |
| 只有單邊規格 | 只用那一側算 Cpk | 例如表面粗糙度只有 USL |

## 注意事項

- **σ 的估計方法**：要用組內 σ（R̄/d₂），不是整體 σ。整體 σ 包含組間變異，會把 σ 墊大、低估 Cpk。
- **非常態資料**：Cpk 假設常態。偏態資料（表面粗糙度、同心度）要用 Box-Cox 轉換或非參數的能力指數。
- **短期 vs 長期**：Cp/Cpk 是短期的（組內變異）。Pp/Ppk 用整體變異（長期）。客戶常常要的是 Ppk。
- **樣本數的信心**：用 30 筆樣本算出的 Cpk，信賴區間很寬。報告點估計的同時要附上信賴區間。
- **Cpk ≠ 零缺陷**：就算 Cpk=2.0 理論上也有不良率（約 0.002 PPM）。超高關鍵的應用需要更高的 Cpk 或製程驗證。

## Scripts

| Script | 說明 | 用法 |
|--------|-------------|-------|
| `scripts/cpk.py` | 從製程資料計算 Cp、Cpk、Cpm 和不良 PPM | `python scripts/cpk.py --help` |

執行 `python scripts/cpk.py --verify` 來跑內建的健全性測試。

## 參考資料

- Cp/Cpk/Pp/Ppk 的比較，見 `references/capability-indices.md`
- 非常態的能力分析，見 `references/non-normal-capability.md`
