---
name: deep-research
description: "在動手建造新東西之前做深入研究與探索。探索本機專案裡可重用的程式碼、研究競爭對手、閱讀論壇與評論、分析 plugin 生態系、調查技術選項，並產出完整的研究簡報。三種深度：focused（30 分鐘）、wide（1-2 小時）、deep（3-6 小時）。觸發詞：'research this', 'discovery', 'explore the space', 'what should I build', 'competitive analysis', 'before I start building', 'research before coding'。不適用於附引用的事實查核研究報告（那由另一套流程處理）；這個是建造前的產品探索。"
compatibility: claude-code-only
---

# Deep Research

在建造新東西之前，做全面的研究與探索。不是憑訓練資料直接開始寫程式，這個 skill 會廣泛且深入地探索：本機探索、網路研究、競品分析、生態系訊號、預測未來，並產出一份研究簡報，讓實際建造的效率提高 10 倍。

## 深度等級

差別在於**企圖心的範圍**，不只是時間。

| 深度 | 目的 | 範圍 |
|-------|---------|-------|
| **focused** | 回答一個具體的問題 | 一個決定：「CodeMirror vs ProseMirror？」：針對性搜尋、本機掃描、1-2 個比較。產出一頁的建議。 |
| **wide** | 了解整個領域 | 新產品或新功能的全貌。競品、生態系、使用者需求、架構選項。夠寫一份 spec。 |
| **deep** | 規劃大型建造 | 一個角落都不放過。包含 wide 的所有內容，**再加上**函式庫/元件研究、plugin 生態系、挖掘 GitHub issues、社群情緒、預測未來，以及對每個決定做技術深入探討。夠支撐好幾週的開發。 |

預設：**wide**

## 工作流程

### 1. 理解意圖

詢問使用者：
- 你要建造**什麼**？（一句話）
- **為什麼**？它解決什麼問題？是給誰用的？
- **限制？**技術棧偏好、預算、時程、必備功能？
- **既有的成果？**有沒有可以延續的專案？有沒有可以參考的 repo？

使用者只給一個簡短的提示（「在 Cloudflare 上做 Obsidian 的替代品」），就夠了，剩下的缺口靠研究補上。

### 2. 本機探索

掃描使用者的機器，找相關的前人成果：

```bash
# Find related projects by name/keyword
ls ~/Documents/ | grep -i "KEYWORD"

# Read CLAUDE.md of related projects for architecture context
find ~/Documents -maxdepth 2 -name "CLAUDE.md" -exec grep -l "KEYWORD" {} \;

# Check for reusable patterns, schemas, components
find ~/Documents -maxdepth 3 -name "schema.ts" -o -name "ARCHITECTURE.md" | head -20
```

找到的每個相關專案：
- 讀 CLAUDE.md（技術棧、架構、陷阱）
- 檢查有沒有可重用的程式碼（schema、元件、工具函式、設定）
- 記下哪些做得好、哪些不好（從 git 歷史、TODO 註解看）

另外也檢查：
- Basalt Cortex（`~/Documents/basalt-cortex/`）裡相關的客戶、聯絡人和知識事實
- `grep -rl "KEYWORD" ~/Documents/basalt-cortex/ --include="*.md"`

### 3. 網路研究

廣泛搜尋，了解整個領域：

- **產品類別**：「markdown note app」、「knowledge management tool for teams」
- **競品**：搜尋「best X」、「X alternatives」、「X vs Y」，找出前 5-10 名
- **開源**：在 GitHub 搜尋開源替代品，看 star 數
- **架構**：「how to build X」、「X tech stack」、「building X with [framework]」
- **技術文件**：查看 llms.txt，以及關鍵技術的官方文件
- **平台範例**：「built with Cloudflare Workers」、「D1 full-text search example」
- **教學與案例研究**：「building a Y from scratch」、「lessons learned building Z」

### 4. 生態系與社群研究（wide + deep）

不要只看核心產品，生態系會揭露使用者真正需要什麼：

**Plugin 與外掛**：
- 主要競品有哪些 plugin？最受歡迎的那些，揭露了核心產品缺少什麼。
- 例如 Obsidian 有 1800 多個 plugin，前 20 名告訴你 Obsidian 原生做不好的地方。
- 搜尋：「top [product] plugins」、「[product] plugin directory」

**GitHub issues 與功能請求**：
- 查看主要競品的 GitHub repo，找按讚最多的 issue
- 依 thumbs-up 反應排序，這是直接的使用者需求訊號
- 查看已關閉的 issue，了解功能是怎麼實作的

**論壇討論**：
- Reddit：r/[product]、r/selfhosted、r/webdev、相關的利基 subreddit
- Hacker News：搜尋產品類別
- Discord/Discourse：產品專屬的社群
- 使用者喜歡什麼？抱怨什麼？希望有什麼？

**App store 與評論網站**：
- 1 星評價 = 未被滿足的需求（產品在這方面失敗）
- 5 星評價 = 該保留的東西（使用者喜歡，不要弄壞）
- 3 星評價 = 有趣的中間地帶（還可以，但是……）
- 搜尋：ProductHunt、G2、Capterra、App Store 評論

**整合需求**：
- 使用者想連接哪些系統？（Zapier 整合、API 需求）
- 這些揭露了真實的工作流程，使用者是把工具用膠帶黏在一起用的

### 5. 競品深入分析（wide + deep）

每個主要競品都要做（wide 3-5 個，deep 5-10 個）：

| 問題 | 怎麼研究 |
|----------|----------------|
| 功能 | Landing page、文件、changelog |
| 定價 | 定價頁面、比較網站 |
| 使用者抱怨 | Reddit、HN、app store 評論 |
| 技術棧 | Wappalyzer、view-source、職缺、部落格文章 |
| 它們做得好的地方 | 5 星評價、產品 demo |
| 它們做得差的地方 | 1 星評價、論壇抱怨、「從這個產品遷出」的遷移指南 |
| 文件品質 | 讀它們的文件網站：夠完整嗎？哪些主題需要最多的說明？（複雜的主題 = 使用者會卡關的地方） |
| 說明/支援內容 | 說明中心、FAQ、知識庫、支援論壇：使用者最常問什麼問題？ |
| 新手引導/教學 | 入門指南、影片教學、互動式導覽：它們怎麼教使用者用產品？它們假設使用者已經知道什麼？ |
| API 文件 | 如果有 API：文件寫得多好？用了什麼模式？提供什麼 SDK？ |
| 遷移指南 | 有沒有「從 X 轉過來」的指南？這些揭露了它們自認的優勢，**以及**使用者覺得難以轉換的地方 |

### 6. 函式庫與元件研究（deep 模式）

研究建構的基本單元，也就是已經存在、你可以使用或借鏡的東西：

**React / UI 函式庫**：
- 在 npm 搜尋特定類別的套件（「react markdown editor」、「react kanban」、「react data table」）
- 檢查每週下載量、最後發布日期、GitHub star 數、open issue 數量
- 讀 README 和範例：它們用了什麼模式？
- 檢查 bundle 大小（bundlephobia.com）：符合專案限制嗎？
- 看最好的那幾個的原始碼，它們的架構已經被真實使用驗證過

**Headless / 無樣式的函式庫**：
- Headless UI、Radix、React Aria、Downshift：你需要的功能有哪些現成的 primitive？
- 這些通常比完整的元件庫更好，因為樣式由你控制
- 檢查 shadcn/ui 是不是已經包好你需要的東西

**Hook 與工具函式**：
- TanStack（Query、Table、Virtual、Router）：哪些相關？
- React Hook Form、Zod、date-fns、Zustand：針對常見問題的成熟解法
- 搜尋「awesome-react」清單和精選合集

**平台專屬的函式庫**：
- 對 Cloudflare：什麼能在 Workers 上運作？（沒有 Node.js API、沒有原生模組）
- 查看 Cloudflare 自己的範例和起始範本
- 搜尋「cloudflare workers」加上你需要的功能

**每個函式庫要記錄什麼**：

| 問題 | 為什麼重要 |
|----------|---------------|
| 它能解決我們的問題嗎？ | 功能是否符合 |
| Bundle 大小 | 效能預算 |
| 最後發布日期 | 還有在維護嗎？ |
| Open issue / PR | 社群健康度 |
| 能在我們的平台上運作嗎？ | Cloudflare Workers 有限制 |
| 它用了什麼模式？ | 就算我們不用這個函式庫，它的模式也很有價值 |

**洞察**：就算你決定自己做客製的，研究現有的函式庫，也會讓你看到那些經得起真實使用者考驗的模式。一個有 1 萬 star 的函式庫，API 是經過數千名開發者打磨的，偷學他們的設計決定。

### 7. 平台能力深入探討（wide + deep）

**這很關鍵。**Claude 的訓練資料對平台功能總是落後。Cloudflare、Vercel、Firebase、Supabase 都不斷在推出新能力。你以為不存在的功能，可能上個月就上線了。Basalt Cortex 專案之所以存在，就是因為有些能力（Workers AI toMarkdown、Vectorize metadata filtering、D1 FTS5）不主動去找就看不出來。

**不要靠訓練資料判斷平台能力。**去讀實際的最新文件。

#### 怎麼研究平台

1. **抓取平台的 changelog/部落格**：
   - Cloudflare：`https://blog.cloudflare.com/` + `https://developers.cloudflare.com/changelog/`
   - Vercel：`https://vercel.com/changelog`
   - Firebase：`https://firebase.google.com/support/releases`
   - Supabase：`https://supabase.com/changelog`

2. **讀完整的產品目錄**，不只是你已經在用的服務：
   - Cloudflare：Workers、D1、R2、KV、Vectorize、Queues、Durable Objects、Workers AI、AI Gateway、Workflows、Containers、Browser Rendering、Tunnel、Email Routing、Images、Stream、Hyperdrive、Pipelines、Sandbox
   - Vercel：Functions、Edge Middleware、KV、Postgres、Blob、AI SDK、Cron、Firewall
   - Firebase：Firestore、Auth、Storage、Functions、Hosting、Extensions、Genkit、App Check

3. **每個服務都問**：它能解決我們正在建造的產品裡的某個問題嗎？

4. **找最近才推出的功能**，它們擴大了可能性：
   - 邊緣端有新的 AI 模型可用嗎？
   - 有新的儲存 primitive 嗎？
   - 有新的網路能力嗎？
   - 有新的驗證/身分功能嗎？
   - 有新的 build/部署選項嗎？

#### Cloudflare 能力檢查清單（其他平台依此擴充）

逐項檢視，並問「這對我們在做的東西有用嗎？」：

| 類別 | 要調查的服務 |
|----------|----------------------|
| **運算** | Workers、Cron Triggers、Queues consumers、Workflows（多步驟）、Containers、Durable Objects（有狀態）、Tail Workers |
| **儲存** | D1（SQL + FTS5）、R2（物件）、KV（key-value）、Durable Object storage（強一致性） |
| **AI** | Workers AI 模型（文字、圖片、embedding、語音、翻譯、toMarkdown）、Vectorize（語意搜尋）、AI Gateway（快取/路由） |
| **網路** | 自訂網域、Tunnel、Spectrum（TCP/UDP）、WebSockets、Hyperdrive（資料庫 proxy） |
| **安全** | WAF、Turnstile（CAPTCHA）、Bot Management、API Shield、DDoS |
| **媒體** | Images（即時縮放/最佳化）、Stream（影片）、Browser Rendering（截圖、產生 PDF） |
| **Email** | Email Routing（規則）、Email Workers（可程式化的收信處理） |
| **可觀測性** | Workers Logs、Analytics Engine、GraphQL analytics |

#### 要記錄什麼

每個相關的能力都記下：
- 它做什麼（一句話）
- 在這個產品裡可以怎麼用
- 任何限制或價格上的考量
- 範例：「Workers AI `toMarkdown()` 可以在邊緣端把任何上傳的 PDF/DOCX 轉成 markdown，我們可以用它來做文件匯入，不需要任何外部服務」

#### 為什麼這很重要

「做一個筆記 app」和「做一個能把任何檔案轉成 markdown、能跨所有筆記做語意搜尋、能用 AI 產生摘要、能透過背景 Workflows 同步、還能用 Browser Rendering 渲染 PDF 的筆記 app」，差別在於**知道平台提供了什麼**。大多數開發者只用到平台的 20%，因為他們從沒看過另外的 80%。

### 8. 預測未來（deep 模式）

想得比現在已存在的東西更遠：

**平台路線圖**：根據上面對 changelog 和部落格的研究，平台正往哪個方向走？有什麼在 beta？有什麼已宣布但還沒 GA？

**AI 整合**：不是「加個聊天機器人」，要想得更深。當工具能讀取、推理並對使用者的資料採取行動時，有什麼可能？如果每則筆記都能做語意搜尋呢？如果 app 能自己寫文件呢？如果上傳的東西自動轉成 markdown 呢？

**裝置與輸入方式的演進**：手機優先、語音輸入、穿戴裝置、空間運算。2 到 5 年後，使用者可能怎麼跟這個東西互動？

**資料來源**：還有什麼新的輸入可以餵進來？感測器、API、即時資料、跨 app 的脈絡？

**相鄰的機會**：緊鄰這個問題的還有什麼問題？例如在做筆記 app：相鄰的是任務管理、專案追蹤、團隊溝通。使用者現在用膠帶把什麼東西黏在一起？

**匯流趨勢**：哪些原本分開的工具正在被統一？（Email + 聊天 + 任務 = Slack。筆記 + 資料庫 + wiki = Notion。下一個是什麼？）

### 9. 技術研究（deep 模式）

針對每個主要的架構決定：

| 決定領域 | 要回答的問題 |
|--------------|-------------------|
| 編輯器 / UI 框架 | 選項、取捨、社群規模、我們的經驗 |
| 資料庫 | SQL vs NoSQL vs 檔案、託管 vs 自架、我們的技術棧支援度 |
| 驗證 | Better-auth、Clerk、Auth.js、自製，哪個適合？ |
| 託管 / 部署 | Cloudflare、Vercel、Railway：限制和能力 |
| 搜尋 | FTS5、Elasticsearch、Meilisearch、Vectorize，什麼規模？ |
| 即時 | WebSockets、SSE、Durable Objects，我們需要嗎？ |
| 檔案儲存 | R2、S3、本機，存取模式是什麼？ |
| API 設計 | REST、tRPC、GraphQL，這個使用情境需要什麼？ |

### 10. 整合

產出研究簡報，存到 `.jez/artifacts/research-brief-{topic}.md`：

```markdown
# Research Brief: [Topic]
**Depth**: [focused|wide|deep]
**Date**: YYYY-MM-DD
**Research time**: [duration]

## Executive Summary
[2-3 sentences: what to build, why, key insight from research]

## Competitive Landscape
| Product | Strengths | Weaknesses | Pricing | Users |

### Key Insights
[What winners do well, what gaps exist in the market]

## Ecosystem Signals
### Most Popular Plugins/Add-ons
[Top plugins for competitors — reveals unmet needs]
### Most Requested Features
[From GitHub issues, forums, reviews — sorted by demand]
### Integration Patterns
[What systems users connect to — reveals real workflows]

## User Needs
[What real users want, from reviews/forums/complaints]

## Technical Landscape
| Decision | Options | Recommendation | Why |

## Libraries and Components
| Need | Library | Stars | Size | Fits platform? | Notes |
[Key libraries evaluated for each major feature]

## Platform Capabilities
| Service | Could use for | Impact |
[Every platform service evaluated against the product's needs]
[Flag recently shipped features the team may not know about]

## Reusable From Existing Projects
| Project | What to reuse | Location |

## Future Possibilities
### Platform roadmap
### AI opportunities
### Adjacent problems
### 2-5 year horizon

## Proposed Architecture
[Stack, data model sketch, key flows]

## Risks and Open Questions
[Things research couldn't answer]

## Suggested Phases
[Build order based on research findings]

## Sources
[Links to everything read]
```

## 小提醒

- 儘早開始寫簡報，邊研究邊補充，這份成品就是交付物
- deep 模式用 sub-agent 來平行處理網路研究和本機探索
- 「Reusable From Existing Projects」這一節常常能省下好幾週的工作
- 生態系訊號（plugin、issue、評論）往往比競品的功能清單更有價值
- 把簡報存到 `.jez/artifacts/`，對之後的 session 和實際的建造階段都有用
- 簡報是活的文件，在建造過程中學到更多，就更新它
