---
name: plankton-code-quality
description: "用 Plankton 在寫入當下強制程式碼品質：透過 hook 在每次檔案編輯時自動格式化、lint，並用 Claude 驅動的修復。設定檔案編輯時的格式化、lint 或自動修復 hook 時使用。"
metadata:
  origin: community
---

# Plankton Code Quality Skill

Plankton（作者：@alxfazio）的整合參考，它是 Claude Code 的寫入當下程式碼品質強制系統。Plankton 透過 PostToolUse hook，在每次檔案編輯時跑 formatter 和 linter，然後啟動 Claude 子程序去修 agent 沒抓到的違規。

## 何時使用

- 你想要每次編輯檔案都自動格式化和 lint（不是只在 commit 時才做）
- 你需要防範 agent 去改 linter 設定來讓檢查通過，而不是去修程式碼
- 你想要分層的模型路由來做修復（簡單的風格問題用 Haiku，邏輯用 Sonnet，型別用 Opus）
- 你同時用多種語言（Python、TypeScript、Shell、YAML、JSON、TOML、Markdown、Dockerfile）

## 運作方式

### 三階段架構

每次 Claude Code 編輯或寫入檔案時，Plankton 的 `multi_linter.sh` PostToolUse hook 都會執行：

```
Phase 1: Auto-Format (Silent)
├─ Runs formatters (ruff format, biome, shfmt, taplo, markdownlint)
├─ Fixes 40-50% of issues silently
└─ No output to main agent

Phase 2: Collect Violations (JSON)
├─ Runs linters and collects unfixable violations
├─ Returns structured JSON: {line, column, code, message, linter}
└─ Still no output to main agent

Phase 3: Delegate + Verify
├─ Spawns claude -p subprocess with violations JSON
├─ Routes to model tier based on violation complexity:
│   ├─ Haiku: formatting, imports, style (E/W/F codes) — 120s timeout
│   ├─ Sonnet: complexity, refactoring (C901, PLR codes, oxlint complexity) — 300s timeout
│   └─ Opus: type system, deep reasoning (unresolved-attribute) — 600s timeout
├─ Re-runs Phase 1+2 to verify fixes
└─ Exit 0 if clean, Exit 2 if violations remain (reported to main agent)
```

### 主 agent 看得到什麼

| 情境 | Agent 看到 | Hook exit |
|----------|-----------|-----------|
| 沒有違規 | 什麼都沒有 | 0 |
| 全部被子程序修好 | 什麼都沒有 | 0 |
| 子程序跑完後仍有違規 | `[hook] N violation(s) remain` | 2 |
| 建議性訊息（重複、舊工具） | `[hook:advisory] ...` | 0 |

主 agent 只會看到子程序修不掉的問題。大部分的品質問題都是在背後悄悄解決的。

### 設定保護（防範鑽規則漏洞）

LLM 會去改 `.ruff.toml` 或 `biome.json` 把規則關掉，而不是修程式碼。Plankton 用三層擋下這種行為：

1. **PreToolUse hook**：`protect_linter_configs.sh` 在編輯發生之前，就擋下對所有 linter 設定檔的修改
2. **Stop hook**：`stop_config_guardian.sh` 在 session 結束時，用 `git diff` 偵測設定檔的變動
3. **受保護檔案清單**：`.ruff.toml`、`biome.json`、`.shellcheckrc`、`.yamllint`、`.hadolint.yaml` 等等

### 強制使用的套件管理工具

Bash 上的 PreToolUse hook 會擋下舊的套件管理工具：
- `pip`、`pip3`、`poetry`、`pipenv` → 擋下（改用 `uv`）
- `npm`、`yarn`、`pnpm` → 擋下（改用 `bun`）
- 允許的例外：`npm audit`、`npm view`、`npm publish`

## 設定

### 快速開始

> **注意：** Plankton 需要從它的 repo 手動安裝。安裝前請先檢查程式碼。

```bash
# 安裝核心依賴
brew install jaq ruff uv

# 安裝 Python linter
uv sync --all-extras

# 啟動 Claude Code，hook 會自動啟用
claude
```

沒有安裝指令，也不用設定 plugin。你在 Plankton 目錄裡執行 Claude Code 時，會自動載入 `.claude/settings.json` 裡的 hook。

### 整合到各個專案

要在你自己的專案裡使用 Plankton 的 hook：

1. 把 `.claude/hooks/` 目錄複製到你的專案
2. 複製 `.claude/settings.json` 的 hook 設定
3. 複製 linter 的設定檔（`.ruff.toml`、`biome.json` 等）
4. 安裝你用到的語言所需的 linter

### 各語言的依賴

| 語言 | 必要 | 選用 |
|----------|----------|----------|
| Python | `ruff`, `uv` | `ty` (types), `vulture` (dead code), `bandit` (security) |
| TypeScript/JS | `biome`；用 `complexity` 時需要 `oxlint` (>= 1.37.0) | `semgrep`, `knip` (dead exports) |
| Shell | `shellcheck`, `shfmt` | — |
| YAML | `yamllint` | — |
| Markdown | `markdownlint-cli2` | — |
| Dockerfile | `hadolint` (>= 2.12.0) | — |
| TOML | `taplo` | — |
| JSON | `jaq` | — |

## 搭配 ECC

### 互補，不重疊

| 關注點 | ECC | Plankton |
|---------|-----|----------|
| 程式碼品質強制 | PostToolUse hook（Prettier、tsc） | PostToolUse hook（20 幾種 linter + 子程序修復） |
| 安全掃描 | AgentShield、security-reviewer agent | Bandit (Python)、Semgrep (TypeScript) |
| 設定保護 | — | PreToolUse 擋下 + Stop hook 偵測 |
| 套件管理工具 | 偵測 + 設定 | 強制使用（擋下舊的 PM） |
| CI 整合 | — | 給 git 用的 pre-commit hook |
| 模型路由 | 手動（`/model opus`） | 自動（違規複雜度 → 層級） |

### 建議的組合

1. 安裝 ECC 當作你的 plugin（agents、skills、commands、rules）
2. 加上 Plankton 的 hook 做寫入當下的品質強制
3. 用 AgentShield 做安全稽核
4. 用 ECC 的 verification-loop 當作 PR 之前的最後一道關卡

### 避免 Hook 衝突

如果同時跑 ECC 和 Plankton 的 hook：
- ECC 的 Prettier hook 和 Plankton 的 biome formatter，在 JS/TS 檔案上可能會衝突
- 解法：用 Plankton 的時候，把 ECC 的 Prettier PostToolUse hook 關掉（Plankton 的 biome 比較完整）
- 兩者可以在不同的檔案類型上並存（ECC 處理 Plankton 沒涵蓋的部分）

## 設定參考

Plankton 的 `.claude/hooks/config.json` 控制所有行為：

```json
{
  "languages": {
    "python": true,
    "shell": true,
    "yaml": true,
    "json": true,
    "toml": true,
    "dockerfile": true,
    "markdown": true,
    "typescript": {
      "enabled": true,
      "js_runtime": "auto",
      "biome_nursery": "warn",
      "semgrep": true
    }
  },
  "phases": {
    "auto_format": true,
    "subprocess_delegation": true
  },
  "subprocess": {
    "tiers": {
      "haiku":  { "timeout": 120, "max_turns": 10 },
      "sonnet": { "timeout": 300, "max_turns": 10 },
      "opus":   { "timeout": 600, "max_turns": 15 }
    },
    "volume_threshold": 5
  }
}
```

**重要設定：**
- 把你沒用到的語言關掉，hook 會跑得比較快
- `volume_threshold`：違規數量超過這個值，就會自動升級到更高的模型層級
- `subprocess_delegation: false`：完全跳過 Phase 3（只回報違規）

## 環境變數覆寫

| 變數 | 用途 |
|----------|---------|
| `HOOK_SKIP_SUBPROCESS=1` | 跳過 Phase 3，直接回報違規 |
| `HOOK_SUBPROCESS_TIMEOUT=N` | 覆寫各層級的 timeout |
| `HOOK_DEBUG_MODEL=1` | 記錄模型選擇的決策 |
| `HOOK_SKIP_PM=1` | 繞過套件管理工具的強制規則 |

## 參考資料

- Plankton（作者：@alxfazio）
- Plankton REFERENCE.md：完整的架構文件（作者：@alxfazio）
- Plankton SETUP.md：詳細的安裝指南（作者：@alxfazio）

## ECC v1.8 新增內容

### 可直接複製的 Hook Profile

設定嚴格的品質行為：

```bash
export ECC_HOOK_PROFILE=strict
export ECC_QUALITY_GATE_FIX=true
export ECC_QUALITY_GATE_STRICT=true
```

### 語言 Gate 對照表

- TypeScript/JavaScript：優先用 Biome，Prettier 當後備
- Python：Ruff format/check
- Go：gofmt

### 設定檔竄改防護

執行品質強制時，如果在同一輪迭代裡改了設定檔，要標記出來：

- `biome.json`、`.eslintrc*`、`prettier.config*`、`tsconfig.json`、`pyproject.toml`

如果設定檔是為了壓掉違規而改的，merge 之前必須經過明確的 review。

### CI 整合模式

CI 裡用的指令要跟本機 hook 一樣：

1. 執行 formatter 檢查
2. 執行 lint/type 檢查
3. strict 模式下盡早失敗
4. 發佈修復摘要

### 健康指標

追蹤：
- 被 gate 標記的編輯次數
- 平均修復時間
- 依類別統計的重複違規
- 因為 gate 失敗而被擋下的 merge

---

## Gabe 的補充：oxlint complexity + ratchet 上限 (JS/TS)

補上上面模型路由表在 JS/TS 方面的缺口。Python 的複雜度（ruff C901、PLR）已經會路由到 Sonnet。JS/TS 卻沒有預設開啟的對應規則。

### 使用 oxlint 時，把它的 `complexity` 規則打開

oxlint 的 `complexity` 規則（來源：eslint 的 `complexity` 規則移植而來）屬於 "restriction" 類別，oxlint 預設不會啟用，必須手動打開。已對照 [Oxlint's complexity rule](https://oxc.rs/docs/guide/usage/linter/rules/eslint/complexity)（2026-08-27）驗證：預設選項是 `max: 20`。這條規則在 oxlint >= 1.37.0 才可用。

這個 skill 的「各語言的依賴」表，對 TypeScript/JS 整體而言仍把 `oxlint` 列為選用。採用 `complexity` 規則時，要用 oxlint >= 1.37.0，並把它當成必要依賴。把這條規則加進專案已經在用的、受支援的 oxlint 設定檔（`.oxlintrc.json`、`.oxlintrc.jsonc`、`oxlint.config.ts` 或 `oxlint.config.mts`）。如果都沒有，就建立一個；不要在同一個目錄裡建立第二份設定檔。

在選定初始要強制的上限之前，先量測程式碼庫目前最糟的複雜度分數。下面的樣板是刻意不完整的：在 commit `"error"` gate 之前，要把 `<MEASURED_CEILING>` 換成那個分數，必要時再加一點餘裕。Oxlint 預設的 20 是長期目標，不是適用於所有專案的安全起始上限。

```json
{
  "rules": {
    "complexity": ["error", { "max": "<MEASURED_CEILING>" }]
  }
}
```

執行 oxlint 之前要先把佔位符換掉；在 repo 量測完成之前，它不是有效的數值門檻。真實的程式碼庫要怎麼設定上限，請見下面的 ratchet 段落。

### 模型路由那一列

把 oxlint 的 `complexity` 違規，加到 Phase 3 子程序表中現有 Python 項目的同一列：

```
├─ Sonnet: complexity, refactoring (C901, PLR codes, oxlint complexity), 300s timeout
```

跟 Python 的 C901/PLR 同一層級。不管哪種語言，複雜度違規都是重構的工作，語言不會改變模型層級。

### Ratchet 上限技巧

來源：[Hunk PR #861](https://github.com/modem-dev/hunk/pull/861)（2026-08-26 merge，是透過 GitHub API 對照該 PR 自己的 diff 和描述驗證的，不是憑記憶轉述）。Hunk 在 `.oxlintrc.json` 裡用 `"error", { "max": 80 }` 打開了 oxlint 的 `complexity` 規則。當時他們自己最糟的分數是 78（`App`），其次是 76（`validateFileViewLayout`）。引用 PR 內文：「This is intentionally an initial regression ceiling rather than the long-term target... so 80 adds enforcement without grandfathering or suppressions. The ceiling can be ratcheted downward as existing hotspots are simplified.」還有：「A global ceiling does not prevent a function below 80 from growing toward it.」

這個技巧，照那個 PR 實際的做法：

1. 量測程式碼庫目前最糟的複雜度分數（規則觸發時，oxlint 會回報）。
2. 把強制執行的上限設成至少跟那個最糟分數一樣高，不要設成 oxlint 自己預設的 20。必要時加一點餘裕，這樣初次啟用時，才不會因為還沒修的分數而讓 CI 失敗（hunk 在最糟 78 的情況下用了 80）。
3. 把它以 `"error"` commit 進去，接到現有的 lint CI 步驟。從第一個 commit 起，這就是真正的 gate，不是建議。
4. 絕對不要 grandfather。上限是全域的。今天分數 40 的函式不能豁免，它之後仍然不能越過上限。這才是重點：抓的是成長，不只是今天最糟的那幾個。
5. 絕對不要整批壓掉。不准用逐檔或逐函式的 disable 註解讓違規消失。要嘛修好，要嘛讓它保持在上限以下。
6. 每次有被標記的熱點被重構到上限以下，就對整個程式碼庫重新量測全域最大值。只把上限手動降到仍然至少跟其餘每個函式分數一樣高的值（再加上任何刻意保留的餘裕）。這是手動步驟，要當成獨立的 commit 去做，不是自動化的。上限就是這樣隨著時間往 linter 真正的預設值 20 靠近，而不是永遠停在程式碼庫最糟的分數。

有一點要老實說：那個 PR 本身是在一個 commit 裡，直接從「規則關閉」跳到 `"error"` 強制執行。它沒有先經過只回報或只警告的階段。如果團隊從來沒量過自己最糟的分數，又不想要 CI 突然失敗，先把規則設成 `"warn"` 跑一輪 CI，再改成 `"error"`，是合理的分階段做法，但那個分階段的步驟是 Gabe 自己審慎的做法，並不是在 hunk 的 PR 裡驗證過的東西。如果你採用了，要講清楚，不要把它歸給原始來源。
