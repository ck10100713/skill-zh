---
name: zoom-meeting-sdk-react-native
description: 給 React Native 用的 Zoom Meeting SDK。在 React Native iOS/Android app 中使用 @zoom/meetingsdk-react-native 嵌入 Zoom 會議、JWT 驗證、加入／開始流程、平台設定和 native bridge 疑難排解時使用。
user-invocable: false
triggers:
  - react native meeting sdk
  - zoom react native
  - meetingsdk-react-native
  - join meeting in react native
  - start meeting with zak
  - zoom mobile sdk wrapper
---

# Zoom Meeting SDK（React Native）

在建置需要嵌入式 Zoom 會議加入／開始流程的 React Native app 時使用這個 skill。

## 快速連結

1. **[生命週期工作流程](concepts/lifecycle-workflow.md)** - init -> auth -> join/start -> in-meeting -> cleanup
2. **[架構](concepts/architecture.md)** - JS wrapper、native bridge、iOS/Android SDK 各層
3. **[高層情境](concepts/high-level-scenarios.md)** - 實用的產品模式
4. **[設定指南](examples/setup-guide.md)** - 安裝套件加平台需求
5. **[加入會議模式](examples/join-meeting-pattern.md)** - JWT + meetingNumber + password
6. **[開始會議模式](examples/start-meeting-pattern.md)** - 以 ZAK 為基礎的主持人開始流程
7. **[SKILL.md](SKILL.md)** - 完整導覽

## 核心 API（Wrapper）

來自 `@zoom/meetingsdk-react-native` wrapper 的介面：

- `initSDK(config)`
- `isInitialized()`
- `updateMeetingSetting(config)`
- `joinMeeting(config)`
- `startMeeting(config)`
- `cleanup()`

參見：**[Wrapper API](references/wrapper-api.md)**

## 重要備註

- 你仍然需要設定好 native iOS/Android Meeting SDK 的相依套件。
- `joinMeeting` 和 `startMeeting` 會回傳來自 native 層的數字狀態／錯誤碼。
- 主持人開始流程要傳入 `zoomAccessToken`（ZAK）。
- JWT 的產生要留在後端，絕對不要把 SDK secret 嵌進 app。
- 目前的文件指出 React Native 支援到 `0.75.4`；不支援 Expo。

## 平台指南

- **[iOS 設定](references/ios-setup.md)** - Podfile、選用的 ReplayKit／app group 欄位
- **[Android 設定](references/android-setup.md)** - Gradle 相依套件加選項對應
- **[Native Bridge 備註](references/native-bridge-notes.md)** - 行為差異和陷阱

## 疑難排解

- **[常見問題](troubleshooting/common-issues.md)**
- **[版本漂移](troubleshooting/version-drift.md)**
- **[已棄用／矛盾之處](troubleshooting/deprecated-and-contradictions.md)**

## 相關 Skill

- **[zoom-meeting-sdk](../SKILL.md)** - 上層的 Meeting SDK 總覽
- **[zoom-oauth](../../oauth/SKILL.md)** - 驗證流程與 token 管理
- **[zoom-general](../../general/SKILL.md)** - 跨產品的架構決策

## 文件索引

### 從這裡開始

1. [SKILL.md](SKILL.md)
2. [生命週期工作流程](concepts/lifecycle-workflow.md)
3. [架構](concepts/architecture.md)
4. [設定指南](examples/setup-guide.md)

### 概念

- [生命週期工作流程](concepts/lifecycle-workflow.md)
- [架構](concepts/architecture.md)
- [驗證與 Token 模型](concepts/auth-and-token-model.md)
- [高層情境](concepts/high-level-scenarios.md)

### 範例

- [設定指南](examples/setup-guide.md)
- [加入會議模式](examples/join-meeting-pattern.md)
- [開始會議模式](examples/start-meeting-pattern.md)
- [Provider Hook 模式](examples/provider-hook-pattern.md)

### 參考資料

- [Wrapper API](references/wrapper-api.md)
- [Android 設定](references/android-setup.md)
- [iOS 設定](references/ios-setup.md)
- [Native Bridge 備註](references/native-bridge-notes.md)
- [官方來源](references/official-sources.md)

### 疑難排解

- [常見問題](troubleshooting/common-issues.md)
- [版本漂移](troubleshooting/version-drift.md)
- [已棄用與矛盾之處](troubleshooting/deprecated-and-contradictions.md)

## 營運

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘預檢與除錯檢查清單。
