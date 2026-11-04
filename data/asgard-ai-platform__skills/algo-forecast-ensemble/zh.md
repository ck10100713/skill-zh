---
name: "algo-forecast-ensemble"
description: "把多個預測模型組合成集成預測，以提高準確度。當使用者需要提升預測的可靠度、組合 ARIMA/Prophet/ETS 的輸出，或建立穩健的預測流程時使用，即使他們說的是『combine forecasts』『model averaging』或『which forecast should I trust』。"
metadata:
  category: "WP-47 時間序列預測"
  tags: ["forecasting", "ensemble", "model-combination", "accuracy"]
---

# 集成預測

## 概述

集成預測把多個模型的預測結合起來，降低變異並提高準確度。3-5 個差異夠大的模型做簡單平均，常常比最好的單一模型還準。方法：等權重平均、誤差倒數加權、用 meta-learner 做 stacking。「forecast combination puzzle」顯示簡單平均很難被打敗。

## 何時使用

**觸發條件：**
- 手上有多個預測模型，而且表現差不多
- 降低預測風險比追求最高準確度更重要
- 建立對單一模型故障有韌性的正式環境流程

**不該使用的情況：**
- 有一個模型明顯勝過其他所有模型時（直接用那個模型）
- 運算預算只夠跑一個模型時

## 演算法

```
IRON LAW: Simple Average Often Beats Complex Combination
The "forecast combination puzzle" (Stock & Watson, 2004): equal-weight
averaging of diverse models frequently outperforms sophisticated
weighting schemes. This is because weight estimation introduces noise
that offsets the theoretical gain. Start with simple average and only
move to weighted combination if you have abundant validation data.
```

### 階段 1：輸入驗證
從 3 個以上差異夠大的模型（例如 ARIMA、ETS、Prophet、ML 類）產生預測。確保模型真的有差異（假設 / 方法不同）。
**關卡：** 有 3 個以上的模型預測，且模型用的方法論不同。

### 階段 2：核心演算法
**簡單平均：** ŷ_ensemble = (1/M) × Σ ŷ_m

**誤差倒數加權：** w_m = (1/MSE_m) / Σ(1/MSE_j)，ŷ_ensemble = Σ w_m × ŷ_m

**Stacking：** 訓練一個 meta-model（線性迴歸），從各個模型經交叉驗證的預測中學出最佳權重。

### 階段 3：驗證
在保留資料上比較集成與各個別模型。集成應該：平均誤差較低，而且最大誤差也較低（更穩健）。
**關卡：** 集成的 RMSE ≤ 最佳個別模型的 RMSE。

### 階段 4：輸出
回傳集成預測，附上各成員模型的貢獻。

## 輸出格式

```json
{
  "ensemble_forecast": [{"period": "2025-04", "forecast": 1200, "lower_95": 1050, "upper_95": 1350}],
  "model_forecasts": {"arima": 1180, "prophet": 1220, "ets": 1200},
  "weights": {"arima": 0.35, "prophet": 0.30, "ets": 0.35},
  "metadata": {"method": "inverse_error_weighted", "ensemble_rmse": 42, "best_individual_rmse": 48}
}
```

## 範例

### 輸入輸出範例
**輸入：** 下個月銷售額的預測：ARIMA=1180、Prophet=1220、ETS=1200
**預期：** 簡單平均 = 1200。如果 ARIMA 歷史表現最好（MSE 最低），加權平均會往 1180 偏。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 所有模型都同意 | 集成 = 個別模型 | 有共識，信心高 |
| 模型之間差很多 | 集成 = 折衷，信賴區間很寬 | 不確定性高，標記起來人工複查 |
| 其中一個模型是離群值 | 平均會減弱離群值的影響 | 集成的穩健性好處 |

## 注意事項

- **多樣性是關鍵**：組合 5 個 ARIMA 變體沒什麼幫助。要組合根本上不同的方法（統計 + ML + 人工判斷）。
- **權重不穩定**：用過去資料估出的最佳權重，未來不一定最佳。簡單平均可以避開這個不穩定。
- **誤差之間的相關性**：如果模型誤差彼此相關（常常如此），集成的改善就有限。要找誤差不相關的模型。
- **信賴區間**：組合點預測很容易。要正確地組合預測區間，需要了解誤差的相關結構。
- **過度設計的風險**：對穩定、已經很了解的序列，一個調得好的單一模型可能勝過集成。集成在不確定或波動大的序列上才有價值。

## 參考資料

- 預測組合方法的綜述，見 `references/combination-survey.md`
- Stacking meta-learner 的實作，見 `references/stacking.md`
