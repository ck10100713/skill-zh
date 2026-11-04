---
name: zoom-meeting-sdk-electron
description: |
  給 Electron 桌面應用程式用的 Zoom Meeting SDK。當要透過 Node addon wrapper 在 Electron app 裡嵌入 Zoom 會議，
  並涉及 JWT auth、加入／開始會議流程、settings controller 和 raw data 整合時使用。
user-invocable: false
triggers:
  - electron meeting sdk
  - zoom meeting sdk electron
  - embed zoom in electron
  - electron zoom bot
  - zoom node addon
  - zoom raw data electron
---

# Zoom Meeting SDK (Electron)

建構 Electron 桌面 app，並透過 Electron wrapper 嵌入 Zoom Meeting SDK 功能時，就用這個 skill。

## 從這裡開始

1. **[Lifecycle Workflow](concepts/lifecycle-workflow.md)** - init -> auth -> join/start -> in-meeting -> cleanup
2. **[SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)** - Electron 裡的 service/controller/event 模型
3. **[Setup Guide](examples/setup-guide.md)** - 相依套件和 build 的預期
4. **[Authentication Pattern](examples/authentication-pattern.md)** - SDK JWT 產生和 auth callback
5. **[Join Meeting Pattern](examples/join-meeting-pattern.md)** - 開始／加入會議的執行流程
6. **[SKILL.md](SKILL.md)** - 完整導覽

## 核心備註

- Electron wrapper 是建構在原生 Meeting SDK 之上，透過 Node addon 橋接。
- SDK key/secret 要留在 server 端；在 backend 產生 SDK JWT。
- 各功能的支援程度隨平台／版本而異；實作前先查模組文件。
- Raw data 和 IPC 的做法在 production 需要明確的安全強化。

## 參考資料

- [Electron API Reference Index](references/electron-reference.md)
- [Module Map](references/module-map.md)
- [Deprecated and Contradictions](troubleshooting/deprecated-and-contradictions.md)

## 相關 skill

- [zoom-meeting-sdk](../SKILL.md)
- [zoom-oauth](../../oauth/SKILL.md)
- [zoom-general](../../general/SKILL.md)


## 合併自 meeting-sdk/electron/SKILL.md

# Zoom Meeting SDK Electron - Documentation Index

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
- [Authentication Pattern](examples/authentication-pattern.md)
- [Join Meeting Pattern](examples/join-meeting-pattern.md)
- [Raw Data Pattern](examples/raw-data-pattern.md)

## 參考資料

- [Electron API Reference](references/electron-reference.md)
- [Module Map](references/module-map.md)

## 疑難排解

- [Common Issues](troubleshooting/common-issues.md)
- [Version Drift](troubleshooting/version-drift.md)
- [Deprecated and Contradictions](troubleshooting/deprecated-and-contradictions.md)

## 營運

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘的上線前檢查和除錯清單。
