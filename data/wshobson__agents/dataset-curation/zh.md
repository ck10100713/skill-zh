---
name: dataset-curation
description: 為監督式 fine-tuning 與偏好訓練準備、格式化並驗證資料集。適用於把原始資料轉成訓練格式、套用 chat template、設定 sequence packing、產生合成訓練資料，或在開跑前撰寫 dataset card 的時候。
---

# 資料集整理（Dataset Curation）

這個 skill 假設 `finetuning-method-selection` 已經把你導到這裡，所以下一步是準備資料，不是選方法。內容包含：依目標方法選格式、最常造成無聲訓練失敗的 template/packing 機制、混入合成資料又不會 collapse 的規則，以及在開跑前為 Phase 2 收尾的 dataset card。

**輸入：** 原始範例（示範資料、偏好判斷或任務 prompt），加上來自 `finetuning-method-selection` 的路由決定。
**輸出格式：** 一份格式化、packed、驗證過的 JSONL 資料集，加上填好的 dataset card，這是 `/finetune` 在啟動訓練前會檢查的 Phase 2 產出。

## 格式選擇

| 方法 | 形狀 | 筆數 |
|---|---|---|
| SFT，單輪 | Instruct（`instruction`/`response` 或 `prompt`/`completion`） | 底線約 1,000+ |
| SFT，多輪 | Conversation / ChatML `messages` 清單 | 底線約 1,000+ |
| DPO / ORPO | 偏好配對（`prompt`、`chosen`、`rejected`） | 依方法而定，見 `preference-optimization` |
| KTO | 非配對（`prompt`、`completion`、`label`） | 依方法而定，見 `preference-optimization` |
| GRPO / RLVR | 只有 prompt（`prompt` + verifier metadata） | 依方法而定，見 `grpo-rlvr-training` |

- **SFT 建議的底線是約 1,000+ 筆**，這不是目標。低於這個數量，少數低品質或重複的範例就會主導 gradient；超過之後就是**品質重於數量**，一份較小、驗證過又去重的資料集，勝過較大但雜訊多的資料集。
- 這是 ChatML 的形狀，供你參考；其他四種格式加上 ShareGPT 轉換說明放在 `references/formats-and-templates.md`：

  ```json
  {"messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]}
  ```

## Chat Template 與 Loss Masking

套用目標模型的 chat template 一定要在任何串接或 packing **之前**，絕對不能在之後。先把原始文字 pack 起來、再對整包 template，會弄壞 turn 邊界，role marker 會落在每個範例裡錯誤的位置。

- **只在 assistant 回應上訓練。** 對 system/user 的 turn 以及 template 自己的 role marker 做 loss mask（labels tensor 裡填 `-100`），只有 assistant turn 的內容 token 會計入 loss。
- **Template/tokenizer 不一致是最常見的無聲失敗之一。** 模型用某個 chat template 訓練，卻用另一個 template 來 serve 或評估，效果會變差但不會報錯。要確認訓練用的那個 template 字串，在 inference 和 eval 時也套用。
- **資料集維持 `messages` 形狀**，讓 trainer 去套 template 和做 mask（目前的 TRL 用 `assistant_only_loss=True`）。事先 render 成扁平的文字欄位，會毀掉 masking 需要的 turn 邊界。完整的程式碼草稿在 `references/formats-and-templates.md`。訓練前先做個檢查：只 decode 沒被 mask 的位置，預期只會看到 assistant 的文字：

  ```python
  keep = batch["labels"][0] != -100
  print(tokenizer.decode(batch["input_ids"][0][keep]))
  ```

## Packing

**不做 packing 的話，40–70% 的運算花在 padding 上**，因為長度不一的範例用固定 sequence 長度做 batch，每個範例長度和 batch 最大長度之間的空隙都浪費掉。Packing 把多個範例串進同一條 sequence，一直串到最大長度，可以省掉大部分的浪費。

- **Packing 會改變 batch 的語意。** 一條 packed sequence 可以包含好幾個原始範例，所以一打開 packing，「每個 epoch 的 step 數」和任何以範例數量為基準的 LR schedule 都會位移，要用 packed sequence 的數量重新計算 schedule 的里程碑。
- **一定要：在放大到完整訓練前，先 decode 並手動檢查 5–10 條 packed sequence。** 確認範例邊界落在預期的位置、每個子範例的 template marker 都完整，而且 loss mask 在每條 packed sequence 裡仍然只涵蓋 assistant。這不是選配，packing 的 bug 是無聲的（loss 曲線看起來正常），要到幾小時後看 eval 品質才會浮現：

  ```python
  for seq in packed_dataset.select(range(10)):
      print(tokenizer.decode(seq["input_ids"]))
  ```

## 合成資料規則

- **至少保留 25% 的真實資料當作 collapse 的防線。** 如果模型生成的資料占比越來越高、又沒有真實資料的底線，經過幾代之後品質會明顯 collapse，25% 真實資料是守得住的最低限度。**通用領域的 replay 資料筆數也算在這個底線內**，「真實」的意思是「不是為這個任務、由這個 student 生成的」，不是「人類寫的」。一份從頭到尾都是合成的資料集，只靠 replay 就能達到 ≥25% 的底線（見 `references/synthetic-data.md` 的 Replay-Mix Construction 做法），所以要在 dataset card 裡寫明哪些筆數算「真實」，不要讓這條底線在結構上永遠達不到。
- **Magpie 和 rejection sampling 是主力。** Magpie 從模型自己的 template prior 抽出 prompt；rejection sampling 對每個 prompt 生成多個候選，只留下通過 filter 的。兩者都勝過單純的一次生成。
- **針對 student 的目標式生成，樣本效率比靜態生成高 1.3–2 倍**，因為瞄準 student 實際的失敗模式，用比較少的過濾後範例就能達到品質門檻。
- **過濾後的典型通過率是 10–30%。** 量要據此規劃，目標 10,000 筆、通過率 15%，就需要約 65,000+ 筆原始生成。
- 生成方法排名、過濾漏斗、replay-mix 的建構方式和 distillation 模式都在 `references/synthetic-data.md`。

## Dataset Card

每個要進訓練的資料集都要有一張 card，這是 `/finetune` 啟動前會檢查的 Phase 2 必備產出。Card 不是隨便寫寫的文件，**一定要**包含這些欄位：

- **來源（Provenance）**：每一筆資料從哪來（真實來源、合成方法，或兩者都有），可追溯到 `trace-to-training-data` 的輸出。
- **數量（Counts）**：總筆數，以及有切分的話，每個 split（train/eval/held-out）的筆數。
- **合成/真實比例**：實測的比例，對照上面 ≥25% 的真實底線檢查。
- **去重方法**：exact-match、semantic（embedding 門檻），或兩者並用，參考 `references/synthetic-data.md` 的過濾漏斗。
- **使用的 template**：確切的 chat template 字串/識別碼，在 inference 和 eval 都要保持一致，這就是把 `eval-harness-first` 的一次執行綁回 checkpoint 的東西。
- **Packing 設定**：有沒有用 packing、最大 sequence 長度，以及確認上面那個 5–10 條 sequence 的手動檢查已經做過。

少了這六個欄位任何一個的資料集，都還沒準備好交給 `/finetune`。Card 是一道關卡，不是事後補寫的摘要。

### Phase 2 離場檢查表

交給 `/finetune` 之前，先確認：

1. 格式符合方法（上面的表）。
2. Template 在串接之前套用。
3. Loss 只 mask 到 assistant turn。
4. 5–10 條 packed sequence 已 decode 並讀過。
5. 最終混合資料中真實資料 ≥25%。
6. Dataset card 完整，六個欄位都有。

## 參考資料

- `references/formats-and-templates.md`：各格式的 JSONL 範例、目前 TRL 的 masking 程式碼，以及 ShareGPT 轉換說明。
- `references/synthetic-data.md`：生成方法排名、過濾漏斗、replay-mix 建構，以及 teacher→student 的 distillation 模式。

相關 skill：`finetuning-method-selection` 負責導到這裡；`lora-qlora-recipes`、`vision-sft` 和 `preference-optimization` 會使用這個 skill 產出的資料集；`trace-to-training-data` 是 graded-trajectory 資料集的來源追溯；`eval-harness-first` 負責對產出的 checkpoint 評分。
