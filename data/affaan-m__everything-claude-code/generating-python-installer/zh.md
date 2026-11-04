---
name: generating-python-installer
description: "Commercial-grade Python installer expert for Windows: Nuitka extreme compilation, dist slimming, DLL footprint analysis, and Inno Setup packaging to ship the smallest, fastest installers. Use when a Python app must ship as a minimal, fast-starting Windows installer; not for basic script-to-exe conversion. 中文觸發：Nuitka 極限最佳化、Python 商業打包、極限編譯 Python、dist 瘦身、DLL 分析、最小安裝包、最快啟動、商業級打包風格"
---

# Generating Python Installer (Commercial-Grade)

You are a **Python commercial deployment expert**. Your goal is the **smallest, fastest-starting, cleanest** Windows installer. The core approach is **"Nuitka folder mode (dist) + Inno Setup packaging"** — no single-file builds, no stray console window.

## When to Activate

Activate when the user explicitly asks for **advanced** Python packaging or size/startup optimization on Windows:

- Nuitka extreme / commercial-grade compilation, smallest-size or fastest-startup builds
- `dist` folder slimming, DLL footprint analysis, 32-bit vs 64-bit size tradeoffs
- Inno Setup packaging with full metadata and a clean, residue-free uninstall

This skill targets advanced size/startup optimization — not basic one-file "script to exe" conversion.

## How It Works

1. **Confirm build parameters** — app name, version, publisher, exe name, source/output dirs, icon. Never auto-fill; ask the user.
2. **Verify the source build** — console disabled, LTO enabled, VC++ runtime present.
3. **Compile with Nuitka** using the module-exclusion and plugin strategy below.
4. **Slim the `dist` folder** — strip debug symbols, caches, tests, and docs, with safeguards for runtime-required metadata.
5. **Analyze DLLs** to find and trim the largest dependencies.
6. **Package with Inno Setup** — LZMA2 ultra compression, full metadata, residue-free uninstall, and an arch-matched VC++ redistributable.

## Examples

- "用 Nuitka 把這個 PySide2 專案打成最小體積的商業安裝包" → run the full workflow: recommend 32-bit, exclude WebEngine/3D/Charts, slim `dist`, package with Inno Setup.
- "我的 exe 有 400 MB，怎麼瘦身到一半" → analyze DLLs, switch to `opencv-python-headless`, drop `opengl32sw`, apply `dist` slimming.
- "安裝後在純淨系統打不開" → ensure the matching-arch VC++ redistributable is bundled in the Inno Setup script.

---

## 核心理念

堅持 **"Nuitka 資料夾模式(dist) + Inno Setup 封裝"** 方案。拒絕單檔案版，拒絕黑窗。

---

## 實戰參考案例（生產級 PySide2 桌面應用，323 MB，含 OpenCV / Playwright）

### 專案概況
- **總體積**: 323 MB
- **打包工具**: PyInstaller 4.7 (32位)
- **主要依賴**: PySide2 (22.52 MB), OpenCV (62.38 MB), Playwright (76.74 MB)
- **Python 版本**: Python 3.8 (32位)
- **DLL 數量**: 71 個，總計 93.23 MB

### 關鍵最佳化策略
1. PASS: **使用 32 位 Python** → 體積減少 20-30%
2. PASS: **base_library.zip 壓縮標準庫** → 0.74 MB
3. PASS: **精簡模組排除** → 無 pytest/unittest/setuptools
4. PASS: **精簡 Qt 外掛** → 只保留必要外掛

### 體積分佈

| 元件 | 體積 | 佔比 | 最佳化建議 |
|------|------|------|---------|
| playwright | 76.74 MB | 23.8% | 非必要可移除 |
| OpenCV | 62.38 MB | 19.3% | 用 opencv-python-headless |
| PySide2 | 22.52 MB | 7.0% | 排除 WebEngine/3D/Charts |
| 其他依賴 | 161.36 MB | 49.9% | - |

### 預期效果對比

| 專案型別 | Nuitka 原始 | 最佳化後 | 參考專案實測 |
|---------|------------|--------|----------------|
| Tkinter + 標準庫 | 150-250 MB | **80-120 MB** | - |
| PyQt/PySide | 200-400 MB | **120-250 MB** | 323 MB (含 OpenCV 等) |
| 含 numpy/pandas | 300-600 MB | **180-350 MB** | - |

---

## 核心工作流 (Workflow) - WARNING: 嚴格執行

當使用者請求打包時，按照以下步驟操作：

**步驟 1：強制引數確認（FAIL: 禁止使用預設值）**

> **WARNING: 重要規則：以下所有引數必須逐一向使用者確認，禁止自動填充或使用預設值！**

必須向使用者詢問並確認以下資訊（*等待使用者明確回覆後才能繼續*）：

| 引數 | 說明 | 示例 |
|------|------|------|
| **軟體名稱** (App Name) | 軟體顯示名稱 | `紅墨批註` |
| **版本號** (Version) | 語義化版本號 | `1.0.0` |
| **釋出者/公司名** (Publisher) | 控制面板顯示的釋出者 | `YourCompany` |
| **主程式** (Exe Name) | 主可執行檔名 | `RedInk.exe` |
| **源路徑** (Source Dir) | Nuitka dist 資料夾絕對路徑 | `D:\project\dist` |
| **輸出路徑** (Output Dir) | 安裝包生成位置 | `D:\project\output` |
| **圖示路徑** (Icon Path) | .ico 檔案絕對路徑（可選但推薦） | `D:\project\icon.ico` |
| **官網地址** (URL) | 可選，用於控制面板連結 | `https://example.com` |

**詢問模板：**
> "請提供以下打包引數，我需要您逐一確認：
> 1. 軟體名稱：
> 2. 版本號：
> 3. 釋出者/公司名：
> 4. 主程式檔名（如 xxx.exe）：
> 5. 源路徑（Nuitka dist 資料夾）：
> 6. 輸出路徑（安裝包儲存位置）：
> 7. 圖示路徑（.ico 檔案，可留空）：
> 8. 官網地址（可留空）：
>
> 請逐一填寫，或回覆"跳過"表示使用空值。"

**步驟 2：原始檔質量與編譯檢查（關鍵）**
在生成程式碼之前，必須向使用者發出以下**關鍵確認**（因為 Inno Setup 只是打包工具，無法改變程式本身的執行屬性）：

> "WARNING: **編譯引數檢查**：
> 1. **去黑窗**：請確認您的 dist 資料夾是使用 `nuitka --windows-console-mode=disable` 編譯的。（否則安裝後依然會有黑框）
> 2. **高效能**：請確認是否使用了 `--lto=yes`。（否則啟動速度可能不理想）
> 3. **執行庫**：請確保 dist 資料夾內已包含必要的 VC++ 執行庫，防止在純淨系統上無法執行。
>
> **確認原始檔已準備好請回復"確認"，否則請先重新編譯。**"

**步驟 3：生成程式碼**
使用者確認後，輸出包含 **完整後設資料** 和 **解除安裝圖示修復** 的程式碼。

---

## Nuitka 極限最佳化編譯（基於 參考專案經驗）

### 一、32 位 vs 64 位選擇策略

**參考專案使用 32 位 Python 的原因**：

| 元件 | 64位體積 | 32位體積 | 節省 |
|------|---------|---------|------|
| python3x.dll | ~4.5 MB | ~3.8 MB | 15% |
| Qt5Core.dll | ~8 MB | ~5 MB | 37% |
| numpy | ~30 MB | ~20 MB | 33% |
| **總體** | 基準 | **-20~30%** | - |

**推薦使用 32 位條件**：
- PASS: 程式記憶體佔用 < 2GB
- PASS: 不處理超大檔案（< 2GB）
- PASS: 目標使用者是普通辦公電腦

**32 位編譯方法**：
```bash
# 1. 安裝 32 位 Python（和 64 位可以共存）
# 下載地址：https://www.python.org/downloads/windows/

# 2. 用 32 位 Python 安裝依賴
py -3.12-32 -m pip install -r requirements.txt

# 3. 用 32 位 Python 編譯
py -3.12-32 -m nuitka --standalone ...你的引數
```

### 二、模組排除清單（參考專案驗證過的）

**安全排除列表**（執行時不需要）：
```
unittest,test,pytest,_pytest,doctest,pdb,pdbpp,
setuptools,pip,distutils,pkg_resources,
email.mime,http.server,xmlrpc,pydoc
```

**預期效果**：節省 **30-50 MB**

### 三、GUI 框架專用最佳化

#### Tkinter 極限最佳化（推薦，最輕量）
```bash
nuitka --standalone --windows-console-mode=disable ^
    --lto=yes ^
    --jobs=8 ^
    --enable-plugin=tk-inter ^
    --enable-plugin=anti-bloat ^
    --noinclude-pytest-mode=nofollow ^
    --noinclude-setuptools-mode=nofollow ^
    --nofollow-import-to=unittest,test,pytest,_pytest,doctest,pdb,pdbpp ^
    --nofollow-import-to=setuptools,pip,distutils,pkg_resources ^
    --nofollow-import-to=email.mime,http.server,xmlrpc,pydoc ^
    --python-flag=no_docstrings ^
    --output-dir=dist ^
    --windows-icon-from-ico=icon.ico ^
    --remove-output ^
    main.py
```

**預期體積**：80-120 MB（最佳化後）

#### PyQt5 / PySide2 最佳化
```bash
nuitka --standalone --windows-console-mode=disable ^
    --lto=yes ^
    --jobs=8 ^
    --enable-plugin=pyqt5 ^
    --enable-plugin=anti-bloat ^
    --noinclude-pytest-mode=nofollow ^
    --noinclude-setuptools-mode=nofollow ^
    --nofollow-import-to=unittest,test,pytest,_pytest,doctest,pdb ^
    --nofollow-import-to=setuptools,pip,distutils,pkg_resources ^
    --nofollow-import-to=PyQt5.QtWebEngine,PyQt5.QtWebEngineWidgets ^
    --nofollow-import-to=PyQt5.Qt3D,PyQt5.QtCharts ^
    --python-flag=no_docstrings ^
    --include-qt-plugins=sensible,styles,platforms ^
    --output-dir=dist ^
    --windows-icon-from-ico=icon.ico ^
    --remove-output ^
    main.py
```

**預期體積**：120-250 MB（最佳化後）

### 四、一鍵編譯指令碼模板

**儲存為 `build_optimized.bat`（專案根目錄）**：

```batch
@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Nuitka 極限最佳化編譯（參考 參考專案）
echo ========================================

REM === 配置區域（請修改為你的實際值） ===
set APP_NAME=你的軟體名
set MAIN_FILE=main.py
set ICON_FILE=icon.ico

REM === 自動檢測 CPU 核心數 ===
REM 用 Windows 自帶環境變數（wmic 在 Win11 22H2+ 已移除，探不到會讓 --jobs=0 單執行緒編譯）
set CPU_CORES=%NUMBER_OF_PROCESSORS%
if not defined CPU_CORES set CPU_CORES=4
set /a BUILD_JOBS=%CPU_CORES%

REM === 參考專案的模組排除清單 ===
set EXCLUDE_MODULES=unittest,test,pytest,_pytest,doctest,pdb,pdbpp
set EXCLUDE_MODULES=%EXCLUDE_MODULES%,setuptools,pip,distutils,pkg_resources
set EXCLUDE_MODULES=%EXCLUDE_MODULES%,email.mime,http.server,xmlrpc,pydoc

echo.
echo [1/4] 清理舊編譯...
if exist dist rd /s /q dist
if exist build rd /s /q build

echo.
echo [2/4] Nuitka 編譯中（應用 參考專案最佳化策略）...
echo - CPU 核心: %CPU_CORES% (使用 %BUILD_JOBS% 執行緒)
echo - 模組排除: %EXCLUDE_MODULES%
echo.

nuitka --standalone ^
    --windows-console-mode=disable ^
    --lto=yes ^
    --jobs=%BUILD_JOBS% ^
    --enable-plugin=anti-bloat ^
    --enable-plugin=tk-inter ^
    --noinclude-pytest-mode=nofollow ^
    --noinclude-setuptools-mode=nofollow ^
    --nofollow-import-to=%EXCLUDE_MODULES% ^
    --python-flag=no_docstrings ^
    --output-dir=dist ^
    --windows-icon-from-ico=%ICON_FILE% ^
    --remove-output ^
    %MAIN_FILE%

if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 編譯失敗！
    pause
    exit /b 1
)

echo.
echo [3/4] 統計編譯結果...
for /f %%a in ('powershell -NoProfile -Command "(Get-ChildItem -LiteralPath 'dist\%APP_NAME%.dist' -Recurse -File | Measure-Object -Property Length -Sum).Sum"') do set TOTAL_SIZE=%%a
set TOTAL_SIZE=%TOTAL_SIZE:,=%
set /a SIZE_MB=%TOTAL_SIZE% / 1048576
echo - 編譯後體積: %SIZE_MB% MB

echo.
echo [4/4] 執行瘦身清理（參考 參考專案策略）...
powershell -ExecutionPolicy Bypass -File slim_dist.ps1 -DistPath "dist\%APP_NAME%.dist"

echo.
echo ========================================
echo 編譯完成！
echo ========================================
pause
```

### 五、dist 瘦身指令碼（參考專案級別清理）

**儲存為 `slim_dist.ps1`（和 build_optimized.bat 同目錄）**：

```powershell
param(
    [string]$DistPath
)

$ErrorActionPreference = "Continue"  # 不靜默吞錯：刪除失敗會顯示出來，避免假成功

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "dist 瘦身清理（參考 參考專案策略）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not (Test-Path $DistPath)) {
    Write-Host "[錯誤] 找不到目錄: $DistPath" -ForegroundColor Red
    exit 1
}

# 統計初始體積
$InitialSize = (Get-ChildItem -Path $DistPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "`n初始體積: $([math]::Round($InitialSize, 2)) MB" -ForegroundColor Yellow

# 參考專案特徵：沒有 .pdb, .pyi, __pycache__, test 等
Write-Host "`n[應用 參考專案的清理策略...]" -ForegroundColor Green

# 1. 刪除除錯符號
Write-Host "`n[1/7] 刪除 .pdb 除錯符號..." -ForegroundColor Green
$pdbFiles = Get-ChildItem -Path $DistPath -Recurse -Include *.pdb -File
$pdbSize = ($pdbFiles | Measure-Object -Property Length -Sum).Sum / 1MB
if ($pdbFiles.Count -gt 0) {
    $pdbFiles | Remove-Item -Force
    Write-Host "  刪除 $($pdbFiles.Count) 個檔案，節省 $([math]::Round($pdbSize, 2)) MB"
} else {
    Write-Host "  未發現 .pdb 檔案（已最佳化）" -ForegroundColor Gray
}

# 2. 刪除型別提示
Write-Host "`n[2/7] 刪除 .pyi 型別提示..." -ForegroundColor Green
$pyiFiles = Get-ChildItem -Path $DistPath -Recurse -Include *.pyi -File
$pyiSize = ($pyiFiles | Measure-Object -Property Length -Sum).Sum / 1MB
if ($pyiFiles.Count -gt 0) {
    $pyiFiles | Remove-Item -Force
    Write-Host "  刪除 $($pyiFiles.Count) 個檔案，節省 $([math]::Round($pyiSize, 2)) MB"
} else {
    Write-Host "  未發現 .pyi 檔案（已最佳化）" -ForegroundColor Gray
}

# 3. 刪除 __pycache__
Write-Host "`n[3/7] 刪除 __pycache__ 快取..." -ForegroundColor Green
$pycacheDirs = Get-ChildItem -Path $DistPath -Recurse -Directory -Filter "__pycache__"
$pycacheSize = 0
foreach ($dir in $pycacheDirs) {
    $size = (Get-ChildItem -Path $dir.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $pycacheSize += $size
    Remove-Item -Path $dir.FullName -Recurse -Force
}
if ($pycacheDirs.Count -gt 0) {
    Write-Host "  刪除 $($pycacheDirs.Count) 個目錄，節省 $([math]::Round($pycacheSize / 1MB, 2)) MB"
} else {
    Write-Host "  未發現 __pycache__（已最佳化）" -ForegroundColor Gray
}

# 4. 刪除測試目錄
Write-Host "`n[4/7] 刪除 test/tests 測試目錄..." -ForegroundColor Green
$testDirs = Get-ChildItem -Path $DistPath -Recurse -Directory | Where-Object { $_.Name -match '^tests?$' }
$testSize = 0
foreach ($dir in $testDirs) {
    $size = (Get-ChildItem -Path $dir.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $testSize += $size
    Remove-Item -Path $dir.FullName -Recurse -Force
}
if ($testDirs.Count -gt 0) {
    Write-Host "  刪除 $($testDirs.Count) 個目錄，節省 $([math]::Round($testSize / 1MB, 2)) MB"
} else {
    Write-Host "  未發現測試目錄（已最佳化）" -ForegroundColor Gray
}

# 5. 刪除文件和示例
Write-Host "`n[5/7] 刪除 docs/examples 文件目錄..." -ForegroundColor Green
$docDirs = Get-ChildItem -Path $DistPath -Recurse -Directory | Where-Object { $_.Name -match '^(docs|examples|samples|demo)$' }
$docSize = 0
foreach ($dir in $docDirs) {
    $size = (Get-ChildItem -Path $dir.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $docSize += $size
    Remove-Item -Path $dir.FullName -Recurse -Force
}
if ($docDirs.Count -gt 0) {
    Write-Host "  刪除 $($docDirs.Count) 個目錄，節省 $([math]::Round($docSize / 1MB, 2)) MB"
} else {
    Write-Host "  未發現文件目錄（已最佳化）" -ForegroundColor Gray
}

# 6. 刪除 .pyc 檔案
Write-Host "`n[6/7] 刪除 .pyc 位元組碼..." -ForegroundColor Green
$pycFiles = Get-ChildItem -Path $DistPath -Recurse -Include *.pyc -File
$pycSize = ($pycFiles | Measure-Object -Property Length -Sum).Sum / 1MB
if ($pycFiles.Count -gt 0) {
    $pycFiles | Remove-Item -Force
    Write-Host "  刪除 $($pycFiles.Count) 個檔案，節省 $([math]::Round($pycSize, 2)) MB"
} else {
    Write-Host "  未發現 .pyc 檔案（已最佳化）" -ForegroundColor Gray
}

# 7. 精簡 .dist-info 後設資料
Write-Host "`n[7/7] 精簡 .dist-info 後設資料..." -ForegroundColor Green
$distInfoDirs = Get-ChildItem -Path $DistPath -Recurse -Directory -Filter "*.dist-info"
$removedCount = 0
$removedSize = 0
foreach ($infoDir in $distInfoDirs) {
    # 僅刪安裝期記賬檔案；保留 METADATA 與 entry_points.txt（執行期被 importlib.metadata 讀取，刪除會破壞外掛發現）
    $filesToRemove = @("RECORD", "INSTALLER", "direct_url.json")
    foreach ($fileName in $filesToRemove) {
        $file = Join-Path $infoDir.FullName $fileName
        if (Test-Path $file) {
            $size = (Get-Item $file).Length
            $removedSize += $size
            Remove-Item $file -Force
            $removedCount++
        }
    }
}
if ($removedCount -gt 0) {
    Write-Host "  刪除 $removedCount 個後設資料檔案，節省 $([math]::Round($removedSize / 1MB, 2)) MB"
} else {
    Write-Host "  未發現可清理的後設資料（已最佳化）" -ForegroundColor Gray
}

# 統計最終體積
$FinalSize = (Get-ChildItem -Path $DistPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
$SavedSize = $InitialSize - $FinalSize
$SavedPercent = if ($InitialSize -gt 0) { ($SavedSize / $InitialSize) * 100 } else { 0 }

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "清理完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "初始體積: $([math]::Round($InitialSize, 2)) MB" -ForegroundColor Yellow
Write-Host "最終體積: $([math]::Round($FinalSize, 2)) MB" -ForegroundColor Green
Write-Host "節省空間: $([math]::Round($SavedSize, 2)) MB ($([math]::Round($SavedPercent, 1))%)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 對比 參考專案
Write-Host "[對比參考]" -ForegroundColor Yellow
Write-Host "參考專案總體積: 323 MB (包含 PyQt, OpenCV, Playwright 等重量級庫)" -ForegroundColor Gray
Write-Host "如果你的專案是純 Tkinter + 標準庫，目標應該在 80-150 MB" -ForegroundColor Gray
```

**預期效果**：節省 **15-30%** 體積

### 六、DLL 依賴分析工具

**儲存為 `analyze_dlls.py`（用於找出體積大戶）**：

```python
"""
DLL 依賴分析工具
參考 參考專案的 DLL 管理策略，幫助識別體積大戶和最佳化建議
"""
import sys
from pathlib import Path

def analyze_dlls(dist_path: str):
    """分析 dist 目錄中的 DLL 依賴"""
    dist_dir = Path(dist_path)

    if not dist_dir.exists():
        print(f"[錯誤] 目錄不存在: {dist_path}")
        return

    print("=" * 70)
    print("DLL 依賴分析（參考 參考專案策略）")
    print("=" * 70)

    # 收集所有 DLL
    dll_files = list(dist_dir.rglob("*.dll"))

    if not dll_files:
        print("\n未發現 DLL 檔案")
        return

    # 按大小排序
    dll_data = [(dll, dll.stat().st_size) for dll in dll_files]
    dll_data.sort(key=lambda x: x[1], reverse=True)

    total_size = sum(size for _, size in dll_data)

    print(f"\n總 DLL 數量: {len(dll_files)}")
    print(f"總 DLL 體積: {total_size / 1024 / 1024:.2f} MB\n")

    # 參考專案對比
    print("[對比參考] 參考專案的 DLL 情況:")
    print("  - 總數量: 71 個")
    print("  - 總體積: 93.23 MB")
    print("  - 最大的: libopenblas (26.85 MB), opengl32sw (15.25 MB)\n")

    # 分析大於 3MB 的 DLL
    large_dlls = [(dll, size) for dll, size in dll_data if size > 3 * 1024 * 1024]

    if large_dlls:
        print("=" * 70)
        print("WARNING:  大於 3MB 的 DLL（需重點關注）")
        print("=" * 70)

        for dll, size in large_dlls:
            size_mb = size / 1024 / 1024
            relative_path = dll.relative_to(dist_dir)
            name_lower = dll.name.lower()

            print(f"\n{size_mb:8.2f} MB  {dll.name}")
            print(f"           位置: {relative_path.parent}")

            # 最佳化建議
            suggestions = get_optimization_suggestion(name_lower)
            if suggestions:
                for suggestion in suggestions:
                    print(f"            {suggestion}")

    # 檢查冗餘 DLL
    print("\n" + "=" * 70)
    print(" 冗餘檢查")
    print("=" * 70)

    # 檢查除錯版本
    debug_dlls = [dll for dll, _ in dll_data if dll.stem.endswith('d')]
    if debug_dlls:
        print(f"\nWARNING:  發現 {len(debug_dlls)} 個除錯版本 DLL（可以刪除）:")
        for dll in debug_dlls:
            print(f"  - {dll.name}")
    else:
        print("\nPASS: 未發現除錯版本 DLL（已最佳化）")

    # VC++ Runtime
    vc_runtimes = [dll for dll, _ in dll_data if 'vcruntime' in dll.name.lower() or 'msvcp' in dll.name.lower()]
    if vc_runtimes:
        print(f"\n[VC++ Runtime 庫] 發現 {len(vc_runtimes)} 個:")
        for dll in vc_runtimes:
            size_mb = dll.stat().st_size / 1024 / 1024
            print(f"  - {dll.name} ({size_mb:.2f} MB)")
        print("   這些是必需的，參考專案也包含了這些檔案")

    # 全部 DLL 列表
    print("\n" + "=" * 70)
    print(" 完整 DLL 列表（按體積排序，前 20）")
    print("=" * 70)
    print(f"\n{'體積 (MB)':>10}  {'檔名':<30}  位置")
    print("-" * 70)

    for dll, size in dll_data[:20]:
        size_mb = size / 1024 / 1024
        relative_path = dll.relative_to(dist_dir)
        location = str(relative_path.parent) if relative_path.parent != Path('.') else "根目錄"
        print(f"{size_mb:10.2f}  {dll.name:<30}  {location}")

    if len(dll_data) > 20:
        remaining_size = sum(size for _, size in dll_data[20:]) / 1024 / 1024
        print(f"... 還有 {len(dll_data) - 20} 個 DLL，共 {remaining_size:.2f} MB")


def get_optimization_suggestion(dll_name: str) -> list:
    """根據 DLL 名稱給出最佳化建議"""
    suggestions = []

    if "openblas" in dll_name or "mkl" in dll_name:
        suggestions.append("數學運算庫，參考專案的 libopenblas 有 26.85 MB")
        suggestions.append("如不需要高效能運算可考慮輕量版")

    elif "opencv" in dll_name or "ffmpeg" in dll_name:
        suggestions.append("OpenCV 相關，參考專案的 opencv_videoio_ffmpeg 有 18.48 MB")
        suggestions.append("考慮用 opencv-python-headless")

    elif "qt5" in dll_name or "qt6" in dll_name or "pyside" in dll_name:
        suggestions.append("Qt 庫，參考專案的 Qt5Core 有 5.13 MB")
        suggestions.append("可排除不需要的模組（WebEngine, 3D, Charts）")

    elif "opengl" in dll_name and "sw" in dll_name:
        suggestions.append("OpenGL 軟體渲染器，參考專案保留了 15.25 MB")
        suggestions.append("通常可以刪除（使用硬體渲染）")

    elif "d3dcompiler" in dll_name:
        suggestions.append("DirectX 編譯器，參考專案有 3.53 MB")

    elif "mfc140" in dll_name:
        suggestions.append("MFC 庫，參考專案有 4.89 MB")

    return suggestions


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python analyze_dlls.py <dist目錄路徑>")
        print("示例: python analyze_dlls.py dist/main.dist")
        sys.exit(1)

    analyze_dlls(sys.argv[1])
```

**使用方法**：
```bash
python analyze_dlls.py dist/你的軟體名.dist
```

---

## 完整最佳化工作流

### 步驟 1：修改編譯指令碼配置

編輯 `build_optimized.bat`，修改這 3 行：

```batch
set APP_NAME=你的軟體名      REM 改成實際名稱
set MAIN_FILE=main.py        REM 你的主程式檔案
set ICON_FILE=icon.ico       REM 你的圖示檔案
```

### 步驟 2：一鍵編譯+瘦身

```bash
# 在專案根目錄執行
build_optimized.bat
```

### 步驟 3：分析 DLL 依賴

```bash
python analyze_dlls.py dist/你的軟體名.dist
```

### 步驟 4：根據分析結果最佳化

**如果用了 OpenCV** → 改用無頭版
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

**如果用了 Qt** → 排除不需要的模組
```batch
# 在編譯命令中新增
--nofollow-import-to=PyQt5.QtWebEngine,PyQt5.Qt3D,PyQt5.QtCharts
```

**刪除軟體渲染器**（如果不需要）
```powershell
# 在 dist 目錄執行
Remove-Item "opengl32sw.dll" -Force
```

---

## VC++ 執行庫處理方案

### 方案一：靜態連結（推薦）
```bash
nuitka --static-libpython=yes ...
```

### 方案二：捆綁執行庫安裝（商業釋出推薦）
在 Inno Setup 指令碼中新增：

```iss
; WARNING: VC++ 執行庫架構必須與 Python/Nuitka 構建架構一致。
; 本 skill 推薦 32 位 Python，故預設捆綁 vc_redist.x86.exe；
; 若用 64 位 Python 編譯，請把下面兩處改為 vc_redist.x64.exe。
[Files]
Source: "{#MySourceDir}\..\vc_redist.x86.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Run]
Filename: "{tmp}\vc_redist.x86.exe"; Parameters: "/quiet /norestart"; StatusMsg: "正在安裝執行庫..."; Flags: waituntilterminated
```

> 下載地址：[Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

---

## Inno Setup 指令碼模板（商業終極版）

```iss
; =====================================================================
;  WARNING: 商業級 Python 安裝指令碼 (Inno Setup 6.x)
;  特性：LZMA2 極限壓縮 | 全中文 | 完整後設資料 | 無殘留解除安裝
;  參考：參考專案(323 MB, LZMA2 壓縮)
; =====================================================================

; --- 1. 引數定義 ---
#define MyAppName        "{{APP_NAME}}"
#define MyAppVersion     "{{APP_VERSION}}"
#define MyAppPublisher   "{{PUBLISHER}}"
#define MyAppURL         "{{APP_URL}}"
#define MyAppExeName     "{{EXE_NAME}}"
#define MySourceDir      "{{SOURCE_DIR}}"
#define MyOutputDir      "{{OUTPUT_DIR}}"
;#define MyIconPath      "{{ICON_PATH}}"

[Setup]
; --- 身份識別 ---
AppId={{GENERATE_RANDOM_GUID}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; --- 安裝路徑與許可權 ---
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=no
PrivilegesRequired=admin

; --- 輸出設定 ---
OutputDir={#MyOutputDir}
OutputBaseFilename=Setup_{#MyAppName}_v{#MyAppVersion}

; --- 視覺體驗 ---
WizardStyle=modern
#ifdef MyIconPath
SetupIconFile={#MyIconPath}
UninstallDisplayIcon={app}\{#MyAppExeName}
#endif

; ---  核心壓縮 (參考 參考專案) ---
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; --- 架構 ---
; 注意：僅 64 位 Python 構建才設此項。本 skill 推薦 32 位 Python——
; 32 位構建請保持註釋，使應用按 32 位安裝並與上面捆綁的 vc_redist.x86.exe 匹配。
; 僅當用 64 位 Python 編譯時才取消註釋。
;ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"

[Icons]
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\解除安裝 {#MyAppName}"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
```

---

## 佔位符說明

| 佔位符 | 說明 | 示例值 |
|--------|------|--------|
| `{{APP_NAME}}` | 軟體顯示名稱 | `紅墨批註` |
| `{{APP_VERSION}}` | 版本號 | `1.0.0` |
| `{{PUBLISHER}}` | 釋出者/公司名 | `MyCompany` |
| `{{APP_URL}}` | 官網地址 | `https://example.com` |
| `{{EXE_NAME}}` | 主程式檔名 | `RedInk.exe` |
| `{{SOURCE_DIR}}` | Nuitka dist 資料夾路徑 | `D:\project\dist\RedInk.dist` |
| `{{OUTPUT_DIR}}` | 安裝包輸出路徑 | `D:\project\output` |
| `{{ICON_PATH}}` | 圖示檔案路徑 | `D:\project\icon.ico` |
| `{{GENERATE_RANDOM_GUID}}` | **需生成唯一GUID** | 使用 Inno Setup "Tools > Generate GUID" |

---

## 常見問題 (FAQ)

### Q1: 安裝後雙擊程式無反應？
1. 開啟 CMD，手動執行 exe 檢視錯誤資訊
2. 檢查是否缺少 VC++ 執行庫
3. 檢查 Nuitka 編譯是否成功

### Q2: 安裝包體積過大？
**最佳化方法**：
1. 使用 32 位 Python 編譯（節省 20-30%）
2. 應用 參考專案的模組排除清單
3. 啟用 Anti-Bloat 外掛
4. 執行 dist 資料夾瘦身指令碼
5. 分析 DLL，移除不必要的大檔案

### Q3: 防毒軟體誤報？
**解決方案**：
- 提交到主流防毒廠商進行白名單申請
- 購買程式碼簽名證書（推薦：Sectigo, DigiCert）
- 避免使用 UPX 壓縮

### Q4: 安裝時提示 Windows 已保護你的電腦？
- 購買 EV 程式碼簽名證書（可立即獲得信任）
- 普通程式碼簽名證書需要積累安裝量後逐漸獲得信任

---

## 實戰問題處理記錄（更新 2026-02-07）

- **安裝後提示缺少 python3xx.dll**：必須使用 Nuitka `--standalone`；確認 dist 記憶體在該 dll；不要打單檔案版。
- **安裝後點選無反應**：GUI 啟動期可能被重依賴阻塞；將重依賴延遲到"開始匯出"再 import；新增日誌排查。
- **Nuitka + MinGW 在非 ASCII 路徑報錯**：把原始碼複製到 ASCII 目錄再編譯；設定 `PYTHONIOENCODING=utf-8`。
- **Inno Setup 警告 `x64` 已棄用（僅 64 位構建需要 64 位安裝模式時）**：改為 `ArchitecturesInstallIn64BitMode=x64compatible`；32 位構建無需此項。
- **`--disable-console` 已廢棄**：改用 `--windows-console-mode=disable`。
- **dist 出現 `_nuitka_temp.exe`**：在 [Files] 中排除它。

---

## 最佳化效果預期

| 最佳化組合 | 體積減少 | 啟動提升 | 風險等級 |
|----------|----------|----------|----------|
| 基礎編譯 | 基準 | 基準 | 無 |
| + `--lto=yes` | 5-10% | 10-20% | PASS: 無 |
| + anti-bloat | 15-25% | - | PASS: 無 |
| + 模組排除 | 20-35% | 5% | PASS: 無 |
| + dist 瘦身 | 25-40% | - | PASS: 無 |
| + 32 位編譯 | 40-60% | - | PASS: 無 |
| **全部組合** | **45-65%** | **15-25%** | PASS: **無風險** |

> WARNING: **不建議使用 UPX 壓縮**，雖然能進一步減小體積，但極易觸發防毒軟體誤報。

---

**基於 參考專案實戰經驗最佳化，助你打造商業級安裝包！**
