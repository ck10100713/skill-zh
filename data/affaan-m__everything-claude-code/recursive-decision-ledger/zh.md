---
name: recursive-decision-ledger
description: 重複做 rollout（「Prime Gauss」風格的遞迴提示），同時維護一份只能追加的決策帳本，記錄各次試驗、標記、一致性檢查和晉升關卡，讓遞迴產生的信心絕對不會自動核准實盤交易、deploy 或破壞性操作。使用者要求重複 rollout、標記式決策流程、高維度搜尋、隨機最佳化、探索局部最佳解、ensemble 比較，或需要看得到證據軌跡的遞迴推理時使用。
license: MIT
metadata:
  origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# 遞迴決策帳本

使用者想靠重複 rollout 或「Prime Gauss」風格的遞迴提示，逼出更深的運算時，使用這個 skill。
保留有用的部分：重複試驗、先前的記憶、新資訊，和明確的標記。
拿掉不安全的部分：假裝這個迴圈能證明確定性。
Remove the unsafe part: pretending the loop proves certainty.

## 帳本契約

每次 rollout 都要記錄：

- rollout id 和時間戳；
- 先前被接受的贏家和先前的觀察名單；
- 吸收進來的新資訊；
- 搜尋空間大小；
- 用到的模型家族或啟發式方法；
- 試驗次數和有效試驗次數；
- 前幾名候選；
- 決策標記；
- 與先前帳本的一致性標記；
- 晉升關卡的結果。

append-only 的帳本優先用 JSONL，給人看的摘要用 Markdown。

## Rollout 迴圈

1. 載入先前的帳本。
2. 在時間步零擷取新資訊。
3. 跑有界的搜尋。
4. 標記每個候選：accept、watch、reject、decay watch，或 needs replay。
5. 把贏家與先前的贏家、最近一次標記過的 rollout 做比較。
6. 當漂移、尾部風險、資料過期或 replay 失敗讓先前的標記失效時，
   就把候選降級。
7. 先追加產出物，再做摘要。

## 一致性標記

加上一個精簡的一致性標記：

```text
Ensemble matches prior winner: true
Recursive matches prior winner: false
Latest rollout match: true
Live promotion allowed: false
Reason: replay and freshness gates not satisfied
```

## 晉升規則

交易、資金配置、production deploy、migration 或破壞性
操作，遞迴產生的信心不等於核准。

預設用 paper、dry-run、唯讀、預覽或分階段模式，除非使用者
明確核准實際執行，而且 repo／服務的關卡也支援。

只有在以下情況才晉升：

- 候選在選定的指標上勝過先前被接受的贏家；
- 正確性和 replay 檢查通過；
- 風險上限明確；
- 證據是持久的；
- 需要時，使用者已核准實際執行的步驟。

## 摘要形式

先講決策，不要講戲劇性的過程：

```text
第 15 次 rollout 完成。先前的贏家仍然成立，但優勢衰退了 17%。
狀態：watch，不上實盤。下一個關卡：20 筆 replay 成交，且新的
orderbook 時效低於門檻。
```
