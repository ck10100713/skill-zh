---
name: grpo-rlvr-training
description: 用 GRPO 和 reinforcement learning from verifiable rewards（RLVR）訓練推理和可驗證任務的行為。適用於任務成功與否可以用演算法檢查（數學、程式碼、tool call、結構化輸出）、設計 GRPO reward function，或 GRPO 訓練發散、出現 reward hacking 的時候。
---

# GRPO 與 RLVR 訓練

這個 skill 假設 `finetuning-method-selection` 已經把你導到這裡，因為目標行為有可驗證的 pass/fail 訊號，而不是示範資料（`lora-qlora-recipes`）或偏好配對（`preference-optimization`）。接下來的內容是：什麼時候 RL 才是對的工具、參考做法、強制的 reward 檢視關卡，以及基本做法出問題時怎麼挑選 GRPO 變體。

**輸入：** 一個路由決定（透過 GRPO 做 RLVR），加上目標任務的 verifier（程式碼執行器、測試套件、schema 檢查器或 grader）。
**輸出格式：** 一份經過驗證的 GRPO config，內容是 `references/grpo-memory.md` 裡的 kwarg 數值和 `references/reward-functions.md` 裡的 reward function，不是隨口的建議，`llm-finetuning-training-engineer` 會直接拿去用。

## 什麼時候適用 RL

只有在任務成功與否**可以用演算法檢查**的時候，GRPO+RLVR 才划算，例如 unit test 通過、parser 接受輸出、tool call 符合預期的 schema、數學答案符合 ground truth。如果評分輸出需要人的判斷或主觀的 rubric，那首先是 eval-harness 和 judge 校準的問題，見 `eval-harness-first`，不是直接跳去 RL 的理由。

開始 GRPO 訓練之前，先確認模型對目標任務**有時候**已經能成功。RL 是透過往已經有效的樣本重新加權來磨利既有的能力，它沒辦法從零裝上一個能力。

- **模型從來不成功，即使在低 temperature 下取很多樣本也一樣：** 缺口在於格式或對任務的理解，不是 policy 的精修。先回頭做 SFT（`lora-qlora-recipes`），等 base 的成功率不是零了，再回到這個 skill。
- **模型有時候成功、但不穩定：** 這就是 GRPO 的甜蜜點，繼續看下面的「做法」。

整個 plugin 的固定原則：**DPO 管品味，GRPO 管推理。** 如果訊號是兩個都可接受的輸出之間的偏好，那是 `preference-optimization` 的事，不是這個 skill。

## 做法（The Recipe）

參考做法是 TRL 的 `GRPOTrainer`，搭配以 vLLM 為基礎的生成：

```python
from trl import GRPOConfig, GRPOTrainer

grpo_args = GRPOConfig(
    output_dir="./outputs-grpo",
    use_vllm=True,
    vllm_mode="colocate",       # 單張 GPU；多 GPU 用 "server"
    num_generations=8,          # 下限，再少 group-relative baseline 就會失真
    learning_rate=5e-7,         # GRPO 已經確定的範圍
    beta=0.01,                  # 相對於 reference policy 的 KL 係數
    per_device_train_batch_size=8,
    gradient_accumulation_steps=4,
    bf16=True,
    logging_steps=10,
    seed=3407,
)

trainer = GRPOTrainer(
    model=SFT_CHECKPOINT,
    args=grpo_args,
    reward_funcs=[format_reward, correctness_reward],   # references/reward-functions.md
    train_dataset=prompts,       # 只有 prompt，GRPO 會自己生成 completion
    processing_class=tokenizer,
)

trainer.train()
```

- **`vllm_mode="colocate"`** 讓生成和訓練在同一張 GPU 上跑，是單 GPU 機器的預設。
- **`vllm_mode="server"`** 指向獨立的 vLLM server 行程，是多 GPU 的做法，生成和訓練不會搶同一個裝置。
- **`num_generations` ≥ 8** 是下限，不是建議：GRPO 的 advantage 估計是相對於 group 的平均值，每個 prompt 少於 8 個樣本，baseline 就會有雜訊。
- **Reward 是複合的**：format reward（輸出有沒有 parse 成功/符合要求的結構）加上 correctness reward（答案有沒有驗證通過）。格式正確但答案錯的，和格式錯誤的，不應該得到同樣的分數；只用 correctness 會丟掉這個訊號。
- **`learning_rate=5e-7`** 和 **`beta=0.01`** 是已確定的起點；要等 base 訓練穩定、而且 reward 檢視過（見下）之後才偏離這些值。

依目標大小級距的這套做法所需的記憶體估算：`references/grpo-memory.md`。

## 檢視規則（The Inspection Rule）

**在開始真正的訓練之前，把 reward function 跑在 50–100 筆取樣的輸出上，並且親自讀過結果。** 這是一道關卡，不是只做一次的健全性檢查。

如果 reward function 的判斷和人讀那批樣本的結果不一致，先修 reward function。針對沒檢視過的 reward 做訓練，或是調超參數去補償一個悄悄打錯分數的 reward，就是 reward hacking 的由來：模型乾淨俐落地朝錯誤的目標最佳化，而這不會以訓練迴圈 bug 的形式浮現。

這個檢視是 `/finetune` 的 Phase 1 關卡輸入，在這裡抓出壞掉的 reward function 的那 50–100 筆樣本的閱讀，就是該指令在放行 GRPO brief 之前會檢查的東西。

可供檢視的完整 reward function 實作，包含 exact-match、schema 驗證、unit test 執行、length-penalty 包裝，以及 rubric-as-reward 的 judge 模式：`references/reward-functions.md`。

## 變體選擇

上面的基本做法是預設值。只有當特定的失敗模式出現時才使用變體，不要預先套用：

| 失敗模式 | 變體 | 原因 |
|---|---|---|
| Entropy collapse / 退化的長 chain-of-thought | **DAPO** | 把 clip 邊界拆開，並放寬在長推理 trace 上對探索過度正則化的 KL 懲罰 |
| Reward 或輸出長度不論品質如何都往上走 | **Dr.GRPO** | 移除 GRPO 的 length-normalization 偏誤，讓 reward 追蹤的是正確性，而不是 completion 長度 |
| 訓練 mixture-of-experts 模型 | **GSPO** | 把 importance-sampling ratio 移到 sequence 層級，而不是逐 token，逐 token 的 ratio 在 MoE 路由上不穩定，所以在這裡 GSPO 是必要的，不是選配 |

從純 GRPO 開始。留意特定的症狀，也就是長 CoT 上 entropy 崩塌、長度與 reward 相關，或 MoE 不穩定，然後才換成上面對應的變體。在基本做法實際出現失敗模式之前，不要預先選定變體。

## VLM RL 僅供參考

Vision-language RL **在 v1 中這個 plugin 不會執行**，這裡記錄是為了提供脈絡，不是一條可以直接跑的路徑。工具鏈分散在 ms-swift 和衍生自 EasyR1 的 fork 之間，還沒有一行指令的 TRL 做法，而且把單純文字的 GRPO 套用到 VLM，很容易 reward hacking：模型最佳化文字推理的 trace 而忽略圖片，學到的是聽起來正確，卻沒有真的看輸入。VLM RL 是這個 skill 支援的做法之外的研究性嘗試，不是上面「做法」的一個變體。

## 參考資料

- `references/reward-functions.md`：完整的 Python reward function（exact-match 正確性、schema 驗證、unit test 執行、length-penalty 包裝，以及 rubric-as-reward 的 judge 模式），在任何訓練之前依「檢視規則」來檢視。
- `references/grpo-memory.md`：依目標大小級距的記憶體估算、vLLM sleep-mode 和 optimizer-state 的技巧、Unsloth 的長 context RL chunking，以及 decode 量大的 rollout 在 DGX Spark 上的頻寬注意事項。

相關 skill：一旦存在可驗證的 pass/fail 訊號，`finetuning-method-selection` 就會導到這裡；`preference-optimization` 是處理偏好配對（而非可驗證 reward）的姊妹 skill；`eval-harness-first` 涵蓋任何不是純粹靠程式碼檢查的 reward 所需的 judge 校準。在 DGX Spark 上，如果裝了 `dgx-spark-ops` plugin，這個 skill 的記憶體表沒涵蓋到的記憶體/散熱補救階梯，就交給它的 skill 處理。
