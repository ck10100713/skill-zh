---
name: consistency-check
description: "拿 entity registry 掃描所有 GDD，找出跨文件的衝突。先 grep 再讀，只盯著衝突的章節和不一致的數值。"
argument-hint: "[full | since-last-review | entity:<name> | item:<name>]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(bash "*/.claude/skills/consistency-check/../../hooks/yaml-helper.sh" resolve_config *), Bash(git log *), Bash(bash .claude/scripts/registry.sh validate*)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,system_overrides`



# Consistency Check

把所有 GDD 拿去跟 entity registry（`design/registry/entities.yaml`）比對，找出跨文件的
不一致。採用先 grep 的做法：
registry 只讀一次，然後只針對提到已登錄名稱的 GDD 章節下手，
除非有衝突需要調查，否則不讀完整文件。

**這個 skill 是寫入當下的安全網。** 它抓的是 `/design-system` 逐章檢查
可能漏掉的東西，也是 `/review-all-gdds` 的整體審查
抓得太晚的東西。

**何時執行：**
- 每寫完一份新的 GDD 之後（在進下一個系統之前）
- 在 `/review-all-gdds` 之前（讓那個 skill 從乾淨的基準線開始）
- 在 `/create-architecture` 之前（不一致會污染下游的 ADR）
- 隨時：`/consistency-check entity:[name]`，專門檢查某一個 entity

**輸出：** 衝突報告，加上選擇性的 registry 修正

---

每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。

**`workflow`**（見 `.claude/docs/workflow-modes.md`），針對每份 GDD 依它的
**有效** tier 套用：如果區塊裡有列出那份 GDD 的系統（它的
檔名主體），就用 `system_overrides` 那一列，否則用專案的值：
- `full`：對所有 GDD 章節做完整的 entity-registry 交叉比對。
- `standard`：只對必要章節做交叉比對。報告的
  Scope 那行要說明這件事，而在這些章節之外、替已登錄名稱寫出的每個值，
  都要列為「在這個 tier 沒有檢查」（Phase 3 會套用這一點）。
- `minimal`：沒有意義（沒有 GDD 可以檢查）。

## Phase 1: 解析參數並載入 Registry

**模式：**
- 沒有參數 / `full`：把所有已登錄的項目對所有 GDD 檢查
- `since-last-review`：只檢查自上一份審查報告之後修改過的 GDD
- `entity:<name>`：在所有 GDD 裡檢查某一個特定 entity
- `item:<name>`：在所有 GDD 裡檢查某一個特定 item

**載入 registry：**

```
Read path="design/registry/entities.yaml"
```

如果檔案不存在，或是沒有項目：
> "Entity registry is empty. Run `/design-system` to write GDDs — the registry
> is populated automatically after each GDD is completed. Nothing to check yet."

Verdict: **NOT ASSESSED — entity registry empty**。停下：什麼都沒比對，
所以沒有 PASS 可以給，也沒有東西可以寫。

從 registry 建立四個查找表：
- **entity_map**：`{ name → { source, attributes, referenced_by } }`
- **item_map**：`{ name → { source, value_gold, weight, ... } }`
- **formula_map**：`{ name → { source, variables, output_range } }`
- **constant_map**：`{ name → { source, value, unit } }`

數出已登錄項目的總數。回報：
```
Registry loaded: [N] entities, [N] items, [N] formulas, [N] constants
Scope: [full | since-last-review | entity:name]
```

對 `entity:<name>` 或 `item:<name>`，如果 registry 裡沒有那個名稱的項目，
verdict 就是 **NOT ASSESSED — `<name>` is not in the registry**：列出
最接近的已登錄名稱，然後停。檢查一個沒登錄的名稱，
什麼都沒比對，那不是 PASS。

---

## Phase 2: 找出範圍內的 GDD

```
Glob pattern="design/gdd/*.md"
```

排除放在 `design/gdd/` 裡、但不是系統 GDD 的文件：
`game-concept.md`、`systems-index.md`、`game-pillars.md`、`gameplay-tags.md`、
`entity-registry.md`、`fixture-swap-ledger.md`、`sound-bible.md`，還有任何
`gdd-cross-review-*.md`（`/review-all-gdds` 寫在這裡的報告）。

`since-last-review` 模式：
```bash
git log --name-only --pretty=format: -- design/gdd/ | grep "\.md$" | sort -u
```
限制在最近一份 `design/gdd/gdd-cross-review-*.md`
檔案的建立日期之後修改過的 GDD。

掃描之前先回報範圍內的 GDD 清單。**如果清單是空的**（沒有系統
GDD，或 `since-last-review` 找不到有變動的），verdict 就是
**NOT ASSESSED — no GDDs in scope**：說明是哪個過濾條件造成零個，然後停。
掃描空的東西找不到衝突，那不是 PASS。

---

## Phase 3: 先 Grep 的衝突掃描

每個已登錄的項目，都對每份範圍內的 GDD grep 該項目的名稱。
**不要**做完整讀取，只擷取符合的行和它們緊鄰的
context（-C 3 行）。

這是核心的最佳化：不是讀 10 份 GDD × 每份 400 行
（4,000 行），而是 grep 50 個 entity 名稱 × 10 份 GDD（50 次針對性搜尋，
每次命中大約回傳 10 行）。

**有效 tier 是 `standard` 的 GDD，只比對必要章節底下的命中。**
有效 tier 是每份 GDD 各自算的：`system_overrides.<stem>`
會取代那份 GDD 的專案 tier，兩個方向都可以（`full` 那一列會讓
每個章節都被比對）。對每份這樣的 GDD 用 `^## ` grep 一次，取得它的標題
和行號，把每個名稱命中歸到它上方最近的標題底下：
只有在 Overview、Detailed Rules / Detailed Design、Formulas、Edge
Cases、Dependencies 或 Acceptance Criteria 底下的命中才會比對，而當
`project.yaml` 設了 `workflow_overrides.tuning_knobs: true` 時，還要加上 Tuning Knobs（那個旗標
只讀一次；它只會增加章節）。其他任何命中（沒有旗標的 Tuning Knobs、Player Fantasy、任何其他章節）
都不會產生發現，也不會記錄；
把每一個有寫出值的命中（名稱、GDD、章節）列在報告的
`Not checked at this tier` 那行。

### 3a: Entity 掃描

對 entity_map 裡的每個 entity：

```
Grep pattern="[entity_name]" glob="design/gdd/*.md" output_mode="content" -C 3
```

每個 GDD 命中，都擷取 entity 名稱附近提到的值：
- 任何數值屬性（數量、成本、持續時間、範圍、比率）
- 任何分類屬性（類型、層級、類別）
- 任何衍生值（總計、輸出、結果）
- entity_map 裡登錄的任何其他屬性

把擷取到的值跟 registry 項目比對。

**衝突偵測：**
- Registry 說 `[entity_name].[attribute] = [value_A]`。GDD 說 `[entity_name] has [value_B]`。→ **CONFLICT**
- Registry 說 `[item_name].[attribute] = [value_A]`。GDD 說 `[item_name] is [value_B]`。→ **CONFLICT**
- GDD 提到 `[entity_name]`，但沒有指定那個屬性。→ **NOTE**（不算衝突，只是無法驗證）

### 3b: Item 掃描

對 item_map 裡的每個 item，在所有 GDD 裡 grep item 名稱。擷取：
- 賣價 / 價值 / 金幣價值
- 重量
- 堆疊規則（可堆疊 / 不可堆疊）
- 類別

跟 registry 項目的值比對。

### 3c: Formula 掃描

對 formula_map 裡的每個 formula，在所有 GDD 裡 grep formula 名稱。擷取：
- 公式附近提到的變數名稱
- 提到的輸出範圍或上限值

跟 registry 項目比對：
- 變數名稱不同 → **CONFLICT**
- 輸出範圍寫得不一樣 → **CONFLICT**

### 3d: Constant 掃描

對 constant_map 裡的每個 constant，在所有 GDD 裡 grep constant 名稱。擷取：
- 常數名稱附近提到的任何數值

跟 registry 的值比對：
- 數字不同 → **CONFLICT**

---

## Phase 4: 深入調查（只針對衝突）

Phase 3 發現的每個衝突，都針對有衝突的 GDD 做有針對性的完整章節讀取，
取得精確的 context：

```
Read path="design/gdd/[conflicting_gdd].md"
```
（檔案很大的話，改用範圍更寬的 context 的 Grep）

按章節讀：用 Grep 工具
（pattern `^#`、content mode）找出有衝突那個章節的標題，再用 offset 和 limit 讀那段範圍。

用完整的 context 確認衝突。判斷：
1. **哪份 GDD 是對的？** 看 registry 裡的 `source:` 欄位，
   source GDD 是權威的擁有者。任何跟它矛盾的其他 GDD，
   就是需要更新的那個。
2. **registry 本身過期了嗎？** 如果 source GDD 在 registry 項目寫入之後又更新過
   （看 git log），registry 可能已經過時。
3. **這是真的設計變更嗎？** 如果衝突代表一個刻意的
   設計決定，處理方式是：更新 source GDD、更新 registry，
   再修正所有其他 GDD。

每個衝突都要分類：
- **🔴 CONFLICT**：同一個具名的 entity/item/formula/constant，在
  不同 GDD 裡有不同的值。架構開始之前必須解決。
- **⚠️ STALE REGISTRY**：source GDD 的值變了，但 registry 沒更新。
  registry 需要更新；其他 GDD 可能本來就是對的。
- **ℹ️ UNVERIFIABLE**：提到了 entity，但沒有寫出可比較的屬性。
  不是衝突；只是記下這個參照。

---

## Phase 5: 輸出報告

```
## Consistency Check Report
Date: [date]
Registry entries checked: [N entities, N items, N formulas, N constants]
GDDs scanned: [N] ([list names])
Scope: [all GDD sections | required sections only — workflow: standard | per GDD — name each GDD whose effective tier differs, and its tier]
Not checked at this tier: [each value stated outside the required sections (name, GDD, section) — or "none"; omit when every GDD is at `full`]

---

### Conflicts Found (must resolve before architecture)

🔴 [Entity/Item/Formula/Constant Name]
   Registry (source: [gdd]): [attribute] = [value]
   Conflict in [other_gdd].md: [attribute] = [different_value]
   → Resolution needed: [which doc to change and to what]

---

### Stale Registry Entries (registry behind the GDD)

⚠️ [Entry Name]
   Registry says: [value] (written [date])
   Source GDD now says: [new value]
   → Update registry entry to match source GDD, then check referenced_by docs.

---

### Unverifiable References (no conflict, informational)

ℹ️ [gdd].md mentions [entity_name] but states no comparable attributes.
   No conflict detected. No action required.

---

### Clean Entries (no issues found)

✅ [N] registry entries verified across all GDDs with no conflicts.

---

Verdict: PASS | CONFLICTS FOUND | NOT ASSESSED
```

**Verdict：**
- **CONFLICTS FOUND**：偵測到一個以上的衝突。列出解決步驟。
- **NOT ASSESSED**：什麼都沒比對：entity registry 是空的，或
  指定的 entity 不在裡面（Phase 1），或沒有 GDD 在範圍內（Phase 2）。要說明是
  哪一種。
- **PASS**：沒有衝突。Registry 和 GDD 對所有檢查過的值意見一致，而且至少涵蓋一份 GDD。

---

## Phase 6: Registry 修正

**寫入之前先重讀。** Phase 1 在掃描之前讀了 registry，
之後別的 skill 或 session 可能已經改過它。每次 Edit 之前，讀
目前的 `design/registry/entities.yaml`，在它的章節裡找到那個項目，
並把 Edit 錨定在該項目目前的文字上，絕對不要錨定在 Phase 1 看到的內容。
新項目要附加在它那個章節最後一個既有項目之後。

如果發現過期的 registry 項目，問：
> "May I update `design/registry/entities.yaml` to fix the [N] stale entries?"

每個過期項目：
- 更新 `value` / 屬性欄位
- 把 `revised:` 設成今天的日期
- 加一則 YAML 註解記錄舊值：`# was: [old_value] before [date]`

如果在 GDD 裡發現 registry 沒有的新項目，問：
> "Found [N] entities/items mentioned in GDDs that aren't in the registry yet.
> May I add them to `design/registry/entities.yaml`?"

只加入出現在一份以上 GDD 的項目（真正跨系統的事實）。

**絕對不要刪除 registry 項目。** 如果某個項目從所有 GDD 都被移除了，就設 `status: deprecated`。

寫完之後，跑 `bash .claude/scripts/registry.sh validate`，並在 verdict 之前修掉
這次寫入新增或改動的項目的每一列問題（DUPLICATE、STATUS 或 LAYOUT 列，
或是它指到的路徑的 PATH_MISSING 列）；其他項目的問題只要告訴使用者，
不要沒被要求就去修。如果腳本不存在，或沒有任何輸出，就說 registry 檢查沒有跑，
然後把你寫的項目對照檔案標頭裡的規則重新讀一遍。

寫完之後：Verdict: **COMPLETE** — consistency check finished.
如果還有衝突沒解決：Verdict: **BLOCKED** — [N] conflicts need manual resolution before architecture begins.

### 6b: 附加到 Reflexion Log

如果發現任何 🔴 CONFLICT 項目（不管有沒有解決），
就問："May I append [N] entries to `docs/consistency-failures.md` (creating it if
absent)?" 回答 yes 就為每個衝突附加一筆；回答 no 就說明衝突沒有被記錄。

```markdown
### [YYYY-MM-DD] — /consistency-check — 🔴 CONFLICT
**Domain**: [system domain(s) involved]
**Documents involved**: [source GDD] vs [conflicting GDD]
**What happened**: [specific conflict — entity name, attribute, differing values]
**Resolution**: [how it was fixed, or "Unresolved — manual action needed"]
**Pattern**: [generalised lesson, e.g. "Item values defined in combat GDD were not
referenced in economy GDD before authoring — always check entities.yaml first"]
```

如果 `docs/consistency-failures.md` 不存在，附加之前先用這個標頭建立它：

```markdown
# Consistency Failure Log

<!-- Auto-maintained by /consistency-check. Do not edit manually. -->
<!-- One entry per detected conflict, in chronological order. -->

| Date | GDD A | GDD B | Conflict Type | Status |
|------|-------|-------|---------------|--------|
```

然後附加新的衝突項目。絕對不要自己決定跳過記錄，檔案不存在不是丟掉衝突歷史的理由；只有使用者說「no」才可以。

---

## Phase 7: Session 狀態與收尾

靜默地附加到 `production/session-state/active.md`（檔案不存在就建立）：

```
<!-- CONSISTENCY-CHECK: [date] | GDDs checked: [N] | Conflicts found: [N] | Log: docs/consistency-failures.md -->
```

> **指向 `docs/consistency-failures.md`，也就是 Phase 6 實際附加內容
> 的那個檔案。** 麵包屑是留給未來 session 去追的指標。指向
> 一個沒人寫入的檔案，會讓那個 session 去找永遠找不到的衝突歷史，
> 而且過程中不會有任何錯誤。絕對不要在這裡編一個報告檔名。

然後用 `AskUserQuestion` widget 收尾：

- **Prompt**："Consistency check complete — [N] conflicts found. What next?"
- **選項**：
  - `[A] Fix the highest-priority conflict now`
  - `[B] Run /design-review on the most conflicted GDD`
  - `[C] Stop here`

在 collaborative 和 guided 模式，絕對不要用純文字結束這個 skill，一定要
用這個 widget 收尾。在 autonomous 模式，印出發現和建議的
下一步，然後用 `log_decision` 記錄（不用 widget）。

---

## 復原 / 參考

- **如果是 PASS**：跑 `/review-all-gdds` 做整體的設計理論審查，如果所有 MVP GDD 都完成了，
  就跑 `/create-architecture`。
- **如果是 CONFLICTS FOUND**：修正被標記的 GDD，然後重跑
  `/consistency-check` 確認已解決。
- **如果是 STALE REGISTRY**：更新 registry（Phase 6），然後重跑驗證。
- 每寫完一份新的 GDD 就跑 `/consistency-check`，及早抓到問題，
  不要等到架構階段才發現。
