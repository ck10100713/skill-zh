---
name: ito-training
description: 檢查已完成預訂的 Itô 算力是否提供 ML 訓練，當官方後端可用時，交接一份經過明確確認的訓練 manifest。在 ito-compute 已預訂 GPU 節點之後，使用者想在那批機器上做預訓練、微調或 RL 時使用。ECC 自己沒有實作任何訓練堆疊。
metadata:
  origin: ECC
  status: scaffold
---

# Itô Training

`ito-training` 是 ECC 中負責 Itô 算力上訓練的官方 skill。ECC
自己絕對不會執行訓練器、排程器或資料 pipeline；它也絕對不會預訂、
保留或花錢。這個 skill 是接在 `ito-compute` 的**已完成預訂**之後。

## Current production boundary

目前還沒有託管式訓練。ECC 的 bridge 只開放 `login`、
`logout`、`auth`、`find`、`status` 和有明確把關的 `evals`。它沒有
`train` 指令，而官方 CLI 的 `run` 指令和交易台的 `training-run`
後端仍然只是骨架。本地端可以強制保證的是：ECC 在解析或啟動帶有憑證的官方 client 之前，
就會拒絕 `train`。

因此要在認證或任何指令執行之前就停下來。回報缺少的功能，並把控制權還給
發起的 agent。絕對不要用本地訓練器、SSH 輔助工具、瀏覽器工作流程或購買端點來替代。

## Required entitlement

當訓練功能實作完成後，第一道關卡是由伺服器驗證的已完成
預訂。Harness 的記憶、RFQ、報價、節點 IP 或 SSH 存取，都不能證明
有資格。後端必須回傳最新的訓練資格，綁定到
已認證的帳戶、預訂、GPU 拓撲、region、fabric 和期限。
過期、被撤銷、不相符、不完整或已經釋放的預訂，在確認之前都要以 fail
closed 處理。

## Future CLI and API contract

預計的指令名稱是 `train`。未來的交接必須等同於：

```sh
ecc ito train \
  --booking <server-verified-booking-id> \
  --manifest <absolute-reviewed-json-file> \
  --confirmation-ref <opaque-non-authorizing-reference> \
  --idempotency-key <stable-retry-key> \
  --json
```

經過審查的 manifest 必須指明模型大小與 revision、附有去污染來源紀錄的資料
參照、訓練目標、後訓練配方、以美元計的預算上限、checkpoint 政策，以及最大增量
成本。任何原始的 API key、SSH key、節點密碼、bearer token 或資料集
憑證，都不能出現在引數、manifest、log、MCP 結果或對話中。

Client 必須對 manifest 路徑做規範化、拒絕 symlink、以不跟隨連結的方式開啟一般
檔案、要求適當的擁有者和嚴格的權限、強制限制大小，並對已開啟的
file descriptor 的內容做 hash。在任何工作負載變更之前，那個 digest
必須與綁定在確認裡的 digest 完全相等。路徑被替換、digest 不符、檔案過大或可變動的
不安全檔案，都要以 fail closed 處理。

建立工作負載必須由官方 API（不是 ECC）負責，並回傳結構化 JSON，
包含 `ok`、`live_api_contacted`、`notice`，以及 `data` 或 `error`。
訓練資料必須包含穩定的預訂、run、manifest 和 idempotency ID，
加上一個狀態列舉。錯誤必須包含穩定的代碼，以及不含 secret 的安全訊息。

## Confirmation and execution gates

建立工作負載之前，要求以下全部成立：

1. 來自官方後端的最新資格與訓練可用性。
2. 可供審查、不可變的 manifest，以及確定性的 digest。
3. 另外一份單次使用的確認，綁定帳戶、動作、manifest 和
   成本，有效期短，並有重放保護。CLI 引數只帶有
   不透明、不具授權效力的確認參照；伺服器在帶外解析並
   消耗這個 bearer 能力。
4. 由呼叫者提供的 idempotency key，並與 run 一起以原子方式保留。
5. 伺服器端對 fabric、容量、資料政策、checkpoint 儲存空間和成本的
   驗證，包含 manifest 的預算上限。

認證只代表身分，不代表有工作負載的權限。登入、API key、報價
或已完成的預訂，絕對不能取代訓練確認。
檢視和產生計畫不能建立工作負載。取消和清理
是另外的變更操作，各有自己限定範圍的確認和 idempotency
邊界。

## Lifecycle and recovery

在同一個官方 client 開放租戶範圍的狀態、log、指標、checkpoint 列表、取消和清理之前，
正式環境的介面都是不完整的。
每個操作都需要有限制的連線和整體 timeout、會感知撤銷的
錯誤，以及結構化的輸出。遇到不確定的傳輸失敗之後，重試之前要先用
idempotency key 查詢狀態；絕對不要只因為第一次的回應遺失，就建立第二個 run。
被撤銷的憑證會停止輪詢，並把控制權還給發起的 agent，而不會自動啟動登入。

要誠實回報各階段關卡的結果；絕對不要覆寫失敗的 eval 關卡。清理必須是
可觀察的，而且除非另外明確授權了那個經濟行為，否則不能釋放或修改底層的預訂。

## Proposed backend stages

這些階段描述的是未來的後端（Layer 0.3），不是 ECC 裡現有的程式碼：

1. Data prep — manifest、去重、對 eval 套件做去污染；
   用 150M-ladder 決策工作，作為自訂資料便宜的事前檢查。
2. Parallelism and precision — 依模型大小、節點數、fabric 選擇；
   浪費資源的組合會被拒絕。
3. Checkpointing and fault tolerance — async DCP、torchft；偵測 < 10 分鐘，
   恢復 < 15 分鐘。Loss spike 後的重啟是建議的、需要人工把關的動作。
4. Curriculum and eval gates — 分階段的 pretrain / mid-train / long-context /
   post-training，每個階段都有固定的 eval 組合；關卡失敗就停止 run。
5. Post-training — SFT → DPO → RLVR（帶有 DAPO 穩定性修正的 GRPO），
   訓練器/rollout 分離，並限制過期程度。

後端會輸出交易台的遙測資料（goodput、中斷率、checkpoint
頻寬），讓交易台能誠實地為訓練區塊定價。

在官方 runtime 裡，上面每個關卡和生命週期操作都存在之前，
這個 skill 都只是一個 fail closed 的可用性檢查，加上文件交接。
