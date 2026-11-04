---
name: git-workflow
description: Git 工作流程模式，包含分支策略、commit 慣例、保持歷史乾淨易讀、merge 前整理本地 commit、merge 對 rebase、衝突解決，以及適用於各種規模團隊的協作開發最佳實務。選擇分支策略、撰寫 commit 慣例、在 pull request 前整理歷史、決定要 merge 還是 rebase，或解決衝突時使用。
metadata:
  origin: ECC
---

# Git Workflow Patterns

Git 版本控制、分支策略和協作開發的最佳實務。

## When to Activate

- 為新專案設定 Git 工作流程
- 決定分支策略（GitFlow、trunk-based、GitHub flow）
- 撰寫 commit message 和 PR 描述
- 解決 merge 衝突
- 管理 release 和版本 tag
- 讓新進團隊成員上手 Git 的做法

## Branching Strategies

### GitHub Flow (Simple, Recommended for Most)

最適合持續部署和中小型團隊。

```
main (protected, always deployable)
  │
  ├── feature/user-auth      → PR → merge to main
  ├── feature/payment-flow   → PR → merge to main
  └── fix/login-bug          → PR → merge to main
```

**規則：**
- `main` 隨時都可以部署
- 從 `main` 建立 feature branch
- 準備好 review 時，開 Pull Request
- 核准且 CI 通過後，merge 進 `main`
- merge 之後立刻部署

### Trunk-Based Development (High-Velocity Teams)

最適合 CI/CD 很強、有 feature flag 的團隊。

```
main (trunk)
  │
  ├── short-lived feature (1-2 days max)
  ├── short-lived feature
  └── short-lived feature
```

**規則：**
- 大家都 commit 到 `main`，或是生命週期非常短的 branch
- 用 feature flag 把未完成的工作藏起來
- merge 之前 CI 一定要通過
- 一天部署好幾次

### GitFlow (Complex, Release-Cycle Driven)

最適合有固定發版時程的專案和企業專案。

```
main (production releases)
  │
  └── develop (integration branch)
        │
        ├── feature/user-auth
        ├── feature/payment
        │
        ├── release/1.0.0    → merge to main and develop
        │
        └── hotfix/critical  → merge to main and develop
```

**規則：**
- `main` 只放可以上 production 的程式碼
- `develop` 是整合用的 branch
- feature branch 從 `develop` 切出來，merge 回 `develop`
- release branch 從 `develop` 切出來，merge 到 `main` 和 `develop`
- hotfix branch 從 `main` 切出來，同時 merge 到 `main` 和 `develop`

### When to Use Which

| Strategy | Team Size | Release Cadence | Best For |
|----------|-----------|-----------------|----------|
| GitHub Flow | 不限 | 持續 | SaaS、web app、新創公司 |
| Trunk-Based | 5 人以上、有經驗 | 一天多次 | 高速團隊、有 feature flag |
| GitFlow | 10 人以上 | 固定時程 | 企業、受法規管制的產業 |

## Commit Messages

### Conventional Commits Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### Types

| Type | Use For | Example |
|------|---------|---------|
| `feat` | 新功能 | `feat(auth): add OAuth2 login` |
| `fix` | 修 bug | `fix(api): handle null response in user endpoint` |
| `docs` | 文件 | `docs(readme): update installation instructions` |
| `style` | 格式調整，沒有程式碼變動 | `style: fix indentation in login component` |
| `refactor` | 程式碼重構 | `refactor(db): extract connection pool to module` |
| `test` | 新增/更新測試 | `test(auth): add unit tests for token validation` |
| `chore` | 維護性的雜務 | `chore(deps): update dependencies` |
| `perf` | 效能改善 | `perf(query): add index to users table` |
| `ci` | CI/CD 變更 | `ci: add PostgreSQL service to test workflow` |
| `revert` | 還原先前的 commit | `revert: revert "feat(auth): add OAuth2 login"` |

### Good vs Bad Examples

```
# BAD：含糊，沒有脈絡
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "WIP"

# GOOD：清楚、具體，說明為什麼
git commit -m "fix(api): retry requests on 503 Service Unavailable

The external API occasionally returns 503 errors during peak hours.
Added exponential backoff retry logic with max 3 attempts.

Closes #123"
```

### Commit Message Template

在 repo 根目錄建立 `.gitmessage`：

```
# <type>(<scope>): <subject>
# # Types: feat, fix, docs, style, refactor, test, chore, perf, ci, revert
# Scope: api, ui, db, auth, etc.
# Subject: imperative mood, no period, max 50 chars
#
# [optional body] - explain why, not what
# [optional footer] - Breaking changes, closes #issue
```

用這個指令啟用：`git config commit.template .gitmessage`

## Merge vs Rebase

### Merge (Preserves History)

```bash
# 建立一個 merge commit
git checkout main
git merge feature/user-auth

# 結果：
# *   merge commit
# |\
# | * feature commits
# |/
# * main commits
```

**適用時機：**
- 把 feature branch merge 進 `main`
- 你想保留確切的歷史
- 有多個人在這個 branch 上工作
- 這個 branch 已經 push 出去，別人可能已經以它為基礎開發

### Rebase (Linear History)

```bash
# 把 feature commit 改寫到目標 branch 上
git checkout feature/user-auth
git rebase main

# 結果：
# * feature commits (rewritten)
# * main commits
```

**適用時機：**
- 用最新的 `main` 更新你本地的 feature branch
- 你想要線性、乾淨的歷史
- 這個 branch 只存在本地（沒有 push 過）
- 只有你一個人在這個 branch 上工作

### Rebase Workflow

```bash
# 用最新的 main 更新 feature branch（開 PR 之前）
git checkout feature/user-auth
git fetch origin
git rebase origin/main

# 解決任何衝突
# 測試應該仍然要通過

# Force push（只有在你是唯一的貢獻者時才這樣做）
git push --force-with-lease origin feature/user-auth
```

### When NOT to Rebase

```
# 絕對不要 rebase 符合下列情況的 branch：
- 已經 push 到共用 repository 的
- 別人已經以它為基礎開發的
- 受保護的 branch（main、develop）
- 已經 merge 過的

# 原因：rebase 會改寫歷史，破壞別人的工作
```

## Pull Request Workflow

### PR Title Format

```
<type>(<scope>): <description>

Examples:
feat(auth): add SSO support for enterprise users
fix(api): resolve race condition in order processing
docs(api): add OpenAPI specification for v2 endpoints
```

### PR Description Template

```markdown
## What

Brief description of what this PR does.

## Why

Explain the motivation and context.

## How

Key implementation details worth highlighting.

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Screenshots (if applicable)

Before/after screenshots for UI changes.

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Tests pass locally
- [ ] Related issues linked

Closes #123
```

### Code Review Checklist

**給 Reviewer：**

- [ ] 程式碼有解決所述的問題嗎？
- [ ] 有沒有沒處理到的邊界情況？
- [ ] 程式碼好讀、好維護嗎？
- [ ] 測試夠不夠？
- [ ] 有沒有安全上的疑慮？
- [ ] commit 歷史乾淨嗎（需要的話有 squash）？

**給作者：**

- [ ] 請人 review 之前，先自己 review 過
- [ ] CI 通過（測試、lint、typecheck）
- [ ] PR 大小合理（最好小於 500 行）
- [ ] 只跟單一功能/修正有關
- [ ] 描述有清楚說明這次的變更

## Conflict Resolution

### Identify Conflicts

```bash
# merge 之前先檢查有沒有衝突
git checkout main
git merge feature/user-auth --no-commit --no-ff

# 如果有衝突，Git 會顯示：
# CONFLICT (content): Merge conflict in src/auth/login.ts
# Automatic merge failed; fix conflicts and then commit the result.
```

### Resolve Conflicts

```bash
# 查看有衝突的檔案
git status

# 在檔案裡查看衝突標記
# <<<<<<< HEAD
# content from main
# =======
# content from feature branch
# >>>>>>> feature/user-auth

# 做法 1：手動解決
# 編輯檔案，移除標記，保留正確的內容

# 做法 2：用 merge 工具
git mergetool

# 做法 3：接受其中一邊
git checkout --ours src/auth/login.ts    # 保留 main 的版本
git checkout --theirs src/auth/login.ts  # 保留 feature 的版本

# 解決之後，stage 並 commit
git add src/auth/login.ts
git commit
```

### Conflict Prevention Strategies

```bash
# 1. 讓 feature branch 保持小而且生命週期短
# 2. 經常 rebase 到 main 上
git checkout feature/user-auth
git fetch origin
git rebase origin/main

# 3. 要動到共用檔案時，先跟團隊溝通
# 4. 用 feature flag，不要用長壽命的 branch
# 5. 及時 review 並 merge PR
```

## Branch Management

### Naming Conventions

```
# Feature branch
feature/user-authentication
feature/JIRA-123-payment-integration

# 修 bug
fix/login-redirect-loop
fix/456-null-pointer-exception

# Hotfix（production 的問題）
hotfix/critical-security-patch
hotfix/database-connection-leak

# Release
release/1.2.0
release/2024-01-hotfix

# 實驗/POC
experiment/new-caching-strategy
poc/graphql-migration
```

### Branch Cleanup

```bash
# 刪除已經 merge 的本地 branch
git branch --merged main | grep -v "^\*\|main" | xargs -n 1 git branch -d

# 刪除遠端 branch 已被刪除的 remote-tracking 參照
git fetch -p

# 刪除本地 branch
git branch -d feature/user-auth  # 安全刪除（只有已 merge 才能刪）
git branch -D feature/user-auth  # 強制刪除

# 刪除遠端 branch
git push origin --delete feature/user-auth
```

### Stash Workflow

```bash
# 儲存進行中的工作
git stash push -m "WIP: user authentication"

# 列出 stash
git stash list

# 套用最近一次的 stash
git stash pop

# 套用指定的 stash
git stash apply stash@{2}

# 丟棄 stash
git stash drop stash@{0}
```

## Release Management

### Semantic Versioning

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes
MINOR: New features, backward compatible
PATCH: Bug fixes, backward compatible

Examples:
1.0.0 → 1.0.1 (patch: bug fix)
1.0.1 → 1.1.0 (minor: new feature)
1.1.0 → 2.0.0 (major: breaking change)
```

### Creating Releases

```bash
# 建立 annotated tag
git tag -a v1.2.0 -m "Release v1.2.0

Features:
- Add user authentication
- Implement password reset

Fixes:
- Resolve login redirect issue

Breaking Changes:
- None"

# 把 tag push 到遠端
git push origin v1.2.0

# 列出 tag
git tag -l

# 刪除 tag
git tag -d v1.2.0
git push origin --delete v1.2.0
```

### Changelog Generation

```bash
# 從 commit 產生 changelog
git log v1.1.0..v1.2.0 --oneline --no-merges

# 或是用 conventional-changelog
npx conventional-changelog -i CHANGELOG.md -s
```

## Git Configuration

### Essential Configs

```bash
# 使用者身分
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 預設 branch 名稱
git config --global init.defaultBranch main

# Pull 的行為（用 rebase 而不是 merge）
git config --global pull.rebase true

# Push 的行為（只 push 目前的 branch）
git config --global push.default current

# 自動修正打錯的指令
git config --global help.autocorrect 1

# 更好的 diff 演算法
git config --global diff.algorithm histogram

# 彩色輸出
git config --global color.ui auto
```

### Useful Aliases

```bash
# 加到 ~/.gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --all
    amend = commit --amend --no-edit
    wip = commit -m "WIP"
    undo = reset --soft HEAD~1
    contributors = shortlog -sn
```

### Gitignore Patterns

```gitignore
# 依賴
node_modules/
vendor/

# Build 產出
dist/
build/
*.o
*.exe

# 環境檔
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# 作業系統檔案
.DS_Store
Thumbs.db

# Log
*.log
logs/

# 測試覆蓋率
coverage/

# 快取
.cache/
*.tsbuildinfo
```

## Common Workflows

### Starting a New Feature

```bash
# 1. 更新 main branch
git checkout main
git pull origin main

# 2. 建立 feature branch
git checkout -b feature/user-auth

# 3. 修改並 commit
git add .
git commit -m "feat(auth): implement OAuth2 login"

# 4. Push 到遠端
git push -u origin feature/user-auth

# 5. 在 GitHub/GitLab 上建立 Pull Request
```

### Updating a PR with New Changes

```bash
# 1. 做額外的修改
git add .
git commit -m "feat(auth): add error handling"

# 2. Push 更新
git push origin feature/user-auth
```

### Syncing Fork with Upstream

```bash
# 1. 加上 upstream remote（只要做一次）
git remote add upstream https://github.com/original/repo.git

# 2. Fetch upstream
git fetch upstream

# 3. 把 upstream/main merge 進你的 main
git checkout main
git merge upstream/main

# 4. Push 到你的 fork
git push origin main
```

### Undoing Mistakes

```bash
# 還原最後一個 commit（保留修改）
git reset --soft HEAD~1

# 還原最後一個 commit（捨棄修改）
git reset --hard HEAD~1

# 還原已經 push 到遠端的最後一個 commit
git revert HEAD
git push origin main

# 還原特定檔案的修改
git checkout HEAD -- path/to/file

# 修改最後一個 commit 的 message
git commit --amend -m "New message"

# 把忘記加的檔案補進最後一個 commit
git add forgotten-file
git commit --amend --no-edit
```

## Git Hooks

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 跑 linting
npm run lint || exit 1

# 跑測試
npm test || exit 1

# 檢查有沒有 secret
if git diff --cached | grep -E '(password|api_key|secret)'; then
    echo "Possible secret detected. Commit aborted."
    exit 1
fi
```

### Pre-Push Hook

```bash
#!/bin/bash
# .git/hooks/pre-push

# 跑完整的測試套件
npm run test:all || exit 1

# 檢查有沒有 console.log
if git diff origin/main | grep -E 'console\.log'; then
    echo "Remove console.log statements before pushing."
    exit 1
fi
```

## Anti-Patterns

```
# BAD：直接 commit 到 main
git checkout main
git commit -m "fix bug"

# GOOD：用 feature branch 和 PR

# BAD：commit secret
git add .env  # 裡面有 API key

# GOOD：加進 .gitignore，用環境變數

# BAD：巨大的 PR（1000 行以上）
# GOOD：拆成更小、更聚焦的 PR

# BAD：「Update」這種 commit message
git commit -m "update"
git commit -m "fix"

# GOOD：有描述性的 message
git commit -m "fix(auth): resolve redirect loop after login"

# BAD：改寫公開的歷史
git push --force origin main

# GOOD：公開的 branch 用 revert
git revert HEAD

# BAD：長壽命的 feature branch（好幾週/好幾個月）
# GOOD：讓 branch 保持短命（幾天），經常 rebase

# BAD：commit 產生出來的檔案
git add dist/
git add node_modules/

# GOOD：加進 .gitignore
```

## Quick Reference

| Task | Command |
|------|---------|
| 建立 branch | `git checkout -b feature/name` |
| 切換 branch | `git checkout branch-name` |
| 刪除 branch | `git branch -d branch-name` |
| Merge branch | `git merge branch-name` |
| Rebase branch | `git rebase main` |
| 查看歷史 | `git log --oneline --graph` |
| 查看修改 | `git diff` |
| Stage 修改 | `git add .` 或 `git add -p` |
| Commit | `git commit -m "message"` |
| Push | `git push origin branch-name` |
| Pull | `git pull origin branch-name` |
| Stash | `git stash push -m "message"` |
| 還原最後一個 commit | `git reset --soft HEAD~1` |
| Revert commit | `git revert HEAD` |
