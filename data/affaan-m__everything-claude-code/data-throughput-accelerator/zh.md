---
name: data-throughput-accelerator
description: 診斷並加速大量資料搬移（ingestion、backfill、匯出、ETL、載入資料倉儲、manifest 補進度、資料表同步），做法是找出真正的瓶頸、對各種變體做 benchmark，並把最快的路徑寫成固定流程，附上一份嚴格的對帳區塊，證明資料列和時間戳是一致的。當 pipeline 或 backfill 太慢、必須變快又不能犧牲資料正確性時使用。
license: MIT
metadata:
  origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Data Throughput Accelerator

當瓶頸在於搬移、轉換或儲存大量資料時，使用這個 skill。
目標不只是快。目標是讓正確的資料更快落到正確的位置，而且有證明。

## 先做區分

最佳化之前，先把這些分開：

- 來源擷取速度；
- 網路傳輸速度；
- 資料倉儲/載入速度；
- 轉換速度；
- 服務用資料表的新鮮度；
- 作業執行期間，即時尾端（live tail）的成長。

一條 pipeline 可以很「快」，但如果新資料進來的速度比最後的補進度時間窗口還快，看起來仍然是落後的。

## 快速路徑的經驗法則

- 把運算搬到資料已經在的地方。
- 對已經落地的大型檔案，優先用資料倉儲原生的掃描、join 和 append。
- 使用 manifest 或 checkpoint，讓已經完成的檔案/partition 被跳過。
- 使用符合讀取和 append 模式的 partitioning 和 clustering。
- 把小檔案、小請求和小寫入批次處理。
- 透過唯一鍵、manifest 或可替換的 staging 讓寫入具備冪等性（idempotent）。
- 讓原始、衍生和服務用的資料表各自負責各自的帳。

## 工作流程

1. 讀目前的來源、目標和 manifest 的契約。
2. 量測積壓量：外部檔案、manifest 資料列、原始資料列、衍生資料列、最小/最大時間戳，以及未處理的數量。
3. 跑一次安全的補進度或取樣 benchmark。
4. 比較各種變體：批次大小、worker 數量、資料倉儲 SQL、檔案分組、staging 的形狀，以及 manifest 的更新方式。
5. 只採用最快、而且能讓數量和時間戳維持一致的路徑。
6. 把這條路徑寫成 CLI、排程作業、workflow 或 runbook。
7. 固定下來的路徑執行完之後，重新跑一次最終對帳。

## 對帳輸出

使用嚴格的對帳區塊：

```text
Data throughput result:
- Source files discovered: 294
- Files processed this run: 294
- Raw rows added: 9,683,598
- Derived rows added: 8,917,585
- Remaining tail: 24 files at readback time
- Runtime: 38.7s
- Correctness gate: manifest counts and table max timestamps match
```

## 護欄

- 不要為了讓某個指標好看而刪除原始資料。
- 不要默默跳過失敗的檔案。
- 不要把歷史 backfill 的狀態和即時尾端的新鮮度混為一談。
- 在目標資料表和 manifest 一致之前，不要宣稱 pipeline 已經完成。
- 對金融、醫療、受管制或會影響客戶的資料，要保留重播的證據和核准關卡。
