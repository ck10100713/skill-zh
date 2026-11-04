---
name: agent-runtime-gateway-smoke-test
description: 用一個不需要工具的任務，驗證本機 agent API、臨時的 gateway tunnel 和遠端 sandbox 的 callback，最後還原原本的 app 連線。
metadata:
  origin: ECC
---

# Agent Runtime Gateway Smoke Test

當 agent 任務跑在遠端 sandbox，並透過 gateway 回呼本機 API 時，用這個流程。它能驗證整條路徑，而且不依賴已連接的工具，也不碰私有的正式環境資料。

## 何時啟用

- 本機 agent API 需要做端到端的 runtime 檢查。
- 任務派送之後卡住，gateway 或 tunnel 可能連不到。
- Web app 暫時指向本機 API 來測試 agent。
- 先前的測試讓 web app 一直指向已經停掉的 API。

## 必要輸入

- 以 repo 相對路徑寫的啟動 API 和 web app 的說明。
- Gateway 的 route 路徑，以及它預期的匿名回應。
- 一個隔離的測試 agent、一個不需要工具的 prompt，以及它確切的預期答案。
- 能檢查任務狀態，並確認 callback 有打到本機 API 的方法。
- Provider 的憑證，透過專案正常的 secret store 提供。在共用文件裡只寫 provider 的名字，絕對不要把憑證的值複製進 skill 或測試報告。

如果缺少這些輸入，就回報缺了什麼，不要自己猜 endpoint，也不要用真實帳號。

## 授權與清理

先確認你有授權：透過選定的 tunnel provider 對外開放本機測試 API、派送測試任務，以及暫時修改 web app 的 route。要用隔離的本機 web app 或測試 deployment；不要在這個 smoke test 裡切換共用的正式環境 app。Tunnel 的存取範圍只開放必要的、有驗證的 route。

在修改 route 之前先裝好清理機制：不管成功、錯誤、逾時、中斷或取消，都要還原記下來的目標，並在停掉 API 和 tunnel 之前確認健康狀態。只追蹤這個測試建立的 process ID 或資源。如果還原失敗，要立刻回報，並保留復原所需的證據，不要宣稱成功。

## Smoke Test

1. **記錄並檢查原本的 route。** 記下 web app 目前的 API 目標，並確認它是健康的。把這個值留在本機，之後還原用。確認測試 agent 和資料跟真實使用者是隔離的。
2. **啟動本機 API 和 tunnel。** 用 process manager 讓兩者在整個測試期間都保持運作。驗證 API 健康。用匿名身分探測 gateway route，確認它回傳文件記載的驗證回應，通常是 `401` 或 `403`。確認這次探測有出現在本機 API 的 log；光有 edge 的回應，不能證明 API 真的被打到。
3. **兩項檢查都通過後，才切換 web app。** 驗證 web app 發出的請求會打到本機 API。web server 重啟或設定重新載入之後，要再檢查一次 route。
4. **跑一個不需要工具的任務。** 用一個短 prompt，並有確切的預期答案。確認遠端 sandbox 有呼叫本機 gateway、任務進入終止狀態，而且回傳的答案相符。排隊中或執行中的任務不算通過。
5. **還原原本的 route。** 把 web app 設回記錄下來的 API 目標，驗證那個目標和一個代表性頁面能載入，然後停掉測試 API 和 tunnel。如果還原失敗，要立刻回報 route 壞了。

檢查指令範例，其中的值由專案提供：

```sh
curl --silent --show-error --output /dev/null --write-out '%{http_code}\n' "$LOCAL_API_HEALTH_URL"
curl --silent --show-error --output /dev/null --write-out '%{http_code}\n' "$PUBLIC_GATEWAY_PROBE_URL"
```

第一個指令應該回傳專案定義的健康狀態。第二個應該回傳文件記載的匿名驗證狀態，**而且**要出現在本機 API 的 log 裡。兩個 URL 都不要放憑證。

## 已連接工具的後續測試

要等不需要工具的任務通過後，才另外跑這個測試。使用明確的測試連線和授權。「連線是否存在」和「授予了哪些動作」要當成兩件不同的事來回報。不要因為動作搜尋是空的，就推論沒有任何 app 連著。不要拿真實帳號執行寫入動作來當 smoke test。

## 失敗處理

| 觀察到的現象 | 下一步檢查 |
| --- | --- |
| 網頁能載入，但 API 請求失敗 | 比對設定的 API 目標和正在監聽的 process，並還原原本的 route。 |
| Gateway 探測得到連線錯誤或 `404` | 派送任務前，先檢查 tunnel 的存活時間、route 路徑和本機 API 的健康狀態。 |
| Gateway 探測得到 `401` 或 `403`，但本機 log 沒有紀錄 | 這個回應可能來自 tunnel 的 edge；驗證 callback 路徑。 |
| 任務一直排隊或執行中 | 檢查是不是被別的 dispatcher 認領了，以及 sandbox 有沒有連到本機 gateway。 |
| 任務結束但答案錯誤 | 擷取任務狀態和已遮蔽的錯誤；不要說 smoke test 成功。 |

## 輸出約定

回傳一份簡短報告，內容包含：

- 本機 API 是否健康：是或否
- Gateway 探測的狀態，以及本機 log 的確認
- 是否觀察到遠端 callback：是或否
- 不需要工具的任務的終止狀態，以及確切答案是否相符
- 原本的 web API route 是否已還原且健康：是或否
- 一個尚未解決的阻礙或下一步動作（如果有）

報告裡不要放帳號資料、憑證的值、個人路徑、公開的 tunnel URL 和原始的私有 log。原始的操作員筆記留在本機。

## 相關 Skill

- `hermes-imports`：分享前先把本機工作流程做去識別化。
- `agent-introspection-debugging`：agent 執行反覆失敗時用。
- `verification-loop`：修改 runtime 程式碼之後用。
