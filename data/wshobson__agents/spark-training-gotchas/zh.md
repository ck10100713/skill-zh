---
name: spark-training-gotchas
description: 預先檢查並診斷在 NVIDIA DGX Spark 上做 ML 訓練時已知的十種失敗模式。在 DGX Spark 上的訓練執行啟動失敗、在低於 128GB 上限時就 OOM、執行到一半變慢，或是在 GB10 上開跑任何數小時的訓練任務之前使用。
---

# Spark Training Gotchas

DGX Spark 的 GB10 晶片（Grace Blackwell、SM121、128GB 統一記憶體、aarch64）在啟動、記憶體、散熱、頻寬和精度方面，有十種反覆出現的失敗模式。每一種都命名為 G1–G10，方便用編號來檢查，這個編號是關鍵，因為執行這些檢查的工具都依賴它。要在長時間執行之前讀這個，不要等到第六個小時之後才讀。

## When to Use This Skill

- 訓練執行啟動失敗，出現 import 錯誤或 segfault，卻沒有指向真正的原因。
- 執行 OOM，但 `nvidia-smi` 還顯示有餘裕。
- 一開始跑得好好的執行，在中途吞吐量下降。
- 在 GB10 上開跑任何數小時或多個 epoch 的任務之前。
- 把兩台 Spark 串在一起，要在選定平行化策略之前。
- 為 Spark 上的執行在 FP8 和 NVFP4 之間做選擇。

## Common Issues Quick Reference

| # | Symptom | Fix |
|---|---|---|
| G1 | undefined symbol / segfault | cu130 wheel or container |
| G2 | flash-attn wrong backend used | skip pip build; monkeypatch on NGC |
| G3 | OOM despite headroom | drop page cache |
| G4 | throughput drop / reboot | expect ~100W sustained cap |
| G5 | memory-bound step slow | budget 180–192 GB/s |
| G6 | cache evicted mid-run | one GPU server at a time |
| G7 | NVFP4 slower than FP8 | stay FP8 unless `sm_121a` |
| G8 | playbook fails outright | check upstream issues |
| G9 | env breaks after install | use a container |
| G10 | 2-Spark TP hangs | DDP/FSDP only, never TP |

## The Ten Gotchas

### G1: CUDA 12/13 ABI Mismatch

- **SYMPTOM：** `ImportError: undefined symbol`，指出某個 CUDA 函式，或在第一次呼叫 `.cuda()` 時 segfault。
- **CAUSE：** 大多數 PyPI wheel 連結的是 `libcudart.so.12`；Spark 搭載的是 CUDA 13。pip 從不檢查 CUDA ABI，所以只有在 import 或第一次啟動 kernel 時才會浮現。
- **CHECK：** `references/gotcha-checks.md` G1，也就是 wheel 的 CUDA build 標籤。
- **FIX：** 從 `download.pytorch.org/whl/cu130` 重新安裝，或使用匹配的 container。

### G2: flash-attn — Skip the pip Build, Watch Unsloth's Auto-Detect

- **SYMPTOM：** `pip install flash-attn` 仍然失敗/卡住。Unsloth 也可能在你明確要求 SDPA 的情況下，悄悄改用 flash-attn 來訓練。
- **CAUSE：** 直接用 pip 沒有 aarch64/sm_121 的 wheel，不過 NGC container 附有能用的 SM121 flash-attn，而且 Unsloth 會自動優先選它，把 `attn_implementation="sdpa"` 丟掉。
- **CHECK：** `references/gotcha-checks.md` G2，也就是 flash-attn 是否已存在而且能用。
- **FIX：** 直接用 pip：跳過 flash-attn，用 SDPA（不變）。在 NGC 上：唯一可靠的覆寫方式，是 `references/gotcha-checks.md` G2 裡的 monkeypatch。

### G3: UMA OOM Below 128GB

- **SYMPTOM：** 在模型載入/訓練期間 OOM，而 `nvidia-smi` 仍然回報低於 128GB 上限的可用記憶體，或是在某些環境下，直接回報 `[N/A]` 而不是數字。
- **CAUSE：** 載入 safetensors 時，mmap 和 CUDA allocator 會重複計算頁面；QLoRA 可能比 bf16 *更早* OOM，因為反量化會增加暫時性的配置。
- **CHECK：** `references/gotcha-checks.md` G3，讀取 `free -g` 和 `/proc/meminfo`，不要讀 `nvidia-smi`。
- **FIX：** 用 `sync; echo 3 > /proc/sys/vm/drop_caches` 清掉 page cache。需要 root，這是兩次執行之間的重置，不是訓練中途的步驟。

### G4: Thermal Throttling

- **SYMPTOM：** 數小時的執行中途吞吐量下降，或是機器在持續負載下自己重新開機。
- **CAUSE：** 持續功耗的上限大約是 100W，相對於額定的 240W；長時間執行會頂到這個天花板，然後降頻，有時甚至重新開機。
- **CHECK：** `references/gotcha-checks.md` G4，取樣 `nvidia-smi --query-gpu=temperature.gpu,power.draw`。
- **FIX：** 如果功耗在 240W 以下停滯、溫度卻持續攀升，就把降頻視為原因；改善散熱，或限制執行的長度。

### G5: Bandwidth Ceiling

- **SYMPTOM：** 受記憶體頻寬限制的工作負載，尤其是以 decode 為主的 RL 迴圈，停在遠低於預期的吞吐量。
- **CAUSE：** 273 GB/s 是規格上的天花板，不是持續的值；實測的頻寬落在 180–192 GB/s。
- **CHECK：** `references/gotcha-checks.md` G5，觀察到的 step 時間對照實測範圍，不要對照規格。
- **FIX：** 以 180–192 GB/s 來估算吞吐量預算；修訂建立在 273 GB/s 這個數字上的計畫。

### G6: Global UMA Resource Contention

- **SYMPTOM：** 某個行程的 KV cache/權重在執行中途被悄悄驅逐，它自己的 log 裡沒有 OOM。
- **CAUSE：** 統一記憶體是一個全域的記憶體池；沒有上限或接近滿載的行程，會跟其他任何東西競爭，並可能把對方驅逐。小型、有界限的工作負載就不會，一個 <4GB 的 LoRA，可以跟 `gpu-memory-utilization<=0.5` 的 vLLM 並存。
- **CHECK：** `references/gotcha-checks.md` G6，其他佔用 GPU 的行程，以及它們有沒有設上限。
- **FIX：** 「一次只跑一個重量級任務」的規則，適用於**沒有上限或接近滿載**的工作負載，先限制上限或停掉不相關的伺服器。小型、有設上限的工作負載不需要停。

### G7: NVFP4 Slower Than FP8 on SM121

- **SYMPTOM：** 在 Spark 上把推論工作負載從 FP8 換成 NVFP4，反而變慢，不是變快。
- **CAUSE：** 除非 kernel 以 `sm_121a` 為目標，否則 SM121 缺少 `cvt.e2m1x2`；沒有它，NVFP4 會慢大約 32%。
- **CHECK：** `references/gotcha-checks.md` G7，capability 回報 `(12, 1)`；build 是否以 `sm_121a` 為目標？
- **FIX：** 除非 build 以 `sm_121a` 為目標，否則留在 FP8。

### G8: Stale Official Playbooks

- **SYMPTOM：** 照著官方的 DGX Spark playbook 做，仍然失敗，本地也沒有任何設定錯誤能解釋。
- **CAUSE：** 官方的 playbook 以前就出過壞掉的情況；整個 stack 的變動速度比文件快。
- **CHECK：** `references/gotcha-checks.md` G8，playbook repo 最近的 issue。
- **FIX：** 在為昂貴的執行相信某個做法之前，先檢查 `github.com/NVIDIA/dgx-spark-playbooks` 的 issue。

### G9: Container-First, Not Bare Pip

- **SYMPTOM：** 昨天還能用的直接 pip 環境，在一次不相關的 `pip install` 之後壞掉，或是兩個「一模一樣」的環境行為不同。
- **CAUSE：** 直接用 pip，會讓 Triton、xformers 和 transformers 各自獨立漂移；沒有任何東西把它們釘在 GB10 的 SM121 目標上。
- **CHECK：** `references/gotcha-checks.md` G9，是 container 還是直接用 pip？
- **FIX：** 偏好 NGC container（tag 的指引請看 `spark-environment-setup`）或 Unsloth 的 container。如果無法避免直接用 pip，就照 NVIDIA 的安裝順序，包含對 Unsloth 使用 `--no-deps`。

### G10: Dual-Spark Is DDP/FSDP Only

- **SYMPTOM：** 跨兩台 Spark 的 tensor-parallel 啟動卡住、比單台 Spark 慢很多，或直接報錯。
- **CAUSE：** ConnectX-7 的速度足以應付梯度/參數同步（DDP、FSDP），但對 TP 細粒度的流量來說太窄了。
- **CHECK：** `references/gotcha-checks.md` G10，設定的平行化策略。
- **FIX：** 在兩台 Spark 的環境，選 DDP 或 FSDP，絕對不要用 tensor parallelism，在這裡 TP 只能用於單節點。

## Fast Triage

在做其他任何事之前，最便宜的檢查：

```bash
python3 -c "import torch; print(torch.version.cuda)"  # expect 13.x (G1); NGC builds have no +cu130 tag — that's not a failure
```

```python
import torch; print(torch.cuda.get_device_capability())  # expect (12, 1) (G7)
```

```bash
{ [ -f /.dockerenv -o -f /run/.containerenv ] || grep -qE 'docker|containerd' /proc/1/cgroup; } 2>/dev/null && echo container || echo unknown  # G9
```

`assets/preflight.sh` 會執行 G1、G3、G4、G7、G9，並且每個 gotcha 輸出一行固定格式的結果：G 編號在最前面，接著是可自動化時的 PASS/FAIL/WARN、無法取得時的 SKIP，或是原始讀數時的 `INFO:`（G3、G4）。完整指令請看 `references/gotcha-checks.md`。另外請看 `spark-environment-setup`，了解這裡假設已經能用的環境。
