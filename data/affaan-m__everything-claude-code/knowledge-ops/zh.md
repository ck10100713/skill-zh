---
name: knowledge-ops
description: 跨多個儲存層（本地檔案、MCP 記憶、向量資料庫、Git repo）的知識庫管理、匯入、同步與檢索。使用者想儲存、整理、同步、去重，或跨自己的知識系統搜尋時使用。
metadata:
  origin: ECC
---

# Knowledge Operations

管理一套多層的知識系統，用來在多個儲存位置之間匯入、整理、同步和檢索知識。

優先採用實際運作中的工作區模型：
- 程式碼工作放在真正 clone 下來的 repo
- 進行中的執行 context 放在 GitHub、Linear 和 repo 本地的工作 context 檔案
- 更廣泛、給人看的筆記可以放在非 repo 的 context/封存資料夾
- 跨機器的持久記憶屬於知識庫，不是影子 repo 工作區

## When to Activate

- 使用者想把資訊存進他的知識庫
- 把文件、對話或資料匯入結構化儲存
- 在各系統之間同步知識（本地檔案、MCP 記憶、Supabase、Git repo）
- 對既有知識去重或整理
- 使用者說「save this to KB」、「sync knowledge」、「what do I know about X」、「ingest this」、「update the knowledge base」
- 任何超出單純記憶回想的知識管理任務

## Knowledge Architecture

### Layer 1: Active execution truth
- **來源：** GitHub issue、PR、討論、release notes、Linear 的 issue/專案/文件
- **用途：** 工作目前的實際運作狀態
- **規則：** 如果某件事影響進行中的工程計畫、roadmap、rollout 或 release，優先先放在這裡

### Layer 2: Claude Code Memory (Quick Access)
- **路徑：** `~/.claude/projects/*/memory/`
- **格式：** 帶 frontmatter 的 Markdown 檔案
- **類型：** 使用者偏好、回饋、專案 context、參考資料
- **用途：** 跨對話持續存在的快速存取 context
- **在 session 開始時自動載入**

### Layer 3: MCP Memory Server (Structured Knowledge Graph)
- **存取方式：** MCP 記憶工具（create_entities、create_relations、add_observations、search_nodes）
- **用途：** 對所有已儲存記憶做語意搜尋、建立關係對應
- **跨 session 持久保存，具有可查詢的圖結構**

### Layer 4: Knowledge base repo / durable document store
- **用途：** 整理過的持久筆記、session 匯出、綜合研究、操作者記憶、長篇文件
- **規則：** 當內容不是 repo 擁有的程式碼時，這是跨機器 context 的首選持久儲存

### Layer 5: External Data Store (Supabase, PostgreSQL, etc.)
- **用途：** 結構化資料、大型文件儲存、全文搜尋
- **適合：** 太大而放不進記憶檔案的文件、需要 SQL 查詢的資料

### Layer 6: Local context/archive folder
- **用途：** 給人看的筆記、封存的作戰計畫、本地媒體整理、暫時的非程式碼文件
- **規則：** 可寫入來儲存資訊，但不是影子程式碼工作區
- **不要用在：** 進行中的程式碼變更，或應該放在上游的 repo 事實

## Ingestion Workflow

當需要擷取新知識時：

### 1. Classify
這是哪一種知識？
- 商業決策 -> 記憶檔案（project 類型）+ MCP 記憶
- 進行中的 roadmap / release / 實作狀態 -> 先放 GitHub + Linear
- 個人偏好 -> 記憶檔案（user/feedback 類型）
- 參考資訊 -> 記憶檔案（reference 類型）+ MCP 記憶
- 大型文件 -> 外部資料儲存 + 在記憶中放摘要
- 對話/session -> 知識庫 repo + 在記憶中放簡短摘要

### 2. Deduplicate
檢查這項知識是否已經存在：
- 在記憶檔案裡搜尋既有條目
- 用相關詞彙查詢 MCP 記憶
- 在建立另一份本地筆記之前，先檢查資訊是否已經在 GitHub 或 Linear 裡
- 不要建立重複項目。改為更新既有的條目。

### 3. Store
寫入適當的層：
- 一律更新 Claude Code 記憶，方便快速存取
- 用 MCP 記憶來提供語意搜尋和關係對應
- 當資訊改變了專案的即時事實時，先更新 GitHub / Linear
- 持久的長篇新增內容，commit 到知識庫 repo

### 4. Index
更新任何相關的索引或摘要檔案。

## Sync Operations

### Conversation Sync
定期把對話歷史同步到知識庫：
- 來源：Claude session 檔案、Codex session、其他 agent 的 session
- 目的地：知識庫 repo
- 產生 session 索引，方便快速瀏覽
- Commit 並 push

### Workspace State Sync
把重要的工作區設定和 script 鏡像到知識庫：
- 產生目錄對照圖
- commit 之前先遮蔽敏感設定
- 追蹤隨時間的變化
- 不要把知識庫或封存資料夾當成即時的程式碼工作區

### GitHub / Linear Sync
當資訊影響進行中的執行時：
- 更新相關的 GitHub issue、PR、討論、release notes 或 roadmap 討論串
- 當工作需要持久的規劃 context 時，把輔助文件附加到 Linear
- 只有在本地筆記之後仍有價值時，才事後鏡像一份

### Cross-Source Knowledge Sync
把來自多個來源的知識拉到同一個地方：
- Claude/ChatGPT/Grok 的對話匯出
- 瀏覽器書籤
- GitHub 活動事件
- 寫狀態摘要，commit 並 push

## Memory Patterns

```
# 短期：目前 session 的 context
用 TodoWrite 追蹤 session 內的任務

# 中期：專案記憶檔案
寫到 ~/.claude/projects/*/memory/ 做跨 session 回想

# 長期：GitHub / Linear / KB
把進行中的執行事實放在 GitHub + Linear
把持久、綜合過的 context 放在知識庫 repo

# 語意層：MCP 知識圖
用 mcp__memory__create_entities 存放永久的結構化資料
用 mcp__memory__create_relations 建立關係對應
用 mcp__memory__add_observations 為已知的實體加入新事實
用 mcp__memory__search_nodes 找既有知識
```

## Best Practices

- 記憶檔案要精簡。把舊資料封存，不要讓檔案無限增長。
- 所有知識檔案都用 frontmatter（YAML）放 metadata。
- 儲存之前先去重。先搜尋，再建立或更新。
- 每組事實偏好只有一個權威的存放處。避免同一份計畫在本地筆記、repo 檔案和追蹤工具文件裡有平行的副本。
- commit 到 Git 之前，先遮蔽敏感資訊（API key、密碼）。
- 知識檔案使用一致的命名慣例（小寫 kebab-case）。
- 用主題/分類標記條目，方便檢索。

## Quality Gate

完成任何知識操作之前：
- 沒有建立重複的條目
- 被 Git 追蹤的檔案裡的敏感資料都已遮蔽
- 索引和摘要已更新
- 為該資料類型選了適當的儲存層
- 相關的地方已加上交叉引用
