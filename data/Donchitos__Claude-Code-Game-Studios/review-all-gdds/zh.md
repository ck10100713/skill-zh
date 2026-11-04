---
name: review-all-gdds
description: "跨 GDD 的整體審查：系統之間的矛盾、主導策略、經濟失衡、認知負荷過重、支柱偏移。"
argument-hint: "[focus: full | consistency | design-theory | since-last-review]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Agent, Bash(bash "*/.claude/skills/review-all-gdds/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/review-scope.sh*)
model: opus
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,system_overrides`

# Review All GDDs

這個 skill 會同時讀取每一份系統 GDD，並做兩種互補的
審查，這兩種審查沒辦法對單一 GDD 各別做：

1. **Cross-GDD Consistency**：文件之間的矛盾、過時的引用，以及擁有權衝突
2. **Game Design Holism**：只有把所有系統放在一起看才會浮現的問題：
   主導策略、壞掉的經濟系統、認知負荷過重、支柱偏移、互相競爭的成長循環

**這跟 `/design-review` 不一樣**，後者審查單一 GDD 的內部
完整度。這個 skill 審查的是所有 GDD 之間的*關係*。

**什麼時候跑：**
- 所有 MVP 層級的 GDD 都各別核准之後
- 任何 GDD 在製作中途大幅修訂之後
- 在 `/create-architecture` 開始之前（建立在不一致的 GDD 上的架構，
  會繼承那些不一致）

每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
屬於 `automation_always_ask` 的類別一律要詢問）。

**參數模式：**

**Focus：** `$ARGUMENTS`（空白 = `full`）

- **沒有參數 / `full`**：一致性和設計理論兩個 pass 都跑
- **`consistency`**：只做 cross-GDD 一致性檢查（比較快）
- **`design-theory`**：只做遊戲設計整體性檢查
- **`since-last-review`**：只看上次審查報告之後有修改過的 GDD（以 git 為準）

---

**每份 GDD 的 `workflow`**（依 `.claude/docs/workflow-modes.md`）：每份 GDD 依它
實際生效的等級驗證，也就是專案的值，如果上面的區塊有列出該系統的
`system_overrides` 那一列，就以它覆蓋。在 `full` 時，驗證所有 GDD 的全部 8
段。在 `standard` 時，驗證 5 個必要段落；
選用段落（Player Fantasy、Tuning Knobs、有條件的 Formulas）只當作
建議提出。在 `minimal` 時，這個 skill 不適用（沒有 GDD）。

## Phase 1: Load Everything

**現在讀 `references/1-load.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

### Parallel Execution

Phase 2（Consistency）和 Phase 3（Design Theory）是獨立的：它們讀
同樣的 GDD 輸入，但產出各別的報告。同時把兩個都生成為平行的 `Agent`
agent，不要等 Phase 2 完成才
開始 Phase 3。兩份結果都收齊後，才寫合併報告。

兩個都以 `game-designer` sub-agent 生成（`subagent_type: game-designer`），GDD
一致性和設計理論審查是它的專長領域。

**生成 Phase 2 和 Phase 3 的 agent 時，一定要傳：**
- 各階段需要的已載入 GDD **內容**，**不是檔案路徑**。把
  段落貼進去；sub-agent 有自己的 context，沒辦法重讀 Phase 1 的
  結果，所以給路徑會逼它整個重讀（也跟下面「不要重讀」的
  規則矛盾）。只傳該階段的那一部分：Phase 2（一致性）需要每份 GDD 的
  Dependencies、Detailed Design/Rules、Formulas、Tuning Knobs 和 Acceptance
  Criteria；Phase 3（設計理論）需要 Player Fantasy、成長/獎勵
  結構和遊戲支柱。
- 完整的 entity registry 內容（`design/registry/entities.yaml`），如果在 Phase 1b 載入過（貼 registry 的文字，不只是檔案路徑）
- 指派給該 agent 那個階段的具體檢查項目（Phase 2 拿 2a–2f；Phase 3 拿 3a–3g）
- 引擎名稱和版本：`project.yaml` 的 `engine.name` 和 `engine.version`，各欄位獨立解析（如果某個 key 不存在或是空的，就用 `.claude/docs/technical-preferences.md`），加上 `docs/engine-reference/[engine]/VERSION.md`

不要指望 subagent 會重讀這些檔案：它有自己的 context window，除非在 `Agent` prompt 裡明確傳進去，否則它拿不到 Phase 1 的結果。

---

## Phase 2: Cross-GDD Consistency

**現在讀 `references/2-consistency.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 3: Game Design Holism

**現在讀 `references/3-design-holism.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 4: Cross-System Scenario Walkthrough

**現在讀 `references/4-scenarios.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 5: Output the Review Report

**現在讀 `references/5-report.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 6: Write Report and Flag GDDs

**現在讀 `references/6-write.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Phase 7: Handoff

**現在讀 `references/7-handoff.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Error Recovery Protocol

**首先，驗證產出物。** 如果回傳合約指定了路徑，在把這個階段
當作完成之前，先確認路徑存在：**一個被指名的產出物如果不在
磁碟上，這個階段就是失敗，不管回應讀起來多流暢。** agent 可能
燒掉整個階段，回傳一段看似合理的開場白，卻什麼都沒寫，
這既不是 BLOCKED，也不是錯誤，也不是「無法完成」，所以下面的觸發條件
永遠不會被觸發。要恢復它，並點名沒達成的合約；context
通常還在。

如果任何生成的 agent 回傳 BLOCKED、出錯或無法完成：**立刻
把它提出來，不要越過被它擋住的依賴往下走，而且一定要產出
部分報告**（這裡的重試範圍 = 更少的 GDD / 單一系統）。完整流程：
`.claude/docs/error-recovery-protocol.md`。

---

## Collaborative Protocol

**在 `collaborative` 模式（預設）。** `guided` 和 `autonomous` 模式請
看 `.claude/docs/automation-modes.md`。在 `autonomous` 模式下，
PASS/CONCERNS/FAIL 的結論仍然會印出並記錄，只有結尾的
交接 widget 會被跳過。

1. **默默地讀**：呈現任何東西之前，先載入所有 GDD
2. **全部秀出來**：在請求任何行動之前，先呈現完整的一致性和設計理論分析
3. **區分阻擋與建議**：不是每個問題都要擋住
   架構；要清楚說明哪些會擋
4. **不要做設計決策**：標出矛盾和選項，但絕對不要
   單方面決定哪份 GDD「才對」
5. **寫之前先問**：寫報告或更新
   系統索引之前先確認
6. **要具體**：每個問題都必須引用確切的 GDD、段落和相關文字；
   不准含糊的警告
