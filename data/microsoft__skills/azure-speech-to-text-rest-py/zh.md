---
name: azure-speech-to-text-rest-py
description: |-
  用於短音訊的 Azure Speech to Text REST API（Python）。不用 Speech SDK，就能對 60 秒以內的音訊檔做簡單的語音辨識。
  Triggers: "speech to text REST", "short audio transcription", "speech recognition REST API", "STT REST", "recognize speech REST".
  DO NOT USE FOR: 長音訊（超過 60 秒）、即時串流、批次轉錄、自訂語音模型、語音翻譯。這些情況請改用 Speech SDK 或 Batch Transcription API。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# 用於短音訊的 Azure Speech to Text REST API

簡單的 REST API，用來把短音訊檔（60 秒以內）轉成文字。不需要 SDK，只要發 HTTP request。

## 前置需求

1. **Azure subscription** - [免費建立一個](https://azure.microsoft.com/free/)
2. **Speech 資源** - 在 [Azure Portal](https://portal.azure.com/#create/Microsoft.CognitiveServicesSpeechServices) 建立
3. **取得憑證** - 部署完成後，到資源 > Keys and Endpoint

## 環境變數

```bash
# 必填
AZURE_SPEECH_KEY=<your-speech-resource-key>
AZURE_SPEECH_REGION=<region>  # 例如 eastus、westus2、westeurope

# 替代做法：直接用 endpoint
AZURE_SPEECH_ENDPOINT=https://<region>.stt.speech.microsoft.com
```

## 安裝

```bash
pip install requests
```

## 驗證與生命週期

> **🔑 下面每個程式碼範例都適用兩條規則：**
>
> 1. **支援兩種驗證模式。** 想快速存取就用 subscription key（`Ocp-Apim-Subscription-Key` header），或是透過 `Authorization` request header 帶 Microsoft Entra token（包含用 `DefaultAzureCredential` 取得的 token），見下面的「Option 2」。絕對不要把憑證寫死在原始碼裡。
> 2. **檔案和 HTTP 資源都用 context manager**，這樣檔案 handle 和網路連線才會確實釋放：
>    - 同步：`with open(...) as f:`，要重複使用連線時再加 `with requests.Session() as session:`
>    - 非同步：`async with aiohttp.ClientSession() as session:`
>
> 範例片段可能會簡化這段設定，但 production 的程式碼一定要兩條規則都遵守。

## 快速開始

```python
import os
import requests

def transcribe_audio(audio_file_path: str, language: str = "en-US") -> dict:
    """Transcribe short audio file (max 60 seconds) using REST API."""
    region = os.environ["AZURE_SPEECH_REGION"]
    api_key = os.environ["AZURE_SPEECH_KEY"]
    
    url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json"
    }
    
    params = {
        "language": language,
        "format": "detailed"  # 或 "simple"
    }
    
    with open(audio_file_path, "rb") as audio_file:
        response = requests.post(url, headers=headers, params=params, data=audio_file)
    
    response.raise_for_status()
    return response.json()

# 用法
result = transcribe_audio("audio.wav", "en-US")
print(result["DisplayText"])
```

## 音訊需求

| 格式 | Codec | 取樣率 | 備註 |
|--------|-------|-------------|-------|
| WAV | PCM | 16 kHz、單聲道 | **建議使用** |
| OGG | OPUS | 16 kHz、單聲道 | 檔案比較小 |

**限制：**
- 音訊最長 60 秒
- 發音評估：最長 30 秒
- 沒有部分／中間結果（只有最終結果）

## Content-Type Header

```python
# WAV PCM 16kHz
wav_headers = {
    "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000"
}

# OGG OPUS
ogg_headers = {
    "Content-Type": "audio/ogg; codecs=opus"
}
```

## 回應格式

### Simple 格式（預設）

```python
params = {"language": "en-US", "format": "simple"}
```

```json
{
  "RecognitionStatus": "Success",
  "DisplayText": "Remind me to buy 5 pencils.",
  "Offset": "1236645672289",
  "Duration": "1236645672289"
}
```

### Detailed 格式

```python
params = {"language": "en-US", "format": "detailed"}
```

```json
{
  "RecognitionStatus": "Success",
  "Offset": "1236645672289",
  "Duration": "1236645672289",
  "NBest": [
    {
      "Confidence": 0.9052885,
      "Display": "What's the weather like?",
      "ITN": "what's the weather like",
      "Lexical": "what's the weather like",
      "MaskedITN": "what's the weather like"
    }
  ]
}
```

## Chunked Transfer（建議使用）

想要更低的延遲，就把音訊分 chunk 串流：

```python
import os
import requests

def transcribe_chunked(audio_file_path: str, language: str = "en-US") -> dict:
    """Stream audio in chunks for lower latency."""
    region = os.environ["AZURE_SPEECH_REGION"]
    api_key = os.environ["AZURE_SPEECH_KEY"]
    
    url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json",
        "Transfer-Encoding": "chunked",
        "Expect": "100-continue"
    }
    
    params = {"language": language, "format": "detailed"}
    
    def generate_chunks(file_path: str, chunk_size: int = 1024):
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk
    
    response = requests.post(
        url, 
        headers=headers, 
        params=params, 
        data=generate_chunks(audio_file_path)
    )
    
    response.raise_for_status()
    return response.json()
```

## 驗證選項

### Option 1：Subscription Key（簡單）

```python
headers = {
    "Ocp-Apim-Subscription-Key": os.environ["AZURE_SPEECH_KEY"]
}
```

### Option 2：Bearer Token

```python
import requests
import os

def get_access_token() -> str:
    """Get access token from the token endpoint."""
    region = os.environ["AZURE_SPEECH_REGION"]
    api_key = os.environ["AZURE_SPEECH_KEY"]
    
    token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    
    response = requests.post(
        token_url,
        headers={
            "Ocp-Apim-Subscription-Key": api_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "0"
        }
    )
    response.raise_for_status()
    return response.text

# 在 request 裡使用 token（有效期 10 分鐘）
token = get_access_token()
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
    "Accept": "application/json"
}
```

## Query 參數

| 參數 | 必填 | 值 | 說明 |
|-----------|----------|--------|-------------|
| `language` | **是** | `en-US`、`de-DE` 等 | 語音的語言 |
| `format` | 否 | `simple`、`detailed` | 結果格式（預設：simple） |
| `profanity` | 否 | `masked`、`removed`、`raw` | 髒話處理方式（預設：masked） |

## Recognition Status 值

| 狀態 | 說明 |
|--------|-------------|
| `Success` | 辨識成功 |
| `NoMatch` | 偵測到語音，但沒有符合的字詞 |
| `InitialSilenceTimeout` | 只偵測到靜音 |
| `BabbleTimeout` | 只偵測到雜訊 |
| `Error` | 服務內部錯誤 |

## 髒話處理

```python
# 用星號遮蔽髒話（預設）
params = {"language": "en-US", "profanity": "masked"}

# 完全移除髒話
params = {"language": "en-US", "profanity": "removed"}

# 原樣保留髒話
params = {"language": "en-US", "profanity": "raw"}
```

## 錯誤處理

```python
import requests

def transcribe_with_error_handling(audio_path: str, language: str = "en-US") -> dict | None:
    """Transcribe with proper error handling."""
    region = os.environ["AZURE_SPEECH_REGION"]
    api_key = os.environ["AZURE_SPEECH_KEY"]
    
    url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    try:
        with open(audio_path, "rb") as audio_file:
            response = requests.post(
                url,
                headers={
                    "Ocp-Apim-Subscription-Key": api_key,
                    "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
                    "Accept": "application/json"
                },
                params={"language": language, "format": "detailed"},
                data=audio_file
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("RecognitionStatus") == "Success":
                return result
            else:
                print(f"Recognition failed: {result.get('RecognitionStatus')}")
                return None
        elif response.status_code == 400:
            print(f"Bad request: Check language code or audio format")
        elif response.status_code == 401:
            print(f"Unauthorized: Check API key or token")
        elif response.status_code == 403:
            print(f"Forbidden: Missing authorization header")
        else:
            print(f"Error {response.status_code}: {response.text}")
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
```

## 非同步版本

```python
import os
import aiohttp
import asyncio

async def transcribe_async(audio_file_path: str, language: str = "en-US") -> dict:
    """Async version using aiohttp."""
    region = os.environ["AZURE_SPEECH_REGION"]
    api_key = os.environ["AZURE_SPEECH_KEY"]
    
    url = f"https://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json"
    }
    
    params = {"language": language, "format": "detailed"}
    
    async with aiohttp.ClientSession() as session:
        with open(audio_file_path, "rb") as f:
            audio_data = f.read()
        
        async with session.post(url, headers=headers, params=params, data=audio_data) as response:
            response.raise_for_status()
            return await response.json()

# 用法
result = asyncio.run(transcribe_async("audio.wav", "en-US"))
print(result["DisplayText"])
```

## 支援的語言

常用的語言代碼（[完整清單](https://learn.microsoft.com/azure/ai-services/speech-service/language-support)）：

| 代碼 | 語言 |
|------|----------|
| `en-US` | 英文（美國） |
| `en-GB` | 英文（英國） |
| `de-DE` | 德文 |
| `fr-FR` | 法文 |
| `es-ES` | 西班牙文（西班牙） |
| `es-MX` | 西班牙文（墨西哥） |
| `zh-CN` | 中文（普通話） |
| `ja-JP` | 日文 |
| `ko-KR` | 韓文 |
| `pt-BR` | 葡萄牙文（巴西） |

## 最佳實務

1. **同步或非同步選一個，然後保持一致。** 同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 只選一種模式。
2. **檔案和 HTTP 資源都用 context manager。** 同步程式碼用 `with open(...) as f:`，要重複使用連線時再加 `with requests.Session() as session:`；非同步程式碼用 `async with aiohttp.ClientSession() as session:`。
3. **用 WAV PCM 16kHz 單聲道**，相容性最好
4. **啟用 chunked transfer**，延遲比較低
5. **快取 access token** 9 分鐘（有效期是 10 分鐘）
6. **指定正確的語言**，辨識才會準
7. 需要信心分數時**用 detailed 格式**
8. production 程式碼要**處理所有的 RecognitionStatus 值**

## 什麼時候不要用這個 API

遇到下列需求，請改用 Speech SDK 或 Batch Transcription API：

- 音訊超過 60 秒
- 即時串流轉錄
- 部分／中間結果
- 語音翻譯
- 自訂語音模型
- 批次轉錄大量檔案

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/pronunciation-assessment.md](references/pronunciation-assessment.md) | 發音評估的參數和評分 |
