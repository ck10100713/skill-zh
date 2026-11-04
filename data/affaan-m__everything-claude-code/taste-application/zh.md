---
name: taste-application
description: 拿提煉好的風格包生成新影片，並剪成完成品：從參考片的剪輯節奏規劃 take、在 fal 上生成、用風格包量測出來的 LUT 調色、照量測到的節奏剪輯、穿插既有素材、合成疊加 plate、產出 3D 道具，最後用數字驗證結果。當使用者想用擷取好的風格做影片、補充既有素材，或把生成的片段組成真正的剪輯時就用。
metadata:
  origin: ECC
---

# Taste Application

流程的後半段。**taste-distillation** 把參考片量測成一個風格包，
這個 skill 則是對著那個包去生成，再把結果剪起來。

## 執行與交付規範

原始實作就放在這裡的 `scripts/`，不需要另外 checkout `ito-video`。
本機處理要安裝 `scripts/requirements.txt`。
只有要跑 provider 時才安裝 `scripts/requirements-live.txt`。除了憑證之外，實際的
上傳、送出和下載還需要明確設定 `TASTE_FORGE_ALLOW_LIVE=1`，
而且只能在使用者授權的那次執行才設。
`--dry-run` 一樣不需要憑證，會產出有標記的佔位內容。
遇到不明確的 provider timeout，不要當成新的付費工作重送。先檢查
provider 那邊的請求，再決定要不要重新送出。

直接用現有的完成 take，完全不呼叫任何 provider：

```bash
python scripts/pipeline.py --genre example --root stylepacks \
  --takes media/take-a.mp4 media/take-b.mp4 --duration 12 --fps 30 \
  --out out/review-v1.mp4
```

`--duration` 是**盡力而為的節奏目標**，不是精確的長度。完整的
鏡頭可能讓剪出來的成品比較短或比較長；組裝器不會複製
片段，也不會補白去湊目標。輸出的 manifest 會保留實際的
`duration`，並加上 `duration_contract`，裡面有要求與實際的秒數、
不足量、超出量，還有 `cadence_target` 策略。差距達到
一個輸出畫格以上就會明確警告。沒有提供精確長度的模式；
需要精確長度時，請檢查 receipt，並在交付前修改或退回這個
剪輯。

pipeline 會保留每次執行調好色的鏡頭檔，因為可編輯的 FCPXML
和 EDL 都參照它們。它會拒絕輸出檔名衝突，並回報時間軸
匯出失敗。完成 render 不等於存好了剪輯專案，也不等於創意核可。
在實際編輯前後，都要保存來源素材和有版本的專案 checkpoint；
存檔路徑和 digest 要跟記憶體裡的時間軸 receipt 分開記錄。

可直接 clone 使用的 Fal graph 和它的離線輸入編譯器記錄在
`workflows/README.md`。送出前先編譯 brief 和風格方向；
不要假設一個沒接上的 schema 欄位會影響模型 prompt。付費執行前，
要對著實際的 provider 驗證目前的 endpoint 欄位。

Blender 要用完整、有貼圖的來源 GLB；retopology 是另外命名的
衍生物，絕不取代那個來源。`blender_prop.py` 支援
明確的 `--width 1920 --height 1080 --fps 30 --receipt receipt.json`，
並保留風格包導出的邊緣光和材質貼圖。存檔場景跟 render
場景是兩回事；請檢查 receipt 的狀態和打包的圖片。

Resolve 疊加要用 `taste.resolve.apply_placements`，並注入
來自明確選定、有版本的目標的物件。把 `source_end_mode`
設成在那台主機上驗證過的慣例。不要假設不同 Resolve 版本的
來源結尾都是 inclusive。這個 adapter 會把重疊的效果配置在
保留軌道的上方，並在每個 placement 之後立刻檢查，全部
append 完再檢查一次。Composite 的整數值必須符合已安裝的 API；在已驗證的
Studio 21 主機上，Screen 是 5，不是舊版 builder 那個錯誤的 22。
receipt 只證明記憶體內的 placement。先存專案、驗證它的
checkpoint，再檢查實際 render 出來的檔案，然後才能回報已交付。

## 何時啟用

- 「用這個風格做一支影片」/「套用風格包」/「補充這段素材」
- 把生成的片段組成有真正剪輯節奏的東西
- 從某個外觀產出 3D 道具，再把它放回影片裡
- 驗證成品是否真的符合它的參考

## 分工

**模型負責內容、運動、構圖和光線結構。風格包負責顏色和節奏。**
這是量測出來的結果，不是風格偏好，數字請看
taste-distillation。實務上的後果：

- 生成 prompt 裡**完全不放顏色用語**。加上
  *「Colour: none. Render neutral. Grading is applied afterwards.」*
- 保持**兩個分開的 flag**：`--brief`（發生什麼事：主體、動作、地點）
  和 `--style-steer`（看起來怎樣）。合在一起會讓風格字眼滲進
  場景（「teal」變成一個青色物件），主體字眼滲進調色。
- 模型對**局部、可檢查的規則**的反應，比對全域規則好太多。
  「背景純黑、不打光；主體往白色爆」有效；
  「極端對比」沒用。

## 生成 TAKE，不是鏡頭

「對上節奏」最直覺的讀法是一個鏡頭生成一次。這在成本上很荒謬。
參考片平均每個鏡頭 0.78 秒，而 endpoint 最短 4 秒，
一支 10 秒的片子會變成 **12 次呼叫、生成 48 秒、只用到 10 秒
（效率 21%）**，而且十二個互不相干的片段被縫在一起，
本來應該看起來是連續的。

剪輯師是跑一個比較長的 take，再在裡面剪。把鏡頭分組成約 5 秒的 take：
**3 次呼叫、生成 13 秒、效率 77%**，而且連續的鏡頭
真的互相有關係，因為它們出自同一次生成。

要告訴模型你要的形狀，不然它會 render 出一個慢速鎖定的推軌，
裡面切六刀看起來就像卡頓：

> "Filmed as ONE continuous take with no hard cuts inside it. It will be cut into
> 6 pieces of roughly 0.8s in the edit, so the framing, subject and light must
> keep changing throughout — any 0.8s window has to stand alone as its own shot."

## 剪輯規則

- **要重新編碼，絕不 stream-copy。** Stream copy 只能切在關鍵幀上，在
  平均鏡頭長度 0.78 秒的情況下，每個邊界都會被捨入到最近的 GOP，
  毀掉整個 pipeline 存在的目的。
- **補充既有素材時，用它自己的鏡頭邊界。** 把基底影片切成連續的片段再
  依序播放，只是把原片重新組回去：每個「切點」都落在鏡頭中間，
  看不出來。實測一個 20 鏡頭的組裝只偵測到 12 個切點。
  偵測真正的邊界，然後每隔 N 個取一個，確保連續選出的片段一定不連續。
  這讓切點量測從 1.29 秒降到 0.83 秒，目標是 0.78 秒。
- **從參考片的分布取樣鏡頭長度**，不要用平均值，
  這樣剪出來的片子才會繼承節奏的變異，不會被壓平成一樣長的片段。

## 調色規則

- **有片子的話，直接量測勝過烤好的 LUT：** 量它、
  對齊它的 L\* CDF、套用分區色度。`grade_clip_direct` 達到 MAE 1.58，
  對比 34.0 對 34.7。
- **片子的直方圖跟參考不像時，用錨定，不要做 CDF 對齊。** 把一支
  68% 全黑的生成片硬壓到一個繁忙的參考直方圖上，整個背景都被
  從黑色抬起來：背景保留率掉到 26.0%（CDF），錨定則是 69.0%，
  但 MAE 和對比看起來都還是很漂亮。預設用錨定色調。
- **批次大小很重要。** 一次調 48 幀會 OOM 把 process 殺掉；
  6 幀是安全的。

## 已還原的 fal 平台行為

這些觀察和 endpoint 範例來自還原出來的 workflow。
請重新檢查目前的 endpoint metadata；它們不保證適用於每個未來的
provider 版本。內附的 graph 範本記錄了另外驗證過的
workflow 輸入，包括明確的生成音訊控制。

這些都是花了真實時間才摸出來的。設計 graph 之前先查一遍。

| 限制 | 細節 |
|---|---|
| **完全沒有 3D renderer** | fal 有 `image-to-3d`、`text-to-3d`、`3d-to-3d`，沒有別的。每個 `3d-to-3d` endpoint 輸出的都是另一個 mesh。沒有 `3d-to-image`/`3d-to-video` 類別，所以產出的 GLB **不能**重新進入 fal 的影片 graph。要在本機 render，再用 `fal-ai/ffmpeg-api/images-to-video`。 |
| **compose 不能疊加** | `fal-ai/ffmpeg-api/compose` 會用 *"Multiple video tracks are not supported"* 拒絕第二條軌道，而且它把 `image` 軌道也算成影片軌道。它只能排一條影片軌道。**要在本機用 ffmpeg 合成。** |
| **compose 的 keyframe 單位是毫秒** | 回應裡完全沒提。用秒送出的任務會被接受，回傳的影片短了 1000 倍。 |
| **extract-frame 只提供第一幀/中間幀/最後一幀** | 不能指定任意時間戳。把這三張當成三張不同的 conditioning 圖。 |
| **DAG 裡沒有迴圈，也沒有字串串接** | 每個鏡頭的 fan-out 必須一個節點一個節點手寫，或是留在本機做。 |
| **Kling 3.0 沒有 reference-to-video** | v3 系列只有 text/image/motion-control；reference-to-video 在 `o3` 系列：`fal-ai/kling-video/o3/pro/reference-to-video`。 |
| **前綴不一致** | `bytedance/*`、`tripo3d/*`、`meshy/*`、`minimax/*`、`openai/*` **沒有** `fal-ai/` 前綴。`kling-video`、`veo3.1`、`flux-*`、`hunyuan-3d`、`ffmpeg-api` 有。 |

### Endpoint 推薦

| 位置 | 最佳 | 高 CP 值替代 |
|---|---|---|
| reference→video | `bytedance/seedance-2.5/reference-to-video`（720p 約 $0.473/s） | `fal-ai/kling-video/o3/pro/reference-to-video`（約 $0.112/s） |
| image→3D | `fal-ai/hunyuan-3d/v3.1/pro/image-to-3d`（$0.375，最多 8 個視角） | `tripo3d/h3.1/image-to-3d`（$0.20） |
| text→3D | `fal-ai/hunyuan-3d/v3.1/pro/text-to-3d` | `tripo3d/h3.1/text-to-3d` |
| retopology | `fal-ai/hunyuan-3d/v3.1/smart-topology`（$0.75） | `tripo3d/tripo/remesh`（便宜約 75 倍） |
| part split | `fal-ai/hunyuan-3d/v3.1/part`（只有 FBX） | `tripo3d/tripo/segment` |
| text→image | `fal-ai/nano-banana-pro`（統一 $0.15） | `fal-ai/flux-2-pro`（$0.03/MP） |

同樣 5 秒，Seedance 的價格大約是 Kling o3 的 4 倍。它的價值在
多參考的保真度（最多 50 個混合的圖像/影片/音訊參考），用單張靜態圖
做 conditioning 時就**不值**這個價。

模型 ID 和價格會變。承諾任何一個之前，先到 fal.ai/models 驗證。

## 3D 分支

```bash
python mint3d.py --genre <name> --from-stills 4 --retopo --render
python mint3d.py --genre <name> --prompt "a cracked chrome visor" --render
```

- **先生成乾淨的 plate，不要從參考靜態圖擷取。** endpoint
  明列的輸入要求很簡單：背景單純、單一物件、
  物件佔畫面 50% 以上。參考 reels 剛好相反：拼貼、
  廣角、多個主體、燒進去的圖形，這些會產生雕出來的
  雜訊。Text → 單一物件 plate → mesh 大約多花 $0.15，
  差別就是能用的 mesh 和被丟掉的 mesh。
- **多視角是一個個有名字的角度欄位，不是 list。** `input_image_url`（正面，
  必填），然後是 `back_image_url`、`left_image_url`、`right_image_url`、
  `left_front_image_url`、`right_front_image_url`、`top_image_url`、
  `bottom_image_url`。沒有 `input_image_urls`，也沒有 `multi_view` flag，
  亂編這些只會讓每次 mint 都退化成單視角，看起來卻還在運作。
  標錯角度比省略那個視角更糟，因為模型會相信它。
- **用 key 取 GLB，不要用位置。** 回應除了 `model_glb`，還帶一個 `thumbnail`
  PNG 和 `model_urls` 區塊；取第一個 URL 只有在 key 順序沒變之前有效，
  而預覽 PNG 也能正常下載，直到 Blender 拒絕開啟它才會出錯。
- **要求 PBR 貼圖。** 沒有的話 mesh 打光起來像塗過的紙板。
- **如果有人要編輯或綁骨架，就做 retopology。** 生成的 mesh 又密又亂。
- **在本機 render 來把迴圈收起來。** turntable 一旦變成影格，
  它就是素材，而下游每個階段本來就會處理素材：調色、剪、
  用 screen 當元素疊上去，或是上傳當 conditioning 參考。PATH 上有
  Blender 就用 Blender；預設保留一個依賴很少的軟體光柵器，
  因為 headless GL context 是容器裡最常缺的東西，而只能在
  工作站上跑的 renderer 不算 pipeline 的一部分。

## 先驗證，再相信

其他每個階段都宣稱有結果。要去檢查，而且要檢查**分布形狀**，
不只是統計量：

- `background`：低於 L\*10 的畫面占比，對照**風格包**的數字。要跟
  參考比，**不要**跟來源片比：68% 全黑的生成來源片比
  24–55% 區間內的任何參考都黑，所以「保留來源的黑」
  要求的是錯的東西，同時也等於放過一個被抬起來的調色。
- `chroma_mae`：每個分區的 a\*/b\* 誤差，用**中位數**（跟
  風格包目標的量測方式一致；這裡用平均值，是拿一個對偏態敏感的統計量
  去比一個穩健的，會把定義不一致回報成誤差）。
- `contrast` / `black_point` / `white_point`
- `banding`：*夾在有資料的 bin 之間*的空 L\* 直方圖 bin。算總共的
  空 bin 數沒用：一支本來就偏暗的片子，亮部 bin 本來就是空的。
- `cadence`：偵測到的平均鏡頭長度，對照參考的。

小心**單位陷阱**：OpenCV 的 Lab 慣例會隨 dtype 改變。float32 時，
L\* 是 0–100，a\*/b\* 有正負號；uint8 時，L\* 是 0–255，a\*/b\* 有
+128 的偏移。混用的話，色度誤差會報出好幾百。

## 完整鏈

```bash
python pipeline.py --genre <name> --refs a.mov b.mov \
  --brief "what happens" --duration 12 \
  --base-video existing.mp4 --out out/FINAL.mp4
```

mint → distill → (mint3d) → apply → forge → verify。第 1 到 3 階段有 cache，
所以反覆改 brief 絕不會重新量測任何東西。`--dry-run` 會把每個網路
呼叫都 stub 掉：計畫、prompt、軌道配置和 manifest 都還是會跑一遍。

## 反模式

| 不要 | 原因 |
|---|---|
| 一個鏡頭生成一次 | 效率 21%，12 個互不相干的片段 |
| 在 prompt 裡放顏色 | 量測證實沒用；還會把成品推離 LUT 想要的中性基底 |
| 剪輯用 stream-copy | 只有關鍵幀的邊界會毀掉不到一秒的節奏 |
| 把基底影片連續切開 | 只是重組原片；每個切點都看不出來 |
| 相信 compose 能疊加 | 不行；它會拒絕第二條軌道 |
| 傳秒給 compose | 悄悄地短了 1000 倍 |
| 只靠 MAE 就出貨 | 要加上背景占比檢查 |

## 借來的素材會帶著擷取 App 的 UI

在已交付的剪輯裡找到最糟的單一瑕疵：成品影片帶著
別人的愛心按鈕、觀看數和留言泡泡，因為基底素材是螢幕錄影，
而沒有任何東西把它們裁掉。

**`content_mask` 解決不了這個問題，它的 bounding box 還會更糟。**
時間變異會保留介面外框，因為外框會*動*：愛心在跳、
計數在跑，所以 mask 把它標成移動的內容。在三支參考片上量測，
介面明明就在右邊邊緣，mask 的 bbox 每次都保留 100% 的寬度。

能把兩者分開的訊號是時間**中位數**，不是變異。素材會動，
所以很多幀的中位數會平均成一團糊，幾乎沒有邊緣能量；外框
待在固定座標，所以它的邊緣完整留下來。中位數幀上的 Sobel
能量在外框上亮起、在內容上安靜：實測其中一支參考片的右側欄是 0.23，
內部背景是 0.03；另一支是 0.31 對 0.15。

兩個各花了一輪才搞清楚的實作細節：

- **要從每個外圍帶最內側的離群點之後開始裁，不要從邊緣往內走。**
  當目前這條線還是熱的就往內走，會馬上停住，因為最外面幾條線是
  letterbox，純黑、邊緣能量是零，而外框坐落在*那個的裡面*，
  在寬度的 90–95% 處。天真的版本只裁掉 1% 畫面，
  愛心按鈕還留在鏡頭裡。
- **直式來源進橫式剪輯時，要縮放到填滿（cover），不要補邊（pad）。**
  把 9:16（裁掉 UI 後更窄）補進 16:9，畫面約 60% 變成
  黑邊，有個鏡頭幾乎是個空的長方形，還污染了
  背景指標，因為黑邊是純黑。Cover 會損失兩側，
  對置中構圖的素材來說是對的取捨。

## 疊加 Plate 是元素，不是整片罩色

光暈 plate 的覆蓋率天生只有約 4%。照畫面尺寸合成上去，
會得到一個小小的亮點停在鏡頭中間，看起來像貼紙，在已交付的剪輯
裡就是一個無法解釋的彩色斑點。

- **先把每個 plate 收緊到它的 alpha bounding box。** 這會把覆蓋率
  從約 4% 拉到 15–35%，並把尺寸控制權交給呼叫端，而不是繼承
  元素碰巧佔了來源畫面的多少比例。
- **依覆蓋率選擇整片罩色或元素。** 擴散的 plate（收緊後 <10%）
  適合以低不透明度拉伸到全畫面；集中的 plate 則要縮放到
  畫面寬度的 35–70% 再放置。
- **每個鏡頭用有 seed 的 RNG 變化位置、縮放和旋轉**，這樣
  剪輯可重現，但沒有兩個蓋章的鏡頭共用同一個標記。同一個 plate 在
  同一個位置每隔 N 個鏡頭出現，看起來就像浮水印。
- 元素的幾何在 Python 裡解，不要用 ffmpeg 的 expression：`pad()` 會拒絕
  負的偏移，也不能 pad 到比輸入還小，所以過大或跑出畫面的元素
  會讓整個 filtergraph 掛掉。

## 下游交接（Resolve / Blender）

**mp4 旁邊一定要附上可編輯的時間軸。** 攤平的影片是觀看用的版本，
也是調色師唯一沒辦法處理的東西：每個切點都烤進去了，
鏡頭不能再分開。`forge.py` 會寫出 FCPXML 1.9 和 CMX3600 EDL，
參照各個調好色的鏡頭檔，所以成品會以可以重剪、重調色的時間軸
落地。

要驗證匯出，不要假設：檢查 asset-clip 的 offset 等於
前面所有長度的累加（沒有空隙）、每個 `ref` 都對得到有宣告的
asset、每個 `media-rep src` 都真的存在於磁碟上，
還有總長跟 mp4 一致。一個匯入得進去但會漂移的時間軸，比大聲失敗的更糟。

兩件會悄悄毀掉成果的事：

- **匯入前必須先設好專案影格率。** Resolve 在第一次建立時間軸時就鎖定
  時間軸 fps，並悄悄地把節奏 conform 掉。在平均鏡頭長度不到一秒時，
  那個 conform 看得出來。
- **交付的鏡頭已經調過色。** `look.cube` 是給新素材和對色用的
  *標準化* LUT，套用到交付的鏡頭上
  會重複調色。Node 1，前面什麼都不放，修正放後面。

要附上一份交接文件，裡面放量測到的目標值
（`scripts/HANDOFF-TEMPLATE.md` 是填好的範例）：分區色度表、
包含**節奏變異**的剪輯節奏分布（剪輯師如果只對上平均
卻對不上變異，做出來的東西讀起來會完全不同），
還有一份明確的「不要做」清單。

Blender 的部分，`scripts/blender_prop.py` 的打光是從風格包導出的：
黑色世界加透明底片（所以 render 出來合成時不用摳像），
主光加邊緣光（只有主光的話，輪廓會死在黑色裡），
邊緣光的顏色是把風格包的峰值色度分區經 Lab→linear sRGB 轉換而來，
讓道具吃到跟素材調色相同的色偏。**View transform 用 Standard，不要用 AgX/Filmic，
也不要在 Blender 裡調色**，因為 AgX 在 LUT 看到像素之前就先套了
自己的色調曲線，調兩次會疊加。

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
