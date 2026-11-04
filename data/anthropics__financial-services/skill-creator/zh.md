---
name: skill-creator
description: 建立有效 skill 的指南。當使用者想建立新 skill（或更新現有 skill），為 Claude 的能力加上專門知識、工作流程或工具整合時，應該使用這個 skill。
license: Complete terms in LICENSE.txt
---

# Skill Creator

這個 skill 提供建立有效 skill 的指引。

## 關於 Skill

Skill 是模組化、自給自足的套件，透過提供專門知識、工作流程和工具來擴充 Claude 的能力。
可以把它們想成特定領域或任務的「新人上手指南」，它們把 Claude 從通用型 agent
變成具備程序性知識的專門 agent，而這種知識是任何模型都無法完整擁有的。

### Skill 能提供什麼

1. 專門的工作流程：針對特定領域的多步驟程序
2. 工具整合：說明如何處理特定檔案格式或 API
3. 領域專業知識：公司專屬的知識、schema、商業邏輯
4. 附帶資源：用於複雜、重複任務的 script、參考資料和素材

## 核心原則

### 簡潔是關鍵

Context window 是公共財。Skill 要跟 Claude 需要的所有其他東西共用 context window：system prompt、對話歷史、其他 Skill 的 metadata，還有使用者實際的請求。

**預設假設：Claude 已經很聰明。** 只加入 Claude 還沒有的 context。對每一則資訊都要質疑："Claude 真的需要這段說明嗎？" 還有 "這一段值得花這些 token 嗎？"

簡潔的範例優於冗長的說明。

### 設定適當的自由度

讓具體程度配合任務的脆弱度和變化程度：

**高自由度（文字說明）**：用在有多種做法都可行、決策取決於 context，或由經驗法則引導做法的時候。

**中自由度（偽代碼或帶參數的 script）**：用在有偏好的模式、允許某些變化，或設定會影響行為的時候。

**低自由度（特定 script、少量參數）**：用在操作脆弱又容易出錯、一致性很關鍵，或必須照特定順序執行的時候。

把 Claude 想成在探索一條路：兩側是懸崖的窄橋需要明確的護欄（低自由度），空曠的原野則允許走很多路線（高自由度）。

### Skill 的結構

每個 skill 都有一個必要的 SKILL.md 檔，以及選用的附帶資源：

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md（必要）

每個 SKILL.md 包含：

- **Frontmatter**（YAML）：包含 `name` 和 `description` 欄位。Claude 只會讀這兩個欄位來判斷什麼時候使用這個 skill，所以要把這個 skill 是什麼、什麼時候該用，描述得清楚又完整，這點非常重要。
- **本文**（Markdown）：使用這個 skill 的說明與指引。只有在 skill 觸發「之後」才會載入（如果有載入的話）。

#### 附帶資源（選用）

##### Script（`scripts/`）

需要確定性可靠度、或經常被重寫的任務所用的可執行程式碼（Python/Bash 等）。

- **什麼時候該放**：同一段程式碼一再被重寫，或需要確定性的可靠度時
- **範例**：處理 PDF 旋轉任務的 `scripts/rotate_pdf.py`
- **好處**：省 token、結果確定，而且可以不載入 context 就直接執行
- **注意**：Claude 可能還是需要讀 script，以便修補或做環境專屬的調整

##### 參考資料（`references/`）

需要時才載入 context 的文件和參考資料，用來輔助 Claude 的流程和思考。

- **什麼時候該放**：Claude 工作時應該參考的文件
- **範例**：財務 schema 用 `references/finance.md`、公司 NDA 範本用 `references/mnda.md`、公司政策用 `references/policies.md`、API 規格用 `references/api_docs.md`
- **使用情境**：資料庫 schema、API 文件、領域知識、公司政策、詳細的工作流程指南
- **好處**：讓 SKILL.md 保持精簡，只在 Claude 判斷需要時才載入
- **最佳實務**：如果檔案很大（>10k 字），在 SKILL.md 裡附上 grep 搜尋模式
- **避免重複**：資訊應該放在 SKILL.md 或參考檔其中之一，不要兩邊都放。除非真的是 skill 的核心，否則詳細資訊優先放參考檔，這樣 SKILL.md 保持精簡，資訊也找得到，又不會佔用 context window。SKILL.md 只留必要的程序指示和工作流程指引，詳細的參考資料、schema 和範例移到參考檔。

##### 素材（`assets/`）

不打算載入 context，而是用在 Claude 產出成果裡的檔案。

- **什麼時候該放**：skill 需要在最終成果中使用某些檔案時
- **範例**：品牌素材用 `assets/logo.png`、PowerPoint 範本用 `assets/slides.pptx`、HTML/React 樣板用 `assets/frontend-template/`、字型用 `assets/font.ttf`
- **使用情境**：範本、圖片、圖示、樣板程式碼、字型、會被複製或修改的範例文件
- **好處**：把輸出資源和文件分開，讓 Claude 不用載入 context 就能使用這些檔案

#### Skill 裡不該放什麼

Skill 只該包含直接支援其功能的必要檔案。「不要」建立多餘的文件或輔助檔案，包括：

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- 等等

Skill 只該放 AI agent 完成手上工作所需的資訊。不該包含建立它的過程、安裝與測試程序、給使用者看的文件這類輔助脈絡。多建文件只會增加雜亂和混淆。

### 漸進式揭露的設計原則

Skill 用三層載入機制來有效管理 context：

1. **Metadata（name + description）**：永遠在 context 裡（約 100 字）
2. **SKILL.md 本文**：skill 觸發時才載入（<5k 字）
3. **附帶資源**：Claude 需要時才載入（無上限，因為 script 可以不讀進 context window 就執行）

#### 漸進式揭露的模式

SKILL.md 本文只放重點，並控制在 500 行以內，減少 context 膨脹。接近這個上限時就把內容拆成獨立檔案。拆出去之後，一定要在 SKILL.md 裡參照它們，並清楚說明什麼時候該讀，這樣讀 skill 的人才知道它們存在、什麼時候該用。

**關鍵原則：** 當 skill 支援多種變體、框架或選項時，SKILL.md 只留核心工作流程和選擇指引。變體專屬的細節（模式、範例、設定）移到獨立的參考檔。

**模式 1：高階指南加參考檔**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Claude 只在需要時才載入 FORMS.md、REFERENCE.md 或 EXAMPLES.md。

**模式 2：依領域組織**

對於有多個領域的 Skill，依領域組織內容，避免載入不相關的 context：

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

使用者問到銷售指標時，Claude 只會讀 sales.md。

同樣地，對於支援多個框架或變體的 skill，依變體組織：

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

使用者選擇 AWS 時，Claude 只會讀 aws.md。

**模式 3：條件式細節**

先呈現基本內容，再連結到進階內容：

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Claude 只在使用者需要那些功能時，才會讀 REDLINING.md 或 OOXML.md。

**重要準則：**

- **避免多層巢狀的參照**：參照要從 SKILL.md 起算只深一層。所有參考檔都應該直接從 SKILL.md 連結。
- **替較長的參考檔加目錄**：超過 100 行的檔案，在開頭放目錄，讓 Claude 預覽時能看到完整範圍。

## Skill 建立流程

建立 skill 包含這些步驟：

1. 用具體範例理解這個 skill
2. 規劃可重複使用的 skill 內容（script、參考資料、素材）
3. 初始化 skill（執行 init_skill.py）
4. 編輯 skill（實作資源並撰寫 SKILL.md）
5. 打包 skill（執行 package_skill.py）
6. 依實際使用狀況迭代

照順序做這些步驟，只有在有明確理由說明不適用時才能跳過。

### 步驟 1：用具體範例理解 Skill

只有在 skill 的使用模式已經很清楚時才跳過這一步。即使是處理現有的 skill，這一步仍然有價值。

要建立有效的 skill，得清楚理解這個 skill 會怎麼被使用的具體範例。這種理解可以來自使用者直接給的範例，或是產生出來、並經使用者回饋驗證過的範例。

舉例來說，建立 image-editor skill 時，相關的問題包括：

- "image-editor skill 要支援什麼功能？編輯、旋轉，還有別的嗎？"
- "可以舉幾個這個 skill 會怎麼被使用的例子嗎？"
- "我想得到使用者可能會說『幫我去除這張圖的紅眼』或『旋轉這張圖』。你還想到其他使用方式嗎？"
- "使用者說什麼話應該觸發這個 skill？"

為了避免讓使用者應接不暇，不要在一則訊息裡問太多問題。先從最重要的問題開始，需要時再追問，效果會比較好。

當你清楚這個 skill 該支援什麼功能時，就結束這一步。

### 步驟 2：規劃可重複使用的 Skill 內容

要把具體範例變成有效的 skill，對每個範例這樣分析：

1. 想想怎麼從零開始執行這個範例
2. 找出重複執行這些工作流程時，哪些 script、參考資料和素材會有幫助

範例：建立 `pdf-editor` skill 來處理 "幫我旋轉這個 PDF" 這類請求時，分析結果是：

1. 旋轉 PDF 每次都得重寫同樣的程式碼
2. 在 skill 裡存一個 `scripts/rotate_pdf.py` script 會很有幫助

範例：設計 `frontend-webapp-builder` skill 來處理 "幫我做一個 todo app" 或 "幫我做一個追蹤步數的儀表板" 這類請求時，分析結果是：

1. 寫前端 webapp 每次都需要同樣的 HTML/React 樣板
2. 在 skill 裡存一個含樣板 HTML/React 專案檔的 `assets/hello-world/` 範本會很有幫助

範例：建立 `big-query` skill 來處理 "今天有多少使用者登入？" 這類請求時，分析結果是：

1. 查詢 BigQuery 每次都得重新摸索資料表 schema 和關聯
2. 在 skill 裡存一份記錄資料表 schema 的 `references/schema.md` 檔會很有幫助

要決定 skill 的內容，就分析每個具體範例，整理出要放進去的可重複使用資源清單：script、參考資料和素材。

### 步驟 3：初始化 Skill

到這一步，就是要真的建立 skill 了。

只有在要開發的 skill 已經存在、只需要迭代或打包時，才跳過這一步。這種情況就直接進入下一步。

從零開始建立新 skill 時，一律要執行 `init_skill.py` script。這個 script 會方便地產生新的範本 skill 目錄，自動包含 skill 需要的一切，讓建立 skill 的流程更有效率也更可靠。

用法：

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

這個 script 會：

- 在指定路徑建立 skill 目錄
- 產生帶有正確 frontmatter 和 TODO 佔位符的 SKILL.md 範本
- 建立範例資源目錄：`scripts/`、`references/` 和 `assets/`
- 在每個目錄加入可以自訂或刪除的範例檔

初始化之後，依需要自訂或移除產生的 SKILL.md 和範例檔。

### 步驟 4：編輯 Skill

編輯（新產生的或現有的）skill 時，記得這個 skill 是為了另一個 Claude 實例而建立的。放進對 Claude 有幫助、而且不顯而易見的資訊。想想哪些程序性知識、領域專屬細節或可重複使用的素材，能幫另一個 Claude 實例更有效地執行這些任務。

#### 學習已驗證的設計模式

依 skill 的需求參考這些指南：

- **多步驟流程**：順序式工作流程和條件邏輯，見 references/workflows.md
- **特定輸出格式或品質標準**：範本和範例模式，見 references/output-patterns.md

這些檔案包含有效 skill 設計的既定最佳實務。

#### 從可重複使用的 Skill 內容開始

開始實作時，先從前面找出來的可重複使用資源下手：`scripts/`、`references/` 和 `assets/` 檔案。注意這一步可能需要使用者提供輸入。例如實作 `brand-guidelines` skill 時，使用者可能需要提供品牌素材或範本放進 `assets/`，或提供文件放進 `references/`。

加入的 script 一定要實際跑過測試，確保沒有 bug、輸出符合預期。如果有很多類似的 script，只需要測試具代表性的樣本，就能確信它們都能運作，同時兼顧完成時間。

所有 skill 用不到的範例檔案和目錄都應該刪除。初始化 script 會在 `scripts/`、`references/` 和 `assets/` 裡建立範例檔來示範結構，但大部分 skill 不會全都用到。

#### 更新 SKILL.md

**撰寫準則：** 一律使用祈使句／不定詞形式。

##### Frontmatter

撰寫含 `name` 和 `description` 的 YAML frontmatter：

- `name`：skill 名稱
- `description`：這是 skill 主要的觸發機制，幫助 Claude 理解什麼時候該用這個 skill。
  - 要同時寫出這個 Skill 做什麼，以及什麼時候該用的具體觸發條件／情境。
  - 所有「什麼時候用」的資訊都放在這裡，不要放本文。本文只在觸發之後才載入，所以本文裡的「When to Use This Skill」段落對 Claude 沒有幫助。
  - `docx` skill 的 description 範例："Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"

YAML frontmatter 不要放任何其他欄位。

##### 本文

撰寫使用這個 skill 及其附帶資源的說明。

### 步驟 5：打包 Skill

skill 開發完成後，必須打包成可散布的 .skill 檔，再分享給使用者。打包流程會先自動驗證 skill，確保符合所有要求：

```bash
scripts/package_skill.py <path/to/skill-folder>
```

可選的輸出目錄指定：

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

打包 script 會：

1. 自動**驗證** skill，檢查：

   - YAML frontmatter 格式和必要欄位
   - Skill 命名慣例和目錄結構
   - Description 的完整度和品質
   - 檔案組織和資源參照

2. 驗證通過就**打包**，建立以 skill 命名的 .skill 檔（例如 `my-skill.skill`），包含所有檔案並維持散布所需的正確目錄結構。.skill 檔就是副檔名為 .skill 的 zip 檔。

如果驗證失敗，script 會回報錯誤並結束，不會建立套件。修好驗證錯誤後，再執行一次打包指令。

### 步驟 6：迭代

測試 skill 之後，使用者可能會要求改進。這通常發生在剛用完 skill、對 skill 表現還記憶猶新的時候。

**迭代工作流程：**

1. 在真實任務上使用這個 skill
2. 注意哪裡卡住或沒效率
3. 找出 SKILL.md 或附帶資源該怎麼更新
4. 實作修改並再次測試
