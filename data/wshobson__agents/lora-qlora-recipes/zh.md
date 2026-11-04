---
name: lora-qlora-recipes
description: 用目前最佳實務的超參數設定 LoRA 與 QLoRA 監督式微調。在撰寫或審查 LoRA/QLoRA 訓練設定、選擇 rank/alpha/target modules，或在 LoRA、QLoRA 與全參數微調之間做決定時使用。
---

# LoRA & QLoRA Recipes

這個 skill 假設路由決策已經做完了：
`finetuning-method-selection` 應該已經把你導到這裡，
因為資料的形態是示範資料（SFT），
不是偏好配對，也不是可驗證的 reward 訊號。
接下來講的是設定 adapter 本身的
目前最佳實務配方：要鎖定哪些 module、
rank 和 alpha 怎麼定大小、learning rate 用多少，
以及 QLoRA 什麼時候真的能多出餘裕、
什麼時候只是多了風險。
資料集準備和品質檢查是另一回事，見
`dataset-curation`。

**輸入：** 一個路由決策（用 LoRA/
QLoRA 做 SFT）加上目標模型大小等級。
**輸出格式：** 一份驗證過的 adapter 設定，
也就是下面那些 kwarg 的值，不是自由發揮的建議，
`llm-finetuning-training-engineer` 在產生
可執行腳本時會直接使用它。

## The Reference Recipe

參考配方是「LoRA Without Regret」
（Thinking Machines/Schulman，2025-09），
現在已是 LoRA/QLoRA SFT 公認的慣例。

### Target Modules

要鎖定 **all-linear** 的 module，
不是只鎖 attention：

```python
target_modules = [
    "q_proj", "k_proj", "v_proj", "o_proj",   # attention
    "gate_proj", "up_proj", "down_proj",      # MLP — matters most
]
```

MLP 層（`gate_proj`、`up_proj`、
`down_proj`）影響最大，只鎖 attention 是
比較舊、效果也較差的慣例。為了省記憶體而
少鎖 module，是下面的 Failure
Mode，不是正當的最佳化。

### Alpha and Learning Rate

- **`lora_alpha = 2 * r`** 是公認的
  慣例（NeurIPS 2025「intruder dimensions」
  的結果）。不要脫離 rank 單獨手動調 alpha，
  每次都從 rank 推出來。
- **LoRA 的 learning rate ≈ 對應全參數微調 LR 的
  10 倍。** 以 QLoRA 來說，
  **2e-4** 是標準的起點。完整的
  超參數表和範例：
  `references/hyperparameters.md`。

### Rank by Task

Rank 要看任務決定，沒有單一的全域預設值：

| Task | Rank |
|---|---|
| RL (GRPO/RLVR adapters) | 1–32 |
| General default | 16–32 |
| SFT at scale | up to ~256 |

Rank 越高不代表越好，它提高泛化能力的同時，
也一樣提高死背的能力。從符合任務的那一列開始，
只有在較低的 rank 在 held-out eval 上
明顯欠擬合時才往上一列，不要把它當成預設的保險。

### Effective Batch Size

**Effective batch size 要維持在 32 以下。**
這個配方是在那個規模下驗證的，
把 effective batch 拉更高是沒驗證過的外推，
不是白賺的吞吐量。

## Unsloth Defaults

Unsloth 是這個 plugin 預設的快速路徑參考實作，
但有一個例外：messages 形態的對話式 SFT 搭配
`assistant_only_loss=True` 時，Unsloth
2026.7.x 編譯過的 trainer 根本沒有 messages 形態
的路徑，這個組合預設要走
純 TRL 的逃生口（`references/unsloth-trl-mapping.md`），
而不是罕見退化時才用的備案。
它的開箱即用預設值，以及每一個為什麼這樣設：

- **`lora_dropout=0`**：最佳化過的 kernel
  路徑假設 dropout 是零，設成非零
  就會失去 fused kernel 的加速。
- **`bias="none"`**：在這個 rank 範圍內，
  bias 項只會增加 adapter 參數，
  品質提升微乎其微。
- **`use_gradient_checkpointing="unsloth"`**：
  Unsloth 版本的 checkpointing，不是原版 HF
  的 checkpointing，比完全不用 checkpointing
  大約省 **30% VRAM**。
- **`optim="adamw_8bit"`**：8-bit AdamW 能降低
  optimizer state 的記憶體，在 LoRA/QLoRA
  adapter 的規模下對品質影響可忽略。
- **`random_state`** 固定：把 LoRA 的初始化
  釘死，讓不同次執行可以重現，
  要當成一般的 seed 看待，不是可以調的參數。

這些會一起出現在 `get_peft_model`
的呼叫裡：

```python
model = FastLanguageModel.get_peft_model(
    model,
    r=32,
    target_modules=target_modules,
    lora_alpha=64,               # 2 * r
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)
```

確切的 kwarg 名稱和它們在純 TRL/PEFT 的對應寫法，
以及包含 `SFTConfig` 的完整範例設定：
`references/unsloth-trl-mapping.md`
和 `references/hyperparameters.md`。

## LoRA vs QLoRA vs Full FT

| Situation | Default choice |
|---|---|
| Adapting behavior on demonstrations | LoRA |
| Base model doesn't fit in bf16 at target rank | QLoRA |
| Injecting dense new domain knowledge | Full FT (see `finetuning-method-selection`) |
| Unsure which one | LoRA — upgrade to QLoRA only if memory forces it |

- **QLoRA** = NF4 量化的凍結 base 權重 +
  BF16 adapter。這讓 65B 等級的
  模型能在 48GB 上訓練，省記憶體的是
  量化過的 base，不是 adapter 本身。
- **全參數微調不是預設。** 只留給大量灌入新知識的情況，
  也就是目標是在權重層級改變模型知道什麼，
  不是調整某種行為。
  在這個 skill 的範圍內，其他所有情況都以
  LoRA 或 QLoRA 為起始假設。
- **在 DGX Spark 上，QLoRA 可能比
  同等的 bf16 LoRA 更早 OOM**，即使
  QLoRA 穩態的記憶體用量比較小，
  因為 bitsandbytes 的反量化 buffer 是
  CUDA 端的暫時性配置，會在載入時暴衝。
  QLoRA OOM 不代表模型放不下，
  `dgx-spark-ops` plugin 的
  `spark-memory-thermal-ops` skill 涵蓋完整的
  OOM 處理階梯（下一步該試的是 bf16 LoRA，
  不是把 QLoRA 再縮小）。

## Failure Modes

- **在不支援 BF16 的 GPU 上 fp16 發散。**
  在沒有穩定 BF16 支援的硬體上用 fp16 訓練，
  是 loss 暴衝和無聲發散的已知來源。
  只要硬體支援，就強制用 `bf16=True`，
  不要把 fp16 當成等價的退路。
  選 dtype 前先確認硬體支援：

  ```bash
  python -c "import torch; print(torch.cuda.is_bf16_supported())"
  ```

- **小資料集用太高的 rank 會 overfit。**
  為「大規模 SFT」挑的 rank（最高約 256），
  用在沒有那種規模的資料集上，
  只會死背不會泛化。要依上面的 Rank by Task
  表挑 rank，不要挑最大的數字。
- **為了省記憶體拿掉 target modules，
  省不了多少卻傷害品質。**
  `gate_proj`/`up_proj`/`down_proj` 上的 adapter
  參數只占模型總大小的一小部分，
  砍掉它們幾乎不會改變記憶體用量，卻會明顯傷害品質。
  如果記憶體吃緊，先改用 QLoRA，
  或降低 rank/batch/pack 長度，再考慮縮減
  target modules。

這三個 failure mode 有個共通點：
它們看起來像訓練迴圈的 bug（loss 暴衝、
卡住不動、死背），其實是和上面參考配方
相牴觸的設定選擇。在直接除錯訓練迴圈之前，
先拿設定對照這個 skill。

## References

- `references/hyperparameters.md`：依任務類型整理的
  完整 rank/alpha/LR 表、rsLoRA 備註、
  batch/packing 的交互影響，
  以及一份完整的 Unsloth 範例設定。
- `references/unsloth-trl-mapping.md`：每個
  Unsloth kwarg 對應到 TRL/PEFT 的
  寫法、目前 TRL API 的備註，
  以及何時該退回純 TRL 的逃生口規則。

相關 skill：`finetuning-method-selection`
會導向這裡；`dataset-curation` 涵蓋
這個 skill 沒講的資料面；`llm-finetuning-training-engineer`
是這個 skill 產出的設定的下游使用者。
