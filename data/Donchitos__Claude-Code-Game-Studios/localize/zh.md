---
name: localize
description: "在地化流程：找出寫死的字串、抽出字串表、文化審查、配音、RTL，並執行 string freeze。"
argument-hint: "[scan|extract|validate|status|brief|cultural-review|vo-pipeline|rtl-check|freeze|qa]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/localize/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`



# Localization Pipeline

在地化不只是翻譯 — 它是讓遊戲在每一種語言和地區都有原生感的完整流程。
爛的在地化會破壞沉浸感、讓玩家困惑，還會卡住平台認證。這個 skill 涵蓋
從字串抽取，到文化審查、配音錄製、
RTL 版面測試，再到在地化 QA 簽核的完整流程。

**Modes：**
- `scan` — 找出寫死的字串和在地化的反模式（唯讀）
- `extract` — 抽出字串並產生可以直接拿去翻譯的表格
- `validate` — 檢查翻譯的完整度、placeholder 和長度
- `status` — 所有 locale 的覆蓋率矩陣
- `brief` — 產生給外部團隊的譯者背景說明文件
- `cultural-review` — 標出文化上敏感的內容、符號、顏色、慣用語
- `vo-pipeline` — 管理配音在地化：腳本、錄音規格、整合
- `rtl-check` — 驗證 RTL 語言的版面、鏡像和字型支援
- `freeze` — 執行 string freeze；在翻譯開始前鎖住來源字串
- `qa` — 在 release 前跑完整的在地化 QA 週期

如果沒有給子指令，就輸出用法然後停下來。Verdict: **FAIL** — 缺少必要的子指令。

---

每一次 `AskUserQuestion` 呼叫都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

## Phase 2A: Scan Mode

在 **code root** 搜尋寫死的、玩家看得到的字串（依 `.claude/docs/code-root-resolution.md` 解析）。**如果 code root 解析不出來，就回報 `NOT ASSESSED — code root unresolved`，不要回報零命中。** 解析不出來的 root 得到零命中，會被讀成「沒有東西要在地化」，這正是這條規定要防的失誤：

- UI 程式碼裡沒有包在在地化函式（`tr()`、`Tr()`、`NSLocalizedString`、`GetText` 等）裡的字串字面值
- 應該參數化的字串串接
- 使用位置式 placeholder（`%s`、`%d`）而不是具名 placeholder（`{playerName}`）的字串
- 混用了跟 locale 有關的資料（數字、日期、貨幣），卻沒有用 locale-aware 格式化的格式字串

搜尋在地化的反模式：

- 沒有用 locale-aware 函式的日期/時間格式化
- 沒有 locale 意識的數字格式化（`1,000` vs `1.000`）
- 內嵌在圖片或貼圖裡的文字（標記 `assets/` 裡的資產檔）
- 假設文字方向是由左到右的字串（位置式版面、字串組裝順序）
- 寫死在字串邏輯裡的性別/單複數假設（必須用複數形式或性別 token）
- 寫死的標點符號（例如 `"You won!"` — 驚嘆號的用法依 locale 而異）

回報所有發現，附上檔案路徑和行號。這個模式是唯讀的 — 不會寫任何檔案。

---

## Phase 2B: Extract Mode

- 掃描所有原始碼檔，找在地化字串的參照
- 跟 `assets/data/strings/` 裡既有的字串表比對
- 替還沒有 key 的字串產生新條目
- 依慣例建議 key 名稱：`[category].[subcategory].[description]`
  - 範例：`ui.hud.health_label`、`dialogue.npc.merchant.greeting`、`menu.main.play_button`
- 每個新條目都必須有 `context` 欄位 — 給譯者的註解，說明：
  - 它出現在哪裡（哪個畫面、哪個 scene）
  - 最大字元長度
  - 任何 placeholder 的意義（`{playerName}` = 玩家自己選的顯示名稱）
  - 如果適用，性別/單複數的脈絡

輸出要加進字串表的新字串 diff。

把 diff 呈現給使用者。問：「May I write these new entries to `assets/data/strings/strings-en.json`?」

使用者答應就只寫 diff（新條目），不要整份取代。Verdict: **COMPLETE** — strings extracted and written.

---

## Phase 2C: Validate Mode

讀 `assets/data/strings/` 裡所有字串表檔案。對每個 locale，檢查：

- **Completeness** — key 在來源（en）有，但這個 locale 沒有翻譯
- **Placeholder mismatches** — 來源有 `{name}`，但翻譯漏掉或多加了
- **String length violations** — 翻譯超過來源 `context` 欄位記錄的字元上限
- **Plural form count** — locale 需要 N 種複數形式；翻譯提供的比較少
- **Orphaned keys** — 翻譯存在，但 code root 裡沒有任何東西參照這個 key
- **Stale translations** — 翻譯寫完之後來源字串又改了（標記要重翻）
- **Encoding** — 有非 ASCII 字元，而且字型 atlas 有支援（不確定就標記）

依 locale 和嚴重度分組回報驗證結果。這個模式是唯讀的 — 不會寫任何檔案。

---

## Phase 2D: Status Mode

- 計算來源表裡可在地化字串的總數
- 每個 locale：計算已翻譯、未翻譯、stale（翻譯之後來源又改了）的數量
- 產生覆蓋率矩陣：

```markdown
## Localization Status
Generated: [Date]
String freeze: [Active / Not yet called / Lifted]

| Locale | Total | Translated | Missing | Stale | Coverage |
|--------|-------|-----------|---------|-------|----------|
| en (source) | [N] | [N] | [N] | [N] | [N]% |
| [locale] | [N] | [N] | [N] | [N] | [X]% |

> **Every cell above is a count you must take from the string table — including
> the source row.** Do not pre-fill the source locale as `100%`: that asserts a
> result before counting, and on a project with no `assets/data/strings/` it
> produces a coverage report for a table that does not exist. If the string table
> is absent, the whole status output is
> **`NOT ASSESSED — no string table found`**, not a matrix of zeros with a
> confident source row.

### Issues
- [N] hardcoded strings found in source code (run /localize scan)
- [N] strings exceeding character limits
- [N] placeholder mismatches
- [N] orphaned keys
- [N] strings added after freeze was called (freeze violations)
```

這個模式是唯讀的 — 不會寫任何檔案。

---

## Phase 2E: Brief Mode

產生譯者背景說明文件。這份文件會連同字串表匯出檔，
一起寄給外部翻譯團隊或在地化廠商。

讀：
- `design/gdd/` — 擷取遊戲類型、語氣、背景設定、角色名稱。依章節讀
  GDD：用 Grep 工具（pattern `^#`，
  content mode）找出你需要的標題，再用 offset 和 limit 讀那幾段範圍。
- `assets/data/strings/strings-en.json` — 來源字串表
- `design/narrative/` 裡任何既有的世界觀或敘事文件

產生 `production/localization/translator-brief-[locale]-[date].md`：

```markdown
# Translator Brief — [Game Name] — [Locale]

## Game Overview
[2-3 paragraph summary of the game, genre, tone, and audience]

## Tone and Voice
- **Overall tone**: [e.g., "Darkly comic, not slapstick — think Terry Pratchett, not Looney Tunes"]
- **Player address**: [e.g., "Second person, informal. Never formal 'vous' — always 'tu' for French"]
- **Profanity policy**: [e.g., "Mild — PG-13 equivalent. Match intensity to source, do not soften or escalate"]
- **Humour**: [e.g., "Wordplay exists — if a pun cannot translate, invent an equivalent local joke; do not translate literally"]

## Character Glossary
| Name | Role | Personality | Notes |
|------|------|-------------|-------|
| [Name] | [Role] | [Personality] | [Do not translate / transliterate as X] |

## World Glossary
| Term | Meaning | Notes |
|------|---------|-------|
| [Term] | [What it means] | [Keep in English / translate as X] |

## Do Not Translate List
The following must appear verbatim in all locales:
- [Game name]
- [UI terms that match in-engine labels]
- [Brand or trademark names]

## Placeholder Reference
| Placeholder | What it represents | Example |
|-------------|-------------------|---------|
| `{playerName}` | Player's chosen display name | "Shadowblade" |
| `{count}` | Integer quantity | "3" |

## Character Limits
Tight UI fields with hard limits are marked in the string table `context` field.
Where no limit is stated, target ±30% of the English length as a guideline.

## Contact
Direct questions to: [placeholder for user/team contact]
Delivery format: JSON, same schema as strings-en.json
```

問：「May I write this translator brief to `production/localization/translator-brief-[locale]-[date].md`?」

---

## Phase 2F: Cultural Review Mode

用 `Agent` 派出 `localization-lead`。請他針對目標 locale 稽核下列各項的文化敏感度（從 `assets/data/strings/` 和 `assets/` 讀取）：

### Content Areas to Review

**符號與手勢**
- 大拇指、OK 手勢、勝利手勢 — 意義依地區而異
- 美術、UI 或音訊裡的宗教或靈性符號
- 國旗、地圖呈現方式、有爭議的領土

**顏色**
- 白色（在某些亞洲文化代表哀悼）、綠色（在某些地區有政治聯想）、紅色（幸運 vs 危險）
- 跟文化聯想衝突的警示/警告顏色

**數字**
- 4（日文/中文裡代表死亡）、13、666 — 標記它們在 UI 裡的使用（房號、道具數量、價格）

**幽默與慣用語**
- 翻成其他 locale 會變成冒犯的慣用語
- 在某些市場不適當的廁所/身體幽默（特別是日本、德國、中東）
- 圍繞特定地區文化上敏感話題的黑色幽默

**暴力與內容分級**
- 會需要在 DE（德國）、AU（澳洲）、CN（中國）或 AE（阿聯）更改分級的內容
- 血的顏色、血腥程度、毒品參照 — 全部標記，必要時做區域專用的資產版本

**名稱與呈現方式**
- 在目標 locale 中冒犯、粗俗或帶有負面意義的角色名稱
- 對國籍、宗教或族群的刻板印象呈現

用表格呈現發現：

| Finding | Locale(s) Affected | Severity | Recommended Action |
|---------|--------------------|----------|--------------------|
| [Description] | [Locale] | [BLOCKING / ADVISORY / NOTE] | [Change / Flag for review / Accept] |

BLOCKING = 該 locale 上線前必須修。ADVISORY = 建議修改。NOTE = 僅供參考。

問：「May I write this cultural review report to `production/localization/cultural-review-[date].md`?」

---

## Phase 2G: VO Pipeline Mode

管理配音在地化流程。從參數判斷子任務：

- `vo-pipeline scan` — 找出所有需要配音錄製的對話行
- `vo-pipeline script` — 產生附導演筆記的錄音腳本
- `vo-pipeline validate` — 檢查所有錄好的配音檔都在，而且命名正確
- `vo-pipeline integrate` — 驗證配音檔在程式碼/資產裡有被正確參照

### VO Pipeline: Scan

讀 `assets/data/strings/` 和 `design/narrative/`。找出：
- 所有對話行（key 符合 `dialogue.*`）和來源文字
- 已經錄好的行（`assets/audio/vo/` 裡有音檔）
- 還沒錄的行

輸出錄音清單：

```
## VO Recording Manifest — [Date]

| Key | Character | Source Line | Status |
|-----|-----------|-------------|--------|
| dialogue.npc.merchant.greeting | Merchant | "Welcome, traveller." | Recorded |
| dialogue.npc.merchant.haggle | Merchant | "That's my final offer." | Needs recording |
```

### VO Pipeline: Script

為每個角色產生錄音腳本文件，依 scene 分組。包含：

- 角色名稱和簡短的個性註記
- 完整的對話行，罕見專有名詞附發音指南
- 每一行的情緒/導演註記（`[Warm, welcoming]`、`[Annoyed, clipped]`）
- 任何屬於對話回應的行（提供脈絡：「Player just said X」）

問：「May I write the VO recording scripts to `production/localization/vo-scripts-[locale]-[date].md`?」

### VO Pipeline: Validate

用 Glob 找 `assets/audio/vo/[locale]/` 底下所有 `.wav`/`.ogg` 檔。跟錄音清單交叉比對。回報：
- 缺少的檔案（腳本有那一行，但沒有音檔）
- 多出的檔案（音檔存在，但沒有對應的字串 key）
- 違反命名慣例的檔案

### VO Pipeline: Integrate

用 Grep 在 code root 找配音音檔的參照。驗證每個被參照的路徑都存在於 `assets/audio/vo/[locale]/`。回報壞掉的參照。

---

## Phase 2H: RTL Check Mode

由右到左的語言（阿拉伯文、希伯來文、波斯文、烏爾都文）除了翻譯文字之外，還需要版面鏡像。
這個模式驗證實作。

判斷 engine：從 `project.yaml` 讀 `engine.name`；如果這個 key 不存在或是空的（包括 `project.yaml` 沒有 `engine:` 區塊的情況），就退回讀 `.claude/docs/technical-preferences.md`。然後檢查：

**版面鏡像**
- engine 有啟用 RTL 版面嗎？（Godot：`Control.layout_direction`，Unity：`RTL Support` package，Unreal：文字方向旗標）
- 所有 UI 容器都設成自動鏡像，還是位置寫死？
- 進度條、血條和方向指示有正確鏡像嗎？

**文字渲染**
- 有載入支援阿拉伯文/希伯來文字元集的字型嗎？
- 阿拉伯文有用正確的連字（連寫字體）渲染嗎？
- 需要的話，數字有顯示成東阿拉伯數字嗎？

**字串組裝**
- 有沒有任何字串串接假設是由左到右的閱讀順序？
- 句子結構反過來之後，句子裡的 `{placeholder}` 位置還能正常運作嗎？

**資產檢視**
- 有沒有帶方向箭頭或非對稱設計、需要鏡像版本的 UI 圖示？
- 有沒有任何圖片內嵌文字的資產，需要 RTL 版本？

要檢查的 Grep pattern：
- scene/prefab 檔裡 engine 專屬的 RTL 旗標
- 任何 `HBoxContainer`、`LinearLayout`、`HorizontalBox` 節點 — 驗證 layout_direction 設定
- 對話或 UI 程式碼附近用 `+` 做的字串串接

回報發現。標出 BLOCKING 的問題（不修就無法閱讀的內容）和 ADVISORY 的問題（外觀改善）。

問：「May I write this RTL check report to `production/localization/rtl-check-[date].md`?」

---

## Phase 2I: Freeze Mode

String freeze 會鎖住來源（英文）字串表，讓翻譯可以進行，
不會有來源在譯者腳下一直變動。

### freeze call

檢查 `production/localization/freeze-status.md` 裡目前的 freeze 狀態（如果它存在的話）。

如果已經 frozen：
> "String freeze is currently ACTIVE (called [date]). [N] strings have been added or modified since freeze. These are freeze violations — they require re-translation or an approved freeze lift."

如果還沒 frozen，呈現 freeze 前的 checklist：

```
Pre-Freeze Checklist
[ ] All planned UI screens are implemented
[ ] All dialogue lines are final (no further narrative revisions planned)
[ ] All system strings (error messages, tutorial text) are complete
[ ] /localize scan shows zero hardcoded strings
[ ] /localize validate shows no placeholder mismatches in source (en)
[ ] Marketing strings (store description, achievements) are final
```

使用 `AskUserQuestion`：
- Prompt: "Call string freeze now? This writes `production/localization/freeze-status.md` (Status: ACTIVE) and locks the source table."
- Options: `[A] Yes — call string freeze now` / `[B] No — I still have strings to add`

選 [A]：寫 `production/localization/freeze-status.md`：

```markdown
# String Freeze Status

**Status**: ACTIVE
**Called**: [date]
**Called by**: [user]
**Total strings at freeze**: [N]

## Post-Freeze Changes
[Any strings added or modified after freeze are listed here automatically by /localize extract]
```

### freeze lift

如果參數包含 `lift`：問「May I update `freeze-status.md` to LIFTED?」，然後把它的 Status 設成 `LIFTED`，並記錄原因和日期。警告：「Lifting the freeze requires re-translation of all modified strings. Notify the translation team.」

### freeze check (auto-integrated into extract)

當 `extract` 模式發現新增或修改的字串，而且 `freeze-status.md` 顯示 Status: ACTIVE — 要在 extract 自己的「May I write」問題裡點名 `freeze-status.md`，核准後把新的 key 附加到它的 `## Post-Freeze Changes`，並警告：
> "⚠️ String freeze is active. [N] new/modified strings have been added. These are freeze violations. Notify your localization vendor before proceeding."

---

## Phase 2J: QA Mode

在地化 QA 是專門的一輪檢查，在翻譯交付之後、
任何 locale 上線之前進行。它跟 `/localize validate` 不一樣（那個檢查
完整度）— 這是以實際遊玩為基礎的結構化品質檢查。

用 `Agent` 派出 `localization-lead`，帶上：
- 要做 QA 的目標 locale
- 遊戲裡所有畫面/流程的清單（來自 `design/gdd/` 或 `/content-audit` 的輸出）
- 目前的 `/localize validate` 報告
- 文化審查報告（如果有的話）

請 localization-lead 產出涵蓋下列項目的 QA 計畫：

1. **Functional string check** — 每個字串在遊戲裡顯示時都沒有被截斷、沒有 placeholder 錯誤、沒有編碼損毀
2. **UI overflow check** — 翻譯後超出 UI 範圍的字串（就算在字元上限內，有些語言還是會變長）
3. **Contextual accuracy** — 在遊戲裡抽查 10% 的字串，檢查翻譯準確度和用語自然程度
4. **Cultural review items** — 驗證文化審查裡所有 BLOCKING 項目都已解決
5. **VO sync check** — 如果有配音，驗證翻譯後的對嘴或字幕時間是可接受的
6. **Platform cert requirements** — 檢查平台專屬的在地化需求（年齡分級文字、法律聲明、ESRB/PEGI/CERO 文字）

為每個 locale 輸出 QA 判定：

```
## Localization QA Verdict — [Locale]

**Status**: PASS / PASS WITH CONDITIONS / NOT ASSESSED / FAIL
**Reviewed by**: localization-lead
**Date**: [date]

### Findings
| ID | Area | Description | Severity | Status |
|----|------|-------------|----------|--------|
| LOC-001 | UI Overflow | "Settings" button text overflows on [Screen] | BLOCKING | Open |
| LOC-002 | Translation | [Key] translation is literal — sounds unnatural | ADVISORY | Open |

### Conditions (if PASS WITH CONDITIONS)
- [Condition 1 — must resolve before ship]

### Sign-Off
[ ] All BLOCKING findings resolved
[ ] Producer approves shipping [Locale]
```

第一個符合的條件勝出：只要有任何 BLOCKING 發現還開著，就是 **FAIL**；否則，如果有檢查
沒辦法執行就是 **NOT ASSESSED** — 這些檢查是以實際遊玩為基礎的，所以一個沒人
在遊戲裡玩過的 locale（或翻譯沒有交付的），光靠字串表是不能通過的；
要點名每一個沒執行的檢查；否則，如果還有條件沒解決，就是 **PASS WITH
CONDITIONS**；否則是 **PASS**。NOT ASSESSED 的優先順序高於兩種
通過 — 沒玩過的 locale 就是沒通過 — 而低於 FAIL，所以
開著的 BLOCKING 發現永遠不會被它蓋住。

問：「May I write this localization QA report to `production/localization/loc-qa-[locale]-[date].md`?」

**Gate 整合**：在 `workflow: full`，Polish → Release gate 要求每個要上線的翻譯 locale 都有 PASS 或 PASS WITH CONDITIONS 的判定（`standard` 是建議；`minimal` 則取消）。FAIL 只會擋住那個 locale 的 release — 其他 locale 的 QA 如果通過，仍然可以繼續。NOT ASSESSED 的 locale 就是沒通過：它的 QA 根本沒跑。

---

## Phase 3: Rules and Next Steps

### Rules
- 英文（en）永遠是來源 locale
- 每個字串表條目都必須有 `context` 欄位，附上譯者註解、字元上限和 placeholder 意義
- 絕對不要直接修改翻譯檔 — 產生 diff 供審查
- 字元上限必須逐個 UI 元素定義，並在 validate 模式裡強制執行
- 把字串送給譯者之前，一定要先呼叫 string freeze — 絕對不要翻譯一個一直在動的目標
- RTL 支援必須從一開始就設計進去 — 事後補 RTL 版面很貴
- 任何要商業販售的 locale 都必須做文化審查
- 配音腳本必須附導演筆記 — 光有原始對話行會錄出平淡的聲音

### Recommended Workflow

```
/localize scan            → find hardcoded strings
/localize extract         → build string table
/localize freeze          → lock source before sending to translators
/localize brief           → generate translator briefing document
[Send to translators]
/localize validate        → check returned translations
/localize cultural-review → flag culturally sensitive content
/localize rtl-check       → if shipping Arabic / Hebrew / Persian
/localize vo-pipeline     → if shipping dubbed VO
/localize qa              → full localization QA pass
```

等 `qa` 對你要上線的每個翻譯 locale 都回傳 PASS 或 PASS WITH CONDITIONS 之後，執行 `/gate-check release` 時要附上 QA 報告的路徑。
