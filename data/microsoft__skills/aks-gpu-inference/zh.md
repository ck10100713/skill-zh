---
name: aks-gpu-inference
description: "用感知 profile 的唯讀證據診斷 Day-2 的 AKS GPU 和 KAITO 事故。WHEN: 'Insufficient nvidia.com/gpu'、GPU pod 卡在 Pending、載入模型時 OOM、DCGM/VRAM、KAITO Workspace 沒 ready，或 GPU autoscaling。不要用在：初始設定（airunway-aks-setup）、非 GPU 事故（aks-troubleshooting）、單獨的 VM 配額（azure-quotas），或一般成本問題（選用 azure-cost plugin 的 cost-analysis 或 cost-optimization）。"
license: MIT
metadata:
  author: Microsoft
  version: "1.1.1"
---

# AKS GPU 推論 Day-2

## 速查

| 屬性 | 值 |
|---|---|
| 適用情境 | AKS GPU／KAITO 故障 |
| 證據 | 綁定的目標、events／status、`gpuProfile`、DCGM |

## 何時使用這個 Skill

用在排程、VRAM／OOM、KAITO 就緒狀態和工作負載擴縮。排除的情境
依上面所述導向其他 skill。

## MCP 工具

用 host 提供的合適 Azure 讀取工具，或 reference 裡的唯讀查詢。

## Host 能力檢查關卡

執行任何 reference 裡的 pipeline 之前，先確認 host 有授權
對綁定目標執行所需的 shell 和 `kubectl`／`az` 指令。
以檔案為基礎的蒐集，還需要核准的 artifact 儲存位置，以及能存取
它用到的所有附帶檔案。光有一個受管控的 Azure CLI 工具，並不代表
具備這些能力。只有在 host 讀取工具公告的 schema 能提供所需證據時，
才可以用同等的 host 讀取取代指令。

如果無法執行或被禁止，就直說，然後分析使用者提供或
已遮蔽的 events、status、log 和 metrics，或給操作人員一份限定範圍的
蒐集計畫。說明哪些讀取沒有執行，需要缺少的證據才能下的
結論一律標示為未確認。絕對不要透過 Azure MCP 去跑 `kubectl`，也不要
繞過 host 的政策。下面的授權要求依然適用。

## 流程

1. 綁定 subscription、cluster、kube context、pool 和受影響的資源。
2. 擷取確切的 events／status 和觀察到的 `gpuProfile`，並說明跑了哪些讀取。
3. 依情況導向 [scheduling](references/gpu-scheduling.md)、
   [observability](references/gpu-observability.md)、
   [KAITO](references/kaito-workspaces.md) 或
   [scaling](references/gpu-cost-and-scaling.md)。
4. 把 container／host 的 OOM 和裝置配置失敗分開看。遇到 `OOMKilled` 時，
   要對照 container 的記憶體 limit／用量和 node 狀態。對於
   Managed+Install 的裝置記憶體證據，使用 port 19400 的 exporter 和
   事故時段的 `FB_USED`／`FB_FREE`；容量估算表不能當作成因的證據。
5. KAITO 沒 ready 時，要警告刪除 Workspace 並不會移除它的 GPU pool；
   清理是另一件事，需要明確授權。
6. 回報證據、信心程度、缺少的證據，以及該交給誰處理。

在擴縮、cordon／drain、刪除、
啟用 add-on 或更動監控設定之前，都要有明確授權。

## 錯誤處理

| 狀況 | 處理 |
|---|---|
| 證據缺漏或互相矛盾 | 標示為未確認；向負責人要求提供／讀取 |
| 未知的 profile | 保留證據；不要開出整套修復方案 |
| 需要變更 | 另外提出，等授權 |
