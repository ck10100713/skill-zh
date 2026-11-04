---
layout: "default"
skill: "grilling"
author: "Matt Pocock"
category: "規劃與釐清"
summary: "用設計樹一輪一輪拷問你的想法，直到沒有任何假設"
source: "https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: grilling
description: 針對計畫、決策或想法，毫不留情地拷問使用者。當使用者想對自己的想法做壓力測試，或用了任何「grill」相關觸發詞時使用。
---

毫不留情地訪談使用者，直到你們達成共識。把整件事畫成一棵**設計樹**：每個決策都會分岔出掛在它底下的其他決策。

用**回合**來處理這棵樹。**前線（frontier）**是所有前置條件都已經定案的決策，也就是你_現在_就能問、不必去猜還沒聽到的答案的那些問題。一個回合就把整條前線一次問完：每題編號，並附上你的建議答案。然後等使用者回答完，再進下一回合。

一個回合的格式長這樣：

```
❓ **Q1** - **<問題標題>**: <問題內容，可以有好幾段，也可以附多個選項>

➡️ <你的建議答案>

---

❓ **Q2** - **<問題標題>**: <問題內容，可以有好幾段，也可以附多個選項>

➡️ <你的建議答案>
```

每題的措辭要讓使用者回「好」就等於採用你的建議答案。

使用者每回答一輪，樹就會重塑：定案的決策把前線往外推，解鎖原本卡在它們身上的問題。重新算出前線，再問下一回合。如果某題的答案取決於這回合另一個還沒回答的問題，它屬於_之後_的回合，不屬於這一回合。

找_事實_是你的工作，永遠不是使用者的。前線上的問題如果需要環境裡的事實（檔案系統、工具等等），就派一個有全新 context window 的 sub-agent 去查；凡是你自己查得到的東西，都不要問使用者。也不要因此卡住：一個還在跑的探查就是一個尚未定案的前置條件，所以只有依賴它的下游問題要等 sub-agent 回報，前線上其他問題現在就問。_決策_是使用者的：每一個都交給他們決定，然後等。

前線清空時，這次訪談就結束了：設計樹的每條分支都走過，沒有任何東西被默默假設。在使用者確認你們已經達成共識之前，不要依此採取行動。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent with a fresh context window to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
~~~~~
{% endraw %}

</section>
</div>
