---
layout: "default"
skill: "writing-beats"
author: "Matt Pocock"
category: "寫作與文件"
summary: "把素材一個 beat 一個 beat 組成有地基的文章"
source: "https://github.com/mattpocock/skills/blob/main/skills/in-progress/writing-beats/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: writing-beats
description: 寫作，exploit：把原始素材組裝成由一個個 beat 構成的旅程，在某個 beat 倚靠一個術語之前先把它打好地基。
disable-model-invocation: true
---

<what-to-do>

使用者已經（或即將）傳來一份原始素材的 markdown 檔。這是 **exploit**：探索已經做完，素材堆已經固定。決定一條穿過它的路徑，並從素材堆裡挖東西來填每個 beat。

如果使用者沒說文章要存到哪裡，就問一次並記住路徑。

然後進行一場逐 beat 的旅程，像「自己選擇冒險」那種風格：

1. **確立先備知識。** 在任何 beat 之前，先跟使用者確定讀者走進來時已經知道什麼：一開始就**已打好地基（grounded）** 的概念。其他所有東西都必須由某個 beat 先打好地基，後面的 beat 才能使用。見[打地基](#grounding)。
2. 從原始素材寫出 2 到 3 個候選的**起始 beat**。每個都是進入這篇文章的不同入口。每個都只能倚靠已打好地基的概念；註明每一個會打好哪些新概念的地基。在寫進文章檔之前，先把這些 beat 給使用者看。使用者挑一個。預覽那個選擇解鎖了哪些 beat，就像讓使用者往那條路的前方看一小段。
3. 使用者挑好起始 beat 之後，**只把那個 beat** 寫進文章檔。一個 beat 可以是一句話，也可以是好幾段，視那個 beat 本來需要什麼而定。寫到這裡就停。
4. 從磁碟重新讀文章檔。然後提供 2 到 3 個候選的**下一個 beat**：從文章目前的位置出發，旅程可以轉向的不同方向。每個都必須能從目前已打好地基的集合抵達；註明每一個會打好什麼地基。
5. 重複第 3 到 5 步，直到文章自然結束。

</what-to-do>

<supporting-info>

## 打地基

每個**概念**在某個 beat 能倚靠它之前，都必須先**打好地基**：讀者要嘛走進來時就知道，要嘛在之前的 beat 遇過它。一個去抓還沒打好地基的概念的 beat 會讓讀者迷路；這是旅程唯一不能做的一步。單位是概念，不是它的名稱：就算看不到任何行話，一個 beat 也可能倚靠讀者缺少的想法。如果概念有名稱（一個**術語**），替它打地基就是把想法和術語一起落地。

一個概念有兩種方式被打好地基：

- **先備知識（Prerequisite）**：在第一個 beat 之前就已打好地基。由讀者自己帶來。一開始就固定。
- **引入（Introduced）**：由某個 beat 建立它，從此對之後的每個 beat 來說它都已打好地基。

所以每個 beat 做兩件事：它**需要**已經打好地基的概念，而且它**打好**新的概念的地基。隨時保持一份目前為止已打好地基的清單，每個 beat 落地時就更新。

這就是塑造「自己選擇冒險」的東西。一個候選 beat 只有在它需要的一切都已打好地基時才抵達得了；選一個替概念 X 打地基的 beat，會解鎖所有等著 X 的 beat。你提供下一個 beat 時，它們都必須能從目前已打好地基的集合抵達，並且說明每一個打好什麼地基，這樣使用者才看得出它開啟了哪些路。

最大的槓桿是：你讓什麼變成先備知識、又讓什麼在文章裡面打地基。前面要求太多，就會把沒有那些知識的讀者擋在門外；裡面打太多地基，開頭的 beat 就會淹沒在定義裡。確立先備知識時，要跟使用者一起決定這點，並且每當一個誘人的 beat 結果需要一個還沒人打過地基的概念時，就重新檢討：解法要嘛是在它之前加一個打地基的 beat，要嘛是把那個概念升格成先備知識。

## 什麼是 beat

beat 是旅程中的一步。它只做一件事：鋪設場景、落下一個重點、問一個問題、丟出一個題外話、轉個角度。然後就停，把讀者留在下一個 beat 可以轉向的位置。

beat 的大小取決於它需要什麼：

- 如果那一步就只有這樣，就是一句話（「然後三個星期什麼事都沒發生。」）。
- 如果那一步需要鋪陳，就是一小段。
- 如果 beat 是一個獨立的小故事、論證或範例，就是好幾段。

如果一個「beat」需要五段和三個小標題，它就不是 beat；它是兩個 beat 黏在一起。把它拆開。

## 從素材堆裡取材

從原始素材堆取材，來填充每個 beat。你可以改寫、拆開、重新組合或引用。素材堆是採石場。

## 結束旅程

文章在旅程完成時結束，不是在素材堆用完時。大多數素材堆都會有沒用上的剩餘片段。這沒問題；這正是素材比你需要的多的意義。

## 寫作節奏

- 一次附加一個 beat。絕對不要先寫後面的。
- 每次寫入之前，都從磁碟重新讀文章檔。絕對要保留使用者的編輯。
- 如果使用者大幅修改了之前的 beat，就讓它改變接下來的內容。
- 如果使用者說「重寫那個 beat」或「回去試試不同的第 3 個 beat」，就照做：原地編輯，其他的不要動。

</supporting-info>
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: writing-beats
description: Writing, exploit; assemble raw material into a journey of beats, grounding each term before a beat leans on it.
disable-model-invocation: true
---

<what-to-do>

The user has passed (or will pass) a markdown file of raw material. This is **exploit**: the exploring is done, the pile is fixed. Commit to a path through it and mine the pile to fill each beat.

If the user did not say where to save the article, ask once and remember the path.

Then run a beat-by-beat journey, choose-your-own-adventure style:

1. **Establish the prerequisites.** Before any beats, settle with the user what the audience already knows walking in: the concepts that are **grounded** from the start. Everything else must be grounded by a beat before a later beat can use it. See [Grounding](#grounding).
2. Write 2–3 candidate **starting beats**, drawn from the raw material. Each is a different entry point into the article. Each may only lean on grounded concepts; note what new concepts each one grounds. Show the user the beats before writing to the article file. The user picks one. Preview what beats that pick unlocks, as if the user is seeing a little way down the path.
3. Once the user picks a starting beat, write **only that beat** to the article file. A beat may be one sentence or several paragraphs, whatever that beat naturally is. Stop there.
4. Re-read the article file from disk. Then offer 2–3 candidate **next beats**: different directions the journey could pivot to from where the article now stands. Each must be reachable from the current grounded set; note what each one grounds.
5. Loop steps 3–5 until the article reaches a natural end.

</what-to-do>

<supporting-info>

## Grounding

Every **concept** has to be **grounded** before a beat can lean on it: the audience either walked in knowing it or met it in an earlier beat. A beat that reaches for an ungrounded concept loses the reader; that is the one move the journey can't make. The unit is the concept, not the word for it: a beat can lean on an idea the reader lacks even with no jargon in sight. Where a concept has a name (a **term**), grounding it means landing the idea and the term together.

A concept gets grounded one of two ways:

- **Prerequisite**: grounded before the first beat. The audience brings it. Fixed at the start.
- **Introduced**: a beat establishes it, and from then on it's grounded for every later beat.

So each beat does two jobs: it **requires** concepts that are already grounded, and it **grounds** new ones. Keep a running list of what's grounded so far, and update it each time a beat lands.

This is what shapes the choose-your-own-adventure. A candidate beat is only reachable if everything it requires is already grounded; picking a beat that grounds concept X unlocks every beat that was waiting on X. When you offer next beats, they must all be reachable from the current grounded set, and say what each one grounds, so the user can see which paths it opens.

The big lever is what you make a prerequisite versus what you ground inside the piece. Demand too much up front and you shut out readers who don't have it; ground too much inside and the early beats drown in definitions. Settle this with the user when you establish prerequisites, and revisit it whenever a tempting beat turns out to require a concept nothing has grounded yet: the fix is either a grounding beat before it, or promoting the concept to a prerequisite.

## What is a beat

A beat is one move in the journey. It does one thing: sets a scene, lands a point, asks a question, drops an aside, twists the angle. Then it stops, leaving the reader at a place where the next beat can pivot.

A beat is sized by what it needs:

- A single sentence if that's all the move is ("And then nothing happened for three weeks.").
- A short paragraph if the move needs setup.
- Multiple paragraphs if the beat is a self-contained vignette, argument, or example.

If a "beat" needs five paragraphs and three subheadings, it's not a beat; it's two beats glued together. Split it.

## Pulling from the pile

Pull material from the raw pile to populate each beat. You can paraphrase, split, recombine, or quote. The pile is a quarry.

## Ending the journey

The article ends when the journey is complete, not when the pile is empty. Most piles will have leftover fragments that don't make it in. That is fine; that is the point of having more raw material than you need.

## Writing rhythm

- Append one beat at a time. Never write ahead.
- Re-read the article file from disk before every write. Preserve user edits absolutely.
- If the user edits a previous beat substantially, let it change what comes next.
- If the user says "rewrite that beat" or "go back and try a different beat 3", do it: edit in place, leave the rest alone.

</supporting-info>
~~~~~
{% endraw %}

</section>
</div>
