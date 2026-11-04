---
name: scribe
description: "Zoom AI Services Scribe 的參考 skill。在導向轉錄工作流程之後，處理上傳或已儲存的媒體、Build 平台 JWT 驗證、fast mode 轉錄、批次工作，或轉錄 pipeline 設計時使用。"
user-invocable: false
triggers:
  - "scribe"
  - "ai services scribe"
  - "zoom scribe"
  - "transcribe audio file"
  - "transcribe video file"
  - "batch transcription"
  - "fast mode transcription"
  - "build platform jwt"
---

# Zoom AI Services Scribe

Zoom AI Services Scribe 的背景參考，涵蓋：
- 同步的單一檔案轉錄（`POST /aiservices/scribe/transcribe`）
- 非同步的批次工作（`/aiservices/scribe/jobs*`）
- 透過重複上傳短檔案實現的瀏覽器麥克風偽串流
- 由 webhook 驅動的批次狀態更新
- Build 平台 JWT 的產生與憑證處理

官方文件：
- https://developers.zoom.us/docs/ai-services/
- https://developers.zoom.us/docs/ai-services/scribe/
- https://developers.zoom.us/docs/api/ai-services/
- https://developers.zoom.us/api-hub/ai-services/methods/endpoints.json
- Quickstart 範例：https://github.com/zoom/scribe-quickstart/

## 路由守則

- 如果使用者需要把**上傳或已儲存的媒體轉錄成文字**，先導向這裡。
- 如果使用者需要**即時會議媒體**，不走檔案上傳／批次工作，就導向 [../rtms/SKILL.md](../rtms/SKILL.md)。
- 如果使用者需要 AI Services 路徑的 **Zoom REST API 清單**，就串接 [../rest-api/SKILL.md](../rest-api/SKILL.md)。
- 如果使用者需要 webhook 簽章模式，或一般的 HMAC receiver 強化，可選擇性串接 [../webhooks/SKILL.md](../webhooks/SKILL.md)。

## 快速連結

1. [concepts/auth-and-processing-modes.md](concepts/auth-and-processing-modes.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [examples/fast-mode-node.md](examples/fast-mode-node.md)
4. [examples/batch-webhook-pipeline.md](examples/batch-webhook-pipeline.md)
5. [references/api-reference.md](references/api-reference.md)
6. [references/environment-variables.md](references/environment-variables.md)
7. [references/samples-validation.md](references/samples-validation.md)
8. [references/versioning-and-drift.md](references/versioning-and-drift.md)
9. [troubleshooting/common-drift-and-breaks.md](troubleshooting/common-drift-and-breaks.md)
10. [RUNBOOK.md](RUNBOOK.md)

## 核心工作流程

1. 取得 Build 平台憑證，並產生 HS256 JWT。
2. 單一短檔案選擇 **fast mode**，已儲存的封存檔／大量檔案選擇 **batch mode**。
3. 送出轉錄請求。
4. 批次工作的話，輪詢工作／檔案狀態，或接收 webhook 通知。
5. 持久化並後處理轉錄 JSON。

## 託管環境的 Fast-Mode 守則

- Fast-mode API 的正式限制是 `100 MB` 和 `2 hours`，但託管的瀏覽器流程仍可能在上游回應回來之前就逾時。
- 目前已部署範例的觀察結果：
  - 約 17.2 MB 的 MP4 在約 `26s` 內完成
  - 約 38.6 MB 的 MP4 在約 `26-37s` 內完成
  - 約 59.2 MB 的 MP4 在後端約 `32-34s` 內完成
  - 有些約 59.2 MB 的瀏覽器請求，前端仍然出現 `504`，但後端日誌之後顯示 `200`
- 把前端 `504` 加上後端 `200`，視為瀏覽器／邊緣節點的逾時競賽，不要自動當成轉錄失敗。
- 對託管的 UI，fast mode 優先用非同步 request／輪詢的包裝，而不是讓瀏覽器撐著等完整的上游回應。
- 對比較大或比較不可預測的媒體，就算檔案仍在 fast-mode 的正式大小限制內，也優先用 batch mode。

## 瀏覽器麥克風模式

- `scribe` 沒有公開文件記載的即時串流 API 介面。
- 如果想要瀏覽器麥克風的體驗，用偽串流：
  1. 把麥克風音訊切成短片段擷取
  2. 透過非同步的 fast-mode 包裝上傳每個片段
  3. 輪詢完成狀態
  4. 依序附加各片段的轉錄
- 建議的起始節奏：
  - 片段大小：`5 seconds`
  - 可接受範圍：`5-10 seconds`
  - 同時進行中的片段請求數：`2-3`
- 這是讓轉錄逐步更新的實用 UI 模式，不能取代 `rtms`。
- 把它當成備用的 demo 模式，不是首選的 production 架構。
- 它會增加重複上傳的開銷、片段邊界的漂移、瀏覽器 codec／容器格式的差異，以及轉錄拼接的複雜度。
- 如果使用者要的是真正的即時串流擷取、低延遲的連續媒體，或伺服器推送的媒體傳輸，就改導向 [../rtms/SKILL.md](../rtms/SKILL.md)。

## Endpoint 介面

| 模式 | Method | 路徑 | 用途 |
|------|--------|------|-----|
| Fast | `POST` | `/aiservices/scribe/transcribe` | 單一檔案的同步轉錄 |
| Batch | `POST` | `/aiservices/scribe/jobs` | 送出非同步批次工作 |
| Batch | `GET` | `/aiservices/scribe/jobs` | 列出工作 |
| Batch | `GET` | `/aiservices/scribe/jobs/{jobId}` | 檢視工作摘要／狀態 |
| Batch | `DELETE` | `/aiservices/scribe/jobs/{jobId}` | 取消排隊中／處理中的工作 |
| Batch | `GET` | `/aiservices/scribe/jobs/{jobId}/files` | 檢視每個檔案的結果 |

## 高階情境

- 使用者上傳一份錄音後，隨選的片段轉錄。
- 儲存在 S3 的通話封存檔的批次轉錄。
- 由 webhook 驅動、把轉錄寫入你的資料庫／搜尋索引的 ETL pipeline。
- 把 Zoom 管理的錄影匯出到你自己的儲存空間後，重新轉錄。
- 需要時間戳、聲道分離和說話者提示的離線法遵或品質檢查工作流程。

## 串接

- 已儲存的 Zoom 錄影 -> [../rest-api/SKILL.md](../rest-api/SKILL.md) + `scribe`
- Webhook 驗證強化 -> [../webhooks/SKILL.md](../webhooks/SKILL.md)
- 即時的逐字稿／媒體 -> [../rtms/SKILL.md](../rtms/SKILL.md)
- 跨產品路由 -> [../general/SKILL.md](../general/SKILL.md)

## 營運

- [RUNBOOK.md](RUNBOOK.md)：5 分鐘的 preflight 與除錯檢查表。
