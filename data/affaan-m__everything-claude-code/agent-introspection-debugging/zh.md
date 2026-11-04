---
name: agent-introspection-debugging
description: 針對 AI agent 失敗的結構化自我除錯工作流程，包含擷取、診斷、受控恢復和自省報告。當 agent 執行失敗，而你需要的是可重現的診斷，不是重試時使用。
metadata:
  origin: ECC
---

# Agent Introspection Debugging

當 agent 的執行一直失敗、消耗 token 卻沒有進展、在同樣的工具上打轉，或是偏離原本的任務時，使用這個 skill。

這是一個工作流程 skill，不是隱藏的 runtime。它教 agent 在升級給人類之前，先有系統地替自己除錯。

## When to Activate

- 達到最大工具呼叫次數／迴圈上限的失敗
- 重複重試卻沒有往前進展
- Context 成長或 prompt 漂移，開始降低輸出品質
- 檔案系統或環境狀態和預期不符
- 工具失敗，很可能透過診斷加上更小的修正動作就能恢復

## Scope Boundaries

在這些情況啟用這個 skill：
- 在盲目重試之前先擷取失敗狀態
- 診斷常見的 agent 專屬失敗模式
- 套用受控的恢復動作
- 產出結構化、人類可讀的除錯報告

不要把這個 skill 當作以下情況的主要依據：
- 改完程式碼之後的功能驗證；用 `verification-loop`
- 已經有範圍更窄的 ECC skill 時的框架專屬除錯
- 目前的 harness 無法自動強制執行的 runtime 承諾

## Four-Phase Loop

### Phase 1: Failure Capture

在嘗試恢復之前，先精確記錄失敗。

擷取：
- 錯誤類型、訊息，以及可取得時的 stack trace
- 最後一段有意義的工具呼叫序列
- agent 當時想做什麼
- 目前的 context 壓力：重複的 prompt、過大的貼上日誌、重複的計畫，或是失控的筆記
- 目前的環境假設：cwd、branch、相關服務的狀態、預期的檔案

最低限度的擷取範本：

```markdown
## Failure Capture
- Session / task:
- Goal in progress:
- Error:
- Last successful step:
- Last failed tool / command:
- Repeated pattern seen:
- Environment assumptions to verify:
```

### Phase 2: Root-Cause Diagnosis

在改動任何東西之前，先把失敗對應到已知的模式。

| 模式 | 可能的原因 | 檢查 |
| --- | --- | --- |
| 最大工具呼叫次數／重複同一個指令 | 迴圈，或沒有出口的觀察路徑 | 檢查最近 N 次工具呼叫有沒有重複 |
| Context 溢出／推理品質下降 | 無限制的筆記、重複的計畫、過大的日誌 | 檢查最近的 context 有沒有重複和低訊號的大量內容 |
| `ECONNREFUSED` / timeout | 服務不可用或 port 錯誤 | 驗證服務健康狀態、URL 和 port 的假設 |
| `429` / 額度耗盡 | 重試風暴或缺少 backoff | 計算重複呼叫的次數，檢查重試的間隔 |
| 寫入後檔案不見／過時的 diff | race、錯的 cwd，或 branch 漂移 | 重新檢查路徑、cwd、git status 和檔案是否真的存在 |
| 「修好」之後測試仍然失敗 | 假設錯了 | 隔離出確切失敗的測試，重新推導 bug |

診斷的問題：
- 這是邏輯失敗、狀態失敗、環境失敗，還是政策失敗？
- agent 是不是忘了真正的目標，開始去優化錯的子任務？
- 這個失敗是確定性的還是暫時的？
- 能驗證這個診斷的、最小又可回復的動作是什麼？

### Phase 3: Contained Recovery

用能改變診斷面的最小動作來恢復。

安全的恢復動作：
- 停止重複重試，重新陳述假設
- 修剪低訊號的 context，只保留目前的目標、阻礙和證據
- 重新檢查實際的檔案系統／branch／行程狀態
- 把任務縮小到一個失敗的指令、一個檔案，或一個測試
- 從臆測式的推理，切換到直接觀察
- 當失敗風險高，或是被外部因素卡住時，升級給人類

不要宣稱沒有根據的自動修復動作，像是「重設 agent 狀態」或「更新 harness 設定」，除非你真的在目前的環境裡用實際的工具在做這些事。

受控恢復的檢查清單：

```markdown
## Recovery Action
- Diagnosis chosen:
- Smallest action taken:
- Why this is safe:
- What evidence would prove the fix worked:
```

### Phase 4: Introspection Report

用一份報告結尾，讓下一個 agent 或人類能看懂這次恢復。

```markdown
## Agent Self-Debug Report
- Session / task:
- Failure:
- Root cause:
- Recovery action:
- Result: success | partial | blocked
- Token / time burn risk:
- Follow-up needed:
- Preventive change to encode later:
```

## Recovery Heuristics

依這個順序優先採用這些介入方式：

1. 用一句話重新陳述真正的目標。
2. 驗證世界的狀態，不要相信記憶。
3. 縮小失敗的範圍。
4. 執行一個有鑑別力的檢查。
5. 然後才重試。

不好的模式：
- 用稍微不同的措辭，把同一個動作重試三次

好的模式：
- 擷取失敗
- 分類模式
- 執行一個直接的檢查
- 只有在檢查支持時才改變計畫

## Integration with ECC

- 如果有改過程式碼，恢復之後用 `verification-loop`。
- 當失敗模式值得變成直覺或之後的 skill 時，用 `continuous-learning-v2`。
- 當問題不是技術失敗，而是決策不明確時，用 `council`。
- 如果失敗來自衝突的本機狀態或 repo 漂移，用 `workspace-surface-audit`。

## Output Standard

當這個 skill 啟用時，不要只用「我修好了」結尾。

一定要提供：
- 失敗模式
- 根本原因的假設
- 恢復動作
- 證明情況現在已經變好、或仍然被卡住的證據
