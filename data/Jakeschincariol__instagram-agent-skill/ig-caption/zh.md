---
name: ig-caption
description: >-
  寫 Instagram 的 caption（貼文文字）：撐過「... 更多」截斷的那一行、正文、唯一的
  請求、搜尋關鍵字和三個 hashtag，發出去前先檢查過一輪。使用者說「寫 caption」
  「幫這篇配文」「說明欄要放什麼」，手上有做好的 reel 或輪播需要配文，或是問
  hashtag 的事，就用這個。
---

# ig-caption

這個資料夾裡有一支工具，可以跑：

```bash
python3 caption.py caption.txt
python3 caption.py caption.txt --keywords "client proposals,agency pricing"
```

它會照動態消息顯示的樣子把 caption 印出來：前 125 個字元框起來，其他的都藏在
點開之後。先讀那個框，再讀你寫的其他東西。

## 先決定這篇 caption 的任務

跳過這一步，caption 就會毀掉。

**任務 A：影片已經勾住人了。** Reel 在前兩秒就自帶 hook（開場鉤子），口白和字卡都有。
caption 不是第二個 hook，跟影片搶戲只會兩邊都輸。它的任務是提出請求、補上讓請求
說得通的脈絡，還有放進大家會搜尋的字。

**任務 B：caption 本身就是內容。** 一張照片、單張圖、或是開了一個懸念的輪播封面。
這時第一行就是 hook，運作方式跟 Reel 的 hook 一樣：具體、短，停在懸崖邊，不要停在
句子中間。

問清楚你在寫哪一種。如果使用者的 Reel 已經有很強的 hook，就寫 A，並說明原因。

## 結構

```
Line 1      125 characters of visible space. Job A: the ask, plainly.
            Job B: the hook.
            Never a greeting, never a hashtag, never an emoji as the first
            character.
Body        short paragraphs, one line of white space between each. Two to six
            of them. This is where the search terms live.
The ask     one. Comment a keyword, save it, or DM. One.
Hashtags    up to five, on their own line at the bottom, or none.
```

（對照：第一行有 125 個字元的可見空間，任務 A 就直白提出請求，任務 B 放 hook，絕對
不要用打招呼、hashtag 或 emoji 開頭；正文是短段落，段落間空一行，二到六段，搜尋
關鍵字放這裡；請求只有一個，留言關鍵字、收藏或私訊；hashtag 最多五個，單獨一行放
最底下，或乾脆不放。）

上限是 2,200 個字元，但幾乎沒有東西需要寫到 2,200。讓人願意點開、然後交出 600 字元
的 caption，勝過交出 1,800 字元的。

## 老實說 hashtag 這件事

hashtag 已經不是拿來衝觸及的工具了，平台也用產品改動講明了。**Instagram 在
2025 年 12 月 18 日把每篇貼文的 hashtag 上限降到五個**，原本是三十個，並告訴創作者
「using fewer (up to 5) more targeted hashtags, rather than many generic ones」
（用少一點、最多 5 個、更精準的 hashtag，不要用一堆通用的）效果比較好。Adam Mosseri
在 2025 年 2 月就說過，hashtag 沒辦法增加觸及，它是標籤，不是推播工具。

所以：最多五個，要具體，當主題標籤用。如果使用者備忘錄裡存了一整串二十個，那串現在
就是累贅，檢查工具會直接判不合格。

`#viral`、`#fyp`、`#explorepage`、`#foryou` 什麼都沒描述到。刪掉。

## 搜尋關鍵字現在比 hashtag 重要

Instagram 搜尋會讀 caption 的文字。所以使用者想被搜到的那個詞，要用人會打的說法
放進 caption，放在一句讀起來正常的句子裡。「Client proposals」是第三行裡的字，不是
放在最底下一大串裡的「#clientproposals」。

跟使用者要兩三個這種詞，再丟給檢查工具：

```bash
python3 caption.py draft.txt --keywords "client proposals,agency pricing"
```

## 規則

- **caption 裡不放連結。** caption 不能點。正文裡的網址是死字，等於在說「我不用這個
  平台」。放個人簡介或私訊。
- **一個請求。** 兩個請求等於沒有。`caption.py` 會數。
- **留言關鍵字要是大家打得出來的字。** 一個字，沒有空格，沒有 emoji，而且影片裡也要
  講出來。`Comment CONTRACT` 可以。`Comment "the contract guide"` 不行。
- **有連結的話，第一則留言另外寫。** 在收據裡註明。
- **emoji 當標點用，不是當裝飾。** 每 100 個字元超過 4 個，檢查工具就會標出來。
- **替代文字值得花 20 秒。** 輪播和照片都要寫。螢幕閱讀器會讀，Instagram 也會讀。

## 流程

1. 決定任務 A 還是 B，並講出來。
2. 寫草稿。
3. 用 `/ig-human` 跑一遍。caption 很短，所以 AI 味在這裡比這套其他地方都更明顯。
4. 帶著使用者的搜尋關鍵字跑 `caption.py`。每個 FAIL 都要修。每個 WARN 都要明講你的
   決定，不要默默帶過。
5. 印出可以直接複製的區塊，然後是收據：

```
CAPTION READY
job:        A - the reel carries the hook
visible:    118 of 125 characters used before the cut
ask:        one, comment CONTRACT
hashtags:   3
search:     "client proposals" in line 3, "agency pricing" in line 5
linter:     READY
```

不會發文。使用者自己貼上。
