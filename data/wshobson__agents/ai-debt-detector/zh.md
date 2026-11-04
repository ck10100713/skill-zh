---
name: ai-debt-detector
description: >-
  在產生程式碼之後、接受 AI 建議之後，或審查 AI 寫的模組時使用。
  程式碼能跑但感覺很脆弱、錯誤處理看起來很薄、懷疑有遺留的資源或缺少清理，
  或 agent 說做完了但可能藏著債務時，也用這個。
  專抓 AI agent 會犯、而人類不會犯的特定失敗模式。
---

# AI Debt Detector

## 概覽

AI agent 產生的程式碼能走通 happy path，卻藏著債務：缺少錯誤處理、遺留的資源、被忽略的失敗模式、幻覺出來的套件，還有悄悄發生的架構漂移。這個 skill 會強制針對 AI agent 確實會做錯的那些模式，做一次有針對性的稽核。

## 何時使用

- 任何 AI 產生程式碼的 session 之後（產出 20 行以上）
- merge AI 產生的 PR 之前
- 程式碼能跑但總覺得哪裡怪怪的
- vibe-coding 衝刺之後，這時債務累積得最快
- agent 說做完了，卻沒有展示驗證結果

## 流程

程式碼產生之後，掃描這些 AI 特有的債務模式：

1. **FAILURE MODES（失敗模式）** - 這個失敗的時候會怎樣？
   - 網路逾時？磁碟滿了？權限被拒？輸入是 null？
   - 有 try/catch 嗎？它是抓特定的錯誤，還是把所有東西都吞掉？
   - 失敗時資源有清理嗎？（stream 關閉、連線歸還、暫存檔刪除）

2. **ORPHANS（孤兒資源）** - 有什麼東西被建立了卻從沒被清理？
   - 暫存檔、event listener、interval、subscription、連線
   - 每個 open/create 都有對應的 cleanup/dispose/close 呼叫嗎？
   - 在 React 裡：每個 addEventListener 在 cleanup 裡都有 removeEventListener 嗎？

3. **EDGE CASES（邊界情況）** - 什麼輸入會把它弄壞？
   - 空陣列/空字串？null/undefined？好幾 MB 的輸入？Unicode？並行呼叫？
   - 程式碼有假設走 happy path 嗎？（AI 幾乎一定會）

4. **HALLUCINATED DEPS（幻覺出來的相依套件）** - 所有的 import 真的都存在嗎？
   - 每個套件都在 package.json/requirements.txt 裡嗎？
   - API 方法是真的嗎？（AI 會發明聽起來很合理但根本不存在的方法）
   - 這個函式庫的最新版本還有匯出這個函式嗎？

5. **ARCHITECTURAL DRIFT（架構漂移）** - 這符合專案的模式嗎？
   - 錯誤處理的風格跟既有程式碼一樣嗎？
   - 有用專案既有的工具函式（而不是重新發明）嗎？
   - 有遵循檔案結構的慣例嗎？

## 警訊（立刻停下來修）

- `catch (e) {}` 或 `catch (e) { console.log(e) }` - 錯誤被吞掉
- 開了資源卻沒有 `finally` 區塊
- `// TODO: handle error` - AI 的推託手法
- import 的路徑在專案裡不存在
- 設了 timeout，但逾時時沒有 abort/cleanup
- 資料庫連線開了，卻從來沒有釋放回 pool

## 常見錯誤

- 以為能編譯就代表正確（編譯只檢查語法，不檢查邏輯）
- 只審查 diff，沒有檢查 AI 沒有產生的東西（缺少的錯誤路徑）
- 以為 AI 用了正確的函式庫版本（它常常用已棄用的 API）
- 因為垃圾回收會處理，就跳過孤兒檢查（連線、listener、計時器它不會處理）

## 為什麼要有這個

AI agent 系統性地針對「看起來正確」和「通過 happy path」做最佳化。它們漏掉失敗模式、遺留資源、幻覺出相依套件的比率，明顯高於人手寫的程式碼。這個 skill 強制針對這些特定的盲點做稽核。
