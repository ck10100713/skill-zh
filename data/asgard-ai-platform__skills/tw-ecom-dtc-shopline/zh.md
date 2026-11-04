---
name: "tw-ecom-dtc-shopline"
description: "透過 mcp-shopline，在台灣電商情境下串接並營運 Shopline。當使用者需要在 Shopline 商店同步訂單、管理商品、執行促銷或核對庫存；比較 Shopline 與 91APP/Shopify 用於台灣 DTC；或除錯非同步寫入的傳播問題時使用。查 API schema（請去看 mcp-shopline 文件）或非台灣的 Shopline 部署「不要」用這個。"
metadata:
  category: "WP-01 電商"
  domain: "ecommerce-tw"
  layer: "platform"
  related_mcps: ["mcp-shopline"]
  related_skills: ["tw-ecom-channel-strategy", "tw-ecom-invoice-ezpay", "tw-ecom-payment-newebpay", "ecom-rfm-analysis", "ecom-promo-roi", "ecom-inventory-health"]
  last_verified: "2026-04"
  tags: ["taiwan", "e-commerce", "shopline", "platform", "integration"]
---

# Shopline 串接方法論

## 何時使用這個 skill

- 在 Shopline 和內部 ERP / 資料倉儲之間同步訂單、商品、會員或庫存
- 跨 `mcp-shopline` 的多個 tool 建立多步驟自動化（例如：訂單 → 發票 → 物流）
- 把 Shopline 的狀態和外部系統（會計、WMS、電子發票平台）做核對
- 設計橫跨讀取 + 寫入 tool 的促銷 / 優惠券 / 限時特賣工作流程
- 除錯非預期行為：訂單遺失、寫入後讀到過期資料、查詢通路時 403

## 何時「不要」使用

- 你需要單一 endpoint 的精確 API schema，請直接讀 tool 描述或 Shopline Open API 文件
- 商家用的是 Shopify、91APP、Cyberbiz 或其他非 Shopline 平台，請先用 `tw-ecom-channel-strategy`
- Shopline 商店不在台灣（HK/SG/MY），這個 skill 裡的幣別、發票和物流假設都是 TWD + 台灣專屬

## 核心概念

Shopline 是在台灣 DTC 和全通路品牌之間很受歡迎的 SaaS 電商平台。一個 **merchant** 帳號可以擁有多個 **shop**（店面）；每個 shop 可以透過多個 **channel**（線上 + POS 實體門市）銷售。`mcp-shopline` 把 Shopline Open API v1 包成 143 個 tool（75 個讀取、68 個寫入），全部限定在一個 API token = 一個 merchant 情境內。

挑 tool 時要看兩個軸：

- **讀取 vs 寫入。** 寫入 tool 在描述裡會加上 `[WRITE]` 前綴，且需要允許變更的 API token scope。讀取 tool 很安全；寫入 tool 會修改 production 資料。
- **領域。** 訂單、商品與庫存、分析、顧客、分類與促銷、訂單延伸（退貨/配送/對話/評價）、店鋪設定。分析 tool 是預先彙總好的，優先用它們，不要在 `query_orders` 上自己手刻彙總。

金額一律是 TWD 浮點數。日期是 `YYYY-MM-DD` 字串。線上訂單的狀態是 `confirmed`；POS 訂單是 `completed`，兩個搞混會無聲地丟掉一半資料。

## 決策樹

```
What is the user asking for?
│
├─ Aggregate metric (revenue, AOV, top products, trend)?
│    → Analytics / Orders summary tools
│      get_sales_summary · get_top_products · get_sales_trend
│      get_channel_comparison · get_rfm_analysis · get_promotion_roi
│
├─ Specific order / customer / product lookup?
│    → Read-detail tools
│      get_order_detail · get_customer_profile · get_product_variants
│
├─ Inventory question (stock, low-stock, warehouse)?
│    → Products & Inventory read tools
│      get_inventory_overview · get_low_stock_alerts ·
│      get_stock_by_warehouse · get_locked_inventory
│
├─ Promotion / coupon / flash sale?
│    ├─ Read  → list_promotions · get_promotion_detail ·
│    │          list_flash_price_campaigns · list_affiliate_campaigns
│    └─ Write → promotion write tools (12) — split into three sub-families:
│              flat promo · flash price · gift/add-on. See
│              references/tool-catalog.md for exact tool per family.
│
├─ Modify an order (status, tag, fulfill, cancel)?
│    → Order write tools (8) — require write scope
│
├─ Create/update customer, adjust store credits, group membership?
│    → Customer write tools (6)
│
└─ Configuration / debug (token scope, channels, payments, delivery)?
     → Store Settings read tools
       get_token_info (always start here when debugging permissions)
       list_channels · list_payments · list_delivery_options
```

## 實作指引

常見的多 tool 流程。每個流程都用下面的 tool 名稱；端到端的完整範例見 `examples/sample_scenario.md`。

**訂單同步（Shopline → 內部 ERP）**

- 用 `query_orders` 以日期區間輪詢；要「同時」包含 `confirmed`（線上）和 `completed`（POS）兩種狀態
- 每筆訂單都呼叫 `get_order_detail` 取得品項，呼叫 `get_order_transactions` 取得付款紀錄
- 如果配送資訊重要，呼叫 `get_order_delivery`，注意：配送有自己的 ID，要出貨執行後才拿得到
- 要保存 `order.channel.created_by_channel_name` 的值，不能只存 `created_from`，否則會失去實體門市的身份
- 用檢查點記錄已處理到的最新日期，避免重複抓取；每次執行再重掃最近 24-48 小時，以抓到延遲的狀態變更

**促銷設定與衡量**

- 事前檢查：用 `list_promotions` + `search_promotions` 避免活動名稱重複
- 依類型選對應的促銷寫入 tool 來建立（一般促銷 vs 限時特價 vs 滿額贈 vs 加價購）
- 上線後，用 `get_promotion_analysis`（成效）+ `get_promotion_roi`（相對基準的提升）來衡量
- 聯盟行銷活動用 `get_affiliate_campaign_usage`，這個至少要有一筆使用該活動的訂單才能用

**會員 / RFM 同步**

- 完整會員同步：`list_customers`（分頁）→ 需要時再對每位呼叫 `get_customer_profile`（不要大量呼叫，成本很高）
- 分群：用 `get_rfm_analysis`，不要從原始訂單自己算，它是預先彙總好的，而且符合 Shopline 對會員的定義
- 等級 / 點數狀態：`list_membership_tiers`、`list_member_point_rules`、`list_store_credits`
- `get_customer_lifecycle` 會比較兩個期間的 RFM，找出升級和流失

**庫存同步與補貨**

- 快照：`get_inventory_overview`（總計）+ `get_stock_by_warehouse`（各倉庫矩陣）
- 營運訊號：`get_low_stock_alerts`、`get_locked_inventory`（被待處理訂單預留的）、`get_slow_movers`（過剩庫存）
- 調撥規劃：`get_stock_transfer_suggestions`，這是伺服器端的啟發式演算法，輸出當建議，不要當命令
- 補貨：`list_purchase_orders` → `get_purchase_order_detail`；用採購單寫入 tool 來建立

## 常見陷阱

- **訂單狀態依通路而分：`confirmed` vs `completed`。** 線上訂單用 `confirmed`；POS 用 `completed`。tool 預設兩者都包含，但如果你傳了自訂的 `status` 篩選卻漏掉一個，就會無聲地丟掉一半資料。一定要用 `get_channel_comparison` 確認線上和 POS 的筆數看起來合理。
- **分頁上限。** `per_page` 最大 50，而且搜尋結果總共最多 10,000 筆。大範圍要把日期區間切開（Shopline Open API 內部用 `fetch_all_pages_by_date_segments`，但你自己的多步驟流程也需要同樣的紀律）。對高流量商家查 30 天的熱銷品，會撞到上限。
- **非同步寫入的傳播：寫入後立刻讀可能是過期的。** 呼叫 `[WRITE]` tool（例如 `update_order_status`、`adjust_store_credit`）之後，立刻讀取可能還是回傳寫入前的狀態。不要在同一個同步步驟裡，用寫入後讀取的結果當下游邏輯的判斷依據。要建立核對迴圈，或把寫入回應本身的 `updated_at` 往下傳。（TODO: 向 Shopline Open API 支援或 mcp-shopline 維護者確認確切的傳播時間窗。）
- **目前還不支援 webhook（截至 2026-04）。** `mcp-shopline` 的 roadmap 把 webhook 列為待辦。在那之前，所有事件偵測都靠輪詢。要據此預算 API 呼叫次數，並選一個輪詢頻率（訂單 5-15 分鐘、庫存每小時），同時遵守 tool 強制的頁與頁之間 0.2 秒延遲。
- **通路 endpoint 常常 403/422，改從訂單 payload 取得。** `list_channels` / `get_channel_detail` 需要另外的權限，多數 token 都沒有。同樣的資訊（店名、通路類型）可以從任何訂單明細的 `order.channel.created_by_channel_name` 取得，通路 tool 失敗時，就把它當作權威來源。
- **寫入 tool 需要明確的 scope，而且測試裡要 `SHOPLINE_TEST_WRITES=1`。** token 預設是唯讀 scope；production 寫入失敗通常代表沒被授予 scope，不是 tool 壞掉。除錯時先用 `get_token_info` 確認 scope，再去懷疑是 bug。在測試環境裡，寫入被這個環境變數卡住，CI 裡除非有專用的測試商店，否則不要設它。

## IRON LAW

**絕對不要只靠 `status` 或 `created_from` 來篩選訂單。** 線上訂單用 `confirmed`、POS 用 `completed`，而店鋪身份存在 `order.channel.created_by_channel_name`，不是 `created_from`（`"shop"` / `"pos"`）。任何寫死單一狀態、或用 `created_from` 當依據的訂單查詢，都會無聲地丟掉 POS 營收、把門市銷售歸錯店，或兩者皆是。一定要同時傳入兩種狀態（或省略篩選），而且下游紀錄裡一定要帶著通路名稱。

### 合理化藉口對照表

| "但是…" | 為什麼錯 |
|---|---|
| 我只需要線上訂單，`status=confirmed` 就夠了 | POS 訂單用 `completed`，hard-code `confirmed` 會靜默丟失所有實體門市營收 |
| `created_from` 欄位明確標示 `"shop"` vs `"pos"`，用它來分類就好 | `created_from` 不是通路身份的權威來源；門市名稱只在 `order.channel.created_by_channel_name` 中，跨店分析時用 `created_from` 會錯誤合併所有實體店 |
| 只拿 `confirmed` 是效能最佳化，不是資料遺失 | 範圍縮小不等於最佳化；用日期區間分頁才是正確的效能手段，不是靠省略 POS 訂單 |
| 這個報表只給線上部門，POS 不在範圍內 | 商業邏輯範圍不等於查詢範圍；即使報表只看線上，下游 ERP 或發票系統仍可能吃到這份 query 結果 |

## 輸出格式

完成 Shopline 任務時，產出這個結構：

```markdown
# Shopline Task: {one-line summary}

## Context
- Merchant / shop: {name} (single-merchant token assumed)
- Scope of work: {read-only analysis | sync | write mutation | full integration}
- Date window / entity scope: {…}

## Tool Plan
| Step | Tool | Read/Write | Purpose |
|------|------|-----------|---------|
| 1 | get_token_info | R | Confirm scope covers the tools below |
| 2 | {tool} | R/W | {…} |
| … | … | … | … |

## Assumptions & Open Questions
- {assumption grounded in a Shopline constraint}
- TODO: {anything that needs verification against mcp-shopline or Open API docs}

## Execution Notes
- Both `confirmed` and `completed` statuses included: Y/N
- Channel name carried forward from `order.channel.created_by_channel_name`: Y/N
- Pagination strategy (date segmentation if >10k results): {…}
- Read-after-write handling (reconciliation loop, not immediate re-read): {…}

## Deliverable
{the actual answer, dataset, or change summary}
```

## 相關

- **MCP**：`mcp-shopline`
- **Skill**：`tw-ecom-channel-strategy`（Shopline vs 91APP/Shopify 的決策）、`tw-ecom-invoice-ezpay`（電子發票交接）、`tw-ecom-payment-newebpay`（金流對帳）、`ecom-rfm-analysis`（分群方法論）、`ecom-promo-roi`（提升衡量）、`ecom-inventory-health`（庫存 KPI）
- **參考資料**：`references/tool-catalog.md`（每個 tool 一行，依領域分組）、`examples/sample_scenario.md`（端到端的訂單 → 發票流程）

_Last verified: 2026-04_
