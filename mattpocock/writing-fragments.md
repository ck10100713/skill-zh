---
layout: "default"
skill: "writing-fragments"
author: "Matt Pocock"
category: "寫作與文件"
summary: "用拷問挖出原始寫作片段，先不管結構"
source: "https://github.com/mattpocock/skills/blob/main/skills/in-progress/writing-fragments/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: writing-fragments
description: "寫作，explore：挖掘原始片段，還沒有結構。"
disable-model-invocation: true
---

<what-to-do>

這是純粹的 **explore**：在不鎖定結構的情況下，拓寬可以寫的東西的空間。鎖定是 _exploit_，是另一個 skill 的工作。進行一場產出片段的 grilling session，毫不留情地訪談使用者，不管他們想寫什麼。強加階段、大綱或文章結構，不在這裡的範圍內。

當片段從對話的任何一方浮現時，就把它們附加到單一一份 markdown 檔。

如果使用者沒傳路徑，就問一次要把文件存在哪裡，然後在這個 session 的剩餘時間裡記住它。

從使用者說的第一句話就開始擷取片段，包括最初的 prompt。

第一次寫入時，在最上面放一個 H1，寫上暫定標題（之後可以改），其他什麼都不放：沒有 metadata、沒有目錄、沒有日期。

</what-to-do>

<supporting-info>

## 什麼是片段

片段是任何可能留存到最終文章的文字。它必須_作者讀得懂_（作者看得出它的意思），但不需要定義自己的術語，也不需要讓毫無背景的讀者看得懂。標準是「這是一段好文字嗎？」，不是「這是一個獨立完整的論點嗎？」

片段刻意是各式各樣的。可以當片段的例子：

- 一句你想在某處用上、但還不知道用在哪的犀利句子。
- 一個主張，加上一行理由。
- 一個小故事：發生過的事、一段程式碼、一個情境、一個類比。
- 一個半成形的想法：「關於 X 為什麼感覺像 Y，之後再想清楚。」
- 一句引用、一段對話、一句偶然聽到的話。
- 一串憑感覺連在一起的相關觀察。
- 一句抱怨、一個坦白、一個笑點。
- 一個**主導詞（leading word）**：一個精簡的比喻或自創詞，整篇文章都可以掛在它上面（用一個詞替想法命名，就像 _tracer bullets_ 或 _fog of war_ 替整個模式命名那樣）。

這些之中，主導詞是最有價值、最值得落下的片段。它有承重作用：在 explore 階段命名對了，它之後會塑造結構、轉場和標題，在整個 exploit 階段持續帶來回報。當對話繞著一個反覆出現的想法打轉時，就推著大家替它造一個詞。

小說家的日記就是範本：多年來沒有結構的觀察，之後被挖掘成原始素材。片段就是觀察。

## 檔案格式

```markdown
# Working title

A first fragment lives here.

It can be multiple paragraphs. It can include lists, code, quotes: whatever
shape the fragment naturally takes.

---

A second fragment.

---

> A quoted line that the user wants to keep around.

A reaction to it.

---

- A cluster of related observations
- That hang together by feel
- And want to be near each other
```

片段之間用水平線分隔（`\n---\n`）。本文裡沒有標題。沒有標籤。除了加入的順序以外沒有其他順序。

## 寫作節奏

安靜地附加。不要為每個片段徵求許可。順帶提一下你加了什麼（「加進去了」），但不要用存檔對話框打斷對話。

每次寫入之前：從磁碟重新讀檔。使用者可能在兩輪之間編輯、重排或刪掉片段，所以要保留他們的改動。絕對不要覆蓋檔案；只能附加（或者，如果使用者要求，原地編輯某個特定片段）。

使用者隨時可以說「砍掉最後一個」「把那個寫得更犀利」「把那兩個合併」。把這些當成最優先的指示。

</supporting-info>
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: writing-fragments
description: "Writing, explore: mine raw fragments, no structure yet."
disable-model-invocation: true
---

<what-to-do>

This is pure **explore**: widen the space of what could be written without committing to structure. Committing is _exploit_, a separate skill's job. Run a grilling session that produces fragments, interviewing the user relentlessly about whatever they want to write about. Imposing phases, outlines, or article structure is out of scope here.

As fragments emerge from either side of the conversation, append them to a single markdown file.

If the user did not pass a path, ask once where to save the document, then remember it for the rest of the session.

Capture fragments from the very first thing the user says, including the initial prompt.

On first write, put a single H1 at the top with a working title (it can change later) and nothing else: no metadata, no TOC, no date.

</what-to-do>

<supporting-info>

## What is a fragment

A fragment is any piece of text that might survive into the final article. It must be _readable by the author_ (the author can tell what it means), but it does not need to define its terms or be comprehensible to a cold reader. The bar is "is this a piece of good writing?", not "is this a self-contained argument?"

Fragments are deliberately heterogeneous. Examples of what could be a fragment:

- A sharp sentence you'd want to deploy somewhere but don't yet know where.
- A claim with a one-line justification.
- A vignette: a thing that happened, a code snippet, a scenario, an analogy.
- A half-thought: "something about how X feels like Y, work this out later."
- A quote, a piece of dialogue, an overheard line.
- A list of related observations that hang together by feel.
- A complaint, a confession, a punchline.
- A **leading word**: a compact metaphor or coinage the whole piece can hang on (one term that names the idea, the way _tracer bullets_ or _fog of war_ names a whole pattern).

Of these, the leading word is the most valuable fragment to land. It is load-bearing: name the right one in explore and it shapes the structure, the transitions, and the title later, paying dividends through the entire exploit phase. When the conversation circles a recurring idea, push to coin a word for it.

The novelist's diary is the model: years of unstructured noticings that later get mined for raw material. Fragments are noticings.

## File format

```markdown
# Working title

A first fragment lives here.

It can be multiple paragraphs. It can include lists, code, quotes: whatever
shape the fragment naturally takes.

---

A second fragment.

---

> A quoted line that the user wants to keep around.

A reaction to it.

---

- A cluster of related observations
- That hang together by feel
- And want to be near each other
```

Fragments are separated by a horizontal rule (`\n---\n`). No headings inside the body. No tags. No order beyond the order they were added.

## Writing rhythm

Append silently. Don't ask permission for each fragment. Mention what you added in passing ("adding that"), but don't interrupt the conversation with save dialogs.

Before every write: re-read the file from disk. The user may have edited, reordered, or deleted fragments between turns, so preserve their changes. Never overwrite the file; only append (or, if the user asks, edit a specific fragment in place).

The user can say "cut the last one", "rewrite that one sharper", "merge those two" at any time. Treat those as first-class instructions.

</supporting-info>
~~~~~
{% endraw %}

</section>
</div>
