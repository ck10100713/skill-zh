---
name: agent-security-hardening
description: 針對會處理不受信任內容、呼叫工具、寫入工作區檔案、管理 runtime 識別碼或處理憑證的 AI agent 框架，提供安全強化指引。建構或審查 agent runtime、自主 worker、工具 gateway、記憶服務或多租戶 agent 部署時使用。一般的 web 應用程式安全或攻擊式測試不要用這個。
metadata:
  origin: ECC
---

# Agent 安全強化

強化 agent 把不受信任的資料轉成檔案系統、網路、記憶或工具動作的那些邊界。要針對被審查的框架，產出具體的控管措施和測試；只有 checklist、沒有強制執行證據的，都算不完整。

## 重要

- 把模型輸出、檢索到的內容、工具輸出、記憶和跨 agent 訊息，都當成不受信任的輸入。
- 外部整合預設唯讀，每一項寫入能力要分別授權。
- 就算上游的 prompt 或 schema 已經驗證過某個值，也要在動作邊界再驗證一次。
- 當身分、目的地、所有權或隔離範圍無法證明時，要在產生副作用之前 fail closed。
- 刪除、發布、輪替憑證或其他不可逆的動作之前，真正的工具入口必須針對那個確切的操作和資源範圍，對已驗證的主體做授權，然後要求明確確認或有效且限定範圍的事先核准。證據缺少或無效就擋下動作。
- 硬性上限要用主管需求定義的值，以及從部署設定驗證過的更嚴格的值。兩者都沒定義時，標成「必須決定的事項」，並測試實作會拒絕沒有上限的設定；不要自己編一個看似合理的值。

## 何時啟用

- 建構自主 agent、工具 gateway、記憶服務或 agent 對 agent 的協定
- 審查把模型輸出對應成指令、路徑、URL、憑證或 API 變更的程式碼
- 在長時間執行的 agent process 裡隔離租戶、專案、session 或工作區
- 強化暫存檔、log、工具回應或外部內容的匯入

## 強化流程

### 1. 畫出信任邊界

把每個邊界列成 `source -> parser -> validator -> side effect`。包含使用者的直接輸入、模型輸出、檢索到的文件、記憶、環境變數、工具結果，以及其他 agent 傳來的訊息。

每個副作用都要記錄：

- 授權它的身分和範圍；
- 緊接在它之前執行的確切 validator；
- 最大輸入和輸出大小；
- 產生的稽核證據；
- 操作被中斷時的復原路徑。

每一個寫入、指令、網路變更和憑證使用，都有一個具名的授權邊界時，這個步驟才算完成。

### 2. 驗證識別碼、環境變數值和 URL

對會變成檔名、key、selector 或指令參數的識別碼用白名單。Agent ID 有 issue 定義的硬上限 64 個字元；部署設定可以選更嚴格的正整數上限，但不能調高這個界線：

```python
import re

SAFE_AGENT_ID_CHARS = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_-]*$")
HARD_MAX_AGENT_ID_LENGTH = 64

def require_agent_id(value: object, *, max_length: int) -> str:
    if (
        isinstance(max_length, bool)
        or not isinstance(max_length, int)
        or not 1 <= max_length <= HARD_MAX_AGENT_ID_LENGTH
    ):
        raise RuntimeError("configured agent ID limit must be between 1 and 64")
    if (
        not isinstance(value, str)
        or len(value) > max_length
        or not SAFE_AGENT_ID_CHARS.fullmatch(value)
    ):
        raise ValueError("invalid agent identifier")
    return value
```

當識別碼會變成 CLI 參數時，要透過 argv API 傳入，並在支援的情況下放在指令的 end-of-options 標記之後。字元驗證不能取代參數分隔。

建構 client 之前，要拒絕不存在和只有空白字元的環境變數值：

```python
def require_env(name: str, environ: dict[str, str]) -> str:
    value = environ.get(name)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} is required")
    return value
```

解析 URL，只允許部署需要的 scheme，要求要有 host，拒絕內嵌憑證，而且當 URL 由攻擊者控制時要擋掉私有網路的目的地。每一個對外連線和 redirect 跳轉，都要把連線固定到已驗證的公開位址，或在連線時驗證實際連上的對端位址，這樣 DNS rebinding 才無法越過邊界。帶憑證的請求在附上憑證之前，必須使用 HTTPS 並驗證憑證。停用自動跨 origin 轉發憑證；當 scheme 或 origin 改變時，要移除憑證並重新授權新目的地，或拒絕這個 redirect。每一跳都要重新驗證目的地、連線位址和傳輸層。

測試要證明：空值、過長、格式錯誤、穿越路徑形式、帶憑證和未授權目的地的值，都會在任何副作用之前被拒絕，而且 DNS rebinding 和跨 origin redirect 無法把憑證帶給未核准的對端，這個步驟才算完成。

### 3. 限制檔案系統存取

在串接路徑之前，要拒絕使用者控制的絕對路徑和穿越元件。在每個平台上都要拒絕 Windows 不安全的元件，讓行為保持可攜：保留的裝置名稱（`CON`、`NUL`、`COM1`、`LPT1`，包含帶副檔名的形式，例如 `nul.txt`）、以點或空白結尾的名稱（Win32 會把它們去掉），還有 `:`（相對於磁碟機的路徑，或 NTFS alternate data stream 語法，例如 `report.txt:ads`）。把工作區和候選路徑都 resolve 之後，再證明候選路徑被包含在工作區內：

```python
import re
from pathlib import Path

WINDOWS_RESERVED_NAME = re.compile(
    r"(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(\..*)?",
    re.IGNORECASE,
)

def workspace_path(workspace: Path, requested: str) -> Path:
    # 檢查元件之前，先一致地處理兩種平台的分隔符號。
    relative = Path(requested.replace("\\", "/"))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("path must be workspace-relative")
    for part in relative.parts:
        if ":" in part or part.endswith((".", " ")) or WINDOWS_RESERVED_NAME.fullmatch(part):
            raise ValueError("path component is not portable")

    root = workspace.resolve(strict=True)
    candidate = (root / relative).resolve(strict=False)
    if not candidate.is_relative_to(root):
        raise ValueError("path escapes workspace")
    return candidate
```

包含性檢查沒辦法消除 symlink race。對敏感的寫入，在平台支援的情況下，要相對於受信任的目錄 handle 來開啟、拒絕 symlink 目標、以獨占方式建立檔案，並在開啟後驗證擁有者和權限。

測試涵蓋了同名前綴的兄弟路徑、巢狀 `..`、絕對路徑、symlink 逃逸、保留的裝置名稱、結尾的點或空白、alternate data stream 語法，以及一個合法的巢狀工作區路徑，這個步驟才算完成。

### 4. 保護暫存資料和憑證

- 敏感檔案用只有擁有者能存取的權限建立，例如 `0o600`；私有目錄用 `0o700`。
- 憑證或租戶資料，優先用使用者私有的 runtime 目錄，不要用共用的暫存目錄。
- 用原子操作建立不可預測的名稱；不要先檢查再建立。
- 在 `finally` 裡移除暫存資料，清理失敗時要保留一份已遮蔽的錯誤紀錄。
- 不要讓 secret 出現在指令參數、模型 context、log、trace、例外訊息和工具回應裡。
- 透過平台的 secret store 或限定範圍的環境變數注入來傳遞 secret，並輪替已外洩的憑證。
- 把歸零處理當成盡力而為：可變的位元組緩衝區可以被覆寫，但不可變的語言字串無法可靠地抹除。

檔案權限檢查、強制錯誤的清理測試和 log 擷取測試都顯示 secret 的值絕對不會留存在核准的邊界之外，這個步驟才算完成。

### 5. 限制並清理工具輸出

讀取工具輸出時要設位元組上限，不要收集沒有上限的串流。保留結構化欄位、移除不允許的控制字元，並附加明確的截斷標記和原始位元組數。後續需要做鑑識比對時，要保留內容的 hash。

不要把格式錯誤的輸出悄悄變成空的成功值。要回傳有型別的失敗，指出產生它的工具、邊界和驗證原因，而且不要回顯敏感內容。

過大的輸出、無效的編碼、終端機控制序列、格式錯誤的結構化資料，和正常的回應，都有確定性的測試，這個步驟才算完成。

## 驗證關卡

在宣稱框架已強化之前，要透過它真正的入口驗證以下所有行為：

1. 不受信任的指令仍然只是資料，無法觸發工具或寫入。
2. 沒有「操作加資源」授權，也沒有確認或限定範圍事先核准的不可逆動作，不會留下任何副作用。
3. 跨租戶和跨工作區的識別碼，會在動作邊界被拒絕。
4. 穿越路徑和 symlink 逃逸的嘗試，不會改變檔案系統。
5. 強制失敗後，不會留下帶憑證的暫存檔或 log。
6. 過大或格式錯誤的工具輸出，會回傳明確且有界的錯誤。

要回報使用的指令、結束狀態、被拒絕的輸入，以及觀察到副作用不存在。只用 mock 的測試，無法證明作業系統的權限、symlink 處理、subprocess 隔離或網路對外的控管。

## 常見問題

### 驗證只存在於 prompt 裡

Prompt 指令只是建議。把同樣的不變條件搬進緊接在副作用之前的確定性程式碼，並測試一個違反它的模型回應。

### 正規化後的路徑仍然逃逸

字串前綴檢查會把 `/work/app` 和 `/work/application` 這種兄弟路徑搞混。要 resolve 路徑，並用以路徑元件為單位的包含檢查，然後另外測試 symlink。

### 遮蔽發生在記錄之後

要在值進入 logger、tracer、例外或模型 context 之前就遮蔽。加一個用哨兵 secret 的擷取測試，並斷言所有輸出管道裡都沒有那個哨兵。

## 何時不要用

- 一般應用程式的驗證、授權、SQL injection、XSS、CSRF 和 API 安全，用 `security-review`。
- 整個 repo 的自動化漏洞掃描，用 `security-scan`。
- 主機、容器、防火牆或雲端的強化，用基礎設施專屬的指引。
- 不要把這個 skill 用在滲透測試、exploit 開發或未授權的存取。

## 相關 Skill

- `agent-harness-construction`
- `security-review`
- `security-scan`
