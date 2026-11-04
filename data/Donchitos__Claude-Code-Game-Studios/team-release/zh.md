---
name: team-release
description: "統籌發布團隊（release-manager、qa-lead、devops-engineer、producer），把發布從候選版本一路執行到 deploy。"
argument-hint: "[version number or 'next'] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-release/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team Release

**參數檢查：** 如果沒有提供版本號：
1. 讀 `production/session-state/active.md` 和 `production/milestones/` 裡最近的檔案（如果存在），推斷目標版本。
2. 如果找到版本：回報「No version argument provided — inferred [version] from milestone data. Proceeding.」然後用 `AskUserQuestion` 確認：「Releasing [version]. Is this correct?」
3. 如果找不到任何版本：用 `AskUserQuestion` 問「What version number should be released? (e.g., v1.0.0)」，等使用者輸入後才繼續。絕對不准預設一個寫死的版本字串。

呼叫這個 skill 時，用結構化的 pipeline 來統籌發布團隊。

**決策點：** 每個 phase 轉換時，用 `AskUserQuestion` 把 subagent 的提案做成可選項目給使用者選。先在對話中寫出 agent 的完整分析，再用簡短的標籤收下決定。
在 `collaborative` 模式下，使用者核准後才能進下一個 phase。
在 `guided` 模式下，pipeline 會自動往下走，除非某個 phase BLOCKED；
在 `autonomous` 模式下會從頭跑到尾，每個 phase 的結果用 `log_decision` 記錄下來。
屬於 `automation_always_ask` 類別的決策（`is_always_ask_category` helper）不管什麼模式一律要問。參見 `.claude/docs/automation-modes.md`。

## Phase 0: Resolve Config

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size,workflow,project.stage`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，就用 `.claude/docs/config-resolution.md` 裡的預設值。

**階段檢查：在 spawn 任何東西之前。** 這個 skill 會把東西發布出去，而 `/gate-check release` 是必須先通過的就緒 gate；只有它的 PASS 才會把 `project.stage` 設成 `Release`。如果解析出來的 `project.stage` 是別的值（`Polish`、更早的階段，或沒設定），就在 Phase 1 之前停下，什麼都不要 spawn：

> "The release readiness gate has not passed (project.stage: [stage]) — run
> `/gate-check release` first."

然後用 `AskUserQuestion` 問，在每個 `automation` 模式下都要問，絕對不會替使用者做出放行的決定：`[A] Stop — I'll run /gate-check release (recommended)`
/ `[B] Proceed anyway — override the stage check`。選 `[A]`：結束這次 run，Verdict **BLOCKED** — release gate not passed。選 `[B]`：用純文字問原因，然後把這次放行記成 `Stage override: project.stage was [stage] — release gate not
passed; the user chose to proceed: [reason]`，寫進 Phase 1 的 brief、go/no-go 紀錄（`go-no-go-[version].md`）和最終報告。放行絕對不會改動 stage 本身。

`review_mode` 決定 director gate 的深度，而這條 pipeline 沒有 director gate：
下面任何 phase 在任何 `review_mode` 下，都不會 spawn CD-、TD-、PR- 或 AD-PHASE-GATE。它的 phase gate 就是 pipeline 自己的決策點（定義在下面的 `team.size` 底下），在這些點上工作的 agent 是團隊成員，不是 director gate。

`automation` 決定上面「決策點」那段的行為。各模式如何改變 pipeline 的行為，見上面的決策點說明和 `.claude/docs/automation-modes.md`。

**`team.size`**：哪些 agent 啟用（跟 review_mode 的 gate 深度和 workflow docs 互相獨立）。
- **`individual`**（預設）：只有 `release-manager`。其他 agent 透過 release-manager 諮詢，不會另外 spawn。
- **`small`**：加上 `producer` + `devops-engineer` + `qa-lead` + `community-manager`。
- **`studio`**：再加上 `security-engineer` + `analytics-engineer` + `localization-lead` + `performance-analyst`，遊戲是多人遊戲時再加 `network-programmer`（也就是文件中寫的完整 pipeline）。
在 `individual` 下需要用到的非核心 agent，會改由最接近的核心 agent 處理，並附一則說明。**「Phase gate」指的是這條 pipeline 自己列出、以 `AskUserQuestion` 決策點收尾的任何 phase**：可能是上面「決策點」底下的某個轉換、階段檢查，或 Phase 6 的 deploy 問題，**不管 `automation` 是哪個模式都一樣。** `guided` 和 `autonomous` 改變的是 gate 怎麼通過（自動往下走，或用 `log_decision` 記錄），不是它算不算 gate，所以下面的有界例外條件 (3) 在每個模式下的 gate 都成立。被限制成「只在 phase gate 出場」的 agent，只會在這些時點 spawn，其他時候不會。這個「依啟用名單縮小範圍」的規則適用於下面整條 pipeline：任何 phase 只要點名了啟用名單以外的 agent，就改由最接近的核心 agent 處理，不 spawn 它。

**在 Phase 1 之前先公布啟用名單，絕對不准讓縮減悄悄發生。**
spawn 任何東西之前，先用一行講清楚這次實際會 spawn 哪些 agent，以及下面 pipeline 有點名、但在目前 `team.size` 下**不會** spawn 的有哪些。例如：

> `Active set (team.size: <resolved>): <the agents listed for that size above>.`
> `Not spawned this run: <every other agent this pipeline names> — consulted`
> `through <nearest active core agent>. Raise team.size (or modes.rigor) to widen.`

內容要直接從上面的 `team.size` 清單和這個檔案自己的 pipeline 所點名的 agent 填，不要照抄範例。每個 orchestrator 這兩組名單都不一樣。

下面這條 pipeline 看起來像多 agent 的 fan-out，但在預設值下其實只有一兩個 agent：`team-release` 點名了十個、只跑一個，`team-narrative` 在五個 phase 裡點名了六個、只跑 `writer` 一個。**這樣縮減是對的**：`team.size` 是以嚴謹度為前提的，預設收窄就是用來省 token 的。
如果不明講，讀的人就分不出「正確縮減過的 run」和「壞掉的 pipeline」，而上面那條「由最接近的核心 agent 處理並附說明」的規則是在路由當下才觸發，從來不會交代整個 run 的樣子。

這跟這個檔案其他地方的「略過的檢查要回報」是同一條規則：**一個有被執行、卻從沒被講出來的限制，對讀輸出的人來說，跟從來沒執行過的限制看起來一模一樣。**

## Team Composition
- **release-manager** — 發布 tag、版本管理、changelog、patch notes、deploy
- **qa-lead** — 測試簽核、回歸測試套件、發布品質 gate
- **devops-engineer** — 建置管線、產物、deploy 自動化
- **security-engineer** — 發布前的安全稽核（遊戲有線上／多人功能或玩家資料時才叫）
- **network-programmer** — 網路程式碼穩定性簽核（遊戲有多人功能時才叫）
- **analytics-engineer** — 驗證遙測事件有正確觸發、儀表板已經上線
- **localization-lead** — 驗證每個要上線的字串都已翻譯
- **performance-analyst** — 把發布版 build 對照它的效能目標做 benchmark
- **community-manager** — 上線公告與面向玩家的訊息，依 patch notes 撰寫
- **producer** — go/no-go 決策、利害關係人溝通、排程

## How to Delegate

用 `Agent` 工具把每個團隊成員 spawn 成 subagent：
- `subagent_type: release-manager` — 發布 tag、版本管理、changelog、patch notes、deploy
- `subagent_type: qa-lead` — 測試簽核、回歸測試套件、發布品質 gate
- `subagent_type: devops-engineer` — 建置管線、產物、deploy 自動化
- `subagent_type: security-engineer` — 針對線上／多人／資料功能的安全稽核
- `subagent_type: analytics-engineer` — 遙測事件驗證與儀表板就緒度
- `subagent_type: community-manager` — 上線溝通，依 patch notes 撰寫
- `subagent_type: producer` — go/no-go 決策、利害關係人溝通
- `subagent_type: network-programmer` — 網路程式碼穩定性簽核（遊戲有多人功能時才叫）
- `subagent_type: localization-lead` — 翻譯完整度簽核（Phase 4）
- `subagent_type: performance-analyst` — 對照目標的效能 benchmark（Phase 4）

**給每個 agent 的 brief 要精簡，不要整包 context 倒過去。** 共用的輸入只讀**一次**，再把整理過的 brief 直接寫在 prompt 裡：只放每個 agent 真正需要的那幾行，你已經讀過的文件絕對不要只丟檔案路徑（agent 拿到路徑會把整份檔案重讀一遍）。只有你還沒讀、而且只有那個 agent 需要的文件，才給路徑。

**每個 agent 的 prompt 結尾都要加上回傳約定：**「Write your full output to `[path]` — that named path is your write authorisation under the bounded exception below, so write it without a separate approval prompt. Return **only** (1) the path written, (2) a ≤5-bullet summary of decisions, (3) any BLOCKED/CONCERNS items, one line each. Do not restate the documents you read.」沒有這個約定的話，agent 會把它讀過的東西全部倒回這個 session。

**`[path]` 要換成真實路徑。** 每個 agent 一個檔案，放在
`production/releases/` 底下，只有兩個例外，它們的位置在別處固定好了。啟用中的 agent 代替名單外的 agent 時，寫的是被代替的那個 agent 的檔案：

| Phase / agent | Writes to | Destination fixed by |
|---|---|---|
| 1 producer | `production/releases/release-plan-[version].md` | this skill |
| 2 release-manager | `production/releases/release-checklist-[version].md` | `/release-checklist` |
| 3 qa-lead | `production/releases/qa-gate-[version].md` | this skill |
| 3 devops-engineer | `production/releases/build-[version].md` | this skill |
| 3 security-engineer | `production/releases/security-signoff-[version].md` | this skill |
| 3 network-programmer | `production/releases/netcode-signoff-[version].md` | this skill |
| 4 localization-lead | `production/releases/localization-signoff-[version].md` | this skill |
| 4 performance-analyst | `production/releases/performance-signoff-[version].md` | this skill |
| 4 analytics-engineer | `production/releases/analytics-signoff-[version].md` | this skill |
| 5 go/no-go | `production/releases/go-no-go-[version].md` | this skill |
| 6 release-manager | `docs/patch-notes/[version].md` | `/patch-notes` |
| 6 community-manager | `production/releases/announcement-[version].md` | this skill |
| 7 release-manager | `production/releases/release-report-[version].md` | this skill |

> **這十三個輸出，每一個都需要指名目的地。** `production/releases/` 是 `/release-checklist` 本來就在寫的地方，而 `docs/patch-notes/[version].md` 是 `/patch-notes` 本來就在寫的地方，所以不管是哪個 skill 產出的，發布紀錄都會落在同一個地方。
>
> **每個 agent 一個獨立檔案，不是把一份紀錄一路附加下去。** Phase 3 和 Phase 4 會平行 spawn agent；兩個 agent 附加寫入同一個檔案會產生競爭，輸的那一方的章節會悄悄消失。

> **為什麼這不違反 Collaboration Protocol。** `CLAUDE.md` 要求 agent 在 Write/Edit 之前先問「May I write this to [filepath]?」。這裡 spawn 出來的 subagent **不問**就寫，這是刻意設計的有界例外，不是疏忽，跟 `consistency-check` 附加寫入 `active.md` 是同一個決定。這個例外只在三個條件**同時**成立時才有效：(1) 路徑是**你**在 prompt 裡指定的，所以使用者核准這個 phase 的時候，就等於核准了目的地；(2) 它是 `production/`、`docs/` 或 `tests/` 底下的新產物，絕對不是改既有的原始碼或設定；(3) 產生它的那個 phase，本身在 pipeline 往下走之前有 `AskUserQuestion` 把關。這三條以外，agent 一定要先問。**不要靠「每個 subagent 都問一次」來「修」這件事**：每個 agent 每個 phase 都跳一次提示，會讓 orchestrator 根本沒辦法用，這就是這個例外存在的原因。

只要 pipeline 允許，就把互相獨立的 agent 平行啟動（例如 Phase 3 的 agent 可以同時跑）。

## Pipeline

### Phase 1: Release Planning
委派給 **producer**：
- 確認所有 milestone 驗收標準都已達成
- 找出任何從這次發布延後的範圍項目
- 設定目標發布日期並通知團隊
- 輸出：附範圍確認的發布授權

### Phase 2: Release Candidate
委派給 **release-manager**：
- 在 `main` 上，把所有相關檔案裡的版本號升上去；帶著這次升版的 commit 就是 release candidate。開發是 trunk-based：一次發布就是 `main` 上的一個 tag（在 Phase 6 打上），不是一個 branch
- 確認 Polish 階段的發布檢查表（`/release-checklist`，在 `/gate-check release` 之前跑）對這個候選版本是完整的；只有在不存在任何檢查表時，才現在跑它
- 只有這次發布需要穩定化（凍結、平台認證）時，才從候選版本切出 `release/[version]` branch：那裡只修 bug，而且每個修正也都要落在 `main` 上
- 輸出：release candidate 的 commit（如果有切 `release/*` branch，也一併附上）與檢查表

### Phase 3: Quality Gate (parallel)
平行委派：
- **qa-lead**：執行完整的回歸測試套件。測試所有關鍵路徑。驗證在這個 `workflow` 下，`/gate-check release` 會擋的嚴重程度都沒有未結的 bug：每個層級的 S1，在 `full` 下連 S2 和 S3 也是。簽核品質。
- **devops-engineer**：為所有目標平台建置發布產物。驗證 build 乾淨且可重現。在 CI 裡跑自動化測試。
- **security-engineer** *（如果遊戲有線上功能、多人功能或玩家資料）*：進行發布前的安全稽核。審查驗證機制、反作弊、資料隱私合規。簽核安全態勢。
- **network-programmer** *（如果遊戲有多人功能）*：簽核網路程式碼的穩定性。驗證 lag compensation、斷線重連處理，以及負載下的頻寬使用。

只要這兩個 agent 任何一個在啟用名單內，就根據 `project.yaml` 裡的 `platform.online` 和 `platform.multiplayer`，加上遊戲有沒有儲存玩家資料，來決定它的條件。不存在的 key 不等於 `false`：要問使用者，不要假設是離線遊戲。基於這些理由而被略過的 agent，要在 Phase 3 的輸出裡點名講明，例如 `security-engineer: not spawned — platform.online: false, platform.multiplayer: false, no player data`。

### Phase 4: Localization, Performance, and Analytics
委派（資源允許的話，可以跟 Phase 3 平行）：
- 驗證所有字串都已翻譯（可用的話，委派給 **localization-lead**）
- 對照目標跑效能 benchmark（可用的話，委派給 **performance-analyst**）
- **analytics-engineer**：驗證所有遙測事件在發布版 build 上都有正確觸發。確認儀表板有收到資料。檢查關鍵漏斗（新手引導、進度、適用的話還有營利）都有埋點。
- 輸出：在地化、效能與分析的簽核，每個 agent 一個檔案（見上表）

### Phase 5: Go/No-Go
委派之前，先拿到 **technical-director** 的發布簽核。producer 不能 spawn agent，所以由 orchestrator 來做：只有在 `review_mode: full` 時才 spawn `technical-director`，這是 director 審查，不是 PHASE-GATE，所以 `lean` 和 `solo` 會跳過。請它針對 release candidate 的技術狀態，回覆 GO、CONCERNS 或 NO-GO，或是 NOT ASSESSED 並指明它讀不到什麼。沒有 spawn 它的時候，go/no-go 紀錄要寫 `technical-director sign-off: not run
(review_mode: <mode>)`，而不是把它列成已經給過簽核；NOT ASSESSED 的回答要照實記錄，絕對不算成簽核。

委派給 **producer**，並把到目前為止收集到的每份簽核都傳給它：
- 收集以下各方的簽核：qa-lead、release-manager、devops-engineer、security-engineer（如果在 Phase 3 有 spawn）、network-programmer（如果在 Phase 3 有 spawn），以及 technical-director（如果上面有 spawn）
- 如果有階段檢查的放行，就把它當作 `Stage override:` 那一行，帶進 go/no-go 紀錄
- 評估任何未結問題：是會擋發布的，還是可以帶著上線？
- 做出 go/no-go 的決定
- 輸出：附理由的發布決定

**如果 producer 宣告 NO-GO：**
- 立刻揭露這個決定：「PRODUCER: NO-GO — [rationale, e.g., S1 bug found in Phase 3].」
- 用 `AskUserQuestion` 提供選項：
  - 修好 blocker，重跑受影響的 phase
  - 把發布延到之後
  - 附書面理由，強行推翻 NO-GO（使用者必須提供書面說明）
- **整個跳過 Phase 6**：不要打 tag、不要 deploy 到 staging、不要 deploy 到 production、也不要 spawn community-manager。
- 產出一份部分報告，摘要 Phase 1–5，以及被跳過的部分（Phase 6）和原因。
- Verdict: **BLOCKED** — release not deployed.

使用者選了「Override NO-GO with documented rationale」之後：
- 問（用純文字，不要用 widget）：「Please describe the justification for overriding the NO-GO verdict. This will be embedded in the release record.」
- 等使用者寫下理由。
- 在 Phase 6 之前，把這段理由文字嵌進部分核准紀錄：附加一個「⚠️ Override Justification: [user's text]」欄位。
- 然後才進 Phase 6。

### Phase 6: Deployment (if GO)

**不管 `modes.automation` 是什麼，這個 phase 一律需要使用者的明確核准，連 `autonomous` 模式也一樣。** 正式環境 deploy 不可逆、風險又高；它不在可設定的 `automation_always_ask` 類別之內，所以這個 skill 無條件地替它把關。
在打 tag 或 deploy 之前，用 `AskUserQuestion`：
- Prompt: "Producer verdict is GO. Execute Phase 6 — tag, deploy to staging,
  deploy to production?"
- Options: `[A] Yes, deploy` / `[B] Staging only — hold production` / `[C] Stop here`

得到明確核准之後，才委派給 **release-manager** + **devops-engineer**：
- 在版本控制裡打上發布 tag
- 把 Polish 階段草擬的 changelog（`/changelog`）定稿，加上 gate 之後有變動的內容
- Deploy 到 staging 做最後的 smoke test
- Deploy 到 production（只有使用者在上面核准了 production 才做）
- 人工的團隊動作：發布後 48 小時內監看儀表板與錯誤率。在 48 小時的時間點，用 `/retrospective` 排定一次後續回顧。

跟 deploy 平行，委派給 **release-manager**：
- 用 `/patch-notes [version]` 把 Polish 階段草擬的 patch notes 定稿：release-manager 有那個 skill，也有它的 `git log` 步驟需要的 Bash 存取；`community-manager` 兩者都沒有

然後把這些 patch notes 交給 **community-manager**：
- 準備上線公告（商店頁更新、社群媒體、社群貼文）
- 如果有 S3 以上的問題隨版本上線，草擬已知問題貼文
- 輸出：所有面向玩家的發布溝通內容，在 deploy 確認時就可以直接發佈

### Phase 7: Post-Release
- **release-manager**：產生發布報告（上線了什麼、延後了什麼、指標）
- **producer**：更新 milestone 追蹤，向利害關係人溝通
- **qa-lead**：監看進來的 bug 回報，找出回歸問題
- **community-manager**：發佈所有面向玩家的溝通內容，監看社群情緒
- **analytics-engineer**：確認線上儀表板正常；有任何關鍵事件缺失就發出警示
- 延續 Phase 6 的 48 小時監看期：發布後 48 小時內持續盯著 bug、儀表板和社群情緒（release-manager 自己的監看會一路跑到它的 72 小時報告）
- 如果出了問題，排定發布後的回顧

## Error Recovery Protocol

**先驗證產物。** 如果回傳約定指定了路徑，在把這個 phase 當成做完之前，先確認該路徑真的存在：**指名的產物不在磁碟上，就是失敗的 phase，不管回覆讀起來多流暢。** agent 可能耗掉整個 phase，回你一段看似合理的開場白，卻什麼都沒寫；這既不是 BLOCKED、也不是錯誤、也不是「無法完成」，所以下面的觸發條件永遠不會被觸發。要叫它繼續，並指明沒達成的約定；context 通常還在。

如果任何 spawn 出去的 agent 回傳 BLOCKED、出錯或無法完成：**立刻揭露，不要越過它所阻擋的依賴項繼續往下走，而且一定要產出部分報告。**完整流程：`.claude/docs/error-recovery-protocol.md`。

常見的阻擋原因：
- 輸入檔案缺失（找不到 story、GDD 不存在）→ 導向建立它的 skill
- ADR 狀態是 Proposed → 不要實作；決定之後，用 `/architecture-decision accept ADR-NNNN` 接受它
- 範圍太大 → 用 `/create-stories` 拆成兩個 story
- ADR 和 story 的指示互相衝突 → 把衝突揭露出來，不要猜

## File Write Protocol

所有檔案寫入（發布檢查表、changelog、patch notes、deploy 腳本）都委派給 sub-agent 和 sub-skill。兩者遵守**不同**的規則，而這個區別在這裡比 pipeline 其他地方都更重要：

- **透過 `Agent` spawn 的 sub-agent** 適用上面「為什麼這不違反 Collaboration Protocol」所記載的**有界例外**：路徑是你指定的、產物是 `production/`、`docs/` 或 `tests/` 底下的新檔案、而且這個 phase 有 `AskUserQuestion` 把關。在這些範圍內，sub-agent **不會**每次寫入都問；範圍之外就一定要問。
- **Sub-skill** 不是 sub-agent，例外不適用於它們。它們遵守一般的 Collaboration Protocol，寫入前要先問。

這個 orchestrator 不會直接寫檔案。這裡沒有任何東西授權對外可見或不可逆的動作：tag、push、build 和商店頁面的變更，不管適用上面哪一條規則，都需要明確的確認。

## Output

一份摘要報告，涵蓋：發布版本、範圍、品質 gate 結果、go/no-go 決定、deploy 狀態，以及監看計畫。

Verdict: **COMPLETE** — release executed and deployed.
Verdict: **BLOCKED** — release halted; the stage check stopped it, go/no-go was NO, or a hard blocker is unresolved.

## Next Steps

- 發布後監看儀表板 48 小時。
- 如果發布期間發生重大問題，跑 `/retrospective`。
- 除非階段檢查被放行，否則 `project.stage` 會是 `Release`：`/gate-check release` 是 Polish → Release 的就緒 gate，在這個 skill 之前跑。放行之後，stage 仍然是原本的值。只有 `/gate-check` 會改變 `project.stage`（在 PASS，或使用者接受風險的 CONCERNS 時），所以這個 skill 絕對不會寫它或 `production/stage.txt`。`Release` 是 `project.stage` enum 裡的最終階段，沒有上線後的 stage 值。上線／上線後的狀態要記在發布報告裡，不要記在 `project.stage`。
