---
name: scientific-db-pubmed-database
description: 直接用 PubMed 和 NCBI E-utilities 搜尋生物醫學文獻的工作流程，涵蓋 MeSH 查詢、PMID 查找、引用文獻擷取，以及以 API 為基礎的文獻監控。任務需要的是 PubMed 的生物醫學文獻、而不是一般網頁搜尋時使用。
metadata:
  origin: community
---

# PubMed 資料庫

任務需要的是 PubMed 的生物醫學文獻、而不是一般網頁搜尋時，使用這個 skill。

## 何時使用

- 搜尋 MEDLINE 或生命科學文獻。
- 用 MeSH 詞、欄位標籤、日期或文章類型建立 PubMed 查詢。
- 查找 PMID、摘要、出版 metadata 或相關引用文獻。
- 進行系統性回顧的搜尋，需要可重複使用的搜尋字串。
- 直接從 Python、shell 或其他 HTTP client 使用 NCBI E-utilities。

## 查詢建構

先從研究問題出發，拆成幾個概念，再用布林運算子把概念組合起來。

```text
concept_1 AND concept_2 AND filter
synonym_a OR synonym_b
NOT exclusion_term
```

好用的 PubMed 欄位標籤：

- `[ti]`：標題
- `[ab]`：摘要
- `[tiab]`：標題或摘要
- `[au]`：作者
- `[ta]`：期刊名稱縮寫
- `[mh]`：MeSH 詞
- `[majr]`：主要 MeSH 主題
- `[pt]`：出版類型
- `[dp]`：出版日期
- `[la]`：語言

範例：

```text
diabetes mellitus[mh] AND treatment[tiab] AND systematic review[pt] AND 2023:2026[dp]
(metformin[nm] OR insulin[nm]) AND diabetes mellitus, type 2[mh] AND randomized controlled trial[pt]
smith ja[au] AND cancer[tiab] AND 2026[dp] AND english[la]
```

## MeSH 與副標題

概念有穩定的受控詞彙時，優先用 MeSH。主題很新或用語不統一時，把 MeSH 和標題/摘要用詞搭配使用。

正確的副標題語法是把副標題放在欄位標籤之前：

```text
diabetes mellitus, type 2/drug therapy[mh]
cardiovascular diseases/prevention & control[mh]
```

只有主題必須是論文核心時才用 `[majr]`。它能提高精確度，但可能漏掉相關的研究。

## 篩選條件

出版類型：

- `clinical trial[pt]`
- `meta-analysis[pt]`
- `randomized controlled trial[pt]`
- `review[pt]`
- `systematic review[pt]`
- `guideline[pt]`

日期篩選：

```text
2026[dp]
2020:2026[dp]
2026/03/15[dp]
```

可取得性篩選：

```text
free full text[sb]
hasabstract[text]
```

## E-utilities 工作流程

NCBI E-utilities 支援可重複的 API 工作流程：

1. `esearch.fcgi`：搜尋並回傳 PMID。
2. `esummary.fcgi`：回傳輕量的文章 metadata。
3. `efetch.fcgi`：抓取摘要或完整紀錄，格式有 XML、MEDLINE 或純文字。
4. `elink.fcgi`：找出相關文章和連結的資源。

正式環境的 script 要帶 email 和 API key。API key 存在環境變數裡，絕對不要放進 commit 的檔案或指令歷史。

```python
import os
import time
import requests

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def esearch(query: str, retmax: int = 20) -> list[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "tool": "ecc-pubmed-search",
        "email": os.environ.get("NCBI_EMAIL", ""),
    }
    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        params["api_key"] = api_key

    response = requests.get(f"{BASE}/esearch.fcgi", params=params, timeout=30)
    response.raise_for_status()
    time.sleep(0.35)
    return response.json()["esearchresult"]["idlist"]


pmids = esearch("hypertension[mh] AND randomized controlled trial[pt] AND 2024:2026[dp]")
print(pmids)
```

批次處理時，優先用 NCBI 的 history server 參數（`usehistory=y`、`WebEnv`、`query_key`），不要把很長的 PMID 清單塞進 URL。

## 輸出紀律

每一輪搜尋都要記錄：

- 完整的搜尋字串
- 搜尋的資料庫
- 搜尋日期
- 使用的篩選條件
- 結果數量
- 匯出格式
- 任何手動排除

範例：

```markdown
| Database | Date searched | Query | Filters | Results |
| --- | --- | --- | --- | ---: |
| PubMed | 2026-05-11 | `sickle cell disease[mh] AND CRISPR[tiab]` | 2020:2026[dp], English | 42 |
```

## Review 檢查清單

- 欄位標籤是有效的 PubMed 標籤嗎？
- 比較新的主題，有把 MeSH 詞搭配自由文字的同義詞嗎？
- 日期範圍明確而且合適嗎？
- 搜尋紀錄的細節夠不夠重現這個查詢？
- API key 是從環境變數載入的嗎？
- HTTP 程式碼有呼叫 `raise_for_status()`，或在解析前用其他方式處理非 200 的回應嗎？
- 有遵守 rate limit 嗎？

## 參考資料

- [PubMed help](https://pubmed.ncbi.nlm.nih.gov/help/)
- [NCBI E-utilities documentation](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [NCBI API key guidance](https://support.nlm.nih.gov/kbArticle/?pn=KA-05317)
- NCBI 支援：<eutilities@ncbi.nlm.nih.gov>
