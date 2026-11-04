---
name: agentic-engineering
description: 以 agentic engineer 的方式工作：先寫 eval 再執行、拆解任務，並依成本選擇模型。規劃或執行會由 agent 從頭做到尾的工程工作時使用。
metadata:
  origin: ECC
---

# Agentic Engineering

用在由 AI agent 做大部分實作、人類負責把關品質和風險控管的工程工作流程。

## 運作原則

1. 執行之前先定義完成條件。
2. 把工作拆成 agent 大小的單元。
3. 依任務複雜度選模型等級。
4. 用 eval 和回歸檢查來衡量。

## Eval 優先迴圈

1. 定義能力 eval 和回歸 eval。
2. 跑基準線，記下失敗特徵。
3. 執行實作。
4. 重跑 eval，比較差異。

## 任務拆解

套用 15 分鐘單元規則：
- 每個單元都應該能獨立驗證
- 每個單元都應該只有一個主要風險
- 每個單元都應該有明確的完成條件

## 模型選擇

- Haiku：分類、樣板轉換、範圍很窄的修改
- Sonnet：實作和重構
- Opus：架構、根因分析、跨多個檔案的不變條件

## Session 策略

- 緊密耦合的單元，繼續用同一個 session。
- 大的階段轉換之後，開新的 session。
- 里程碑完成後再 compact，不要在積極除錯的時候 compact。

## AI 產生的程式碼的 Review 重點

優先看：
- 不變條件和 edge case
- 錯誤邊界
- 安全和授權的假設
- 隱藏的耦合和上線風險

如果自動化的 format/lint 已經在管風格，就不要把 review 的力氣浪費在純風格的爭論上。

## 比對資料之前，先解讀工具結果

處理文件讀取和處理迴圈時，要依序檢查三個邊界：

1. 檢查工具或傳輸層的外層封包，看有沒有錯誤或結果不明的狀況。
2. 解碼回應，並依該工具文件記載的約定檢查操作狀態。外層的成功旗標或
   有 payload，都不能證明所要求的操作成功了。狀態可能在結構化內容、
   解碼後的文字或其他有文件記載的欄位裡；`result.ok` 不是通用的 MCP
   欄位。缺少或無法辨識的狀態，一律視為未知。
3. 確認操作成功之後，才驗證文件的形狀並比對它的欄位。操作失敗不等於
   文件識別碼不符。

要保留操作名稱、有的話的 request/correlation ID、相關的狀態和錯誤細節，
以及診斷所需的原始回應。記錄或分享之前，要遮蔽 secret 和私人文件資料。
不要用後面一個回應的形狀去重建缺少的回應。

### 可移植的分類範例

下面的 adapter 用的是**示意用的讀取工具約定**，不是 MCP schema：
`isError` 是必要的布林值；為 false 時，`result.ok` 是必要的操作
狀態。成功的讀取會回傳 `result.document`，裡面有字串型別的 `id`；失敗的
讀取可能帶有 `result.error`。請把這個 adapter 換成實際工具的
約定，包含它有文件記載的解碼和文件驗證規則。

```javascript
function decodeRead(response) {
  if (!response || typeof response.isError !== 'boolean') {
    return { kind: 'unknown_response' };
  }
  if (response.isError) return { kind: 'tool_error' };

  const result = response.result;
  if (result?.ok === false) {
    return { kind: 'operation_error', error: result.error };
  }
  if (result?.ok !== true) return { kind: 'unknown_response' };

  const document = result.document;
  if (!document || typeof document.id !== 'string') {
    return { kind: 'invalid_document' };
  }
  return { kind: 'document', document };
}

function inspectRead(response, expectedId, decode = decodeRead) {
  const outcome = decode(response);
  if (outcome.kind !== 'document') return outcome;

  return outcome.document.id === expectedId
    ? { kind: 'match', document: outcome.document }
    : { kind: 'field_mismatch', actualId: outcome.document.id, expectedId };
}
```

合成的評估案例（不是重現任何歷史事故）：

| 在這個示意約定下的輸入 | 預期的分類 |
| --- | --- |
| `isError: true` | `tool_error`；不做欄位比對 |
| `isError: false`、`result.ok: false`、維護中的錯誤、沒有文件 | `operation_error`；保留維護的細節，不算不符 |
| `isError: false`、缺少操作狀態 | `unknown_response`；不做欄位比對 |
| 確認成功、缺少文件或 ID 不是字串 | `invalid_document`；不做欄位比對 |
| 確認成功、有效文件且 ID 符合預期 | `match` |
| 確認成功、有效文件但 ID 不同 | `field_mismatch` |

分類本身不授權寫入或重試。暫時性的維護仍然是帶著自己證據的操作失敗；
要依工具文件記載的復原政策處理。文件記載的全服務維護失敗，應該讓整批
作業停下來，而不是對每一列都重複同樣的請求；單一的授權錯誤，
不能證明是全服務維護。如果寫入逾時或結果不明，
要保留這個不確定性，並透過有文件記載的狀態/回讀機制先對帳，再考慮
重試。絕對不要只因為讀取失敗或回傳的欄位不同，就推論寫入失敗、重複寫入，
或覆蓋文件。

## 成本紀律

每個任務都要追蹤：
- 模型
- token 估計值
- 重試次數
- 實際耗時
- 成功或失敗

只有在較低等級的模型因明確的推理缺口而失敗時，才升級模型等級。
