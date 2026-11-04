---
name: project-flow-ops
description: 在 GitHub 和 Linear 之間運作執行流程：分流處理 issue 和 pull request、串起進行中的工作，並讓 GitHub 維持對外公開、Linear 維持內部執行層。使用者想控制 backlog、分流 PR，或協調 GitHub 到 Linear 時使用。
metadata:
  origin: ECC
---

# Project Flow Ops

這個 skill 把互不相連的 GitHub issue、PR 和 Linear 任務，變成一條統一的執行流程。

問題是協調，不是寫程式的時候，就用它。

## 何時使用

- 分流處理累積的 PR 或 issue backlog
- 決定什麼該放進 Linear、什麼該只留在 GitHub
- 把進行中的 GitHub 工作，連結到內部的執行流程
- 把 PR 分類成 merge、port/rebuild、close 或 park
- 稽核 review 留言、CI 失敗或過期的 issue，是否正在卡住執行

## 運作模式

- **GitHub** 是公開和社群的事實
- **Linear** 是進行中、已排程工作的內部執行事實
- 不是每個 GitHub issue 都需要有 Linear issue
- 只有在工作符合下列情況時，才建立或更新 Linear：
  - 進行中
  - 已委派
  - 已排程
  - 跨職能
  - 重要到值得在內部追蹤

## 核心工作流程

### 1. 先讀公開的那一面

蒐集：

- GitHub issue 或 PR 的狀態
- 作者和 branch 的狀態
- review 留言
- CI 狀態
- 連結的 issue

### 2. 把工作分類

每個項目最後都應該落在這幾種狀態之一：

| 狀態 | 意義 |
|-------|---------|
| Merge | 自成一體、符合政策、已就緒 |
| Port/Rebuild | 想法有用，但應該在 ECC 裡手動重新落地 |
| Close | 方向錯誤、過期、不安全或重複 |
| Park | 可能有用，但現在還沒排程 |

### 3. 決定是否需要 Linear

只有在下列情況才建立或更新 Linear：

- 已經積極規劃要執行
- 牽涉到多個 repo 或工作流
- 這項工作需要內部的負責人或排序
- 這個 issue 是更大的 program 流程的一部分

不要機械式地把所有東西都鏡像過去。

### 4. 讓兩個系統保持一致

當工作進行中：

- GitHub 的 issue/PR 應該公開說明目前發生了什麼事
- Linear 應該在內部追蹤負責人、優先順序和執行流程

當工作出貨或被否決：

- 把公開的結論貼回 GitHub
- 相應地標記 Linear 任務

## Review 規則

- 絕對不要只憑標題、摘要或信任就 merge，要看完整的 diff
- 來源在外部的功能，如果有價值但不是自成一體，就應該在 ECC 裡重建
- CI 是紅的，就要分類並修好，或擋下；不要假裝它可以 merge 了
- 如果真正的阻礙是產品方向，就直接講，不要躲在工具後面

## 輸出格式

回傳：

```text
PUBLIC STATUS
- issue / PR state
- CI / review state

CLASSIFICATION
- merge / port-rebuild / close / park
- one-paragraph rationale

LINEAR ACTION
- create / update / no Linear item needed
- project / lane if applicable

NEXT OPERATOR ACTION
- exact next move
```

## 好的使用情境

- 「稽核目前開著的 PR backlog，告訴我哪些該 merge、哪些該重建」
- 「把 GitHub issue 對應到我們的 ECC 1.x 和 ECC 2.0 program 流程」
- 「檢查這個是否需要 Linear issue，還是應該只留在 GitHub」
