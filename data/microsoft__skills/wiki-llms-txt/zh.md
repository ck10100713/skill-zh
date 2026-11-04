---
name: wiki-llms-txt
description: 依照 llms.txt 規格，產生 llms.txt 和 llms-full.txt 檔案，讓專案文件對 LLM 友善。適用於使用者想建立 LLM 可讀的摘要、llms.txt 檔案，或讓 wiki 能被語言模型存取時。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# llms.txt 產生器

依照 [llms.txt 規格](https://llmstxt.org/)，產生 `llms.txt` 和 `llms-full.txt` 檔案，讓 LLM 能友善地存取 wiki 文件。

## 這個 Skill 什麼時候啟動

- 使用者要求產生 `llms.txt`，或提到 llms.txt 標準
- 使用者想讓文件「對 LLM 友善」或「LLM 可讀」
- 使用者要一份給語言模型用的專案摘要檔
- 使用者提到 `llms-full.txt` 或展開 context 的文件

## 解析來源 Repository（一定要先做）

產生之前，先解析來源 repository 的背景：

1. **檢查 git remote**：執行 `git remote get-url origin`
2. **問使用者**：_"這是只在本機的 repository，還是你有來源 repository 的 URL？"_
   - 有遠端 URL → 存成 `REPO_URL`
   - 只在本機 → 只用相對路徑
3. **決定預設 branch**：執行 `git rev-parse --abbrev-ref HEAD`
4. 沒解析清楚之前，**不准繼續**

## llms.txt 格式（符合規格）

檔案遵循 [llms.txt 規格](https://llmstxt.org/)：

```markdown
# {Project Name}

> {Dense one-paragraph summary — what it does, who it's for, key technologies}

{Important context paragraphs — constraints, architectural philosophy, non-obvious things}

## {Section Name}

- [{Page Title}]({relative-path-to-md}): {One-sentence description of what the reader will learn}

## Optional

- [{Page Title}]({relative-path-to-md}): {Description — these can be skipped for shorter context}
```

### 關鍵規則

1. **H1**：專案名稱（剛好一個，必要）
2. **Blockquote**：密集、具體的摘要（必要）。一定要是**這個**專案獨有的。
3. **Context 段落**：不明顯的限制，以及不特別告訴 LLM 它就會搞錯的事
4. **H2 段落**：依主題組織，每個都有一串 `[Title](url): Description` 的項目
5. **「Optional」H2**：有特殊意義，這裡的連結可以跳過，以縮短 context
6. **相對連結**：所有路徑都相對於 wiki 目錄
7. **動態**：**所有**內容都從實際的 wiki 頁面推導，不是範本
8. **段落順序**：最重要的放前面：Onboarding → Architecture → Getting Started → Deep Dive → Optional

### 描述的品質

| ❌ 差 | ✅ 好 |
|--------|---------|
| "Architecture overview" | "System architecture showing how Orleans grains communicate via message passing with at-least-once delivery" |
| "Getting started guide" | "Prerequisites, local dev setup with Docker Compose, and first API call walkthrough" |
| "The API reference" | "REST endpoints with auth requirements, rate limits, and request/response schemas" |

## llms-full.txt 格式

結構和 `llms.txt` 相同，但把完整內容 inline 進來：

```markdown
# {Project Name}

> {Same summary}

{Same context}

## {Section Name}

<doc title="{Page Title}" path="{relative-path}">
{Full markdown content — frontmatter stripped, citations and diagrams preserved}
</doc>
```

### Inline 規則

- 每個頁面都要**移除 YAML frontmatter**（`---` 區塊）
- **保留 Mermaid 圖表**：維持 `` ```mermaid `` fence 完整
- **保留引用**：所有 `[file:line](URL)` 連結原樣保留
- **保留表格**：所有 markdown 表格維持完整
- **保留 `<!-- Sources: -->` 註解**：這些提供圖表的出處

## 前置條件

當 wiki 頁面已經存在時（透過 `/deep-wiki:generate` 或 `/deep-wiki:page`），這個 skill 效果最好。如果還沒有 wiki：

1. 建議先執行 `/deep-wiki:generate`
2. 或是從 README + 原始碼掃描產生一份最精簡的 `llms.txt`（不含 wiki 頁面連結）

## 輸出檔案

產生三個檔案：

| 檔案 | 用途 | 可發現性 |
|------|---------|-----------------|
| `./llms.txt` | 根目錄的探索檔 | 依 llms.txt 規格的標準路徑。GitHub MCP 的 `get_file_contents` 和 `search_code` 會先找到這個。 |
| `wiki/llms.txt` | Wiki 相對連結 | 用於 VitePress deployment 和 wiki 內部導覽。 |
| `wiki/llms-full.txt` | 完整 inline 的內容 | 給需要把所有文件放在同一個檔案的 agent 的完整參考。 |

根目錄的 `./llms.txt` 連到 `wiki/` 裡（例如 `[Guide](./wiki/onboarding/contributor-guide.md)`）。`wiki/llms.txt` 使用 wiki 相對路徑（例如 `[Guide](./onboarding/contributor-guide.md)`）。

如果根目錄的 `llms.txt` 已經存在，而且**不是**由 deep-wiki 產生的，就不要覆蓋它。

## 驗證檢查清單

完成之前：

- [ ] `llms.txt` 裡所有連結的檔案都真的存在
- [ ] `llms-full.txt` 裡所有 `<doc>` 區塊都有真實內容（不是空的）
- [ ] Blockquote 是這個專案獨有的（不是通用的制式內容）
- [ ] 段落依重要性排序
- [ ] 各段落之間沒有重複的頁面項目
- [ ] 「Optional」段落只放真正選用的內容
- [ ] `llms.txt` 簡潔（1 到 5 KB）
- [ ] `llms-full.txt` 包含所有 wiki 頁面
