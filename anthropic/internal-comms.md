---
layout: "default"
skill: "internal-comms"
author: "Anthropic"
category: "寫作與文件"
summary: "依溝通類型載入對應範本，寫 3P 更新、電子報、FAQ 等內部文件"
source: "https://github.com/anthropics/skills/blob/main/skills/internal-comms/SKILL.md"
license: "Apache-2.0"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: internal-comms
description: 一套協助我撰寫各種內部溝通文件的資源，使用我的公司慣用的格式。只要被要求寫任何內部溝通（狀態報告、主管更新、3P 更新、公司電子報、FAQ、事故報告、專案更新等），Claude 都應該使用這個 skill。
license: Complete terms in LICENSE.txt
---

## 什麼時候用這個 skill
要寫內部溝通文件時，這個 skill 適用於：
- 3P 更新（Progress、Plans、Problems，進度、計畫、問題）
- 公司電子報
- FAQ 回覆
- 狀態報告
- 主管更新
- 專案更新
- 事故報告

## 怎麼用這個 skill

要寫任何內部溝通文件：

1. **從需求判斷溝通類型**
2. **從 `examples/` 目錄載入對應的指引檔**：
    - `examples/3p-updates.md` - 給 Progress/Plans/Problems 團隊更新
    - `examples/company-newsletter.md` - 給全公司電子報
    - `examples/faq-answers.md` - 回答常見問題
    - `examples/general-comms.md` - 其他不明確符合上述任何一類的情況
3. **照那個檔案裡的具體指示**處理格式、語氣和內容蒐集

如果溝通類型跟現有的指引都對不上，就問使用者想要的格式，或請他們補充更多背景。

## 關鍵字
3P updates, company newsletter, company comms, weekly update, faqs, common questions, updates, internal comms
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: internal-comms
description: A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use this skill whenever asked to write some sort of internal communications (status reports, leadership updates, 3P updates, company newsletters, FAQs, incident reports, project updates, etc.).
license: Complete terms in LICENSE.txt
---

## When to use this skill
To write internal communications, use this skill for:
- 3P updates (Progress, Plans, Problems)
- Company newsletters
- FAQ responses
- Status reports
- Leadership updates
- Project updates
- Incident reports

## How to use this skill

To write any internal communication:

1. **Identify the communication type** from the request
2. **Load the appropriate guideline file** from the `examples/` directory:
    - `examples/3p-updates.md` - For Progress/Plans/Problems team updates
    - `examples/company-newsletter.md` - For company-wide newsletters
    - `examples/faq-answers.md` - For answering frequently asked questions
    - `examples/general-comms.md` - For anything else that doesn't explicitly match one of the above
3. **Follow the specific instructions** in that file for formatting, tone, and content gathering

If the communication type doesn't match any existing guideline, ask for clarification or more context about the desired format.

## Keywords
3P updates, company newsletter, company comms, weekly update, faqs, common questions, updates, internal comms
~~~~~
{% endraw %}

</section>
</div>
