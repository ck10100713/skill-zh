---
name: hermes-tweet
description: >
  安裝並操作 Hermes Tweet，這是 Hermes Agent 的 plugin，用於 X/Twitter 研究、時間軸讀取、推文分析，以及需要核准關卡的私人或會改變狀態的操作。適用於安裝 Hermes Tweet、研究 X/Twitter 帳號、監控發表訊號、調查提及、稽核抽獎活動，或準備需要關卡的 X 操作的時候。當 Hermes Agent 的工作流程需要最新的 X/Twitter 脈絡時，要主動使用。讀取與操作的 tool 都需要 XQUIK_API_KEY。
license: MIT
metadata:
  version: "0.1.13"
  source: https://github.com/Xquik-dev/hermes-tweet
  homepage: https://github.com/Xquik-dev/hermes-tweet#readme
---

# Hermes Tweet

Hermes Tweet 為 Hermes Agent 加上一組 X/Twitter 工具集。適用於社群聆聽、帳號研究、發表監控、客服分流、抽獎稽核，以及讓私人或會改變狀態的操作保持明確的受控工作流程。

## 什麼時候用這個 Skill

當使用者想要做下面這些事的時候用這個 skill：

- 把 Hermes Tweet 安裝到 Hermes Agent runtime
- 找出可用的 X/Twitter 讀取與操作路由
- 讀取 X/Twitter 的帳號、推文、趨勢、monitor 或搜尋資料
- 在草擬回應或活動之前，彙整公開訊號
- 讓私人和會改變狀態的操作，必須在操作者明確意圖之後才能執行

## 設定

透過 Hermes 安裝並啟用 plugin：

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

Hermes 在安裝和更新時會掃描 plugin。每個警告都要檢視。有 dangerous 判定時，會擋下安裝或停用更新。

在 Hermes runtime 主機上設定 API key：

```bash
export XQUIK_API_KEY="<your-key>"
export HERMES_TWEET_ENABLE_ACTIONS="false"
```

只讀的 session 要讓 `HERMES_TWEET_ENABLE_ACTIONS` 保持 false。只有在進行已核准的私人讀取、寫入、monitor、webhook、extraction、draw 或媒體操作時，才設為 `true`。

## 輸入

選擇路由之前，先詢問這些輸入：

- 目標：研究、監控、客服分流、抽獎稽核，或操作準備
- 對象：帳號 handle、推文 URL、關鍵字、清單、monitor 或趨勢
- 時間範圍與新鮮度需求
- 是否涉及任何私人或會改變狀態的操作
- 確認 Hermes runtime 有 `XQUIK_API_KEY`

## 工作流程

1. 用 `tweet_explore` 搜尋內建的 endpoint catalog，找出符合的路由。
2. 選定 catalog 路由之後，透過 `tweet_read` 讀取公開的 X/Twitter 資料。
3. 只有在明確核准之後，才對私人或會改變狀態的路由使用 `tweet_action`。
4. API key 放在環境變數或 Hermes runtime 的 env 檔案中。
5. 不要把憑證貼進 prompt、issue、PR 留言或 tool 輸入。
6. 當使用者要的是活動、monitor、客服或抽獎的工作流程，而不是單次讀取時，載入[工作流程模式](references/workflows.md)。

## Tool 模型

| Tool | 用途 |
| --- | --- |
| `tweet_explore` | 不使用 API key，搜尋內建的 endpoint catalog。 |
| `tweet_read` | 設定了 `XQUIK_API_KEY` 時，呼叫 catalog 列出的公開唯讀 endpoint。 |
| `tweet_action` | 只有在啟用操作關卡時，才呼叫私人讀取、寫入、monitor、webhook、extraction、draw 和媒體操作。 |

## 輸出格式

回傳簡潔的操作輸出：

```text
摘要：
- 檢查了什麼、為什麼檢查

讀取路由：
- Catalog 路徑、輸入，以及結果摘要

操作計畫：
- 提議的私人或會改變狀態的操作，每一項都等待明確核准

下一步檢查：
- 有用的話，列出後續的路由或監控頻率
```

## 使用範例

在草擬回覆之前先研究某個帳號：

```text
用 Hermes Tweet 檢視 @example 最近的公開脈絡，再草擬回覆。
保持操作停用。
```

監控發表用的關鍵字：

```text
今天追蹤 X/Twitter 上對「Example Launch」的提及。
彙整主題和值得注意的帳號。不要發文。
```

準備一則受控的貼文：

```text
草擬一則發表推文，並列出你會使用的確切 tweet_action 呼叫。
在任何操作路由之前，先等待核准。
```

擷取結構化的路由筆記：

```json
{
  "objective": "support-triage",
  "route": "/api/v1/x/search",
  "action_gate": "disabled",
  "approval_required": true
}
```

## 疑難排解

- 如果只出現 `tweet_explore`，請在 Hermes runtime 主機上設定 `XQUIK_API_KEY`，並重新載入或重啟目前的 Hermes session。
- 如果操作路由無法使用，請讓公開讀取保持獨立。只有在進行已核准的私人或會改變狀態的操作時，才設定 `HERMES_TWEET_ENABLE_ACTIONS=true`。
- 如果路由不符，請再次使用 `tweet_explore`，並選擇 catalog 中列出的路徑，不要亂猜 endpoint。

## 最佳實務

- 把 Hermes Tweet 當作 Hermes 原生的 X/Twitter 層，不是通用的 API 包裝。
- 研究預設保持唯讀。建立或修改 monitor 之前要先取得核准。
- 在私人或會改變狀態的呼叫之前，使用 Desktop 或 gateway 的操作者審核。
- 呼叫 `tweet_read` 或 `tweet_action` 之前，驗證確切的 catalog 路徑。
- 環境變數改變之後，重啟 gateway、cron 或長時間執行的 Hermes session。

## 另請參閱

social-publishing plugin 與 Hermes Tweet 互補，用於廣泛的多平台發佈。Hermes Tweet 專注於 Hermes Agent 的 X/Twitter 工具集，以及它先讀取、需核准關卡的操作模型。

當路由邊界不清楚時，請見[endpoint 與核准契約](references/endpoint-contract.md)。官方指南見 https://github.com/Xquik-dev/hermes-tweet#readme。
