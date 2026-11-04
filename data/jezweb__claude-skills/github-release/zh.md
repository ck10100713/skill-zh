---
name: github-release
description: "準備並發布 GitHub release。會先把程式碼清理到適合公開發布（掃 secret、清個人檔案、檢查 LICENSE/README），建立版本 tag，再用 gh CLI 發布。用 'release'、'publish'、'open source'、'prepare for release'、'create release' 或 'github release' 觸發。"
compatibility: claude-code-only
---

# GitHub Release

把專案清理乾淨並 release 到 GitHub。分兩階段：先做安全檢查，再打 tag 發布。

## 前置條件

- 已安裝 `gh` CLI 並完成認證（`gh auth status`）
- 已安裝 `gitleaks` 用來掃 secret（`brew install gitleaks` 或從 GitHub 下載）
- Git repository 已設定 remote

## 工作流程

### 階段 1：清理

任何公開發布之前都要先跑這些檢查。遇到 blocker 就停。

#### 1. 掃描 secret（BLOCKER）

```bash
gitleaks detect --no-git --source=. --verbose
```

如果找到 secret：**停下來**。把 secret 移掉，改放環境變數。用 `git log -S "secret_value"` 檢查 git 歷史，如果歷史裡有，就用 BFG Repo-Cleaner。

如果沒裝 gitleaks，就手動檢查：

```bash
# Check for .env files
find . -name ".env*" -not -path "*/node_modules/*"

# Check config files for hardcoded secrets
grep -ri "api_key\|token\|secret\|password" wrangler.toml wrangler.jsonc .dev.vars 2>/dev/null
```

#### 2. 移除個人檔案

檢查並移除不該發布的 session/規劃檔案：

- `SESSION.md`：session 狀態
- `planning/`、`screenshots/`：工作用資料夾
- `test-*.ts`、`test-*.js`：本機測試檔

要嘛刪掉，要嘛加進 `.gitignore`。

#### 3. 驗證 LICENSE

```bash
ls LICENSE LICENSE.md LICENSE.txt 2>/dev/null
```

如果沒有：建立一個。先看 repo 的可見度（`gh repo view --json visibility -q '.visibility'`）。public repo 用 MIT。private repo 可以考慮改用專有授權。

#### 4. 驗證 README

檢查 README 存在，而且有基本的章節：

```bash
grep -i "## Install\|## Usage\|## License" README.md
```

缺章節的話，release 前先補上。

#### 5. 檢查 .gitignore

確認必要的規則都在：

```bash
grep -E "node_modules|\.env|dist/|\.dev\.vars" .gitignore
```

#### 6. Build 測試（不擋 release）

```bash
npm run build 2>&1
```

#### 7. 相依套件稽核（不擋 release）

```bash
npm audit --audit-level=high
```

#### 8. 建立清理 commit

如果清理過程有任何改動：

```bash
git add -A
git commit -m "chore: prepare for release"
```

### 階段 2：發布

#### 1. 決定版本

看 `package.json` 目前的版本，或問使用者。確保版本號以 `v` 開頭。

#### 2. 確認 tag 不存在

```bash
git tag -l "v[version]"
```

如果已存在，問使用者要刪掉重建還是換一個版本。

#### 3. 顯示這次要發布的內容

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$LAST_TAG" ]; then
  git log --oneline --no-merges HEAD | head -20
else
  git log --oneline --no-merges ${LAST_TAG}..HEAD
fi
```

#### 4. 建立 tag 並 push

```bash
git tag -a v[version] -m "Release v[version]"
git push origin $(git branch --show-current)
git push origin --tags
```

#### 5. 建立 GitHub Release

```bash
gh release create v[version] \
  --title "Release v[version]" \
  --notes "[auto-generated from commits]"
```

預先發布版加 `--prerelease`，草稿加 `--draft`。

#### 6. 回報

給使用者看：
- Release 網址
- 後續步驟（有的話，像是 npm publish、對外公告）

## 參考檔案

| 什麼時候 | 讀什麼 |
|------|------|
| 詳細的安全檢查 | [references/safety-checklist.md](references/safety-checklist.md) |
| Release 的實際流程 | [references/release-workflow.md](references/release-workflow.md) |
