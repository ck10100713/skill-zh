---
layout: default
skill: verification-before-completion
author: Jesse Vincent
category: 測試與驗證
summary: 沒跑過驗證指令，不准說完成
source: https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md
license: MIT
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

~~~~~markdown
---
name: verification-before-completion
description: 當你準備宣稱工作已完成、已修好或已通過時使用，在 commit 或開 PR 之前也要用。要求先跑驗證指令、確認輸出，才能做任何成功的宣稱；永遠是證據先於斷言。
---

# 完成前先驗證

## 概觀

**核心原則：** 永遠證據先於宣稱。

**違反這條規則的字面，就是違反這條規則的精神。**

## 鐵律

```
沒有新鮮的驗證證據，就不准宣稱完成
```

如果你沒有在這則訊息裡跑過驗證指令，你就不能宣稱它通過。

## 關卡函式

```
在宣稱任何狀態或表達滿意之前：

1. 找出：哪個指令能證明這個宣稱？
2. 執行：跑「完整」的指令（新鮮、完整）
3. 閱讀：完整輸出，檢查 exit code，數失敗數
4. 驗證：輸出有證實這個宣稱嗎？
   - 如果沒有：附上證據，說出實際狀態
   - 如果有：附上證據，說出宣稱
5. 到這時才可以：做出宣稱

跳過任何一步 = 說謊，不是驗證
```

## 常見失誤

| 宣稱 | 需要 | 不夠格 |
|-------|----------|----------------|
| 測試通過 | 測試指令輸出：0 失敗 | 上一次的結果、「應該會過」 |
| Linter 乾淨 | Linter 輸出：0 錯誤 | 部分檢查、自行推論 |
| Build 成功 | Build 指令：exit 0 | Linter 過了、log 看起來沒問題 |
| Bug 修好了 | 重測原本的症狀：通過 | 程式改了、假設已修好 |
| 回歸測試有效 | 驗證過紅綠循環 | 測試過了一次 |
| Agent 完成了 | VCS diff 顯示有改動 | Agent 回報「成功」 |
| 需求達成 | 逐行比對的檢查清單 | 測試通過 |

## 危險訊號：停下來

- 用了「應該」「大概」「看起來」
- 驗證之前就表達滿意（「太好了！」「完美！」「完成！」之類）
- 沒驗證就要 commit/push/開 PR
- 相信 agent 的成功回報
- 依賴部分驗證
- 心想「就這一次」
- 累了，想趕快收工
- **任何在沒跑驗證的情況下暗示成功的措辭**

## 防止自我合理化

| 藉口 | 現實 |
|--------|---------|
| 「現在應該可以了」 | 去「跑」驗證 |
| 「我很有把握」 | 有把握 ≠ 有證據 |
| 「就這一次」 | 沒有例外 |
| 「Linter 過了」 | Linter ≠ 編譯器 |
| 「Agent 說成功了」 | 自己獨立驗證 |
| 「我累了」 | 疲累 ≠ 藉口 |
| 「部分檢查就夠了」 | 部分什麼都證明不了 |
| 「換個說法，規則就不適用了」 | 精神重於字面 |

## 關鍵模式

**測試：**
```
✅ [跑測試指令] [看到：34/34 pass] 「全部測試通過」
❌ 「現在應該會過」/「看起來是對的」
```

**回歸測試（TDD 紅綠）：**
```
✅ 寫好 → 跑（通過）→ 把修正還原 → 跑（「必須」失敗）→ 還原回來 → 跑（通過）
❌ 「我已經寫好回歸測試了」（沒做紅綠驗證）
```

**Build：**
```
✅ [跑 build] [看到：exit 0] 「Build 通過」
❌ 「Linter 過了」（linter 不會檢查編譯）
```

**需求：**
```
✅ 重讀計畫 → 建檢查清單 → 逐項驗證 → 回報缺口或完成
❌ 「測試過了，這階段完成」
```

**委派給 agent：**
```
✅ Agent 回報成功 → 檢查 VCS diff → 驗證改動 → 回報實際狀態
❌ 直接相信 agent 的回報
```

## 何時適用

**以下情況之前「一律」適用：**
- 「任何」形式的成功／完成宣稱
- 「任何」表達滿意的話
- 「任何」對工作狀態的正面陳述
- Commit、開 PR、完成任務
- 進到下一個任務
- 委派給 agent

**規則涵蓋：**
- 一字不差的說法
- 換句話說和同義詞
- 暗示成功的語氣
- 「任何」暗示完成或正確的溝通
~~~~~

</section>
<section markdown="1">

## 英文原文

~~~~~markdown
---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness
~~~~~

</section>
</div>
