---
name: growth-log
description: 寫成長日誌，從完成的工作裡提煉出可重複使用的模式（根本原因、可轉移的規則、可辨識的訊號），而不是流水帳式地敘述事件；附 4 到 8 句的範本，以及合併重複項目的紀律。完成複雜任務、除錯過程、失敗或 rollback 之後記錄學到什麼、回顧一段時間的進展，或是交付關卡問你學到了什麼時使用。
metadata:
  version: 1.1.0
  origin: ECC
---

# Growth Log Skill

> **問題：** 大多數人把「修了 X 的 bug」寫成學習日誌。那是流水帳，不是學習產物。真正的成長日誌會提煉出*模式*，讓你下次能認出它。
>
> **這個 skill 教你：** 怎麼寫出能跨 session 累積複利的學習紀錄。適用於任何筆記系統：Markdown 檔、Notion、Obsidian、純文字。範本是通用的，請依你的環境調整。

## When to Activate

- 完成複雜任務之後（多檔案、新功能、架構變更）
- 失敗、犯錯，或是「這比預期的難」的時刻之後
- 想回顧一段時間內學到了什麼的時候

**什麼時候不要啟用：** 瑣碎的變更（改錯字、單行微調、沒有除錯過程的設定值變更）。判斷門檻：*這項任務有沒有牽涉到除錯、重做、rollback，或是不明顯的決策？* 有，就寫一則紀錄。沒有，就跳過。

## The Three Rules

### Rule 1: Failures > Achievements

失敗的養分比成功更濃。一個花了 2 小時才找到的 bug，教你的比 3 個一次就成功的功能還多。

**Bad：** 「Successfully implemented the login flow.」
**Good（web 開發）：** 「Login flow: session token wasn't persisting because the cookie `SameSite` defaulted to `Lax` in Chrome 128+. Pattern: always explicitly set `SameSite=None; Secure` when cross-origin. Signal to recognize: auth breaks after browser upgrade or when crossing origin boundaries.」
**Good（資料 pipeline）：** 「CSV import failed silently on empty rows because `pandas.read_csv(dropna=False)` keeps zero-width rows that `len()` counts as valid. Pattern: always `df.dropna(how='all', inplace=True)` before row-count validation.」

### Rule 2: The Bole Principle (伯乐原则)

寫新的紀錄之前，先問：*「這跟我已經記過的某件事，本質上是不是一樣的？」*

根本原因相同、症狀不同，就**合併**，不要重複。新的根本原因，才開新紀錄。

**怎麼檢查：** 寫之前，先用你的根本原因的關鍵字搜尋現有的紀錄。如果找到吻合的，就把你的新症狀當作額外的範例，加在既有那則紀錄底下，不要另外建一則重複的。

**範例：** 「建立檔案之後忘了更新輸出索引」和「完成任務之後忘了更新 skill 評分」，根本原因一樣（沒有自動的記錄觸發機制）。合併成一則關於「任務後的記錄缺口」的紀錄。

### Rule 3: Must Be Transferable

每則紀錄都必須能回答：*「下次我遇到類似的情況，會有什麼不同的做法？」*

如果你寫不出那句話，代表你還沒提煉出模式。

**怎麼從具體事件提煉出模式：**
1. 用一句話說明發生了什麼
2. 反覆問「為什麼？」，直到找到根本原因（通常要問 3 到 5 個為什麼）
3. 一般化：「這是哪一類的問題？」（不是「Chrome 128 的 bug」，而是「瀏覽器的預設值變更，破壞了既有的行為」）
4. 寫成：「下次我看到 [訊號]，我會 [動作]。」
5. 說出訊號：有什麼具體可觀察的現象，告訴你這個模式正在發作？

## Entry Template

**範圍：** 每個不同的根本原因寫一則紀錄。一般長度：4 到 8 句。如果寫超過 2 分鐘，你是在敘述事件。如果不到 30 秒，代表挖得不夠深。

```markdown
## [Title: the pattern, not the event]

### Context
- What was I trying to do?
- What went wrong / what worked surprisingly well?

### Root Cause / Core Insight
- The underlying mechanism, not just the symptom

### The Pattern (transferable)
- Next time [similar situation], I will [specific action].
- Signal to recognize: [what observable tells me this pattern is active?]

### Related
- [entry-name](../path/to/related-entry.md)
```

## Entry Types

四種類型都用上面的範本。類型決定哪幾個段落的份量最重：

| Type | When to Use | Emphasis | Example Title |
|------|------------|----------|---------------|
| **Failure** | 有東西壞了、需要除錯，或是需要重做 | Root Cause | "Config inheritance ≠ behavior inheritance across sessions" |
| **Methodology** | 從工作中浮現了一個可重複的流程 | Context / Pattern | "PPT → open-book exam study guide: three-layer structure" |
| **Pattern Discovery** | 對工具、系統或思考方式的可重複使用的洞見 | Pattern section | "PR description template: describe the gap, not the feature" |
| **Capability Change** | 可衡量的技能進步 | Context（前後對比） | "Git: from clone/push to independent PR with 12 commits" |

## Quality Checklist

定稿一則成長日誌之前：

- [ ] 標題說的是*模式*，不是事件嗎？
- [ ] 有沒有一句「Next time I will...」？
- [ ] 「Signal to recognize」夠具體，足以讓你下次觸發這個模式嗎？
- [ ] 寫之前有搜尋既有的紀錄，確認沒有重複嗎？（Bole Principle）
- [ ] 有把根本原因和症狀區分開來嗎？
- [ ] 相關的記憶有互相連結嗎？
- [ ] 這則紀錄是 4 到 8 句嗎？比較短 = 太淺；比較長 = 在敘述事件。

## Anti-Patterns

- 避免：「Fixed bug in payment module」（這是事件，不是模式）
- 避免：逐字複製 git commit message（commit 描述改了什麼；日誌提煉的是為什麼重要）
- 避免：每個 commit 都寫一則紀錄（只有在浮現出模式時才寫）
- 避免：跳過可轉移的那句話（沒有它就只是流水帳，這點沒得商量）
- 避免：把同一個模式用不同標題重複記錄（違反 Bole Principle，寫之前要先搜尋）

## Storage

紀錄存在你平常放筆記的地方。常見做法：
- 放在 `growth-log/` 目錄裡的 Markdown 檔（一天一個檔案：`YYYY-MM-DD.md`）
- Notion、Obsidian 或你的筆記 app 裡一個專用的區塊
- 命名慣例一致的純文字檔

挑一種慣例，然後堅持下去。可搜尋性比格式重要。

## If You Use Delivery Gate

`delivery-gate` 這個 Stop hook，會透過檔案系統的時間戳記，檢查學習檔案今天有沒有被修改。這個 skill 教的是*該寫什麼*，讓 delivery-gate 檢查的那個檔案真的有用的模式，不是空洞的時間戳記。

```
Task completes → delivery-gate checks: was the learning file touched today?
  → Stale (no file modified): block — "what did you learn?"
  → Fresh (file touched): pass — this skill ensures the content is useful
```

只有強制執行卻沒有方法論，會產生空洞的紀錄。只有方法論卻沒有強制執行，會讓記錄被遺忘。兩者各自都有用；合在一起才形成完整的迴圈。
