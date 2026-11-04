---
name: patch-notes
description: "從 git 歷史和 changelog 產生給玩家看的 patch notes，把開發者的語言翻成玩家看得懂的說法。"
argument-hint: "[version] [--style brief|detailed|full]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/patch-notes/../../hooks/yaml-helper.sh" resolve_config *), Bash(git log *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次檔案寫入，都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

# Patch Notes

## Provenance check — before reading any history

**確認你要讀的歷史是屬於「這款」遊戲的。** 在 Phase 2 之前執行，
沒過就停下來。

1. 取樣最近的 log：`git log --oneline -20`。**如果它是空的或 git
   不能用，就跳過這個檢查** — 沒有東西可分類，
   而 Phase 2 的沒有 changelog 資料的分支才是正確的停止點。
2. **對範圍內的每一個 commit 逐一分類**，歸入恰好一類：
   - **Game** — 改變玩家玩的遊戲：機制、內容、平衡、
     美術、音訊、UI，或其中任何一項的 bug。
   - **Framework / maintenance** — 改變 CCGS 本身或專案的工具：
     主旨提到 skill、hook、agent、測試計畫、CI、框架自己的
     文件。**不放進給玩家的 notes，但也不是要停下來的理由。**
   - **Unclear** — 當成 framework。你沒辦法有把握歸類的 commit，
     就不該拿來寫玩家看的文案。
3. 然後根據計數決定：
   - **至少有一個 Game commit** → 繼續，而且**只**用那些。要說明
     用了幾個、總共幾個，讓讀的人看得出過濾有執行。
   - **零個 Game commit** → 停下來，用下面的訊息，並給出計數（總共幾個裡的 0 個），讓讀的人看得出過濾有執行。

> **逐個 commit 過濾；不要因為 repo 裡剛好有維護性的工作就停下來。**
> 每個建立在這個框架上的專案，都會累積動到
> hook、CI 和 skill 的 commit — 遊戲 repo *就是*框架 repo，所以以 repo 為單位的
> 停止，幾乎會在每個真實專案上觸發。危險不在於這類
> commit *存在*；而是它們會被**渲染成給玩家看的文案**。
> 把它們排除正好解決這點，而以 repo 為單位的停止做不到。

繼續之前，先便宜地佐證一下：Game commit 應該會提到
`design/` 和 code root（`src/`、`Assets/` 或 `Source/`）裡出現的系統。如果
它們提到的產品是那些目錄
從來沒提過的，那才是真正的錯誤歷史訊號 — 停下來。

如果範圍內**沒有任何** commit 是這款遊戲的，就講出來並停下來：

> "The git history in this repo does not appear to belong to [game]: 0 of the [N]
> recent commits are Game commits. The recent
> commits describe [what they actually describe]. I cannot generate release notes
> from it — point me at the right history, or supply the change list directly."

Verdict: **BLOCKED** — 在這裡停下來，不產生 notes。

**為什麼這是硬性停止，不是警告。** 框架內部的 commit 被渲染成
玩家文案，讀起來就像真的變更：一個 session-hook 的 timeout，會變成*「Fixed an
issue where progress from your last session could be lost on launch」*，
而這款遊戲**根本沒有存檔系統**。那段文案很流暢、很可信，而且完全是假的。
讀的人分辨不出差別；只有這個檢查能分辨。

---

## Phase 1: Parse Arguments

- `version`：要產生 notes 的 release 版本（例如 `1.2.0`）
- `--style`：輸出風格 — `brief`（條列重點）、`detailed`（附脈絡）、`full`（附開發者評論）。預設：`detailed`。

如果沒有提供版本，繼續之前先問使用者。

---

## Phase 2: Gather Change Data

- 如果 `production/releases/[version]/changelog.md` 的內部 changelog 存在，就讀它
- 也檢查 `docs/CHANGELOG.md` 裡相關版本的條目
- 作為退路，在前一個 release tag 和目前的 tag/HEAD 之間執行 `git log`
- 讀 `production/sprints/` 裡的 sprint 回顧，取得脈絡
- 讀 `design/balance/` 裡任何平衡變更文件
- 如果有的話，讀 QA 的 bug 修復紀錄

**如果沒有任何 changelog 資料**（`production/releases/[version]/changelog.md`
和 `docs/CHANGELOG.md` 裡這個版本的條目都不存在，而且 git log 是空的或不能用）：

> "No changelog data found for [version]. Run `/changelog [version]` first to generate the
> internal changelog, then re-run `/patch-notes [version]`."

Verdict: **BLOCKED** — 在這裡停下來，不產生 notes。

---

## Phase 2b: Detect Tone Guide and Template

**偵測語氣指南** — 起草 notes 之前，檢查有沒有寫作風格的指引：

1. 檢查 `.claude/docs/technical-preferences.md` 有沒有任何「tone」、「voice」或「style」
   欄位或章節。
2. 如果 `docs/PATCH-NOTES-STYLE.md` 存在就檢查它。
3. 如果 `design/community/tone-guide.md` 存在就檢查它。
4. 如果任何來源包含語氣/聲音/風格的指示，就把它們擷取出來，並套用
   到產生的 notes 的用語和框架上。
5. 如果哪裡都找不到語氣指引，預設是：
   對玩家友善、非技術性的用語；熱情但不誇大；
   聚焦在玩家體驗到什麼，不是開發者改了什麼。

**偵測範本** — 檢查有沒有 patch notes 範本：

1. 用 Glob 找 `docs/patch-notes-template.md` 和 `.claude/docs/templates/patch-notes-template.md`。
2. 如果在其中任一處找到，就讀它，並把它當成 Phase 4 的輸出結構，
   取代內建的風格範本（Brief / Detailed / Full）。把
   範本的各章節用分類好的資料填進去，把每個分類對應到
   意思相同的範本章節（New Content → 它的新功能章節，
   Bug Fixes → 它的修復章節）；沒有對應章節的分類，放到
   最接近的那一個底下，絕對不能丟掉。範本的頁首和頁尾文字照原樣保留。
   要在輸出裡說明用了哪個範本 — 而且如果有傳 `--style`，
   也要說明範本取代了它。
3. 如果找不到，就用 Phase 4 定義的內建風格範本。

---

## Phase 3: Categorize and Translate

把所有變更分到給玩家看的類別：

- **New Content**：新功能、地圖、角色、道具、模式
- **Gameplay Changes**：平衡調整、機制變更、成長變更
- **Quality of Life**：UI 改善、便利功能、無障礙
- **Bug Fixes**：依系統分組（戰鬥、UI、網路等）
- **Performance**：玩家可能感受得到的最佳化改善
- **Known Issues**：對還沒解決的問題保持透明

把開發者的語言翻成玩家的語言：

- "Refactored damage calculation pipeline" → "Improved hit detection accuracy"
- "Fixed null reference in inventory manager" → "Fixed a crash when opening inventory"
- "Reduced GC allocations in combat loop" → "Improved combat performance"
- 移除純內部、不影響玩家的變更
- 平衡變更要保留具體數字（damage: 50 → 45）

---

## Phase 4: Generate Patch Notes

### Brief Style
```markdown
# Patch [Version] — [Title]

**New**
- [Feature 1]
- [Feature 2]

**Changes**
- [Balance/mechanic change with before → after values]

**Fixes**
- [Bug fix 1]
- [Bug fix 2]

**Known Issues**
- [Issue 1]
```

### Detailed Style
```markdown
# Patch [Version] — [Title]
*[Date]*

## Highlights
[1-2 sentence summary of the most exciting changes]

## New Content
### [Feature Name]
[2-3 sentences describing the feature and why players should be excited]

## Gameplay Changes
### Balance
| Change | Before | After | Reason |
| ---- | ---- | ---- | ---- |
| [Item/ability] | [old value] | [new value] | [brief rationale] |

### Mechanics
- **[Change]**: [explanation of what changed and why]

## Quality of Life
- [Improvement with context]

## Bug Fixes
### Combat
- Fixed [description of what players experienced]

### UI
- Fixed [description]

### Networking
- Fixed [description]

## Performance
- [Improvement players will notice]

## Known Issues
- [Issue and workaround if available]
```

### Full Style
包含 Detailed 的全部內容，再加上：
```markdown
## Developer Commentary
### [Topic]
> [Developer insight into a major change — why it was made, what was considered,
> what the team learned. Written in first-person team voice.]
```

---

## Phase 5: Review Output

檢查產生的 notes：

- 沒有內部行話（把技術術語換成對玩家友善的用語）
- 沒有提到內部系統、ticket 或 sprint 編號
- 平衡變更有附上前後數值
- Bug 修復描述的是玩家的體驗，不是技術原因
- 語氣符合遊戲的調性（依遊戲風格調整正式程度）

---

## Phase 6: Save Patch Notes

把完成的 patch notes 呈現給使用者，並附上：各類別的變更數量，以及任何被排除的內部變更（供審查）。

問：「May I write these patch notes to `docs/patch-notes/[version].md`, and an
archive copy to `production/releases/[version]/patch-notes.md`?」

使用者答應就兩個檔案都寫，目錄不存在的話先建立。
如果不答應，就什麼都不寫。

---

## Phase 7: Next Steps

Verdict: **COMPLETE** — patch notes generated and saved.（如果寫入被
拒絕：Verdict: **COMPLETE** — patch notes generated and shown, not saved.）

- 執行 `/release-checklist`，在發佈前驗證所有其他 release gate 都達成了。
- 公開張貼之前，把 patch notes 草稿分享給 community-manager 做語氣審查。
