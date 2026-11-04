---
name: sequence-load
description: "找出符合條件的 lead，並批次加入 Apollo 的開發信 sequence。在一個流程裡處理 enrichment、建立聯絡人、去重和加入 sequence。"
user-invocable: true
argument-hint: "[targeting criteria + sequence name]"
---

# Sequence Load

端到端地找出、enrich 並載入聯絡人到開發信 sequence。使用者透過 "$ARGUMENTS" 提供目標條件和 sequence 名稱。

## 範例

- `/apollo:sequence-load add 20 VP Sales at SaaS companies to my "Q1 Outbound" sequence`
- `/apollo:sequence-load SDR managers at fintech startups → Cold Outreach v2`
- `/apollo:sequence-load list sequences`（顯示所有可用的 sequence）
- `/apollo:sequence-load directors of engineering, 500+ employees, US → Demo Follow-up`
- `/apollo:sequence-load reload 15 more leads into "Enterprise Pipeline"`

## Step 1 — 解析輸入

從 "$ARGUMENTS" 擷取：

**目標條件：**
- 職稱 → `person_titles`
- 資深程度 → `person_seniorities`
- 產業關鍵字 → `q_organization_keyword_tags`
- 公司規模 → `organization_num_employees_ranges`
- 地點 → `person_locations` 或 `organization_locations`

**Sequence 資訊：**
- Sequence 名稱（"to"、"into" 或 "→" 之後的文字）
- 數量：要加入多少聯絡人（沒指定時預設 10）

如果使用者只說「list sequences」，跳到 Step 2 並顯示所有可用的 sequence。

## Step 2 — 找到 Sequence

用 `mcp__claude_ai_Apollo_MCP__apollo_emailer_campaigns_search` 找到目標 sequence：
- 把 `q_name` 設為輸入中的 sequence 名稱

如果沒有符合或有多個符合：
- 用表格顯示所有可用的 sequence：| Name | ID | Status |
- 請使用者挑一個

## Step 3 — 取得 Email 帳號

用 `mcp__claude_ai_Apollo_MCP__apollo_email_accounts_index` 列出已連結的 email 帳號。

- 如果只有一個帳號 → 自動使用
- 如果有多個 → 顯示出來並問要用哪個寄信

## Step 4 — 找出符合的人

用 `mcp__claude_ai_Apollo_MCP__apollo_mixed_people_api_search` 搭配目標條件。
- 把 `per_page` 設為要求的數量（預設 10）

用預覽表格呈現候選人：

| # | Name | Title | Company | Location |
|---|---|---|---|---|

詢問：**「要把這 [N] 位聯絡人加入 [Sequence Name] 嗎？這會消耗 [N] 個 Apollo credit 做 enrichment。」**

等確認之後才繼續。

## Step 5 — Enrich 並建立聯絡人

對每一位核准的 lead：

1. **Enrich**：用 `mcp__claude_ai_Apollo_MCP__apollo_people_bulk_match`（每次呼叫最多批次 10 筆），帶入：
   - 每個人的 `first_name`、`last_name`、`domain`
   - `reveal_personal_emails` 設為 `true`

2. **建立聯絡人**：對每位 enrich 完成的人，用 `mcp__claude_ai_Apollo_MCP__apollo_contacts_create`，帶入：
   - `first_name`、`last_name`、`email`、`title`、`organization_name`
   - 如果有的話，`direct_phone` 或 `mobile_phone`
   - `run_dedupe` 設為 `true`

收集所有已建立的聯絡人 ID。

## Step 6 — 加入 Sequence

用 `mcp__claude_ai_Apollo_MCP__apollo_emailer_campaigns_add_contact_ids`，帶入：
- `id`：sequence ID
- `emailer_campaign_id`：同一個 sequence ID
- `contact_ids`：已建立的聯絡人 ID 陣列
- `send_email_from_email_account_id`：選定的 email 帳號 ID
- `sequence_active_in_other_campaigns`：`false`（安全的預設值）

## Step 7 — 確認加入結果

顯示摘要：

---

**Sequence 載入成功**

| 欄位 | 值 |
|---|---|
| Sequence | [Name] |
| 加入的聯絡人 | [count] |
| 寄件帳號 | [email address] |
| 使用的 credit | [count] |

**已加入的聯絡人：**

| Name | Title | Company | Email |
|---|---|---|---|

---

## Step 8 — 提供後續動作

詢問使用者：

1. **再載入更多**：找出並加入另一批 lead
2. **檢視 sequence**：顯示 sequence 詳情和所有已加入的聯絡人
3. **移除聯絡人**：用 `mcp__claude_ai_Apollo_MCP__apollo_emailer_campaigns_remove_or_stop_contact_ids` 移除特定聯絡人
4. **暫停聯絡人**：用 `status: "paused"` 和一個 `auto_unpause_at` 日期重新加入
