---
name: skill-scout
description: 在建立新 skill 之前，先搜尋現有的本地、marketplace、GitHub 和網路上的 skill 來源。使用者想為某個工作流程建立、打造、fork 或尋找 skill 時使用。
metadata:
  origin: community
---

# Skill Scout

建立新 skill 之前，先使用這個 skill。目標是避免重複做社群或 marketplace 已經有的東西，同時在採用任何外部東西之前都要先審查。

來源：從已停滯的社群 PR #1232（作者 `redminwang`）搶救而來。

## 何時使用

- 使用者說「create a skill」、「build a skill」、「make a skill」或「new skill」。
- 使用者問「有沒有做 X 的 skill？」或「有沒有能做 Y 的 skill？」
- 使用者描述了一個工作流程，而你正要建議建立新 skill。
- 使用者想 fork 或擴充現有的 skill。

如果使用者明確說要跳過搜尋或從頭建立，就確認收到，然後照他要的建立流程進行。

## 運作方式

### 步驟 1：掌握意圖

擷取：

- 這個 skill 要執行的任務。
- 使用它的觸發條件。
- 涉及的領域、工具、框架或資料來源。
- 三到五個搜尋關鍵字，加上有用的同義詞。

### 步驟 2：搜尋本地來源

先搜尋已安裝的和 marketplace 的 skill 名稱。優先用本地來源，因為它們已經是使用者環境的一部分。

```bash
find ~/.claude/skills -maxdepth 2 -name SKILL.md 2>/dev/null | grep -iE "keyword|synonym"
find ~/.claude/plugins/marketplaces -path '*/skills/*/SKILL.md' 2>/dev/null | grep -iE "keyword|synonym"
```

再搜尋 frontmatter 裡的 description：

```bash
grep -RilE "keyword|synonym" ~/.claude/skills ~/.claude/plugins/marketplaces 2>/dev/null
```

### 步驟 3：搜尋遠端來源

使用可用的 GitHub 和網頁搜尋工具。查詢要簡潔：

```bash
gh search repos "claude code skill keyword" --limit 10 --sort stars
gh search code "name: keyword" --filename SKILL.md --limit 10
```

網頁搜尋最多用三個針對性的查詢，例如：

```text
"claude code skill" keyword
"SKILL.md" keyword
"affaan-m/ECC" keyword
```

### 步驟 4：審查外部符合項目

在建議採用或 fork 任何外部 skill 之前：

- 讀 `SKILL.md` 的 frontmatter 和指示。
- 找有沒有意料之外的 shell 指令、檔案寫入、網路呼叫、憑證處理或套件安裝。
- 檢查這個 repository 看起來有沒有在維護。
- 優先複製到全新的本地 branch 再審查 diff，不要直接編輯 marketplace 的原件。

### 步驟 5：排序結果

依這個順序為候選項目排名：

1. skill 名稱中的關鍵字完全吻合。
2. description 中的關鍵字或同義詞吻合。
3. 本地已安裝或 marketplace 來源。
4. 有近期活動、有在維護的 GitHub 來源。
5. 只有網頁提到。

最後的清單上限為 10 筆。

### 步驟 6：提出決策選項

給使用者一張簡短的表：

| 選項 | 意義 |
| --- | --- |
| Use existing | 直接呼叫或安裝符合的 skill。 |
| Fork or extend | 複製最接近的 skill 再修改。 |
| Create fresh | 確認沒有接近的符合項目後，建立新 skill。 |

只有在使用者選了那條路，或搜尋後找不到接近的符合項目時，才建立新 skill。

## 範例

### 結果表

```markdown
| # | Skill | Source | Why it matches | Gap |
| --- | --- | --- | --- | --- |
| 1 | article-writing | Local ECC | Drafts articles and guides | Not focused on release notes |
| 2 | content-engine | Local ECC | Multi-format content workflow | Heavier than needed |
| 3 | blog-writer | GitHub | Blog writing skill with recent commits | Needs security review |
```

### 給使用者看的摘要

```markdown
I found two close local matches and one external candidate. The closest fit is
`article-writing`; it covers drafting and revision, but it does not include the
release-note checklist you asked for. I can either use it as-is, fork it into a
release-note variant, or create a fresh skill.
```

## 反模式

- 搜尋是合理的做法時，不要直接跳去建立新 skill。
- 沒讀過外部 skill 就不要安裝。
- 不要丟出一長串沒排序的弱符合項目。
- 不要把只有網頁提到的來源當成可信來源。
- 不要直接編輯已安裝的 marketplace 原件。

## 相關

- `search-first`：通用的「先搜尋再動手建」工作流程。
- `skill-stocktake`：稽核已安裝 skill 的健康度、重複和缺口。
- `agent-sort`：分類並整理現有的 agent 和 skill。
