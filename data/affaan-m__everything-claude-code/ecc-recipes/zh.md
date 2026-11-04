---
name: ecc-recipes
description: 把描述的工作流對應到正確的 ECC command 群組，附上執行順序與停止條件；或瀏覽從 commands 目錄即時讀出的所有 command 群組 recipe 家族。只提供建議，絕不執行。在被問到哪些 command 能跑某個工作流、某個任務的 command 順序，或要列出 ECC pipeline 時使用；不適用於執行任務（導向 command 本身）、單一 command 的文件（用 ecc-guide）或 prompt 改寫（用 prompt-optimizer）。
argument-hint: <workflow description | empty=list all>
origin: community
author: KyawZinLatt
metadata:
  version: "1.0.0"
---

# ECC Recipes

「我的工作流該用哪一組 ECC slash-command、照什麼順序、
什麼時候該停」的單一入口。也能瀏覽每個 command 群組的 recipe 家族。

補上兩個既有 skill 之間的缺口：

- `ecc-guide`：列出 command 與去哪讀文件，但只是平面的目錄。
- `prompt-optimizer`：把任務對應到元件，但輸出的是單一 prompt，
  不是帶有執行順序和停止條件的多 command 群組。

這個 skill 補上的是：**家族分組 + 執行順序 + 停止條件。**

## 何時啟用

- 「<某個工作流> 該跑哪一組 command？」
- 「做 MVP / 修缺陷 / 重構的 command 順序是什麼？」
- 「給我看所有 ECC command 群組的 recipe」（目錄模式）
- 「ECC 有多少個工作流 pipeline？」
- 使用者呼叫 `/ecc-recipes`，不管有沒有附描述。

### 不要使用的情況

- 使用者要現在就把任務做完：導向真正的 command，不要只描述它。
- 使用者要某「一個」command 的深入文件：用 `ecc-guide`。
- 使用者要改寫一份 prompt 草稿：用 `prompt-optimizer`。

## 核心原則

**從現在的檔案回答，不要靠記憶。** command 集合會變；絕對不要
寫死數量或成員清單。每次執行都要讀即時的 `commands/` 目錄，
再分類成家族。

### 即時讀取

解析 commands 目錄（取第一個存在的），再列出名稱：

```bash
for D in \
  "$HOME"/.claude/plugins/marketplaces/ecc/commands \
  "$HOME"/.claude/plugins/cache/ecc/ecc/*/commands \
  ./commands \
  ./.claude/commands \
  "$HOME"/.claude/commands; do
  [ -d "$D" ] && CMD_DIR="$D" && break
done
[ -z "${CMD_DIR:-}" ] && { echo "No ECC commands directory found."; return 1; }
find "$CMD_DIR" -maxdepth 1 -name '*.md' -exec basename {} .md \; | sort
```

如果有 `manifests/install-*.json`，可以選擇性地讀來做更豐富的分組。只讀
所需的最少檔案。

## 家族分類（依前綴）

依開頭的前綴把 command 名稱分組；已知的單獨 command 用手動對應。家族
是即時推導出來的，下面的表是*分類規則*，不是固定不變的清單。

| 家族前綴 | Recipe 含義 | 典型執行順序 |
|---|---|---|
| `orch-*` | 依任務類型分關卡的 Research、Plan、TDD、Review、Commit | 依任務種類挑一個 orch-*；它自己會跑內部階段 |
| `multi-*` | 多模型工作流 | `multi-plan` 然後 `multi-execute` 然後 review（或用 `multi-workflow` 端到端） |
| `prp-*` | PRD 到計畫到實作到 PR 的 pipeline | `prp-prd` 然後 `prp-plan` 然後 `prp-implement` 然後 `prp-commit` 然後 `prp-pr` |
| `epic-*` | 大型多單元 epic，平行進行 | `epic-decompose` 然後 `epic-claim` 然後 `epic-validate` 然後 `epic-review` 然後 `epic-unblock` 然後 `epic-sync` 然後 `epic-publish` |
| `loop-*` | 受管的自主 loop 與監控 | `loop-start <pattern>` 然後用 `loop-status` 觀察 |
| `gan-*` | generator 與 evaluator 的 loop | `gan-build`（程式碼）或 `gan-design`（UI）；會自己 loop |
| `*-build` / `*-review` / `*-test` | 各語言的 CI 三件組 | `<lang>-test`（TDD）然後 `<lang>-build`（修）然後 `<lang>-review` |
| `hookify-*` | 行為 hook 管理 | `hookify` 然後 `hookify-list` 然後 `hookify-configure` |
| `learn` / `instinct-*` / `evolve` / `promote` / `prune` | 持續學習 | `learn` 然後 `instinct-status` 然後 `evolve` 然後 `promote` |
| 單獨 command | `santa-loop`、`plan`、`plan-prd`、`pr`、`code-review`、`checkpoint` 等 | 單獨使用，或當群組之間的銜接 |

任何不符合前綴規則的 command，都列在**單獨 command** 底下，
附上它的一行說明。

## 運作方式

```
1. Live-read command names from CMD_DIR.
2. Classify into families by prefix and a singleton map.
3. If a workflow description was given -> MATCH MODE.
   If none -> CATALOG MODE.
4. Advisory only: print the plan. Never run the matched commands.
```

### 目錄模式（沒有描述）

輸出家族表：每個家族、成員數、成員、一行含義、
典型執行順序。最後附上 command 總數，並提示使用者描述一個
工作流來取得對應的 recipe。

### 對應模式（有給描述）

1. 用一句話重述工作流。
2. 挑最適合的 1 到 2 個家族；各用一行說明理由。
3. **執行順序區塊**：符合家族的確切 command 順序。
4. **停止條件**：一定要明確（最大執行次數、完成訊號、
   review 通過，或單次執行）。對自主 loop，要警告
   訂閱額度燒光的風險，並建議加上保底上限。
5. **去哪讀**：`commands/<name>.md` 路徑，加上 `/ecc-guide <name>`。

## 輸出範本（對應模式）

```
Workflow: <one-sentence restatement>

Best fit: <family> — <why>
(Alt: <family> — <why>)

Run-order:
  /<cmd1>   # job
  /<cmd2>   # job
  /<cmd3>   # job
  STOP when: <condition>
  WARNING (autonomous loops only): an unbounded loop burns subscription/credits —
  add a max-iteration or max-cost backstop alongside the completion signal.

Read full docs:
  commands/<cmd1>.md   (or: /ecc-guide <cmd1>)
```

## 範例

**目錄：** `/ecc-recipes` → 印出家族表與總數。

**對應：** `/ecc-recipes plan a whole app upfront then auto-build with adversarial
review until done` → 最適合：`loop-*`（自主）包住 `gan-*` 或
`santa-loop`（對抗式）。執行順序：`plan-prd` 然後
`loop-start rfc-dag --mode safe` 然後監控 `loop-status`；所有單元
連續 N 次通過 review 就停止（加一個最大迭代數的保底來限制消耗）。

**對應：** `/ecc-recipes fix a bug in my Go service` → 最適合：`orch-fix-defect`
（重現、修、review、commit）。替代方案：`go-test` 然後 `go-build` 然後
`go-review`。停止：regression 測試轉綠且 review 通過。

## 非目標

- 不是執行者，只提供建議。
- 不做各 command 的深入文件，那是 `ecc-guide` 的事。
- 不改寫 prompt，那是 `prompt-optimizer` 的事。
- 絕對不要寫死 command 數量或成員清單，一律即時讀取。
