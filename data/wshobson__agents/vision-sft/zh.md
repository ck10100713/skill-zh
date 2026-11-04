---
name: vision-sft
description: 用監督式學習，在圖片加文字的資料上微調視覺語言模型（VLM）。要把 VLM 調整到某個視覺領域或任務、設定凍結 vision tower 的 LoRA，或除錯「有在訓練但沒學到東西」的 VLM 微調時使用。
---

# Vision-Language SFT

這個 skill 假設 `finetuning-method-selection` 已經把你導到這裡：資料型態是圖片加文字的示範資料，不是偏好配對或可驗證的 reward 訊號，而且 base 是視覺語言模型，不是純文字模型。`lora-qlora-recipes` 涵蓋純文字的 LoRA/QLoRA 做法，這個 skill 是針對 vision tower 和 projector 把那套做法特化；如果你對 LoRA 的基本概念（rank、alpha、target modules）還不熟，先讀那個 skill。

**Input：** 一份圖片加文字的資料集，以及已經從模型目錄選好的 VLM base model。
**Output format：** 一份驗證過的 adapter 設定，包含哪些元件要凍結、LoRA 的 target modules，以及 `min_pixels`/`max_pixels` 預算。`llm-finetuning-training-engineer` 在產生可執行的腳本時會直接使用它。

## Quick Reference

| Situation | Default |
|---|---|
| 在熟悉的圖片上調整行為 | 凍結 tower+projector，LoRA r=8–16, α=16–32 |
| 視覺領域轉移 | 解凍最後 6 層 ViT，vision LR 低 5–10 倍 |
| 在目標 rank 下 bf16 放不下 | QLoRA，而且只能搭配凍結的 vision tower |
| `fast_inference=True` | `finetune_vision_layers=False` |
| Loss 正常，但 eval 沒進步 | 先檢查下面的 Two Silent Killers |

## The Consensus Recipe

凍結 vision tower 和 projector。只在 LLM 上加 LoRA，all-linear（跟純文字 SFT 一樣的 attention + MLP target 清單，見 `lora-qlora-recipes`），**r=8–16、α=16–32**。這是已經定案的預設值，用來調整 VLM 的行為，又不會干擾它看東西的方式。

- **Vision tower 和 projector 預設保持凍結。** 它們已經編碼了通用的視覺表示；重新訓練它們通常沒必要，而且對大多數任務來說只增加風險，沒有增加能力。
- **LoRA rank 比純文字的一般預設值低**（這裡是 r=8–16，純文字 SFT 是 r=16–32），因為只加在 LLM 的 adapter 是在調整行為，不是注入新的視覺知識。
- **QLoRA 只允許搭配凍結的 vision tower。** 量化 base 的同時又解凍並訓練 vision 層，是不支援而且不穩定的，把這當成硬性的搭配規則，不是可以調的參數。如果 vision tower 需要解凍，就放棄 QLoRA，改用 bf16 LoRA。

```python
# freeze tower + projector; LoRA on LLM only
for name, param in model.named_parameters():
    if "vision_tower" in name or "projector" in name:
        param.requires_grad = False

target_modules = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]  # LLM-only, all-linear — r=8-16, alpha=16-32
```

## When to Unfreeze

解凍 vision 層是刻意的升級，不是預設決定。只有在領域轉移發生在視覺面、不是文字面的時候才這樣做。

- **只在視覺領域轉移時才解凍。** 如果任務是在 tower 已經看得懂的圖片（圖表、日常照片）上教新行為，上面凍結 tower 的做法就夠了。當視覺領域本身是 tower 不熟悉的（衛星影像、醫學掃描、密集的技術圖），而且凍結 tower 的做法遇到瓶頸時，才解凍。
- **解凍最後 6 層 ViT 是最佳甜蜜點。** 解凍最後六層 vision-transformer（不是整個 tower），比凍結的 baseline 在 DocVQA 上測得 **+1.7pt，訓練成本約 1.75 倍**。把六層當成值得付出的上限；再往上就是花算力卻換不到對應的結果。
- **解凍時，vision LR 必須比 LLM LR 低 5–10 倍。** Vision tower 預訓練出來的表示，比 LLM 的 adapter 更脆弱；兩邊用同一個 LR，可能在 LLM adapter 來得及補償之前，就先把視覺表示覆寫掉了。
- **在 patch-embedding 層用高 LoRA rank 有 NaN 風險。** 如果 patch embedding 在解凍的範圍裡，rank 要設低，並密切觀察最早幾個 step 的 loss，這是 VLM 裡最脆弱、最需要小心套 LoRA 的地方之一。

## The Two Silent Killers

這兩個都會造成「訓練沒報錯、但也沒學到東西」的 run：loss 曲線看起來正常，模型卻沒進步，兩者都不會丟出例外，所以都需要在訓練前明確檢查，光看乾淨的訓練 log 不夠。

- **Image-tag/count mismatch。** 套用模板的文字中，每個圖片 placeholder token，都必須一對一對應到實際傳給 collator 的一個媒體項目。不一致（一個 placeholder 卻附上零張或兩張圖；或有圖卻沒有 placeholder）在大多數 collator 裡不會報錯，只會悄悄讓圖片和文字錯位，模型就「有在訓練但什麼都沒學到」。訓練開始前，要對每一筆範例（不是只抽樣）驗證 placeholder 對媒體的一對一對應。完整的驗證檢查清單細節：`references/collators-and-pitfalls.md`。
- **`min_pixels`/`max_pixels` 解析度預算。** 這一組是 VLM SFT 裡對品質和記憶體影響最大的單一超參數，比 rank、alpha 或 LR 都重要。設太低，會悄悄把圖片降到任務需要的解析度以下（文件上的小字變得看不清楚，訓練卻「成功」了）；設太高，會爆掉 activation 記憶體預算，或逼得 batch 太小而訓練不穩。要針對每個資料集刻意設定，不要留在框架的預設值。

## Unsloth Specifics

- **`UnslothVisionDataCollator`** 是 Unsloth 做 VLM SFT 預期要用的 collator，它處理 `references/collators-and-pitfalls.md` 裡描述的圖片 tag 對齊，以及各架構 processor 的規約。不要拿純文字的 collator 來處理 VLM 資料。
- **`fast_inference=True` 時，`finetune_vision_layers=False` 是必要的。** vLLM 無法 serve 掛在 vision 層上的 LoRA adapter，所以即使訓練成功，只要 fast-inference 設定同時解凍了 vision 層，serve 時就會失敗。如果做法要求解凍最後 6 層 ViT（見上面的 When to Unfreeze），這次 run 就不能用 fast inference，兩者二選一，不能兼得。

## Model Choice

Base VLM 的選擇不在這個 skill 的範圍內，它只放在一個地方：`finetuning-method-selection` 的 `references/model-catalog.md` 模型目錄。這個 skill 和它的 references 只依架構家族描述做法，絕對不會推薦哪個模型勝過另一個。

VLM 強化學習（VLM-GRPO）在這個 plugin 裡只有參考資料：VLM-RL 特有的零散工具鏈和 reward hacking 失敗模式，是在 `grpo-rlvr-training` 裡講，不在這裡。這個 skill 的範圍只到監督式微調為止。

## Failure Modes

上面每個章節一再出現的錯誤，就是把乾淨的 loss 曲線當成 run 很健康的證明。看起來正常的曲線，**既**符合正常運作的 run，**也**符合任何一個 silent killer，因為不管怎樣模型都在訓練「某些東西」，只是有 killer 的時候，訓練的不是對齊好的圖文訊號。Loss 曲線正常、eval 分數卻持平，意思是在動任何超參數之前，先重跑 `references/collators-and-pitfalls.md` 裡的檢查清單。

## References

- `references/collators-and-pitfalls.md` — 各架構的 collator 對照表、帶圖片 placeholder 的資料集格式範例、訓練前驗證檢查清單，以及作為進階模式的兩階段 projector 對齊做法。

相關的 skill：`finetuning-method-selection` 會把你導到這裡；`lora-qlora-recipes` 涵蓋這個 skill 所特化的純文字 LoRA 基本概念；`grpo-rlvr-training` 涵蓋 VLM-RL（僅供參考）；`dataset-curation` 涵蓋這個 skill 沒有處理的圖文資料集準備。
