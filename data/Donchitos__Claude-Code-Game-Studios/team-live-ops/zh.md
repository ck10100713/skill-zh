---
name: team-live-ops
description: "統籌 live-ops 團隊（live-ops-designer、economy-designer、analytics-engineer、community-manager、writer），負責一個賽季或限時活動。"
argument-hint: "[season name or event description] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-live-ops/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team Live Ops

**參數檢查：** 如果沒有提供賽季名稱或活動描述，就輸出：
> "Usage: `/team-live-ops [season name or event description] [--review full|lean|solo]` — Provide the name or description of the season or live event to plan."
然後立刻停止，不要 spawn 任何 subagent，也不要讀任何檔案。

帶了有效參數時，就用結構化的規劃 pipeline 來統籌 live-ops 團隊。

**決策點：** 每個 phase 轉換時，用 `AskUserQuestion` 把 subagent 的提案做成可選項目給使用者選。先在對話中寫出 agent 的完整分析，再用簡短的標籤收下決定。
在 `collaborative` 模式下，使用者核准後才能進下一個 phase。
在 `guided` 模式下，pipeline 會自動往下走，除非某個 phase BLOCKED；
在 `autonomous` 模式下會從頭跑到尾，每個 phase 的結果用 `log_decision` 記錄下來。
屬於 `automation_always_ask` 類別的決策（`is_always_ask_category` helper）不管什麼模式一律要問。參見 `.claude/docs/automation-modes.md`。

## Phase 0: Resolve Config

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size,workflow`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，就用 `.claude/docs/config-resolution.md` 裡的預設值。

`review_mode` 決定 director gate 的深度，而這條 pipeline 沒有 director gate：
下面任何 phase 在任何 `review_mode` 下，都不會 spawn CD-、TD-、PR- 或 AD-PHASE-GATE。它的 phase gate 就是 pipeline 自己的決策點（定義在下面的 `team.size` 底下），在這些點上工作的 agent 是團隊成員，不是 director gate。

`automation` 決定上面「決策點」那段的行為。各模式如何改變 pipeline 的行為，見上面的決策點說明和 `.claude/docs/automation-modes.md`。

**`team.size`**：哪些 agent 啟用（跟 review_mode 的 gate 深度和 workflow docs 互相獨立）。
- **`individual`**（預設）：`live-ops-designer` + `economy-designer`。其他 agent 透過這兩個諮詢，不會另外 spawn。
- **`small`**：加上 `analytics-engineer` + `community-manager`。
- **`studio`**：再加上 `writer` + `narrative-director`（也就是文件中寫的完整 pipeline）。
在 `individual` 下需要用到的非核心 agent，會改由最接近的核心 agent 處理，並附一則說明。**「Phase gate」指的是這條 pipeline 自己列出、以 `AskUserQuestion` 決策點收尾的任何 phase**：可能是上面「決策點」底下的某個轉換，也可能是下面 pipeline 裡寫明的 **Gate** 步驟，**不管 `automation` 是哪個模式都一樣。** `guided` 和 `autonomous` 改變的是 gate 怎麼通過（自動往下走，或用 `log_decision` 記錄），不是它算不算 gate，所以下面的有界例外條件 (3) 在每個模式下的 gate 都成立。被限制成「只在 phase gate 出場」的 agent，只會在這些時點 spawn，其他時候不會。這個「依啟用名單縮小範圍」的規則適用於下面整條 pipeline：任何 phase 只要點名了啟用名單以外的 agent，就改由最接近的核心 agent 處理，不 spawn 它。

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
- **live-ops-designer** — 賽季結構、活動節奏、留存機制、戰鬥通行證
- **economy-designer** — live 經濟平衡、商店輪替內容與價格（節奏由 live-ops-designer 決定）、貨幣定價、保底計時器
- **analytics-engineer** — 成功指標、A/B 測試設計、事件追蹤、儀表板規格
- **community-manager** — 面向玩家的公告、活動說明、賽季訊息
- **narrative-director** — 賽季敘事主題、故事弧線、世界事件的包裝
- **writer** — 活動說明、獎勵道具名稱、賽季氛圍文字、公告文案

## How to Delegate

用 `Agent` 工具把每個團隊成員 spawn 成 subagent：
- `subagent_type: live-ops-designer` — 賽季／活動結構與留存機制
- `subagent_type: economy-designer` — live 經濟平衡與獎勵定價
- `subagent_type: analytics-engineer` — 成功指標、A/B 測試、活動埋點
- `subagent_type: community-manager` — 面向玩家的溝通與訊息
- `subagent_type: narrative-director` — 賽季主題與敘事包裝
- `subagent_type: writer` — 所有面向玩家的文字：活動說明、道具名稱、文案

**給每個 agent 的 brief 要精簡，不要整包 context 倒過去。** 共用的輸入只讀**一次**，再把整理過的 brief 直接寫在 prompt 裡：只放每個 agent 真正需要的那幾行，你已經讀過的文件絕對不要只丟檔案路徑（agent 拿到路徑會把整份檔案重讀一遍）。只有你還沒讀、而且只有那個 agent 需要的文件，才給路徑。

**每個 agent 的 prompt 結尾都要加上回傳約定：**「Write your full output to `[path]` — that named path is your write authorisation under the bounded exception below, so write it without a separate approval prompt. Return **only** (1) the path written, (2) a ≤5-bullet summary of decisions, (3) any BLOCKED/CONCERNS items, one line each. Do not restate the documents you read.」沒有這個約定的話，agent 會把它讀過的東西全部倒回這個 session。

**`[path]` 要換成真實路徑。** 工作中的產出放在
`production/live-ops/[season-slug]/` 底下，`[season-slug]` 是參數轉成的 slug：全小寫、空格換成連字號。每個 agent 一個檔案，這樣平行的 phase 就不會共用同一個檔：

| Phase / agent | Writes to |
|---|---|
| 1 live-ops-designer | `production/live-ops/[season-slug]/brief.md` |
| 2 narrative-director | `production/live-ops/[season-slug]/narrative.md` |
| 3 economy-designer | `production/live-ops/[season-slug]/economy.md` |
| 4 analytics-engineer | `production/live-ops/[season-slug]/analytics.md` |
| 5 narrative-director | `production/live-ops/[season-slug]/narrative-text.md` |
| 5 writer | `production/live-ops/[season-slug]/copy.md` |
| 6 community-manager | `production/live-ops/[season-slug]/comms.md` |

這些是工作草稿；`design/live-ops/seasons/` 底下的最終文件是用它們彙整出來的（見 Output Documents）。

> **為什麼這不違反 Collaboration Protocol。** `CLAUDE.md` 要求 agent 在 Write/Edit 之前先問「May I write this to [filepath]?」。這裡 spawn 出來的 subagent **不問**就寫，這是刻意設計的有界例外，不是疏忽，跟 `consistency-check` 附加寫入 `active.md` 是同一個決定。這個例外只在三個條件**同時**成立時才有效：(1) 路徑是**你**在 prompt 裡指定的，所以使用者核准這個 phase 的時候，就等於核准了目的地；(2) 它是 `production/`、`docs/` 或 `tests/` 底下的新產物，絕對不是改既有的原始碼或設定；(3) 產生它的那個 phase，本身在 pipeline 往下走之前有 `AskUserQuestion` 把關。這三條以外，agent 一定要先問。**不要靠「每個 subagent 都問一次」來「修」這件事**：每個 agent 每個 phase 都跳一次提示，會讓 orchestrator 根本沒辦法用，這就是這個例外存在的原因。

只要 pipeline 允許，就把互相獨立的 agent 平行啟動（Phase 3 和 4 可以同時跑）。

## Pipeline

### Phase 1: Season/Event Scoping
委派給 **live-ops-designer**：
- 定義賽季或活動：類型（賽季、限時活動、挑戰）、持續時間、主題方向
- 列出內容清單：有什麼新東西（模式、道具、挑戰、劇情節拍）
- 定義留存鉤子：賽季期間是什麼讓玩家每天／每週回來
- 找出資源預算：有多少新內容要做、多少可以重複利用
- 輸出：包含範圍、內容清單與留存機制概述的賽季 brief

### Phase 2: Narrative Theme
委派給 **narrative-director**：
- 讀 Phase 1 的賽季 brief
- 設計賽季敘事主題：這個活動怎麼跟遊戲世界連起來？
- 定義玩家在活動中會發現的核心故事鉤子
- 找出這個賽季可以推進的既有背景設定線索
- 輸出：敘事包裝文件（主題、故事鉤子、背景設定的連結）

### Phase 3: Economy Design (parallel with Phase 4)
委派給 **economy-designer**：
- 讀賽季 brief，以及 `design/live-ops/economy-rules.md` 裡現有的經濟規則
- 設計獎勵軌道：免費層的進度、付費層的價值主張
- 規劃賽季內經濟：賽季貨幣、商店輪替內容、定價
- 為任何隨機要素定義保底計時器機制與壞運氣保護
- 確認付費軌道裡沒有 pay-to-win 的道具
- 輸出：附獎勵表、定價與貨幣流向的經濟設計文件

### Phase 4: Analytics and Success Metrics (parallel with Phase 3)
委派給 **analytics-engineer**：
- 讀賽季 brief
- 定義成功指標：參與率目標、留存提升目標、戰鬥通行證完成率
- 設計賽季期間要跑的 A/B 測試（例如不同的獎勵節奏）
- 指定這個賽季的內容所需要的新遙測事件
- 輸出：附成功標準與埋點需求的分析計畫

### Phase 5: Content Writing (parallel)
要等 Phase 3 和 Phase 4 的結果都收齊之後才開始。平行委派：
- **narrative-director**（如果需要）：撰寫這個賽季的遊戲內敘事文字（過場腳本、NPC 對白、世界事件說明）
- **writer**：撰寫所有面向玩家的文字：活動名稱、獎勵道具說明、挑戰目標文字、賽季氛圍文字
- 兩者都要讀 Phase 2 的敘事包裝文件

### Phase 6: Player Communication Plan
委派給 **community-manager**：
- 讀賽季 brief、經濟設計與敘事包裝
- 草擬賽季上線公告（語氣、重點亮點、各平台版本）
- 規劃溝通節奏：上線前預告、上線日貼文、賽季中提醒、最後一週的 FOMO 推送
- 為第一天的 patch notes 草擬已知問題章節的佔位內容
- 輸出：附各接觸點草稿文案的溝通行事曆

### Phase 7: Review and Sign-off
收集所有 phase 的產出，呈現一份整合後的賽季計畫：
- 賽季 brief（Phase 1）
- 敘事包裝（Phase 2）
- 經濟設計與獎勵表（Phase 3）
- 分析計畫與成功指標（Phase 4）
- 文字內容清單（Phase 5）
- 溝通行事曆（Phase 6）

給使用者一份摘要，包含：
- **內容範圍**：正在製作什麼
- **經濟健康檢查**：獎勵軌道感覺公平、不坑人嗎？
- **分析就緒度**：成功標準有定義、也有埋點嗎？
- **倫理審查**：拿 Phase 3 的經濟設計對照 `design/live-ops/ethics-policy.md` 檢查
  - 如果檔案不存在：標出「ETHICS REVIEW SKIPPED: `design/live-ops/ethics-policy.md` not found. Economy design was not reviewed against an ethics policy. Recommend creating one before production begins.」把這個標記放進賽季設計的輸出文件。在 next steps 加上：建立 `design/live-ops/ethics-policy.md`。
  - 如果檔案存在而且發現違規：標出「ETHICS FLAG: [element] in Phase 3 economy design violates [policy rule]. Approval is blocked until this is resolved.」絕對不准發 COMPLETE verdict，也不准寫輸出文件。用 `AskUserQuestion` 提供選項：修改經濟設計 / 附上書面理由後強行放行 / 取消。使用者選擇修改的話：重新 spawn economy-designer 產出修正後的設計，再回到 Phase 7 審查。使用者選擇取消的話：以 Verdict: BLOCKED 結束，內容為「Live ops design cancelled due to unresolved ethics violation. Resolve the flagged issues and re-run /team-live-ops.」
- **待解問題**：開始製作之前還需要決定的事

交給製作團隊之前，要請使用者核准賽季計畫。只有在使用者核准、而且沒有未解決的倫理違規時，才能發 COMPLETE verdict。如果有倫理違規沒解決，就以 Verdict: **BLOCKED** 結束。

## Output Documents

所有文件都存到 `design/live-ops/`，**但 orchestrator 寫之前要先問。** `design/` 不在有界寫入例外涵蓋的三個目錄（`production/`、`docs/`、`tests/`）裡，所以拿到這些路徑的 sub-agent 一定得先問。不要靠放寬例外來讓它不出聲。
改照 `team-level` 的模式：sub-agent 把它們的工作產物寫在 `production/` 底下，例外可以涵蓋到那裡；**你**來彙整最終文件，並透過 `AskUserQuestion` 問：「May I write the season plan to
`design/live-ops/…`?」核准後才寫。

路徑：
- `seasons/S[N]_[name].md` — 賽季設計文件（來自 Phase 1-3）
- `seasons/S[N]_[name]_analytics.md` — 分析計畫（來自 Phase 4）
- `seasons/S[N]_[name]_comms.md` — 溝通行事曆（來自 Phase 6）

## Error Recovery Protocol

**先驗證產物。** 如果回傳約定指定了路徑，在把這個 phase 當成做完之前，先確認該路徑真的存在：**指名的產物不在磁碟上，就是失敗的 phase，不管回覆讀起來多流暢。** agent 可能耗掉整個 phase，回你一段看似合理的開場白，卻什麼都沒寫；這既不是 BLOCKED、也不是錯誤、也不是「無法完成」，所以下面的觸發條件永遠不會被觸發。要叫它繼續，並指明沒達成的約定；context 通常還在。

如果任何 spawn 出去的 agent 回傳 BLOCKED、出錯或無法完成：**立刻揭露，不要越過它所阻擋的依賴項繼續往下走，而且一定要產出部分報告。** 被略過的 agent 那一節要留成一個有名字的缺口，絕對不准用你自己的內容填進去。完整流程：`.claude/docs/error-recovery-protocol.md`。

如果 BLOCKED 狀態無法解決，就以 Verdict: **BLOCKED** 結束，不要發 COMPLETE。

## File Write Protocol

Sub-agent 把它們的工作產物寫在 `production/` 底下，依據的是上面「為什麼這不違反 Collaboration Protocol」所記載的**有界例外**：路徑是你指定的、產物是 `production/`、`docs/` 或 `tests/` 底下的新檔案、而且這個 phase 有 `AskUserQuestion` 把關。在這些範圍內，sub-agent **不會**每次寫入都問；範圍之外就一定要問。`design/live-ops/` 底下的**最終文件**（賽季設計、分析計畫、溝通行事曆）是例外：orchestrator 自己彙整，並在自己的「May I write …?」提示之後親自寫入（見上面的 Output Documents）。

## Output

一份摘要，涵蓋：賽季主題與範圍、經濟設計重點、成功指標、內容清單、溝通計畫，以及開始製作前還需要使用者決定的待解事項。

Verdict: **COMPLETE** — season plan produced and handed off for production.

## Next Steps

- 對賽季設計文件跑 `/design-review` 做一致性驗證。
- 跑 `/sprint-plan` 排定這個賽季的內容製作工作（在沒有 sprint 的 `workflow: minimal` 下，改把它加進 brief 的 build order）。
- 賽季內容準備好 deploy 時，跑 `/team-release`。
- 如果這次 run 因為倫理標記而以 **BLOCKED** 結束：依 `design/live-ops/ethics-policy.md` 修改經濟設計，再重新執行 `/team-live-ops`；上面三個步驟要等到計畫 COMPLETE 才做。
