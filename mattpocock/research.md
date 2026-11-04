---
layout: "default"
skill: "research"
author: "Matt Pocock"
category: "除錯與調查"
summary: "丟給背景 agent 查第一手來源並寫成文件"
source: "https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: research
description: 對照高可信度的第一手來源調查一個問題，並把發現存成 repo 裡的一份 Markdown 檔。當使用者想要研究某個主題、蒐集文件或 API 的事實，或要把查資料的苦工丟給背景 agent 時使用。
---

啟動一個**背景 agent** 來做研究，這樣它在讀資料的時候你可以繼續工作。讓它從全新的 context window 開始。

它的工作：

1. 對照**第一手來源**（官方文件、原始碼、規格、官方 API）調查這個問題，不要看別人整理的二手文章。每個說法都要追回到擁有它的原始出處。
2. 把發現寫進單一一份 Markdown 檔，每個說法都標明出處。
3. 存在 repo 原本就放這類筆記的地方；照現有慣例，如果沒有慣例，就放在合理的位置並說明放哪。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads. Start it with a fresh context window.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
~~~~~
{% endraw %}

</section>
</div>
