---
name: prompt-caching-strategy
description: >-
  最佳化 LLM 的 prompt caching 命中率，降低 API 成本並改善延遲。
  分析 prompt 結構，找出可快取與不可快取的內容，
  並建議如何重新調整結構，讓快取重複使用的程度最大化。
  TRIGGER when: 使用者說「prompt cache」、「cache hit rate」、「reduce LLM cost」、
  「optimize token usage」、「cheaper LLM calls」，或詢問 OpenAI/Anthropic/其他服務商的
  prompt caching 策略。
  DO NOT TRIGGER when: 使用者只是想最佳化單一 prompt 的品質
  （改用 prompt-optimizer），或詢問一般的快取基礎設施。
metadata:
  origin: community
  author: cyberspace-cs
  version: "1.0.0"
---

# Prompt Caching Strategy

把可重複使用的 prompt 內容安排好，提高快取的重複使用率，然後量測輸入成本和延遲。能省多少，取決於模型、平台、快取資格、寫入、保留時間、重複使用次數和輸出量。這個 skill 在 runtime 的快取命中和節省**沒有被量測過**；下面的範例只驗證算術，沒有呼叫任何服務商。

## 何時啟用

用在重複的 API 請求，這些請求共用經過授權的指示、工具或參考資料。要先確認確切的服務商 endpoint、模型、服務層級和快取模式。在選定費率、最短前綴長度或保留時間之前，先查閱它目前的文件。快取不會減少 context window 的使用量。

## 運作方式

### 保持穩定的前綴

讓可重複使用的指示、工具 schema 和範例保持穩定；在 API 允許的情況下，把會變動的問題、時間戳記和檢索結果放在這些內容後面。要遵守服務商的序列化順序：Claude 是 tools、system，然後是 messages。要讓前綴相符，內容必須完全相同，包括工具 schema 和相關的請求設定。前綴一改變，從那個點之後就可能無法重複使用。動態的後綴如果之後原封不動地被重複使用，本身也可能被快取。

```text
Reusable prefix: approved tools, instructions, stable examples/reference
Changing suffix: current question, fresh retrieval results, request metadata
```

只選相關的 context。為了達到資格門檻而硬塞 prompt，或擴大存取範圍，需要另外提出成本和品質上的理由。

### 保持使用者與工作區的界線

在快取查詢或重複使用之前，先授權內容的存取。應用程式管理的快取 handle 和計費 key，要限定在核准的使用者、工作區、服務商帳號、模型和內容版本範圍內。只分享明確核准用在該範圍的素材。快取 key 是路由/計費的提示，不是授權的關卡，也不是 sandbox。服務商的快取隔離不能取代應用程式的存取檢查。權限或內容變更時，要讓應用程式的參照失效；並遵守服務商的保留/刪除控制。避免把私有的 prompt 內容寫進 log。Context 的選擇、能力、sandbox 的強制執行和證據，都與快取最佳化各自獨立。

## 服務商的要求與使用量證據

連結的文件才是權威；不同的 endpoint 和 SDK 版本，可能會有不同的使用量欄位名稱。要把那個版本和計數器一起記錄下來。

| 服務商 | 要驗證的要求 | 要記錄的計數器 |
| --- | --- | --- |
| OpenAI | 各模型專屬的自動/明確模式、最短長度、保留時間，以及寫入/讀取的價格；較早和較新的模型不一樣 | Responses 的 `usage.input_tokens_details.cached_tokens`，以及有的話的 `cache_write_tokens`；輸入和輸出的總量。Chat Completions 用 `prompt_tokens_details.cached_tokens` |
| Claude | 支援的平台、模型的最小值、`cache_control` 的支援和 TTL；快取寫入的成本可能比一般輸入高 | `input_tokens`、`cache_creation_input_tokens`、`cache_read_input_tokens`、`output_tokens`；費率不同時，依 TTL 拆開寫入 |
| Gemini | 模型的最小值和 API：Interactions 支援 implicit caching；明確的 cache 物件需要 GenerateContent | Interactions 的 `usage.total_cached_tokens`；GenerateContent 的 `usage_metadata` 快取/輸入/輸出計數器，加上明確快取的 token 數量和保留時間 |

針對選定的模型，使用 [OpenAI 的 prompt caching 指南](https://developers.openai.com/api/docs/guides/prompt-caching)和[價格](https://developers.openai.com/api/docs/pricing/)。如果是 Chat Completions，要查[使用量 schema](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)。一般輸入要用總量減去快取讀取，以及另外回報的寫入量來推算；不要把同一批 token 算兩次。

使用 [Claude 的 prompt caching 指南](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)，了解目前的模型/平台限制和 TTL 費率。它的 `input_tokens` 把一般輸入和快取的讀取、寫入分開計算。即使標記了要快取，過短的前綴也可能讓所有快取計數器都是零。不要假設每個 Claude 模型或託管平台的最小值或讀取價格都一樣。

使用 [Gemini 的快取指南](https://ai.google.dev/gemini-api/docs/caching)、[GenerateContent 快取指南](https://ai.google.dev/gemini-api/docs/generate-content/caching)和[價格](https://ai.google.dev/gemini-api/docs/pricing)。明確快取的儲存，是依 token 數量和保留時間計費，跟讀取、一般輸入和輸出分開。Implicit 命中不保證。要驗證所選 endpoint 的計費類別，不要照抄別家服務商的費率。

## 成本比較計算器

把實際的使用量正規化成不重疊的類別，並用相同幣別、每百萬 token 的價格。當 TTL、模態、服務層級或模型的價格不同時，要把寫入類別拆開。儲存用的是百萬 token 小時；其他適用的費用，例如工具和 grounding，要各自列一行。量測期間內，要包含所有的 warmup、miss、過期、刷新和重試請求。

```text
baseline = (ordinary + written + read) * ordinary_input_rate / 1e6
           + output * output_rate / 1e6
actual   = ordinary * ordinary_input_rate / 1e6
           + written * cache_write_rate / 1e6
           + read * cache_read_rate / 1e6
           + output * output_rate / 1e6
           + storage_token_hours * storage_rate / 1e6
savings  = baseline - actual
```

這個反事實推算把 prompt 和輸出的量固定住。明確快取建立時，要把另外計費的建立輸入，算進寫入類別；使用該 endpoint 文件記載的費率。不存在的類別設為零。如果 warmup 請求或輸出不同，要另外比較實際前後的帳單。絕對不要把快取折扣套用在總帳單，或輸出 token 上。

可執行的計算器吃的是正規化後的計數器，不是服務商的原始回應：

```javascript
function compareCacheCost(usage, rates) {
  const counts = ['uncached', 'written', 'read', 'output', 'storageTokenHours'];
  const prices = ['input', 'write', 'read', 'output', 'storage'];
  for (const [values, keys] of [[usage, counts], [rates, prices]]) {
    for (const key of keys) {
      if (!Number.isFinite(values[key]) || values[key] < 0) {
        throw new Error(`${key} must be a finite nonnegative number`);
      }
    }
  }
  const outputCost = usage.output * rates.output / 1e6;
  const storageCost = usage.storageTokenHours * rates.storage / 1e6;
  const baseline = (usage.uncached + usage.written + usage.read)
    * rates.input / 1e6 + outputCost;
  const actual = (usage.uncached * rates.input + usage.written * rates.write
    + usage.read * rates.read) / 1e6 + outputCost + storageCost;
  return { baseline, actual, savings: baseline - actual, outputCost, storageCost };
}
```

## 範例

這些是假設的價格和數量，不是服務商的報價，也不是實測的命中。十次呼叫，每次都包含 10,000 token 的穩定前綴、2,000 token 的變動後綴，以及 2,000 個輸出 token。假設有一次前綴寫入和九次完整的前綴讀取。

| 類別 | Token 數 | 範例費率（每百萬） | 成本 |
| --- | ---: | ---: | ---: |
| 一般輸入 | 20,000 | $3.00 | $0.0600 |
| 快取寫入 | 10,000 | $3.75 | $0.0375 |
| 快取讀取 | 90,000 | $0.30 | $0.0270 |
| 輸出 | 20,000 | $15.00 | $0.3000 |
| 儲存 | 0 token-hours | $0.00 | $0.0000 |

基準線：120,000 個輸入 token，以 $3 計價，加上同樣的輸出 = **$0.6600**。
有快取：**$0.4245**，節省 **$0.2355**。寫入的溢價已經算進去了；$0.3000 的輸出帳單維持不變。在這些假設下，輸出量大的工作負載，輸入端節省的絕對金額相同，只是占總成本的比例較小。

如果明確快取把 10,000 個 token 保留兩小時，以假設的每百萬 token 小時 $1 計算，要加上 **$0.0200** 的儲存費。實際成本變成 **$0.4445**。要做真正的估算，請用所選 Gemini endpoint 的價格。

對只呼叫一次的情況，那次前綴寫入花的是 $0.0375，而不是一般輸入的 $0.0300：**多花 $0.0075**，而且沒有讀取的節省。對低於所選模型文件記載最小值的 500 token 前綴，要把請求視為沒有快取；在沒有計數器的情況下宣稱未來會命中，會高估節省。重複過期或前綴一直在變，也可能讓預期的節省變成更高的成本。

## 驗證流程

1. 從目前的文件，擷取符合資格的前綴大小和模型/平台的要求。
2. 在 ECC repo 裡，用 `node tests/skills/prompt-caching-strategy.test.js` 執行離線的範例和邊界情況。
3. 如果服務商的流量已獲授權，就比較配對的請求，並依核准的使用者/工作區，彙總實際的快取 token 數、所有輸入類別、輸出、儲存、延遲和實際成本。也要記錄 miss 和重寫。
4. 把快取讀取除以總輸入 token，回報成 token 命中率；請求命中率另外回報。分母和取樣期間要寫清楚。
5. 如果沒有量測任何流量，就把命中率、延遲改善和實際節省標記為未量測。離線算術無法證明任何 runtime 的快取行為。

## 與其他 Skill 的關係

- **prompt-optimizer** 在最佳化重複使用之前，先改善 prompt 的品質。
- **context-budget** 找出不必要的 context；快取仍然會消耗它。
- **cost-aware-llm-pipeline** 把快取跟路由、重試和其他成本做比較。
