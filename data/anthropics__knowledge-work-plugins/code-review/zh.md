---
name: code-review
description: 從安全性、效能和正確性檢查程式碼變更。給 PR URL 或 diff、說「review this before I merge」「is this code safe?」時觸發，或當要檢查變更有沒有 N+1 query、injection 風險、漏掉的邊界情況、錯誤處理缺口時使用。
argument-hint: "<PR URL, diff, or file path>"
---

# /code-review

> 如果看到不認識的 placeholder，或需要確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

用結構化的角度審查程式碼變更，涵蓋安全性、效能、正確性和可維護性。

## 用法

```
/code-review <PR URL or file path>
```

審查提供的程式碼變更：@$1

如果沒有指定檔案或 URL，就問要審查什麼。

## 運作方式

```
┌─────────────────────────────────────────────────────────────────┐
│                      CODE REVIEW                                   │
├─────────────────────────────────────────────────────────────────┤
│  STANDALONE（永遠能用）                                          │
│  ✓ 貼 diff、PR URL，或指定檔案                                  │
│  ✓ 安全稽核（OWASP top 10、injection、auth）                    │
│  ✓ 效能審查（N+1、記憶體洩漏、複雜度）                          │
│  ✓ 正確性（邊界情況、錯誤處理、race condition）                 │
│  ✓ 風格（命名、結構、可讀性）                                   │
│  ✓ 附程式碼範例的可執行建議                                     │
├─────────────────────────────────────────────────────────────────┤
│  SUPERCHARGED（連上你的工具之後）                                │
│  + 版本控制：自動拉 PR diff                                      │
│  + 專案追蹤：把發現連到 ticket                                   │
│  + 知識庫：對照團隊的 coding standard 檢查                       │
└─────────────────────────────────────────────────────────────────┘
```

## 審查面向

### 安全性
- SQL injection、XSS、CSRF
- 認證與授權缺陷
- 程式碼裡的 secret 或憑證
- 不安全的反序列化
- Path traversal
- SSRF

### 效能
- N+1 query
- 不必要的記憶體配置
- 演算法複雜度（熱路徑裡的 O(n²)）
- 缺少資料庫 index
- 沒有上限的查詢或迴圈
- 資源洩漏

### 正確性
- 邊界情況（空輸入、null、overflow）
- Race condition 與並行問題
- 錯誤處理與傳遞
- Off-by-one 錯誤
- 型別安全

### 可維護性
- 命名清不清楚
- 單一職責
- 重複的程式碼
- 測試覆蓋率
- 不直觀的邏輯有沒有文件

## 輸出

```markdown
## Code Review: [PR title or file]

### Summary
[1-2 sentence overview of the changes and overall quality]

### Critical Issues
| # | File | Line | Issue | Severity |
|---|------|------|-------|----------|
| 1 | [file] | [line] | [description] | 🔴 Critical |

### Suggestions
| # | File | Line | Suggestion | Category |
|---|------|------|------------|----------|
| 1 | [file] | [line] | [description] | Performance |

### What Looks Good
- [Positive observations]

### Verdict
[Approve / Request Changes / Needs Discussion]
```

## 如果有連接器

如果有連上 **~~source control**：
- 從 URL 自動拉 PR diff
- 檢查 CI 狀態和測試結果

如果有連上 **~~project tracker**：
- 把發現連到相關的 ticket
- 確認 PR 有符合所述的需求

如果有連上 **~~knowledge base**：
- 對照團隊的 coding standard 和風格指南檢查變更

## 小提醒

1. **提供背景**：說「這是熱路徑」或「這會處理 PII」，我就能抓到重點。
2. **指定關注點**：說「重點看安全性」可以縮小審查範圍。
3. **附上測試**：我也會檢查測試覆蓋率和品質。
