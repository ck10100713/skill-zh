---
name: documentation-lookup
description: 透過 Context7 MCP 取得最新的函式庫與框架文件，不要靠訓練資料。遇到設定問題、API 參考、程式碼範例，或使用者提到框架名稱（例如 React、Next.js、Prisma）時啟用。
metadata:
  origin: ECC
---

# 查文件（Context7）

當使用者問到函式庫、框架或 API 時，透過 Context7 MCP（工具 `resolve-library-id` 和 `query-docs`）取得最新文件，不要靠訓練資料。

## 核心概念

- **Context7**：提供即時文件的 MCP server；函式庫和 API 的問題用它，不用訓練資料。
- **resolve-library-id**：依函式庫名稱和問題，回傳 Context7 相容的函式庫 ID（例如 `/vercel/next.js`）。
- **query-docs**：針對指定的函式庫 ID 和問題取得文件與程式碼片段。一定要先呼叫 resolve-library-id 拿到有效的函式庫 ID。

## 何時使用

使用者出現下列情況就啟用：

- 問設定或組態問題（例如「Next.js middleware 要怎麼設定？」）
- 要求依賴某個函式庫的程式碼（「幫我寫一個 Prisma query 來...」）
- 需要 API 或參考資訊（「Supabase 有哪些 auth 方法？」）
- 提到特定框架或函式庫（React、Vue、Svelte、Express、Tailwind、Prisma、Supabase 等）

只要需求取決於函式庫、框架或 API 準確且最新的行為，就用這個 skill。適用於所有設定了 Context7 MCP 的 harness（例如 Claude Code、Cursor、Codex）。

## 運作方式

### 步驟 1：解析函式庫 ID

呼叫 **resolve-library-id** MCP 工具，帶入：

- **libraryName**：從使用者問題中取出的函式庫或產品名稱（例如 `Next.js`、`Prisma`、`Supabase`）。
- **query**：使用者的完整問題。這樣可以提高結果排序的相關性。

查文件之前，一定要先取得 Context7 相容的函式庫 ID（格式 `/org/project` 或 `/org/project/version`）。沒有從這一步拿到有效的函式庫 ID，就不准呼叫 query-docs。

### 步驟 2：挑出最符合的結果

從解析結果中，用下列標準挑一個：

- **名稱符合度**：優先選跟使用者問的完全一致或最接近的。
- **Benchmark 分數**：分數越高代表文件品質越好（100 最高）。
- **來源信譽**：有的話優先選 High 或 Medium 信譽。
- **版本**：如果使用者指定了版本（例如「React 19」、「Next.js 15」），有列出對應版本的函式庫 ID 就優先選它（例如 `/org/project/v1.2.0`）。

### 步驟 3：取得文件

呼叫 **query-docs** MCP 工具，帶入：

- **libraryId**：步驟 2 選出的 Context7 函式庫 ID（例如 `/vercel/next.js`）。
- **query**：使用者具體的問題或任務。問得具體才拿得到相關的片段。

上限：每個問題呼叫 query-docs（或 resolve-library-id）不要超過 3 次。如果 3 次之後答案還是不清楚，就講明不確定，用手上最好的資訊回答，不要猜。

### 步驟 4：使用文件

- 用取得的最新資訊回答使用者的問題。
- 有幫助的話，附上文件中相關的程式碼範例。
- 在重要時註明函式庫或版本（例如「在 Next.js 15 中...」）。

## 範例

### 範例：Next.js middleware

1. 用 `libraryName: "Next.js"`、`query: "How do I set up Next.js middleware?"` 呼叫 **resolve-library-id**。
2. 從結果中依名稱和 benchmark 分數挑出最符合的（例如 `/vercel/next.js`）。
3. 用 `libraryId: "/vercel/next.js"`、`query: "How do I set up Next.js middleware?"` 呼叫 **query-docs**。
4. 用回傳的片段和文字回答；相關的話，附上文件中最精簡的 `middleware.ts` 範例。

### 範例：Prisma query

1. 用 `libraryName: "Prisma"`、`query: "How do I query with relations?"` 呼叫 **resolve-library-id**。
2. 選官方的 Prisma 函式庫 ID（例如 `/prisma/prisma`）。
3. 用該 `libraryId` 和問題呼叫 **query-docs**。
4. 回傳 Prisma Client 的寫法（例如 `include` 或 `select`），附上文件中的簡短程式碼片段。

### 範例：Supabase auth 方法

1. 用 `libraryName: "Supabase"`、`query: "What are the auth methods?"` 呼叫 **resolve-library-id**。
2. 挑 Supabase 文件的函式庫 ID。
3. 呼叫 **query-docs**；整理 auth 方法，並附上取得文件中最精簡的範例。

## 最佳實務

- **問得具體**：盡量用使用者的完整問題當 query，相關性比較好。
- **注意版本**：使用者提到版本時，有的話就用解析步驟拿到的對應版本函式庫 ID。
- **優先官方來源**：有多個符合的結果時，優先選官方或主要套件，不選社群 fork。
- **不要帶敏感資料**：送給 Context7 的任何 query 都要先把 API key、密碼、token 和其他 secret 遮掉。在把使用者的問題傳給 resolve-library-id 或 query-docs 之前，要先假設它可能含有 secret。
