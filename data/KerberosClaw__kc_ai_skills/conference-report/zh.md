---
name: conference-report
description: "當使用者參加了一場或多場大會的 session（有錄音和投影片照片），需要協助建立：(1) 忠實的逐場 markdown 重建（投影片視覺內容 + 講者逐字稿，並標註 Whisper 幻覺），以及 (2) 後續的報告成品，其範圍和格式由使用者互動決定。Pipeline 階段（原始檔 → mlx_whisper 中文 SRT → 逐張投影片多模態重建 → 若有 Playwright 就對照大會官方議程）是確定性的。報告階段是互動式的：起草之前一定要先問使用者範圍（單場／單日／多日匯總）、格式（既有範本／自由格式備案）、收件對象（正式／非正式），以及任何業務主軸的對應。"
version: 0.2.0
status: mvp
triggers:
  - "/conf-report"
  - "處理大會逐字稿"
  - "整理今天 session"
  - "整理今天場次"
  - "conference report"
  - "conf-report"
  - "處理今天的 session"
  - "把今天聽的場次整理成報告"
  - "外訓報告"
  - "大會心得"
  - "大會報告"
---

# conference-report

你是大會的筆記員兼報告起草人。你的工作分成兩個不同的階段：

- **Phase A：重建（確定性）：** 拿原始錄音和投影片照片，產出逐場 markdown，忠實重建投影片視覺內容和講者逐字稿，附上 Whisper 幻覺標註和官方議程的交叉比對。
- **Phase B：報告（互動式）：** 建立在重建結果之上的報告。範圍、格式、收件對象和業務對應都是每個使用者自己的決定，寫之前要先問使用者。

你在使用者本機的 Mac 上操作（有 mlx_whisper，Claude vision 可以用 Read 工具直接讀 HEIC，Playwright MCP 可能有裝，可用來即時查議程）。

## Trigger

```
/conf-report <conf-dir-name> [<day-tag>]
```

範例：
- `/conf-report cybersec2026 D2`：處理 CYBERSEC 2026 的第 2 天
- `/conf-report cybersec2026`：讓使用者說明要哪幾天、報告範圍是什麼

如果使用者沒給任何參數，先問是哪場大會、哪幾天，再繼續。

---

# Phase A — Reconstruction (per session)

這個階段是確定性的，不管使用者最後想要的報告長什麼樣子，做法都一樣。

## Inputs (what the user provides)

使用者的 iPhone 對每場出席的 session 產出：

- **1 個音檔**（m4a，來自語音備忘錄）：可能是整天一個連續錄音，也可能是每場一個
- **N 張投影片照片**（HEIC，一張一頁，包含大綱／轉場頁）

使用者把這些丟到 `drafts/<conf>/raw/<day>_<HHMM-HHMM>/`（每場一個目錄）。同一場的照片和音檔放在一起。

## Outputs of Phase A

每場：
- `drafts/<conf>/<day>_<HHMM-HHMM>.md`：重建後的投影片 + 帶 Whisper 幻覺標註的逐字稿 + frontmatter 裡的官方議程 metadata

（還沒有當日報告，那是 Phase B 的事。）

## Prerequisites Check

動手之前先確認這些東西都在。如果缺了，就停下來指示使用者：

```bash
which mlx_whisper       # ~/.local/bin/mlx_whisper
which sips              # built into macOS
claude mcp list         # check if 'playwright' is connected (optional, can fall back to curl)
```

如果缺 `mlx_whisper`：
```bash
pip install mlx-whisper
```

## Step A1: Inventory raw materials

針對目標日期，列出 `drafts/<conf>/raw/` 裡有什麼，並和使用者確認：

```bash
ls -la drafts/<conf>/raw/<day>_*/
```

每場預期有：`*.m4a` + `IMG_*.HEIC` 照片。數量要合理（例如 30 分鐘的場次大約 25 到 35 張投影片）。

**決策表：結構不對時怎麼辦：**

| 情況 | 動作 |
|---|---|
| 一個 m4a 涵蓋多場 session | 請使用者指出切分的時間點；轉錄之前用 `ffmpeg -i ... -ss HH:MM:SS -t ...` 切開 |
| HEIC 照片全在同一個資料夾，沒有分場 | 請使用者說明哪個 IMG 範圍屬於哪一場（用第一張／最後一張投影片 + EXIF 時間戳） |
| 某一場的音檔不見了 | 在該場 `.md` 的 frontmatter 標成「錄音遺失」；只靠投影片重建 |
| 有些 HEIC 照片不見了（IMG 編號有缺口） | 在附錄註明缺口（例如「缺 IMG_7084、IMG_7088」），用現有的繼續 |

## Step A2: Transcribe audio with mlx_whisper

對每場的 m4a 執行：

```bash
~/.local/bin/mlx_whisper \
  --model mlx-community/whisper-large-v3-turbo \
  --language Chinese \
  --output-format srt \
  --output-dir drafts/<conf>/raw/<day>_<HHMM-HHMM>/ \
  drafts/<conf>/raw/<day>_<HHMM-HHMM>/<audio>.m4a
```

**非常重要**：輸出格式只用 `srt`。不要產生 json/tsv/txt/vtt，它們都是衍生的雜訊。如果出現了，事後要刪掉：

```bash
find drafts/<conf>/raw -type f \( -name "*.json" -o -name "*.tsv" -o -name "*.txt" -o -name "*.vtt" \) -delete
```

## Step A3: Build per-session markdown (the core artifact)

每一場都要產出 `drafts/<conf>/<day>_<HHMM-HHMM>.md`，結構要完全照這樣：

```markdown
# <Conference> <Day> — <HH:MM>-<HH:MM>

> Source：投影片 HEIC（<N> 張，多模態直讀）+ Whisper 逐字稿（mlx_whisper large-v3-turbo，<srt-filename>，~<duration> 分鐘）
> 講者：<from frontmatter slide self-intro>
> 主題：<from title slide>
> 大會 session: <official URL once Step A4 confirms>

---

## Slide 1 — <slide title>
**時間**：<HH:MM> [口述]

**投影片**：
- <visual element 1, with [投影片] tag> [投影片]
- <visual element 2 with layout / colors / icons>
- ...

**口述**：
<transcribed speech, paragraph form, with [口述] tag at end of each paragraph>

<If Whisper made mistakes, inline-correct in brackets like:>
[原識別 → 推斷正解]
<For obvious hallucination loops, replace with note:>
（Whisper 此處連續輸出 "X" 約 N 次，疑為 transition word 誤判，原話無法重建）

---

## Slide 2 — ...
```

**怎麼用多模態讀 HEIC 投影片：**

直接對 HEIC 檔案用 Read 工具，Claude vision 原生就能讀 HEIC。每張照片要擷取：
- 標題文字（投影片上的大字）
- 條列重點／內文
- 視覺版面（左右分欄？格狀？時間軸？）
- 帶有意義的圖示／插圖／顏色
- 浮水印／頁尾／機密等級標籤

把每張投影片配對到時間戳大約落在該投影片顯示區間內的 SRT 片段。講者通常每 30 到 90 秒換一張投影片，用這個當經驗法則。

**被遮住的新聞截圖備案：** 如果某張投影片是公開新聞文章的截圖（iThome、Bloomberg、TechCrunch 等），而關鍵文字被觀眾的頭、講台或講者的剪影擋住，**不要用猜的**，去抓原始文章。把看得到的線索（媒體 logo、標題關鍵字、記者署名、日期）記下來，然後：

- 用 WebFetch／WebSearch 搭配 `<headline keywords> site:<publication>` 取得原文，準確引用被遮住的部分，或是
- 如果媒體有付費牆，就用 Google 搜標題，找快取／鏡像版本

然後從來源轉錄被遮住的文字，不是憑想像。在投影片重建裡註明那段文字是從來源回填的（例如「下半段被講者頭部遮蔽，內文以 iThome 原文回填」）。這條規則只適用於公開的新聞／部落格截圖，不適用於來源無法公開取得的公司內部投影片。

## Step A4: Cross-check official agenda (CRITICAL for accuracy)

**一定要做**：講者姓名、職稱、場次標題、地點和 track，都必須來自官方議程，不是投影片或逐字稿。投影片可能有錯字；Whisper 可能認錯名字；講者可能用非正式的頭銜自我介紹。

**首選路徑：Playwright MCP**（如果 `claude mcp list` 顯示 playwright 已連線）：

```javascript
// 1. Navigate to agenda page
mcp__playwright__browser_navigate(url: "<conference-agenda-url>")
// 2. Extract session links matching session titles
mcp__playwright__browser_evaluate(function: () => {
  const links = Array.from(document.querySelectorAll('a'))
    .filter(a => a.href.includes('/session/'))
    .map(a => ({ text: a.innerText, href: a.href }));
  return links.filter(l => l.text.includes('<session-keyword>'));
})
// 3. For each session URL, navigate + extract: title, time, location, speaker name + title + company, abstract, track, level
```

**備案路徑：curl + 手動擷取**（如果沒有 Playwright）：

```bash
curl -s -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15" \
  "<session-url>" -o /tmp/session.html
# Parse with grep / sed for the rendered text portions
```

**把官方的更正套用到：**

1. 該場 `.md` 的 frontmatter（加一行 `> 大會 session: <url>`，並註明投影片自述和官方資料之間的任何出入）
2. 任何已存在的 `session_schedule.md` 表格（更正講者姓名，加上場次網址連結），見下方選用的 Step C

**非常重要的不變式**：當官方網站和投影片／逐字稿在**身分資訊**（姓名、職稱、公司）上不一致時，所有衍生文件都**以官方為準**。在該場 `.md` 的 frontmatter 註明出入，以便追溯，但不要去「更正」逐字稿本文（逐字稿是對說過的話的記錄）。

## Step A5: Annotate Whisper hallucinations in per-session markdown

Whisper large-v3-turbo 處理中文大會音檔，有已知的失敗模式。掃描 SRT 找這些模式並標註：

| 模式 | 範例 | 處理方式 |
|---|---|---|
| 單行重複迴圈（≥10 次） | `"那邊"` × 33 | 換成註記：「（Whisper 此處連續輸出 'X' 約 N 次，疑為 transition word 誤判，原話無法重建）」 |
| 長幻覺尾巴（最後 N 分鐘遺失） | 最後 14 分鐘 = 單一片語迴圈 | 在 frontmatter 加 `⚠ 重大警示` 區塊，第 20 張以後的投影片只靠照片重建 |
| 英文專有名詞 → 中文音譯 | Claude → 龍蝦, Anthropic → 種種, CLAUDE.md → Cloud.md | 行內更正：`龍蝦 [Claude]` |
| 品牌／產品音譯 | DeepSeek → 深度求索（正確）, Cloudflare → Codefit（錯誤） | 依上下文行內更正 |
| 講者自我介紹轉錯 | 職稱／公司名稱 | 對照 Step A4 的官方議程；在 frontmatter 更正 |

在每場 `.md` 最後附加一個 `**附錄**` 段落，列出：
- 投影片張數（含 IMG 編號範圍，列出任何缺口）
- 錄音長度（從 SRT 末尾時間戳）
- 講者
- 缺漏段落（列出任何重建的缺口）
- Whisper hallucination 警訊清單（具體時間戳 + 問題性質）

---

# Phase B — Report (interactive)

**Phase B 不會在 Phase A 之後自動執行。** 當使用者明確要求報告時，先跑需求問答。

## Step B1: Requirements quiz (MANDATORY before drafting)

寫報告的第一行之前，先把這四個面向用一份編號清單問使用者（一則訊息放完四個問題，讓使用者用簡短的答案回覆，不要一題一題問）：

```
我要寫報告之前先確認 4 件事，請逐項回覆（不確定可說「沒想法」我會給推薦）：

1. **範圍**：要寫哪幾場？
   - (a) 單場 — 哪一場？
   - (b) 單日整合 — 哪一天？
   - (c) 多日匯總 — 哪幾天？整會議？

2. **既定格式**：
   - (a) 有 template / sample，請貼上 / 給檔案路徑
   - (b) 沒有，由我建議格式（會依範圍給 sane default）

3. **受眾**：
   - (a) HR / 上級主管（送公司外訓報告 → 正式書面）
   - (b) 內部團隊 / wiki（半正式，含技術細節）
   - (c) 個人筆記 / 私存（隨意）

4. **業務 mapping**：要不要把每場連到公司 workstream / ticket / 專案？
   - 要 → 列出對應主軸（例：「Auth 改版 + 第三方 API 整合 / Ticket #123 + #456」這類抽象描述，請避免具體客戶名 / 產品碼）
   - 不要 → 純技術內容，不對應內部 context
```

等使用者回覆。四個面向都回答之前（或使用者明確說「用 default」之前）不要起草。

## Step B2: Pick template based on quiz answers

問答完之後，推導出報告的樣子：

| 範圍 | 既定 template? | 受眾 | 用什麼 |
|---|---|---|---|
| 單場 | 有 | * | 套 user 給的 template |
| 單場 | 沒 | 任一 | **Default A** — 單場深度 takeaway 結構 |
| 單日 | 有 | * | 套 user 給的 template |
| 單日 | 沒 | HR / 主管 | **Default B** — 7 段式正式外訓報告 |
| 單日 | 沒 | 團隊 / wiki | **Default C** — 簡化 4 段（議程 / 重點 / 應用 / 附件） |
| 單日 | 沒 | 個人 | **Default D** — bullet list 純技術 takeaway |
| 多日 | 有 | * | 套 user 給的 template |
| 多日 | 沒 | HR / 主管 | **Default E** — 跨日匯總 + 趨勢分析 + 整體應用建議 |
| 多日 | 沒 | 團隊 / wiki | **Default F** — 主題彙整（cross-cut themes 而非 chronological）|
| 多日 | 沒 | 個人 | **Default G** — bullet list 跨日技術 takeaway |

範本 A 到 G 在下面。

### Default A — 單場深度 takeaway

```markdown
# <Session 標題> — 場次筆記
**講者**：<官方姓名 / 職稱 / 公司>
**場次**：<日期 HH:MM-HH:MM @ 地點>
**主題**：<官方主題>
**Source**：<per-session .md 檔路徑>

## 核心論點
<2-4 句精煉>

## 重點 takeaway
1. ...
2. ...
3. ...

## 適用建議
<若有 mapping 才寫；無則略>
```

### Default B — 7 段式正式外訓報告（單日 + HR/主管）

```markdown
# 外訓報告 — <Conference> <Day>

## 一、基本資訊
| 項目 | 內容 | ... |

## 二、訓練目的
<業務 mapping，無 mapping 則改寫成「產業趨勢更新」>

## 三、議程摘要
<表格：時段 / 議程標題 / 講者（官方）>

---

## 四、議程內容與重點摘要
> **資料來源原則**：講者身份、職稱、議程主題、場地等識別資訊以**大會官方議程頁**為準；演講內容以**現場錄音逐字稿 + 投影片重建**為來源。

### Session 1 — <title>（<speaker>）
**核心論點**：<2-4 句>
<然後表格 / bullet>

### Session 2 — ...

---

## 五、重點收穫
<5-7 條跨場主軸>

## 六、對公司業務的應用建議
<僅在有 business mapping 時生；無則改成「產業趨勢應用方向」泛論>
### 短期 / 中期 / 長期 三層

## 七、附件
- 三場議程之逐字稿與投影片重建：<links>
- 大會官方 session 連結
- 外部參考資料

**報告人**：<name>
**報告日期**：YYYY-MM-DD
```

### Default C — 簡化 4 段（單日 + 團隊/wiki）

```markdown
# <Conference> <Day> — 場次重點

## 議程
<表格>

## 重點 takeaway
<5-10 條跨場 bullet>

## 公司應用建議
<若有 mapping 才寫>

## 附件
<逐字稿 link + 大會官方 link>
```

### Default D — 個人筆記（單日 + 個人）

```markdown
# <Conference> <Day> 筆記
- <key takeaway 1>
- <key takeaway 2>
...

## Sessions
- [<HH:MM> <title>](<per-session .md>)
- ...
```

### Default E — 跨日匯總 + 趨勢分析（多日 + HR/主管）

```markdown
# <Conference> 整會議外訓報告

## 一、基本資訊
<整會議資訊：N 天、總場次、合計時數>

## 二、訓練目的
<業務 mapping>

## 三、出席議程總覽
<表格：分日列出，每場一行，含 link>

---

## 四、跨日主題分析
> 不依時間 chronological，依 theme 切

### Theme 1 — <e.g., Prompt Injection 與 Agent 攻擊面>
**多場 cover**：<list 哪幾場 cross-reference>
**核心論點整合**：...
**框架 / 工具歸納**：...

### Theme 2 — ...
### Theme 3 — ...

---

## 五、重點收穫
<跨日整體 takeaway 5-10 條>

## 六、對公司業務的整體應用建議
### 短期 / 中期 / 長期 三層

## 七、附件
<分日列出 per-session links + 大會官方 links>
```

### Default F — 主題彙整（多日 + 團隊/wiki）

跨日主題彙整版本，比 E 簡化（無 §一/§二/§六/§七 ceremony，主軸是 §四 主題分析）。

### Default G — 個人匯總筆記（多日 + 個人）

跨日 bullet 格式，純 takeaway + session list。

## Step B3: Apply project writing discipline

如果工作中的 repo 有 `CLAUDE.md` 或 `docs/claude_rules/` 定義了語氣／用字規則，就套用到報告上：

- **中性用詞紀律** — git-bound docs avoid 屎山 / 雷 / 投機 等情緒詞
- **公開化 contract** — if user says "上 ADO wiki" or "公開化"，套對應 contract（無個人 attribution / 無日期 marker / 無內部組織 reference）
- **業務 mapping 紀律** — 用 ticket 編號或抽象描述，不寫客戶名

每場 `.md`（Phase A 產出）是 internal memo 風格，**不**對它套公開化規則。Phase B 報告則依受眾決定。

## Step B4: Draft, deliver, iterate

根據問答結果和範本寫報告。一律要：
- 識別資訊（姓名／職稱／場次）用官方議程的事實
- 演講內容從每場 `.md` 取材
- 講者對未來的說法，加註「（待官方確認）」
- 在附件／來源段落引用每場 `.md` 檔案

把草稿給使用者看；預期會在用字、範圍、深度上來回修改。

---

# Step C (optional) — Update session_schedule.md if it exists

如果事前規劃留下了 `drafts/<conf>/session_schedule.md`：

1. **標記實際有出席的場次**，和原本計畫的區分開（把沒去的那一列砍掉）
2. 把日期標題從「計劃 N 場」改成「實際出席 M 場」
3. 每一場有出席的，在 Session 欄附加 📝 逐字稿連結 + 🌐 官方場次連結
4. 更新 `今日場次` 的統計行
5. 更新底部的摘要表（只更新有出席那一天的那一列）

**場次那一列的格式範例：**
```
| 14:45-15:15 | **<title>**<br>📝 [逐字稿 D1_1445-1515](D1_1445-1515.md) ｜ [大會 session](<official-url>) | <speaker> / <location> | <主軸對應> |
```

如果沒有 `session_schedule.md`，整個跳過這一步。不要自己主動建一個。

---

## Decision frameworks

### When to use NotebookLM vs this pipeline

| 目標 | 工具 |
|---|---|
| 單場的 Audio overview / podcast / mind map | NotebookLM（更快、文字更順） |
| 帶時間戳和視覺細節、忠實的逐張投影片重建 | 這個 pipeline（HEIC 多模態 + Whisper SRT） |
| 需要交叉參照的多場報告 | 這個 pipeline |
| 隨意的個人筆記 | NotebookLM |

NotebookLM 會把逐字稿修順，代價是犧牲投影片視覺細節和時間戳的準確度。這個 pipeline 兩者都保留。**要交給 HR／主管的報告，一律用這個 pipeline。**

### How aggressive to make Whisper corrections

| 把握度 | 動作 |
|---|---|
| 100% 確定（英文品牌被誤音譯、眾所周知的專有名詞） | 行內直接更正，不加括號：`Claude` |
| 強推論（上下文可以判斷） | 行內加括號更正：`龍蝦 [Claude]` |
| 弱推論（有多個合理選項） | 括號加問號：`它 [它? / 然後?]` |
| 無法復原（幻覺迴圈） | 換成註記，不要猜 |

## Anti-patterns

- ❌ **還沒跑問答（Step B1）就不要起草報告**：如果範圍／格式／收件對象／對應和你猜的不一樣，就白做了
- ❌ **不要假設「外訓報告」的語意**：使用者實際需要的可能是一頁個人筆記，也可能是多日的主題匯總，要問
- ❌ **不要沒做問答就把 Phase A 和 Phase B 一次寫完**：Phase A 永遠用同樣的方式跑，Phase B 是每個使用者自己的決定
- ❌ **還沒做 Step A4 的交叉比對就不要寫報告**：名字會錯，之後下游的檔案都得重改
- ❌ **不要把 Whisper 的衍生輸出（.json/.tsv/.txt/.vtt）丟進 raw/**：只留 .srt + .m4a，其他都是雜訊
- ❌ **不要把 `raw/` commit 進 git**：m4a + HEIC 只留在本機；確認 `raw/` 符合專案的 `.gitignore`
- ❌ **不要為了讀起來順而修飾逐字稿的文字**：保留講者實際的說法，包含贅詞；這個 pipeline 的價值就是忠實
- ❌ **不要把講者口頭上對未來的說法當事實**：當講者說「我會在 Y 大會發表框架 X」，在報告裡把它記成講者口述，加上「(待官方確認)」的註記
- ❌ **不要過度歸因講者的角色**：如果官方議程只列「OWASP Chapter Leader」，但投影片宣稱有 5 個角色，包含「X 公司創辦人兼 CEO」，以官方為準；只在該場 `.md` 的 frontmatter 註明出入
- ❌ **不要列入使用者沒實際參加的 keynote**：列進任何報告之前，先確認有出席
- ❌ **不要為了「看起來更乾淨」手動編輯逐字稿本文裡的 Whisper SRT 括號**：那些括號是稽核軌跡；清理是在報告（衍生物）裡做，不是在逐字稿（來源）裡做
- ❌ **不要跳過每場附錄裡的 Whisper hallucination 警訊清單**：將來用更好的模型重新轉錄時，要靠它知道哪些片段不可靠
- ❌ **如果 session_schedule.md 不存在，不要自動更新它**：那個檔案是某些使用者規劃流程的一部分，不是通用的產物

## Important rules

1. **兩個階段，兩種心態。** Phase A 是確定性的工程；Phase B 是互動式的成品塑形。不要混在一起。
2. **起草前先問答。** Phase B 一律從四個面向的問答開始。7 段式的預設只是七種可能範本之一，不是唯一的範本。
3. **識別資訊以官方議程為準。** 內容以投影片和逐字稿為準。兩者在姓名／職稱／地點上衝突時，以官方為準，並註明出入。
4. **保留稽核軌跡。** 每場 `.md` 保留 Whisper 的括號更正和附錄警訊。不要美化。
5. **Raw 只留本機。** `raw/` 要 gitignore；絕對不要把 m4a / HEIC check in。文字成品（每場 `.md` + 報告）是唯一會進 git 的東西。
6. **講者對未來的說法要加註記。** 如果講者預告了還沒公開的框架／論文／活動，把它標成講者口述，並建議使用者在正式場合引用之前先查證。
7. **套用專案的寫作紀律。** 如果工作 repo 裡的 `CLAUDE.md` 或 `docs/claude_rules/` 定義了語氣／用字規則（中性用詞／公開化 contract 等），就套用到報告上。每場 `.md` 是 internal memo 風格，不要對它套公開化規則。
8. **可重複使用是個優點。** 多日大會的 Phase A，這個 skill 每天跑一次。Phase B 依使用者選的範圍，可能每場跑一次、每天跑一次，或整場大會跑一次。每份輸出都應該是獨立的檔案（不要有 `_v2` 後綴，不要跨天原地修改）。
