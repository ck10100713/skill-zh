---
name: zoom-video-sdk-flutter
description: |
  給 Flutter 用的 Zoom Video SDK。用 flutter_zoom_videosdk 在 Flutter 裡建構自訂視訊 session app，
  並涉及事件驅動架構、session 生命週期處理和行動平台整合模式時使用。
user-invocable: false
triggers:
  - video sdk flutter
  - zoom flutter video sdk
  - flutter video session
  - flutter_zoom_videosdk
  - zoom custom video flutter
  - flutter live transcription zoom
---

# Zoom Video SDK (Flutter)

用 Zoom Video SDK 建構自訂即時視訊 session 體驗的 Flutter app，就用這個 skill。

## 快速連結

1. **[Lifecycle Workflow](concepts/lifecycle-workflow.md)** - init -> joinSession -> media/control -> leave -> cleanup
2. **[SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)** - 以 helper 為基礎的 API 介面和事件模型
3. **[High-Level Scenarios](concepts/high-level-scenarios.md)** - 常見的產品模式
4. **[Setup Guide](examples/setup-guide.md)** - 套件設定加上平台前置條件
5. **[Session Join Pattern](examples/session-join-pattern.md)** - 帶 token 的 session 加入流程
6. **[Event Handling Pattern](examples/event-handling-pattern.md)** - listener 對應和 action 路由
7. **[SKILL.md](SKILL.md)** - 完整導覽

## 核心備註

- Video SDK 的 session 是自訂 session，不是 Zoom Meetings。
- SDK 憑證要留在 server 端；在 backend 產生 JWT token。
- 整合高度依賴事件驅動；要及早綁定 listener 流程。
- 功能支援和 enum 名稱可能隨 wrapper／原生版本而漂移。

## 參考資料

- [Flutter Reference Index](references/flutter-reference.md)
- [Module Map](references/module-map.md)
- [Official Sources](references/official-sources.md)
- [Deprecated and Contradictions](troubleshooting/deprecated-and-contradictions.md)

## 相關 skill

- [zoom-video-sdk](../SKILL.md)
- [zoom-oauth](../../oauth/SKILL.md)
- [zoom-general](../../general/SKILL.md)


## 合併自 video-sdk/flutter/SKILL.md

# Zoom Video SDK Flutter - Documentation Index

## 從這裡開始

1. [SKILL.md](SKILL.md)
2. [Lifecycle Workflow](concepts/lifecycle-workflow.md)
3. [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)
4. [Setup Guide](examples/setup-guide.md)

## 概念

- [Lifecycle Workflow](concepts/lifecycle-workflow.md)
- [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)
- [High-Level Scenarios](concepts/high-level-scenarios.md)

## 範例

- [Setup Guide](examples/setup-guide.md)
- [Session Join Pattern](examples/session-join-pattern.md)
- [Event Handling Pattern](examples/event-handling-pattern.md)

## 參考資料

- [Flutter Reference Index](references/flutter-reference.md)
- [Module Map](references/module-map.md)
- [Official Sources](references/official-sources.md)

## 疑難排解

- [Common Issues](troubleshooting/common-issues.md)
- [Version Drift](troubleshooting/version-drift.md)
- [Deprecated and Contradictions](troubleshooting/deprecated-and-contradictions.md)

## 營運

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘的上線前檢查和除錯清單。
