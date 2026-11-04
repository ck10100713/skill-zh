---
name: content-audit
description: "稽核 GDD 規定的內容數量和實際做出來的，看計畫 vs 已完成的落差。"
argument-hint: "[system-name | --summary | (no arg = full audit)]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/content-audit/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys workflow,automation`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次檔案寫入都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。

上面已經解析好了，直接用。沒有這個區塊 → 用 `.claude/docs/config-resolution.md` 裡的預設值。

# Content Audit

> 稽核之前先解析 `modes.workflow`：這個 skill 依 tier 而定的行為
>（「只稽核必要章節裡的規格」）要跟著解析出來的 tier 走，絕對不能
> 用假設的 tier。當 `design/gdd/systems-index.md` 這類必要輸入
> 不存在時，要回報
> **`NOT ASSESSED — NO DATA`**，不要去算落差百分比（沒有任何規格時，
> 那會除以零）。


這個 skill 被呼叫時：

解析參數：
- 沒有參數 → 對所有系統做完整稽核
- `[system-name]` → 只稽核那一個系統
- `--summary` → 只出摘要表，不寫檔案

---

**`workflow`**（見 `.claude/docs/workflow-modes.md`）：
- `full`：對所有 GDD 規格做完整的內容數量稽核。
- `standard`：只稽核必要章節裡的規格；在那些章節之外找到的任何數量，
  都列為「在這個 tier 沒有稽核」。
- `minimal`：跑不了（沒有 systems index）。

## 輸入不足：產出任何報告之前先檢查這個

**如果這個 skill 需要的輸入不存在，答案是「跑不了」，
不是一份填好的報告。** 先檢查，檢查不過就停。

1. 列出這個 skill 要讀的輸入（資料檔、先前的報告、profiler 輸出、
   測試結果、registry、原始碼）。
2. 每一項都記錄 `FOUND` 或 `ABSENT`，不是「假設存在」。
3. 如果某個章節需要的任何輸入是 ABSENT，那個章節就是
   **`NOT ASSESSED — NO DATA`**。不要估，不要從
   相鄰的產物推論，也不要留一個規定要填的格子讓下一個
   讀範本的人去填。
4. 如果**所有**需要的輸入都是 ABSENT，就停下來，把
   **`NOT ASSESSED — NO DATA`** 當作整份報告的 verdict 回報，並指出缺了什麼、
   哪個 skill 會產出它（`design/gdd/systems-index.md` 是 `/map-systems`，GDD 是 `/design-system`）。

**`NOT ASSESSED` 的 verdict 是成功。** 沒有資料時，
它就是對「資料怎麼說？」最正確、最有用的答案。它要防的失敗模式
很明確：一份 verdict 列舉裡沒有「跑不了」狀態的報告，會產生
**假的乾淨通過**：一個沒有素材也沒有標準的專案，素材稽核卻回報 COMPLIANT；
或是一份效能分析，沒有任何 profiler 資料、也從沒設過預算，卻回報「對 16.67ms 預算有 >99% 的餘裕」。

**沒有證據，不代表沒有問題。** 因為沒有檔案可掃，所以掃不到任何東西，
這並沒有驗證任何事。要說清楚是這兩種情況的哪一種，
光看綠色結果，讀的人分不出來。

---

## Phase 1: 蒐集 Context

1. **讀 `design/gdd/systems-index.md`**，取得完整的系統清單、它們的
   類別，以及 MVP／優先層級。按章節讀：用 Grep 工具（pattern `^#`、content mode）
   找出需要的標題，再用 offset 和 limit 讀那幾段範圍。

2. **先用 registry 計數**：如果 `design/registry/entities.yaml` 存在，先讀它。
   它的 `entities` 和 `items` 章節就是這次稽核要數的、跨 GDD 的具名內容，
   已經整理好，每個項目都有 `source:` GDD：
   ```
   Grep pattern="^  - name:" path="design/registry/entities.yaml" output_mode="content" -A 2
   ```
   `- name:` 會出現在 registry 的四個章節；只保留 `-A 2` 的 context
   顯示它位於 `entities:` 或 `items:` 底下的名稱（這次稽核要數的
   具名內容，不是 `formulas:`/`constants:`）。把這些當成
   **計畫中**的具名內容集合，不用完整讀擁有它們的 GDD。
   **如果 `design/registry/entities.yaml` 不存在或沒有項目**（在 `/design-system` 填入之前，
   它出貨時是個空的 stub），就跳過這步，
   改靠下面的 GDD 掃描，行為不變，只是比較貴。

3. **L0 預掃描**：在完整讀任何 GDD 之前，先跑**兩個** grep，
   它們回答不同的問題，不能共用同一個 pattern：

   a. 哪些 GDD 有 Summary（分母／fail-open 檢查）：
   ```
   Grep pattern="^## Summary" glob="design/gdd/*.md" output_mode="files_with_matches"
   ```

   b. 哪些 GDD 真的有宣告內容數量（縮小範圍的步驟）：
   ```
   Grep pattern="[0-9]+[[:space:]]+(enemies|enemy types|levels|areas|maps|stages|items|weapons|equipment|abilities|skills|spells|cutscenes|conversations|dialogue scenes|bosses|quests)|(enemy|item|weapon|ability|level) types:" glob="design/gdd/*.md" output_mode="files_with_matches"
   ```

   > **兩個掃描要分開。** `## Summary` 會比對到每一份合規的 GDD，
   > 所以跟它取聯集什麼都縮不小，而像
   > `N enemies` 這種字面的 placeholder 不會比對到任何真實的 GDD。Pattern (b) 比對的是數字後面接
   > 步驟 5 實際擷取的那些內容名詞。

   **缺少 Summary 時要 fail open。** 先確立分母：glob
   `design/gdd/*.md` 並數出 **N**。**掃描 (a)** 比對到的數量少於 N，代表
   那些 GDD 早於 `## Summary`，絕對不要把沒有 Summary 當成這個系統
   不在範圍內；(a) 零個比對，意思是「還沒有任何 GDD 有 Summary」，不是「沒有
   可稽核的內容」。要完整讀沒比對到的範圍內 GDD。

   單一系統稽核：跳過這步，直接完整讀。
   完整稽核：完整讀 **掃描 (b)** 比對到、
   **而且還沒被步驟 2 的 registry 項目完整涵蓋**的 GDD，
   再加上掃描 (a) 漏掉的每一份，**fail-open 規則勝過這個
   縮小範圍**：沒有 `## Summary` 的 GDD 就算掃描 (b)
   沒比對到它，也要完整讀。只有那種有 Summary、卻沒有內容數量字眼的 GDD（純
   機制的 GDD），才註明為「No auditable content counts」，不用完整讀。

4. **完整讀範圍內的 GDD 檔案**（如果有指定系統名稱，就是那個單一系統的 GDD）。這一步
   需要整份 GDD：用它的標題（用 Grep 工具找：pattern `^#`、content mode）
   分段讀，因為超過 40 KB 的整檔 Read 會被拒絕。

5. **每份 GDD，擷取明確的內容數量或清單**，並記下每一項所在的 `##` 章節。在 `standard`，必要章節（`.claude/docs/workflow-modes.md`）之外的數量，
   要放到 "Not audited at this tier" 清單，絕對不能放進 inventory。找像這樣的模式：
   - "N enemies" / "enemy types:" / 具名敵人清單
   - "N levels" / "N areas" / "N maps" / "N stages"
   - "N items" / "N weapons" / "N equipment pieces"
   - "N abilities" / "N skills" / "N spells"
   - "N dialogue scenes" / "N conversations" / "N cutscenes"
   - "N quests" / "N missions" / "N objectives"
   - 任何明確列舉的清單（具名內容項目的條列清單）

6. **用擷取到的資料建立內容 inventory 表**：

   | System | Content Type | Specified Count/List | Source GDD |
   |--------|-------------|---------------------|------------|

   注意：如果 GDD 只用描述性的方式講內容、沒有給數量，就記成
   "Unspecified" 並標記起來，沒有指定數量是值得註明的設計缺口。

---

## Phase 2: 實作掃描

Phase 1 找到的每種內容類型，都掃描相關目錄，數出
已經實作了多少。用 Glob 和 Grep 找檔案。

**在 Unreal 上，內容放在 `Content/`**（地圖和資料資產都是），而
code root（`Source/<Module>/`）只放 C++。所以在 Unreal 上，下面每個 `assets/…` glob
也要在 `Content/` 底下跑（用 `*.uasset` 取代資料副檔名），
而關卡是 `Content/**/*.umap`。跳過這點，會在每個
Unreal 專案找到零個關卡，並把它們全報成 NOT STARTED。

**在 Unity 上，內容放在 `Assets/` 底下**（大小寫要完全比對，
見 `.claude/docs/code-root-resolution.md`），而且很少放在 `data/` 資料夾。所以
在 Unity 上，下面每個 `assets/…` glob 也要在 `Assets/` 底下跑，不要求
要有 `data/` 這一段，items 的話是 `Assets/**/items/**`、`Assets/**/Items/**` 和
`Assets/**/*Item*.asset`，而且資料檔包含 `.asset`（ScriptableObject）
和 `.prefab`。跳過這點，會在 Unity 專案找到零個 item、ability、quest 和對話，
並把它們全報成 NOT STARTED。

**Levels / Areas / Maps：**
- Glob `assets/**/*.tscn`、`assets/**/*.unity`、`assets/**/*.umap`
- Glob **code root** 找 scene 檔案：`*.tscn`（Godot）、`*.unity`（Unity）；在 Unreal 上改用 `Content/**/*.umap`（見上）。依 `.claude/docs/code-root-resolution.md` 解析 root。**如果 code root 解析不出來，就回報 `NOT ASSESSED — code root unresolved`，不要回報零個命中。**
- 在名為 `levels/`、`areas/`、`maps/`、
  `worlds/`、`stages/` 的子目錄裡找 scene 檔案
- 數出看起來是關卡／場景定義的不重複檔案（不含 UI scene）

**Enemies / Characters / NPCs：**
- Glob `assets/data/**/enemies/**`、`assets/data/**/characters/**`
- Glob `<code root>/**/enemies/**`、`<code root>/**/characters/**`
- 找定義 entity 數值的 `.json`、`.tres`、`.asset`、`.yaml` 資料檔
- 在角色子目錄裡找 scene/prefab 檔案

**Items / Equipment / Loot：**
- Glob `assets/data/**/items/**`、`assets/data/**/equipment/**`、
  `assets/data/**/loot/**`
- 找 `.json`、`.tres`、`.asset` 資料檔

**Abilities / Skills / Spells：**
- Glob `assets/data/**/abilities/**`、`assets/data/**/skills/**`、
  `assets/data/**/spells/**`
- 找 `.json`、`.tres`、`.asset` 資料檔

**Dialogue / Conversations / Cutscenes：**
- Glob `assets/**/*.dialogue`、`assets/**/*.csv`、`assets/**/*.ink`
- 在 `assets/data/` 裡 grep 對話資料檔

**Quests / Missions：**
- Glob `assets/data/**/quests/**`、`assets/data/**/missions/**`
- 找 `.json`、`.yaml` 定義檔

**引擎專屬的注意事項（要在報告中說明）：**
- 數量只是近似值：這個 skill 沒辦法完美解析每種引擎
  格式，也分不出僅限編輯器的檔案和實際出貨的內容
- Scene 檔可能同時包含 gameplay 內容和系統／UI scene；掃描
  會數所有比對到的，並註明這個但書

---

## Phase 3: 落差報告

產出落差表：

```
| System | Content Type | Specified | Found | Gap | Status |
|--------|-------------|-----------|-------|-----|--------|
```

**Status 類別：**
- `COMPLETE`：Found ≥ Specified（100% 以上）
- `IN PROGRESS`：Found 是 Specified 的 50–99%
- `EARLY`：Found 是 Specified 的 1–49%
- `NOT STARTED`：Found 是 0

**優先度旗標：**
符合下列情況，就在報告中把系統標成 `HIGH PRIORITY`：
- Status 是 `NOT STARTED` 或 `EARLY`，而且
- 該系統在 systems index 裡被標成 MVP 或 Vertical Slice，或者
- systems index 顯示該系統卡住了下游的系統

**摘要行：**
- 規定的內容項目總數（Specified 欄所有值的總和）
- 找到的內容項目總數（Found 欄所有值的總和）
- 整體落差百分比：`(Specified - Found) / Specified * 100`

Found 是 `NOT ASSESSED`（code root 解析不出來）的那一列，沒有 Gap 或
Status，絕對不是 `NOT STARTED`，而且不計入兩個總數；摘要要點名它。

---

## Phase 4: 輸出

### 完整稽核和單一系統模式

把落差表和摘要呈現給使用者。問："May I write the full report to `docs/content-audit-[YYYY-MM-DD].md`?"

回答 yes 就寫檔案：

```markdown
# Content Audit — [Date]

## Summary
- **Total specified**: [N] content items across [M] systems
- **Total found**: [N]
- **Gap**: [N] items ([X%] unimplemented)
- **Scope**: [Full audit | System: name] — [all GDD sections | required sections only (workflow: standard)]
- **Not audited at this tier**: [counts found only outside the required sections — or "none"; omit at `full`]

> Note: Counts are approximations based on file scanning.
> The audit cannot distinguish shipped content from editor/test assets.
> Manual verification is recommended for any HIGH PRIORITY gaps.

## Gap Table

| System | Content Type | Specified | Found | Gap | Status |
|--------|-------------|-----------|-------|-----|--------|

## HIGH PRIORITY Gaps

[List systems flagged HIGH PRIORITY with rationale]

## Per-System Breakdown

### [System Name]
- **GDD**: `design/gdd/[file].md`
- **Content types audited**: [list]
- **Notes**: [any caveats about scan accuracy for this system]

## Recommendation

Focus implementation effort on:
1. [Highest-gap HIGH PRIORITY system]
2. [Second system]
3. [Third system]

## Unspecified Content Counts

The following GDDs describe content without giving explicit counts.
Consider adding counts to improve auditability:
[List of GDDs and content types with "Unspecified"]
```

寫完報告後，問：

> "Would you like to create backlog stories for any of the content gaps?"

回答 yes：使用者選的每個系統，建議一個 story 標題，並依落差的大小，
引導他們用 `/create-stories [epic-slug]` 或 `/quick-design`。

### --summary 模式

直接把落差表和摘要印在對話裡。不要寫檔案。
最後說："Run `/content-audit` without `--summary` to write the full report."

---

## Phase 5: 下一步

稽核之後，推薦最有價值的後續動作：

- 如果任何系統是 `NOT STARTED` 而且有 MVP 標記 → "Run `/design-system [name]` to
  add missing content counts to the GDD before implementation begins."
- 如果總落差 >50% → "Run `/sprint-plan` to allocate content work across upcoming sprints."
- 如果任何系統被標成 HIGH PRIORITY → "Run `/create-stories [epic-slug]` for each HIGH PRIORITY gap."
- 如果用了 `--summary` → "Run `/content-audit` (no flag) to write the full report to `docs/`."

用符合這次執行的 verdict 收尾：
- Verdict: **COMPLETE** — content audit finished.
- Verdict: **NOT ASSESSED — NO DATA**：缺少必要輸入（見最上面的
  說明）、範圍內沒有任何東西給出數量（沒有 registry 項目，而且每份 GDD 都是
  "Unspecified" 或 "No auditable content counts"），或有某個 Found 數量取不到
  （`NOT ASSESSED — code root unresolved`）；要點名是哪一種，數量缺少的話
  要點名 `/design-system`。算不出落差的執行，絕對不要印 COMPLETE。
