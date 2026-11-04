---
name: data-quality-frameworks
description: 用 Great Expectations、dbt test 和 data contract 實作資料品質驗證。在建構資料品質 pipeline、實作驗證規則，或建立 data contract 時使用。
---

# 資料品質框架

用 Great Expectations、dbt test 和 data contract 實作資料品質的正式環境模式，確保資料 pipeline 可靠。

## 何時使用這個 Skill

- 在 pipeline 裡實作資料品質檢查
- 設定 Great Expectations 驗證
- 建構完整的 dbt test 套件
- 在團隊之間建立 data contract
- 監控資料品質指標
- 在 CI/CD 裡自動化資料驗證

## 核心概念

### 1. 資料品質維度

| 維度        | 說明              | 檢查範例                                      |
| ---------------- | ------------------------ | -------------------------------------------------- |
| **Completeness** | 沒有缺漏值        | `expect_column_values_to_not_be_null`              |
| **Uniqueness**   | 沒有重複            | `expect_column_values_to_be_unique`                |
| **Validity**     | 值在預期的範圍內 | `expect_column_values_to_be_in_set`                |
| **Accuracy**     | 資料符合現實     | 交叉參照驗證                         |
| **Consistency**  | 沒有矛盾        | `expect_column_pair_values_A_to_be_greater_than_B` |
| **Timeliness**   | 資料夠新          | `expect_column_max_to_be_between`                  |

### 2. 資料的測試金字塔

```
          /\
         /  \     Integration Tests (cross-table)
        /────\
       /      \   Unit Tests (single column)
      /────────\
     /          \ Schema Tests (structure)
    /────────────\
```

## 快速開始

### Great Expectations 設定

```bash
# Install
pip install great_expectations

# Initialize project
great_expectations init

# Create datasource
great_expectations datasource new
```

```python
# great_expectations/checkpoints/daily_validation.yml
import great_expectations as gx

# Create context
context = gx.get_context()

# Create expectation suite
suite = context.add_expectation_suite("orders_suite")

# Add expectations
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id")
)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeUnique(column="order_id")
)

# Validate
results = context.run_checkpoint(checkpoint_name="daily_orders")
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。

## Summary: {total_passed}/{total_tables} tables passed")
        report.append("")

        for table, result in results.items():
            status = "✅" if result.passed else "❌"
            report.append(f"### {status} {table}")
            report.append(f"- Expectations: {result.total_expectations}")
            report.append(f"- Failed: {result.failed_expectations}")

            if not result.passed:
                report.append("- Failed checks:")
                for detail in result.details:
                    if not detail["success"]:
                        report.append(f"  - {detail['expectation']}: {detail['observed_value']}")
            report.append("")

        return "\n".join(report)

# Usage
context = gx.get_context()
pipeline = DataQualityPipeline(context)

tables_to_validate = {
    "orders": "orders_suite",
    "customers": "customers_suite",
    "products": "products_suite",
}

results = pipeline.run_all(tables_to_validate)
report = pipeline.generate_report(results)

# Fail pipeline if any table failed
if not all(r.passed for r in results.values()):
    print(report)
    raise ValueError("Data quality checks failed!")
```

## 最佳實務

### 該做的

- **及早測試** - 轉換之前先驗證來源資料
- **漸進式測試** - 發現問題就加測試
- **記錄 expectation** - 每個測試都有清楚的描述
- **失敗時發警報** - 跟監控整合
- **替 contract 加版本** - 追蹤 schema 變更

### 不該做的

- **不要什麼都測** - 專注在關鍵欄位
- **不要忽略警告** - 它們常常是失敗的前兆
- **不要跳過新鮮度** - 過期的資料就是壞資料
- **不要寫死門檻** - 用動態的 baseline
- **不要孤立地測試** - 關聯性也要測
