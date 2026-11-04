---
name: meeting-sdk/linux
description: "Zoom Meeting SDK for Linux：C++ 無介面（headless）會議機器人，可存取原始音訊/視訊、做逐字稿、錄製，並整合 AI，用於伺服器端自動化"
user-invocable: false
triggers:
  - "linux meeting bot"
  - "headless zoom bot"
  - "meeting sdk linux"
  - "zoom raw recording linux"
  - "meeting transcription bot"
  - "zoom docker bot"
  - "pulseaudio zoom"
  - "meeting sdk raw data"
---

# Zoom Meeting SDK - Linux 開發

用 Zoom Meeting SDK 在 Linux 上打造無介面會議機器人的專家指引。這個 SDK 讓你能在伺服器端參加會議、擷取原始媒體、做逐字稿，以及用 AI 自動化會議。

## 如何打造自動加入並錄製的會議機器人

需求符合下列情況時，就使用這個 skill：
- 可見的機器人加入真實的 Zoom 會議
- 機器人自己錄製原始媒體
- 或是機器人在加入後觸發 Zoom 代管的雲端錄影流程

Skill 串接：
- 主要：`meeting-sdk/linux`
- 需要 OBF/ZAK 查詢、排程或雲端錄影設定時，加上 `zoom-rest-api`
- 需要在會後取得雲端錄影時，加上 `zoom-webhooks`

最精簡的原始錄製流程：

```cpp
JoinParam join_param;
join_param.userType = SDK_UT_WITHOUT_LOGIN;
auto& params = join_param.param.withoutloginuserJoin;
params.meetingNumber = meeting_number;
params.userName = "Recording Bot";
params.psw = meeting_password.c_str();
params.app_privilege_token = obf_token.c_str();

SDKError join_err = meeting_service->Join(join_param);
if (join_err != SDKERR_SUCCESS) {
    throw std::runtime_error("join_failed");
}

// 在 MEETING_STATUS_INMEETING 的 callback 裡：
auto* record_ctrl = meeting_service->GetMeetingRecordingController();
if (!record_ctrl) {
    throw std::runtime_error("recording_controller_unavailable");
}

if (record_ctrl->CanStartRawRecording() != SDKERR_SUCCESS) {
    throw std::runtime_error("raw_recording_not_permitted");
}

SDKError record_err = record_ctrl->StartRawRecording();
if (record_err != SDKERR_SUCCESS) {
    throw std::runtime_error("start_raw_recording_failed");
}

GetAudioRawdataHelper()->subscribe(new MyAudioDelegate());
```

當機器人必須自己掌握 PCM/YUV 媒體，或要直接餵給 AI pipeline 時，用**原始錄製**。  
當需求是會後取得 Zoom 代管的 MP4/M4A/逐字稿檔案時，用**雲端錄影加 webhooks**。

**官方文件**：https://developers.zoom.us/docs/meeting-sdk/linux/  
**API 參考**：https://marketplacefront.zoom.us/sdk/meeting/linux/  
**範例 Repo（原始錄製）**：https://github.com/zoom/meetingsdk-linux-raw-recording-sample  
**範例 Repo（無介面）**：https://github.com/zoom/meetingsdk-headless-linux-sample

## 快速連結

**剛接觸 Meeting SDK Linux？照這條路徑走：**

1. **[linux.md](linux.md)**：含完整流程的快速入門指南
2. **[concepts/high-level-scenarios.md](concepts/high-level-scenarios.md)**：可上線的機器人架構
3. **[meeting-sdk-bot.md](meeting-sdk-bot.md)**：附重試邏輯、耐用的機器人
4. **[references/linux-reference.md](references/linux-reference.md)**：相依套件、Docker、CMake

**常見使用情境：**
- **逐字稿機器人** → [high-level-scenarios.md#scenario-1-transcription-bot](concepts/high-level-scenarios.md)
- **錄製機器人** → [high-level-scenarios.md#scenario-2-recording-bot](concepts/high-level-scenarios.md)
- **AI 會議助理** → [high-level-scenarios.md#scenario-3-ai-meeting-assistant](concepts/high-level-scenarios.md)
- **品質監控** → [high-level-scenarios.md#scenario-4-monitoring-quality-bot](concepts/high-level-scenarios.md)
- **自動加入加錄製機器人** → [meeting-sdk-bot.md](meeting-sdk-bot.md)，有原始錄製的編排、重試，以及雲端錄影的交接

**遇到問題？**
- Docker 音訊問題 → [references/linux-reference.md#pulseaudio-setup](references/linux-reference.md)
- 原始錄製權限被拒 → [meeting-sdk-bot.md#raw-recording-permission-denied](meeting-sdk-bot.md)
- 建置錯誤 → [references/linux-reference.md#troubleshooting](references/linux-reference.md)

## 機器人的路由規則

如果使用者要求打造**自動加入 Zoom 會議並錄製**的機器人，從
[meeting-sdk-bot.md](meeting-sdk-bot.md) 開始。

- 用 **Meeting SDK Linux** 處理可見的參加者、加入流程和原始錄製控制。
- 當機器人必須取得 OBF/ZAK token、排程會議，或啟用帳號端的錄影設定時，串接 **zoom-rest-api**。
- 當需求是會議結束後取得 Zoom 雲端錄影時，串接 **zoom-webhooks**。

## SDK 概覽

Zoom Meeting SDK for Linux 是一個**針對無介面伺服器環境最佳化的 C++ 函式庫**：
- **無介面運作**：不需要 GUI，非常適合 Docker/雲端
- **原始資料存取**：YUV420 視訊、32kHz 的 PCM 音訊
- **GLib 事件迴圈**：非同步處理 callback 事件
- **Docker 就緒**：為 CentOS/Ubuntu 預先設定好的 Dockerfile
- **PulseAudio 整合**：為無介面環境提供虛擬音訊裝置

### 與 Video SDK 的主要差異

| 功能 | Meeting SDK (Linux) | Video SDK |
|---------|-------------------|-----------|
| **主要用途** | 以機器人身分加入既有會議 | 主持自訂的視訊 session |
| **可見性** | 可見的參加者 | Session 參加者 |
| **UI** | 無介面（沒有 UI） | 可選的自訂 UI |
| **驗證** | 外部會議需要 JWT 加 OBF/ZAK | 只要 JWT |
| **錄製控制** | 必須呼叫 `StartRawRecording()` | 直接存取原始資料 |
| **平台** | 僅限 Linux | Windows、macOS、iOS、Android |

## 前置需求

### 系統需求
- **OS**：Ubuntu 22+、CentOS 8/9、Oracle Linux 8
- **架構**：x86_64
- **編譯器**：支援 C++11 的 gcc/g++
- **建置工具**：cmake 3.16+

### 開發相依套件
```bash
# Ubuntu
apt-get install -y build-essential cmake \
    libx11-xcb1 libxcb-xfixes0 libxcb-shape0 libxcb-shm0 \
    libxcb-randr0 libxcb-image0 libxcb-keysyms1 libxcb-xtest0 \
    libglib2.0-dev libcurl4-openssl-dev pulseaudio

# CentOS
yum install -y cmake gcc gcc-c++ \
    libxcb-devel xcb-util-image xcb-util-keysyms \
    glib2-devel libcurl-devel pulseaudio
```

### 必要的憑證
1. **Zoom Meeting SDK App**（Client ID 和 Secret）→ [到 Marketplace 建立](https://marketplace.zoom.us/)
2. **JWT Token** → 用 Client ID/Secret 產生
3. **外部會議**：OBF token 或 ZAK token → [透過 REST API 取得](../references/bot-authentication.md)
4. **原始錄製**：會議錄製 Token（選填）→ [透過 API 取得](https://developers.zoom.us/docs/meeting-sdk/apis/#operation/meetingLocalRecordingJoinToken)

## 快速開始

### 1. 下載並解壓縮 SDK

```bash
# 從 https://marketplace.zoom.us/ 下載
tar xzf zoom-meeting-sdk-linux_x86_64-{version}.tar

# 整理檔案
mkdir -p demo/include/h demo/lib/zoom_meeting_sdk
cp -r h/* demo/include/h/
cp lib*.so demo/lib/zoom_meeting_sdk/
cp -r qt_libs demo/lib/zoom_meeting_sdk/
cp translation.json demo/lib/zoom_meeting_sdk/json/

# 建立必要的 symlink
cd demo/lib/zoom_meeting_sdk && ln -s libmeetingsdk.so libmeetingsdk.so.1
```

### 2. 初始化與驗證

```cpp
#include "zoom_sdk.h"

USING_ZOOM_SDK_NAMESPACE

// 初始化 SDK
InitParam init_params;
init_params.strWebDomain = "https://zoom.us";
init_params.enableLogByDefault = true;
init_params.rawdataOpts.audioRawDataMemoryMode = ZoomSDKRawDataMemoryModeHeap;
InitSDK(init_params);

// 用 JWT 驗證
AuthContext auth_ctx;
auth_ctx.jwt_token = your_jwt_token;
CreateAuthService(&auth_service);
auth_service->SDKAuth(auth_ctx);
```

### 3. 加入會議

```cpp
// 在 onAuthenticationReturn callback 裡
void onAuthenticationReturn(AuthResult ret) {
    if (ret == AUTHRET_SUCCESS) {
        JoinParam join_param;
        join_param.userType = SDK_UT_WITHOUT_LOGIN;
        
        auto& params = join_param.param.withoutloginuserJoin;
        params.meetingNumber = 1234567890;
        params.userName = "Bot";
        params.psw = "password";
        params.isVideoOff = true;
        params.isAudioOff = false;
        
        meeting_service->Join(join_param);
    }
}
```

### 4. 存取原始資料

```cpp
// 在 onMeetingStatusChanged callback 裡
void onMeetingStatusChanged(MeetingStatus status, int iResult) {
    if (status == MEETING_STATUS_INMEETING) {
        auto* record_ctrl = meeting_service->GetMeetingRecordingController();
        
        // 開始原始錄製（啟用原始資料存取）
        if (record_ctrl->CanStartRawRecording() == SDKERR_SUCCESS) {
            record_ctrl->StartRawRecording();
            
            // 訂閱音訊
            auto* audio_helper = GetAudioRawdataHelper();
            audio_helper->subscribe(new MyAudioDelegate());
            
            // 訂閱視訊
            IZoomSDKRenderer* video_renderer;
            createRenderer(&video_renderer, new MyVideoDelegate());
            video_renderer->setRawDataResolution(ZoomSDKResolution_720P);
            video_renderer->subscribe(user_id, RAW_DATA_TYPE_VIDEO);
        }
    }
}
```

## 主要功能

| 功能 | 說明 |
|---------|-------------|
| **無介面運作** | 沒有 GUI，非常適合 Docker/伺服器部署 |
| **原始音訊（PCM）** | 以 32kHz 擷取混合音訊或每位使用者的音訊 |
| **原始視訊（YUV420）** | 以連續的 planar 格式擷取視訊畫格 |
| **GLib 事件迴圈** | 非同步 callback 處理 |
| **Docker 支援** | 為 CentOS/Ubuntu 預先建好的 Dockerfile |
| **PulseAudio 虛擬裝置** | 無介面環境下的音訊 |
| **分組討論室** | 以程式管理分組討論室 |
| **聊天** | 傳送/接收會議中的聊天 |
| **錄製控制** | 本機、雲端和原始錄製 |

## 關鍵陷阱與最佳實務

### ⚠️ 關鍵：Docker/無介面環境要用 PulseAudio

**Docker 裡原始音訊的第一大問題：**

即使在無介面環境，原始音訊也需要 PulseAudio 和一個設定檔。

**解法**：
```bash
# 安裝 PulseAudio
apt-get install -y pulseaudio pulseaudio-utils

# 建立設定檔
mkdir -p ~/.config
cat > ~/.config/zoomus.conf << EOF
[General]
system.audio.type=default
EOF

# 啟動 PulseAudio 並建立虛擬裝置
pulseaudio --start --exit-idle-time=-1
pactl load-module module-null-sink sink_name=virtual_speaker
pactl load-module module-null-sink sink_name=virtual_mic
```

參見：[references/linux-reference.md#pulseaudio-setup](references/linux-reference.md)

### 需要原始錄製權限

跟 Video SDK 不同，Meeting SDK 需要明確的權限才能存取原始資料：

```cpp
// 一定要先呼叫 StartRawRecording()
auto* record_ctrl = meeting_service->GetMeetingRecordingController();

SDKError can_record = record_ctrl->CanStartRawRecording();
if (can_record == SDKERR_SUCCESS) {
    record_ctrl->StartRawRecording();
    // 現在可以訂閱音訊/視訊了
} else {
    // 需要：主持人/共同主持人身分，或是錄製 token
}
```

**取得權限的方式**：
1. 機器人是主持人/共同主持人
2. 主持人授予錄製權限
3. 使用 `recording_token` 參數（透過 [REST API](https://developers.zoom.us/docs/meeting-sdk/apis/#operation/meetingLocalRecordingJoinToken) 取得）
4. 加入時使用 `app_privilege_token`（OBF）

### 需要 GLib 主迴圈

SDK 的 callback 是透過 GLib 事件迴圈執行的：

```cpp
#include <glib.h>

// 設定主迴圈
GMainLoop* loop = g_main_loop_new(NULL, FALSE);

// 為週期性任務加上 timeout
g_timeout_add_seconds(10, check_meeting_status, NULL);

// 執行迴圈（會阻塞，直到結束）
g_main_loop_run(loop);
```

**沒有 GLib 迴圈時**：callback 永遠不會觸發，加入會議會無限期卡住。

### 建議使用 Heap 記憶體模式

原始資料一律用 heap 模式，避免大畫格造成 stack overflow：

```cpp
init_params.rawdataOpts.videoRawDataMemoryMode = ZoomSDKRawDataMemoryModeHeap;
init_params.rawdataOpts.shareRawDataMemoryMode = ZoomSDKRawDataMemoryModeHeap;
init_params.rawdataOpts.audioRawDataMemoryMode = ZoomSDKRawDataMemoryModeHeap;
```

### 執行緒安全

SDK 的 callback 在 SDK 的執行緒上執行：
- 不要在 callback 裡做繁重的操作
- 不要在 callback 內部呼叫 `CleanUPSDK()`
- 用執行緒安全的佇列傳遞資料
- 共用狀態要用 mutex

## 可上線的架構

### 逐字稿機器人

**參見**：[concepts/high-level-scenarios.md#scenario-1](concepts/high-level-scenarios.md)

```
Join Meeting → StartRawRecording → Subscribe Audio → 
Stream to AssemblyAI/Whisper → Generate Real-time Transcript
```

### 錄製機器人

**參見**：[concepts/high-level-scenarios.md#scenario-2](concepts/high-level-scenarios.md)

```
Join Meeting → StartRawRecording → Subscribe Audio+Video → 
Write YUV+PCM → FFmpeg Merge → Upload to Storage
```

### AI 會議助理

**參見**：[concepts/high-level-scenarios.md#scenario-3](concepts/high-level-scenarios.md)

```
Join Meeting → Real-time Transcription → AI Analysis → 
Extract Action Items → Generate Summary
```

## 範例應用程式

**官方 Repo**：

| 範例 | 說明 | 連結 |
|--------|-------------|------|
| **Raw Recording Sample** | 傳統 C++ 做法，使用 config.txt | [GitHub](https://github.com/zoom/meetingsdk-linux-raw-recording-sample) |
| **Headless Sample** | 現代的 TOML 設定，附 CLI 和 Docker Compose | [GitHub](https://github.com/zoom/meetingsdk-headless-linux-sample) |

**各自示範什麼**：

- **Raw Recording Sample**：完整的原始資料流程、PulseAudio 設定、Docker 多發行版支援
- **Headless Sample**：AssemblyAI 整合、Anthropic AI、可上線的設定管理

## 文件庫

### 核心概念
- **[linux.md](linux.md)**：快速入門與核心流程
- **[concepts/high-level-scenarios.md](concepts/high-level-scenarios.md)**：可上線的機器人架構
- **[meeting-sdk-bot.md](meeting-sdk-bot.md)**：附重試邏輯、耐用的機器人

### 平台參考
- **[references/linux-reference.md](references/linux-reference.md)**：相依套件、CMake、Docker、疑難排解

### 驗證
- **[../references/authorization.md](../references/authorization.md)**：SDK JWT 的產生
- **[../references/bot-authentication.md](../references/bot-authentication.md)**：機器人的 token 類型（ZAK、OBF、JWT）

### 進階功能
- **[../references/breakout-rooms.md](../references/breakout-rooms.md)**：以程式管理分組討論室
- **[../references/ai-companion.md](../references/ai-companion.md)**：AI Companion 控制

## 常見問題

| 問題 | 原因 | 解法 |
|-------|-------|----------|
| **Docker 裡沒有音訊** | 缺少 PulseAudio 設定 | 建立 `~/.config/zoomus.conf` |
| **原始錄製被拒** | 沒有權限 | 用主持人/共同主持人身分，或是錄製 token |
| **Callback 沒有觸發** | 缺少 GLib 主迴圈 | 加上 `g_main_loop_run()` |
| **建置錯誤（XCB）** | 缺少 X11 函式庫 | 安裝 libxcb 套件 |
| **驗證時 segfault** | OpenSSL 版本不符 | 安裝 libssl1.1 |

**完整的疑難排解**：[references/linux-reference.md#troubleshooting](references/linux-reference.md)

## 資源

- **官方文件**：https://developers.zoom.us/docs/meeting-sdk/linux/
- **API 參考**：https://marketplacefront.zoom.us/sdk/meeting/linux/
- **開發者論壇**：https://devforum.zoom.us/
- **GitHub 範例**： 
  - https://github.com/zoom/meetingsdk-linux-raw-recording-sample
  - https://github.com/zoom/meetingsdk-headless-linux-sample

---

**需要協助？** 先看 [linux.md](linux.md) 的快速入門，再看 [high-level-scenarios.md](concepts/high-level-scenarios.md) 了解可上線的模式。

## 營運

- [RUNBOOK.md](RUNBOOK.md)：5 分鐘的事前檢查和除錯檢查清單。
