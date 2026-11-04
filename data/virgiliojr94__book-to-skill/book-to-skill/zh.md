---
name: book-to-skill
description: "把書籍和文件（PDF、EPUB、DOCX、HTML、Markdown、純文字、RTF、搭配 Calibre 的 MOBI/AZW）轉成結構化的 agent skill，萃取出框架、心智模型、原則、技巧和反模式。使用者想透過 GitHub Copilot CLI、Amp、Claude Code、Hermes Agent、OpenCode 或 OpenClaw 研讀某份文件、在工作時套用作者的框架，或把檔案建成可重複使用的知識庫時使用。"
---

<!--
跨 agent 備註（僅供參考；host agent 會忽略）：
  - 相容的 skill 根目錄：GitHub Copilot CLI (~/.copilot/skills, ~/.agents/skills,
    .github/skills, .claude/skills, .agents/skills)、Amp (.agents/skills,
    ~/.config/agents/skills, ~/.config/amp/skills)、Claude Code (~/.claude/skills)、
    Hermes Agent ($HERMES_HOME/skills, .hermes/skills, .agents/skills)、
    OpenClaw (${OPENCLAW_STATE_DIR:-~/.openclaw}/skills, .agents/skills, skills/；
    ~/.agents/skills 只有在預設 state 時才適用)。
    OpenCode (~/.config/opencode/skills, ~/.claude/skills, .opencode/skills,
    ~/.agents/skills, .agents/skills)。
  - 刻意省略 `allowed-tools`，以保持跟 agent 無關：Copilot CLI 用
    `shell`/MCP-server 名稱，Claude 用 `Bash`/`Read`/`Write`/`Glob`/`Grep`，Amp
    另外加了 `shell_command`。這個 skill 需要 shell（用來執行 extract.py）和檔案
    讀寫，各個 host 在第一次使用時都會跳出提示來要這些權限。
  - 參數提示：<path-to-document-folder-or-glob>... [skill-name-slug]
-->

# Book-to-Skill Converter

把寫下來的知識轉成可執行的 agent skill，做法是萃取結構，而不是產出摘要。

## 理念

書裡有結晶化的專業知識：框架、原則和技巧，都是花了好幾年才發展出來的。這個 skill 把那些知識萃取成 GitHub Copilot CLI、Amp、Claude Code、Hermes Agent、OpenCode、OpenClaw 或其他相容 agent 可以反覆運用的格式。
**萃取結構，不要做摘要。** skill 不是讀書心得。它是一組工具箱：
- 有名字的框架（有明確應用方式的心智模型）
- 可執行的原則（引導決策的規則）
- 技巧（一步一步的方法）
- 反模式（要避免什麼，以及為什麼）
- 語氣校準（作者怎麼思考、怎麼溝通）

**保留作者的精確用詞。** 框架通常是有理由才取那個特定名字的。「The 5 Whys」不能跟「多問幾次為什麼」互換。要抓住確切的表述。

**依需要分層，深度適中。** 簡單的書 → 簡單的 skill。有 10 個以上框架的複雜書 → 帶有 reference 檔和隨選章節的 skill。

---

## 運作模式

有四條路徑。依使用者的要求來分流：

### 1. 完整轉換（預設）
**觸發：** 使用者提供一個或多個文件/目錄/glob 路徑，沒有特別指示
**動作：** 執行下面所有步驟（Step 0 到 9）
**輸出：** 完整的 skill，包含 SKILL.md、chapters/、glossary、patterns、cheatsheet

### 2. 只做分析
**觸發：** 使用者說「analyze」、「just extract」，或「我想在產生之前先看過」
**動作：** 執行 Step 0 到 3，然後產出結構化的萃取報告（找到的框架、原則、技巧）。到此為止，不要產生 skill 檔案。
**輸出：** 給使用者審閱的分析報告

### 3. 根據先前的分析來產生
**觸發：** 使用者已經有分析筆記，或之前跑過 analyze-only
**動作：** 跳過 Step 0 到 3，把提供的分析當輸入，執行 Step 4 到 9
**輸出：** 根據提供的分析產生 skill 檔案

### 4. 更新 / 併入（既有的 Skill）
**觸發：** 使用者提供一個或多個新的來源路徑，並表示想更新既有的 skill（可以是指向既有的 skill 資料夾、提供 `SKILLS_HOME` 裡已存在的 skill slug，或明確要求更新）。
**動作：** 執行 Step 0（範圍外檢查）、Step 1（驗證輸入）、Step 1.5（判斷書的類型）和 Step 2（萃取新檔案）。然後跳到 Step 5（辨識/偵測既有的 skill 路徑），執行 **Update / Fold-in Workflow**，把新內容合併進既有的 skill 檔案。
**輸出：** 更新後的既有 skill，帶有新增/修訂的章節摘要，以及合併後的索引/詞彙表。

---

## Skill 位置

這個 converter 可以在多種 skill 系統下執行。尋找這個 converter 的輔助 script，或寫出產生的書籍 skill 時，依下面的順序優先選擇：

1. GitHub Copilot CLI 個人 skill：`~/.copilot/skills/`
2. 跨 agent 的個人 skill（Copilot、Amp、Codex；OpenClaw 用預設 state 時）：`~/.agents/skills/`
3. Claude Code 個人 skill：`~/.claude/skills/`
4. 專案本地的 Copilot skill：`.github/skills/`
5. 專案本地的 Claude skill：`.claude/skills/`
6. 專案本地的 Amp / Copilot / OpenClaw skill：`.agents/skills/`
7. Amp 全域 skill：`~/.config/agents/skills/`
8. Amp 舊版全域 skill：`~/.config/amp/skills/`
9. Hermes Agent 個人 skill：`$HERMES_HOME/skills/`（預設是 `~/.hermes/skills/`）
10. Hermes Agent 專案 skill：`.hermes/skills/` 或 `.agents/skills/`
11. OpenClaw 個人 skill：`${OPENCLAW_STATE_DIR:-~/.openclaw}/skills/`（使用中的 state；`~/.agents/skills/` 只有在預設 state 時才共用）
12. OpenClaw 專案 skill：`.agents/skills/` 或 `skills/`
11. OpenCode 個人 skill：`~/.config/opencode/skills/` 或 `~/.agents/skills/`
12. OpenCode 專案 skill：`.opencode/skills/` 或 `.agents/skills/`

對於**產生出來的**書籍 skill，優先放在使用者層級的跨 agent 根目錄 `~/.agents/skills/`：一份實體副本就能服務跨 agent 的 host，以及用預設 state 的 OpenClaw。Copilot CLI 和 Amp 原生就會探索到它；Claude Code 需要從 `~/.claude/skills/<skill_name>` 建一個 symlink（在 Step 10 建立，規則見 Step 5）。只有使用者明確要求時，才選 host 私有或專案本地的根目錄。`BOOK_TO_SKILL_SCOPE=project` 或 `personal` 可以讓自動化明確指定這個選擇；不要僅僅因為兩種範圍都可用，就強制問一個範圍的問題。

---

## Step 0：範圍外檢查

如果沒有提供任何參數，就停下來並回應：
> "book-to-skill requires a supported document path, folder, or glob pattern. Usage: `book-to-skill <path-to-document-folder-or-glob>... [skill-name-slug]`"

整個工作流程中：
- **先解析目的地根目錄。** 在查詢任何既有 skill 之前，先決定這次執行會寫到哪裡：依 Step 5 的表格和選擇規則，選使用者 host 的個人根目錄或專案本地根目錄。要求專案本地的就用它的專案本地根目錄，絕對不要用個人根目錄。下面提到「解析後的根目錄」，就是指這個目的地。
- 辨識輸入路徑，以及選用的 skill slug。
- 如果最後一個參數不是存在或能比對到任何檔案的檔案、資料夾或 glob，而且看起來像 skill slug（例如小寫加連字號、英數字），就當成 `SKILL_NAME`。
- 其他所有參數都當成 `INPUT_PATHS` 清單。
- 如果任何輸入路徑是既有的 skill 目錄（含有 `SKILL.md` 和 `chapters/` 子資料夾），或 `SKILL_NAME` 符合解析後根目錄中既有的 skill slug，就把這次執行標記為 **Update/Fold-in** 操作（Mode 4）。
- **重跑防護。** 完整轉換開始萃取之前，依 Step 5 的命名選項推導出預期的 skill slug（author-concept 形式、by-title 形式，以及任何給定的 `SKILL_NAME`），並到解析後的根目錄檢查有沒有符合的既有項目。有符合的話就停下來問使用者：「`<skill-name>` already exists. Choose: (1) Update/Fold-in (Mode 4), (2) verify the existing skill is complete and stop, or (3) force full regeneration.」使用者選好之前不要重新萃取。如果是在中斷的執行之後做 context 恢復（網路斷線、對話被重播或延續），要重用那次執行回報的萃取工作目錄（輸出裡的 `Workdir ->`，或你在 `BOOK_SKILL_WORKDIR` 設的路徑），**但前提是它仍然完整，而且仍然符合目前的輸入和選項**：目錄存在、它的 `metadata.json` 讀得到、它列的 `sources` 跟現在要轉換的檔案在檔名**和內容指紋**上一一對應（萃取器會在 `metadata.json` 裡記錄每個來源的 `sha256`；要對每個檔案現在的樣子重新計算指紋，並要求完全一致，`book_to_skill/utils.py` 裡的 `reuse_is_safe()` 就是這個檢查的可執行版本），而且它記錄的 `extraction_mode` 就是這次執行用的 mode（Step 2 的「確認萃取出來的是你要的文件」規則）。如果它不見了（暫存被清掉）、它的 `metadata.json` 不見了、來源不再相符（檔名不同，或內容指紋變了）、記錄的 metadata 裡有來源沒有 `sha256`（是在有指紋功能之前記錄的，無法確認新鮮度），或 mode 不同，就明講這件事，並重新開始萃取，不要接續。有疑慮就先問使用者，再決定要丟掉還是接續。

---

## Step 1：驗證輸入

確認 `INPUT_PATHS` 裡至少有一個支援的檔案、目錄或 glob pattern。
目錄和 glob 要展開，找出符合的支援檔案（`.pdf`、`.epub`、`.docx`、`.txt`、`.md`、`.markdown`、`.rst`、`.adoc`、`.html`、`.htm`、`.rtf`、`.mobi`、`.azw`、`.azw3`）。

如果找不到任何支援的檔案，就停下來並給出清楚的錯誤訊息。

---

## Step 1.5：判斷內容類型

萃取之前，先問使用者：

> "What kind of content do these sources have? This helps me choose the best extraction method.
>
> 1. **Technical** — has code blocks, tables, formulas, diagrams (e.g. programming books, academic papers, architecture guides)
> 2. **Text-heavy** — mostly prose, few or no tables/code (e.g. management, productivity, narrative non-fiction)
> 3. **Not sure** — I'll use the fast method and warn you if quality seems limited"

把答案存成 `BOOK_TYPE`：
- 選項 1 → `BOOK_TYPE=technical`
- 選項 2 → `BOOK_TYPE=text`
- 選項 3 → `BOOK_TYPE=text`

**如果 `BOOK_TYPE=technical`**，繼續之前先告知使用者：
> "📐 Technical mode selected — PDFs attempt Docling for layout-aware extraction. EPUBs and other formats use their existing text extractors; code, tables, and formulas may lose structure. Check each source's `extraction_method` and `fallback_reason` in metadata.json for the actual extraction path."

**如果 `BOOK_TYPE=text`**，告知：
> "📄 Text mode selected — using the fastest suitable extractor for each file type. Plain text/Markdown/HTML are usually ready in seconds; PDFs use pdftotext when available."

---

## Step 2：從來源文件萃取文字

執行萃取 script，傳入輸入路徑：

```bash
SCRIPT_PATH=""
HERMES_HOME_RESOLVED="${HERMES_HOME:-$HOME/.hermes}"
OPENCLAW_STATE_DIR_RESOLVED="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
HERMES_PROJECT_TRUSTED=false
if [ -n "$PROJECT_ROOT" ] && [ "${HERMES_AGENT:-}" = true ] && \
  command -v hermes >/dev/null 2>&1 && \
  command -v python3 >/dev/null 2>&1 && \
  hermes config get skills.trusted_project_dirs --json 2>/dev/null | PROJECT_ROOT="$PROJECT_ROOT" python3 -c 'import json, os, pathlib, sys; root=pathlib.Path(os.environ["PROJECT_ROOT"]).resolve(); sys.exit(not any(pathlib.Path(p).expanduser().resolve() == root for p in json.load(sys.stdin)))' 2>/dev/null
then
  HERMES_PROJECT_TRUSTED=true
fi

CANDIDATES=(
  "$HOME/.copilot/skills/book-to-skill/scripts/extract.py"
  "$HOME/.agents/skills/book-to-skill/scripts/extract.py"
  "$HOME/.claude/skills/book-to-skill/scripts/extract.py"
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills/book-to-skill/scripts/extract.py"
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/*/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/*/*/*/book-to-skill/scripts/extract.py
  "${OPENCLAW_STATE_DIR_RESOLVED}/skills"/*/*/*/*/*/*/book-to-skill/scripts/extract.py
  "$HOME/.config/opencode/skills/book-to-skill/scripts/extract.py"
  "$HERMES_HOME_RESOLVED/skills/book-to-skill/scripts/extract.py"
  "$HERMES_HOME_RESOLVED"/skills/*/book-to-skill/scripts/extract.py
)
if [ "${HERMES_AGENT:-}" != true ]; then
  # Project-local roots are resolved against the git worktree, not the current
  # directory: an agent can be invoked from anywhere inside the project (e.g.
  # `src/nested`) and these roots still have to be found — that is how OpenCode
  # and the other hosts discover project skills. The CWD-relative forms are kept
  # so the probe also works outside a git repository.
  if [ -n "$PROJECT_ROOT" ]; then
    CANDIDATES+=(
      "$PROJECT_ROOT/.github/skills/book-to-skill/scripts/extract.py"
      "$PROJECT_ROOT/.claude/skills/book-to-skill/scripts/extract.py"
      "$PROJECT_ROOT/.agents/skills/book-to-skill/scripts/extract.py"
      "$PROJECT_ROOT/.opencode/skills/book-to-skill/scripts/extract.py"
    )
  fi
  CANDIDATES+=(
    ".github/skills/book-to-skill/scripts/extract.py"
    ".claude/skills/book-to-skill/scripts/extract.py"
    ".agents/skills/book-to-skill/scripts/extract.py"
    "skills/book-to-skill/scripts/extract.py"
    "skills"/*/book-to-skill/scripts/extract.py
    "skills"/*/*/book-to-skill/scripts/extract.py
    "skills"/*/*/*/book-to-skill/scripts/extract.py
    "skills"/*/*/*/*/book-to-skill/scripts/extract.py
    "skills"/*/*/*/*/*/book-to-skill/scripts/extract.py
    "skills"/*/*/*/*/*/*/book-to-skill/scripts/extract.py
    ".opencode/skills/book-to-skill/scripts/extract.py"
  )
  if [ -n "$PROJECT_ROOT" ]; then
    CANDIDATES+=(
      "$PROJECT_ROOT/skills/book-to-skill/scripts/extract.py"
      "$PROJECT_ROOT/skills"/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/*/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/*/*/*/book-to-skill/scripts/extract.py
      "$PROJECT_ROOT/skills"/*/*/*/*/*/*/book-to-skill/scripts/extract.py
    )
  fi
fi
CANDIDATES+=(
  "$HOME/.config/agents/skills/book-to-skill/scripts/extract.py"
  "$HOME/.config/amp/skills/book-to-skill/scripts/extract.py"
)
if [ "$HERMES_PROJECT_TRUSTED" = true ]; then
  CANDIDATES=(
    "$PROJECT_ROOT/.hermes/skills/book-to-skill/scripts/extract.py"
    "$PROJECT_ROOT/.hermes/skills"/*/book-to-skill/scripts/extract.py
    "$PROJECT_ROOT/.agents/skills/book-to-skill/scripts/extract.py"
    "$PROJECT_ROOT/.agents/skills"/*/book-to-skill/scripts/extract.py
    "${CANDIDATES[@]}"
  )
fi
for candidate in "${CANDIDATES[@]}"
do
  if [ -f "$candidate" ]; then
    SCRIPT_PATH="$candidate"
    break
  fi
done

if [ -z "$SCRIPT_PATH" ]; then
  echo "Could not find scripts/extract.py for book-to-skill" >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

"$PYTHON_BIN" "$SCRIPT_PATH" $INPUT_PATHS --mode <BOOK_TYPE> --install-missing ask
```

萃取之前，script 會檢查偵測到的格式所需要的選用 Python 套件。如果缺少比較好的萃取器，它會提示使用者有哪些可用的 fallback。非互動式的 session 預設走 fallback，除非 install mode 明確設成 `yes`。

**提示：預先檢查環境：** 執行 `"$PYTHON_BIN" "$SCRIPT_PATH" --check`，會印出每種格式的報告，說明哪些萃取器已安裝，以及缺少的部分要用什麼指令安裝，過程中不會處理任何檔案。使用者回報設定或品質問題時很有用。

這會建立一個**每次執行專屬**的工作目錄：預設是 `<tempdir>/book_skill_work-<pid>/`，或是你在 `BOOK_SKILL_WORKDIR` 設的確切路徑，裡面包含：
- `full_text.txt`：所有來源合併後的萃取文字，有清楚、看得見的分界。
- `metadata.json`：合併後的整體大小、字數、頁數、token 數、被丟掉的 EPUB 圖片數、解析後的 `workdir`，以及詳細的各個已處理 `sources` 清單。

執行完成時會印出這三個路徑（`Workdir ->`、`Text ->`、`Meta ->`）。**要從那個輸出（或 `metadata.json` 自己的 `workdir` 欄位）取得路徑，不要假設固定位置**：每次執行的目錄名稱都不同，這樣同一台機器上並行的萃取才不會互相覆蓋結果。

讀那次執行的 `metadata.json` 來檢查結果。

**產生任何東西之前，一定要先確認萃取出來的是你要的文件**：檢查 `metadata.json` 裡的 `filename` / `source_file`，或 `full_text.txt` 第一行的 `SOURCE:` 標頭。如果你在等背景執行，要等*它*專屬的 workdir：輪詢共用路徑可能會拿到另一次執行的輸出。

---

## Step 2.5：預先估算成本

讀這次執行的 `metadata.json`（萃取輸出裡的 `Meta ->` 路徑），在**做任何產生動作之前**，先給使用者一份估算：

```
📖 Sources detected: <total_sources> source(s)
<list each source filename and format from the sources metadata list>
<if images_dropped > 5: warn that N source images were not read>
📄 Combined Pages/Sections: ~<N> | Words: ~<N> | Total tokens: ~<N>K

💰 Estimated token cost (Full Conversion / Update):
   Input  (reading + prompts): ~<N>K tokens
   Output (skill files generated/updated):  ~<N>K tokens
   Total:                           ~<N>K tokens

   Cost: multiply the token counts above by your model's current
   input/output per-1M-token rates (prices and model names change often —
   do not hardcode them; quote today's rate and label it as an estimate).

   ⏱  Estimated time: ~<N> minutes

📁 Files to be generated/updated:
   SKILL.md + chapter files + glossary + patterns + cheatsheet

➡  Proceed with Full Conversion / Update? (or type "analyze only" to preview first)
```

**怎麼估算：**
- Input token ≈ metadata 裡的 `estimated_tokens` × 1.3（每個章節 pass 的 prompt 額外開銷）
- Output token ≈ 章節數 × 每章預算 + 4,000（SKILL.md）+ 4,500（glossary + patterns + cheatsheet）
  - 依 `BOOK_TYPE` 的每章預算中位數（DEPTH 在稍後的 Step 4 決定，可能會把它調高）：`text` ≈ 1,000，`technical` ≈ 1,800。如果使用者已經表明是只當參考還是要深入研讀，就用 Step 7 矩陣中對應的那一列。
- 成本：回報 token 數，再乘上使用者目前每百萬 token 的 input/output 費率。**不要寫死美元金額**：模型名稱和價格常常在變；如果要顯示，要標成估算並註明日期。

等使用者確認再繼續。如果他們說「analyze only」，就切到 Mode 2。

---

## Step 2.6：大型書籍（> 50k token）的 REPL 式存取

靈感來自 Recursive Language Model（RLM）的範式：把 `full_text.txt` 當成可以查詢的語料庫，不要一次整份讀進來。把整份檔案載入 context，會燒掉你之後產生內容時需要的預算。

對於超過約 50k token 的書，優先用程式化的探查，不要不設範圍就 `Read(full_text.txt)`：

```bash
# Size check before any Read
wc -w "$FULL_TEXT_PATH"

# Find chapter offsets without loading the whole file
grep -n -E "^\s*(Chapter|CHAPTER)\s+[0-9]+" "$FULL_TEXT_PATH" | head -40

# Pull only the chapter you need (lines start..end inclusive)
sed -n '<start>,<end>p' "$FULL_TEXT_PATH"

# Verify a framework is actually mentioned before claiming it in SKILL.md
grep -c -i "westrum\|dora" "$FULL_TEXT_PATH"

# Targeted Read with offset/limit avoids dumping the full file
# Read(file_path=full_text.txt, offset=<line>, limit=<lines>)
```

Step 3（結構分析）、Step 7（每章摘要）和 Step 8（glossary / patterns 萃取）都用這個做法。50k token 以下的書，直接 `Read` 一次就好。

為什麼重要：200 頁的書大約是 75k token。每一章重讀一次（28 個 pass）要花約 2M 的 input token；改用 grep + sed 只取相關的片段，產生的成本就會跟輸出成正比，不是跟來源成正比。

---

## Step 3：分析書的結構

讀萃取出來的 `full_text.txt` 前 8,000 個字元，辨識出：
- 書名和**作者**
- **章節結構**（找「Chapter N」、「PART I」、有編號的標題、目錄）
- **核心主題**和主題領域
- 大約的章節數

如果有目錄的話，再讀目錄區段，把所有章節對應出來。

**如果 mode 是「Analyze Only」：** 現在就產出萃取報告然後停止。結構如下：
```
## Extraction Report — <Title>

### Author's Core Frameworks
- **<Framework Name>**: <what it is and when to apply>

### Key Principles
- <Principle>: <actionable rule>

### Techniques & Methods
- <Technique>: <step-by-step or how-to>

### Anti-patterns
- <What to avoid>: <why>

### Suggested Skill Name
`{author-lastname}-{core-concept}` — e.g. `cialdini-influence`

### Chapters Detected
| # | Title | Main Frameworks |
```

---

## Step 4：詢問目的（僅限完整轉換）

產生之前，先問使用者：

> "What should this skill help you do? (Pick one or more)
> 1. Apply the author's frameworks while working
> 2. Think with the author's mental models
> 3. Reference specific chapters and concepts
> 4. All of the above"

用答案來決定 SKILL.md 的 Core 區段要重點強調什麼。

**從答案推導出 `DEPTH`（不用另外再問）：**
- 答案**只有**選項 3（reference） → `DEPTH=reference`：精簡、方便快速查詢的章節。
- 答案包含選項 1、2 或 4 → `DEPTH=study`：更深入的章節，有更多實例細節、範例和推理。

`DEPTH` 和 `BOOK_TYPE` 一起決定 Step 7 裡每章的 token 預算。**不要**另外問「study 還是 reference」：這裡就推導出來了。（在 Mode 2/3，Step 4 會被跳過，預設 `DEPTH=study`。）

---

## Step 5：決定 skill 名稱

如果有提供 `SKILL_NAME`，就用它當 skill slug。
否則，提出兩個選項讓使用者選：
- **用作者-概念**：`{author-lastname}-{core-concept}`（例如 `cialdini-influence`、`meadows-systems`）
- **用書名**：把書名轉成小寫加連字號（例如 `designing-data-intensive-apps`）

如果這本書有很強的方法論辨識度，預設用作者-概念的格式。

選擇目的地 skill 根目錄（`SKILLS_HOME`）。先從使用者明確的要求或 `BOOK_TO_SKILL_SCOPE` 解析出**範圍**，再探測 **host**。要求專案本地/專案輸出，就選專案本地那一列；要求個人/全域輸出，就選個人那一列。如果兩種範圍都沒有要求，維持既有的個人預設（非 Hermes 的 host 用 `~/.agents/skills`）。不要僅僅因為存在專案本地的根目錄，就強制問一個範圍的問題。選中的根目錄寫入之前，可能還是需要 host 批准。

| Host agent | 個人 skill 根目錄 | 專案本地根目錄 |
|---|---|---|
| **GitHub Copilot CLI** | `~/.agents/skills`（原生探索得到） | `.github/skills` → `.claude/skills` → `.agents/skills` |
| **Amp** | `~/.agents/skills`（原生探索得到） | `.agents/skills` |
| **OpenAI Codex** | `~/.agents/skills`（原生探索得到；會跟隨 symlink） | `.agents/skills` |
| **Hermes Agent** | `$HERMES_HOME/skills/<category>`（預設是 `~/.hermes/skills/<category>`） | `.hermes/skills/<category>` → `.agents/skills` |
| **Claude Code** | `~/.agents/skills` + 從 `~/.claude/skills/<skill_name>` 建 symlink | `.claude/skills` |
| **OpenClaw** | `${OPENCLAW_STATE_DIR:-~/.openclaw}/skills`（使用中的 state；`~/.agents/skills` 只有預設 state 才適用） | `.agents/skills` → `skills/` |

Hermes Agent 是唯一保留自己個人根目錄的 host：它把個人 skill 依類別分區，而且不會掃描跨 agent 根目錄。要用目前使用中 profile 的 `HERMES_HOME`，並選一個符合所產生 skill 主題的類別。不要手動組 profile 路徑。如果使用者選了專案本地的 Hermes 根目錄，產生之後要執行 `hermes skills trust <project-root>`，並用 `hermes skills list` 驗證探索得到；專案信任之前，專案 skill 都不會生效。

OpenClaw 要用使用中 state 目錄的 `skills/` 根目錄：`${OPENCLAW_STATE_DIR:-~/.openclaw}/skills/`。共用的 `~/.agents/skills` 相容根目錄，只有在 `OPENCLAW_STATE_DIR` 沒設定或是預設的 `~/.openclaw` 時才探索得到；用非預設 state 時，不要宣稱 OpenClaw 看得到安裝在共用根目錄的東西。產生之後用 `openclaw skills list` 驗證探索得到。
| **OpenCode** | `~/.agents/skills`（原生探索得到；也會讀 `~/.config/opencode/skills` 和 `~/.claude/skills`） | `.opencode/skills` → `.agents/skills` → `.claude/skills` |

Hermes Agent 是唯一保留自己個人根目錄的 host：它把個人 skill 依類別分區，而且不會掃描跨 agent 根目錄。要用目前使用中 profile 的 `HERMES_HOME`，並選一個符合所產生 skill 主題的類別。不要手動組 profile 路徑。如果使用者選了專案本地的 Hermes 根目錄，產生之後要執行 `hermes skills trust <project-root>`，並用 `hermes skills list` 驗證探索得到；專案信任之前，專案 skill 都不會生效。

OpenCode 原生就會掃描跨 agent 的 `~/.agents/skills` 根目錄，所以上面產生 skill 的預設已經涵蓋它，不需要 symlink，也不需要信任步驟。它也會讀自己管理的 `~/.config/opencode/skills` 根目錄，以及 Claude 相容根目錄 `~/.claude/skills`；只有使用者要求時，才用 OpenCode 管理的根目錄。專案 skill 的探索方式，是從工作目錄往上走到 git worktree，所以如果產生之後 skill 沒出現，就開一個新的 session。（`~/.cache/opencode/skills` 是從 `skills.urls` 下載遠端 skill 的快取，不是用來寫 skill 的根目錄，絕對不要把產生的 skill 寫到那裡。）

選擇規則：
1. 個人安裝：把 `SKILLS_HOME` 設成 `~/.agents/skills`（目錄不存在就建立）。有一個例外，避免預設值在別人家裡發明慣例：如果 `~/.agents/skills` 不存在，**而且** host 的私有根目錄裡已經有 skill，就改用私有根目錄，並在報告裡說明原因。
2. **Claude Code 不會掃描 `~/.agents/skills`**：產生完成後，Step 10 會用 `ln -sfn "$HOME/.agents/skills/<skill_name>" "$HOME/.claude/skills/<skill_name>"` 把 skill 連過去。
3. **Hermes Agent 的個人安裝用上面 Hermes 那一列**，不用跨 agent 根目錄，也不用 symlink。
4. 如果使用者明確要求 host 私有的根目錄（`~/.copilot/skills`、`~/.claude/skills`、`~/.config/agents/skills`、`~/.config/amp/skills`），就照辦並跳過 symlink。
5. 如果使用者明確要求專案本地輸出，就用他的 host 對應的專案本地那一列。
6. 如果選擇需要知道 host（專案本地輸出、Hermes 個人根目錄、OpenClaw state 根目錄，或 Claude Code symlink），而你無法辨識，就問：「Which agent are you running in — OpenCode, OpenClaw, Hermes Agent, GitHub Copilot CLI, Amp, Codex, or Claude Code?」
7. OpenClaw 的個人輸出，用 `${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/skills`。共用的 `~/.agents/skills` 根目錄，只有在 `OPENCLAW_STATE_DIR` 沒設定或等於預設的 `$HOME/.openclaw` 時，才是有效的 OpenClaw 目的地；否則用使用中的 state 根目錄，或專案/額外目錄。
8. 如果使用者明確要求 OpenClaw 管理的個人根目錄，就用使用中的 state 根目錄，並用 `openclaw skills list` 驗證探索得到。

把 `SKILLS_HOME` 設成選中的根目錄，並檢查 `$SKILLS_HOME/<skill_name>/` 是否已經存在。在 Claude Code 上，還要檢查 `~/.claude/skills/<skill_name>` 是否是**真正的目錄**（不是 symlink）：之前的安裝可能放在那裡；如果是，繼續之前先提議遷移（把目錄移到 `~/.agents/skills/`，再用 symlink 取代原本的路徑）。
如果 skill 已經存在，提示使用者選擇：
1. **Update / Fold-in**（Mode 4）：把新檔案/內容整合進既有 skill 的各個組成。
2. **Overwrite**：刪除並從頭重新產生 skill。
3. **Rename**：加上 `-2`，或用不同的自訂 slug。

如果使用者選 **Update / Fold-in**，就在 Step 2.5 之後立刻進入 **Update / Fold-in Workflow** 區段（跳過 Step 3、4、6、7、8、9）。

---

## Step 6：建立 skill 的目錄結構

```bash
mkdir -p "$SKILLS_HOME/<skill_name>/chapters"
```

---

## Step 7：產生章節摘要

**TOKEN 預算規則：非常重要（自適應）：**

每章的預算會依 `BOOK_TYPE` 和 `DEPTH` 縮放。技術性的章節需要空間放程式碼和表格；study 深度需要空間放推導過程。從這個矩陣挑預算：

| | `DEPTH=reference` | `DEPTH=study` |
|---|---|---|
| `BOOK_TYPE=text` | 800–1,200 tokens | 1,000–1,800 tokens |
| `BOOK_TYPE=technical` | 1,200–1,800 tokens | 2,000–3,000 tokens |

- 這些是每個檔案的目標，不是硬性上限：內容密集的章節可以超過，單薄的可以少一點。密度還是比長度重要（Quality Rule #3）：絕對不要為了湊數字而灌水。
- 檔案是隨選載入的，所以章節比較大，只有在那一章真的被讀到時才會花 token。
- 如果在兩個格子之間拿不定主意（例如內容混合的書），就用比較低的預算，讓深度來自精確，不是份量。

**`DEPTH=study` 要靠內容來換，不是靠把數字加大。** 標準的區段範本（Core Idea → Connects To）自然會讓一份密集的散文章節落在約 700 到 900 token。要*誠實地*達到 study 預算，不能靠灌水，study 深度的章節必須加進具體的素材：
- 在 `## Worked Example` 區段下，**重現這一章裡的一個實作範例或成品**（例如範例新聞稿、一段示範對話、填好的範本、作者一路推演的某個決定）。這是最大的槓桿，也是學習者會回來看的主要內容。
- 把每個框架的「How」**擴充成明確的步驟或準則**，不要只有一行。
- 對最重要的 1 到 2 個框架，**加一段簡短的「為什麼有效 / 失敗模式」說明**。

如果某一章確實沒有實作範例、也難以擴充，就讓它落在 study 下限以下，不要灌水，並在它的 Core Idea 裡註明這一章內容單薄。相對地，`reference` 深度的章節會刻意省略實作範例，只保留能直接拿來做決定的精華。

對於 Step 3 辨識出的每一個章節/主要區段：

用 `metadata.json` 裡頂層的 `chapter_ranges`（有的話；`start_line`/`end_line` 是 1-based 且包含頭尾，給 `sed`/`Read` 用）去讀萃取出來的 `full_text.txt` 的對應區段；否則就 grep 章節標題。（`sources[].chapter_ranges` 用同樣的欄位，但行號只對應那個來源自己的文字，不是合併後的 `full_text.txt`。）

用下面的結構建立 `$SKILLS_HOME/<skill_name>/chapters/ch<NN>-<slug>.md`。

**依 `BOOK_TYPE` 調整重點：**
- `technical` → 優先處理「Code Examples」、「Reference Tables」和「Commands & APIs」區段；保留確切的語法
- `text` → 優先處理「Frameworks Introduced」、「Mental Models」和「Key Takeaways」；跳過空的技術性區段

```markdown
# Chapter N: <Full Title>

## Core Idea
<1–2 sentences: the single most important thing this chapter teaches>

## Frameworks Introduced
- **<Framework Name>**: <exact formulation — preserve the author's naming>
  - When to use: <specific situation>
  - How: <steps or criteria>

## Key Concepts
- **<Term>**: <precise definition in 1 sentence>
(5–10 most important terms from this chapter)

## Mental Models
<2–4 frameworks or thinking tools. Write as "Use X when Y" or "Think of X as Y">

## Anti-patterns
- **<What to avoid>**: <why it fails>

## Code Examples *(technical books only — omit if BOOK_TYPE=text)*
<!-- Copy the most instructive snippet from the chapter. Preserve indentation exactly. -->
```<language>
<key code example from this chapter>
```
- **What it demonstrates**: <one line>

## Reference Tables *(technical books only — omit if BOOK_TYPE=text)*
<!-- Reproduce any comparison matrix, parameter table, or decision table from the chapter in markdown. -->

## Worked Example *(DEPTH=study only — omit for DEPTH=reference)*
<!-- Reproduce or reconstruct one concrete example the author works through: a
     sample document, a dialogue, a filled-in template, a before/after, or a
     decision walked end-to-end. This is what makes a study chapter worth its
     budget. Keep it faithful to the source; never copy long raw passages —
     reconstruct the example compactly. -->

## Key Takeaways
1. <Actionable insight>
2. <Actionable insight>
3. <Actionable insight>
(3–7 takeaways a practitioner must remember)

## Connects To
- **Ch N**: <why this chapter relates>
- **<Concept>**: <external concept or standard it connects with>
```

---

## Step 8：產生輔助檔案

### glossary.md
建立 `$SKILLS_HOME/<skill_name>/glossary.md`：
- 書裡每個重要的名詞，依字母排序
- 格式：`**Term** — definition (Ch N)`
- 最多 1,500 tokens

### patterns.md
建立 `$SKILLS_HOME/<skill_name>/patterns.md`：
- 書裡所有具體的技巧、設計模式、演算法
- 格式：`## Pattern Name\n**When to use**: ...\n**How**: ...\n**Trade-offs**: ...`
- 最多 2,000 tokens

### cheatsheet.md
建立 `$SKILLS_HOME/<skill_name>/cheatsheet.md`：

**這是 skill 裡最有差異化的一層，要把它當成推理的輔助，不是關鍵字清單。** 誰都可以去 glossary grep 一個名詞。cheatsheet 抓的是作者的*判斷*：他們會做的決定，以及為什麼。這個檔案能把「我懂這些字」變成「我會照作者的方式行動」。

依序優先處理：
1. **決策規則**：「當 X 時，做 Y，因為 Z。」作者運用的 if/then 邏輯，寫成讀者不用重讀整本書就能套用的形式。
2. **決策樹 / 流程圖**（用巢狀 bullet 或小表格）：給超過兩個分支的選擇。
3. **權衡矩陣**：把互相競爭的選項，依作者在意的維度打分，讓讀者能在自己的限制下做選擇。
4. **門檻與預設值**：作者堅持的具體數字、比例或經驗法則（例如「函式保持在約 20 行以內」、「error budget < 10% 時發警報」）。
5. **徵兆與壞味道**：快速辨認情境的啟發式（「如果你看到 X，你大概遇到 Y 麻煩了」）。

避免：只有名詞→定義的列（那是 glossary），以及散文段落（那是 chapters）。每一行都應該幫讀者*決定*某件事。

- 格式以精簡的表格和決策規則為主；內容要像你工作時放在身邊的一張列印紙。
- 最多 1,200 tokens。

---

## Step 9：產生主要的 SKILL.md

**重要的 TOKEN 預算：SKILL.md 本文要控制在 4,000 token 以下。**
壓縮（compaction）是從尾端開始截斷的，所以要把最重要的內容放在最前面。

建立 `$SKILLS_HOME/<skill_name>/SKILL.md`：

```markdown
---
name: <skill_name>
description: "Knowledge base from \"<Full Title>\" by <Author(s)>. Use when applying <author>'s frameworks for <key topics, 3–6 terms>, studying the book, or referencing its concepts."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# <Full Title>
**Author**: <Author(s)> | **Pages**: ~<N> | **Chapters**: <N> | **Generated**: <YYYY-MM-DD>

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `replication`, `pricing`, or another indexed topic; I find and read the relevant chapter
- **With chapter** — ask for `ch05`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read
the relevant chapter file before answering.

---

## Core Frameworks & Mental Models
<!-- ~2,000 tokens: the author's most important named frameworks and principles.
     Preserve exact names. Write as "Use X when Y", "Prefer X over Y because Z".
     This is a toolkit, not a summary. -->

<generate 2,000 tokens of the most critical frameworks and insights here>

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-<slug>.md) | <Title> | <framework1>, <framework2> |
| [ch02](chapters/ch02-<slug>.md) | <Title> | <framework1>, <framework2> |
...

## Topic Index

<!-- Alphabetical. Major terms/frameworks → chapter(s) that cover them. -->
- **<Term>** → ch<N>[, ch<N>]
- **<Term>** → ch<N>

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides
- Full text: `<output_text from metadata.json>` — grep it for depth the chapter files omit (local extraction, not shipped)

---

## Scope & Limits

This skill covers the book content only. For hands-on implementation in your codebase,
combine with project-specific tools. For topics beyond this book, check related skills
or ask the agent directly.
<if images_dropped > 5: state that N source images were not read>
```

---

## Step 9.5：掃描產生出來的 skill

回報成功、在另一個 session 載入這個 skill、或發布它之前，先執行這個建議性的安全掃描：

```bash
SKILL_CONVERTER_ROOT="$(cd "$(dirname "$SCRIPT_PATH")/.." && pwd)"
"$PYTHON_BIN" "$SKILL_CONVERTER_ROOT/tools/scan_generated_skill.py" "$SKILLS_HOME/<skill_name>"
```

如果掃描器以非 0 結束，就停下來，請人類審查它回報的檔案/行號。不要偷偷改寫產生的檔案，而且在問題解決或明確被接受之前，不要載入或發布這個 skill。

---

## Step 10：清理與回報

如果 host 是 Claude Code，而且 `SKILLS_HOME` 是 `~/.agents/skills`（預設的個人安裝），就用 symlink 把 skill 暴露給 Claude Code，因為 Claude Code 只會掃描 `~/.claude/skills`：

```bash
mkdir -p "$HOME/.claude/skills"
LINK="$HOME/.claude/skills/<skill_name>"
TARGET="$HOME/.agents/skills/<skill_name>"
if [ -d "$LINK" ] && [ ! -L "$LINK" ]; then
  CLAUDE_STATUS="skipped-realdir"                 # Step 5 migration declined; leave the old dir
else
  ln -sfn "$TARGET" "$LINK" 2>/dev/null || true
  # Read the link back — do NOT trust that `ln` did what was asked. On Windows/MSYS
  # `ln -s` may COPY instead of link (or need Developer Mode / an elevated shell), and
  # PowerShell/cmd have no `ln` at all. The report must reflect what is on disk, not the
  # fact that the command ran.
  if [ -L "$LINK" ] && [ "$(readlink "$LINK")" = "$TARGET" ]; then
    CLAUDE_STATUS="linked"
  elif [ -e "$LINK" ]; then
    CLAUDE_STATUS="copy"                           # a real file/dir landed instead of a link
  else
    CLAUDE_STATUS="absent"                         # ln unavailable or refused
  fi
fi
```

必須有 real-directory 的防護：對既有的真實目錄執行 `ln -sfn`，會把連結巢狀地建在它*裡面*（`~/.claude/skills/<skill_name>/<skill_name>`），讓 Claude Code 繼續載入過期的副本。如果使用者拒絕了 Step 5 的遷移，就跳過 symlink，並在報告裡說明：在遷移之前，Claude Code 會繼續用舊目錄。

**回報任何關於連結的事情之前，先把連結讀回來確認。** symlink 是一個宣稱，不是事實：「Discoverable by」那一行要根據 `CLAUDE_STATUS`（磁碟上實際的狀態）來填，絕對不要根據「指令已經下過了」。**連結不見了或是副本時，不要直接失敗中止**：skill 在 hub 上存在，其他每個 host 仍然找得到；誠實的報告是「已寫到 `~/.agents/skills/<skill_name>`；在建立連結之前，Claude Code 看不到它」，不是中止。（Windows 的線索，未驗證：directory junction，也就是在提升權限的 `cmd` 裡用 `mklink /J`，或在 PowerShell 裡用 `New-Item -ItemType Junction`，既不需要 Developer Mode 也不需要 symlink 權限；如果你嘗試這個，也不會改變「先讀回再回報」的規則。）

如果使用者選的是 host 私有或專案本地的根目錄（Step 5，規則 3-4），就跳過這個。

然後清理萃取的 workdir：

```bash
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

Remove **the work directory this run actually used** — the `Workdir ->` path from the
extraction output, which is also stored as `workdir` in `metadata.json`. Never delete a
directory you did not create: another extraction may be running beside yours.

```bash
# WORKDIR is the path this run reported; quote it in case of spaces.
rm -rf "$WORKDIR"
```

Equivalently, if you still have the metadata file:

```bash
"$PYTHON_BIN" - "$WORKDIR_METADATA_JSON" <<'PY'
import json
import shutil
import sys
from pathlib import Path

meta_path = Path(sys.argv[1])
workdir = json.loads(meta_path.read_text(encoding="utf-8")).get("workdir")
if workdir:
    shutil.rmtree(workdir, ignore_errors=True)
PY
```

Older copies of this file removed a single fixed `book_skill_work` directory. That path is
no longer used, so such a cleanup is now a harmless no-op rather than something that could
delete a concurrent run's output.

然後向使用者回報：

```
✅ Skill created: $SKILLS_HOME/<skill_name>/

📚 Book: <Full Title> — <Author>
📄 Pages: ~<N> | Chapters: <N>

Files generated:
  SKILL.md         — core frameworks + index   (~X tokens)
  chapters/        — <N> chapter summaries     (~X tokens each, ~X total)
  glossary.md      — key terms                 (~X tokens)
  patterns.md      — techniques & patterns     (~X tokens)
  cheatsheet.md    — quick reference           (~X tokens)
  ─────────────────────────────────────────────────────
  Total skill size: ~X tokens (loaded on-demand, not all at once)

💡 Tip: check your agent's session cost/usage command to see actual token usage.

Usage:
  Ask for <skill_name>                  → load core frameworks
  Ask <skill_name> about <topic>        → find and explain a topic
  Ask <skill_name> for ch<N>            → dive into a specific chapter

Discoverable by: <only what is true for the chosen destination — see below>

Somewhere else?  mv ~/.agents/skills/<skill_name> <dest_root>/<skill_name> \
                   && ln -sfn <dest_root>/<skill_name> ~/.claude/skills/<skill_name>

Prompted for permission on every file? That is your host gating writes outside the
working directory. Say "save it in this project" and re-run to write inside it.

Reload (if your agent doesn't auto-detect new skills):
  GitHub Copilot CLI:  /skills reload
  Claude Code:         restart the session
  Amp:                 restart the session
  Hermes Agent:         start a new session
  OpenClaw:             openclaw skills list (new session if watcher disabled)
  OpenCode:             start a new session

Share this skill (optional):
  GitHub repo, installable on any host (Step 11):  say "publish"
  Copilot ecosystem:  gh skill publish $SKILLS_HOME/<skill_name>
```

「Discoverable by」那一行要根據 `CLAUDE_STATUS`（讀回來的結果）填寫，絕對不要根據 `ln` 有執行過這個事實，以 `~/.agents/skills` 安裝為例：
- `linked` → "Copilot CLI, Amp, Codex (natively); Claude Code via symlink ~/.claude/skills/<skill_name>"
- `skipped-realdir` → "Copilot CLI, Amp, Codex (natively); **NOT** Claude Code — migrate the real directory at ~/.claude/skills/<skill_name> first"
- `copy` 或 `absent` → "Copilot CLI, Amp, Codex (natively); **NOT** Claude Code — the host could not create the symlink (a plain copy drifts on the next Update/Fold-in). Enable Developer Mode / create the link manually, or run the skill from ~/.agents/skills"
- Hermes Agent 個人根目錄 → "Hermes Agent (from `$HERMES_HOME/skills/<category>`)"；不宣稱有 symlink，也不宣稱跨 agent，因為其他 host 不會掃描 Hermes 根目錄
- 其他 host 私有或專案本地的根目錄 → 只列出會掃描那個根目錄的 host；不宣稱有 symlink

「Somewhere else?」這個搬移行，必須對實際走過的路徑是正確的，這樣才不會弄壞這次執行剛建好的 symlink。**`mv` 的目標永遠是最終的 skill 目錄 `<dest_root>/<skill_name>`，絕對不是 `<dest_root>` 本身。** `mv ~/.agents/skills/mybook ~/.copilot/skills && ln -sfn ~/.copilot/skills ~/.claude/skills/mybook` 看起來合理，其實是錯的：skill 會落在 `~/.copilot/skills/mybook`，但連結指向的是上一層的根目錄，於是 Claude Code 解析到一個沒有 `SKILL.md` 的目錄，這正是這一行要避免的壞掉狀況。要代入使用者實際指定的目的地，讓印出來的指令帶著真實的路徑，不需要再解讀任何東西：
- `~/.agents/skills` + symlink → `mv ~/.agents/skills/<skill_name> <dest_root>/<skill_name> && ln -sfn <dest_root>/<skill_name> ~/.claude/skills/<skill_name>`
- host 私有的根目錄（包含 Hermes Agent） → `mv <src_root>/<skill_name> <dest_root>/<skill_name>`
- 專案本地的根目錄 → `mv <project_root>/<skill_name> <dest_root>/<skill_name>`

「Prompted for permission on every file?」這一行，是回答那些會管制工作目錄以外寫入的 host（任何個人範圍的根目錄都在 cwd 之外）：目的地上面已經宣告過了，一行解法（重新執行並要求專案本地的根目錄）就放在旁邊。只在個人範圍的安裝保留它；使用者已經選了專案本地就拿掉。

---

## Step 11：把產生的 skill 發布到 GitHub（選用）

Step 10 的報告之後，只提議一次，而且只有在 Step 9.5 的掃描通過時才提議：

> "Want me to publish this skill to GitHub so any Agent Skills host can install it with `npx skills add`? (yes / skip)"

如果使用者拒絕，就在這裡停下。需求：`gh` CLI，而且已驗證（檢查 `gh auth status`）。如果 `gh` 不存在或沒驗證，提議幫忙設定（`brew install gh` 或 https://cli.github.com，然後 `gh auth login`），或走沒有 `gh` 的路徑：使用者在 GitHub 網頁介面建一個選好可見度的空 repo，然後你執行下面的 `git init`/`add`/`commit` 指令，接著 `git remote add origin <repo-url> && git push -u origin main`。下面的可見度規則，對網頁建的 repo 完全一樣適用。

**可見度是獨立的封閉式問題：絕對不推測，絕對不從前面的答案裡讀出來。** 使用者一接受，就單獨問它，並要求一個字的回覆：

> "Private or public repository? Reply with one word: `private` or `public`."

**回覆必須*就是* `public`，不是只是包含它：這是硬性規則，不是建議。** 除了一種情況，每次執行 `gh repo create` 都要帶 `--private`：可見度問題的答案就是單純的 `public` 這個字。禁止子字串比對，因為**關於來源授權的句子不是可見度的答案**：「it's public domain」、「the book is public domain」、「it's publicly available」都是在描述素材，不是 repo，全部都要解析成 `--private`。換句話說、一個句子、含糊的答案、沉默，或是你自己的推測，都不算同意：重問一次，如果回覆還是不是單純的那個字，就用 `--private` 並在報告裡說明。private repo 之後可以改成 public；但是把從書籍衍生的內容公開推上去，是無法撤回的。

**著作權關卡：建立 repo 之前一律要套用：** chapter 檔案是合成的摘要，不是原始文字，但仍然衍生自來源素材。依據 README 的 Copyright & fair use 政策，從**第三方有著作權的書**產生的 skill 必須保持 private；只有當來源是使用者自己的文章、開放授權的內容，或使用者明確確認他有權公開再散布的素材，才提議 public，並說明適用的是哪一種情況。能接觸到公司內部素材，不等於有權公開它：從內部文件產生的 skill 要保持 **private**，除非使用者說明他持有發布權。

如果接受：

1. 在 `$SKILLS_HOME/<skill_name>/` 裡加一個 repo 的 `README.md`（絕對不要覆蓋既有檔案）：包含 skill 標題、一段描述（「Agent skill generated from *<Title>* by <Author> with [book-to-skill](https://github.com/virgiliojr94/book-to-skill)」）、下面第 3 步的安裝指令、檔案清單，以及一則說明內容是合成的摘要、不是書的原文。
2. 把 skill 資料夾初始化成 git repository，並建立 remote（預設 repo 名稱是 `<skill_name>`；讓使用者可以覆寫，有些人偏好加上 `<skill_name>-skill` 後綴）。**巢狀 repo 防護：** 先檢查 skill 資料夾是否已經在某個 git repository 裡面（`git -C "$SKILLS_HOME/<skill_name>" rev-parse --show-toplevel`，像 `.claude/skills/` 這種專案本地根目錄一定是這樣）。如果是，就不要在原地 `git init`：外層 repository 會把這個資料夾記錄成嵌入式 repo（gitlink，mode 160000），卻沒有 `.gitmodules`，外層專案的全新 clone 會默默漏掉這個 skill。改成把 skill 資料夾複製到暫存目錄，在副本裡執行下面的指令，並告訴使用者：發布出去的 repo（不是專案本地的資料夾）才是 remote 的工作副本。

```bash
cd "$SKILLS_HOME/<skill_name>"
git init -b main
git add -A
git commit -m "Add <skill_name> skill"
gh repo create <repo_name> --private --source . --push
# --private is the default; substitute --public ONLY under the visibility rule above
# (the visibility answer WAS the bare word "public" AND the copyright gate allows it)
```

3. 回報 repo URL 和跨 host 的安裝指令：

```
✅ Published: https://github.com/<owner>/<repo_name> (<private|public>)

Install on any Agent Skills host:
  npx skills add https://github.com/<owner>/<repo_name> --skill <skill_name>
```

   如果巢狀 repo 防護被觸發，而且 repo 是從暫存副本發布的，要多加一行：那個本地資料夾永遠不會有 remote，所以 Update/Fold-in 推送的提議永遠不會出現在它上面：

```
⚠️  Published from a copy: <skill folder> sits inside another git repository, so it has
    no remote of its own. To publish a later update, re-run Step 11, or clone
    https://github.com/<owner>/<repo_name> and fold new material into the clone.
```

根層的 `SKILL.md` 版面，正是 `skills` CLI 會偵測的格式，所以這個 repo 原樣就能安裝，不需要重新調整結構。除了巢狀 repo 的情況，本地資料夾仍是這台機器上的實際安裝，也是 remote 的工作副本，所以之後的 Update/Fold-in 執行可以把改動 commit 並 push 到同一個 remote。

---

## Update / Fold-in Workflow

對 `$SKILLS_HOME/<skill_name>/` 的既有 skill 執行 Update/Fold-in 操作時：

### 1. 讀取既有 Skill 的結構
讀取並解析既有 skill 的檔案：
- 讀 `$SKILLS_HOME/<skill_name>/SKILL.md`，解析既有的 **Chapter Index**、**Topic Index**、metadata（作者、總章節數）和 **Core Frameworks**。
- 列出 `$SKILLS_HOME/<skill_name>/chapters/` 裡所有檔案，找出最大的章節編號（例如 `ch12`）。
- 讀 `$SKILLS_HOME/<skill_name>/glossary.md`、`$SKILLS_HOME/<skill_name>/patterns.md` 和 `$SKILLS_HOME/<skill_name>/cheatsheet.md`，看已經索引了哪些名詞和框架。

### 2. 比對內容，辨識修訂與新增
分析這次執行的 `full_text.txt`（萃取輸出裡的 `Text ->` 路徑）裡新萃取出來的文字，辨識新內容屬於：
- **對既有章節的更新/修訂**：如果新內容的某一段直接更新或擴充了既有章節的主題，就讀既有的章節檔，把新的細節合併進去，並重寫該檔案。
- **新增**：如果內容引入了新的章節、論文或獨立的區段，就在 `chapters/` 底下建立**新的章節摘要檔**。這些檔案的編號從既有最大章節編號之後開始（例如既有章節到 `ch12` 為止，就建立 `ch13-*.md`、`ch14-*.md` 等等）。

### 3. 產生或更新章節摘要檔
對每個新增或修訂的章節：
- 讀萃取出來的新文字中對應的區段。
- 依照 **Step 7** 的格式準則來建立摘要。
- 寫入/更新 `$SKILLS_HOME/<skill_name>/chapters/` 裡的檔案。

### 4. 合併輔助檔案
- **合併 glossary.md**：
  - 讀既有的 `$SKILLS_HOME/<skill_name>/glossary.md`。
  - 從新內容萃取所有新的名詞和定義（Step 8 的 glossary 準則）。
  - 把既有和新的名詞合併，並依字母排序。
  - 如果名詞已經存在，就把新的章節/來源參照附加上去（例如 `**Term** — definition (Ch 4, Ch 13)`）。
  - 用完整合併、排序過的清單重寫 `$SKILLS_HOME/<skill_name>/glossary.md`。
- **合併 patterns.md**：
  - 讀既有的 `$SKILLS_HOME/<skill_name>/patterns.md`。
  - 從新內容萃取任何新的技巧、演算法或模式。
  - 附加新的 pattern，確保格式一致，並讓總長度保持精簡（2,500 token 以下）。
- **合併 cheatsheet.md**：
  - 讀既有的 `$SKILLS_HOME/<skill_name>/cheatsheet.md`。
  - 萃取新的比較規則、決策表或參數指南。
  - 乾淨地整合進 cheatsheet 的結構。

### 5. 重新產生主要的 SKILL.md
更新主要的 skill 檔案 `$SKILLS_HOME/<skill_name>/SKILL.md`：
- **Metadata**：把章節數加一、更新預估頁數，適當的話加入新的來源名稱。把 `Generated` 日期更新成今天。
- **Core Frameworks**：把新內容中影響最大的心智模型或原則併進去（確保整個檔案仍在 4,000 token 以下）。
- **Chapter Index**：把新章節附加到索引表，連結到新建立的檔案。
- **Topic Index**：依字母順序合併新主題。如果既有的主題也被新章節涵蓋，就把新章節的連結附加到它那一行（例如 `- **Topic** → ch05, ch13`）。

### 6. 掃描、清理與回報
檔案成功寫入並合併之後，先執行 **Step 9.5**，再進入 **Step 10** 做清理，並印出客製化的更新報告，總結新增的章節、合併的 glossary 名詞，以及更新過的索引。如果 skill 資料夾是帶有 remote 的 git repository（透過 **Step 11** 發布的），就提議 commit 這次更新並 push。

---

## 品質規則

1. **萃取結構，不要做摘要**：抓有名字的框架、確切的表述、反模式；不要做章節回顧
2. **保留作者的精確用詞**：「The 5 Whys」≠「多問幾次為什麼」；保留確切的命名
3. **密度勝過完整**：1,000 token 的摘要，勝過 10,000 token 的節錄
4. **實踐者的口吻**：寫「Use X when Y」，不要寫「The book explains X」
5. **SKILL.md 要把重點放前面**：壓縮會保留前 5,000 個 token；最重要的內容要排最前面
6. **章節檔是隨選載入的**：載入之前不會算進 skill 的預算
7. **絕對不要複製書的原文**：永遠要合成、摘要、萃取訊號
8. **Topic index 很關鍵**：agent 就是靠它導航到正確的章節檔
