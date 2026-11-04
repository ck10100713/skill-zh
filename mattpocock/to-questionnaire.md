---
layout: "default"
skill: "to-questionnaire"
author: "Matt Pocock"
category: "規劃與釐清"
summary: "把你答不出來的決策變成問卷給別人填"
source: "https://github.com/mattpocock/skills/blob/main/skills/productivity/to-questionnaire/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: to-questionnaire
description: 把你沒辦法完全回答的決策，變成一份讓別人填寫的問卷。
disable-model-invocation: true
---

把使用者自己沒辦法回答的事，變成一份**問卷**：一份 Markdown 文件，交給某個人非同步填寫，或是開會時一起填。收件人握有使用者缺少的知識；問卷就是把它從他們身上挖出來。

**拷問「寄送」，不是拷問「主題」。** 只針對「寄送」這件事訪談使用者，這是他們一定答得出來的：寄給誰、需要對方回什麼。文件裡的問題則針對收件人知道的和使用者需要的之間的**落差**。


1. **要寄給誰？** 用一次交流問出收件人的角色、專長，以及跟使用者的關係。這會決定問卷的語氣和需要帶多少 context。完成的標準是你知道收件人是誰，以及他知道哪些使用者不知道的事。

2. **你需要對方回什麼？** 用一次交流問出使用者自己解決不了、需要從這個人那裡得到的具體決策或事實。完成的標準是你有一份具體清單，列出使用者拿到回覆後必須能做到或能決定的事。

3. **寫問卷。** 針對第 1、2 步的落差擬定問題，照下面的文件結構。寫到目前目錄的 `to-questionnaire-<slug>.md`（slug 取自主題），並回報路徑。完成的標準是檔案存在，而且使用者在第 2 步提到的每一項都有對應的問題涵蓋。

## 文件結構

把文件包裝成一份**探索式問卷**：使用者缺少 context，收件人握有它。問題依重要性由高到低排序，因為非同步代表你可能只有一次機會；一旦超過少數幾題，就依主題用 `##` 標題分組。用下面的範本來寫。

<questionnaire-template>

# <問卷標題>

**目的：** 為什麼有這份問卷，以及有哪個決策押在它上面。

**來自：** <使用者>，**給：** <收件人>，**你的回答會怎麼被使用：** <去向>

## 背景

一段話，讓不在使用者腦袋裡的收件人搞清楚方向。足夠讓他回答得好就好，不要寫到一頁。

## 怎麼回答

截止日和大概需要的心力。只回答一部分和「我不知道」都有用：把不確定的標出來，不要直接跳過。

## <主題標題>

每個主題一個 `##` 區塊。每個區塊底下放它的問題，依重要性由高到低。每個問題只有一個想法，絕不複合，正下方直接附一個答案欄，只有在問題可能被誤解或容易引來敷衍回答時，才加一行_為什麼這很重要_。

<question-example>
### 上線時，系統預期要承受多大的負載？

_為什麼這很重要：它決定我們現在就要為突發流量配置資源，還是可以延後。_

>
</question-example>

## 還有其他嗎？

結尾的萬用題：有沒有我們沒問到、但應該知道的事？

</questionnaire-template>
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: to-questionnaire
description: Turn a decision you can't fully answer into a questionnaire for someone else to fill in.
disable-model-invocation: true
---

Turn something the user can't answer alone into a **questionnaire**: a Markdown document they hand to one person to fill in async, or fill out together over a meeting. The recipient holds knowledge the user lacks; the questionnaire pulls it out of them.

**Grill the send, not the subject.** Interview the user only about the _send_, which they can always answer: who it goes to, and what they need back. The questions in the document then target the **gap** between what the recipient knows and what the user needs.


1. **Who is it going to?** Ask, in one exchange, the recipient's role, expertise, and relationship to the user. This fixes the questionnaire's tone and how much context it must carry. Done when you know who the recipient is and what they know that the user doesn't.

2. **What do you need back?** Ask, in one exchange, the specific decisions or facts the user can't resolve alone and needs from this person. Done when you have a concrete list of what the user must walk away able to do or decide.

3. **Write the questionnaire.** Draft questions aimed at the gap from steps 1–2, following the Document structure below. Write it to `to-questionnaire-<slug>.md` in the current directory (slug from the topic) and report the path. Done when the file exists and every item the user named in step 2 is covered by a question.

## Document structure

Frame the document as a **discovery questionnaire**: the user lacks context, the recipient holds it. Order questions most-important-first, since async means you may only get one pass, and group them under `##` headings by theme once there are more than a handful. Write it using the template below.

<questionnaire-template>

# <Questionnaire title>

**Purpose:** why this questionnaire exists and the decision riding on it.

**From:** <the user>, **To:** <the recipient>, **How your answers will be used:** <where they go>

## Context

One paragraph orienting a recipient who wasn't in the user's head. Enough to answer well, not a page.

## How to answer

Deadline and rough effort. Partial answers and "I don't know" are useful: flag anything you're unsure of rather than skipping it.

## <Theme heading>

One `##` section per theme. Under each, its questions, most-important-first. Every question is one idea, never compound, with an answer stub directly beneath, and a one-line _why this matters_ only where the question could be misread or invite a throwaway answer.

<question-example>
### What load is the system expected to handle at launch?

_Why this matters: it decides whether we provision for burst traffic now or defer it._

>
</question-example>

## Anything else?

A closing catch-all: anything we didn't ask that we should know?

</questionnaire-template>
~~~~~
{% endraw %}

</section>
</div>
