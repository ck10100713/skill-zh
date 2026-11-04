---
layout: "default"
skill: "claude-handoff"
author: "Matt Pocock"
category: "Agent 與工作流"
summary: "把對話交接給背景 agent，讓它立刻接著做"
source: "https://github.com/mattpocock/skills/blob/main/skills/in-progress/claude-handoff/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: claude-handoff
description: 把目前的對話交接給一個全新的背景 agent，讓它立刻接手工作。
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

寫一份交接摘要，總結目前的對話，讓全新的 agent 可以接著做下去。存到使用者作業系統的暫存目錄，然後啟動一個背景 agent，用這份摘要當它的 prompt：`claude --bg --name "<descriptive name>" -- "$(cat <summary file>)"`。傳檔案的方式可以避免 shell 去執行摘要裡的反引號或展開 `$`。它會在目前的工作目錄啟動並立刻返回；使用者用 `claude agents` 來管理它。

一定要帶 `-n`/`--name` 並取一個有描述性的名字（例如 `--name "Fix login bug"`）；它決定在工作清單、session 選擇器和終端機標題上顯示的名稱。

摘要裡要有一節「suggested skills」，列出下一個 agent 該用 Skill 工具呼叫哪些 skill。

其他產出物已經記錄過的內容（spec、計畫、ADR、issue、commit、diff）不要重複寫，用路徑或 URL 引用就好。

敏感資訊一律遮掉，例如 API key、密碼、個人可識別資訊，因為這份摘要會變成 agent 的 prompt。

如果使用者有帶參數，就把它當成下一個 session 要專注的事，並據此調整摘要內容。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: claude-handoff
description: Hand the current conversation off to a fresh background agent that picks up the work immediately.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a handoff summary of the current conversation so a fresh agent can continue the work. Save it to the temporary directory of the user's OS, then launch a background agent seeded with it as its prompt: `claude --bg --name "<descriptive name>" -- "$(cat <summary file>)"`. Passing the file keeps the shell from running backticks or expanding `$` in the summary. It starts in the current working directory and returns immediately; the user manages it with `claude agents`.

Always pass `-n`/`--name` with a descriptive name (e.g. `--name "Fix login bug"`); it sets the display name shown in the job list, session picker, and terminal title.

Include a "suggested skills" section in the summary, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information, since the summary becomes the agent's prompt.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the summary accordingly.
~~~~~
{% endraw %}

</section>
</div>
