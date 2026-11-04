---
name: ito-inference
description: 檢查已完成預訂的 Itô 算力是否提供模型服務，當官方後端可用時，交接一份經過明確確認的服務 manifest。在 ito-compute 已預訂 GPU 節點之後，使用者要求 OpenAI 相容的端點、ito-serve、託管的 Kimi，或自行託管的開放權重推論時使用。ECC 自己沒有實作任何服務堆疊。
metadata:
  origin: ECC
  status: scaffold
  aliases: ito-serve, hosted-open-weights
---

# Itô Inference

`ito-inference` 是 ECC 中負責 Itô 算力推論服務的唯一官方 skill。提到 `ito-serve`
的需求都導到這裡；不要建立或安裝第二個 `ito-serve` skill。ECC 絕對不會 SSH 到節點、下載權重、啟動
引擎或對外開放端點；它也絕對不會預訂、保留或花錢。

## Current production boundary

目前還沒有託管式服務。ECC 的 bridge 只開放 `login`、
`auth`、`find`、`status` 和有明確把關的 `evals`。它沒有 `serve` 指令。
官方 runtime 只把 `inference` 記載為不支援的相容性
探測；ECC 不會呼叫它，也不依賴它。MCP 介面只開放 auth、
find 和 status。本地端可以強制保證的是：ECC 在解析或啟動帶有憑證的官方 client 之前，
就會拒絕 `serve`。

因此要在認證或任何指令執行之前就停下來。回報缺少的功能，並把控制權還給
發起的 agent。絕對不要用本地執行器、SSH 輔助工具、瀏覽器工作流程、購買端點，或任何未被追蹤的
本地 `ito-serve` 草稿來替代。

## Required entitlement

當服務功能實作完成後，第一道關卡是由伺服器驗證的已完成預訂。Harness 的記憶、RFQ、報價、節點 IP 或 SSH 存取，都不能證明有資格。
後端必須回傳最新的服務資格，綁定到
已認證的帳戶、預訂、GPU 拓撲、region、fabric、期限和模型政策。過期、被撤銷、不相符、不完整或已經釋放的預訂，
在確認之前都要以 fail closed 處理。

## Future CLI and API contract

預計的指令名稱是 `serve`；在正式環境的契約上線後，`inference` 只能作為
明確標示為已棄用的相容別名保留。
未來的交接必須等同於：

```sh
ecc ito serve \
  --booking <server-verified-booking-id> \
  --manifest <absolute-reviewed-json-file> \
  --confirmation-ref <opaque-non-authorizing-reference> \
  --idempotency-key <stable-retry-key> \
  --json
```

經過審查的 manifest 必須指明模型 revision、引擎與版本、
量化方式、tensor/pipeline 拓撲、端點對外開放的政策、產物
checksum、儲存空間上限、runtime 限制、選用的 TTFT/TPOT 目標，以及
最大的增量成本。任何原始的 API key、SSH key、節點密碼或 bearer
token，都不能出現在引數、manifest、log、MCP 結果或對話中。

Client 必須對 manifest 路徑做規範化、拒絕 symlink、以不跟隨連結的方式開啟一般
檔案、要求適當的擁有者和嚴格的權限、強制限制大小，並對已開啟的
file descriptor 的內容做 hash。在任何工作負載變更之前，那個 digest
必須與綁定在確認裡的 digest 完全相等。路徑被替換、digest 不符、檔案過大或可變動的
不安全檔案，都要以 fail closed 處理。

建立工作負載必須由官方 API（不是 ECC）負責，並回傳結構化 JSON，
包含 `ok`、`live_api_contacted`、`notice`，以及 `data` 或 `error`。服務
資料必須包含穩定的預訂、工作負載、manifest 和 idempotency ID，加上一個
狀態列舉；在健康檢查和模型檢查通過之前，不能宣稱端點已上線。錯誤必須包含穩定的代碼，以及不含 secret 的安全訊息。

## Confirmation and execution gates

建立工作負載之前，要求以下全部成立：

1. 來自官方後端的最新資格與服務可用性。
2. 可供審查、不可變的 manifest，以及確定性的 digest。
3. 另外一份單次使用的確認，綁定帳戶、動作、manifest 和
   成本，有效期短，並有重放保護。CLI 引數只帶有
   不透明、不具授權效力的確認參照；伺服器在帶外解析並
   消耗這個 bearer 能力。
4. 由呼叫者提供的 idempotency key，並與工作負載一起以原子方式保留。
5. 伺服器端對 fabric、容量、模型政策、儲存空間和成本的驗證。

認證只代表身分，不代表有工作負載的權限。登入、API key、報價
或已完成的預訂，絕對不能取代服務確認。檢視
和產生計畫不能建立工作負載。取消和清理是另外的變更操作，各有自己限定範圍的確認和 idempotency 邊界。

## Lifecycle and recovery

在同一個官方 client 開放租戶範圍的狀態、log、指標、取消和清理操作之前，
正式環境的介面都是不完整的。每個
操作都需要有限制的連線和整體 timeout、會感知撤銷的錯誤，
以及結構化的輸出。遇到不確定的傳輸失敗之後，重試之前要先用
idempotency key 查詢狀態；絕對不要只因為第一次的回應遺失，就建立第二個工作負載。
被撤銷的憑證會停止輪詢，並把控制權還給發起的 agent，而不會自動啟動登入。

只有在端點健康、模型身分和 canary 推論全部通過之後，才回報 `ready`。
要誠實回報中間和終結的失敗狀態。清理必須是可觀察的，
而且除非另外明確授權了那個經濟行為，否則不能釋放或修改底層的預訂。

## Proposed backend stages

這些階段描述的是未來的後端，不是 ECC 裡現有的程式碼：

1. 驗證資格、拓撲、fabric 和成本的關卡。
2. 把固定 checksum 的權重抓到由後端管理的儲存空間。
3. 產出並驗證可供審查的拓撲/引擎計畫。
4. 透過供應商的 control plane 啟動，絕對不從 ECC 直接用 root SSH。
5. 暖機、測試健康與模型身分、跑 SLO canary，然後註冊
   端點和已遮蔽的設定。

在官方 runtime 裡，上面每個關卡和生命週期操作都存在之前，
這個 skill 都只是一個 fail closed 的可用性檢查，加上文件交接。
