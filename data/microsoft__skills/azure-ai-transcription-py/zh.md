---
name: azure-ai-transcription-py
description: |
  Azure AI Transcription SDK（Python 版）。用於即時和批次的語音轉文字，支援時間戳記和說話者分離。
  Triggers: "transcription", "speech to text", "Azure AI Transcription", "TranscriptionClient"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-transcription
---

# Azure AI Transcription SDK（Python）

Azure AI Transcription（語音轉文字）的 client 函式庫，支援即時和批次轉錄。

## 安裝

```bash
pip install azure-ai-transcription
```

## 環境變數

```bash
TRANSCRIPTION_ENDPOINT=https://<resource>.cognitiveservices.azure.com
TRANSCRIPTION_KEY=<your-key>  # 金鑰認證用；使用 DefaultAzureCredential/TokenCredential 時不需要
```

## 認證與生命週期

> **🔑 下面每一段範例程式都適用兩條規則：**
>
> 1. **支援兩種認證模式：** 金鑰認證用 `AzureKeyCredential(os.environ["TRANSCRIPTION_KEY"])`，Entra ID 用 `DefaultAzureCredential()` 或任何 `TokenCredential`。正式環境優先用 `DefaultAzureCredential`；絕對不要把憑證寫死在程式碼裡。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport 和 socket 才會確實被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:`
>
> 範例片段可能會省略這些設定，但正式環境的程式碼一定要遵守這兩條規則。

使用 subscription key 認證：

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient

with TranscriptionClient(
    endpoint=os.environ["TRANSCRIPTION_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["TRANSCRIPTION_KEY"]),
) as client:
    transcriptions = list(client.list_transcriptions())
```

## 轉錄（批次）

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient

with TranscriptionClient(
    endpoint=os.environ["TRANSCRIPTION_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["TRANSCRIPTION_KEY"]),
) as client:
    job = client.begin_transcription(
        name="meeting-transcription",
        locale="en-US",
        content_urls=["https://<storage>/audio.wav"],
        diarization_enabled=True,
    )
    result = job.result()
    print(result.status)
```

## 轉錄（即時）

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.transcription import TranscriptionClient

with TranscriptionClient(
    endpoint=os.environ["TRANSCRIPTION_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["TRANSCRIPTION_KEY"]),
) as client:
    stream = client.begin_stream_transcription(locale="en-US")
    stream.send_audio_file("audio.wav")
    for event in stream:
        print(event.text)
```

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.xxx` 的同步 client 和 `azure.xxx.aio` 的非同步 client。每個模組選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。來自 `azure.identity.aio` 的非同步 `DefaultAzureCredential` 也要用 `async with credential:`，token 和 transport 才會被清掉。
3. 有多位說話者時**開啟說話者分離**
4. 存在 blob storage 的長檔案**用批次轉錄**
5. 為了產生字幕**要擷取時間戳記**
6. **指定語言**可以提高辨識準確度
7. 即時轉錄要**處理串流的 backpressure**
8. 完成後要**關閉轉錄 session**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專門範例（非主打）。 |
