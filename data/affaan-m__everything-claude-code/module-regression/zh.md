---
name: module-regression
description: >-
  在大型 repo 裡，用 REGRESSION.md 帳本管理跨模組的回歸，帳本記錄每個模組的下游使用者和可執行的驗收指令。變更之後，執行被改的模組和每個受影響的下游指令，並依專案的交付政策，把實際觀察到的 exit code 當作回歸證據。用於模組回歸、回歸帳本、影響稽核、下游驗證，以及「改 A 可能弄壞 B」的變更。
metadata:
  origin: ECC
---

# Module Regression Ledger

## When to Activate

- repo 至少有三個互相依賴的模組，或之前改 A 曾經弄壞 B。
- 某項變更會改動模組對外可觀察的行為，必須同時證明該模組和下游使用者仍然正常。
- 專案已經有可執行的測試或對帳指令，應該依相依關係整理起來。

## Anti-Patterns

- 對沒有跨模組相依的小型 repo 建立回歸帳本。
- 手動猜相依關係，或把一次掃描當成永遠正確。
- 用模型審查取代可執行驗收指令的 exit code。

## Related Skills

- `test-collaboration`：TEST-ID、測試資產和缺陷回歸的證據。
- `ai-regression-testing`：從重要缺陷衍生出來的可執行回歸測試。
- `contract-first`：跨服務或跨 client 的合約驗證。
- `change-impact`：實作前後的爆炸半徑分析。

## Problem

大型專案裡，模組互相依賴。人和 agent 常常只驗證被改的模組，下游使用者卻悄悄壞掉。缺陷幾天後才出現，在彙總、匯出或對外行為出錯的時候。

解法是一份**回歸帳本**（`REGRESSION.md`）加上確定性的稽核：任何相關變更之後，執行被改的模組和所有受影響的下游使用者。交付要求每個指令都通過。

## Three Required Fields per Module

```markdown
## Module 03 — Shop Data Cleaning
Downstream consumers: 05-aggregation, 07-final-export
Dependency evidence: `<repository dependency graph or reproducible scan command>`
Regression acceptance command: `pytest tests/test_03.py && python scripts/reconcile.py --module 03`
Propagation rule: external behavior change → run 05 and 07; internal-only change with a green module check → downstream may be exempted
```

1. **Downstream consumers**：從 repo 的相依圖、建置工具，或可重現的 import/呼叫掃描推導出來，並記錄所用的指令或工具。各生態系的擷取方式不同；這個 skill 不假裝有一個通用的掃描器能解析每種語言。無法用機械方式確立的邊，標成 `unverified`。受影響的 unverified 邊，會擋住「全綠」的結論，直到有人確認它的範圍，或把相關模組納入這次執行為止。
2. **Regression acceptance command**：帳本的核心資產。每個模組都需要一個可執行的指令來證明它仍然正常：測試、對帳腳本，或 golden sample 的 diff。沒有它，稽核就會退化成「模型看過了，沒發現問題」。
3. **Propagation rule**：寫明變更之後哪些下游模組必須跑，以及什麼情況下免跑是合理的。

## Connection to TESTS.md

`REGRESSION.md` 不維護商業規則或測試缺口。它參照 test-registry 成品裡穩定的 TEST-ID：

```markdown
Related test points: TEST-ORDER-001, TEST-REFUND-003
```

- 哪些規則必須被保護、它們的覆蓋狀態，以及證據放在哪裡，歸 `test-collaboration` 和 test registry 管。
- 變更後哪些模組和指令必須重跑，歸這個 skill 和回歸帳本管。
- 目前的 session 負責規劃帳本裡的指令。經使用者或既有任務範圍授權之後，由受信任的 host 執行並回傳 exit code。這個 skill 沒有加專屬的 agent 或 slash command。

## Ledger Discipline

- 驗收指令偏好用**對帳式**的，而不是只做斷言的檢查。golden sample、上游總數和會計關係這類外部事實，比 mock 或鬆散的斷言更難被不小心削弱。
- 只根據可重現的證據來更新下游清單。相依關係變了，就重跑記錄下來的 repo 工具或掃描；沒有證據，不要手動編輯邊。
- 把帳本放在 repo 根目錄或 `docs/` 底下，並從專案的指示/地圖成品連到它，免得變成孤兒。

## Audit Flow

透過 host 的 skill 入口呼叫 `module-regression`，例如在 Codex 裡用 `$module-regression`。目前的 session 負責規劃並回報稽核。repo 指令透過受信任的 host runner，在既有的使用者授權範圍內執行；只有在指令需要新的權限時才詢問。成功的 exit code 是回歸證據，絕不是 ECC 正式認定的完成或整合權限。

1. **列出變更**：先選定並記錄稽核基準（用 PR 的 merge-base 或最後一個驗證過全綠的 commit）。合併 `git diff --name-only <base> HEAD`、未 stage 的 `git diff --name-only`、已 stage 的 `git diff --cached --name-only`，以及包含未追蹤檔案的 `git status -s` 路徑，再把聯集對應到帳本裡的模組。光是工作區乾淨，不能證明沒有相關變更。
2. **解析傳播**：根據每個模組的下游清單和規則。
3. **執行前先審查。** 把帳本裡的指令當作不受信任的 repo 內容。把有界的指令清單、風險、預期的工作區、逾時、環境和網路需求，拿出來給人審查。確認既有的任務授權涵蓋每個指令，只有新的權限才需要請求核准。只透過受信任的 host 邊界執行；否則把指令標成 `NOT RUN`。
4. **執行回歸**：在那份授權範圍內，對被改的模組和每個必要的下游模組執行，記錄每個指令和 exit code。
5. **以 exit code 把關**。所有必要指令都綠，而且沒有受影響的 unverified 邊，這個變更才可以往下走。任何失敗或未解決的邊，都代表變更還沒完成；修好或確認之後，從步驟 3 重跑。
   - 用受控的證據歸因：如果基準是綠的、只有 A 改了、B 現在紅了，就檢查 B 失敗的對帳/斷言，並把交接欄位追回 A。如果 B 在變更之前就是紅的，就記成既有的債，不要怪 A。變更批次越小，歸因越準。把最後一個綠的 commit 記在帳本裡。
6. **回報稽核結果**：包含被改的模組、執行過的指令、關鍵輸出、exit code、豁免和理由。

## Four Invariants

1. **結論 = exit code。** 沒有可執行驗收指令的模組，是帳本缺口，不算通過。
2. **稽核者只回報，不修。** 由變更作者修失敗並要求重跑。
3. **紅燈不准交付。** 下游使用者失敗，代表目前的變更還沒做完。
4. **每個重要缺陷都要留下持久的證據。** 修 bug 必須建立或連結一個 TEST-ID，並指出它的回歸測試、lint 規則、schema 檢查，或明確的人工出口。只修程式碼不算完成。

## Boundary with Adjacent Methods

| 方法 | 負責 | 成品 | 驗證時間 |
|---|---|---|---|
| `contract-first` | 跨 client/服務的欄位合約 | `CONTRACT.md` 或既有的同等檔案 | 整合對帳 |
| `test-collaboration` | 測試資產、必要的測試點、bug 防護和證據 | `TESTS.md` 或既有的同等檔案 | 需求、bug、測試變更和交付 |
| `module-regression` | 同一個 codebase 內跨模組的行為回歸 | `REGRESSION.md` 或既有的同等檔案 | 每次相關變更之後 |

## Progressive Adoption

- 少於三個模組，或沒有跨模組參照，而且之前沒發生過跨模組的壞掉：不要建立帳本。
- 第一次發生「A 弄壞 B」的事件：當天就建立帳本。
- 如果測試和對帳腳本已經存在，導入主要就是依模組整理它們的指令，並驗證下游證據。
