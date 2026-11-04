---
name: ito-compute
description: 透過另外安裝的官方 CLI，查詢即時 GPU 庫存、送出經過認證的 Itô 固定費率 RFQ、檢查 RFQ 或採購狀態、撤銷裝置憑證，並執行有明確把關的節點資格驗證。使用者要找 H100/H200 算力、申請固定算力費率、查看 Itô 算力狀態、驗證 GPU 節點、撤銷 Itô 存取，或租用/購買 GPU 算力、而且需要說明支援範圍的邊界時使用。
---

# Itô Compute

使用官方的 Itô compute CLI 或 MCP 伺服器。ECC 沒有實作平行的 client、本地模擬、預訂、
工作負載執行器或推論伺服器。ECC 自己不做任何瀏覽器自動化。

## Install the canonical local package

`ito-compute-cli` 目前尚未發布。要從它的官方 repository 自己建置，
不要用 `npx`、`npm exec` 或來路不明的套件：

```sh
git clone https://github.com/Ito-Markets/ito-cloud-runtime.git
cd ito-cloud-runtime/cli/ito-compute-cli
npm ci
npm run check
```

把 `ECC_ITO_CLI_EXECUTABLE` 設成明確的絕對路徑，指向建置好的入口：

```text
/absolute/path/to/ito-cloud-runtime/cli/ito-compute-cli/dist/bin/ito.js
```

ECC 絕對不會透過 `PATH` 去尋找這個帶有憑證的 client。
`ecc ito login` 執行的是裝置授權，而且絕對不會繼承 `ITO_API_KEY`。
僅供驗證用的 `auth`，以及 `find` 和 `status`，在有設定時會直接轉發 `ITO_API_KEY`；
不需要 `ITO_AUTH_MODE=legacy`。絕對不要把
key 或 token 放進引數、被追蹤的檔案、MCP 結果、log 或對話中。

## CLI workflow

1. 第一次操作之前先執行 `ecc ito login`。ECC 會把這件事委派給
   官方 CLI 的裝置授權，它預設會打開 Itô 驗證頁面，
   並把裝置 token 存進 macOS Keychain。用
   `ecc ito login --no-browser` 可以不跳出頁面。ECC 自己不做
   瀏覽器自動化。如果發起的 agent 無法完成需要登入的瀏覽器步驟，就把確切的指令交給使用者；等核准完成之後，
   回到原本的任務，繼續執行 `ecc ito auth`。
   裝置 token 預設使用 macOS Keychain。改用檔案 token 必須是明確的選擇，
   而且它的資料夾和 token 檔案都必須維持僅限擁有者存取（0700 和 0600）。
2. 執行 `ecc ito auth` 來驗證既有憑證；它絕對不會啟動登入，
   而且會拒絕 `--no-browser`。
3. 在 `ecc ito find` 之前，要先取得買方明確同意送出 RFQ 的授權。
   - 必須有 `gpu`、`count`、整數的 `days`、`max-rate`、`nodes`、
     `gpus-per-node`、`storage-tb`、`start-window`、`form-factor`、
     `contract-type`、`fabric`、`region`，以及是否允許分批滿足的決定。
   - 要求 `count == nodes * gpus-per-node`；絕對不要自己推導拓撲。
   - 只有在買方明確接受任何 fabric 或 region 時，才用 `any`。
   - 省略 `--allow-split` 代表 false。
4. 執行即時的 RFQ 指令：

   ```sh
   ecc ito find \
     --gpu h200 \
     --count 8 \
     --nodes 1 \
     --gpus-per-node 8 \
     --days 30 \
     --storage-tb 1 \
     --start-window 2099-08-15 \
     --max-rate 3.00 \
     --form-factor bare_metal \
     --contract-type reservation \
     --fabric infiniband \
     --region us-east-1
   ```

5. 執行 `ecc ito status` 來檢查 RFQ 和採購訂單。
   遇到不確定的傳輸失敗之後，要先查狀態，再重複 `find`。
6. 當報價準備好，而且買方明確同意時，接受它：

   ```sh
   ecc ito accept rfq_<ticket-id>
   ```

   這會把票據送到交易台做人工審核。它不會轉移資金，
   也不會預訂容量。沒有買方的明確授權，不要接受。
7. 只有在使用者明確要求撤銷這台裝置時，才執行 `ecc ito logout`。
   遠端撤銷失敗時，官方 CLI 會保留本地憑證，讓
   操作者可以重試；絕對不要手動刪除 token 來代替。

庫存價格只是參考價。RFQ 不等於預訂容量。只有當官方結果包含
非 null 的確定報價時，才把費率視為固定。

## Live node qualification

`ecc ito evals` 把官方 CLI 狹窄的即時轉接器，開放給另外安裝的
`sixtytwo-cli==0.3.33`。它不會透過 ECC 開放本地 fixture 的執行。
呼叫它之前，必須全部滿足以下條件：

- 營運者授權可以聯絡指名的節點；
- `ITO_ENABLE_SIXTYTWO_LIVE=1`；
- `--live-sixtytwo`；
- 明確的節點清單；以及
- 一個已存在的絕對路徑設定資料夾，裡面有 `sixtytwo.yaml`。

```sh
ecc ito evals \
  --cluster clu_prod_example \
  --live-sixtytwo \
  --nodes gpu-01,gpu-02 \
  --config-dir /absolute/path/to/qualification-config
```

官方轉接器只能對明確指定的節點，執行固定版本的檢查和
`sixtytwo test --full`。它不能租用、啟動、
復原、修復、重置、購買或訂購任何資源。ECC 不會把
`ITO_API_KEY` 或模型/雲端憑證轉發到節點資格驗證裡。

## MCP workflow

建置官方套件，然後用絕對路徑設定 stdio 伺服器：

```json
{
  "mcpServers": {
    "ito-compute": {
      "command": "node",
      "args": [
        "/absolute/path/to/ito-cloud-runtime/cli/ito-compute-cli/dist/bin/ito-mcp.js"
      ]
    }
  }
}
```

這個伺服器只開放：

- `ito_auth`
- `ito_find`
- `ito_status`
- `ito_accept`

`ito_auth` 驗證既有憑證；它不會啟動裝置登入。使用
`ito_auth`，收集買方明確的授權和每一項硬性限制，呼叫
`ito_find`，需要時再用 `ito_status` 輪詢。當報價準備好，而且
買方明確同意時，用票據 id 呼叫 `ito_accept`。交易台的
報價通常只是參考價，在交易台確認之前沒有約束力；結果會帶有 `quote_class`。

## Rent or purchase semantics

`find` 會送出 RFQ，可能回傳確定報價，但它不會租用、
購買、預訂、佈建或轉移資金。`accept` 把報價送到交易台
做人工審核；它不會轉移資金，也不會預訂容量。`status` 是
偏讀取的操作，不過供應商的端點可能會對帳既有的採購
訂單。ECC 說明裡那個被動的 dashboard 連結，是使用者自己操作的另一條網頁
路徑；不要拿來當成缺少 CLI 功能時的替代品去開啟或操作。

## Unsupported operations

支援的 client 介面無法鎖定報價、預訂容量、執行
工作負載或提供推論服務。`accept` 是交給交易台的交接，不是購買。
MCP 伺服器不開放資格驗證；請使用上面明確的 CLI 指令。不要
自己發明額外的工具或購買路徑。本地 CLI 不存在或即時操作失敗時，
不要用瀏覽器或 fixture 來替代。回報缺少的功能，然後停下來。
