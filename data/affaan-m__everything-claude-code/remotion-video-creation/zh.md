---
name: remotion-video-creation
description: Remotion（用 React 製作影片）的最佳實踐。29 條領域專屬規則，涵蓋 3D、動畫、音訊、字幕、圖表、轉場等等。用 React 搭配 Remotion 製作影片時使用，包括動畫、音訊、字幕、圖表或轉場。
metadata:
  tags: remotion, video, react, animation, composition, three.js, lottie
---

## 何時使用

只要處理 Remotion 程式碼，就使用這個 skill 來取得領域專屬的知識。

## 如何使用

閱讀各個規則檔案，取得詳細說明和程式碼範例：

- [rules/3d.md](rules/3d.md) - 在 Remotion 中使用 Three.js 和 React Three Fiber 製作 3D 內容
- [rules/animations.md](rules/animations.md) - Remotion 的基礎動畫技巧
- [rules/assets.md](rules/assets.md) - 把圖片、影片、音訊和字型匯入 Remotion
- [rules/audio.md](rules/audio.md) - 在 Remotion 中使用音訊和聲音：匯入、裁切、音量、速度、音高
- [rules/calculate-metadata.md](rules/calculate-metadata.md) - 動態設定 composition 的長度、尺寸和 props
- [rules/can-decode.md](rules/can-decode.md) - 用 Mediabunny 檢查影片是否能被瀏覽器解碼
- [rules/charts.md](rules/charts.md) - Remotion 的圖表與資料視覺化模式
- [rules/compositions.md](rules/compositions.md) - 定義 composition、still、資料夾、預設 props 和動態 metadata
- [rules/display-captions.md](rules/display-captions.md) - 在 Remotion 中以 TikTok 風格的分頁與逐字高亮顯示字幕
- [rules/extract-frames.md](rules/extract-frames.md) - 用 Mediabunny 在特定時間點從影片擷取畫格
- [rules/fonts.md](rules/fonts.md) - 在 Remotion 中載入 Google Fonts 和本機字型
- [rules/get-audio-duration.md](rules/get-audio-duration.md) - 用 Mediabunny 取得音訊檔的長度（秒）
- [rules/get-video-dimensions.md](rules/get-video-dimensions.md) - 用 Mediabunny 取得影片檔的寬和高
- [rules/get-video-duration.md](rules/get-video-duration.md) - 用 Mediabunny 取得影片檔的長度（秒）
- [rules/gifs.md](rules/gifs.md) - 顯示與 Remotion 時間軸同步的 GIF
- [rules/images.md](rules/images.md) - 用 Img 元件在 Remotion 中嵌入圖片
- [rules/import-srt-captions.md](rules/import-srt-captions.md) - 用 @remotion/captions 把 .srt 字幕檔匯入 Remotion
- [rules/lottie.md](rules/lottie.md) - 在 Remotion 中嵌入 Lottie 動畫
- [rules/measuring-dom-nodes.md](rules/measuring-dom-nodes.md) - 在 Remotion 中量測 DOM 元素的尺寸
- [rules/measuring-text.md](rules/measuring-text.md) - 量測文字尺寸、讓文字配合容器大小，以及檢查溢出
- [rules/sequencing.md](rules/sequencing.md) - Remotion 的排序模式：延遲、裁切、限制項目的長度
- [rules/tailwind.md](rules/tailwind.md) - 在 Remotion 中使用 TailwindCSS
- [rules/text-animations.md](rules/text-animations.md) - Remotion 的字體排版與文字動畫模式
- [rules/timing.md](rules/timing.md) - Remotion 的插值曲線：linear、easing、spring 動畫
- [rules/transcribe-captions.md](rules/transcribe-captions.md) - 在 Remotion 中把音訊轉錄成字幕
- [rules/transitions.md](rules/transitions.md) - Remotion 的場景轉場模式
- [rules/trimming.md](rules/trimming.md) - Remotion 的裁切模式：剪掉動畫的開頭或結尾
- [rules/videos.md](rules/videos.md) - 在 Remotion 中嵌入影片：裁切、音量、速度、循環、音高
