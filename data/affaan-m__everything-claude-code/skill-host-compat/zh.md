---
name: skill-host-compat
description: 在送出 skill PR 之前，檢查 ECC skill 的 frontmatter 是否適用 Codex/Cursor，以及有沒有 Claude 專屬的變數替換。
origin: ECC
---

# Skill 主機相容性

開 skill PR 之前，先對 `skills/` 跑一次 CI 用的同一套主機相容性檢查。這個檢查針對的是 Codex 和 Cursor 的副本，不是 Claude 專屬的執行品質。

## 何時啟用

- 在 `skills/` 底下新增或編輯 skill
- 把 skill 複製到 `.agents/skills/` 或 `.cursor/skills/`
- Review 時有人問某個 skill 能不能安全地安裝到 Codex 或 Cursor
- CI 回報 `validate-skill-host-compat.js` 的發現

## 核心概念

標準版 skill 放在 `skills/`。Codex 載入 `.agents/skills/`。Cursor 載入較小的 `.cursor/skills/` 子集。CONTRIBUTING 記載這個同步是手動的。

`validate-skills.js` 只檢查 `SKILL.md` 存在，以及 `name` / `description` 是可用的 YAML。`tests/ci/codex-skill-surface.test.js` 只看得到 `.agents/skills/`。這支 script 是跨目錄樹的關卡：

1. Codex/Cursor 副本裡，可執行的 `bash` / `sh` / `zsh` 程式碼區塊出現 Claude 專屬的替換變數（`${CLAUDE_SESSION_ID}`、`${CLAUDE_SKILL_DIR}`、`${CLAUDE_PLUGIN_ROOT}`、`${CLAUDE_PROJECT_DIR}`、`$ARGUMENTS`）會失敗。Codex 會把這些 token 當成字面文字留著。在 Codex 副本裡，要把 `${CLAUDE_PROJECT_DIR}` 改寫成 `$(pwd)` 或明確的路徑。
2. Codex 副本只能使用 `name`、`description`、`metadata`、`license` 和 `allowed-tools`。`origin: ECC` 可以留在標準版 `skills/` 副本上，但 Codex 副本上必須移除。
3. 列在 `agents/openai.yaml` 裡、而且在 `skills/` 有對應目錄的 skill，必須有 `.agents/skills/<name>/`。Cursor 副本是選用的；有的話，`name:` 必須跟目錄名稱一致。
4. CONTRIBUTING 檢查清單項目（When to Activate、Anti-Patterns、name 跟目錄一致、500/800 行上限）只會警告。只有加 `--strict-checklist` 才會失敗。

`validate-skills.js` 的 frontmatter WARN 預設維持不變（#1663）。

## 程式碼範例

從 repo 根目錄：

```bash
node scripts/ci/validate-skill-host-compat.js
```

只印出數量，不失敗：

```bash
node scripts/ci/validate-skill-host-compat.js --inventory
```

把檢查清單的警告升級成失敗：

```bash
node scripts/ci/validate-skill-host-compat.js --strict-checklist
```

Slash command：

```
/skill-host-compat
/skill-host-compat --inventory
```

## 反模式

Codex 和 Cursor 的副本，必須把可執行區塊裡 Claude 專屬的替換變數解析掉。標準版中限定 Claude 範圍的範例仍然有效。POSIX 的 `$1` 和 `${1}` 參數有歧義，需要人工檢視，不會讓這道關卡失敗。這個程式碼區塊就是被禁止的寫法：

```bash
echo "${CLAUDE_SESSION_ID}"
ls "${CLAUDE_SKILL_DIR}"
node "${CLAUDE_PLUGIN_ROOT}/scripts/setup.js" $ARGUMENTS
cd "${CLAUDE_PROJECT_DIR}"
```

不要在 `.agents/skills/` 底下的 Codex 副本加 `version:` 或 `origin:`。不要把 `validate-skills.js` 通過當成 Codex 安全。不要要求 `skills/` 的每個項目都要有 Cursor 副本。

## 最佳實務

- CONTRIBUTING 範本要求的話，標準版就保留 `origin: ECC`。
- Codex 副本要拿掉 `origin`、`version` 和 `argument-hint`。
- bash 區塊裡放可跨主機的指令（`npx`、`ecc` 或已解析的根目錄）。Codex 副本裡的 `${CLAUDE_PROJECT_DIR}` 要改寫成 `$(pwd)` 或明確的路徑。標準版的說明裡保留有效的 Claude 範圍寫法；在目標副本裡才解析主機變數。
- 變更是新增 skill 時，先跑這支 script，再跑 `npm test`。
- 用 `--inventory` 看檢查清單警告的量，又不會讓整個目錄樹失敗。

## 相關 Skill

- `skill-comply`：執行期的行為軌跡，不是主機可攜性
- `skill-stocktake`：對已安裝的 `~/.claude/skills` 做整體稽核
- `skill-scout`：建立新 skill 之前，先搜尋現有的 skill
