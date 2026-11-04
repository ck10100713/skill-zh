---
name: start
description: "引導第一次使用的人完成入門，並挑選合適的工作流程。使用時機：使用者是新手、剛 clone 或安裝這個 studio、還沒有想法或引擎、問要從哪裡開始，或是想把既有的遊戲帶進來。"
argument-hint: "[no arguments]"
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Bash(bash .claude/scripts/project-state.sh*), Bash(bash .claude/scripts/set-stage.sh *), Bash(bash .claude/scripts/config-set.sh *)
model: sonnet
---

# Guided Onboarding

新使用者的進入點。它假設你沒有遊戲點子、沒有引擎，也沒有經驗：它會讀
專案、問使用者從哪裡開始、顯示它對專案做了什麼假設，
並指出唯一的下一步。它絕對不會自己去執行那一步。

它會把這些設定寫進 `project.yaml`，全部透過 helper，而且只在明確的 yes 之後：
`project.stage`（連同它的舊版鏡像 `production/stage.txt`）、`modes.rigor` 和
`modes.automation`。它絕對不會寫 `modes.review_mode` 或 `production/review-mode.txt`，也不會寫
rigor 管理的其他任何設定（`modes.workflow`、`docs.density`、`qa.level`、
`modes.story_granularity`、`team.size`）：寫入的值會把那個設定釘在 rigor 展開之上，
而鏡像檔案的優先順序比它更高。

用提問工具來問。沒有提問工具的話，把選項編號列出來，然後結束你的回合等待。
問題是回覆裡的最後一樣東西：它後面不准有路徑、註記或建議。被略過或關閉的
問題不算回答：要用純文字再問一次。

Phase 2、4 和 5 的問題會塑造專案，所以在每一種自動化模式下都要問。
引擎不在其中：由 `/setup-engine` 來選。Phase 6 的最後一個問題遵循
`project.yaml` 裡已有的 `modes.automation`，依
`.claude/docs/automation-modes.md`；沒有設定的話，就問它。

## Phase 1: Read the project

執行 `bash .claude/scripts/project-state.sh` 並保留它的各列。先不要顯示；它們用來
檢查 Phase 2 使用者的回答。

| Row | Use |
|---|---|
| `engine`, `code_root`, `source_files` | 有沒有設引擎，以及有多少程式碼。`source_files` 是 `unknown` 代表找不到程式碼根目錄：要這樣說，絕對不要說「沒有程式碼」 |
| `concept` | `design/gdd/game-concept.md` 或 `design/game-brief.md` 存在 |
| `gdd_files`, `adr` | 磁碟上的設計文件和架構決策（它們在 Phase 4 決定階段） |
| `prototype`, `sprint`, `milestone`, `story` | 其他既有的工作 |
| `origin_url` | 包含 `donchitos/claude-code-game-studios`，比對時不分大小寫：這個 clone 仍然指向範本 repo，所以 push 或 pull request 會送到那裡。在其他擁有者底下的 fork 是使用者自己的 |
| `stage` | 已經記錄的階段，如果有的話 |

忽略 `phase_inferred`：它是從檔案數量猜的，而一個有程式碼但沒有設計
文件的專案不在 Production。如果 helper 失敗，要說出來，並手動讀同樣的事實
（`project.yaml` 裡的引擎、那兩個 concept 檔案、程式碼根目錄的檔案、`design/gdd/`）。

helper 不會回報 rigor 或 automation。如果 `project.yaml` 存在就讀它，並記下
`modes.rigor` 和 `modes.automation` 有沒有設定：已設定的值要保留，它的問題
不要問（Phase 4 和 5）。

**回來的使用者**（已設定引擎，而且 `concept` 存在）：什麼都不要問。說出引擎、
找到的 concept 或 brief，以及 review mode：如果有設就是 `modes.review_mode`，否則就是
`modes.rigor` 所暗示的那個（`minimal` → `solo`、`standard` → `lean`、`full` → `full`）。建議用 `/help` 找下一步，如果適用就加上
範本 remote 的註記，然後停下來。

## Phase 2: Ask where the user is

用提問工具問："Welcome! Where are you starting from with your game?" 選項：
- `A) No idea yet`：沒有遊戲概念；去探索並找出要做什麼。
- `B) Vague idea`：一個主題、一種感覺或類型（"something with space"、"a cozy farming game"）。
- `C) Clear concept`：核心想法和類型都知道了，但還沒寫下來。
- `D) Existing work`：已經有設計文件、原型、程式碼或計畫。

等待回答。如果它跟 Phase 1 矛盾，把你找到的東西說一次，然後再問：
在空專案上選 D（"this looks like a fresh template; would A or B fit better?"），
或是磁碟上有程式碼卻選 A（"I found code in `[code_root]`; did you mean D?"）。如果沒有選項符合，讓使用者描述
他們的情況，並依那個去分流。

## Phase 3: Route

只指出眼前的下一步。完整的路徑等到 Phase 6，在知道 rigor 之後再說。

- **A，沒有想法：** 從零開始沒問題。`/brainstorm open` 是自由探索；`/brainstorm
  [hint]` 從一個字或主題開始。下一步：`/brainstorm open`，如果想得到提示，就用提示。
  把它描述成 "turns no idea into a written design the next step builds from"；
  那份設計多長取決於 rigor，所以留到 Phase 6 再說。
- **B，模糊的想法：** 請對方用幾個字說出想法，照單全收，並指出
  `/brainstorm [their words]`。
- **C，清楚的概念：** 請對方用一句話說出概念（類型和核心機制），用純文字。然後問："How would you like to proceed?" 選項：`Formalize it first`（`/brainstorm
  [concept]` 把它寫下來）/ `Jump straight in`（現在就 `/setup-engine`，之後再寫設計）。
  下一步就是他們選的。
- **D，既有的工作：** 說出 Phase 1 找到的東西（"N source files under `[code_root]`, N design
  documents, engine [X / not set]"）。下一步：沒有設引擎、而且頂多只有一個概念時，用 `/setup-engine`；
  否則用 `/project-stage-detect`。

然後說："I'll lay out the full path in a moment."

## Phase 4: Show what you assume, then save it

算出兩個值。

**階段。** 路徑 A、B 和 C：`Concept`。路徑 D，從 Phase 1 的各列判斷：

| On disk | Stage |
|---|---|
| 沒有引擎，或除了概念之外什麼都沒有（`gdd_files` 為 0） | `Concept` |
| `gdd_files` 1 個以上，`adr` 為 0 | `Systems Design` |
| `adr` 1 個以上 | `Technical Setup` |

**Rigor。** 如果 `modes.rigor` 在 `project.yaml` 裡已經設定，保留它並說出來。否則
從使用者在 Phase 2 和 3 說的話推論，使用
`.claude/docs/settings-guidance.md` §3 裡的訊號：

| 使用者的話提到 | Rigor |
|---|---|
| open world、RPG、sim、sandbox、factions、crafting、economy、MMO、multiplayer、many systems | `full` |
| release、commercial、Steam、one clear core loop | `standard` |
| jam、weekend、prototype、first game、small、just trying | `minimal` |
| 以上都沒有，或還沒有想法 | `minimal`（預設） |

路徑 B 的提示仍然算是一種描述："some kind of open-world survival sim" 就是 `full`。

顯示這張卡片：

```
What I'll set up
  Stage:  [stage]  ([why, from what was found or picked])
  Rigor:  [value]  ([why, in the user's words] | already set)
          minimal: short brief, coarse stories, tests optional; about 4 steps to code
          standard: about 8 design documents before code; standard QA evidence
          full: everything in standard plus validation builds; evidence everywhere
  /settings changes either of these any time.
```

然後用提問工具問："Save these to `project.yaml` (and the stage to
`production/stage.txt`)?" 選項：`Save them` / `Don't save`。不要問關於 rigor
本身的問題：卡片已經顯示了它，而 `/settings` 可以改它。

- **Save them：** 執行 `bash .claude/scripts/set-stage.sh "[stage]"`，然後，只有在 rigor 還沒設定時，
  執行 `bash .claude/scripts/config-set.sh modes.rigor [value]`。檢查讀回來的各列
  是否相符。說："Saved. Rigor `[value]` sets six other settings; `/settings` shows them and changes
  any of them."
- **Don't save**，或任何不是明確 yes 的回答：什麼都不寫，在這次執行中保留這些值，並說
  它們沒有被儲存。

如果 helper 以非零狀態結束，顯示它的輸出，說明哪個設定沒有寫入，並用
這次執行的值繼續。

## Phase 5: Ask how much to confirm

如果 `modes.automation` 已經設定，說 "Automation is `[value]`" 然後繼續。否則問：
"Last one: how much should I confirm with you as we work?" 選項：
- `Guided (Recommended)`：小事我自己決定，大事仍然會停下來問（範圍改變、
  刪除、schema 變更）。
- `Collaborative`：每個重要步驟之前都先問，寫入之前先顯示草稿。
- `Autonomous`：我直接進行並記錄決定，只有在一律詢問的類別才停下來。最快，
  token 用得最多。

對應：`Guided` → `guided`、`Collaborative` → `collaborative`、`Autonomous` → `autonomous`。
這個選擇就是寫入它的同意：執行 `bash .claude/scripts/config-set.sh modes.automation [value]`，
除非 Phase 4 的儲存被拒絕了（那就說它沒有被儲存）。

## Phase 6: Show the path

說："Here's your path at rigor `[value]`. Every skill still runs at any rigor; rigor changes
what's required, not what's allowed."

路徑從 Phase 3 指出的那個步驟開始。當那是 `/brainstorm`（路徑 A 和 B，以及 C 的
`Formalize it first`）時，把 `/brainstorm` 列第一、`/setup-engine` 列第二：各自
不需要另一個就能執行。

**`minimal`：4 個步驟到能跑的程式碼**
1. `/setup-engine`：選擇並設定引擎
2. `/brainstorm`：寫出一頁的 `design/game-brief.md`
3. `/create-stories`：把 brief 的 MVP 清單轉成 story（不需要 epic 或 sprint 計畫）
4. `/dev-story`：第一行遊戲程式碼

**`standard`**
- Concept：`/setup-engine` → `/brainstorm` → `/prototype` → `/art-bible` → `/gate-check`
- Systems Design：`/map-systems` → `/design-system`（每個系統一次）→ `/review-all-gdds` →
  `/gate-check`
- Architecture：`/create-architecture` → `/architecture-decision`（每個決策一次）→
  `/create-control-manifest` → `/architecture-review` → `/test-setup` → `/ux-design`
  （無障礙和互動模式）→ `/gate-check`
- Pre-Production：`/ux-design`（HUD 和主要畫面）→ `/create-epics` → `/create-stories` →
  `/sprint-plan` → `/gate-check`
- Production：`/dev-story`

每個 `/gate-check` 讓專案前進一個階段，而且只有在通過時才會。

**`full`：** 包含 `standard` 的全部，再加上 Pre-Production 裡的 `/vertical-slice` 和 `/playtest-report`，
以及每份 GDD 之後的 `/design-review`。

**路徑 D 帶有既有的工作**（階段是 `Systems Design` 或更後面，或磁碟上有程式碼）改用這個。
只印出適用的步驟，而 brief 只印出適用的那一個來源。在 `minimal` 時：
1. `/project-stage-detect`：專案在哪個階段，以及缺了什麼
2. `/adopt`：既有的檔案是不是 skill 讀得懂的格式
3. `/setup-engine`：只有在沒有設引擎時；`engine` 有指名引擎時就省略
4. brief，只有在 `concept` 不存在時：當程式碼根目錄有 10 個以上的原始碼檔案時，用 `/reverse-document design [code_root]`
   （它會從遊戲寫出 brief），這時完全不要提到
   `/brainstorm`；少於 10 個時才用 `/brainstorm`

在 `standard` 和 `full` 時，步驟 1 到 3，然後 `/design-system retrofit [path]`、
`/architecture-decision retrofit [path]`、`/architecture-review` 和 `/gate-check`。

把 `minimal` 呈現成有文件依據的底線，不是比較差的模式，並且說一次它的取捨：沒有 GDD，所以
設計問題會在程式碼裡才浮現。

如果 `origin_url` 指向範本 repo，加上："Your clone's `origin` still points at the
CCGS template repo, so a push or pull request would go there. When you're ready, run
`git remote rename origin template`, then `git remote add origin <your repo URL>`. `UPGRADING.md`
pulls updates from `template`; skip its own `git remote add template` step, since that remote now
exists." 建議它；不要執行它。

問："Would you like to start with [first step]?" 選項：`Yes, start with [first step]` /
`Something else first`。不管哪個答案都進入 Phase 7，絕對不會去執行那個步驟。

## Phase 7: Hand off

只回應一行："Type `[skill]` to begin." 不要啟動那個 skill，也不要為它呼叫
skill 工具，即使在 yes 之後也一樣：由使用者自己輸入。如果他們選了別的，就用同樣的方式
點名那個對應的 skill。

結論：**COMPLETE**，使用者已經了解狀況並完成交接。如果使用者在 Phase 7 之前就停了，
說明哪些設定已儲存、哪些沒有。
