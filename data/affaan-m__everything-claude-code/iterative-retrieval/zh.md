---
name: iterative-retrieval
description: 逐步精煉 context 檢索的模式，用來解決 sub-agent 的 context 問題。當 sub-agent 缺少所需的 context，必須分好幾輪精煉檢索時使用。
metadata:
  origin: ECC
---

# Iterative Retrieval Pattern

解決多 agent 工作流程裡的「context 問題」：sub-agent 要等到開始工作，才知道自己需要什麼 context。

## When to Activate

- 啟動 sub-agent，而它需要的程式碼庫 context 無法事先預測
- 建構 context 會逐步精煉的多 agent 工作流程
- 在 agent 任務中遇到「context 太大」或「缺少 context」的失敗
- 設計用於程式碼探索、類似 RAG 的檢索 pipeline
- 最佳化 agent 編排中的 token 用量

## The Problem

Sub-agent 是帶著有限的 context 被啟動的。它們不知道：
- 哪些檔案裡有相關的程式碼
- 程式碼庫裡有哪些慣用模式
- 專案用的是什麼術語

標準做法都會失敗：
- **全部都送**：超過 context 上限
- **什麼都不送**：agent 缺少關鍵資訊
- **猜需要什麼**：常常猜錯

## The Solution: Iterative Retrieval

一個 4 階段的迴圈，逐步精煉 context：

```
┌─────────────────────────────────────────────┐
│                                             │
│   ┌──────────┐      ┌──────────┐            │
│   │ DISPATCH │─────│ EVALUATE │            │
│   └──────────┘      └──────────┘            │
│        ▲                  │                 │
│        │                  ▼                 │
│   ┌──────────┐      ┌──────────┐            │
│   │   LOOP   │─────│  REFINE  │            │
│   └──────────┘      └──────────┘            │
│                                             │
│        Max 3 cycles, then proceed           │
└─────────────────────────────────────────────┘
```

### Phase 1: DISPATCH

先做一次範圍廣的初始查詢，收集候選檔案：

```javascript
// 從高層次的意圖開始
const initialQuery = {
  patterns: ['src/**/*.ts', 'lib/**/*.ts'],
  keywords: ['authentication', 'user', 'session'],
  excludes: ['*.test.ts', '*.spec.ts']
};

// 派給檢索 agent
const candidates = await retrieveFiles(initialQuery);
```

### Phase 2: EVALUATE

評估檢索到的內容是否相關：

```javascript
function evaluateRelevance(files, task) {
  return files.map(file => ({
    path: file.path,
    relevance: scoreRelevance(file.content, task),
    reason: explainRelevance(file.content, task),
    missingContext: identifyGaps(file.content, task)
  }));
}
```

評分標準：
- **High (0.8-1.0)**：直接實作目標功能
- **Medium (0.5-0.7)**：包含相關的樣式或型別
- **Low (0.2-0.4)**：只有間接相關
- **None (0-0.2)**：不相關，排除

### Phase 3: REFINE

根據評估結果更新搜尋條件：

```javascript
function refineQuery(evaluation, previousQuery) {
  return {
    // 加入在高相關檔案裡發現的新樣式
    patterns: [...previousQuery.patterns, ...extractPatterns(evaluation)],

    // 加入在程式碼庫裡發現的術語
    keywords: [...previousQuery.keywords, ...extractKeywords(evaluation)],

    // 排除已確認不相關的路徑
    excludes: [...previousQuery.excludes, ...evaluation
      .filter(e => e.relevance < 0.2)
      .map(e => e.path)
    ],

    // 針對特定缺口
    focusAreas: evaluation
      .flatMap(e => e.missingContext)
      .filter(unique)
  };
}
```

### Phase 4: LOOP

用精煉後的條件重複（最多 3 輪）：

```javascript
async function iterativeRetrieve(task, maxCycles = 3) {
  let query = createInitialQuery(task);
  let bestContext = [];

  for (let cycle = 0; cycle < maxCycles; cycle++) {
    const candidates = await retrieveFiles(query);
    const evaluation = evaluateRelevance(candidates, task);

    // 檢查 context 是否足夠
    const highRelevance = evaluation.filter(e => e.relevance >= 0.7);
    if (highRelevance.length >= 3 && !hasCriticalGaps(evaluation)) {
      return highRelevance;
    }

    // 精煉後繼續
    query = refineQuery(evaluation, query);
    bestContext = mergeContext(bestContext, highRelevance);
  }

  return bestContext;
}
```

## Practical Examples

### Example 1: Bug Fix Context

```
Task: "Fix the authentication token expiry bug"

Cycle 1:
  DISPATCH: Search for "token", "auth", "expiry" in src/**
  EVALUATE: Found auth.ts (0.9), tokens.ts (0.8), user.ts (0.3)
  REFINE: Add "refresh", "jwt" keywords; exclude user.ts

Cycle 2:
  DISPATCH: Search refined terms
  EVALUATE: Found session-manager.ts (0.95), jwt-utils.ts (0.85)
  REFINE: Sufficient context (2 high-relevance files)

Result: auth.ts, tokens.ts, session-manager.ts, jwt-utils.ts
```

### Example 2: Feature Implementation

```
Task: "Add rate limiting to API endpoints"

Cycle 1:
  DISPATCH: Search "rate", "limit", "api" in routes/**
  EVALUATE: No matches - codebase uses "throttle" terminology
  REFINE: Add "throttle", "middleware" keywords

Cycle 2:
  DISPATCH: Search refined terms
  EVALUATE: Found throttle.ts (0.9), middleware/index.ts (0.7)
  REFINE: Need router patterns

Cycle 3:
  DISPATCH: Search "router", "express" patterns
  EVALUATE: Found router-setup.ts (0.8)
  REFINE: Sufficient context

Result: throttle.ts, middleware/index.ts, router-setup.ts
```

## Integration with Agents

在 agent 的 prompt 裡使用：

```markdown
When retrieving context for this task:
1. Start with broad keyword search
2. Evaluate each file's relevance (0-1 scale)
3. Identify what context is still missing
4. Refine search criteria and repeat (max 3 cycles)
5. Return files with relevance >= 0.7
```

## Best Practices

1. **先廣後窄，逐步收斂** - 初始查詢不要訂得太死
2. **學會程式碼庫的術語** - 第一輪常常會揭露命名慣例
3. **追蹤缺了什麼** - 明確找出缺口，才能驅動精煉
4. **見好就收** - 3 個高相關檔案勝過 10 個普通的
5. **有把握地排除** - 低相關的檔案不會突然變得相關

## Related

- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - Subagent orchestration 章節
- `continuous-learning` skill - 用於隨時間逐漸改善的模式
- 隨 ECC 打包的 agent 定義（手動安裝路徑：`agents/`）
