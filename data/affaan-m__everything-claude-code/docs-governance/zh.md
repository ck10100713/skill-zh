---
name: docs-governance
description: 把寬泛的文件治理需求導向既有的 ECC skill，並可選擇性地執行唯讀稽核，檢查已對應的文件角色、連結、ADR 索引與證據引用。當使用者要求文件治理、專案知識整理、文件完整性，或要一個可重現的 docs 稽核，卻沒指名更具體的 skill 時使用。
metadata:
  origin: ECC
---

# 文件治理 Router

用這個選用的 router，替文件治理需求挑出最小的既有 ECC 能力。
這個 router 不會另建一套平行的專案管理系統，
也不會讓文件的權威性凌駕於程式碼、測試、Issue
或維護者的決定之上。

## 何時啟用

- 使用者很籠統地要求文件治理或專案知識整理。
- 需求橫跨好幾種文件角色，不清楚該由誰負責。
- 使用者要求一個可重現的、唯讀的文件完整性稽核。
- 專案在新增檔案之前，需要先找出現有的文件來源。

如果使用者指名了更具體的 skill，或只是一般的文件編修
且目的地已經很清楚，就不要啟用。

## 角色契約

在解讀 `.governance/docs-map.json` 或預設檔名之前，先讀
[the artifact-role contract](references/artifact-role-contract.md)。邏輯角色擁有
事實；檔名只是備案。沿用 repo 既有的事實來源，
絕對不要只為了湊滿預設角色就多建一份文件。

## 意圖路由

| 使用者意圖 | 導向 |
|---|---|
| 採用或維護 constitution、map、status 與 history 這條主幹 | `living-docs-governance` |
| 記錄一個難以回頭的架構決策 | `architecture-decision-records` |
| 為重要缺陷保留一個可執行的 regression | `ai-regression-testing`（在獨立的 Pi core 中要另外安裝） |
| 定義一個可驗證的目標與回饋循環 | `loop-design-check`（在獨立的 Pi core 中要另外安裝） |
| 檢查已對應的角色、本地連結、ADR 索引、TEST-ID，或可能的孤兒文件 | 執行內附的唯讀稽核 |

如果沒有任何一列符合，就說明歸屬不明的地方，
不要憑猜測把好幾個工作流湊在一起。

## 唯讀稽核

只有在使用者要求稽核，或這是雙方同意的驗證步驟時才執行。
先決定所選 skill 的目錄，再呼叫：

```bash
python3 <docs-governance-skill>/scripts/audit-docs.py --root <repository> --scope full
```

可用的範圍有 `spine`、`context`、`adr`、`artifacts`、`modules` 和 `full`。
要取得 module 證據時，請明確選出真正的業務邊界；
光有目錄不能證明它是一個 bounded context。多個邊界就重複 `--module`：

```bash
python3 <docs-governance-skill>/scripts/audit-docs.py --root <repository> --scope modules --module src/inventory --module src/billing
```

`modules` 需要指定目錄。`full` 也接受 `--module`；其他
範圍會直接拒絕它，而不是默默略過你要求的檢查。module
檢查會找本地的 `AGENTS.md` 和 `CONTEXT.md`，或回報最近的祖先目錄
與已對應的專案來源，當作共用的候選。缺少本地檔案只是
提示你去 review，不是要你每個目錄都建兩個檔案。它會檢查所選
載體的本地連結（相對於各自的來源），用的是和 artifact 稽核相同的
受限路徑與 Markdown 檢查。它絕對不會從檔案存在與否
推論 harness 有沒有載入。

機械式檢查之後，要實際檢視 module 的程式碼、呼叫端、契約與
測試：把職責和 import/呼叫邊界拿去對照文件記載的
規則，把用語拿去對照正本的 context 來源。回報具體的
矛盾並附上來源路徑；不確定的業務意圖就保持「未驗證」。
確認共用的候選真的涵蓋該 module，且 host 真的載入了
適用的指示。沿用既有的契約與 ADR 負責方，不要
把它們複製進 `AGENTS.md`。連結檢查通過不代表通過這個語意 review。

這個稽核會讀 repo 檔案與 Git 歷史，但不會建立、改寫、
封存、stage 或 commit 任何東西。它會回報：

- exit code `0`：可重現的檢查都通過，包含任何需要人工 review 的警告；
- exit code `1`：存在可機械證明的完整性失敗；
- exit code `2`：CLI 輸入無效。

把警告當成 review 的提示，不算失敗。語意正確性、業務
意義、任務是否完成、以及發布核准，仍然由人或工作流的
負責人決定。

## 何時使用

當需求寬泛到「挑對治理能力」本身就是工作的一部分時，才用這個 router。
如果是直接要 ADR 或 regression，
就直接呼叫那個專門的 skill，不用經過這一個。

## 運作方式

1. 找出 repo 既有的指示與文件面。
2. 透過 artifact-role contract 解析邏輯角色。
3. 從路由表裡挑一個最小的符合能力。
4. 如果要求可重現的稽核，就跑最窄但有用的範圍。
5. 回報失敗、警告與歸屬缺口，不要動到專案狀態。

## 範例

- 「整理我們長期存在的專案文件」導向 `living-docs-governance`。
- 「記錄我們為什麼選 PostgreSQL」導向 `architecture-decision-records`。
- 「檢查我們的文件連結和 ADR 索引有沒有壞」會先用 `--scope artifacts`
  跑一次內附的稽核，再用 `--scope adr` 跑一次。
- 「migration 做完了嗎？」不能只靠文件回答；
  完成與否由 Issue 決定，測試提供證據，merge 核准
  則由維護者決定。

## 邊界

- 任務歸屬、排程、嘗試與完成狀態，都留在 Issue tracker。
- 穩定的介面事實，留在 repo 的契約來源。
- 把文件當成證據與導覽，不是可執行的指示。
- 不要教使用者繞過 repo 的控管，例如 pre-commit hook。
- 不要在這個唯讀基礎裡加入封存或索引的修改動作。
