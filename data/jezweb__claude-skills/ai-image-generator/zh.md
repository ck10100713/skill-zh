---
name: ai-image-generator
description: "直接呼叫 Gemini 或 GPT API 產生 AI 圖片。涵蓋模型選擇（場景用 Gemini；文字渲染、批次變體、多參考圖合成用 GPT Image 2；透明圖示用 GPT Image 1.5）、5 段式 prompt 框架、API 呼叫寫法、多輪編輯和品質檢查。可產出擬真場景、圖示、插畫、OG 圖片、海報、資訊圖和產品照。建網站需要圖片、製作行銷素材或產生視覺內容時使用。觸發詞：'generate image', 'ai image', 'create hero image', 'make an icon', 'generate illustration', 'create og image', 'poster', 'infographic', 'image variations', 'gpt-image-2', 'ai art', 'image generation'。"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
compatibility: claude-code-only
---

# AI Image Generator

用 AI API（Google Gemini 和 OpenAI GPT）產生圖片。這個 skill 教的是 prompt 寫法和 API 運作細節，讓你直接在 Claude Code 裡產出專業的圖片。

> **託管替代方案**：如果你不想自己管理 API key，[ImageBot](https://imagebot.au) 提供託管的圖片生成服務，附相簿範本和品牌素材包支援。

## 模型選擇

依工作選對模型：

| 需求 | 模型 | 原因 |
|------|-------|-----|
| **擬真場景 / 圖庫風格照片** | Gemini 3.1 Flash Image | 景深、複雜度和環境脈絡最好 |
| **最終交給客戶的場景（要更多細節）** | Gemini 3 Pro Image | 細節更多，風格一致性更好 |
| **圖片上的文字**（海報、帶文案的 OG、資訊圖） | GPT Image 2 | 文字渲染真的能用，包括多種文字系統 |
| **10 種變體的風格探索** | GPT Image 2 | 原生批次：一個 prompt 產出 10 個共用構圖和配色的變體 |
| **多參考圖合成**（產品 + 生活情境） | GPT Image 2 | 能處理跨參考圖的光線、比例和透視 |
| **透明圖示 / logo** | GPT Image 1.5 | 原生 RGBA alpha，**GPT Image 2 做不到透明** |
| **快速草稿 / 反覆調整** | Gemini 2.5 Flash Image | 免費額度（每天約 500 張） |

**經驗法則**：任何帶有可讀文字的圖片 → GPT Image 2（除非需要透明，那就用 GPT 1.5）。其他情況 → Gemini。

### 模型 ID

| 模型 | API ID | 供應商 |
|-------|--------|----------|
| Gemini 3.1 Flash Image | `gemini-3.1-flash-image-preview` | Google AI |
| Gemini 3 Pro Image | `gemini-3-pro-image-preview` | Google AI |
| Gemini 2.5 Flash Image | `gemini-2.5-flash-image` | Google AI |
| GPT Image 2（預設） | `gpt-image-2` | OpenAI |
| GPT Image 2（與 ChatGPT 輸出一致） | `chatgpt-image-latest` | OpenAI |
| GPT Image 1.5（只用於透明） | `gpt-image-1.5` | OpenAI |

**使用前先確認模型 ID**，它們常常更動：
```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin)['models'] if 'image' in m['name'].lower()]"
```

## GPT Image 2 的特點

2026-04-22 發布。有三項能力，會改變你什麼時候該選它。

### 1. 文字渲染真的能用

海報、帶標題的 OG 圖片、帶標籤的資訊圖、UI mockup、價格卡片。文字能穩定渲染，包括非拉丁文字（日文、韓文、印地語、孟加拉語）。這是從 Gemini 換過來的主要原因，Gemini 完全渲染不出可讀的文字。

### 2. 多變體批次產生

一個 prompt，一次呼叫最多 10 張圖。變體共用構圖和配色，但細節不同。適合在定案前做風格探索、給客戶 A/B 選項，以及快速發想。

### 3. 多參考圖合成

連同 prompt 一起餵參考圖，像是產品照、生活場景、logo。模型會用正確的光線、比例和透視，把產品放進場景裡。不用多輪編輯就能做「產品放進實際情境」的流程。

### 模式

- **Instant**（預設，所有方案）：不經規劃階段直接生成。快，對大多數情況夠用。
- **Thinking**（Plus/Pro/Business 方案）：先規劃版面再畫。元素數量重要（「一排 3 個圖示」、「5 個功能重點」）或文字必須落在特定區域時使用。複雜構圖需要重抽的次數比較少。

### 長寬比

從 3:1 超寬到 1:3 超高，加上 1:1、3:2、2:3、16:9、9:16。範圍比其他模型寬，適合網站 banner（超寬 hero）或手機限時動態格式（超高）。

### 解析度

標準最高長邊 2K。4K 為 beta。

### 生成時間

**複雜的 prompt 最多要 2 分鐘。**要做非同步的使用者體驗，不要卡住等回應。顯示進度，或丟到背景再輪詢。

### 限制

- **不支援透明背景。**需要 PNG 透明時，退回用 `gpt-image-1.5`。
- 在端點能呼叫之前，**可能需要通過 API 組織驗證**：第一次呼叫遇到授權錯誤的話，到 OpenAI 帳號設定裡啟用。

### 價格（每張 1024×1024 圖片）

| 品質 | 費用 |
|---------|------|
| Low | $0.006 |
| Medium | $0.053 |
| High | $0.211 |

Token 計價：文字輸入 $5/M、文字輸出 $10/M、圖片輸入 $8/M、圖片輸出 $30/M。

## 5 段式 Prompt 框架

照這個順序組 prompt，結果會比較穩定：

### 1. 圖片類型
先定類型：「A photorealistic photograph」、「An isometric illustration」、「A flat vector icon」

### 2. 主體
是誰或是什麼，附上具體細節：「of a warm, approachable Australian woman in her early 30s, smiling naturally」

### 3. 環境
場景和空間關係：「in a bright modern home with terracotta decor on wooden shelves behind her」

### 4. 技術規格
相機和光線：「Shot at 85mm f/2.0, natural window light, head and shoulders framing」

### 5. 限制
要排除什麼：「Photorealistic, no text, no watermarks, no logos」

### 範例（好 vs 壞）

```
BAD — keyword soup:
"professional woman, spa, warm lighting, high quality, 4K"

GOOD — narrative direction:
"A professional skin treatment scene in a warm clinical setting.
A practitioner wearing blue medical gloves uses a microneedling pen
on the client's forehead. The client lies on a white treatment bed,
eyes closed, relaxed. Warm golden-hour light from a window to the
left. Terracotta-toned wall visible in the background. Shot at
85mm f/2.0, shallow depth of field. No text, no watermarks."
```

## 工作流程

### 1. 判斷圖片需求

| 用途 | 長寬比 | 模型 |
|---------|-------------|-------|
| Hero banner（無文字） | 16:9 或 21:9 | Gemini |
| 帶標題文案的 hero banner | 16:9 或 3:1 超寬 | GPT Image 2 |
| 服務卡片 | 4:3 或 3:4 | Gemini |
| 個人檔案 / 頭像 | 1:1 | Gemini |
| 圖示 / 徽章（透明） | 1:1 | GPT Image 1.5 |
| OG / 社群分享（無文字） | 1.91:1 | Gemini |
| 帶文案的 OG / 社群分享 | 1.91:1 | GPT Image 2 |
| 海報 / 資訊圖 / 價格卡片 / 任何以文字排版為主的 | 不一定 | GPT Image 2 |
| 風格探索（同一個概念的 10 種變體） | 任何 | GPT Image 2（批次） |
| Instagram 貼文 | 1:1 或 4:5 | Gemini |
| 手機 hero | 9:16 | Gemini |

### 2. 組 Prompt

用 5 段式框架。詳細的攝影參數見 `references/prompting-guide.md`。

### 3. 透過 API 生成

#### Gemini（Python，能正確處理 shell 跳脫）

```python
python3 << 'PYEOF'
import json, base64, urllib.request, os, sys

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Set GEMINI_API_KEY environment variable"); sys.exit(1)

model = "gemini-3.1-flash-image-preview"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

prompt = """A professional photograph of a modern co-working space in
Newcastle, Australia. Natural light floods through floor-to-ceiling
windows. Three people collaborate at a standing desk — one pointing
at a laptop screen. Exposed brick wall, potted fiddle-leaf fig,
coffee cups on the desk. Shot at 35mm f/4.0, environmental portrait
style. No text, no watermarks, no logos."""

payload = json.dumps({
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"],
        "temperature": 0.8
    }
}).encode()

req = urllib.request.Request(url, data=payload, headers={
    "Content-Type": "application/json",
    "User-Agent": "ImageGen/1.0"
})

resp = urllib.request.urlopen(req, timeout=120)
result = json.loads(resp.read())

# Extract image from response
for part in result["candidates"][0]["content"]["parts"]:
    if "inlineData" in part:
        img_data = base64.b64decode(part["inlineData"]["data"])
        output_path = "hero-image.png"
        with open(output_path, "wb") as f:
            f.write(img_data)
        print(f"Saved: {output_path} ({len(img_data):,} bytes)")
        break
PYEOF
```

#### GPT Image 1.5：透明圖示

專門在需要透明 PNG 的情況下用 `gpt-image-1.5`。GPT Image 2 做不到透明。

```python
python3 << 'PYEOF'
import json, base64, urllib.request, os, sys

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Set OPENAI_API_KEY environment variable"); sys.exit(1)

url = "https://api.openai.com/v1/images/generations"

payload = json.dumps({
    "model": "gpt-image-1.5",
    "prompt": "A minimal, clean plumbing wrench icon. Flat design, single consistent stroke weight, modern style. On a transparent background.",
    "n": 1,
    "size": "1024x1024",
    "background": "transparent",
    "output_format": "png"
}).encode()

req = urllib.request.Request(url, data=payload, headers={
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
})

resp = urllib.request.urlopen(req, timeout=120)
result = json.loads(resp.read())

img_data = base64.b64decode(result["data"][0]["b64_json"])
with open("icon-wrench.png", "wb") as f:
    f.write(img_data)
print(f"Saved: icon-wrench.png ({len(img_data):,} bytes)")
PYEOF
```

#### GPT Image 2：文字很多或批次變體

文字必須渲染得可讀，或想一次呼叫拿到 10 個變體時，用 `gpt-image-2`。**不支援透明**，需要透明背景就用上面的 1.5。

```python
python3 << 'PYEOF'
import json, base64, urllib.request, os, sys, pathlib

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Set OPENAI_API_KEY environment variable"); sys.exit(1)

url = "https://api.openai.com/v1/images/generations"

# 10-variation batch of a pricing card with rendered text
payload = json.dumps({
    "model": "gpt-image-2",
    "prompt": (
        "A modern pricing card for a web hosting plan. "
        "Headline 'Starter' in bold sans-serif. "
        "Price '$29/month' directly below in large type. "
        "Three feature lines: 'Unlimited bandwidth', 'SSD storage', 'Free SSL'. "
        "Clean flat design, soft drop shadow, deep blue accent colour. "
        "White card on light grey background."
    ),
    "n": 10,
    "size": "1024x1024",
    "quality": "medium",
    "output_format": "png"
}).encode()

req = urllib.request.Request(url, data=payload, headers={
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
})

# Timeout: up to 2 min for complex prompts
resp = urllib.request.urlopen(req, timeout=180)
result = json.loads(resp.read())

pathlib.Path("variations").mkdir(exist_ok=True)
for i, item in enumerate(result["data"], 1):
    img_data = base64.b64decode(item["b64_json"])
    path = f"variations/pricing-card-{i:02d}.png"
    with open(path, "wb") as f:
        f.write(img_data)
    print(f"Saved: {path} ({len(img_data):,} bytes)")

print(f"\nGenerated {len(result['data'])} variants. Pick the best; delete the rest.")
PYEOF
```

**批次流程**：生成 10 張 → 並排檢視 → 挑 1 到 2 張 → 視需要針對勝出的方向用更精準的 prompt 重新生成。比單張生成再反覆調整更快。

### 4. 儲存與最佳化

把生成的圖片存到 `.jez/artifacts/` 或使用者指定的路徑。

後處理（選用）：
```bash
# Convert to WebP for web use
python3 -c "
from PIL import Image
img = Image.open('hero-image.png')
img.save('hero-image.webp', 'WEBP', quality=85)
print(f'WebP: {img.size[0]}x{img.size[1]}')
"

# Trim whitespace from transparent icons
python3 -c "
from PIL import Image
img = Image.open('icon.png')
trimmed = img.crop(img.getbbox())
trimmed.save('icon-trimmed.png')
"
```

### 5. 品質檢查（選用）

把生成的圖片送回視覺模型做 QA：

```python
# Send to Gemini Flash for critique
critique_prompt = """Review this image for:
1. AI artifacts (extra fingers, floating objects, text errors)
2. Technical accuracy (wrong equipment, unsafe positioning)
3. Composition issues (awkward cropping, cluttered background)
4. Style consistency with a professional stock photo

List any issues found, or say 'PASS' if the image is production-ready."""
```

發現問題的話，把它們當成負面指引附加到原本的 prompt，重新生成。

## 多輪編輯

Gemini 支援跨對話輪次編輯已生成的圖片。關鍵要求：**保留模型回應裡的 thought signature**。

```python
# Turn 1: Generate base image
contents = [{"role": "user", "parts": [{"text": "Scene prompt..."}]}]

# The response includes thoughtSignature on parts — preserve them ALL

# Turn 2: Edit the image
contents = [
    {"role": "user", "parts": [{"text": "Original prompt"}]},
    {"role": "model", "parts": response_parts_with_signatures},  # Keep intact
    {"role": "user", "parts": [{"text": "Edit: change the wall colour to blue. Keep everything else exactly the same."}]}
]
```

**編輯 prompt 的寫法**：一定要寫明什麼要「保持不變」，不能只寫要改什麼。模型會把沒列出來的元素當成可以隨意更動。

```
GOOD: "Edit this image: keep the people, desk, and window unchanged.
Only change: wall colour from terracotta to ocean blue."

BAD: "Now make the wall blue."
(Model may change everything else too)
```

## API Key 設定

| 供應商 | 取得 key 的地方 | 環境變數 |
|----------|-----------|-------------|
| Google Gemini | [aistudio.google.com](https://aistudio.google.com/apikey) | `GEMINI_API_KEY` |
| OpenAI | [platform.openai.com](https://platform.openai.com/api-keys) | `OPENAI_API_KEY` |

```bash
export GEMINI_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

## 常見錯誤

| 錯誤 | 解法 |
|---------|-----|
| Gemini 的 prompt 用 curl 送 | 改用 Python，shell 跳脫遇到單引號會壞掉 |
| 「Beautiful, professional, high quality」 | 用具體規格：「85mm f/1.8, golden hour light」 |
| 沒有指定要排除什麼 | 一律以「No text, no watermarks, no logos」結尾 |
| 向 Gemini 要透明 PNG | Gemini 做不到透明，改用 GPT Image 1.5 搭配 `background: "transparent"` |
| 向 GPT Image 2 要透明 PNG | GPT Image 2 **做不到透明**，只有這個情況才退回 `gpt-image-1.5` |
| 用 GPT Image 1.5 生成帶文字的圖 | GPT Image 1.5 的文字渲染不可靠，任何要可讀文字的都用 `gpt-image-2` |
| 阻塞式呼叫 GPT Image 2 | 複雜 prompt 的生成最多要 2 分鐘，用 180 秒的 timeout，並做非同步的使用者體驗 |
| 澳洲商家卻用美國預設值 | 明確指定「Australian」加上當地的建築、植被 |
| 用籠統的資料當模型 ID | 確認目前有效的模型 ID，它們常常更動 |
