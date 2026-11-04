---
name: spark-memory-thermal-ops
description: 在 NVIDIA DGX Spark 上跑長時間 ML 任務時，管理統一記憶體和散熱。在規劃 GB10 上訓練執行的記憶體餘裕、任務在統一記憶體上 OOM，或監控數小時訓練期間的溫度和功耗時使用。
---

# Spark Memory & Thermal Ops

DGX Spark 的 GB10 晶片只有一個 128GB 的統一記憶體（UMA）池，由 CPU 和 GPU 共用，而且持續功耗的上限遠低於它的額定值。這兩點都打破了獨立 GPU 的假設：餘裕不是 `nvidia-smi` 回報的那樣，而且一個一開始很快的任務，會在執行到一半時變慢，卻沒有任何東西設定錯誤。這個 skill 涵蓋規劃記憶體餘裕、處理真正發生的 OOM，以及在長時間任務中監看散熱。啟動時的失敗模式（ABI 不匹配、flash-attn、playbook 損壞），請看 `spark-training-gotchas`，這個 skill 假設任務已經成功啟動。

## Common Issues Quick Reference

| Situation | Do this |
|---|---|
| Planning headroom before launch | Budget against `free -g`, not `nvidia-smi` — see UMA Memory Model |
| Job OOMs on unified memory | Work the OOM Ladder in order: flush, then batch/pack, then method downgrade |
| Throughput drops mid-run | Check the power/temp log before assuming a config bug — see Thermal Monitoring |
| Trainer + inference server both wanted | Run one at a time — see Concurrent Workloads |

## When to Use This Skill

- 在啟動前，對照 128GB 的記憶體池估算訓練執行的大小：這個模型、方法，加上 batch/packing 的組合放不放得下。
- 執行在載入中途或某個 step 中途 OOM，而處理的順序很重要：第一步、第二步、第三步該試什麼。
- 在數小時的任務期間監看溫度和功耗，判斷變慢是散熱降頻，還是別的原因。
- 打算在同一台機器上，同時跑 trainer 和推論伺服器（vLLM、Ollama）。

## UMA Memory Model

Spark 沒有獨立的 GPU VRAM，GPU 和 CPU 共用同一個 128GB 的記憶體池。這帶來兩個結果：

- **`nvidia-smi` 和 `cudaMemGetInfo` 會低估壓力，甚至什麼都不回報。** 兩者回報的都是 CUDA allocator 看得到的記憶體，不是記憶體池實際的狀態。一台機器可以在 `nvidia-smi` 裡顯示還有餘裕，卻照樣 OOM，因為 page cache 和 allocator 看不到的 mmap 頁面，消耗的是同一個記憶體池。在某些 driver/環境下，記憶體查詢會直接回傳 `[N/A], [N/A]` 而不是數字，腳本如果去 grep 數值，什麼都拿不到，而不是一個會誤導人的低估值（見 `spark-training-gotchas` 的 gotcha G3）。

- **模型載入是暫時的尖峰，不是穩定狀態。** 載入 safetensors 權重時，會先 mmap 這個檔案，再複製進 CUDA tensor。在載入期間的一段時間內，mmap 的頁面和 CUDA 的副本會同時算在記憶體池裡。如果餘裕是依載入後的用量來估，而不是這個加倍的暫時尖峰，一個訓練時放得下的模型，還是可能在載入時 OOM。

規劃和診斷要用 `free -g`，不要用 `nvidia-smi`：

```bash
free -g | awk 'NR==2 {print "free:", $4, "GB"}'
```

經驗法則：取那個 free 的數字，扣掉幾 GB 給 OS/driver 的開銷，然後對照結果來抓預算，不要對照 128GB 的規格數字。`references/uma-accounting.md` 裡的試算表接受參數量、dtype 和方法當輸入，回傳一個記憶體估算值，用來對照已知的基準點。

### Planning Sequence

啟動前，依序處理這些：

1. 讀取 `free -g`；扣掉 OS/driver 的開銷，得出預算。
2. 從 `references/uma-accounting.md` 估算權重 + optimizer + 梯度 + activation。
3. 對照最接近的基準點（70B QLoRA、27B LoRA、9B 全量微調），不要只看估算值。
4. 如果估算值很接近預算，一開始就用比較短的 packing 或比較小的 batch，這比在執行到一半撞上 OOM Ladder 便宜。

### Example: Sizing a 70B QLoRA Run

用試算表的公式，對照 ≈40GB 的基準點做健全性檢查：

```python
params = 70e9
weights_gb = params * 0.5 / 1e9      # NF4, step 1
adapter_gb = 0.5                     # step 5, negligible
total_gb = weights_gb + adapter_gb   # + activations
print(f"{total_gb:.0f}GB before activations")
```

光是權重就落在 ≈40GB 的基準點附近。同一類模型，如果計畫估出來遠高於這個數字，就是該重新檢查 dtype 和方法的訊號。

## The OOM Ladder

任務在統一記憶體上 OOM 時，依序處理這個階梯。每一步都比前一步更有破壞性，不要跳著做：**縮小 batch size 絕對不是第 1 步。**

1. **清掉 buffer cache。** 先前執行留下的 page cache，或是讀取大型資料集的 page cache，常常佔掉好幾 GB「不見的」餘裕。這一步只需要重跑一次，不會動到任務的設定：

   ```bash
   sync; echo 3 > /proc/sys/vm/drop_caches
   ```

   需要 root；這是兩次執行之間的重置，不是訓練中途的步驟。這一步背後完整的診斷，請看 `spark-training-gotchas`（gotcha G3）。

2. **縮小 batch size 或 packing 長度。** 只有在清掉 cache 後仍騰不出足夠餘裕時，才縮小 batch size 或 packing 長度，這是第一個會改變執行內容的步驟。優先縮 packing 長度，在長 context 下，它對 activation 用量的影響更直接。

3. **降級方法：先試 bf16 LoRA，再來才是 QLoRA。** 如果清掉 cache、縮小 batch/pack 後仍然 OOM，就把方法降一級，下一步是 bf16 LoRA，不是反過來。QLoRA 的 bitsandbytes 反量化緩衝區是暫時性的 CUDA 端配置，可能比同等的 bf16 LoRA 執行更早 OOM，雖然 QLoRA 的穩定狀態用量比較小。QLoRA 發生 OOM，不代表這個模型放不下。

三步都做完、任務還是放不下，才往下退（換更小的模型、多台 Spark）。

## Thermal Monitoring

數小時的執行會頂到 Spark 的持續功耗上限，遠低於額定值，這是平台預期中的行為，不是該拿來硬找理由解釋的症狀：

- 溫度和功耗要跟著訓練 log 一起取樣，不要等發現變慢之後才取樣。每 30-60 秒一次，就能把吞吐量的下降跟散熱事件對應起來。保留 `assets/thermal-sample.sh` 寫出的 CSV 輸出格式，這樣時間戳記才能跟 log 對得上：

  ```bash
  bash assets/thermal-sample.sh 30 thermal.log
  ```

- **持續約 100W 的功耗是平台的上限，不是設定的 bug。** 不要為了「修好」一個高原期而重新調整 batch size 或精度，那是機器在負載下的正常行為。如果溫度持續攀升，功耗卻停留在額定的 240W 以下，那就是要認出來的特徵。

- 要明確記錄降頻事件，不要讓執行悄悄變慢卻沒留下紀錄。一個執行兩小時後每個 step 的時間翻倍，應該在 log 裡看得到，並對照該時間戳記的散熱取樣。完整的降頻診斷：`spark-training-gotchas`（gotcha G4）。

## Concurrent Workloads

因為 128GB 的記憶體池是全域的，被驅逐（eviction）發生時，兩個行程的 log 都不會顯示 OOM：

- 「一次只跑一個重量級任務」這條規則，適用於**沒有上限或接近滿載**的工作負載：沒設上限的 trainer 和推論伺服器（vLLM、Ollama）會競爭同一個記憶體池。小型、有設上限的工作負載就不會：一個 <4GB 的 LoRA 微調，可以跟 `gpu-memory-utilization<=0.5` 的 vLLM 並存，所以在停掉另一個行程之前，要檢查的是它的上限，不是只看它有沒有在跑。

- 在沒有上限/接近滿載的競爭下，推論伺服器會悄悄驅逐 trainer 的頁面，反過來也一樣，兩邊都不會記錄錯誤，所以執行變慢或 KV cache 不見了，是要檢查的競爭症狀。在長時間或吃滿整個記憶體池的執行之前，先停掉不相關、*沒有上限*的伺服器。

先檢查有哪些佔用 GPU 的行程：

```bash
ps aux | grep -E 'vllm|ollama|trl|axolotl' | grep -v grep
```

這個流程是 `spark-training-gotchas`（gotcha G3、G4、G6）的補充，那個 skill 處理的是啟動時的失敗；這個處理的是執行中的任務。

記憶體試算表：`references/uma-accounting.md`。
