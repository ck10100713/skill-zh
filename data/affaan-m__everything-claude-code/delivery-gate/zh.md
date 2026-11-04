---
name: delivery-gate
description: 一個 Stop hook，在品質檢查通過之前，擋住 Claude 結束工作。會偵測合理化的說法（表面文字的啟發式判斷）、過期的學習紀錄（檔案系統 mtime）和磁碟空間不足。透過機械式地強制執行學習記錄的習慣，來補足 self-audit。當要在品質檢查和學習記錄真的通過之前，機械式地擋住 Claude 宣稱工作完成時使用。
metadata:
  version: 1.1.1
  origin: ECC
---

# Delivery Gate：給 Claude Code 的機械式品質關卡

一個 **Stop hook**，在 Claude 結束 session 之前檢查三件事，只用**確定性的檢查**：檔案修改時間戳、磁碟用量，以及對 transcript 文字做的 regex 比對。沒有 AI 推論。

這跟推理型的關卡（像 `self-audit`）不同：delivery-gate 檢查機器可以驗證的事實；self-audit 則是從四個推理面向檢查輸出品質。兩者合起來就是縱深防禦：
- **delivery-gate**：「今天有動過學習資料庫嗎？磁碟空間安全嗎？」
- **self-audit**：「檔案內容正確、完整而且誠實嗎？」

這跟 CI pipeline 關卡是同一種模式：自動、確定性的檢查，驗證機器可讀的事實，而不是相信自己回報的狀態。

## 它檢查什麼

| 檢查 | 機制 | 命中時 |
|-------|-----------|--------|
| 合理化的說法 | 對 transcript 尾端做 regex | **只警告**（絕不阻擋） |
| 過期的學習資料庫 | 5 個可設定路徑的 mtime | 部分過期就警告；在複雜任務中，>=3 個過期，或 growth-log 過期，就**阻擋** |
| 磁碟空間 < 50GB | `shutil.disk_usage` | 提醒 |
| 磁碟空間 < 30GB | `shutil.disk_usage` | 警告 |
| 磁碟空間 < 15GB | `shutil.disk_usage` | **阻擋**（exit 2），每次 Stop 都阻擋 |

合理化偵測會對「skip tests for now」和「pre-existing bug」這類說法發出警告，它們是思考可能被草草打住的表面訊號。它自己絕不會阻擋，因為 regex 的啟發式判斷可能誤報。會阻擋的條件是：磁碟到了危急程度（任何 session），或者在複雜任務（>=3 次 Edit/Write 呼叫）中，`>=3 個學習資料庫過期`，或 `growth-log` 特別過期。如果專案的記憶目錄不存在，就跳過學習資料庫的檢查：hook 只會警告它無法驗證學習記錄，複雜任務不會被阻擋（磁碟檢查仍然適用）。

hook 對同一次 Stop 最多只阻擋一次。當 Claude Code 帶著 `stop_hook_active: true` 重新執行它（Claude 已經因為這個 hook 繼續過一次），它就 exit 0，所以 agent 修不好的狀況（例如磁碟空間不足）不會把 session 困在無窮迴圈裡。

## 為什麼

Claude Code 內建的檢查涵蓋程式碼品質（build → type → lint → test）。但還有一種不同的失敗模式：agent 產出了可以運作的程式碼，但 **session 的衛生被忽略了**：沒有記錄學習、有被合理化的捷徑、磁碟默默被用光。

在很多次「出貨就忘」的 session 之後，人並沒有成長。這個 hook 強制執行這個習慣：複雜任務 → 必須動到學習資料庫。

## 安裝

從 ECC repository 的根目錄：

```bash
mkdir -p ~/.claude/scripts
cp skills/delivery-gate/hooks/quality-gate.py ~/.claude/scripts/
```

加到 `~/.claude/settings.json`：
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/scripts/quality-gate.py",
        "timeout": 5
      }]
    }]
  }
}
```

## 學習資料庫

在你專案的記憶目錄（`~/.claude/projects/<encoded-project-path>/memory/`，專案路徑中每個非英數字元都會變成 `-`）裡建立這些檔案。hook 會檢查其中哪些在今天更新過：

```
memory/
├── growth-log/          # Daily learning entries (directory)
├── decisions/log.md     # Decision log
├── output-index.md      # Index of session outputs
├── ratings-tracker.md   # Skill ratings over time
└── tooling_capabilities.md  # Known tools inventory
```

自訂 `LIBS` dict 來符合你自己的檔案結構。

## 設定

編輯 `quality-gate.py`：

| 變數 | 預設值 | 用途 |
|----------|---------|---------|
| `RATIONALIZE` | 4 個模式 | 偵測合理化說法的 regex 模式 |
| `LIBS` | 5 個資料庫 | 要檢查今天是否有更新的檔案/目錄 |
| `COMPLEX_THRESHOLD` | 3 | 判定為複雜任務所需的 Edit/Write 呼叫次數 |
| `DISK_REMIND_GB` | 50 | 低於這個值就提醒 |
| `DISK_WARN_GB` | 30 | 低於這個值就警告 |
| `DISK_CRIT_GB` | 15 | 低於這個值就阻擋 |

## 範例

**簡單的 session，允許：**
```
edit_count=1 (< 3, not complex) → exit 0
```

**複雜任務，有記錄學習，允許：**
```
edit_count=5 (complex) → checks LIBS → growth-log + 2 others updated today (2 stale) → exit 0
```

**複雜任務，沒有學習，阻擋：**
```
edit_count=4 (complex) → checks LIBS → all 5 stale → exit 2
stderr: "Blocked: complex task but >=3 learning libs stale."
```

**磁碟空間不足，阻擋：**
```
disk_free=12GB < 15GB critical → exit 2
stderr: "Blocked: disk space at 12GB (<15GB). Free space before continuing."
```

## 限制

這個 hook 強制執行的是動到學習資料庫的**習慣**，不是所記錄內容的**品質**。在複雜任務中，只有 `growth-log` 今天有更新，而且過期的資料庫最多 2 個，才會通過；光更新 `output-index.md` 仍然會被阻擋。沒有專案記憶目錄的話就沒東西可以檢查，所以只會警告。這是刻意的設計：機械式的關卡檢查的是機器可以驗證的事實。要驗證內容品質，要搭配 `self-audit`。

## 相容性

- Python 3.8+（使用 `from __future__ import annotations`）
- 跨平台：Windows、macOS、Linux
- 除了標準函式庫之外沒有任何相依套件

## 品質

這份程式碼經過 4 輪自動化 code review（CodeRabbit + Greptile），找出並修好了 9 個真正的 bug。

## 另見

- `self-audit`：推理品質關卡（完整性/一致性/有根據/誠實）
- `verification-loop`：程式碼品質檢查（build/type/lint/test）
- `gateguard`：PreToolUse 的安全關卡
