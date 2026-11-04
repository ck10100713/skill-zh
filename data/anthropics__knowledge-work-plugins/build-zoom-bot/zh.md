---
name: build-zoom-bot
description: 建置 Zoom 會議機器人、錄製工具或即時媒體工作流程。當要用程式加入會議、處理即時媒體或逐字稿，或結合 Meeting SDK、RTMS 和後端服務時使用。
---

# /build-zoom-bot

這個 skill 用在加入會議、擷取媒體或回應即時 session 資料的自動化。

## 涵蓋範圍

- Bot 架構
- 會議加入策略
- 即時媒體與逐字稿處理
- 後端協調
- 儲存、後處理與事件流程設計

## 工作流程

1. 先釐清這個 bot 需要加入、觀察、轉錄、摘要，還是採取行動。
2. 以 Meeting SDK 和 RTMS 作為核心實作路徑來導向。
3. 需要時，加上 REST API 做會議與資源管理，加上 Webhooks 處理非同步事件。
4. 及早點出環境和生命週期的限制。

## 主要參考

- [meeting-sdk](../meeting-sdk/SKILL.md)
- [rtms](../rtms/SKILL.md)
- [scribe](../scribe/SKILL.md)
- [rest-api](../rest-api/SKILL.md)
- [webhooks](../webhooks/SKILL.md)

## 常見錯誤

- 把批次轉錄和即時媒體當成同一種工作流程
- 在定義加入權限和驗證模型之前就先設計 bot
- 忘了會後儲存和重試行為
