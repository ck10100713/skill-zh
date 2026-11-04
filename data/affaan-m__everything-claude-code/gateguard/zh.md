---
name: gateguard
description: "PreToolUse 的「強制出示事實」關卡：第一次 Edit/Write/Bash（包含 MultiEdit 和 NotebookEdit）嘗試會被拒絕，直到 agent 拿出具體事實（import 它的檔案、資料 schema、使用者指令的原話），才允許重試；A/B 測試的品質提升了 2.25 分。啟用或設定 GateGuard hook、用環境變數豁免路徑，或處理第一次碰檔案被拒絕的情況時使用。"
metadata:
  origin: community
---

# GateGuard — Fact-Forcing Pre-Action Gate

一個 PreToolUse hook，強迫 Claude 在編輯之前先做調查。它不問自我評估的問題（「你確定嗎？」），而是要求拿出具體事實。調查這個動作本身會帶來覺察，這是自我評估從來做不到的。

## When to Activate

- 處理任何一個「改檔案會影響多個模組」的程式碼庫
- 專案裡有資料檔，而且有特定的 schema 或日期格式
- 團隊要求 AI 產生的程式碼必須符合既有的寫法
- 任何 Claude 傾向用猜的、而不是去調查的工作流程

## Core Concept

LLM 的自我評估沒用。問它「你有沒有違反任何政策？」，答案永遠是「沒有」。這已經被實驗驗證過了。

但是問「列出每一個 import 這個模組的檔案」，就會強迫 LLM 去跑 Grep 和 Read。調查本身會產生 context，改變輸出的結果。

**三階段關卡：**

```
1. DENY  — block the first Edit/Write/Bash attempt
2. FORCE — tell the model exactly which facts to gather
3. ALLOW — permit retry after facts are presented
```

沒有任何競爭對手三個都做。大多數只做到拒絕這一步。

## Evidence

兩個獨立的 A/B 測試，相同的 agent、相同的任務：

| Task | Gated | Ungated | Gap |
| --- | --- | --- | --- |
| Analytics module | 8.0/10 | 6.5/10 | +1.5 |
| Webhook validator | 10.0/10 | 7.0/10 | +3.0 |
| **Average** | **9.0** | **6.75** | **+2.25** |

兩個 agent 產出的程式碼都能跑、都能過測試。差別在設計的深度。

## Gate Types

### Edit / MultiEdit Gate (first edit per file)

MultiEdit 的處理方式完全一樣：批次裡的每個檔案都會各自被擋；沒有自己的 `file_path` 的項目，視同這次呼叫的 `file_path` 來擋。NotebookEdit 被當成對它的 `notebook_path` 做 Edit 來擋：同樣的類別、同樣的檢查 key、同樣的 credit 與上限規則、同樣的完整問題（cell 的變更不會被讀取），而且絕不會走「只改註解」的放行。

問題取決於目標的類別（見[依目標類別的問題](#questions-by-target-class)）。對 **code** 目標，Edit 關卡會問：

```
Before editing {file_path}, present these facts:

1. List ALL files that import/require this file (search the tree — Glob/Grep, or find/grep via Bash)
2. List the public functions/classes affected by this change
3. If this file reads/writes data files, show field names, structure,
   and date format (use redacted or synthetic values, not raw production data)
4. Quote the user's current instruction verbatim
```

這四題是完整的集合，只要沒辦法有把握地讀懂這次變更，就會全部問。能讀懂的時候（見[問題要配合變更](#questions-fit-the-change)），如果編輯沒有動到任何公開宣告，就改問檔案或其模組裡有哪些呼叫點依賴被改動的行為，而且變更不處理資料時會拿掉第 3 題。

### Write Gate (first new file creation)

對 **code** 目標，Write 關卡會問：

```
Before creating {file_path}, present these facts:

1. Name the file(s) and line(s) that will call this new file
2. Confirm no existing file serves the same purpose (search the tree — Glob/Grep, or find/grep via Bash)
3. If this file reads/writes data files, show field names, structure,
   and date format (use redacted or synthetic values, not raw production data)
4. Quote the user's current instruction verbatim
```

新內容不處理資料時，會拿掉第 3 題。

### Questions fit the change

對 **code** 目標，關卡會讀取它即將放行的變更（Edit 的 `old_string`/`new_string`、這個檔案的每一筆 MultiEdit 項目、Write 的 `content`），並決定三件事：

- **公開介面（Public surface）：** 任一邊有一行宣告或對外暴露了公開名稱。JS/TS：`export`、`exports`、`public`、`declare`（`.d.ts` 檔一律算）；Python：不以 `_` 開頭的 `def`/`class`、dunder、`__all__`、模組層級的公開賦值（例如 `BASE_URL = ...`）（`__init__.py` 一律算）；Go：首字母大寫的 `func`/`type`/`var`/`const` 名稱、`package`、以大寫開頭的行；Rust：`pub`、`impl`、`trait`、`extern`、`#[macro_export]`、`#[derive]`、`#[repr]`、`#[no_mangle]`；shell：function 定義、`export`、`declare -x`；PowerShell：`function`、`filter`、`param`、`Export-ModuleMember`、`[CmdletBinding`。已匯出的容器的成員也算，要從檔案判斷：已匯出的 interface、enum、type、物件或 export 清單裡面的行、已匯出的 class 的成員宣告、`__all__` 的項目、公開的 class 屬性和 dataclass 欄位，以及 `pub` 的 enum、struct、trait 或 `use` 清單的成員。Java、Kotlin、C#、C、C++ 和 batch 檔，以及所有的 Write，一律視為有動到公開介面。有動到就保留第 1 和第 2 題；否則兩題都換成「列出這個檔案或其模組裡，依賴被改動行為的呼叫點」。
- **資料（Data）：** 任何一邊出現跟檔案 I/O、格式（`json`、`csv`、`yaml` 等）、序列化、編碼、schema、SQL、資料儲存、瀏覽器儲存、日期和讀取時鐘有關的字詞；在 shell script 裡，還包括重導向到檔案、`curl`、`wget`、`jq`，以及 PowerShell 的檔案和網路 cmdlet。沒有這些字詞，就拿掉資料那一題。開啟 `GATEGUARD_EXTERNAL_CONTRACT_QUESTION` 後，保留資料問題的變更還會多問一題：repo 之外有什麼東西決定了它的格式或語意。
- **瑣碎（Trivial）：** 見[只改註解和空白的編輯](#comment-and-whitespace-only-edits)。

支援的副檔名：`.js .mjs .cjs .jsx .ts .tsx .mts .cts .py .pyi .go .rs .java .kt .kts .cs .c .h .cc .cpp .cxx .hpp .hh .hxx .sh .bash .zsh .ps1 .psm1 .bat .cmd`。其他任何副檔名、缺少欄位或欄位不是字串、MultiEdit 項目超過 64 筆、單邊超過 64 KiB、或總共超過 256 KiB，都代表要問完整的問題，一字不差：原本的四題（importer、公開 API、資料 schema、使用者的指令），開啟 `GATEGUARD_EXTERNAL_CONTRACT_QUESTION` 時是五題。敏感目標、hard link 的目標和 NotebookEdit 呼叫，一律問完整的問題。其他類別則保留各自類別的問題。每個問題都有穩定的 id（`importers`、`public-api`、`local-callers`、`callers`、`no-duplicate`、`data-schema`、選用時才有的 `external-contract`、`quote-instruction`，以及每個類別問題各一個），列在 `docs/gateguard/change-profile.md`。

### Questions by target class

程式碼相關的問題，對 `SKILL.md`、README、測試或 YAML 檔來說毫無意義，所以第一次碰檔案的關卡會先替目標分類。

分類用的是目標相對於專案根目錄的路徑（先看 `CLAUDE_PROJECT_DIR`，再看 payload 的 `cwd`，最後是 process 目錄），所以放在例如 `~/work/tests/` 底下的專案，不會讓每個檔案都被當成測試。開頭的 `.claude/worktrees/<name>/` 會被去掉，因為 worktree 是專案的鏡像，但只有在 `<root>/.claude/worktrees/<name>/.git` 存在時才去；否則路徑維持在 `.claude` 底下。對 Windows 風格的路徑（以及任何含 `::$` 的片段），會先去掉結尾的點和空白，以及 `:stream` 後綴，所以 `CLAUDE.md.` 和 `CLAUDE.md::$DATA` 都分類成 `CLAUDE.md`。根目錄之外的目標，用絕對路徑來分類。路徑會轉成小寫、以 `/` 分隔，第一個符合的規則勝出：

1. **instruction**：basename 是 `CLAUDE.md`、`AGENTS.md`、`AGENT.md`、`GEMINI.md`、`SKILL.md`、`copilot-instructions.md`、`.cursorrules` 或 `.windsurfrules`；任何 `.mdc` 檔；位於 `.claude`、`agents`、`commands`、`skills`、`rules`、`hooks`、`.cursor`、`.codex` 或 `.opencode` 目錄底下的 `.md`/`.mdx`/`.txt` 檔；或是 `.github/` 底下的 `*instructions*.md` 檔
2. **test**：`*.test.*`、`*.spec.*`、`test_*.py`、`*_test.py`、`*_test.go`，或任何在 `tests`、`test` 或 `__tests__` 目錄底下的東西
3. **prose**：`.md`、`.mdx`、`.txt`、`.rst`、`.adoc`
4. **config**：`.json`、`.jsonc`、`.yaml`、`.yml`、`.toml`、`.ini`，或是不以程式碼副檔名結尾的 `.env` / `.env.*` 檔（`.env.local` 是 config；`.env.example.ts` 和 `.envrc` 是 code）
5. **code**：其他全部（`hooks/` 或 `skills/` 底下的 `.js` 算 code）

每個類別最後都會問「逐字引用使用者目前的指令」，保留批次同伴警告，而且除非另有註明，Edit、MultiEdit 和 Write 用同一組問題。標了 *(search)* 的項目，會帶上後綴「(search the tree — Glob/Grep, or find/grep via Bash)」。

| Class | Questions |
|---|---|
| instruction | 說出讀取這個檔案的 harness/loader（Claude Code、Codex、Cursor、OpenCode 等）以及它什麼時候載入 · 描述 agent 的行為會因此有什麼改變 · 確認沒有既有的指令、skill 或 agent 檔已經涵蓋這件事 *(search)* |
| test | 說出被測試的行為是什麼，以及它跑的是哪個模組/函式 · 說出涵蓋這個模組的既有測試檔，或確認沒有 *(search)* |
| prose (Write) | 說出這份文件取代或重複了哪份既有的文件 *(search)* · 說明它會從哪裡被連結或引用 · 解釋為什麼要建新檔，而不是編輯既有的檔案 |
| prose (Edit) | 列出引用到被改動段落的其他文件或程式碼 *(search)* · 說明這次變更修正或新增了什麼 |
| config | 說出哪個 process/工具會讀這個檔案、什麼時候讀 · 描述這次變更的效果 · 確認沒有把 secret 或憑證以明文寫進去 |

簡化版的拒絕訊息（在 `GATEGUARD_FACT_FORCE_FULL_DENIALS` 之後）會對同一個類別附上一行提示。對 code 目標，這行提示會點出跟完整拒絕訊息相同的問題，每題用一個簡短的片語；外部契約問題關閉時，變更讀不懂的 Edit 會保留固定的提示（importer/呼叫者、受影響的 API、如果有的話資料 schema）。選擇開啟的話，會多加外部契約的片語。除了訊息文字之外，類別只決定[同輩合併](#same-turn-sibling-creation-collapse)：哪些檔案可以合併，以及同輩必須跟第一個檔案屬於同一類別。

### Destructive Bash Gate (every destructive command)

觸發條件：`rm -rf`、`git reset --hard`、`git push --force`、`drop table` 等等。

```
1. List all files/data this command will modify or delete
2. Write a one-line rollback procedure
3. Quote the user's current instruction verbatim
```

### Routine Bash Gate (once per session)

```
1. The current user request in one sentence
2. What this specific command verifies or produces
```

唯讀的探查不會消耗這個關卡：在它觸發之前，只要指令的每個以 `;`、`|`、`&&` 或 `||` 分隔的片段，都是 `ls`、`pwd`、`cat`、`head`、`tail`、`wc`、`grep`、`rg`、`find`、`fd`、`tree`，或帶唯讀選項的 `git status`/`log`/`diff`/`show`/`ls-files`/`rev-parse`/`branch`（PowerShell 則是：`Get-ChildItem`、`Get-Content`、`Select-String`、`Get-Location`、它們的別名、`rg`、`git`），就會放行，並計入 `routine_readonly_passes`。第一個不是這類的指令仍然會被擋。任何重導向、`tee`、替換、反引號、變數、環境變數賦值、包裝指令（`env`、`sudo`、`xargs`、`sh -c`）、不認識的指令、`find -exec`/`-delete`、`fd -x`、`rg --pre`/`-z`、`tree -o`、`git` 的全域選項或寫入/執行選項，或是 PowerShell 的 `$`、`@`、`(`、`{` 或 `--%`，都會讓指令變成一般指令。破壞性指令的偵測先執行，而且不受影響。

用 session id 或 transcript 路徑當 key 的 session 狀態，閒置 8 小時後過期；退回用專案目錄當 key 時，閒置 30 分鐘後過期。

## Parallel Batches and Partial Application

第一次碰檔案的關卡會獨立評估每一次工具呼叫。當對一個還沒碰過的檔案的好幾個編輯，被放在同一個平行批次送出時，第一個呼叫會被拒絕，而這次拒絕會把該檔案標記為已檢查，所以批次裡的同伴編輯會被套用。沒有任何東西會被回滾：檔案最後可能只有同伴編輯，沒有被拒絕的那個。

拒絕訊息會點名檔案，並警告批次同伴可能已經被套用。要照字面意思看待：

- 對還沒碰過的檔案，相依的編輯要依序送，不要放在平行批次。定義和它的第一次使用、或 import 和它的呼叫點，不可以放在同一個批次。
- 第一次碰檔案被拒絕後，要提出事實、重試被拒絕的編輯，並且在繼續做批次裡其他任何事之前，先重新讀一次檔案。

不可能做整個批次的鎖：hook 一次只看到一個工具呼叫，所以關卡無法知道哪些呼叫是一起送來的。

## What Counts as Already Done

第一次碰檔案被拒絕，目的是強迫調查。如果 transcript 顯示調查已經發生過，或是答案會跟上一次的拒絕一字不差地重複，關卡會附上一則說明直接放行，不拒絕。底下每一條規則，只要有任何模糊的地方，都會退回一般的拒絕。

### Order of checks

對每個 Edit/Write/NotebookEdit 目標（以及每一筆 MultiEdit 項目），關卡依下列順序決定；第一條適用的規則勝出：

1. **豁免**（`GATEGUARD_EXEMPT_GLOBS`、Claude 的設定檔）：放行。操作者的豁免是最高權威：它凌駕後面所有規則，包括敏感目標和 hard-link 規則，所以只要某個 glob 涵蓋了 `src/auth/**` 或某個 hard link 檔案，就等於關掉它的檢查。只豁免那些不經檢查也可以編輯的路徑。
2. **Subagent** 呼叫：放行（父 session 已經被擋過了），但[敏感](#sensitive-targets)或 [hard-link](#hard-linked-targets) 目標除外：除非父 session 已經擋過，否則每條路徑拒絕一次。subagent 的重試不會替父 session 解鎖這條路徑。
3. 這個 session 中**已經檢查過**：放行。
4. **敏感或 hard-link 目標？** 如果是，直接跳到拒絕（第 9 步）。
5. **先前搜尋的 credit**：附帶說明放行。
6. **只改註解或空白的 Edit**：附帶說明放行，不標記為已檢查。
7. **同輩合併**：附帶說明放行。
8. **拒絕上限**（`GATEGUARD_FACT_FORCE_MAX_DENIALS`，選用）：一旦這個 session 的拒絕次數達到上限，就放行。
9. **拒絕**：計入 `fact_force_denials`。

credit、瑣碎和同輩放行，永遠不會消耗拒絕上限。

### Sensitive targets

有些檔案不經完整檢查就改，代價太高，所以先前搜尋的 credit、只改註解或空白的放行、變更輪廓（change profile）、同輩合併和拒絕上限，對它們一律不適用：它們在第一次碰的時候照樣被拒絕，就跟沒有這些規則時一樣，而且拒絕照常計次。拒絕訊息會多帶一行：「Sensitive target: prior-search credit, sibling collapse, and the denial cap do not apply.」目標是否敏感，是用跟它的類別相同的小寫、專案相對路徑，**以及**它真實（解開 symlink 後）的位置來判斷，只要其中一個符合就算：

- 它的檔名是 `.env`、`.netrc` 或 `.pgpass`，以 `.env.` 開頭，以 `.pem`、`.key`、`.p12` 或 `.pfx` 結尾，或以 `id_rsa`、`id_ed25519`、`id_ecdsa`、`id_dsa`、`credentials` 或 `secrets.` 開頭；
- 任何一個路徑片段剛好是 `auth`、`authn`、`authz`、`security`、`secrets`、`payment`、`payments`、`billing` 或 `migrations`（只比對完整片段：`src/author.py`、`docs/authoring.md` 和 `lib/paymentutils.py` 都是一般檔案）；
- 或是位於 `.github/workflows/` 底下。

真實位置是檔案本身的 realpath（存在的話），否則是它最近的既有目錄的 realpath 加上路徑的其餘部分，並且相對於專案根目錄的 realpath 來判斷，所以 `src/tools -> ../auth` 會讓 `src/tools/login.py` 變成敏感。專案之外的真實位置，用它的絕對路徑來判斷。判斷過程中的任何錯誤（懸空的 symlink、本該是目錄的地方是個檔案、權限錯誤）都視為敏感。破壞性和一般的 shell 關卡不受影響。

### Hard-linked targets

有超過一個 hard link 的檔案（`nlink > 1`，或是指向這種檔案的 symlink），也能用另一個名字存取，那個名字可能是敏感的，或屬於別的類別，所以被編輯的路徑本身說明不了什麼會被改動。它得到跟敏感目標一樣的待遇：沒有先前搜尋的 credit、變更輪廓、只改註解的放行、同輩合併、拒絕上限或 subagent 繞過，而且它的拒絕訊息帶的是「Hard-linked target: prior-search credit, sibling collapse, and the denial cap do not apply.」，不是敏感那一行（兩者都是的目標，會說「Sensitive target」）。除了「檔案不存在」之外的 stat 錯誤，視為 hard-linked；還不存在的新檔案則不算。

### Prior-search credit

當**目前這一輪人類回合**裡，已經有一個合格的搜尋涵蓋了該檔案時，Edit、Write、NotebookEdit 或 MultiEdit 項目會被放行，並帶一則點名該搜尋的 `additionalContext` 說明：

- **合格的工具：** `Glob`、`Grep`、`LS`，以及以 `rg`、`grep`、`egrep`、`fgrep`、`git grep`、`git ls-files`、`find`、`fd`、`ls`、`tree`、`Get-ChildItem`、`gci`、`Select-String` 或 `sls` 開頭的 Bash/PowerShell 指令片段。**`Read` 絕對不算**：Claude Code 本來就要求編輯前要先 Read，所以它沒有多證明任何事。
- **目前這一輪人類回合：** 回合從最新一則真實的使用者訊息開始，或從一次 compaction（compact-summary 紀錄或 `compact_boundary` 標記）開始，所以 compaction 之前的搜尋永遠不算。工具結果、meta 和 sidechain 紀錄不會開啟一個回合。只讀 transcript 的尾端（最後 256 KiB / 2000 行）；如果回合在那個視窗之前就開始了，只要視窗內每個 `promptId` 都一致，整個視窗就當作目前的回合。視窗裡有兩個以上的 `promptId`，代表有一個回合是透過掃描不認得的紀錄開始的，所以那個視窗不給 credit。完全沒有回合起點的 transcript，也不給 credit。
- **完成且明確的結果：** 搜尋需要在該回合裡有一個不是錯誤的 `tool_result`（`is_error` 為 `true` 或 `"true"`，或內容以 `<tool_use_error>` 開頭就算錯誤）。出現超過一次的 tool-use id，一律不算。
- **不是同一個批次：** 在被擋的呼叫自己的 assistant 訊息裡送出的搜尋，一律不算，因為決定編輯的時候還沒看到它們的結果。如果 payload 的 `tool_use_id` 遺失，或不在 transcript 裡，就改為排除該回合最新的 assistant 訊息。沒有訊息 id 的搜尋，一律不算。
- **詞幹比對（Stem match）：** 目標的詞幹（basename 去掉最後一個副檔名、小寫、至少 4 個字元）必須以完整單字的形式出現，也就是前後以非英數字元或文字的兩端為界，出現在 Glob pattern、Grep 的 pattern 或 glob，或 shell 片段裡。`payment.py` 會被搜 `payment` 或 `payment_service` 的搜尋給予 credit，但搜 `payments` 的不行。排除項永遠不是詞幹的來源。泛用的詞幹（`index`、`main`、`init`、`__init__`、`utils`、`util`、`types`、`readme`、`test`、`tests`、`config`、`mod`、`lib`、`setup`、`app`、`spec`、`helpers`、`common`）永遠不比對。對測試目標，會先去掉一個測試詞綴（`.test`、`.spec`，以及 Python 和 Go 的 `test_` 或 `_test`），所以 `rg tokenizer src tests` 會給 `tests/tokenizer.test.js` credit；`index.test.js` 仍然會化約成泛用的 `index`。
- **排除項永遠不給 credit：** Grep 的 `glob` 會在最上層的逗號處切開；以 `!` 開頭的項目是排除項。在 shell 片段裡，以 `!` 開頭的 `rg -g`/`--glob`/`--iglob` 值、`grep --exclude`/`--exclude-dir`、`fd -E`/`--exclude`、`ls -I`/`--ignore`/`--hide`、`tree -I`、`git ls-files -x`、git 的 `:!x`/`:^x`/`:(exclude)x` pathspec、在 `-not` 或 `!` 底下、或後面接 `-prune` 的 `find -name`/`-path`/…，以及 PowerShell 的 `-Exclude`，都是排除項。如果某個排除項涵蓋了目標（它的 glob 符合檔名或路徑上的任何目錄，或是它點名了詞幹），那個搜尋就完全無法替目標給 credit：`rg -g '!widget.py' TODO .` 永遠不給 `widget.py` credit，而 `rg -g '!*.md' widget .` 仍然會給。`--exclude-from`、`--ignore-file` 和 `git ls-files -X` 會隱藏 hook 看不到的名稱，所以這種片段永遠不給 credit。限制搜尋範圍的檔名 glob（Grep 的 `glob: '*.py'`、`rg -g '*.py'`、`grep --include`、`find -name`、`tree -P`、`-Include`/`-Filter`），必須符合目標的檔名，詞幹才算數。檔案類型的過濾也是一樣：`rg -t`/`--type` 和 Grep 的 `type` 會納入該類型的 glob，`rg -T`/`--type-not` 會排除它們，`fd -e`/`--extension` 會納入 `*.<ext>`，所以 `rg -t py tokenizer src` 永遠不給 `tokenizer.js` credit。不認識的類型名稱、`--type-add` 或 `--type-clear`，會讓該片段永遠不給 credit。
- **查找不算搜尋：** 範圍只限於目標自己檔名的搜尋（每個 include glob、Glob pattern 或每個路徑 pattern，都以那個確切的檔名結尾，例如 `Glob **/tokenizer.js`、`find -name tokenizer.js`、`rg -g tokenizer.js`、Grep `glob: 'tokenizer.js'`），只可能找到目標本身，所以永遠不給它 credit。`Glob **/tokenizer.*` 仍然會給。
- **範圍（Scope）：** `Glob`、`Grep` 和 `LS` 只對嚴格位於它們搜尋過的目錄之內的目標給 credit（它們的 `path`，否則是工具的 `cwd`，再加上 Glob pattern 字面上的開頭目錄）。Glob pattern 同時也是個過濾器：它必須符合目標的路徑，詞幹才算數，所以 `Glob **/tokenizer.py` 永遠不給 `tokenizer.js` credit。沒有萬用字元的 Glob 是單一檔案的查找：它沒有指定任何目錄，只對直接位於它目錄裡的檔案給 credit，絕不給被查找的檔案本身。路徑就是目標本身的搜尋，不是搜尋。
- **Shell 片段：** 沒有路徑運算元的片段，只有在它是遞迴的（預設是 `rg`、`git grep`、`git ls-files`、`find`、`fd` 和 `tree`；`grep -r`/`-R`/`--recursive`、`ls -R`、`Get-ChildItem -Recurse`），而且不是由 pipe 餵入時才算；否則它讀的是 stdin，不是目錄樹。路徑運算元全部都解析到目標的片段，只讀了目標，不算（`ls src/a.py` 永遠不給 `src/a.py` credit）。包含 `$( )`、反引號、`<( )`、`>( )` 或 heredoc 的指令，或長度超過 8192 個字元的指令，一律不給 credit。
- **Shell 範圍：** shell 片段只對等於或位於它某個路徑運算元之內的目標給 credit（相對於工具的 `cwd` 解析；glob 運算元必須符合目標或它上層的目錄，而預設 git pathspec 的 `*` 也會符合 `/`），沒有運算元時則對位於 `cwd` 之內的目標給 credit：`rg payment docs` 或 `grep -rn payment /usr/share/doc` 永遠不給 `src/payment.py` credit。在任何運算元之前的輸入重導向（`rg payment < file`），或字詞裡面的 `<`，讀的是 stdin，永遠不算。在同一個指令裡 `cd <dir>` 之後，相對運算元相對於那個目錄解析；在任何其他目錄變更之後，或是在該回合的另一次呼叫裡變更之後，只有絕對運算元算數。
- **目錄比對（只限新檔案）：** **建立一個還不存在的檔案的 Write**，在搜尋剛好點名了目標所在的目錄時，也可以比對成功：Glob 的 `path` 加上 pattern 的字面前綴（以萬用字元開頭、又沒有 `path` 的 pattern，不指定任何目錄）、Grep 或 LS 的 `path`，或 shell 的路徑運算元。對 shell 運算元，grep 類工具的 pattern 參數會被跳過（除非 pattern 是由 `-e`/`-f`/`--regexp`/`--file`/`-Pattern` 提供的），有值的旗標（`-g`、`--include`、`-name`、`-Filter` 等）的值會被跳過，結尾的 `/`、`/*` 和 `/**` 會被去掉，`.`、`~`/`$` 路徑和 glob 不指定任何目錄，而且運算元在檢查當下必須是一個存在的目錄。如果該回合中有任何 Bash/PowerShell 呼叫改變了目錄（`cd`、`pushd`、`popd`、`chdir`、`Set-Location`、`sl`、`Push-Location`、`Pop-Location`），整個回合的 shell 目錄比對就會關閉；詞幹比對仍然適用。**Edit、MultiEdit，以及覆寫既有檔案的 Write，只用詞幹比對。**
- **路徑：** 相對的目標和搜尋路徑，會先相對於工具的 `cwd` 解析，再用 `CLAUDE_PROJECT_DIR`，最後是 process 目錄。只有 Windows 路徑的比較不分大小寫。shell 指令是用 bash 的引號規則來讀的，所以在 Windows 上，運算元寫成 `C:/x/src` 時才給 credit；反斜線寫法（`C:\x\src`，有沒有加引號都一樣）和 MSYS 寫法（`/c/x/src`）都不給 credit，寫入會照常被拒絕。
- **說明，不是拒絕：** 被給予 credit 的檔案會被標記為已檢查，`fact_force_credited` 加一；拒絕次數和序號不受影響。MultiEdit 逐項給 credit，並像先前一樣拒絕第一個沒有 credit 的項目。
- **退回拒絕：** transcript 遺失、無法讀取或不是檔案、紀錄是亂碼，或有任何內部錯誤，都表示不給 credit。
- **拒絕訊息中最接近的失誤：** 當一個普通的（不是敏感或 hard-link 的）第一次碰檔案被拒絕，而且該回合中有一個呼叫提到了該檔案卻沒有給它 credit 時，拒絕訊息會多加一行「Closest search this turn did not count (`<tool>` `<detail>`): `<why>`.」，點名最接近的那個呼叫以及它失敗的原因：在同一個批次送出、它的過濾條件排除了該檔案、它的搜尋路徑不包含該檔案、它搜尋的是 pipe 進來的輸入、它是 `Read` 或其他指令而不是搜尋，或是檔名太泛用而無法比對。detail 會經過清理並截斷成 60 個字元；不會顯示 transcript 的其他文字。

### Comment and whitespace-only edits

舊文字和新文字只差在註解和空白的 Edit，不會改變任何行為，所以第一次碰檔案的問題沒有任何意義。對一個不敏感的 `code`、`test` 或 `prose` 目標做這種 Edit（或是該檔案的所有項目都是這種變更的 MultiEdit），會附上說明「Comment or whitespace-only change to `<file>`」放行。這個檔案**不會**被標記為已檢查：下一次對它做會改變程式碼的變更時，會遇到正常的第一次碰檔案關卡。這次放行計入 `trivial_allows`，而且完全不影響拒絕次數。

它只適用於[問題要配合變更](#questions-fit-the-change)裡列出的副檔名，而且只有在每個項目都能乾淨地讀懂時才適用：

- 註解是 `//` 和 `/* */`（C 家族）、`#`（Python）、字詞開頭的 `#`（shell）、`#` 和 `<# #>`（PowerShell），或 `REM` 行（batch）；C 的前置處理器行和 batch 的 `::` 標籤是程式碼；指令性質的註解也是程式碼（shebang、編碼 cookie、`# type:`、`# noqa`、`# nosec`、`// @ts-...`、`eslint-...`、`//go:build`、`// +build`、`//go:embed`、Rust 的文件註解、`#Requires`、`shellcheck`、`NOLINT`、`NOSONAR`、fallthrough 標記和類似的東西）；字串裡面的空白、程式碼之間的換行、以及 token 之間有沒有空白，都是程式碼（`a+b` → `a + b` 不算瑣碎）；
- Python 程式碼行的縮排是程式碼；
- 永遠不算瑣碎：Write；任何多行或 raw 的字串形式（反引號、三引號、`r"`、`R"`、`@"`、`$"`、f-string、Kotlin 的 `$`）、延伸到行尾的字串、以 `\`、`??/` 結尾的行註解或程式碼行、巢狀或沒有結束的區塊註解；在 JS/TS 裡，任何在註解之外的 `/`（regex 和除法分不出來）、類 JSX 的標籤，以及 `-->`；在 shell script 裡，heredoc、反引號、雙引號內的 `$(`、`$'...'`、續行和 here-string（完整的清單見設計筆記）；
- config、instruction、敏感和 hard-link 的目標，以及 NotebookEdit 呼叫，永遠不能這樣放行。

這個編輯還會對照目前的檔案做檢查（檔案必須是最多 1 MiB 的一般檔案，由 hook 讀取，從不儲存）：`old_string` 必須能依照 Edit 工具套用的方式找到，變更前後的行必須如上所述比對相等，而且它們前面的文字必須結束在一般的程式碼中，不能在 template literal、docstring、raw string、heredoc 或 here-string 裡面，也不能接在續行之後。檔案遺失、無法讀取或更大，或是 Go 檔案 import 了 `"C"`，都永遠不能這樣放行。

### Same-turn sibling creation collapse

同一個目錄裡一次建了好幾個新檔案時，每個檔案的答案都會一模一樣，所以只拒絕第一個：

- 適用於**對還不存在的檔案做 Write**，而且它的類別是 `code`、`test` 或 `prose`。永遠不合併的有：`config` 和 `instruction` 檔，以及任何路徑片段以 `.` 開頭（dotfile 和每一個以點開頭的目錄：`.claude`、`.github`、`.git`、`.husky`、`.devcontainer`、`.githooks`、`.idea`、`.vscode` 等）或是 8.3 短檔名（`CLAUDE~1`）的路徑，用跟類別相同的專案相對路徑來檢查。
- 目錄也會被解析成它的**真實位置**（跟隨 symlink；不存在的目錄從最近的既有上層解析）。如果它跟寫出來的路徑不同，真實路徑必須在專案之內、屬於同一個類別，而且通過同樣的篩選，所以像 `src/tools -> .claude/hooks` 這樣的 symlink 永遠不會合併。關卡是以真實目錄當 key。任何檔案系統錯誤都表示不合併。
- 這樣的 Write 被拒絕之後，之後在**同一個目錄、同一個類別**對新檔案的第一次 Write，會附上說明「Sibling of `<first>` (gated earlier at denial #`<n>` this session)」放行。code 的拒絕絕不會讓測試、README 或 config 檔通過。
- 視窗是**同一個人類回合**。回合 id 是回合起點紀錄本身的 `promptId`，沒有的話是它的 `uuid`，再沒有的話是那筆紀錄的雜湊。當回合在 transcript 尾端之前就開始時，id 是視窗內每一筆 user 紀錄都一致同意的 `promptId`（Claude Code 會把它蓋在 prompt 和該回合每一個工具結果上）；如果它們不一致，就沒有回合 id。只有在**完全沒有 transcript 路徑可用**時，沒有回合 id 所記錄的關卡才會比對 **120 秒**；transcript 遺失、無法讀取或得不到回合 id，都表示不合併。有回合範圍的關卡永遠不會比對沒有回合 id 的呼叫，反之亦然；蓋了未來時間戳的關卡會被忽略。
- 先檢查先前搜尋的 credit。**Edit 和 MultiEdit 永遠不合併**，既有的檔案也永遠不會被當成同輩。

### Canonical path keys

已檢查的狀態是以標準化的路徑當 key：相對的 `file_path` 會先相對於工具的 `cwd`（工具執行的地方）解析，再用 `CLAUDE_PROJECT_DIR`，最後是 process 目錄，用 `/` 當分隔符號，只有在 Windows 上才轉小寫。`a.py`、`./a.py` 和絕對路徑共用同一次第一次碰檔案。較早版本寫下的狀態檔（原始 key）仍然有效。`GATEGUARD_EXEMPT_GLOBS` 保留它專案相對的比對方式（見下）。

### In-session counters

每個 session 的狀態檔（在 `GATEGUARD_STATE_DIR` 底下）會記錄這些欄位。它們只記錄類別名稱，絕不記錄路徑（除了 `dir_gates`，它存的是每個目錄經過清理的第一個檔案）：

| Field | Meaning |
|---|---|
| `fact_force_credited` | 因先前搜尋 credit 而放行的第一次碰檔案次數 |
| `denials_by_class` | 每個目標類別（`code`、`prose`、`test` 等）的拒絕次數 |
| `credited_by_class` | 每個目標類別的 credit 次數 |
| `sibling_allows` | 因同輩合併而放行的 Write 次數 |
| `dir_gates` | 每個類別和目錄下，開啟同輩視窗的那次拒絕（回合、時間、第一個檔案、序號）；上限 50 筆 |
| `cap_allows` | 因拒絕上限（`GATEGUARD_FACT_FORCE_MAX_DENIALS`）而放行的第一次碰檔案次數；這些永遠不算拒絕 |
| `trivial_allows` | 沒經過第一次碰檔案檢查就放行的只改註解或空白的編輯次數；這些永遠不會把檔案標記為已檢查 |
| `routine_readonly_passes` | 一般 shell 關卡觸發之前放行的唯讀 shell 指令次數；這些永遠不會把它標記為已檢查 |

遺失或格式錯誤的欄位會載入成空值或零，所以舊的狀態檔仍然可以繼續運作。

### Compatibility and limits

- **兩個新的、選用的環境變數：** `GATEGUARD_FACT_FORCE_MAX_DENIALS`（不設定表示沒有上限）和 `GATEGUARD_METRICS`（不設定表示沒有指標）。既有的控制項沒有改變。
- **先前允許的東西，現在沒有任何一個會被拒絕**，除了 subagent 第一次碰敏感或 hard-link 的目標，以及每個 notebook 第一次的 NotebookEdit（以前 NotebookEdit 沒有被擋）。其他規則只會移除拒絕，而且從不回傳 `permissionDecision: "allow"`，所以其他 hook 和權限規則仍然適用。
- **信任限制：** 先前搜尋的 credit 讀的是本機的 transcript 檔，原則上 agent 有可能寫入它。這個 credit 驗證的是觀察到的行為（搜尋跑過而且有回傳），不是意圖，也不是結果被讀得多仔細。

## Quick Start

### Option A: Use the ECC hook (zero install)

`scripts/hooks/gateguard-fact-force.js` 這個 hook 已經包含在這個 plugin 裡。透過 hooks.json 啟用它。

如果 GateGuard 擋住了設定或修復的工作，就用 `ECC_GATEGUARD=off` 啟動 session。要做 hook 層級的控制，繼續用 `ECC_DISABLED_HOOKS` 搭配 GateGuard 的 hook ID。

在長 session 裡，只有前 `GATEGUARD_FACT_FORCE_FULL_DENIALS` 次（預設 3 次）的 fact-force 拒絕會送出完整的事實區塊；之後的拒絕會被壓縮成一行，帶著拒絕的序號，所以幾乎一樣的區塊不會在 context window 裡累積，也不會放大模型的重複迴圈（#2142）。提出事實之後重試同一個檔案或指令，絕對不會再次觸發關卡。那是一個訊息預算；想在若干次拒絕之後就不再拒絕新檔案，請設定選用的拒絕預算 `GATEGUARD_FACT_FORCE_MAX_DENIALS`（見下）。

#### Graduated controls

`ECC_GATEGUARD=off`（或 `GATEGUARD_DISABLED=1`）會把關卡整個關掉。這張表裡的變數**不會**：每個只縮小一種行為，而最關鍵的破壞性 Bash 檢查仍會持續運行：

| Variable | Default | Effect |
|---|---|---|
| `GATEGUARD_BASH_ROUTINE_DISABLED` | 不設定（關卡開啟） | 只停用**一般 Bash** 關卡。破壞性 Bash 關卡（`rm -rf`、`git reset --hard`、`drop table`、`dd if=` 等）不受影響。 |
| `GATEGUARD_EXEMPT_GLOBS` | 不設定（沒有豁免） | 以逗號分隔的 glob；符合的 Edit/Write/MultiEdit/NotebookEdit 目標會跳過第一次碰檔案的 fact-forcing，即使它是敏感或 hard-link 的也一樣。適用於 import 價值低的目錄樹（測試、產生出來的產物、暫存目錄），在那裡「誰 import 這個 / 什麼 schema」沒有意義。 |
| `GATEGUARD_FACT_FORCE_FULL_DENIALS` | `3` | 有多少次拒絕會送出完整的事實區塊，之後的才壓縮成一行。`0` 表示從第一次拒絕就開始壓縮。 |
| `GATEGUARD_FACT_FORCE_MAX_DENIALS` | 不設定（沒有上限） | 一個**拒絕預算**：限制一個 session 最多會吃到多少次第一次碰檔案的 Edit/Write/MultiEdit/NotebookEdit 拒絕。一旦發出了這麼多次拒絕，後續的新路徑就直接放行，不再拒絕（計入 `cap_allows`，不算拒絕）；`0` 表示從第一次就放行。先前搜尋的 credit 和同輩合併會先執行，而且永遠不會用掉它，[敏感](#sensitive-targets)和 [hard-link](#hard-linked-targets) 的目標則永遠會被拒絕。破壞性和一般的 Bash 仍然被擋。hook 並行執行時，這個上限是盡力而為：遺失一次計數更新可能多出一次拒絕，但絕不會讓新路徑提早通過。選用：不設定，或任何不是非負整數的值（允許前後有空白），會維持「每個新路徑都拒絕」的行為；格式錯誤的值會在 stderr 報告一次（`ignoring malformed GATEGUARD_FACT_FORCE_MAX_DENIALS=…; the denial cap is not active.`）。不像 `GATEGUARD_FACT_FORCE_FULL_DENIALS` 是只改變拒絕訊息文字多寡的**訊息預算**，這個變數改變的是操作會不會被擋下。簡化版的拒絕訊息會點出這個變數。 |
| `GATEGUARD_BASH_EXTRA_DESTRUCTIVE` | 不設定 | 額外的破壞性指令 pattern，以 regex 原始碼表示，加到內建的集合上。格式錯誤的 regex 視為沒設定（內建的仍然適用），並在 stderr 記錄一次。 |
| `GATEGUARD_STATE_DIR` | `~/.gateguard` | 每個 session 的關卡狀態存放的位置。如果狀態無法持久化，關卡會直接放行操作，不陷入迴圈，並在警告中點出這個變數。 |
| `GATEGUARD_METRICS` | 不設定（關閉） | 每一次 Edit/Write/MultiEdit/NotebookEdit/Bash/PowerShell 的決定，都在 `<GATEGUARD_STATE_DIR>/metrics.jsonl` 記一行（見[Decision metrics](#decision-metrics)）。絕不改變任何決定。 |
| `GATEGUARD_EXTERNAL_CONTRACT_QUESTION` | 不設定（關閉） | 在資料 schema 問題之後加一題 code 問題：說出 repo 之外有什麼決定了格式、單位、時區或協定語意。實驗性：在隱藏意圖的試驗裡，它沒有改變結果（`docs/gateguard/question-effectiveness.md`）。絕不改變任何決定。 |

`GATEGUARD_BASH_ROUTINE_DISABLED`、`GATEGUARD_METRICS` 和 `GATEGUARD_EXTERNAL_CONTRACT_QUESTION` 接受 `1`、`true`、`on`、`enabled`、`enable` 或 `yes`（不分大小寫和空白）；任何其他值都會讓一般關卡維持開啟、指標維持關閉、而且那一題不會被問。

#### Decision metrics

設了 `GATEGUARD_METRICS=1` 之後，每個關卡決定都會在狀態目錄的 `metrics.jsonl` 附加一行 JSON（一次 MultiEdit 呼叫，會為它決定的每個檔案各寫一行）：

```json
{"v":1,"ts":"2026-09-01T10:02:00.000Z","session":"3f9c0a1b2d4e","tool":"Edit","class":"code","decision":"deny","reason":"near-miss:out-of-scope","questions":["local-callers","quote-instruction"],"sensitive":false,"profile":{"known":true,"language":"js","touchesPublicSurface":false,"touchesData":false,"trivial":false}}
```

| Field | Meaning |
|---|---|
| `v` | schema 版本（`1`） |
| `session` | session key 的 sha256 的前 12 個十六進位字元 |
| `tool` | `Edit`、`Write`、`MultiEdit`、`NotebookEdit`、`Bash` 或 `PowerShell` |
| `class` | 目標類別，shell 指令則是 `null` |
| `decision` | `deny`、`credit`、`sibling`、`cap`、`trivial`、`pass-checked`、`pass-exempt`、`pass-subagent`、`routine-deny`、`routine-readonly`、`destructive-deny` 或 `pass` |
| `reason` | 簡短代碼：`first-touch`、`sensitive`、`hard-linked`、`near-miss:<code>`、`subagent-sensitive`、`subagent-hard-linked`、`prior-search`、`comment-whitespace`、`same-turn-dir`、`max-denials`、`checked`、`exempt-glob`、`claude-settings`、`no-path`、`subagent`、`readonly-git`、`readonly`、`first-command`、`routine-checked`、`routine-disabled`、`destructive`、`destructive-retry`、`state-error` |
| `questions` | 第一次碰檔案被拒絕時的問題 id；其他情況是 `null` |
| `sensitive` | 目標是不是[敏感目標](#sensitive-targets) |
| `profile` | 算過變更輪廓時的輪廓旗標；其他情況是 `null` |

**隱私：** 這些行絕不包含路徑、指令、檔案內容、transcript 文字，或 session id 本身；每個文字欄位都必須是簡短的小寫代碼，否則寫成 `null`。指標的錯誤會被忽略。超過 1 MiB 後，檔案會被改名成 `metrics.jsonl.1`，取代前一個。

用下面的指令彙整指標：

```bash
node scripts/gateguard-report.js            # GATEGUARD_STATE_DIR or ~/.gateguard
node scripts/gateguard-report.js --dir /path/to/state --json
```

它會先讀 `metrics.jsonl.1`，再讀 `metrics.jsonl`，跳過格式錯誤的行，並依每個 session 和整體印出：各類型的決定數、依類別和原因的拒絕數、跟在 near-miss 搜尋之後的第一次碰檔案拒絕所占的比例、第一次碰檔案之中拒絕、credit、同輩合併、上限和瑣碎編輯的比率、一般唯讀放行數，以及被問最多次的問題 id。

#### Turning the gate off completely

| Variable | Effect |
|---|---|
| `ECC_GATEGUARD=off` | 在這個 session 停用 GateGuard。接受 `0`、`false`、`off`、`disabled` 或 `disable`。 |
| `GATEGUARD_DISABLED=1` | 效果相同。只認 `1`：上面那些寫法在這裡**不**適用。 |

要做 hook 層級的控制，繼續用 `ECC_DISABLED_HOOKS` 搭配 GateGuard 的 hook ID。

#### Glob semantics for `GATEGUARD_EXEMPT_GLOBS`

Pattern 會比對整個專案相對的目標路徑。專案根目錄是 `CLAUDE_PROJECT_DIR`，沒有的話退回 hook payload 的 `cwd`，再退回 hook process 的工作目錄。相對的 glob 永遠不會豁免那個根目錄之外的目標。明確的絕對 glob 會比對整個絕對目標路徑，可以刻意豁免專案之外的路徑。

pattern 和路徑都用 `/` 當分隔符號，並用小寫比對。`*` 在單一片段內比對，`**` 跨片段比對，`?` 比對一個非分隔符號的字元。`**/` 包含零層目錄，所以 `**/tests/**` 也會比對到 `tests/foo.js`。格式錯誤的 pattern 會被丟棄，不會給出任何豁免。豁免在所有其他規則之前套用，包括敏感和 hard-link 規則（見 [Order of checks](#order-of-checks)）。

從 2.2.1 開始，`services/**` 只涵蓋專案根目錄的 services 目錄樹，`*.md` 只涵蓋它根目錄的 Markdown 檔。要涵蓋專案內所有的 Markdown 檔，請用 `**/*.md`。既有的、沒有錨定的豁免可能需要調整：

```json
{
  "env": {
    "GATEGUARD_BASH_ROUTINE_DISABLED": "1",
    "GATEGUARD_EXEMPT_GLOBS": "**/tests/**,tests/**,**/*.test.*,**/docs/**,**/dist/**"
  }
}
```

### Option B: Full package with config

```bash
pip install gateguard-ai
gateguard init
```

這會加上 `.gateguard.yml`，用來做每個專案的設定（自訂訊息、忽略的路徑、關卡的開關）。

## Anti-Patterns

- **不要改用自我評估。** 問「你確定嗎？」永遠得到「確定」。這已經被實驗驗證過。
- **不要跳過資料 schema 檢查。** 兩個 A/B 測試的 agent 都假設日期是 ISO-8601，但真實資料用的是 `%Y/%m/%d %H:%M`。檢查資料結構（用遮蔽過的值）可以避免這整類 bug。
- **不要擋每一個 Bash 指令。** 一般的 bash 每個 session 只擋一次。破壞性的 bash 則每次都擋。這樣的平衡能避免拖慢速度，同時攔下真正的風險。

## Best Practices

- 讓關卡自然地觸發。不要試圖預先回答關卡的問題，調查本身才是提升品質的關鍵。編輯之前針對目標做一次真正的搜尋就是調查，而且會得到 credit（見 [What Counts as Already Done](#what-counts-as-already-done)）。
- 針對你的領域客製關卡訊息。如果你的專案有特定的慣例，就把它們加進關卡的 prompt。
- 用 `.gateguard.yml` 忽略 `.venv/`、`node_modules/`、`.git/` 這類路徑。

## Related Skills

- `safety-guard`：執行期的安全檢查（互補，不重疊）
- `code-reviewer`：編輯之後的 review（GateGuard 是編輯之前的調查）
