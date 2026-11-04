---
name: debug
description: 結構化的除錯流程：重現、隔離、診斷、修復。用錯誤訊息或 stack trace 觸發，或像是「staging 正常但 prod 壞掉」「deploy 之後有東西壞了」，或行為跟預期不符、原因又不明顯的時候。
argument-hint: "<error message or problem description>"
---

# /debug

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

進行一場結構化的除錯，有系統地找出並修復問題。

## 用法

```
/debug $ARGUMENTS
```

## 運作方式

```
┌─────────────────────────────────────────────────────────────────┐
│                       DEBUG                                        │
├─────────────────────────────────────────────────────────────────┤
│  步驟 1：REPRODUCE（重現）                                         │
│  ✓ 搞清楚預期行為和實際行為                                       │
│  ✓ 找出確切的重現步驟                                             │
│  ✓ 判斷範圍（什麼時候開始的？誰受影響？）                         │
│                                                                    │
│  步驟 2：ISOLATE（隔離）                                           │
│  ✓ 縮小到特定的元件、服務或程式路徑                               │
│  ✓ 檢查最近的變更（deploy、設定變更、相依套件）                   │
│  ✓ 檢視 log 和錯誤訊息                                            │
│                                                                    │
│  步驟 3：DIAGNOSE（診斷）                                          │
│  ✓ 提出假設並驗證                                                 │
│  ✓ 追蹤程式路徑                                                   │
│  ✓ 找出根本原因（不只是症狀）                                     │
│                                                                    │
│  步驟 4：FIX（修復）                                               │
│  ✓ 提出修法並說明                                                 │
│  ✓ 考慮副作用和邊界情況                                           │
│  ✓ 建議防止 regression 的測試                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 我需要你提供什麼

跟我說說問題。下面任何一項都有幫助：
- 錯誤訊息或 stack trace
- 重現步驟
- 最近改了什麼
- Log 或截圖
- 預期行為 vs. 實際行為

## 輸出

```markdown
## Debug Report: [Issue Summary]

### Reproduction
- **Expected**: [What should happen]
- **Actual**: [What happens instead]
- **Steps**: [How to reproduce]

### Root Cause
[Explanation of why the bug occurs]

### Fix
[Code changes or configuration fixes needed]

### Prevention
- [Test to add]
- [Guard to put in place]
```

## 如果有連接 connector

如果有連接 **~~monitoring**：
- 拉出問題發生前後的 log、錯誤率和指標
- 顯示可能相關的近期 deploy 和設定變更

如果有連接 **~~source control**：
- 找出最近動到受影響程式路徑的 commit 和 PR
- 檢查問題是否跟某個特定變更有關

如果有連接 **~~project tracker**：
- 搜尋相關的 bug 回報或已知問題
- 找到原因後，為修復建立 ticket

## 小提醒

1. **錯誤訊息要原封不動貼上**：不要改寫。確切的文字很重要。
2. **說明改了什麼**：最近的 deploy、相依套件更新和設定變更是頭號嫌疑犯。
3. **附上脈絡**：「staging 正常但 prod 不行」或「只影響大 payload」可以很快縮小範圍。
