---
name: hermes-imports
description: 把本地的 Hermes 操作員工作流程，轉成經過清理的 ECC skill 和 release-pack 產出物。準備把 Hermes 工作流程公開給 ECC 重複使用，又不能洩漏私有的 workspace 狀態、憑證或僅限本機的路徑時使用。
metadata:
  origin: ECC
---

# Hermes Imports

要把反覆使用的 Hermes 工作流程，變成可以安全放進 ECC 發佈的東西時，就用這個 skill。

Hermes 是操作員的 shell。ECC 是可重複使用的工作流程層。匯入應該把穩定的模式從 Hermes 搬進 ECC，但不能搬走私有的狀態。

## When To Use

- 某個 Hermes 工作流程已經重複了夠多次，值得變成可重複使用的。
- 某個本地的操作員 prompt 應該變成公開的 ECC skill。
- 發表、內容、研究或工程的工作流程，需要經過清理的交接文件。
- 某個工作流程提到本地路徑、憑證、個人資料集，或是私人帳號名稱，發佈之前必須移除。

## Import Rules

- 把本地路徑轉成 repo 相對路徑或佔位符。
- 把真實的帳號名稱換成角色標籤，例如 `operator`、`default profile` 或 `workspace owner`。
- 描述憑證需求時，只寫提供者的名稱。
- 範例要保持精簡、偏操作。
- 不要發佈原始的 workspace 匯出檔、token、OAuth 檔案、健康資料、CRM 資料或財務資料。
- 如果工作流程需要私有狀態才說得通，就留在本地。

## Sanitization Checklist

commit 匯入的工作流程之前，掃描下列項目：

- 像 `/Users/...` 這樣的絕對路徑
- `~/.hermes` 路徑，除非這份文件明確是在說明本地設定
- API key、token、cookie、OAuth 檔案或 bearer 字串
- 電話號碼、私人 email 地址和個人聯絡人關係圖
- 還沒公開的客戶名稱、家人名字或帳號名稱
- 營收、健康或 CRM 細節
- 含有私有系統工具輸出的原始 log

## Conversion Pattern

1. 找出可重複的操作員迴圈。
2. 去掉私有的輸入和輸出。
3. 把本地路徑改寫成 repo 相對路徑的範例。
4. 把一次性的指示，變成 `When To Use` 段落和簡短的流程。
5. 加上具體的輸出要求。
6. 開 PR 之前，先跑一次 secret 和本地路徑的掃描。

## Example: Launch Handoff

本地的 Hermes prompt：

```text
Read my local workspace files and finalize launch copy.
```

適合 ECC 的安全版本：

```text
Use the public release pack under docs/releases/<version>/.
Return one X thread, one LinkedIn post, one recording checklist, and the missing assets list.
```

## Example: Quiet-Hours Operator Job

本地的 Hermes job：

```text
Run my private inbox, finance, and content checks overnight.
```

適合 ECC 的安全版本：

```text
Describe the scheduler policy, the quiet-hours window, the escalation rules, and the categories of checks. Do not include private data sources or credentials.
```

## Output Contract

回傳：

- 候選的 ECC skill 名稱
- 經過清理的工作流程摘要
- 需要的公開輸入
- 已移除的私有輸入
- 剩餘的風險
- 應該建立或更新的檔案
