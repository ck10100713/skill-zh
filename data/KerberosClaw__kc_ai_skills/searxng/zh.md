---
name: searxng
description: "當使用者想透過已設定好的本機 SearXNG 實例，而不是外部搜尋 API，進行注重隱私的網頁、圖片、新聞或影片搜尋時使用。對 SEARXNG_URL 呼叫內附的 script，支援結果數量上限／分類／語言／時間範圍，可回傳人類好讀的輸出或 JSON。不適用於沒有設定 SearXNG 實例的搜尋，或需要取得需驗證／私人資料的情況。"
author: Avinash Venkatswamy
version: 1.0.2
status: stable
homepage: https://searxng.org
triggers:
  - "search for"
  - "search web"
  - "find information"
  - "look up"
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["python3"]},"config":{"env":{"SEARXNG_URL":{"description":"SearXNG instance URL","default":"http://localhost:8080","required":true}}}}}
---

# SearXNG Search

你是注重隱私的搜尋操作員。你把搜尋請求導向使用者設定好的 SearXNG 實例並回報結果，不引入任何第三方 API 依賴。

用你本機的 SearXNG 實例搜尋網路，它是一個尊重隱私的 metasearch 引擎。

## Not For

- 如果缺少 `SEARXNG_URL`，而且連不到任何本機／預設的實例，就不要用。
- 不要爬取需驗證的頁面或使用者的私人帳號。
- 不要把搜尋結果的摘要片段當成已查證的事實；要標明不確定的地方，必要時順著來源往下查。

## Commands

### Web Search
```bash
uv run {baseDir}/scripts/searxng.py search "query"              # Top 10 results
uv run {baseDir}/scripts/searxng.py search "query" -n 20        # Top 20 results
uv run {baseDir}/scripts/searxng.py search "query" --format json # JSON output
```

### Category Search
```bash
uv run {baseDir}/scripts/searxng.py search "query" --category images
uv run {baseDir}/scripts/searxng.py search "query" --category news
uv run {baseDir}/scripts/searxng.py search "query" --category videos
```

### Advanced Options
```bash
uv run {baseDir}/scripts/searxng.py search "query" --language en
uv run {baseDir}/scripts/searxng.py search "query" --time-range day
```

## Configuration

**必填：** 把環境變數 `SEARXNG_URL` 設成你的 SearXNG 實例：

```bash
export SEARXNG_URL=https://your-searxng-instance.com
```

或是在你的 Clawdbot 設定裡設定：
```json
{
  "env": {
    "SEARXNG_URL": "https://your-searxng-instance.com"
  }
}
```

預設值（沒設定時）：`http://localhost:8080`

## Features

- 重視隱私（使用你自己的本機實例）
- 多引擎聚合
- 多種搜尋分類
- 豐富的格式化輸出
- 給程式使用的快速 JSON 模式

## API

使用你本機 SearXNG 的 JSON API 端點（預設不需要驗證）。
