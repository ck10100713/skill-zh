---
name: ponytail-help
description: >
  ponytail 等級、skill 和指令的快速參考。一次性顯示。
  用於 /ponytail-help、「ponytail help」、「how do I use ponytail」。
---

# Ponytail Help

被呼叫時，顯示這張參考卡。一次性，**不要**改模式、
寫旗標檔案，或保存任何東西。

## 等級

| 等級 | 觸發 | 有什麼改變 |
|-------|---------|-------------|
| **Lite** | `/ponytail lite` | 做使用者要求的，用一行說明比較小的選項。 |
| **Full** | `/ponytail` | 最小但完整的改動、邏輯需要時附上檢查，以及一份說明跳過了什麼和有什麼風險的回覆。預設值。 |
| **Ultra** | `/ponytail ultra` | 另外還會質疑需求，在動手做之前先提出反駁。 |

等級會一直維持，直到被改掉或 session 結束。

## Skills

| Skill | 觸發 | 功能 |
|-------|---------|--------------|
| **ponytail** | `/ponytail` | 偷懶模式本身：用最少的新程式碼，回覆清楚地說明跳過的工作和風險。 |
| **ponytail-review** | `/ponytail-review` | 對 diff 做品質審查：bug、安全、負載、缺少的測試、速度、該砍什麼。每個發現都說明會出什麼問題、怎麼修。 |
| **ponytail-audit** | `/ponytail-audit` | 對整個 repo 做同樣的品質審查，並排序。 |
| **ponytail-debt** | `/ponytail-debt` | 把 `shortcut:` 註解收集成有追蹤的帳本。 |
| **ponytail-gain** | `/ponytail-gain` | 量測影響的計分板：更少程式碼、更低成本、更快速度。 |
| **ponytail-help** | `/ponytail-help` | 就是這張卡片。 |

在 Codex CLI 和 IDE 擴充套件裡，用 `$ponytail:ponytail`、
`$ponytail:ponytail-review` 或 `$ponytail:ponytail-help` 來呼叫 skill。Claude Code 和 OpenCode 用
上面的斜線指令形式（OpenCode 六個都以斜線指令提供）。

## 停用

說「stop ponytail」或「normal mode」。隨時可以用 `/ponytail` 恢復。
`/ponytail off` 也行。

## Band（Claude Code）

`/ponytail band` 會隱藏 prompt 上方的 band，同一個指令再下一次就會讓它回來。
`/ponytail band on` 和 `/ponytail band off` 則是直接設定。等級不會變。
`/ponytail band import` 會把你過去的 Claude Code session（成本、agent 時間、token）加進計分板。

## 設定預設模式

預設模式 = `full`，每個 session 都自動啟用。要改它：

**環境變數**（優先順序最高）：
```bash
export PONYTAIL_DEFAULT_MODE=ultra
```

**設定檔**（`~/.config/ponytail/config.json`，Windows：`%APPDATA%\ponytail\config.json`）：
```json
{ "defaultMode": "lite" }
```

設成 `"off"` 可以關閉 session 開始時的自動啟用，需要時再
用 `/ponytail` 手動啟用。

解析順序：環境變數 > 設定檔 > `full`。

## 更新

只要啟用一次自動更新：打開 `/plugin`，進入 Marketplaces，選 ponytail，Enable auto-update。之後 Claude Code 會在啟動時拉新版本（它提示時，執行 `/reload-plugins`）。手動更新：`/plugin marketplace update ponytail`，然後 `/reload-plugins`。

如果 `/plugin` 無法辨識，代表你的 Claude Code 太舊了。更新它（`npm install -g @anthropic-ai/claude-code@latest`，或 `brew upgrade claude-code`），然後重新啟動。其他的 host 有各自的更新流程。

## 更多

完整文件 + 範例：https://github.com/DietrichGebert/ponytail
