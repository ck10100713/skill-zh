---
name: codehealth-mcp
description: 透過 CodeScene MCP 取得即時的結構性 Code Health：編輯前先審查、修改後驗證分數變化，並在 commit 和 PR 時把關。適用於審查程式碼品質、重構、檢查 AI 的改動有沒有讓某個檔案變差，或 commit/PR 之前。
metadata:
  origin: community
---

# Code Health MCP (CodeScene)

給 AI 輔助寫程式用的結構性可維護性回饋。它補足風格/lint 類的 skill（`coding-standards`、`plankton-code-quality`），提供**設計層級**的健康分數和退化關卡。

**Upstream:** [codescene-oss/codescene-mcp-server](https://github.com/codescene-oss/codescene-mcp-server)
**Package:** `@codescene/codehealth-mcp`（透過 npx 走 stdio）

## Security and boundaries

**Opt-in (ECC)：** `mcp-configs/mcp-servers.json` 裡的 `codescene` 區塊只是範本。ECC plugin 安裝時不會自動啟用內附的 MCP 伺服器。你想用的話，才把這個項目複製到自己的設定。安裝/同步 ECC 時，可以用 `ECC_DISABLED_MCPS=codescene,...` 排除它。

**Credentials：** 沒有內附 token。請自己設定 `CS_ACCESS_TOKEN`（見 upstream repo 裡的 [getting-a-personal-access-token.md](https://github.com/codescene-oss/codescene-mcp-server/blob/main/docs/getting-a-personal-access-token.md)）。絕對不要把 token commit 進 repo。

**工具會讀什麼：** 被呼叫時，工具會分析你指定的**本地 repository** 裡的檔案和 git 狀態（你傳入的路徑，加上 `analyze_change_set` 用的 branch context）。它們不會自己執行。standalone 模式請參考 upstream 的隱私文件：[codescene-mcp-server README](https://github.com/codescene-oss/codescene-mcp-server#frequently-asked-questions) 和 [CodeScene policies](https://codescene.com/policies)。不要把這個 skill 用在機密、憑證，或是你不想被分析的路徑上。

**如果 MCP 無法使用（離線、token 錯誤、伺服器當掉）：** 不要編造 Code Health 分數。告訴使用者這項檢查被跳過了。要有使用者明確同意才能繼續。MCP 停擺時，優先用 lint/測試/verification-loop 來把關。伺服器連上之後，再重新啟用檢查。

## When to Use

- 使用者要求**審查程式碼品質**、**重構**某個檔案，或檢查 **AI 的改動有沒有讓**可維護性**變差**
- 編輯**熱點**（hotspot）、舊模組或不熟悉的檔案之前
- **commit** 或 **pull request** 之前，需要可維護性的防護網時
- agent 寫了很大的 diff 之後，驗證 Code Health 沒有退化
- 搭配 `verification-loop`、`tdd-workflow` 或 `/quality-gate` 當作結構性檢查（不能取代測試/lint）

## When to Activate

觸發條件跟上面的 **When to Use** 一樣，這個標題是 ECC 用來自動啟用 skill 的。

## How It Works

### 1. Connect the MCP server

把 `mcp-configs/mcp-servers.json` 裡的 `codescene` 項目複製到你的 harness MCP 設定。

**Claude Code**（`~/.claude.json` → `mcpServers`）：

```json
"codescene": {
  "command": "npx",
  "args": ["-y", "@codescene/codehealth-mcp"],
  "env": {
    "CS_ACCESS_TOKEN": "YOUR_CS_ACCESS_TOKEN_HERE"
  }
}
```

**專案範圍：** 把同樣的區塊合併進 repo 根目錄的 `.mcp.json`。

Token 設定寫在 upstream repo 的文件裡（上面的連結）。standalone 模式用下面列出的四個工具，不需要付費的 CodeScene 平台帳號。重啟 session，確認 `codescene` 伺服器已連上，再去依賴分數。

### 2. Call standalone tools only

| Tool | When to use |
|------|-------------|
| `code_health_review` | 修改檔案**之前**做完整的結構分析 |
| `code_health_score` | 每次修改後快速取得數字分數（檢查變化量） |
| `pre_commit_code_health_safeguard` | 擋下會造成 Code Health 退化的 commit |
| `analyze_change_set` | 開 PR **之前**做 branch 層級的檢查 |

**不要**呼叫只有平台版才有的工具（例如整個 repository 的技術債熱點清單）。**不要**引用 `delta_analysis`，standalone 沒有這個。

### 3. Interpret scores (1–10)

| Range | Meaning | Agent behavior |
|-------|---------|----------------|
| **9.0–10.0** | 綠色，健康 | 比較安全可以擴充；仍然優先用垂直切片 |
| **4.0–8.9** | 黃色，有技術債 | 小心行事；不要順手重構 |
| **1.0–3.9** | 紅色，嚴重技術債 | 只能縮小範圍 |

### 4. Run the feedback loop

**動檔案之前**

1. 對目標路徑執行 `code_health_review`。
2. 記下基準分數和列出的 code smell。
3. 規劃能完成任務的最小改動。

依分數決定範圍：**低於 5**：只能做最小的 diff；**5–7**：不要大範圍重構；**高於 7**：比較安全可以重構，每次編輯之後仍要驗證。

**每次修改之後**

1. 對同一個檔案執行 `code_health_score`。
2. 跟 `code_health_review` 得到的基準比較。
3. 如果分數**退步**，先修好再繼續。分數比你開始時還低，就絕對不要標記任務完成。

**每次 commit 之前**：對 repository 路徑執行 `pre_commit_code_health_safeguard`。

**PR 之前**：對 base branch（例如 `main`）執行 `analyze_change_set`。

## Examples

### Example: Flask maintainability improvement

在 `pallets/flask` 上，一個只用 standalone 工具的 agent 迴圈：

1. 對目標模組執行 `code_health_review`（基準 **4.82**）
2. 針對列出的 smell 做有針對性的重構
3. 每次編輯後執行 `code_health_score`
4. commit 前執行 `pre_commit_code_health_safeguard`
5. PR 前執行 `analyze_change_set`

結果：Code Health **4.82 → 9.1**（只用免費的 standalone token）。

### Example: AGENTS.md enforcement block

貼到專案的 `AGENTS.md` 或 `CLAUDE.md`：

```md
## Code Health (CodeScene MCP)

Before modifying any file: run `code_health_review`, note score and issues.

- Score below 5: problematic range — scope changes narrowly.
- Score 5–7: warning range — no broad refactors.

After each change: run `code_health_score` to verify delta.

- If score regressed: fix before continuing; never declare done if score dropped.

Before every commit: run `pre_commit_code_health_safeguard`.

Before PR: run `analyze_change_set`.
```

### Example: anti-patterns vs correct loop

```markdown
# BAD: Edit first, check later
[large refactor without code_health_review]

# BAD: Ignore score drop
"Tests pass" → mark task done while Code Health decreased

# BAD: Broad refactor on red-score file (below 5)
Drive-by cleanup across the module

# GOOD: review → small change → score → commit safeguard → analyze_change_set
```

## Pairing with ECC

| ECC skill / flow | Code Health MCP role |
|------------------|----------------------|
| `coding-standards` | 風格/命名；Code Health 看結構/複雜度 |
| `plankton-code-quality` | 寫程式當下的 lint/format；Code Health 是編輯前後的結構關卡 |
| `verification-loop` / `/quality-gate` | 在「完成」之前，加上結構退化檢查 |
| `security-review` | 安全性 vs 可維護性，相關時兩個都用 |
| `tdd-workflow` | 測試通過 ≠ 設計健康，重構後要檢查分數 |

**Context 小提醒：** ECC 建議把 MCP 的數量控制在少數。做實質編輯時啟用 `codescene`，不需要時就停用。

## Related Skills

- `coding-standards`：基礎慣例
- `plankton-code-quality`：寫程式當下的 lint/format hook
- `verification-loop`：build/測試/lint 關卡
- `tdd-workflow`：測試先行的開發
- `security-review`：安全檢查清單
- `documentation-lookup`：透過 Context7 查函式庫文件（互不相干）
