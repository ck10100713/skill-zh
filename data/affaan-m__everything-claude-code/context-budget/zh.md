---
name: context-budget
description: 把即時的 context 檢查導向 Codex 或 Claude Code 原生的計量器，不掃描檔案；只有在被明確要求時，才執行有界限的靜態元件稽核。適用於詢問剩餘容量或已安裝的 context 開銷的 context-budget 需求。
metadata:
  origin: ECC
---

# Context Budget

即時的 session 用量，用供應商原生的計量器。把另外一套、
估算性質的安裝稽核，放在明確 opt-in 之後才做。

## Default: Live Context

沒有要求稽核的呼叫，一律當成即時 context 的請求。
包括詢問目前的視窗、剩餘容量、餘裕、token
用量，或 context 明細。

這條預設路徑：

- 不要呼叫或使用工具。
- 不要掃描或讀取檔案。
- 不要執行 shell 指令、供應商 CLI、除錯記錄或 MCP 探索。
- 只回覆原生指令，加上一句簡短的說明。

依目前啟用的 harness 導向：

| Harness | Native command | Guidance |
| --- | --- | --- |
| Codex CLI | `/status` | 顯示目前的 token 用量和剩餘的 context 容量。用 `/statusline` 並啟用 **Context stats** 加 **Token counters**，就能在頁尾常駐顯示計量器。 |
| Codex app | `/status` | 顯示目前對話串的 context 用量和速率限制。 |
| Claude Code | `/context` | 顯示即時的 context 明細。用 `/context all` 看展開的項目。 |
| Other or unknown | None verified | 說明 ECC 無法讀取供應商的即時狀態，並問目前用的是哪個 harness。 |

這些指令記載在 [Codex 指令參考](https://developers.openai.com/codex/cli/slash-commands)和 [Claude Code 指令參考](https://code.claude.com/docs/en/commands)。

Skill 無法代替使用者呼叫 TUI 的斜線指令。絕對不要用估算的掃描
取代原生指令，也絕對不要從「context 很重」或「還剩多少」
這類說法去推斷使用者要求稽核。

## Explicit Static Audit

只有在使用者明確說出
`--audit`、「audit installed components」，或同樣明確無歧義的措辭時，才執行安裝/設定稽核。
`--verbose` 只會改變報告的細節程度，它本身不代表 opt-in 稽核。

如果稽核範圍不明確，在讀取任何東西之前，先問 harness
和安裝根目錄。每次稽核都要有界限而且唯讀：

1. 只檢查指名的 plugin/安裝根目錄，以及指名的 harness 已知的
   設定檔。
2. 絕對不要遞迴列舉 workspace 根目錄、家目錄、供應商
   快取、對話記錄、除錯記錄或不相關的 worktree。
3. 絕對不要為了計算工具數量而啟動供應商 CLI、MCP 伺服器或除錯 session。
4. 每個元件類別的清單輸出上限是 50 個項目。其餘的用摘要帶過。
5. 不要寫暫存記錄，也不要把設定內容複製進報告。

只稽核跟 eager discovery（預先探索）有關的元件 metadata：

- agent 和 skill 的描述；
- 當 harness 預先探索指令時，指令的描述；
- 在明確指名的範圍內、永遠載入的指示檔案；
- 現有有界限的 manifest 有公開時，已設定的 MCP 工具 schema。

完整的 skill、agent、指令和規則本文，通常是按需載入的內容。
把它們的磁碟大小，跟估算的 eager 開銷分開回報，不要
把每份本文都加進 session 基準裡。

## Audit Output

回傳一份精簡的報告，包含：

- harness 和實際檢查過的路徑；
- 依元件類別估算的 eager/探索開銷；
- 已安裝的數量，和最重的 metadata 項目；
- 假設、無法取得的量測，以及最多三項最佳化建議。

每個計算出來的 token 數字，都是靜態設定開銷的估算，
不是即時的 session context。不要宣稱估算值是供應商回報的、
目前的、精確的，或是已實現節省的證據。把使用者引導回
原生的即時 context 指令，查看目前的用量。

## Optional Selected-Record Diagnostic

只有在使用者為了這個診斷明確選定某個檔案時，才檢查已持久化的記錄。這跟預設的即時 context 請求和安裝稽核是分開的。

做本地檔案診斷時，要明確選定一個穩定、一般的 JSONL 檔案，或是你
打算檢查的快照。把下面範例的路徑換掉；這不會去尋找或重新連回 session。
這段程式碼只會印出彙總的位元組數。它一次讀一行，所以記憶體用量取決於
最大的那筆記錄；避免很大的記錄和還在持續成長的檔案。

```sh
python3 - "/path/to/selected-session.jsonl" <<'EOF'
import json
import sys

total = attachment = other = unclassified = 0
try:
    with open(sys.argv[1], "rb") as source:
        for raw in source:
            size = len(raw)
            total += size
            try:
                record = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                unclassified += size
                continue
            record_type = record.get("type") if isinstance(record, dict) else None
            if not isinstance(record_type, str):
                unclassified += size
            elif record_type == "attachment":
                attachment += size
            else:
                other += size
except OSError:
    print("Cannot read selected JSONL file.", file=sys.stderr)
    raise SystemExit(1)

pct = attachment * 100.0 / total if total else 0.0
print(f"persisted {total}B | attachment records {attachment}B ({pct:.1f}%) | "
      f"other records {other}B | unclassified {unclassified}B")
EOF
```

三個類別加起來等於原始檔案的位元組數，包含換行符號和空白行。
`attachment` 是精確的記錄類型過濾，不保證符合 harness 目前內部的
schema。其他記錄的 `type` 是不同的字串；格式錯誤的 JSON、無效的 UTF-8、非物件的
值、缺少或非字串的 type，以及空白行，都歸為 unclassified。這兩個類別都不代表
「對話」，百分比也只是已持久化位元組數的佔比。

這些數字無法證明目前使用中的 context、剩餘空間、token 用量、計費，或是重新連線時會載入什麼。
要看 harness 回報的目前 context 和用量，請使用對應版本的
[`/context` 和 `/usage` 指令（`/cost` 是別名）](https://code.claude.com/docs/en/commands)。
