---
name: anti-reversing-techniques
description: 了解軟體分析時會遇到的反逆向、混淆和保護技術。分析惡意程式的規避技術、為 CTF 題目實作反除錯保護、逆向被加殼的 binary，或建構需要偵測虛擬化環境的資安研究工具時，使用這個 skill。
---

> **僅限授權使用**：這個 skill 包含雙重用途的資安技術。進行任何繞過或分析之前：
>
> 1. **確認授權**：確認你有軟體擁有者明確的書面許可，或是在合法的資安情境下運作（CTF、授權的滲透測試、惡意程式分析、資安研究）
> 2. **記錄範圍**：確保你的活動在授權所定義的範圍內
> 3. **法律合規**：要知道未經授權繞過軟體保護，可能違反法律（CFAA、DMCA 反規避條款等）
>
> **合法的使用情境**：惡意程式分析、授權的滲透測試、CTF 競賽、學術資安研究、分析你自己擁有或有權利的軟體

# 反逆向技術

了解在授權的軟體分析、資安研究和惡意程式分析中會遇到的保護機制。這些知識能幫分析人員繞過保護，完成合法的分析工作。

進階技術請見 [references/advanced-techniques.md](references/advanced-techniques.md)

---

## 輸入 / 輸出

**你要提供的：**

- **Binary 路徑或樣本**：要分析的執行檔、DLL 或韌體映像檔
- **平台**：Windows x86/x64、Linux、macOS、ARM，會影響適用哪些檢查
- **目標**：為動態分析而繞過、辨識保護類型、建構偵測程式碼、為 CTF 而實作

**這個 skill 會產出：**

- **保護辨識**：具名的技術（例如 RDTSC 計時檢查、PEB BeingDebugged），以及它在 binary 中的位置
- **繞過策略**：具體的 patch 位址、hook 點，或讓每個檢查失效的工具指令
- **分析報告**：結構化的發現，列出每一層保護、嚴重程度和建議的繞過方式
- **程式碼成品**：用來繞過或實作檢查的 Python/IDAPython script、GDB 指令序列，或 C stub

---

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。

## 疑難排解

**偵測技術在 x86 上有效，但在 ARM 上沒用**

RDTSC 和 CPUID 只有 x86 才有。在 ARM 上，用 `MRS x0, PMCCNTR_EL0`（需要 kernel PMU 存取權）或 `clock_gettime(CLOCK_MONOTONIC)`。ARM 上沒有 PEB/TEB，要換成 `/proc/self/status`（Linux）或 `task_info`（macOS）。用平台專屬的 API 重建偵測邏輯。

**把合法的除錯器或分析工具誤判成偵測到了**

當 Process Monitor 或防毒軟體的 hook 讓 syscall 延遲變大時，計時檢查會被觸發。在啟動時校準門檻：把受保護的路徑量測 3 次，用 `mean + 3*stddev`。ptrace 檢查的話，結束之前先透過 `/proc/<pid>/comm` 確認 TracerPid 的 comm 名稱：它可能是無關的監控工具，不是除錯器。

**繞過的 patch 造成當機，而不是繼續執行**

在把條件跳轉改成 NOP 之前，先把「偵測到」那個分支完整追蹤一遍。如果它會初始化或釋放之後要用的 heap 狀態，patch 掉跳轉就會跳過那段設定、弄壞狀態。改成把比較的運算元 patch 成預期的「乾淨」值，或是在斷點上用 x64dbg 的「Set condition to always false」，不要去改 byte。

---

## 相關 Skill

- `binary-analysis-patterns`：ELF/PE/Mach-O 的靜態與動態分析工作流程
- `memory-forensics`：process 記憶體的取得、artifact 萃取和即時分析
- `protocol-reverse-engineering`：解碼自訂的二進位協定和加密的網路流量
