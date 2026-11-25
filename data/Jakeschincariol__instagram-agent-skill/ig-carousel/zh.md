---
name: ig-carousel
description: >-
  做一則 Instagram 輪播：讓人想往右滑的封面、每一張的文案，還有可以直接上傳的
  1080x1350 圖檔。使用者說「輪播」「投影片」「滑動貼文」「把這個做成輪播」，或是
  手上有清單型、步驟型的點子，做成單張圖會死掉時，就用這個。
---

# ig-carousel

輪播是版面上停留時間最長的格式，因為往右滑算一次互動，往下滑不算。它還有第二次
機會：對第一次沒互動的人，Instagram 可以從後面某一張開始再推一次，所以第二張也要能
自己站得住。

這個格式獎勵「一個重點拆成幾個步驟」，懲罰「把 caption 剁成好幾段」。

## 什麼時候用它，不用 Reel

點子有**順序而且需要重看**的時候用輪播：步驟、分成幾個部分的框架、前後對比、值得
截圖的清單。點子有動作、有人臉，或是 payoff 要親眼看到發生的時候，用 Reel。

如果點子只是一個主張，兩個都不是。交給 `/ig-reel`，並講明原因。

## 結構

6 到 10 張。上限是 20 張，但 20 張幾乎都是一本沒人看完的書。少於 5 張，滑的動作
根本開始不了。

```
1         COVER     the hook. 6 words or fewer, at a size that is legible in
                    the grid at thumbnail. One line of promise under it.
2         THE STAKE why this matters, in one sentence. This slide is also a
                    second cover, so it cannot be setup.
3 to N    ONE IDEA PER SLIDE. A headline of 3 to 7 words, at most 25 words
                    under it. If a slide needs a paragraph, it is two slides.
N+1       RECAP     the whole thing as a list. This is the screenshot slide.
LAST      CTA       one action. Save, comment a keyword, or follow. One.
```

（對照：COVER 是 hook，6 個字以內，大小要在個人檔案格狀縮圖裡也看得清楚，底下放一行
承諾；THE STAKE 用一句話講為什麼重要，這張也是第二個封面，所以不能拿來鋪陳；第 3 到
N 張一張一個重點，標題 3 到 7 個字，底下最多 25 個字，需要一段話就拆成兩張；RECAP
把全部列成清單，這張是讓人截圖的；最後一張 CTA（行動呼籲）只要一個動作，收藏、留言
關鍵字或追蹤。）

## 每張文案的規則

- **封面決定 80% 的成績。** 六個字。要大。封面沒人滑，後面再好都救不了。
- **為格狀裁切設計。** 個人檔案的格狀版面會裁成直的長方形，而且確切比例已經改過
  不只一次。用 1080x1350 做，封面文字放在正中間附近，四邊各留 120 像素空白，裁切就
  沒差了。
- **幫每張編號**（3/8）。看得到終點，看完的人會變多。
- **沒有任何一張是一大段文字。** 25 個字講不完就拆開。
- **重點整理那張是大家會截圖轉傳的。** 轉傳是你能拿到最強的訊號。讓它獨立成立，
  沒有前後文也看得懂。
- **每張都放帳號名稱**，小小的，放在底部角落。截圖傳出去不會帶著你。
- **至少封面要有替代文字。** 螢幕閱讀器會讀，Instagram 也會讀。

## 產出圖檔

Instagram 要 1080x1350（4:5）、JPEG 或 PNG，最多 20 張。用 HTML 做，再把每張印出來：

```bash
# one <section> per slide, 1080x1350, page-break-after: always
# then Chrome headless --print-to-pdf, or any HTML-to-image you already use
```

HTML 寫成 `width:1080px; height:1350px`，只用一個強調色，字不要小於 32px，因為這是在
手機上用大約三分之一的實際大小在看。如果專案有品牌 skill 或設計系統，就用它，不要
自己發明配色。

## 輸出

先給每張的文案，列成編號清單，讓使用者十秒內看完，在產圖之前可以先改。然後是
**caption**，輪播的 caption 屬於 `/ig-caption` 裡的任務 B：這裡 caption 是有在出力的，
因為封面已經把它的六個字用掉了。

兩個都要跑過 `/ig-human`。使用者核准文案之後，才產圖檔。

```
CAROUSEL  ·  8 slides

1  COVER   THE $18,000 CLAUSE
           One line I now put in every contract.
2  STAKE   I approved the work. They asked for the money back nine days later.
3          WHAT IT SAYS
           Payment on delivery, not on approval.
...
7  RECAP   All four lines, in order.
8  CTA     Comment CONTRACT and I will send the full clause.

Caption: Job B, hook in line 1, one ask, 3 tags.
```

（範例主題是「價值 18,000 美元的那條條款」：我現在每份合約都會加的一行字。）

不會上傳任何東西。使用者自己發。
