---
name: "algo-forecast-arima"
description: "建立 ARIMA 模型做時間序列預測，包含趨勢與季節性分解。當使用者需要從歷史序列資料預測未來數值、檢定平穩性或挑選 ARIMA 參數時使用，即使他們說的是『time series forecast』『predict next month sales』或『ARIMA model』。"
metadata:
  category: "WP-47 時間序列預測"
  tags: ["forecasting", "arima", "time-series", "statistics"]
---

# ARIMA 時間序列模型

## 概述

ARIMA(p,d,q) 結合自迴歸（AR）、差分（I）和移動平均（MA）來做時間序列預測。季節性變體：SARIMA(p,d,q)(P,D,Q,s)。資料必須平穩（透過差分達成）。最適合有明確趨勢 / 季節性模式的單變量序列。

## 何時使用

**觸發條件：**
- 預測單變量時間序列（銷售、需求、流量）
- 資料有明確的趨勢和（或）季節性模式
- 需要具備統計性質、可解釋的模型

**不該使用的情況：**
- 有很多外部特徵的多變量預測（用 ML 模型）
- 非常長期的預測（ARIMA 的信賴區間會快速變寬）
- 不規則 / 事件驅動的資料（用因果模型）

## 演算法

```
IRON LAW: ARIMA Requires STATIONARY Data
Non-stationary data (trend, changing variance) violates ARIMA assumptions.
Test stationarity with ADF test (p < 0.05 = stationary).
If non-stationary: difference the series (d=1 usually suffices).
If still non-stationary after d=2, ARIMA may not be appropriate.
```

### 階段 1：輸入驗證
檢查：時間間隔固定、沒有缺值（需要的話做補值）、至少 50 筆觀測值（理想上有 2 個以上完整的季節週期）。用 ADF 檢定測試平穩性。
**關卡：** 資料間隔規律、長度足夠、已評估平穩性。

### 階段 2：核心演算法
1. **平穩性**：ADF 檢定。如果 p > 0.05，就做差分（d=1），再檢定一次。
2. **參數選擇**：檢視 ACF/PACF 圖。或用 auto_arima（以 AIC 為基礎的網格搜尋）。
   - p（AR 項）：PACF 截尾的 lag
   - q（MA 項）：ACF 截尾的 lag
   - d：需要的差分次數
3. **擬合模型**：最大概似估計
4. **預測**：產生預測值與信賴區間

### 階段 3：驗證
檢查殘差：應該是白噪音（沒有自相關）。Ljung-Box 檢定（p > 0.05 = 沒有自相關）。殘差呈常態分布。
**關卡：** 殘差通過 Ljung-Box 檢定，沒有殘留的模式。

### 階段 4：輸出
回傳預測值與信賴區間。

## 輸出格式

```json
{
  "forecasts": [{"period": "2025-04", "forecast": 1250, "lower_95": 1100, "upper_95": 1400}],
  "model": {"order": [1,1,1], "seasonal_order": [1,1,1,12], "aic": 520.3},
  "metadata": {"training_periods": 60, "forecast_horizon": 12}
}
```

## 範例

### 輸入輸出範例
**輸入：** 12 筆呈上升趨勢的月資料：[10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]

**步驟 1：** 一階差分 = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]（常數 → 平穩，d=1 就夠）

**步驟 2：** 最簡單能擬合的模型是 ARIMA(0,1,0)，也就是漂移 μ=2 的隨機漫步。

**預期預測（ARIMA(0,1,0)，drift=2）：**
- 第 13 期：32 + 2 = **34**
- 第 14 期：32 + 4 = **36**
- 第 15 期：32 + 6 = **38**

驗證：差分後的序列是常數（2）→ 不需要 AR/MA 項。殘差剛好是 0 → 完美擬合（玩具範例）。真實資料的殘差應該要通過 Ljung-Box（p > 0.05）。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 沒有趨勢、沒有季節性 | ARIMA(p,0,q) | 不需要差分 |
| 只有強烈趨勢 | ARIMA(p,1,q) | 一次差分就能去除線性趨勢 |
| 多重季節性 | ARIMA 可能吃力 | 改考慮 Prophet 或 TBATS |

## 注意事項

- **過度差分**：d=1 就夠卻用 d=2，會引入不必要的雜訊。再次差分之前，先檢查一階差分是不是已經平穩。
- **Auto-ARIMA 不是魔法**：以 AIC 為基礎的選擇可能挑出過擬合的模型。不管是不是自動選的，都一定要檢查殘差診斷。
- **信賴區間變寬很快**：多步預測會累積不確定性。超過 2-3 個季節週期的點預測就不要相信。
- **日曆效應**：工作日、假日、閏年會影響月 / 週資料。ARIMA 原生不處理這些，要加回歸變數或改用 Prophet。
- **結構性斷點**：ARIMA 假設資料產生過程是穩定的。COVID、市場衝擊或政策改變都會打破這個假設。

## 參考資料

- ACF/PACF 的判讀指南，見 `references/acf-pacf.md`
- SARIMA 季節性參數的選擇，見 `references/seasonal-arima.md`
