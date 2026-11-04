---
name: debugview
description: |
  Sysinternals DebugView CLI (DbgViewCli)，用命令列擷取並分析 Windows 的 usermode 與 kernel-mode 除錯輸出。
  USE FOR: capturing OutputDebugString output, kernel DbgPrint/KdPrint capture, boot-time debug logging, remote debug monitoring, filtering debug output by PID or process name, crash dump analysis, automated debug capture with bounded execution.
  DO NOT USE FOR: non-Windows platforms, application-level logging frameworks (log4j, serilog), Azure Monitor or cloud telemetry, ETW tracing (use WPR/xperf instead), user-mode crash dumps (use WinDbg).
  Triggers: "debug output", "DbgView", "DebugView", "kernel debug", "capture debug logs", "boot logging", "OutputDebugString", "DbgPrint", "KdPrint", "remote debug monitor", "debug capture CLI".
---

# Sysinternals DebugView CLI (DbgViewCli)

命令列介面，用來即時擷取 Windows 應用程式（OutputDebugString）和 kernel-mode driver（DbgPrint/KdPrint）的除錯輸出。
專為 script、自動化，以及 AI agent 驅動的除錯擷取流程設計。

## Installation

DbgViewCli 是獨立的原生 Windows 執行檔（靜態連結，沒有相依套件）。
把 `dbgviewcli.exe` 放進 PATH，或是直接用完整路徑呼叫。

> **SECURITY：執行任何 dbgviewcli binary 之前，一定要先用 `Get-AuthenticodeSignature` 確認它有 Microsoft Corporation 的 Authenticode 簽章。沒簽章或是其他發行者簽的 binary 一律拒絕。**

```bash
# No package manager install — copy binary to a PATH location
copy dbgviewcli.exe C:\Tools\
```

## Requirements

| Requirement | Details |
|-------------|---------|
| OS | Windows Vista 或更新版本（x64、ARM64） |
| Privileges | Win32 擷取用一般使用者即可；kernel/boot 擷取需要 **Administrator** |
| Driver | Kernel 擷取需要 Dbgv.sys driver（會自動解出並載入） |

## Core Workflow

```
1. Detect/status check   →  dbgviewcli --status
2. Start capture          →  dbgviewcli [options]
3. Filter output          →  --filter/--exclude/--pid-filter/--process-filter
4. Bounded execution      →  --duration/--max-lines/--wait-for
5. Output/log results     →  stdout or --log <file>
6. Stop                   →  Ctrl+C or automatic exit on bounds
```

## Command-Line Parameters

### Capture Control

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--capture` | `-c` | 啟用擷取 | on |
| `--no-capture` | | 停用擷取 | |
| `--kernel` | `-k` | 啟用 kernel 除錯輸出（需要 admin） | off |
| `--win32` | `-w` | 啟用 Win32 OutputDebugString 擷取 | on |
| `--global` | `-g` | 啟用全域 Win32 擷取（session 0） | off |
| `--passthrough` | | 讓除錯輸出繼續傳給 debugger | on |
| `--verbose-kernel` | `-v` | 啟用詳細的 kernel 輸出 | off |
| `--pids` | | 在輸出中顯示 process ID | on |

### Filtering

| Parameter | Short | Description |
|-----------|-------|-------------|
| `--filter <pattern>` | `-i` | 包含過濾（以分號分隔的萬用字元） |
| `--exclude <pattern>` | `-e` | 排除過濾（以分號分隔的萬用字元） |
| `--pid-filter <pid>` | | 只顯示特定 PID 的輸出 |
| `--process-filter <name>` | | 只顯示指定名稱 process 的輸出（子字串比對） |

### Bounded Execution (AI-Agent Friendly)

| Parameter | Description |
|-----------|-------------|
| `--duration <seconds>` | N 秒後自動停止 |
| `--max-lines <N>` | 擷取到 N 行後自動停止 |
| `--wait-for <pattern>` | 一直擷取到符合 pattern 為止，然後結束 |
| `--tail <N>` | 緩衝最後 N 行，結束時一次輸出 |
| `--no-banner` | 不顯示版本橫幅（pipe 輸出比較乾淨） |
| `--status` | 輸出機器可讀的狀態後結束 |

### Time Display

| Parameter | Description |
|-----------|-------------|
| `--elapsed` | 從開始算起經過的時間（預設） |
| `--clock` | 實際時鐘時間 HH:MM:SS |
| `--clock-ms` | 含毫秒的實際時鐘時間 HH:MM:SS.mmm |

### Output Format

| Parameter | Description |
|-----------|-------------|
| `--format text` | Tab 分隔的文字（預設） |
| `--format csv` | 逗號分隔值 |
| `--format xml` | XML 元素 |

### Logging

| Parameter | Description |
|-----------|-------------|
| `--log <file>` | 把輸出寫進檔案 |
| `--log-append` | 附加到既有的 log |
| `--log-limit <MB>` | log 檔案大小上限（MB） |
| `--log-wrap` | log 滿了就從頭覆寫 |
| `--log-daily` | 每天一個新的 log 檔 |

### Boot Logging (Requires Admin)

| Parameter | Description |
|-----------|-------------|
| `--boot-enable` | 啟用開機時的 kernel 除錯記錄 |
| `--boot-disable` | 停用開機時的記錄 |
| `--boot-status` | 顯示開機記錄的狀態後結束 |

### Remote Monitoring

| Parameter | Description |
|-----------|-------------|
| `--connect <computer>` | 連線到遠端的 DbgView instance |
| `--disconnect` | 中斷和遠端的連線 |

### Crash Dump & File Operations

| Parameter | Description |
|-----------|-------------|
| `--crashdump <file>` | 分析 crash dump 裡的除錯輸出 |
| `--load <file>` | 載入已儲存的 log 檔 |
| `--save <file>` | 結束時儲存擷取到的輸出 |

### Runtime Control (Inter-Process)

| Parameter | Description |
|-----------|-------------|
| `--pause` | 透過 named event 暫停執行中的 DbgViewCli instance |
| `--resume` | 恢復已暫停的 DbgViewCli instance |
| `--stop` | 讓執行中的 DbgViewCli instance 正常停止 |

### Miscellaneous

| Parameter | Short | Description |
|-----------|-------|-------------|
| `--quit` | `-q` | 結束執行中的 GUI DbgView instance |
| `--accepteula` | | 接受 EULA（寫入 registry key，跳過提示） |
| `--version` | | 顯示版本後結束 |
| `--help` | `-?` | 顯示說明 |

## Usage Examples

### Basic Win32 Capture (bounded)

```bash
# Capture for 30 seconds, no banner, output as text
dbgviewcli --no-banner --duration 30

# Capture until a specific error appears
dbgviewcli --no-banner --wait-for "*ERROR*" --max-lines 10000
```

### Kernel Debug Capture (requires admin)

```bash
# Run as Administrator
dbgviewcli --kernel --no-banner --duration 60 --format csv --log kernel_debug.csv
```

### Process-Specific Filtering

```bash
# Filter by PID
dbgviewcli --no-banner --pid-filter 1234 --duration 10

# Filter by process name
dbgviewcli --no-banner --process-filter "myapp.exe" --max-lines 500
```

### Pattern-Based Filtering

```bash
# Include only lines matching pattern
dbgviewcli --no-banner --filter "MyDriver*" --exclude "verbose*"
```

### Tail Mode (recent context)

```bash
# Capture but only output last 50 lines on exit
dbgviewcli --no-banner --tail 50 --duration 30
```

### Status Check (machine-readable)

```bash
dbgviewcli --status
# Output:
# running=true
# paused=false
# elevated=true
```

### Boot Logging

```bash
# Enable (requires admin, persists across reboot)
dbgviewcli --boot-enable

# Check status
dbgviewcli --boot-status

# Disable
dbgviewcli --boot-disable
```

### Remote Monitoring

```bash
dbgviewcli --connect SERVER01 --no-banner --duration 60
```

### Runtime Control (Pause/Resume/Stop)

```bash
# Pause a running instance from another terminal
dbgviewcli --pause

# Resume the paused instance
dbgviewcli --resume

# Gracefully stop a running instance
dbgviewcli --stop
```

### EULA Acceptance (Unattended)

```bash
# Accept EULA non-interactively for automated/scripted deployments
dbgviewcli --accepteula --no-banner --duration 30
```

## Architecture

| Module | File | Purpose |
|--------|------|---------|
| Main | `dbgviewcli.c` | 進入點、參數解析、擷取迴圈、Ctrl+C handler |
| Capture | `cli_capture.c` | DBWIN 共用記憶體、讀取 kernel driver |
| Driver | `cli_driver.c` | Kernel driver 載入/卸載、權限提升 |
| Filter | `cli_filter.c` | 萬用字元的包含/排除比對 |
| Output | `cli_output.c` | Console 輸出、log 檔、CSV/XML/text 格式 |
| Boot Log | `cli_bootlog.c` | 開機時載入 driver 的 registry 設定 |
| Remote | `cli_remote.c` | 遠端監控用的 TCP socket 連線/讀取 |

## Key Design Decisions

1. **Static CRT linking** — 沒有 DLL 相依，在任何 Windows 系統都能跑
2. **stdout/stderr separation** — 除錯輸出 → stdout；錯誤/狀態 → stderr
3. **Bounded execution** — `--duration`、`--max-lines`、`--wait-for` 保證自動化時一定會結束
4. **Clean output** — `--no-banner` 去掉雜訊，方便 pipe 或 agent 使用
5. **Machine-readable status** — `--status` 輸出 key=value，方便程式檢查
6. **Graceful shutdown** — `SetConsoleCtrlHandler` 確保 Ctrl+C 時能乾淨卸載 driver

## Best Practices

1. **script 或自動化使用時，一律加 `--no-banner`。** 橫幅文字會污染結構化輸出，讓 parser 搞混。
2. **一律用 `--duration`、`--max-lines` 或 `--wait-for` 限制執行範圍。** 不設限的話擷取會一直跑下去。
3. **擷取前先檢查狀態** — 用 `--status` 偵測是不是已經有另一個 instance 在跑。
4. **輸出要給程式解析時，用 `--format csv` 或 `--format xml`。**
5. **優先用 `--pid-filter` 或 `--process-filter`**，不要廣泛擷取，才能減少雜訊。
6. **只在需要時才用 Administrator 執行** — kernel 和開機記錄需要提權，Win32 擷取不用。
7. **組合多個上限比較保險** — `--duration 60 --max-lines 10000` 一起用，哪個先到就先停。
8. **用 `--tail`** 回答「剛剛發生什麼事」這類問題，不要擷取完整歷史。

## Bundled Resources

| Type | File | Purpose |
|------|------|---------|
| Script | `scripts/detect-dbgview.ps1` | 在 PATH 或常見目錄找 dbgviewcli.exe |
| Script | `scripts/capture-wrapper.ps1` | 有參數驗證的安全限時擷取 |
| Script | `scripts/boot-logging-workflow.ps1` | 端到端的開機記錄生命週期管理 |
| Reference | `references/driver-ioctls.md` | Kernel driver 的 IOCTL 代碼與 buffer 結構 |
| Reference | `references/output-formats.md` | Text/CSV/XML 輸出格式規格 |
| Reference | `references/remote-protocol.md` | TCP 遠端監控的 wire protocol |

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| Kernel 擷取出現 "Access denied" | 用 Administrator 執行 |
| Win32 擷取沒有輸出 | 確認目標 app 有用 `OutputDebugString`；檢查有沒有 debugger 掛著 |
| 已經有另一個 instance 在跑 | 用 `--status` 檢查；用 `--quit` 結束既有的 GUI instance |
| 開機記錄沒擷取到東西 | 確認 `--boot-enable` 是用 admin 執行的；driver 必須在 System32\Drivers |
| 遠端連線失敗 | 確認目標機器有執行 DbgView，且遠端功能已在 2020-2030 port 啟用 |
