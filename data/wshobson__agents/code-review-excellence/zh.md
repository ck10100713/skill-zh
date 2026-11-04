---
name: code-review-excellence
description: 掌握有效的 code review 實務，給出有建設性的回饋、及早抓到 bug、促進知識分享，同時維持團隊士氣。在審查 pull request、建立審查標準，或指導開發者時使用。
---

# Code Review 的卓越做法

透過有建設性的回饋、有系統的分析和協作式的改進，把 code review 從把關轉變成知識分享。

## 何時使用這個 Skill

- 審查 pull request 和程式碼變更
- 為團隊建立 code review 標準
- 透過 review 指導資淺的開發者
- 進行架構審查
- 建立審查檢查清單和指南
- 改善團隊協作
- 縮短 code review 的週期
- 維持程式碼品質標準

## 核心原則

### 1. 審查的心態

**Code Review 的目標：**

- 抓出 bug 和邊界情況
- 確保程式碼好維護
- 在團隊內分享知識
- 落實程式碼標準
- 改善設計和架構
- 建立團隊文化

**不是目標的：**

- 炫耀知識
- 吹毛求疵格式（用 linter）
- 不必要地擋住進度
- 照你的偏好重寫

### 2. 有效的回饋

**好的回饋是：**

- 具體而且可執行
- 有教育性，不帶批判
- 針對程式碼，不針對人
- 平衡（好的地方也要稱讚）
- 有優先順序（關鍵的 vs 有也不錯的）

```markdown
❌ Bad: "This is wrong."
✅ Good: "This could cause a race condition when multiple users
access simultaneously. Consider using a mutex here."

❌ Bad: "Why didn't you use X pattern?"
✅ Good: "Have you considered the Repository pattern? It would
make this easier to test. Here's an example: [link]"

❌ Bad: "Rename this variable."
✅ Good: "[nit] Consider `userCount` instead of `uc` for
clarity. Not blocking if you prefer to keep it."
```

### 3. 審查範圍

**要審查什麼：**

- 邏輯的正確性和邊界情況
- 安全漏洞
- 效能影響
- 測試覆蓋率和品質
- 錯誤處理
- 文件和註解
- API 設計和命名
- 架構是否適配

**不用手動審查的：**

- 程式碼格式（用 Prettier、Black 等）
- import 的整理
- lint 違規
- 單純的錯字

## 審查流程

### Phase 1：蒐集脈絡（2 到 3 分鐘）

```markdown
Before diving into code, understand:

1. Read PR description and linked issue
2. Check PR size (>400 lines? Ask to split)
3. Review CI/CD status (tests passing?)
4. Understand the business requirement
5. Note any relevant architectural decisions
```

### Phase 2：高階審查（5 到 10 分鐘）

```markdown
1. **Architecture & Design**
   - Does the solution fit the problem?
   - Are there simpler approaches?
   - Is it consistent with existing patterns?
   - Will it scale?

2. **File Organization**
   - Are new files in the right places?
   - Is code grouped logically?
   - Are there duplicate files?

3. **Testing Strategy**
   - Are there tests?
   - Do tests cover edge cases?
   - Are tests readable?
```

### Phase 3：逐行審查（10 到 20 分鐘）

```markdown
For each file:

1. **Logic & Correctness**
   - Edge cases handled?
   - Off-by-one errors?
   - Null/undefined checks?
   - Race conditions?

2. **Security**
   - Input validation?
   - SQL injection risks?
   - XSS vulnerabilities?
   - Sensitive data exposure?

3. **Performance**
   - N+1 queries?
   - Unnecessary loops?
   - Memory leaks?
   - Blocking operations?

4. **Maintainability**
   - Clear variable names?
   - Functions doing one thing?
   - Complex code commented?
   - Magic numbers extracted?
```

### Phase 4：摘要與決定（2 到 3 分鐘）

```markdown
1. Summarize key concerns
2. Highlight what you liked
3. Make clear decision:
   - ✅ Approve
   - 💬 Comment (minor suggestions)
   - 🔄 Request Changes (must address)
4. Offer to pair if complex
```

撰寫審查回饋之前，先讀 `references/review-techniques.md`，裡面有檢查清單、提問的措辭、協作和嚴重度的技巧。

做特定語言、架構、測試品質或安全的審查之前，先讀 `references/review-patterns.md`，裡面有審查模式和檢查清單。

## 給出困難的回饋

### 模式：三明治法（修改版）

```markdown
Traditional: Praise + Criticism + Praise (feels fake)

Better: Context + Specific Issue + Helpful Solution

Example:
"I noticed the payment processing logic is inline in the
controller. This makes it harder to test and reuse.

[Specific Issue]
The calculateTotal() function mixes tax calculation,
discount logic, and database queries, making it difficult
to unit test and reason about.

[Helpful Solution]
Could we extract this into a PaymentService class? That
would make it testable and reusable. I can pair with you
on this if helpful."
```

### 處理意見分歧

```markdown
When author disagrees with your feedback:

1. **Seek to Understand**
   "Help me understand your approach. What led you to
   choose this pattern?"

2. **Acknowledge Valid Points**
   "That's a good point about X. I hadn't considered that."

3. **Provide Data**
   "I'm concerned about performance. Can we add a benchmark
   to validate the approach?"

4. **Escalate if Needed**
   "Let's get [architect/senior dev] to weigh in on this."

5. **Know When to Let Go**
   If it's working and not a critical issue, approve it.
   Perfection is the enemy of progress.
```

## 最佳實務

1. **及時審查**：24 小時內，最好當天
2. **限制 PR 大小**：要有效審查，最多 200 到 400 行
3. **分時段審查**：最多 60 分鐘，要休息
4. **使用審查工具**：GitHub、GitLab 或專門的工具
5. **能自動化的就自動化**：linter、formatter、安全掃描
6. **建立默契**：emoji、稱讚和同理心都很重要
7. **隨時能找到你**：複雜的問題提議一起 pair
8. **向別人學習**：看別人寫的 review 留言

## 常見陷阱

- **完美主義**：因為小小的風格偏好就擋住 PR
- **範圍蔓延**：「While you're at it, can you also...」
- **不一致**：對不同的人用不同的標準
- **延遲審查**：讓 PR 放好幾天
- **消失**：要求修改之後就不見人影
- **橡皮圖章**：沒有真的審查就核准
- **Bike Shedding**：對瑣碎的細節爭論不休

## 範本

### PR 審查留言範本

```markdown
## Summary

[Brief overview of what was reviewed]

## Strengths

- [What was done well]
- [Good patterns or approaches]

## Required Changes

🔴 [Blocking issue 1]
🔴 [Blocking issue 2]

## Suggestions

💡 [Improvement 1]
💡 [Improvement 2]

## Questions

❓ [Clarification needed on X]
❓ [Alternative approach consideration]

## Verdict

✅ Approve after addressing required changes
```
