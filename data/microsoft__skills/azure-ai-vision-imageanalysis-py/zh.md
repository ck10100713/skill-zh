---
name: azure-ai-vision-imageanalysis-py
description: |
  Azure AI Vision Image Analysis SDK，支援影像描述、標籤、物件、OCR、人物偵測和智慧裁切。適用於電腦視覺和影像理解任務。
  Triggers: "image analysis", "computer vision", "OCR", "object detection", "ImageAnalysisClient", "image caption".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-vision-imageanalysis
---

# Azure AI Vision Image Analysis SDK for Python

Azure AI Vision 4.0 影像分析的 client library，包含影像描述、標籤、物件、OCR 等功能。

## Installation

```bash
pip install azure-ai-vision-imageanalysis
```

## Environment Variables

```bash
VISION_ENDPOINT=https://<resource>.cognitiveservices.azure.com  # 所有驗證方式都需要
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
VISION_KEY=<your-api-key>  # 只有下面舊版 API key 驗證路徑才需要
```

## Authentication & Lifecycle

> **🔑 下面每個程式範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、account/API key，因為它們會繞過 Entra 的稽核和金鑰輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - Production：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在 production 安全的 credential。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 會確實被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例程式碼可能會省略這部分設定，但 production 程式碼一定要兩條規則都遵守。

```python
import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用指定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with ImageAnalysisClient(
    endpoint=os.environ["VISION_ENDPOINT"],
    credential=credential,
) as client:
    result = client.analyze_from_url(
        image_url="https://aka.ms/azsdk/image-analysis/sample.jpg",
        visual_features=[VisualFeatures.CAPTION],
    )
```

### Legacy: API Key (existing keyed deployments)

新程式碼請用上面的 `DefaultAzureCredential`。只有在既有的 key 驗證部署還沒遷移到 Entra ID 時才用 `AzureKeyCredential`，例如還在進行 Entra 上線的受管制環境。

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

with ImageAnalysisClient(
    endpoint=os.environ["VISION_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["VISION_KEY"]),
) as client:
    result = client.analyze_from_url(
        image_url="https://aka.ms/azsdk/image-analysis/sample.jpg",
        visual_features=[VisualFeatures.CAPTION],
    )
```

## Analyze Image from URL

```python
from azure.ai.vision.imageanalysis.models import VisualFeatures

image_url = "https://example.com/image.jpg"

result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[
        VisualFeatures.CAPTION,
        VisualFeatures.TAGS,
        VisualFeatures.OBJECTS,
        VisualFeatures.READ,
        VisualFeatures.PEOPLE,
        VisualFeatures.SMART_CROPS,
        VisualFeatures.DENSE_CAPTIONS
    ],
    gender_neutral_caption=True,
    language="en"
)
```

## Analyze Image from File

```python
with open("image.jpg", "rb") as f:
    image_data = f.read()

result = client.analyze(
    image_data=image_data,
    visual_features=[VisualFeatures.CAPTION, VisualFeatures.TAGS]
)
```

## Image Caption

```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.CAPTION],
    gender_neutral_caption=True
)

if result.caption:
    print(f"Caption: {result.caption.text}")
    print(f"Confidence: {result.caption.confidence:.2f}")
```

## Dense Captions (Multiple Regions)

```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.DENSE_CAPTIONS]
)

if result.dense_captions:
    for caption in result.dense_captions.list:
        print(f"Caption: {caption.text}")
        print(f"  Confidence: {caption.confidence:.2f}")
        print(f"  Bounding box: {caption.bounding_box}")
```

## Tags

```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.TAGS]
)

if result.tags:
    for tag in result.tags.list:
        print(f"Tag: {tag.name} (confidence: {tag.confidence:.2f})")
```

## Object Detection

```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.OBJECTS]
)

if result.objects:
    for obj in result.objects.list:
        print(f"Object: {obj.tags[0].name}")
        print(f"  Confidence: {obj.tags[0].confidence:.2f}")
        box = obj.bounding_box
        print(f"  Bounding box: x={box.x}, y={box.y}, w={box.width}, h={box.height}")
```

## OCR (Text Extraction)

```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.READ]
)

if result.read:
    for block in result.read.blocks:
        for line in block.lines:
            print(f"Line: {line.text}")
            print(f"  Bounding polygon: {line.bounding_polygon}")
            
            # 字詞層級的細節
            for word in line.words:
                print(f"  Word: {word.text} (confidence: {word.confidence:.2f})")
```

## People Detection

```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.PEOPLE]
)

if result.people:
    for person in result.people.list:
        print(f"Person detected:")
        print(f"  Confidence: {person.confidence:.2f}")
        box = person.bounding_box
        print(f"  Bounding box: x={box.x}, y={box.y}, w={box.width}, h={box.height}")
```

## Smart Cropping

```python
result = client.analyze_from_url(
    image_url=image_url,
    visual_features=[VisualFeatures.SMART_CROPS],
    smart_crops_aspect_ratios=[0.9, 1.33, 1.78]  # 直式、4:3、16:9
)

if result.smart_crops:
    for crop in result.smart_crops.list:
        print(f"Aspect ratio: {crop.aspect_ratio}")
        box = crop.bounding_box
        print(f"  Crop region: x={box.x}, y={box.y}, w={box.width}, h={box.height}")
```

## Async Client

```python
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.identity.aio import DefaultAzureCredential

async def analyze_image():
    async with DefaultAzureCredential() as credential:
        async with ImageAnalysisClient(
            endpoint=endpoint,
            credential=credential
        ) as client:
            result = await client.analyze_from_url(
                image_url=image_url,
                visual_features=[VisualFeatures.CAPTION]
            )
            print(result.caption.text)
```

## Visual Features

| Feature | Description |
|---------|-------------|
| `CAPTION` | 用一句話描述影像 |
| `DENSE_CAPTIONS` | 多個區域的描述 |
| `TAGS` | 內容標籤（物件、場景、動作） |
| `OBJECTS` | 物件偵測，附 bounding box |
| `READ` | OCR 文字擷取 |
| `PEOPLE` | 人物偵測，附 bounding box |
| `SMART_CROPS` | 建議的縮圖裁切區域 |

## Error Handling

```python
from azure.core.exceptions import HttpResponseError

try:
    result = client.analyze_from_url(
        image_url=image_url,
        visual_features=[VisualFeatures.CAPTION]
    )
except HttpResponseError as e:
    print(f"Status code: {e.status_code}")
    print(f"Reason: {e.reason}")
    print(f"Message: {e.error.message}")
```

## Image Requirements

- 格式：JPEG、PNG、GIF、BMP、WEBP、ICO、TIFF、MPO
- 大小上限：20 MB
- 尺寸：50x50 到 16000x16000 像素

## Best Practices

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.ai.vision.imageanalysis` 同步 client 和 `azure.ai.vision.imageanalysis.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with ImageAnalysisClient(...) as client:`（同步）或 `async with ImageAnalysisClient(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **只選需要的功能**，優化延遲和成本
4. **高吞吐量情境用非同步 client**
5. **處理 HttpResponseError**，應付無效影像或驗證問題
6. **開啟 gender_neutral_caption**，讓描述更包容
7. **指定 language**，取得在地化的描述
8. **smart_crops_aspect_ratios 要配合**你的縮圖需求
9. **同一張影像要分析多次時，快取結果**

## Reference Files

| File | Contents |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打功能、operation group 涵蓋範圍，以及 production 檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要與進階情境的專屬非主打範例。 |
