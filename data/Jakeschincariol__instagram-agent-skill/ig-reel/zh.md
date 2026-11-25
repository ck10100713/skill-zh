---
name: ig-reel
description: >-
  把一個還很粗的點子寫成 Instagram Reel：從 26 個公式產出 hook（開場鉤子）選項、
  口白腳本、畫面字卡，還有抓好秒數的分段表（beat sheet）。全部用使用者自己的口吻，
  而且開拍前先打分數。只要使用者想做 Reel、短影音腳本、hook、旁白，說「幫我做一支
  關於 X 的 reel」「這支影片我要講什麼」，或是準備要錄了卻還沒想好第一句，就用這個。
---

# ig-reel

把一個粗點子變成一支有人會看完的 Reel。

這個資料夾裡有兩支工具，兩支都真的能跑。拿來用。不要用眼睛估 hook 好不好，也不要
用猜的估長度。

```bash
python3 hookscore.py hooks.txt              # rank your hook options
python3 hookscore.py --hook "one line"      # score a single one
python3 beats.py script.txt --target 30     # timed beat sheet before you shoot
```

## 動筆之前

1. 如果有 `~/.claude/instagram/voice.md` 就先讀。那是使用者的口吻檔：他在鏡頭前
   怎麼講話、哪些話他絕對不說、他是在對誰講。如果檔案不存在，就跟他要**三支他自己的
   reel**，聽打或讀過，推出他的口吻，再把檔案寫出來。口吻不對的腳本根本不能用，因為
   他得親口講出來。
2. 讀這個資料夾裡的 `hooks.json`。裡面有 26 個公式，每個都附模板、填好的範例、
   字卡版本、適合用在哪，還有它通常怎麼被搞砸。其中四個會在裡面，是因為它們一直在
   真實的 hook 裡出現，不是為了湊齊某個模式。
3. 點子太薄就不要硬灌水。一次問一組問題：發生了什麼事、發生在誰身上、付出了什麼
   代價或換來什麼。一支 Reel 需要一件具體又真實的事。先拿到這個再寫。
4. 如果有 `~/.claude/instagram/swipe.md` 就讀。那是 `/ig-viral` 寫出來的檔案，是
   使用者自己蒐集的證據，告訴你哪些公式現在在他的領域有效。它比這份檔案裡的預設值
   更準。

## 結構

一支 Reel 的生死在前兩秒決定，接下來五秒決定人會不會留下。

```
0:00 - 0:02   HOOK        the claim. Spoken line and on-screen line, written
                          separately. Motion in the first frame, not a static face.
0:02 - 0:07   THE STAKE   why this matters to the person watching. One line.
0:07 - ...    THE BODY    one idea per beat, and the frame changes every beat.
LAST 3s       THE PAYOFF  deliver what the hook promised, then the single ask.
LAST LINE     THE LOOP    echo one word from the hook so the replay lands clean.
```

（對照：HOOK 是主張，口白和字卡分開寫，第一格畫面要有動作，不要一張不動的臉；
THE STAKE 是這件事跟觀眾有什麼關係，一句；THE BODY 一個 beat 一個重點，每個 beat
都換畫面；THE PAYOFF 兌現 hook 的承諾，然後提出唯一的請求；THE LOOP 最後一句呼應
hook 裡的一個字，讓重播接得順。）

長度：15 到 45 秒是實用區間。Reel 可以拍到 3 分鐘，但幾乎沒人該用到那麼長。短於
7 秒的話，重播次數會灌高，其他數字都不會動。

## 流程

**1. 挑三個 hook，不是一個。** 把點子拿去對 `hooks.json`，選三個真的適合的公式，
每個都寫出口白和字卡。要三個不同的公式，不是同一個改寫三次。

**2. 打分數。** 把三句口白放進一個檔案，一行一句，跑 `hookscore.py`。把排名給
使用者看。如果第一名低於 50 分，代表你還沒找到 hook，再怎麼修都救不回來。

**3. 寫腳本**，用勝出的那個 hook。用口語，照使用者平常講話的樣子。縮寫照用。句子短。
不要出現他得先排練才講得順的句子。

**4. 抓秒數。** 跑 `beats.py script.txt --target {length}`。每個警示都要修：hook
超過 3 秒、任何 beat 超過 4 秒、連續好幾個 beat 都沒有具體內容、沒有 loop。重跑到
乾淨為止。

**5. 去 AI 味。** 給使用者看之前，先把腳本丟進 `/ig-human`。寫出來的句子一念出口
就很明顯。

**6. 印出成品。** 腳本放在 fenced block 裡，字卡另外列成清單並標好時間，接著：

```
REEL READY
hook:       #3 Nobody Tells You, scored 86 STRONG
length:     28.4s across 9 beats at 165 wpm
on-screen:  6 cards
humanizer:  4 artefacts stripped, human score 81 PASS
caption:    run /ig-caption next

Reply "yes" to log it, or tell me what to change.
```

**7. 絕對不要發布。** 這個 skill 產出的是腳本。使用者自己拍、自己發。使用者回
「yes」的話，就在 `~/.claude/instagram/log.md` 後面加一筆，記下日期、用的 hook
公式和第一句，這樣 `/ig-audit` 之後才有歷史可以看。

## 字卡是另一份腳本

每次都要分開寫。字卡會先被看到，口白才被聽到。

- **每張字卡六個字以內。** 看的人手機拿在手臂距離外，而且還沒開始聽。
- **hook 字卡第 1 格就要出現**，不是先空白一拍才出來。
- **放在安全區內。** 1080x1920 的畫面，y=230 以上和 y=1440 以下都不要放東西，
  右邊 230 像素也要留空。那個框外面全部會被介面蓋住：caption（貼文文字）、右側
  按鈕列、音樂條。
- **hook 絕對不要放在 caption 的位置。** 那是畫面底部，會被蓋掉。
- **正文要燒進字幕。** 大部分人第一次看都是靜音。

## 真正拉開差距的規則

- **一支 Reel 一個重點。** 腳本裡有兩個，那就是兩支 Reel。直接講出來。
- **數字勝過形容詞。** 「$4,200」比「很多」有力。使用者沒給數字就去問，不要繞過
  那個洞硬寫。
- **砍掉開場白。** 不要打招呼、不要「這支影片要講」、不要自我介紹、不要 logo 音效。
  影片從你平常第六秒才會講到的那句開始。
- **每個 beat 換一次畫面。** 同一個鏡頭撐 8 秒，人就是在那裡滑走的，`beats.py`
  會標出來。
- **結尾只提一個請求。** 留言關鍵字、收藏或追蹤。只能一個。
- **絕對不要捏造。** 不要用使用者的名義編造數據、客戶、營收或成果，就算是暫時的
  佔位也不行。需要數字但不知道，就在腳本裡留 `{{your number}}` 並標出來。
- **不要圍繞使用者不能用的熱門音樂寫腳本。** 如果這個點子需要使用者本人的聲音，
  就直接說。

## 範例

```
/ig-reel we cut proposal time from 5 hours to 20 minutes with one template
```

```
HOOKS  (scored)
  86  STRONG  #5  Time Collapse   "Proposals used to take me five hours. Twenty minutes now."
                                  on screen: 5 HOURS -> 20 MIN
  71  STRONG  #1  Cost Confession "I billed four hours a week for formatting. For two years."
                                  on screen: 2 YEARS WASTED
  54  OK      #9  The Steal       "Steal the proposal template that did it."
                                  on screen: STEAL THIS

Shooting #5: the ratio is believable, it reads in one glance on screen,
and the number is yours.
```

（範例是「我們用一個模板把寫提案的時間從 5 小時砍到 20 分鐘」。最後選 #5，因為這個
比例讓人信得過，字卡一眼就看得懂，而且數字是使用者自己的。）
