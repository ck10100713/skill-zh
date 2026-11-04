---
name: session-guard
description: >-
  在處理複雜的多步驟任務、session 越來越長（40+ 次工具呼叫）、agent 開始無視先前遵守過的規則、慣例開始跑掉、輸出品質似乎下降，或發生任何 context compaction 事件之後使用。透過行為上的自我約束，預防長 session 的悄悄損壞，以及 context compaction 造成的失憶。
---

# Session Guard

## Overview

長 session 會悄悄壞掉。Context compaction 會不聲不響地丟掉指令。Hook 解決不了這件事（多位開發者在 GitHub issue #19471、#9796、#64171 都確認過）。這個 skill 用行為上的自我約束來預防這兩種問題：監控健康度、在 compaction 之後固定住關鍵規則、在損壞發生前就先拆分。沒有套件、沒有資料庫，純粹靠行為約束，在每個 harness 都能用。

## When to Use

- Session 超過 40 次工具呼叫
- Agent 跟先前的決定自相矛盾
- 風格/命名慣例開始跑掉
- 發生任何 context compaction 事件之後
- 任務範圍無限膨脹

## Health Signals

| Signal | Threshold | Action |
|--------|-----------|--------|
| Tool call count | >40 | YELLOW: checkpoint + recite critical rules |
| Tool call count | >60 | RED: split or compact with anchor |
| Agent contradicts earlier decision | Any | VERIFY: re-read source of truth |
| Style/naming drift | Any | RECITE: state the active rules aloud |
| File read returns unexpected content | Any | RE-READ: don't trust cached state |
| Task scope growing unbounded | Continuous | SPLIT: one task per session |

## Protocol

### Green Zone (0-40 tool calls)
正常運作。不需要介入。

### Yellow Zone (40-60 tool calls)
1. CHECKPOINT - 用一段話摘要目前進度
2. RECITE - 把最關鍵的 3-5 條現行規則大聲說出來：「Active rules: [naming convention], [file structure], [error handling pattern], [testing requirement]」
3. ASSESS - 快做完了嗎？那就衝過去。還沒做完？準備拆分。
4. REDUCE - 不要做探索性的讀取。只做有針對性的操作。

### Red Zone (60+ tool calls OR drift signal)
1. STOP - 不要再做任何工具呼叫
2. VERIFY - 重新讀專案規則（不要相信記憶）
3. CHECKPOINT - 把狀態寫進 handoff 文件
4. SPLIT - 建立 handoff，建議開一個全新的 session

## Context Anchoring (anti-compaction)

發生 compaction 的時候（先前的 context 突然消失，或是在 /compact 之後）：

1. 立刻重新讀專案的規則檔
2. 在你的回應裡大聲 RECITE 那 3-5 條關鍵規則
3. 在執行之前，VERIFY 你計畫的下一步動作符合那些規則
4. 如果對任何先前的決定有疑慮，就重新讀來源檔案，不要用猜的

### What survives compaction:
- 最近的使用者訊息（高優先順序）
- 目前正在使用的 skill 本文（上限 5K token，最舊的先被丟掉）
- Git 狀態和專案結構
- compaction「之後」才讀進來的檔案內容

### What gets LOST in compaction:
- 對話早期做的決定
- 只用口頭說過、沒寫進檔案的架構規則
- 工具輸出的 context（檔案讀取、指令輸出）

### Compaction-Safe Pattern
關鍵指示要放在檔案裡（CLAUDE.md、CONTEXT.md），不要放在對話裡。規則如果重要，就必須存在 agent 可以重新讀取的檔案裡，不能只是先前口頭講好的東西。

## Common Mistakes

- 相信自己在 50 次以上的工具呼叫後還記得規則（你不記得，要重新讀）
- 為了保險而重新讀「所有東西」（浪費工具呼叫，要有針對性）
- 因為感覺沒問題，就假設 context 沒問題（compaction 是無聲的）
- 發現問題「之後」才拆分（要在「之前」拆，重點是預防，不是補救）

## Why This Matters

Context compaction 是 2026 年平台上排名第一、還沒解決的問題。Hook 解決不了（已確認：agent 會無視 compaction 之後注入的內容，因為 compaction 摘要會產生敘事上的慣性）。這個 skill 是輕量的行為對策：沒有基礎設施、沒有套件，只有紀律嚴明的自我監控，在每個 harness 都能用。
