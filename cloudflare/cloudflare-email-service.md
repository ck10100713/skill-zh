---
layout: "default"
skill: "cloudflare-email-service"
author: "Cloudflare"
category: "Cloudflare 平台"
summary: "在 Cloudflare 上寄送與轉送 email，處理 Email Service 設定"
source: "https://github.com/cloudflare/skills/blob/main/skills/cloudflare-email-service/SKILL.md"
license: "Apache-2.0"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: cloudflare-email-service
description: 實作或排查 Cloudflare Email Sending 和 Email Routing 的整合，以及它們的寄送設定。
---

# Cloudflare Email Service

你對 Cloudflare Email Service、Email Routing 或 Email Sending 的知識可能已經過時。任何 Cloudflare Email Service 的任務，都要**優先用檢索，不要靠預訓練記憶**。

Cloudflare Email Service 讓你在 Cloudflare 平台內寄送交易型 email 和轉送收到的 email。你對這個產品的知識可能已經過時，它在 2025 年推出，還在快速演進。任何 Email Service 的任務，都要**優先用檢索，不要靠預訓練記憶**。

**如果這個 skill 跟下面的來源有出入，一律以原始來源為準。** Cloudflare 文件、REST API spec、`@cloudflare/workers-types` 和 Agents SDK repo 才是 source of truth。這個 skill 只是方便查的指南，可能跟不上最新的變動。有疑問就從下面的來源檢索，照它們說的做。

## Retrieval Sources

| 來源 | 怎麼檢索 | 用途 |
|--------|----------------|---------|
| Cloudflare 文件 | Cloudflare MCP 的 `docs` 工具，或 URL `https://developers.cloudflare.com/email-service/index.md` | API 參考、限制、價格、最新功能 |
| REST API spec | `https://developers.cloudflare.com/api/resources/email_sending/index.md` | Email Sending REST API 的 OpenAPI spec |
| Workers types | `https://www.npmjs.com/package/@cloudflare/workers-types` | 型別簽章、binding 的形狀 |
| Agents SDK 文件 | [Email agent walkthrough](https://developers.cloudflare.com/agents/examples/email-agent/index.md) | 在 Agents SDK 裡處理 email |

## FIRST: Check Prerequisites

寫任何 email 程式碼之前，先確認基本條件都到位：

1. **網域上架了嗎？** 執行 `npx wrangler email sending list`，看哪些網域已啟用 email sending。如果網域不在清單裡，執行 `npx wrangler email sending enable userdomain.com`，完整設定步驟見 [cli-and-mcp.md](references/cli-and-mcp.md)。
2. **Binding 設好了嗎？** 在 `wrangler.jsonc` 裡找 `send_email`（Workers 用）
3. **有裝 postal-mime 嗎？** 執行 `npm ls postal-mime`（只有接收、解析 email 才需要）

## What Do You Need?

從這裡開始。找到你的情境，再點連結看完整細節。

| 我想要… | 路徑 | Reference |
|--------------|------|-----------|
| **從 Cloudflare Worker 寄 email** | Workers binding（不需要 API key） | [sending.md](references/sending.md) |
| **從用 [Cloudflare Agents SDK](https://developers.cloudflare.com/agents/index.md) 做的 AI agent 寄 email** | Agent class 裡的 `onEmail()` + `replyToEmail()` | [sending.md](references/sending.md) |
| **從外部的 app 或 agent 寄 email**（Node.js、Go、Python 等） | 用 Bearer token 打 REST API | [rest-api.md](references/rest-api.md) |
| **從 coding agent 寄 email**（Claude Code、Cursor、Copilot 等） | MCP 工具、wrangler CLI 或 REST API | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **接收並處理進來的 email**（Email Routing） | Workers 的 `email()` handler | [routing.md](references/routing.md) |
| **設定 Email Sending 或 Email Routing** | `wrangler email sending enable` / `wrangler email routing enable`，或用 Dashboard | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **改善送達率、避免進垃圾信匣** | 驗證、內容、合規 | [deliverability.md](references/deliverability.md) |

## Sending Workflow

Workers 優先用 binding；外部 app 或使用者明確要求時才用 REST。寫程式碼之前，先讀 [sending.md](references/sending.md) 或 [rest-api.md](references/rest-api.md)，檢索所選任務對應的文件。這些指南涵蓋設定、收件人、附件、header、限制、回應處理和錯誤；Workers 那份還涵蓋 Agents SDK 整合，以及配合專案設定的型別。

## Common Mistakes

| 錯誤 | 為什麼會發生 | 修正 |
|---------|---------------|-----|
| wrangler 設定裡忘了 `send_email` binding | Email Service 用的是 binding，不是 API key | 在 wrangler.jsonc 加上 `"send_email": [{ "name": "EMAIL" }]` |
| 從未驗證的網域寄信 | 網域必須先上架到 Email Sending，才能第一次寄信 | 執行 `wrangler email sending enable yourdomain.com`，或在 Dashboard 上架 |
| 在 email handler 裡讀了兩次 `message.raw` | raw stream 只能讀一次，第二次讀會是空的 | 先緩衝：`const raw = await new Response(message.raw).arrayBuffer()` |
| 缺 `text` 欄位（只有 HTML） | 有些 email 用戶端只顯示純文字，而且也有助於垃圾信評分 | 一律同時附上 `html` 和 `text` 版本 |
| 拿 email 做行銷或大量寄送 | Email Service 只給交易型 email 用 | 電子報和行銷活動請用專門的行銷 email 平台 |
| 轉寄到未驗證的目的地 | `message.forward()` 只能用在已驗證的地址 | 執行 `wrangler email routing addresses create user@gmail.com`，或在 Dashboard 新增 |
| 用假地址測試 | 寄到不存在的地址會退信，傷害寄件者信譽 | 開發時用你自己掌控的真實地址 |
| 把 API token 寫死在原始碼裡 | 程式碼裡的 token 會被 commit 出去、洩漏 | 用環境變數或 Cloudflare secrets |
| 忽略 `from` 網域的要求 | `from` 地址必須使用已上架到 Email Service 的網域 | 先驗證網域，再從 `anything@that-domain.com` 寄 |
| 在 REST API 的 `from` 物件裡用 `email` key | REST API 的 `from` 物件用的是 `address`，不是 `email` | REST 用 `{ "address": "...", "name": "..." }`，Workers 用 `{ "email": "...", "name": "..." }` |
| 在 REST API 用 `replyTo` | REST API 的欄位名稱是 snake_case | REST API 用 `reply_to`，Workers binding 用 `replyTo` |

## References

讀跟你情境相符的那份就好，不需要全部讀。

- **[references/sending.md](references/sending.md)**：Workers binding、附件和 Agents SDK email 的文件地圖。
- **[references/rest-api.md](references/rest-api.md)**：HTTP 寄送、request schema、回應和錯誤的文件地圖。
- **[references/routing.md](references/routing.md)**：進來的 `email()` handler、轉送、回覆、解析。接收 email 用。
- **[references/cli-and-mcp.md](references/cli-and-mcp.md)**：網域設定、wrangler 指令、MCP 工具。第一次設定用。
- **[references/deliverability.md](references/deliverability.md)**：SPF/DKIM/DMARC、退信、suppression、最佳實務。

## Skill feedback

如果使用者反映這個 skill 給了錯誤或過時的指引，或是缺了資訊，就去讀 [references/skill-feedback.md](references/skill-feedback.md)。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: cloudflare-email-service
description: Implement or troubleshoot Cloudflare Email Sending and Email Routing integrations and their delivery configuration.
---

# Cloudflare Email Service

Your knowledge of the Cloudflare Email Service, Email Routing or Email Sending may be outdated. **Prefer retrieval over pre-training** for any Cloudflare Email Service task.

Cloudflare Email Service lets you send transactional emails and route incoming emails, all within the Cloudflare platform. Your knowledge of this product may be outdated — it launched in 2025 and is evolving rapidly. **Prefer retrieval over pre-training** for any Email Service task.

**If there is any discrepancy between this skill and the sources below, always trust the original source.** The Cloudflare docs, REST API spec, `@cloudflare/workers-types`, and Agents SDK repo are the source of truth. This skill is a convenience guide — it may lag behind the latest changes. When in doubt, retrieve from the sources below and use what they say.

## Retrieval Sources

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| Cloudflare docs | Cloudflare MCP `docs` tool or URL `https://developers.cloudflare.com/email-service/index.md` | API reference, limits, pricing, latest features |
| REST API spec | `https://developers.cloudflare.com/api/resources/email_sending/index.md` | OpenAPI spec for the Email Sending REST API |
| Workers types | `https://www.npmjs.com/package/@cloudflare/workers-types` | Type signatures, binding shapes |
| Agents SDK docs | [Email agent walkthrough](https://developers.cloudflare.com/agents/examples/email-agent/index.md) | Email handling in Agents SDK |

## FIRST: Check Prerequisites

Before writing any email code, verify the basics are in place:

1. **Domain onboarded?** Run `npx wrangler email sending list` to see which domains have email sending enabled. If the domain isn't listed, run `npx wrangler email sending enable userdomain.com` or see [cli-and-mcp.md](references/cli-and-mcp.md) for full setup instructions.
2. **Binding configured?** Look for `send_email` in `wrangler.jsonc` (for Workers)
3. **postal-mime installed?** Run `npm ls postal-mime` (only needed for receiving/parsing emails)

## What Do You Need?

Start here. Find your situation, then follow the link for full details.

| I want to... | Path | Reference |
|--------------|------|-----------|
| **Send emails from a Cloudflare Worker** | Workers binding (no API keys needed) | [sending.md](references/sending.md) |
| **Send emails from an AI agent built with [Cloudflare Agents SDK](https://developers.cloudflare.com/agents/index.md)** | `onEmail()` + `replyToEmail()` in Agent class | [sending.md](references/sending.md) |
| **Send emails from an external app or agent** (Node.js, Go, Python, etc.) | REST API with Bearer token | [rest-api.md](references/rest-api.md) |
| **Send emails from a coding agent** (Claude Code, Cursor, Copilot, etc.) | MCP tools, wrangler CLI, or REST API | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **Receive and process incoming emails** (Email Routing) | Workers `email()` handler | [routing.md](references/routing.md) |
| **Set up Email Sending or Email Routing** | `wrangler email sending enable` / `wrangler email routing enable`, or Dashboard | [cli-and-mcp.md](references/cli-and-mcp.md) |
| **Improve deliverability, avoid spam folders** | Authentication, content, compliance | [deliverability.md](references/deliverability.md) |

## Sending Workflow

Prefer the binding for Workers; use REST for external apps or when explicitly requested. Read [sending.md](references/sending.md) or [rest-api.md](references/rest-api.md) to retrieve the documentation for the selected task before writing code. These guides cover setup, recipients, attachments, headers, limits, response handling, and errors; the Workers guide also covers Agents SDK integration and types matched to the project configuration.

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Forgetting `send_email` binding in wrangler config | Email Service uses a binding, not an API key | Add `"send_email": [{ "name": "EMAIL" }]` to wrangler.jsonc |
| Sending from an unverified domain | Domain must be onboarded onto Email Sending before first send | Run `wrangler email sending enable yourdomain.com` or onboard in Dashboard |
| Reading `message.raw` twice in email handler | The raw stream is single-use — second read returns empty | Buffer first: `const raw = await new Response(message.raw).arrayBuffer()` |
| Missing `text` field (HTML only) | Some email clients only show plain text; also helps spam scores | Always include both `html` and `text` versions |
| Using email for marketing/bulk sends | Email Service is for transactional email only | Use a dedicated marketing email platform for newsletters and campaigns |
| Forwarding to unverified destinations | `message.forward()` only works with verified addresses | Run `wrangler email routing addresses create user@gmail.com` or add in Dashboard |
| Testing with fake addresses | Bounces from non-existent addresses hurt sender reputation | Use real addresses you control during development |
| Hardcoding API tokens in source code | Tokens in code get committed and leaked | Use environment variables or Cloudflare secrets |
| Ignoring the `from` domain requirement | The `from` address must use a domain onboarded to Email Service | Verify the domain first, then send from `anything@that-domain.com` |
| Using `email` key in REST API `from` object | REST API uses `address` not `email` for `from` object | Use `{ "address": "...", "name": "..." }` for REST, `{ "email": "...", "name": "..." }` for Workers |
| Using `replyTo` in REST API | REST API uses snake_case field names | Use `reply_to` for REST API, `replyTo` for Workers binding |

## References

Read the reference that matches your situation. You don't need all of them.

- **[references/sending.md](references/sending.md)** — Documentation map for Workers binding, attachments, and Agents SDK email.
- **[references/rest-api.md](references/rest-api.md)** — Documentation map for HTTP sending, request schemas, responses, and errors.
- **[references/routing.md](references/routing.md)** — Inbound `email()` handler, forwarding, replying, parsing. For receiving emails.
- **[references/cli-and-mcp.md](references/cli-and-mcp.md)** — Domain setup, wrangler commands, MCP tools. For first-time setup.
- **[references/deliverability.md](references/deliverability.md)** — SPF/DKIM/DMARC, bounces, suppressions, best practices.

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
~~~~~
{% endraw %}

</section>
</div>
