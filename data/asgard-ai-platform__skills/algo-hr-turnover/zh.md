---
name: "algo-hr-turnover"
description: "建立員工離職預測模型，找出離職風險與留任的驅動因素。當使用者需要預測哪些員工可能離開、找出留任風險因子，或排定 HR 介入的優先順序時使用，即使他們說的是『attrition prediction』『who is going to quit』或『employee retention model』。"
metadata:
  category: "WP-42 HR 演算法"
  tags: ["hr", "turnover-prediction", "attrition", "retention"]
---

# 員工離職預測

## 概述

離職預測用分類模型（邏輯迴歸、隨機森林、XGBoost）估計員工在特定期間內（通常 6-12 個月）離開的機率。特徵包含年資、薪酬、績效、晉升歷史和敬業度訊號。

## 何時使用

**觸發條件：**
- 找出高自願離職風險的員工
- 量化是哪些因素在推動離職，以便有針對性地介入
- 把留任預算優先投向影響最大的員工

**不該使用的情況：**
- 規劃非自願資遣時（流程和倫理都不同）
- 員工數 < 200 時（資料不足，無法可靠建模）

## 演算法

```
IRON LAW: Turnover Models Predict RISK, Not Certainty
A predicted 80% turnover probability means "employees with similar
profiles historically left 80% of the time." It does NOT mean this
specific employee WILL leave. Never use model outputs as sole basis
for employment decisions — that creates legal and ethical liability.
```

### 階段 1：輸入驗證
收集：員工人口統計、年資、薪酬（相對市場）、最近一次晉升日期、績效評等、主管異動歷史、敬業度調查分數、通勤距離。結果變數：N 個月內自願離職。
**關卡：** 至少 200 筆離職事件，且特徵在離職日之前就取得。

### 階段 2：核心演算法
1. 特徵工程：年資分組、薪資比（薪水/市場中位數）、距離上次晉升的時間、主管年資、敬業度趨勢
2. 處理類別不平衡：離職率通常 10-20%。用 SMOTE 或 class weight。
3. 訓練：邏輯迴歸（可解釋，HR 偏好）或 GBDT（準確度較高）
4. 輸出：每位員工的離職機率 + 主要風險因子

### 階段 3：驗證
評估：AUC、precision-recall（在可行動的門檻下）。回測：模型有沒有正確標出過去 6 個月離職的員工？
**關卡：** AUC > 0.70，最高十分位的 precision > 50%。

### 階段 4：輸出
回傳風險分數，附上驅動因子分析。

## 輸出格式

```json
{
  "risk_scores": [{"employee_id": "E123", "turnover_prob": 0.72, "risk_tier": "high", "top_drivers": ["low_comp_ratio", "no_promotion_3yr"]}],
  "metadata": {"model": "xgboost", "auc": 0.78, "prediction_window_months": 12}
}
```

## 範例

### 輸入輸出範例
**輸入：** 員工：年資 4 年、薪資比 0.85、3 年沒升遷、敬業度分數下降中
**預期：** 高風險（>0.6）。主要驅動因子：薪酬低於市場、職涯停滯。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 新進員工（< 6 個月） | 預測不可靠 | 行為資料不足 |
| 績效頂尖、薪酬高 | 仍可能離開 | 非財務因素（主管、文化）也很重要 |
| 組織重整後的時期 | 模型很可能漂移 | 異常狀況會扭曲模式 |

## 注意事項

- **倖存者偏誤**：訓練資料只包含被雇用、而且待得夠久才能被觀察到的人。很早期就離開的人可能代表性不足。
- **特徵洩漏**：「開始找工作」或「更新 LinkedIn」是很強的預測因子，但拿來用在倫理和法律上都有問題。只用公司內部的 HR 資料。
- **自我實現預言**：如果主管對「高風險」員工另眼看待（少投資、少給專案），模型預測就會變成自我實現。
- **法律限制**：直接或透過代理變數使用受保護的屬性（年齡、性別、族群），可能違反勞動法規。要稽核是否有差別性影響。
- **留任介入的時機**：找出風險，要 HR 真的採取行動才有用。要把模型放進有具體介入觸發條件的留任流程裡。

## 參考資料

- 從 HR 資料做特徵工程，見 `references/hr-features.md`
- HR 應用中的倫理 AI，見 `references/ethical-hr-ai.md`
