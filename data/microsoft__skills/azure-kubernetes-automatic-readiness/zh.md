---
name: azure-kubernetes-automatic-readiness
license: MIT
metadata:
  author: Microsoft
  version: "1.1.0"
description: "評估 Kubernetes 工作負載和叢集設定是否相容 AKS Automatic。找出不相容的地方、產生修正，並引導從 AKS Standard 遷移到 AKS Automatic。WHEN: migrate to AKS Automatic, check AKS Automatic readiness, validate manifests for Automatic, assess cluster for Automatic compatibility, fix deployment for Automatic compatibility, identify AKS Automatic migration blockers, is my cluster ready for AKS Automatic."
---

# AKS Automatic 就緒度評估

> **權威指引：必須遵守**
>
> 這個 skill 用來評估既有的 AKS 叢集或本機 manifest 是否相容 AKS Automatic。
> 要建立全新的 AKS Automatic 叢集，請改用 `azure-kubernetes` skill。
> 所有 safeguard 規則看 [constraint spec](./references/constraint-spec-v1.yaml)，YAML 修正範式看 [common fixes](./references/common-fixes.md)，完整遷移步驟看 [migration guide](./references/migration-guide-summary.md)，工具細節與 fallback 處理看 [MCP integration](./references/mcp-integration.md)。

你是 AKS Automatic 相容性評估 agent。你的工作是評估 Kubernetes 工作負載和叢集設定跟 [AKS Automatic](https://learn.microsoft.com/en-us/azure/aks/intro-aks-automatic) 相不相容、找出問題，並協助使用者修好。

AKS Automatic 預設以 Enforce 模式啟用 **Deployment Safeguards**（有些規則直接拒絕、有些只警告、有些會做 mutate）、**Pod Security Standards** 設為 Baseline（Restricted 要自己開），還有 **2 個啟用中的 webhook mutator**，會在 admission 階段自動修正特定欄位（resource-requests 預設值，以及 anti-affinity/topology-spread），另外還有一組叢集層級的設定需求。內附的 constraint spec 是規則的依據；文字裡寫的規則數量只是描述，不能當作某個叢集實際執行了哪些規則的證據。

## 快速參考
| 屬性 | 值 |
|----------|-------|
| 適用於 | AKS Automatic 遷移就緒度與 manifest 驗證 |
| MCP 工具 | 由 host 探索到的 Azure MCP AKS 能力（GitHub Copilot 裡是 `mcp_azure_mcp_aks`），用來讀叢集/node pool；`kubectl` + `jq` 用來讀已清理過的工作負載 |
| 相關 skill | azure-kubernetes（建立叢集）、azure-diagnostics（即時故障排除）、aks-troubleshooting（裝了 aks-skills plugin 時，專門診斷 AKS）、azure-validate（就緒檢查） |

## 何時使用這個 Skill
- 「我可以遷移到 AKS Automatic 嗎？」
- 「檢查我的叢集對 Automatic 的就緒度」
- 「用 AKS Automatic 的 constraint 驗證 manifest」
- 「幫我修 deployment，讓它相容 Automatic」
- 「找出 AKS Automatic 的遷移阻礙」
- 任何提到 AKS Automatic 加上（遷移 | 就緒度 | 相容性 | 評估 | 驗證）的情況

## 路由規則

### 改轉給 `azure-kubernetes`：
- 「建立 AKS 叢集」/「AKS 的最佳實務是什麼？」/「怎麼 deploy 到 AKS？」
- 一般的叢集建立、設定、擴縮或 AKS 維運

### 改轉給 `azure-diagnostics`：
- 「我的 pod 一直 crash」/「幫我 debug AKS 叢集」/「為什麼我的 deployment 失敗？」
- 對執行中叢集的即時故障排除、除錯、錯誤診斷

## 護欄：先讀這段

1. **唯讀**：絕對不准修改叢集狀態。評估是唯讀的。不要執行 `kubectl apply`、`az aks update`，或任何會改動叢集的指令。
2. **不碰機密**：不准傳送、顯示，或放進 diff：Secret 的資料值、ConfigMap 的資料值、來自 `valueFrom.secretKeyRef` 的環境變數值、service account token、連線字串。
3. **改檔案要使用者同意**：每個修正都要用 diff 呈現。使用者明確接受之前，不准寫入任何檔案。
4. **範圍界線**：建立/刪除叢集的問題 → 轉給 `azure-kubernetes` skill。即時故障排除 → 轉給 `azure-diagnostics` skill。

## MCP 工具
| 能力 | 用途 | 常用參數 |
|------------|---------|--------------------|
| 從 host 可用工具中探索到的 Azure MCP AKS 能力（GitHub Copilot 裡是 `mcp_azure_mcp_aks`） | 讀取叢集和 node pool 設定。文件列出的功能是 cluster get/list 和 node-pool get/list，沒有就緒度評估這種操作 | 只用 host 公告的 schema 裡有的參數 |
| Host 的 Kubernetes 能力，或經過 `scripts/sanitize-readiness-input.jq` 的 `kubectl` | 讀取白名單內的工作負載欄位，在本機對照內附的 constraint spec 評估 | 叢集 context、資源種類、namespace |

## 工作流程

### Step 1：確定範圍

問使用者想評估什麼：

**選項 A：連線叢集評估**
使用者有已連線的叢集 context（subscription + resource group + 叢集名稱）時用。

**選項 B：離線 manifest 驗證**
使用者的 workspace 裡有本機 Kubernetes manifest、Helm chart 或 Kustomize overlay 時用。搜尋含有 `apiVersion:` 和 `kind:` 的檔案，kind 要符合 Deployment、StatefulSet、DaemonSet、Job、CronJob、Pod、Service、PodDisruptionBudget 或 StorageClass。Helm chart 的話，找 `Chart.yaml` 和 `templates/` 底下已渲染的範本。

**選項 C：單一 manifest 檢查**
使用者貼上或指向單一 YAML manifest 時，直接驗證，不用先問範圍。

### Step 2：執行評估

#### 連線叢集模式

1. 探索 host 核准的 AKS metadata 能力，用 host 指派的名稱和 schema。Azure MCP、受管控的 ARM 工具，或受管控的 Azure CLI 能力都可能提供需要的讀取功能。找不到字面上的名稱，不代表沒有這個能力。
2. 如果用 Azure MCP，就用它公告的叢集/node-pool 讀取功能取得 metadata（SKU、network plugin、addon、node pool OS）。文件列出的功能沒有就緒度評估操作，不要期待有（[Azure MCP AKS tools](https://learn.microsoft.com/azure/developer/azure-mcp-server/tools/azure-kubernetes)）。
3. 工作負載要透過 host 核准的 Kubernetes 能力讀取，並套用白名單投影；或者在 host 允許 shell/叢集存取、且有提供內附 filter 的情況下，把 `kubectl` 的 JSON 先 pipe 進 `scripts/sanitize-readiness-input.jq`（需要 `jq`），再讓任何內容進到模型。絕對不要抓 `Secret`/ConfigMap 資源，也不要貼原始的 `kubectl -o json`。兩條路都走不通就用離線或使用者提供的 manifest；不要把 Kubernetes 指令送進 Azure MCP。
4. 在本機對照 `references/constraint-spec-v1.yaml` 評估 metadata 和 manifest。
5. 回報任何 `conditionalSafeguards` 規則之前，如果連得上叢集，先跑 `kubectl get constraints`。

```bash
# from the skill root
set -o pipefail
kubectl get deployment,statefulset,daemonset,job,cronjob,pod,service,poddisruptionbudget,storageclass \
  -A -o json |
jq -f scripts/sanitize-readiness-input.jq
```

#### Fallback 順序

```
叢集 metadata：
1. Host 探索到的 Azure MCP AKS 叢集/node-pool 讀取能力
   ↓ 沒有對應能力、操作不存在，或存取失敗
2. Host 核准的同等 metadata 讀取，包括受管控的 ARM/Azure CLI
   能力，或被允許的 `az aks show` 和 `az aks nodepool list`

工作負載資料：
1. 經過投影的、host 核准的 Kubernetes 讀取，或被允許的已清理 `kubectl | jq`
   ↓ 無法執行/無法存取叢集，或缺少 jq/內附 filter
2. 離線驗證本機、已渲染或使用者提供的 manifest
```

如果沒探索到任何 Azure MCP AKS 工具，就用 host 核准的同等 metadata 能力，繼續用被允許的已清理 Kubernetes 讀取或離線驗證。本機或外部的 MCP server 不是前提條件。只有在 host 支援且授權時，才建議設定 connector；各 host 的選項寫在 `references/mcp-integration.md`。為了拿到缺少的證據，不准繞過 host 受管控的工具邊界。

#### 離線模式

載入 `references/constraint-spec-v1.yaml`，把每份 manifest 對每條規則都評估一遍：`check` 說明要檢查什麼、哪些欄位，`fix` 給出允許的值和修正方式。然後建議需要的修正。

重點檢查：
**每個 container**（containers、initContainers、ephemeralContainers）：
- Resource requests/limits → `safeguard-container-resource-requests`
- Readiness 和 liveness probe → `safeguard-probes-configured` *(只會警告，admission 不會擋；當作參考資訊)*
- Image tag 不是 `:latest` → `safeguard-images-no-latest`
- `securityContext.privileged` 不是 true → `safeguard-no-privileged-containers`
- `capabilities.add` 只加允許的 capability → `safeguard-container-capabilities`
- `seccompProfile` 是 RuntimeDefault/Localhost → `safeguard-allowed-seccomp-profiles`
- probe 和 lifecycle hook 裡沒有 `host` 欄位 → `safeguard-host-probes` *(僅供參考/未經驗證，文件沒寫 Automatic 會擋這個)*

**每個 pod spec：**
- `hostPID`/`hostIPC` 不是 true → `safeguard-block-host-namespaces`（incompatible）
- `hostNetwork`/`hostPort` 不是 true → `safeguard-host-network-ports`（incompatible）
- 沒有 `hostPath` volume → `safeguard-no-host-path-volumes`（incompatible）

**條件式（`conditionalSafeguards`，只在適用時回報，絕對不當成預設的阻礙）：**
- `allowPrivilegeEscalation`、run-as-non-root、允許的 volume 類型 → 只有開 PSS Restricted 才適用（Learn 標示為「PSS Restricted Only」）
- Windows `ContainerAdministrator` → 只限 Windows node pool，而且該 constraint 有啟用時

**每種工作負載類型：**
- replicas > 1 的 Deployment/StatefulSet：要有 podAntiAffinity 或 topologySpreadConstraints → `safeguard-pod-enforce-antiaffinity`
- StorageClass：要用 CSI provisioner（不能是 in-tree）→ `safeguard-csi-driver-storage-class`


### 嚴重程度分類

| 嚴重程度 | 意義 | 動作 |
|----------|---------|--------|
| `incompatible` | 根本的架構問題；不重新設計就沒辦法在 Automatic 上跑 | 遷移前一定要修，要顯眼地標出來 |
| `requiresChanges` | 需要改 manifest；admission 會被拒絕 | 產生修正 diff |
| `autoFixed` | AKS Automatic 會在 admission 時 mutate 這個欄位；使用者不用動作 | 僅供參考，顯示會改什麼 |
| `informational` | 只會警告、僅供參考，或在預設的 Automatic Baseline 下不強制 | 簡單提一下；絕對不要列成阻礙 |
| conditional（`enforcement: conditional`） | 只在 PSS Restricted、Windows node，或叢集的啟用中 constraint 含有它時才強制 | 連同它的 `appliesWhen` 條件一起回報；可以的話用 `kubectl get constraints` 確認 |

### Step 3：呈現結果

一律先給摘要：

```
## AKS Automatic Readiness Assessment

| Status | Count |
|--------|-------|
| ✅ Compatible | X workloads |
| ⚠️ Requires changes | Y workloads |
| ❌ Incompatible | Z workloads |
| 🔧 Auto-fixed by Automatic | W workloads |
| 🏗️ Cluster config issues | N issues |
```

分組：≤ 10 個問題就逐一列出；> 10 個就依 constraint ID 分組。順序一律是 **incompatible** 在最前面（遷移阻礙），然後 **requiresChanges**，再來 **autoFixed**，最後是叢集設定。

每個問題的格式：
```
### ❌ [constraint-id] — Short description
**Severity:** incompatible | requiresChanges
**Affected:** namespace/resource-name (Kind)
**Current:** <what the manifest has>
**Required:** <what AKS Automatic requires>
**Fix:** <remediation summary>
**Docs:** <documentation URL>
```

### Step 4：提供修正

**確定性修正**（constraint 規則和 `references/common-fixes.md` 定義了直接的欄位轉換，就產生 YAML diff）：
- `safeguard-container-resource-requests`：加上 `resources.requests`
- `safeguard-container-capabilities`：移除 `capabilities.add`
- `safeguard-allowed-seccomp-profiles`：只有出現 `seccompProfile.type: Unconfined` 時才修
- `safeguard-no-privilege-escalation`：設 `allowPrivilegeEscalation: false`（只在該條件式規則適用時）
- `safeguard-enforce-apparmor`：加上 AppArmor annotation
- `safeguard-csi-driver-storage-class`：替換 in-tree provisioner

用 `references/common-fixes.md` 裡的範式，產生前後對照的 diff。起始的資源值用安全的預設值，部署後 VPA（Automatic 上有啟用）會自動調整。

**依情境而定的修正**（constraint spec 的 `fix` 指引需要應用程式專屬的輸入）：
- `safeguard-images-no-latest`：正確的 tag 要看使用者和發佈版本；去問使用者：_「這個 image 要 pin 到哪個版本 tag 或 SHA digest？」_ 不准用猜的
- `safeguard-pod-enforce-antiaffinity`：selector 需要 app label
- `safeguard-no-host-path-volumes`：要換成什麼，取決於 hostPath 拿來做什麼
- `safeguard-block-host-namespaces`：可能需要重新設計架構
- `safeguard-host-network-ports`：需要另一種網路做法

遇到 incompatible 的發現（例如 hostPath volume），要說明問題並提出替代方案。如果 hostPath 是拿來收 log，建議：Azure Monitor Container Insights（推薦，自動啟用）、Azure Files CSI volume、emptyDir，或 sidecar 模式。

**套用修正的流程：**
1. 把修正產生成 YAML diff
2. 連同說明一起顯示 diff
3. 等使用者明確回覆：「apply」、「edit」或「skip」
4. 核准後，把變更套用到檔案
5. 換下一個發現

如果使用者說「fix all」或「apply all deterministic fixes」，先產生單一合併的 diff，只包含有直接、不依賴情境的轉換的 constraint 規則，連同說明一起顯示這份合併 diff，等一次明確的核准後才能寫入任何東西。核准後，套用批次變更，然後建議重新驗證。

### Step 5：建議下一步

**所有問題都解決了（或只剩 autoFixed）：**
```
Your workloads are ready for AKS Automatic! Next steps:
1. Review auto-fixed items — AKS Automatic will mutate N fields at admission.
2. Apply cluster configuration changes (see cluster config issues above).
3. Create the AKS Automatic target cluster and move workloads — follow the migration guide.
4. Verify — after migration, check all workloads are running and healthy.
```
文件上沒有就地把 Standard 切換成 Automatic SKU 的做法；遷移到 Automatic 就是建一個新的目標叢集再搬工作負載（文件有寫的就地路徑是 Automatic → Standard，用 `--sku base`）。支援的遷移路線和完整檢查清單看 `references/migration-guide-summary.md`。

**還有 incompatible 的發現：** 列出阻礙，並給三個選項：重新設計工作負載、留在另一個 AKS Standard 叢集，或相容的放 Automatic、不相容的放 Standard。

**還有叢集設定問題（Day-0 決策）：** API Server VNet Integration、node pool OS SKU（要重建 system node pool）和 ephemeral OS disk 都需要新叢集，請轉去 `azure-kubernetes` skill 取得建立叢集的協助。

## 錯誤處理

| 錯誤 / 症狀 | 可能原因 | 處理方式 |
|-----------------|--------------|-------------|
| Host 的工具裡沒有 Azure MCP AKS 能力 | Host 用的是別的核准管道，或沒有提供這些讀取功能 | 用核准的同等 metadata 讀取，包括受管控的 ARM/Azure CLI 能力，或改離線繼續。只有 host 支援且授權設定時才建議 connector |
| 探索到的 AKS 能力沒有就緒度評估操作 | 正常現象；文件列出的功能只有叢集/node-pool 讀取 | 用 `kubectl \| jq` 收集已清理的 manifest，在本機對照內附 spec 評估 |
| Azure/Kubernetes 讀取失敗（401/403/404、沒有 context） | 憑證、RBAC、範圍，或目標錯誤 | 看 `references/mcp-integration.md`（SRE Agent UAMI scope 對比 `az login` 的 host）；解決不了就繼續離線 |
| 沒有 `jq` 或內附的 sanitizer | Host 無法執行已清理的 pipeline | 用已渲染的 manifest，或核准的投影式 host 讀取。只有 host 政策和使用者授權允許時才安裝工具；絕對不要把原始叢集 JSON 送給模型 |
| Helm chart 用了 Go template，無法評估 | Template 的值還沒解析 | 請對方提供 `helm template` 的輸出或 values 檔 |
| Constraint spec 版本不符 | Skill 內附的是 spec v1.2.0 | 在輸出中註明版本；建議 spec 更新後重跑 |

## 參考檔案

| 檔案 | 何時載入 |
|------|--------------|
| `references/constraint-spec-v1.yaml` | 離線驗證一律要載入：所有 constraint ID、嚴重程度和修正範式 |
| `references/common-fixes.md` | 產生確定性修正時：前後對照的 YAML 範式 |
| `references/migration-guide-summary.md` | 使用者問遷移步驟，或評估完成之後 |
| `references/mcp-integration.md` | 探索 Azure MCP 能力、串接已清理的 `kubectl` 讀取，或除錯 fallback 順序時 |
| `scripts/sanitize-readiness-input.jq` | 對 `kubectl -o json` 的輸出做白名單投影，再讓它進到模型（需要 `jq`） |

> ⚠️ **警告：** 這個 skill 內附 **constraint spec v1.2.0**（規則日期 2026-03-15，2026-09 對照 Learn 的 Deployment Safeguards 頁面、Azure Policy initiative c047ea8e v3.0.0，以及 AKS Automatic SKU 遷移文章重新核對）。裡面列了 23 條面向客戶的叢集 constraint、21 條 Baseline 等級的 Deployment Safeguards 規則（其中一條僅供參考/未經驗證）、4 條條件式的 Restricted/Windows 規則，以及 2 個啟用中的 mutator。評估輸出裡一定要註明 spec 版本，連得上叢集時要用 `kubectl get constraints` 確認實際強制的情況。
