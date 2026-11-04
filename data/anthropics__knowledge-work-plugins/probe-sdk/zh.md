---
name: probe-sdk
description: "Zoom Probe SDK 的參考 skill。在導向某個預檢（preflight）工作流程之後，用於在使用者加入之前測試瀏覽器相容性、媒體權限、音訊或視訊診斷，以及網路就緒度時使用。"
user-invocable: false
triggers:
  - "probe sdk"
  - "zoom probe"
  - "@zoom/probesdk"
  - "media diagnostics"
  - "network diagnostic"
  - "preflight check"
  - "diagnose audio video"
  - "browser compatibility diagnostics"
  - "diagnostic report"
---

# Zoom Probe SDK

在會議或 session 工作流程之前，針對使用者裝置和網路做預檢診斷的背景參考。

官方文件：
- https://developers.zoom.us/docs/probe-sdk/
- https://marketplacefront.zoom.us/sdk/probe/index.html

參考範例：
- https://github.com/zoom/probesdk-web

## 導向護欄

- 當使用者需要的是 client 端診斷和就緒度評分（裝置／網路／瀏覽器能力），而不是加入會議／session 時，使用 Probe SDK。
- 如果使用者需要嵌入式會議流程，導向 [../meeting-sdk/SKILL.md](../meeting-sdk/SKILL.md)。
- 如果使用者需要自訂的即時 session UX，導向 [../video-sdk/SKILL.md](../video-sdk/SKILL.md)。
- 如果使用者需要事件／API 的後端編排，就串接 [../rivet-sdk/SKILL.md](../rivet-sdk/SKILL.md)、[../oauth/SKILL.md](../oauth/SKILL.md) 和 [../rest-api/SKILL.md](../rest-api/SKILL.md)。

## 快速連結

從這裡開始：
1. [probe-sdk.md](probe-sdk.md)
2. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
3. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
4. [examples/diagnostic-page-pattern.md](examples/diagnostic-page-pattern.md)
5. [examples/comprehensive-network-pattern.md](examples/comprehensive-network-pattern.md)
6. [references/probe-reference-map.md](references/probe-reference-map.md)
7. [references/environment-variables.md](references/environment-variables.md)
8. [references/versioning-and-compatibility.md](references/versioning-and-compatibility.md)
9. [references/samples-validation.md](references/samples-validation.md)
10. [references/source-map.md](references/source-map.md)
11. [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
12. [RUNBOOK.md](RUNBOOK.md)

## 常見的生命週期模式

1. 初始化 `Prober` / `Reporter`。
2. 請求媒體權限並列舉裝置。
3. 執行針對性的診斷（`diagnoseAudio`、`diagnoseVideo`）。
4. 執行完整的網路診斷（`startToDiagnose`），並把統計資料串流到 UI。
5. 產生最終報告並套用就緒度關卡。
6. 停止／清理（`stopToDiagnose`、`stopToDiagnoseVideo`、`releaseMediaStream`、`cleanup`）。

## 高層情境

- 在 Meeting SDK 加入動作之前的預先加入診斷頁面。
- 擷取結構化報告以便客戶疑難排解的客服工作流程。
- 給 kiosk 或受控端點環境的裝置認證流程。
- 針對進階媒體功能做瀏覽器能力把關。

詳情請見 [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)。

## 串接

- 會議預先加入的關卡：[../meeting-sdk/web/SKILL.md](../meeting-sdk/web/SKILL.md)
- 視訊 session 就緒度關卡：[../video-sdk/web/SKILL.md](../video-sdk/web/SKILL.md)
- 遙測／報告匯入後端：[../rivet-sdk/SKILL.md](../rivet-sdk/SKILL.md) + [../rest-api/SKILL.md](../rest-api/SKILL.md)

## 環境變數

- 選用的 `.env` key 以及如何取得這些值，請見 [references/environment-variables.md](references/environment-variables.md)。

## 營運

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘預檢與除錯檢查清單。
