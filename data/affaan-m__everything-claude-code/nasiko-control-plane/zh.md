---
name: nasiko-control-plane
description: 透過 ECC 管理實驗性的 Nasiko CLI 生命週期：唯讀的狀態檢查、需經同意才能安裝且先 dry-run 預覽的指定合格版本，以及會檢查所有權的解除安裝，全程在明確的遙測和機密界線之下。使用者要求安裝、檢查或移除 Nasiko CLI，或確認它是否存在時使用。
---

# Nasiko CLI Lifecycle Bridge

使用者明確要求 ECC 安裝、檢查或移除合格的 Nasiko CLI 時，用這個 skill。
這個 skill 不會操作 Nasiko control plane。

## Safety contract

- 一開始先跑 `ecc nasiko status --json`。status 是唯讀的。
- 安裝一律需要使用者明確同意，並加上 `--yes`。
- 只安裝 ECC 合格的指定版本，目前是 `v0.1.0`。
- 先用 `ecc nasiko install --version v0.1.0 --dry-run --json` 預覽。
- 要等使用者審閱過版本、registry 來源、digest 和目的地之後，才用
  `ecc nasiko install --version v0.1.0 --yes --json` 安裝。
- 只移除仍然合格、由 ECC 管理的執行檔，用
  `ecc nasiko uninstall --version v0.1.0 --yes --json`。移除前先用
  `--dry-run` 預覽。
- 合格的來源是 `https://github.com/Nasiko-Labs/nasiko`，授權為
  Apache-2.0；壓縮檔和解開後執行檔的 SHA-256 值都有固定。
- 絕對不要用下載來的 shell 或 PowerShell
  bootstrap 腳本取代合格的指令。
- 絕對不要把機密或憑證放進指令參數、紀錄、skill 輸出、
  安裝 metadata 或 ECC 狀態裡。
- Nasiko 的遙測，以及任何和 Nasiko 或 Ito 的分享，都必須是 opt-in，
  而且要另外揭露。安裝不等於同意遙測。

## Lifecycle boundary

最初的 ECC bridge 支援合格的安裝、唯讀的狀態，以及
會檢查所有權的解除安裝。連線、驗證、
啟動、deploy 或關閉這些動作，在它們有自己經過驗證的 ECC
合約之前，直接使用正統的 Nasiko CLI。不要猜 CLI 的動詞。

安裝 CLI 並不能證明 control-plane server 正在運作、
agent 受到治理、路由或 ACL 有效、可觀測性完整、遙測
已啟用，或 Ito 運算已連上。每個狀態都要分開回報。

## Failure behavior

- 如果平台、架構、版本、manifest、digest、壓縮檔、執行檔或
  目的地沒通過驗證，就停下來，不要執行該成品。
- 不要退回使用 `latest`。
- 不要搜尋任意的 `PATH` 項目。用 ECC 的合格位置，或為了開發驗證而明確指定的
  絕對路徑 `ECC_NASIKO_CLI_EXECUTABLE`。
- 不要把部分完成或有歧義的安裝當成成功。
