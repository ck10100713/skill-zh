---
name: verification-loop
description: 對 Claude Code session 的成果跑六階段驗證：build、型別檢查、lint、含覆蓋率的測試、安全 grep 和 diff review，最後產出 PASS/FAIL 的驗證報告。完成功能或重構之後、建立 PR 之前，或必須通過品質關卡時使用。
license: MIT
metadata:
  origin: ECC
---

# Verification Loop Skill

給 Claude Code session 用的完整驗證系統。

## 何時使用

在這些時候呼叫這個 skill：
- 完成功能或重大程式碼變更之後
- 建立 PR 之前
- 想確保品質關卡通過時
- 重構之後

## 驗證階段

### 階段 1：Build 驗證
```bash
set -o pipefail  # report the build's exit status, not tail's
# Check if project builds
npm run build 2>&1 | tail -20
# OR
pnpm build 2>&1 | tail -20
```

如果 build 失敗，就停下來，修好再繼續。

### 階段 2：型別檢查
```bash
set -o pipefail
# TypeScript projects
npx --no-install tsc --noEmit 2>&1 | sed -n '1,30p'

# Python projects
pyright . 2>&1 | sed -n '1,30p'
```

回報所有型別錯誤。繼續之前，先修掉嚴重的。

### 階段 3：Lint 檢查

用 `sed` 限制顯示的輸出，同時把整個串流讀完。這樣在啟用 `pipefail` 時，
成功的 linter 才不會因為 SIGPIPE 而失敗。
```bash
set -o pipefail
# JavaScript/TypeScript
npm run lint 2>&1 | sed -n '1,30p'

# Python
ruff check . 2>&1 | sed -n '1,30p'
```

### 階段 4：測試套件
```bash
set -o pipefail
# Run tests with coverage
npm run test -- --coverage 2>&1 | tail -50

# Check coverage threshold
# Target: 80% minimum
```

回報：
- 測試總數：X
- 通過：X
- 失敗：X
- 覆蓋率：X%

### 階段 5：安全掃描
```bash
# Check for secrets
grep -rn "sk-" --include="*.ts" --include="*.js" . 2>/dev/null | head -10
grep -rn "api_key" --include="*.ts" --include="*.js" . 2>/dev/null | head -10

# Check for console.log
grep -rn "console.log" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -10
```

### 階段 6：Diff Review
```bash
# Show what changed
git diff --stat
git diff HEAD~1 --name-only
```

逐一 review 每個變更的檔案，找：
- 非預期的變更
- 缺少的錯誤處理
- 可能的邊界情況

## 目標驗收

當要求的成果需要部署或目標環境的驗證時，
要把目標驗收跟本機檢查分開回報。已知的話，記錄環境和
安裝的版本、證據，以及下一個被允許的檢查，或明確的
存取相依。本機檢查通過、review、merge 或 release，
都不代表目標驗收。已執行的目標檢查，要回報 VERIFIED 或 FAILED，並附上證據。
沒有授權，不要存取 production 或做外部變更。對
只在本機的任務，把目標驗收標成不適用。

例如：本機檢查 PASS；staging 驗證 NOT PERFORMED（沒有存取權）；
下一步：由被授權的維護者執行 staging smoke test。

## 輸出格式

跑完所有階段之後，產出一份驗證報告：

```
VERIFICATION REPORT
==================

Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]

Overall:   [READY/NOT READY] for PR
Target:    [VERIFIED/FAILED/NOT PERFORMED/NOT APPLICABLE] (environment/version, evidence)
Next permitted step: [check or access dependency; none if complete/not applicable]

Issues to Fix:
1. ...
2. ...
```

## 持續模式

對長時間的 session，每 15 分鐘或在重大變更之後跑一次驗證：

```markdown
Set a mental checkpoint:
- After completing each function
- After finishing a component
- Before moving to next task

Run: /verify
```

## 與 Hook 整合

這個 skill 補足 PostToolUse hook，但提供更深入的驗證。
Hook 會立刻抓到問題；這個 skill 提供全面的 review。
