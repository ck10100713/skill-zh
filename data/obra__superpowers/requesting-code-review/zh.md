---
name: requesting-code-review
description: 完成任務、實作重大功能，或 merge 之前，用來確認工作符合需求時使用
---

# Requesting Code Review

派出 code reviewer subagent，在問題連鎖擴大之前抓出來。Reviewer 拿到的是精準準備好、用來評估的 context，絕對不是你 session 的歷史。

**核心原則：** 早點審查，常常審查。

## 何時要求審查

**一定要：**
- 在 subagent-driven development 裡每個任務完成之後
- 完成重大功能之後
- Merge 到 main 之前

**非必要但有價值：**
- 卡住的時候（換個新視角）
- 重構之前（做基準檢查）
- 修完複雜的 bug 之後

## 怎麼要求

**1. 取得 git SHA：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or: git merge-base origin/main HEAD
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 派出 code reviewer subagent：**

派出一個 `general-purpose` subagent，並填好 [code-reviewer.md](code-reviewer.md) 的範本

**佔位符：**
- `{DESCRIPTION}` - 你做了什麼的簡短摘要
- `{PLAN_OR_REQUIREMENTS}` - 它應該做什麼
- `{BASE_SHA}` - 起始 commit
- `{HEAD_SHA}` - 結束 commit

**3. 針對回饋採取行動：**
- Critical 問題立刻修
- Important 問題在繼續之前修
- Minor 問題記下來之後處理
- Reviewer 錯了就反駁（附上理由）

## 範例

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | cut -d' ' -f1)
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch code reviewer subagent]
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  PLAN_OR_REQUIREMENTS: Task 2 from docs/superpowers/plans/deployment-plan.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## 常見的合理化藉口

| 藉口 | 現實 |
|--------|---------|
| 「我自己看 diff 就好，不用派 reviewer」 | 你是協調者，直接在對話裡審 diff，會燒掉你持續推進工作所需要的 context window。派出 reviewer subagent：diff 和評估都留在它的 context 裡，只有發現會回到你這邊。 |
| 「Reviewer 需要我整個 session 的歷史才能理解這個變更」 | 給它精準準備好的 context，絕對不要給你 session 的歷史。這樣 reviewer 才會專注在工作成果，而不是你的思考過程。 |

## 警訊

**絕對不要：**
- 因為「這很簡單」就跳過審查
- 忽略 Critical 問題
- 帶著沒修好的 Important 問題繼續往下走
- 跟有道理的技術回饋爭辯

**如果 reviewer 錯了：**
- 用技術理由反駁
- 拿出證明它能運作的程式碼／測試
- 要求釐清

範本見：[code-reviewer.md](code-reviewer.md)
