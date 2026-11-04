---
name: comp-analysis
description: 分析薪酬：市場對標、薪資帶定位、股權建模。用「what should we pay a [role]」「is this offer competitive」「model this equity grant」觸發，或當使用者上傳薪酬資料想找出異常值與留任風險時使用。
argument-hint: "<role, level, or dataset>"
---

# /comp-analysis

> 如果看到不認識的 placeholder，或需要確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

分析薪酬資料，用於市場對標、薪資帶定位和規劃。協助拿薪酬跟市場資料比對，支援招募、留任和股權規劃。

## 用法

```
/comp-analysis $ARGUMENTS
```

## 我需要你提供什麼

**選項 A：單一職位分析**
「What should we pay a Senior Software Engineer in SF?」

**選項 B：上傳薪酬資料**
上傳 CSV，或貼上你的薪資帶。我會分析定位、找出異常值，並跟市場比較。

**選項 C：股權建模**
「Model a refresh grant of 10K shares over 4 years at a $50 stock price.」

## 薪酬框架

### 總薪酬的組成
- **Base salary**：現金薪酬
- **Equity**：RSU、股票選擇權或其他股權
- **Bonus**：年度目標獎金、簽約獎金
- **Benefits**：健康、退休、福利（比較難量化）

### 關鍵變數
- **Role**：職能與專業
- **Level**：IC 職級、管理職級
- **Location**：依地區做薪資調整
- **Company stage**：新創 vs. 成長期 vs. 上市公司
- **Industry**：科技 vs. 金融 vs. 醫療

### 資料來源
- **有 ~~compensation data**：拉已驗證的對標資料
- **沒有**：用網路研究、公開薪資資料，以及使用者提供的背景
- 一定要註明資料的新鮮度和來源的限制

## 輸出

提供 base、equity 和 total comp 的百分位區間（25th、50th、75th、90th）。要包含地區調整和公司階段的背景。

```markdown
## Compensation Analysis: [Role/Scope]

### Market Benchmarks
| Percentile | Base | Equity | Total Comp |
|------------|------|--------|------------|
| 25th | $[X] | $[X] | $[X] |
| 50th | $[X] | $[X] | $[X] |
| 75th | $[X] | $[X] | $[X] |
| 90th | $[X] | $[X] | $[X] |

**Sources:** [Web research, compensation data tools, or user-provided data]

### Band Analysis (if data provided)
| Employee | Current Base | Band Min | Band Mid | Band Max | Position |
|----------|-------------|----------|----------|----------|----------|
| [Name] | $[X] | $[X] | $[X] | $[X] | [Below/At/Above] |

### Recommendations
- [Specific compensation recommendations]
- [Equity considerations]
- [Retention risks if applicable]
```

## 如果有連接器

如果有連上 **~~compensation data**：
- 依職位、職級和地區拉已驗證的市場對標
- 拿你的薪資帶跟即時市場資料比較

如果有連上 **~~HRIS**：
- 拉目前員工的薪酬資料來做薪資帶分析
- 自動找出異常值和留任風險

## 小提醒

1. **地區很重要**：做對標一定要指定地區。SF、Austin、London 差很多。
2. **看總薪酬，不只 base**：要把股權、獎金和福利都算進去才完整。
3. **資料要保密**：薪酬資料很敏感，結果只會留在你的對話裡。
