---
name: changelog
description: "從 git commit 和 sprint 資料自動產生 changelog，分內部版和玩家版。"
argument-hint: "[version|sprint-number]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/changelog/../../hooks/yaml-helper.sh" resolve_config *), Bash(git log *), Bash(git tag --list*), Bash(git rev-parse *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次檔案寫入都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。

# Changelog

## Recent History

最近的 commit：

!`git log --oneline -30 2>/dev/null || true`

最近的 tag（由新到舊）：

!`git tag --list --sort=-v:refname 2>/dev/null | head -5`

## 來源檢查：信任上面的歷史之前先做

**上面的 commit 可能不屬於這款遊戲。** 這個 skill 的歷史區塊是在內文執行*之前*
自動解析的，所以讀取已經發生了，這個檢查管的是那份輸出能不能用，不是有沒有去抓。

1. 讀上面注入的 commit 標題。**如果一個都沒有（log 是空的，或 git 不能用），就跳過這個檢查**：
   沒有東西可以分類，Phase 1 的沒有歷史分支就是正確的停法。
2. **逐一分類**：**Game**（機制、內容、平衡、美術、音訊、
   UI，或這些東西的 bug）、**Framework / maintenance**（標題提到 skill、
   hook、agent、測試計畫、CI，或框架自己的文件），或是 **Unclear**，
   而 Unclear 一律當成 Framework。
3. 依數量決定：
   - **至少有一個 Game commit** → 只用那些繼續，並說明用了
     幾個、總共幾個。
   - **零個 Game commit** → 停下來，用下面的訊息。

> **逐個 commit 過濾；repo 裡有維護工作，不代表它是錯的 repo。**
> 用這個框架的每個專案都會累積動到 hook、CI 和
> skill 的 commit，遊戲 repo *就是*框架 repo，所以遇到它們就停，
> 幾乎每個真實專案都會觸發。真正的傷害是這些 commit 變成發行文案，
> 把它們排除就能精準防止這件事。
>
> 這條規則刻意跟 `/patch-notes` 的保持一致，兩者讀
> 同一份歷史、給不同的讀者，不能對「這是誰的歷史」有不同判斷。要改就兩邊一起改。

真正的錯誤歷史訊號是另一種：Game commit 提到的產品，
`design/` 和 code root（`src/`、`Assets/` 或 `Source/`）從來沒提過。
如果看到這種情況，就停。

如果範圍內**沒有任何** commit 是這款遊戲的，就直說並停下：

> "The git history in this repo does not appear to belong to [game]: 0 of the [N]
> recent commits are Game commits. The recent
> commits describe [what they actually describe]. I cannot generate a changelog
> from it — point me at the right history, or supply the change list directly."

Verdict: **BLOCKED** — stop here without generating a changelog.

**為什麼這是硬性停止，不是警告。** 框架內部的 commit 被當成玩家文案
來寫，讀起來就像真的變更：一個 session-hook 的 timeout 會變成 *"Fixed an
issue where progress from your last session could be lost on launch"*，
而那款遊戲**根本沒有存檔系統**。那段文案流暢、可信，而且完全是假的。
讀的人分不出差別；只有這個檢查分得出來。

**不要把前言存在當成證據。** 有注入輸出，只代表指令跑了，
絕對不代表它的主題是你的遊戲。

---

這兩個區塊都是在這個 skill 執行前解析好的。把它們當作 Phase 2 的起點，
不要重跑同樣的指令。

---

## Phase 1: 解析參數

從參數讀目標版本或 sprint 編號。有給版本的話，用對應的 git tag。有給 sprint 編號的話，用 sprint 的日期範圍。

確認 repository 已初始化：跑 `git rev-parse --is-inside-work-tree` 確認 git 可用。如果不是 git repo，告知使用者並優雅地中止。

**如果沒有歷史可讀**（不是 git repository，或還沒有任何 commit）：

> "No git history found. A changelog is built from commits — commit the work
> first, or supply the change list directly."

Verdict: **BLOCKED** — stop here without generating a changelog.

---

## Phase 2: 蒐集變更資料

讀上一個 tag 或 release 之後的 git log：

```
git log --oneline [last-tag]..HEAD
```

如果沒有 tag，要明確限定範圍：`git log --oneline -n 100`。不要
退回去讀完整的 log：在成熟的 repo 上，為了涵蓋一次 release 的 changelog，那是幾千行，
而且最舊的那些最不相關。
如果 100 個 commit 追溯得不夠遠，就說出來，並要求使用者給起始 ref，
不要盲目擴大範圍。

讀 `production/sprints/` 裡相關期間的 sprint 報告，了解計畫中的工作和變更背後的 context。

讀 `design/gdd/` 裡已完成的設計文件，找這段期間實作的新功能。按章節讀：用 Grep 工具（pattern `^#`、content mode）找出需要的標題，再用 offset 和 limit 讀那幾段範圍。

---

## Phase 3: 分類變更

把每個變更歸到下列其中一個類別：

- **New Features**：全新的遊戲系統、模式或內容
- **Improvements**：既有功能的強化、UX 改善、效能提升
- **Bug Fixes**：修正壞掉的行為
- **Balance Changes**：遊戲數值、難度、經濟的調校
- **Technical Debt / Refactoring**：遊戲程式碼的重構和清理，而且不改變玩家看到的任何東西，也就是 commit 說的是重構、清理或整理，沒有提到任何修正、功能或調校。只放內部 changelog；絕對不放玩家版
- **Known Issues**：團隊知道但還沒解決的問題
- **Miscellaneous**：不符合上面類別的變更，或是訊息太模糊、無法有把握分類的 commit

每個 commit 都要檢查訊息裡有沒有 task ID 或 story 參照
（例如 `[STORY-123]`、`TR-`、`#NNN` 或類似的東西）。數出沒有任何 task 參照的 commit，
並把這個數字放進 Phase 4 的 Metrics 章節：`Commits without task reference: [N]`。

---

## Phase 4: 產生內部 Changelog

```markdown
# Internal Changelog: [Version]
Date: [Date]
Sprint(s): [Sprint numbers covered]
Commits: [Count] ([first-hash]..[last-hash])

## New Features
- [Feature Name] -- [Technical description, affected systems]
  - Commits: [hash1], [hash2]
  - Owner: [who implemented it]
  - Design doc: [link if applicable]

## Improvements
- [Improvement] -- [What changed technically and why]
  - Commits: [hashes]
  - Owner: [who]

## Bug Fixes
- [BUG-ID] [Description of bug and root cause]
  - Fix: [What was changed]
  - Commits: [hashes]
  - Owner: [who]

## Balance Changes
- [What was tuned] -- [Old value -> New value] -- [Design intent]
  - Owner: [who]

## Technical Debt / Refactoring
- [What was cleaned up and why]
  - Commits: [hashes]

## Miscellaneous
- [Change that didn't fit other categories, or vague commit message]
  - Commits: [hashes]

## Known Issues
- [Issue description] -- [Severity] -- [ETA for fix if known]

## Metrics
- Total commits: [N]
- Files changed: [N]
- Lines added: [N]
- Lines removed: [N]
- Commits without task reference: [N]
```

---

## Phase 5: 產生玩家版 Changelog

```markdown
# What is New in [Version]

## New Features
- **[Feature Name]**: [Player-friendly description of what they can now do
  and why it is exciting. Focus on the experience, not the implementation.]

## Improvements
- **[What improved]**: [How this makes the game better for the player.
  Be specific but avoid jargon.]

## Bug Fixes
- Fixed an issue where [describe what the player experienced, not what was
  wrong in the code]
- Fixed [player-visible symptom]

## Balance Changes
- [What changed in player-understandable terms and the design intent.
  Example: "Healing potions now restore 50 HP (up from 30) -- we felt
  players needed more recovery options in late-game encounters."]

## Known Issues
- We are aware of [issue description in player terms] and are working on a
  fix. [Workaround if one exists.]

---
Thank you for playing! Your feedback helps us make the game better.
Report issues at [link].
```

---

## Phase 6: 輸出

把兩份 changelog 都輸出給使用者。內部 changelog 是主要的工作文件。玩家版 changelog 在審閱後就可以貼到社群上。

---

## Phase 7: 提議寫入檔案

呈現完 changelog 之後，問使用者：

> "May I write this changelog to `docs/CHANGELOG.md`?
> [A] Yes, append this entry (recommended if the file already exists)
> [B] Yes, overwrite the file entirely
> [C] No — I'll copy it manually"

- 問之前先檢查 `docs/CHANGELOG.md` 是否存在。如果存在，預設推薦
  **[A] append**。
- 使用者選 [A]：把新的內部 changelog 條目附加到現有檔案的最上面
  （最新的條目在最前面）。
- 使用者選 [B]：用新的 changelog 覆寫整個檔案。
- 使用者選 [C]：停在這裡，不寫入。

寫入成功後：Verdict: **CHANGELOG WRITTEN** — changelog saved to `docs/CHANGELOG.md`.
使用者拒絕的話：Verdict: **COMPLETE** — changelog generated.

---

## Phase 7: 下一步

- 用 `/patch-notes [version]` 產生一份有排版、可存檔的公開發行版本。
- 對外發布 changelog 之前，先用 `/release-checklist`。

### 準則

- 絕對不要在玩家版 changelog 裡洩漏內部程式碼參照、檔案路徑或開發者名字
- 把相關的變更歸在一起，不要一個一個列 commit
- 如果 commit 訊息不清楚，去看相關的檔案和 sprint 資料找 context
- 平衡變更一定要附上設計理由，不能只放數字
- Known issues 要誠實，玩家會欣賞透明
- 如果 git 歷史很亂（merge commit、revert、fixup commit），就整理成通順的敘述，不要一個 commit 一個 commit 照字面列
