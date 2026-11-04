---
name: scientific-db-uspto-database
description: USPTO 專利與商標資料的工作流程，涵蓋官方紀錄查找、PatentSearch 查詢、TSDR 檢查、轉讓資料，以及可重現的智財研究紀錄。任務需要美國專利或商標局系統的官方專利或商標紀錄時使用。
metadata:
  origin: community
---

# USPTO 資料庫

任務需要美國專利商標局（USPTO）系統的官方美國專利或商標紀錄時，使用這個 skill。

## 何時使用

- 搜尋已核准專利或公開前的公開案。
- 檢查專利申請狀態、file-wrapper 資料、轉讓紀錄，或公開的審查歷史。
- 查詢商標狀態、文件或轉讓歷史。
- 建立可重現的先前技術、專利組合或智財版圖研究紀錄。
- 把 USPTO 紀錄跟 Google Patents、Lens.org、Semantic Scholar 或公司專利頁面等次級工具比對。

不要用這個 skill 提供法律意見。把它當成蒐集資料和驗證紀錄的工作流程。

## 來源選擇

優先使用官方的 USPTO 或 USPTO 支援的管道：

- Open Data Portal（ODP）：已遷移的 USPTO 資料集和 API 目前的家。
- Patent File Wrapper：公開的專利申請書目資料和 file wrapper 紀錄。
- PatentSearch API：PatentsView 的搜尋 API，涵蓋已核准專利和公開前公開案資料集。
- TSDR Data API：商標狀態和文件擷取。
- Patent and Trademark Assignment Search：所有權轉移紀錄。
- ODP 裡的 PTAB 資料：專利審判暨上訴委員會（Patent Trial and Appeal Board）程序。

次級來源只當作方便查找的索引。答案很重要時，要用官方紀錄交叉驗證。

## 驗證與 Secret

許多 USPTO API 流程需要 API key。把 key 存在環境變數或 secret manager，絕對不要放進 commit 的檔案或貼出來的對話紀錄。

常見的環境變數名稱：

```bash
export USPTO_API_KEY="..."
export PATENTSVIEW_API_KEY="..."
```

PatentSearch 要用 `X-Api-Key` header 帶 key。TSDR 則依照目前 USPTO API Manager 的說明和 rate limit 指引操作。

## PatentSearch 工作流程

問題跟趨勢、發明人、受讓人、分類、日期或專利組合切片有關時，用 PatentSearch 做廣泛的專利和公開前公開案搜尋。

流程：

1. 從目前的 PatentSearch 參考文件或 Swagger UI 找出 endpoint。
2. 建立帶明確篩選條件的 JSON 查詢。
3. 只請求分析需要的欄位。
4. 用確定的方式排序和分頁。
5. 記錄 endpoint、查詢內容、日期、資料時效備註和結果數量。

Python 請求骨架：

```python
import os
import requests

API_KEY = os.environ["PATENTSVIEW_API_KEY"]
BASE = "https://search.patentsview.org/api/v1"

payload = {
    "q": {
        "_and": [
            {"patent_date": {"_gte": "2024-01-01"}},
            {"assignees.assignee_organization": {"_text_any": ["Google", "Alphabet"]}},
        ]
    },
    "f": ["patent_id", "patent_title", "patent_date"],
    "s": [{"patent_date": "desc"}],
    "o": {"per_page": 100, "page": 1},
}

response = requests.post(
    f"{BASE}/patent/",
    headers={"X-Api-Key": API_KEY, "Content-Type": "application/json"},
    json=payload,
    timeout=30,
)
response.raise_for_status()
print(response.json())
```

重複使用查詢之前，先到線上的 PatentSearch 文件確認目前的 endpoint 名稱、欄位路徑、請求參數，以及 API key 是否還能用。

## 商標/TSDR 工作流程

任務需要商標案件狀態、文件、圖像、所有人歷史或審查事件時，用 TSDR。

流程：

1. 把申請序號或註冊號碼標準化。
2. 查看目前的 TSDR API 說明和必要的 API-key header。
3. 先抓狀態，需要時才抓文件。
4. 下載 PDF、ZIP 和多案件資料時，遵守比較低的 rate limit。
5. 在輸出裡記下擷取日期和序號/註冊號碼。

大量拉商標資料時，優先用有文件記載的批量資料流程，不要爬公開頁面。

## File Wrapper 與審查歷史

申請狀態、交易歷史和審查文件：

- 從 ODP 的 Patent File Wrapper 搜尋開始。
- 有精確識別碼就用：申請號、公開號、專利號或當事人名稱。
- 記錄這筆紀錄是已核准專利、公開前公開案，還是審查中的申請案。
- 引用之前，先對照紀錄詳細頁面核對文件日期和狀態。

## 轉讓工作流程

專利或商標所有權：

1. 用專利/申請/註冊號碼、讓與人、受讓人，或有的話用 reel/frame，搜尋官方轉讓資料。
2. 記錄轉讓文字、簽署日期、登記日期和當事人。
3. 把轉讓紀錄和目前法律上所有權的結論區分開來。
4. 所有權有實質影響時，把結果標記出來交給律師或主題專家審閱。

## 可重現的輸出

每一輪 USPTO 研究都要附一張紀錄表：

```markdown
| Source | Date searched | Identifier/query | Filters | Results | Notes |
| --- | --- | --- | --- | ---: | --- |
| PatentSearch | 2026-05-11 | `assignee=Alphabet AND date>=2024` | patent endpoint | 118 | API docs checked before run |
| TSDR | 2026-05-11 | `serial=90000000` | status only | 1 | API-key flow, no document bulk pull |
```

最後的書面報告要分開寫：

- 官方紀錄的事實
- 推論分析
- 次級來源的方便比對結果
- 尚未解決的缺口，或需要法律審閱的紀錄

## Review 檢查清單

- 有先用官方的 USPTO 或 USPTO 支援的來源嗎？
- 執行程式碼前，有確認目前的 endpoint 和欄位名稱嗎？
- API key 有沒有留在檔案、shell 歷史和輸出紀錄之外？
- 查詢紀錄有包含搜尋日期和精確的請求形式嗎？
- 有遵守 rate limit 嗎？
- 有避免下法律結論，或明確升級處理嗎？
- 次級來源有標示為次級嗎？

## 參考資料

- [USPTO APIs catalog](https://developer.uspto.gov/api-catalog)
- [USPTO Open Data Portal](https://data.uspto.gov/)
- [PatentSearch API reference](https://search.patentsview.org/docs/docs/Search%20API/SearchAPIReference/)
- [PatentSearch API updates](https://search.patentsview.org/docs/)
- [TSDR API bulk download FAQ](https://developer.uspto.gov/faq/tsdr-api-bulk-download)
