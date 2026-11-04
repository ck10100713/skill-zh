---
name: vertical-slice
description: "Pre-production 驗證：做一個端到端的 build，在投入 Production 之前確認完整的遊戲循環做得出來。在 GDD、架構、UX 規格都完成之後執行。"
argument-hint: "[--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/vertical-slice/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow`

上面已經解析好了，直接用；`--review` 會在這次執行中覆蓋 `review_mode`。如果沒有這個區塊，就用
`.claude/docs/config-resolution.md` 裡的預設值。

# Vertical Slice



## Purpose

**vertical slice** 回答的問題跟概念原型不一樣：
*「我們能不能照時程，用 production 品質做出完整的遊戲循環？」*

**預設用法**：在 Pre-Production 後期執行，GDD、架構和 UX 規格都完成之後。它是一個接近 production 品質的 build，展示一次完整的 [start → challenge → resolution] 循環。

**Pivot 之後？** 如果先前 vertical slice 的結論是 PIVOT，讓你回頭修改 GDD 和架構，修完後再跑一次重新驗證。要跑幾次都可以，直到出現 PROCEED 或 KILL 的結論為止。

它驗證四件事：

1. Pipeline（團隊真的做得出這種品質的內容嗎？）
2. 執行可行性（架構決策對這款遊戲正確嗎？）
3. 樂趣能不能存活（概念原型的樂趣，在完整設計之後還在嗎？）
4. **Velocity**（這花了多久？那就是你真正的 production 速率估計。）

**專案更早期？** 如果你還沒寫 GDD，想先驗證核心點子值不值得設計，改跑 `/prototype`（概念原型）。

---

## Phase 1: Resolve Review Mode and Load Context


完整的檢查模式見 `.claude/docs/director-gates.md`。各個 gate 的定義放在 `.claude/docs/director-gates/[gate-id].md`，由被派出去的 agent 自己讀它的 gate 檔，不要在父 session 裡讀。


每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一定要問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
`automation_always_ask` 列的類別一律要問）。

讀下面這些檔案，了解完整的設計意圖。GDD、ADR 和 control manifest 都要分段讀：用 Grep 工具（pattern `^#`，content mode）找出需要的標題，再用 offset 和 limit 讀那些範圍。
- `CLAUDE.md`：技術棧和引擎
- `design/gdd/game-concept.md`：核心幻想和遊戲支柱（或
  `design/game-brief.md`，在 `rigor: minimal` 時取代它的一頁式簡報，
  有 pitch、核心循環和「他們的感受」那一行，沒有支柱）
- `design/gdd/systems-index.md`：MVP 系統和它們的優先級
- `docs/architecture/architecture.md`：分層結構
- `docs/architecture/control-manifest.md`：實作的技術規則
- 要切的那些系統的關鍵 GDD

---

## Phase 2: Define the Slice Scope and Validation Question

開始做之前，先定義**可以被證偽的驗證問題**：

> *「玩家從零開始，有沒有在 [N] 分鐘內體驗到 [game-concept.md 或 game-brief.md 的核心幻想]，
> 而且不需要開發者引導？我們能不能在 [X] 天內，用有代表性的品質做出一個這樣的循環？」*

兩個部分都重要：玩家體驗，以及 build 的可行性。

**範圍紀律：**
- 包含所有核心循環的系統（這是下限）。如果某個系統是完成一次 [start → challenge → resolution] 循環必需的，就一定要放進 slice。
- **目標範圍：3 到 5 分鐘打磨過、連續不中斷的遊玩。** 這是業界標準的 vertical slice 長度，夠長，可以展示機制和調性；夠短，可以用有代表性的品質做出來。如果你的 slice 要玩超過 5 分鐘，就砍內容，不要砍品質。
- **先砍範圍，再考慮砍品質。** 品質很差、跟預期遊戲完全不像的 slice，沒辦法驗證 production 的可行性。
- 如果範圍感覺大到 1 到 3 週做不完，就是 slice 的範圍抓錯了。問題不是太大做不完，而是這個 slice 想一次證明太多東西。

**範圍蔓延警告：** vertical slice 是 pre-production 階段範圍最容易蔓延的時刻。功能感覺「快好了」，就會很想再加「最後一個系統」。要忍住。砍，不要擴。

開始做之前，先把範圍給使用者看並取得確認。

---

## Phase 3: Plan the Build

用條列定義：
- 要實作的系統（會用到哪些 GDD 段落）
- 完整的遊戲循環（[start] → [challenge] → [resolution] 要寫得精確）
- 美術和音效的品質等級（可以用 placeholder，有代表性的更好）
- 針對驗證問題，具體、可量測的成功準則
- 硬性時間上限：[X] 天。超過就代表範圍錯了，停下來重新評估。

開始做之前，請使用者確認範圍。確認時要點名 checkpoint 檔案：「我可以把這份計畫記錄到 `production/session-state/active.md` 嗎？」

確認之後，把 session checkpoint 寫到 `production/session-state/active.md`（`production/session-state/` 不存在就建立）。內容包含：概念名稱、驗證問題、範圍內的系統、美術品質等級，以及目前的階段（「Phase 4 — Implement」）。每個 build 日結束時更新這個檔案，記錄完成了什麼。如果 session 在 slice 做到一半中斷，這是主要的復原機制，跨好幾週的 Engine build 會橫跨很多個 session。

---

## Phase 4: Implement

問：「我可以建立 vertical slice 目錄 `prototypes/[concept-name]-vertical-slice/` 然後開始實作嗎？」

如果同意，就建立目錄。每個檔案開頭都必須有：

```
[comment] VERTICAL SLICE - NOT FOR PRODUCTION
[comment] Validation Question: [What this build is proving]
[comment] Date: [Current date]
```

`[comment]` 要用每個檔案自己的註解語法來寫：GDScript（`.gd`）和 Python 用 `#`，C#、C++ 和 JavaScript 用 `//`，Lua 用 `--`，HTML 和 Markdown 用 `<!-- … -->`。標頭用錯語言的語法會變成 parse error，不是標籤。沒辦法放註解的檔案（JSON、引擎產生的場景和專案檔）不用加。

**品質標準**：比概念原型高，但不是完整 production：
- 遵守 `docs/architecture/control-manifest.md` 的架構分層
- 命名慣例：用 `project.yaml` 的 `naming.*`；任何缺少或空白的 key（包含 `project.yaml` 根本沒有 `naming` 區塊的情況），用 `.claude/docs/technical-preferences.md` 的
- 不要寫死遊戲數值，用常數或設定檔
- 關鍵路徑要有基本的錯誤處理
- 可以用 placeholder 美術，有代表性的更好

**多輪循環：** 寫完最初的檔案後，請使用者跑 build 並回報觀察到什麼。每一輪：
1. 使用者執行，回報錯誤或觀察
2. Agent 修錯誤或調整系統
3. 重複，直到完整的 [start → challenge → resolution] 循環可以玩

**沉沒成本 checkpoint（預定時程的第 3 天）：** 如果完整的遊戲循環還不能展示，就停下來重新評估。要嘛範圍太大，要嘛有架構假設是錯的。把阻礙明確講出來，不要繼續硬 iterate。

循環可以展示之後，至少做 1 次 playtest。

**Playtest 小技巧：** 如果能找到沒看過這款遊戲的人來玩（朋友、家人、線上社群都行），就安靜看他們玩，什麼都不要解釋，也不要引導。他們的困惑會露出遊戲自己沒講清楚的地方。這比自己測好得多。

**找不到外部測試者？** 在團隊內輪替：Dev A 做了系統 X，所以 Dev A 對系統 Y 來說就是新手測試者。兩個人的團隊也能有效輪替。一個人的話？先離開 2 到 3 天，再用新玩家的身分玩一遍，你拿不到完美的第一印象訊號，但能抓到關鍵的阻礙。也可以試「安靜走查」：一次把自己的 slice 玩完，中途不停下來修任何東西，把每一次猶豫的瞬間都記下來。

**想要更豐富的觀察資料？** 請測試者邊玩邊**出聲思考**：即時講出自己在做什麼、為什麼。「我在想要怎麼攻擊……我按了 E……沒反應……是用點的嗎？」這樣可以在困惑發生的當下就浮現，不用事後回想。最適合用在 onboarding 和 UI 清晰度的驗證。測手感還是安靜觀察比較好；出聲思考會稍微改變體驗，但能產出細緻得多的 UX 資料。

**非同步遠端選項：** 錄一段 Loom 或 OBS，把 build 交給某個人，請他錄下螢幕加聲音再把影片寄給你。你可以拿到真實的第一印象資料，不用同步排時間。跨時區也能用。

**要在 AI、NPC 或複雜系統行為還沒完整實作前測試？** 用 **Wizard of Oz** 技巧：一個人正常玩，另一個人偷偷即時操控 NPC 或系統行為，讓玩家以為那是自動的。這可以在實作完成之前，先驗證 AI 或經濟系統的*設計意圖*，並且清楚看出系統必須產出哪些行為才會感覺對。特別適合 AI 系統在 slice 範圍內、但還沒打磨到可以不加引導測試的 vertical slice。

---

## Phase 5: Playtest Debrief

循環可以展示了。在寫報告之前，先從實際遊玩中收集有結構的觀察。絕對不要跳過去直接產報告，報告的品質取決於你在這裡抓到的觀察。

一字不差地說：
> 「從頭完整玩一次 [start → challenge → resolution] 循環，
> 假裝你是個不知道這個 build 怎麼做出來的新玩家。不要跳著玩，
> 也不要用開發者的捷徑。完整玩完一輪再回來，
> 或是遇到卡住你的東西時就回來。」

使用者回來之後，**一次問一個**這些問題：

1. **Loop completion：**
   > 「你有靠自己完成完整的 [start → challenge → resolution] 循環嗎？
   > 有沒有需要我的任何引導，或是事先知道這個 build 的什麼東西？」

2. **Time check：**
   > 「從開始到第一個有意義的動作，花了多久？
   > 就是你第一次覺得自己真的在玩這款遊戲的那一刻。」

3. **Core fantasy：**
   > 「這款遊戲應該要讓你感覺到 [game-concept.md 或 game-brief.md 的核心幻想]。
   > 有嗎？老實說，不要回答『有一點』，要講你具體感受到什麼、在什麼時候。」

4. **Blockers：**
   > 「什麼東西卡住你、讓你困惑，或是把你拉出體驗？
   > 有沒有哪個時刻你不確定該做什麼，或是有東西壞掉？」

5. **Pipeline check：**
   > 「以開發者的身分，不是玩家，你覺得整款遊戲能用這個品質做出來嗎？
   > 做這些東西花的時間，有什麼讓你意外的？」

6. **Verdict：**
   > 「PROCEED、PIVOT 還是 KILL，還有具體理由。」

如果任何答案很模糊，就問：「你能告訴我那件事發生的具體時刻嗎？」精確的觀察才能填進報告，模糊的只會產出沒用的報告。

**驗證項目有任何一個是 NO 的時候，不能給 PROCEED。** `/gate-check production` 會讓 Vertical Slice Validation 裡有任何 NO 的 slice 直接 FAIL：玩家沒有開發者引導就完成循環（問題 1）、前 2 分鐘內就學會要做什麼（問題 2，更久就是 no）、核心機制手感好（問題 3）、沒有關鍵的破壞樂趣的 bug（問題 4）。這些答案只要有一個是 no，結論就是 PIVOT 或 KILL（由使用者選），而且報告要指出是哪個 NO。

**NOT ASSESSED 是第四種結論。** 當還沒有人從頭玩過完整循環時（使用者這次 session 沒辦法玩，或是玩到一半就停了），驗證就沒有進行，結論是 **NOT ASSESSED**，並附上原因。它的排序高於 PROCEED，低於 PIVOT 和 KILL：沒玩過的 slice 還沒資格拿 PROCEED，而已知會失敗的 slice 比沒人玩過的更有行動價值。它絕對不能被記成 PROCEED。

---

## Phase 6: Generate Vertical Slice Report


整個 build 過程都要追蹤 velocity。記錄：
- Day 1：做了什麼
- Day 2：做了什麼
- 以此類推

這是你將來能拿到最誠實的 production 速率資料。不要跳過。它會直接餵進 sprint 規劃（在 `workflow: minimal` 沒有 sprint 的情況下，就餵進簡報的 build order）。

讀 `.claude/docs/templates/vertical-slice-report.md` 取得報告結構。如果找不到範本檔，就用這個備用結構：
- `## Vertical Slice Report — [Game Title] — [Date]`
- `### Executive Summary`（PROCEED / PIVOT / KILL / NOT ASSESSED 結論 + 兩句理由）
- `### Core Loop Validation`（測了什麼、什麼過了、什麼沒過）
- `### Feel Assessment`（動畫、操作、回饋：主觀筆記）
- `### Technical Findings`（效能、引擎問題、架構風險）
- `### Velocity Log`（逐日實際進度，不要跳過）
- `### Lessons Learned`（做到接近 production 品質時打破的假設；pipeline 或架構有什麼讓我們意外；下次 slice 範圍想改什麼）
- `### Recommended Next Steps`

每個段落都要根據這次 session 觀察到和做出來的東西填寫。velocity log 必須反映實際的逐日進度，不是估計，這是你將來能拿到最誠實的 production 速率資料。把所有 placeholder 文字換成真實的觀察。建議要帶上 Phase 5 的結論（包含 NOT ASSESSED）和它的原因。

問：「我可以把這份報告寫到
`prototypes/[concept-name]-vertical-slice/REPORT.md`，並把它的一列加進
`prototypes/index.md` 嗎？」

如果同意，就寫檔。然後更新 `prototypes/index.md`（不存在就建立）：在 vertical slice 表格附加一列，內容有概念名稱、日期、結論，和 REPORT.md 的連結。註明這是第一次跑的 slice，還是 PIVOT 之後的重跑。這份報告裡的 velocity log 是整個專案裡最有價值的資料之一，要拿來跟 sprint 估算互相對照。

---

## Phase 7: Creative Director Review

**Review mode 檢查：**
- `solo` → 跳過。註記：「CD-PLAYTEST skipped — Solo mode.」
- `lean` → 跳過（這不是 PHASE-GATE）。註記：「CD-PLAYTEST skipped — Lean mode.」
- `full` → 用 gate **CD-PLAYTEST**（`.claude/docs/director-gates/cd-playtest.md`）透過 `Agent` 派出 `creative-director`，除非 slice 的結論是 NOT ASSESSED：沒有遊玩過就沒有東西可以審，所以註記「CD-PLAYTEST skipped — the slice has not been played yet.」

要傳給它：完整的 REPORT.md 內容、驗證問題、`design/gdd/game-concept.md` 的遊戲支柱和核心幻想（或 `rigor: minimal` 時 `design/game-brief.md` 的 pitch 和「他們的感受」那一行）。

creative director 會對照遊戲的創意願景和支柱，評估 vertical slice 的結果，並回傳該 gate 的其中一個結論：APPROVE、CONCERNS 或 REJECT。把它套用到建議上：

- **APPROVE** → 建議維持不變。
- **CONCERNS** → 把疑慮和建議一起呈現，然後用 `AskUserQuestion`：`Revise the recommendation` / `Accept with noted concerns` / `Discuss further`。由使用者決定，director 不決定。
- **REJECT**（核心幻想不存在）→ PROCEED 的建議不成立。用 `AskUserQuestion` 請使用者選 `PIVOT` 或 `KILL`，並針對那個選擇執行 Phase 8。PIVOT 或 KILL 的建議維持不變。
- **NOT ASSESSED** [缺少輸入] → director 沒有做出判斷，所以它既不支持也不推翻建議（`.claude/docs/director-gates.md`）：指出缺了什麼，然後補上並重跑 gate，或是在報告裡記錄 `CD-PLAYTEST: NOT ASSESSED — [input]`。

當 director 回傳 CONCERNS、REJECT 或 NOT ASSESSED 時，問「我可以更新
`prototypes/[concept-name]-vertical-slice/REPORT.md` 和它在 `prototypes/index.md` 的那一列嗎？」，然後把 director 的結論和理由記錄到 REPORT.md，如果最終建議有變，兩邊都要更新。

---

## Phase 8: Summary and Next Steps

輸出摘要：驗證問題、velocity 資料和最終建議。附上 `prototypes/[concept-name]-vertical-slice/REPORT.md` 的連結。

**如果是 PROCEED：**
你的 vertical slice 驗證了完整的遊戲循環。專案準備好進入 Production。

在 `workflow: minimal`：`/create-stories`（從簡報來），然後對第一個 story 跑 `/dev-story`，下面這份清單的其餘部分是 `standard`/`full` 的路線。

建議的下一步（`standard`/`full`）：
- `/create-epics layer:foundation`：規劃 Foundation 層的 epic
- `/create-epics layer:core`：規劃 Core 層的 epic
- `/create-stories [epic-slug]`：把每個 epic 拆成可以實作的 story
- `/sprint-plan`：用 slice 的 velocity 資料規劃第一個 sprint
- `/gate-check production`：正式把階段推進到 Production

**Playtest 備註：** `/gate-check` 會找有文件記錄的 playtest 證據。要通過 gate，至少需要 1 次有記錄的 session，且 REPORT.md 顯示 PROCEED。更多 session 能給更可靠的訊號，讓整個團隊投入 Production 之前，建議做 3 次以上，但這不是硬性的 gate。

**如果是 PIVOT：**

在回頭修訂 GDD 之前，先留下帶往下一輪的備忘。問這兩個問題（純文字，一次一個）：

1. 「哪些系統或機制在這個品質等級下行得通，修訂後的設計應該保留？」
2. 「具體是什麼失敗了：核心循環、架構、pipeline，還是樂趣？」

問：「我可以把這些寫到 `prototypes/[concept-name]-vertical-slice/PIVOT-NOTE.md` 嗎？」

如果同意，就寫檔，內容有：什麼行得通、什麼失敗、需要修訂的具體系統或架構決策，以及下一個 slice 該用不同的方式證明什麼。下次在 PIVOT 之後跑 `/vertical-slice` 時，要去 `prototypes/` 目錄找 `PIVOT-NOTE.md`，用它來擬定新的驗證問題，並作為範圍決策的依據。

- 用 `/design-system [mechanic]` 修訂受影響的 GDD
- 用 `/architecture-decision` 處理架構問題
- 然後重跑 `/vertical-slice`，驗證修訂後的方向

**如果是 KILL：**

放棄這個概念之前，先確認結論站得住腳：

- [ ] 即使是有經驗的玩家，完整的遊戲循環也要超過 5 分鐘？
- [ ] 任何一次 playtest session 都沒觀察到情緒高點（愉悅、驚喜、滿足）？
- [ ] 試過 2 次以上 slice 之後，仍有 50% 以上的測試者在同一個點困惑或卡住？
- [ ] 架構問題會需要重做已建好內容的 50% 以上？
- [ ] 這是同一個概念的第 3 次 vertical slice 嘗試？

如果符合 2 項以上 → KILL 的結論站得住腳。如果只符合 0 到 1 項 → 一次有針對性的 PIVOT 也許還能救回這個概念。

**把這次 kill 記錄到 `prototypes/GRAVEYARD.md`**（不存在就建立）。
問：「我可以把這個附加到 `prototypes/GRAVEYARD.md` 嗎？」如果同意，加一筆：

```
## [Concept Name] Vertical Slice — YYYY-MM-DD
- **Kill reason:** [what specifically prevented the player from experiencing the core fantasy]
- **What worked at slice quality:** [systems or mechanics that held up]
- **What failed:** [core loop issue, architecture decision, or pipeline blocker]
- **Next time:** [one specific change for the next time a similar concept is attempted]
```

- 帶著學到的東西回到 `/brainstorm`
- 或是先跑 `/prototype [new-concept]`，用低成本測試新方向

**如果是 NOT ASSESSED：**

slice 做出來了，但沒有被驗證。說明是哪個原因造成的，然後把 Phase 5 的遊玩和 debrief 補完（要從 `production/session-state/active.md` 這個 checkpoint 接著做），並且在詢問之後，用結論更新 REPORT.md 和它在 `prototypes/index.md` 的那一列。不要把這個 slice 拿去跑 `/gate-check production`，好像它已經通過一樣：NOT ASSESSED 不是 PROCEED。

---

### Important Constraints

- vertical slice 的程式碼絕對不准重構成 production 程式碼，它只是參考
- Production 程式碼絕對不准從 `prototypes/` import
- 如果建議是 PROCEED，production 實作要從頭寫，slice 只當作設計參考
- 範圍可以砍，品質不能砍：品質很差的 slice 什麼都證明不了
- 總工時：1 到 3 週。更久就代表範圍太大，砍 slice 的範圍，不要砍品質。
- 第 3 天沉沒成本規則：如果到那時完整的遊戲循環還不能展示，就停下來把阻礙講出來
- **網路／多人遊戲：** 本機的 vertical slice 沒辦法驗證網路機制的手感。延遲會根本性地改變戰鬥、移動和預測的手感，在 0ms 本機測試，跟 80ms 網路延遲下的感覺會完全不同。slice 可以驗證遊戲循環有趣且完整，但沒辦法驗證網路機制在真實條件下手感好不好。網路手感需要真實的 peer 或模擬延遲。
