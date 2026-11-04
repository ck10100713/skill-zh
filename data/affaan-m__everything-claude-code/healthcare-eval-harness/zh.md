---
name: healthcare-eval-harness
description: 醫療應用部署用的病人安全評估 harness。針對 CDSS 準確度、PHI 外洩、臨床工作流程完整性和整合合規性的自動化測試套件。安全測試失敗就擋下部署。醫療部署必須以 CDSS 準確度、PHI 外洩和工作流程完整性的病人安全測試作為關卡時使用。
metadata:
  version: "1.0.0"
  origin: Health1 Super Speciality Hospitals — contributed by Dr. Keyur Patel
---

# Healthcare Eval Harness — Patient Safety Verification

醫療應用部署用的自動化驗證系統。只要有一個 CRITICAL 失敗，就擋下部署。病人安全沒有商量的餘地。

> **注意：** 範例用 Jest 當作參考的測試執行器。請依你的框架（Vitest、pytest、PHPUnit 等）調整指令，測試類別和通過門檻跟框架無關。

## When to Use

- 任何 EMR/EHR 應用部署之前
- 修改 CDSS 邏輯（藥物交互作用、劑量驗證、評分）之後
- 變更牽涉到病人資料的資料庫 schema 之後
- 修改驗證或存取控制之後
- 設定醫療應用的 CI/CD pipeline 時
- 解決臨床模組的 merge 衝突之後

## How It Works

這個 eval harness 依序跑五個測試類別。前三個（CDSS Accuracy、PHI Exposure、Data Integrity）是 CRITICAL 關卡，要求 100% 通過，只要失敗一個就擋下部署。其餘兩個（Clinical Workflow、Integration）是 HIGH 關卡，要求 95% 以上通過。

每個類別對應一個 Jest 的測試路徑 pattern。CI pipeline 用 `--bail`（第一次失敗就停）跑 CRITICAL 關卡，並用 `--coverage --coverageThreshold` 強制執行覆蓋率門檻。

### Eval Categories

**1. CDSS Accuracy（CRITICAL，要求 100%）**

測試所有臨床決策支援的邏輯：藥物交互作用配對（兩個方向）、劑量驗證規則、臨床評分對照已發表的規格、沒有漏報、沒有默默失敗。

```bash
npx jest --testPathPattern='tests/cdss' --bail --ci --coverage
```

**2. PHI Exposure（CRITICAL，要求 100%）**

測試受保護健康資訊（PHI）的外洩：API 錯誤回應、console 輸出、URL 參數、瀏覽器儲存、跨機構隔離、未驗證的存取、service role key 不存在。

```bash
npx jest --testPathPattern='tests/security/phi' --bail --ci
```

**3. Data Integrity（CRITICAL，要求 100%）**

測試臨床資料的安全：已鎖定的就診紀錄、稽核軌跡紀錄、cascade delete 保護、並行編輯的處理、沒有孤兒紀錄。

```bash
npx jest --testPathPattern='tests/data-integrity' --bail --ci
```

**4. Clinical Workflow（HIGH，要求 95% 以上）**

測試端到端的流程：就診生命週期、範本渲染、用藥組合、藥物/診斷搜尋、處方 PDF、red flag 警示。

```bash
tmp_json=$(mktemp)
npx jest --testPathPattern='tests/clinical' --ci --json --outputFile="$tmp_json" || true
total=$(jq '.numTotalTests // 0' "$tmp_json")
passed=$(jq '.numPassedTests // 0' "$tmp_json")
if [ "$total" -eq 0 ]; then
  echo "No clinical tests found" >&2
  exit 1
fi
rate=$(echo "scale=2; $passed * 100 / $total" | bc)
echo "Clinical pass rate: ${rate}% ($passed/$total)"
```

**5. Integration Compliance（HIGH，要求 95% 以上）**

測試外部系統：HL7 訊息解析（v2.x）、FHIR 驗證、檢驗結果對應、格式錯誤訊息的處理。

```bash
tmp_json=$(mktemp)
npx jest --testPathPattern='tests/integration' --ci --json --outputFile="$tmp_json" || true
total=$(jq '.numTotalTests // 0' "$tmp_json")
passed=$(jq '.numPassedTests // 0' "$tmp_json")
if [ "$total" -eq 0 ]; then
  echo "No integration tests found" >&2
  exit 1
fi
rate=$(echo "scale=2; $passed * 100 / $total" | bc)
echo "Integration pass rate: ${rate}% ($passed/$total)"
```

### Pass/Fail Matrix

| Category | Threshold | On Failure |
|----------|-----------|------------|
| CDSS Accuracy | 100% | **擋下部署** |
| PHI Exposure | 100% | **擋下部署** |
| Data Integrity | 100% | **擋下部署** |
| Clinical Workflow | 95%+ | 警告，經 review 後允許 |
| Integration | 95%+ | 警告，經 review 後允許 |

### CI/CD Integration

```yaml
name: Healthcare Safety Gate
on: [push, pull_request]

jobs:
  safety-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci

      # CRITICAL 關卡：要求 100%，第一次失敗就中止
      - name: CDSS Accuracy
        run: npx jest --testPathPattern='tests/cdss' --bail --ci --coverage --coverageThreshold='{"global":{"branches":80,"functions":80,"lines":80}}'

      - name: PHI Exposure Check
        run: npx jest --testPathPattern='tests/security/phi' --bail --ci

      - name: Data Integrity
        run: npx jest --testPathPattern='tests/data-integrity' --bail --ci

      # HIGH 關卡：要求 95% 以上，自訂門檻檢查
      # HIGH 關卡：要求 95% 以上
      - name: Clinical Workflows
        run: |
          TMP_JSON=$(mktemp)
          npx jest --testPathPattern='tests/clinical' --ci --json --outputFile="$TMP_JSON" || true
          TOTAL=$(jq '.numTotalTests // 0' "$TMP_JSON")
          PASSED=$(jq '.numPassedTests // 0' "$TMP_JSON")
          if [ "$TOTAL" -eq 0 ]; then
            echo "::error::No clinical tests found"; exit 1
          fi
          RATE=$(echo "scale=2; $PASSED * 100 / $TOTAL" | bc)
          echo "Pass rate: ${RATE}% ($PASSED/$TOTAL)"
          if (( $(echo "$RATE < 95" | bc -l) )); then
            echo "::warning::Clinical pass rate ${RATE}% below 95%"
          fi

      - name: Integration Compliance
        run: |
          TMP_JSON=$(mktemp)
          npx jest --testPathPattern='tests/integration' --ci --json --outputFile="$TMP_JSON" || true
          TOTAL=$(jq '.numTotalTests // 0' "$TMP_JSON")
          PASSED=$(jq '.numPassedTests // 0' "$TMP_JSON")
          if [ "$TOTAL" -eq 0 ]; then
            echo "::error::No integration tests found"; exit 1
          fi
          RATE=$(echo "scale=2; $PASSED * 100 / $TOTAL" | bc)
          echo "Pass rate: ${RATE}% ($PASSED/$TOTAL)"
          if (( $(echo "$RATE < 95" | bc -l) )); then
            echo "::warning::Integration pass rate ${RATE}% below 95%"
          fi
```

### Anti-Patterns

- 「因為上次有過」就跳過 CDSS 測試
- 把 CRITICAL 的門檻設在 100% 以下
- 對 CRITICAL 的測試套件使用 `--no-bail`
- 在整合測試裡 mock 掉 CDSS 引擎（必須測真實的邏輯）
- 安全關卡是紅燈時仍允許部署
- 跑 CDSS 測試套件時沒有加 `--coverage`

## Examples

### Example 1: Run All Critical Gates Locally

```bash
npx jest --testPathPattern='tests/cdss' --bail --ci --coverage && \
npx jest --testPathPattern='tests/security/phi' --bail --ci && \
npx jest --testPathPattern='tests/data-integrity' --bail --ci
```

### Example 2: Check HIGH Gate Pass Rate

```bash
tmp_json=$(mktemp)
npx jest --testPathPattern='tests/clinical' --ci --json --outputFile="$tmp_json" || true
jq '{
  passed: (.numPassedTests // 0),
  total: (.numTotalTests // 0),
  rate: (if (.numTotalTests // 0) == 0 then 0 else ((.numPassedTests // 0) / (.numTotalTests // 1) * 100) end)
}' "$tmp_json"
# 預期：{ "passed": 21, "total": 22, "rate": 95.45 }
```

### Example 3: Eval Report

```
## Healthcare Eval: 2026-03-27 [commit abc1234]

### Patient Safety: PASS

| Category | Tests | Pass | Fail | Status |
|----------|-------|------|------|--------|
| CDSS Accuracy | 39 | 39 | 0 | PASS |
| PHI Exposure | 8 | 8 | 0 | PASS |
| Data Integrity | 12 | 12 | 0 | PASS |
| Clinical Workflow | 22 | 21 | 1 | 95.5% PASS |
| Integration | 6 | 6 | 0 | PASS |

### Coverage: 84% (target: 80%+)
### Verdict: SAFE TO DEPLOY
```
