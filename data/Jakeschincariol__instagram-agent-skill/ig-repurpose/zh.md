---
name: ig-repurpose
description: >-
  把一份長內容，像是 YouTube 影片、Podcast、直播、電子報、部落格文章或客戶通話，
  變成一整週的 Reel 和輪播貼文。當使用者說「幫我改編這個」「把這個做成 Reel」
  「我有一支影片／Podcast／逐字稿」「幫我切」，或貼上一段長內容想放到 Instagram 時使用。
---

# ig-repurpose

一份好的長內容裡面有四到六則貼文。大部分人只抽出一則，其他都丟了。

## 輸入

逐字稿、文章、電子報、腳本、通話摘要、直播。如果使用者給網址，而這個 session 有逐字稿工具，就用它；沒有的話請他直接貼上。抽取任何東西之前，先把整份讀完。

如果來源是使用者自己的影片，也跟他要檔案。用他自己畫面做的 Reel，勝過把他講過的話再唸一次的 Reel。

## 抽取，不要摘要

影片的摘要不是 Reel。沒人想看摘要。把整份內容過一遍，把能獨立成立的東西拉出來：

| 抽什麼 | 是什麼 |
| --- | --- |
| **主張** | 每一句會引發爭論的話 |
| **數字** | 每個數據、成本、時間長度、百分比 |
| **故事** | 每個有人物、有場景、有付出代價的時刻 |
| **機制** | 每個「這件事實際上是這樣運作的…」 |
| **錯誤** | 每個承認搞砸了的地方 |
| **金句** | 每一句原封不動就能引用的話 |

動筆之前先列出你找到什麼，附上數量。如果這份內容抽出來不到四項，它就是薄的，硬擠出四則貼文也會一樣薄。直接講。

## 接著幫每個抽出的東西選格式

不是每樣都該做成 Reel。

- **主張、錯誤、故事** 做成 Reel。它們需要聲音和臉。
- **機制、條列清單** 做成輪播。它們需要被反覆看。
- **一句金句** 做成限時動態的一格，不要做成貼文。

## 然後排出一整週

每個抽出的東西變成一則貼文，每則貼文都要完全能獨立成立。觀眾沒看過原始內容，以後也不會看。永遠不要寫「就像我在上一支影片說的」。貼文本身就是全部。

每則都從 `ig-reel/hooks.json` 指定一個 hook 公式，而且要換著用。同一個來源出五則貼文、hook 形狀都一樣，看起來就像內容農場，因為它就是。

如果來源是使用者自己的影片，**就用實際的畫面**。他講那句話的片段，帶著真實的反應，每次都勝過重錄。在句子結束處剪，不要在換氣處剪。

整週的順序：最強的主張放第一天，故事放週中，機制放最後，那時候喜歡前面幾則的人正等著看。

## 輸出

```
SOURCE: "Why we killed discovery calls" (42 min podcast, 8,900 words)

FOUND  5 claims, 9 numbers, 3 stories, 4 mechanisms, 2 mistakes, 7 quotable lines

WEEK
TUE  REEL      #2  Negative Command  Stop running discovery calls
                                     use the 14:20 clip, he laughs at the end
WED  CAROUSEL  Job B caption         The 4-question form that replaced the call
FRI  REEL      #21 Mid-Sentence      "...and he asked for a refund nine days later"
SUN  REEL      #5  Time Collapse     Six hours a week back, one deleted link

Say "write Tuesday" and I will draft it.
```

（範例大意：來源是一集 42 分鐘的 Podcast，抽出 5 個主張、9 個數字、3 個故事、4 個機制、2 個錯誤、7 句金句。週二 Reel「別再開需求訪談會議」，用 14:20 那段，他最後有笑；週三輪播介紹取代會議的 4 題表單；週五 Reel 從句子中間切入；週日 Reel 講刪掉一個連結、每週省回六小時。說「寫週二」就開始寫草稿。）

之後依使用者要求一次寫一則草稿，每則都經過 `/ig-reel` 和 `/ig-human`。不要一次丟四份完成的腳本。它們會聽起來都一樣，使用者最後一支都不會拍。
