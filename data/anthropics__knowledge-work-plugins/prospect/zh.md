---
name: prospect
description: "從 ICP 到名單的完整 pipeline。用白話描述你的理想客戶，就能得到一份排好名次、附 email 和電話的決策者名單表。"
user-invocable: true
argument-hint: "[describe your ideal customer]"
---

# Prospect

一次從 ICP 描述走到排好名次、已補強資料的名單。使用者透過 "$ARGUMENTS" 描述他們的理想客戶。

## 範例

- `/apollo:prospect VP of Engineering at Series B+ SaaS companies in the US, 200-1000 employees`
- `/apollo:prospect heads of marketing at e-commerce companies in Europe`
- `/apollo:prospect CTOs at fintech startups, 50-500 employees, New York`
- `/apollo:prospect procurement managers at manufacturing companies with 1000+ employees`
- `/apollo:prospect SDR leaders at companies using Salesforce and Outreach`

## 步驟 1：解析 ICP

從 "$ARGUMENTS" 的自然語言描述中擷取結構化的篩選條件：

**公司篩選條件：**
- 產業／垂直領域關鍵字 → `q_organization_keyword_tags`
- 員工人數範圍 → `organization_num_employees_ranges`
- 公司所在地 → `organization_locations`
- 特定網域 → `q_organization_domains_list`

**人員篩選條件：**
- 職稱 → `person_titles`
- 資歷層級 → `person_seniorities`
- 人員所在地 → `person_locations`

如果 ICP 很模糊，往下之前先問 1 到 2 個釐清問題。至少需要職稱／角色，以及產業或公司規模。

## 步驟 2：搜尋公司

用公司篩選條件呼叫 `mcp__claude_ai_Apollo_MCP__apollo_mixed_companies_search`：
- 產業／垂直領域用 `q_organization_keyword_tags`
- 規模用 `organization_num_employees_ranges`
- 地理位置用 `organization_locations`
- 把 `per_page` 設為 25

## 步驟 3：補強排名前面的公司資料

用前 10 筆結果的網域呼叫 `mcp__claude_ai_Apollo_MCP__apollo_organizations_bulk_enrich`。這會揭露營收、融資、人數和公司基本面資料，協助替公司排名。

## 步驟 4：找出決策者

用下列參數呼叫 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search`：
- 來自 ICP 的 `person_titles` 和 `person_seniorities`
- 限定在已補強資料的公司網域範圍內的 `q_organization_domains_list`
- `per_page` 設為 25

## 步驟 5：補強排名前面的名單資料

> **點數警告**：往下之前，要明確告訴使用者會消耗多少點數（credits）。

用 `mcp__claude_ai_Apollo_MCP__apollo_people_bulk_match` 每次呼叫最多補強 10 筆名單，參數是：
- 每個人的 `first_name`、`last_name`、`domain`
- `reveal_personal_emails` 設為 `true`

如果超過 10 筆名單，就分成多次呼叫。

## 步驟 6：呈現名單表

以排好名次的表格顯示結果：

### Leads matching: [ICP Summary]

| # | Name | Title | Company | Employees | Revenue | Email | Phone | ICP Fit |
|---|---|---|---|---|---|---|---|---|

**ICP Fit** 評分：
- **Strong**：職稱、資歷、公司規模和產業全部符合
- **Good**：4 項條件符合 3 項
- **Partial**：4 項條件符合 2 項

**摘要**：在 Y 家公司中找到 X 筆名單。消耗了 Z 點。

## 步驟 7：提議後續動作

問使用者：

1. **全部存進 Apollo**：對每筆名單用 `mcp__claude_ai_Apollo_MCP__apollo_contacts_create` 並帶 `run_dedupe: true`，批次建立聯絡人
2. **載入序列**：問要哪個序列，並對這些聯絡人執行載入序列的流程
3. **深入研究某家公司**：對名單中任何一家公司執行 `/apollo:company-intel`
4. **調整搜尋**：調整篩選條件後重新執行
5. **匯出**：把名單格式化成 CSV 風格的表格，方便複製貼上
