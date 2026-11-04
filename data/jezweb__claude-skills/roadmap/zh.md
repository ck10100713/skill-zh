---
name: roadmap
description: "規劃並執行整個應用程式的建置。產生分階段的交付 roadmap，然後自主執行：一個階段一個階段做，在里程碑 commit、部署、測試，持續做到完成或卡住為止。模式：plan（產生 roadmap）、start（開始執行）、resume（從上次中斷的地方繼續）、status（顯示進度）。觸發詞：'roadmap'、'start building'、'resume the build'、'keep going'、'build the whole thing'、'execute the roadmap'、'what phase are we on'。"
compatibility: claude-code-only
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# Roadmap

為建置整個應用程式產生一份完整的技術 roadmap。要詳細到 Claude Code 能接手任何一個階段，並自主執行好幾個小時。

這不是高層次的策略文件。它是一份**交付藍圖**：每個階段都有具體的任務，每個任務都能執行，整體的順序讓你能從階段 1 一路做到上線，不用回頭。

## 什麼時候用

- 開始一個大型的新產品（在 deep-research 之後，或從產品簡報開始）
- 把模糊的想法轉成可執行的計畫
- 規劃橫跨多週、會跨越許多 Claude Code session 的建置
- 在說「build this」之前：roadmap 就是你交給 Claude Code 去執行的東西

## 輸入

這個 skill 需要下列其中一種：

| 輸入 | 去哪裡找 |
|-------|-----------------|
| Deep research 簡報 | `.jez/artifacts/research-brief-{topic}.md`（來自 `/deep-research`） |
| 產品簡報 | 使用者描述他想建置什麼 |
| 既有的半成品 app | 讀 CLAUDE.md + codebase 來了解現有的東西 |
| 要仿製/改良的競品 | URL 或產品名稱，由這個 skill 分析它 |

如果使用者只說「規劃一個跑在 Cloudflare 上的筆記 app」，這樣就夠了，需要的話再提出釐清問題。

## 工作流程

### 1. 確立願景

在做任何技術規劃之前，先釐清：

- **一句話**：這是什麼？（"A cloud-native markdown knowledge workspace for teams and AI agents"）
- **給誰**：主要使用者、次要使用者、agent？（"Jez first, then Jezweb team, then clients"）
- **為什麼**：既有工具哪裡做不到？缺口在哪？（"Existing tools are headless — you can't browse them or stumble across things"）
- **限制**：技術堆疊、預算、時程、必備項目？（"Cloudflare, must have MCP, needs to be a PWA"）
- **不做什麼**：明確排除在範圍之外的是什麼？（"No real-time CRDT collab, no plugin ecosystem"）

### 2. 定義技術堆疊

根據願景和限制，鎖定技術堆疊：

```markdown
| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | [framework] | [reason] |
| Backend | [framework + runtime] | [reason] |
| Database | [engine + ORM] | [reason] |
| Auth | [provider] | [reason] |
| Storage | [service] | [reason] |
| Search | [method] | [reason] |
| Hosting | [platform] | [reason] |
```

如果有 deep-research 簡報，就從那裡取用建議。沒有的話，根據使用者既有的技術堆疊做出有主見的選擇（去 `~/Documents/` 查看慣用模式）。

### 3. 設計資料模型

勾勒出完整產品需要的所有資料表/集合。不是只有階段 1，而是完整的模型。這能避免建置到一半要重新設計 schema。

```markdown
## Data Model

### [entity]
  id, [type]
  [field], [type], [constraints]
  ...
  created_at, updated_at

### [entity]
  ...

### Relationships
- [entity] has many [entity] via [field]
- [entity] belongs to [entity] via [field]
```

標出哪些資料表是在哪個階段需要的。階段 1 可能 8 張表只用得到 3 張，但先全部設計好，可以避免 migration 的痛苦。

### 4. 規劃階段

這是 roadmap 的核心。每個階段必須：

- **有明確的目標**：一句話描述這個階段完成後有什麼不同
- **可以獨立部署**：每個階段結束後，app 都能運作（功能較少而已）
- **建立在前一個階段上**：沒有任何階段需要把前面做的東西拆掉重來
- **能在 1-3 個 Claude Code session 內完成**：如果一個階段要超過一天，就拆開

#### 階段結構

每個階段：

```markdown
## Phase N — [Name]
*Goal: [One sentence — what the user can do after this phase that they couldn't before]*
*Depends on: Phase N-1*
*Estimated effort: [hours/sessions]*

### What's New
[Bullet list of user-visible features]

### Database Changes
[New tables, new columns, migrations needed]

### API Routes
[New endpoints this phase adds]

### Frontend
[New pages, components, UI changes]

### Infrastructure
[New Cloudflare resources, secrets, config]

### Task Checklist
[Actionable tasks grouped by area — these are what Claude Code executes]

#### Setup
- [ ] [task]

#### Data Layer
- [ ] [task]
- [ ] [task]

#### API
- [ ] [task]

#### Frontend
- [ ] [task]

#### Testing & Polish
- [ ] [task]
- [ ] [task]

### Definition of Done
[How to verify this phase is complete — what to test, what to deploy]
```

### 5. 階段規劃模式

#### 階段 1：永遠是 MVP

第一個階段必須產出**一個人能拿來做一件事**的東西。不是 demo，也不是骨架：而是一個能運作的工具，能取代使用者目前在用的任何方式（就算只是試算表或 Apple Notes）。

階段 1 的範圍測試：「你會用這個取代你現在用的東西嗎？」如果不會，MVP 就太單薄了。

典型的階段 1：
- 認證（單一使用者或僅限邀請）
- 核心資料模型（2-3 張表）
- 主要實體的 CRUD
- 基本 UI（列表 + 詳情 + 建立/編輯）
- 部署到正式網域
- 最基本的樣式（深色模式、響應式）

#### 階段 2：讓它變真

第二個階段把 MVP 變成你敢拿給別人看的東西：
- 打磨 UI
- 加入次要功能（搜尋、篩選、排序）
- 更好的錯誤處理和驗證
- 空狀態和 onboarding（用 `onboarding-ux` skill）
- 行動版響應式
- 資料匯出/匯入

#### 階段 3：差異化的特色

是什麼讓這個產品和替代品不同？在這裡把它做出來：
- AI 功能、MCP server、語意搜尋
- 競品沒有的東西
- 讓人選擇它而不選老牌產品的理由

#### 階段 4 以後：成長型功能

之後每個階段都增加能力：
- 多使用者 / 團隊功能
- 進階檢視（圖、canvas、行事曆、看板）
- 整合（API、webhook、第三方連接）
- 管理 / 設定
- 效能優化
- 對外的功能（分享、嵌入、白標）

#### 最後階段：平台

只有在產品正朝多租戶 / SaaS 發展時才做：
- 客戶工作區
- 計費 / 方案
- 白標 / 自訂網域
- 給第三方存取的 API token

### 6. 建置順序

用表格整理各階段：

```markdown
| Phase | Goal | New tables | New routes | Sessions |
|-------|------|-----------|-----------|----------|
| 1 | Personal MVP | 3 | 8 | 2-3 |
| 2 | Polish + search | +1 | +4 | 1-2 |
| 3 | AI + MCP | +1 (vectors) | +5 | 2-3 |
| 4 | Team features | +2 | +6 | 2-3 |
| 5 | Integrations | 0 | +4 | 1-2 |
| 6 | Platform | +2 | +8 | 3-4 |
```

### 7. 刻意不做的事

列出明確排除在範圍外的項目和原因。這能避免執行過程中範圍蔓延：

```markdown
## Deliberately Not Building (v1)

- Real-time collaborative editing (CRDTs) — too complex, Phase 5+ at earliest
- Plugin ecosystem — too much surface area
- Native mobile app — PWA is good enough
- Offline-first with local storage — we're cloud-native
```

### 8. Schema 演進地圖

顯示資料庫如何隨階段成長：

```markdown
| Table | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|-------|---------|---------|---------|---------|
| users | ✓ | | | |
| notes | ✓ | +tags col | +embeddings | |
| folders | ✓ | | | |
| note_links | | ✓ | | |
| workspaces | | | | ✓ |
| workspace_users | | | | ✓ |
```

### 9. API 範圍地圖

顯示 API 如何成長：

```markdown
| Route | Phase | Auth | Purpose |
|-------|-------|------|---------|
| POST /api/auth/* | 1 | — | Authentication |
| GET/POST /api/notes | 1 | Yes | Note CRUD |
| GET /api/search | 2 | Yes | Full-text search |
| GET /api/search/semantic | 3 | Yes | Vector search |
| GET/POST /mcp/tools | 3 | Token | MCP interface |
| POST /api/workspaces | 4 | Yes | Team workspaces |
```

## 輸出

把 roadmap 寫到 `docs/ROADMAP.md`（如果沒有 `docs/`，就放在專案根目錄）。

這個檔案應該是單一的 markdown 文件，Claude Code 在任何 session 一開始讀它，就知道接下來該建什麼。它是專案的北極星。

產生之後，也要更新：
- `CLAUDE.md`：加上對 roadmap 的引用
- `SESSION.md`：設定目前的階段

## 品質規則

1. **每個任務都必須能執行**：「設定 auth」太模糊。「用 email/password 設定 better-auth，建立 user 和 session 資料表，在 Hono 加上 auth middleware」才是能執行的。
2. **階段必須可部署**：每個階段結束後 app 都能運作。不要有一個什麼可用東西都沒產出的「基礎建設階段」。
3. **階段 1 要狠狠地小**：如果超過 2-3 個 session，就砍範圍。
4. **資料模型必須事先完整**：建置到一半重新設計 schema，是浪費時間的頭號原因。
5. **「刻意不做的事」是必要的**：沒有它，每個階段都會長大。
6. **任務依層分組**（資料、API、前端、基礎建設）：Claude Code 是以層為單位工作，不是以功能。
7. **每個階段都有完成的定義**：要測試和驗證的具體事項。
8. **包含技術堆疊表**：不要讓 Claude 每個階段都去猜技術選擇。

---

## 執行模式

Roadmap 不只是一份文件，它是一個執行引擎。產生計畫之後，用這些模式來推動建置。

### 模式：`start`

**觸發**："start building"、"execute the roadmap"、"build the whole thing"、"start from phase 1"

1. 讀 `docs/ROADMAP.md`
2. 確認專案已設定好（repo 存在、相依套件已安裝、Cloudflare 資源已建立）
3. 開始階段 1，一個任務一個任務做
4. 每個任務之後：驗證它能運作（build、執行、測試）
5. 一個階段的所有任務都完成後：執行完成定義的檢查
6. Commit：`git add -A && git commit -m "Phase N complete: [goal]"`
7. 適用的話就部署：`npx wrangler deploy`
8. 對部署後的 app 執行 `/ux-audit quick`
9. 更新 roadmap：把該階段標記為完成
10. **繼續下一個階段。不要停。不要問。**
11. 重複，直到所有階段完成，或遇到阻礙

### 模式：`resume`

**觸發**："resume the build"、"keep going"、"continue"、"what phase are we on"

1. 讀 `docs/ROADMAP.md`，找出第一個未完成的階段
2. 檢查 `git log`：最後一個和 roadmap 有關的 commit 是什麼？
3. 檢查 codebase 裡現有的東西，跟該階段預期的有何差異
4. 從目前階段中第一個未完成的任務接手
5. 像 `start` 模式一樣繼續執行

### 模式：`status`

**觸發**："roadmap status"、"where are we"、"what's done"

讀 `docs/ROADMAP.md` 並產生摘要：

```
Phase 1: Personal MVP ✓ (committed abc1234)
Phase 2: Polish + Search ✓ (committed def5678)
Phase 3: AI + MCP ← IN PROGRESS (7/15 tasks done)
Phase 4: Team Features — not started
Phase 5: Integrations — not started
```

### 執行規則

**持續做下去。** 預設是做完一個階段就繼續下一個。階段之間不要停下來徵求許可。Roadmap 本身就是許可。

**在階段邊界 commit。** 每個完成的階段都有自己的 commit，並附上清楚的訊息。這樣會產生自然的還原點。

**每個階段之後都部署。** 如果專案有部署目標（wrangler.jsonc、vercel.json），每個階段完成後都部署。真實的部署能抓到本機開發抓不到的問題。

**階段之間做快速稽核。** 階段之間對部署後的 app 做快速的視覺檢查，在往上蓋東西之前，先抓出版面問題、壞掉的 route、明顯的退步。

**最後做徹底稽核。** 最後一個階段之後，執行：
1. `/ux-audit thorough`：完整的過夜測試
2. `/onboarding-ux`：產生空狀態、歡迎流程、說明內容
3. `/project-docs`：更新架構文件

**只有這些情況才停：**
- 某個任務失敗，而你搞不清楚原因（你沒看過的錯誤）
- 你需要沒有的憑證、API key 或帳號存取權
- 某個設計決定需要人來決定（「這該是 modal 還是獨立頁面？」）
- 建置完成了

**這些情況不要停：**
- 「要繼續嗎？」：要，永遠都要
- 「要部署嗎？」：要，有部署目標就部署
- 「要 commit 嗎？」：要，在階段邊界 commit
- 不會擋住下一個任務的小問題：記成 GitHub issue，然後繼續

### 進度追蹤

直接在 `docs/ROADMAP.md` 裡標記完成的階段：

```markdown
## Phase 1 — Personal MVP ✅
*Completed: 2026-03-19, commit abc1234*
*Goal: Replace Apple Notes for one user.*
```

至於目前的階段，標記已完成的任務：

```markdown
### Task Checklist
- [x] D1 schema — notes, folders tables
- [x] Hono API routes: CRUD for notes
- [ ] CodeMirror 6 integration  ← CURRENT
- [ ] Quick switcher (Cmd+K)
```

這表示 `resume` 讀了 roadmap 就知道該從哪裡接手。

### 這如何取代 dev-session

舊的 `dev-session` skill 是管理 SESSION.md 檔案，用於跨 session 交接。Roadmap 的進度追蹤取代了它：

| dev-session 有 | roadmap 有 |
|----------------|-------------|
| 有「Current Position」的 SESSION.md | ROADMAP.md 裡打勾的任務 |
| 「Resume Instructions」 | 下一個沒打勾的任務本身就是指示 |
| 「What Works」區塊 | 附 commit hash 的已完成階段 |
| 檢查點 commit | 階段邊界 commit |
| 收尾 session | 最後階段 + 徹底稽核 |

Roadmap 就是 session 檔案。不需要另外的追蹤文件。
