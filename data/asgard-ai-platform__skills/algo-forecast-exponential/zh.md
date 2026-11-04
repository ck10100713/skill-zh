---
name: "algo-forecast-exponential"
description: "用指數平滑法（加權移動平均）做時間序列預測。當使用者需要簡單穩健的預測、為季節性資料實作 Holt-Winters，或想在不用複雜模型下建立輕量預測時使用，即使他們說的是『simple forecast』『moving average prediction』或『smoothing method』。"
metadata:
  category: "WP-47 時間序列預測"
  tags: ["forecasting", "exponential-smoothing", "holt-winters", "time-series"]
---

# 指數平滑

## 概述

指數平滑對過去的觀測值給予呈指數遞減的權重。三種變體：Simple（SES，只有水準）、Holt（水準 + 趨勢）、Holt-Winters（水準 + 趨勢 + 季節性）。ETS 框架（Error-Trend-Seasonality）提供一個統一的統計模型。快、可解釋，在短期預測上能和複雜模型一較高下。

## 何時使用

**觸發條件：**
- 要快速預測、設定越少越好
- 短期預測（往前 1-2 個季節週期）
- 資料有明確的水準、趨勢和（或）季節性成分

**不該使用的情況：**
- 長期預測（不確定性累積太快）
- 外部回歸變數很重要時（用迴歸或 ML 模型）

## 演算法

```
IRON LAW: Smoothing Parameters Control the Bias-Variance Trade-Off
α (level), β (trend), γ (seasonality) range [0,1].
- α near 1: react quickly to changes, noisy forecasts (high variance)
- α near 0: smooth forecasts, slow to adapt (high bias)
Optimize via minimizing MSE on training data (or use information criteria).
Never hand-pick smoothing parameters without validation.
```

### 階段 1：輸入驗證
辨識成分：只有水準（SES）、水準+趨勢（Holt）、水準+趨勢+季節性（Holt-Winters）。判斷：趨勢 / 季節性是加法還是乘法。
**關卡：** 已辨識成分結構，且知道季節週期。

### 階段 2：核心演算法
**Holt-Winters（加法）：**
1. 初始化：level₀ = mean(第一季)，trend₀ = (mean(第 2 季) - mean(第 1 季))/s，seasonal₀ 取自第一季的偏差
2. 每個 t 的更新公式：
   - Level: ℓₜ = α(yₜ - sₜ₋ₛ) + (1-α)(ℓₜ₋₁ + bₜ₋₁)
   - Trend: bₜ = β(ℓₜ - ℓₜ₋₁) + (1-β)bₜ₋₁
   - Seasonal: sₜ = γ(yₜ - ℓₜ) + (1-γ)sₜ₋ₛ
3. 預測：ŷₜ₊ₕ = ℓₜ + h×bₜ + sₜ₊ₕ₋ₛ

### 階段 3：驗證
檢查：樣本內 RMSE、殘差模式。和 naive 基準（最後一個值、季節性 naive）比較。
**關卡：** 贏過 naive 基準，殘差沒有系統性模式。

### 階段 4：輸出
回傳預測值，附上平滑後的各成分。

## 輸出格式

```json
{
  "forecasts": [{"period": "2025-04", "forecast": 1150, "level": 1100, "trend": 20, "seasonal": 30}],
  "parameters": {"alpha": 0.3, "beta": 0.1, "gamma": 0.15},
  "metadata": {"method": "holt_winters_additive", "seasonal_period": 12, "rmse": 45}
}
```

## 範例

### 輸入輸出範例
**輸入：** 36 個月的月銷售額，明顯上升趨勢，12 月有高峰
**預期：** Holt-Winters 加法。預測延續趨勢，並重複 12 月的季節性。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 沒有趨勢、沒有季節性 | SES（只有 α） | 最簡單的變體就夠了 |
| 季節振幅越來越大 | 用乘法 | 加法會低估高峰 |
| 序列非常短（<2 個季節） | 只能用 SES 或 Holt | 無法估計季節性 |

## 注意事項

- **加法 vs 乘法**：如果季節波動隨水準等比例放大，就用乘法。選錯會讓預測很差，尤其在極端值。
- **初始化的敏感度**：第一季的值設定了基準。早期資料雜訊大、初始化不好，會一路影響整個預測。
- **阻尼趨勢**：長期預測時，線性趨勢外推不切實際。用阻尼趨勢（φ 參數）讓趨勢隨時間變平。
- **多重季節性**：標準 Holt-Winters 只處理一個季節週期。如果日資料同時有週和年的模式，用 TBATS 或 STL+ETS。
- **對離群值敏感**：一個離群值就可能讓水準估計大幅位移（尤其 α 高的時候）。要先偵測並處理離群值。

## 參考資料

- ETS 框架與模型選擇，見 `references/ets-framework.md`
- 阻尼趨勢的變體，見 `references/damped-trend.md`
