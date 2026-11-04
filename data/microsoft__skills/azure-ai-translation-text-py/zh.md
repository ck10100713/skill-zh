---
name: azure-ai-translation-text-py
description: |
  Azure AI Text Translation SDK，用於即時文字翻譯、音譯、語言偵測和字典查詢。適合在應用程式裡翻譯文字內容。
  Triggers: "text translation", "translator", "translate text", "transliterate", "TextTranslationClient".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-translation-text
---

# Azure AI Text Translation SDK for Python

Azure AI Translator 文字翻譯服務的 client library，用於即時文字翻譯、音譯和各種語言操作。

## Installation

```bash
pip install azure-ai-translation-text
```

## Environment Variables

```bash
AZURE_TRANSLATOR_ENDPOINT=https://<resource>.cognitiveservices.azure.com  # Entra ID 驗證需要（必須是自訂子網域 endpoint）
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
# 只有下面舊版 API key 驗證路徑才需要：
AZURE_TRANSLATOR_KEY=<your-api-key>
AZURE_TRANSLATOR_REGION=<your-region>  # 例如 eastus、westus2；用 key 連全域 endpoint 時必填
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
from azure.ai.translation.text import TextTranslationClient

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用指定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with TextTranslationClient(
    endpoint=os.environ["AZURE_TRANSLATOR_ENDPOINT"],
    credential=credential,
) as client:
    result = client.translate(body=["Hello, world!"], to=["es"])
```

### Legacy: API Key (existing keyed deployments)

新程式碼請用上面的 `DefaultAzureCredential`。Translator 服務有兩個特殊狀況，讓 API key 驗證在既有部署中仍然很常見：

- **Token credential 驗證需要自訂子網域 endpoint**（`https://<resource>.cognitiveservices.azure.com`）。如果你只有全域 endpoint（`https://api.cognitive.microsofttranslator.com`），就得先建立自訂子網域，在那之前只能繼續用 key 的路徑。
- **Key + region** 是連全域 endpoint 的標準設定。region 會以 `Ocp-Apim-Subscription-Region` header 送出，只要用多服務或全域的 Translator key 就必填。

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.text import TextTranslationClient

# 對全域 endpoint 使用 key + region（最常見的 key 設定）
with TextTranslationClient(
    credential=AzureKeyCredential(os.environ["AZURE_TRANSLATOR_KEY"]),
    region=os.environ["AZURE_TRANSLATOR_REGION"],
) as client:
    result = client.translate(body=["Hello, world!"], to=["es"])

# 對自訂子網域 endpoint 使用 key（不需要 region）
with TextTranslationClient(
    endpoint=os.environ["AZURE_TRANSLATOR_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_TRANSLATOR_KEY"]),
) as client:
    result = client.translate(body=["Hello, world!"], to=["es"])
```

## Basic Translation

```python
# 翻成單一語言
result = client.translate(
    body=["Hello, how are you?", "Welcome to Azure!"],
    to=["es"]  # 西班牙文
)

for item in result:
    for translation in item.translations:
        print(f"Translated: {translation.text}")
        print(f"Target language: {translation.to}")
```

## Translate to Multiple Languages

```python
result = client.translate(
    body=["Hello, world!"],
    to=["es", "fr", "de", "ja"]  # 西班牙文、法文、德文、日文
)

for item in result:
    print(f"Source: {item.detected_language.language if item.detected_language else 'unknown'}")
    for translation in item.translations:
        print(f"  {translation.to}: {translation.text}")
```

## Specify Source Language

```python
result = client.translate(
    body=["Bonjour le monde"],
    from_parameter="fr",  # 來源是法文
    to=["en", "es"]
)
```

## Language Detection

```python
result = client.translate(
    body=["Hola, como estas?"],
    to=["en"]
)

for item in result:
    if item.detected_language:
        print(f"Detected language: {item.detected_language.language}")
        print(f"Confidence: {item.detected_language.score:.2f}")
```

## Transliteration

把文字從一種文字系統轉成另一種：

```python
result = client.transliterate(
    body=["konnichiwa"],
    language="ja",
    from_script="Latn",  # 從拉丁字母
    to_script="Jpan"      # 轉成日文文字
)

for item in result:
    print(f"Transliterated: {item.text}")
    print(f"Script: {item.script}")
```

## Dictionary Lookup

查詢其他譯法和定義：

```python
result = client.lookup_dictionary_entries(
    body=["fly"],
    from_parameter="en",
    to="es"
)

for item in result:
    print(f"Source: {item.normalized_source} ({item.display_source})")
    for translation in item.translations:
        print(f"  Translation: {translation.normalized_target}")
        print(f"  Part of speech: {translation.pos_tag}")
        print(f"  Confidence: {translation.confidence:.2f}")
```

## Dictionary Examples

取得譯文的用法範例：

```python
from azure.ai.translation.text.models import DictionaryExampleTextItem

result = client.lookup_dictionary_examples(
    body=[DictionaryExampleTextItem(text="fly", translation="volar")],
    from_parameter="en",
    to="es"
)

for item in result:
    for example in item.examples:
        print(f"Source: {example.source_prefix}{example.source_term}{example.source_suffix}")
        print(f"Target: {example.target_prefix}{example.target_term}{example.target_suffix}")
```

## Get Supported Languages

```python
# 取得所有支援的語言
languages = client.get_supported_languages()

# 翻譯語言
print("Translation languages:")
for code, lang in languages.translation.items():
    print(f"  {code}: {lang.name} ({lang.native_name})")

# 音譯語言
print("\nTransliteration languages:")
for code, lang in languages.transliteration.items():
    print(f"  {code}: {lang.name}")
    for script in lang.scripts:
        print(f"    {script.code} -> {[t.code for t in script.to_scripts]}")

# 字典語言
print("\nDictionary languages:")
for code, lang in languages.dictionary.items():
    print(f"  {code}: {lang.name}")
```

## Break Sentence

找出句子邊界：

```python
result = client.find_sentence_boundaries(
    body=["Hello! How are you? I hope you are well."],
    language="en"
)

for item in result:
    print(f"Sentence lengths: {item.sent_len}")
```

## Translation Options

```python
result = client.translate(
    body=["Hello, world!"],
    to=["de"],
    text_type="html",           # "plain" 或 "html"
    profanity_action="Marked",  # "NoAction", "Deleted", "Marked"
    profanity_marker="Asterisk", # "Asterisk", "Tag"
    include_alignment=True,      # 包含字詞對齊
    include_sentence_length=True # 包含句子邊界
)

for item in result:
    translation = item.translations[0]
    print(f"Translated: {translation.text}")
    if translation.alignment:
        print(f"Alignment: {translation.alignment.proj}")
    if translation.sent_len:
        print(f"Sentence lengths: {translation.sent_len.src_sent_len}")
```

## Async Client

```python
from azure.ai.translation.text.aio import TextTranslationClient
from azure.identity.aio import DefaultAzureCredential

async def translate_text():
    async with DefaultAzureCredential() as credential:
        async with TextTranslationClient(
            credential=credential,
            endpoint=endpoint,
        ) as client:
            result = await client.translate(
                body=["Hello, world!"],
                to=["es"]
            )
            print(result[0].translations[0].text)
```

## Client Methods

| Method | Description |
|--------|-------------|
| `translate` | 把文字翻成一種或多種語言 |
| `transliterate` | 在不同文字系統之間轉換文字 |
| `detect` | 偵測文字的語言 |
| `find_sentence_boundaries` | 找出句子邊界 |
| `lookup_dictionary_entries` | 查字典取得譯法 |
| `lookup_dictionary_examples` | 取得用法範例 |
| `get_supported_languages` | 列出支援的語言 |

## Best Practices

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **批次翻譯**：一個 request 送多段文字（最多 100 段）
4. **已知來源語言就指定**，可以提高準確度
5. **高吞吐量情境用非同步 client**
6. **快取語言清單**：支援的語言不會常常變
7. **依照你的應用程式需求適當處理**髒話
8. **翻譯 HTML 內容時用 html text_type**
9. **需要字詞對應的應用程式要開 alignment**

## Reference Files

| File | Contents |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打功能、operation group 涵蓋範圍，以及 production 檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要與進階情境的專屬非主打範例。 |
