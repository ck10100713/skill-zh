---
layout: "default"
skill: "handoff"
author: "Matt Pocock"
category: "Agent 與工作流"
summary: "把目前對話壓成交接文件給下一個 agent"
source: "https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: handoff
description: 把目前的對話壓縮成交接文件，讓另一個 agent 接手。
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

寫一份交接文件，總結目前的對話，讓全新的 agent 可以接著做下去。存到使用者作業系統的暫存目錄（`$TMPDIR`，沒有就用 `/tmp`；Windows 是 `%TEMP%`），不要存在目前的 workspace。

文件裡要有一節「suggested skills」，列出下一個 agent 該用 Skill 工具呼叫哪些 skill。

其他產出物已經記錄過的內容（spec、計畫、ADR、issue、commit、diff）不要重複寫，用路徑或 URL 引用就好。

敏感資訊一律遮掉，例如 API key、密碼、個人可識別資訊。

如果使用者有帶參數，就把它當成下一個 session 要專注的事，並據此調整文件內容。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows) - not the current workspace.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
~~~~~
{% endraw %}

</section>
</div>
