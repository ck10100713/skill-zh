---
layout: "default"
skill: "skill-creator"
author: "Anthropic"
category: "設定與維護"
summary: "寫 skill、跑 eval 對比、迭代改進並最佳化觸發描述"
source: "https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md"
license: "Apache-2.0"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: skill-creator
description: 建立新的 skill、修改並改進既有的 skill，以及衡量 skill 的表現。當使用者想從零建立 skill、編輯或最佳化既有的 skill、跑 eval 來測試 skill、用變異分析對 skill 的表現做 benchmark，或最佳化 skill 的 description 以提高觸發準確度時使用。
---

# Skill Creator

一個用來建立新 skill 並反覆改進它們的 skill。

大方向來說，建立 skill 的流程是這樣：

- 決定你想讓這個 skill 做什麼，以及大致上該怎麼做
- 寫一份 skill 的草稿
- 建立幾個測試 prompt，用能使用這個 skill 的 claude 去跑它們
- 協助使用者從定性和定量兩方面評估結果
  - 在背景執行的同時，如果還沒有定量 eval，就先草擬一些（如果已經有了，可以直接用，或是覺得有地方需要改就修改）。然後向使用者說明它們（如果本來就有，就說明現有的那些）
  - 用 `eval-viewer/generate_review.py` 這支 script 把結果秀給使用者看，也讓他們看定量指標
- 根據使用者評估結果後的回饋重寫 skill（如果定量 benchmark 顯示出明顯的缺陷，也要改）
- 重複，直到你滿意為止
- 擴大測試集，用更大的規模再試一次

你使用這個 skill 時的工作，是弄清楚使用者現在在這個流程的哪個位置，然後跳進去幫他們往下個階段前進。舉例來說，也許他們一開始是說「我想做一個 X 的 skill」。你可以幫忙釐清他們的意思、寫草稿、寫測試案例、搞清楚他們想怎麼評估、跑所有的 prompt，然後重複。

另一方面，也許他們已經有 skill 的草稿了。這種情況下你可以直接跳到這個迴圈的 eval／迭代部分。

當然，你要隨時保持彈性，如果使用者說「我不需要跑一堆評估，跟我一起憑感覺做就好」，你可以改那樣做。

然後 skill 做完之後（不過再說一次，順序是有彈性的），你也可以跑 skill description 改進工具，我們有一支專門的 script，用來最佳化 skill 的觸發。

懂了嗎？懂了。

## 與使用者溝通

使用 skill creator 的人，對程式術語的熟悉程度差異很大。如果你還沒聽說（你怎麼可能聽說，這是最近才開始的），現在有一股趨勢：Claude 的威力啟發水電工打開終端機，讓爸媽和祖父母去 google「how to install npm」。不過另一方面，大部分使用者大概都相當懂電腦。

所以請注意語境線索，來判斷該怎麼措辭！預設情況下，只是給你一點概念：

- 「evaluation」和「benchmark」是邊緣，但可以
- 「JSON」和「assertion」要看到使用者有明顯的跡象表示他們知道這些是什麼，才能不加解釋就直接用

如果有疑慮，簡短解釋一下術語是可以的，不確定使用者會不會懂時，也請放心用簡短的定義來釐清術語。

---

## 建立 skill

### 抓出意圖

先從理解使用者的意圖開始。目前的對話裡可能已經有使用者想保存的工作流程（例如他們說「把這個變成 skill」）。如果是這樣，先從對話紀錄裡擷取答案：用到的工具、步驟的順序、使用者做過的修正、觀察到的輸入／輸出格式。使用者可能需要補上缺口，而且在進入下一步之前應該要確認。

1. 這個 skill 應該讓 Claude 能做什麼？
2. 這個 skill 應該在什麼時候觸發？（什麼樣的使用者說法／情境）
3. 預期的輸出格式是什麼？
4. 要不要建立測試案例來驗證這個 skill 有效？輸出可以客觀驗證的 skill（檔案轉換、資料擷取、程式碼產生、固定的工作流程步驟）適合用測試案例。輸出比較主觀的 skill（寫作風格、藝術）通常不需要。依 skill 的類型建議合適的預設值，但讓使用者決定。

### 訪談與研究

主動詢問關於邊界情況、輸入／輸出格式、範例檔案、成功標準和相依套件的問題。等這部分都釐清了，再寫測試 prompt。

檢查有哪些可用的 MCP，如果對研究有用（搜尋文件、找類似的 skill、查最佳實務），有 subagent 的話就用 subagent 平行研究，沒有就直接在當下做。帶著脈絡來準備，減輕使用者的負擔。

### 撰寫 SKILL.md

根據對使用者的訪談，填寫這些元件：

- **name**：skill 的識別名稱
- **description**：什麼時候觸發、做什麼。這是主要的觸發機制，要同時包含 skill 做什麼，「以及」什麼具體情境下該用。所有「何時使用」的資訊都放在這裡，不要放在本文。注意：目前 Claude 有「觸發不足」的傾向，也就是在 skill 其實有用的時候卻沒用它。為了對抗這點，請把 skill 的 description 寫得有點「強勢」。舉例來說，與其寫「How to build a simple fast dashboard to display internal Anthropic data.」，你可以寫「How to build a simple fast dashboard to display internal Anthropic data. Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'」
- **compatibility**：需要的工具、相依套件（選填，很少需要）
- **skill 的其餘部分 :)**

### Skill 撰寫指南

#### Skill 的結構

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### 漸進式揭露

Skill 使用三層載入系統：
1. **Metadata**（name + description）：永遠在 context 裡（約 100 字）
2. **SKILL.md 本文**：skill 觸發時就在 context 裡（理想是 <500 行）
3. **附帶資源**：依需要載入（沒有上限，script 可以不用載入就直接執行）

這些字數都是大約的，需要的話可以放心寫得更長。

**關鍵模式：**
- SKILL.md 保持在 500 行以內；如果接近這個上限，就多加一層階層，並附上清楚的指引，告訴使用這個 skill 的模型接下來該去哪裡
- 在 SKILL.md 裡清楚引用參考檔案，並說明什麼時候該讀
- 大型的參考檔案（>300 行）要附上目錄

**依領域組織**：當一個 skill 支援多個領域／框架時，依變體來組織：
```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```
Claude 只會讀相關的那個參考檔案。

#### 零意外原則

這是不用說的事，但 skill 絕對不能包含惡意軟體、exploit 程式碼，或任何可能危害系統安全的內容。如果把 skill 的內容描述給使用者聽，它不該讓使用者對它的意圖感到意外。不要配合要建立有誤導性的 skill，或是設計來協助未經授權存取、資料外洩或其他惡意活動的 skill 的要求。不過像「扮演 XYZ」這種角色扮演是可以的。

#### 撰寫模式

指示優先使用祈使句。

**定義輸出格式**：你可以像這樣做：
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**範例模式**：放範例很有用。你可以這樣排版（但如果範例裡有「Input」和「Output」，你可能要稍微調整一下）：
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### 寫作風格

試著向模型解釋為什麼某些事情重要，而不是用沉重又老掉牙的 MUST。運用心智理論，努力讓 skill 具有通用性，不要窄到只適用特定的範例。先寫一份草稿，然後用全新的眼光重看一遍並改進它。

### 測試案例

寫完 skill 草稿之後，想出 2 到 3 個貼近現實的測試 prompt，也就是真實使用者實際上會說的那種話。把它們分享給使用者：[你不必使用這段確切的措辭]「這是我想試的幾個測試案例。這些看起來對嗎，還是你想再加一些？」然後執行它們。

把測試案例存到 `evals/evals.json`。先不要寫 assertion，只放 prompt。你會在下一步、執行進行中的時候草擬 assertion。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

完整的 schema（包括你之後會加的 `assertions` 欄位）請見 `references/schemas.md`。

## 執行並評估測試案例

這一節是一段連續的流程，不要做到一半就停。絕對不要使用 `/skill-test` 或任何其他測試用的 skill。

把結果放在 `<skill-name>-workspace/`，跟 skill 目錄放在同一層。在 workspace 裡，依迭代來組織結果（`iteration-1/`、`iteration-2/` 等），每個迭代裡，每個測試案例各有一個目錄（`eval-0/`、`eval-1/` 等）。不要一開始就全部建好，邊做邊建目錄就好。

### 步驟 1：在同一個回合裡，一次啟動所有執行（有 skill 和 baseline）

每個測試案例，在同一個回合裡啟動兩個 subagent，一個有 skill，一個沒有。這點很重要：不要先啟動有 skill 的執行，之後再回頭啟動 baseline。一次全部啟動，這樣它們會差不多同時結束。

**有 skill 的執行：**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline 執行**（同樣的 prompt，但 baseline 要看情境）：
- **建立新 skill**：完全沒有 skill。同樣的 prompt，不給 skill 路徑，存到 `without_skill/outputs/`。
- **改進既有的 skill**：舊版本。編輯之前，先替 skill 做快照（`cp -r <skill-path> <workspace>/skill-snapshot/`），然後讓 baseline 的 subagent 指向那份快照。存到 `old_skill/outputs/`。

替每個測試案例寫一份 `eval_metadata.json`（assertion 現在可以先留空）。根據它在測試什麼，給每個 eval 一個有描述性的名字，不要只叫「eval-0」。目錄也用這個名字。如果這個迭代用了新的或修改過的 eval prompt，要替每個新的 eval 目錄建立這些檔案，不要假設它們會從上一個迭代延續過來。

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### 步驟 2：執行進行中時，草擬 assertion

不要只是等執行結束，你可以好好利用這段時間。替每個測試案例草擬定量的 assertion，並向使用者說明。如果 `evals/evals.json` 裡已經有 assertion，就檢視它們並說明它們檢查什麼。

好的 assertion 是可以客觀驗證的，而且有描述性的名稱，在 benchmark viewer 裡要讀起來很清楚，讓瞄一眼結果的人馬上看得懂每一條在檢查什麼。主觀的 skill（寫作風格、設計品質）比較適合用定性方式評估，不要硬把 assertion 套在需要人類判斷的東西上。

草擬完 assertion 之後，更新 `eval_metadata.json` 檔案和 `evals/evals.json`。也要向使用者說明他們會在 viewer 裡看到什麼，包括定性的輸出和定量的 benchmark。

### 步驟 3：執行完成時，記錄計時資料

每個 subagent 任務完成時，你會收到一則包含 `total_tokens` 和 `duration_ms` 的通知。立刻把這份資料存到那個執行目錄裡的 `timing.json`：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

這是唯一能記錄這份資料的機會，它是透過任務通知傳來的，其他地方不會保存。通知一來就處理，不要想等累積起來再一起處理。

### 步驟 4：評分、彙整，並啟動 viewer

所有執行都完成之後：

1. **替每次執行評分**：啟動一個 grader subagent（或直接在當下評分），讓它讀 `agents/grader.md`，並對照輸出評估每條 assertion。把結果存到每個執行目錄裡的 `grading.json`。grading.json 的 expectations 陣列必須使用 `text`、`passed` 和 `evidence` 這些欄位（不要用 `name`/`met`/`details` 或其他變體），viewer 依賴這些確切的欄位名稱。可以用程式檢查的 assertion，就寫一支 script 來跑，不要用肉眼判斷，script 更快、更可靠，而且可以在各個迭代間重複使用。

2. **彙整成 benchmark**：從 skill-creator 目錄執行彙整 script：
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   這會產生 `benchmark.json` 和 `benchmark.md`，裡面有每個配置的 pass_rate、時間和 token，附上平均值 ± 標準差和差異（delta）。如果是手動產生 benchmark.json，viewer 預期的確切 schema 請見 `references/schemas.md`。
把每個有 skill 的版本放在它對應的 baseline 前面。

3. **做一輪分析**：讀 benchmark 資料，找出彙總統計可能藏起來的模式。要找什麼請見 `agents/analyzer.md`（「Analyzing Benchmark Results」一節），像是不管有沒有 skill 都一定會通過的 assertion（沒有鑑別力）、變異很大的 eval（可能不穩定），以及時間／token 的取捨。

4. **啟動 viewer**，同時呈現定性的輸出和定量的資料：
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   第 2 個迭代以後，還要加上 `--previous-workspace <workspace>/iteration-<N-1>`。

   **Cowork／headless 環境：** 如果沒有 `webbrowser.open()` 可用，或環境沒有顯示器，就改用 `--static <output_path>` 寫出一個獨立的 HTML 檔，而不是啟動 server。使用者點「Submit All Reviews」時，回饋會以 `feedback.json` 檔下載。下載後，把 `feedback.json` 複製到 workspace 目錄，讓下一個迭代去讀取。

注意：請用 generate_review.py 來建立 viewer，不需要自己寫客製的 HTML。
5. **告訴使用者**類似這樣的話：「我已經在你的瀏覽器裡打開結果了。有兩個分頁：『Outputs』讓你逐一點過每個測試案例並留下回饋，『Benchmark』顯示定量的比較。看完之後回來這裡跟我說一聲。」

### 使用者在 viewer 裡看到什麼

「Outputs」分頁一次顯示一個測試案例：
- **Prompt**：給的任務
- **Output**：skill 產出的檔案，盡可能直接內嵌顯示
- **Previous Output**（第 2 個迭代以後）：收合的區塊，顯示上一個迭代的輸出
- **Formal Grades**（如果有跑評分）：收合的區塊，顯示 assertion 通過／失敗
- **Feedback**：一個文字框，打字時會自動儲存
- **Previous Feedback**（第 2 個迭代以後）：他們上次的意見，顯示在文字框下方

「Benchmark」分頁顯示統計摘要：每個配置的通過率、時間和 token 用量，附上每個 eval 的細項和分析者的觀察。

可以用上一個／下一個按鈕或方向鍵導覽。完成後，他們點「Submit All Reviews」，會把所有回饋存到 `feedback.json`。

### 步驟 5：讀取回饋

使用者告訴你他們看完了，就讀 `feedback.json`：

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

回饋是空的，代表使用者覺得沒問題。把改進的重點放在使用者有具體抱怨的測試案例上。

用完之後，把 viewer server 關掉：

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## 改進 skill

這是整個迴圈的核心。你已經跑過測試案例，使用者也檢視過結果了，現在你要根據他們的回饋把 skill 變得更好。

### 如何思考改進

1. **從回饋中歸納通則。** 這裡的大方向是：我們想建立的 skill，要能在許多不同的 prompt 上被使用一百萬次（也許是字面上的，也許更多，誰知道）。而你和使用者在這裡只拿幾個範例反覆迭代，因為這樣進展比較快。使用者對這些範例瞭若指掌，評估新的輸出很快。但如果你和使用者一起開發的 skill 只對那些範例有效，那就沒用。與其加入瑣碎、過度擬合的修改，或是壓迫性的限制性 MUST，如果有頑固的問題，不妨試著發散一下，用不同的比喻，或建議不同的工作模式。這樣嘗試的成本相對很低，說不定就會找到很棒的做法。

2. **保持 prompt 精簡。** 把沒發揮作用的東西移除。一定要讀 transcript，不能只看最後的輸出。如果看起來 skill 讓模型浪費了一堆時間在做沒有生產力的事，可以試著把 skill 裡讓它那樣做的部分拿掉，看看會怎樣。

3. **解釋原因。** 盡力解釋你要求模型做的每件事背後的**原因**。現在的 LLM 很*聰明*。它們有不錯的心智理論，在好的 harness 下，可以超越死板的指示，真正把事情做成。就算使用者的回饋很簡短或帶著挫折，也要試著真正理解任務、理解使用者為什麼那樣寫，以及他們實際寫了什麼，然後把這份理解傳達到指示裡。如果你發現自己在寫全大寫的 ALWAYS 或 NEVER，或是用超級死板的結構，那是個黃燈，可以的話，重新換個角度，解釋理由，讓模型明白你要求的事為什麼重要。這是更人性化、更有力、也更有效的做法。

4. **找出跨測試案例的重複工作。** 讀測試執行的 transcript，注意 subagent 是不是都各自獨立寫了類似的 helper script，或是對某件事採取了同樣的多步驟做法。如果 3 個測試案例都讓 subagent 寫了 `create_docx.py` 或 `build_chart.py`，那就是一個很強的訊號，表示 skill 應該把那支 script 打包進去。寫一次，放進 `scripts/`，然後告訴 skill 去用它。這樣能讓之後每一次呼叫都不用重新發明輪子。

這項任務相當重要（我們想一年創造數十億的經濟價值！），而你的思考時間不是瓶頸；慢慢來，好好琢磨。我建議先寫一份修訂草稿，然後用全新的眼光重看一遍並改進。真的盡力進入使用者的腦袋，理解他們想要和需要什麼。

### 迭代迴圈

改進 skill 之後：

1. 把你的改進套用到 skill 上
2. 把所有測試案例重跑到一個新的 `iteration-<N+1>/` 目錄裡，包括 baseline 的執行。如果你是在建立新 skill，baseline 一直都是 `without_skill`（沒有 skill），這在各個迭代間保持不變。如果你是在改進既有的 skill，用你的判斷來決定什麼適合當 baseline：使用者一開始帶來的原始版本，還是上一個迭代。
3. 啟動 reviewer，用 `--previous-workspace` 指向上一個迭代
4. 等使用者檢視完並告訴你他們看完了
5. 讀新的回饋，再次改進，重複

一直做到：
- 使用者說他們滿意了
- 回饋全部都是空的（一切看起來都很好）
- 你沒有再取得有意義的進展

---

## 進階：盲測比較

當你想要在兩個版本的 skill 之間做更嚴謹的比較時（例如使用者問「新版真的比較好嗎？」），有一套盲測比較系統。細節請讀 `agents/comparator.md` 和 `agents/analyzer.md`。基本概念是：把兩份輸出交給一個獨立的 agent，不告訴它哪個是哪個，讓它判斷品質。然後分析贏的那個為什麼贏。

這是選用的，需要 subagent，大部分使用者不會用到。人工檢視的迴圈通常就夠了。

---

## Description 最佳化

SKILL.md frontmatter 裡的 description 欄位，是決定 Claude 會不會呼叫某個 skill 的主要機制。建立或改進 skill 之後，主動提議要不要最佳化 description 來提高觸發準確度。

### 步驟 1：產生觸發 eval 的查詢

建立 20 個 eval 查詢，混合應該觸發和不該觸發的。存成 JSON：

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

這些查詢必須貼近現實，是 Claude Code 或 Claude.ai 使用者真的會打的東西。不是抽象的請求，而是具體、明確、細節夠多的請求。例如檔案路徑、使用者工作或處境的個人脈絡、欄位名稱和值、公司名稱、URL。加一點背景故事。有些可以是小寫、含縮寫或打錯字、或口語的說法。混合不同的長度，並把重點放在邊界情況，而不是做成一目了然的案例（使用者會有機會簽核這些）。

不好的：`"Format this data"`、`"Extract text from PDF"`、`"Create a chart"`

好的：`"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

**應該觸發**的查詢（8-10 個），要考慮涵蓋範圍。你要的是同一個意圖的不同說法，有些正式、有些口語。要包含使用者沒有明說 skill 名稱或檔案類型、但顯然需要它的情況。再放進一些不常見的使用情境，以及這個 skill 跟別的 skill 競爭、但應該勝出的情況。

**不該觸發**的查詢（8-10 個），最有價值的是差一點就會觸發的：跟 skill 有共同的關鍵字或概念，但實際上需要別的東西的查詢。想想相鄰的領域、用單純的關鍵字比對會觸發但其實不該觸發的模糊措辭，以及查詢碰到了 skill 能做的事、但處在另一個工具更合適的情境。

要避免的關鍵：不要讓不該觸發的查詢明顯無關。拿「寫一個 fibonacci 函式」當 PDF skill 的反向測試太簡單了，什麼都測不出來。反向案例應該真的棘手。

### 步驟 2：與使用者一起檢視

用 HTML 範本把 eval 集呈現給使用者檢視：

1. 從 `assets/eval_review.html` 讀取範本
2. 替換佔位符：
   - `__EVAL_DATA_PLACEHOLDER__` → eval 項目的 JSON 陣列（外面不要加引號，因為它是 JS 變數的賦值）
   - `__SKILL_NAME_PLACEHOLDER__` → skill 的名稱
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → skill 目前的 description
3. 寫到暫存檔（例如 `/tmp/eval_review_<skill-name>.html`）並打開：`open /tmp/eval_review_<skill-name>.html`
4. 使用者可以編輯查詢、切換 should-trigger、新增／移除項目，然後點「Export Eval Set」
5. 檔案會下載到 `~/Downloads/eval_set.json`，如果有多個（例如 `eval_set (1).json`），要去 Downloads 資料夾檢查最新的版本

這一步很重要，壞的 eval 查詢會導出壞的 description。

### 步驟 3：執行最佳化迴圈

告訴使用者：「這會花一點時間，我會在背景跑最佳化迴圈，並定期回來檢查。」

把 eval 集存到 workspace，然後在背景執行：

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

使用 system prompt 裡的 model ID（驅動目前這個 session 的那個），這樣觸發測試才會符合使用者實際體驗到的。

執行期間，定期 tail 輸出，向使用者更新目前跑到第幾個迭代、分數看起來如何。

這會自動處理完整的最佳化迴圈。它把 eval 集拆成 60% 訓練集和 40% 保留的測試集，評估目前的 description（每個查詢跑 3 次，得到可靠的觸發率），然後呼叫 Claude 根據失敗的地方提出改進。它會在訓練集和測試集上重新評估每個新的 description，最多迭代 5 次。完成時，它會在瀏覽器裡打開一份 HTML 報告，顯示每個迭代的結果，並回傳帶有 `best_description` 的 JSON，這個 description 是依測試分數而不是訓練分數挑選的，以避免過度擬合。

### Skill 觸發是怎麼運作的

了解觸發機制，有助於設計更好的 eval 查詢。Skill 會連同 name + description 出現在 Claude 的 `available_skills` 清單裡，Claude 根據那段 description 決定要不要參考某個 skill。要知道的重點是，Claude 只會對它自己不容易處理的任務參考 skill，像「讀這份 PDF」這種簡單、一步的查詢，就算 description 完美符合，也可能不會觸發 skill，因為 Claude 用基本工具就能直接處理。複雜、多步驟或專門的查詢，在 description 符合時，就會穩定地觸發 skill。

這表示你的 eval 查詢要夠實質，讓 Claude 真的會因為參考 skill 而受益。像「讀檔案 X」這種簡單的查詢是很差的測試案例，不管 description 品質如何，它們都不會觸發 skill。

### 步驟 4：套用結果

從 JSON 輸出裡取出 `best_description`，更新 skill 的 SKILL.md frontmatter。讓使用者看修改前後的對照，並回報分數。

---

### 打包並呈現（只有在 `present_files` 工具可用時）

檢查你有沒有 `present_files` 工具。如果沒有，就跳過這一步。如果有，就打包 skill，並把 .skill 檔呈現給使用者：

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

打包完後，把使用者導向產出的 `.skill` 檔案路徑，讓他們可以安裝。

---

## Claude.ai 專用的指示

在 Claude.ai 裡，核心工作流程是一樣的（草稿 → 測試 → 檢視 → 改進 → 重複），但因為 Claude.ai 沒有 subagent，有些做法要改變。以下是需要調整的地方：

**執行測試案例**：沒有 subagent 就沒有平行執行。每個測試案例，讀 skill 的 SKILL.md，然後照著它的指示自己去完成測試 prompt。一次做一個。這比獨立的 subagent 沒那麼嚴謹（skill 是你寫的，你又自己在執行它，所以你有完整的脈絡），但這是有用的健全性檢查，而且人工檢視這一步會補償這點。跳過 baseline 的執行，直接用 skill 照要求完成任務就好。

**檢視結果**：如果你沒辦法開瀏覽器（例如 Claude.ai 的 VM 沒有顯示器，或是你在遠端 server 上），就完全跳過瀏覽器 reviewer。改成直接在對話裡呈現結果。每個測試案例，顯示 prompt 和輸出。如果輸出是使用者需要看的檔案（像 .docx 或 .xlsx），就存到檔案系統，並告訴他們放在哪裡，讓他們可以下載檢查。直接在對話裡請他們給回饋：「這樣看起來如何？有什麼想改的嗎？」

**Benchmark**：跳過定量的 benchmark，它依賴 baseline 比較，沒有 subagent 的話，這沒有意義。把重點放在使用者的定性回饋。

**迭代迴圈**：跟之前一樣，改進 skill、重跑測試案例、請求回饋，只是中間沒有瀏覽器 reviewer。如果有檔案系統，你還是可以把結果整理到迭代目錄裡。

**Description 最佳化**：這一節需要 `claude` CLI 工具（具體來說是 `claude -p`），只有在 Claude Code 裡才有。如果你在 Claude.ai 就跳過。

**盲測比較**：需要 subagent。跳過。

**打包**：`package_skill.py` 這支 script 在任何有 Python 和檔案系統的地方都能用。在 Claude.ai 裡，你可以執行它，使用者就能下載產出的 `.skill` 檔。

**更新既有的 skill**：使用者可能是要你更新既有的 skill，而不是建立新的。這種情況下：
- **保留原本的名稱。** 記下 skill 的目錄名稱和 frontmatter 的 `name` 欄位，原封不動地使用。例如，如果已安裝的 skill 是 `research-helper`，就輸出 `research-helper.skill`（不是 `research-helper-v2`）。
- **編輯前先複製到可寫入的位置。** 已安裝的 skill 路徑可能是唯讀的。複製到 `/tmp/skill-name/`，在那裡編輯，再從副本打包。
- **如果是手動打包，先在 `/tmp/` 暫存**，再複製到輸出目錄，直接寫入可能會因為權限而失敗。

---

## Cowork 專用的指示

如果你在 Cowork 裡，主要要知道這幾件事：

- 你有 subagent，所以主要的工作流程（平行啟動測試案例、跑 baseline、評分等）全都能用。（不過，如果你遇到嚴重的逾時問題，可以改成依序而不是平行執行測試 prompt。）
- 你沒有瀏覽器或顯示器，所以產生 eval viewer 時，要用 `--static <output_path>` 寫出一個獨立的 HTML 檔，而不是啟動 server。然後提供一個使用者可以點開、在瀏覽器裡打開那個 HTML 的連結。
- 回饋的運作方式不同：因為沒有執行中的 server，viewer 的「Submit All Reviews」按鈕會把 `feedback.json` 當成檔案下載。然後你可以從那裡讀取它（你可能得先請求存取權限）。
- 打包可以運作，`package_skill.py` 只需要 Python 和檔案系統。
- Description 最佳化（`run_loop.py` / `run_eval.py`）在 Cowork 裡應該可以正常運作，因為它是透過 subprocess 使用 `claude -p`，不是瀏覽器，但請等到你完全做完 skill、而且使用者同意它狀態不錯之後再做。
- **更新既有的 skill**：使用者可能是要你更新既有的 skill，而不是建立新的。照上面 claude.ai 一節裡的更新指引做。

---

## 參考檔案

agents/ 目錄裡有給專門 subagent 的指示。需要啟動相關的 subagent 時再去讀。

- `agents/grader.md`：如何對照輸出評估 assertion
- `agents/comparator.md`：如何對兩份輸出做盲測的 A/B 比較
- `agents/analyzer.md`：如何分析為什麼某個版本贏過另一個

references/ 目錄有額外的文件：
- `references/schemas.md`：evals.json、grading.json 等的 JSON 結構

---

為了強調，這裡再重複一次核心迴圈：

- 弄清楚這個 skill 是關於什麼
- 草擬或編輯 skill
- 用能使用這個 skill 的 claude 去跑測試 prompt
- 與使用者一起評估輸出：
  - 建立 benchmark.json 並執行 `eval-viewer/generate_review.py` 來幫使用者檢視它們
  - 執行定量的 eval
- 重複，直到你和使用者都滿意
- 打包最終的 skill 並交還給使用者。

如果你有 TodoList 之類的東西，請把這些步驟加進去，確保你不會忘記。如果你在 Cowork 裡，請特別把「Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases」放進你的 TodoList，確保這件事會發生。

祝好運！
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as is or modify if you feel something needs to change about them). Then explain them to the user (or if they already existed, explain the ones that already exist)
  - Use the `eval-viewer/generate_review.py` script to show the user the results for them to look at, and also let them look at the quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws that become apparent from the quantitative benchmarks)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always be flexible and if the user is like "I don't need to run a bunch of evaluations, just vibe with me", you can do that instead.

Then after the skill is done (but again, the order is flexible), you can also run the skill description improver, which we have a whole separate script for, to optimize the triggering of the skill.

Cool? Cool.

## Communicating with the user

The skill creator is liable to be used by people across a wide range of familiarity with coding jargon. If you haven't heard (and how could you, it's only very recently that it started), there's a trend now where the power of Claude is inspiring plumbers to open up their terminals, parents and grandparents to google "how to install npm". On the other hand, the bulk of users are probably fairly computer-literate.

So please pay attention to context cues to understand how to phrase your communication! In the default case, just to give you some idea:

- "evaluation" and "benchmark" are borderline, but OK
- for "JSON" and "assertion" you want to see serious cues from the user that they know what those things are before using them without explaining them

It's OK to briefly explain terms if you're in doubt, and feel free to clarify terms with a short definition if you're unsure if the user will get it.

---

## Creating a skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding to the next step.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs - if useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: When to trigger, what it does. This is the primary triggering mechanism - include both what the skill does AND specific contexts for when to use it. All "when to use" info goes here, not in the body. Note: currently Claude has a tendency to "undertrigger" skills -- to not use them when they'd be useful. To combat this, please make the skill descriptions a little bit "pushy". So for instance, instead of "How to build a simple fast dashboard to display internal Anthropic data.", you might write "How to build a simple fast dashboard to display internal Anthropic data. Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- **the rest of the skill :)**

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** - As needed (unlimited, scripts can execute without loading)

These word counts are approximate and you can feel free to go longer if needed.

**Key patterns:**
- Keep SKILL.md under 500 lines; if you're approaching this limit, add an additional layer of hierarchy along with clear pointers about where the model using the skill should go next to follow up.
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant:
```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```
Claude reads only the relevant reference file.

#### Principle of Lack of Surprise

This goes without saying, but skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like a "roleplay as an XYZ" are OK though.

#### Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats** - You can do it like this:
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern** - It's useful to include examples. You can format them like this (but if "Input" and "Output" are in the examples you might want to deviate a little):
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing Style

Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs. Use theory of mind and try to make the skill general and not super-narrow to specific examples. Start by writing a draft and then look at it with fresh eyes and improve it.

### Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: [you don't have to use this exact language] "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `assertions` field, which you'll add later).

## Running and evaluating test cases

This section is one continuous sequence — don't stop partway through. Do NOT use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.). Don't create all of this upfront — just create directories as you go.

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. This is important: don't spawn the with-skill runs first and then come back for baselines later. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run** (same prompt, but the baseline depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case (assertions can be empty for now). Give each eval a descriptive name based on what it's testing — not just "eval-0". Use this name for the directory too. If this iteration uses new or modified eval prompts, create these files for each new eval directory — don't assume they carry over from previous iterations.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: While runs are in progress, draft assertions

Don't just wait for the runs to finish — you can use this time productively. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update the `eval_metadata.json` files and `evals/evals.json` with the assertions once drafted. Also explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.

### Step 3: As runs complete, capture timing data

When each subagent task completes, you receive a notification containing `total_tokens` and `duration_ms`. Save this data immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere. Process each notification as it arrives rather than trying to batch them.

### Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run** — spawn a grader subagent (or grade inline) that reads `agents/grader.md` and evaluates each assertion against the outputs. Save results to `grading.json` in each run directory. The grading.json expectations array must use the fields `text`, `passed`, and `evidence` (not `name`/`met`/`details` or other variants) — the viewer depends on these exact field names. For assertions that can be checked programmatically, write and run a script rather than eyeballing it — scripts are faster, more reliable, and can be reused across iterations.

2. **Aggregate into benchmark** — run the aggregation script from the skill-creator directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, with mean ± stddev and the delta. If generating benchmark.json manually, see `references/schemas.md` for the exact schema the viewer expects.
Put each with_skill version before its baseline counterpart.

3. **Do an analyst pass** — read the benchmark data and surface patterns the aggregate stats might hide. See `agents/analyzer.md` (the "Analyzing Benchmark Results" section) for what to look for — things like assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), and time/token tradeoffs.

4. **Launch the viewer** with both qualitative outputs and quantitative data:
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   **Cowork / headless environments:** If `webbrowser.open()` is not available or the environment has no display, use `--static <output_path>` to write a standalone HTML file instead of starting a server. Feedback will be downloaded as a `feedback.json` file when the user clicks "Submit All Reviews". After download, copy `feedback.json` into the workspace directory for the next iteration to pick up.

Note: please use generate_review.py to create the viewer; there's no need to write custom HTML.

5. **Tell the user** something like: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you're done, come back here and let me know."

### What the user sees in the viewer

The "Outputs" tab shows one test case at a time:
- **Prompt**: the task that was given
- **Output**: the files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): collapsed section showing last iteration's output
- **Formal Grades** (if grading was run): collapsed section showing assertion pass/fail
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time, shown below the textbox

The "Benchmark" tab shows the stats summary: pass rates, timing, and token usage for each configuration, with per-eval breakdowns and analyst observations.

Navigation is via prev/next buttons or arrow keys. When done, they click "Submit All Reviews" which saves all feedback to `feedback.json`.

### Step 5: Read the feedback

When the user tells you they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus your improvements on the test cases where the user had specific complaints.

Kill the viewer server when you're done with it:

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## Improving the skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

### How to think about improvements

1. **Generalize from the feedback.** The big picture thing that's happening here is that we're trying to create skills that can be used a million times (maybe literally, maybe even more who knows) across many different prompts. Here you and the user are iterating on only a few examples over and over again because it helps move faster. The user knows these examples in and out and it's quick for them to assess new outputs. But if the skill you and the user are codeveloping works only for those examples, it's useless. Rather than put in fiddly overfitty changes, or oppressively constrictive MUSTs, if there's some stubborn issue, you might try branching out and using different metaphors, or recommending different patterns of working. It's relatively cheap to try and maybe you'll land on something great.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Make sure to read the transcripts, not just the final outputs — if it looks like the skill is making the model waste a bunch of time doing things that are unproductive, you can try getting rid of the parts of the skill that are making it do that and seeing what happens.

3. **Explain the why.** Try hard to explain the **why** behind everything you're asking the model to do. Today's LLMs are *smart*. They have good theory of mind and when given a good harness can go beyond rote instructions and really make things happen. Even if the feedback from the user is terse or frustrated, try to actually understand the task and why the user is writing what they wrote, and what they actually wrote, and then transmit this understanding into the instructions. If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag — if possible, reframe and explain the reasoning so that the model understands why the thing you're asking for is important. That's a more humane, powerful, and effective approach.

4. **Look for repeated work across test cases.** Read the transcripts from the test runs and notice if the subagents all independently wrote similar helper scripts or took the same multi-step approach to something. If all 3 test cases resulted in the subagent writing a `create_docx.py` or a `build_chart.py`, that's a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it. This saves every future invocation from reinventing the wheel.

This task is pretty important (we are trying to create billions a year in economic value here!) and your thinking time is not the blocker; take your time and really mull things over. I'd suggest writing a draft revision and then looking at it anew and making improvements. Really do your best to get into the head of the user and understand what they want and need.

### The iteration loop

After improving the skill:

1. Apply your improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. If you're creating a new skill, the baseline is always `without_skill` (no skill) — that stays the same across iterations. If you're improving an existing skill, use your judgment on what makes sense as the baseline: the original version the user came in with, or the previous iteration.
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review and tell you they're done
5. Read the new feedback, improve again, repeat

Keep going until:
- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

---

## Advanced: Blind comparison

For situations where you want a more rigorous comparison between two versions of a skill (e.g., the user asks "is the new version actually better?"), there's a blind comparison system. Read `agents/comparator.md` and `agents/analyzer.md` for the details. The basic idea is: give two outputs to an independent agent without telling it which is which, and let it judge quality. Then analyze why the winner won.

This is optional, requires subagents, and most users won't need it. The human review loop is usually sufficient.

---

## Description Optimization

The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

### Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

The queries must be realistic and something a Claude Code or Claude.ai user would actually type. Not abstract requests, but requests that are concrete and specific and have a good amount of detail. For instance, file paths, personal context about the user's job or situation, column names and values, company names, URLs. A little bit of backstory. Some might be in lowercase or contain abbreviations or typos or casual speech. Use a mix of different lengths, and focus on edge cases rather than making them clear-cut (the user will get a chance to sign off on them).

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

For the **should-trigger** queries (8-10), think about coverage. You want different phrasings of the same intent — some formal, some casual. Include cases where the user doesn't explicitly name the skill or file type but clearly needs it. Throw in some uncommon use cases and cases where this skill competes with another but should win.

For the **should-not-trigger** queries (8-10), the most valuable ones are the near-misses — queries that share keywords or concepts with the skill but actually need something different. Think adjacent domains, ambiguous phrasing where a naive keyword match would trigger but shouldn't, and cases where the query touches on something the skill does but in a context where another tool is more appropriate.

The key thing to avoid: don't make should-not-trigger queries obviously irrelevant. "Write a fibonacci function" as a negative test for a PDF skill is too easy — it doesn't test anything. The negative cases should be genuinely tricky.

### Step 2: Review with user

Present the eval set to the user for review using the HTML template:

1. Read the template from `assets/eval_review.html`
2. Replace the placeholders:
   - `__EVAL_DATA_PLACEHOLDER__` → the JSON array of eval items (no quotes around it — it's a JS variable assignment)
   - `__SKILL_NAME_PLACEHOLDER__` → the skill's name
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → the skill's current description
3. Write to a temp file (e.g., `/tmp/eval_review_<skill-name>.html`) and open it: `open /tmp/eval_review_<skill-name>.html`
4. The user can edit queries, toggle should-trigger, add/remove entries, then click "Export Eval Set"
5. The file downloads to `~/Downloads/eval_set.json` — check the Downloads folder for the most recent version in case there are multiple (e.g., `eval_set (1).json`)

This step matters — bad eval queries lead to bad descriptions.

### Step 3: Run the optimization loop

Tell the user: "This will take some time — I'll run the optimization loop in the background and check on it periodically."

Save the eval set to the workspace, then run in the background:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt (the one powering the current session) so the triggering test matches what the user actually experiences.

While it runs, periodically tail the output to give the user updates on which iteration it's on and what the scores look like.

This handles the full optimization loop automatically. It splits the eval set into 60% train and 40% held-out test, evaluates the current description (running each query 3 times to get a reliable trigger rate), then calls Claude to propose improvements based on what failed. It re-evaluates each new description on both train and test, iterating up to 5 times. When it's done, it opens an HTML report in the browser showing the results per iteration and returns JSON with `best_description` — selected by test score rather than train score to avoid overfitting.

### How skill triggering works

Understanding the triggering mechanism helps design better eval queries. Skills appear in Claude's `available_skills` list with their name + description, and Claude decides whether to consult a skill based on that description. The important thing to know is that Claude only consults skills for tasks it can't easily handle on its own — simple, one-step queries like "read this PDF" may not trigger a skill even if the description matches perfectly, because Claude can handle them directly with basic tools. Complex, multi-step, or specialized queries reliably trigger skills when the description matches.

This means your eval queries should be substantive enough that Claude would actually benefit from consulting a skill. Simple queries like "read file X" are poor test cases — they won't trigger skills regardless of description quality.

### Step 4: Apply the result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show the user before/after and report the scores.

---

### Package and Present (only if `present_files` tool is available)

Check whether you have access to the `present_files` tool. If you don't, skip this step. If you do, package the skill and present the .skill file to the user:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

After packaging, direct the user to the resulting `.skill` file path so they can install it.

---

## Claude.ai-specific instructions

In Claude.ai, the core workflow is the same (draft → test → review → improve → repeat), but because Claude.ai doesn't have subagents, some mechanics change. Here's what to adapt:

**Running test cases**: No subagents means no parallel execution. For each test case, read the skill's SKILL.md, then follow its instructions to accomplish the test prompt yourself. Do them one at a time. This is less rigorous than independent subagents (you wrote the skill and you're also running it, so you have full context), but it's a useful sanity check — and the human review step compensates. Skip the baseline runs — just use the skill to complete the task as requested.

**Reviewing results**: If you can't open a browser (e.g., Claude.ai's VM has no display, or you're on a remote server), skip the browser reviewer entirely. Instead, present results directly in the conversation. For each test case, show the prompt and the output. If the output is a file the user needs to see (like a .docx or .xlsx), save it to the filesystem and tell them where it is so they can download and inspect it. Ask for feedback inline: "How does this look? Anything you'd change?"

**Benchmarking**: Skip the quantitative benchmarking — it relies on baseline comparisons which aren't meaningful without subagents. Focus on qualitative feedback from the user.

**The iteration loop**: Same as before — improve the skill, rerun the test cases, ask for feedback — just without the browser reviewer in the middle. You can still organize results into iteration directories on the filesystem if you have one.

**Description optimization**: This section requires the `claude` CLI tool (specifically `claude -p`) which is only available in Claude Code. Skip it if you're on Claude.ai.

**Blind comparison**: Requires subagents. Skip it.

**Packaging**: The `package_skill.py` script works anywhere with Python and a filesystem. On Claude.ai, you can run it and the user can download the resulting `.skill` file.

**Updating an existing skill**: The user might be asking you to update an existing skill, not create a new one. In this case:
- **Preserve the original name.** Note the skill's directory name and `name` frontmatter field -- use them unchanged. E.g., if the installed skill is `research-helper`, output `research-helper.skill` (not `research-helper-v2`).
- **Copy to a writeable location before editing.** The installed skill path may be read-only. Copy to `/tmp/skill-name/`, edit there, and package from the copy.
- **If packaging manually, stage in `/tmp/` first**, then copy to the output directory -- direct writes may fail due to permissions.

---

## Cowork-Specific Instructions

If you're in Cowork, the main things to know are:

- You have subagents, so the main workflow (spawn test cases in parallel, run baselines, grade, etc.) all works. (However, if you run into severe problems with timeouts, it's OK to run the test prompts in series rather than parallel.)
- You don't have a browser or display, so when generating the eval viewer, use `--static <output_path>` to write a standalone HTML file instead of starting a server. Then proffer a link that the user can click to open the HTML in their browser.
- For whatever reason, the Cowork setup seems to disincline Claude from generating the eval viewer after running the tests, so just to reiterate: whether you're in Cowork or in Claude Code, after running tests, you should always generate the eval viewer for the human to look at examples before revising the skill yourself and trying to make corrections, using `generate_review.py` (not writing your own boutique html code). Sorry in advance but I'm gonna go all caps here: GENERATE THE EVAL VIEWER *BEFORE* evaluating inputs yourself. You want to get them in front of the human ASAP!
- Feedback works differently: since there's no running server, the viewer's "Submit All Reviews" button will download `feedback.json` as a file. You can then read it from there (you may have to request access first).
- Packaging works — `package_skill.py` just needs Python and a filesystem.
- Description optimization (`run_loop.py` / `run_eval.py`) should work in Cowork just fine since it uses `claude -p` via subprocess, not a browser, but please save it until you've fully finished making the skill and the user agrees it's in good shape.
- **Updating an existing skill**: The user might be asking you to update an existing skill, not create a new one. Follow the update guidance in the claude.ai section above.

---

## Reference files

The agents/ directory contains instructions for specialized subagents. Read them when you need to spawn the relevant subagent.

- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison between two outputs
- `agents/analyzer.md` — How to analyze why one version beat another

The references/ directory has additional documentation:
- `references/schemas.md` — JSON structures for evals.json, grading.json, etc.

---

Repeating one more time the core loop here for emphasis:

- Figure out what the skill is about
- Draft or edit the skill
- Run claude-with-access-to-the-skill on test prompts
- With the user, evaluate the outputs:
  - Create benchmark.json and run `eval-viewer/generate_review.py` to help the user review them
  - Run quantitative evals
- Repeat until you and the user are satisfied
- Package the final skill and return it to the user.

Please add steps to your TodoList, if you have such a thing, to make sure you don't forget. If you're in Cowork, please specifically put "Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases" in your TodoList to make sure it happens.

Good luck!
~~~~~
{% endraw %}

</section>
</div>
