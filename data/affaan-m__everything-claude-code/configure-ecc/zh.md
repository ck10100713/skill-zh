---
name: configure-ecc
description: "在目前的 harness 裡執行對話式的 ECC 設定精靈：盤點安裝狀況，在 Claude Code 裡收集範圍（user/project/local）和 hook 模式（off/minimal/standard/strict），在 Codex 用它原生的 plugin 生命週期，或把專案層級的內容安裝到 ./.kimi-code 底下，然後預覽、套用並驗證。適用於安裝、更新、重新設定或修復 ECC 安裝、變更 hook 設定檔，或在不同安裝範圍之間搬移 ECC。"
metadata:
  origin: ECC
---

# Configure ECC

在目前的 harness 裡執行一個對話式的精靈。先盤點，只收集
支援的選項，預覽，確認一次，以非互動方式套用，驗證，
成功之後才顯示歡迎畫面。絕對不要把 ECC clone 到暫存
目錄，也不要手動複製 plugin 元件。

在人手操作的終端機裡，正式的進入點是 `ecc setup` 和
`npx ecc-universal setup`。在 harness 裡面，改用下面明確的非互動
指令。

## Route by the current harness

- 在 Claude Code 裡，用下面完整的範圍加 hook 精靈。
- 在 Codex 裡，用 Codex 原生的 plugin 生命週期。不要提供 Claude 的範圍，
  也不要把 ECC 的四種 Claude hook 設定檔對應到 Codex。
- 在 Kimi 裡，把專案層級的內容安裝到 `./.kimi-code`。Kimi 沒有
  提供 ECC 的 Claude 生命週期 hook 設定檔。
- 如果不確定是哪個 harness，說明偵測到的證據，並在執行任何會變更資料的指令之前，
  先問要設定哪個 harness。

這個 skill 是安裝後的重新設定路徑。它無法攔截或
取代供應商內建的首次安裝 UI。

## Claude Code: run the full conversational wizard

### 1. Inventory without changing anything

兩個指令都要執行，並摘要已安裝的 ECC 範圍、啟用狀態和
marketplace 來源：

```bash
claude plugin list --json
claude plugin marketplace list --json
```

只有一個既有的 `ecc@ecc` 安裝時，視為重新設定。不要把 Claude 供應商自己提供的「Open home page」按鈕
當成已安裝的證據。遇到多個 ECC
範圍、舊版/手動安裝、格式錯誤的設定，或 marketplace 衝突時，停下來並回報 setup 回傳的復原方式；
絕對不要猜該刪哪個狀態。

### 2. Collect exactly two choices

只問一個範圍的問題，而且要求給一個值：

- `user | project | local`
- `user` 是這位使用者的全域設定。
- `project` 透過 repository 設定共享。
- `local` 只屬於目前專案，是私人的。

只有被選中的範圍，才在視覺上標示成已選取或安裝中。如果使用者
從單一既有安裝選了不同的範圍，就把它描述成範圍遷移，並在下面的指令加上 `--move-scope`。

只問一個 hook 模式的問題，而且要求給一個值：

- `off | minimal | standard | strict`
- `off` 保留 skill 和指令，但停用 ECC 的 hook 自動化。
- `minimal` 啟用最輕量的生命週期和安全自動化。
- `standard` 在品質和安全自動化之間取得平衡。
- `strict` 啟用最強的檢查和提醒。

Hook 偏好是個人的 Claude plugin 設定，它不會跟著
選擇的安裝範圍走。

### 3. Preview and confirm once

優先用 plugin 內附的 setup script。代入選好的兩個值，
只有在範圍遷移時才加上 `--move-scope`：

```bash
node "$CLAUDE_PLUGIN_ROOT/scripts/setup.js" --mode claude-plugin \
  --scope <scope> --hooks <hooks> [--move-scope] --dry-run --json
```

如果沒有 `$CLAUDE_PLUGIN_ROOT`，就用已發布的 npm 套件：

```bash
npx --yes --package ecc-universal ecc setup --mode claude-plugin \
  --scope <scope> --hooks <hooks> [--move-scope] --dry-run --json
```

只顯示一份確認摘要，內容包含規劃的動作、一個範圍、
一個 hook 模式、marketplace 動作，以及任何來源到目的地的遷移。
問一個是/否的問題。不要透過 harness 的 shell 工具執行單純的互動式 `ecc setup`，
因為那個 shell 通常不是 TTY。

### 4. Apply the explicit choices

確認之後，用同樣的路徑再跑一次，但不要加 `--dry-run`。每個選項都要
明確指定，並要求 JSON 輸出，這樣才能確定性地檢查成功與否：

```bash
node "$CLAUDE_PLUGIN_ROOT/scripts/setup.js" --mode claude-plugin \
  --scope <scope> --hooks <hooks> [--move-scope] --yes --json
```

備用方案：

```bash
npx --yes --package ecc-universal ecc setup --mode claude-plugin \
  --scope <scope> --hooks <hooks> [--move-scope] --yes --json
```

### 5. Verify, then render the welcome

要求 exit status 為零，而且 setup 結果裡的 `scope` 和 `hooks` 等於
選擇的值。然後獨立執行：

```bash
claude plugin list --json
```

只有在選定的範圍裡剛好有一個啟用的 `ecc@ecc` 項目時才繼續。當
`$CLAUDE_PLUGIN_ROOT` 可用時，把成功的 setup 的
`action`（`installed`、`updated`、`migrated`、`resumed` 或
`already-migrated`）傳給內附的 renderer：

呼叫它之前，要求供應商回報的版本符合
`scripts/lib/terminal-welcome.js` 裡的 `ECC_VERSION_PATTERN`。遇到非預期的
版本文字就拒絕，不要把它插進 shell 指令裡。

```bash
node -e 'const { renderTerminalWelcome } = require(process.env.CLAUDE_PLUGIN_ROOT + "/scripts/lib/terminal-welcome"); process.stdout.write(renderTerminalWelcome({ action: process.argv[1], version: process.argv[2], color: process.stdout.isTTY }));' "<action>" "<installed-version>"
```

歡迎畫面只顯示一次。遇到失敗、dry-run、取消、範圍或
hook 不符，或無法驗證的狀態時，不要顯示；改為回報錯誤和
復原方式。驗證過變更之後，告訴使用者執行
`/reload-plugins` 或重新啟動 Claude Code。

## Codex: use the native plugin lifecycle

用 `codex plugin marketplace list --json` 和
`codex plugin list --available --json` 盤點。Codex 原生的 plugin 指令沒有
Claude 風格的 `user | project | local` 選擇器。Codex 原生 plugin 確實支援
供應商專屬的 hook，但 Codex 需要明確的信任。讓 Codex
顯示那個信任決定；不要問 Claude 的四種設定檔 hook 問題，
也不要宣稱那些設定檔可以對應到 Codex。

如果 ECC marketplace 不存在，就加進去。否則更新它的快照：

```bash
codex plugin marketplace add affaan-m/ECC
codex plugin marketplace upgrade ecc --json
```

要求一次確認，然後安裝，或以冪等的方式更新已安裝的
快取，並驗證：

```bash
codex plugin add ecc@ecc --json
codex plugin list --json
```

只有在 JSON 回報 ECC 已安裝，而且提供它的
`installedPath` 時才繼續。然後顯示已驗證 bundle 的歡迎畫面：

只能使用 Codex JSON 回傳的那個完整絕對 `installedPath`。拒絕
控制字元，並要求已安裝的版本符合
`ECC_VERSION_PATTERN`。直接用這個參數陣列呼叫 `node`；這是
工具 API 的呼叫，不是 shell 指令：

```text
["<installedPath>/scripts/welcome.js", "--action", "configured", "--version", "<installed-version>"]
```

如果目前的 harness 無法用獨立的參數陣列呼叫可執行檔，就跳過歡迎畫面。
絕對不要用 Codex JSON 的值去組出 shell 指令。

絕對不要宣稱 Claude 的 `off | minimal | standard | strict` 設定檔
已經套用到 Codex。

## Kimi: install the project surface

確認之前，先說明能力摘要：目的地
`./.kimi-code`；ECC 生命週期 hook 是 `hooks=unsupported`。不要問
Claude 的範圍或 hook 模式問題。先預覽：

```bash
npx --yes --package ecc-universal ecc install --profile core --target kimi --dry-run
```

針對那個專案目的地顯示一次確認，然後套用同一個
指令，但不加 `--dry-run`。用這個驗證：

```bash
npx --yes --package ecc-universal ecc doctor --target kimi
```

只有在 doctor 成功，而且已安裝的指示和 skill 都還留在
`./.kimi-code` 裡面時，才顯示：

```bash
npx --yes --package ecc-universal ecc welcome --action configured
```

不要宣稱 Kimi 已安裝或設定了 ECC 的生命週期 hook。
