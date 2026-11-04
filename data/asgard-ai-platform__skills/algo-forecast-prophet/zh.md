---
name: "algo-forecast-prophet"
description: "用 Meta 的 Prophet 為含有假日與變化點的商業時間序列建立預測模型。當使用者需要好上手的時間序列預測、處理缺值與假日，或自動偵測變化點時使用，即使他們說的是『forecast with Prophet』『business forecast』或『easy time series model』。"
metadata:
  category: "WP-47 時間序列預測"
  tags: ["forecasting", "prophet", "time-series", "business-analytics"]
---

# Prophet 預測

## 概述

Prophet（Meta）把時間序列分解成 趨勢 + 季節性 + 假日 + 誤差。使用以 Stan 擬合的加法（或乘法）模型。原生就能處理缺值、離群值和假日效應。為日 / 週粒度的商業時間序列而設計。

## 何時使用

**觸發條件：**
- 以日 / 週頻率預測商業指標（銷售、流量、互動）
- 資料有強烈的季節性模式和已知的假日效應
- 需要快速、合理的預測，但沒有深厚的時間序列專業

**不該使用的情況：**
- 高頻資料（小於一小時）：Prophet 是為日級以上設計的
- 需要因果 / 解釋性模型時（Prophet 是描述性的）
- 非常短的時間序列（< 2 個季節週期）

## 演算法

```
IRON LAW: Prophet Is an Additive Regression Model, NOT Classical Time Series
y(t) = g(t) + s(t) + h(t) + ε(t)
- g(t): piecewise linear or logistic trend with automatic changepoints
- s(t): Fourier series for yearly/weekly/daily seasonality
- h(t): user-specified holiday effects
Prophet does NOT model autocorrelation in residuals. If residuals are
autocorrelated, the uncertainty intervals will be too narrow.
```

### 階段 1：輸入驗證
準備 DataFrame，欄位：ds（日期戳記）、y（指標）。有的話加入回歸變數欄位。指定：國家假日、自訂假日、成長類型。
**關卡：** 資料格式正確，至少有 2 個完整的季節週期。

### 階段 2：核心演算法
1. 選成長模型：'linear'（預設）或 'logistic'（需設 cap 和 floor）
2. 設定季節性：yearly（預設）、weekly（預設）、自訂（例如 monthly）
3. 加入假日：內建的國家假日 + 自訂事件（促銷、上市）
4. 擬合模型：`m = Prophet(); m.fit(df)`
5. 產生未來的 DataFrame 並預測：`m.predict(future)`

### 階段 3：驗證
檢查：預測的各成分（趨勢、季節性、假日）符合直覺。交叉驗證：用 Prophet 內建的 `cross_validation()` 搭配滾動視窗。評估 MAPE、RMSE。
**關卡：** MAPE 對這個使用情境來說可以接受，各成分通過目視檢查。

### 階段 4：輸出
回傳預測，附上分解後的各成分。

## 輸出格式

```json
{
  "forecasts": [{"ds": "2025-04-15", "yhat": 1200, "yhat_lower": 1050, "yhat_upper": 1350}],
  "components": {"trend": "upward_3pct", "yearly_seasonality": "peak_in_december", "weekly_seasonality": "low_on_weekends"},
  "metadata": {"mape": 0.08, "training_days": 730, "forecast_days": 90}
}
```

## 範例

### 輸入輸出範例
**輸入：** 2 年的每日網站流量，有聖誕節高峰和夏季低谷
**預期：** 預測抓到：上升趨勢、週模式（平日 > 週末）、年度模式（聖誕節高峰、夏季低谷）。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 很多天缺資料 | Prophet 原生處理 | 不像 ARIMA，不需要補值 |
| 趨勢突然改變 | 自動偵測變化點 | 這是 Prophet 相對 ARIMA 的主要特色 |
| 乘法季節性 | 設 seasonality_mode='multiplicative' | 季節振幅隨趨勢放大的時候 |

## 注意事項

- **預設的變化點敏感度**：Prophet 可能多偵測或少偵測趨勢變化。調 `changepoint_prior_scale`（預設 0.05）：越高越有彈性，越低越平滑。
- **預測太平**：如果趨勢變化點設得太保守，長期預測可能平得不切實際。提高彈性，或指定成長上限。
- **假日效應需要自己指定**：Prophet 不會自動發現假日。你必須提供假日 DataFrame，漏掉的假日就不會被建模。
- **不適用因果推論**：Prophet 找得出模式，但不解釋原因。加入回歸變數只顯示相關，不代表因果。
- **不確定性區間**：以歷史趨勢變化的變異為基礎，不是殘差自相關。如果殘差有結構，區間可能太窄。

## 參考資料

- Prophet 超參數調校指南，見 `references/prophet-tuning.md`
- 交叉驗證的最佳實務，見 `references/prophet-cv.md`
