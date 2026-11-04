---
name: finishing-a-development-branch
description: 當實作完成、所有測試都通過，而你需要決定怎麼整合這份工作時使用
---

# Finishing a Development Branch

## 概述

**核心原則：** 驗證測試 → 偵測環境 → 呈現選項 → 執行選擇 → 清理。

**開始時宣告：**「I'm using the finishing-a-development-branch skill to complete this work.」

## 步驟 1：驗證測試

跑專案完整的測試套件（`npm test` / `cargo test` / `pytest` / `go test ./...`）。

**如果測試失敗**，回報失敗並停下來：選單要等套件全綠之後才出現：

```
Tests failing (<N> failures). Must fix before completing:

[Show failures]
```

**如果測試通過：** 繼續步驟 2。

## 步驟 2：偵測環境

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
# Capture now, while still inside the workspace — Step 5 changes directory
# before cleanup (Step 6) needs this value
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

這會決定要顯示哪個選單，以及怎麼清理：

| 狀態 | 選單 | 清理 |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON`（一般 repo） | 標準的 3 個選項 | 沒有 worktree 要清理 |
| `GIT_DIR != GIT_COMMON`，有名稱的 branch | 標準的 3 個選項 | 依來源決定（見步驟 6） |
| `GIT_DIR != GIT_COMMON`，detached HEAD | 精簡的 2 個選項（沒有 merge） | 由外部管理，留在原地 |

## 步驟 3：確定 Base Branch

Base branch 就是這份工作當初從哪裡分出來的：通常會寫在計畫、對話，或這個 branch 的 upstream 裡。如果還不知道，就問：「This branch split from <your best guess> - is that correct?」merge 之前要先確認：merge 到錯的 base，要還原很麻煩。

## 步驟 4：呈現選項

**一般 repo 和有名稱 branch 的 worktree：只呈現這 3 個選項，一個都不能多：**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)

Which option?
```

**Detached HEAD：只呈現這 2 個選項，一個都不能多：**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)

Which option?
```

選單要完全照寫的呈現：簡潔，每個選項都來自上面的清單。只有在你的搭檔明確要求時，才會發生捨棄這份工作（見下面的「如果你的搭檔要求捨棄這份工作」）。等他們的答案；整合的決定是他們的。

## 步驟 5：執行選擇

### 選項 1：在本機 Merge

```bash
# Get main repo root for CWD safety
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

# Merge first — verify success before removing anything
git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>
```

如果 merge 之後的結果測試失敗：停下來，把 worktree 和 branch 留在原地，然後調查：什麼都還沒 push，所以這次 merge 只在本機，可以復原。

一旦 merge 之後的結果全綠：清理 worktree（步驟 6），然後刪除 branch：

```bash
git branch -d <feature-branch>
```

### 選項 2：Push 並建立 PR

```bash
git push -u origin <feature-branch>
# From a detached HEAD, name the new branch on the remote:
# git push origin HEAD:refs/heads/<new-branch>
```

然後用該 forge 的工具（如果有 CLI 就用它，或是大多數 forge 在你 push 時會印出的建立連結），對 <base-branch> 建立 pull/merge request，如果 repo 有 PR 範本和慣例就照著做，並把 URL 回報給你的搭檔。

保留 worktree：你的搭檔會在那裡針對 PR 回饋反覆修改。

### 選項 3：保持原樣

回報：「Keeping branch <name>. Worktree preserved at <path>.」

### 如果你的搭檔要求捨棄這份工作

這條路徑只存在於回應明確的「把這份工作丟掉」請求。先確認：

```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

等那個確切的確認。收到之後：

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
```

然後清理 worktree（步驟 6），並強制刪除 branch：

```bash
git branch -D <feature-branch>
```

## 步驟 6：清理工作區

**選項 1 和已確認的捨棄會執行這步。** 選項 2 和 3 一律保留 worktree。兩個呼叫方都已經切換到主 repo 的根目錄（移除 worktree 必須從 worktree 外面執行），並使用步驟 2 在切換目錄之前擷取的 `GIT_DIR`/`GIT_COMMON`/`WORKTREE_PATH` 值。

**如果 `GIT_DIR == GIT_COMMON`：** 一般 repo，沒有 worktree 要清理。完成。

**如果 `WORKTREE_PATH` 在 `.worktrees/` 或 `worktrees/` 底下：** 這個 worktree 是 Superpowers 建立的，由我們負責清理：

```bash
git worktree remove "$WORKTREE_PATH"
git worktree prune  # Self-healing: clean up any stale registrations
```

**如果移除被拒絕**（`contains modified or untracked files`）：這個 worktree 裡有別處不存在的檔案：沒 commit 的計畫、筆記或暫存工作。絕對不要自作主張用 `--force`。讓你的搭檔看到有什麼風險，並問他們：

```bash
git -C "$WORKTREE_PATH" status --porcelain -uall
```

```
Worktree removal refused — these files were never committed:

<file list>

1. Commit them to <branch> before cleanup
2. Move them into <main repo root>
3. Delete them (unrecoverable)

Which?
```

執行他們的選擇，然後移除 worktree。

**其他情況：** 這個工作區歸宿主環境管理，留在原地。如果你的平台有提供離開工作區的工具，就用它。

## 快速參考

| 選項 | Merge | Push | 保留 Worktree | 清理 Branch |
|--------|-------|------|---------------|----------------|
| 1. 在本機 merge | 是 | - | - | 是 |
| 2. 建立 PR | - | 是 | 是 | - |
| 3. 保持原樣 | - | - | 是 | - |
| 捨棄（只在明確要求時） | - | - | - | 是（強制） |

## 常見的合理化藉口

| 藉口 | 現實 |
|--------|---------|
| 「這個 session 稍早測試通過了」 | 對你即將整合的那棵樹跑一次套件。一次全綠只能證明它跑的那棵樹。 |
| 「他們顯然想要 merge」 | 整合是你的搭檔的決定。呈現選單，然後等。 |
| 「他們看起來做完這個功能了，我來提議捨棄它」 | 選單照寫的就是完整的。只有你的搭檔明明白白地要求時，才會發生捨棄。 |
| 「『對，丟掉它』就算確認」 | 只有打出 `discard` 這個字，才授權刪除。 |
| 「PR 已經開了，所以 worktree 現在是雜物」 | PR 的回饋就在那個 worktree 裡修。工作落地之前，它都要留著。 |
| 「另一個 worktree 看起來過期了，我也順便清掉」 | 只清理 `.worktrees/` 或 `worktrees/` 底下的 worktree。其他的都屬於宿主。 |
| 「移除被拒絕了，`--force` 只是把清理做完」 | 被拒絕表示有檔案只存在於那個 worktree 裡。`--force` 會永久摧毀它們。讓你的搭檔看，然後問。 |
| 「merge 後的結果失敗大概是 flaky」 | Merge 後的結果失敗，一切都要停。調查的時候，branch 和 worktree 都留在原地。 |
| 「Base branch 顯然是 main」 | 確認分岔點，或去問。merge 到錯的 base，要還原很麻煩。 |
| 「Push 被拒絕了，force-push 就能解決」 | Push 被拒絕表示遠端有變動。去調查；只有你的搭檔明確要求時才能 force-push。 |
