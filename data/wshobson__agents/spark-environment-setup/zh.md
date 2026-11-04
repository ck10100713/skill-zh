---
name: spark-environment-setup
description: 在 NVIDIA DGX Spark（GB10、aarch64、CUDA 13）上建立可用的 ML 訓練/推論環境。在 DGX Spark 上安裝 PyTorch/Unsloth/TRL/vLLM、在 aarch64 上遇到 libcudart 或 wheel ABI 錯誤，或在 NGC container 和直接用 pip 安裝之間做選擇時使用。
---

# Spark Environment Setup

DGX Spark 搭載 GB10 Grace Blackwell 晶片：aarch64 CPU、SM121 GPU、128GB 統一記憶體、CUDA 13。這個平台比一般 x86 CUDA 12 的機器更窄也更新，所以套件的選擇和 ABI 的匹配比平常更重要，aarch64 + CUDA 13 的 wheel 生態系還在逐步補齊中。

## When to Use This Skill

- 為訓練或推論設定一台全新的 Spark 機器。
- 遇到提到 `libcudart`、缺少 symbol，或是「裝得好好的，但載入不了」的 wheel 的 import 錯誤。
- 框架安裝（PyTorch、Unsloth、TRL、vLLM、xformers）失敗、卡住，或悄悄退回用 CPU。
- 決定要用 NGC container 還是直接用 pip。
- 在 OS 重灌或 base image 更新之後，要從頭重新驗證，恢復可用的環境。

這些情況的解法大致相同：讓 container/wheel 的組合對應 CUDA 13 和 SM121，不要跟 ABI 對著幹。

## Container-First Rule

先講快速決策，再看下面的細節：

- 標準的訓練/推論工作 → NGC PyTorch container。
- 以 Unsloth 為中心的微調 → Unsloth container（它已經附上針對這條路徑驗證過、釘好版本的 Triton/xformers/transformers 組合）。
- 兩者都不適合（自訂的系統套件、本機 IDE 的直譯器）→ 直接用 pip，照下面的確切順序進行。

預設用 container。一般工作用 `nvcr.io/nvidia/pytorch:25.09-py3` 當 base，這是確認在這個硬體上能用的最新 tag；如果本機有更新的、被認可的 tag，就拉那個，不要卡死在 `25.11-py3`。NGC 的 tag 是有日期的，所以直接跑是沒問題的：

```bash
docker run --runtime=nvidia --gpus all -it --rm \
  nvcr.io/nvidia/pytorch:25.09-py3
```

相對地，`unsloth/unsloth:dgxspark-latest` 是會變動的 tag，要做任何需要可重現的事之前，先解析並釘住它的 digest；光用 tag 只是探索的步驟，不是預設的呼叫方式。完整的 pull、檢查、釘住的流程，以及 `finetuning/` 執行目錄的 flag 理由和 volume mount，請看 `references/container-workflow.md`。直接用 pip 是例外。

偏好 container 的原因是為了釘住版本，不是為了方便。Triton、xformers 和 transformers 的版本跟 GB10 的 SM121 目標和 CUDA 13 之間有很窄的互動關係；container 會把它們鎖在一起，對應到已在這個硬體上驗證過的組合。直接用 pip，這個解析工作就留給你自己做，一個壞掉的 import 接著一個。

確實需要直接用 pip 時，要原封不動、依序照 NVIDIA playbook 的安裝順序：

```bash
pip install "transformers==5.13.1" "peft==0.19.1" "hf_transfer==0.1.9" "datasets==4.3.0" "trl==1.8.0"
pip install --no-deps "unsloth==2026.7.2" "unsloth_zoo==2026.7.2" "bitsandbytes==0.49.2"
pip install -U "torchao==0.17.0"
```

第二個指令的 `--no-deps` 旗標不能省，在 aarch64 上讓 pip 重新解析 Unsloth 的依賴樹，是很常見會拉進不相容的 torch 或 triton 版本的原因。第三行也不能省：NGC base image 內建的 `torchao` 對目前的 `peft` 的 LoRA 掛載路徑來說太舊了（`ImportError: ... torchao ... only versions above 0.16.0 are supported`），這是硬性阻礙，不是警告。上面每一個 `==` 的版本釘選都是關鍵，取自 `references/stack-matrix.md` 裡標有日期、已知可用的版本矩陣（以它的 `Last verified` 日期判斷是否過期）。沒釘版本的安裝，會解析出目前 PyPI 上的版本，遠遠超出這個 Unsloth release 所支援的範圍。

有新的、被認可的 release 公布時，就拉新的 tag。只有在專案需要額外疊加一個系統套件時，才從這兩個 base 之一在本機重建，不要為了「升級」image 已經釘好版本的元件而重建。兩條路徑的細節請看 `references/container-workflow.md`。

還有一個前置檢查：官方的 DGX Spark playbook 以前就出過壞掉的情況。在照著某個做法一字不改地跑一次長時間的任務之前，先到 `github.com/NVIDIA/dgx-spark-playbooks`（以及 `references/stack-matrix.md` 裡的其他資源）檢查最近的 issue。

## The ABI Rule

在 Spark 上最常見的單一失敗原因，是 CUDA 12/13 的 ABI 不匹配：一個針對 `libcudart.so.12` 建出來的 wheel，被載入到只有 `libcudart.so.13` 的系統上。安裝通常會成功；失敗是後來才以缺少 symbol 的錯誤，或是不明顯指向 CUDA 的 segfault 浮現。

解法：從 `download.pytorch.org/whl/cu130`（有 cu130 標籤的 aarch64 build）拉 wheel，或使用上面那些 container 之一，它們已經帶有匹配的 build。在追查一個提到 CUDA symbol 的 stack trace 之前，先檢查已安裝的 wheel 是針對哪個 CUDA 標籤建出來的：

```bash
python3 -c "import torch; print(torch.version.cuda)"
```

如果輸出不是以 `13` 開頭，那麼要先修的就是 ABI 不匹配。NGC container 的 build（例如 `nvcr.io/nvidia/pytorch:25.09-py3`）是在內部針對 CUDA 13 建 torch 的，沒有 `+cu130` 的 wheel 標籤，在那裡 `pip show torch` 不會顯示 `cu130`，光是沒有這個，不算失敗。

典型的症狀：

- `ImportError: undefined symbol`，指向某個 CUDA runtime 函式。
- 第一次呼叫 `.cuda()` 就 segfault，沒有有用的 traceback。
- Wheel 乾淨地安裝完成，卻在 import 時失敗，因為 pip 的解析器只檢查版本限制，不檢查 CUDA ABI。
- 兩個「一模一樣」的環境行為不同，通常是其中一個有 cu130 的 wheel，另一個留著 cu121/cu124 的舊東西。

不管是哪種症狀，解法都一樣：讓 wheel 的 CUDA 標籤對應系統，或是使用已經對應好的 container。

## Component Quick Table

最可能碰到的幾個元件的精簡狀態。包含 wheel URL、build 旗標、sm_121 vs sm_121a 的差別，以及標有日期、已知可用的版本矩陣的完整表格，請看 `references/stack-matrix.md`。

| Component | Status |
|---|---|
| PyTorch | ✅ official cu130 aarch64 wheels |
| bitsandbytes | ✅ works out of the box |
| Triton | ✅ needs the `TRITON_PTXAS_PATH` parameter set |
| flash-attn | ❌ skip pip build; NGC bundles a working one — see `spark-training-gotchas` G2 |
| xformers | source build only (`TORCH_CUDA_ARCH_LIST=12.1`) |
| vLLM | nightly wheels only |
| TransformerEngine / NVFP4 train | container-only |

其他的一切，包含 Unsloth、Axolotl、TRL、PEFT，都能透過上面 container 優先的路徑乾淨地安裝。LLaMA-Factory 和 NeMo 在 Spark 上很脆弱，先去查上游的 issue。

## Verification Commands

在跑任何昂貴的東西之前，先確認環境真的看得到 GPU：

```python
import torch
print(torch.cuda.is_available(), torch.version.cuda)
```

這個呼叫會回傳兩個值，確切的輸出格式是一行 `<bool> <cuda-version>`：

```text
True 13.0
```

如果它印出的是 `False`，不要直接就去重裝 wheel，ABI 不匹配只是幾個可能原因之一：

| Hypothesis | Quick check |
|---|---|
| Runtime/flags | `nvidia-smi` fails in-container too |
| Device visibility | `echo $CUDA_VISIBLE_DEVICES` |
| Permissions | `ls -l /dev/nvidia*` |
| CUDA init state | wedged process; retry fresh shell/container |
| ABI mismatch (usual culprit) | `torch.version.cuda` not `13.x` |

先檢查 `nvidia-smi`，如果它沒有顯示 GPU，那就是前三個之一，不是 ABI。確認是 ABI 之後，才重裝 wheel。每個假設的細節請看 `references/stack-matrix.md`。在 container 啟動之後、安裝專案專屬的套件之前，馬上執行這個檢查。

再一個檢查：如果訓練開始後 Triton kernel 編譯失敗，就設定 `TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas` 再重試，完整的 workaround 清單請看 `references/stack-matrix.md`。

## Next Steps

驗證過的環境只是起點。另外請看：`spark-training-gotchas`，用於訓練執行前的失敗前置檢查；以及 `spark-memory-thermal-ops`，用於長時間執行時的統一記憶體 OOM 和散熱降頻。
