---
name: taste
description: 給音樂影片和短影音剪輯用的創意方向層，專攻 angelcore / cloud-trance / hyperpop 這一系：有一套命名風格的美學詞彙、情緒＋色彩＋光線系統、對拍剪輯語法，還有一條把 ECC 各個影片 skill 串起來的流程，從 b-roll 生成一路到發布。當影片要看起來是有意為之、而不只是堪用時就用：音樂影片、fancam、以情緒板為底的 reels，或是想幫 AI 生成的 b-roll 找一個一致的視覺方向。
origin: ECC
---

# Taste

大部分 AI 影片的建議只講到*怎麼 render 畫面*。這個 skill 是它上面那一層：
**畫面該長什麼樣、用什麼順序、切在什麼節奏上，成品才會是一個有意圖的整體，而不是一堆生成結果的堆疊。**

它收錄的是一種特定的品味：**angelcore / cloud-trance / hyperpop** 這一系
（Bladee「Silver Surfer」時期的空靈 trance，混上厚重的 angelcore），
是從一批收藏的 Reels，加上逛過約 70 個條目的視覺風格庫提煉出來的。
它刻意有立場。品味是一種觀點，不是菜單。

> 配套檔案 `references/genre-taxonomy.md` 放了完整的命名風格目錄。
> 這個檔案是可以直接動手的那一層：情緒、語法、流程，還有一份對拍的鏡頭計畫。

## 何時啟用

- 製作**音樂影片**、歌詞影片、fancam 或 visualizer。
- 做短影音的**剪輯 / reel**，而且重點是*感覺*，不是資訊。
- 驅動 **AI b-roll 生成**（fal.ai、Veo、Kling 等），prompt 需要一個一致的方向，而不是各自為政的氛圍。
- 在任何 render 之前，組一份**情緒板**或挑視覺風格。
- 使用者說「taste」、「讓它感覺像 X」、「給它一個方向」、「angelcore」、
  「cloud trance」、「hyperpop edit」、「Bladee」、「dreamcore」，或是點名某個收藏的參考。
- 目前的剪輯堪用，但看起來平、很通用、像 AI 垃圾，或是風格前後不一致。

這個 skill 站在 `video-editing`（機制面）和 `remotion-video-creation`（渲染器）**之上**。
*怎麼做*用那兩個，*做什麼、為什麼*用這個。

## 核心主張

1. **Taste 是最後一層，但必須最先決定。** `video-editing` 說得沒錯，
   品味是最後的人工把關。陷阱在於：如果到最後才決定品味，前面每一次生成、每一刀都是在猜。
   在第一個 prompt 之前就選好方向，再讓它去約束所有東西。
2. **一致性勝過新鮮感。** 一個外觀貫穿 30 個鏡頭，贏過 30 種外觀。
   一個命名風格（見下）就是一種約束，白送你一致性。
3. **對著歌剪，不要對著素材剪。** 音樂影片的時間軸就是波形。
   每一個硬切都要落在拍點或 transient 上。畫格的計算在流程那一節。
4. **選擇性地生成，狠狠地剪。** AI 能做出不存在的 b-roll，
   但做不出品味。你還是得丟掉 80%。

## 美學詞彙（提煉版）

參考素材庫涵蓋大量*有命名*的視覺風格，完整清單在
`references/genre-taxonomy.md`。有用的做法不是背 70 個名字，而是看出
**一個風格名稱就是一整套 prompt 加調色的預設。** 你選了一個，
它的色盤、質感、打光和主題就整組繼承過來。

風格會聚成幾個家族。挑一個**主**家族，最多再加**一個**點綴：

| 家族 | 屬於這個家族的風格 | 給人的感覺 |
|--------|-------------|----------|
| **Ethereal / divine** | spiritualism、glacial folk、beacons、zen core、fairy tale | 失重、神聖、發光、柔 |
| **Hyperpop / Y2K-cyber** | cyberdelia、acid house、acid nora、neo aggressano、new liquid | 亮面、鉻金屬、霓虹、kawaii-cyber |
| **Dark / occult** | dark academia、smoke nostalgia、communist core、abstract tech | 高反差、不祥、顆粒感 |
| **Retro / print** | retro surfers、art deco、adventure pulp、classic advertising、magazine collage、bumper stickers | 平面、圖像化、半色調、懷舊 |
| **Organic / textural** | microbiology core、weaving patterns、fruitage retro、cozy blanket、pacific punk wave | 觸感、微距、編織、濕潤 |
| **Systemic / data** | numbers、mazes、code web、heatmap、pixel、8-bit | 網格、生成式、示意圖 |

**以目前這個專案來說**，主家族是 **Ethereal / divine**，點綴是 **Hyperpop / Y2K-cyber**，
也就是神聖的光和結晶般的綻放，間或點上鉻金屬和霓虹。這個組合
*就是* angelcore × cloud-trance 的 brief。

## 情緒系統：angelcore × cloud-trance

直接從最強的幾支參考 reels 提煉出來。這是具體的調色方案。

### 色盤
- **基底：** 近乎全黑的虛空（#05060a）和骨白（#f4f1ea）。大多數畫面不是這個就是那個。
- **神聖點綴：** 熔金 / 餘燼橘（#ffb24d → #ff7a18），是黑暗裡*唯一的暖光*。
- **結晶點綴：** 虹彩的紫→青→洋紅 bokeh（#8a6bff、#4fc3ff、#ff6ad5），
  是 hyperpop 的綻放，用在明亮的畫面。
- **危險點綴（要節制）：** 單色畫面上一點發光的紅（#ff2a2a），
  只留給一兩個震撼切點。
- **Hyperpop 主體：** 糖果粉頭髮 / 鉻金屬 / 亮白，襯著藍天。

規則：**每個鏡頭只有一個點綴色。** 金色待在暗的畫面，虹彩待在亮的畫面，
同一個鏡頭絕對不要兩個都出現。

### 光線與質感
- 黑暗被單一暖光源刺穿（餘燼綻放、神聖光束）。高反差、深黑。
- 結晶 / 亮片 bokeh、鏡頭光暈、bloom、漏光，要*天堂感*，不要髒。
- 暗的畫面加底片顆粒和輕微色差，亮的畫面保持乾淨的亮面。
- 在留白處放微距細節：一個主角物件置中在黑底上（鑰匙、眼睛、齒輪、花瓣、水）。
- 主題：有翼的人影、雲、光環、天使、結晶結構、糖果賽博肖像。

### 運動
- 緩慢、漂浮、失重的鏡頭（漂移、慢推、慢繞），這才是 *cloud* trance。
- 只有在 drop 才爆發速度。其他時候一切都在呼吸。
- 粒子往上飄（餘燼、灰塵、亮片），往上的運動等於升天。

## 剪輯語法（提煉版）

從參考剪輯裡歸納出反覆出現、定義這個風格的手法：

1. **鎖拍的硬切。** verse / drop 不用溶接。切在 kick 上。眼睛要能
   感覺到 BPM。
2. **黑底微距主角插入。** 單一銳利的物件置中在黑色留白裡，
   撐 1 到 2 拍就切。把這些做成節奏蒙太奇，就是 cloud-trance 的招牌。
3. **Bloom / 爆炸揭示。** 白色或餘燼色的 bloom 在 transient 上把畫面炸白，
   然後解析成下一個鏡頭。就是「神聖閃光」轉場。
4. **單色畫面中的彩色跳出。** 一段用黑白，然後某個單一彩色元素
   （紅眼睛、金色火焰、粉紅頭髮）在強拍上衝出來。
5. **進 drop 的變速。** 在 drop 前最後一小節把素材從慢拉到快，
   在第一拍硬切到正常速度。
6. **字幕關鍵字強調（只用在口說 / 歌詞段落）。** 全大寫，
   一兩個字用點綴色標出，跟人聲同步。用在歌詞影片，不要用在純 visualizer。
7. **Reaction PiP（只用在解說 / 剪輯評論）。** 在 b-roll 上疊一個
   畫中畫的說話人頭。不在音樂影片本身的範圍內，會寫進來是因為素材庫大量使用它。

**不准做的事：** 在有節奏的段落用 crossfade 轉場；一個鏡頭超過一個點綴色；
一個鏡頭撐過它的樂句；畫面上出現看得清楚的 UI 外框（要裁掉）；
同一條時間軸混用不同長寬比。

## 流程：混用 ECC 的影片 skill

這個 skill 是指揮。每個 ECC skill 是一件樂器。不要跳層。

```
0. TASTE (this skill)        decide genre + mood + grammar BEFORE anything renders
1. STRUCTURE (video-editing) map the song: timestamps for intro/verse/drop/bridge/outro
2. GENERATE (fal-ai-media)   make b-roll per genre prompt-presets; throw away 80%
3. CUT (video-editing/FFmpeg) beat-cut + reframe to 9:16; assemble selects on the grid
4. COMPOSE (remotion-video-creation) overlays, blooms, lyric text, beat-synced sequencing
5. MOTION (motion-* skills)  easing curves, light-leak/particle motion, transition timing
6. AUDIO (fal-ai-media)      transition risers/impacts to sell the cuts (track itself is in Ableton)
7. POLISH                    grade to the palette above, final pacing pass, export
8. DISTRIBUTE (content-engine) platform-native versions + caption/cover
```

| 步驟 | 要載入的 ECC skill | 在這裡做什麼 |
|------|-------------------|-------------------|
| 結構與剪輯 | `video-editing` | FFmpeg 剪 / 串接 / 重新構圖、EDL、場景 / 靜音偵測 |
| 生成 b-roll | `fal-ai-media` | 依風格預設使用圖像 / 影片模型 |
| 合成與疊加 | `remotion-video-creation` | 對拍的 `<Sequence>`、文字、bloom、遮罩 |
| 動態時序 | `motion-foundations`、`motion-patterns`、`motion-advanced` | easing、彈簧、光 / 粒子運動 |
| 伺服器端影片 | `videodb` | 智慧重新構圖，素材很大時做索引 |
| 發布 | `content-engine` | 各平台的版本、封面、字幕 |
| 配音 / 歌詞旁白 | `video-editing`（ElevenLabs 那節） | 只有需要口說層時才用 |

## 拍點計算（把剪點鎖在歌上）

目前這首是 **138 BPM、B minor**。常數：

- `seconds_per_beat = 60 / 138 = 0.43478s`
- `frames_per_beat   = fps × 0.43478`  →  **24fps: 10.43**、**30fps: 13.04**、**60fps: 26.09**
- `1 bar (4 beats)   = 1.7391s`  →  30fps：**52.17 frames**
- `8-bar phrase      = 13.913s`  →  這首歌的 loop 長度

在 Remotion 裡，把每個 `from={}` 都吸附到拍點：
```ts
const FPS = 30;
const BPM = 138;
const beat = (n: number) => Math.round(n * (60 / BPM) * FPS); // beat(n) → frame
// cut on beats 0,4,8,... :  <Sequence from={beat(0)} durationInFrames={beat(4)}> ...
```

## 對拍的鏡頭計畫（這支音樂影片）

歌曲編排（出自專案自己的筆記）是
**Intro → Verse → Drop → Bridge → Drop → Outro（約 2:05）**。把品味對應到每個段落：

| 段落 | 風格 / 情緒傾向 | 語法 | 鏡頭點子 |
|---------|-----------------|---------|------------|
| **Intro** | Ethereal/divine，近乎全黑 | 慢推、不切 | 虛空裡的餘燼綻放；一道金色光束；灰塵上升 |
| **Verse** | Dark + 黑底微距主角 | 每 2 拍硬切 | 鑰匙、眼睛、齒輪、水滴、花瓣，節奏式微距蒙太奇 |
| **Drop** | Hyperpop 綻放 + 結晶 | 變速進入、在第一拍切、快 | 糖果粉人影、鉻金屬、虹彩 bokeh、有翼升天 |
| **Bridge** | Spiritualism，失重 | 一個長的定格鏡頭、彩色跳出 | 雲 + 光環；單一紅色點綴衝出一次 |
| **Drop 2** | 同 Drop，加強 | 在 transient 上加神聖閃光 bloom | 翅膀張開、亮片爆開、漏光拉到最滿 |
| **Outro** | Glacial folk，冷靜 | 慢慢淡出到黑 | 結晶結構消融；餘燼熄滅 |

## fal.ai Prompt 預設（依情緒）

搭配 `fal-ai-media` 使用。每個預設都是把風格套到專案色盤上。所有 prompt 都附加
`9:16, vertical, cinematic, film grain, volumetric light, no text, no watermark`。

- **Divine void：** "a single molten-gold ember bloom rising in an infinite near-black void,
  deep shadow, one warm light source, weightless dust particles, holy, high contrast"
- **Macro hero：** "extreme macro of an antique brass key / a human eye / interlocking gears,
  centered on pure black negative space, razor-sharp detail, single rim light"
- **Crystalline bloom：** "iridescent violet-cyan-magenta crystalline bokeh, glittering light
  refraction, dreamy lens flares, heavenly glow, soft focus, hyperpop angelcore"
- **Candy-cyber portrait：** "candy-pink-haired figure, glossy chrome accents, bright blue sky,
  Y2K hyperpop, clean gloss, saturated, kawaii-cyber"
- **Winged ascension：** "a winged figure ascending into clouds, halo of light, bone-white and
  gold, volumetric god-rays, ethereal, religious iconography, soft"
- **Cold outro：** "pale crystalline ice structure slowly dissolving, glacial folk, cold blue
  and bone white, minimal, calm, fading to black"

每個預設生成 6 到 10 張，留 2 到 3 張。要有動態的話，用 image-to-video 模型
讓靜態圖動起來，或直接生成短片段；鏡頭運動照 Motion 的規則保持緩慢。

## FFmpeg 配方（剪輯 + 重新構圖）

```bash
# Reframe any landscape/raw clip to 9:16 (center crop)
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" v.mp4

# Beat-cut a clip to exactly N beats at 138 BPM (e.g. 2 beats = 0.8696s)
ffmpeg -i in.mp4 -t 0.8696 -c copy beat2.mp4

# Concatenate beat-selects into the verse montage
for f in selects/*.mp4; do echo "file '$f'"; done > concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy verse.mp4

# Strip UI chrome / status bar from a screen-recorded reference (crop top+bottom)
ffmpeg -i reel.mp4 -vf "crop=iw:ih-300:0:150" clean.mp4
```

## Remotion 合成骨架（對拍）

```tsx
import { AbsoluteFill, Sequence, Video, Img, useCurrentFrame, interpolate } from "remotion";

const FPS = 30, BPM = 138;
const beat = (n: number) => Math.round(n * (60 / BPM) * FPS);

const Bloom: React.FC = () => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 3, 12], [0, 1, 0], { extrapolateRight: "clamp" }); // divine flash on a transient
  return <AbsoluteFill style={{ background: "radial-gradient(#fff,#ffb24d)", opacity: o, mixBlendMode: "screen" }} />;
};

export const AngelcoreMV: React.FC = () => (
  <AbsoluteFill style={{ background: "#05060a" }}>
    {/* Verse: macro hero-on-black, hard cut every 2 beats */}
    <Sequence from={beat(0)} durationInFrames={beat(2)}><Video src="/selects/key.mp4" /></Sequence>
    <Sequence from={beat(2)} durationInFrames={beat(2)}><Video src="/selects/eye.mp4" /></Sequence>
    <Sequence from={beat(4)} durationInFrames={beat(2)}><Video src="/selects/gear.mp4" /></Sequence>
    {/* Drop: crystalline bloom + flash on the one */}
    <Sequence from={beat(8)} durationInFrames={beat(16)}><Video src="/selects/crystalline.mp4" /></Sequence>
    <Sequence from={beat(8)} durationInFrames={beat(1)}><Bloom /></Sequence>
  </AbsoluteFill>
);
```
Render：`npx remotion render src/index.ts AngelcoreMV out.mp4`。專案設定、音軌綁定和 render 參數
請看 `remotion-video-creation`。

## 關鍵原則

1. **在第一次生成之前先決定風格。** 挑一個主家族加一個點綴。
2. **每個鏡頭只有一個點綴色。** 金色在暗處，虹彩在亮處，紅色只出現一次。
3. **每一個硬切都落在拍點上。** 用拍點計算，有節奏的段落不要轉場。
4. **黑底微距主角是招牌動作。** 把它練到熟，verse 就靠它撐。
5. **生成 10 張，留 2 張。** 一致性來自淘汰，不是來自 prompt 寫得更用力。
6. **裁掉外框。** 最終畫面不准有狀態列、字幕或 UI。
7. **品味先決定，最後才評斷。** 先定方向，然後在每一刀上捍衛它。

## 相關 Skills

- `video-editing`：這個 skill 所站在上面的機制流程（FFmpeg、重新構圖、EDL、收尾）
- `remotion-video-creation`：可程式化的對拍合成與渲染
- `fal-ai-media`：生成 b-roll、轉場音效和 riser
- `motion-foundations`、`motion-patterns`、`motion-advanced`：easing 和動態時序
- `videodb`：大量素材用的伺服器端智慧重新構圖和索引
- `content-engine`：各平台原生的發布、封面、字幕
- `frontend-design-direction`：同樣的「先決定方向」紀律，只是用在 UI
