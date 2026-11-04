---
name: verify
description: 針對隔離的假 $HOME 實際執行 claude-for-msft-365-install 的管理員 script 和指令，驗證對它們所做的變更。
---

# 驗證 claude-for-msft-365-install

這個 plugin 是**管理員用的 CLI 工具**，不是 app。沒有東西要 build，也沒有 server 要啟動。操作介面就是終端機：macOS 上是 `scripts/*.sh`，Windows 上是 `scripts/*.ps1`。

## Lint 關卡

```bash
python3 scripts/check.py           # from the REPO ROOT, not the plugin dir
bash -n claude-for-msft-365-install/scripts/<script>.sh
```

`check.py` 會 lint 每一個 manifest，並自行安裝 pre-commit hook，用來對 `.claude-plugin/plugin.json` 做 patch 版本號遞增。commit 之前要先跑。

## 針對假 $HOME 執行 script

每個 macOS script 都從 `$HOME` 解析 Office 路徑，所以覆寫它就能得到一個用完即丟的沙盒，可以放心測試會造成破壞的 `--apply` 路徑，不會動到真實的 Office 資料。

```bash
S=<scratchpad>/sandbox
for app in Excel Word Powerpoint; do
  mkdir -p "$S/Library/Containers/com.microsoft.$app/Data/Documents/wef"
done
printf '<x/>' > "$S/Library/Containers/com.microsoft.Excel/Data/Documents/wef/aaaaaaaa-1111-1111-1111-111111111111.manifest-a.xml"

HOME=$S ./scripts/clear-addin-cache.sh                      # list
HOME=$S ./scripts/clear-addin-cache.sh --id <GUID>          # dry-run
HOME=$S ./scripts/clear-addin-cache.sh --id <GUID> --apply  # destructive
```

至少放**兩個 ID，分布在兩個 app**，而且**大小寫混用**。這兩個特性都抓到過真正的 bug：跨 app 的影響範圍，還有一個區分大小寫的 glob 回報 "already clear"，結果讓管理員跑去整個資料夾清空。

## 證明儲存空間有被保留

這個 plugin 最關鍵的承諾是：清除 manifest 絕對不會動到使用者的聊天紀錄。驗證方法是在操作前後，對兩棵目錄樹做快照比對，而且要針對**真實的** `$HOME`：

```bash
snap() {
  for app in Excel Word Powerpoint; do
    find "$HOME/Library/Containers/com.microsoft.$app/Data/Library/WebKit/WebsiteData" \
         -type f -exec stat -f '%N %z %m' {} \; 2>/dev/null
    find "$HOME/Library/Containers/com.microsoft.$app/Data/Documents/wef" \
         -type f -exec stat -f 'WEF %N %z' {} \; 2>/dev/null
  done | sort
}
snap > before.txt;  <run the script>;  snap > after.txt;  diff before.txt after.txt
```

Manifest 放在 `Data/Documents/wef`，儲存空間放在 `Data/Library/WebKit/WebsiteData`。這是不同的子樹，diff 應該只顯示你移除的那個 manifest。**把任何你放進去的檔案還原，再 diff 一次，確認你把機器留得跟你找到時一樣。**

## 注意事項

- **Bash 工具跑的是 zsh。** Script 是 `#!/usr/bin/env bash`，要測試 bash 專屬的行為（`shopt`、glob 語意），請在 `bash <<'EOF' … EOF` 裡面測，不要直接在行內測。
- **`PRAGMA integrity_check` 和 `SELECT count(*)` 在匯出的 IndexedDB 檔案上會失敗**，錯誤是 `no such collation sequence: IDBKEY`。這是 WebKit 的自訂排序規則，不是檔案損毀，連來源檔案也會失敗。要驗證完整性，請在兩邊都跑 `SELECT sum(length(value)) FROM Records;`。
- **沒有在 Windows 上實際跑過，就絕對不要宣稱 `.ps1` script 能用。** macOS 沒有 PowerShell，所以只在這裡驗證過的 `.ps1` 變更，等於沒驗證。要在真正的 Windows 主機上、用 Windows PowerShell 5.1 執行，而且在行為測試之前，一定要先做**語法解析檢查**：

  ```powershell
  $e = $null
  [System.Management.Automation.PSParser]::Tokenize(
    (Get-Content -Raw .\clear-addin-cache.ps1), [ref]$e) | Out-Null
  if ($e.Count) { $e | ForEach-Object { $_.Message } } else { 'parse ok' }
  ```

  一個檔案在 macOS 上可能完全沒問題，到了 Windows 上卻完全無法解析（見下方的 ASCII 說明），所以要先確認能解析。

- **`.ps1` 檔案必須是純 ASCII**（由 `scripts/check.py` 強制檢查）。Windows PowerShell 5.1 會把沒有 BOM 的 `.ps1` 當成 ANSI 讀取，所以破折號（em dash）會被解碼成包含 `"` 的亂碼，把字串截斷並破壞解析。`clear-addin-cache.ps1` 就是這樣壞掉才發布出去的，而且沒有任何 macOS 檢查抓得到。
- 測試參數解析器。`--flag` 當最後一個參數時，會讓 `shift 2` 在 `set -e` 下失敗，並以 exit 1 結束且**沒有任何輸出**；每個 flag 都需要 `[ $# -ge 2 ]` 的防護。
