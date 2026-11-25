---
name: ig-audit
description: >-
  幫使用者檢討已經發過的內容：哪些 Reel 真的有效、為什麼有效、哪些該停掉。
  當使用者貼上 Instagram 洞察報告或過去的貼文，問「什麼內容有效」「這支為什麼爆掉」
  「幫我看數據」「幫我健檢內容」，或想知道該多做什麼時使用。
---

# ig-audit

一個帳號什麼內容有效，唯一誠實的來源就是那個帳號自己。每本 Instagram 教學裡的每條規則，包括這套 skill 裡的，都只是先驗假設。使用者自己最近 30 則貼文才是證據。

## 輸入

使用者手上有哪種就跟他要哪種：

- 每則貼文的洞察數據：觀看數、觸及、互動、觀看時間、收藏、分享、追蹤，還有觸及裡非粉絲的比例。截圖也可以。
- 或是最近表現最好和最差的 Reel 的留存曲線。這一張截圖比其他資料加起來都有用。
- 或只給貼文和觀看數，第一輪分析這樣就夠了。

如果 `~/.claude/instagram/log.md` 存在也要讀，裡面記了每則貼文用的是哪個 hook（開頭鉤子）公式。

## 真正該量的東西

原始觀看數是頁面上最沒用的數字，因為它主要取決於帳號本來有多少粉絲。改算下面這些，並把計算過程列出來：

| 指標 | 怎麼算 | 告訴你什麼 |
| --- | --- | --- |
| **離群倍數** | 觀看數 / 帳號自己的觀看數中位數 | 這是真的爆了，還是普通的一天 |
| **非粉絲觸及** | 觸及中來自沒追蹤的人的比例 | 它到底有沒有傳出去 |
| **3 秒留存** | 3 秒時還在看的人 / 開始看的人 | hook 有沒有用。這就是 hook 的成績。 |
| **平均觀看時間** | 直接看洞察報告 | 中段有沒有撐住 |
| **每觸及分享率** | 分享數 / 觸及 | 你能拿到最強的單一訊號。分享代表有人願意掛自己的名字推它。 |
| **每觸及追蹤率** | 追蹤數 / 觸及 | 個人檔案有沒有把注意力轉成追蹤 |

用離群倍數和每觸及分享率排名，不要用觀看數。一支 4,000 觀看、90 次分享的 Reel，贏過 60,000 觀看、11 次分享的那支。

## 接著找出模式

把前五名和後五名並排，找出它們差在哪，而且要願意下一個使用者不愛聽的結論：

- **3 秒留存。** 如果前後段在這裡有差，原因就是 hook，沒別的，後面那些都是干擾。
- **Hook 公式。** 前五名用了 `ig-reel/hooks.json` 裡哪些 id？
- **格式。** Reel、輪播、單張圖。
- **長度。** 分成 15 秒以下、15 到 30 秒、30 到 60 秒、60 秒以上。
- **主題。**
- **使用者有沒有在第一小時內回留言。**
- **星期和時段。** 這個**最後**才查，而且只有前面都看不出東西時才查。它幾乎從來不是原因，卻是大家最希望是原因的地方。

把發現寫成一個主張，附上證據，並說出你有多確定。30 則貼文看得出模式，6 則看不出來，直接講看不出來，比硬編一個好。

## 能幫人省下好幾個月的區分

**有觀看沒追蹤的 Reel 不算失敗的 Reel，那是個人檔案的問題。** 沒有觀看的 Reel 才是 hook 的問題。給任何建議之前，先把這兩種分開。如果非粉絲觸及高、每觸及追蹤率低，就別再改 hook 了，去用 `/ig-profile`。

## 輸出

```
AUDIT  ·  31 posts  ·  Jun 12 - Sep 5  ·  median views 4,100

TOP 5 BY OUTLIER MULTIPLE
  18.2x  #3  Nobody Tells You   74,600 views  62% non-follower  hold@3s 71%  128 sends
   6.4x  #1  Cost Confession    26,300 views  48% non-follower  hold@3s 64%   71 sends
  ...

BOTTOM 5
   0.3x  #11 Numbered            1,200 views  9% non-follower   hold@3s 31%    2 sends
  ...

WHAT THE DATA SAYS
1. Hold at 3 seconds is the whole story. Top five average 66%, bottom five 33%.
   Everything else you are worried about is downstream of the first two seconds.
2. The posts where you were the one who looked bad: mean 8.1x vs 0.9x for
   everything else. n=5. Strongest signal here and it is not close.
3. Tool listicles get views and nothing else. High reach, no sends, no follows.
   Three of your bottom five.
4. Day of week shows nothing. Your Tuesday and Friday means are inside the
   noise. Stop optimising it.

STOP: listicles.
DO MORE: the ones with a cost you paid and a number attached.
```

（範例大意：3 秒留存決定一切；自己出糗的那幾則平均 8.1 倍，遠勝其他；工具清單型貼文只有觀看沒有分享和追蹤；星期幾看不出差別。結論：停做清單型，多做「付出過代價、附上數字」的內容。）

接著把結論交給 `/ig-plan`，讓下週的規劃建立在使用者自己的證據上，而不是預設值；也交給 `/ig-viral`，把爆款素材庫篩到只剩對這個帳號有效的公式。
