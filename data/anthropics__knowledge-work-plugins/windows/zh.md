---
name: zoom-meeting-sdk-windows
description: |
  Zoom Meeting SDK for Windows：原生 C++ SDK，用來把 Zoom 會議嵌入 Windows 桌面應用程式。
  支援自訂 UI 架構、raw video/audio 資料、無介面（headless）bot，以及和會議功能的深度整合。
  內含 SDK 架構模式和 Windows message loop 的處理方式。
user-invocable: false
triggers:
  - "meeting sdk windows"
  - "windows meeting sdk"
  - "windows meeting bot"
  - "c++ meeting sdk windows"
  - "custom ui meeting windows"
---

# Zoom Meeting SDK（Windows）

把 Zoom 的會議能力嵌入 Windows 桌面應用程式，用於原生 C++ 整合和無介面 bot。

## 剛接觸 Zoom SDK？從這裡開始！

**最快掌握 SDK 的方法：**

1. **[SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)** - 學會適用於全部 35 個以上功能的通用模式
2. **[Authentication Pattern](examples/authentication-pattern.md)** - 讓 bot 能實際加入會議
3. **[Windows Message Loop](troubleshooting/windows-message-loop.md)** - 解決 callback 不觸發的第一大原因

**要建立自訂 UI？**
- [Custom UI Architecture](concepts/custom-ui-architecture.md) - SDK 渲染實際上是怎麼運作的（子 HWND、D3D 等）
- [Custom UI Video Rendering Example](examples/custom-ui-video-rendering.md) - 完整的可運作程式碼
- [SDK-Rendered vs Self-Rendered](concepts/custom-ui-vs-raw-data.md) - 選對做法
- [Custom UI Interface Methods](references/interface-methods.md) - 全部 13 個必要的虛擬方法

**遇到問題？**
- 建置錯誤 → [Build Errors Guide](troubleshooting/build-errors.md)
- Callback 不觸發 → [Windows Message Loop](troubleshooting/windows-message-loop.md)
- 快速診斷 → [Common Issues](troubleshooting/common-issues.md)
- 效能 / 服務品質 → [service-quality.md](examples/service-quality.md)
- 部署備註 → [deployment.md](references/deployment.md)
- 在 git bash 裡跑 MSBuild → [Build Errors Guide](troubleshooting/build-errors.md#msbuild-command-pattern)
- 完整導覽 → [SKILL.md](SKILL.md)

## 前置條件

- 有 Meeting SDK 憑證（Client ID 和 Secret）的 Zoom app
- Visual Studio 2019/2022 或更新版本
- Windows 10 或更新版本
- C++ 開發環境
- 用 vcpkg 管理相依套件

> **驗證需要協助嗎？** 產生 JWT token 的方式，見 **[zoom-oauth](../../oauth/SKILL.md)** skill。

## 專案偏好與心得

> **重要**：這些是從真實專案經驗中換來的偏好。建立新專案時要照著做。

### 不要用 CMake：用原生的 Visual Studio `.vcxproj`

**一律建立原生的 Visual Studio `.sln` + `.vcxproj` 專案**，不要建 CMake 專案。理由：
- 對 Windows C++ 開發者來說更標準、更熟悉
- 開發者雙擊 `.sln` 就能立刻在 Visual Studio 中開啟
- 專案設定（include 目錄、lib 目錄、前置處理器定義）在 VS 的 Property Pages UI 裡更容易看到和編輯
- 不需要額外的 CMake 工具或設定步驟
- 對開發者更友善，也更容易理解和維護

### `config.json` 必須在 Solution Explorer 中看得到

`config.json` 檔案（包含 `sdk_jwt`、`meeting_number`、`passcode`）必須：
1. **加進 `.vcxproj`**，做成 `<None>` 項目，並設 `<CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>`
2. **放在 `.vcxproj.filters` 檔案的「Config」filter 裡**，讓它出現在 Solution Explorer 的「Config」資料夾下
3. **讓開發者能直接在 Solution Explorer 輕鬆編輯**：他們絕對不用跑到 File Explorer 去找它

`.vcxproj` 項目的範例：
```xml
<ItemGroup>
  <None Include="config.json">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </None>
</ItemGroup>
```

`.vcxproj.filters` 項目的範例：
```xml
<ItemGroup>
  <Filter Include="Config">
    <UniqueIdentifier>{GUID-HERE}</UniqueIdentifier>
  </Filter>
</ItemGroup>
<ItemGroup>
  <None Include="config.json">
    <Filter>Config</Filter>
  </None>
</ItemGroup>
```

## 概覽

Windows SDK 是**原生 C++ SDK**，設計用於：
- **桌面應用程式**：可完全控制 UI 的原生 Windows app
- **無介面 bot**：不需要 UI 就能加入會議
- **Raw media 存取**：擷取/送出音訊和視訊串流
- **本機錄製**：把會議錄在本機或雲端

### 關鍵的架構洞察

SDK 對每個功能都遵循**通用的 3 步驟模式**：
1. **取得 controller**（singleton）：`meetingService->Get[Feature]Controller()`
2. **實作事件 listener**：`class MyListener : public I[Feature]Event { ... }`
3. **註冊並使用**：`controller->SetEvent(listener)`，然後呼叫方法

**這適用於所有功能**：音訊、視訊、聊天、錄製、參與者、螢幕分享、分組討論室、webinar、Q&A、投票、白板，以及另外 20 個以上！

了解更多：**[SDK Architecture Pattern Guide](concepts/sdk-architecture-pattern.md)**

## 快速開始

### 1. 下載 Windows SDK

從 [Zoom Marketplace](https://marketplace.zoom.us/) 下載：
- 解壓縮 `zoom-meeting-sdk-windows_x86_64-{version}.zip`

### 2. 設定專案結構

```
your-project/
  YourApp/
    SDK/
      x64/
        bin/          # DLL files and dependencies
        h/            # Header files
        lib/          # sdk.lib
      x86/
        bin/
        h/
        lib/
    YourApp.cpp
    YourApp.vcxproj
    config.json
```

複製 SDK 檔案：
```cmd
xcopy /E /I sdk-package\x64 your-project\YourApp\SDK\x64\
xcopy /E /I sdk-package\x86 your-project\YourApp\SDK\x86\
```

### 3. 安裝相依套件（vcpkg）

```powershell
# 安裝 vcpkg
git clone https://github.com/Microsoft/vcpkg.git C:\vcpkg
cd C:\vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg integrate install

# 安裝相依套件
.\vcpkg install jsoncpp:x64-windows
.\vcpkg install curl:x64-windows
```

### 4. 設定 Visual Studio 專案

**Project Properties → C/C++ → General → Additional Include Directories：**
```
$(SolutionDir)SDK\$(PlatformTarget)\h
C:\vcpkg\packages\jsoncpp_x64-windows\include
C:\vcpkg\packages\curl_x64-windows\include
```

**Project Properties → Linker → General → Additional Library Directories：**
```
$(SolutionDir)SDK\$(PlatformTarget)\lib
```

**Project Properties → Linker → Input → Additional Dependencies：**
```
sdk.lib
```

**Post-Build Event**（把 DLL 複製到輸出目錄）：
```cmd
xcopy /Y /D "$(SolutionDir)SDK\$(PlatformTarget)\bin\*.*" "$(OutDir)"
```

### 5. 設定憑證

建立 `config.json`：
```json
{
  "sdk_jwt": "YOUR_JWT_TOKEN",
  "meeting_number": "1234567890",
  "passcode": "password123",
  "zak": ""
}
```

### 6. 建置並執行

- 在 Visual Studio 中開啟 solution
- 選擇 x64 或 x86 設定
- 按 F5 建置並執行

## 核心工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  InitSDK    │───►│  AuthSDK    │───►│ JoinMeeting │───►│ Raw Data    │
│             │    │  (JWT)      │    │             │    │ Subscribe   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                         │                   │
                         ▼                   ▼
                   OnAuthComplete      onInMeeting
                     callback           callback
```

**⚠️ 非常重要**：要加上 Windows message loop，不然 callback 不會觸發！
```cpp
while (!done) {
    MSG msg;
    while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
}
```
參閱：[Windows Message Loop Guide](troubleshooting/windows-message-loop.md)

## 程式碼範例

> **💡 小撇步**：這些是最精簡的範例。完整、測試過的程式碼請見：
> - [Authentication Pattern](examples/authentication-pattern.md) - 完整的驗證工作流程
> - [Raw Video Capture](examples/raw-video-capture.md) - 完整的視訊擷取
> - [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md) - 實作任何功能

### 重要：Include 順序

**非常重要**：header 一定要照這個確切的順序 include，不然會有建置錯誤：

```cpp
#include <windows.h>      // MUST be first
#include <cstdint>         // MUST be second (SDK headers use uint32_t)
// ... other standard headers ...
#include <zoom_sdk.h>
#include <meeting_service_components/meeting_audio_interface.h>  // BEFORE participants!
#include <meeting_service_components/meeting_participants_ctrl_interface.h>
```

參閱：[Build Errors Guide](troubleshooting/build-errors.md)，取得所有相依問題的修正方式。

### 1. 初始化 SDK

```cpp
#include <windows.h>
#include <cstdint>
#include <zoom_sdk.h>

using namespace ZOOM_SDK_NAMESPACE;

bool InitMeetingSDK() {
    InitParam initParam;
    initParam.strWebDomain = L"https://zoom.us";
    initParam.strSupportUrl = L"https://zoom.us";
    initParam.emLanguageID = LANGUAGE_English;
    initParam.enableLogByDefault = true;
    initParam.enableGenerateDump = true;
    
    SDKError err = InitSDK(initParam);
    if (err != SDKERR_SUCCESS) {
        std::wcout << L"InitSDK failed: " << err << std::endl;
        return false;
    }
    return true;
}
```

### 2. 用 JWT 驗證

```cpp
#include <windows.h>
#include <cstdint>
#include <auth_service_interface.h>
#include "AuthServiceEventListener.h"

IAuthService* authService = nullptr;

void OnAuthenticationComplete() {
    std::cout << "Authentication successful!" << std::endl;
    JoinMeeting();  // 接著加入會議
}

bool AuthenticateSDK(const std::wstring& jwtToken) {
    CreateAuthService(&authService);
    if (!authService) return false;
    
    // 在呼叫 SDKAuth 之前先設定事件 listener
    authService->SetEvent(new AuthServiceEventListener(&OnAuthenticationComplete));
    
    // 用 JWT 驗證
    AuthContext authContext;
    authContext.jwt_token = jwtToken.c_str();
    
    SDKError err = authService->SDKAuth(authContext);
    if (err != SDKERR_SUCCESS) {
        std::wcout << L"SDKAuth failed: " << err << std::endl;
        return false;
    }
    
    // 非常重要：要加上 message loop，不然 callback 不會觸發！
    // 完整範例見：examples/authentication-pattern.md
    
    return true;
}
```

**AuthServiceEventListener.h：**
```cpp
#include <windows.h>
#include <cstdint>
#include <auth_service_interface.h>
#include <iostream>

using namespace ZOOM_SDK_NAMESPACE;

class AuthServiceEventListener : public IAuthServiceEvent {
public:
    AuthServiceEventListener(void (*onComplete)()) 
        : onAuthComplete(onComplete) {}
    
    void onAuthenticationReturn(AuthResult ret) override {
        if (ret == AUTHRET_SUCCESS && onAuthComplete) {
            onAuthComplete();
        } else {
            std::cout << "Auth failed: " << ret << std::endl;
        }
    }
    
    // 必須實作「所有」純虛擬方法（共 6 個）
    void onLoginReturnWithReason(LOGINSTATUS ret, IAccountInfo* info, LoginFailReason reason) override {}
    void onLogout() override {}
    void onZoomIdentityExpired() override {}
    void onZoomAuthIdentityExpired() override {}
#if defined(WIN32)
    void onNotificationServiceStatus(SDKNotificationServiceStatus status, SDKNotificationServiceError error) override {}
#endif

private:
    void (*onAuthComplete)();
};
```

**完整的可運作程式碼見**：[Authentication Pattern Guide](examples/authentication-pattern.md)

### 3. 加入會議

```cpp
#include <meeting_service_interface.h>
#include "MeetingServiceEventListener.h"

IMeetingService* meetingService = nullptr;

void OnMeetingJoined() {
    std::cout << "Joining meeting..." << std::endl;
}

void OnInMeeting() {
    std::cout << "In meeting now!" << std::endl;
    // 在這裡開始擷取 raw data
}

void OnMeetingEnds() {
    std::cout << "Meeting ended" << std::endl;
}

bool JoinMeeting(UINT64 meetingNumber, const std::wstring& password) {
    CreateMeetingService(&meetingService);
    if (!meetingService) return false;
    
    // 設定事件 listener
    meetingService->SetEvent(
        new MeetingServiceEventListener(&OnMeetingJoined, &OnMeetingEnds, &OnInMeeting)
    );
    
    // 準備加入參數
    JoinParam joinParam;
    joinParam.userType = SDK_UT_WITHOUT_LOGIN;
    
    JoinParam4WithoutLogin& params = joinParam.param.withoutloginuserJoin;
    params.meetingNumber = meetingNumber;
    params.userName = L"Bot User";
    params.psw = password.c_str();
    params.isVideoOff = false;
    params.isAudioOff = false;
    
    SDKError err = meetingService->Join(joinParam);
    if (err != SDKERR_SUCCESS) {
        std::wcout << L"Join failed: " << err << std::endl;
        return false;
    }
    return true;
}
```

**MeetingServiceEventListener.h：**
```cpp
#include <windows.h>
#include <cstdint>
#include <meeting_service_interface.h>
#include <iostream>

using namespace ZOOM_SDK_NAMESPACE;

class MeetingServiceEventListener : public IMeetingServiceEvent {
public:
    MeetingServiceEventListener(
        void (*onJoined)(),
        void (*onEnded)(), 
        void (*onInMeeting)()
    ) : onMeetingJoined(onJoined), 
        onMeetingEnded(onEnded),
        onInMeetingCallback(onInMeeting) {}
    
    void onMeetingStatusChanged(MeetingStatus status, int iResult) override {
        if (status == MEETING_STATUS_CONNECTING) {
            if (onMeetingJoined) onMeetingJoined();
        }
        else if (status == MEETING_STATUS_INMEETING) {
            if (onInMeetingCallback) onInMeetingCallback();
        }
        else if (status == MEETING_STATUS_ENDED) {
            if (onMeetingEnded) onMeetingEnded();
        }
    }
    
    // 必須實作「所有」純虛擬方法（共 9 個）
    void onMeetingStatisticsWarningNotification(StatisticsWarningType type) override {}
    void onMeetingParameterNotification(const MeetingParameter* param) override {}
    void onSuspendParticipantsActivities() override {}
    void onAICompanionActiveChangeNotice(bool isActive) override {}
    void onMeetingTopicChanged(const zchar_t* sTopic) override {}
    void onMeetingFullToWatchLiveStream(const zchar_t* sLiveStreamUrl) override {}
    void onUserNetworkStatusChanged(MeetingComponentType type, ConnectionQuality level, unsigned int userId, bool uplink) override {}
#if defined(WIN32)
    void onAppSignalPanelUpdated(IMeetingAppSignalHandler* pHandler) override {}
#endif

private:
    void (*onMeetingJoined)();
    void (*onMeetingEnded)();
    void (*onInMeetingCallback)();
};
```

**所有必要方法見**：[Interface Methods Guide](references/interface-methods.md)

### 4. 訂閱 Raw Video

```cpp
#include <windows.h>
#include <cstdint>
#include <rawdata/zoom_rawdata_api.h>
#include <rawdata/rawdata_renderer_interface.h>
#include <zoom_sdk_raw_data_def.h>  // REQUIRED for YUVRawDataI420
#include "ZoomSDKRendererDelegate.h"

IZoomSDKRenderer* videoHelper = nullptr;
ZoomSDKRendererDelegate* videoSource = new ZoomSDKRendererDelegate();

bool StartVideoCapture(uint32_t userId) {
    // 步驟 1：「先」開始 raw recording（必要！）
    IMeetingRecordingController* recordCtrl = 
        meetingService->GetMeetingRecordingController();
    
    SDKError canStart = recordCtrl->CanStartRawRecording();
    if (canStart != SDKERR_SUCCESS) {
        std::cout << "Cannot start recording: " << canStart << std::endl;
        return false;
    }
    
    recordCtrl->StartRawRecording();
    
    // 等待錄製初始化
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    
    // 步驟 2：建立 renderer
    SDKError err = createRenderer(&videoHelper, videoSource);
    if (err != SDKERR_SUCCESS || !videoHelper) {
        std::cout << "createRenderer failed: " << err << std::endl;
        return false;
    }
    
    // 步驟 3：設定解析度並訂閱
    videoHelper->setRawDataResolution(ZoomSDKResolution_720P);
    err = videoHelper->subscribe(userId, RAW_DATA_TYPE_VIDEO);
    if (err != SDKERR_SUCCESS) {
        std::cout << "Subscribe failed: " << err << std::endl;
        return false;
    }
    
    std::cout << "Video capture started! Frames arrive in onRawDataFrameReceived()" << std::endl;
    return true;
}
```

**ZoomSDKRendererDelegate.h：**
```cpp
#include <windows.h>
#include <cstdint>
#include <rawdata/rawdata_renderer_interface.h>
#include <zoom_sdk_raw_data_def.h>
#include <fstream>
#include <iostream>

using namespace ZOOM_SDK_NAMESPACE;

class ZoomSDKRendererDelegate : public IZoomSDKRendererDelegate {
public:
    void onRawDataFrameReceived(YUVRawDataI420* data) override {
        if (!data) return;
        
        // YUV420 (I420) 格式：Y plane + U plane + V plane
        int width = data->GetStreamWidth();
        int height = data->GetStreamHeight();
        
        // 計算 buffer 大小
        // Y = 完整解析度，U/V = 各為四分之一解析度
        size_t ySize = width * height;
        size_t uvSize = ySize / 4;  // (width/2) * (height/2)
        
        // 總大小：width * height * 1.5 bytes
        
        // 存成檔案（播放：ffplay -f rawvideo -pixel_format yuv420p -video_size 1280x720 output.yuv）
        std::ofstream outputFile("output.yuv", std::ios::binary | std::ios::app);
        outputFile.write(data->GetYBuffer(), ySize);    // 亮度
        outputFile.write(data->GetUBuffer(), uvSize);   // 藍色差
        outputFile.write(data->GetVBuffer(), uvSize);   // 紅色差
        outputFile.close();
    }
    
    void onRawDataStatusChanged(RawDataStatus status) override {
        std::cout << "Raw data status: " << status << std::endl;
    }
    
    void onRendererBeDestroyed() override {
        std::cout << "Renderer destroyed" << std::endl;
    }
};
```

**完整的視訊擷取指南**：[Raw Video Capture Guide](examples/raw-video-capture.md)

### 5. 訂閱 Raw Audio

```cpp
#include <rawdata/rawdata_audio_helper_interface.h>

class ZoomSDKAudioRawDataDelegate : public IZoomSDKAudioRawDataDelegate {
public:
    void onMixedAudioRawDataReceived(AudioRawData* data) override {
        // 處理 PCM 音訊（所有參與者混合在一起）
        std::ofstream pcmFile("audio.pcm", std::ios::binary | std::ios::app);
        pcmFile.write((char*)data->GetBuffer(), data->GetBufferLen());
        pcmFile.close();
    }
    
    void onOneWayAudioRawDataReceived(AudioRawData* data, uint32_t node_id) override {
        // 處理特定參與者的音訊
    }
};

// 訂閱音訊
IZoomSDKAudioRawDataHelper* audioHelper = GetAudioRawdataHelper();
audioHelper->subscribe(new ZoomSDKAudioRawDataDelegate());
```

### 6. 主要的 Message Loop（非常重要！）

**⚠️ 沒有這個，CALLBACK 就不會觸發！**

```cpp
#include <windows.h>
#include <thread>
#include <chrono>

int main() {
    // 初始化 COM
    CoInitialize(NULL);
    
    // 載入設定並初始化
    LoadConfig();
    InitMeetingSDK();
    AuthenticateSDK(sdk_jwt);
    
    // 非常重要：給 SDK callback 用的 Windows message loop
    // SDK 用 Windows message pump 來分派 callback
    // 沒有它的話，callback 會排進佇列，但「永遠」不會觸發！
    MSG msg;
    while (!g_exit) {
        // 處理所有待處理的 Windows 訊息
        while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
            if (msg.message == WM_QUIT) {
                g_exit = true;
                break;
            }
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
        
        // 短暫 sleep，避免 busy-waiting
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    // 清理
    CleanSDK();
    CoUninitialize();
    
    return 0;
}
```

**為什麼 message loop 這麼重要**：SDK 用 Windows COM/messaging 處理非同步 callback。沒有 `PeekMessage()` 的話，SDK 會把訊息排進佇列，但永遠不會被取出或分派，所以 callback 永遠不會執行。

**沒有 message loop 時的症狀**：
- 驗證逾時（即使 JWT 有效）
- 加入會議逾時
- 完全沒有 callback 事件觸發
- 看起來像網路/驗證問題，其實是 message loop 的問題

**詳細說明見**：[Windows Message Loop Guide](troubleshooting/windows-message-loop.md)

## 常見問題與解法

| 問題 | 解法 |
|-------|----------|
| **Callback 不觸發 / 驗證逾時** | 加上 Windows message loop → [指南](troubleshooting/windows-message-loop.md) |
| **`uint32_t` / `AudioType` 錯誤** | 修正 include 順序 → [指南](troubleshooting/build-errors.md) |
| **Abstract class 錯誤** | 實作所有虛擬方法 → [指南](references/interface-methods.md) |
| **怎麼實作 [功能]？** | 照通用模式做 → [指南](concepts/sdk-architecture-pattern.md) |
| **驗證失敗** | 檢查 JWT token 與錯誤碼 → [指南](troubleshooting/common-issues.md) |
| **收不到視訊 frame** | 先呼叫 StartRawRecording() → [指南](examples/raw-video-capture.md) |

**完整的疑難排解**：[Common Issues Guide](troubleshooting/common-issues.md)

## 如何實作任何功能

SDK 有 **35 個以上的功能 controller**（音訊、視訊、聊天、錄製、參與者、螢幕分享、分組討論室、webinar、Q&A、投票、白板、字幕、AI companion 等等）。

**適用於所有功能的通用模式：**

1. **取得 controller**（singleton）：
   ```cpp
   IMeetingAudioController* audioCtrl = meetingService->GetMeetingAudioController();
   IMeetingChatController* chatCtrl = meetingService->GetMeetingChatController();
   // ... 還有 33 個 controller 可用
   ```

2. **實作事件 listener**（observer 模式）：
   ```cpp
   class MyAudioListener : public IMeetingAudioCtrlEvent {
       void onUserAudioStatusChange(IList<IUserAudioStatus*>* lst) override {
           // 對音訊事件做出反應
       }
       // ... 實作所有必要的方法
   };
   ```

3. **註冊並使用**：
   ```cpp
   audioCtrl->SetEvent(new MyAudioListener());
   audioCtrl->MuteAudio(userId, true);  // 使用功能
   ```

**含範例的完整指南**：[SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)

## 可用的範例

| 範例 | 說明 |
|---------|-------------|
| **SkeletonDemo** | 最精簡的加入會議範例：從這裡開始 |
| **GetVideoRawData** | 訂閱 raw 視訊串流 |
| **GetAudioRawData** | 訂閱 raw 音訊串流 |
| **SendVideoRawData** | 把自訂視訊當成虛擬攝影機送出 |
| **SendAudioRawData** | 把自訂音訊當成虛擬麥克風送出 |
| **GetShareRawData** | 擷取螢幕分享內容 |
| **LocalRecording** | 本機 MP4 錄製 |
| **ChatDemo** | 會議中的聊天功能 |
| **CaptionDemo** | 隱藏式字幕/即時轉錄 |
| **BreakoutDemo** | 分組討論室管理 |

## 詳細參考資料

### 🎯 核心概念（從這裡開始！）
- **[concepts/sdk-architecture-pattern.md](concepts/sdk-architecture-pattern.md)** - **實作「任何」功能的通用模式**：搞懂這個，整個 SDK 就通了！

### 📚 完整範例
- **[examples/authentication-pattern.md](examples/authentication-pattern.md)** - 用 JWT token 的完整可運作驗證
- **[examples/raw-video-capture.md](examples/raw-video-capture.md)** - YUV420 視訊擷取，附詳細的格式說明

### 🔧 疑難排解指南
- **[troubleshooting/windows-message-loop.md](troubleshooting/windows-message-loop.md)** - **為什麼 callback 不觸發**（最重要！）
- **[troubleshooting/build-errors.md](troubleshooting/build-errors.md)** - SDK header 相依問題與修正方式
- **[troubleshooting/common-issues.md](troubleshooting/common-issues.md)** - 快速診斷流程與錯誤碼表

### 📖 參考資料
- **[references/interface-methods.md](references/interface-methods.md)** - 如何實作「所有」必要的虛擬方法
- **[references/windows-reference.md](references/windows-reference.md)** - 相依套件、Visual Studio 設定
- **[../references/authorization.md](../references/authorization.md)** - SDK JWT 的產生
- **[../references/bot-authentication.md](../references/bot-authentication.md)** - Bot token 類型（ZAK、OBF、JWT）

### 🎨 各功能專屬的指南
- **[../references/breakout-rooms.md](../references/breakout-rooms.md)** - 以程式管理分組討論室
- **[../references/ai-companion.md](../references/ai-companion.md)** - AI Companion 控制

## 範例儲存庫

| 儲存庫 | 說明 |
|------------|-------------|
| [meetingsdk-windows-raw-recording-sample](https://github.com/zoom/meetingsdk-windows-raw-recording-sample) | 官方的 raw data 擷取範例 |
| [meetingsdk-windows-local-recording-sample](https://github.com/zoom/meetingsdk-windows-local-recording-container-sample) | 搭配 Docker 的本機錄製 |

## 播放 Raw 視訊/音訊檔案

Raw YUV/PCM 檔案沒有 header，你必須明確指定格式。

### 播放 Raw YUV 視訊
```cmd
ffplay -video_size 1280x720 -pixel_format yuv420p -f rawvideo output.yuv
```

### 把 YUV 轉成 MP4
```cmd
ffmpeg -video_size 1280x720 -pixel_format yuv420p -f rawvideo -i output.yuv -c:v libx264 output.mp4
```

### 播放 Raw PCM 音訊
```cmd
ffplay -f s16le -ar 32000 -ac 1 audio.pcm
```

### 把 PCM 轉成 WAV
```cmd
ffmpeg -f s16le -ar 32000 -ac 1 -i audio.pcm output.wav
```

### 合併視訊 + 音訊
```cmd
ffmpeg -video_size 1280x720 -pixel_format yuv420p -f rawvideo -i output.yuv ^
       -f s16le -ar 32000 -ac 1 -i audio.pcm ^
       -c:v libx264 -c:a aac -shortest output.mp4
```

**重要的 flag：**
| Flag | 說明 |
|------|-------------|
| `-video_size WxH` | Frame 的尺寸（例如 1280x720） |
| `-pixel_format yuv420p` | I420/YUV420 planar 格式 |
| `-f rawvideo` | Raw 視訊輸入（沒有容器） |
| `-f s16le` | 有號 16-bit little-endian PCM |
| `-ar 32000` | 取樣率（Zoom 用 32kHz） |
| `-ac 1` | 單聲道（立體聲用 `-ac 2`） |

## 驗證要求（2026 更新）

> **重要**：從 **2026 年 3 月 2 日**起，要加入自己帳號以外的會議的 app，必須經過授權。

使用以下其中一種：
- **App Privilege Token（OBF）** - 建議給 bot 使用（JoinParam 中的 `app_privilege_token`）
- **ZAK Token** - Zoom Access Key（JoinParam 中的 `userZAK`）
- **On Behalf Token** - 用於特定情境（JoinParam 中的 `onBehalfToken`）

## 📖 完整文件庫

這個 skill 包含從真實除錯經驗整理出來的完整指南：

### 🎯 從這裡開始
- **[SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)** - 主要文件：適用於任何功能的通用模式
- **[SKILL.md](SKILL.md)** - 完整的導覽指南

### 📚 依類別

**核心概念：**
- [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md) - 每個功能如何運作（singleton + observer 模式）

**完整範例：**
- [Authentication Pattern](examples/authentication-pattern.md) - 附完整程式碼的可運作 JWT 驗證
- [Raw Video Capture](examples/raw-video-capture.md) - YUV420 視訊擷取的說明

**疑難排解：**
- [Windows Message Loop](troubleshooting/windows-message-loop.md) - **非常重要**：為什麼 callback 不觸發
- [Build Errors](troubleshooting/build-errors.md) - SDK header 相依問題的修正
- [Common Issues](troubleshooting/common-issues.md) - 快速診斷與錯誤碼

**參考資料：**
- [Interface Methods](references/interface-methods.md) - 所有必要的虛擬方法（6 個 auth + 9 個 meeting）
- [Windows Reference](references/windows-reference.md) - 平台設定
- [Authorization](../references/authorization.md) - JWT 的產生
- [Bot Authentication](../references/bot-authentication.md) - Bot token 類型
- [Breakout Rooms](../references/breakout-rooms.md) - 分組討論室 API
- [AI Companion](../references/ai-companion.md) - AI 功能

### 🚨 最重要的問題（來自真實除錯）

1. **Callback 不觸發** → 缺少 Windows message loop（99% 的問題）
   - 見：[Windows Message Loop Guide](troubleshooting/windows-message-loop.md)

2. **建置錯誤** → SDK header 相依問題（`uint32_t`、`AudioType` 等）
   - 見：[Build Errors Guide](troubleshooting/build-errors.md)

3. **Abstract class 錯誤** → 缺少虛擬方法的實作
   - 見：[Interface Methods Guide](references/interface-methods.md)

### 💡 關鍵洞察

**學會這 3 步驟模式之後，你就能實作 35 個以上功能中的「任何一個」：**
1. 取得 controller → 2. 實作事件 listener → 3. 註冊並使用

見：[SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)

## 官方資源

- **官方文件**：https://developers.zoom.us/docs/meeting-sdk/windows/
- **API 參考**：https://marketplacefront.zoom.us/sdk/meeting/windows/annotated.html
- **開發者論壇**：https://devforum.zoom.us/
- **SDK 下載**：https://marketplace.zoom.us/

---

**文件版本**：依據 Zoom Windows Meeting SDK v6.7.2.26830

**需要協助？** 從 [SKILL.md](SKILL.md) 開始，取得完整的導覽。


## 合併自 meeting-sdk/windows/SKILL.md

# Zoom Windows Meeting SDK - 完整文件索引

## 🚀 快速開始路徑

**如果你剛接觸這個 SDK，請照這個順序：**

1. **讀架構模式** → [concepts/sdk-architecture-pattern.md](concepts/sdk-architecture-pattern.md)
   - 這份教你適用於「所有」功能的通用公式
   - 一旦理解它，你只要讀 `.h` 檔就能實作任何功能

2. **修正建置錯誤** → [troubleshooting/build-errors.md](troubleshooting/build-errors.md)
   - SDK header 相依問題
   - 必要的 include 順序

3. **實作驗證** → [examples/authentication-pattern.md](examples/authentication-pattern.md)
   - 完整的可運作 JWT 驗證程式碼

4. **修正 callback 問題** → [troubleshooting/windows-message-loop.md](troubleshooting/windows-message-loop.md)
   - **非常重要**：為什麼沒有 Windows message loop，callback 就不會觸發
   - 這是最難診斷的問題！

5. **實作虛擬方法** → [references/interface-methods.md](references/interface-methods.md)
   - 所有必要方法的完整清單
   - 如何避免 abstract class 錯誤

6. **擷取視訊（選用）** → [examples/raw-video-capture.md](examples/raw-video-capture.md)
   - YUV420 格式的說明
   - 完整的 raw data 擷取工作流程

7. **排解任何問題** → [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
   - 快速診斷檢查清單
   - 錯誤碼表
   - 「看到 X 就做 Y」的對照表

---

## 📂 文件結構

```
meeting-sdk/windows/
├── SKILL.md                           # 主要的 skill 概覽
├── SKILL.md                           # 這個檔案：導覽指南
│
├── concepts/                          # 核心的架構模式
│   ├── sdk-architecture-pattern.md   # 最重要的文件
│   │                                  # 適用於任何功能的通用公式
│   ├── singleton-hierarchy.md        # SDK 服務的導覽指南
│   │                                  # 4 層深的服務樹，何時/如何使用
│   ├── custom-ui-architecture.md     # Custom UI 渲染如何運作
│   │                                  # 子 HWND、D3D、版面配置、事件
│   └── custom-ui-vs-raw-data.md      # SDK 渲染 vs 自行渲染
│                                      # Custom UI 做法的決策指南
│
├── examples/                          # 完整的可運作程式碼
│   ├── authentication-pattern.md     # 含完整程式碼的 JWT 驗證
│   ├── raw-video-capture.md          # 含 YUV420 細節的視訊擷取
│   │                                  # 錄製 vs 串流、權限
│   ├── custom-ui-video-rendering.md  # 含視訊容器的 Custom UI
│   │                                  # 主講者 + 圖庫版面
│   ├── breakout-rooms.md             # 完整的分組討論室指南
│   │                                  # 5 種角色、建立/管理/加入
│   ├── chat.md                       # 發送/接收聊天訊息
│   │                                  # 富文字、討論串、檔案傳輸
│   ├── captions-transcription.md     # 即時轉錄與隱藏式字幕
│   │                                  # 多語言翻譯
│   ├── local-recording.md            # 本機 MP4 錄製
│   │                                  # 權限流程、encoder 監控
│   ├── share-raw-data-capture.md     # 螢幕分享的 raw data 擷取
│   │                                  # 來自分享內容的 YUV420 frame
│   └── send-raw-data.md              # 虛擬攝影機/麥克風/分享
│                                      # 送出自訂的視訊/音訊/分享
│
├── troubleshooting/                   # 解決問題的指南
│   ├── windows-message-loop.md       # 非常重要：為什麼 callback 失敗
│   ├── build-errors.md               # Header 相依問題修正 + MSBuild
│   └── common-issues.md              # 快速診斷流程
│
└── references/                        # 參考文件
    ├── interface-methods.md           # 必要的虛擬方法
    │                                  # Auth(6) + Meeting(9) + CustomUI(13)
    ├── windows-reference.md           # 平台設定
    ├── authorization.md               # JWT 的產生
    ├── bot-authentication.md          # Bot token 類型
    ├── breakout-rooms.md              # 分組討論室功能
    └── ai-companion.md                # AI Companion 功能
```

---

## 🎯 依使用情境

### 我想建立會議 bot
1. [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md) - 了解模式
2. [Authentication Pattern](examples/authentication-pattern.md) - 加入會議
3. [Windows Message Loop](troubleshooting/windows-message-loop.md) - 修正 callback 問題
4. [Interface Methods](references/interface-methods.md) - 實作 callback

### 我遇到建置錯誤
1. [Build Errors Guide](troubleshooting/build-errors.md) - SDK header 相依問題
2. [Interface Methods](references/interface-methods.md) - Abstract class 錯誤
3. [Common Issues](troubleshooting/common-issues.md) - Linker 錯誤

### 我遇到執行階段錯誤
1. [Windows Message Loop](troubleshooting/windows-message-loop.md) - Callback 不觸發
2. [Authentication Pattern](examples/authentication-pattern.md) - 驗證逾時
3. [Common Issues](troubleshooting/common-issues.md) - 錯誤碼表

### 我想建立 Custom UI 會議 app
1. [Custom UI Architecture](concepts/custom-ui-architecture.md) - SDK 渲染如何運作
2. [SDK-Rendered vs Self-Rendered](concepts/custom-ui-vs-raw-data.md) - 選擇你的做法
3. [Custom UI Video Rendering](examples/custom-ui-video-rendering.md) - 完整的可運作程式碼
4. [Interface Methods](references/interface-methods.md) - 13 個 Custom UI 虛擬方法
5. [Build Errors Guide](troubleshooting/build-errors.md) - 在 git bash 裡跑 MSBuild

### 我想擷取視訊/音訊
1. [Raw Video Capture](examples/raw-video-capture.md) - 完整的視訊工作流程
   - 錄製 vs 串流的做法
   - 權限要求（主持人、OAuth token）
   - 音訊 PCM 擷取
2. [Share Raw Data Capture](examples/share-raw-data-capture.md) - 螢幕分享擷取
   - 訂閱 RAW_DATA_TYPE_SHARE
   - 處理動態解析度
3. [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md) - Controller 模式
4. [Common Issues](troubleshooting/common-issues.md) - 收不到 frame

### 我想使用分組討論室
1. [Breakout Rooms Guide](examples/breakout-rooms.md) - 完整的分組討論室工作流程
   - 5 種角色：Creator、Admin、Data、Assistant、Attendee
   - 建立、設定、管理、加入/離開討論室
2. [Common Issues](troubleshooting/common-issues.md) - 分組討論室的錯誤碼

### 我想實作聊天
1. [Chat Guide](examples/chat.md) - 發送/接收訊息
   - 富文字格式（粗體、斜體、連結）
   - 私訊與討論串
   - 檔案傳輸事件

### 我想使用即時轉錄
1. [Captions & Transcription Guide](examples/captions-transcription.md) - 即時轉錄
   - 自動語音轉文字
   - 多語言翻譯
   - 手動的隱藏式字幕（主持人功能）

### 我想錄製會議
1. [Local Recording Guide](examples/local-recording.md) - 本機 MP4 錄製
   - 權限請求的工作流程
   - zTscoder.exe encoder 監控
   - 圖庫檢視 vs 主講者

### 我想實作某個特定功能
1. [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md) - **從這裡開始！**
2. 在 `SDK/x64/h/meeting_service_interface.h` 裡找到 controller
3. 在 `SDK/x64/h/meeting_service_components/` 裡找到 header
4. 照通用模式做：取得 controller → 實作 listener → 使用方法

### 我想了解 SDK 的架構
1. [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md) - 完整的架構概覽
2. [Singleton Hierarchy](concepts/singleton-hierarchy.md) - 在服務樹中導覽（4 層）
3. [Interface Methods](references/interface-methods.md) - 事件 listener 模式
4. [Authentication Pattern](examples/authentication-pattern.md) - 服務模式

---

## 🔥 最重要的文件

### 1. SDK Architecture Pattern（⭐ 主要文件）
**[concepts/sdk-architecture-pattern.md](concepts/sdk-architecture-pattern.md)**

這是最重要的一份文件。它教你通用的 3 步驟模式：
1. 取得 controller（singleton 模式）
2. 實作事件 listener（observer 模式）
3. 註冊並使用

一旦理解這個模式，你只要讀 SDK header，就能實作 **35 個以上功能中的任何一個**。

**關鍵洞察**：Zoom SDK 遵循完全一致的架構。每個功能的運作方式都一樣。

---

### 2. Windows Message Loop（⚠️ 最常見的問題）
**[troubleshooting/windows-message-loop.md](troubleshooting/windows-message-loop.md)**

99% 的「callback 不觸發」問題，都是缺少 Windows message loop 造成的。這份文件說明：
- 為什麼 SDK 需要 `PeekMessage()` 迴圈
- 如何正確實作
- 如何診斷 callback 的問題

**這是開發過程中最難找到的 bug**（花了大約 2 小時）。

---

### 3. Build Errors Guide
**[troubleshooting/build-errors.md](troubleshooting/build-errors.md)**

SDK header 有相依性的 bug，會造成建置錯誤。這份文件提供：
- 必要的 include 順序
- 缺少 `<cstdint>` 的修正
- 缺少 `AudioType` 的修正
- 缺少 `YUVRawDataI420` 的修正

---

## 📊 依文件類型

### Concepts（為什麼與怎麼做）
- [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md) - 通用的實作模式
- [Singleton Hierarchy](concepts/singleton-hierarchy.md) - SDK 服務的導覽指南（4 層深）

### Examples（完整的可運作程式碼）
- [Authentication Pattern](examples/authentication-pattern.md) - JWT 驗證
- [Raw Video Capture](examples/raw-video-capture.md) - 用 YUV420 擷取視訊、錄製 vs 串流
- [Custom UI Video Rendering](examples/custom-ui-video-rendering.md) - SDK 渲染的視訊容器
- [Breakout Rooms](examples/breakout-rooms.md) - 建立、管理、加入分組討論室
- [Chat](examples/chat.md) - 發送/接收有富文字格式的訊息
- [Captions & Transcription](examples/captions-transcription.md) - 即時轉錄與隱藏式字幕
- [Local Recording](examples/local-recording.md) - 含權限流程的本機 MP4 錄製
- [Share Raw Data Capture](examples/share-raw-data-capture.md) - 螢幕分享的 raw data 擷取
- [Send Raw Data](examples/send-raw-data.md) - 虛擬攝影機、麥克風和分享

### Troubleshooting（解決問題）
- [Windows Message Loop](troubleshooting/windows-message-loop.md) - Callback 問題
- [Build Errors](troubleshooting/build-errors.md) - 編譯問題
- [Common Issues](troubleshooting/common-issues.md) - 快速診斷

### References（查閱資訊）
- [Interface Methods](references/interface-methods.md) - 必要的虛擬方法
- [Windows Reference](references/windows-reference.md) - 平台設定
- [Authorization](../references/authorization.md) - JWT 的產生
- [Bot Authentication](../references/bot-authentication.md) - Bot token
- [Breakout Rooms](../references/breakout-rooms.md) - 分組討論室 API
- [AI Companion](../references/ai-companion.md) - AI 功能

---

## 💡 從真實除錯得到的關鍵心得

這些文件是從實際除錯一個無法運作的 Zoom SDK 範例中整理出來的。以下是關鍵的洞察：

### 關鍵發現：

1. **Windows Message Loop 是「必要」的**（不是選用）
   - SDK 用 Windows message pump 觸發 callback
   - 沒有它的話，callback 會排進佇列但永遠不會觸發
   - 表現為「驗證逾時」，即使 JWT 是有效的
   - 見：[Windows Message Loop Guide](troubleshooting/windows-message-loop.md)

2. **SDK Header 有相依性的 bug**
   - SDK header 缺少 `#include <cstdint>`
   - `meeting_participants_ctrl_interface.h` 沒有 include `meeting_audio_interface.h`
   - `rawdata_renderer_interface.h` 只有 forward-declare `YUVRawDataI420`
   - 見：[Build Errors Guide](troubleshooting/build-errors.md)

3. **Include 順序非常重要**
   - `<windows.h>` 必須是「第一個」
   - `<cstdint>` 必須是「第二個」
   - 然後再依特定順序放 SDK header
   - 見：[Build Errors Guide](troubleshooting/build-errors.md)

4. **所有虛擬方法都必須實作**
   - 包含 WIN32 條件編譯的方法
   - SDK v6.7.2 需要 6 個 auth 方法 + 9 個 meeting 方法
   - 不同版本有不同的要求
   - 見：[Interface Methods Guide](references/interface-methods.md)

5. **這個架構一致得很漂亮**
   - 每個功能都遵循同一個 3 步驟模式
   - Controller 是 singleton
   - 事件 listener 使用 observer 模式
   - 學會這個模式之後，你就能實作任何功能
   - 見：[SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)

---

## 🎓 依技能程度的學習路徑

### 初學者（從沒用過 Zoom SDK）
1. 閱讀 [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)，了解整體設計
2. 跟著 [Authentication Pattern](examples/authentication-pattern.md)，加入你的第一場會議
3. 遇到問題時，參考 [Common Issues](troubleshooting/common-issues.md)

### 中階（熟悉 SDK 基礎）
1. 深入研究 [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)，實作多個功能
2. 學習 [Raw Video Capture](examples/raw-video-capture.md)，做媒體處理
3. 把 [Interface Methods](references/interface-methods.md) 當作參考資料

### 進階（建構正式環境的 bot）
1. 研讀 [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)，學會實作「任何」功能
2. 精通 [Windows Message Loop](troubleshooting/windows-message-loop.md)，理解非同步 callback 的流程
3. 用通用模式直接參考 SDK header

---

## 🔍 如何找到你需要的東西

### 「我的程式碼編譯不過」
→ [Build Errors Guide](troubleshooting/build-errors.md)

### 「驗證逾時」
→ [Windows Message Loop](troubleshooting/windows-message-loop.md)

### 「Callback 永遠不觸發」
→ [Windows Message Loop](troubleshooting/windows-message-loop.md)

### 「Abstract class 錯誤」
→ [Interface Methods](references/interface-methods.md)

### 「我要怎麼實作 [功能]？」
→ [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)

### 「我要怎麼加入會議？」
→ [Authentication Pattern](examples/authentication-pattern.md)

### 「我要怎麼擷取視訊？」
→ [Raw Video Capture](examples/raw-video-capture.md)

### 「這個錯誤碼是什麼意思？」
→ [Common Issues](troubleshooting/common-issues.md) - 完整的錯誤碼表（SDKERR、AUTHRET、Login、BO、Phone、OBF）

### 「我要怎麼使用分組討論室？」
→ [Breakout Rooms Guide](examples/breakout-rooms.md)

### 「SDK 是怎麼運作的？」
→ [SDK Architecture Pattern](concepts/sdk-architecture-pattern.md)

### 「我要怎麼導覽到特定的 controller/功能？」
→ [Singleton Hierarchy](concepts/singleton-hierarchy.md)

### 「我要怎麼發送/接收聊天訊息？」
→ [Chat Guide](examples/chat.md)

### 「我要怎麼使用即時轉錄？」
→ [Captions & Transcription Guide](examples/captions-transcription.md)

### 「我要怎麼做本機錄製？」
→ [Local Recording Guide](examples/local-recording.md)

### 「我要怎麼擷取螢幕分享？」
→ [Share Raw Data Capture](examples/share-raw-data-capture.md)

---

## 📝 文件版本

所有文件都是依據 **Zoom Windows Meeting SDK v6.7.2.26830**。

不同的 SDK 版本可能有：
- 不同的必要 callback 方法
- 不同的錯誤碼
- 不同的 API 行為

如果使用不同的版本，用 `grep "= 0" SDK/x64/h/*.h` 來確認必要的方法。

---

記住：[SDK Architecture Pattern](concepts/sdk-architecture-pattern.md) 是了解 Windows Meeting SDK 如何組合在一起最快的方法。如果你在除錯 custom UI 或事件流程的問題，請先讀它。

## 營運

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘的啟動前檢查與除錯檢查清單。
