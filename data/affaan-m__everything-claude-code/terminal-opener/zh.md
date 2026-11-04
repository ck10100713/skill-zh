---
name: terminal-opener
description: 透過一個可重複使用、不經過 shell 的啟動計畫，把執行檔和它的引數陣列開在看得見的終端機視窗裡，支援 dry-run、JSON、能力偵測、分離式 fallback 和獨立復原模式。當 Codex 需要在新的主機終端機視窗中開啟互動式 CLI、SSH session、本機開發 process、sandbox，或其他以 argv 為基礎的指令；診斷是否有支援的終端機可用；或在要求的終端機不被支援時提供可操作的計畫時使用。
---

# Terminal Opener

用 `scripts/open-terminal.js`，把執行檔和每個引數都保留成
分開的 process 項目。絕對不要把 shell 指令字串插值進去。每一次
spawn 都要保持 `shell: false`。預設用不會真的啟動的計畫。只有在
使用者明確要求開真正的視窗、而且 argv 已經審查過之後，才用 `--launch`。
被啟動的 process 會繼承呼叫端 process 的完整環境，
包括帶有祕密的變數。啟動器不會過濾
環境。要從一個環境暴露給目標指令也安全的 shell 來執行它。

## 啟動指令

啟動器的選項放在 `--` 之前，然後只傳一個執行檔，接著是
它的引數陣列：

```bash
node skills/terminal-opener/scripts/open-terminal.js \
  --launch \
  --cwd /absolute/host/path \
  -- ssh -t example.test command-with-arguments
```

先跑一般模式。讓 WezTerm 先嘗試用 mux 開新視窗，如果 mux
不可用，啟動器再 fallback 成分離式的 `wezterm start` process。
用了 fallback 時，要讀 JSON 輸出裡的 `muxFailure`（或
人類可讀的失敗那一行），診斷 mux 路徑為什麼失敗。

## 從終端機設定中復原

當使用者設定或 mux 狀態可能干擾要求的指令時，加上 `--recover` 或 `--standalone`。用下面的參數
啟動一個分離式的 WezTerm process：

```text
--skip-config start --always-new-process
```

要預期復原模式會刻意略過所有使用者的終端機設定。

## 啟動前先檢查

省略 `--launch`（或加上 `--dry-run`），再加上 `--json`，就能檢查確切的
執行檔、argv、工作目錄、終端機 adapter、主要啟動方式和
fallback，而不會開視窗。把 JSON 計畫當作給呼叫端的
組合邊界。

不帶指令執行 `--detect --json`，可以探測終端機是否可用。當 adapter 缺少或不被支援時，
照著回傳的 `action` 做。目前的 adapter 用的是 WezTerm；
其他被要求的終端機，要當成不被支援的計畫處理，
不要當成要執行的指令。
