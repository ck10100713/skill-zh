---
name: taste-distillation
description: 把一組參考影片量測成可重複使用的風格包：調色做成 3D LUT、剪輯節奏做成鏡頭長度分布、主角靜態圖、screen 混合的疊加 plate，還有給生成模型用的文字規格。當使用者想擷取參考素材的外觀、建立可重複的外觀、從參考片產出素材，或重現某人的調色和節奏時就用。
metadata:
  origin: ECC
---

# Taste Distillation

這個獨立 skill 的實作放在 `scripts/`；後續的生成或本機 take 剪輯請用
`taste-application`。每個命名風格各自放在自己的包裡。從 Flash Ethereal
量到的數據，不准悄悄拿去給 Fluid Sketch 或 3D Cyber Glitch 用。量到的零是有效
資料；要把它和欄位不存在區分開來。

本機依賴在 `scripts/requirements.txt`。另外授權的
provider 工作還需要 `scripts/requirements-live.txt`、憑證，
以及明確設定 `TASTE_FORGE_ALLOW_LIVE=1`。`--dry-run` 不會讀憑證，
也不會送出任何工作。不要從本機的 endpoint 名稱就推斷 workflow 已經存好；
要用 provider 那邊實際的 workflow 或請求當證據。

把參考影片變成一個**風格包**：一個放量測結果和素材的資料夾，
後面的階段會以確定性的方式取用。

## 何時啟用

- 「擷取這幾支片的外觀」/「提煉這個氛圍」/「讓這個可以重複」
- 使用者有參考素材，想要 LUT、調色，或是對得上的節奏
- 建立依風格分類的外觀庫
- 任何原本的答案會是「在 prompt 裡描述那個風格」的需求

## 核心發現

**Prompt 做不出調色，量測可以。**

在真實素材上量測：三次付費生成，一次比一次加重顏色指示，
中間調的 a\* 從 +1.9 → +2.8 → +0.3，目標是 **+24.9**，而對比
始終沒離開約 19，目標是 **34.7**。把量測好的風格包套在同一批
素材上，一次確定性的處理就達到色度 MAE **1.88**、對比 **33.7**，
而且免費。

所以分工是：**模型提供內容、運動和光線結構；
風格包提供外觀。** 生成 prompt 裡的顏色字眼比沒用還糟：它們花錢，
還會把 render 推離 LUT 想要的中性基底。要在 prompt 裡明講：*「Colour: none. Render neutral. Grading
is applied afterwards.」*

## 風格包裡有什麼

```
stylepacks/<genre>/
  grade.json      measured colour statistics (see below)
  cadence.json    every detected shot boundary + the derived distribution
  look.cube       33^3 LUT, drag straight into Resolve as a node LUT
  spec.json       VLM description, grounded in the measurements
  grounding.txt   the measured facts fed to the VLM
  stills/         full-res frames from the longest shots (conditioning images)
  plates/         screen-blend overlay elements lifted onto black
  props/          minted GLB meshes
  pack.json       manifest
```

## 執行方式

```bash
python mint.py --genre <name> --refs a.mov b.mov c.mov     # offline, no API key
python distill.py --genre <name>                            # one VLM call
```

`mint.py` 是純數值分析：不連網、不需要 key、結果確定，所以風格包
可以重新產生，不用備份。

## 重要的量測

### 依亮度分區量色度，不要全域量

顏色的特徵通常只存在於**一個亮度區段**。全域的 a\*/b\* 偏移
在數學上無法表示 split-toning。要在各分區內量色度
（`L* edges [0,15,35,55,75,100]`）。

一個真實的特徵：紫色在 L\*25（a\* +24.9、b\* −17.5），兩端都接近中性。
只回報最暗和最亮的分區，會把它說成「均勻色偏」，
所以**一定要把整條曲線印出來。**

### 用中位數 + MAD，絕不用平均 + 標準差

真實參考集的色度是強烈右偏的。在其中一支量測的 reel 上，
中間調色度的平均是 36.9，中位數卻是 17.5，所以用平均做的 LUT 把
顏色推得比素材該有的強約 3 倍。

### 對比是 std(L\*)，不是白減黑

白減黑的範圍在幾乎任何真實素材上都約是 100，
完全沒有鑑別力。

### 背景占比是一級統計量

記錄低於 L\*10 的像素占比。分布的任何一個矩都看不到它：
一支片子可以平均、標準差和色度都對，黑卻已經被
抬成灰。曾經就是這樣，一個調色拿到 MAE 1.88 / 對比 33.7，
實際畫面卻是一團混濁的紫色。

### 量測之前先遮掉介面

螢幕錄影的參考片帶有靜態的東西：letterbox 黑邊、狀態列、
愛心圖示、字幕文字。這些全都會被當成外觀算進統計：
黑邊會灌高陰影的權重，紅色愛心會讓 a\* 偏向洋紅。
**時間變異可以乾淨地把它們分開**：素材會動，介面不會動，
所以不需要手動調整裁切。在真實素材上，這樣大約保留 65% 的
像素。

### 節奏需要自適應的門檻

合適的 content-detector 門檻跟素材有關：高對比的
動作參考片，用 30 就切得夠明顯；情緒型的片子，切點就藏在它底下。
從高到低掃過一系列門檻，取**最高**的那個，只要它還能找回
最敏感設定所找到的鏡頭的 90% 以上，這樣會偏向真實的切點，
而不是雜訊。要拒絕那些意味著荒謬切點頻率（>100/分鐘）的門檻；
連續的攝影機運動會讓偵測器每一幀都觸發。

整個掃描用共用的 `StatsManager`，在**一次解碼**中跑完。天真的版本
每個門檻都重新解碼，在 60fps 的來源上，這就是幾秒和幾分鐘的差別。

## 疊加 Plate：是素材，不是截圖

靜態圖是整個畫面，合成一張上去只是在上面再放一張圖。
**Plate** 是參考片的圖形詞彙（光斑、拖尾、glitch
碎片），被取到黑底上，所以用 screen 混合就不用摳像。

兩個陷阱，都是在真實素材上踩到的：

1. **絕對門檻會失效。** 在明亮的參考片上，用 `L>55 AND chroma>12`
   去選，會選到約 90% 的畫面，那個「plate」就是整張圖，包括一張
   認得出來的臉。要用**百分位**（約前 3%）來選，並且
   **拒絕任何覆蓋超過約 22% 畫面的 plate。**
2. **依分離度排名，不要依亮度。**「亮且飽和的像素占比」
   會把一個洗白的畫面排第一，而一個全黑、只有一道強烈光斑的畫面，
   也就是真正的特徵，反而排在接近最後。要用 `p99.5(energy) / median(energy)` 計分。

評分前也要先遮罩：燒進去的字型又亮、又飽和、
對比又高，所以沒遮罩的話，產出的是一個完美的 plate，內容是別人的片頭
字卡。

## 讓 VLM 有根據

在要求描述之前，先把量測結果放進 system prompt。
沒有根據的時候，VLM 對一段有 +24.9 a\* 色偏的素材，
會回報「沒有明顯調色，中性」。有根據的話，它會正確描述
色偏，還能自己推論出次要的點綴色。

要禁止含糊用詞（`varied`、`mixed`、`dynamic`、`some`、`often`、`neutral`、
`or`），因為模型沒辦法 render「變化的光線」。**要在程式裡強制執行這個禁令，
不要只寫在 prompt 裡：** 大約每三次執行就有一次被違反。要
逐欄位重問，N 次嘗試後保留最不含糊的答案，而不是直接失敗。

值得跟使用者講清楚的但書：規格一旦以量測結果為根據，
它就不再是對那些量測的獨立檢查了。

## LUT 烘焙的坑

- LUT 只能編碼**逐像素的 RGB 函數**。任何依賴分布的東西
  （直方圖匹配、百分位錨點）都必須在烘焙*之前*化簡成
  常數，否則它會悄悄量到均勻的 LUT 網格，而不是素材。
- `cv2.cvtColor(LAB2RGB)` **內部會 clamp**，所以用它做的色域外測試
  會回報 0%。要自己手動把 Lab 轉成 linear sRGB；一次真實量測是 83.3% 色域外。
- 色度轉移要用 offset，不要用 affine。Affine 會除以來源的 σ，
  然後過衝：在真實素材上，它把 b\* 翻到 +11.6，目標是 −17.5。
  Offset 把 MAE 從 6.23 降到 2.13。
- 色域壓縮讓執行時間變成 3.8 倍，MAE 卻一樣。把它做成選用。

## 反模式

| 不要 | 原因 |
|---|---|
| 對著合成的測試素材調整 | 在一個專案上造成四個不同的錯誤結論；真實素材把每一個都推翻了 |
| 只相信 MAE | 在一個明顯壞掉的畫面上，1.88 的 MAE 看起來像成功 |
| 色度用平均/標準差 | 右偏；推得太用力，約 3 倍 |
| 只比較兩端的分區 | 兩端本來就接近中性 |
| 描述完外觀就停手 | 規格是給內容和結構的；顏色是風格包的事 |

## 交接

風格包就是介面。它一旦存在，就用 **taste-application** skill 去
對著它生成和組裝，或是直接把 `look.cube` 交給調色師。

## 內附的程式碼

這個 skill 裡的 `scripts/` 是可以運作的實作，不是偽碼。它沒有
任何專案專屬的假設：指向任何參考影片，就能產出一個
風格包。

```bash
pip install -r scripts/requirements.txt
export FAL_KEY=...            # only needed for the stages that call fal
```

在 `TASTE_FORGE_DRY_RUN=1` 或 `--dry-run` 下，所有網路呼叫都會被 stub，
所以計畫、prompt、軌道配置和 manifest 都能在不花錢的情況下檢查。
