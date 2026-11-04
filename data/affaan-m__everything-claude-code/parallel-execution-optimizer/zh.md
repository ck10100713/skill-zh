---
name: parallel-execution-optimizer
description: 把任務拆成由平行 lane 組成的相依圖，加速完成：用 lane 矩陣規劃、批次執行讀取和檢查、依檔案/worktree/branch/服務隔離寫入範圍，最後用驗證表收尾。適用於使用者想靠平行作業、並行 agent、批次 tool call、獨立 worktree、多條獨立驗證 lane，或有範圍限制的同質工作（共用準備工作、逐筆紀錄操作仍須循序）把任務大幅加快，同時不犧牲正確性。
license: MIT
metadata:
  origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Parallel Execution Optimizer

當速度來自「同時做彼此獨立的事」時就用這個 skill：repo 檢視、檔案讀取、API 檢查、瀏覽器檢查、build/test lane、deploy 後的回讀確認，或多 worktree 的實作。如果同質的工作在各筆紀錄之間會重複做同樣沒變的準備，即使每筆紀錄的操作必須循序進行，也可以用它。

## 核心模式

動手之前，先把急迫感變成一張相依圖。

1. 定義目標和完成訊號。
2. 把工作切成 lane。
3. 把每條 lane 標成 parallel、sequential 或 gated。
4. 把獨立的讀取/檢查一起跑。
5. 寫入要依檔案、worktree、branch、服務或資料集隔離。
6. 只有在證據顯示各 lane 相容之後才 merge。
7. 用驗證表收尾，不要只丟一句含糊的「變快了」。

## Lane 矩陣

大規模推進之前，先寫一張精簡的矩陣：

```text
Lane | Can run in parallel? | Write surface | Risk | Verification
Repo scan | yes | none | low | rg/git status outputs
Backend patch | maybe | src/api | medium | unit tests
Frontend patch | maybe | app/components | medium | browser screenshot
Deploy readback | after build | remote service | high | live URL + logs
```

只有在各 lane 的寫入範圍不會互相衝突時，才讓它們平行跑。

## 執行規則

- 把檔案讀取、搜尋、狀態檢查和 metadata 查詢批次處理。
- 大型、彼此無關的實作 lane 要用獨立的 worktree。
- 長時間執行的測試、build、backfill 和 deploy，要在獨立的 session 啟動，之後再有意識地去輪詢。
- 如果某條 lane 發現了會改變計畫的阻礙，就暫停相依的 lane 並更新矩陣。
- 背景程序絕對不可以活過這一輪，除非使用者明確要求要有持續運作的服務。
- 沒有明確的 gate，不要平行執行破壞性指令、migration、對同一張表的寫入，或會影響線上客戶的 deploy。

## 有範圍限制的同質工作

當一個有限的紀錄群組共用已被接受的不變輸入（例如一份對應表和 tool 契約）時，就重複使用準備工作。這樣可以減少重複的探索和任務設定；它並不要求並行寫入。

1. 定義有範圍的紀錄集合、由 owner 定義的完成單位、順序、排除項目、完成訊號、已被接受的對應表/契約版本，以及重新規劃的條件。要依照已接受的來源條件檢查選取範圍是否完整涵蓋；只驗證被選到的紀錄，不能證明這個集合是完整的。
2. 探索共用的來源，並且只準備一次不變的輸入。記錄它們的版本和有效條件；只有在這些條件還成立時才重複使用。
3. 在對每筆紀錄產生影響之前，先檢查它目前的版本、權限、前置條件，以及確切要做的影響。共用的準備工作不等於共用的授權。要求使用針對已檢查版本的條件式寫入、能偵測中途變更的 transaction，或在檢查與寫入期間一直持有的鎖。遇到衝突就停；如果沒有這類保護可用，就不要寫。
4. 驗證該筆紀錄的實際結果。每次驗證成功後，把它的證據和剩餘工作集合一起往下帶。嘗試寫入不等於驗證成功；結果不確定時，要先釐清再重試。
5. 在實際的准入契約允許時，讓一個群組由同一個 executor 處理。如果准入要求分開的寫入種類或階段，就保留這些界線，並根據驗證後回傳的 key 和版本去準備下一個被允許的階段；不要為了速度擴大指派範圍或繞過核准。
6. 只要契約和前置條件仍然有效，就在同一個有範圍的任務內繼續。當出現真實的相依關係、契約變更或風險需要時，才另外建立任務或 review，不要每成功一次就來一次。

### Planner/Executor 範例

下面是一個合成的逐步示範，不是實測的執行時間基準，也不是實際跑過的 connector 測試。紀錄 A、B、C 彼此獨立，使用同一份已接受的對應表 M1 和 tool 契約 T1。寫入保持循序。

```text
Planner:
  group = [A, B, C]
  shared = accepted mapping M1 + tool contract T1 + source references
  verified = {}
  remaining = [A, B, C]

Executor for A:
  confirm shared inputs are still valid
  read A's current version; check permission and prerequisites
  determine exact effect; apply with the same conflict protection; verify outcome
  carry forward verified = {A: outcome evidence}, remaining = [B, C]

Executor for B, then C:
  reuse shared preparation and carried state
  repeat each record's version, permission, prerequisite, effect, outcome checks
  remove a record from remaining only after verifying its success

Replan:
  if T1 changes to T2, pause dependent work and review the changed contract
  if B's prerequisite fails, leave B unresolved and review that dependency
  preserve A's verified evidence; refresh only inputs invalidated by the change
```

往下帶的狀態應該包含：群組、共用輸入的版本和有效條件、每筆紀錄已驗證的結果、未解決/不確定的影響、剩餘的紀錄、已完成工作的排除項目，以及下一個必要的檢查。恢復執行時，要重新驗證可能已經改變的輸入；不要只因為換了新的 executor 接手，就把已完成的操作重做一遍。新的使用者請求或範圍變更，要當成新的契約。

### Connector 變更後恢復

舉一個合成的交接情境：A 已完成，並被排除在後續變更之外；B 失敗，且已確認沒有任何影響；C 從未嘗試；D 的結果不明確。把這些各操作的狀態和證據帶到新的 connector 路徑。A 持續排除。在考慮重試之前，先釐清 D；從仍然被授權的未解決工作重建可執行集合，B 和 C 要等它們的檢查通過才納入。驗證新的 tool 契約，並保留確切要做的影響。不要把原本的批次重新建成可執行狀態，也不要因為後來某次嘗試成功了，就抹掉先前的偏差。

### 評估標準

用這個示範檢查：一般的成功能夠依 A → B → C 推進，不會重複做沒變的來源探索或完整的任務準備。確認契約變更或前置條件失敗時，仍然會觸發相關的 review，每筆紀錄的檢查保持完整，未驗證的結果仍然維持未解決。在 connector 變更時，確認已完成的排除項目有保留下來，失敗/未嘗試的工作需要目前的授權，不明確的影響要先釐清。要把實際執行過的內容和這份提議的評估分開回報。不要從這個範例推斷延遲改善，也不要推斷 ECC/connector 的錯誤歸屬。

對一個已經就緒的群組，在現有的 journal 裡保留就緒、交接和第一個動作的時間。把必要的檢查和核准等待，跟 coordinator 的等待分開；client 端的呼叫重疊並不能證明後端有並行，也不能證明吞吐量改善。如果 GROUP_A 中某個相依步驟被拒絕，就先擱置它，同時讓獲得授權的獨立 GROUP_B 繼續進行。在 owner 的完成單位內維持時間順序，並保留所有被排除的紀錄/區間。要拿某種選取條件的拼寫變體和一筆被排除的紀錄，對照已接受的條件做測試；在任何未準備好的寫入之前，保留被遺漏的合格工作和溢出的部分。檢查版本衝突或沒有衝突保護時，不會產生寫入。這些仍然只是提議的合成檢查，不是在實際系統上執行的結果。

## 輸出格式

回報時用這個格式：

```text
Parallel execution result:
- Lanes run: 5
- Lanes completed: 4
- Blocked lane: deploy readback, waiting on DNS propagation
- Fast path found: batched repo scan + focused tests
- Verification: lint pass, unit pass, live smoke pass
```

## 失敗模式

- 更多並行造成互相衝突的編輯。
- 去 benchmark 工具，而不是任務本身。
- 還沒證明正確就把「快」當成完成。
- 忘了輪詢正在跑的 session。
- 用一句成功摘要把跳過的檢查藏起來。
