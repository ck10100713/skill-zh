---
name: parallel-debugging
description: 用互相競爭的假設、平行調查、證據蒐集與根因仲裁來除錯複雜問題。在除錯有多個可能成因的 bug、做根因分析，或組織平行調查工作流程時使用。
version: 1.0.2
---

# Parallel Debugging

用 Analysis of Competing Hypotheses（ACH）方法，搭配平行的 agent 調查，來除錯複雜問題的框架。

## When to Use This Skill

- Bug 有多個說得通的根因
- 最初的除錯嘗試沒找出問題
- 問題橫跨多個模組或元件
- 需要有證據支持的系統化根因分析
- 想在除錯時避免確認偏誤

## Hypothesis Generation Framework

從 6 種失效模式類別產生假設：

### 1. Logic Error

- 條件邏輯不正確（運算子錯誤、漏掉情況）
- 迴圈或陣列存取的 off-by-one 錯誤
- 缺少邊界案例處理
- 演算法實作不正確

### 2. Data Issue

- 無效或非預期的輸入資料
- 型別不符或轉型錯誤
- 本應有值的地方是 null/undefined/None
- 編碼或序列化問題
- 資料被截斷或溢位

### 3. State Problem

- 並行操作之間的 race condition
- 過期的快取回傳舊資料
- 初始化或預設值不正確
- 共用 state 被意外修改
- 狀態機轉換錯誤

### 4. Integration Failure

- 違反 API 契約（請求/回應不符）
- 元件之間版本不相容
- 不同環境之間設定不一致
- 缺少或錯誤的環境變數
- 網路逾時或連線失敗

### 5. Resource Issue

- 記憶體洩漏導致效能逐漸變差
- Connection pool 耗盡
- File descriptor 或 handle 洩漏
- 磁碟空間或配額用盡
- 低效率的處理造成 CPU 飽和

### 6. Environment

- 缺少執行期相依套件
- 函式庫或框架版本錯誤
- 平台特有的行為差異
- 權限或存取控制問題
- 與時區或地區設定相關的行為

## Evidence Collection Standards

### What Constitutes Evidence

| Evidence Type     | Strength | Example                                                         |
| ----------------- | -------- | --------------------------------------------------------------- |
| **Direct**        | 強   | `file.ts:42` 的程式碼是 `if (x > 0)`，應該是 `if (x >= 0)` |
| **Correlational** | 中   | 錯誤率在 commit `abc123` 之後上升                      |
| **Testimonial**   | 弱     | 「在我的機器上是好的」                                       |
| **Absence**       | 不一定 | 在這條程式碼路徑上找不到 null 檢查                            |

### Citation Format

引用證據時一律附上 file:line 參照：

```
**Evidence**: The validation function at `src/validators/user.ts:87`
does not check for empty strings, only null/undefined. This allows
empty email addresses to pass validation.
```

### Confidence Levels

| Level               | Criteria                                                                            |
| ------------------- | ----------------------------------------------------------------------------------- |
| **High (>80%)**     | 有多項直接證據、因果鏈清楚、沒有互相矛盾的證據      |
| **Medium (50-80%)** | 有一些直接證據、因果鏈說得通、有小幅的模糊之處                     |
| **Low (<50%)**      | 多半是相關性證據、因果鏈不完整、有一些互相矛盾的證據 |

## Result Arbitration Protocol

所有調查者都回報之後：

### Step 1: Categorize Results

- **Confirmed**：高信心、證據充分、因果鏈清楚
- **Plausible**：中等信心、有一些證據、因果鏈合理
- **Falsified**：有證據反駁這個假設
- **Inconclusive**：證據不足，無法證實也無法推翻

### Step 2: Compare Confirmed Hypotheses

如果有多個假設被證實，依下列順序排序：

1. 信心等級
2. 支持證據的數量
3. 因果鏈的強度
4. 沒有互相矛盾的證據

### Step 3: Determine Root Cause

- 如果有一個假設明顯勝出：宣告它是根因
- 如果多個假設的可能性相當：可能是複合問題（多個成因共同造成）
- 如果沒有任何假設被證實：根據已蒐集的證據產生新的假設

### Step 4: Validate Fix

在宣告 bug 已修好之前：

- [ ] 修正處理的是找出來的根因
- [ ] 修正沒有引入新問題
- [ ] 原本的重現案例不再失敗
- [ ] 相關的邊界案例都有涵蓋
- [ ] 已新增或更新相關測試
