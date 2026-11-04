---
name: brainstorm
description: "引導使用者找出並選定遊戲概念。使用者想要遊戲點子、新概念、game jam 點子，或想探索其他方向時使用，包括放棄目前的點子重來。"
argument-hint: "[genre or theme hint, or 'open'] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, WebSearch, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/brainstorm/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,docs.density,workflow`

上面已經解析好了，直接用。沒有這個區塊 → 用 `.claude/docs/config-resolution.md` 裡的預設值
（`workflow: minimal`、`review_mode: solo`、`automation: collaborative`、`docs.density: terse`），
並且說明設定沒有讀到。

# Brainstorm

把「沒有點子」或「粗略的點子」變成一份寫下來的設計，讓下一步可以接著蓋。寫多少
取決於 `workflow`：

- **`minimal`：** 走下面的 Lean Brief 流程：一頁式的 `design/game-brief.md`，寫完就停。不問
  探索性問題、不定 pillars、不跑 director gate、不寫 `game-concept.md`，也不要載入
  `references/full-concept.md`。
- **`standard` 或 `full`：** 讀 `references/full-concept.md` 並照著做。它會用
  `.claude/docs/templates/game-concept.md` 寫出
  `design/gdd/game-concept.md`。它的 gate 遵循
  `.claude/docs/director-gates.md`；每個 director agent 都會拿到它自己的 gate 檔，
  `.claude/docs/director-gates/<gate-id in lower case>.md`（`cd-pillars.md`、
  `ad-concept-visual.md`、`td-feasibility.md`、`pr-scope.md`），這些檔案你自己不用讀。

skill 名稱後面輸入的文字裡如果有 `--review`，這次執行就用它覆蓋 `review_mode`。
`docs.density` 決定每個章節的深度：`terse` = 條列；`balanced` = 附簡短理由；
`thorough` = 理由加替代方案。提問遵循 `.claude/docs/automation-modes.md`
（collaborative 會問、guided 只問重大決定、autonomous 記錄後直接往下走；
一律要問的類別還是要問）。

提問要用提問工具。沒有的話，把選項編號列出來，然後結束你這一輪等回覆。
問題要放在回覆的最後：後面不要再接建議或傾向。被跳過或被關掉的
問題不算回答：用純文字再問一次。

## Lean Brief 流程（`workflow: minimal`）

幾輪對話就好，不是十五輪：把撐起這款遊戲的想法濃縮在一頁，然後就去寫
程式。用範本 `.claude/docs/templates/game-brief.md` 來寫（六個必填欄位、三個
一句話欄位）。如果 `design/game-brief.md` 已經存在，就讀它並修改，不要從頭來過。

1. **Concept。** 根據 skill 名稱後面輸入的提示（沒有的話就問一個快速的開放式問題），
   提出 **2 或 3 個一句話概念**（動詞開頭，或是類型和主題的混搭），不是
   完整的概念卡。請使用者挑一個或組合起來。這是每次執行都會問的唯一一個創意問題。
2. **在對話中填寫 brief**，每輪填好幾個欄位：
   - **Working title：** brief 的標題行。從選定的概念提供一個，讓使用者
     自己改；`/create-stories` 會用它來命名 epic 資料夾。
   - **Pitch：** 興奮感十足的一句話。
   - **Core loop：** 玩家重複做的 2 到 4 個步驟。
   - **Player goal & fail state**：玩家想做什麼，以及怎樣算輸。
     `/create-stories` 會把它轉成驗收標準。
   - **MVP：** 讓它成為這款遊戲的那份精簡清單；每一項都會變成一個 story。**超過 7
     項：要反駁。** 說明這對 MVP 來說太長，提出要砍哪些項目（砍掉
     core loop 照樣能運作的那些），並讓 brief 維持在 7 項以內。
   - **Out of scope：** 他們刻意不做的東西（被砍掉的項目放這裡）。
   - **Build order：** 風險最高或最沒被驗證過的部分先做。
   - **Who it's for and what they feel**、**Art & audio direction**、**Reference game**（
     最接近的已發行遊戲，以及 MVP 保留它的哪個部分）：各一行；提供選項，不要強迫。
3. **完整顯示填好的 brief。** 然後單獨問一個問題："Brief is ready. May I write it
   to `design/game-brief.md`?" `Yes — write it` / `Revise a field first`。只有對這個問題明確
   回答 yes 才寫；同意某個刪減或說「繼續」都不算同意寫入。要修改的話，改指定的欄位、
   顯示修改前後，再問一次。然後寫入
   `design/game-brief.md`，需要的話建立資料夾。這個 tier 絕對不准寫 `design/gdd/game-concept.md`。
4. **下一步。** 讀 `project.yaml` 的 `engine.name`：
   1. `/setup-engine`：設定引擎。**只有**在 `engine.name` 不存在或
      是空的時候才列它：在 minimal 路徑上，它通常在這個 skill 之前就跑過了。
   2. `/create-stories`：把 MVP 清單變成 story。在 `minimal` 沒有獨立的
      `/create-epics` 或 `/sprint-plan`；build order 就是計畫。
   3. `/dev-story`：第一行遊戲程式碼。

   然後一行摘要：pitch、MVP 項目數量，還有 `design/game-brief.md`。以這行
   收尾：`Verdict: COMPLETE — game brief written; next stop is code.`

如果使用者在寫入之前就停了，要說明 brief 沒有寫入，所以它只存在於這段
對話裡。
