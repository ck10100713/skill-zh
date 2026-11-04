---
name: workers-best-practices
description: 給正式環境應用程式用的 Cloudflare Workers 最佳實務。在撰寫、審查或設定 Workers 時使用。
---

你對 Cloudflare Workers API、型別和設定的知識可能已經過時。撰寫或審查 Workers 程式碼時，**優先用檢索，不要靠預訓練記憶**。

既有程式碼以專案已安裝的版本、產生出來的型別和 Wrangler 相容性設定為基準。要驗證 API、設定、執行期行為和限制的說法時，去檢索相關的 Cloudflare 文件。

## References

依任務讀對應的段落：

| Reference | 什麼時候用 |
|-----------|----------------|
| [Configuration and observability](references/configuration.md) | 相容性日期、binding、產生的型別、secret、log 和 trace |
| [Runtime patterns](references/runtime-patterns.md) | Streaming、promise 生命週期、request 狀態、服務呼叫、安全性和執行期測試 |
| [Platform API checks](references/platform-apis.md) | Handler 簽章、平台類別、binding 存取和序列化 |

證據不足時，參考 [Workers best practices](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/index.md)，或到 [Cloudflare docs directory](https://developers.cloudflare.com/directory/index.md) 找出相關產品。設定欄位以已安裝的 Wrangler schema 為準。較新的型別套件不會凌駕專案已設定的目標。

## Keep Compatibility Dates Current

新的 Worker 用今天的日期。既有的 Worker 要鼓勵定期更新，更新時檢視相容性變更並跑相關測試。既有行為要依它設定的日期和 flag 來評估，見[相容性指引](references/configuration.md#keep-compatibility_date-current)。

## Enable Observability

建立 Worker 或準備上正式環境時，要啟用 [Workers Logs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/index.md) 和 [Traces](https://developers.cloudflare.com/workers/observability/traces/index.md)。把 `observability.enabled` 和 `observability.traces.enabled` 都設成 `true`，只設最上層那個不會啟用 trace。用結構化 JSON logging，並依工作負載設定取樣。審查時，缺 log 或 trace 就要指出來。見[設定範例](references/configuration.md#enable-workers-logs-and-traces)。

## Place Compute Near Regional Databases

如果 Worker 會對同一個區域型資料庫連續發多次查詢，部署前要明確設定 placement，對應該資料庫的供應商和區域。缺位置資訊就問，既有的 placement 選擇要保留，並確認 handler 符合資格、檢查部署後的 request 耗時。見[資料庫 placement](references/configuration.md#place-compute-near-regional-databases)。

## Anti-Patterns to Flag

| Anti-pattern | 後果與建議做法 |
|-------------|-----------------------------------|
| 對無上限的資料使用 `await response.text()` 或類似的整包緩衝 | 可能耗盡 Worker 記憶體；[大型或無上限的 body 要用 stream](references/runtime-patterns.md#stream-request-and-response-bodies)。 |
| 在原始碼或設定檔裡寫死 secret | 會透過版本控制洩漏憑證；改用 Wrangler secrets。 |
| 用 `Math.random()` 產生對安全敏感的 token 或 ID | 值可預測；改用 `crypto.randomUUID()` 或 `crypto.getRandomValues()`。 |
| 啟動了非同步工作卻沒 await、沒 return，也沒掛到 `ctx.waitUntil()` | 工作可能被丟掉、錯誤會漏掉；要把它綁在 request 或背景工作的生命週期上。 |
| 模組層級的可變 request 狀態 | 會在 request 之間洩漏資料，也可能造成 I/O 擁有權錯誤；request 狀態要明確傳遞。 |
| 用 Cloudflare REST API 做 Worker binding 就能做的操作 | 多出網路和驗證的額外負擔；用現成的 binding。 |
| 把 `ctx.passThroughOnException()` 當一般的錯誤處理 | 轉給 origin 可能掩蓋 Worker 的失敗；改用明確的錯誤處理和結構化的錯誤回應。 |
| 手寫 `Env`，內容跟 Wrangler binding 重複 | 可能跟設定脫節；用 `wrangler types` 產生 binding 型別。 |
| 直接用字串比對 secret 值 | 可能暴露時間差；用 [Web Crypto 比對寫法](references/runtime-patterns.md#use-web-crypto-for-secure-token-generation)。 |
| 解構 `ctx` 的方法，例如 `const { waitUntil } = ctx` | 會失去接收者（receiver）；要呼叫 `ctx.waitUntil(...)`。 |
| 在 `Env` 或 handler 參數上用 `any` | 會藏住 binding 和 handler 契約的錯誤；用專案產生的型別和平台型別。 |
| 用 `as unknown as T` 硬湊平台型別 | 會藏住不相容的地方；要修掉底層契約。 |
| 用 `implements` 代替繼承平台的 base class | 繼承不到執行期行為、`this.ctx` 和 `this.env`；用對應的 base class。 |
| 在平台類別的 method 裡用沒綁定的 `env.X` | binding 要透過 `this.env.X` 存取；見 [binding 存取模式](references/platform-apis.md#binding-access--the-most-common-error)。 |
| 對 Queues、Workflow step、storage 和 WebSocket 套用同一套序列化規則 | 可能擋掉合法的 payload，或放行不支援的；要查[各自的 API 和編碼](references/platform-apis.md#serialization-boundaries)。 |

## Validation

受影響的 Workers 行為，用專案現有的檢查：binding 或 handler 契約有改就跑 type-check，行為有改就跑相關的執行期測試。專案要求的檢查要保留；小範圍的修改不需要做完整的 Workers 稽核。

## Scope

這個 skill 涵蓋 Workers 專屬的最佳實務和 code review。相關主題：

- **Durable Objects**：載入 `durable-objects` skill
- **Workflows**：見 [Rules of Workflows](https://developers.cloudflare.com/workflows/build/rules-of-workflows/index.md)
- **CLI 指令**：載入 `cf-cli` skill，或在有 Wrangler 設定檔的專案裡載入 `wrangler` skill

## Skill feedback

如果使用者反映這個 skill 給了錯誤或過時的指引，或是缺了資訊，就去讀 [references/skill-feedback.md](references/skill-feedback.md)。
