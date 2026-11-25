---
name: ig-viral
description: >-
  去找出使用者領域裡現在真的有效的 reel，依照每支比自己帳號平常表現高出多少來排名，
  標出每支用的 hook 公式，整理成一份可以照著拍的 swipe file（素材庫）。使用者說「幫我
  找爆紅影片」「現在什麼內容有效」「我這個領域的人都在發什麼」「拆解這個帳號」
  「幫我做一份 swipe file」「這支 reel 為什麼這麼紅」，或是問下一支要拍什麼卻拿不出
  證據回答時，就用這個。
---

# ig-viral

這是做研究的 skill。這套裡其他 skill 都在寫東西，只有這個是出去看。一個月跑一次，
不是每天跑。公式能撐一季。

這個資料夾裡有一支工具，可以跑：

```bash
python3 swipe.py captured.tsv --out ~/.claude/instagram/swipe.md
```

## 讓這件事值得做的那個觀念

**原始觀看數不是證據。** 兩百萬粉絲的帳號拿到 40 萬觀看，只是平淡的一個禮拜二。
四千粉絲的帳號拿到 40 萬觀看，代表它找到了什麼，而那個東西可以複製。

所以這裡全部用 **outlier multiple（爆發倍數）** 排名：觀看數除以那個帳號自己最近的
中位數。高於 3 倍是訊號。低於 1.5 倍就只是那個帳號的日常，數字看起來再大也學不到
東西。

蒐集的帳號要在**使用者自己規模的大約 10 倍以內**。一個公式在 200 萬粉絲有效，常常
就是因為它有 200 萬粉絲。

## 步驟 1：挑帳號

跟使用者要 6 到 12 個帳號，或是你提名單讓他核准：

- **4 個直接競品**：同領域、同類產品，稍微領先一點。
- **4 個鄰近帳號**：不同領域，同一群受眾。格式往往是從這裡借來的，在你的領域還沒人
  用之前。
- **2 到 4 個大帳號**：大很多的帳號，只看格式，絕對不學發文頻率或語氣。

也請他打開自己的**珍藏（Saved）**。那是最快、最相關的素材庫，而且已經照他的品味
篩過了。

## 步驟 2：實際去看

用這個 session 真的有的瀏覽工具：內建瀏覽器、連到使用者自己 Chrome 的瀏覽器擴充，
或是 computer-use 工具。這件事沒有 API，也不需要，因為量小到用讀的就夠。

**沒得商量的規則：**

- **絕對不要代替使用者登入 Instagram，也絕對不要跟他要密碼。** 如果頁面需要登入，
  那個已經登入的人是使用者。在他在場的情況下操作他的瀏覽器，或請他貼上來。
- **這是閱讀，不是爬蟲。** 十個帳號，每個看十幾支 reel，用人的速度。大量自動蒐集
  違反 Instagram 的使用條款，帳號會被限制操作。不要寫爬蟲、不要用爬蟲服務，也不要
  在背景重複跑這件事。
- **抄公式，絕對不抄影片。** 抄 hook 的形狀、結構、長度、剪接節奏。不要抄他們的
  腳本、聲音、剪輯。swipe file 的每一列都要註明來自哪個帳號。

**每支 reel 要記錄的東西**，用創作者自己的原話：

| 欄位 | 說明 |
| --- | --- |
| account | 帳號名稱 |
| followers | 從個人檔案看 |
| median | 目測最近 12 支 reel，取中間那個觀看數 |
| views | 這支 reel 的觀看數 |
| hook | 第一句，口白或字卡，逐字照抄，文法錯也照抄 |
| on-screen | 第一張字卡，如果跟 hook 不一樣 |
| length | 秒數 |
| cta | 結尾他們請觀眾做什麼 |

median 是最重要的一欄。沒有它，你又回到用粉絲數排名，而這個 skill 存在就是為了阻止
這件事。

**Instagram 給你看的不夠時：** 同樣的 hook 句型也在 YouTube Shorts 上跑，那邊觀看數
和逐字稿都是公開的，也不用登入。這是正當的第二個素材庫，而且口白 hook 更好拿：

```bash
# view counts for a channel's shorts
python3 -m yt_dlp --flat-playlist --playlist-end 40 -J \
  "https://www.youtube.com/@HANDLE/shorts" > channel.json

# the spoken first line of one short, from its auto-captions
python3 -m yt_dlp --skip-download --write-auto-subs --sub-langs "en.*" \
  --sub-format json3 -o hook "https://www.youtube.com/watch?v=VIDEO_ID"
```

把時間戳在 3.0 秒以內的字幕字全部拿出來。那就是 hook，是講出來的樣子，不是寫出來的
樣子。

## 步驟 3：排名

填一個 tab 分隔的檔案，第一列是標題，然後跑腳本：

```
account	followers	median	views	hook
@someone	48000	11000	412000	nobody tells you your first 30 reels are supposed to flop
```

```bash
python3 swipe.py captured.tsv --out ~/.claude/instagram/swipe.md
```

它會算出爆發倍數，用 `/ig-reel` 寫腳本時用的同一套 26 個公式幫 hook 命名，用
`hookscore.py` 幫每個 hook 打分數，然後印出前三分之一和後三分之一差在哪裡。

## 步驟 4：小心講出代表什麼

只報三件事，不要多：

1. **哪些公式在前三分之一特別多**，附次數。兩個公式在六個帳號裡各出現四次，算是
   發現。一個出現兩次，不算。
2. **前三分之一在結構上有什麼共通點**是後三分之一沒有的：hook 長度、payoff 是不是
   視覺的、第一格畫面有沒有動、請求放在哪裡。
3. **沒被分類的那幾列。** 分類器叫不出名字的 hook，要嘛是雜訊，要嘛是 `hooks.json`
   裡還沒收的公式。一列一列自己讀。這是輸出裡最有價值的一欄，也是腳本要印出數量的
   原因。

然後用白話講出樣本數和信心程度。六個帳號共四十支 reel 撐得起一個結論。十二支撐不起，
把這件事講清楚，就是研究和星座運勢的差別。

## 步驟 5：變成可以拍的東西

前三名的公式，各寫一個**使用者的版本**：他自己的故事、他自己的數字，套進現在有效的
形狀。每一個都交給 `/ig-reel`，公式編號已經選好。

絕對不要丟回一句「做一支跟這支一樣的 reel」。要交回一句他明天就能講的 hook。

## 輸出

```
SWIPE  ·  38 reels  ·  7 accounts  ·  baseline: account median

OUTLIERS (above 3x)
  38.4x  hook 86  #3  Nobody Tells You   @acct_a    412,000  (median 10,700)
  11.2x  hook 79  #9  The Steal          @acct_c    180,000  (median 16,100)
  ...

WHAT IS OVER-INDEXING
  #3 Nobody Tells You   x5 in the top third, 0 in the bottom
  #2 Negative Command   x4
  median hook length    8 words up top, 19 at the bottom

UNCLASSIFIED (6)
  Two of these are the same shape and it is not in hooks.json: a hook that
  opens on someone else's comment read out loud. Worth adding.

YOUR VERSION
  #3  "Nobody tells you the first 20 proposals are supposed to lose."
  ...
```

（UNCLASSIFIED 那段的意思是：有兩個是同一種形狀，`hooks.json` 裡沒有，就是開頭直接
把別人的留言念出來，值得加進去。）

把 swipe file 寫到 `~/.claude/instagram/swipe.md`。`/ig-reel` 和 `/ig-plan` 都會讀
它，這就是重點：跑過一次之後，這套其他 skill 就是用使用者自己的證據在做事，不是用
預設值。

這個 skill 不會發文、追蹤、按讚或傳訊息。它只讀。
