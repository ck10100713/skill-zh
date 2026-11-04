---
name: git-workflow
description: "引導式 git 工作流程：準備 PR、清理 branch、解決 merge conflict、處理 monorepo tag、squash-and-merge 模式。當被要求準備 PR、清 branch、解 conflict 或打 release tag 時使用。"
compatibility: claude-code-only
---

# Git Workflow

針對常見的 git 操作提供引導式流程，這些操作照著結構化步驟做會更順。

## PR 準備

準備 pull request 時：

1. **蒐集 context**
   - `git log main..HEAD --oneline`：列出 branch 上所有 commit
   - `git diff main...HEAD --stat`：看所有改動的檔案
   - `git status`：檢查有沒有還沒 commit 的東西

2. **擬 PR 內容**
   - 標題：70 字元以內，描述這次改動（不是 branch 名稱）
   - 內文：摘要「為什麼」，列出關鍵改動，加上測試計畫
   - 用 commit 歷史來寫摘要，不要靠記憶

3. **Push 並建立 PR**
   ```bash
   git push -u origin HEAD
   gh pr create --title "..." --body "$(cat <<'EOF'
   ## Summary
   - ...

   ## Test plan
   - [ ] ...

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

4. **驗證**：用 `gh pr view --web` 在瀏覽器打開

## Branch 清理

安全地清掉已經 merge 的 branch：

1. **切到 main 並拉最新**
   ```bash
   git checkout main && git pull
   ```

2. **列出已 merge 的 branch**（排除 main/master/develop）
   ```bash
   git branch --merged main | grep -vE '^\*|main|master|develop'
   ```

3. **刪除本地已 merge 的 branch**
   ```bash
   git branch --merged main | grep -vE '^\*|main|master|develop' | xargs -r git branch -d
   ```

4. **清掉遠端追蹤 ref**
   ```bash
   git fetch --prune
   ```

5. **列出沒有本地追蹤的遠端 branch**（選用）
   ```bash
   git branch -r --merged origin/main | grep -vE 'main|master|develop|HEAD'
   ```

## Merge Conflict 解決

PR 有 conflict 時：

1. **評估 conflict 的範圍**
   ```bash
   git fetch origin
   git merge origin/main --no-commit --no-ff
   git diff --name-only --diff-filter=U  # List conflicted files
   ```

2. **對每個有 conflict 的檔案**，讀檔案並解決：
   - 如果兩邊改的是不同區域，兩邊都留
   - 如果在架構上不相容，採用 main branch 的做法，再把 PR 的意圖重新套在上面

3. **如果 rebase 比較乾淨**（commit 不多、沒有共用歷史）：
   ```bash
   git rebase origin/main
   # Resolve conflicts per commit, then:
   git rebase --continue
   ```

4. **如果 rebase 很亂**（conflict 很多、架構已經分歧）：
   - 中止：`git rebase --abort` 或 `git merge --abort`
   - 抽出有用的程式碼：`git show origin/branch:path/to/file > /tmp/extracted.txt`
   - 手動把改動套到 main
   - 關掉原本的 PR 並說明原因

5. **驗證**：跑測試，確認 diff 看起來正確

## Monorepo Release Tag

在 monorepo 裡，tag 要限定在 package 範圍：

```bash
# ❌ Ambiguous in monorepos
git tag v2.1.0

# ✅ Scoped to package
git tag contextbricks-v2.1.0
git push origin contextbricks-v2.1.0
```

格式：`{package-name}-v{semver}`

## 先建 .gitignore 再 init

建立新 repo 時，一定要在第一次 `git add` **之前**先建好 `.gitignore`：

```bash
cat > .gitignore << 'EOF'
node_modules/
.wrangler/
dist/
.dev.vars
*.log
.DS_Store
.env
.env.local
EOF

git init && git add . && git commit -m "Initial commit"
```

**如果 node_modules 已經被追蹤了：**
```bash
git rm -r --cached node_modules/
git commit -m "Remove node_modules from tracking"
```

## Private Repo 授權稽核

要發布或分享 private repo 之前：

```bash
gh repo view --json visibility -q '.visibility'
```

如果是 `PRIVATE`，確認：
- `LICENSE` 是專有授權聲明（不是 MIT/Apache）
- `package.json` 有 `"license": "UNLICENSED"` 和 `"private": true`
- 沒有 `CONTRIBUTING.md`，README 裡也沒有「歡迎貢獻」的字眼
