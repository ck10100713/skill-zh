---
name: storage-analyzer
description: >
  macOS / Windows 只讀儲存分析助手（自動識別系統）。掃描整機磁碟佔用，找出
  佔空間大戶，把每一項分成 🟢可自動清理 / 🟡需人工判斷 / 🔴謹慎清理 三級並給出
  可執行處置方案，生成排版精美、可摺疊、命令可一鍵複製的互動式 HTML 報告，並可
  起本地服務在網頁上一鍵刪除（移廢紙簍/直接刪）。掃描全程只讀。務必在以下場景
  使用：使用者說"儲存分析""磁碟滿了""C盤/硬碟滿了""空間不夠""清理空間"
  "清理磁碟""佔空間""哪些東西佔地方""幫我看看儲存""看一下電腦儲存/空間"
  "儲存空間""電腦空間不夠""記憶體滿了/不夠/不足""看下記憶體/儲存"（中文口語裡
  "記憶體"常指儲存空間）"storage analysis""disk cleanup""清快取""磁碟清理"；
  或使用者抱怨電腦沒空間、想知道什麼東西吃硬碟、想要清理建議時。注意：若使用者明確
  指執行記憶體/RAM（如"哪個程序吃記憶體""記憶體佔用高"想看活動監視器），那是 RAM
  不是儲存，不屬於本 skill。
---

# Storage Analyzer

對 macOS / Windows 做一次只讀儲存分析，產出互動式 HTML 報告。流程：掃描 → 分析分級 → 生成網頁 → 開啟。

## 鐵律

- **全程只讀。** 只能跑掃描/統計/列目錄/讀元資訊（df、du、diskutil、stat、ls）。掃描階段不執行刪除、移動、清空回收站或改許可權。
- **清理必須有明確授權。** 只請求分析不等於授權刪除；使用者已批准具體物件時，Agent 可在相同邊界內代為操作，無需要求再點一次瀏覽器。網頁按鈕保留逐次確認。
- **估算標註清楚。** 涉及"可釋放空間"一律說明是估算值。
- **路徑、命令保留原文不翻譯。**

## 執行流程

### Step 1 掃描（只讀）

從宿主當前載入的 Skill 位置取得實際絕對目錄並設為 `STORAGE_SKILL_DIR`；每個新 shell 都要重新賦值。輸出寫入當前任務的工作目錄，指令碼使用帶引號的絕對路徑：

```bash
python3 "$STORAGE_SKILL_DIR/scripts/scan.py" > storage_scan.json
```

`scan.py` 自動識別系統（`sys.platform`）：
- **macOS**：掃 home、library、caches、containers、group_containers、app_support、applications、downloads、dev_caches，用 `du` 算大小。
- **Windows**：掃 user_profile、appdata_local、appdata_roaming、temp、downloads、program_files(_x86)、dev_caches，用 `os.scandir` 算大小；`system.disks` 含所有磁碟機代號。

輸出 JSON：`system`（系統/磁碟資訊，含 `disk_name` 主盤名 + `disks` 全部盤）+ `groups`（各組子目錄大小，已降序、過濾 50MB 以下）。Windows 同次掃描複用子目錄統計，避免重複遍歷。頂層分組存在父子包含關係，不能直接相加；可釋放空間還受硬連結、壓縮和回收站保留影響。讀取 `warnings` 並在報告中說明未讀全的路徑。讀不到的目錄標 `denied`，需在報告裡列出並提示遺漏體量。

Windows 使用 `py -3` 或 `python`；在 PowerShell 用 `py -3 "$STORAGE_SKILL_DIR/scripts/scan.py" | Out-File -Encoding utf8 storage_scan.json`，後續 JSON 讀取支援 UTF-8 BOM。PowerShell 同樣先設定 `$STORAGE_SKILL_DIR` 為實際絕對目錄。

### Step 2 分析與分級

先看 `system.os` 判斷系統，讀對應的資料佈局參考：macOS 讀 [references/macos.md](references/macos.md)，Windows 讀 [references/windows.md](references/windows.md)（講該系統東西存哪、怎麼辨認、歸哪一級）。然後讀 `storage_scan.json` 做這幾件事：

1. **挑 Top 5** 佔用大戶，判定型別（系統資產/應用本體/應用資料/應用快取/開發快取/使用者檔案/媒體內容/下載內容/虛擬機器映象/回收站/其他）。
2. **識別"神秘大目錄"**：UUID 命名的 Container、不明的隱藏目錄，要追查它屬於哪個 App、裝的是什麼（例如某 97GB 的 UUID Container 實為 Bilibili 離線影片快取）。必要時 `ls`/`du` 深入一層看清楚，但仍只讀。
3. **三級分類 = 清理決策清單，不是全盤點。** 只把"存在'要不要動它'這個決策"的項放進三燈；日常在用的正常應用、作業系統本身、海量零碎小檔案沒有清理決策，不進三燈，它們落在磁碟條的藍色"系統及其他"裡。判定標準：
   - 🟢 **可自動清理**：純快取、臨時檔案、安裝包殘留、明確可再生且不影響功能、不丟使用者資料（pip/uv/npm/Xcode DerivedData 等開發快取、瀏覽器快取）。
   - 🟡 **需人工判斷**：含使用者資料或有判斷成本（離線影片、文件、專案程式碼 node_modules、聊天記錄、設計稿）。給內容畫像 + 至少 3 句處置路徑（應用內清理 / 系統工具 / 檔案管理器手動審查，三選最合適）+ 風險提示。**所有橙燈項在服務模式下自動有「在訪達/資源管理器開啟」按鈕**（跳過去自己審查刪）；如果該項有一個核實過、刪了不破壞 App 的安全子路徑（如 B站離線影片的 `.Downloads` 目錄、舊備份目錄），給它 `trash_paths` → 網頁出現「移到廢紙簍」按鈕（橙燈只准移廢紙簍、可逆，絕不給"直接刪除"）。App 託管又無安全子路徑的（Chrome/微信）只給開啟按鈕、不給 trash_paths。按鈕下方會自動寫明注意事項（開啟只檢視不刪、移廢紙簍可逆需清空才釋放等）；如果某項在檔案管理器裡是 App 內部格式、不方便手動挑選，給它一個 `open_note` 欄位做客觀說明（會顯示在注意事項裡）。**口吻要中性、像產品說明**：直接描述"這裡是什麼結構、為什麼不好手動刪、想精細操作該去哪"，不要寫成"我發現/提醒注意/看著像沒影片"這種暴露開發者踩坑視角的話。
   - 🔴 **謹慎清理（有決策但不建議手刪）**：你可能想動、但建議別手刪的具體項——重複安裝的應用、想解除安裝的大應用、執行中應用的核心資料等。給"為什麼不建議手刪" + `indirect_release` 寫**具體解除安裝步驟**（自帶解除安裝器 / 啟動臺長按 / 右鍵移廢紙簍 / AppCleaner 清殘留 / App Store 可重灌等，要可照做不是空話）。應用項給 `app_paths`（真實 `.app` 絕對路徑陣列）→ 網頁出現「在檔案管理器開啟（去解除安裝）」按鈕，定位到 App 讓使用者自己正規解除安裝。**紅燈不給刪除/解除安裝按鈕**（應用在系統目錄、可能要管理員密碼、可能有自帶解除安裝器和殘留，後臺代刪不穩妥）。**純系統檔案、APFS 快照不要單獨列紅卡**（沒有清理決策），歸藍色即可；系統層面的釋放技巧（重啟釋 swap、Time Machine 快照策略、可清除空間自動回收）寫進 `summary.long_term` 長期建議。

不要把專案、git worktree（包括 `.git` 指標檔案）、專案依賴或整個開發工具目錄當作快取。Windows 二次檢視大小也要排除 junction/symlink，不能只看體積或目錄名判斷可刪。pnpm store 優先 `pnpm store prune`，Go 模組快取優先 `go clean -modcache`；不提供整個 store、global 或工具安裝根目錄的刪除按鈕。硬連結不因刪除另一條連結就失效，但也不能把邏輯大小當作一定可釋放的空間。

每個 🟢 項要給：預估釋放空間、清理前需關閉的程序、可一鍵複製的清理命令（用移到廢紙簍或 App 自身清理入口的安全方式，謹慎用 `rm`；如用 `rm` 必須是明確的快取子目錄）。

**大小欄位寫乾淨**：`size` / `size_estimate` 用"約 14 GB""合計約 8.6 GB"即可——"約"已表示估算，不要再加"（估算）"，重複且不專業（模板也會自動去掉這種冗餘括號）。可再生屬性已由分級標題和按鈕說明覆蓋，別塞進大小欄位。

### Step 3 生成互動報告

把分析結果以 UTF-8 寫成 analysis JSON（schema 見 `scripts/build_report.py` 頂部註釋）。Windows PowerShell 不用預設 ANSI 寫檔案，用 `Set-Content -Encoding utf8` 或 Python 的 `encoding="utf-8"`；已有中文變成問號的 JSON 必須從原內容重生成，換字型無法恢復丟失字元。

**🟢 項必須帶 `trash_paths`**（具體可刪的絕對路徑陣列，區別於人類可讀的 `path` 展示欄位）——這是網頁刪除按鈕的前提，漏了按鈕就不出現。

**預設用一鍵刪除模式（`server.py`）開啟報告**，因為這個 skill 的核心價值就是網頁上能直接清理：
```bash
python3 "$STORAGE_SKILL_DIR/scripts/server.py" storage_analysis.json   # 自動開瀏覽器，Ctrl+C 停，閒置 30 分鐘自動退出
```
`server.py` 起在 127.0.0.1 + 隨機埠 + 隨機 token。🟢 項給「移到廢紙簍」(可逆) +「直接刪除」(不可逆，實際釋放量以磁碟統計為準)；🟡 項給「在訪達開啟」+（有安全子路徑時）「移到廢紙簍」。**安全模型——三套白名單，許可權從嚴到寬**：`rm` 只允許綠燈 `trash_paths`；`trash` 允許綠燈+橙燈 `trash_paths`（橙燈永遠不能 rm）；`open`（在檔案管理器開啟，非破壞性）允許上述全部 + 橙燈真實 `path`。刪除請求校驗整個批次，限制在使用者目錄內，拒絕主目錄、資料根目錄、連結和專案/worktree；應用安裝目錄僅允許開啟。所有請求 Host 校驗，操作請求還校驗 token，每次點選瀏覽器先 confirm。osascript/SHFileOperationW 入廢紙簍，macOS 首次彈訪達自動化授權點允許即可。

僅當使用者明確只想要一份可分享/留存的只讀檔案時，才用靜態模式（無刪除按鈕，因為 `file://` 開啟的頁面碰不到檔案系統）：
```bash
python3 "$STORAGE_SKILL_DIR/scripts/build_report.py" storage_analysis.json storage-report.html
```

**排障：網頁上沒有刪除/移廢紙簍按鈕** = 要麼開的是靜態報告（改用 `server.py`），要麼 🟢 項漏了 `trash_paths`（補上重啟服務）。

報告閱讀流（固定順序）：磁碟總覽卡片（容量 + 進度條 + 三色容量 pills + 系統資訊，純資料）→ 佔用排行 Top5 → 執行建議 → 🟢🟡🔴 三級可摺疊卡片（命令一鍵複製）→ 長期最佳化建議。即"現狀 → 診斷 → 處方 → 操作 → 預防"。

注意 `summary.overview` 要寫成一句話洞察（直接說最大佔用是什麼、能釋放多少），不要重複總/已用/可用數字——那些已在卡片大數字裡顯示。overview 渲染在"執行建議"小節開頭作引子（普通文字），緊接著是 `summary.priority` 優先順序清單。

磁碟進度條把"已用"拆成分段：綠(可自動清)+橙(需手動)+紅(已識別的不建議動項)+藍(系統及其他，自動取 已用−綠−橙−紅 的餘量)，餘下為可用(灰底)。`summary.tier_stats` 的 green / yellow / red 三個值都要以可解析的 GB 數字開頭（如 "約 27.8 GB"），指令碼從中取數算分段；藍色段和"系統及其他"pill 由模板自動算餘量。

pills 只渲染解析出的純數字（如"約 5.5 GB"），不顯示資料裡的附註，所以 tier_stats 三個值寫乾淨的數字即可，別加"僅已識別項/系統未計"這類道歉式說明——系統檔案本來就歸在藍色段，紅色只放你能量化的 🔴 項（重複應用、可解除安裝大應用等），量不準的系統檔案/快照自然落到藍色。

使用可終止的託管執行會話啟動服務，記錄程序和地址；工具等待超時不代表服務失敗，先核實已有程序，不重複啟動。任務結束時停止本次服務並核實埠釋放；只有使用者要繼續使用頁面才保留並說明 30 分鐘空閒退出。

### Step 4 對話裡給摘要

報告生成後，在對話裡用一段話給結論先行的摘要：總可釋放估算、最該先清的 2-3 項、風險最高的一項。細節讓使用者看網頁。

## 依賴與執行前提

- 全部指令碼是 **Python 3 標準庫**，零第三方依賴（不用 pip install）。
- **macOS** 需要 Python 3；先檢查 `python3 --version`。`du`、`diskutil`、`osascript` 由系統提供。
- **Windows** 預設沒裝 Python——需先裝 Python 3，且命令多為 `python` 或 `py -3`（不是 `python3`）。本 skill 命令示例寫的是 `python3`，在 Windows 上自動改用 `python` / `py -3`。
- 本 skill 是 **agent 驅動**：掃描出資料後由 agent（Claude）做分級分析，不是雙擊即用的獨立 App。

## 平臺狀態

- **macOS**：完整實現並實測（掃描 / 報告 / 一鍵刪除全驗證過）。
- **Windows**：程式碼已寫（`scan.py` 的 `scan_windows`、`server.py` 的 `_trash_windows` 走 `SHFileOperationW`），包含社群 Windows 真機反饋對應的修復；自動化驗證見倉庫 CI，回收站桌面互動仍需按當前機器核實。首次在 Windows 跑要核對：目標目錄路徑、`os.scandir` 大小、回收站刪除是否正常。多磁碟機代號已支援（主盤分段條 + 其他盤列表）。

## 長期最佳化建議素材（寫進報告 summary.long_term）

- 定期清理：`brew cleanup`、Xcode DerivedData、瀏覽器快取
- 視覺化工具：DaisyDisk、GrandPerspective、OmniDiskSweeper
- 大檔案歸檔到外接盤 / iCloud / NAS；macOS「系統設定 > 通用 > 儲存空間」的最佳化選項
