---
name: help
description: "我接下來該做什麼？卡住了或不知道要做什麼的時候用。"
argument-hint: "[optional: what you just finished, e.g. 'finished design-review' or 'stuck on ADRs']"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash(bash "*/.claude/skills/help/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash "*/.claude/skills/help/../../scripts/story-status.sh"), Bash(bash .claude/scripts/story-status.sh*), Bash(bash .claude/scripts/artifact-check.sh *), Bash(bash ".claude/scripts/artifact-check.sh" *), Bash(bash ./.claude/scripts/artifact-check.sh *), Bash(git log *)
model: haiku
---

# Studio Help — What Do I Do Next?

這個 skill 是唯讀的 — 它只回報發現，不會寫任何檔案。

這個 skill 會精確判斷你在遊戲開發流程的哪個位置，
並告訴你下一步是什麼。它是**輕量**的 — 不是完整稽核。要做完整的
缺口分析，請用 `/project-stage-detect`。

## Live Project State

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys project.stage,workflow`

這些在 skill 執行前就已經解析好了，直接用：

- config 區塊裡的 **`project.stage`** 是 Step 2 的權威階段
  — 它已經套用了 `project.yaml` → `production/stage.txt` 的 fallback，
  而且會保留含空格的值（`Systems Design`）。
- config 區塊裡的 **`workflow`** 是 Step 2 和 Step 5 用的 tier — 不要重讀。
- 如果沒有顯示 config 區塊，代表 shell 前處理被停用了；退回用
  `.claude/docs/config-resolution.md` 裡的預設值。

---

## Step 1: Read the Catalog

讀 `.claude/docs/workflow-catalog.yaml`。這是所有階段、
各階段的步驟（依序）、每個步驟是必要還是選用，以及
代表完成的產出物 glob 的權威清單。

---

## Step 1b: Find Skills Not in the Catalog

讀完 catalog 之後，用 Glob 找 `.claude/skills/*/SKILL.md`，取得所有已安裝 skill 的完整清單。
對每個檔案，從 frontmatter 取出 `name:` 欄位。

拿它跟 catalog 裡的 `command:` 值比對。任何名稱沒有出現在 catalog command 裡的 skill，
就是**未編入 catalog 的 skill** — 還是可以用，但不屬於
有 phase gate 的 workflow。

把這些收集起來給 Step 7 輸出用 — 以頁尾區塊的形式顯示：

```
### Also installed (not in workflow)
- `/skill-name` — [description from SKILL.md frontmatter]
- `/skill-name` — [description]
```

只有在至少有一個未編入 catalog 的 skill 時才顯示這個區塊。依使用者目前的階段，最多列
10 個最相關的（production 階段列 QA skill，production/polish 階段列 team
skill，依此類推）。

---

## Step 2: Determine Current Phase

**先從上面的 config 區塊取 `workflow`。** 如果是 `minimal`，
專案走的是 minimal 路徑，不是階段階梯：跳過這個步驟的其餘部分，
讀 session 脈絡（**Step 3**），然後直接去 **Step 4m**。在這個 tier，
不要去對應 `project.stage` — minimal 路徑上沒有任何東西會跑 `/gate-check`，所以
不管專案走到哪，stage 都還是 Concept，
而照著走 Concept 階段，會把已經有 story 的專案
送回概念文件、美術聖經和系統地圖。

否則，依這個順序檢查：

1. **從上面的 config 區塊取 `project.stage`** — 已經解析好了。把它的值對應到 catalog 的階段 key：
   - "Concept" → `concept`
   - "Systems Design" → `systems-design`
   - "Technical Setup" → `technical-setup`
   - "Pre-Production" → `pre-production`
   - "Production" → `production`
   - "Polish" → `polish`
   - "Release" → `release`

2. **如果兩者都沒設**，從產出物推斷階段（取最前進的那個）：
   - code root 有 10 個以上的原始碼檔 → `production`
   - `production/epics/**/story-*.md` 存在 → `pre-production`
   - `docs/architecture/adr-*.md` 存在 → `technical-setup`
   - `design/gdd/systems-index.md` 存在 → `systems-design`
   - `design/gdd/game-concept.md`（或 `design/game-brief.md`）存在 → `concept`
   - 什麼都沒有 → `concept`（全新專案）

3. **`workflow`** 已經在這個步驟開頭取得了（依
   `.claude/docs/workflow-modes.md`）。它決定選用文件
   要不要當成下一步浮出來（Step 5）。

---

## Step 3: Read Session Context

如果 `production/session-state/active.md` 存在就讀它 — 但只讀它的 STATUS
和 CHECKPOINT 區塊（schema：`.claude/docs/templates/session-state.md`）；
它們下面的敘述可能很長。找出標記
（`Grep pattern="<!-- /?(STATUS|CHECKPOINT) -->" path="production/session-state/active.md" output_mode="content" -n`），
然後從第一個到最後一個用 `Read` 讀。沒有標記的檔案是在 schema 之前寫的：改讀它
最後一個 `## Session Extract` 區塊。擷取：
- 最近在做什麼
- 任何進行中的任務或未解的問題
- STATUS 區塊裡目前的 epic/feature/task（如果有的話）

這會告訴你使用者剛做完什麼、或卡在哪 — 用它來讓輸出更貼近使用者。
每個 tier 都會做這步：在 `minimal`，它是 Step 4m 所依賴的
checkpoint 唯一的一次讀取（checkpoint 寫著「Next step: /story-done」
就代表工作已經寫好了）。從這裡開始，`minimal` 去 **Step 4m**，不是 Step 4。

---

## Step 4: Check Step Completion for the Current Phase

對目前階段的每個步驟（來自 catalog）：

### Artifact-based checks

**用確定性的方式解析 — 一次呼叫，不要每個步驟各 glob 一次：**

```
Bash: bash .claude/scripts/artifact-check.sh --phase [current-phase]
```

照寫的樣子執行，這裡和下面都一樣：從專案根目錄、用相對路徑 —
不要用絕對路徑、不要 `cd`、不要 `2>&1`。這個 skill 的權限授權就是比對這個形式；
其他形式都會要使用者核准。

它會對照工作目錄，評估 catalog 裡每個 `glob`、`pattern`、`min_count` 和 `any_of`，
每個步驟回報一行。狀態對應如下：

| status | Report as |
|---|---|
| `PRESENT` | **Complete** |
| `ABSENT` | **Incomplete** |
| `SHORT` | **Incomplete** — say how far short (`count=`/`min=` are given) |
| `PATTERN_MISS` | **Incomplete** — the file exists but lacks its marker; say so, since "missing" would send the user to recreate a file they already have |
| `NO_CHECK` | **MANUAL** if the step carries a `note=`, else **UNKNOWN** — completion is not trackable (e.g. repeatable implementation work) |

不要用 Glob/Grep 重新推導這些。特別是 `any_of`，它是一份
**替代方案**清單 — 符合一個就夠 — 手動評估很容易出現錯誤的
「incomplete」：`engine-setup` 只要 `project.yaml` 裡有 `engine.name`
**或**有舊版 `.claude/docs/technical-preferences.md` 裡的 `Engine:` 那行，就算滿足，
而 script 會回報是哪個替代方案符合（`alt=`/`match=`）。

**`NO_CHECK` 絕對不代表完成。** script 會在各列之前印一個 `NO_CHECK:` 總數；
如果一個階段大部分都是 NO_CHECK，就直白地講出來，不要暗示
這個階段快完成了。

### Special case: production phase — read `sprint-status.yaml`

當目前階段是 `production`，在做任何以 glob 為基礎的 story 檢查之前，先看有沒有
`production/sprint-status.yaml`。如果存在，就直接讀它：

- `status: in-progress` 的 story → 顯示為「currently active」
- `status: ready-for-dev` 的 story → 顯示為「next up」
- `status: done` 的 story → 算成完成
- `status: blocked` 的 story → 連同 `blocker` 欄位一起顯示為阻礙

這樣不用掃 markdown 就能拿到精確的逐 story 狀態。`implement` 和 `story-done` 這兩步
跳過 glob 產出物檢查 — 以 YAML 為準。

### Special case: `repeatable: true` (non-production)

對 production 以外的可重複步驟（例如「System GDDs」），產出物
檢查只能告訴你*有沒有*做過任何工作，不能告訴你做完了沒。
要用不同方式標示 — 顯示偵測到什麼，再註明它可能還在進行中。

---

## Step 4m: The Minimal Path (`workflow: minimal` only)

在 `minimal`，路線是 catalog 的 `paths.minimal`，不是某個階段：engine →
`design/game-brief.md` → stories → `/dev-story` ↔ `/story-done`。一次呼叫就解析出來：

```
Bash: bash .claude/scripts/artifact-check.sh --path minimal
```

狀態的對應方式跟 Step 4 完全一樣。`implement` 和 `story-done` 是
`NO_CHECK`，這是刻意的 — 下面的 story status 行就是它們的檢查。下一步
是下列條件中第一個符合的：

1. `engine-setup` 不是 PRESENT → `/setup-engine`
2. `game-brief` 不是 PRESENT → 當 code root
   已經有這款遊戲（有 10 個以上原始碼檔，也就是 Step 2 用來判斷
   `production` 的測試）就用 `/reverse-document design [code root]`：在 `minimal` 它會依
   已經做好的東西寫出 `design/game-brief.md`。否則用 `/brainstorm`（在 `minimal` 它會寫出
   一頁的 brief），但對已經做好的遊戲，它會開啟一個新點子。
3. `create-stories` 不是 PRESENT → 不帶參數的 `/create-stories`（在
   `minimal` 它直接從 brief 的 MVP 清單建出 story）
4. 已有 story → 下面的清單是在你讀這個 skill 之前，由 `.claude/scripts/story-status.sh`
   印出來的：每個未完成的 story 一行，**已經依
   路線的順序排好** — 先 `IN_REVIEW`，再 `IN_PROGRESS`，再 `TODO`（`Ready`
   或 `Not Started` 的 story）依 build order 排 — 然後是 `BLOCKED`、`OTHER`、
   `NO_STATUS` 和 `COMPLETE` 的數量：

!`bash "${CLAUDE_SKILL_DIR}/../../scripts/story-status.sh"`

   **Next up 是第一個 `IN_REVIEW`、`IN_PROGRESS` 或 `TODO`
   那一行的 story。** 清單已經是最新的；不要再跑一次 script，也
   不要重讀或重新排序 story 檔：
   `In Review` 的 story 要先結案，才輪到繼續做 `In Progress` 的 — 它的
   工作已經寫好了，而 `/story-done` 很快。
   - `IN_REVIEW` → 工作已經寫好，等著結案：
     `/story-done [path]`
   - `IN_PROGRESS` → 它**還沒**做完 — 不管程式碼或 commit
     看起來怎樣，只有 `/story-done` 能讓 story 變成 Complete。只有在使用者、`active.md` 或 git log 說
     它的實作已經寫好時，才建議
     `/story-done [path]`；否則建議 `/dev-story [path]` 繼續做
   - `TODO` → `/dev-story [path]`
   - `BLOCKED` 的 story → 點名它和它的 blocker；它絕對不會是 Next up
   - **沒有 `IN_REVIEW`、`IN_PROGRESS` 或 `TODO` 的行，但還有 `BLOCKED`、`OTHER` 或
     `NO_STATUS` 的行** → 接下來沒有東西可以做，而 build
     order **還沒**完成。點名這些 story 各自的 status（照原樣寫的），
     blocked 的 story 還要附上 blocker（從那個 story 的檔案讀）。
     Next up 就是清掉其中第一個：解決它的 blocker，或給
     `OTHER` 或 `NO_STATUS` 的 story 一個路線讀得懂的 `Status:` 行（一旦可以做了就寫 `Ready`）
   - **每個 story 都是 `Complete`（或 `Done`）** → brief 的 build order 做完了。
     要講出來，並提供三條路：玩玩看這個 build；用 `/create-stories` 從 brief
     加入下一批 story；或者，如果遊戲已經大到一頁 brief 裝不下，就用 `/settings` 把
     `modes.rigor` 調高。

**在 `minimal`，絕對不要把下面任何一項講成必要的或阻礙：** 遊戲
概念文件、美術聖經、系統地圖、GDD、`/create-epics`、sprint plan、
`/gate-check`，或 sprint 收尾（`/smoke-check`、`/team-qa`、
`/retrospective`）。brief 取代了設計文件，它的 build order
取代了 sprint plan（`.claude/docs/workflow-modes.md` — `minimal` 的底線）。
使用者要求的話，每一項還是可以跑；只有在
使用者的參數問到它時才提。

然後跳過 Step 5 和 Step 8，用 Step 7 裡 `minimal` 的格式呈現。

---

## Step 5: Find Position and Identify Next Steps

從完成度資料，判斷：

1. **最後一個確認完成的步驟** — 最前面的已完成必要步驟
2. **目前的 blocker** — 第一個未完成的*必要*步驟（這是
   使用者接下來一定要做的）
3. **選用的機會** — 可以在 blocker 之前或同時做的未完成*選用*步驟。**依 workflow tier 決定要不要列出**：在
   `full`，全部列出；在 `standard`，只有當某個選用文件
   對目前的 system/階段是必要時才列（不要把真正選用的文件標成
   缺口）。在 `minimal` 這個步驟不會執行 — 由 Step 4m 取代
4. **接下來的必要步驟** — 目前 blocker 之後的必要步驟
   （顯示成「coming up」，讓使用者可以提早規劃）

如果使用者有給參數（例如「just finished design-review」），就用它
跳過他們點名的那個步驟，即使產出物檢查的結果不明確。

---

## Step 6: Check for In-Progress Work

如果 `active.md` 顯示有進行中的任務或 epic：
- 把它顯眼地放在最上面：「It looks like you were working on [X]」
- 建議繼續做，或確認它是不是已經完成

---

## Step 7: Present Output

保持**簡短直接**。這是快速定位，不是報告。

```
## Where You Are: [Phase Label]

**In progress:** [from active.md, if any]

### ✓ Done
- [completed step name]
- [completed step name]

### → Next up (REQUIRED)
**[Step name]** — [description]
Command: `[/command]`

### ~ Also available (OPTIONAL)
- **[Step name]** — [description] → `/command`
- **[Step name]** — [description] → `/command`

### Coming up after that
- [Next required step name] (`/command`)
- [Next required step name] (`/command`)

---
Approaching **[next phase]** gate → run `/gate-check` when ready.
```

**在 `minimal`** 改用這個格式 — 不要階段標籤，不要 gate 那行。`N`
只計算 status 行寫 `Complete` 或 `Done` 的 story，也只有這些
放在 ✓ Done 底下。`N` 和 `M` 是 `COMPLETE` 那行的兩個數字；
它不會點名任何完成的 story，所以 ✓ Done 給的是數量，不是標題：

```
## Where You Are: Minimal path — [N] of [M] stories complete

**In progress:** [from active.md, if any]

### ✓ Done
- Engine: [engine] · Game brief · [N] stories

### → Next up
**[Story NNN: title]** — [what it delivers]
Command: `/story-done [story-path]` for an In Review story, or an In Progress one whose work is written; otherwise `/dev-story [story-path]`

### Coming up after that
- [the next Ready stories in build order, at most 3]
```

**格式規則：**
- `✓` 代表確認完成
- `→` 代表目前必要的下一步（只有一個 — 第一個 blocker）
- `~` 代表現在可以做的選用步驟
- 指令用行內 backtick code 顯示
- 如果某個步驟沒有指令（例如「Implement Stories」），就說明該怎麼做，不要顯示 slash command
- 對 MANUAL 步驟，問使用者：「I can't tell if [step] is done — has it been completed?」

Verdict: **COMPLETE** — next steps identified.

---

## Step 8: Gate Warning (if close)

在 `minimal` 跳過這個步驟 — minimal 路徑沒有 phase gate。

在目前階段的步驟之後，檢查使用者是不是快要碰到 gate 了：
- 如果目前階段所有必要步驟都完成了（或快完成了），
  加上：「You're close to the **[Current] → [Next]** gate. Run `/gate-check` when ready.」
- 如果還剩好幾個必要步驟，就跳過 gate 警告 — 現在還不相關。

---

## Step 9: Escalation Paths

給完建議之後，如果使用者看起來卡住或困惑，加上：

```
---
Need more detail?
- `/project-stage-detect` — full gap analysis with all missing artifacts listed
- `/gate-check` — formal readiness check for your next phase
- `/start` — re-orient from scratch
- `/settings` — if the process feels mismatched to your project, adjust
  `modes.rigor`. Apply the change-triggers in
  `.claude/docs/settings-guidance.md § 4`: a **lower** tier when the user sounds
  overwhelmed by process (and rigor isn't already `minimal`), or a **higher** tier
  when the project has outgrown it (many systems, or in Production on
  `workflow: minimal`)
```

只有在使用者的輸入透露出困惑時才顯示這個（例如「I don't know」、「stuck」、
「lost」、「not sure」）。單純問「what's next?」就不要顯示。
只有在 `settings-guidance.md § 4` 的觸發條件真的成立時，才顯示 `/settings` 的 rigor 那行 —
使用者聽起來被流程壓垮了（而且 rigor 還不是 `minimal`），或專案
已經超出它的 tier — 不是每次困惑的詢問都顯示。在 `minimal`，省略
`/gate-check` 那行：minimal 路徑沒有 phase gate（Step 4m）。

---

## Collaborative Protocol

- **絕對不要自動執行下一個 skill。** 推薦它，讓使用者自己叫用。
- **MANUAL 步驟要問使用者**，不要假設完成或未完成。
- **配合使用者的語氣** — 如果他們聽起來壓力很大（「I'm totally lost」），
  就安撫他們，並給一個行動，不要給六個的清單。
- **只給一個主要建議** — 使用者離開時應該清楚知道接下來
  就只有一件事要做。選用步驟和「coming up」只是次要脈絡。
