---
name: windows-desktop-e2e
description: 用 pywinauto 和 Windows UI Automation，對 Windows 原生桌面 app（WPF、WinForms、Win32/MFC、Qt）做 E2E 測試。要用 pywinauto 或 UI Automation 為 Windows 原生桌面 app 寫 E2E 測試時使用。
metadata:
  origin: ECC
---

# Windows 桌面 E2E 測試

用 **pywinauto** 搭配 Windows UI Automation（UIA），對 Windows 原生桌面應用程式做端對端測試。涵蓋 WPF、WinForms、Win32/MFC 和 Qt（5.x / 6.x），其中 Qt 另有專屬章節說明。

## 何時啟用

- 為 Windows 原生桌面應用程式撰寫或執行 E2E 測試
- 從零開始建立桌面 GUI 測試套件
- 診斷不穩定（flaky）或失敗的桌面自動化測試
- 為既有 app 加上可測試性（AutomationId、accessible name）
- 把桌面 E2E 整合進 CI/CD 流程（GitHub Actions 的 `windows-latest`）

### 何時不要使用

- Web 應用程式 → 用 `e2e-testing` skill（Playwright）
- Electron / CEF / WebView2 app → HTML 那層需要的是瀏覽器自動化，不是 UIA
- 行動 app → 用各平台專用的工具（UIAutomator、XCUITest）
- 不需要執行 GUI 的純單元測試或整合測試

## 核心概念

所有 Windows 桌面自動化都仰賴 **UI Automation（UIA）**，這是 Windows 內建的無障礙 API。每個支援的框架都會暴露一棵 UIA 元素樹，上面的屬性 Claude 可以讀取並據以操作：

```
你的測試 (Python)
    └── pywinauto (UIA backend)
        └── Windows UI Automation API   ← Windows 內建，與框架無關
            └── App 的 UIA provider      ← 每個框架各自提供
                └── 執行中的 .exe
```

**各框架的 UIA 品質：**

| 框架 | AutomationId | 可靠度 | 備註 |
|-----------|-------------|-------------|-------|
| WPF | 5/5 | 極佳 | `x:Name` 直接對應到 AutomationId |
| WinForms | 4/5 | 良好 | `AccessibleName` = AutomationId |
| UWP / WinUI 3 | 5/5 | 極佳 | Microsoft 完整支援 |
| Qt 6.x | 5/5 | 極佳 | 預設啟用 Accessibility；class name 會變成 `Qt6*` |
| Qt 5.15+ | 4/5 | 良好 | 改良過的 Accessibility 模組 |
| Qt 5.7–5.14 | 3/5 | 普通 | 需要 `QT_ACCESSIBILITY=1`；objectName 要手動設定 |
| Win32 / MFC | 3/5 | 普通 | 可以存取 control ID；常需要靠文字比對 |

## 設定與前置需求

```bash
# Python 3.8+，僅限 Windows
pip install pywinauto pytest pytest-html Pillow pytest-timeout
# 選用：螢幕錄影
# 安裝 ffmpeg 並加進 PATH：https://ffmpeg.org/download.html
```

確認 UIA 連得到：

```python
from pywinauto import Desktop
Desktop(backend="uia").windows()  # 列出所有最上層視窗
```

安裝 **Accessibility Insights for Windows**（Microsoft 出的免費工具），在寫任何測試之前，用它檢視 UIA 元素樹，等於是你的 DevTools。

## 可測試性設定（依框架）

影響最大的一件事，是在寫測試之前，**幫每個可互動的控制項設定穩定的 AutomationId**。

### WPF

```xml
<!-- XAML：x:Name 會自動變成 AutomationId -->
<TextBox x:Name="usernameInput" />
<PasswordBox x:Name="passwordInput" />
<Button x:Name="btnLogin" Content="Login" />
<TextBlock x:Name="lblError" />
```

### WinForms

```csharp
// 在設計工具或程式碼裡設定
usernameInput.AccessibleName = "usernameInput";
passwordInput.AccessibleName = "passwordInput";
btnLogin.AccessibleName = "btnLogin";
lblError.AccessibleName = "lblError";
```

### Win32 / MFC

```cpp
// .rc 檔裡的 control resource ID 會以 AutomationId 字串的形式暴露出來
// IDC_EDIT_USERNAME -> AutomationId "1001"
// Name 優先用 SetWindowText；要更完整的支援就加上 IAccessible
```

### Qt：請看下方專屬章節

---

## Page Object Model

```
tests/
├── conftest.py          # app 啟動 fixture、失敗時截圖
├── pytest.ini
├── config.py
├── pages/
│   ├── __init__.py      # import 需要這個檔案
│   ├── base_page.py     # locator、等待、截圖的輔助函式
│   ├── login_page.py
│   └── main_page.py
├── tests/
│   ├── __init__.py
│   ├── test_login.py
│   └── test_main_flow.py
└── artifacts/           # 截圖、影片、log
```

### base_page.py

```python
import os, time
from pywinauto import Desktop
from config import ACTION_TIMEOUT, ARTIFACT_DIR

class BasePage:
    def __init__(self, window):
        self.window = window

    # --- Locator（依優先順序）---

    def by_id(self, auto_id, **kw):
        """AutomationId，最穩定，優先使用。"""
        return self.window.child_window(auto_id=auto_id, **kw)

    def by_name(self, name, **kw):
        """畫面上看得到的文字 / accessible name。"""
        return self.window.child_window(title=name, **kw)

    def by_class(self, cls, index=0, **kw):
        """控制項 class + index，很脆弱，盡量避免。"""
        return self.window.child_window(class_name=cls, found_index=index, **kw)

    # --- 等待 ---

    def wait_visible(self, spec, timeout=ACTION_TIMEOUT):
        spec.wait("visible", timeout=timeout)
        return spec

    def wait_gone(self, spec, timeout=ACTION_TIMEOUT):
        spec.wait_not("visible", timeout=timeout)
        return spec

    def wait_window(self, title, timeout=ACTION_TIMEOUT):
        """等待新的最上層視窗出現（對話框、子視窗）。"""
        dlg = Desktop(backend="uia").window(title=title)
        dlg.wait("visible", timeout=timeout)
        return dlg

    def wait_until(self, fn, timeout=ACTION_TIMEOUT, interval=0.3):
        """輪詢任意條件，UIA 事件不可靠時使用。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                if fn():
                    return True
            except Exception:
                pass
            time.sleep(interval)
        raise TimeoutError(f"Condition not met within {timeout}s")

    # --- 動作 ---

    def click(self, spec):
        self.wait_visible(spec)
        spec.click_input()

    def type_text(self, spec, text):
        self.wait_visible(spec)
        ctrl = spec.wrapper_object()
        try:
            ctrl.set_edit_text(text)
        except Exception as e:
            # Qt 5.x 的備援做法：UIA Value Pattern 可能不完整
            import sys, pywinauto.keyboard as kb
            print(f"[windows-desktop-e2e] set_edit_text failed ({e}), using keyboard fallback", file=sys.stderr)
            ctrl.click_input()
            kb.send_keys("^a")
            kb.send_keys(text, with_spaces=True)

    def get_text(self, spec):
        ctrl = spec.wrapper_object()
        for attr in ("window_text", "get_value"):
            try:
                v = getattr(ctrl, attr)()
                if v:
                    return v
            except Exception:
                pass
        return ""

    # --- 產出物（Artifact）---

    def screenshot(self, name):
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        path = os.path.join(ARTIFACT_DIR, f"{name}.png")
        self.window.capture_as_image().save(path)
        return path
```

### login_page.py

```python
from pages.base_page import BasePage

class LoginPage(BasePage):
    @property
    def username(self): return self.by_id("usernameInput")

    @property
    def password(self): return self.by_id("passwordInput")

    @property
    def btn_login(self): return self.by_id("btnLogin")

    @property
    def error_label(self): return self.by_id("lblError")

    def login(self, user, pwd):
        self.type_text(self.username, user)
        self.type_text(self.password, pwd)
        self.click(self.btn_login)

    def login_ok(self, user, pwd, main_title="Main Window"):
        self.login(user, pwd)
        return self.wait_window(main_title)

    def login_fail(self, user, pwd):
        self.login(user, pwd)
        self.wait_visible(self.error_label)
        return self.get_text(self.error_label)
```

### conftest.py

> 新專案請優先用 **Tier 1 sandbox fixture**（見下方），它不用額外成本就能提供檔案系統隔離。這個基本版 fixture 只給最精簡/舊式的設定使用。

```python
import os, pytest
os.environ["QT_ACCESSIBILITY"] = "1"  # Qt 5.x 的 UIA 支援需要這個

from pywinauto import Application
from config import APP_PATH, MAIN_WINDOW_TITLE, LAUNCH_TIMEOUT, ARTIFACT_DIR

@pytest.fixture
def app(request):
    if not APP_PATH:
        pytest.exit("APP_PATH environment variable is not set", returncode=1)
    proc = Application(backend="uia").start(APP_PATH, timeout=LAUNCH_TIMEOUT)
    win  = proc.window(title=MAIN_WINDOW_TITLE)
    win.wait("visible", timeout=LAUNCH_TIMEOUT)
    yield win
    # 失敗時截圖
    if getattr(getattr(request.node, "rep_call", None), "failed", False):
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        try:
            win.capture_as_image().save(
                os.path.join(ARTIFACT_DIR, f"FAIL_{request.node.name}.png")
            )
        except Exception:
            pass
    # 先正常關閉，不行再強制 kill
    # proc 是 pywinauto 的 Application，要用 wait_for_process_exit()，不是 wait_for_process()
    try:
        win.close()
        proc.wait_for_process_exit(timeout=5)
    except Exception:
        proc.kill()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, f"rep_{outcome.get_result().when}", outcome.get_result())
```

### config.py

```python
import os
APP_PATH          = os.environ.get("APP_PATH", "")           # 用環境變數設定，不給預設路徑
MAIN_WINDOW_TITLE = os.environ.get("APP_TITLE", "")
LAUNCH_TIMEOUT    = int(os.environ.get("LAUNCH_TIMEOUT", "15"))
ACTION_TIMEOUT    = int(os.environ.get("ACTION_TIMEOUT", "10"))
ARTIFACT_DIR      = os.path.join(os.path.dirname(__file__), "artifacts")
```

### pytest.ini

```ini
[pytest]
testpaths = tests
markers =
    smoke: fast smoke tests for critical paths
    flaky: known-unstable tests
addopts = -v --tb=short --html=artifacts/report.html --self-contained-html
```

## Locator 策略

```
AutomationId  >  Name（文字）  >  ClassName + index  >  XPath
  （穩定）         （好讀）          （脆弱）            （最後手段）
```

用 Accessibility Insights 檢視 → **Properties** 面板 → 先找 `AutomationId`。

```python
# 在 runtime 檢視，貼到 REPL 裡探索元素樹
win.print_control_identifiers()
# 或縮小範圍：
win.child_window(auto_id="groupBox1").print_control_identifiers()
```

## 等待模式

```python
# 等控制項出現
page.wait_visible(page.by_id("statusLabel"))

# 等控制項消失（例如 loading spinner）
page.wait_gone(page.by_id("spinnerOverlay"))

# 等對話框跳出來
dlg = page.wait_window("Confirm Delete")

# 自訂條件（例如文字變了）
page.wait_until(lambda: page.get_text(page.by_id("lblStatus")) == "Ready")
```

**絕對不要把 `time.sleep()` 當成主要的同步手段**，要用 `wait()` 或 `wait_until()`。

## 產出物管理

```python
# 需要時截圖
page.screenshot("after_login")

# 全螢幕擷取（視窗在畫面外或被最小化時）
import pyautogui
pyautogui.screenshot("artifacts/fullscreen.png")

# 用 ffmpeg 錄影（測試前開始，測試後停止）
import subprocess

def start_recording(name):
    return subprocess.Popen([
        "ffmpeg", "-f", "gdigrab", "-framerate", "10",
        "-i", "desktop", "-y", f"artifacts/videos/{name}.mp4"
    ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_recording(proc):
    proc.stdin.write(b"q"); proc.stdin.flush(); proc.wait(timeout=10)
```

## 逐步追蹤（選擇性開啟）

預設的失敗截圖，通常不足以診斷不穩定的測試。下面的步驟層級追蹤**預設是關閉的**，只在重現 flaky 案例時才開。

### 啟用

```bash
E2E_TRACE=1 pytest tests/test_login.py -v
# 把輸入的文字也寫進 JSONL log（有輸入帳密/個資的測試「不要」用）：
E2E_TRACE=1 E2E_TRACE_INCLUDE_TEXT=1 pytest ...
```

### 補進 BasePage

```python
import os, json, time
TRACE_ENABLED      = os.environ.get("E2E_TRACE") == "1"
TRACE_INCLUDE_TEXT = os.environ.get("E2E_TRACE_INCLUDE_TEXT") == "1"

class BasePage:
    _step = 0

    def _trace(self, action, spec=None, text=None):
        if not TRACE_ENABLED:
            return
        BasePage._step += 1
        idx = f"{BasePage._step:03d}"
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        try:
            self.window.capture_as_image().save(
                os.path.join(ARTIFACT_DIR, f"step_{idx}_{action}.png"))
        except Exception:
            pass  # 擷取失敗不能害測試壞掉
        rec = {
            "ts": time.time(), "step": BasePage._step, "action": action,
            "locator": getattr(spec, "criteria", None),
            "text": text if TRACE_INCLUDE_TEXT else ("<redacted>" if text else None),
        }
        with open(os.path.join(ARTIFACT_DIR, "trace.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")

    def click(self, spec):
        self.wait_visible(spec); self._trace("click_before", spec)
        spec.click_input();      self._trace("click_after",  spec)

    def type_text(self, spec, text):
        self.wait_visible(spec); self._trace("type_before", spec, text)
        # ... 既有的 set_edit_text / keyboard 備援 ...
        self._trace("type_after", spec)
```

### 注意事項

- **個資 / 帳密**：`type_text` 的內容預設會被換成 `<redacted>`。登入或付款流程絕對不要設 `E2E_TRACE_INCLUDE_TEXT=1`。
- **額外負擔**：每個動作約 50–200ms，再加上每一步在磁碟上多一張 PNG。不要在預設的 CI matrix 開啟，只在專門重現 flaky 的 job 裡開。
- **產出物膨脹**：一個很長的流程會產生幾十 MB，`retention-days` 要跟著調整。
- **平行/重跑的整潔**：這個簡單範例會一直往 `trace.jsonl` 追加，還用了 class 層級的計數器。重跑之前要先清空 artifact 目錄，平行測試則要給每個 worker 各自的 artifact 目錄。
- **涵蓋缺口**：在 `BasePage` 之外執行的動作（測試程式碼裡直接呼叫 `pywinauto`）不會被追蹤。

## 不穩定測試的處理

```python
# 隔離：等同於 Playwright 的 test.fixme()
@pytest.mark.skip(reason="Flaky: animation race on slow CI. Issue #42")
def test_animated_transition(self, app): ...

# 只在 CI 跳過
@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Flaky in CI #43")
def test_heavy_load(self, app): ...
```

常見原因與解法：

| 原因 | 解法 |
|-------|-----|
| 控制項還沒就緒 | 把 `time.sleep` 換成 `wait_visible` |
| 視窗沒有焦點 | 互動前加上 `win.set_focus()` |
| 動畫進行中 | `wait_until(lambda: not loading_indicator.exists())` |
| 對話框時機問題 | `wait_window(title, timeout=15)` |
| CI 的顯示環境還沒準備好 | 設定 `DISPLAY`，或在 CI 使用虛擬桌面 |
| `set_edit_text` 丟出 NotImplementedError | 缺少 UIA ValuePattern（Qt 5.x 常見），`BasePage.type_text` 已經會退回用 `keyboard.send_keys` |
| 控制項存在但 `wait_visible` 逾時 | 視窗被最小化或在畫面外，等待之前先呼叫 `win.restore()` + `win.set_focus()` |

## 測試隔離與 Sandbox

隔離分三層，選能滿足需求的最輕那一層。

### Tier 1：檔案系統隔離（預設，一律使用）

每個測試透過 `subprocess.Popen` 和 `Application.connect()`，各自拿到獨立的 `APPDATA` / `LOCALAPPDATA` / `TEMP`。pytest 的 `tmp_path` fixture 會自動負責清理。

```python
# conftest.py：用這個取代基本版的 `app` fixture
import os, subprocess, pytest
from pywinauto import Application
from config import APP_PATH, APP_ARGS, APP_TITLE, LAUNCH_TIMEOUT, ACTION_TIMEOUT, ARTIFACT_DIR

@pytest.fixture(scope="function")
def app(request, tmp_path):
    """每個測試用全新的 process + 隔離的使用者資料目錄。"""
    if not APP_PATH:
        pytest.exit("APP_PATH not set", returncode=1)

    # 把所有每位使用者的儲存位置，都導向隔離的暫存目錄
    sandbox_env = os.environ.copy()
    sandbox_env["QT_ACCESSIBILITY"]  = "1"
    sandbox_env["APPDATA"]           = str(tmp_path / "AppData" / "Roaming")
    sandbox_env["LOCALAPPDATA"]      = str(tmp_path / "AppData" / "Local")
    sandbox_env["TEMP"] = sandbox_env["TMP"] = str(tmp_path / "Temp")
    for p in (sandbox_env["APPDATA"], sandbox_env["LOCALAPPDATA"], sandbox_env["TEMP"]):
        os.makedirs(p, exist_ok=True)

    if not APP_TITLE:
        pytest.exit("APP_TITLE environment variable is not set", returncode=1)

    # shlex.split 能處理含空白的引號參數；單純的 split() 會被它搞壞
    import shlex
    # 用 subprocess 啟動才能傳入 env；再用 PID 讓 pywinauto 連上去
    proc = subprocess.Popen(
        [APP_PATH] + shlex.split(APP_ARGS),
        env=sandbox_env,
    )
    pw_app = Application(backend="uia").connect(process=proc.pid, timeout=LAUNCH_TIMEOUT)
    win    = pw_app.window(title=APP_TITLE)
    win.wait("visible", timeout=LAUNCH_TIMEOUT)
    yield win

    if getattr(getattr(request.node, "rep_call", None), "failed", False):
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        try:
            win.capture_as_image().save(
                os.path.join(ARTIFACT_DIR, f"FAIL_{request.node.name}.png")
            )
        except Exception:
            pass
    try:
        win.close()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
    # tmp_path 會由 pytest 自動清理

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, f"rep_{outcome.get_result().when}", outcome.get_result())
```

### Tier 2：Windows Job Object（選用：限制 process 的生命週期）

把 process 掛到 Job Object 上，當測試 fixture 的 job handle 被 GC 時，它就會**自動被終止**。也能避免 app 產生逃過 fixture 清理的子 process。

> **隔離的範圍：**Job Object **不會**虛擬化檔案系統存取，也不會
> 擋網路流量。檔案寫入與網路的隔離，需要 AppContainer、
> Windows 防火牆規則，或 Tier 3（Windows Sandbox）。Tier 2 只用在
> 控制 process 生命週期與子 process 的範圍。

不需要額外的相依套件。

```python
import ctypes, ctypes.wintypes as wt

def restrict_process(pid: int):
    """
    把 process 掛到 Job Object 上，防止它：
    - 在 job 之外產生 process（LIMIT_KILL_ON_JOB_CLOSE）
    不會擋網路，網路要用 Windows 防火牆規則處理。
    """
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    # 最小權限：SET_QUOTA (0x0100) | TERMINATE (0x0001)
    PROCESS_SET_QUOTA_AND_TERMINATE    = 0x0101

    kernel32 = ctypes.windll.kernel32
    job   = kernel32.CreateJobObjectW(None, None)
    hproc = kernel32.OpenProcess(PROCESS_SET_QUOTA_AND_TERMINATE, False, pid)

    # 正確的 struct 配置：LimitFlags 在 offset +16，不是 +44
    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", wt.LARGE_INTEGER),
            ("PerJobUserTimeLimit",     wt.LARGE_INTEGER),
            ("LimitFlags",             wt.DWORD),
            ("MinimumWorkingSetSize",   ctypes.c_size_t),
            ("MaximumWorkingSetSize",   ctypes.c_size_t),
            ("ActiveProcessLimit",      wt.DWORD),
            ("Affinity",               ctypes.c_size_t),
            ("PriorityClass",          wt.DWORD),
            ("SchedulingClass",        wt.DWORD),
        ]

    info = JOBOBJECT_BASIC_LIMIT_INFORMATION()
    info.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    ok = kernel32.SetInformationJobObject(job, 2, ctypes.byref(info), ctypes.sizeof(info))
    if not ok:
        raise ctypes.WinError()
    kernel32.AssignProcessToJobObject(job, hproc)
    kernel32.CloseHandle(hproc)
    return job  # 要一直保留，job 被 GC 時就會關閉（連帶殺掉 process）

# 在 proc = subprocess.Popen(...) 之後：  job = restrict_process(proc.pid)
```

### Tier 3：Windows Sandbox（CI 的整個 OS 隔離）

當你每次執行都需要乾淨的 Windows 映像檔（沒有殘留的 registry key、沒有共用的 GPU 狀態、真正的隔離），就把**整個測試套件**放到
[Windows Sandbox](https://learn.microsoft.com/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-overview) 裡面跑。

**需求：**Windows 10/11 Pro 或 Enterprise，並啟用虛擬化。

在專案根目錄建立 `e2e-sandbox.wsb`：

```xml
<Configuration>
  <MappedFolders>
    <!-- App 執行檔（唯讀） -->
    <MappedFolder>
      <HostFolder>C:\path\to\your\build\Release</HostFolder>
      <SandboxFolder>C:\app</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
    <!-- 測試套件（可讀寫，因為要寫入產出物） -->
    <MappedFolder>
      <HostFolder>C:\path\to\your\e2e_test</HostFolder>
      <SandboxFolder>C:\e2e_test</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <!--
      Windows Sandbox 啟動時沒有 Python。先靜默安裝，
      再安裝相依套件並執行測試。產出物會透過上面的
      MappedFolder 寫回 host。
    -->
    <Command>powershell -Command "
      winget install --id Python.Python.3.11 --silent --accept-package-agreements;
      $env:PATH += ';' + $env:LOCALAPPDATA + '\Programs\Python\Python311\Scripts';
      cd C:\e2e_test;
      pip install -r requirements.txt;
      pytest tests\ -v
    "</Command>
  </LogonCommand>
</Configuration>
```

啟動：`WindowsSandbox.exe e2e-sandbox.wsb`

> pywinauto 和 app 都在 sandbox **裡面**執行（需要在同一個 session）。
> 產出物會透過對應的資料夾寫回 host。

### 各 Tier 比較

| Tier | 隔離範圍 | 設定成本 | CI 可用 | 何時使用 |
|------|-----------|-----------|-------------|----------|
| 1：`tmp_path` 環境變數導向 | 檔案系統 | 零 | 一律可用 | 所有測試的預設 |
| 2：Job Object | Process 樹 | 低 | 一律可用 | 防止子 process 逃脫 |
| 3：Windows Sandbox | 整個 OS | 中 | 需要 Pro/Enterprise 映像檔 | 每晚的乾淨環境執行 |

### 防止測試卡住

加上 `pytest-timeout` 來限制任何單一測試的時間。在 `pytest.ini` 裡設定 `timeout = 60` 和 `timeout_method = thread`。注意：`thread` 方法在 Windows 上殺不掉 Qt app 的子 process，要在 `conftest.py` 加上 `atexit.register(lambda: [p.kill() for p in psutil.Process().children(recursive=True)])` 來回收孤兒 process。

## CI/CD 整合

```yaml
# .github/workflows/e2e-desktop.yml
name: Desktop E2E
on: [push, pull_request]

jobs:
  e2e:
    runs-on: windows-latest   # 真實的 GUI 環境，不需要 Xvfb
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }

      - name: Install deps
        run: pip install pywinauto pytest pytest-html Pillow

      - name: Build app
        run: cmake --build build --config Release  # 依你的建置系統調整

      - name: Run E2E
        env:
          APP_PATH: ${{ github.workspace }}\build\Release\MyApp.exe
          APP_TITLE: "My Application"
          CI: "true"
        run: pytest tests/ --html=artifacts/report.html --self-contained-html --junitxml=artifacts/results.xml -v

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: e2e-artifacts
          path: artifacts/
          retention-days: 14
```

## Qt 專屬

### 在 Qt 5.x 啟用 UIA

Qt 5.x 的 accessibility 在某些 build 預設是關閉的（尤其是 5.7–5.14）。要在啟動**之前**設定環境變數。Qt 6.x 預設就啟用 accessibility，Qt 6 可以跳過這一步。

```python
# conftest.py：加在 module 最上面
import os
os.environ["QT_ACCESSIBILITY"] = "1"
```

或是在 CI 裡 export：

```yaml
env:
  QT_ACCESSIBILITY: "1"
```

### 為 Qt Widget 加上穩定的識別碼

```cpp
// 建議：同時設定 objectName 和 accessibleName
void setTestId(QWidget* w, const char* id) {
    w->setObjectName(id);
    w->setAccessibleName(id);  // 會變成 UIA 的 Name 屬性
}

// 在你的 dialog 建構函式裡：
setTestId(ui->usernameEdit, "usernameInput");
setTestId(ui->passwordEdit, "passwordInput");
setTestId(ui->loginButton,  "btnLogin");
setTestId(ui->errorLabel,   "lblError");
```

把所有 ID 集中放在一個 header 裡，避免打錯字：

```cpp
// test_ids.h
#define TID_USERNAME   "usernameInput"
#define TID_PASSWORD   "passwordInput"
#define TID_BTN_LOGIN  "btnLogin"
#define TID_LBL_ERROR  "lblError"
```

### Qt 專屬的怪癖

**QComboBox**：下拉選單是獨立的最上層視窗：

```python
from pywinauto import Desktop

def select_combo_item(page, combo_spec, item_text):
    page.click(combo_spec)
    # 下拉選單會以新的根層級視窗出現
    # class_name 會依 Qt 版本而異，要用 Accessibility Insights 確認
    # Qt 5.x: "Qt5QWindowIcon"  |  Qt 6.x: "Qt6QWindowIcon"，要用 Accessibility Insights 確認
    popup = Desktop(backend="uia").window(class_name_re="Qt[56]QWindowIcon")
    popup.wait("visible", timeout=5)
    popup.child_window(title=item_text).click_input()
```

**QMessageBox / QDialog**：同樣是獨立的最上層視窗：

```python
dlg = page.wait_window("Confirm")          # 等對話框標題
dlg.child_window(title="OK").click_input() # 點裡面的按鈕
```

**QTableWidget / QTableView**：存取 row/cell：

```python
table = page.by_id("tblUsers").wrapper_object()
cell  = table.cell(row=0, column=1)
print(cell.window_text())
```

**自繪的控制項**（只有 `paintEvent`、`QGraphicsView`、`QOpenGLWidget`）：UIA 看不到它們的內部。請用下面的 Fallback 章節。

## 備援方案：截圖模式

當控制項無法透過 UIA 取得時（自繪、第三方、遊戲引擎）：

```bash
pip install pyautogui Pillow opencv-python
```

```python
import pyautogui, cv2, numpy as np
from PIL import Image

def find_image_on_screen(template_path, confidence=0.85):
    """在螢幕上找出樣板圖片。回傳 (x, y) 中心點，找不到回傳 None。"""
    screen   = np.array(pyautogui.screenshot())
    template = np.array(Image.open(template_path))
    result   = cv2.matchTemplate(
        cv2.cvtColor(screen, cv2.COLOR_RGB2BGR),
        cv2.cvtColor(template, cv2.COLOR_RGB2BGR),
        cv2.TM_CCOEFF_NORMED,
    )
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= confidence:
        h, w = template.shape[:2]
        return max_loc[0] + w // 2, max_loc[1] + h // 2
    return None

def click_image(template_path, confidence=0.85):
    pos = find_image_on_screen(template_path, confidence)
    if pos is None:
        raise RuntimeError(f"Image not found on screen: {template_path}")
    pyautogui.click(*pos)
```

### DPI / 縮放規則（僅限截圖模式）

截圖比對對 Windows 的顯示縮放（100% / 125% / 150%）極度敏感。有三條硬性規則：

1. **用跟目標機器相同的縮放比例擷取樣板。**不要想用 `PIL.Image.resize` 來補救不一致，`cv2.matchTemplate` 對重新取樣造成的雜訊非常脆弱。
2. **固定 CI 的顯示縮放。**在 `windows-latest` 上加一個像 `Set-DisplayResolution 1920 1080 -Force` 的步驟，並關閉各螢幕獨立的 DPI 縮放，讓截圖尺寸可以重現。
3. **把縮放比例跟每個產出物記在一起。**擷取時，把 `GetDpiForWindow(hwnd) / 96` 寫進 `artifacts/<test>/metadata.json`，事後檢討就一目了然，不用靠猜。

> 當被測的 app 是 Qt 寫的，process 層級的 DPI awareness（`SetProcessDpiAwarenessContext`）**可能會跟 Qt 自己的 DPI 處理衝突**。與其在 fixture 裡切換整個 process 的 DPI 模式，不如用「相同縮放的樣板 + 固定 CI」。

### 除錯比對信心值

調整 `confidence` 門檻時，唯一合理的做法是**親眼看**比對結果落在哪裡。下面的 helper 只用來診斷，不要從測試程式碼呼叫它。

```python
def debug_match(template_path, out="artifacts/match_debug.png", confidence=0.85):
    """只用來診斷。把最佳比對的矩形與分數畫回目前的螢幕畫面。

    不能用在正式測試：只在校準 confidence 或追查誤判時使用。
    """
    import os, cv2, pyautogui, numpy as np
    screen = np.array(pyautogui.screenshot())[:, :, ::-1]
    tpl    = cv2.imread(template_path)
    if tpl is None:
        raise RuntimeError(f"Template unreadable: {template_path}")
    res    = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
    _, mv, _, ml = cv2.minMaxLoc(res)
    h, w   = tpl.shape[:2]
    colour = (0, 255, 0) if mv >= confidence else (0, 0, 255)  # 綠色通過 / 紅色失敗
    cv2.rectangle(screen, ml, (ml[0]+w, ml[1]+h), colour, 2)
    cv2.putText(screen, f"score={mv:.3f} thr={confidence}",
                (ml[0], max(20, ml[1]-6)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    cv2.imwrite(out, screen)
    return mv
```

**少用**：圖片比對會因為 DPI 改變、換佈景主題、部分被遮住而失效。
一律先試 UIA，只有真的碰不到的控制項才退回截圖。

## 反模式

```python
# 錯誤：固定 sleep
time.sleep(3)
page.click(page.by_id("btnSubmit"))

# 正確：條件等待
page.wait_visible(page.by_id("btnSubmit"))
page.click(page.by_id("btnSubmit"))
```

```python
# 錯誤：把脆弱的 class+index locator 當主要策略
page.by_class("Edit", index=2).type_keys("hello")

# 正確：AutomationId
page.by_id("usernameInput").set_edit_text("hello")
```

```python
# 錯誤：對像素座標做 assert
assert btn.rectangle().left == 120

# 正確：對內容 / 狀態做 assert
assert page.get_text(page.by_id("lblStatus")) == "Logged in"
assert page.by_id("btnLogout").is_enabled()
```

```python
# 錯誤：所有測試共用同一個 app instance（狀態會互相汙染）
@pytest.fixture(scope="session")
def app(): ...

# 正確：每個測試用全新的 process（頂多每個 class 一個）
@pytest.fixture(scope="function")
def app(): ...
```

## 執行測試

```bash
# 全部測試
pytest tests/ -v

# 只跑 smoke
pytest tests/ -m smoke -v

# 指定檔案
pytest tests/test_login.py -v

# 指定 app 路徑
APP_PATH="C:\build\Release\MyApp.exe" APP_TITLE="MyApp" pytest tests/ -v

# 偵測 flaky 測試（每個重複跑 5 次）
pip install pytest-repeat
pytest tests/test_login.py --count=5 -v
```

## 相關 Skill

- `e2e-testing`：Web 應用程式的 Playwright E2E
- `cpp-testing`：用 GoogleTest 做 C++ 單元/整合測試
- `cpp-coding-standards`：C++ 程式碼風格與模式
