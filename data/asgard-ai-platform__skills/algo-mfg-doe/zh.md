---
name: "algo-mfg-doe"
description: "設計並分析因子實驗，找出顯著的製程因子並最佳化設定。當使用者需要有系統地測試因子效應、最佳化製造製程，或判斷哪些變數最重要時使用，即使他們說的是『which factors affect quality』『optimize process settings』或『design an experiment』。"
metadata:
  category: "WP-48 製造演算法"
  tags: ["manufacturing", "doe", "factorial-design", "optimization"]
---

# 實驗設計（DOE）

## 概述

DOE 有系統地改變製程因子，找出它們對反應變數的影響。完全因子設計測試所有組合；部分因子設計測試經過策略挑選的子集。能找出主效應和交互作用。比一次只改一個因子（OFAT）更有效率，因為 OFAT 會漏掉交互作用。用 ANOVA 分析。

## 何時使用

**觸發條件：**
- 找出哪些製程因子對品質 / 良率有顯著影響
- 為目標表現最佳化製程設定
- 從很多因子中篩選出關鍵的少數

**不該使用的情況：**
- 製程不穩定時（先用 SPC 穩定下來）
- 只有觀察資料、無法操控因子時

## 演算法

```
IRON LAW: One-Factor-At-A-Time (OFAT) MISSES Interactions
Changing one factor while holding others fixed cannot detect
interactions (where the effect of A depends on the level of B).
Full factorial or fractional factorial designs test ALL main effects
AND interactions in fewer runs than OFAT. A 2³ factorial (8 runs)
gives more information than 6 OFAT runs at lower cost.
```

### 階段 1：輸入驗證
定義：反應變數、因子（實務上 2-7 個）、每個因子的水準數（篩選通常用 2，最佳化用 3）、限制條件、雜訊因子。
**關卡：** 因子與水準已定義，且實際上能跑完所有實驗條件。

### 階段 2：核心演算法
**篩選（很多因子）：** 2^(k-p) 部分因子設計。選解析度 III 以上（主效應之間不會混淆）。

**最佳化（少數因子）：** 2^k 完全因子設計，或用中心合成設計（CCD）做反應曲面。

1. 產生設計矩陣（執行順序、因子水準指派）
2. 隨機化執行順序（對有效性至關重要）
3. 執行實驗，記錄反應值
4. 分析：用 ANOVA 看因子顯著性、效應圖、交互作用圖
5. 如果要最佳化：擬合反應曲面模型，找出最佳設定

### 階段 3：驗證
檢查：模型的 R² 足夠、殘差呈常態且隨機。在預測的最佳設定下做確認實驗，結果要符合預測。
**關卡：** 模型顯著、殘差正常、確認實驗通過。

### 階段 4：輸出
回傳顯著因子、效應和最佳設定。

## 輸出格式

```json
{
  "significant_factors": [{"factor": "temperature", "effect": 12.5, "p_value": 0.001}, {"factor": "pressure", "effect": -8.2, "p_value": 0.008}],
  "interactions": [{"factors": "temperature×time", "effect": 5.1, "p_value": 0.03}],
  "optimal": {"temperature": 180, "pressure": 50, "time": 30, "predicted_response": 95.2},
  "metadata": {"design": "2^3_full_factorial", "runs": 8, "replicates": 2, "r_squared": 0.94}
}
```

## 範例

### 輸入輸出範例
**輸入：** 3 個因子（溫度、壓力、時間），各 2 個水準，反應變數 = 良率
**預期：** 2³ = 8 次執行 + 重複。ANOVA 顯示溫度和溫度×壓力的交互作用顯著。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 7 個以上因子 | 部分因子設計 | 完全因子太貴（2⁷=128 次執行） |
| 因子有限制條件 | 受限設計 | 有些因子組合在物理上可能不可行 |
| 非線性反應 | CCD 或 Box-Behnken | 2 水準設計只能擬合線性模型 |

## 注意事項

- **隨機化很關鍵**：沒有隨機化的話，會隨時間變化的因子（操作員疲勞、環境溫度）會混淆結果。一定要隨機化執行順序。
- **Replication vs repetition**：Replication（重新設定並重跑）才能估計誤差。Repetition（同一次執行多次量測）不行。要納入真正的 replicate。
- **別名結構**：部分因子設計會混淆某些效應。解讀結果之前，要先知道哪些效應互為別名（被混淆）。
- **中心點**：在 2 水準設計中加入中心點，用很低的成本就能偵測曲率（非線性）。一定要放 3-5 個中心點。
- **實務顯著 vs 統計顯著**：一個因子可能統計上顯著（p<0.05），但實務上不重要（效應很小）。要看效應的「大小」，不能只看 p 值。

## 參考資料

- 部分因子設計表，見 `references/fractional-tables.md`
- 反應曲面法（RSM），見 `references/rsm.md`
