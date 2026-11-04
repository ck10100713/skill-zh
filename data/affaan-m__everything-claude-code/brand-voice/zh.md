---
name: brand-voice
description: 從真實的貼文、文章、發布說明、文件或網站文案，建立一份源自實際素材的寫作風格檔案，之後在內容、開發信和社群工作流程中重複使用。適用於使用者想要語氣一致、又不想要千篇一律的 AI 文風時。
metadata:
  origin: ECC
---

# Brand Voice

從真實素材建立一份耐用的語氣檔案，之後到處都用這份檔案，不要每次從頭推導風格，也不要退回通用的 AI 文案。

## When to Activate

- 使用者想要特定語氣的內容或開發信
- 為 X、LinkedIn、email、發布貼文、串文或產品更新寫作
- 把某位已知作者的語氣套用到不同管道
- 現有的內容路線需要一套可重複使用的風格系統，而不是一次性的模仿

## Source Priority

用手邊最強的真實素材，順序如下：

1. 近期原創的 X 貼文和串文
2. 文章、論述、備忘錄、發布說明或電子報
3. 真的寄出去且有效的開發信或私訊
4. 產品文件、changelog、README 的論述方式，以及網站文案

不要拿通用的平台範例當素材。

## Collection Workflow

1. 盡量收集 5 到 20 個有代表性的樣本。
2. 除非使用者說舊作品更有代表性，否則優先用近期素材，不用舊的。
3. 如果素材明顯分成兩類，就把「公開發布時的語氣」和「私下工作時的語氣」分開。
4. 如果可以即時存取 X，起草前先用 `x-api` 抓近期的原創貼文。
5. 如果網站文案很重要，把目前的 ECC landing page 和 repo/plugin 的論述方式也納入。

## What to Extract

- 節奏和句子長度
- 壓縮 vs 解釋
- 大小寫習慣
- 括號的用法
- 提問的頻率和目的
- 主張講得多尖銳
- 數字、機制或憑據出現的頻率
- 轉折怎麼寫
- 作者絕對不會做的事

## Output Contract

產出一個可重複使用的 `VOICE PROFILE` 區塊，讓下游的 skill 可以直接取用。用 [references/voice-profile-schema.md](references/voice-profile-schema.md) 裡的 schema。

檔案要有結構，而且短到可以放進 session context 重複使用。重點不是文學評論，重點是能實際拿來重複運用。

## Affaan / ECC Defaults

如果使用者要 Affaan / ECC 的語氣，但即時來源不夠，就從這裡開始，除非有更新的素材可以蓋過它：

- 直接、精簡、具體
- 細節、機制、憑據和數字勝過形容詞
- 括號用來補充限定、縮小範圍，或過度釐清
- 大小寫照慣例，除非有真正的理由要打破
- 很少提問，也不要把問題當誘餌
- 語氣可以尖銳、直率、懷疑或冷面
- 轉折要讓人覺得是掙來的，不是硬抹平的

## Hard Bans

下面這些，一律刪掉重寫：

- 假裝好奇的鉤子
- 「not X, just Y」
- 「no fluff」
- 刻意全小寫
- LinkedIn 思想領袖的腔調
- 誘餌式提問
- 「Excited to share」
- 通用的創業歷程贅詞
- 俗氣的括號

## Persistence Rules

- 同一個 session 裡，相關任務重複使用最近一次確認過的 `VOICE PROFILE`。
- 使用者要求持久化的產物時，把檔案存到他指定的工作區位置或記憶載體。
- 除非使用者明確要求，否則不要建立 repo 追蹤的檔案來存放個人語氣指紋。

## Downstream Use

在下列項目之前或之中使用這個 skill：

- `content-engine`
- `crosspost`
- `lead-intelligence`
- 文章或發布文撰寫
- 跨 X、LinkedIn 和 email 的冷開發或熱開發

如果其他 skill 已經有部分的語氣擷取區塊，以這個 skill 為準。
