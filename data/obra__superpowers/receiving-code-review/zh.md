---
name: receiving-code-review
description: 收到 code review 回饋、實作建議之前使用，尤其是回饋看起來不清楚，或技術上有疑問的時候：要求的是技術上的嚴謹與驗證，不是做表面的附和，也不是盲目照做
---

# Code Review Reception

## 概述

Code review 需要的是技術評估，不是情緒表演。

**核心原則：** 先驗證再實作。先問再假設。技術正確性勝過社交上的舒服。

## 回應模式

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

## 禁止的回應

**絕對不要：**
- 「You're absolutely right!」（明確違反指示檔）
- 「Great point!」／「Excellent feedback!」（表面附和）
- 「Let me implement that now」（在驗證之前）

**改成：**
- 重述技術需求
- 問釐清用的問題
- 如果它是錯的，用技術理由反駁
- 直接開始做（行動 > 言語）

## 處理不清楚的回饋

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

**範例：**
```
your human partner: "Fix 1-6"
You understand 1,2,3,6. Unclear on 4,5.

❌ WRONG: Implement 1,2,3,6 now, ask about 4,5 later
✅ RIGHT: "I understand items 1,2,3,6. Need clarification on 4 and 5 before proceeding."
```

## 依來源不同的處理

### 來自你的搭檔
- **可信任**：理解之後就實作
- 範圍不清楚時**還是要問**
- **不要表面附和**
- **直接跳到行動**，或給技術性的確認

### 來自外部 Reviewer
```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF can't easily verify:
  Say so: "I can't verify this without [X]. Should I [investigate/ask/proceed]?"

IF conflicts with your human partner's prior decisions:
  Stop and discuss with your human partner first
```

**你的搭檔的規則：**「External feedback - be skeptical, but check carefully」

## 針對「專業」功能的 YAGNI 檢查

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage

  IF unused: "This endpoint isn't called. Remove it (YAGNI)?"
  IF used: Then implement properly
```

**你的搭檔的規則：**「You and reviewer both report to me. If we don't need this feature, don't add it.」

## 實作順序

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

## 何時要反駁

在以下情況要反駁：
- 建議會弄壞既有的功能
- Reviewer 沒有完整的 context
- 違反 YAGNI（沒人用的功能）
- 對這個技術棧來說技術上不正確
- 有舊版／相容性的理由
- 跟你的搭檔的架構決策衝突

**怎麼反駁：**
- 用技術理由，不要防衛心態
- 問具體的問題
- 引用能運作的測試／程式碼
- 如果牽涉架構，就把你的搭檔拉進來

**如果你不太好意思當面反駁：** 把這份緊張說出來，然後告訴你的搭檔你看到的問題。他們會欣賞你的誠實。

## 確認正確的回饋

當回饋是正確的：
```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ "Thanks for catching that!"
❌ "Thanks for [anything]"
❌ ANY gratitude expression
```

**為什麼不說謝謝：** 行動就是回答。直接修好。程式碼本身就顯示你聽到了回饋。

**如果你發現自己正要寫「Thanks」：** 刪掉它。改成陳述你做的修正。

## 優雅地更正你自己的反駁

如果你反駁了，而且你錯了：
```
✅ "You were right - I checked [X] and it does [Y]. Implementing now."
✅ "Verified this and you're correct. My initial understanding was wrong because [reason]. Fixing."

❌ Long apology
❌ Defending why you pushed back
❌ Over-explaining
```

用事實陳述更正，然後繼續往下做。

## 常見錯誤

| 錯誤 | 修正 |
|---------|-----|
| 表面附和 | 陳述需求，或直接行動 |
| 盲目實作 | 先對照程式碼庫驗證 |
| 一次做一批、不測試 | 一次一個，每個都測試 |
| 假設 reviewer 是對的 | 檢查它會不會弄壞東西 |
| 避免反駁 | 技術正確性 > 舒服 |
| 只實作一部分 | 先把所有項目都釐清 |
| 無法驗證，還是照做 | 說明限制，請求指示 |

## 真實範例

**表面附和（不好）：**
```
Reviewer: "Remove legacy code"
❌ "You're absolutely right! Let me remove that..."
```

**技術驗證（好）：**
```
Reviewer: "Remove legacy code"
✅ "Checking... build target is 10.15+, this API needs 13+. Need legacy for backward compat. Current impl has wrong bundle ID - fix it or drop pre-13 support?"
```

**YAGNI（好）：**
```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
✅ "Grepped codebase - nothing calls this endpoint. Remove it (YAGNI)? Or is there usage I'm missing?"
```

**不清楚的項目（好）：**
```
your human partner: "Fix items 1-6"
You understand 1,2,3,6. Unclear on 4,5.
✅ "Understand 1,2,3,6. Need clarification on 4 and 5 before implementing."
```

## GitHub 討論串回覆

在 GitHub 上回覆 inline 的 review 留言時，要回覆在那則留言的討論串裡（`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`），不要當成最上層的 PR 留言。
