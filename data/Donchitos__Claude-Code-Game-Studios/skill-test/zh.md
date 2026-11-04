---
name: skill-test
description: "驗證 skill 檔案的結構合規性和行為正確性。四種模式：靜態 linter、spec、類別評分標準、稽核。"
argument-hint: "static [skill-name | all] | spec [skill-or-agent-name] | category [skill-or-agent-name | all] | audit"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/skill-test/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/agent-check.sh*), Bash(bash .claude/scripts/compat-inventory.sh*)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

**自動化模式**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次寫檔，都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
屬於 `automation_always_ask` 的類別一律要詢問）。

# Skill Test

驗證 skill（`.claude/skills/*/SKILL.md`）和 agent（`.claude/agents/*.md`）
的結構合規性和行為正確性。沒有外部依賴，
完全在既有的 skill/hook/template 架構內執行。

**四種模式：**

| Mode | Command | Purpose | Token Cost |
|------|---------|---------|------------|
| `static` | `/skill-test static [name\|all]` | Structural linter — 7 compliance checks per skill, plus agent, delegation and compatibility observations | Low (~1k/skill) |
| `spec` | `/skill-test spec [name]` | Behavioral verifier — evaluates assertions in a skill's or agent's test spec | Medium (~5k each) |
| `category` | `/skill-test category [name\|all]` | Category rubric — checks a skill or agent against its category-specific metrics | Low (~2k each) |
| `audit` | `/skill-test audit` | Coverage report — skills, agent specs, last test dates | Low (~3k total) |

**通過代表什麼。** 每一種模式都是讀檔案，沒有任何一種會執行 skill。`static`：
檔案具備 skill 需要的結構，不代表它的行為正確。`spec`：仔細讀過之後，
指示涵蓋了每一個案例，不代表 Claude 執行時會照著做。
`category`：skill 照字面寫的內容符合它那個類別的評分標準。`audit`：
哪些 skill 和 agent 有 spec，以及各自上次檢查是什麼時候。一個 skill
實際做了什麼，只有執行時才看得出來：在專案的一份用完即丟的副本裡，拿一個真實的需求，
對你用的每個模型，各跑有 skill 和沒有 skill 的版本
（Anthropic 的 Agent Skills 最佳實務，"Build evaluations first"）。

---

## Phase 1: Parse Arguments

從第一個參數判斷模式：

- `static [name]` → 對單一 skill 跑 7 項結構檢查，或對單一 agent 做 agent 觀察
- `static all` → 對所有 skill 跑 7 項結構檢查（Glob `.claude/skills/*/SKILL.md`），外加每個 agent 的觀察
- `spec [name]` → 讀 skill 或 agent 加上它的測試 spec，評估斷言
- `category [name]` → 執行 `studio-tests/quality-rubric.md` 裡該類別專屬的評分標準
- `category all` → 對 catalog 裡每個有 `category:` 的 skill 和 agent 執行類別評分標準
- `audit`（或沒有參數）→ 讀 catalog，列出所有 skill 和 agent，顯示涵蓋率

如果參數無法辨識，輸出用法然後停下來。

**舊的 spec 資料夾。** Glob `CCGS Skill Testing Framework/catalog.yaml`。如果
它存在，先說："`CCGS Skill Testing Framework/` was renamed
`studio-tests/` in 1.2.0, and this skill reads only `studio-tests/`. Move any
specs you wrote there; UPGRADING.md (v1.1.3 → v1.2.0, `studio-tests/`) says how."
然後繼續用 `studio-tests/` 往下做。

**在做 `spec` 或 `category` 之前先解析名稱。** 在
`studio-tests/catalog.yaml` 裡查它：`skills:` 底下的條目是 skill
（`.claude/skills/[name]/SKILL.md`）；`agents:` 底下的條目是 agent
（`.claude/agents/[name].md`）。如果 catalog 裡沒有條目，就用這兩個檔案中存在的那個。
只有兩者都不存在時，才回報 "'[name]' is neither a skill in
`.claude/skills/` nor an agent in `.claude/agents/`." 然後停下來。一個
同時也是一般單字的名稱，仍然是名稱：`/skill-test spec help` 測的是 `/help`
這個 skill，絕對不是在要求這個 skill 的用法。

那 7 項檢查是 lint SKILL.md 的結構，所以只適用於 skill。給定的是 agent
名稱時，`static` 只會跑下面的觀察：agent 檔案沒有
phase 或結論關鍵字可以 lint。絕對不要把 agent 回報成不存在。

---

## Phase 2A: Static Mode — Structural Linter

對每個被測試的 skill，完整讀它的 `SKILL.md` 和它 `references/` 資料夾裡的每個檔案，
並把它們當成一個 skill，對它們跑全部 7 項檢查：最長的 skill 會把每個
階段放在 `references/`。frontmatter 的檢查（1、6 和 7）讀 `SKILL.md`。

### Check 1 — Required Frontmatter Fields
YAML frontmatter 區塊裡必須包含下列全部：
- `name:`
- `description:`
- `argument-hint:`
- `user-invocable:`
- `allowed-tools:`

任何一個缺少就是 **FAIL**。frontmatter 無法解析的檔案，Check 1
也算失敗：格式錯誤的 YAML 是這項檢查就是要抓的結構缺陷，不是
無法評估的檔案；見下面的每個 skill 的結果規則。

### Check 2 — Multiple Phases
skill 必須有 ≥2 個編號的 phase 標題。尋找像這樣的模式：
- `## Phase N` 或 `## Phase N:`
- `## N.`（編號的頂層段落）
- 如果 phase 沒有明確編號，至少要有 2 個不同的 `##` 標題

如果找到的類似 phase 的標題少於 2 個，就是 **FAIL**。

### Check 3 — Verdict Keywords

skill 必須傳達清楚的結果。接受以下任何一種：

- **Gate / review 結論**：`PASS`、`FAIL`、`CONCERNS`、`APPROVED`、
  `BLOCKED`、`COMPLETE`、`READY`、`COMPLIANT`、`NON-COMPLIANT`
- **Go / no-go 結論**：`PROCEED`、`PIVOT`、`KILL`、`GO`、`NO-GO`
- **嚴重度等級**：`CRITICAL`、`HIGH`、`MEDIUM`、`LOW`。稽核類的 skill 用嚴重度
  來排序發現，而不是對整次執行給一個結論。

如果以上都沒有，**而且** skill 會產出評估（它的
description 或內文承諾做審查、稽核、檢查、關卡或就緒度判斷），就是 **FAIL**。

如果以上都沒有，而且 skill 的輸出是一個產出物或一個值，
不是判斷，就是 **WARN**（絕對不是 FAIL）。`/settings` 就是典型的例子：它印出
並寫入設定，沒有結論可給。不要為了
滿足這項檢查而發明一個。

> 如果用比較窄的清單（只認 gate 結論，其他一律硬性 FAIL），會因為
> 不是 skill 自己的錯的原因，錯誤地判它們失敗：`/prototype` 和
> `/vertical-slice` 在自己的 description 裡就宣告了 `PROCEED`/`PIVOT`/`KILL`，
> `/adopt` 和 `/security-audit` 依嚴重度排序，而 `/settings` 依設計
> 就沒有結論。一個對正當的模式產生假失敗的 linter，
> 就不會再被信任。

### Check 4 — Collaborative Protocol Language
skill 必須包含寫入前先詢問的用語。尋找：
- `"May I write"`（標準形式）
- `"before writing"` 或 `"approval"` 出現在寫檔指示附近
- `"ask"` + `"write"` 靠得很近（在同一個段落內）

如果沒有就是 **WARN**（有些唯讀的 skill 理所當然地不會有）。
如果 `allowed-tools` 包含 `Write` 或 `Edit`，卻找不到寫入前先詢問的用語，就是 **FAIL**。

### Check 5 — Next-Step Handoff
skill 必須以建議的下一步動作或後續路徑作結。尋找：
- 最後一段有提到另一個 skill（例如 `/story-done`、`/gate-check`）
- "Recommended next" 或 "next step" 這類說法
- 一個 "Follow-Up" 或 "After this" 段落

如果沒有就是 **WARN**。

### Check 6 — Fork Context Complexity
如果 frontmatter 有 `context: fork`，skill 應該有 ≥5 個 phase 標題
（`##` 層級或編號的 Phase N 標題）。Fork context 是給複雜的多階段
skill 用的；簡單的 skill 不該使用它。

如果設了 `context: fork`，但找到的 phase 少於 5 個，就是 **WARN**。

### Check 7 — Argument Hint Plausibility
`argument-hint` 不能是空的。如果 skill 內文提到多種模式
（例如 "Mode A | Mode B"），hint 應該反映出來。把 hint
對照第一個 phase 的 "Parse Arguments" 段落。

如果 hint 是 `""`，或是文件裡寫的模式跟 hint 不符，就是 **WARN**。

### Agent and Delegation Observations (not scored)

對 skill 跑 `bash .claude/scripts/agent-check.sh --skill [name]`，
對 agent 跑 `bash .claude/scripts/agent-check.sh --agent [name]`，
或是對 `static all` 跑一次 `bash .claude/scripts/agent-check.sh`。它印出的是
觀察，絕對不是結論，而且這裡的任何東西都不會改變 skill 的結論。把它們
報告在 `Observations:` 底下，逐一判斷：

- **`DELEGATION:`** skill 中把工作交給 agent 的部分。讀它，並
  說明 brief 有沒有給出目標、輸出格式、工具和來源，以及邊界，
  還有它有沒有交給 agent 一個只有幾次工具呼叫的工作，或是
  重新檢查 skill 自己的工作。它的 `markers:` 是字數統計，
  用來指出該看哪裡，不是評分。
- **`AGENT:`** 設定的模型、effort 和回合數限制，以及描述旁邊的工具：
  點名描述裡那份工作用不到的任何工具。
- **`NOTE:`** 無法解析的 frontmatter；`asks-user`（agent 沒有
  問問題的工具，所以它的問題屬於它報告的結尾）；一個
  被忽略、或做的比它宣稱的更多的設定（`agent-type-list`、`preload-off`、
  `disallowed-specifier`、`memory-grants`）。
- **`OVERLAP:`** 兩個共用特殊用字的 description：說明各自是否
  仍然能點出自己的 agent，或是哪個請求會被送到錯的那個。

如果腳本無法執行，寫 `Observations: not run (<reason>)`。絕對不要把這一段
省略：缺少的段落讀起來跟乾淨的結果一樣。

### Compatibility Observations (not scored)

對 skill 跑 `bash .claude/scripts/compat-inventory.sh --skill [name]`，
對 agent 跑 `bash .claude/scripts/compat-inventory.sh --agent [name]`，
或是對 `static all` 跑一次 `bash .claude/scripts/compat-inventory.sh`。每一行
`FOUND:` 都是檔案依賴某個只有 Claude Code 提供的東西的地方，並附上
它的功能類別：questions、subagents、skill-loading、shell-lines、arguments、
frontmatter、instructions、hooks、settings 或 tools。Claude Code 全都支援，
所以沒有任何一個是缺陷，也沒有任何一個會改變結論。把它們報告在
`Compatibility:` 底下，每個功能一行，附上它的構造和行號；
對 `static all`，改為依功能給出 `COUNT:` 總數。`NOT FOUND:`
那一行代表這個名稱沒有比對到任何檔案：要這樣說明。如果腳本無法執行，寫
`Compatibility: not run (<reason>)`。

---

### Static Mode Output Format

單一 skill：
```
=== Skill Static Check: /[name] ===

Check 1 — Frontmatter Fields:    PASS
Check 2 — Multiple Phases:       PASS (7 phases found)
Check 3 — Verdict Keywords:      PASS (PASS, FAIL, CONCERNS)
Check 4 — Collaborative Protocol: PASS ("May I write" found)
Check 5 — Next-Step Handoff:     WARN (no follow-up section found)
Check 6 — Fork Context Complexity: PASS (8 phases, context: fork set)
Check 7 — Argument Hint:         PASS

Observations (not scored):
  Delegation, "Phase 3: Implementation" (line 202): ux-designer, ui-programmer.
    The brief names the output file and limits but no sources to read.

Compatibility (not scored):
  questions: AskUserQuestion (lines 13, 88) · shell-lines: shell-line (line 10)
  frontmatter: allowed-tools, argument-hint, model, user-invocable (lines 4-7)

Verdict: WARNINGS (1 warning, 0 failures)
Recommended: Add a "Follow-Up Actions" section at the end of the skill.
```

單一 agent 沒有結論，只有觀察：
```
=== Agent Static Check: qa-lead ===

Model: inherit · Effort: unset · Turn limit: 20
Tools: Read, Glob, Grep, Write, Edit, Bash. Fits the job (it writes test plans).
Observations (not scored):
  asks-user (lines 31, 52): tells the agent to get approval before writing.
  overlap with qa-tester (creation, regression, test): each still singled out.
Compatibility (not scored):
  frontmatter: tools, tools-string, model, maxTurns (lines 4-6)
```

WARN 或 FAIL 那一行要在括號裡點名原因，而且 COMPLIANT 以外的任何
結論，都要以一行 `Recommended:` 點名修正方式作結。

單一 skill 的 `Verdict:` 是四個值之一，跟 `static all` 的
Result 欄位相同：**COMPLIANT**（沒有警告、沒有失敗）、**WARNINGS**（有警告、
沒有失敗）、**NON-COMPLIANT**（任何 FAIL），或是 **NOT ASSESSED**（檔案
讀不到或無法解析，或是它的檢查無法執行，要點名原因）。

對 `static all`，產出一張摘要表，然後列出任何不合規的 skill：
```
=== Skill Static Check: All 74 Skills ===

Skill                  | Result       | Issues
-----------------------|--------------|-------
gate-check             | COMPLIANT    |
design-review          | COMPLIANT    |
story-readiness        | WARNINGS     | Check 5: no handoff
...

Summary: 48 COMPLIANT, 3 WARNINGS, 1 NON-COMPLIANT, 1 NOT ASSESSED
Aggregate Verdict: N WARNINGS / N FAILURES / N NOT ASSESSED

Agents (observations, not scored): 49 read
  asks-user: N agents · agent-type-list: N · preload-off: N · frontmatter: N
  Overlap pairs: [each pair, with whether both are still singled out]
  Delegation blocks: N in N skills; [the ones whose brief lacks a part]

Compatibility (not scored): N FOUND lines in N of N files read
  [feature]: [construct] N files, N hits; ...   (one line per feature)
```

**`NOT ASSESSED` 在這裡是每個 skill 各自的結果，不只是彙總那一行。** 檔案
不存在或以其他方式讀不到（權限、找不到）的 skill，因為連一項
檢查都沒辦法開始，要回報成 `NOT ASSESSED` 並附上原因：絕對不要
從表格中省略，也絕對不要算成 COMPLIANT。排序是**高於
COMPLIANT**、**低於 WARNINGS 和 NON-COMPLIANT**。*有*讀到、但
frontmatter 無法解析的檔案是不同的情況：Check 1 會在它身上失敗（見
上面），所以它要回報成 **NON-COMPLIANT**，不是 NOT ASSESSED：缺陷在
skill 本身，不在 linter 能不能存取它。

**而且要說明分母。** 標題裡的 `All 74 Skills` 必須是
實際檢查的數量，不是存在的數量：兩者不同時，要回報 `[N] of [M] skills checked`。
一份摘要的數字悄悄加起來比自己標題寫的還少，
就是這個 skill 本來該去抓別人的那種失敗。

static 模式不寫檔。

---

## Phase 2B: Spec Mode — Behavioral Verifier

### Step 1 — Locate Files

使用 Phase 1 解析出來的 skill 或 agent 檔案。
從 `studio-tests/catalog.yaml` 查 spec 的路徑，用
對應的 `skills:` 或 `agents:` 條目上的 `spec:` 欄位。

如果任何一個缺少：
- 缺少 skill 或 agent：Phase 1 的訊息。
- catalog 裡缺少 spec 路徑："No spec path set for '[name]' in catalog.yaml."
- 在路徑上找不到 spec 檔案："Spec file missing at [path]. Run `/skill-test audit`
  to see coverage gaps."

### Step 2 — Read Both Files

完整讀 skill（它的 `SKILL.md` 和它 `references/` 資料夾裡的每個檔案），
或 agent 檔案，以及測試 spec 檔案。

### Step 3 — Evaluate Assertions

**要依據執行它的模型看得到的東西來評估。** skill 在一個
session 裡執行，被生成的 agent 在它自己的 context 裡執行，而且兩者都載入了專案的
`CLAUDE.md`，以及它用 `@path` 那一行 import 的每個檔案（被生成的
agent 能逐字引用 `coordination-rules.md`，卻沒有讀過它）。
這些檔案也要讀。那裡面陳述的規則，對每個 skill 和 agent 都算數：
要引用它來自哪個檔案。當 skill 或 agent 自己的檔案跟它矛盾時，
以自己的檔案為準：它是更具體的指示。

**對 agent 來說**，spec 的各個段落是對照 agent 檔案評估的：
也對照它 frontmatter 在 `skills:` 底下列出的每個 skill，Claude
Code 會在啟動時把這些載入 agent：

- **Static Assertions**：逐一對照 agent 的 frontmatter 和內文檢查。
  指名字面值的斷言（`model:` 別名、frontmatter key、
  工具名稱）是跟檔案做精確比對：`model: inherit` 不滿足
  "Model tier is `sonnet`"，接近的比對是 FAIL，絕對不是 PARTIAL。
- **Test Cases**：把每個案例預期的行為，對照 agent 寫下來的指示來評估，
  方式跟下面評估 skill 的一樣。點名 gate ID 的案例（`LP-FEASIBILITY`、`CD-PILLARS`……）
  就是那個 gate 的呼叫：生成它的 skill 會讓 agent 先讀
  `.claude/docs/director-gates/[gate-id].md`，所以那個檔案的 Prompt 和
  Verdicts 就是 agent 對這個案例的指示，也要讀它。
- **Redirect 和 escalation 案例**：agent 被要求做另一個角色負責的工作，
  或是遇到它自己無法解決的衝突。當已載入的 `coordination-rules.md` 涵蓋這個步驟時，案例就算達成：
  rule 2（領域之外不做有約束力的決定）、rule 3（把衝突升級給共同的上層）
  或 rule 5（沒有委派就不碰自己目錄以外的檔案），**而且**
  agent 自己的檔案在它的協作者、委派、升級或「禁止」清單裡點名了負責的角色。
  兩者都要引用；不要要求 agent 用自己的話
  重述這個轉交。當 agent 的檔案
  把那份工作攬給自己，或是沒有任何已載入的檔案點名負責的人時，就是 FAIL。
- **Protocol Compliance**：用 spec 自己的 `## Protocol Compliance` 清單，
  取代下面四項 skill 檢查。

**對 skill 來說**，把 spec 的每個 **Static Assertions** 對照
skill 的 frontmatter 和內文（`SKILL.md` 和它的 `references/` 檔案）用同樣的方式檢查；
字面值是精確比對。`/skill-test static` 只跑它固定的 7 項檢查，所以 spec 自己的 static 行：
結論關鍵字、phase、在某個指名檔案前面的 "May I write"，
要在這裡評估，不然就沒有任何地方會評估。

這個步驟的其餘部分適用於 skill 和 agent 兩者。

對 spec 裡每個 **Test Case**：

1. 讀 **Fixture** 描述（假設的專案檔案狀態）
2. 讀 **Expected behavior** 的步驟
3. 讀每個 **Assertion** 核取方塊

沒有 **Fixture** 的案例，把它的 **Input** 當作 fixture 來讀；沒有
**Assertions** 清單的案例，把每個 **Expected behavior** 項目當成斷言：
大多數 agent spec 都是這樣寫的，案例的結論不會只因為沒有獨立的核取清單就沒有定義。

對每個斷言，評估如果依 fixture 的狀態正確地照著 skill 寫下來的
指示去做，是否會滿足它。這是由 Claude 評估的推理檢查，
不是執行程式碼。

標記每個斷言：
- **PASS**：skill 的指示明確滿足這個斷言
- **PARTIAL**：skill 的指示部分涵蓋它，但有模糊之處
- **FAIL**：依 fixture 的狀態，skill 的指示不會滿足這個斷言
- **NOT ASSESSED**：這個斷言完全無法評估：它提到
  spec 從未定義的 fixture 狀態、依賴靜態閱讀無法決定的
  執行期行為，或是引用了不存在的檔案或段落（一個
  對該行為保持沉默的檔案是 FAIL 或 PARTIAL，不是這個）。排序是
  **高於 PASS**（沒人能評估的斷言，並沒有被滿足）而且
  **低於 PARTIAL 和 FAIL**（有人找出來的模糊之處，比沒人碰得到的
  更值得處理）。不要因為 skill「大概」處理了它，就把一個無法評估的斷言
  判成 PASS：那種判斷正是 spec 要取代的東西。

對 skill 的 **Protocol Compliance** 段落（一定會有），把 spec 自己清單的
每一行，用跟評估案例斷言完全一樣的方式，對照 skill 的檔案來評估：
PASS、PARTIAL、FAIL 或 NOT ASSESSED。spec 會把沒有案例重複的規則放在那裡
（「由上面的 protocol compliance 斷言涵蓋」），所以
沒有被評估的清單，就是一組沒人檢查的規則。當清單沒有涵蓋時，這四項檢查就是
要補上的底線：
- 檢查 skill 有沒有要求在寫檔前先 "May I write"
- 檢查 skill 有沒有在請求核准之前先呈現發現
- 檢查 skill 有沒有以建議的下一步作結
- 檢查 skill 有沒有避免在未經核准的情況下自動建立檔案

### Step 4 — Build Report

```
=== Skill Spec Test: /[name] ===
Date: [date]
Spec: studio-tests/skills/[category]/[name].md

Static Assertions:
  [PASS] [assertion text]
  [NOT ASSESSED] [assertion text]
     Reason: [why it could not be evaluated]

Case 1: [Happy Path — name]
  Fixture: [summary]
  Assertions:
    [PASS] [assertion text]
    [FAIL] [assertion text]
       Reason: The skill's Phase 3 says "..." but the fixture state means "..."
  Case Verdict: FAIL

Case 2: [Edge Case — name]
  ...
  Case Verdict: PASS

Protocol Compliance:
  [PASS] Uses "May I write" before file writes
  [PASS] Presents findings before asking approval
  [PARTIAL] No explicit next-step handoff at end

Overall Verdict: FAIL (1 case failed, 1 protocol line partial)
```

案例的結論取它斷言中最差的結果，整體結論則取
static 斷言、各案例和 Protocol Compliance 之中最差的，順序是：
FAIL、PARTIAL、NOT ASSESSED、PASS。沒人能評估的斷言，會讓
整體結果不會顯示成 PASS。

對 agent 來說，標題是 `=== Agent Spec Test: [name] ===`，`Spec:` 是它在
`studio-tests/agents/` 底下的路徑，而且 `Static Assertions:`
區塊要放在 Case 1 之前。

### Step 5 — Offer to Write Results

"May I write these results to `studio-tests/results/skill-test-spec-[name]-[date].md`
and update `studio-tests/catalog.yaml`?"

如果同意：
- 把結果檔寫到 `studio-tests/results/`
- 更新 `studio-tests/catalog.yaml` 裡該 skill 或 agent 的條目：
  - `last_spec: [date]`
  - `last_spec_result: PASS|PARTIAL|FAIL|NOT ASSESSED`：整體結論

---

## Phase 2D: Category Mode — Rubric Evaluation

### Step 1 — Locate Skill and Category

使用 Phase 1 解析出來的 skill 或 agent 檔案。
在 `studio-tests/catalog.yaml` 裡，它的 `skills:` 或 `agents:` 條目上查 `category:` 欄位。

如果兩個檔案都不存在：Phase 1 的訊息。
如果沒有 `category:` 欄位："No category assigned for '[name]' in catalog.yaml.
Add `category: [name]` to its entry first."

對 `category all`：收集每個有 `category:` 欄位的 skill 和 agent，
逐一處理，skill 和 agent 分開用不同的表格報告。
`category: utility` 的 skill 只對 U1（static 檢查通過）和 U2
（gate 模式正確，如果適用）評估：U1 跳到 static 模式。
對照 `.claude/skills/*/SKILL.md` 和 `.claude/agents/*.md`
（Audit 模式 Step 2 的 glob）交叉檢查：把 catalog 裡缺少、或有列入
但沒有 `category:` 的 skill 或 agent，逐一點名列為 **NOT ASSESSED**：絕對不要悄悄地
從這次執行中排除。

### Step 2 — Read Rubric Section

讀 `studio-tests/quality-rubric.md`。
擷取符合該類別的段落（例如 `### gate`、`### team`；agent 的類別
在 `## Agent Categories` 底下，例如 `### director`）。
如果評分標準沒有該類別的段落，結果就是 **NOT ASSESSED**：
點名缺少的段落，而且絕對不要借用別的類別的指標。

### Step 3 — Read Skill

完整讀 skill 的 `SKILL.md` 和它 `references/` 資料夾裡的每個檔案，或
agent 的 `.claude/agents/[name].md`，
以及 Phase 2B Step 3 描述的專案 context：一個由 `CLAUDE.md`
或它 import 的檔案裡的規則所滿足的指標，就算滿足，要引用那個檔案。
它對 redirect 和 escalation 案例的規則，也決定領域、延後和
升級的指標（D2、D3、L2、S1–S3、O2）。

### Step 4 — Evaluate Rubric Metrics

對該類別評分標準表格裡的每個指標：
1. 檢查 skill 或 agent 寫下來的指示是否明確滿足這個條件
2. 標記 PASS、FAIL、WARN 或 NOT ASSESSED（指標無法評估，要點名原因）
3. 對 FAIL/WARN/NOT ASSESSED，找出文字裡確切的缺口（引用
   相關段落、記下它的缺席，或點名無法評估的是什麼）

### Step 5 — Output Report

對 agent 來說，標題是 `=== Agent Category Check: [name] ([category]) ===`。

```
=== Skill Category Check: /[name] ([category]) ===

Metric G1 — Review mode read:      PASS
Metric G2 — Director panel width:  FAIL
  Gap: Phase 3 spawns only CD-PHASE-GATE at `workflow: full`; TD-PHASE-GATE, PR-PHASE-GATE, AD-PHASE-GATE absent
Metric G3 — Lean mode: PHASE-GATE only: PASS
Metric G4 — Solo mode: no directors:    PASS
Metric G5 — No auto-advance:       PASS

Verdict: FAIL (1 failure, 0 warnings)
Fix: Size the Phase 3 panel from `modes.workflow` — PR at `minimal`, TD + PR at
     `standard`, all four at `full` — and name any perspective a narrower panel leaves out.
```

類別結論，第一個符合的勝出：任何指標失敗就是 **FAIL**；否則
任何指標警告就是 **WARNINGS**；否則任何指標無法
評估（缺少評分標準段落、檔案讀不到）就是 **NOT ASSESSED**；否則
每個指標都通過就是 **PASS**：排序跟 static 和 spec 模式相同。它是
catalog 裡的 `last_category_result`。

### Step 6 — Offer to Update Catalog

"May I update `studio-tests/catalog.yaml` to record this category check
(`last_category`, `last_category_result`) for [name]?"

---

## Phase 2C: Audit Mode — Coverage Report

### Step 1 — Read Catalog

讀 `studio-tests/catalog.yaml`。如果不存在，註記 catalog 還
不存在（第一次執行的狀態）。

### Step 2 — Enumerate All Skills and Agents

Glob `.claude/skills/*/SKILL.md` 取得 skill 的完整清單。
從每個路徑擷取 skill 名稱（目錄名稱）。

Glob `.claude/agents/*.md` 取得 agent 的完整清單：repo 本身，
不是 catalog，才是被涵蓋的集合（`.claude/rules/skill-authoring.md` §5：
gate 是推導它涵蓋的集合，不是列舉它）。把兩個 glob
對照 catalog 的 `skills:`/`agents:` 條目，並把 catalog 裡缺少的
skill 或 agent 逐一點名報告，這樣沒登記的就不會悄悄漏掉。

### Step 3 — Build Skill Coverage Table

對每個 skill：
- 檢查 spec 檔案是否存在（用 catalog 裡的 `spec:` 路徑，或 glob `studio-tests/skills/*/[name].md`）
- 從 catalog 查 `last_static`、`last_static_result`、`last_spec`、`last_spec_result`、
  `last_category`、`last_category_result`、`category`（如果不在
  catalog 裡，就標成 "never" / "—"）
- 優先順序來自 catalog 的 `priority:` 欄位（critical/high/medium/low）

### Step 3b — Build Agent Coverage Table

對 catalog 的 `agents:` 段落裡的每個 agent：
- 檢查 spec 檔案是否存在（用 catalog 裡的 `spec:` 路徑，或 glob `studio-tests/agents/*/[name].md`）
- 從 catalog 查 `last_spec`、`last_spec_result`、`last_category`、
  `last_category_result`、`category`

### Step 4 — Output Report

```
=== Skill Test Coverage Audit ===
Date: [date]

SKILLS (74 total)
Specs written: 73 (99%) | Never static tested: 74 | Never category tested: 74

Skill                  | Cat      | Has Spec | Last Static | S.Result | Last Cat | C.Result | Priority
-----------------------|----------|----------|-------------|----------|----------|----------|----------
gate-check             | gate     | YES      | never       | —        | never    | —        | critical
design-review          | review   | YES      | never       | —        | never    | —        | critical
...

AGENTS (49 total)
Agent specs written: 49 (100%)

Agent                  | Category   | Has Spec | Last Spec   | Result | Last Cat | C.Result
-----------------------|------------|----------|-------------|--------|----------|----------
creative-director      | director   | YES      | never       | —      | never    | —
technical-director     | director   | YES      | never       | —      | never    | —
...

Top 5 Priority Gaps (skills with no spec, critical/high priority):
(none if all specs are written)

Skill coverage:  73/74 specs (99%)
Agent coverage:  49/49 specs (100%)
```

audit 模式不寫檔。

提議："Would you like to run `/skill-test static all` to check structural
compliance across all skills? `/skill-test category all` to run category rubric
checks? Or `/skill-test spec [name]` to run a specific behavioral test?"

---

## Phase 3: Recommended Next Steps

任何模式完成之後，提供符合當下情境的後續動作：

- `static [name]` 之後："Run `/skill-test spec [name]` to validate behavioral
  correctness if a test spec exists."
- 有失敗的 `static all` 之後："Address NON-COMPLIANT skills first. Run
  `/skill-test static [name]` individually for detailed remediation guidance."
- `spec [name]` PASS 之後："Update `studio-tests/catalog.yaml` to record this
  pass date. Consider running `/skill-test audit` to find the next spec gap."
- `spec [name]` FAIL 之後："Review the failing assertions and update the skill
  or agent, or the test spec, to resolve the mismatch."
- `audit` 之後："Start with the critical-priority gaps. Use the spec template
  at `studio-tests/templates/skill-test-spec.md` (agents:
  `agent-test-spec.md`) to create new specs."
