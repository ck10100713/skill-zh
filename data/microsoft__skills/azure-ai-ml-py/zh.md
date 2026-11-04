---
name: azure-ai-ml-py
description: |
  Azure Machine Learning SDK v2（Python 版）。用於 ML workspace、job、模型、資料集、compute 和 pipeline。
  Triggers: "azure-ai-ml", "MLClient", "workspace", "model registry", "training jobs", "datasets"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-ml
---

# Azure Machine Learning SDK v2（Python）

用來管理 Azure ML 資源的 client 函式庫：workspace、job、模型、資料和 compute。

## 安裝

```bash
pip install azure-ai-ml
```

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>  # 所有認證方式都必填
AZURE_RESOURCE_GROUP=<your-resource-group>  # 所有認證方式都必填
AZURE_ML_WORKSPACE_NAME=<your-workspace-name>  # 所有認證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證與生命週期

> **🔑 下面每一段範例程式都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、帳號金鑰或 API key，它們會繞過 Entra 的稽核和金鑰輪替。
>    - 本機開發：直接用 `DefaultAzureCredential` 就好。
>    - 正式環境：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在適合正式環境的憑證。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 才會確實被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **以及** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會省略這些設定，但正式環境的程式碼一定要遵守這兩條規則。

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
import os

# 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接使用指定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
with MLClient(
    credential=credential,
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AZURE_ML_WORKSPACE_NAME"]
) as ml_client:
    for ws in ml_client.workspaces.list():
        print(ws.name)
```

### 從設定檔建立

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# 使用目前目錄或上層目錄的 config.json
with MLClient.from_config(
    credential=DefaultAzureCredential()
) as ml_client:
    for ws in ml_client.workspaces.list():
        print(ws.name)
```

> **長期存活的 `ml_client`：** 這個 skill 後面的範例都假設 `ml_client` 是用上面的模式建立的，而且在整個 script 的生命週期內都還活著。正式環境請把最上層的流程包在單一個 `with MLClient(...) as ml_client:` 區塊裡，這樣底層的 HTTP transport 才會在結束時乾淨地關閉。

## Workspace 管理

### 建立 Workspace

```python
from azure.ai.ml.entities import Workspace

ws = Workspace(
    name="my-workspace",
    location="eastus",
    display_name="My Workspace",
    description="ML workspace for experiments",
    tags={"purpose": "demo"}
)

ml_client.workspaces.begin_create(ws).result()
```

### 列出 Workspace

```python
for ws in ml_client.workspaces.list():
    print(f"{ws.name}: {ws.location}")
```

## 資料資產

### 註冊資料

```python
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

# 註冊單一檔案
my_data = Data(
    name="my-dataset",
    version="1",
    path="azureml://datastores/workspaceblobstore/paths/data/train.csv",
    type=AssetTypes.URI_FILE,
    description="Training data"
)

ml_client.data.create_or_update(my_data)
```

### 註冊資料夾

```python
my_data = Data(
    name="my-folder-dataset",
    version="1",
    path="azureml://datastores/workspaceblobstore/paths/data/",
    type=AssetTypes.URI_FOLDER
)

ml_client.data.create_or_update(my_data)
```

## 模型登錄

### 註冊模型

```python
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

model = Model(
    name="my-model",
    version="1",
    path="./model/",
    type=AssetTypes.CUSTOM_MODEL,
    description="My trained model"
)

ml_client.models.create_or_update(model)
```

### 列出模型

```python
for model in ml_client.models.list(name="my-model"):
    print(f"{model.name} v{model.version}")
```

## Compute

### 建立 Compute Cluster

```python
from azure.ai.ml.entities import AmlCompute

cluster = AmlCompute(
    name="cpu-cluster",
    type="amlcompute",
    size="Standard_DS3_v2",
    min_instances=0,
    max_instances=4,
    idle_time_before_scale_down=120
)

ml_client.compute.begin_create_or_update(cluster).result()
```

### 列出 Compute

```python
for compute in ml_client.compute.list():
    print(f"{compute.name}: {compute.type}")
```

## Job

### Command Job

```python
from azure.ai.ml import command, Input

job = command(
    code="./src",
    command="python train.py --data ${{inputs.data}} --lr ${{inputs.learning_rate}}",
    inputs={
        "data": Input(type="uri_folder", path="azureml:my-dataset:1"),
        "learning_rate": 0.01
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="cpu-cluster",
    display_name="training-job"
)

returned_job = ml_client.jobs.create_or_update(job)
print(f"Job URL: {returned_job.studio_url}")
```

### 監看 Job

```python
ml_client.jobs.stream(returned_job.name)
```

## Pipeline

```python
from azure.ai.ml import dsl, Input, Output
from azure.ai.ml.entities import Pipeline

@dsl.pipeline(
    compute="cpu-cluster",
    description="Training pipeline"
)
def training_pipeline(data_input):
    prep_step = prep_component(data=data_input)
    train_step = train_component(
        data=prep_step.outputs.output_data,
        learning_rate=0.01
    )
    return {"model": train_step.outputs.model}

pipeline = training_pipeline(
    data_input=Input(type="uri_folder", path="azureml:my-dataset:1")
)

pipeline_job = ml_client.jobs.create_or_update(pipeline)
```

## 環境

### 建立自訂環境

```python
from azure.ai.ml.entities import Environment

env = Environment(
    name="my-env",
    version="1",
    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
    conda_file="./environment.yml"
)

ml_client.environments.create_or_update(env)
```

## Datastore

### 列出 Datastore

```python
for ds in ml_client.datastores.list():
    print(f"{ds.name}: {ds.type}")
```

### 取得預設 Datastore

```python
default_ds = ml_client.datastores.get_default()
print(f"Default: {default_ds.name}")
```

## MLClient 操作

| 屬性 | 操作 |
|----------|------------|
| `workspaces` | create, get, list, delete |
| `jobs` | create_or_update, get, list, stream, cancel |
| `models` | create_or_update, get, list, archive |
| `data` | create_or_update, get, list |
| `compute` | begin_create_or_update, get, list, delete |
| `environments` | create_or_update, get, list |
| `datastores` | create_or_update, get, list, get_default |
| `components` | create_or_update, get, list |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.ai.ml` 的同步 client 和非同步 client。每個模組選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with MLClient(...) as client:`（同步）或 `async with MLClient(...) as client:`（非同步）裡。來自 `azure.identity.aio` 的非同步 `DefaultAzureCredential` 也要用 `async with credential:`，token 和 transport 才會被清掉。
3. 資料、模型和環境**要做版本管理**
4. **設定閒置縮減**以降低 compute 成本
5. **使用環境**讓訓練可以重現
6. **串流 job 的 log** 來監看進度
7. 訓練 job 成功之後要**註冊模型**
8. 多步驟流程**用 pipeline**
9. **替資源加 tag**，方便整理和追蹤成本

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專門範例（非主打）。 |
