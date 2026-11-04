---
name: tasteforge-video
description: 用在檔案驅動的多模態圖像、影片和 3D 素材探索；taste 訪談；distill 或 apply 工作流；風格包驗證；可編輯的 EDL/FCPXML 匯出；來源溯源稽核；以及必須在 provider 生成之前就 fail closed 的離線規劃。
metadata:
  origin: ECC
---

# TasteForge Video

要完整獨立的創意 pipeline，先用 `taste-distillation`，再用
`taste-application`。這兩個 ECC skill 直接附帶它們的 Python script：
量測參考片、生成或直通既有的 take、調色、剪輯、
合成、驗證，再交接給 Blender 和 Resolve。這個流程不需要另外的影片
repo。這個 skill 記錄的是 ECC 打包好的離線引擎，以及它嚴格的證據規範。

TasteForge 把「讓它感覺像這個參考」變成可重複、
可檢查的 workflow：訪談品味、把它提煉成結構化的風格
包、驗證風格包、把它量測到的節奏和外觀套用到本機媒體，
再匯出可編輯的時間軸。標準實作是
放在 ECC 裡 `skills/taste-application/scripts/tasteforge/` 的
`tasteforge` 套件。`Ito-Markets/ito-video` 是一個
使用這個打包 ECC 引擎的範例專案。

## 何時使用

- 使用者要求在拍任何素材之前**先訪談影片品味**
  （「問我關於外觀的事」、「訪談我的美學方向」）。
- 使用者想要把**美學提煉成結構化的約束**，也就是可重複使用的
  風格包，而不是感覺（「把這些參考變成一個包」）。
- 使用者想要**驗證風格包**（metadata 完整嗎、符合 schema 嗎、
  節奏量測了嗎、規格提煉了嗎？）。
- 使用者想要**把風格包套用到本機素材**：依風格包量測到的
  節奏，在本機片段上以確定性的方式規劃剪輯。
- 使用者想要**匯出 EDL/FCPXML**：給 DaVinci Resolve / Premiere / Final Cut 的
  可編輯、逐格精準的交接。
- 使用者要求**生成媒體的溯源稽核**：這個風格包、規格或剪輯是從哪來的；
  哪些是本機量測的、哪些是 provider 生成的；
  哪些是 dry-run。
- 使用者要求**從本機參考檔案探索或規劃檔案驅動的多模態圖像、影片或
  3D 素材輸出**，包括分開的 manifest、
  以主體為錨點的 CV 效果，或 Resolve 效果配方。
- 使用者提到 TasteForge、風格包、flashethereal、taste distillation、
  節奏規劃、多模態探索、distill/apply 工作流，或是
  影片的 taste 訪談。

## 本機確定性操作 vs. Provider 生成

這條界線是這個相容性 skill 的核心。它的操作都是
**本機、確定性、離線**：

| 操作 | 確定性？ | ECC 可以執行 |
|---|---|---|
| Taste 訪談 → profile | 是（離線） | 可以 |
| 風格包檢視 / 依 schema 驗證 | 是 | 可以 |
| 提煉 profile（+ 量測依據）→ 規格 | 是（dry-run 語意） | 可以 |
| 把風格包節奏套到本機媒體 → 報告 + 時間軸 | 是 | 可以 |
| 匯出 EDL (CMX3600) / FCPXML 1.9 | 是 | 可以 |
| 溯源 / 譜系報告 | 是 | 可以 |
| 用視覺模型提煉靜態圖 | **provider 生成** | **不可以** |
| Reference-to-video、image-to-3D、託管 compose | **provider 生成** | **不可以** |

**Provider 生成在 ECC 裡必須 fail closed。** 任何實際的 Fal（或其他
provider）呼叫，包括生成鏡頭、產出道具 mesh、託管的 VLM
提煉，都需要在另一條獨立的 lane 下，明確另外授權執行，並有它自己的 review。在這條相容性 lane 裡，ECC 絕不呼叫 Fal、絕不讀任何 API
key 或其他憑證（包括 `FAL_KEY`）、不上傳任何媒體，也不更動
任何 provider 帳號的狀態。當請求需要 provider 生成時，要明確
說出這條界線，跑完本機那一半（訪談、風格包驗證、
規劃、匯出），然後停手。

**絕不宣稱 Fal workflow 已經存好。** 本機對 Fal endpoint、
model id 或 dry-run URL 的引用（它們會出現在風格包 metadata 裡）都是
**僅供參考**：它絕不代表 provider 那邊有 workflow 被存好、
持久化，或被授權執行。離線產出的任何東西都帶有
dry-run/dry_run 語意，要說「dry-run 規格」或「確定性計畫」，絕不說
「由模型生成」。

## 標準實作

- Repository：`affaan-m/ECC`；Python 發行包 `ecc-tasteforge`，套件
  目錄 `skills/taste-application/scripts/tasteforge/`。從
  解壓縮的 ECC 套件安裝：`python3 -m pip install ./skills/taste-application/scripts`。
  範例專案 `Ito-Markets/ito-video` 釘在特定的 ECC commit。
- CLI：`python3 -m tasteforge <command>`，有 `provenance`、`inspect`、`validate`、
  `interview`、`distill`、`apply`、`export`、`multimodal`。`--live` flag 會以
  exit code 2 結束並拒絕。
- Schema 就是契約：taste profile、風格包 manifest、grade、cadence、
  規格、時間軸事件、套用報告（`provider` 以 enum 鎖定為
  `"none"`；`dry_run` 鎖定為 `true`）。
- 還原來源的譜系和刻意排除的項目，放在 repo 的
  `skills/taste-application/SOURCE.md`。執行 `python3 -m tasteforge provenance` 可取得機器
  可讀的版本。

本機確定性指令要用已安裝的 ECC 引擎，並解讀
它輸出的 JSON。沒有的話就安裝打包好的引擎；不要在
行內重寫它的邏輯。`taste.resolve` 是 `tasteforge.resolve` 的相容性 import，
所以創意 script 和範例專案共用同一個驗證過的 Resolve adapter。

`python3 -m tasteforge` CLI 使用已安裝的 `ecc-tasteforge` 發行包。獨立的 `taste-distillation` 和 `taste-application`
script 則放在 ECC 選擇性加入的媒體生成模組裡，有它們自己的 Python
需求。兩條路徑都不需要公開使用者的 repo 或媒體。

要繼續使用已存的 checkout 之前，先記錄它的 commit，並檢查本機 branch
和 worktree 有沒有後續的實作修正。跑標準套件的測試，
和 `python3 -m tasteforge apply --help`；ECC 的文字和 fixture 測試
不能證明被選到的 Python checkout 有實作這份契約。

## 串接創意 Skill

| 階段 | 負責者 | 可審查的成果 |
|---|---|---|
| 創意方向 | `taste` | 命名風格、參考觀察、選定的外觀和避免清單 |
| 提煉與規劃 | `tasteforge-video` | 量測證據、分開的風格規格、dry-run manifest 和節奏計畫 |
| 剪輯與特效 | `video-editing`，搭配選定的渲染器，例如 Remotion、Manim 或 Fusion | 套用後的素材、實際的軌道、可編輯的特效和時間軸 |
| 選用的生成素材或配音 | `fal-ai-media` 或選定的音訊 workflow，在它自己的授權下 | Provider receipt 和檢查過的輸出 |
| 交付 | 剪輯 workflow，需要時再用 `content-engine` | 審查過的確切匯出和發布文案 |

只用專案需要的階段。`taste` skill 歷史上的
angelcore/cloud-trance 色盤和拍點語法只是選用的創意範例；
它們不能覆蓋目前的 brief，也不能把不同編號的風格混在一起。
各風格的方向要用它自己實際的參考，包括 3D Cyber Glitch
和 Fluid Sketch。TasteForge 不取代這些 skill，也不要求每一種
渲染器。3D 的材質、幾何、線框行為、
運動和構圖，都要明確寫在該風格的特徵裡。3D 請求 manifest
是素材的計畫，它不是 mesh。主體錨點描述子只是指名一個
追蹤需求，它不是主體已被偵測或追蹤到的證據。
在宣稱 CV 特效已可靠套用之前，要先檢查實際的軌道、追蹤丟失時的行為，
和 render 出來的主體畫格。

## 工作流

1. **訪談**（`interview`）：收集外觀各軸的答案：色盤、
   顆粒、打光、焦距、攝影機運動、主體構圖、調色、
   情緒形容詞、避免清單，另外單獨收集內容 brief。外觀
   和內容要分開；合在一起是經典的失敗。
2. **提煉**（`distill`）：離線把 profile 對應到規格 schema，
   有提供風格包時，把風格包量測到的依據（黑/白點、對比、
   各分區色度、色盤、剪輯節奏）嵌進去。結果
   是 dry-run 規格：確定性、provider 為 `"none"`。
3. **驗證**（`validate` / `inspect`）：依 schema 檢查風格包；
   回報錯誤與警告（只有 metadata 的風格包缺少靜態圖，
   是警告，不是錯誤）。
4. **套用**（`apply`）：依風格包量測到的節奏規劃鏡頭長度
   （有 seed、確定性），套在使用者的本機片段上；產出
   套用報告和逐格精準的時間軸事件。
5. **匯出**（`export`）：寫出 CMX3600 EDL + FCPXML 1.9，用有理數、
   NTSC 安全的時間，好匯入真正的 NLE。
6. **稽核**（`provenance`）：回報譜系：還原來源的 digest、
   生成歷史、fixture 來源、provider 引用只當作
   指標記錄。

### 套用真實素材而不重複來源

當 brief 要求不重複片段時，要用支援
`apply --no-repeat --fps` 的標準 checkout，並明確設定輸出影格率。如果沒有這些
flag，就回報實作上的缺口，不要悄悄改用
舊版的 round-robin 選擇。嚴格模式讓每個正規化後的來源路徑
最多只用一次，依 manifest 順序，並拒絕不足或太短的來源。
要準備足夠多、審查過的 select 來填滿節奏計畫。這是來源層級的
唯一性，不代表支援同一段錄影裡不同的 in/out 範圍。

套用報告只是剪輯計畫。它不做視覺上的鏡頭排名、
不幫素材調色、不套 LUT、不 render 疊加，也不匯入 Resolve 專案。
風格包量測到的參考節奏，要跟輸出影格率分開。

export CLI 要的是 `{"clips": [...]}`。匯出之前，要把套用結果的
`timeline_events` 包到 `clips` 底下，並傳入套用時用的同一個 `--fps`；
export 預設的影格率不能把計畫重新 conform。
把時間軸交給剪輯 workflow 之前，要檢查輸出的事件數、總影格數、不重複的來源，
和媒體連結。
當那個 workflow 在 NLE 裡套用重疊的特效時，要配置相容的
軌道，並讀回每一個要求的起點、終點和長度。只有
回傳的項目或 append 呼叫成功，並不能證明每個排定的特效
都被放上去了；在 render 之前，要拒絕遺失、偏移或被截斷的 placement。

## 檔案驅動的多模態契約

當本機參考必須驅動圖像、影片和 3D 素材輸出的 dry-run 生成計畫，
同時又要保持風格分離時，用這條路徑：

```bash
python3 -m tasteforge multimodal --config workflow.json --out-dir out/multimodal
```

config 會列出編號的風格和本機證據檔案。這些候選
風格要保持分開，不要混成一個通用的美學：

1. Flash Ethereal
2. 3D Cyber Glitch
3. Fluid Sketch

這個指令用 ffprobe/ffmpeg 量測本機參考，每個風格輸出一份風格
規格、分開的圖像、影片和 3D 素材 manifest、溯源，以及
一份 Resolve 特效配方。特效排程必須是有 seed 的非週期。CV
特效需要真正的主體錨點，它的丟失追蹤政策必須剛好是
`disable_effect_until_track_recovers`；`continue_without_anchor` 和其他所有
政策都 fail closed。每個特效都帶有 placement 約束，
要保護臉部和可讀的文字，並防止裝飾性的角落 mesh 取代全畫面的 3D 作品。

回傳的 receipt 就是 bundle 的邊界。它用相對路徑、位元組大小、SHA-256、風格、模態、
`provider_execution:false` 和精確的參考/時間溯源，綁住每一個輸出的證據
產物。receipt 要求 `provider_calls:0` 必須是精確的整數（JSON 布林值 `false` 無效），
`provider_execution:false`，以及 `dry_run:true`。每份風格規格也
要求明確的 `dry_run:true`。Resolve 特效配方要求同樣的
精確整數 `provider_calls:0`、`provider_execution:false` 和 `dry_run:true`。
每個模態 manifest 和每個巢狀請求，都必須包含全部四個精確的
fail-closed 欄位：整數 `provider_calls:0`、`provider_execution:false`、
`dry_run:true` 和 `submit:false`；每個請求另外還要求
`provider_call_mode:"disabled"`。缺少欄位就是拒絕，不是預設值，
而 `dry_run:false` 必須在寫出任何輸出之前就被拒絕。

在時間軸、證據、probe 和來源長度資料裡，布林值一律當成無效數字。
每個這類數值都必須是有限的實數：拒絕
`true`、`false`、NaN、無限大、負的事件起點、非正的長度、
超出範圍的證據時間，以及結束時間超過所宣告的有限
正時間軸的事件。整檔證據使用明確的整檔時間基準，
絕不捏造時間戳。

receipt 的參考是長度的權威來源。每個驗證過的參考長度都以它引用的 SHA-256 當 key；
同一個 digest 的重複出現，長度必須一致，否則 bundle 無效。
每個特效證據的 `source_duration` 和每個主體錨點的 `source_duration`，
都必須等於那個 digest 驗證過的 receipt 長度，不能只是
包含它引用的時間。Probe 長度和所有 probe 量測，必須描述
用來算位元組數和 SHA-256 的同一份穩定位元組。如果來源在 probe 時被更動，
或在它仍然可用時重新雜湊得到不同結果，就 fail closed，
不要輸出或接受 receipt。

建立之後一定要跑 bundle 驗證。缺少圖像、影片或 3D 素材
manifest 必須 fail closed。被通用化或重複的風格、週期性排程、
沒有錨點的 CV 特效、缺少 placement 約束、provider 執行 flag、
沒有綁定的輸出檔、位元組大小漂移，或 SHA-256 被竄改，都必須 fail closed。
要拒絕是 symlink 的輸出根目錄、中間產物或產物，也要拒絕
特殊檔案（包括 FIFO 和裝置）；輸出必須是
真實目錄樹底下的一般檔案。如果本機的 `ffmpeg` 或 `ffprobe` 不可用，
CLI 必須回傳它有界的、非零的本機媒體處理錯誤，而且不能有 Python
traceback。不要靠刪除證據或削弱驗證來修復失敗的 receipt。

## 範例流程

```bash
# after installing the ECC engine; paths below are your project inputs
python3 -m tasteforge validate stylepacks/flashethereal
python3 -m tasteforge interview --answers answers.json --genre flashethereal --out profile.json
python3 -m tasteforge distill --profile profile.json --pack stylepacks/flashethereal --out spec.json
python3 -m tasteforge apply --pack stylepacks/flashethereal --media media.json --duration 20 --out report.json
python3 -m tasteforge export --events events.json --out-dir out --title flashethereal-cut
python3 -m tasteforge provenance
```

當鏡頭必須生成時，要在使用者明確的 provider 授權下，把審查過的 brief
和風格方向交給 `taste-application`。離線 CLI 仍然維持
fail-closed；它的計畫和可編輯時間軸，不能證明有任何
provider 工作跑過。
