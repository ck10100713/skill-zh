---
name: ig-human
description: 把草稿裡的機器指紋清掉，包括破折號（em dash）、AI 套話、看不見的浮水印字元，送出前再用五項檢測打分數。只要文字需要聽起來像真人就用，例如使用者說 humanize、「這聽起來像 AI 嗎」、「把破折號拿掉」、「de-slop 一下」、「這很像 ChatGPT 寫的」，或是任何 caption（貼文文案）、腳本、留言、回覆、私訊要給使用者看之前。
---

# ig-human

這個資料夾裡有兩個工具，兩個都真的能跑。用它們，不要用肉眼看。

```bash
python3 humanize.py draft.txt --report        # clean it, show what changed
python3 detect.py draft.txt                    # score it, five checks
python3 detect.py before.txt after.txt         # prove the delta
```

兩個工具都會讀 `slop.json`：裡面有 154 個套話單字和片語，各自配好白話的替代詞，另外有 18 類看不見的字元、11 種排版替換、16 個結構上的破綻。每份清單的最後一段是 Instagram 專用的，就是只會出現在 caption 和旁白裡的那些詞。這個檔案本來就是拿來改的。如果使用者有個慣用詞被詞庫拿掉了，就從檔案裡刪掉它。

## 為什麼這件事在 Instagram 上比看起來更重要

Caption 很短，腳本是要唸出來的。在 600 字元的 caption 裡，一句很像書面語的句子，佔整段文字的比例比放在一篇長文裡大得多。旁白如果沒人能自然唸出來，第一次錄就會很明顯。這裡真正會露餡的，不是偵測器把貼文標出來，是有人滑過一則讀起來像品牌官方的東西，或是創作者自己唸自己的腳本都卡住。

## 會自動修掉的

**1. 看不見的字元。** 零寬空格和零寬連接符、word joiner、軟連字號、BOM（位元組順序標記）、Unicode tag 字元、隱形分隔符、不換行空格和窄空格。鍵盤打不出這些東西。它們複製貼上後還在，在每個編輯器裡都看不到，是生成文字裡最機械化的痕跡。`humanize.py` 會全部刪掉，連沒有名字對應的其他 Unicode 格式字元也一起刪。

**2. 排版。** 破折號（em dash）換成逗號，短破折號（en dash）換成連字號，彎引號換成直引號，刪節號換成三個點，項目符號換成連字號。破折號這一關最重要：它會把破折號換成逗號，再把因此留下的重複標點和多出來的句點清乾淨。

**3. 套話詞庫。** delve、leverage、robust、seamless、crucial、testament to、"in today's fast-paced world"，再加上 Instagram 那一段："stop scrolling"、"in today's video"、"follow for more"、"tag someone who needs this"、"the algorithm loves"、"run don't walk"。每個都會換成白話的詞或直接刪掉，保留原本的大小寫，網址不會動到。

## 不會自動修的

結構上的破綻只會**標出來，不會改寫**，因為改句子的結構需要判斷：

- "It's not just X, it's Y" 和 "not only X but also Y"（「不只是 X，更是 Y」這類句型）
- 三段式排比
- 單字一行的設問句："The result?"（「結果呢？」）
- 影片開場白："in this video I'm going to show you"（「這支影片我要教你」）
- 用 emoji 當項目符號的清單
- 連續三個以上全大寫的字
- 一整面 hashtag 牆
- 反射性的討互動句："follow for more"、"tag someone who"、"double tap if"

這份清單是你的工作。每一行被標出來的句子都要親手改寫，意思保留，然後重跑 `detect.py`。分數要從 REVIEW 變成 PASS，靠的就是這一步，這也是腳本做不到的部分。

## 五項檢測

`detect.py` 會對五個訊號打 0 到 100 分，越高越像人：

| 檢測 | 量什麼 | 機器寫的長怎樣 |
| --- | --- | --- |
| BURSTINESS | 句子長度的變化 | 每句都一樣長 |
| SPECIFICITY | 每 100 字裡的數字、名字、具體細節 | 抽象名詞，沒有數字 |
| SLOP DENSITY | 每 100 字命中詞庫幾次 | 罐頭詞彙 |
| FINGERPRINT | 每 1000 字元的隱形字元、破折號、彎引號 | 排版完美得不像人 |
| VOICE | 縮寫、人稱、結構破綻 | 沒有縮寫，刻意鋪陳的揭曉 |

最後判定是平均分佔 60%，**最弱的那一項**佔 40%，因為只要一個訊號就夠露餡了。要拿到 PASS，總分要 70 以上，而且沒有任何一項低於 55。

## 老實講清楚

這是五個在本機跑的經驗法則，參考公開偵測器會看的那些訊號做出來的。全部在使用者的電腦上跑，什麼都不會上傳。它們**不是** GPTZero、Originality、Copyleaks、Winston 或 Turnitin，不會呼叫那些 API，也沒辦法保證那些工具的判定結果。修好這裡量到的東西，通常會讓那些分數跟著動，因為大家量的是同樣的底層特徵。說法就到這裡為止。不要替使用者講得更誇張，也不要跟使用者說他的文字偵測不出來。

## 操作順序

1. `humanize.py draft.txt -o clean.txt --report`
2. 看結構破綻的標記，自己把那幾行改寫。
3. `detect.py draft.txt clean.txt`，秀出前後對照。
4. 如果判定不是 PASS，就修輸出裡點名的最弱那一項，再跑一次。跑兩輪很正常。跑到五輪代表這份草稿是照公式寫的，解法是換一份草稿，多跑幾輪沒用。
5. 給使用者看清理後的文字和分數。絕對不要只給分數。
