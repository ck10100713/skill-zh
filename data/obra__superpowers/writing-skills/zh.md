---
name: writing-skills
description: 建立新的 skill、編輯既有的 skill，或在部署前驗證 skill 是否有效時使用
---

# Writing Skills

## 概述

**寫 skill 就是把 Test-Driven Development 套用在流程文件上。**

**個人 skill 放在你的 runtime 的 skills 目錄**（Claude Code 上是 `~/.claude/skills/`）：其他 runtime 的路徑，見 [codex-tools.md](../using-superpowers/references/codex-tools.md) 或 [gemini-tools.md](../using-superpowers/references/gemini-tools.md)。Codex、Copilot CLI 和 Gemini CLI 也都認得 `~/.agents/skills/` 這個跨 runtime 的別名。

你寫測試案例（搭配 subagent 的壓力情境）、看著它們失敗（基準行為）、寫 skill（文件）、看著測試通過（agent 遵守）、再重構（堵住漏洞）。

**核心原則：** 如果你沒看過 agent 在沒有這個 skill 時失敗，你就不知道這個 skill 教的是不是對的東西。

**必要的背景知識：** 使用這個 skill 之前，你一定要先理解 superpowers:test-driven-development。那個 skill 定義了基本的 RED-GREEN-REFACTOR 循環。這個 skill 是把 TDD 調整來用在文件上。

**官方指引：** Anthropic 官方的 skill 撰寫最佳實務，見 references/anthropic-best-practices.md。這份文件提供額外的模式和指引，補充這個 skill 以 TDD 為主的做法。

## 什麼是 Skill？

**Skill** 是針對已驗證的技巧、模式或工具的參考指南。Skill 幫助未來的 agent 找到並套用有效的做法。

**Skill 是：** 可重複使用的技巧、模式、工具、參考指南

**Skill 不是：** 敘述你曾經怎麼解決一個問題的故事

## Skill 的 TDD 對照

| TDD 概念 | Skill 建立 |
|-------------|----------------|
| **測試案例** | 搭配 subagent 的壓力情境 |
| **Production 程式碼** | Skill 文件（SKILL.md） |
| **測試失敗（RED）** | Agent 在沒有 skill 時違反規則（基準） |
| **測試通過（GREEN）** | Agent 在有 skill 時遵守 |
| **重構** | 在維持遵守的同時堵住漏洞 |
| **先寫測試** | 寫 skill「之前」先跑基準情境 |
| **看著它失敗** | 記錄 agent 使用的確切合理化說法 |
| **最少的程式碼** | 寫出處理那些特定違規的 skill |
| **看著它通過** | 驗證 agent 現在遵守了 |
| **重構循環** | 找出新的合理化說法 → 堵住 → 重新驗證 |

整個 skill 建立的過程，都遵循 RED-GREEN-REFACTOR。

## 何時建立 Skill

**這些情況要建立：**
- 這個技巧對你來說不是直覺上顯而易見的
- 你會在不同專案之間再次參考它
- 這個模式適用範圍廣（不是專案專屬）
- 其他人也會受益

**這些情況不要建立：**
- 一次性的解法
- 別處已有完整文件的標準做法
- 專案專屬的慣例（放在你的指示檔裡）
- 機械式的限制（如果能用 regex／驗證來強制執行，就自動化它，把文件留給需要判斷的情況）

## Skill 類型

### 技巧（Technique）
有步驟可循的具體方法（condition-based-waiting、root-cause-tracing）

### 模式（Pattern）
思考問題的方式（flatten-with-flags、test-invariants）

### 參考（Reference）
API 文件、語法指南、工具文件（office docs）

## 目錄結構


```
skills/
  skill-name/
    SKILL.md              # Main reference (required)
    supporting-file.*     # Only if needed
```

**扁平的命名空間**：所有 skill 都在同一個可搜尋的命名空間

**拆成獨立檔案的情況：**
1. **大量參考資料**（100+ 行）：API 文件、完整的語法
2. **可重複使用的工具**：Script、工具程式、範本

**保持 inline 的內容：**
- 原則與概念
- 程式碼模式（< 50 行）
- 其他所有東西

## 撰寫 SKILL.md

Skill 的 `description` 只說明何時使用它：觸發條件和症狀，以「Use when...」開頭。它絕對不要摘要這個 skill 的工作流程，因為讀到工作流程摘要的 agent，會照著摘要做，而不是去讀整個 skill。

當你撰寫或修改 skill 的 frontmatter、名稱或 description，或需要縮減它的大小時，讀 [references/discovery.md](references/discovery.md)：它有 SKILL.md 範本、description 與關鍵字的指引、命名、token 預算，以及交叉參照其他 skill 的方式。

## 流程圖

當你在 skill 裡加入或修改流程圖時，先讀 [references/flowcharts.md](references/flowcharts.md)：什麼時候流程圖值得放進去、graphviz 的慣例，以及怎麼渲染它。

## 程式碼範例

**一個出色的範例，勝過許多平庸的範例**

選擇最相關的語言：
- 測試技巧 → TypeScript/JavaScript
- 系統除錯 → Shell/Python
- 資料處理 → Python

**好的範例：**
- 完整而且可執行
- 有良好的註解，說明「為什麼」
- 來自真實情境
- 清楚展示模式
- 可以直接改編（不是通用的範本）

**不要：**
- 用 5 種以上的語言實作
- 做填空式的範本
- 寫牽強的範例

你很會移植，一個很棒的範例就夠了。

## 檔案組織

### 自成一體的 Skill
```
defense-in-depth/
  SKILL.md    # Everything inline
```
適用時機：所有內容都放得下，不需要大量參考資料

### 帶有可重複使用工具的 Skill
```
condition-based-waiting/
  SKILL.md    # Overview + patterns
  example.ts  # Working helpers to adapt
```
適用時機：工具是可重複使用的程式碼，不只是敘述

### 帶有大量參考資料的 Skill
```
pptx/
  SKILL.md       # Overview + workflows
  pptxgenjs.md   # 600 lines API reference
  ooxml.md       # 500 lines XML structure
  scripts/       # Executable tools
```
適用時機：參考資料太大，沒辦法放在 inline

在文字中，要透過直譯器來呼叫內附的 script（`bash scripts/tool.sh`、`node scripts/tool.js`），絕對不要只寫裸路徑：有些 harness 的 plugin 打包工具會移除可執行位元，裸的 `scripts/tool.sh` 在那裡會因為 `Permission denied` 而失敗。

## 鐵律（跟 TDD 一樣）

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

這適用於新的 skill，「也」適用於對既有 skill 的修改。

在測試之前就寫了 skill？刪掉。重來。
沒測試就修改 skill？同樣違規。

**沒有例外：**
- 「簡單的補充」也不例外
- 「只是加一個段落」也不例外
- 「文件更新」也不例外
- 不要把沒測試過的變更留著當「參考」
- 跑測試的時候不要「改編」
- 刪掉就是刪掉

**必要的背景知識：** superpowers:test-driven-development skill 解釋了為什麼這很重要。同樣的原則也適用於文件。

## 測試所有類型的 Skill

不同類型的 skill 需要不同的測試方法：

### 強制紀律的 Skill（規則／要求）

**範例：** TDD、verification-before-completion、designing-before-coding

**測試方式：**
- 學術性問題：他們理解規則嗎？
- 壓力情境：在壓力下他們還遵守嗎？
- 合併多種壓力：時間 + 沉沒成本 + 疲憊
- 找出合理化的說法，並加上明確的反制

**成功標準：** Agent 在最大壓力下仍遵守規則

### 技巧型 Skill（how-to 指南）

**範例：** condition-based-waiting、root-cause-tracing、defensive-programming

**測試方式：**
- 應用情境：他們能正確套用這個技巧嗎？
- 變化情境：他們能處理邊界情況嗎？
- 缺少資訊的測試：指示有沒有缺口？

**成功標準：** Agent 成功地把技巧套用到新情境

### 模式型 Skill（心智模型）

**範例：** reducing-complexity、information-hiding 的概念

**測試方式：**
- 辨識情境：他們能辨識這個模式何時適用嗎？
- 應用情境：他們能使用這個心智模型嗎？
- 反例：他們知道何時「不」該套用嗎？

**成功標準：** Agent 正確辨識何時／如何套用這個模式

### 參考型 Skill（文件／API）

**範例：** API 文件、指令參考、函式庫指南

**測試方式：**
- 檢索情境：他們找得到正確的資訊嗎？
- 應用情境：他們能正確使用找到的東西嗎？
- 缺口測試：常見的使用情況都有涵蓋嗎？

**成功標準：** Agent 找到並正確套用參考資訊

## 跳過測試的常見合理化藉口

| 藉口 | 現實 |
|--------|---------|
| 「Skill 顯然很清楚」 | 你覺得清楚 ≠ 其他 agent 覺得清楚。測試它。 |
| 「它只是個參考」 | 參考資料也可能有缺口、有不清楚的段落。測試檢索。 |
| 「測試太小題大做」 | 沒測試過的 skill 一定有問題。一律如此。花 15 分鐘測試能省下好幾個小時。 |
| 「出現問題再測」 | 問題 = agent 沒辦法使用這個 skill。部署「之前」就測試。 |
| 「測試太繁瑣」 | 測試比起在正式環境除錯一個壞掉的 skill 要輕鬆得多。 |
| 「我有信心它很好」 | 過度自信保證會出問題。還是要測試。 |
| 「學術性審查就夠了」 | 讀 ≠ 用。測試應用情境。 |
| 「沒時間測試」 | 部署沒測試過的 skill，之後花更多時間去修它。 |

**這些全部都表示：部署之前先測試。沒有例外。**

## 讓形式對應失敗類型

寫指引之前，先把基準失敗分類。能讓某一種失敗類型滴水不漏的形式，用在另一種上，經過量測反而會適得其反。

| 基準失敗 | 正確的形式 | 錯誤的形式 |
|---|---|---|
| 在壓力下跳過／違反規則（明明知道比較好，還是照做） | 禁止 + 合理化對照表 + 警訊（見 references/bulletproofing.md） | 軟性的指引（「prefer...」、「consider...」） |
| 有遵守，但輸出的形狀不對（臃腫的 prompt、被埋沒的結論、重述規格） | 正向的配方或契約：說明輸出「是」什麼，它的各個部分，依序 | 禁止清單（「don't restate」、「never narrate」） |
| 在他們已經在產出的東西裡，漏掉必要的元素 | 結構性的做法：在他們要填的範本裡，加上 REQUIRED 欄位或位置 | 在範本附近放文字提醒 |
| 行為應該取決於某個條件 | 以可觀察的謂詞為依據的條件式（「if the brief exists, reference it」） | 無條件的規則 + 豁免條款 |

**為什麼禁止在塑形問題上會適得其反：** 在互相競爭的誘因之下（「讓 prompt 自成一體」），agent 會跟「don't X」討價還價。在針對派工 prompt 指引的正面對決措辭測試中，禁止那一組產生的不想要的內容，明顯比配方那一組多（分布完全分離），而且趨勢甚至比完全沒有指引的對照組更差：自己對你的案例做微測試，不要假設，但絕對不要預設就去用禁止。配方沒有什麼可以討價還價的：輸出要嘛符合所述的形狀，要嘛就不符合。

**不管你選哪種形式，都要遵守的規則：**
- **不要有細微差別的條款。** 「Don't X unless it matters」會重新打開談判：在同樣的措辭測試中，只要在一個勝出的配方後面加上一個細微差別的條款，它就從穩定變成雜亂。把真正的例外，表達成它自己的、以可觀察謂詞為依據的條件式。
- **豁免條款劃不出範圍。** 「This limit doesn't apply to code blocks」仍然會抑制程式碼區塊。如果輸出的某個部分必須被豁免，就重新調整結構，讓規則碰不到它。

## 對合理化說法做到滴水不漏

當基準失敗是紀律上的失敗時，在你寫指引「之前」，先讀 [references/bulletproofing.md](references/bulletproofing.md)：堵住漏洞、精神與字面的界線、合理化對照表，以及警訊清單。

## Skill 的 RED-GREEN-REFACTOR

照著 TDD 循環走：

### RED：寫會失敗的測試（基準）

在「沒有」這個 skill 的情況下，用 subagent 跑壓力情境。記錄確切的行為：
- 他們做了哪些選擇？
- 他們用了哪些合理化說法（逐字）？
- 哪些壓力觸發了違規？

這就是「看著測試失敗」：你一定要先看到 agent 自然會怎麼做，才能寫 skill。

### GREEN：寫最少的 Skill

寫出處理那些特定合理化說法的 skill。不要為了假設性的情況加額外的內容。

用「有」這個 skill 的方式跑同樣的情境。Agent 現在應該要遵守。

### REFACTOR：堵住漏洞

Agent 找到新的合理化說法？加上明確的反制。重新測試，直到滴水不漏。

### 在完整情境之前，先對措辭做微測試

完整的壓力情境執行是最後的關卡，但每次迭代又慢又貴。先用微測試驗證措辭本身：

1. **每次呼叫一個全新 context 的樣本**：原始的 API 呼叫，或在沒有 API 存取時用單次執行的 subagent。System prompt = 這份指引實際會放進去的 context（完整的 skill 或 prompt 範本，不是單獨的指引）；user message = 一個會誘發這個失敗的任務。
2. **一定要有一個沒有指引的對照組。** 如果對照組沒有出現這個失敗，就沒有東西要修：停下來，不要寫指引。
3. **每個變體 5 次以上的重複。** 單一樣本會騙人。
4. **手動讀每一個被標記的匹配。** 想的話可以用程式評分，但範本的回聲和被引用的反例會假扮成命中；只看自動計數，會同時高估失敗和成功。
5. **變異也是一項指標。** 當指引發揮作用，各次重複會收斂到同樣的形狀。五次重複得到五種不同的詮釋，表示措辭沒有約束力：先把形式收緊，再增加字數。

微測試驗證的是措辭；它們不能取代針對紀律型 skill 的壓力情境。

**測試方法：** 完整的測試方法，見 [references/testing-skills-with-subagents.md](references/testing-skills-with-subagents.md)：
- 怎麼寫壓力情境
- 壓力類型（時間、沉沒成本、權威、疲憊）
- 系統化地堵住漏洞
- 元測試技巧

## 反模式

### ❌ 敘事式的範例
「In session 2025-10-03, we found empty projectDir caused...」
**為什麼不好：** 太具體，無法重複使用

### ❌ 多語言稀釋
example-js.js、example-py.py、example-go.go
**為什麼不好：** 品質平庸、增加維護負擔

### ❌ 流程圖裡放程式碼
```dot
step1 [label="import fs"];
step2 [label="read file"];
```
**為什麼不好：** 沒辦法複製貼上、難以閱讀

### ❌ 通用的標籤
helper1、helper2、step3、pattern4
**為什麼不好：** 標籤應該要有語意

## 停：進入下一個 Skill 之前

**寫完「任何」skill 之後，你一定要停下來，完成部署流程。**

**不要：**
- 不測試每一個，就批次建立多個 skill
- 在目前這個還沒驗證之前，就進入下一個 skill
- 因為「批次處理比較有效率」就跳過測試

**下面的部署檢查表，「每一個」skill 都必須做。**

部署沒測試過的 skill = 部署沒測試過的程式碼。這違反品質標準。

## Skill 建立檢查表（TDD 改編版）

**重要：下面每一項檢查表項目，都要建立一個 todo。**

**RED 階段：寫會失敗的測試：**
- [ ] 建立壓力情境（紀律型 skill 要有 3 個以上合併的壓力）
- [ ] 在「沒有」skill 的情況下跑情境：逐字記錄基準行為
- [ ] 找出合理化說法／失敗中的模式

**GREEN 階段：寫最少的 Skill：**
- [ ] 名稱只用字母、數字、連字號（不要有括號／特殊字元）
- [ ] YAML frontmatter 要有必填的 `name` 和 `description` 欄位（最多 1024 字元；見 [spec](https://agentskills.io/specification)）
- [ ] Description 以「Use when...」開頭，並包含具體的觸發條件／症狀
- [ ] Description 用第三人稱寫
- [ ] 全文佈滿供搜尋用的關鍵字（錯誤、症狀、工具）
- [ ] 清楚的概述，附核心原則
- [ ] 處理 RED 階段找到的特定基準失敗
- [ ] 指引的形式符合失敗類型（見「讓形式對應失敗類型」）
- [ ] 對於塑造行為的指引：措辭已用沒有指引的對照組做過微測試（5 次以上重複、每個被標記的匹配都手動讀過），純參考型 skill 不適用
- [ ] 程式碼 inline，或連結到獨立的檔案
- [ ] 一個出色的範例（不是多語言）
- [ ] 用「有」skill 的方式跑情境：驗證 agent 現在遵守了

**REFACTOR 階段：堵住漏洞：**
- [ ] 從測試中找出「新的」合理化說法
- [ ] 加上明確的反制（如果是紀律型 skill）
- [ ] 用所有測試迭代的結果，建立合理化對照表
- [ ] 建立警訊清單
- [ ] 重新測試，直到滴水不漏

**品質檢查：**
- [ ] 只有在決策不明顯時，才放小型流程圖
- [ ] 快速參考表
- [ ] 常見錯誤段落
- [ ] 沒有敘事性的說故事
- [ ] 只有工具或大量參考資料才用輔助檔案

**部署：**
- [ ] 把 skill commit 到 git，並 push 到你的 fork（如果有設定）
- [ ] 考慮透過 PR 貢獻回去（如果廣泛有用的話）

## 探索工作流程

未來的 agent 怎麼找到你的 skill：

1. **遇到問題**（「tests are flaky」）
2. **搜尋 skill**（grep description、瀏覽分類）
3. **找到 SKILL**（description 符合）
4. **掃過概述**（這跟我有關嗎？）
5. **讀模式**（快速參考表）
6. **載入範例**（只有在實作時）

**為這個流程做最佳化**：把可搜尋的詞放在前面，而且常常出現。
