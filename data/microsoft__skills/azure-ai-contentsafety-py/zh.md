---
name: azure-ai-contentsafety-py
description: |
  Azure AI Content Safety SDK（Python 版）。用於偵測文字和圖片中的有害內容，提供多級嚴重程度分類。
  Triggers: "azure-ai-contentsafety", "ContentSafetyClient", "content moderation", "harmful content", "text analysis", "image analysis"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-contentsafety
---

# Azure AI Content Safety SDK（Python）

在應用程式裡偵測使用者產生和 AI 產生的有害內容。

## 安裝

```bash
pip install azure-ai-contentsafety
```

## 環境變數

```bash
CONTENT_SAFETY_ENDPOINT=https://<resource>.cognitiveservices.azure.com  # 所有認證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
CONTENT_SAFETY_KEY=<your-api-key>  # 只有用下面舊的 API key 認證路徑時才需要
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
import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions

# 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接使用指定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with ContentSafetyClient(
    endpoint=os.environ["CONTENT_SAFETY_ENDPOINT"],
    credential=credential,
) as client:
    response = client.analyze_text(AnalyzeTextOptions(text="Hello, world!"))
```

### 舊做法：API Key（既有使用金鑰的部署）

新的程式碼應該用上面的 `DefaultAzureCredential`。只有在既有的金鑰部署還沒遷移到 Entra ID 時才用 `AzureKeyCredential`，例如還在完成 Entra 導入的受規範環境。

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions

with ContentSafetyClient(
    endpoint=os.environ["CONTENT_SAFETY_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["CONTENT_SAFETY_KEY"]),
) as client:
    response = client.analyze_text(AnalyzeTextOptions(text="Hello, world!"))
```

如果你也需要用金鑰管理 blocklist，`BlocklistClient` 接受同樣的 `AzureKeyCredential`。

## 分析文字

```python
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
from azure.identity import DefaultAzureCredential

with ContentSafetyClient(endpoint, DefaultAzureCredential()) as client:
    request = AnalyzeTextOptions(text="Your text content to analyze")
    response = client.analyze_text(request)

    # 檢查每個類別
    for category in [TextCategory.HATE, TextCategory.SELF_HARM, 
                     TextCategory.SEXUAL, TextCategory.VIOLENCE]:
        result = next((r for r in response.categories_analysis 
                       if r.category == category), None)
        if result:
            print(f"{category}: severity {result.severity}")
```

## 分析圖片

```python
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData
from azure.identity import DefaultAzureCredential
import base64

with ContentSafetyClient(endpoint, DefaultAzureCredential()) as client:
    # 從檔案讀取
    with open("image.jpg", "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    request = AnalyzeImageOptions(
        image=ImageData(content=image_data)
    )

    response = client.analyze_image(request)

    for result in response.categories_analysis:
        print(f"{result.category}: severity {result.severity}")
```

### 網址上的圖片

```python
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

request = AnalyzeImageOptions(
    image=ImageData(blob_url="https://example.com/image.jpg")
)

response = client.analyze_image(request)
```

## 文字 Blocklist 管理

### 建立 Blocklist

```python
from azure.ai.contentsafety import BlocklistClient
from azure.ai.contentsafety.models import TextBlocklist
from azure.identity import DefaultAzureCredential

with BlocklistClient(endpoint, DefaultAzureCredential()) as blocklist_client:
    blocklist = TextBlocklist(
        blocklist_name="my-blocklist",
        description="Custom terms to block"
    )

    result = blocklist_client.create_or_update_text_blocklist(
        blocklist_name="my-blocklist",
        options=blocklist
    )
```

### 新增封鎖項目

```python
from azure.ai.contentsafety.models import AddOrUpdateTextBlocklistItemsOptions, TextBlocklistItem

items = AddOrUpdateTextBlocklistItemsOptions(
    blocklist_items=[
        TextBlocklistItem(text="blocked-term-1"),
        TextBlocklistItem(text="blocked-term-2")
    ]
)

result = blocklist_client.add_or_update_blocklist_items(
    blocklist_name="my-blocklist",
    options=items
)
```

### 搭配 Blocklist 分析

```python
from azure.ai.contentsafety.models import AnalyzeTextOptions

request = AnalyzeTextOptions(
    text="Text containing blocked-term-1",
    blocklist_names=["my-blocklist"],
    halt_on_blocklist_hit=True
)

response = client.analyze_text(request)

if response.blocklists_match:
    for match in response.blocklists_match:
        print(f"Blocked: {match.blocklist_item_text}")
```

## 嚴重程度

文字分析預設回傳 4 級嚴重程度（0、2、4、6）。要用 8 級（0-7）：

```python
from azure.ai.contentsafety.models import AnalyzeTextOptions, AnalyzeTextOutputType

request = AnalyzeTextOptions(
    text="Your text",
    output_type=AnalyzeTextOutputType.EIGHT_SEVERITY_LEVELS
)
```

## 有害內容類別

| 類別 | 說明 |
|----------|-------------|
| `Hate` | 針對身分（種族、宗教、性別等）的攻擊 |
| `Sexual` | 性內容、關係、身體部位 |
| `Violence` | 肢體傷害、武器、受傷 |
| `SelfHarm` | 自傷、自殺、飲食失調 |

## 嚴重程度級距

| 級別 | 文字範圍 | 圖片範圍 | 意義 |
|-------|------------|-------------|---------|
| 0 | Safe | Safe | 沒有有害內容 |
| 2 | Low | Low | 輕微提及 |
| 4 | Medium | Medium | 中等程度的內容 |
| 6 | High | High | 嚴重的內容 |

## Client 類型

| Client | 用途 |
|--------|---------|
| `ContentSafetyClient` | 分析文字和圖片 |
| `BlocklistClient` | 管理自訂 blocklist |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.ai.contentsafety` 的同步 client 和 `azure.ai.contentsafety.aio` 的非同步 client。每個模組選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with ContentSafetyClient(...) as client:`（同步）或 `async with ContentSafetyClient(...) as client:`（非同步）裡。來自 `azure.identity.aio` 的非同步 `DefaultAzureCredential` 也要用 `async with credential:`，token 和 transport 才會被清掉。
3. 特定領域的詞彙**用 blocklist**
4. **設定嚴重程度門檻**，要符合你的使用情境
5. **處理多個類別**：內容可能在好幾方面都有害
6. 要立即拒絕時**用 halt_on_blocklist_hit**
7. **記錄分析結果**，供稽核和改進使用
8. 需要更細的控制時，**考慮 8 級嚴重程度模式**
9. AI 的輸出在顯示給使用者之前**先審核**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專門範例（非主打）。 |
