---
name: memory-forensics
description: 精通記憶體鑑識技術，包含用 Volatility 與相關工具做記憶體取得、行程分析與 artifact 擷取。在分析記憶體傾印、調查資安事件，或從 RAM 擷取檔做惡意程式分析時使用。
---

# Memory Forensics

取得、分析記憶體傾印並從中擷取 artifact 的完整技術，用於事件應變與惡意程式分析。

## When to Use This Skill

- 在事件應變或入侵調查期間做記憶體分析
- 從 RAM 擷取檔中抽出惡意程式 artifact（行程、被注入的程式碼、網路連線）
- 在關機前，從運作中的 Windows/Linux/macOS 系統取得揮發性記憶體
- 用 Volatility 3 / Rekall 對記憶體傾印做初步分類
- 從行程記憶體中還原憑證、瀏覽器 session 或開啟中的檔案

## Memory Acquisition

### Live Acquisition Tools

#### Windows

```powershell
# WinPmem (Recommended)
winpmem_mini_x64.exe memory.raw

# DumpIt
DumpIt.exe

# Belkasoft RAM Capturer
# GUI-based, outputs raw format

# Magnet RAM Capture
# GUI-based, outputs raw format
```

#### Linux

```bash
# LiME (Linux Memory Extractor)
sudo insmod lime.ko "path=/tmp/memory.lime format=lime"

# /dev/mem (limited, requires permissions)
sudo dd if=/dev/mem of=memory.raw bs=1M

# /proc/kcore (ELF format)
sudo cp /proc/kcore memory.elf
```

#### macOS

```bash
# osxpmem
sudo ./osxpmem -o memory.raw

# MacQuisition (commercial)
```

### Virtual Machine Memory

```bash
# VMware: .vmem file is raw memory
cp vm.vmem memory.raw

# VirtualBox: Use debug console
vboxmanage debugvm "VMName" dumpvmcore --filename memory.elf

# QEMU
virsh dump <domain> memory.raw --memory-only

# Hyper-V
# Checkpoint contains memory state
```

## Detailed section: Volatility 3 Framework

這段原本是這份 SKILL.md 裡一段 2680 bytes 的內容，為了符合 Codex 對 skill 本文 8 KB 的上限，已搬到 `references/details.md`。

## Analysis Workflows

### Malware Analysis Workflow

```bash
# 1. Initial process survey
vol -f memory.raw windows.pstree > processes.txt
vol -f memory.raw windows.pslist > pslist.txt

# 2. Network connections
vol -f memory.raw windows.netscan > network.txt

# 3. Detect injection
vol -f memory.raw windows.malfind > malfind.txt

# 4. Analyze suspicious processes
vol -f memory.raw windows.dlllist --pid <PID>
vol -f memory.raw windows.handles --pid <PID>

# 5. Dump suspicious executables
vol -f memory.raw windows.pslist --pid <PID> --dump

# 6. Extract strings from dumps
strings -a pid.<PID>.exe > strings.txt

# 7. YARA scanning
vol -f memory.raw windows.yarascan --yara-rules malware.yar
```

### Incident Response Workflow

```bash
# 1. Timeline of events
vol -f memory.raw windows.timeliner > timeline.csv

# 2. User activity
vol -f memory.raw windows.cmdline
vol -f memory.raw windows.consoles

# 3. Persistence mechanisms
vol -f memory.raw windows.registry.printkey \
    --key "Software\Microsoft\Windows\CurrentVersion\Run"

# 4. Services
vol -f memory.raw windows.svcscan

# 5. Scheduled tasks
vol -f memory.raw windows.scheduled_tasks

# 6. Recent files
vol -f memory.raw windows.filescan | grep -i "recent"
```

## Data Structures

### Windows Process Structures

```c
// EPROCESS (Executive Process)
typedef struct _EPROCESS {
    KPROCESS Pcb;                    // Kernel process block
    EX_PUSH_LOCK ProcessLock;
    LARGE_INTEGER CreateTime;
    LARGE_INTEGER ExitTime;
    // ...
    LIST_ENTRY ActiveProcessLinks;   // Doubly-linked list
    ULONG_PTR UniqueProcessId;       // PID
    // ...
    PEB* Peb;                        // Process Environment Block
    // ...
} EPROCESS;

// PEB (Process Environment Block)
typedef struct _PEB {
    BOOLEAN InheritedAddressSpace;
    BOOLEAN ReadImageFileExecOptions;
    BOOLEAN BeingDebugged;           // Anti-debug check
    // ...
    PVOID ImageBaseAddress;          // Base address of executable
    PPEB_LDR_DATA Ldr;              // Loader data (DLL list)
    PRTL_USER_PROCESS_PARAMETERS ProcessParameters;
    // ...
} PEB;
```

### VAD (Virtual Address Descriptor)

```c
typedef struct _MMVAD {
    MMVAD_SHORT Core;
    union {
        ULONG LongFlags;
        MMVAD_FLAGS VadFlags;
    } u;
    // ...
    PVOID FirstPrototypePte;
    PVOID LastContiguousPte;
    // ...
    PFILE_OBJECT FileObject;
} MMVAD;

// Memory protection flags
#define PAGE_EXECUTE           0x10
#define PAGE_EXECUTE_READ      0x20
#define PAGE_EXECUTE_READWRITE 0x40
#define PAGE_EXECUTE_WRITECOPY 0x80
```

## Detection Patterns

### Process Injection Indicators

```python
# Malfind indicators
# - PAGE_EXECUTE_READWRITE protection (suspicious)
# - MZ header in non-image VAD region
# - Shellcode patterns at allocation start

# Common injection techniques
# 1. Classic DLL Injection
#    - VirtualAllocEx + WriteProcessMemory + CreateRemoteThread

# 2. Process Hollowing
#    - CreateProcess (SUSPENDED) + NtUnmapViewOfSection + WriteProcessMemory

# 3. APC Injection
#    - QueueUserAPC targeting alertable threads

# 4. Thread Execution Hijacking
#    - SuspendThread + SetThreadContext + ResumeThread
```

### Rootkit Detection

```bash
# Compare process lists
vol -f memory.raw windows.pslist > pslist.txt
vol -f memory.raw windows.psscan > psscan.txt
diff pslist.txt psscan.txt  # Hidden processes

# Check for DKOM (Direct Kernel Object Manipulation)
vol -f memory.raw windows.callbacks

# Detect hooked functions
vol -f memory.raw windows.ssdt  # System Service Descriptor Table

# Driver analysis
vol -f memory.raw windows.driverscan
vol -f memory.raw windows.driverirp
```

### Credential Extraction

```bash
# Dump hashes (requires hivelist first)
vol -f memory.raw windows.hashdump

# LSA secrets
vol -f memory.raw windows.lsadump

# Cached domain credentials
vol -f memory.raw windows.cachedump

# Mimikatz-style extraction
# Requires specific plugins/tools
```

## YARA Integration

### Writing Memory YARA Rules

```yara
rule Suspicious_Injection
{
    meta:
        description = "Detects common injection shellcode"

    strings:
        // Common shellcode patterns
        $mz = { 4D 5A }
        $shellcode1 = { 55 8B EC 83 EC }  // Function prologue
        $api_hash = { 68 ?? ?? ?? ?? 68 ?? ?? ?? ?? E8 }  // Push hash, call

    condition:
        $mz at 0 or any of ($shellcode*)
}

rule Cobalt_Strike_Beacon
{
    meta:
        description = "Detects Cobalt Strike beacon in memory"

    strings:
        $config = { 00 01 00 01 00 02 }
        $sleep = "sleeptime"
        $beacon = "%s (admin)" wide

    condition:
        2 of them
}
```

### Scanning Memory

```bash
# Scan all process memory
vol -f memory.raw windows.yarascan --yara-rules rules.yar

# Scan specific process
vol -f memory.raw windows.yarascan --yara-rules rules.yar --pid 1234

# Scan kernel memory
vol -f memory.raw windows.yarascan --yara-rules rules.yar --kernel
```

## String Analysis

### Extracting Strings

```bash
# Basic string extraction
strings -a memory.raw > all_strings.txt

# Unicode strings
strings -el memory.raw >> all_strings.txt

# Targeted extraction from process dump
vol -f memory.raw windows.memmap --pid 1234 --dump
strings -a pid.1234.dmp > process_strings.txt

# Pattern matching
grep -E "(https?://|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})" all_strings.txt
```

### FLOSS for Obfuscated Strings

```bash
# FLOSS extracts obfuscated strings
floss malware.exe > floss_output.txt

# From memory dump
floss pid.1234.dmp
```

## Best Practices

### Acquisition Best Practices

1. **降到最小足跡**：使用輕量的取得工具
2. **記錄所有事情**：記下擷取的時間、工具與 hash
3. **驗證完整性**：擷取完立刻對記憶體傾印做 hash
4. **保管鏈**：維持正確的鑑識處理程序

### Analysis Best Practices

1. **先看全貌**：先有整體概況，再深入細節
2. **交叉比對**：同一份資料用多個 plugin 查
3. **時間軸關聯**：把記憶體的發現和磁碟/網路的紀錄對照
4. **記錄發現**：留下詳細的筆記和截圖
5. **驗證結果**：用多種方法確認發現

### Common Pitfalls

- **資料過期**：記憶體是揮發性的，要盡快分析
- **傾印不完整**：確認傾印大小符合預期的 RAM 容量
- **符號問題**：確保使用對應該 OS 版本的符號檔
- **Smear**：取得過程中記憶體可能已經變動
- **加密**：有些資料在記憶體中可能是加密的
