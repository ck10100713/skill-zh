---
name: security-scan
description: 用 AgentShield 掃描你的 Claude Code 設定（.claude/ 目錄），找出安全漏洞、錯誤設定和注入風險。檢查 CLAUDE.md、settings.json、MCP server、hook 和 agent 定義。稽核 .claude/ 目錄（CLAUDE.md、settings.json、MCP server、hook 或 agent 定義）時使用。
metadata:
  origin: ECC
---

# 安全掃描 Skill

用 [AgentShield](https://github.com/affaan-m/agentshield) 稽核你的 Claude Code 設定有沒有安全問題。

## 何時啟用

- 設定新的 Claude Code 專案時
- 修改 `.claude/settings.json`、`CLAUDE.md` 或 MCP 設定之後
- Commit 設定變更之前
- 接手一個已有 Claude Code 設定的新 repository 時
- 定期的安全衛生檢查

## 掃描內容

| 檔案 | 檢查項目 |
|------|--------|
| `CLAUDE.md` | 寫死的 secret、自動執行的指示、prompt injection 模式 |
| `settings.json` | 過度寬鬆的 allow 清單、缺少 deny 清單、危險的繞過旗標 |
| `mcp.json` | 有風險的 MCP server、寫死在 env 的 secret、npx 供應鏈風險 |
| `hooks/` | 透過字串插值造成的指令注入、資料外洩、靜默吞掉錯誤 |
| `agents/*.md` | 不受限制的工具存取、prompt injection 攻擊面、缺少 model 規格 |

## 先決條件

必須先安裝 AgentShield。先檢查，需要的話就安裝：

```bash
# Check if installed
npx ecc-agentshield --version

# Install globally (recommended)
npm install -g ecc-agentshield

# Or run directly via npx (no install needed)
npx ecc-agentshield scan .
```

## 使用方式

### 基本掃描

對目前專案的 `.claude/` 目錄執行：

```bash
# Scan current project
npx ecc-agentshield scan

# Scan a specific path
npx ecc-agentshield scan --path /path/to/.claude

# Scan with minimum severity filter
npx ecc-agentshield scan --min-severity medium
```

### 輸出格式

```bash
# Terminal output (default) — colored report with grade
npx ecc-agentshield scan

# JSON — for CI/CD integration
npx ecc-agentshield scan --format json

# Markdown — for documentation
npx ecc-agentshield scan --format markdown

# HTML — self-contained dark-theme report
npx ecc-agentshield scan --format html > security-report.html
```

### 自動修正

自動套用安全的修正（只修標記為可自動修正的項目）：

```bash
npx ecc-agentshield scan --fix
```

這會：
- 把寫死的 secret 換成環境變數參照
- 把萬用字元權限收緊成有範圍的替代做法
- 絕對不會動只能手動處理的建議

### Opus 4.6 深度分析

執行對抗式的三 agent pipeline，做更深入的分析：

```bash
# Requires ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY=your-key
npx ecc-agentshield scan --opus --stream
```

這會執行：
1. **Attacker（紅隊）**：找出攻擊向量
2. **Defender（藍隊）**：建議強化方式
3. **Auditor（最終判定）**：綜合兩方的觀點

### 初始化安全設定

從零開始建立一份安全的 `.claude/` 設定骨架：

```bash
npx ecc-agentshield init
```

會建立：
- 帶有範圍限定權限和 deny 清單的 `settings.json`
- 含安全最佳實務的 `CLAUDE.md`
- `mcp.json` 預留位置

### GitHub Action

加到你的 CI pipeline：

```yaml
- uses: affaan-m/agentshield@v1
  with:
    path: '.'
    min-severity: 'medium'
    fail-on-findings: true
```

## 嚴重程度等級

| 等級 | 分數 | 意義 |
|-------|-------|---------|
| A | 90-100 | 設定安全 |
| B | 75-89 | 有小問題 |
| C | 60-74 | 需要注意 |
| D | 40-59 | 有重大風險 |
| F | 0-39 | 有嚴重漏洞 |

## 解讀結果

### Critical 發現（立刻修）
- 設定檔裡寫死的 API key 或 token
- allow 清單裡有 `Bash(*)`（不受限的 shell 存取）
- hook 裡透過 `${file}` 插值造成的指令注入
- 會執行 shell 的 MCP server

### High 發現（上正式環境前修）
- CLAUDE.md 裡有自動執行的指示（prompt injection 管道）
- 權限裡缺少 deny 清單
- 有不必要 Bash 存取權的 agent

### Medium 發現（建議處理）
- hook 裡靜默吞掉錯誤（`2>/dev/null`、`|| true`）
- 缺少 PreToolUse 安全 hook
- MCP server 設定裡的 `npx -y` 自動安裝

### Info 發現（提醒用）
- MCP server 缺少描述
- 禁止性的指示被正確標記為良好實務

## 連結

- **GitHub**：[github.com/affaan-m/agentshield](https://github.com/affaan-m/agentshield)
- **npm**：[npmjs.com/package/ecc-agentshield](https://www.npmjs.com/package/ecc-agentshield)
