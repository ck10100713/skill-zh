---
layout: "default"
skill: "implement"
author: "Matt Pocock"
category: "測試與驗證"
summary: "照 spec 或 ticket 實作，用 tdd 並收尾 review"
source: "https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: implement
description: "依據 spec 或一組 ticket 實作一項工作。"
disable-model-invocation: true
---

實作使用者在 spec 或 ticket 裡描述的工作。

如果使用者給的是 ticket 參照，先去 issue tracker 抓下來，開工前先講出它的標題。如果參照有歧義，就問。

可行的話，用 Skill 工具呼叫 "tdd"，並且在事先講好的 seam 上做。

型別檢查要常跑，單一測試檔要常跑，完整測試套件最後跑一次就好。

做完之後，用 Skill 工具呼叫 "code-review" 來 review 這次的工作。

把你的成果 commit 到目前的 branch。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "code-review" to review the work.

Commit your work to the current branch.
~~~~~
{% endraw %}

</section>
</div>
