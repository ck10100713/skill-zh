---
name: "algo-hr-compensation"
description: "進行薪酬基準分析，把薪資和市場資料對照定位。當使用者需要評估薪資競爭力、建立薪資級距或分析薪酬公平性時使用，即使他們說的是『are we paying market rate』『salary benchmarking』或『compensation analysis』。"
metadata:
  category: "WP-42 HR 演算法"
  tags: ["hr", "compensation", "benchmarking", "salary-analysis"]
---

# 薪酬基準分析

## 概述

薪酬基準分析把內部薪資水準和外部市場資料比較，評估競爭力。使用 compa-ratio（實際薪資 / 市場中位數）和百分位定位。用來支援薪資級距設計、調薪和公平性分析。

## 何時使用

**觸發條件：**
- 評估目前的薪資在市場上有沒有競爭力
- 設計或更新薪資級距與薪酬結構
- 找出不同族群或職務之間的薪酬公平性缺口

**不該使用的情況：**
- 個別的績效調薪決策（用績效管理）
- 沒有市場資料時（至少要有薪資調查的基準）

## 演算法

```
IRON LAW: Benchmarking Is Only Valid With COMPARABLE Jobs
Matching by job TITLE alone is unreliable — "Senior Engineer" means
vastly different things at different companies. Match by: job content
(duties, scope), level (IC vs manager, experience band), industry,
geography, and company size. Poor job matching produces misleading
market rates.
```

### 階段 1：輸入驗證
收集：內部薪酬資料（底薪、獎金、股權）、市場調查資料（各職務的 P25、P50、P75）、內部職務與調查基準之間的職務對應。
**關卡：** 職務已正確對應，調查資料夠新（< 18 個月）。

### 階段 2：核心演算法
1. 依職務內容、層級和範圍，把內部職務對應到市場基準
2. 把調查資料推算到當前日期：套用預估的市場調幅
3. 計算每位員工的 compa-ratio：實際底薪 / 市場 P50
4. 計算百分位定位：實際薪資落在市場分布的哪裡
5. 分析：依部門、層級、年資、族群檢查公平性缺口

### 階段 3：驗證
檢查：compa-ratio 集中在 0.85-1.15（正常範圍）。標記離群值（< 0.80 薪資偏低，> 1.20 薪資偏高）。檢驗族群之間的公平性。
**關卡：** 分布合理，公平性分析已完成。

### 階段 4：輸出
回傳基準分析結果，附上級距建議。

## 輸出格式

```json
{
  "summary": {"avg_compa_ratio": 0.97, "below_band_pct": 12, "above_band_pct": 8},
  "by_role": [{"role": "Software Engineer", "market_p50": 1800000, "avg_actual": 1750000, "compa_ratio": 0.97}],
  "equity_flags": [{"dimension": "gender", "gap_pct": 3.2, "statistically_significant": true}],
  "metadata": {"employees": 500, "survey_source": "Mercer", "survey_date": "2025-H2"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 50 位工程師，市場 P50=NT$1.8M，實際範圍 NT$1.5M-2.1M
**預期：** 平均 compa-ratio 約 0.97，部分低於級距的員工標記為需要調整。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 熱門市場（科技榮景） | 市場資料很快過時 | 套用較高的推算係數 |
| 混合遠端工作 | 需要依地點調整的級距 | 舊金山和台北的市場薪資差 2-3 倍 |
| 小公司，對不到調查資料 | 用較寬的產業代理資料 | 不完美，但總比沒有好 |

## 注意事項

- **總薪酬**：只做底薪的基準分析，會漏掉股權、獎金和福利。要比較總薪酬才能定位準確。
- **調查資料的落後**：已發布的調查反映的是 6-18 個月前收集的資料。市場變動快的時候，要把資料往前推算。
- **內部公平 vs 外部競爭力**：和市場對齊可能造成內部不公平（新人薪水比資深員工高）。兩邊都要顧。
- **地區差異**：遠端工作讓依地點定薪變複雜。要訂清楚的政策：依總部所在地、員工所在地，或混合。
- **薪酬公平的法律風險**：無法解釋的族群薪資缺口會帶來法律責任。要做迴歸式的公平性分析，並控制合理因素（經驗、績效、層級）。

## 參考資料

- 薪資級距設計方法論，見 `references/band-design.md`
- 薪酬公平的迴歸分析，見 `references/pay-equity.md`
