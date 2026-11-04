---
name: using-git-worktrees
description: 開始需要跟目前工作區隔離的功能開發，或執行實作計畫之前使用：透過原生工具或 git worktree 備援，確保有一個隔離的工作區
---

# Using Git Worktrees

## 概述

確保工作在隔離的工作區裡進行。優先使用你的平台原生的 worktree 工具。只有在沒有原生工具可用時，才退回手動的 git worktree。

**核心原則：** 先偵測既有的隔離。再用原生工具。最後才退回 git。絕對不要跟 harness 對著幹。

**開始時宣告：**「I'm using the using-git-worktrees skill to set up an isolated workspace.」

## 步驟 0：偵測既有的隔離

**建立任何東西之前，先檢查你是不是已經在隔離的工作區裡。**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**Submodule 防護：** 在 git submodule 裡面，`GIT_DIR != GIT_COMMON` 也成立。在下結論「已經在 worktree 裡」之前，先確認你不是在 submodule 裡：

```bash
# If this returns a path, you're in a submodule, not a worktree — treat as normal repo
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**如果 `GIT_DIR != GIT_COMMON`（而且不是 submodule）：** 你已經在一個 linked worktree 裡了。跳到步驟 2（專案設定）。「不要」再建立另一個 worktree。

依 branch 狀態回報：
- 在某個 branch 上：「Already in isolated workspace at `<path>` on branch `<name>`.」
- Detached HEAD：「Already in isolated workspace at `<path>` (detached HEAD, externally managed). Branch creation needed at finish time.」

**如果 `GIT_DIR == GIT_COMMON`（或在 submodule 裡）：** 你在一般的 repo checkout 裡。

使用者有沒有已經在你的指示裡表明他們對 worktree 的偏好？如果沒有，建立 worktree 之前要先徵求同意：

> 「Would you like me to set up an isolated worktree? It protects your current branch from changes.」

任何已經宣告過的偏好，就照辦，不要再問。如果使用者不同意，就在原地工作，跳到步驟 2。

## 步驟 1：建立隔離的工作區

**你有兩種機制。照這個順序試。**

### 1a. 原生 Worktree 工具（優先）

使用者已經要求隔離的工作區了（步驟 0 的同意）。你是不是已經有建立 worktree 的方法？它可能是名稱像 `EnterWorktree`、`WorktreeCreate` 的工具、`/worktree` 指令，或 `--worktree` 旗標。如果有，就用它，並跳到步驟 2。

原生工具會自動處理目錄位置、建立 branch 和清理。有原生工具卻去用 `git worktree add`，會製造出你的 harness 看不到也管理不了的幽靈狀態。

只有在沒有可用的原生 worktree 工具時，才進入步驟 1b。

### 1b. Git Worktree 備援

**只有在步驟 1a 不適用時才用這個**：也就是你沒有可用的原生 worktree 工具。用 git 手動建立 worktree。

#### 目錄選擇

依照這個優先順序。使用者明確的偏好，永遠勝過觀察到的檔案系統狀態。

1. **檢查你的指示裡有沒有宣告的 worktree 目錄偏好。** 如果使用者已經指定了，就用它，不要再問。

2. **檢查有沒有既有的專案內 worktree 目錄：**
   ```bash
   ls -d .worktrees 2>/dev/null     # Preferred (hidden)
   ls -d worktrees 2>/dev/null      # Alternative
   ```
   找到的話就用它。如果兩個都存在，`.worktrees` 優先。

3. **如果沒有其他指引可用**，預設用專案根目錄下的 `.worktrees/`。

#### 安全驗證（只針對專案內的目錄）

**建立 worktree 之前，一定要確認該目錄有被忽略：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**如果「沒有」被忽略：** 加進 .gitignore，commit 這個變更，然後再繼續。

**為什麼重要：** 避免不小心把 worktree 的內容 commit 進 repo。

#### 建立 Worktree

```bash
# Determine path based on chosen location
path="$LOCATION/$BRANCH_NAME"

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**Sandbox 備援：** 如果 `git worktree add` 因為權限錯誤而失敗（被 sandbox 拒絕），告訴使用者 sandbox 擋下了 worktree 的建立，你改在目前的目錄裡工作。然後在原地執行 setup 和基準測試。

## 步驟 2：專案設定

自動偵測並執行適當的 setup：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

## 步驟 3：驗證乾淨的基準

跑測試，確保工作區是乾淨的起點：

```bash
# Use project-appropriate command
npm test / cargo test / pytest / go test ./...
```

**如果測試失敗：** 回報失敗，問是要繼續還是要先調查。

**如果測試通過：** 回報已就緒。

### 回報

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## 快速參考

| 情況 | 動作 |
|-----------|--------|
| 已經在 linked worktree 裡 | 跳過建立（步驟 0） |
| 在 submodule 裡 | 當成一般 repo（步驟 0 的防護） |
| 有原生 worktree 工具 | 用它（步驟 1a） |
| 沒有原生工具 | Git worktree 備援（步驟 1b） |
| `.worktrees/` 存在 | 用它（確認有被忽略） |
| `worktrees/` 存在 | 用它（確認有被忽略） |
| 兩個都存在 | 用 `.worktrees/` |
| 兩個都不存在 | 檢查指示檔，然後預設用 `.worktrees/` |
| 目錄沒被忽略 | 加進 .gitignore + commit |
| 建立時出現權限錯誤 | Sandbox 備援，在原地工作 |
| 基準測試失敗 | 回報失敗 + 詢問 |
| 沒有 package.json/Cargo.toml | 跳過安裝依賴 |

## 常見的合理化藉口

| 藉口 | 現實 |
|--------|---------|
| 「我顯然不在 worktree 裡，不用檢查」 | 執行步驟 0。Harness 建立的隔離和 submodule 都會騙過目測；偵測指令才能定案。 |
| 「`git worktree add` 比找原生工具快」 | 原生工具（例如 `EnterWorktree`）負責目錄位置、建立 branch 和清理。繞過它是第 1 名的錯誤：它會製造出你的 harness 看不到也管理不了的幽靈狀態。 |
| 「Worktree 目錄肯定已經被忽略了」 | 執行 `git check-ignore`。沒被忽略的 worktree 目錄，會把整棵樹 commit 進 repo。 |
| 「隨便什麼目錄名稱都行」 | 明確的指示勝過既有的專案內目錄，而既有的專案內目錄又勝過預設的 `.worktrees/`。 |
| 「工作區是全新的，基準測試可以等」 | 髒的基準會讓之後每個失敗都變得含糊。現在就跑測試；要不要帶著失敗繼續，是你的搭檔決定。 |
