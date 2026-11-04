---
name: azure-mgmt-fabric-py
description: |-
  Azure Fabric Management SDK for Python。用於管理 Microsoft Fabric capacity 和資源。
  Triggers: "azure-mgmt-fabric", "FabricMgmtClient", "Fabric capacity", "Microsoft Fabric", "Power BI capacity".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Azure Fabric Management SDK for Python

用程式管理 Microsoft Fabric capacity 和資源。

## 安裝

```bash
pip install azure-mgmt-fabric
pip install azure-identity
```

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>  # 所有認證方式都必填
AZURE_RESOURCE_GROUP=<your-resource-group>  # 所有認證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證與生命週期

> **🔑 底下每個程式碼範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能運作，程式碼不用改。避免用連線字串、帳號/API key，它們會繞過 Entra 的稽核和輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - 正式環境：設 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential 鏈限制在適合正式環境的 credential。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 才會確實釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且**要 `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會簡化這段設定，但正式環境的程式碼一定要遵守這兩條規則。

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.mgmt.fabric import FabricMgmtClient
import os

# 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接用特定的 credential：
# 見 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with FabricMgmtClient(
    credential=credential,
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
) as client:
    # 後續所有操作都用 `client`（見下面的範例）
    ...
```

## 建立 Fabric Capacity

```python
from azure.mgmt.fabric import FabricMgmtClient
from azure.mgmt.fabric.models import FabricCapacity, FabricCapacityProperties, CapacitySku
from azure.identity import DefaultAzureCredential
import os

resource_group = os.environ["AZURE_RESOURCE_GROUP"]
capacity_name = "myfabriccapacity"

credential = DefaultAzureCredential()
with FabricMgmtClient(
    credential=credential,
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
) as client:
    capacity = client.fabric_capacities.begin_create_or_update(
        resource_group_name=resource_group,
        capacity_name=capacity_name,
        resource=FabricCapacity(
            location="eastus",
            sku=CapacitySku(
                name="F2",  # Fabric SKU
                tier="Fabric"
            ),
            properties=FabricCapacityProperties(
                administration=FabricCapacityAdministration(
                    members=["user@contoso.com"]
                )
            )
        )
    ).result()

print(f"Capacity created: {capacity.name}")
```

## 取得 Capacity 詳細資料

```python
capacity = client.fabric_capacities.get(
    resource_group_name=resource_group,
    capacity_name=capacity_name
)

print(f"Capacity: {capacity.name}")
print(f"SKU: {capacity.sku.name}")
print(f"State: {capacity.properties.state}")
print(f"Location: {capacity.location}")
```

## 列出 Resource Group 裡的 Capacity

```python
capacities = client.fabric_capacities.list_by_resource_group(
    resource_group_name=resource_group
)

for capacity in capacities:
    print(f"Capacity: {capacity.name} - SKU: {capacity.sku.name}")
```

## 列出 Subscription 裡所有 Capacity

```python
all_capacities = client.fabric_capacities.list_by_subscription()

for capacity in all_capacities:
    print(f"Capacity: {capacity.name} in {capacity.location}")
```

## 更新 Capacity

```python
from azure.mgmt.fabric.models import FabricCapacityUpdate, CapacitySku

updated = client.fabric_capacities.begin_update(
    resource_group_name=resource_group,
    capacity_name=capacity_name,
    properties=FabricCapacityUpdate(
        sku=CapacitySku(
            name="F4",  # 擴大
            tier="Fabric"
        ),
        tags={"environment": "production"}
    )
).result()

print(f"Updated SKU: {updated.sku.name}")
```

## 暫停 Capacity

暫停 capacity 以停止計費：

```python
client.fabric_capacities.begin_suspend(
    resource_group_name=resource_group,
    capacity_name=capacity_name
).result()

print("Capacity suspended")
```

## 恢復 Capacity

恢復已暫停的 capacity：

```python
client.fabric_capacities.begin_resume(
    resource_group_name=resource_group,
    capacity_name=capacity_name
).result()

print("Capacity resumed")
```

## 刪除 Capacity

```python
client.fabric_capacities.begin_delete(
    resource_group_name=resource_group,
    capacity_name=capacity_name
).result()

print("Capacity deleted")
```

## 檢查名稱可用性

```python
from azure.mgmt.fabric.models import CheckNameAvailabilityRequest

result = client.fabric_capacities.check_name_availability(
    location="eastus",
    body=CheckNameAvailabilityRequest(
        name="my-new-capacity",
        type="Microsoft.Fabric/capacities"
    )
)

if result.name_available:
    print("Name is available")
else:
    print(f"Name not available: {result.reason}")
```

## 列出可用的 SKU

```python
skus = client.fabric_capacities.list_skus(
    resource_group_name=resource_group,
    capacity_name=capacity_name
)

for sku in skus:
    print(f"SKU: {sku.name} - Tier: {sku.tier}")
```

## Client 操作

| 操作 | 方法 |
|-----------|--------|
| `client.fabric_capacities` | Capacity CRUD 操作 |
| `client.operations` | 列出可用的操作 |

## Fabric SKU

| SKU | 說明 | CU |
|-----|-------------|-----|
| `F2` | 入門級 | 2 Capacity Unit |
| `F4` | 小 | 4 Capacity Unit |
| `F8` | 中 | 8 Capacity Unit |
| `F16` | 大 | 16 Capacity Unit |
| `F32` | X-Large | 32 Capacity Unit |
| `F64` | 2X-Large | 64 Capacity Unit |
| `F128` | 4X-Large | 128 Capacity Unit |
| `F256` | 8X-Large | 256 Capacity Unit |
| `F512` | 16X-Large | 512 Capacity Unit |
| `F1024` | 32X-Large | 1024 Capacity Unit |
| `F2048` | 64X-Large | 2048 Capacity Unit |

## Capacity 狀態

| 狀態 | 說明 |
|-------|-------------|
| `Active` | Capacity 運作中 |
| `Paused` | Capacity 已暫停（不計費） |
| `Provisioning` | 建立中 |
| `Updating` | 修改中 |
| `Deleting` | 移除中 |
| `Failed` | 操作失敗 |

## 長時間執行的操作

所有會修改資源的操作都是長時間執行的操作（LRO）。用 `.result()` 等待：

```python
# 同步等待
capacity = client.fabric_capacities.begin_create_or_update(...).result()

# 或自己輪詢
poller = client.fabric_capacities.begin_create_or_update(...)
while not poller.done():
    print(f"Status: {poller.status()}")
    time.sleep(5)
capacity = poller.result()
```

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會清理乾淨。
3. 在本機執行的程式碼用 **`DefaultAzureCredential`**。在 Azure 上執行的程式碼用特定的 token credential。
4. **暫停沒在用的 capacity**，降低成本
5. **從小的 SKU 開始**，需要時再擴大
6. **用 tag** 追蹤成本和整理資源
7. 建立 capacity 之前**先檢查名稱可用性**
8. **正確處理 LRO**：不要假設會立刻完成
9. **設定 capacity 管理員**：指定可以管理 workspace 的使用者
10. 透過 Azure Monitor 指標**監控 capacity 用量**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、operation group 涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要/進階情境的專屬非主打範例。 |
