---
name: prototype
description: "在寫 GDD 之前做的概念原型：用完即丟的 HTML、Engine 或 Paper 版本，結論是 PROCEED/PIVOT/KILL/NOT ASSESSED。在 /brainstorm 和 /setup-engine 之後使用。"
argument-hint: "[concept-description] [--path html|engine|paper] [--review full|lean|solo] [--spike]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/prototype/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow`

上面已經解析好了，直接用；`--review` 在這次執行會覆蓋 `review_mode`。沒有
這個區塊的話，用 `.claude/docs/config-resolution.md` 裡的預設值。

# Prototype

## Purpose

這是**概念原型** — 一個快速、用完即丟的版本，只回答一個問題：
*「這個核心點子玩起來真的有趣嗎？」*

**預設用法** — 在 `/brainstorm` 和 `/setup-engine` 之後立刻執行，在寫
GDD 或架構文件之前。它的結論會決定這個概念值不值得
投入完整設計文件的成本。

**已經在 production 中？** 你也可以在任何階段執行它，來測試某個特定機制、
設計變更或技術問題。傳入 `--spike` 啟動 spike 模式：一個
輕量、約 4 小時的版本，不需要 GDD 前置條件，也不影響 phase gate。

**已經有完整的 GDD 和架構了？** 想在投入 Production 之前驗證完整的遊戲迴圈，
請改用 `/vertical-slice`。

---

## Phase 1: Define the Question

**現在就讀 `references/1-question.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Phase 2: Load Concept Context

**現在就讀 `references/2-load-context.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Phase 3: Choose the Prototype Path

**現在就讀 `references/3-choose-path.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Phase 4: Plan the Prototype

**現在就讀 `references/4-plan.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Phase 5: Implement

**現在就讀 `references/5-implement.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Phase 6: Playtest Debrief

**現在就讀 `references/6-debrief.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Phase 7: Generate Prototype Report

**現在就讀 `references/7-report.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Phase 8: Creative Director Review

**現在就讀 `references/8-cd-review.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Phase 9: Summary and Next Steps

**現在就讀 `references/9-summary.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

## Spike Mode

**觸發條件：** `--spike` 旗標，或 Phase 1 裡選了「Mid-production spike」這個進入選項。

**現在就讀 `references/spike-mode.md` 並照著做** — 這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復過，就再讀一次。

### Important Constraints

- 原型程式碼絕對不能 import production 的原始碼檔案
- production 程式碼絕對不能 import 原型目錄
- 如果建議是 PROCEED，production 的實作要從頭寫 — 
  原型程式碼絕對不會被 refactor 成 production
- 總投入硬性上限是 1 天（概念原型只測試一個機制）
- 只測試一個機制 — 如果範圍擴大，就停下來並簡化問題
- 不要打磨。除非 UI 本身就是那個機制，否則不要選單、不要 game over、不要音樂、不要 UI
- 如果在 engine 裡迭代了 2 小時還是卡住，就重新定義問題或換路徑
- **3 次 PIVOT 迭代 → 強制做出 KILL 決定。** 如果這是同一個
  概念第三次得到 PIVOT 的結論，這個概念很可能行不通。
  問：「Is this the right idea, or am I in the sunk cost trap?」一個
  從頭做原型的新概念，幾乎一定比第四次迭代一個苦苦掙扎的概念好。
- 做 2-3 個不同的概念變體再挑最好的，是比把一個概念
  迭代到死更健康的策略。原型之間的自然淘汰
  勝過意志力。
- **網路/多人遊戲：** 本機原型沒辦法驗證
  網路機制的手感。延遲會從根本上改變戰鬥、移動和
  預測的手感 — 在 0ms 本機跑的原型，跟 80ms 網路延遲下的感覺
  會完全不同。用本機原型來驗證機制是否
  *有趣*。不要把它當成在真實網路條件下 *手感好* 的證據。
  網路手感需要真實的對等端，或模擬延遲（例如 throttle
  工具、網路條件模擬器）。
