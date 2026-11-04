---
name: quantized-export
description: 把通過晉升的微調模型匯出成正確的部署格式：merged safetensors、僅 LoRA、帶 imatrix 的 GGUF 或 FP8。在 checkpoint 通過晉升之後、替目標裝置挑選量化格式，或匯出的模型 smoke test 失敗時使用。
---

# Quantized Export

這是 `checkpoint-promotion` 交出 `PROMOTE` 判定之後的最後一站：一個通過四階段關卡的 checkpoint，在匯出成目標 runtime 適用的格式、並證明匯出後仍然正常運作之前，都還算不上部署完成。`REJECT` 判定絕對到不了這個 skill，匯出只會從已晉升的 checkpoint 開始。

**Input：** 一個已晉升的 checkpoint（或 LoRA adapter），加上目標部署環境：GPU 等級、serving stack，以及長 context/程式碼/數學類工作負載是否在範圍內。
**Output format：** 一個選定格式的匯出產物，加上一份 smoke test 差異報告，比對 3–5 筆 golden 輸出在匯出前和匯出後的結果。

## Format Map

依硬體和部署型態選格式，不要憑習慣選。選錯的話，不是浪費吞吐量的空間，就是在特定工作負載上悄悄壞掉（見 Workload Overrides）。

- **Hopper 等級以上的 GPU，預設用 FP8。** 它能保持接近 bf16 的品質，記憶體大約減半。只要目標 GPU 支援，又沒有邊緣裝置的限制，這就是安全的首選。
- **AWQ INT4 是給比較舊的 GPU 用的**，也就是 FP8 硬體支援出現之前的那幾代。**GPTQ 在新部署裡已經被取代**，全新的匯出不要用它；同樣的位元寬度下，AWQ 的精度保留得更好，目前的工具支援也更廣。
- **帶 imatrix 建出來的 GGUF（Q4_K_M 量化），是邊緣/llama.cpp 用的格式。** 適合本機或接近 CPU 的部署，不適合追求 GPU serving 吞吐量。它優化的是體積，不是資料中心 GPU 上的 tokens/sec。
- **NVFP4 只給大規模的 Blackwell 部署用，而且明確不要用在 GB10 上。** 在 SM121（GB10）上，NVFP4 跑起來比 FP8 **慢大約 32%**，因為硬體缺少原生的 `cvt.e2m1x2` 路徑，除非 kernel 用 `sm_121a` 編譯。在 GB10 目標上選 NVFP4 是退步，不是升級，那裡請改選 FP8。
- **Merged 還是 LoRA-only，跟量化格式是不同的軸。** Merged 匯出會把 adapter 合併進 base weights：產物比較大，但 serve 時不需要依賴 base model。LoRA-only 把 adapter 分開放：產物小很多，但 serving stack 必須同時載入完全相同的 base model，base 錯了或 revision 不對，輸出會悄悄改變。產物可攜性比儲存空間重要時，選 merged；磁碟空間或多 adapter serving 比較重要時，選 LoRA-only。

### Worked Picks

格式選擇的核心取捨，整理成常見情境的查表：

| Target | Workload | Format |
|---|---|---|
| Datacenter GPU | generic chat | FP8 |
| Datacenter GPU | long-context/code/math | FP8 or W8A8 — never INT4 |
| Older GPU generation | generic | AWQ INT4 |
| Edge device / laptop | llama.cpp serving | GGUF Q4_K_M + imatrix |
| GB10 | any workload | FP8 via vLLM nightly, or GGUF via llama.cpp locally — skip NVFP4 |

```yaml
# quick decision snippet — see the table above for the full map
hopper_or_newer: fp8
older_gpu: awq-int4
edge_llama_cpp: gguf-q4_k_m+imatrix
gb10_any_workload: fp8-vllm-nightly   # never nvfp4 on GB10
```

## Workload Overrides

上面的 Format Map 只是預設值，不是每種工作負載都適用的規則。**長 context、程式碼和數學的工作負載，在 INT4 下會壞掉**：量化誤差會在長序列和精確的 token 層級推理中不斷累積，這在短的一般 prompt 上看不出來。這三類工作負載，就算目標硬體因為成本考量原本適合用 INT4，也**要留在 FP8 或 W8A8**。

- 不要用 MMLU 或類似的廣泛知識 benchmark 來驗證這個 override，它們測不到這種失效模式。**要用實際的任務評測來量**，也就是 `eval-harness-first` 的 golden 和 grader，拿匯出的產物去跑。因為 INT4 在長 context、程式碼或數學上的退化，會先以任務層級的失敗出現（context 掉了、語法壞了、算術錯了），遠早於知識 benchmark 的分數下降。
- 如果這三類工作負載之一在 INT4 匯出後，任務評測退步了，解法是換格式，不是重新調量化配方。同樣位元寬度的 AWQ 和 GPTQ 變體，在這些工作負載上有同樣的累積誤差失效模式。

## The Smoke Test

匯出的 bug 在檔案層級是無聲的。格式有問題的匯出一樣能產生可載入的產物，所以檢查檔案是否存在什麼都證明不了。**每一次匯出都一定要做 smoke test，就算是「應該沒問題」的格式也沒有例外：**

1. **在實際的目標 runtime 裡載入匯出的產物**：FP8/AWQ 用 vLLM，GGUF 用 llama.cpp。不要在跟正式 serving 不同的框架裡隨便載入看看。
2. **跑 3–5 筆 golden prompt**：從 `eval-harness-first` 維護的同一份 `eval/goldens.jsonl` 取，不要臨時另外挑一組。
3. **把每筆輸出跟匯出前同一個 prompt 的生成結果比對**，用同樣的確定性取樣設定：greedy decoding（temperature 0）加固定的 seed，而且要存下來，在匯出前和匯出後的兩次執行中重複使用，不能只是名義上設定一樣。**無損匯出的關卡是逐 byte 一致，任何差異都是 bug。** **有損**（量化）匯出就不可能逐 byte 一致；關卡改成任務 grader 的判定結果要一致，見 `references/export-commands.md` 的 Smoke-Test Script Skeleton。

這要當成關卡來跑，不是手動檢查：

```bash
python smoke_test.py "$EXPORT_PATH" \
    eval/goldens.jsonl pre-export-outputs.jsonl
# non-zero exit on any pre/post mismatch
```

### Failure Signatures

匯出 bug 實際長什麼樣子，不是一個乾淨的通過/失敗旗標：

- **Template 不一致**會表現成亂碼或一路接下去沒斷句的輸出：匯出時內建的 chat template，跟 checkpoint 訓練和評測時用的不一樣，所以輪次邊界或特殊 token 落在錯的位置。
- **`lm_head` 套錯量化**會表現成不符合 template 或語意上無意義，但讀起來仍然流暢的輸出：就算網路其他部分量化得很乾淨，輸出層還是損失了它需要的精度。

跳過這一步的匯出絕對不能出貨。checkpoint 的 `PROMOTE` 判定只說明「還沒匯出的 checkpoint」是好的，對匯出流程完全沒有保證。每次量化方法或 runtime 版本升級都要重跑，不是只有第一次匯出後才跑。每種格式可以直接跑的指令序列，以及 smoke test 腳本骨架，都在 `references/export-commands.md`。

## Related Skills

- `checkpoint-promotion` - 這個 skill 唯一合法的上游來源。沒有 `PROMOTE` 判定的 checkpoint 到不了匯出這一步。
- `eval-harness-first` - 擁有 `eval/goldens.jsonl`，這個 skill 的 smoke test 就是從這裡取 3–5 筆 prompt；也擁有 Workload Overrides 一節要求用來驗證長 context/程式碼/數學的任務評測。
- `finetuning-method-selection` - 它的 `references/model-catalog.md` 是用來確認硬體等級假設的地方（某個 base model 針對哪幾代 GPU），要在照上面 Format Map 選格式之前先查。

**Spark 使用者：** 在 GB10 上，GGUF 搭配 llama.cpp 很適合本機 serving，用 vLLM nightly build 做 FP8 serving 是另一條驗證過的路徑，NVFP4 則是唯一要避開的格式（見上面 Format Map 的例外）。裝好 `dgx-spark-ops` plugin 之後，Spark 專屬的 serving 和散熱問題就交給它的 skill，不要在這裡重新推導。
