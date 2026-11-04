---
name: eval-harness
description: 給 AI coding session 用的 eval 驅動開發（EDD）框架：寫程式之前先定義 capability 與 regression eval，用程式、模型、規則或人工 grader 評分，並追蹤 pass@k 與 pass^k 的可靠度。在為 agent 任務定義 pass/fail 標準、衡量 agent 可靠度、為 prompt 或 agent 變更建立 regression 測試套件，或跨模型版本做 benchmark 時使用。
metadata:
  origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Eval Harness Skill

給 Claude Code session 用的正式評估框架，實踐 eval 驅動開發（EDD）的原則。

## 何時啟用

- 為 AI 輔助的工作流建立 eval 驅動開發（EDD）
- 為 Claude Code 任務完成度定義 pass/fail 標準
- 用 pass@k 指標衡量 agent 可靠度
- 為 prompt 或 agent 變更建立 regression 測試套件
- 跨模型版本對 agent 效能做 benchmark

## 理念

Eval 驅動開發把 eval 當成「AI 開發的單元測試」：
- 在實作「之前」先定義預期行為
- 開發期間持續跑 eval
- 每次變更都追蹤 regression
- 用 pass@k 指標衡量可靠度

## Eval 類型

### Capability Eval
測試 Claude 能不能做以前做不到的事：
```markdown
[CAPABILITY EVAL: feature-name]
Task: Description of what Claude should accomplish
Success Criteria:
  - [ ] Criterion 1
  - [ ] Criterion 2
  - [ ] Criterion 3
Expected Output: Description of expected result
```

### Regression Eval
確保變更沒有破壞既有功能：
```markdown
[REGRESSION EVAL: feature-name]
Baseline: SHA or checkpoint name
Tests:
  - existing-test-1: PASS/FAIL
  - existing-test-2: PASS/FAIL
  - existing-test-3: PASS/FAIL
Result: X/Y passed (previously Y/Y)
```

## Grader 類型

### 1. 程式型 Grader
用程式做確定性檢查：
```bash
# Check if file contains expected pattern
grep -q "export function handleAuth" src/auth.ts && echo "PASS" || echo "FAIL"

# Check if tests pass
npm test -- --testPathPattern="auth" && echo "PASS" || echo "FAIL"

# Check if build succeeds
npm run build && echo "PASS" || echo "FAIL"
```

### 2. 模型型 Grader
用 Claude 評估開放式的輸出：
```markdown
[MODEL GRADER PROMPT]
Evaluate the following code change:
1. Does it solve the stated problem?
2. Is it well-structured?
3. Are edge cases handled?
4. Is error handling appropriate?

Score: 1-5 (1=poor, 5=excellent)
Reasoning: [explanation]
```

### 3. 人工 Grader
標記給人工審查：
```markdown
[HUMAN REVIEW REQUIRED]
Change: Description of what changed
Reason: Why human review is needed
Risk Level: LOW/MEDIUM/HIGH
```

## 指標

### pass@k
「k 次嘗試中至少成功一次」
- pass@1：第一次嘗試的成功率
- pass@3：3 次內成功
- 典型目標：pass@3 > 90%

### pass^k
「k 次試驗全部成功」
- 可靠度的門檻更高
- pass^3：連續 3 次成功
- 用於關鍵路徑

## Eval 工作流

### 1. 定義（寫程式之前）
```markdown
## EVAL DEFINITION: feature-xyz

### Capability Evals
1. Can create new user account
2. Can validate email format
3. Can hash password securely

### Regression Evals
1. Existing login still works
2. Session management unchanged
3. Logout flow intact

### Success Metrics
- pass@3 > 90% for capability evals
- pass^3 = 100% for regression evals
```

### 2. 實作
寫程式讓定義好的 eval 通過。

### 3. 評估
```bash
# Run capability evals
[Run each capability eval, record PASS/FAIL]

# Run regression evals
npm test -- --testPathPattern="existing"

# Generate report
```

### 4. 報告
```markdown
EVAL REPORT: feature-xyz
========================

Capability Evals:
  create-user:     PASS (pass@1)
  validate-email:  PASS (pass@2)
  hash-password:   PASS (pass@1)
  Overall:         3/3 passed

Regression Evals:
  login-flow:      PASS
  session-mgmt:    PASS
  logout-flow:     PASS
  Overall:         3/3 passed

Metrics:
  pass@1: 67% (2/3)
  pass@3: 100% (3/3)

Status: READY FOR REVIEW
```

## 整合模式

### 實作前
```
/eval define feature-name
```
在 `.claude/evals/feature-name.md` 建立 eval 定義檔

### 實作中
```
/eval check feature-name
```
執行目前的 eval 並回報狀態

### 實作後
```
/eval report feature-name
```
產生完整的 eval 報告

## Eval 儲存

把 eval 存在專案裡：
```
.claude/
  evals/
    feature-xyz.md      # Eval definition
    feature-xyz.log     # Eval run history
    baseline.json       # Regression baselines
```

## 最佳實務

1. **寫程式「之前」先定義 eval** - 逼自己把成功標準想清楚
2. **經常跑 eval** - 及早抓到 regression
3. **長期追蹤 pass@k** - 監控可靠度趨勢
4. **能用程式 grader 就用** - 確定性勝過機率性
5. **安全相關要人工審查** - 絕對不要把安全檢查完全自動化
6. **讓 eval 保持快速** - 太慢的 eval 不會被執行
7. **eval 跟程式碼一起版本管理** - eval 是一級產物

## 範例：新增認證

```markdown
## EVAL: add-authentication

### Phase 1: Define (10 min)
Capability Evals:
- [ ] User can register with email/password
- [ ] User can login with valid credentials
- [ ] Invalid credentials rejected with proper error
- [ ] Sessions persist across page reloads
- [ ] Logout clears session

Regression Evals:
- [ ] Public routes still accessible
- [ ] API responses unchanged
- [ ] Database schema compatible

### Phase 2: Implement (varies)
[Write code]

### Phase 3: Evaluate
Run: /eval check add-authentication

### Phase 4: Report
EVAL REPORT: add-authentication
==============================
Capability: 5/5 passed (pass@3: 100%)
Regression: 3/3 passed (pass^3: 100%)
Status: SHIP IT
```

## 本地框架工具

機械式的工具放在 `scripts/lib/eval-harness/`：

```sh
node scripts/eval-harness.js example
```

- Capsule：用 hash 串連的日誌，含五條譜系與本地完整性檢查。
- Inspection：來源 digest、驗證過的 variant 路徑，以及語法警告。
- Replay：宣告的工具與以內容定址的 fixture。缺少 fixture 會 fail
  closed；SE3 以上在 replay 中會被拒絕。Record 模式會呼叫已註冊的
  實作，所以只能註冊可信的函式。
- Receipt：離線驗證 capsule 與產物的位元組，附有具名檢查。
- 回顧性準備：`node scripts/eval-harness.js capsule group <dir> [<dir> ...]`
  會把 1 到 100 個明確選定、已驗證的本地 capsule 快照，依宣告的
  harness 版本，從同一個任務家族分組。重複的快照只算一次；
  身分衝突或無效的 capsule 會讓整份報告被拒絕。這是
  唯讀的紀錄計數，沒有新的 rollout、評分或晉升。請使用小的、
  靜止的 capsule。Payload、目錄參數和原始的 run/capsule ID
  會被省略，但任務家族/版本標籤是原樣保留，digest 引用
  是可以串連的；分享之前請先檢查。營運面的驗證仍待完成。

候選者的執行在所有作業系統上都被停用，因為沒有已驗證的作業系統隔離
後端被實作出來。`gate run`、`runGate`、`runVariant`、直接啟動子 process，
以及已退役的 effect preload，都會以 `gate.isolation_required` 拒絕。沒有
trust 旗標或呼叫端提供的 executor 可以繞過這個拒絕。範例會記錄
那個拒絕，並檢查來源，但不執行或評分。

不要把靜態警告、capsule receipt 或成功的工具測試，
當成候選者隔離或晉升的證據。未來的 gate 需要經過獨立審查的作業系統邊界、
受保護的 checker 與稽核管道，以及致命的 baseline 拒絕。見
`docs/architecture/eval-harness-frameworks.md`。

## 產品 Eval（v1.8）

當行為品質無法只靠單元測試捕捉時，使用產品 eval。

### Grader 類型

1. 程式 grader（確定性斷言）
2. 規則 grader（regex/schema 限制）
3. 模型 grader（LLM-as-judge rubric）
4. 人工 grader（含糊的輸出由人工裁定）

### pass@k 指引

- `pass@1`：直接的可靠度
- `pass@3`：受控重試下的實際可靠度
- `pass^3`：穩定性測試（3 次執行都必須通過）

建議的門檻：
- Capability eval：pass@3 >= 0.90
- Regression eval：release 關鍵路徑要 pass^3 = 1.00

### Eval 反模式

- 讓 prompt 過度擬合已知的 eval 範例
- 只衡量 happy path 的輸出
- 追逐通過率時，忽略成本與延遲的漂移
- 在 release gate 中允許 flaky 的 grader

### 最精簡的 Eval 產物配置

- `.claude/evals/<feature>.md` 定義
- `.claude/evals/<feature>.log` 執行歷史
- `docs/releases/<version>/eval-summary.md` release 快照
