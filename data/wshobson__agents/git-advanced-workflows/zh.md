---
name: git-advanced-workflows
description: 精通進階 Git 工作流程，包含 rebase、cherry-pick、bisect、worktree 與 reflog，用來維持乾淨的歷史並從任何狀況中還原。適用於管理複雜的 Git 歷史、在功能 branch 上協作，或排查 repository 問題的時候。
---

# Git 進階工作流程

精通進階 Git 技巧，維持乾淨的歷史、有效協作，並且有信心地從任何狀況中還原。

## 什麼時候用這個 Skill

- 在 merge 之前整理 commit 歷史
- 把特定 commit 套用到其他 branch
- 找出引入 bug 的 commit
- 同時處理多個功能
- 從 Git 的失誤或遺失的 commit 中還原
- 管理複雜的 branch 工作流程
- 準備乾淨的 PR 供 review
- 同步分歧的 branch

## 核心概念

### 1. 互動式 Rebase

互動式 rebase 是 Git 歷史編輯的瑞士刀。

**常見操作：**

- `pick`：保留 commit 原樣
- `reword`：修改 commit 訊息
- `edit`：修改 commit 的內容
- `squash`：和前一個 commit 合併
- `fixup`：和 squash 一樣，但捨棄訊息
- `drop`：完全移除 commit

**基本用法：**

```bash
# Rebase 最近 5 個 commit
git rebase -i HEAD~5

# Rebase 目前 branch 上所有的 commit
git rebase -i $(git merge-base HEAD main)

# Rebase 到特定 commit 上
git rebase -i abc123
```

### 2. Cherry-Picking

把特定 commit 從一個 branch 套用到另一個 branch，不用 merge 整個 branch。

```bash
# Cherry-pick 單一 commit
git cherry-pick abc123

# Cherry-pick 一段範圍的 commit（不含起點）
git cherry-pick abc123..def456

# Cherry-pick 但不 commit（只放進 staging）
git cherry-pick -n abc123

# Cherry-pick 並修改 commit 訊息
git cherry-pick -e abc123
```

### 3. Git Bisect

在 commit 歷史上做二分搜尋，找出引入 bug 的 commit。

```bash
# 開始 bisect
git bisect start

# 把目前的 commit 標記為壞的
git bisect bad

# 標記已知正常的 commit
git bisect good v1.0.0

# Git 會 checkout 中間的 commit，請測試它
# 然後標記為好或壞
git bisect good  # 或：git bisect bad

# 持續進行直到找到 bug
# 完成後
git bisect reset
```

**自動化 Bisect：**

```bash
# 用腳本自動測試
git bisect start HEAD v1.0.0
git bisect run ./test.sh

# test.sh 正常時應該 exit 0，異常時 exit 1-127（125 除外）
```

### 4. Worktree

同時在多個 branch 上工作，不用 stash 或切換。

```bash
# 列出現有的 worktree
git worktree list

# 為功能 branch 新增 worktree
git worktree add ../project-feature feature/new-feature

# 新增 worktree 並建立新 branch
git worktree add -b bugfix/urgent ../project-hotfix main

# 移除 worktree
git worktree remove ../project-feature

# 清除過期的 worktree
git worktree prune
```

### 5. Reflog

你的安全網：追蹤所有 ref 的移動，連被刪除的 commit 也包含在內。

```bash
# 查看 reflog
git reflog

# 查看特定 branch 的 reflog
git reflog show feature/branch

# 還原被刪除的 commit
git reflog
# 找出 commit hash
git checkout abc123
git branch recovered-branch

# 還原被刪除的 branch
git reflog
git branch deleted-branch abc123
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務

1. **一律使用 --force-with-lease**：比 --force 安全，避免覆蓋別人的工作
2. **只 rebase 本機的 commit**：不要 rebase 已經 push 並共享出去的 commit
3. **寫有描述性的 commit 訊息**：未來的你會感謝現在的你
4. **Atomic commit**：每個 commit 應該只做一個邏輯上的變更
5. **Force push 之前先測試**：確認改寫歷史沒有弄壞任何東西
6. **隨時留意 Reflog**：Reflog 是你的安全網，但從目前 tip 無法到達的 commit，其紀錄預設 30 天後就會過期（`gc.reflogExpireUnreachable`），可到達的紀錄則是 90 天後（`gc.reflogExpire`）
7. **有風險的操作之前先開 Branch**：做複雜的 rebase 之前先建立備份 branch

```bash
# 安全的 force push
git push --force-with-lease origin feature/branch

# 在有風險的操作之前先建立備份
git branch backup-branch
git rebase -i main
# 如果出了問題
git reset --hard backup-branch
```

## 常見陷阱

- **Rebase 公開的 Branch**：會讓協作者遇到歷史衝突
- **沒有 lease 的 Force Push**：可能會覆蓋隊友的工作
- **在 Rebase 中遺失工作**：小心解決衝突，rebase 之後要測試
- **忘記清理 Worktree**：被遺棄的 worktree 會占用磁碟空間
- **實驗前沒有備份**：一律建立安全用的 branch
- **在髒的 Working Directory 上做 Bisect**：bisect 之前先 commit 或 stash

## 還原指令

```bash
# 中止進行中的操作
git rebase --abort
git merge --abort
git cherry-pick --abort
git bisect reset

# 把檔案還原成特定 commit 的版本
git restore --source=abc123 path/to/file

# 復原上一個 commit，但保留變更
git reset --soft HEAD^

# 復原上一個 commit，並捨棄變更
# 警告：--hard 也會刪除未 commit 的變更（已 staged 和未 staged 的），
# 而且 reflog 無法救回它們。先檢查 `git status` 並 stash。
git reset --hard HEAD^

# 盡快還原被刪除的 branch。預設情況下，git gc 可以在 HEAD 的 reflog
# 中未 merge 的 commit 紀錄滿 30 天後清除它們，從每筆紀錄被記錄
# 的時間開始算，不是從刪除時開始算
# 刪除 branch 也會刪除它自己的 reflog；去搜尋 HEAD 的 reflog
git reflog
git branch recovered-branch abc123
```
