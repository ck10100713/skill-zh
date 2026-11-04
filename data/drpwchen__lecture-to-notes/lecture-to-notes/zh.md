---
name: lecture-to-notes
description: "把演講/研討會錄影（影片或音檔：MOV/MP4/M4A/MP3/WAV）轉成結構化的 vault 筆記，流程是本機 GPU 轉錄加上投影片擷取。觸發詞：演講影片, 演講音檔, 上課錄影, '整理演講', '影片轉筆記', '音檔轉筆記'，或使用者直接丟進來的媒體檔。支援批次處理。"
allowed-tools: Read Write Edit Bash Glob Grep Agent
---

# Lecture-to-Notes

把演講錄影（影片或純音檔）轉成結構化筆記。每個吃重的階段都在本機跑，花 0 個 Claude token，Claude 只負責最後的整合。這頁是地圖，細節放在 `reference/`，一個主題一個檔案。

| 檔案 | 裡面有什麼 |
|---|---|
| `reference/pipeline.md` | 各階段的參數、門檻、JSON schema、timeout、可觀測性 |
| `reference/note-spec.md` | 筆記品質規格、tier 評分、寬度表、整合 prompt 的要求 |
| `reference/segmented-mode.md` | 多場演講的工作坊資料夾 → 每段 L2/L3 + Hub + 網頁檢視器 |
| `reference/multi-camera.md` | 一支長錄影加上多支手機影片/照片 → 合成一條時間軸 |
| `reference/decisions.md` | 事後檢討、benchmark、走錯的路、VRAM 實測數據 |

## HARD RULES

1. ==轉錄之前，一定要先問使用者講者用什麼語言==（英文 / 中文 / 中英夾雜）。沒有預設值，`transcribe_video.py` 沒帶 `--lang` 就會直接結束。猜錯的話，Whisper 會把帶口音的英文幻聽成中文，逐字稿就廢了。
2. ==為了速度或趕時間，絕對不准跳過 Stage D（VLM）或 Stage E（grounding）==。==使用者沒有設過 deadline，不要自己編一個。==如果某個階段真的太慢（預估超過 2 小時），回報預估時間然後問使用者。
3. ==絕對不准自動修正逐字稿。==只標記可疑的地方，讓整合階段去判斷。做過的兩種自動修正流程都實測過然後淘汰了，見 `reference/decisions.md#asr-auto-correction`。不要加自動套用的模式。
4. ==不准繞過 collapse 自動重試。==偵測到 token collapse 時，`transcribe_video.py` 會自動跑 `retranscribe_segment.py --auto`。如果重試後 collapse 還在，就往上升級（更寬的 beam + `--no-repeat-ngram-size` + 詞彙表），絕對不是跳過。
5. ==VLM 不做 OCR。==Stage D 只要語意訊號。文字來自 Stage B 的 `quick_text`、Stage B2 的 `clean_text` 或 `pdf_text.json`。`ocr.vlm_text` 是永遠為空的相容欄位。
6. ==所有 GPU 工作都要序列化。==8 GB 的顯卡上，Whisper 和 VLM 不能同時跑，擷取畫面也不能跟轉錄同時進行。
7. ==8 GB 顯卡上，`--beam-size 10` 搭配的 `--batch-size` 絕對不能超過 4==，而且絕對不要把 `--beam-size 15` 和 sequential 模式一起用，那樣會當掉（`0xC0000005`）。這些是 anti-collapse 重試的記憶體上限，==不是建議的第一輪設定==。第一輪就用最陽春的預設值（Step 4）。
8. ==Director 批次派工==：多場演講的批次，把 Steps 1–9 當成一個 subagent 派出去，Step 10 的整合另外派一個全新的 subagent，而且要等 `slides_grounded.json` 出現之後才派。單一 subagent 會在漫長的 GPU 等待中來回空轉，每場演講白白燒掉 30 分鐘以上的實際時間。
9. ==素材一律依「真實拍攝時間」排序，絕對不是依檔名，也不是依印出來的議程。==檔名只是標籤，不是時鐘：攝影機的計數器每天會重來（拍兩天就有兩個 `00000`），錄音筆的 `240526_1119.mp3` 會被排到影片檔中間，現場標的 `-1-`/`-2-` 也會貼到錯的檔案上。任何多來源的課程，在切段之前先跑 `scripts/batch/course_timeline.py`；`manifest.json` 的 clip 順序和 `L1_coarse.md` 的章節順序都必須從它的結果建出來。議程也不是時鐘：2024-05 的 Conference-Y 研討會，第一天提早約 25 分鐘開始，第二天延後約 35 分鐘，但中間休息的間隔卻準到分秒不差。
10. ==🚫 PHI 紅線==：如果錄影內容含有可識別病人的資訊（病例討論、查房、有名有姓的病人），只能在本機轉錄，不准用 `--engine groq`。不確定就問，預設走本機。設了 `LECTURE_LOCAL_ONLY=1`（或 config 的 `privacy.local_only: true`），Groq 和 Gemini 這兩條路徑會在上傳任何東西之前就以 exit 2 結束。

## 輸入類型與路由

==從這裡開始。`route_inputs.py` 是入口==，它會分類資料夾，並印出依序要跑的指令，以及需要人來回答的問題。它只做規劃：不會執行任何東西，也不會寫任何檔案。

```bash
python <skill-dir>/scripts/route_inputs.py <material_dir> [--recursive] [--out-dir DIR] [--json]
```

| 資料夾裡有什麼 | 投影片來源 | 路線 |
|---|---|---|
| 影片，沒有投影片檔 | 從影片擷取畫面 | Path A，Steps 5–7 |
| 音訊/影片 **+ PDF 簡報**（==首選==） | PDF 文字 + 頁面渲染圖 | Path B，`build_slides_from_pdf.py` |
| 音訊/影片 **+ 零散的投影片圖片**（≥3 張） | 圖片本身 | Path B-images，`build_slides_from_images.py` |
| 只有音訊，沒有簡報 | 無 | Path C，只用逐字稿的筆記 |
| N-up 講義 PDF | 裁切後的小圖 | Path B-multi，先跑 `crop_multiup_pdf.py` |
| **多場演講的工作坊資料夾** | 每段各自處理 | `reference/segmented-mode.md` |
| 一支長錄影 + 多支手機影片/照片 | 每個來源各自處理 | `reference/multi-camera.md` |
| `.pptx` / `.docx` / `.key` | — | 自己先轉成 PDF，這裡沒有轉換步驟 |

==多來源契約==：只要有兩個以上獨立的來源，一切動作之前先建立時間軸。有 manifest 的課程資料夾用 `course_timeline.py <course_dir>`（它會寫出 `_seg/real_timeline.json`、把照片對應到錄影上，加上 `--reorder-manifest` 還會在根目錄修正 clip 順序）；散落的素材資料夾則用 `media_capture_index.py --emit-alignment alignment.json`。
==拍攝時間戳只是假設，逐字稿交叉相關（`xcorr_media_offsets.py`）才是證據。==`reliable` 旗標是 false 的來源，起始時間來自 mtime 或根本沒有，不能拿來對齊。任何東西都不會自動修正：宣稱值和實測值差超過 5 秒，就標成 `"conflict": true`，交給人判斷。細節在 `reference/multi-camera.md`。

## Pipeline

每個步驟一個指令加上它的用途；參數、門檻和輸出都在 `reference/pipeline.md`。

### Step 1 — 問語言（必做，沒有指令）

英文 / 中文 / 中英夾雜？講者有口音嗎？句子中間會不會切換語言？使用者沒講的話就用 AskUserQuestion。見 HARD RULE 1。

### Step 2 — 建立演講資料夾

每場演講一個資料夾，放所有中間產物；命名成 `{date}_{speaker}_{topic}`，這是 `finalize_to_vault.py` 會解析的格式。

### Step 3 — GPU 事前檢查

```bash
python <skill-dir>/scripts/gpu_check.py --out-dir "$OUT_DIR" --min-free-mb 6000
```
轉錄之前要過這一關，Stage D 之前也要再過一次。Exit `0` 就繼續，`1` 是警告但繼續，`2` 是被擋住了，把狀況回報出來，==不要在迴圈裡一直重試==。*總* VRAM 低於門檻的顯卡（2–4 GB 的筆電）會回 `GPU_TOO_SMALL`，exit `0`：這不是資源被佔用，等也等不到空間，直接走 CPU 路線（`transcribe_video.py --device cpu --model small`，或 `--engine groq`）。
→ `reference/pipeline.md#gpu-check`

### Step 4 — 轉錄

```bash
python <skill-dir>/scripts/transcribe_video.py "<media>" \
    --output-dir "$OUT_DIR" --lang <zh|en|bilingual|auto>
```
==最陽春的預設值就是 production 設定==（asr-benchmark 2026-07-12 n=15，`breeze25 / novad_nocond`：breeze25、beam 5、關 VAD、關 conditioning），==英文也一樣==：breeze25 在英文音訊上跟 large-v3 打平，所以不要換模型。第一輪不要加 `--beam-size 10`（recall 會掉，而且慢 1.7 倍）、`--initial-prompt`（會編出差不多的詞）或 `--model large-v3`，也==不要從舊批次的執行腳本抄參數==；你這樣做的時候腳本會印出 WARNING。這些參數只屬於 anti-collapse 重試的配方。
預設用本機的 faster-whisper；`--engine groq` 是選配的外送方案（HARD RULE 9）。預設的模型別名是 `breeze25`（需要本機有模型資料夾）；機器上沒有的話，傳 `--model large-v3`，faster-whisper 會自己下載。
超過約 30 分鐘的錄音，改走分塊執行器。
→ `reference/pipeline.md#transcription`

**逐字稿已經在別處有了**（MLX Whisper、雲端 STT、字幕、人工逐字稿）：用匯入取代轉錄：
`python <skill-dir>/scripts/import_transcript.py <file.srt|.vtt|.json> --out-dir "$OUT_DIR"
[--engine NAME] [--model NAME]`。它會寫出同樣的 `transcript.json`/`.txt`，不會動到來源檔，沒加 `--force` 也不會覆寫；下一步是 Step 5。

**用 Gemini 當主要逐字稿**（2026-10-24 實測：3 類共 15 段課程影片，Gemini 97–100 %，本機最佳 64–85 %；遠場禮堂音訊 82 % 對 54–60 %）。只能用在錄影不含 PHI（HARD RULE 10）而且==使用者已經說可以外送==的情況。專案可以在自己的 AGENTS.md 裡記一筆長期同意；其他情況每支錄影都要問，沒拿到同意就跑上面的陽春預設。
```bash
python <skill-dir>/scripts/asr_gemini_primary.py "<media>" -o "$OUT_DIR" --lang <zh|en|bilingual> \
    [--start <ISO wall clock>] [--extra <args for the breeze25 fallback>]
```
1. `--model breeze25`（陽春預設，約 10 倍即時）→ `transcript_anchor.{txt,json}`，這是時鐘==也是交叉比對的依據==：Gemini 偶爾會把人名／術語換掉，也會跟投影片矛盾，所以寫手要拿這個檔案核對人名和數字。`--anchor-model turbo`（beam 1，約 56 倍）一樣能當時鐘，但它的用字太差，不能拿來核對，只在速度比品質重要時才用。
2. `scripts/gemini_asr.py` 把 10 分鐘一塊的音訊送給 Gemini（`--via api` = REST API key；`--via agy` = 無頭模式的 Antigravity CLI，==先讀它 docstring 裡的服務條款說明==），再把每一行重新對齊到本機時鐘（`ts_anchor.py`；對齊率低於 50 % 的 chunk 改用線性縮放）。它也會抓 Gemini 的無聲失敗：chunk 被截短（用本機時鐘做間隔檢查）和重複迴圈（重送，再把迴圈的行丟掉）。
3. Gemini 的過濾器在每條路徑都拒絕的 chunk（「blocked by Gemini's filters」，醫學演講常發生），由 ==breeze25 只轉錄那個 chunk 的範圍==（`--fill-blocked breeze25`，快取在 `*.part.fill`）。
4. 結果會變成 `transcript.json`／`transcript.txt`（JSON 每行有 `source`：`gemini` | `breeze25`），所以 split_segments／build_L1／audit_note 不用改就能跑；`transcript_source.json` 記錄路徑。Gemini 整個失敗（額度、網路）→ 整支檔案退回單純的 breeze25（舊路線）。

HARD RULE 3 依然成立：Gemini 是另一個 ASR 來源，不是修正流程，絕對不要編輯它的行。Gemini 是 LLM，所以只有它有的數字（沒有投影片、沒有第二個來源）在筆記裡維持「未確認」。單獨跑 `gemini_asr.py`（帶 `--anchor`、不補填）仍然是把 Gemini 加成現有 breeze25 逐字稿旁邊==第二個==來源的做法（例如舊課程、遠場禮堂）。
→ `reference/decisions.md#gemini-primary`、`#far-field-hall`。

**遠場禮堂錄音**（聽眾席、PA 系統、非母語講者）：
- 允許把音訊外送的話：把 Gemini 加成一個來源（見上）：術語命中率 82 % 對 54–60 %。
- 否則（離線）：另外跑 `--model large-v3` 和 Qwen3-ASR-1.7B，把所有版本都給寫手（命中率 65 %，聽錯從 22 降到 3）。
- 不管哪種，==只在一個來源出現的數字都算未確認==，直到投影片或第二個來源對得上：同一個模型對同一個數字，兩次跑出 58 % 和 150 %。
音訊前處理（band-pass、降噪、loudnorm、WPE）實測沒有改善，不要做。
→ `reference/decisions.md#far-field-hall`

### Step 5 — Stage A：擷取畫面（只有 Path A）

```bash
python <skill-dir>/scripts/extract_slides.py "<video>" --output-dir "$OUT_DIR" --interval 15
```
寫出 `slides/frame_NNNN.jpg` + `slides/timestamps.json`，相鄰幾乎一樣的畫面用 phash 去重。Path B/B-images 跳過這步。→ `reference/pipeline.md#stage-a`

### Step 6 — Stage B：快速 OCR + 熵值（只有 Path A）

```bash
python <skill-dir>/scripts/quick_ocr.py "$OUT_DIR"
```
對每個畫面跑 RapidOCR → `slides_raw.json`。==必做==：沒有它的話，每張投影片在 Stage D 的閘門看來都像裝飾用的。→ `reference/pipeline.md#stage-b`

### Step 6-alt — Path B / B-images 橋接

```bash
python <skill-dir>/scripts/build_slides_from_pdf.py    "$OUT_DIR"   [--audio-duration-sec N]
python <skill-dir>/scripts/build_slides_from_images.py "<img_dir>" -o "$OUT_DIR" [--audio-duration-sec N]
```
兩種橋接都會直接產出 `slides_raw.json` + `slides_dedup.json`，取代 Steps 5–7。→ `reference/pipeline.md#path-b`

### Step 7 — Stage C：語意去重（只有 Path A）

```bash
python <skill-dir>/scripts/dedup_semantic.py "$OUT_DIR"
```
依文字子集或版面相似度合併相鄰畫面，標記 `dedup.is_canonical`。輸出 `slides_dedup.json`。
→ `reference/pipeline.md#stage-c`

### Step 8 — Stage B2：高品質 OCR（Surya）

```bash
python <skill-dir>/scripts/ocr_surya.py "$OUT_DIR" [--resume]
```
Surya 跑在自己的 venv 裡，處理有文字的 canonical 投影片，RapidOCR 當作淺層的備援。新增 `ocr.clean_text` / `ocr_engine` / `ocr_confidence`。==直接原地更新 `slides_dedup.json`==（一次性備份成 `slides_dedup.pre_b2.json`），並寫出 `slides_ocr.json`。Path B 跳過它，因為 `pdf_text` 本來就乾淨。沒有 Surya venv 的話，它會警告並把全部丟給 RapidOCR，而不是失敗。
→ `reference/pipeline.md#stage-b2`

### Step 9 — Stage D：VLM 訊號

```bash
python <skill-dir>/scripts/vlm_signals.py "$OUT_DIR" --model minicpm-v:8b --num-ctx 4096
```
對每張 canonical 投影片產出語意訊號，前面有一道 4 條件的預先跳過閘門，用來擋裝飾性畫面。先重新檢查 GPU（Step 3）。輸出 `slides_vlm.json`。
`scripts/ocr_slides.py` 是已棄用的 shim，會轉發到這裡，argv 和輸出都一樣。→ `reference/pipeline.md#stage-d`

### Step 10 — Stage E：逐字稿 grounding

```bash
python <skill-dir>/scripts/ground_slides.py "$OUT_DIR"
```
純 Python，0 次 LLM 呼叫。把每張 canonical 投影片對應到它播放期間講的話。輸出 `slides_grounded.json`，也就是整合階段的輸入。
→ `reference/pipeline.md#stage-e`

### Step 11 — 標記可疑的 ASR token

```bash
python <skill-dir>/scripts/flag_asr_suspects.py --dir "$OUT_DIR"
```
在這裡跑，就在 Stage E 之後：它需要的投影片詞彙表來自 `slides_grounded.json`。寫出 `asr_suspects.txt`；==逐字稿本身一個 byte 都不會變==。每一行都當成一個問題，絕對不是替換。
→ `reference/pipeline.md#asr-suspects`

### Step 12 — 分塊預先摘要（只有長演講）

逐字稿超過約 30 分鐘 / 25 k token 的話，把各塊的摘要交給 Sonnet subagent，不要把整份逐字稿讀進主 context。覆蓋率防護（`[CHUNK_END]`、`[CONTINUE_NEEDED]`、預期 chunk 數）一定要有。
→ `reference/pipeline.md#chunked-summarization`

### Step 13 — Stage F：整合（Claude）

批次和長演講分兩輪：==先 Tier-pass，再 Write-pass==：

- **Tier-pass subagent** 讀 `slides_grounded.json` + `transcript.txt` + `pdf_text.json`，套用 tier 評分規則，**只**寫 `slides_final.json`（整數 `tier`、`attachment_name`、`embed_width`、`section_suggestion`）。這個檔案是凍結的 tier 權威。
- **Write-pass subagent** 讀凍結的 `slides_final.json` + 逐字稿 + 投影片文字，寫出 `note_draft.md`，裡面只放 `[[EMBED sN]]` 佔位符，不放路徑、寬度或 callout。

單場短演講一輪就夠了；分成兩輪是為了不讓寫手為了讓自己的 embed 稽核過關，而把結構簡化掉。→ `reference/note-spec.md`
（必讀：品質規格、tier 規則、prompt 要求）

### Step 14 — 渲染、定稿、稽核

```bash
python <skill-dir>/scripts/render_embeds.py    "$OUT_DIR" --note note_draft.md --in-place
python <skill-dir>/scripts/finalize_to_vault.py "$OUT_DIR" [--vault-root PATH]
python <skill-dir>/scripts/audit_note.py "<note path>" --mode lecture --grounding "$OUT_DIR"
```
`render_embeds.py` 把佔位符展開成帶路徑和寬度的 col-0 callout，並稽核 Tier-1/2 的覆蓋率；`finalize_to_vault.py` 把被引用的投影片和筆記複製進 vault；稽核器就是最後的閘門。==一定要帶 `--grounding`==，沒帶的話，圖說↔畫面的檢查只會警告。→ `reference/note-spec.md`
**免審草稿**：這份輸出是機器轉錄加整合出來的，直接寫進 inbox，不用先給使用者看草稿；使用者會在 Obsidian 裡審。

### Step 15 — 網頁檢視器匯出（只要有影片就預設做）

```bash
python <skill-dir>/scripts/build_single_talk_web.py "$OUT_DIR" --plan seg_plan.json
# … Stage F 寫出 L3/ 的檔案 … 然後：
python <skill-dir>/scripts/build_single_talk_web.py "$OUT_DIR" --plan seg_plan.json --export
```
單場演講預設也有同步的 HTML 檢視器，不是只有工作坊才有。
==Stage F 自己撰寫分段計畫==（JSON 清單：seg/start/end/slug/title_zh，從逐字稿和投影片主題推導，不需要人工分段）；==內容章節要靠更多的 segment，不是更多的標題==，檢視器每個 segment 剛好建兩個章節。腳本會從 `transcript.json` 組出 manifest + `segments.json` + L2 切片 + HUB 骨架，並且==自動附加一個只有 L3 的「全場總整理」總覽 segment==（排在最前面：segment 很多時還是需要一個地方把所有東西列出來；HUB 絕對不會在檢視器裡渲染）。接著 Stage F 為每個 segment 寫一份 `L3_segNN_<slug>.md`（==圖片 embed 只用 basename，時間碼用 `` `(V1 MM:SS)` ``==）加上總覽筆記。內容的形式由==一個問題==決定：==這是不是單一的知識體？==（單場演講 → 精華 + 每段一句話；同一位講者的脈絡 → 依主題重組並附來源；多位講者的工作坊 → ==只做目錄，絕對不硬做整合==，規格在 `reference/pipeline.md#web-export`）；只要有任何一份 L3 缺漏，`--export` 就會拒絕執行。
壓縮預設是 ==H.265 CRF 24==（自用；要分享給你無法確認環境的機器時用 `--codec h264`）。多場演講的工作坊維持自己的流程 →
`reference/segmented-mode.md`。→ `reference/pipeline.md#web-export`

## 邊界情況

- **只有音訊、沒有簡報** → 只用逐字稿的筆記，用 `# 逐段筆記`，不用 `# 逐投影片筆記`。
- **N-up 講義 PDF** → 先渲染其中一頁中間的頁面並==親眼看==，再決定網格；對投影片很多的 PDF，啟發式判斷不可靠。然後
  `crop_multiup_pdf.py <pdf> <out_dir> --expected-rows R --expected-cols C`。
  真的是 1-up 的頁面（標題頁）逐頁處理，不要硬塞進共識網格。
- **很長的演講（>90 分鐘）** → 轉錄用分塊執行器，閱讀用 Step 12。**一批錄音** → 嚴格依序轉錄；每個 faster-whisper 實例約佔 4.5 GB RAM。
- **一場演講拆成好幾個檔案** → 做成一份筆記，不是好幾份。
- **投影片是英文，講者講中文** → 兩邊都保留；簡報提供術語，逐字稿提供解釋。
- **講者要求不要錄音** → 排除那段內容。
- **密集文字的講義，不是投影片簡報** → 當作主要來源，但不要用逐投影片的結構。
- **CJK 路徑失敗**（exit 127 / 3221226505）→ 先用 ffmpeg 另外抽出音訊；腳本會重用驗證過的 `audio.wav`。

## 選配的基礎設施

下面全部都是==這台機器的設定，不是必要條件==，pipeline 沒有任何東西依賴它們，通用的替代做法都寫在旁邊。

| 用途 | 通用替代方案 |
|---|---|
| `job_runner.py` 包住長時間 GPU 工作（timeout 時把子行程整棵殺掉） | 單純的 `timeout <n> <cmd>`，或直接在前景跑 |
| `gpu_lease.py` / 並行批次之間的暫停旗標檔 | GPU 階段一次跑一個；config 裡把 `paths.pause_flag` 留空 |
| 整合期間的 `vault-search` / OpenEvidence / Zotero 查詢 | 跳過；只引用演講本身提供的內容 |
| `ntfy` 完成通知 | 跳過 |
| 外部批次控制平面（`run_queue`、`rerun_batch`、`clip_order`、dashboard） | 課程專用，沒有隨附，見 `reference/segmented-mode.md` |

Vault 路徑（`99Attachment/lecture_{slug}`、inbox 資料夾）是==私人 vault 的慣例==，可以設定：`render_embeds.py --attach-root` / `--attach-dir`、`finalize_to_vault.py --vault-root`。

## 相依套件

```bash
ollama pull minicpm-v:8b               # ~5.5 GB Q4_K_M, Stage D
pip install rapidfuzz rapidocr-onnxruntime scikit-image pyyaml json_repair pillow numpy
```
PATH 上要有 `ffmpeg` + `ffprobe`。Surya（Stage B2）放在自己的 venv；在 `config.yaml` 裡把 `ocr_engine.surya_python` 指向它，或留空就退回 RapidOCR。新機器上把 `config.example.yaml` 複製成 `config.yaml`；裡面每個跟機器相關的值預設都是空的，而且可以用環境變數覆蓋。
==選配的相依套件缺少時會大聲降級，不會靜靜降級==：缺 scikit-image 或 RapidOCR 都會被回報並擋住，因為靜靜降級產出的是*錯的*輸出，而不是比較少的輸出（`reference/decisions.md#optional-dependency-degradation`）。

## 檔案位置

```
<skill-dir>/
├── SKILL.md, config.yaml, config.example.yaml
├── reference/  pipeline.md · note-spec.md · segmented-mode.md · multi-camera.md · decisions.md
├── data/       real_words.txt, real_acronyms.txt   (regenerated, not committed)
├── ocr_bench/  engine benchmark harness (bring your own fixtures)
└── scripts/
    ├── route_inputs.py           front door — classifies material, prints the plan
    ├── transcribe_video.py  retranscribe_segment.py  gpu_check.py  groq_asr.py  gemini_asr.py
    ├── import_transcript.py      external SRT / VTT / JSON -> transcript.json
    ├── provenance.py             provenance.json record + `verify <dir>`
    ├── extract_slides.py  quick_ocr.py  dedup_semantic.py  ocr_surya.py
    ├── vlm_signals.py            (ocr_slides.py = deprecated shim → here)
    ├── build_slides_from_pdf.py  build_slides_from_images.py  crop_multiup_pdf.py
    ├── ground_slides.py  flag_asr_suspects.py  make_glossary.py  build_real_words.py
    ├── render_embeds.py  finalize_to_vault.py  audit_note.py  export_web.py
    ├── media_capture_index.py  xcorr_media_offsets.py  query_near_field.py
    ├── _mdpm.py                  AVCHD .MTS recording clock (no container tag)
    ├── adapters/    surya_adapter.py        (production OCR adapters)
    ├── batch/       course_timeline (real-time ordering authority) ·
    │                audit_segmentation (is the proposal still valid?) ·
    │                build_L1 · split_segments · split_L1_by_segment · add_dhash ·
    │                vlm_cache · detect_language · detect_language_audio ·
    │                phi_mask · process_slide_deck     (generic batch layer)
    ├── layout2/     viewer.css, viewer.js   (web viewer assets, edited verbatim)
    └── _common.py  _log.py  _paths.py
```

每場演講的輸出資料夾：

```
{lecture}/
├── metadata.json          run_id + media fingerprint + per-stage status
├── provenance.json        per artifact: stage, tool, engine, model, params, network, input hashes
├── transcript.json/.txt   timestamped segments; .txt is [MM:SS] text, H:MM:SS past an hour
├── asr_suspects.txt       flagged tokens — flags only, never a rewrite
├── alignment.json         multi-source capture-start hypotheses (when applicable)
├── slides/                frame_NNNN.jpg | page_NN.jpg | original photo names
├── slides_raw.json        Stage B    quick text + density + entropy
├── slides_dedup.json      Stage C    canonical markers (Stage B2 updates in place)
├── slides_dedup.pre_b2.json          one-time pre-Stage-B2 snapshot
├── slides_ocr.json        Stage B2   Surya result, for inspection
├── slides_vlm.json        Stage D    VLM signals + vlm_skip + skip_metrics
├── slides_grounded.json   Stage E    transcript grounding + retrieval fields
├── slides_final.json      Stage F    tier + score + attachment_name + width
└── logs/progress_*.jsonl  per-stage event streams (not every stage emits one)
```

每個階段的輸出都是前一階段的超集合，所以可以只重跑某一個階段，不用重做轉錄或擷取畫面。`python <skill-dir>/scripts/provenance.py
verify "$OUT_DIR"` 會列出 `stale`（輸入在它們建好之後被改過，要重跑那個階段）或 `modified`（在階段寫完之後被手動編輯過）的產物。Stage F 用 `provenance.py record` 登記自己（見公開 repo 的 `docs/stage-f-contract.md`）。從資料檔取出的名稱（plan 的 slug、`attachment_name`、embed 目標、投影片檔名）必須留在命令列給定的資料夾內：不在的話，該階段會以 exit 2 結束；要修的是資料，絕對不是檢查。上一層的 `runs.jsonl` 每跑一次階段就記一行摘要，用 `run_id` 串起來。中間產物要留著，tier 判斷出問題時要靠它們除錯。
