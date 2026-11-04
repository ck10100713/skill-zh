---
name: continuous-learning
description: "[已棄用，請改用 continuous-learning-v2] 舊版 v1 的 stop-hook skill 擷取器。v2 是嚴格的超集，採用以 instinct 為基礎、以專案為範圍、hook 可靠的學習。不要呼叫 v1：要求持續學習、session 學習或模式擷取時，請改導向 continuous-learning-v2。"
metadata:
  origin: ECC
---

# Continuous Learning Skill - DEPRECATED

> **已於 2026-04-28 棄用。** 請改用 `continuous-learning-v2`。v2 是嚴格的超集：stop-hook 觀察變成 PreToolUse/PostToolUse 觀察、完整的 skill 變成帶信心分數的原子 instinct，以及只有全域的儲存變成以專案為範圍，再加上全域升級。
>
> 保留這個檔案是為了存檔參考，以及相容既有的安裝。

---

## Original v1 Documentation (archival)

在 Claude Code session 結束時自動評估，擷取可重複使用、能存成學習到的 skill 的模式。

## When to Activate

- 設定從 Claude Code session 自動擷取模式
- 設定用於 session 評估的 Stop hook
- 審查或整理 `~/.claude/skills/learned/` 裡學習到的 skill
- 調整擷取門檻或模式類別
- 比較 v1（這個）和 v2（以 instinct 為基礎）的做法

## Status

這個 v1 skill 仍然支援，但新安裝建議走 `continuous-learning-v2`。只有在你明確想要較簡單的 Stop-hook 擷取流程，或需要相容較舊的學習 skill 工作流程時，才保留 v1。

## How It Works

這個 skill 在每個 session 結束時，以 **Stop hook** 的形式執行：

1. **Session 評估**：檢查 session 的訊息數量是否足夠（預設：10 則以上）
2. **模式偵測**：從 session 中找出可擷取的模式
3. **Skill 擷取**：把有用的模式存到 `~/.claude/skills/learned/`

## Configuration

編輯 `config.json` 來自訂：

```json
{
  "min_session_length": 10,
  "extraction_threshold": "medium",
  "auto_approve": false,
  "learned_skills_path": "~/.claude/skills/learned/",
  "patterns_to_detect": [
    "error_resolution",
    "user_corrections",
    "workarounds",
    "debugging_techniques",
    "project_specific"
  ],
  "ignore_patterns": [
    "simple_typos",
    "one_time_fixes",
    "external_api_issues"
  ]
}
```

## Pattern Types

| Pattern | Description |
|---------|-------------|
| `error_resolution` | 特定錯誤是怎麼解決的 |
| `user_corrections` | 來自使用者更正的模式 |
| `workarounds` | framework/函式庫怪癖的解法 |
| `debugging_techniques` | 有效的除錯方法 |
| `project_specific` | 專案專屬的慣例 |

## Hook Setup

加到你的 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "Stop": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning/evaluate-session.sh"
      }]
    }]
  }
}
```

## Why Stop Hook?

- **輕量**：只在 session 結束時執行一次
- **不阻塞**：不會替每則訊息增加延遲
- **完整的 context**：可以存取整份 session 逐字稿

## Related

- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352)：關於持續學習的章節
- `/learn` 指令：在 session 中途手動擷取模式

---

## Comparison Notes (Research: Jan 2025)

### vs Homunculus

Homunculus v2 採用更精密的做法：

| Feature | Our Approach | Homunculus v2 |
|---------|--------------|---------------|
| Observation | Stop hook (end of session) | PreToolUse/PostToolUse hooks (100% reliable) |
| Analysis | Main context | Background agent (Haiku) |
| Granularity | Full skills | Atomic "instincts" |
| Confidence | None | 0.3-0.9 weighted |
| Evolution | Direct to skill | Instincts → cluster → skill/command/agent |
| Sharing | None | Export/import instincts |

**來自 homunculus 的關鍵洞見：**
> "v1 relied on skills to observe. Skills are probabilistic—they fire ~50-80% of the time. v2 uses hooks for observation (100% reliable) and instincts as the atomic unit of learned behavior."

### Potential v2 Enhancements

1. **以 instinct 為基礎的學習**：更小、原子化的行為，帶信心分數
2. **背景觀察者**：Haiku agent 平行分析
3. **信心衰減**：instinct 被反駁時會失去信心
4. **領域標記**：code-style、testing、git、debugging 等等
5. **演化路徑**：把相關的 instinct 聚合成 skill/指令

完整規格請見：`docs/continuous-learning-v2-spec.md`。
