---
name: enrich-lead
description: "即時 lead enrichment。丟進一個姓名、公司、LinkedIn URL 或 email，就能拿到完整的聯絡人資料卡，包含 email、電話、職稱、公司情報和下一步行動。"
user-invocable: true
argument-hint: "[name, company, LinkedIn URL, or email]"
---

# Enrich Lead

把任何識別資訊變成完整的聯絡人檔案。使用者透過 "$ARGUMENTS" 提供識別資訊。

## 範例

- `/apollo:enrich-lead Tim Zheng at Apollo`
- `/apollo:enrich-lead https://www.linkedin.com/in/timzheng`
- `/apollo:enrich-lead sarah@stripe.com`
- `/apollo:enrich-lead Jane Smith, VP Engineering, Notion`
- `/apollo:enrich-lead CEO of Figma`

## 步驟 1：解析輸入

從 "$ARGUMENTS" 擷取所有能拿到的識別資訊：
- 名、姓
- 公司名稱或網域
- LinkedIn URL
- Email 地址
- 職稱（當作比對的提示）

如果輸入有歧義（例如只有「CEO of Figma」），先用 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search`，搭配相關的職稱和網域篩選來找出這個人，再進行 enrichment。

## 步驟 2：Enrich 這個人

> **Credit 警告**：呼叫之前，先告訴使用者 enrichment 會消耗 1 個 Apollo credit。

用 `mcp__claude_ai_Apollo_MCP__apollo_people_match`，帶上所有能拿到的識別資訊：
- 知道姓名就帶 `first_name`、`last_name`
- 知道公司就帶 `domain` 或 `organization_name`
- 有提供 LinkedIn 就帶 `linkedin_url`
- 有提供 email 就帶 `email`
- 把 `reveal_personal_emails` 設為 `true`

如果比對失敗，就用較寬鬆的篩選條件試 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search`，並列出前 3 位候選人。請使用者挑一位，然後重新 enrich。

## 步驟 3：Enrich 他們的公司

用 `mcp__claude_ai_Apollo_MCP__apollo_organizations_enrich`，帶上這個人的公司網域，拉出公司輪廓（firmographic）背景資料。

## 步驟 4：呈現聯絡人資料卡

輸出格式要完全照下面這樣：

---

**[Full Name]** | [Title]
[Company Name] · [Industry] · [Employee Count] employees

| Field | Detail |
|---|---|
| Email (work) | ... |
| Email (personal) | ... (if revealed) |
| Phone (direct) | ... |
| Phone (mobile) | ... |
| Phone (corporate) | ... |
| Location | City, State, Country |
| LinkedIn | URL |
| Company Domain | ... |
| Company Revenue | Range |
| Company Funding | Total raised |
| Company HQ | Location |

---

## 步驟 5：提供下一步行動

問使用者要採取哪個行動：

1. **Save to Apollo**：透過 `mcp__claude_ai_Apollo_MCP__apollo_contacts_create` 並帶 `run_dedupe: true`，把這個人建立成聯絡人
2. **Add to a sequence**：問要加到哪個 sequence，然後執行載入 sequence 的流程
3. **Find colleagues**：用 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search`，把 `q_organization_domains_list` 設成這家公司，搜尋同公司的更多人
4. **Find similar people**：搜尋其他公司裡有相同職稱／資歷的人
