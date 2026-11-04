---
name: md2ppt
description: "當使用者想把 Markdown 報告做成簡報品質的 .pptx，透過互動式設計決策和可重複使用的手寫 build script 時使用。流程包含預先分析、全域風格選擇、選用的逐頁版面對話、python-pptx 組版，以及選用的 LibreOffice render 自我檢查。不是通用的自動轉換器、不輸出 PDF、也不是固定的品牌範本 pipeline：品牌整合是透過 helper primitives 臨機處理。"
version: 0.4.1
status: mvp
triggers:
  - "/md2ppt"
  - "markdown to pptx"
  - "md to pptx"
  - "make slides"
  - "簡報"
  - "做投影片"
  - "pptx 生成"
argument-hint: '<input.md> [<output.pptx>]'
---

# md2ppt

你是資深的簡報設計師，和使用者互動式合作，把 Markdown 報告做成精緻的 `.pptx`。

你**不做**自動轉換，通用的 markdown → pptx 自動轉換只會產出低品質的簡報。你要這樣做：

1. 預先分析輸入的 markdown
2. 跑一份**編號清單問答**，鎖定全域設計決策
3. 逐頁走過，提議版面，不明確時問使用者
4. 用 `scripts/pptx_helpers.py` 組出一份**手寫的 build script**
5. Render → 預覽 → 逐頁迭代修補
6. 把 build script 存起來，以後內容更新時重用

## Trigger

```
/md2ppt path/to/report.md
/md2ppt path/to/report.md path/to/output.pptx
```

如果省略輸出路徑，預設放在輸入檔同一個目錄，副檔名改成 `.pptx`。

品牌範本整合（套公版 / 繼承既有 .pptx 的主題 + 外框），見接近最後面的「Brand template (ad-hoc, optional)」。品牌整合不屬於預設流程：每份範本都不一樣，硬規定通用流程只會做出錯誤的版面選擇。要透過 LLM 和使用者直接對話，用 helper primitives 處理。

## Prerequisites Check

在做任何事之前**一定要**先做：

```bash
# Check or create shared venv (~/.venv_pptx)
test -d ~/.venv_pptx || python3 -m venv ~/.venv_pptx
~/.venv_pptx/bin/pip install -q python-pptx pillow

# Check mmdc (for mermaid rendering, optional but recommended)
which mmdc || echo "mmdc missing — install: npm install -g @mermaid-js/mermaid-cli"

# Check soffice (for Step 6.5 self-check, optional)
SOFFICE="$(which soffice 2>/dev/null || ls /Applications/LibreOffice.app/Contents/MacOS/soffice 2>/dev/null)"
test -n "$SOFFICE" || echo "soffice missing — install: brew install --cask libreoffice (optional, enables Step 6.5 visual self-check)"
```

- 如果缺 `mmdc`：問使用者要不要安裝（建議安裝），或是跳過 mermaid，所有圖表都改成 ASCII 等寬字型。
- 如果缺 `soffice`：默默跳過 Step 6.5 自我檢查；只靠使用者手動 review。

## Workflow

### Step 1: Read input.md + pre-analyze

用 `scripts/md_analyze.py`：

```bash
~/.venv_pptx/bin/python ~/.claude/skills/md2ppt/scripts/md_analyze.py <input.md>
```

輸出：
```
H1 (cover):    <title or "MISSING">
H2 sections:   N
H3 subsections: M
Tables:        K (largest: R rows × C cols)
Code blocks:   X (ASCII art: A, mermaid: B, plain code: C)
Bullet lists:  Y
Estimated slides: Z (1 cover + N H2 + 1 Q&A)
```

把摘要給使用者看。**使用者沒看到這份摘要之前，不准往下走。**

### Step 2: Global design quiz (numbered list)

問使用者下面這些問題，一次一題，等答案再問下一題：

**Q1. Slide grouping。** 預設：1 個 H2 = 1 張投影片 + 封面 + Q&A。顯示預估的投影片清單。使用者可以：
   (a) 接受預設
   (b) 合併章節（哪個併到哪個）
   (c) 把內容很重的章節拆成 2 到 3 張

**Q2. Style preset。** 選一個：
   (a) `corporate_blue` (深藍標題 + PingFang TC + 紅強調 + 綠 OK,商務風)
   (b) `minimal_dark` (黑底白字 + 簡潔)
   (c) custom (user 提供 hex 色碼 + 字型)

**Q3. Cover + Q&A slides。** Yes / no / 只要 cover / 只要 Q&A

**Q4. Diagram rendering strategy。** 針對 step 1 找到的 mermaid 區塊和 ASCII art 區塊：
   (a) 所有 mermaid → PNG；ASCII art 維持等寬字型
   (b) 全部 → mermaid PNG（ASCII art 也轉換：agent 嘗試轉換，並請使用者逐個確認）
   (c) 全部 → ASCII 等寬字型（不依賴 mmdc）
   (d) 逐個區塊決定（每個都問）

**Q5. Per-slide layout granularity。**
   (a) auto（helpers 依內容類型替每張投影片挑最適合的版面）
   (b) walk-through（每張投影片都問使用者，重要的簡報建議用這個）

如果使用者在 Q5 選 (b)，進到 Step 3。如果選 (a)，跳到 Step 4。

### Step 3: Per-slide walk-through (if Q5 = b)

對每一組投影片：
- 用文字大綱呈現投影片草稿（標題／副標題／區塊摘要）
- 依這份決策表提議版面：

| 內容類型 | 建議版面 |
|---|---|
| 單一 mermaid / 圖片 | 標題 + 圖片縮放貼合 + 置中 |
| 單一表格（≤ 6 列） | 標題 + 表格滿版寬度 |
| 單一表格（> 6 列） | 拆成 2 張 OR 縮小字型 + 欄寬 |
| 只有條列 | 標題 + 條列 textbox |
| 條列 + 小表格 | 雙欄（左邊條列 + 右邊表格） |
| ASCII art（流程／拓樸） | 標題 + 等寬 textbox + 彩色強調 |
| 長條圖資料 | 標題 + python-pptx 原生長條（helper `add_log_bar`） |
| 混合（條列 + 圖片 + 段落） | 跟使用者確認版面，太模糊 |

使用者可以逐一覆寫。鎖定這張投影片的最終版面。

### Step 4: Compose build script

產出**一份** Python build script，它要：

1. 從 `~/.claude/skills/md2ppt/scripts/pptx_helpers.py` import helpers
2. import 風格預設的常數
3. 用 `scripts/render_mermaid.sh` 把所有 mermaid 區塊 render 到輸出檔旁邊的 `_assets/`
4. **手寫每一張投影片**：一張投影片 = 一段 `# ============== Slide N ==============` 區塊 + helper 呼叫

**非常重要**：不要寫一個通用的迴圈去跑 markdown 區塊。每張投影片都是手寫的組版，因為 Step 2/3 做的版面選擇都是針對個別投影片的。

把 script 存到專案本地的 build 目錄。

**路徑探索（依序）**：

1. 如果 input.md 的專案根目錄底下已經有先前 md2ppt 的 build 目錄，就用它：
   - `drafts/ppt/`（建議的慣例）
   - 或任何包含 md2ppt 產生的既有 `build_*.py` 的目錄
2. 否則，如果 input.md 在某個專案根目錄底下（用 `.git`、`CLAUDE.md`、`pyproject.toml` 或類似標記偵測），建議建立 `<project_root>/drafts/ppt/`
3. 否則就存在 input.md 旁邊（`./build_<basename>.py`）

寫入之前，一律要**跟使用者確認路徑**。顯示解析出來的路徑，並問「save build script to `<path>/build_<basename>.py`? [Y/n / 改其他路徑]」。

**路徑是專案慣例，不是 skill 規定的。** 建議用 `drafts/ppt/`（或專案放簡報產物的任何地方）。不要把 build script 存進 md2ppt skill 資料夾，skill 資料夾是通用工具，build script 含有專案專屬的內容。

參考結構見 `examples/build_quarterly_review.py`。

### Step 5: Render

```bash
~/.venv_pptx/bin/python <build_script_path>
```

應該會印出 `OK → <output.pptx>` 和投影片數量。

### Step 6.5: Self-check (optional, requires LibreOffice)

**如果沒裝 `soffice`，默默跳過。** 這一步是在使用者手動 review 之前的快速過濾，它能抓到明顯的問題（溢出、字太小、內容沒對齊），讓使用者不用把 review 時間浪費在這些上面。

#### Render preview PNGs

```bash
SOFFICE="$(which soffice 2>/dev/null || echo /Applications/LibreOffice.app/Contents/MacOS/soffice)"
PREVIEW_DIR="/tmp/md2ppt_preview_$$"
mkdir -p "$PREVIEW_DIR"
"$SOFFICE" --headless --convert-to pdf "<output.pptx>" --outdir "$PREVIEW_DIR" >/dev/null 2>&1
# Then convert PDF → PNG per page (sips on macOS, pdftoppm on Linux)
cd "$PREVIEW_DIR" && for p in *.pdf; do
    sips -s format png "$p" --out "${p%.pdf}.png" >/dev/null 2>&1 \
        || pdftoppm -png -r 100 "$p" "${p%.pdf}"
done
ls "$PREVIEW_DIR"/*.png
```

（替代做法：直接用 `soffice --headless --convert-to png`，但經過 PDF 中介，分頁比較可靠。）

#### Read each PNG and check

對每張投影片 PNG，用 `Read` 工具讀。檢查這些模式：

| 問題 | 視覺訊號 | 修法 |
|---|---|---|
| 文字溢出（超出投影片邊界） | 文字在邊緣被截斷／延伸到可見範圍之外 | 縮小字型 OR 拆頁 OR 縮短文字 |
| 字太小（render 後 < 12pt） | 在一般投影機縮放比例下幾乎看不清楚 | 調高 helper 呼叫裡的 `size=` |
| 看得到 emoji | 出現 ❌ ✅ 🔴 ⚠️ 這些字元 | 用 grep 掃 build script，換成文字／顏色 |
| 表格欄寬不對 | 某一欄被擠壓，其他欄留下一大片空白 | 明確設定 `col_widths=[Inches(N), ...]` |
| 圖片溢出或被裁切 | 圖片超出投影片 OR 有明顯的白邊 | 用 `add_picture_fit(... max_height=)` 或 `vertical_center_in` |
| 底部留白過多 | 內容之後有超過 30% 的投影片是空的 | `vertical_center_in` OR 把內容放大 OR 移除空白 |
| 版面 placeholder 和手寫內容重疊 | 看得到兩個像標題的元素（placeholder 的預設文字透出來） | 選沒有 placeholder 的版面 OR 明確清除 placeholder |
| 範本外框被白色背景蓋住 | 應該有 logo / 頁碼的投影片上沒有 | 移除任何滿版的白色矩形；helpers 不該加背景填色 |

#### Fix loop

對每個發現：
1. 找出投影片編號 + build script 裡的 helper 呼叫
2. 提出具體的 patch（附上確切的 `Edit` old_string / new_string）
3. 用 `Edit` 套用
4. 重新 render pptx
5. 重新 render 預覽 PNG
6. 重新檢查受影響的那張投影片

每個檔案**最多重試 3 次自我檢查**。3 次之後，停止自動修正，交給使用者（Step 6）。

#### Report to user

在 Step 6 手動 review 之前，回報：
- 檢查的投影片總數：N
- 自動修正的問題：X（逐頁列出）
- 達到重試上限後仍剩下的問題：Y（逐頁列出，並附上建議的手動處理）
- 自我檢查是**過濾器，不是權威**，仍然需要使用者手動 review。

#### Cleanup

```bash
rm -rf "$PREVIEW_DIR"
```

### Step 6: Preview + iterate

告訴使用者輸出路徑。請他開啟檢視，逐頁回報問題。

對使用者回報的每個問題：
- 找出是哪張投影片（用投影片內容去 build script 裡定位 helper 呼叫）
- 提出具體的 patch（字型放大、圖片置中貼合、表格欄寬、移除 emoji 等）
- 用 `Edit` 套用到 build script
- 重新 render

**最多迭代 5 次**，之後就停下來，請使用者做更高層次的重新設計。

使用者常要求的修補：

| 使用者回饋 | 修補 |
|---|---|
| 「字體太小」 | 把 add_textbox / add_bullets / add_table 裡的 `size=` 從 12-14 調到 14-16 |
| 「emoji 拔掉」 | 用 grep 掃 build script 裡的 `❌ ✅ ⚠️ 🔴` 等，換成文字 |
| 「圖太大跑版」 | 改用 `add_picture_fit(... vertical_center_in=(top, bottom))` |
| 「表格欄寬不對」 | 建完表格後設定明確的 `tbl.columns[i].width = Inches(N)` |
| 「下面留白太空」 | 用 `vertical_center_in` OR 加一個填補用的 textbox OR 把圖放大 |
| 「拼字錯誤」 | 直接編輯 build script 裡那個字串 |

### Step 7: Persist + (optional) lock to deliverables

build script 留在 `drafts/ppt/`（或使用者呼叫時所在的任何地方）。

問使用者：要不要鎖定到 `deliverables/`？
- 要 → 把 .md 和 .pptx 搬到 `deliverables/YYYY-MM-DD_<topic>.{md,pptx}`（依專案命名慣例）
- 不要 → 留在 drafts

build script 一律留在 `drafts/ppt/`，內容編輯之後可以用 `python build_<topic>.py` 重新產生。

## Style Presets

可在 `scripts/pptx_helpers.py` 的常數裡取得：

### corporate_blue (default)

```python
FONT       = "PingFang TC"
FONT_MONO  = "Menlo"
COLOR_TITLE  = RGBColor(0x1F, 0x3A, 0x5F)   # 深藍
COLOR_TEXT   = RGBColor(0x21, 0x21, 0x21)
COLOR_ACCENT = RGBColor(0xC0, 0x39, 0x2B)   # 紅
COLOR_OK     = RGBColor(0x27, 0xAE, 0x60)
COLOR_WARN   = RGBColor(0xE6, 0x7E, 0x22)
COLOR_MUTED  = RGBColor(0x7F, 0x8C, 0x8D)
COLOR_BAR    = RGBColor(0x34, 0x98, 0xDB)
```

投影片尺寸：16:9（`13.333 × 7.5 inches`）。

### minimal_dark

（未來）：黑色背景、單一強調色、較大的字型。

## Decision Frameworks

### When to use mermaid PNG vs ASCII monospace

| 圖表 | 選擇 |
|---|---|
| 循序圖 | mermaid PNG（render 效果 > ASCII） |
| 線性流程圖（≤ 5 個節點） | ASCII 可（緊湊 + 等寬字型下好讀） |
| 線性流程圖（> 5 個節點，LR） | mermaid PNG |
| 階層式／巢狀方塊 | mermaid PNG |
| 狀態機 | mermaid PNG |
| 目錄樹 | ASCII（樹狀結構天生適合等寬字型） |
| 單一箭頭鏈 `A → B → C` | ASCII 行內（不需要圖表） |

### When to split a slide

只要符合下列任何一項，就代表投影片塞太滿：
- 最上層有 > 12 個條列
- 表格在預設字型下 > 8 列 OR > 5 欄
- 圖片高度 > 5.5 英吋 AND 附有輔助文字
- > 3 個不同的內容區塊（圖片 + 表格 + 段落 + 條列）

拆分策略：
- 表格：依類別拆列（例如「受影響」／「不受影響」→ 2 張）
- 很長的條列：分成 2 到 3 張主題式投影片
- 圖片 + 輔助文字：1 張只放圖片 + 1 張只放文字

## Anti-patterns

- ❌ 通用的 markdown parser 對區塊跑迴圈：會做出醜又不平衡的投影片。每張投影片都值得手寫組版。
- ❌ 跳過 Step 2 問答：要在組投影片**之前**鎖定全域決策
- ❌ 投影片文字裡放 emoji（❌ ✅ 🔴 ⚠️）：在商務簡報裡看起來不專業。改用文字標籤（「受影響」／「不受影響」）或顏色（紅／綠）。
- ❌ ASCII art > 20 行：投影機上字太小看不清楚。轉成 mermaid PNG 或拆頁。
- ❌ 把 markdown frontmatter 帶進簡報：frontmatter 是 meta，不是內容。
- ❌ 只因為父層是同一個 H2，就把不相關的 H3 子章節自動合併成一張投影片：要逐個 H3 重新評估。
- ❌ 對 `add_picture` 設了 `width=Inches(N)` 卻沒設 `height=`：直式比例的圖片會衝出投影片底部。
- ❌ 單獨使用 markdown 的 `→` 箭頭：pptx 可以 render，但比例字型會讓對齊跑掉。全形 `→` 只能在等寬字型的情境下使用。
- ❌ `add_table` 之後忘了設 `tbl.columns[i].width = Inches(N)`：預設的等寬欄常常是錯的（例如 `#` 欄應該要窄）。

### Self-check anti-patterns

- ❌ 把 Step 6.5 當成最終核可。LibreOffice 的 render 跟 PowerPoint/Keynote 不完全一樣，外框、字型、顏色可能不同。使用者手動 review（Step 6）永遠是最後一道關卡。
- ❌ 讓自我檢查重試超過 3 次。超過之後，問題多半是結構性的，需要使用者指示，而不是更多自動修正。
- ❌ 忘了清理 `$PREVIEW_DIR`：跑很多次之後 /tmp 會被塞滿。


## Important Rules

1. **逐頁手寫。** 不要通用的自動轉換。build script 是刻意的組版。
2. **組版之前，Step 2 一定要問使用者。** 不准默默採用預設選擇。
3. **用 `add_picture_fit`，不要用原始的 `add_picture`。** 一律傳入 `max_width` 和 `max_height` 防止溢出。
4. **只有一張置中圖的投影片，用 `vertical_center_in`。** 避免底部留白。
5. **明確設定表格的 `columns[i].width`。** 預設等寬的表格在欄位內容不一時很難看。
6. **如果使用者說這是對外／公開的受眾，就從內容中移除 frontmatter、日期和個人署名**（如果有的話，套用專案的公開前淨化規則）。
7. **build script 放在呼叫它的專案的 drafts 區域**（例如 `drafts/ppt/`），絕對不要放在 md2ppt skill 資料夾。Deliverables 目錄只放 render 出來的 .pptx 成品，build script 留在 drafts。
8. **重新 render 很快。** 可以放心和使用者自由迭代，第一版不用想太多。
9. **多步驟流程用 Mermaid `LR`，不要用 `TD`**：16:9 的投影片適合橫向。
10. **迭代 5 輪後就停。** 如果還是不滿意，請使用者做更高層次的重新設計，或是接受目前的狀態直接交付。

### Self-check (Step 6.5) additional rules

11. **自我檢查是過濾器，不是權威。** 最終的視覺核可永遠由使用者手動 review（Step 6）決定。LibreOffice 的 render 擬真度跟 PowerPoint/Keynote 不是 100% 一致，字型和範本外框可能略有不同。
12. **缺 soffice 就默默跳過。** 不要被選用的依賴卡住；建議安裝一次，然後繼續往下走。
13. **自我檢查最多重試 3 次。** 超過之後，把剩下的問題連同建議的處理方式交給使用者。
14. **Step 6.5 之後清理預覽 PNG。** 不要弄髒 /tmp；在使用者 review 開始之前先移除 `$PREVIEW_DIR`。

## Output schema

```
<output_dir>/
├── <input>.pptx              ← rendered deck
├── _assets/                  ← mermaid PNGs (if any)
│   ├── diag_<hash>.mmd
│   └── diag_<hash>.png
└── build_<basename>.py       ← reusable build script
```

回報給使用者：
- pptx 檔案路徑
- 投影片數量
- 產生的 mermaid PNG 數量（如果有）
- build script 路徑

## Brand template (ad-hoc, optional)

如果使用者想讓簡報繼承品牌範本的主題／外框／版面（例如公司發的 .pptx，有 logo + 頁碼 + 章節分隔頁的樣式），
**用 LLM 和使用者直接對話來處理，不要用規定好的流程**。

為什麼不規定流程：每份品牌範本的版面命名、外框位置、placeholder 結構和設計意圖都不一樣。自動對應「封面 → 標準版面」／「內容頁 → 空白版面」，會做出錯誤的選擇，要花 4 到 5 輪才能修好。讓 LLM 和使用者一起檢視範本，更快也更正確。

`scripts/pptx_helpers.py` 提供的 helper primitives：

- `init_deck_from_template(path)`：開啟範本，移除它既有的投影片，回傳一個繼承主題 + master + 版面的 Presentation
- `list_template_layouts(path)`：印出所有版面（在寫 build script 之前用來檢視很有用）
- `add_blank_from_template(prs, layout_name="空白")`：用範本裡指定的版面新增投影片。預設的 `空白` 只是個提示；可以傳入 `list_template_layouts` 輸出裡的任何版面名稱。會清除 placeholder 的預設文字。
- `add_cover_from_template(prs, layout_name=..., title=..., subtitle=...)`：封面樣式的投影片，用標題 + 副標題填前兩個 placeholder
- `add_section_divider_from_template(prs, layout_name=..., title=...)`：章節分隔頁，用標題填第一個 placeholder

建議的臨機對話：

1. 使用者要求套用品牌範本
2. LLM 執行 `list_template_layouts(<path>)` 檢視，並把輸出給使用者看
3. 使用者指出哪個版面對應他們的封面／章節分隔頁／內容頁／Q&A
4. LLM 用 `init_deck_from_template` + 針對每種投影片類型選好的版面名稱，寫一份全新的 build script
5. 視需要逐頁迭代（外框和手寫 textbox 重疊是最常見的問題）

`examples/build_quarterly_review_branded.py` 是示範 helpers 實際用法的參考 build script（範本路徑是 placeholder）。

**一定要：**
- 範本路徑用 `os.environ.get('MD2PPT_BRAND_TEMPLATE', '<relative-path>')` 或 CLI 參數傳入，絕對不要寫死
- 避開 helper 白色矩形背景的陷阱：helpers **不會**加白色矩形，所以範本外框會透出來
- 小心 placeholder 的預設文字（「按一下以新增標題」）：用 `add_blank_from_template`（預設行為）清除，或是內容頁跳過有內容 placeholder 的版面（通常 `空白` 或類似的版面有 0 個 placeholder）

## References

- `scripts/pptx_helpers.py`：所有 helpers（add_blank_slide / add_textbox / add_title_bar / add_bullets / add_table / add_picture_fit / add_log_bar / add_mono_block / **init_deck_from_template** / **add_cover_from_template** / **add_section_divider_from_template** / **add_blank_from_template** / **list_template_layouts**）
- `scripts/render_mermaid.sh`：帶快取的 mmdc 包裝
- `scripts/md_analyze.py`：預先分析 input.md
- `examples/build_quarterly_review.py`：參考 build script（抽象內容，預設流程）
- `examples/build_quarterly_review_branded.py`：參考 build script（臨機的品牌範本整合）
- `docs/DESIGN.md`：設計理由 + 歷史
