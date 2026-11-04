---
name: finetuning-method-selection
description: 判斷到底要不要 fine-tune，並導向正確的方法（SFT、DPO/ORPO/KTO、GRPO/RLVR、continued pretraining）與 base model。適用於開始任何 fine-tuning 工作、不確定 RAG 或 prompting 夠不夠用，或在偏好最佳化與強化學習方法之間做選擇的時候。
---

# Fine-Tuning 方法選擇

這是 fine-tuning 生命週期的路由 skill：它決定 fine-tuning 到底是不是對的工具，如果是，該用哪種方法、哪個 base-model 大小級距。這個 plugin 裡的其他每個 skill 都假設這個路由已經做過了，所以在打開 `lora-qlora-recipes`、`preference-optimization` 或 `grpo-rlvr-training` 之前，先從這裡開始。

## 什麼時候用這個 Skill

- 開始任何 fine-tuning 工作，且還沒選定 framework 或 base model 的時候。
- 不確定 RAG 或 prompt engineering 能不能用比訓練更低的成本解決問題。
- 針對同一個底層任務，在偏好最佳化（DPO 系列）和強化學習方法（GRPO/RLVR）之間做選擇。
- 在投入一次訓練之前，評估候選的模型/方法組合需要多大規模。

## 快速參考

| 情境 | 路線 |
|---|---|
| 事實常常變動（價格、文件、新聞） | RAG，不是 fine-tuning |
| 想要的行為還在摸索 | Prompt engineering |
| 穩定的領域知識，≥500MB 文字 | 先 CPT 再 SFT，見「先看替代方案」 |
| 有輸入/輸出的示範資料 | SFT，見 `lora-qlora-recipes` |
| 有偏好配對或讚/倒讚 | DPO/ORPO/KTO，見 `preference-optimization` |
| 有可驗證的 pass/fail 訊號 | GRPO+RLVR，見 `grpo-rlvr-training` |
| 還沒有 eval harness | 停下來，見 `eval-harness-first` |

## 先看替代方案（Off-Ramps First）

大部分聽起來像「把這個 fine-tune 一下」的需求，在別的地方做會更好也更便宜。開始訓練之前，先檢查這些替代方案：

- **知識導向且會變動**（缺口是會變的事實，例如價格、文件、時事）：走 RAG，不要 fine-tune。Fine-tune 過的模型烙印的是某個時間點的快照，會變動的事實馬上就過時。
- **行為導向且還在變**（想要的行為還在摸索，或每次請求都不同）：走 prompt engineering。Fine-tuning 會把行為鎖死，不要鎖一個還沒穩定下來的行為。
- **穩定且密集的領域知識**：這是 continued pretraining（CPT）登場的地方，依領域文字的量來決定規模：

| 領域文字量 | 路線 |
|---|---|
| <10MB | 只用 RAG |
| 10MB–500MB | RAG + fine-tune |
| 500MB–10GB | CPT，再 SFT |
| >10GB | 必須用 CPT |

CPT 的 learning rate 約為 **pretraining LR 的 10%**。在這個 plugin 裡 CPT 只提供指引：規模和 LR 的建議在這裡，但這個 plugin 不會執行 CPT 訓練。

## 方法路由

排除掉替代方案之後，這就是完整的決策樹（逐字取自這個 plugin 所根據的研究）：

```
新「事實」？  會變動 → RAG | 穩定且密集 → CPT（LR 約 pretrain 的 10%）→ SFT
新「行為」？ 還在變 → prompt-engineering | 穩定：
  示範資料 → SFT（LoRA/QLoRA、all-linear、α=2r）
  偏好配對 → DPO（有長度偏誤用 SimPO，記憶體受限用 ORPO）
  非配對的 👍/👎 → KTO
  可驗證的成功 → RLVR + GRPO（依失敗模式選 DAPO/GSPO/Dr.GRPO）
Deploy：FP8（Hopper+）| NVFP4（Blackwell 規模）| AWQ（較舊的）| GGUF+imatrix（edge）
在這一切之前：eval harness 必須先存在。
```

從上往下讀這棵樹：先回答「是新事實還是新行為」，再順著符合手上資料形狀的分支走（示範資料、偏好配對、讚/倒讚，或可驗證的成功/失敗）。是資料形狀決定方法，不是反過來。

### 實際的路由範例

- *「使用者希望助理完全照著我們的客服 macro 做。」* 行為穩定，而且可以從對話紀錄中示範 → 示範資料 → **SFT**。
- *「我們有來自審稿者讚/倒讚的好壞回應，但不是成對的。」* → 非配對訊號 → **KTO**，不是 DPO（DPO 需要成對的偏好）。
- *「模型已經能解其中一部分數學題，而且我們可以自動評分對錯。」* → 可驗證的成功訊號 → **GRPO+RLVR**，而且要先確認模型至少有時候會成功（見下面的「關鍵路由事實」）。
- *「我們要讓模型知道這週的價格頁面。」* → 會變動的事實 → **RAG**，完全不需要訓練。

## 關鍵路由事實

- **Loss function 的選擇槓桿很低。** 一項動用 240 張 H100 的研究發現，方法選擇大約只值 1 個百分點，模型規模則值約 50 個百分點，而且 20 種 DPO 變體沒有任何一個贏過原版 DPO。不要在路由決策上花力氣糾結該選哪個 DPO 變體，把力氣花在把資料形狀和規模弄對。
- **DPO 管品味，GRPO+RLVR 管推理。** 編碼了主觀判斷的偏好配對（語氣、風格、「哪個答案比較好」）走 DPO。有可驗證 pass/fail 訊號的任務（數學、程式碼、tool call）則走 GRPO+RLVR。
- **RL 不是用來救一個從來不會成功的模型。** GRPO 和其他 RL 方法是把既有的能力磨得更銳利，不是從零教會一個能力。如果模型還不了解任務或輸出格式，先跑 SFT；等到模型至少有時候會成功，再引入 RL。

### 常見的路由錯誤

- 想用 fine-tuning 修正每週都在變的事實，那是 RAG 的問題，fine-tuning 只會比來源資料更快過時。
- 在確認真正的瓶頸是資料品質還是模型規模之前，就先挑 DPO 變體，變體的選擇只是約 1 個百分點的槓桿，不是約 50 個百分點的那個。
- 在每次 rollout 都失敗的模型上開始 RL 訓練，要先走 SFT，讓 RL 有東西可以磨。
- 把 CPT 當作「模型不懂我們的領域」的預設解法，要先檢查資料量的門檻；低於 500MB 的話，RAG 或 RAG+fine-tune 的迭代速度比 CPT 快。

## 模型選擇

Base model 的選擇是先看大小級距、再看家族，而且很快就會過時，所以只放在一個地方：`references/model-catalog.md`。這個檔案是這個 plugin（以及 DGX Spark ops plugin）裡唯一會點名 base-model 家族的地方。這個 skill 和 `references/memory-math.md` 都不會點名，兩者都只用大小級距來描述模型（例如「8B 級的 LoRA」，不是某個模型名稱）。

這份 catalog 刻意標了日期，因為模型排名每季都在洗牌。它帶有「最後驗證」的日期和一份更新檢查表。採信某一列之前，先檢查那個日期；如果已經過期，推薦其中的模型之前，要先照 catalog 裡的更新檢查表處理一遍。

**當 catalog 和方法 skill 不一致時的優先順序：** catalog 每一列的 Notes 欄位講的是硬體/大小級距的*可行性*，不是方法的建議，實際的方法選擇由 `lora-qlora-recipes` 的 LoRA vs QLoRA vs Full FT 表（依任務形狀路由）決定。

## 記憶體可行性

在決定方法之前，先估算規模：總記憶體 ≈ **參數量 × dtype 位元組數 + optimizer state + gradient + activation**。針對選定的 dtype 和方法（完整 fine-tune、LoRA 或 QLoRA）算出每一項，實際的計算表和大小級距範例放在 `references/memory-math.md`。

特別是在 DGX Spark 上，unified memory 的行為會讓天真的估算失準（載入時的暫時峰值、`nvidia-smi` 低報、長時間執行時的 thermal throttling）。一旦安裝了 `dgx-spark-ops` plugin，Spark 專屬的可行性判斷就交給它的 `spark-memory-thermal-ops` skill，不要在這裡重新推導。

## 相關 Skill

這個 skill 選定方法之後，就交給負責執行該方法的 skill：

- `lora-qlora-recipes`：透過 LoRA/QLoRA 做 SFT
- `preference-optimization`：DPO、ORPO、KTO
- `grpo-rlvr-training`：用可驗證的 reward 做 GRPO

在 eval harness 存在之前，不准選定任何方法，見 `eval-harness-first`。
