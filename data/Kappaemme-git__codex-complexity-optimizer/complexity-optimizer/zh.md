---
name: complexity-optimizer
description: 分析軟體 codebase 的演算法複雜度和效能熱點，然後提出或實作不破壞行為的安全優化。當 Codex 被要求掃描大量檔案、找出低效率的迴圈、巢狀迭代、重複掃描、昂貴的 rendering／重算、N+1 query、可以避免的 O(n^2) 或 O(n) 操作，或是把 O(n^2) 降成 O(n log n) / O(n) 這類複雜度，同時要保住測試、API、輸出和可維護性時使用。
---

# Complexity Optimizer

## Core Rule

只有在目前的行為已經搞清楚、而且能保住的時候才優化。寧可做小而有測試證明的改進，也不要做正確性不明的大改寫。

## Default Behavior

當使用者要求分析、掃描、audit、review，或「給我一份報告」時，自動產出完整的複雜度報告。不用等使用者指定報告欄位。

預設的報告內容：

- 分析的範圍，以及偵測到的技術棧／測試指令。
- 依可能影響大小排序的主要發現。
- 每個發現的檔案和行號。
- 目前的寫法，以及為什麼可能很貴。
- 目前的估計複雜度。
- 建議的修改。
- 修改後的估計複雜度。
- 風險等級。
- 需要的測試、benchmark 或手動檢查。
- 明確聲明沒有修改任何檔案，除非使用者明確要求實作。

只有在使用者要求實作、修、優化、套用、修改、refactor，或是其他明確要求改程式碼的時候，才編輯檔案。如果使用者只要分析或報告，就不要改檔案。

## Workflow

1. 建立基準：
   - 找出語言、framework、測試指令、build 指令，以及對效能敏感的路徑。
   - 動程式碼之前先看現有的測試。
   - 掃描 repo 時，先跑 `scripts/analyze_complexity.py <repo>` 取得第一輪的熱點清單。

2. 排序機會：
   - 優先處理熱路徑、大量輸入的路徑、rendering 迴圈、資料庫／API 迴圈，以及共用的 utility。
   - 把演算法複雜度和常數係數的整理分開。
   - 不要每個警告都去修。掃描器的輸出當線索，不是證據。
   - 只要報告的請求，要看夠多周圍的程式碼來估計目前和建議後的複雜度，不要只停在掃描器的原始輸出。

3. 證明行為：
   - 找出或補上針對要改的函式／元件的聚焦測試。
   - 抓出邊界情況：空輸入、重複值、順序穩定性、null／缺值、錯誤、權限、分頁、時區，以及會改動資料的副作用。
   - 如果沒有測試而且行為不明確，就做最小的 refactor，或是先問預期行為，再動語意。

4. 保守地優化：
   - key 相等性穩定的時候，把重複的線性查找換成 map／set。
   - 只有在資料形狀支持的情況下，才把巢狀掃描換成 indexing、grouping、雙指標掃描、sweep-line、二分搜尋、memoization、batching 或預先計算。
   - UI 程式碼裡，用穩定的 props、memoize 衍生資料、virtualization、debounce，並把昂貴的工作移出 render 路徑，來減少不必要的 render。
   - 資料存取的程式碼裡，用批次抓取、join、preload、cache 或 batching 移除 N+1，同時保住授權和過濾。

5. 驗證：
   - 跑相關的測試和 type／lint／build 指令。
   - 複雜度改善不明顯或對效能很關鍵時，加一個 micro-benchmark 或量測。
   - 回報原本的複雜度、新的複雜度、改動的檔案、跑過的測試，以及剩下的風險。

## First-Pass Scanner

用 skill 目錄裡附的掃描器：

```bash
python3 scripts/analyze_complexity.py /path/to/repo --format markdown
python3 scripts/analyze_complexity.py /path/to/repo --format json
```

掃描器會標出 Python、JavaScript、TypeScript、JSX/TSX、Java、Go、C、C++、C#、Ruby、PHP 和 Swift 檔案裡常見的寫法。它刻意追求好讀的線索，而不是完美的靜態分析。

如果掃描器什麼都沒回報，還是要手動檢查已知的熱路徑。Rendering 的反覆重繪、資料庫 query 的寫法、framework 生命週期的問題，常常需要該 repo 專屬的脈絡才看得出來。

## Optimization Safety Checklist

編輯之前：

- 確認資料量大到複雜度真的有差。
- 確認優化後保住輸出順序，因為呼叫端可能依賴它。
- 確認物件 identity、可變性和 reference 共用不是公開行為的一部分。
- 確認 cache 有有效的失效策略。
- 確認去重不會把顯示標籤相同但實際不同的記錄合併掉。
- 確認資料庫的 batching 保住 tenant、權限、soft-delete、分頁和排序的限制。

編輯之後：

- 先跑範圍窄的測試，再跑範圍最廣的相關測試／build 指令。
- 有 benchmark（原本就有或新加的）時，比對前後的數字。
- 讓 patch 保持局部。不要在不相關的檔案裡亂改格式。

## References

- 常見的 O(n^2) 到 O(n log n) / O(n) 轉換和 framework 專屬的寫法，讀 `references/optimization-playbook.md`。
- 準備最後的分析或 audit 輸出時，讀 `references/report-template.md`。
