---
name: terminal-ops
description: ECC 的證據優先 repo 執行工作流。當使用者想跑某個指令、檢查 repo、除錯 CI 失敗，或推一個範圍很窄的修正，並要求附上確切證據證明執行了什麼、驗證了什麼時使用。
metadata:
  origin: ECC
---

# Terminal Ops

當使用者要的是真正在 repo 裡執行：跑指令、檢查 git 狀態、除錯 CI 或 build、做一個範圍很窄的修正，並準確回報改了什麼、驗證了什麼，就用這個。

這個 skill 刻意比一般的寫程式指引窄。它是證據優先的終端機執行操作員工作流。

## Skill 組合

相關時，把這些 ECC 原生 skill 拉進工作流：

- `verification-loop`：改完之後的確切驗證步驟
- `tdd-workflow`：當正確的修法需要回歸測試覆蓋時
- `security-review`：涉及祕密、認證或外部輸入時
- `github-ops`：任務取決於 CI 執行、PR 狀態或 release 狀態時
- `knowledge-ops`：驗證過的結果需要被記錄成長久的專案 context 時

## 何時使用

- 使用者說「fix」、「debug」、「run this」、「check the repo」或「push it」
- 任務取決於指令輸出、git 狀態、測試結果，或驗證過的本機修正
- 回答必須區分：本機已改、本機已驗證、已 commit、已 push

## 護欄

- 先檢查再編輯
- 如果使用者只要求稽核/review，就保持唯讀
- 優先用 repo 本地的 script 和 helper，不要臨時拼湊 ad hoc 的包裝
- 驗證用的指令沒有重跑之前，不要說已修好
- 除非 branch 真的推到 upstream，否則不要說已 push

## 工作流

### 1. 確定工作範圍

確定：

- 確切的 repo 路徑
- branch
- 本機 diff 狀態
- 要求的模式：
  - inspect
  - fix
  - verify
  - push

### 2. 先讀出問題的地方

在改任何東西之前：

- 檢查錯誤
- 檢查檔案或測試
- 檢查 git 狀態
- 先用已經提供的 log 或 context，不要盲目重讀

### 3. 讓修正保持窄

一次解決一個主要的失敗：

- 先用最小而有用的驗證指令
- 本機的失敗處理掉之後，才升級成更大的 build/test
- 如果某個指令一直以同樣的特徵失敗，就停止大範圍的重試，把範圍縮小

### 4. 準確回報執行狀態

用精確的狀態用語：

- inspected
- changed locally
- verified locally
- committed
- pushed
- blocked

## 輸出格式

```text
SURFACE
- repo
- branch
- requested mode

EVIDENCE
- failing command / diff / test

ACTION
- what changed

STATUS
- inspected / changed locally / verified locally / committed / pushed / blocked
```

## 陷阱

- 能讀到 repo 即時狀態時，不要憑過時的記憶工作
- 不要把窄範圍的修正擴大成整個 repo 的大改
- 不要用破壞性的 git 指令
- 不要忽略不相關的本機工作

## 驗證

- 回應要指名驗證用的指令或測試
- 跟 git 相關的工作要指名 repo 路徑和 branch
- 任何 push 的宣稱都要包含目標 branch 和確切的結果
