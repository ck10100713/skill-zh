---
name: brownfield-retrospective
description: 對既有專案的某一塊，事後補跑 ECC 工程流程。稽核現況、重建過去的決策、產出四軸落差登記表（思考、寫程式的做法、缺少的功能、技術選型），再透過 plan-TDD-review 管線往前執行修正。適用於專案做到一半才導入 ECC、接手別人留下的 codebase，或想知道漏了什麼、從第一天起哪些會做得不一樣。
metadata:
  origin: ECC
---

# Brownfield Retrospective

對一個沒用過 ECC 流程蓋起來的專案，事後補跑 ECC 的工程流程。挑 codebase 裡任何一塊，稽核現有的東西，重建它是怎麼變成這樣的，整理出四軸落差登記表，再透過標準的 ECC 管線把修正往前推進。

整個流程以切片優先：不用先把整個 repo 摸過一遍才有用，而且每個階段都能從磁碟上的持久產出物重新進入。從中間開始，往回推，再往前走。

## When to Activate

- 在一個已經存在、已經成形的 repository 裡導入 ECC
- 使用者說「audit my existing project」、「retro this codebase」或「what did we miss?」
- 接手、繼承，或隔了很久之後回到某個 codebase
- 使用者先問「為什麼會變這樣？」，接著問「該繼續維持這樣嗎？」
- 某個模組、功能或服務，在下一個功能蓋上去之前需要重新思考
- 決定某個舊的區塊該往前修、重寫，還是只留文件記錄、維持原樣

## When Not to Use

- 沒有既有程式碼的全新專案，直接用 `planner` 和 `tdd-workflow`
- 只想導入 spec-driven development、不需要重新設計的循環，`spec-miner` agent 自己就能做
- 上線前的 go/no-go 正式環境就緒度檢查，用 `production-audit`
- 只看安全性的掃描，用 `security-review`
- 團隊流程的回顧（sprint 儀式），這個 skill 稽核的是 codebase，不是人

## The Working Set

所有產出物都寫在被稽核的專案裡面，放在 `docs/retro/<slice>/` 底下：

| File | Phase | Purpose |
|------|-------|---------|
| `gap-register.md` | 0-6 | 狀態機，包含範圍邊界、`Current phase:` 標記和各列資料。這是中途接手時唯一必要的檔案。 |
| `baseline-audit.md` | 1 | Reviewer 的發現、test/CI 快照、TODO 清單。 |
| `reconstructed-spec.md` | 2 | 程式碼現在實際上做了什麼（Requirements + Invariants）。 |
| `target-design.md` | 4 | 這一塊的目標樣貌，以及修正的順序。 |

補寫的決策依 `architecture-decision-records` skill 放到 `docs/adr/`。如果專案用 OpenSpec，`reconstructed-spec.md` 也可以改成 `spec-miner` 產出的 `openspec/specs/<capability>/spec.md`。

## How It Works

### Phase 0 — Pick the Entry Point

從使用者現在在意的東西開始。不要先把整個 repo 畫成地圖。

下面任何一種都是合法的切片：

| User signal | Slice |
|-------------|-------|
| 指名某個目錄、模組或服務 | 那個路徑加上它的直接呼叫者 |
| 指名某個功能或使用者流程 | 實作它的檔案，從進入點往下追 |
| 指名某個 bug、事故或痛點 | 產生它的程式碼，再加一層呼叫鏈 |
| 指名某個依賴或技術選擇 | 所有碰到它的東西 |
| 什麼都沒指名 | 依 churn 排出最熱的 2-3 條路徑，提出來讓使用者選 |

任何事情之前，先把範圍邊界記在 `gap-register.md` 最上面：納入範圍的路徑、進入點、呼叫者、影響範圍。切片大小抓大約 15 個檔案或 2,000 行；如果使用者挑的比這大，就切成有名字的子切片，各自登記成一列工作。一個太大、一個 session 稽核不完的切片，就是永遠做不完的切片。在範圍邊界旁邊放一個 `Current phase:` 標記，每完成一個階段就往前推。

### Phase 1 — Present-State Audit

用證據確認現在有什麼。這時候還不要修任何東西。

1. 偵察這個切片：manifest 和 framework 指紋、進入點、測試的擺放方式、CI 檢查（沿用 `codebase-onboarding` 的偵察步驟，範圍限縮在邊界內）。
2. 跑跟技術堆疊相符的 reviewer，盡量平行跑。每一個發現都必須附上 `file:line` 位置：
   - 該技術堆疊的語言 reviewer（`typescript-reviewer`、`python-reviewer`、`go-reviewer`……）
   - `security-reviewer`
   - `silent-failure-hunter`，找被吞掉的錯誤
   - `type-design-analyzer`，針對不變量用型別編碼的地方
   - `performance-optimizer`，只有這個切片在熱路徑上才用
3. 為目前的狀態拍快照：測試數量和覆蓋率、lint/CI 狀態、範圍內的 `TODO`/`FIXME`/`HACK` 清單。

全部寫進 `baseline-audit.md`。在這個階段就修掉的發現會污染基準線，先留給登記表處理。

### Phase 2 — Backward Reconstruction

從現況往回推，找出造成這個現況的決策。

1. 挖出行為規格：對這個切片跑 `spec-miner`。它產出的 Requirements（WHEN → THEN）和 Invariants 會成為 `reconstructed-spec.md`，也就是 Phase 5 測試的基準真相。
2. 對範圍邊界做 git 考古：
   - 用 `git log --oneline -- <slice>` 看目錄歷史；`--follow` 只能搭配單一檔案路徑使用，看年齡、作者、節奏
   - 最大和最常被 revert 的 commit，也就是設計在壓力下被改掉的地方
   - Churn 熱點，也就是被改的頻率遠高於鄰近檔案的檔案
   - 死路，也就是從沒上線的 branch 或鷹架
3. 決策清單：列出被凍結在程式碼裡的重大決策（技術堆疊與 framework 選擇、資料模型、邊界、錯誤策略、狀態管理）。逐一對照 `docs/adr/`、README 和註解。沒有任何書面紀錄的決策，本身就是既有的思考落差，記到 Phase 3，不要在這裡悄悄補寫。
4. 行為不透明的地方，先用 `code-explorer` 追蹤執行路徑，不要猜意圖。

### Phase 3 — Gap Analysis (Four Axes)

把稽核和重建的結果轉成登記表的列。每一類落差用一個軸：

| Axis | Question | Sources |
|------|-----------|---------|
| Thinking | 有哪些決定做了卻沒記錄？哪些不變量只存在於程式碼裡？ | 決策清單、重建出來的規格 |
| Coding practice | 程式碼哪裡跟 ECC 會怎麼寫不一樣？ | Phase 1 的發現、該語言的 `rules/` 規則包、沒有測試對應的規格項目 |
| Missing features | 第一天就從頭蓋的話，會有哪些東西是這個切片從來沒有的？ | 邊界輸入驗證、可觀測性、rate limiting、冪等性、migration 加 rollback、a11y、i18n、使用者文件、CI 關卡 |
| Technology selection | 選的技術是不是在跟 codebase 作對？過時、重複、有風險或缺漏？ | 依賴清單、git 考古、偵察結果 |

登記表格式（這張表是這個 skill 的持久產出）：

```markdown
| ID | Axis | Gap | Evidence | Forward fix | Severity | Effort | Status |
|----|------|-----|----------|-------------|----------|--------|--------|
| G-001 | practice | Errors swallowed in retry loop | src/api/retry.ts:42 | Propagate + map at boundary | P1 | S | open |
```

- Severity：`P0` 安全外洩或資料遺失，`P1` 正確性，`P2` 做法與可觀測性，`P3` 選型與清理。
- Effort：`S` 不到一個 session，`M` 幾個 session，`L` 需要自己的計畫。
- Status：`open`、`in-progress`、`done`、`wont-fix`。
- 每一列都需要證據位置。指不出來的落差只是意見。

### Phase 4 — Redesign / Rethink

把登記表轉成有順序的計畫。遵循專案既有的任務與核准權責。登記表當作稽核證據，連結到那個系統，不要另外建立互相競爭的正式任務狀態。要重寫、換技術、做 migration 或其他重大變更之前，先確認範圍並取得專案要求的核准。

1. 對 `P0` 和 `P1` 的列跑 `architect` 或 `code-architect`，產出 `target-design.md`：這個切片的目標樣貌、修正順序，以及一份明確的「哪些不改」清單，用來保護現有能正常運作的行為。
2. 為 Phase 2 找到的每個沒有文件的決策補寫 retro-ADR。標記成重建的（`status: proposed (reconstructed)`，日期填 retro 當天，並註明原始決策早於這份記錄）。把觀察到的歷史和推論出來的意圖分開，並且在標成 accepted 之前，要請專案負責人確認這個決策。補寫的 ADR 絕對不准假裝成決策當下寫的。
3. 把登記表每一列分到其中一類：`fix-forward`（就地修復）、`rewrite`（替換整個切片）、`leave-documented`（wont-fix）。`wont-fix` 一定要在登記表裡記下原因，有原因的 wont-fix 會把思考落差補起來，沒講的 wont-fix 會讓落差重新打開。
4. 排 backlog 的順序：先做 `P0`，然後把容易的小勝利和較大的修復穿插，維持動能。

### Phase 5 — Forward Execution

把登記表透過標準 ECC 管線處理，基準節奏是一個 session 做一列：

```text
planner (scope the row)
  → tdd-guide (failing test first — for a legacy gap the first test
    usually encodes the missing invariant from reconstructed-spec.md)
  → implement
  → code-reviewer
  → security-reviewer (if the row touches input, auth, or data)
  → doc-updater + ADR (if the decision changed)
  → conventional commit
  → mark the register row done
```

- 列結案時，同步更新 `gap-register.md` 的狀態；持久的狀態是登記表，不是對話。
- 跨 session 時，透過專案的記憶機制（`unified-memory`、context carriers）交接，讓下一個 session 只靠登記表就能接著做。

### Phase 6 — Closure and Re-Audit

當每一列都是 `done` 或 `wont-fix` 時：

1. 對同一個範圍邊界重跑 Phase 1 的稽核。
2. 跟 `baseline-audit.md` 做 diff，並用 `verification-loop` 驗證，宣稱已關閉的落差必須維持關閉。
3. 把差異（當時的發現、現在的發現、已結案的列、延後的列）記在 `gap-register.md` 底部。
4. 重新冒出來的東西變成新的一列，不算失敗，登記表是個循環，不是做一次就結束。

## Resuming Mid-Stream

任何 session 都可以從中間開始。先讀 `docs/retro/<slice>/gap-register.md`：

- 登記表存在，且有一列是 `in-progress` → Phase 5，把那一列做完。
- 登記表存在，至少有一列，且所有列都已結案 → Phase 6。
- 登記表存在，有 open 的列，但沒有進行中的 → 從 `Current phase:` 標記繼續（Phase 3 登記表等著分類，或是 Phase 4 backlog 等著開第一列）。
- 沒有登記表，但有 `baseline-audit.md` → Phase 2。
- 完全沒有產出物 → 跟使用者一起從 Phase 0 開始。

## Anti-Patterns

- 在挑切片之前就稽核整個 repo，這個流程設計上就是切片優先。
- 在 Phase 1-3 期間修改程式碼，稽核階段的產出是登記表，稽核中途動手改會污染基準線。
- 登記表的列沒有證據位置。
- `wont-fix` 沒有記錄原因。
- 把補寫的 ADR 當成當時留下的紀錄。
- 跳過 Phase 6 的重新稽核，結案要靠驗證，不是靠宣布。

## Related Skills

- `codebase-onboarding`：Phase 1 的偵察基準
- `architecture-decision-records`：Phase 4 的 retro-ADR 補寫
- `tdd-workflow`：Phase 5 的執行紀律
- `verification-loop`：Phase 6 的結案
- `production-audit`：上線就緒度的角度（互補，較後面才用）
- `security-review`：只針對安全性的需求
