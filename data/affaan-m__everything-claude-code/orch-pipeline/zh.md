---
name: orch-pipeline
description: orch-* skill 家族背後共用的統籌引擎，也就是有關卡的 Research-Plan-TDD-Review-Commit pipeline、大小分類器、agent 與指令對照表，以及兩個人工關卡（計畫核准、commit 確認），orch-* 的各個操作 skill 都委派給它。透過 orch-add-feature、orch-fix-defect、orch-change-feature、orch-refine-code 或 orch-build-mvp 間接使用；只有在新增 orch 操作或調整共用階段時才直接閱讀。
metadata:
  origin: ECC
---

# Orchestrator Pipeline (shared engine)

`orch-*` 的 skill 都是薄包裝。它們不會重新實作任何工作，而是
分類請求、選擇要跑*這條* pipeline 的哪些階段，並把
每個階段委派給既有的 ECC agent 或指令。這個檔案就是那條 pipeline。

> 請呼叫某個操作 skill（`orch-add-feature`、`orch-fix-defect`……），不要
> 直接呼叫這個引擎。這個檔案是它們所指向的參考資料。

## When to Use

- 每當某個 `orch-*` 操作 skill 執行時，會被間接載入。
- 只有在要為這個家族新增操作，或調整
  共用的階段、關卡或 agent 對照表時，才直接閱讀。

## The operation family

| Skill | 操作 | 觸發 | 第一步 |
|-------|-----------|---------|------------|
| `orch-add-feature` | feature | 能力還不存在 | 研究並規劃新的切片 |
| `orch-change-feature` | tweak | 能用，但期望的行為不同 | 修改既有行為*和它的測試* |
| `orch-fix-defect` | fix | 壞了；行為不對 | 重現成失敗的測試，再修 |
| `orch-refine-code` | refactor | 行為不變，結構改善 | 在保持測試為綠的同時重新整理結構 |
| `orch-build-mvp` | mvp | 從設計/規格文件起步 | 讀入文件 → 垂直切片 |

> 這些包裝是**組合**既有的 ECC 指令，不是取代它們：
> `/feature-dev`、`/plan`、`/code-review`、`/build-fix`、`/refactor-clean`，以及
> `/gan-build`，加上 `tdd-workflow` skill。orch-* 家族在它們之上
> 加了共用的大小分類器和兩個關卡，
> 讓一把傘一致地涵蓋五種操作。

## Step 0 — Classify size (right-sizing)

儀式的繁瑣程度要跟爆炸半徑成比例。依三個訊號替請求打分，取任何一個訊號
達到的**最高**級別，並用一行說出結果，讓使用者
可以推翻：

| 級別 | 動到的檔案 | 新相依 / 合約 | 設計的模糊程度 | 會跑的階段 |
|------|---------------|---------------------------|------------------|-----------------|
| trivial | 1 個，幾行 | 無 | 無，改動很明顯 | 4 → 5 → 6 |
| small | 1 個檔案 / 1 個函式 | 無 | 讀過程式碼就清楚 | (輕量 1) → 4 → 5 → 6 |
| standard | 2–5 個檔案 | 可能有新的內部模組 | 有一個真正要做的選擇 | 1 → 2 → 4 → 5 → 6 |
| large | 很多 / 橫切 | 新的外部相依、公開 API，或規格文件 | 有多個未決問題 | 1 → 2 → (3) → 4 → 5 → 6 |

階段 0（Intake）一定會跑，上表的遮罩欄沒有列出。決勝規則：
任何碰到安全觸發條件（見下）或公開 API /
合約的，不管檔案數量，**至少**是 standard。

## The phases

每個階段都是委派，不在行內自己做。

- **0. Intake**：重述請求。對 `orch-build-mvp`，要讀規格/設計
  文件，並擷取範圍、已鎖定的決定和功能清單。
- **1. Research & Reuse**：依 `rules/common/development-workflow.md`：先 `gh search repos` /
  `gh search code`，再來是 Context7 / 廠商文件，再來是套件 registry，最後是
  Exa。偏好採用經過驗證的實作，而不是寫全新的程式碼。
- **2. Plan**：委派給 `planner` agent（結構性的決策則用 `architect` /
  `code-architect`）。輸出一份排成薄垂直切片的 `task_list`。→ **GATE 1.**
- **3. Scaffold**：只有 `orch-build-mvp` 才有：立起第一個端到端的切片。
- **4. Implement (TDD)**：透過 `tdd-guide` agent（或 `tdd-workflow` skill）推動每個任務：
  紅 → 綠 → 重構。遵守該操作的第一步規則。
- **5. Review**：`code-reviewer` agent / `/code-review`。每當 diff 碰到安全觸發條件（見下），
  就加上 `security-reviewer`。
- **6. Commit**：conventional commit（`feat:` / `fix:` / `refactor:` / …），每個
  邏輯單位一個。→ **GATE 2.**

## The two gates

這個家族是**有關卡的，不是全自動的**：

1. **GATE 1：Plan 之後。** 呈現 `task_list`；使用者核准之前，
   不准寫實作程式碼。
2. **GATE 2：Commit 之前。** 呈現 diff 摘要和擬好的訊息；
   使用者確認之前，不准 commit。

兩個關卡之間的一切都不停地流過去。

## Agent / command map

| 階段 | 主要 | 備援 / 升級 |
|-------|---------|----------------------|
| Intake / understand | `code-explorer` | 在微調、修 bug 或重構之前，先追蹤既有的路徑 |
| Plan | `planner` | 結構性的決定用 `architect`、`code-architect` |
| Implement | `tdd-guide`（或 `tdd-workflow` skill） | 建置壞掉時用 `build-error-resolver` / `/build-fix` |
| Review | `code-reviewer` / `/code-review` | 語言專屬的 reviewer（`python-reviewer`、`typescript-reviewer`……） |
| Security | `security-reviewer` | — |
| MVP inner loop | `/gan-build "<brief>" --skip-planner` | 驅動 `gan-generator` → `gan-evaluator`；調整 `--max-iterations` / `--pass-threshold` |

語言 reviewer 要配合 repo（看 repo 自己的 `CLAUDE.md`）。

## Security-review trigger

當 diff 碰到下列任何一項時，要拉進 `security-reviewer`：驗證或
授權、使用者輸入處理、資料庫查詢、檔案系統路徑、
外部 API 呼叫、密碼學，或機密 / 憑證。（依 `rules/common/security.md`。）

## Handoff artifacts

pipeline 沒有隱藏的狀態，規劃文件*就是*交接：

- `task_list`（來自 Plan）驅動 Implement 迴圈。
- 比較大的工作，也可能依 `rules/common/development-workflow.md`，
  在 repo 的 `docs/` 底下產出 PRD / 架構 / system_design。
- 審查發現的 CRITICAL / HIGH 問題，在 Gate 2 之前必須解決。

## Verification

- 有說出大小級別，而且符合實際工作
- Gate 1（計畫）和 Gate 2（commit）都有遵守
- 當且僅當碰到安全觸發條件時，才有跑 `security-reviewer`
- commit 符合 conventional 格式，而且範圍限定在單一邏輯變更
- 新的 / 變更的行為有測試；依 `rules/common/testing.md`，覆蓋率 ≥ 80%
