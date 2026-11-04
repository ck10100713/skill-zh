---
name: skill-creator
description: 為使用 Azure SDK 和 Microsoft Foundry 服務的 AI coding agent，建立有效 skill 的指南。適用於建立新 skill 或更新現有 skill 時。
---

# Skill Creator

建立能擴充 AI agent 能力的 skill 的指南，重點放在 Azure SDK 和 Microsoft Foundry。

> **必要 Context：** 建立 SDK 或 API 的 skill 時，使用者一定要提供這個 skill 所依據的 SDK 套件名稱、文件 URL 或 repository 參照。

## 關於 Skills

Skill 是模組化的知識包，能把通用型 agent 變成專業的專家：

1. **程序性知識**：特定領域的多步驟流程
2. **SDK 專業**：Azure 服務的 API 模式、驗證、錯誤處理
3. **領域 context**：Schema、商業邏輯、公司專屬的模式
4. **附帶資源**：用於複雜任務的 script、參考資料、範本

---

## 核心原則

### 1. 簡潔是關鍵

Context window 是共用資源。對每一段內容都要質疑：「這值得它花掉的 token 成本嗎？」

**對領域/程序性的 skill**：Agent 本來就很有能力。只加它還不知道的東西。

**對 SDK/API 的 skill**：使用者一定要提供 SDK 套件名稱、文件 URL 或 repository 參照。沒有這個 context，就不能建立 skill。

### 2. 先看最新的文件

**Azure SDK 一直在變。** Skill 應該指示 agent 去驗證文件：

```markdown
## Before Implementation

Search `microsoft-docs` MCP for current API patterns:

- Query: "[SDK name] [operation] python"
- Verify: Parameters match your installed SDK version
```

### 3. 自由度

讓具體程度符合實作的限制。做法有多種時給高自由度；需要精確執行時給低自由度：

| 自由度    | 什麼時候                             | 範例          |
| ---------- | -------------------------------- | ---------------- |
| **高**   | 有多種有效的做法        | 文字指引  |
| **中** | 有偏好的模式但可變動 | Pseudocode       |
| **低**    | 必須精確                    | 特定的 script |

### 4. 漸進式揭露

Skill 分三個層級載入：

1. **Metadata**（約 100 字）：永遠在 context 裡
2. **SKILL.md 本文**（少於 5k 字）：skill 被觸發時
3. **參考資料**（不限）：需要時

**讓 SKILL.md 保持在 500 行以內。** 接近這個上限時，就拆成參考檔案。

---

## Skill 結構

**快速參考：**

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/      — Executable code
    ├── references/   — Documentation loaded as needed
    └── assets/       — Output resources (templates, images)
```

Azure SDK 的 skill，請遵循下面的 **Skill 段落順序**。領域 skill 則自行判斷如何合理組織。

### SKILL.md 要點

- **Frontmatter**：`name` 和 `description`（description 會觸發 skill）
- **本文**：保持在 500 行以內；大型 skill 要拆成參考檔案

### 附帶資源（選用）

| 類型          | 什麼時候要放                          | 範例                                                   |
| ------------- | ---------------------------------------- | ---------------------------------------------------------- |
| `scripts/`    | 重複使用的程式碼模式                     | 驗證設定、CLI script                                    |
| `references/` | 功能的深入探討和放不下的範例 | `capabilities.md` 索引、`non-hero-scenarios.md`、API 文件 |
| `assets/`     | 輸出範本                         | 樣板程式碼、圖片                                   |

---

## 建立 Azure SDK Skills

為 Azure SDK 建立 skill 時，要一致地遵循這些模式。

### Token 預算指引（必要）

每個 Azure SDK skill 都一定要維持在這些 token 上限內：

| 段落                       | 目標           | 絕對上限     |
| ----------------------------- | ---------------- | ---------------- |
| 安裝 + 環境變數       | 100 tokens       | 150              |
| 驗證與生命週期    | 200 tokens       | 300              |
| 核心流程（1 個範例）     | 300 tokens       | 400              |
| 功能表格                | 200 tokens       | 300              |
| 最佳實務（6 到 8 項）    | 200 tokens       | 250              |
| 參考資料（reference/ 連結） | 100 tokens       | 150              |
| **SKILL.md 總計**            | **約 1100 tokens** | **約 1500 tokens** |

**執行方式**：

- 超過絕對上限 → 重構成 `/references/` 子目錄
- 接近 500 行時 → 把整個段落搬到參考檔案
- 在 skill 的 H1 正下方加上註解 `<!-- Token Count: ~XXXX (target: 1100, max: 1500) -->`

---

### 參考資料抽取指南（必要）

用這些訊號決定什麼放在 SKILL.md、什麼放在 `/references/`：

| 訊號         | 搬到 `/references/`              | 留在 SKILL.md       |
| -------------- | ----------------------------------- | ---------------------- |
| 使用頻率  | 少於 20% 的典型使用                 | 約 80% 以上的流程     |
| 認知負荷 | 進階模式、多種選項 | 單一順利路徑      |
| 範例長度 | 超過 10 行、多條路徑           | 1 到 5 行、單一路徑 |

**內容抽取規則：**

- **批次操作** → `/references/batch-operations.md`
- **錯誤處理**（超出 try-except 的部分）→ `/references/error-handling.md`
- **效能調校** → `/references/performance.md`
- **替代流程** → `/references/workflows-comparison.md`
- **串流/事件** → `/references/streaming.md`
- **進階驗證** → `/references/auth-strategies.md`
- **工具整合** → `/references/tools.md`
- **Breaking change** → `/references/migration.md`

**決定：** 常見情況留在 SKILL.md，邊緣情況搬到 `/references/`。

---

### 核心流程的紀律（必要）

每個 Azure SDK skill 都必須釐清它記錄的是哪個（些）流程。

**情況 1：有單一明確的「核心流程」**（大多數服務）

如果有一個模式涵蓋約 80% 的使用情境：

1. 把它指定為核心流程
2. SKILL.md 裡**只**呈現這個流程（一個完整、可執行的範例）
3. 把替代方案延後到 `/references/`：
   - 批次操作 → `/references/batch-operations.md`
   - 錯誤處理 → `/references/error-handling.md`
   - 效能調校 → `/references/performance.md`
   - 替代流程 → `/references/workflows-comparison.md`

**範例**：Azure Key Vault Secrets（核心流程：用 managed identity 取得 secret）。替代的驗證流程放在 `/references/`：用 `DefaultAzureCredential` 做本機開發、workload identity，以及 service-principal 憑證（client secret 或 certificate）。

**情況 2：有多個同樣有效的「核心流程」**（例如驗證策略、deploy 目標）

如果沒有單一模式佔主導：

1. 把每個主打情境都放進 SKILL.md，就算這代表有多個同樣有效的流程
2. 在 SKILL.md 裡為每個主打情境，各放一個完整、可執行的範例
3. 用 `/references/workflows-comparison.md` 放取捨、次要的變化，以及會讓主檔案膨脹的更深入脈絡
4. 當有效的替代方案是實際使用的核心時，**不要**把它們當成「進階」，它們同樣有效，只是情境不同

**範例**：Azure Identity SDK 有好幾個主打情境。把主要的本機開發和正式環境安全的憑證流程留在 SKILL.md，再用 `/references/credential-types.md` 做更深入的比較，涵蓋 `AzureCliCredential`、workload identity、service principal 的各種變體，以及其他次要的憑證選擇。

**判斷規則**：如果你不確定，問自己：「選擇另一種做法的使用者，會覺得我寫的是錯的嗎？」如果會，那它就是另一個主打情境，要放進 SKILL.md。如果不會，就可以摘要並從 `/references/` 連結過去。

---

### Skill 段落順序

遵循這個結構（依據現有的 Azure SDK skill）：

1. **標題**：`# SDK Name`
2. **安裝**：`pip install`、`npm install` 等
3. **環境變數**：必要的設定，並用行內註解說明什麼時候需要。如果在正式環境使用 `DefaultAzureCredential`，要包含 `AZURE_TOKEN_CREDENTIALS`（設成 `prod` 或 `<specific_credential>`）
4. **驗證與生命週期**：對 Python skill 偏好 `DefaultAzureCredential`：本機開發原樣使用，正式環境則把 `AZURE_TOKEN_CREDENTIALS` 設成 `prod`（或特定目標憑證的名稱）來加以限制。也可以直接改用特定的 Microsoft Entra Token 憑證，例如 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`。**對 Python skill，這個段落一定要以標準的 callout 區塊開頭**（見下面的 [Python 必要的驗證與生命週期 Callout](#required-authentication--lifecycle-callout-python)）。
5. **核心流程**：最小可行的範例（依上面的核心流程紀律）
6. **功能表格**：Client、方法、工具
7. **最佳實務**：編號清單
8. **參考連結**：連到 `/references/*.md` 的表格（Azure SDK skill 要包含 `capabilities.md` + `non-hero-scenarios.md`）

### Python 必要的驗證與生命週期 Callout

> **範圍：** 只限 Python skill（`-py` 後綴）。其他語言可以依各自的慣用寫法。

每個 Python Azure SDK skill 一定要在 `## Authentication & Lifecycle` 段落的開頭，**逐字**放入下面的 callout 區塊，且要在任何程式碼範例之前。這樣能讓使用者在閱讀或複製任何 client 設定程式碼之前，就先看到這兩條不可妥協的規則。

```markdown
## Authentication & Lifecycle

> **🔑 Two rules apply to every code sample below:**
>
> 1. **Prefer `DefaultAzureCredential` for local development.** It works as-is with Azure CLI / VS Code / Developer CLI. For production, either constrain `DefaultAzureCredential` to production-safe credentials or use a specific credential directly. Avoid connection strings, account/API keys — they bypass Entra audit and rotation.
>    - Local dev: `DefaultAzureCredential` works as-is.
>    - Production: set `AZURE_TOKEN_CREDENTIALS=prod` (or `AZURE_TOKEN_CREDENTIALS=<specific_credential>`) to constrain the credential chain to production-safe credentials.
> 2. **Wrap every client in a context manager** so HTTP transports, sockets, and token caches are released deterministically:
>    - Sync: `with <Client>(...) as client:`
>    - Async: `async with <Client>(...) as client:` **and** `async with DefaultAzureCredential() as credential:` (from `azure.identity.aio`)
>
> Snippets may abbreviate this setup, but production code should always follow both rules.
```

**放置規則：**

- 直接插在 `## Authentication & Lifecycle` 標題下面，第一個程式碼範例之前。
- 不要改寫或重組措辭，跨 skill 的一致性就是重點。
- 如果 SDK 完全不支援 Entra ID（很少見，例如某些舊版的 speech REST endpoint、需要 subscription key 的 websocket API），就保留規則 2（context manager），並把規則 1 換成一句話，說明這個 SDK 需要 API key 驗證，以及為什麼目前還不能用 Entra。
- 如果 SDK 只支援 async（例如 `azure-ai-voicelive`），兩條規則都保留，但在條列項目中只顯示 async 的形式。
- 對沒有 client 生命週期的非 Azure Python skill（例如 `pydantic-models-py`），完全跳過這個 callout。

**程式碼範例的執行。** skill 本文裡每個 client 的建構，都必須展示這兩條規則：

- 在使用範例的每個 client 實例化處都要顯示 `with` / `async with`（不只是驗證段落）。
- 在主要的驗證範例中顯示 `DefaultAzureCredential`。**對仍然正式支援 API key 的 SDK，不要刪掉 API-key 範例**：許多現有使用者（尤其是還在完成 Entra 推行的受規管環境）需要一個可以複製貼上就能用的範例。把使用 key 的片段降級，放進一個清楚標示的 `### Legacy: API Key (existing keyed deployments)` 小節，放在同一個 `## Authentication & Lifecycle` 段落裡、主要 `DefaultAzureCredential` 區塊的**後面**。加上一行說明，新程式碼應該用 `DefaultAzureCredential`，使用 key 的路徑是給現有 deployment 的。同時把 `<SERVICE>_KEY` 環境變數加回環境變數區塊，並加上註解 `# Only required for the legacy API-key auth path below`。
- 有少數服務有 key 專屬的怪癖，值得在 Legacy 小節中點出（例如 `azure-ai-translation-text` 在對全域 endpoint 使用 key 時，需要 `region=` 參數，因為 token 憑證驗證需要自訂子網域的 endpoint）。要把這些放在降級的區塊中，不要刪掉範例。
- 對 async 範例，要把來自 `azure.identity.aio` 的 `DefaultAzureCredential`，和 client 一起包在 `async with credential:` 裡。

### 驗證模式（所有語言）

本機開發用 `DefaultAzureCredential`，它支援多種驗證方式。正式環境則用特定的憑證類型，或是設定 `DefaultAzureCredential`，並把環境變數 `AZURE_TOKEN_CREDENTIALS` 設成 `prod` 或指定目標憑證。

如果是在設定 Rust skill，本機開發用 `DeveloperToolsCredential`，正式環境用 `ManagedIdentityCredential`。Rust SDK 不支援 `DefaultAzureCredential`，所以要在每個環境中明確使用適當的憑證。

```python
# Python — note: client is wrapped in `with` for deterministic cleanup
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
# Local dev: DefaultAzureCredential works as-is.
credential = DefaultAzureCredential()
# Production alternative: constrain DefaultAzureCredential with AZURE_TOKEN_CREDENTIALS.
# credential = DefaultAzureCredential(require_envvar=True)
# Or use a specific credential directly in production:
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
with ServiceClient(endpoint, credential) as client:
    client.do_thing()
```

```csharp
// C#
using Azure.Identity;

// Local dev: DefaultAzureCredential. Production: set AZURE_TOKEN_CREDENTIALS=prod or AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// Or use a specific credential directly in production:
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
var client = new ServiceClient(new Uri(endpoint), credential);
```

```java
// Java
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredential;
import com.azure.identity.ManagedIdentityCredentialBuilder;

// Local dev: DefaultAzureCredential. Production: set AZURE_TOKEN_CREDENTIALS=prod or AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// Or use a specific credential directly in production:
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();
ServiceClient client = new ServiceClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();
```

```typescript
// TypeScript
import {
  DefaultAzureCredential,
  ManagedIdentityCredential,
} from "@azure/identity";
// Local dev: DefaultAzureCredential. Production: set AZURE_TOKEN_CREDENTIALS=prod or AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({
  requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"],
});
// Or use a specific credential directly in production:
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();
const client = new ServiceClient(endpoint, credential);
```

```go
// Go
import (
  "context"

  "github.com/Azure/azure-sdk-for-go/sdk/azidentity"
  "github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
)

ctx := context.Background()

// Local dev: DefaultAzureCredential. Production: set AZURE_TOKEN_CREDENTIALS=prod or AZURE_TOKEN_CREDENTIALS=<specific_credential>
cred, err := azidentity.NewDefaultAzureCredential(nil)
if err != nil {
  panic(err)
}

// Or use a specific credential directly in production:
// cred, err := azidentity.NewManagedIdentityCredential(nil)

client, err := azblob.NewClient("https://<account>.blob.core.windows.net/", cred, nil)
if err != nil {
  panic(err)
}

_ = client
_ = ctx
```

```rust
// Rust
use azure_identity::DeveloperToolsCredential;
use azure_storage_blob::BlobServiceClient;

let credential = DeveloperToolsCredential::new(); // Local dev
let client = BlobServiceClient::new(
    "https://<account>.blob.core.windows.net/",
    credential,
    None,
)?;
```

**絕對不要寫死憑證。要用環境變數。**

### 反模式：什麼不要做（必讀）

**這些模式會造成膨脹和低效率。每位 skill 作者在動筆之前，都要先看過這一段。**

#### 反模式 1：「鉅細靡遺的 API 參考」

- ❌ **不要**：在功能表格裡列出全部 50 個 SDK 方法，每種變化都附程式碼範例
- ✅ **要**：在表格裡放 3 到 5 個核心方法；鉅細靡遺的清單連到官方的 Azure API 參考
- **Token 成本**：列出所有方法 + 範例 = 浪費 400 到 600 tokens
- **對使用者的影響**：認知負荷壓倒性地大；使用者不知道該用哪個

#### 反模式 2：「同一個問題有多種解法」

- ❌ **不要**：在本文裡寫「分頁結果有 A、B、C、D 四種做法」
- ✅ **要**：「同步分頁用 `ItemPaged`」（主要範例）；替代方案連到 `/references/`
- **Token 成本**：每個替代做法 = 50 到 100 tokens；5 種做法 = skill 變得沒效率
- **對使用者的影響**：決策癱瘓；使用者會把所有東西重讀一遍

#### 反模式 3：「一個 Skill 裡有初學 + 中階 + 進階」

- ❌ **不要**：一個 skill 從「什麼是 client？」講到「自訂 retry policy」再講到「circuit breaker 模式」
- ✅ **要**：核心流程涵蓋 80% 的使用情境；進階模式放在 `/references/`
- **Token 成本**：每多一個 skill 等級增加 200 到 300 tokens；三個等級 = 額外 600 到 900 tokens
- **對使用者的影響**：專家覺得無聊，初學者應接不暇；沒有人得到他們需要的

#### 反模式 4：「重述官方文件」

- ❌ **不要**：「CosmosClient 的建構函式接收 endpoint（string）和 credential（TokenCredential）。endpoint 用來識別 Azure Cosmos 資源……」
- ✅ **要**：直接給程式碼：`client = CosmosClient(endpoint, credential)`。連到官方文件：`microsoft-docs` MCP。
- **Token 成本**：冗長的說明 = 每個參數 50 到 100 tokens；大型 API 浪費 300 以上 tokens
- **對使用者的影響**：多餘；官方文件才是權威，skill 該展示用法，不是重複它們

#### 反模式 5：「範例就夠了還寫冗長的說明」

- ❌ **不要**：「要建立 client，你首先要用建構函式實例化這個 class，傳入 endpoint 和 credential 參數。endpoint 是一個用來識別你資源的字串……」
- ✅ **要**：立刻給程式碼：`with CosmosClient(endpoint, credential) as client:`

---

### 效率驗證（必要，第 2 階段）

**撰寫期間，要手動驗證 skill 的效率，再來，如果 skill 在 `tests/scenarios/<skill-name>/vally/` 底下有 eval，就跑 Vally eval。**

**1. 量測 token 數：**

用 token 計數器或模型 playground 量測每個段落。和上面 Token 預算指引的目標比較。如果任何段落超過上限，就把內容搬到 `/references/`。

**2. 跑反模式檢查清單：**

- [ ] 沒有鉅細靡遺的 API 參考（顯示 3 到 5 個核心方法，不是 50 個）
- [ ] SKILL.md 裡沒有同一個問題的多種解法
- [ ] 沒有混合初學 + 中階 + 進階
- [ ] 沒有重述官方文件（先放程式碼，連到 microsoft-docs）
- [ ] 沒有冗長的散文（範例優先，文字最少）

**3. 範例數量稽核：**

- [ ] SKILL.md 中記錄的每個主打情境 / 核心流程，各有 1 個完整範例。對同時支援同步和非同步的 Python SDK，同一個流程的同步 + 非同步成對範例，算一個流程，不是兩個。
- [ ] 功能表格包含 3 到 5 個核心方法（不是完整的 API）
- [ ] 每個最佳實務項目最多 1 個範例

**4. Frontmatter 驗證：**

- [ ] `name` 符合 `.github/skills/<name>/SKILL.md`
- [ ] `description` 包含觸發關鍵字
- [ ] `description` 簡潔（約 200 字元是不錯的目標；schema 上限是 1,024 字元）
- [ ] 如果有放選用的 `benchmark_tokens_*` 和 `benchmark_quality_*` metadata 欄位，它們是 `metadata` 底下的扁平字串

**4b. 驗證指引的檢查**（對所有憑證都很關鍵）：

- [ ] 如果 skill 使用 Azure Identity 憑證，要對照該語言/套件目前的官方憑證文件驗證指引（有 Microsoft Learn 就用它；否則用上游 SDK repo 或套件文件）
- [ ] 對 Python skill，開發指引可以推薦 `DefaultAzureCredential`（支援多種開發憑證類型）
- [ ] 對 Python skill 的正式環境指引：單獨使用 `DefaultAzureCredential`（沒有限制）是不夠的；要求用 `AZURE_TOKEN_CREDENTIALS=prod`（或特定的目標憑證）限制憑證鏈，或是直接使用特定憑證（例如 `ManagedIdentityCredential`）
- [ ] 對 Rust skill，開發/正式環境的指引要反映實際支援的憑證（本機開發用 `DeveloperToolsCredential`；正式環境用特定的憑證，例如 `ManagedIdentityCredential`）
- [ ] 正式環境的憑證選擇，連到 `/references/auth-strategies.md` 或官方文件

**4c. 執行 Vally lint/eval（如果 skill 在 `tests/scenarios/<skill-name>/vally/` 底下有 spec）：**

```bash
# If the eval spec uses the shared Rust custom grader plugin, build it first.
(cd tests/scenarios/_shared/vally/grader-plugins/rust-cargo-build-failure && npm install && npm run build)

vally lint --eval-spec tests/scenarios/<skill-name>/vally/eval.yaml \
  --grader-plugin tests/scenarios/_shared/vally/grader-plugins/rust-cargo-build-failure \
  --strict

vally eval --eval-spec tests/scenarios/<skill-name>/vally/eval.yaml \
  --grader-plugin tests/scenarios/_shared/vally/grader-plugins/rust-cargo-build-failure
```

- [ ] `vally lint` 通過，沒有錯誤
- [ ] 有 `COPILOT_TOKEN` 時，`vally eval` 通過（沒有 error 等級的發現）；否則只做 lint 也可以接受，和 [`Vally Evaluation`](../../workflows/vally-evaluation.yml) workflow 的行為一致
- [ ] 沒有 `vally/` spec 的 skill 跳過這個步驟，這對每個 skill 是選用的，不是必要的

**5. 抽查：**

- [ ] 使用者能複製核心流程並立刻執行嗎？
- [ ] 所有範例都遵循最佳實務嗎（context manager、適當的憑證）？
- [ ] 所有環境變數都有記錄嗎？

**輸出：** 驗證之後，在 skill 的標頭用量測到的 token 數加上註解：

```markdown
# Azure Service SDK

<!-- Token Count: ~1180 (target: 1100, max: 1500) -->
```

---

### 標準動詞模式

Azure SDK 在所有語言中使用一致的動詞：

| 動詞     | 行為                     |
| -------- | ---------------------------- |
| `create` | 建立新的；已存在就失敗   |
| `upsert` | 建立或更新             |
| `get`    | 取得；缺少就報錯   |
| `list`   | 回傳集合            |
| `delete` | 就算缺少也算成功      |
| `begin`  | 開始長時間執行的操作 |

### 語言專屬模式

詳細的模式請看 `references/azure-sdk-patterns.md`，包含：

- **Python**：`ItemPaged`、`LROPoller`、context manager、Sphinx docstring。當 SDK 同時提供同步和非同步 client 時，把兩種形式都當作一級選項呈現，不要表達對任何一方的偏好。當 SDK 只有同步或只有非同步時，只記錄可用的模式。不要在單一程式碼範例中混用同步和非同步。一律顯示 `with` / `async with` 的 context manager。
- **.NET**：`Response<T>`、`Pageable<T>`、`Operation<T>`、mock 支援
- **Java**：Builder 模式、`PagedIterable`/`PagedFlux`、Reactor 型別
- **TypeScript**：`PagedAsyncIterableIterator`、`AbortSignal`、瀏覽器的考量
- **Go**：`context.Context` 當第一個參數、透過 `New*Pager()` + `More()/NextPage(ctx)` 的 `runtime.Pager[T]`、透過 `Begin*` + `PollUntilDone(ctx, nil)` 的 `runtime.Poller[T]`、`to.Ptr(...)` helper，以及有型別的 `*azcore.ResponseError`
- **Rust**：透過 `cargo add` 安裝、`azure_core` 的相依規則、`Response<T>`、`Pager<T>`、`RequestContent::from()`、`.into_model()`、明確的憑證型別、Entra ID 驗證所需的 RBAC 角色

### 每個 Skill 都要有的最佳實務（面向使用者）

#### Python、.NET、Java、TypeScript 和 Go 語言

**這兩條規則不只是 skill 自己的撰寫慣例，它們一定要明確寫進每個產生出來的 skill 的 `## Best Practices` 段落，讓照著 skill 做的終端使用者，在自己的程式碼裡也套用它們。**

把這兩項（只依語言/SDK 的特性調整）逐字加進最佳實務清單，當作**前兩項**。不要假設使用者會從範例推論出來。

**標準措辭（Python；其他語言要調整）：**

```markdown
1. **Do not mix sync and async clients in the same call path.** Use either `azure.xxx` sync clients or `azure.xxx.aio` async clients within a single call path — do not combine both.
2. **Always use context managers for clients and async credentials.** Wrap every client in `with Client(...) as client:` (sync) or `async with Client(...) as client:` (async). For async `DefaultAzureCredential` from `azure.identity.aio`, also use `async with credential:` so tokens and transports are cleaned up.
3. **Use `DefaultAzureCredential`** for code that runs locally. For code that runs in Azure, either constrain `DefaultAzureCredential` with `AZURE_TOKEN_CREDENTIALS=prod` (or a specific target credential) or use a specific token credential directly (e.g. `ManagedIdentityCredential`, `WorkloadIdentityCredential`).
```

**SDK 形狀不同時要套用的變體：**

| Skill 類型                                                                    | 把第 1 項調整成                                                                                                                   | 把第 2 項調整成                                                                                                                                                                                                              |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 只有 async 的 SDK（例如 voicelive）                                               | "This SDK is async-only; use the `.aio` namespace throughout."                                                                      | 維持標準                                                                                                                                                                                                                  |
| 以 async 為導向的 framework 指引（例如某些 agent framework） | "Use the framework's documented async patterns where required, but do not claim async is globally preferred for Azure Python SDKs." | 維持標準                                                                                                                                                                                                                  |
| Provider 模式（OpenTelemetry exporter/distro）                             | 維持標準                                                                                                                       | "Call `provider.shutdown()` / `flush()` at process exit to flush telemetry — providers are not context managers."                                                                                                              |
| 用 httpx 的 REST skill                                                        | 維持標準                                                                                                                       | "Use `with httpx.Client(...) as client:` (sync) or `async with httpx.AsyncClient(...) as client:` (async) so connections pool and close deterministically."                                                                    |
| Identity skill                                                                | 維持標準                                                                                                                       | "Use credentials as context managers (`with DefaultAzureCredential() as credential:`) when they own token caches / HTTP transports you want cleaned up; for async, use `async with` on credentials from `azure.identity.aio`." |
| FastAPI（非 Azure）                                                           | "Pick `def` or `async def` per endpoint based on whether you call async I/O; do not mix sync and blocking calls in one handler."    | "Manage long-lived resources (DB pools, HTTP clients) in `lifespan` and inject via `Depends`; use `with`/`async with` for per-request resources."                                                                              |
| 純模型/schema 的 skill（沒有 I/O，例如 pydantic）                               | **兩項都跳過**：不適用                                                                                                  | **跳過**                                                                                                                                                                                                                       |

**程式碼範例的執行。** skill 裡的每個程式碼範例本身，也都必須遵守這兩條規則，讓 skill 展示它所規定的：

- 不要在單一範例裡交錯同步和非同步呼叫。當 SDK 同時提供同步和非同步 client 時，把每種模式放在各自完整、自成一體的範例中，一個 `### Sync` 小節和一個 `### Async` 小節，給予同等的重要性。當 SDK 只有同步或只有非同步時，只顯示可用的模式。
- 每個範例裡每個 client 的實例化，都必須包在 `with` / `async with` 裡。唯一允許的例外，是強制的驗證片段（它說明憑證 + client 建構的模式），以及 client 由 app 擁有的 framework lifespan 模式（例如 FastAPI 的 `lifespan`）。
- 當來自 `azure.identity.aio` 的 async 憑證出現在範例中時，要和 client 一起包在 `async with credential:` 裡。

#### Rust 語言

**這些規則一定要明確寫進每個 Rust skill 的 `## Best Practices` 段落，當作最前面的項目：**

1. **用 `cargo add` 管理相依套件，絕對不要直接編輯 `Cargo.toml`。** 一律用 `cargo add <crate>` 或 `cargo remove <crate>`，不要手動修改 manifest 檔案。官方 crate 發佈在 crates.io，應該透過 cargo 加入。

2. **只有在直接 import `azure_core` 型別時，才把 `azure_core` 加進 `Cargo.toml`。** 如果你的程式碼 import 了像 `azure_core::http::Url`、`azure_core::http::RequestContent` 或 `azure_core::error::ErrorKind` 這樣的型別，就要明確把 `azure_core` 加進相依。如果你只用服務 crate 重新 export 的型別（例如透過 `use azure_storage_blob::BlobClient`），直接依賴 `azure_core` 是選用的。

3. **本機開發用 `DeveloperToolsCredential`，正式環境用 `ManagedIdentityCredential`。** Rust SDK 不支援 `DefaultAzureCredential`，所以要在每個環境中明確使用適當的憑證。

4. **用 `RequestContent::from()` 包裝上傳資料。** 上傳資料（例如 blob）時，把內容包在 `RequestContent::from(your_data)` 裡，確保 SDK 正確處理。

5. **為 Entra ID 驗證指派適當的 RBAC 角色。** 正式環境用 Entra ID 驗證時，要確保身分有被指派必要的 RBAC 角色（例如 blob 寫入存取要有「Storage Blob Data Contributor」）。

6. **一律用 crates.io 驗證套件版本。** 使用某個套件之前，先在 [crates.io](https://crates.io/) 檢查它的版本，確保你用的是穩定且受支援的版本。

7. **讓 `#[non_exhaustive]` 的 model struct 和 enum 具備前瞻性。** Azure Rust SDK 的 request/response model 經常是 `#[non_exhaustive]`。對**可由外部建構**、而且同時 derive `Default` 的 struct，初始化要以 `..Default::default()` 結尾（就算目前已知的每個欄位都設了），必要時用 `#[allow(clippy::needless_update)]` 在局部抑制 lint。對**真正 `#[non_exhaustive]`** 的 struct（Rust 禁止外部使用 struct literal，會產生 E0639），要用提供的 constructor 或 builder，或是先建立預設值，再修改你需要的欄位。比對 SDK 的 enum 時，要包含萬用字元（`_`）分支，讓服務之後新增的 variant 不會破壞比對。如果 skill 記錄了 model 的建構，它的程式碼範例就一定要展示這個模式。完整範例請看 `references/azure-sdk-patterns.md`（Model Types）。

### 有效 Skill 的範例（只拿結構合規的 Skill 當基準）

**只拿已經使用要求的 `references/` 版面（`references/capabilities.md` 加上 `references/non-hero-scenarios.md`）的 Azure SDK skill 當基準。** 早於這個結構的舊 skill 仍然可以提供風格上的想法，但在它們被調整到合規之前，不要直接照搬。

**一個有效的基準 skill 應該**：

1. 維持在 1,500 token 的絕對上限以內或以下（見上面的 Token 預算指引）
2. 涵蓋主打流程（CRUD 或主要操作），而不是每個功能變化
3. 每個概念放 1 到 2 個範例，不是 3 到 5 個
4. API 摘要用表格（憑證類型、RBAC 角色、client 階層）
5. 透過 `microsoft-docs` MCP 連到官方文件，不要重複內容
6. 把進階模式搬到 `/references/`
7. 包含 `references/capabilities.md` 和 `references/non-hero-scenarios.md`

**動筆寫你的 skill 之前**：直接套用上面的檢查清單，然後只模仿適合你使用情境的結構模式。

---

### 處理已廢棄或已改名的 SDK

當 Azure SDK 已廢棄或改名時，要更新 skill，引導使用者改用目前的套件，同時維持向下相容：

**1. 在 skill 最上方加上遷移通知：**

```markdown
> **⚠️ MIGRATION NOTICE**: The [Old Service Name] has been rebranded to **[New Service Name]**. While the package `old-package-name` remains available for compatibility, **new projects should use `new-package-name`** which provides the latest features and updates.
>
> **For new projects**: Use the `new-package-name` package instead.
>
> **This skill remains valid** for existing projects using `old-package-name`, but be aware you're using the legacy package name. The API patterns shown here are compatible with both packages.
```

**2. 顯示兩種安裝選項：**

```markdown
## Installation

### Legacy Package (Old Name)

\`\`\`xml
<dependency>
<groupId>com.azure</groupId>
<artifactId>azure-old-package</artifactId>
<version>4.2.0</version>
</dependency>
\`\`\`

### Recommended Package (New Name)

**For new projects, use the rebranded package:**

\`\`\`xml
<dependency>
<groupId>com.azure</groupId>
<artifactId>azure-new-package</artifactId>
<version>1.0.0</version>
</dependency>
\`\`\`

> **Note**: The API patterns in this skill apply to both packages. Replace package names and imports as needed when using `azure-new-package`.
```

**3. 什麼時候建立新 skill，什麼時候更新現有的：**

- 如果 API 大致相容（class/method 名稱相同或相似），就**更新現有的 skill**
- 如果 API 有顯著改變，就**建立新 skill + 遷移指南**（用 `references/migration.md`）
- 新舊 skill 之間**一律要交叉參照**

**範例：**

- `azure-ai-formrecognizer-java` → `azure-ai-documentintelligence`（服務改名）
- `azure-communication-callingserver-java` → `azure-communication-callautomation`（已廢棄，附遷移指南）

### 範例：Azure SDK Skill 結構

```markdown
---
name: skill-creator
description: |
  Azure AI Example SDK for Python. Use for [specific service features].
  Triggers: "example service", "create example", "list examples".
---

# Azure AI Example SDK

## Installation

\`\`\`bash
pip install azure-ai-example
\`\`\`

## Environment Variables

\`\`\`bash
AZURE_EXAMPLE_ENDPOINT=https://<resource>.example.azure.com
AZURE_TOKEN_CREDENTIALS=prod # Required only if DefaultAzureCredential is used in production
\`\`\`

## Authentication & Lifecycle

> **🔑 Two rules apply to every code sample below:**
>
> 1. **Prefer `DefaultAzureCredential` for local development.** It works as-is with Azure CLI / VS Code / Developer CLI. For production, either constrain `DefaultAzureCredential` to production-safe credentials or use a specific credential directly. Avoid connection strings, account/API keys — they bypass Entra audit and rotation.
>    - Local dev: `DefaultAzureCredential` works as-is.
>    - Production: set `AZURE_TOKEN_CREDENTIALS=prod` (or `AZURE_TOKEN_CREDENTIALS=<specific_credential>`) to constrain the credential chain to production-safe credentials.
> 2. **Wrap every client in a context manager** so HTTP transports, sockets, and token caches are released deterministically:
>    - Sync: `with <Client>(...) as client:`
>    - Async: `async with <Client>(...) as client:` **and** `async with DefaultAzureCredential() as credential:` (from `azure.identity.aio`)
>
> Snippets may abbreviate this setup, but production code should always follow both rules.

\`\`\`python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.example import ExampleClient

# Local dev: DefaultAzureCredential works as-is.
credential = DefaultAzureCredential()

# Production alternative: constrain DefaultAzureCredential with AZURE_TOKEN_CREDENTIALS.
# credential = DefaultAzureCredential(require_envvar=True)

# Or use a specific credential directly in production:

# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes

# credential = ManagedIdentityCredential()

with ExampleClient(
endpoint=os.environ["AZURE_EXAMPLE_ENDPOINT"],
credential=credential,
) as client:
item = client.get_item("example")
\`\`\`

## Core Workflow

\`\`\`python
with ExampleClient(endpoint=endpoint, credential=credential) as client: # Create
item = client.create_item(name="example", data={...})

    # List (pagination handled automatically)
    for item in client.list_items():
        print(item.name)

    # Long-running operation
    poller = client.begin_process(item.id)
    result = poller.result()

    # Cleanup
    client.delete_item(item.id)

\`\`\`

## Reference Files

| File                                                                 | Contents                                               |
| -------------------------------------------------------------------- | ------------------------------------------------------ |
| [references/capabilities.md](references/capabilities.md)             | Capability index (hero coverage + links to deep-dives) |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | Concrete non-hero examples                             |
| [references/tools.md](references/tools.md)                           | Tool integrations                                      |
| [references/streaming.md](references/streaming.md)                   | Event streaming patterns                               |
```

---

## Skill 建立流程

1. **蒐集 SDK Context**：使用者提供 SDK/API 參考（必要）
2. **理解**：從官方文件研究 SDK 的模式
3. **規劃**：找出可重複使用的資源和產品領域分類
4. **建立**：在 `.github/skills/<skill-name>/` 撰寫 SKILL.md
5. **分類**：在 `skills/<language>/<category>/` 建立 symlink
6. **測試**：建立驗收條件和測試情境
7. **文件**：更新 README.md 的 skill 目錄
8. **迭代**：依實際使用情況改進

### 步驟 1：蒐集 SDK Context（必要）

**建立任何 SDK skill 之前，使用者一定要提供：**

| 必要項目                  | 範例                                                   | 目的                  |
| ------------------------- | --------------------------------------------------------- | ------------------------ |
| **SDK 套件**           | `azure-ai-agents`、`Azure.AI.OpenAI`、`azblob`            | 識別確切的 SDK |
| **文件 URL**     | `https://learn.microsoft.com/en-us/azure/ai-services/...` | 主要的事實來源  |
| **Repository**（選填） | `Azure/azure-sdk-for-python`、`Azure/azure-sdk-for-go`    | 用於程式碼模式        |

**如果沒有提供，就提示使用者：**

```
To create this skill, I need:
1. The SDK package name (e.g., azure-ai-projects)
2. The Microsoft Learn documentation URL or GitHub repo
3. The target language (py/dotnet/ts/java/go)
```

**先搜尋官方文件：**

```bash
# Use microsoft-docs MCP to get current API patterns
# Query: "[SDK name] [operation] [language]"
# Verify: Parameters match the latest SDK version
```

### 步驟 2：理解這個 Skill

蒐集具體的範例：

- 「這個 skill 應該涵蓋哪些 SDK 操作？」
- 「哪些觸發詞應該啟動這個 skill？」
- 「開發者常遇到哪些錯誤？」

| 範例任務               | 可重複使用的資源              |
| -------------------------- | ------------------------------ |
| 每次都用同樣的驗證程式碼   | SKILL.md 裡的程式碼範例       |
| 複雜的串流模式 | `references/streaming.md`      |
| 工具設定        | `references/tools.md`          |
| 錯誤處理模式    | `references/error-handling.md` |

### 步驟 3：規劃產品領域分類

Skill 透過 symlink，依**語言**和**產品領域**組織在 `skills/` 目錄中。

**產品領域分類：**

| 分類      | 說明                             | 範例                                     |
| ------------- | --------------------------------------- | -------------------------------------------- |
| `foundry`     | AI Foundry、agent、專案、推論 | `azure-ai-agents-py`、`azure-ai-projects-py` |
| `data`        | Storage、Cosmos DB、Tables、Data Lake   | `azure-cosmos-py`、`azure-storage-blob-py`   |
| `messaging`   | Event Hubs、Service Bus、Event Grid     | `azure-eventhub-py`、`azure-servicebus-py`   |
| `monitoring`  | OpenTelemetry、App Insights、Query      | `azure-monitor-opentelemetry-py`             |
| `identity`    | 驗證、DefaultAzureCredential  | `azure-identity-py`                          |
| `security`    | Key Vault、secret、key、憑證  | `azure-keyvault-py`                          |
| `integration` | API Management、App Configuration       | `azure-appconfiguration-py`                  |
| `compute`     | Batch、ML 運算                       | `azure-compute-batch-java`                   |
| `container`   | Container Registry、ACR                 | `azure-containerregistry-py`                 |

**決定分類**的依據：

1. Azure 服務家族（Storage → `data`、Event Hubs → `messaging`）
2. 主要使用情境（AI agent → `foundry`）
3. 同一個服務領域中現有的 skill

### 步驟 4：建立 Skill

**位置：** `.github/skills/<skill-name>/SKILL.md`

**命名慣例：**

- `azure-<service>-<subservice>-<language>`
- 範例：`azure-ai-agents-py`、`azure-cosmos-java`、`azure-storage-blob-ts`、`azure-storage-blob-go`
- 對於文件文字中的 Go skill，使用簡短的套件名稱（例如 `azblob`）。
- 只在程式碼/import 範例中使用完整的 module import 路徑（例如 `github.com/Azure/azure-sdk-for-go/sdk/storage/azblob`）。

**對 Azure SDK skill：**

1. 在 `microsoft-docs` MCP 搜尋目前的 API 模式
2. 對照已安裝的 SDK 版本驗證
3. 遵循上面的段落順序
4. 範例中要包含清理的程式碼
5. 加上功能比較表

**先寫附帶的資源**，再寫 SKILL.md。

**定稿之前的品質保證：**

1. 撰寫時量測各段落的 token 數（用模型 playground 的 token 計數器）
2. 和 Token 預算指引的目標比較
3. 對照反模式檢查清單驗證（見反模式段落）
4. 如果某個段落超過上限 token 數，就抽取到 `/references/`
5. 執行效率驗證檢查清單，如果 skill 有 spec 的話也包含 `vally lint`/`vally eval`（見效率驗證）
6. 可以在 frontmatter 的 `metadata` mapping 底下，選擇性加入 `benchmark_tokens_*` 和 `benchmark_quality_*` 欄位（扁平的字串值）
7. 在 skill 標頭加上 token 數註解，方便日後維護

**Frontmatter（加上 benchmark metadata 的強化版）：**

```yaml
---
name: azure-service-py
description: |
  Azure Service SDK for Python. Use for [specific features].
  Triggers: "service name", "create resource", "specific operation".
metadata:
  benchmark_tokens_estimated: "1180"
  benchmark_tokens_target: "1100"
  benchmark_tokens_max: "1500"
  benchmark_quality_single_core_workflow: "true"
  benchmark_quality_examples_focused: "true"
  benchmark_quality_no_prose_bloat: "true"
  benchmark_quality_anti_patterns_checked: "true"
---
```

**Metadata 欄位：**（依 Agent Skills 的 `metadata` 規格，所有值都是字串，字串 key 對應字串值）

- `benchmark_tokens_estimated`：實際量測到的 token 數
- `benchmark_tokens_target`：目標效率（通常是 1100）
- `benchmark_tokens_max`：絕對上限（1500；超過就要拆分）
- `benchmark_quality_*`：個別的反模式檢查，每個都是 `"true"`/`"false"` 字串（例如 `benchmark_quality_single_core_workflow`）

### 步驟 5：用 Symlink 分類

在 `.github/skills/` 建立 skill 之後，在適當的分類中建立 symlink：

```bash
# Pattern: skills/<language>/<category>/<short-name> -> ../../../.github/skills/<full-skill-name>

# Example for azure-ai-agents-py in python/foundry:
cd skills/python/foundry
ln -s ../../../.github/skills/azure-ai-agents-py agents

# Example for azure-cosmos-db-py in python/data:
cd skills/python/data
ln -s ../../../.github/skills/azure-cosmos-db-py cosmos-db

# Example for azure-storage-blob-go in go/data:
cd skills/go/data
ln -s ../../../.github/skills/azure-storage-blob-go blob
```

**Symlink 命名：**

- 使用簡短、有描述性的名稱（例如 `agents`、`cosmos`、`blob`）
- 去掉 `azure-` 前綴和語言後綴
- 符合該分類中現有的模式

**驗證 symlink：**

```bash
ls -la skills/python/foundry/agents
# Should show: agents -> ../../../.github/skills/azure-ai-agents-py
```

### 步驟 6：建立測試

**每個 skill 都一定要有驗收條件和測試情境。**

#### 6.1 建立驗收條件

**位置：** `tests/scenarios/<skill-name>/acceptance-criteria.md`

> 驗收條件要放在 `tests/` 目錄樹裡（絕對不要放在 skill 資料夾內、`SKILL.md` 旁邊）。

**來源資料**（依優先順序）：

1. 官方 Microsoft Learn 文件（透過 `microsoft-docs` MCP）
2. repository 裡的 SDK 原始碼
3. skill 裡現有的參考檔案

**格式：**

```markdown
# Acceptance Criteria: <skill-name>

**SDK**: `package-name`
**Repository**: https://github.com/Azure/azure-sdk-for-<language>
**Purpose**: Skill testing acceptance criteria

---

## 1. Correct Import Patterns

### 1.1 Client Imports

#### ✅ CORRECT: Main Client

\`\`\`python
from azure.ai.mymodule import MyClient
from azure.identity import DefaultAzureCredential
\`\`\`

#### ❌ INCORRECT: Wrong Module Path

\`\`\`python
from azure.ai.mymodule.models import MyClient # Wrong - Client is not in models
\`\`\`

## 2. Authentication Patterns

#### ✅ CORRECT: DefaultAzureCredential + context manager

\`\`\`python
credential = DefaultAzureCredential()
with MyClient(endpoint, credential) as client:
client.do_thing()
\`\`\`

#### ❌ INCORRECT: Hardcoded Credentials

\`\`\`python
client = MyClient(endpoint, api_key="hardcoded") # Security risk
\`\`\`

#### ❌ INCORRECT: Connection string / account key when Entra is supported

\`\`\`python
client = MyClient.from_connection_string(os.environ["CONNECTION_STRING"]) # Bypasses Entra audit/rotation
\`\`\`

#### ❌ INCORRECT: Bare client without context manager

\`\`\`python
client = MyClient(endpoint, credential) # Leaks HTTP transport on exception / interpreter exit
client.do_thing()
\`\`\`
```

**要記錄的關鍵模式：**

- Import 路徑（不同 Azure SDK 之間差異很大）
- 驗證模式
- Client 初始化
- Async 變體（`.aio` module）
- 常見的反模式

#### 6.2 建立測試情境

**位置：** `tests/scenarios/<skill-name>/scenarios.yaml`

```yaml
config:
  model: gpt-4
  max_tokens: 2000
  temperature: 0.3

scenarios:
  - name: basic_client_creation
    prompt: |
      Create a basic example using the Azure SDK.
      Include proper authentication and client initialization.
    expected_patterns:
      - "DefaultAzureCredential"
      - "MyClient"
      - "with MyClient" # enforce context manager
    forbidden_patterns:
      - "api_key="
      - "hardcoded"
      - "from_connection_string" # prefer Entra over connection strings
    tags:
      - basic
      - authentication
    mock_response: |
      import os
      from azure.identity import DefaultAzureCredential
      from azure.ai.mymodule import MyClient

      credential = DefaultAzureCredential()
      with MyClient(
          endpoint=os.environ["AZURE_ENDPOINT"],
          credential=credential,
      ) as client:
          # ... rest of working example
          pass
```

**情境設計原則：**

- 每個情境只測**一個**特定的模式或功能
- `expected_patterns`：**一定要**出現的模式
- `forbidden_patterns`：**一定不能**出現的常見錯誤
- `mock_response`：能通過所有檢查的完整、可運作的程式碼
- `tags`：用於篩選（`basic`、`async`、`streaming`、`tools`）

#### 6.3 執行測試

```bash
cd tests
pnpm install

# Check skill is discovered
pnpm harness --list

# Run in mock mode (fast, deterministic)
pnpm harness <skill-name> --mock --verbose

# Run with Ralph Loop (iterative improvement)
pnpm harness <skill-name> --ralph --mock --max-iterations 5 --threshold 85
```

**成功標準：**

- 所有情境都通過（100% 通過率）
- 沒有 false positive（mock 回應一律通過）
- 這些模式能抓到真正的錯誤

### 步驟 7：更新文件

建立 skill 之後：

1. **更新 README.md**：把 skill 加到 Skill Catalog 中適當的語言段落
   - 更新 skill 總數（約第 73 行：`> N skills in...`）
   - 更新 Skill Explorer 連結的數量（約第 15 行：`Browse all N skills`）
   - 更新語言數量表（約第 77 到 83 行）
   - 更新語言段落的數量（例如 `> N skills • suffix: -py`）
   - 更新分類的數量（例如 `<summary><strong>Foundry & AI</strong> (N skills)</summary>`）
   - 在其分類中，依字母順序加入 skill 那一列
   - 更新測試覆蓋率摘要（約第 622 行：`**N skills with N test scenarios**`）
   - 更新測試覆蓋率表：更新該語言的 skill 數量、情境數量和前幾名 skill

2. **重新產生 GitHub Pages 資料**：執行抽取 script，並從單一範圍限定的目錄變更重建文件網站

   ```bash
   (cd docs-site && npx tsx scripts/extract-skills.ts && npm run build)
   ```

   這會更新 `docs-site/src/data/skills.json`（餵給以 Astro 為基礎的文件網站），然後把網站重建到 `docs/`，由 GitHub Pages 提供服務。

3. **確認 AGENTS.md**：確保 skill 數量正確

---

### 步驟 8：從最新的 SDK 來源重新產生現有的 Skill

當現有的 skill 有過時的範例、過期的 API 簽章，或改變了的套件指引時，使用這個流程。

1. **先找出權威的來源檔案**

對 Azure SDK 的各語言 skill，使用官方上游的原始文件和範例當作事實來源：

- Go：`https://github.com/Azure/azure-sdk-for-go/tree/main/sdk/<service>/<module>/README.md`
- Go 範例：`https://github.com/Azure/azure-sdk-for-go/tree/main/sdk/<service>/<module>/`
- Rust：`https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/<service>/<crate>/README.md`
- Rust 範例：`https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/<service>/<crate>/examples/`
- .NET/Java/Python/TS/Go：使用目前的 Microsoft Learn 套件文件 + 官方 SDK repo

2. **精準地更新 skill 內容**

- 更新程式碼片段，使其符合目前的 constructor/method 簽章
- 讓 crate/套件名稱符合官方發佈者的指引
- 除非刻意改變行為，否則保留 skill 的結構/frontmatter
- 上游的建議改變時，更新「Best Practices」和「Reference Links」
- 對 Rust，如果程式碼直接使用 `azure_core` 的型別/import，要確保 `Cargo.toml` 裡有 `azure_core`；如果只使用服務 crate 重新 export 的東西，直接依賴 `azure_core` 是選用的

### API 介面一致性關卡（每個重新產生的 skill 都必須通過）

把各語言權威的來源，當作重新產生的 skill 裡每個片段的契約：

- **Python、.NET、Java、TypeScript、Go**：把目前的 Microsoft Learn API 參考當作契約。
- **Rust**：把官方 SDK repository（`https://github.com/Azure/azure-sdk-for-rust`）和 crates.io 文件當作契約；Rust 套件沒有 Learn 的 API 參考頁面。

在定稿任何重新產生的 skill 之前：

1. 找出片段中顯示的每個 SDK 型別/方法（client、operation group、model constructor、enum 成員、像 `begin_*` 這樣的長時間執行方法）。
2. 對照該語言/套件的權威來源（見上面），驗證每個符號和簽章。
3. 如果權威來源顯示的形狀不同（例如巢狀的 `properties=...` model、改名的方法、`begin_*` 的 LRO 方法），就更新片段使其相符。
4. 重新檢查 import，讓 model/client 的 module 和權威來源完全一致。
5. 在主要片段中，不要保留和權威範例相矛盾的相容捷徑。

### 情境涵蓋關卡（每個重新產生的 skill 都必須通過，所有語言）

當片段能編譯時，重新產生還不算完成，要等 skill 展示出真實使用的廣度，才算完成。

在定稿任何重新產生的 skill 之前：

1. 從該 SDK 目前權威的文件/範例中，找出**主打情境**（有 Microsoft Learn 就用它；否則用上游 SDK repo 和套件文件）。
2. 確保每個主打情境都在 skill 裡有可複製貼上的片段（或在太大時，明確連到附帶的參考檔案）。
3. 新增/更新測試情境，讓主打流程由 harness 的 pattern 驗證。
4. 在 SDK 支援時，至少加入**一個重要的非主打情境**（例如：update/patch、delete/清理、export/import、進階驗證模式、分頁/篩選、retry/錯誤處理，或 LRO 監控）。對同時支援同步和非同步 client 的 Python SDK，以同等優先順序呈現兩種形式；不要把任何一種當作普遍偏好的。
5. 對 Azure SDK skill，把 `references/` 結構化為：
   - `references/capabilities.md`：一份簡潔的索引，記錄每個主打情境以及它被涵蓋的位置（`SKILL.md` 或附帶的參考檔案），加上連到更深入的非主打參考資料的連結，不要有歷史/遷移的敘述。
   - `references/non-hero-scenarios.md`：放刻意不放進主要 `SKILL.md` 的具體非主打範例。
   - 其他 `references/*.md` 檔案，用於專門的深入探討（operation group、工具、evaluator 矩陣等）。
6. 如果 SDK 有廣泛的 operation group 涵蓋（管理類 SDK 很常見），要包含一張 operation-group 表格，並明確指出哪些 group 在片段裡有涵蓋、哪些只在參考資料中提到。
7. 除非 skill 真的展示了所有主要的 operation group，否則絕對不要宣稱「完整的 API 介面」；否則要說明這個 skill 是針對主打流程加上精選的次要情境做最佳化。

### 重新產生流程步驟 3：驗證重新產生的 Skill 行為

```bash
(cd tests && pnpm harness <skill-name> --mock --verbose)
```

如果 skill 有 Vally 情境，定稿之前也要執行那個 eval（在本機或 CI 都可以）。

**Rust 重新產生關卡（Rust skill 必要）：**

重新產生任何 Rust skill 時，要驗證產生出來的 `## Best Practices` 段落，包含這確切的前兩條規則：

1. `Use cargo add to manage dependencies, never edit Cargo.toml directly`
2. `Add azure_core only when importing azure_core types directly`

定稿之前用內容檢查：

```bash
rg -n "Use `cargo add` to manage dependencies, never edit `Cargo.toml` directly|Add `azure_core` only when importing `azure_core` types directly" .github/plugins/azure-sdk-rust/skills/**/SKILL.md
```

除非每個受影響的 Rust skill 裡這兩行都有，否則重新產生就不算完成。

### 重新產生流程步驟 4：更新後重新產生文件產出物

```bash
(cd docs-site && npx tsx scripts/extract-skills.ts && npm run build)
```

### 重新產生流程步驟 5：記錄改了什麼

在 PR/commit 說明中，要包含：

- 用了哪些上游文件/範例
- 修正了哪些片段/簽章
- 跑了哪些測試/eval，以及結果

#### Python plugin 批次做法：`azure-sdk-python`

當請求是「regenerate all Python skills under azure-sdk-python」時使用。

1. **先確定確切的目標範圍**

```bash
# Canonical source of truth for Python plugin skills
ls .github/plugins/azure-sdk-python/skills/*/SKILL.md
```

- 把 `.github/plugins/azure-sdk-python/skills/` 當作權威來源。
- 編輯之後，保持 `.github/skills/<name>` 的連結同步（見下面的 symlink 檢查/修復步驟）。

2. **對每個 skill，從權威來源更新**

- 一律先用 `microsoft-docs` MCP 取得目前的 Microsoft Learn API 指引。
- 用 `pip show <package>` 驗證已安裝的套件版本，然後檢視已安裝的套件或官方 API 參考，驗證片段中用到的每個符號和簽章。
- 對 Azure SDK skill，優先使用套件概觀 + 官方 SDK repo 的範例。
- 對這個 plugin 裡非 Azure 的 Python skill（例如 `fastapi-router-py`、`pydantic-models-py`），保留語言專屬的最佳實務變體，並在不適用生命週期/驗證時，跳過 Azure 專屬的驗證 callout。

3. **一致地套用 Python 的執行規則**

- 對 Azure SDK 的 Python skill，保持標準的段落順序。
- 適用時，確保 `## Authentication & Lifecycle` 以必要的 callout 區塊開頭（逐字）。
- 確保每個 client 範例都使用 `with` / `async with` 的生命週期模式。
- 確保 `## Best Practices` 以兩條必要的面向使用者規則開頭（或針對只有 async／provider 模式 skill 所記錄的變體）。
- 確保每個重新產生的 Azure SDK Python skill 都有 `references/capabilities.md`（索引）和 `references/non-hero-scenarios.md`（具體的非主打範例）。
- 保留現有的 references/assets/scripts，除非它們過時或不正確。

4. **驗證所有重新產生的 Python skill**

```bash
# Fast frontmatter/structure validation for every Python skill
python .github/skills/skill-creator/scripts/quick_validate.py .github/plugins/azure-sdk-python/skills/<skill-name>

# Run Python skill harness in mock mode (all *-py scenarios)
(cd tests && pwsh ./run-harness-by-language.ps1 -Language py -Mock)
```

5. **同步 skill 連結和文件產出物**

```bash
# Ensure .github/skills links point at plugin canonical skills
python .github/scripts/sync_skill_links.py --plugin azure-sdk-python --check
python .github/scripts/sync_skill_links.py --plugin azure-sdk-python --apply

# Refresh docs site data after content changes
(cd docs-site && npx tsx scripts/extract-skills.ts && npm run build)
```

6. **批次重新產生的完成條件**

- 每個目標 `.github/plugins/azure-sdk-python/skills/*/SKILL.md` 都已更新，或明確確認為最新。
- `-py` skill 的 harness mock 執行通過，沒有退化。
- `azure-sdk-python` 的 skill 連結已同步。
- PR 說明包含用到的上游文件、簽章修正和驗證結果。

---

## 漸進式揭露模式

### 模式 1：帶參考資料的高層次指南

```markdown
# SDK Name

## Quick Start

[Minimal example]

## Advanced Features

- **Streaming**: See [references/streaming.md](references/streaming.md)
- **Tools**: See [references/tools.md](references/tools.md)
```

### 模式 2：語言變體

```
azure-service-skill/
├── SKILL.md (overview + language selection)
└── references/
    ├── python.md
    ├── dotnet.md
    ├── go.md
    ├── java.md
    └── typescript.md
```

### 模式 3：功能組織

```
azure-ai-agents/
├── SKILL.md (core workflow)
└── references/
    ├── tools.md
    ├── streaming.md
    ├── async-patterns.md
    └── error-handling.md
```

---

## 設計模式參考

| 參考                          | 內容                             |
| ---------------------------------- | ------------------------------------ |
| `references/workflows.md`          | 循序與條件式的流程 |
| `references/output-patterns.md`    | 範本和範例               |
| `references/azure-sdk-patterns.md` | 各語言專屬的 Azure SDK 模式 |

---

## 反模式

| 不要                                                                          | 為什麼                                                                                 |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| 沒有 SDK context 就建立 skill                                               | 使用者必須提供套件名稱/文件 URL                                            |
| 把「什麼時候用」放在本文                                                      | 本文是在觸發**之後**才載入的                                                         |
| 寫死憑證                                                                   | 安全風險                                                                       |
| 跳過驗證段落                                                    | Agent 會亂發揮                                                      |
| 使用過時的 SDK 模式                                                      | API 會變；先搜尋文件                                                      |
| 包含 README.md                                                              | Agent 不需要 meta 文件                                                      |
| 深層巢狀的參考資料                                                         | 只保持一層深                                                                       |
| 跳過驗收條件                                                       | 沒有測試的 skill 無法驗證                                             |
| 跳過 symlink 分類                                                    | Skill 無法依分類被發現                                             |
| 使用錯誤的 import 路徑                                                         | Azure SDK 有特定的 module 結構                                          |
| Python skill 的 Best Practices 省略同步/非同步 + context manager 條目 | 沒寫下來的規則，終端使用者不會遵守；光靠範例是不夠的 |
| 在同一個 Python 範例中混用同步和非同步                                  | 展示了 skill 本該防止的反模式                      |
| 交出重新產生的 skill，卻沒有任何測試情境                               | 主打流程和退化都無法驗證                                  |
| 從單一順利路徑範例就宣稱涵蓋完整 API                        | 隱藏了使用者在正式環境需要的 operation group 和非主打缺口                   |
| 省略非主打功能的 `references/*.md` 涵蓋                      | 把進階功能排除在 context 之外，且讓 API 的廣度沒有被記錄     |

---

## 檢查清單

完成 skill 之前：

**前置條件：**

- [ ] 使用者提供了 SDK 套件名稱或文件 URL
- [ ] 已透過 `microsoft-docs` MCP 驗證 SDK 的模式
- [ ] 已對照該 SDK 目前官方的語言專屬 API 參考，驗證每個片段的 API 介面（有 Microsoft Learn 就用它，否則用上游 SDK repo，見上面的權威來源）

**Skill 建立：**

- [ ] Description 包含做什麼和**什麼時候**（觸發詞）
- [ ] SKILL.md 在 500 行以內
- [ ] 驗證遵循語言規則（Python/.NET/Java/TS/Go 本機開發用 `DefaultAzureCredential`；Rust 本機開發用 `DeveloperToolsCredential`，正式環境用 `ManagedIdentityCredential`）
- [ ] 範例中包含清理/刪除
- [ ] 參考資料依功能組織（`capabilities.md` 索引 + 專門的深入探討檔案）
- [ ] 該 SDK 目前權威的文件/範例中的主打情境，在片段和測試中都有明確涵蓋
- [ ] 當 SDK 支援明確不同的非主打情境時，至少包含一個高價值的非主打情境（否則註明沒有適用的非主打情境）
- [ ] 對 Azure SDK skill，`references/capabilities.md` 索引主打/非主打的涵蓋，並連到專門的非主打文件
- [ ] 對 Azure SDK skill，`references/non-hero-scenarios.md` 包含和主打片段不同的具體非主打範例
- [ ] 對廣泛的 SDK（尤其是管理類 SDK），operation group 的涵蓋是明確的（片段有涵蓋 vs. 只在參考資料中）
- [ ] **（只限 Python skill）Best Practices 段落包含這兩條面向使用者的規則**（同步或非同步的一致性 + client 和 async 憑證的 context manager），使用符合 skill 類型的變體
- [ ] 對 Rust skill：`## Best Practices` 以 cargo 相依規則 + `azure_core` 直接 import 規則開頭

**分類：**

- [ ] Skill 建立在 `.github/skills/<skill-name>/`
- [ ] Symlink 建立在 `skills/<language>/<category>/<short-name>`
- [ ] Symlink 指向 `../../../.github/skills/<skill-name>`

**測試：**

- [ ] 已建立 `tests/scenarios/<skill-name>/acceptance-criteria.md`，並包含正確/不正確的模式
- [ ] 已建立 `tests/scenarios/<skill-name>/scenarios.yaml`
- [ ] 至少一個主打情境和一個非主打情境有測試涵蓋（當 SDK 兩者都支援時）
- [ ] 所有情境都通過（`pnpm harness <skill> --mock`）
- [ ] Import 路徑有精確記錄

**文件：**

- [ ] 已更新 README.md 的 skill 目錄
- [ ] 指示去搜尋 `microsoft-docs` MCP 取得最新的 API
