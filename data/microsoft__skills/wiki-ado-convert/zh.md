---
name: wiki-ado-convert
description: 把 VitePress/GFM 的 wiki markdown 轉成相容於 Azure DevOps Wiki 的格式。產生一個 Node.js build script，轉換 Mermaid 語法、移除 front matter、修正連結，並把相容 ADO 的副本輸出到 dist/ado-wiki/。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# ADO Wiki 轉換器

產生一個 Node.js build script，把 VitePress/GFM 的 markdown 文件轉成相容於 Azure DevOps Wiki 的格式。原始檔案完全不動，script 會把轉換後的副本放到 `dist/ado-wiki/`。

## 解析來源 Repository（一定要先做）

產生 build script 之前，先解析來源 repository 的背景：

1. **檢查 git remote**：執行 `git remote get-url origin`
2. **問使用者**：_"這是只在本機的 repository，還是你有來源 repository 的 URL？"_
   - 有遠端 URL → 存成 `REPO_URL`，在轉換後的輸出裡保留帶連結的引用
   - 只在本機 → 原樣保留本機的引用
3. 沒解析清楚之前**不准繼續**

## 為什麼需要這個

Azure DevOps Wiki 用的 markdown 方言，在幾個關鍵地方和 GFM、VitePress 不一樣。在 VitePress 裡渲染得很好的文件，發佈成 ADO Wiki 之後，會出現圖表壞掉、露出原始 front matter、死連結和渲染問題。

## ADO Wiki 不相容的地方

### 嚴重：會讓渲染壞掉

| 問題 | VitePress/GFM | ADO Wiki | 修法 |
|-------|--------------|----------|-----|
| Mermaid code fence | ` ```mermaid ` ... ` ``` ` | `::: mermaid` ... `:::` | 轉換開頭/結尾的 fence |
| `flowchart` 關鍵字 | `flowchart TD` | `graph TD` | 把 `flowchart` 換成 `graph`（保留方向） |
| Mermaid label 裡的 `<br>` | `Node[Label<br>Text]` | 不支援 | 移除 `<br>` 的各種寫法（換成空格） |
| 長箭頭 `---->` | `A ---->B` | 不支援 | 換成 `-->` |
| YAML front matter | 檔案開頭的 `---` ... `---` | 會被渲染成看得到的原始文字 | 整個移除 |
| 往上層的相對原始碼連結 | `[text](../../src/file.cs)` | 壞掉（wiki 是獨立的） | 轉成純文字 |
| VitePress 的 container directive | `::: tip` / `::: warning` | 不支援 | 轉成 ADO 的 alert blockquote `> [!TIP]` / `> [!WARNING]` |

### 中等：可能渲染得不是最理想

| 問題 | 備註 |
|-------|-------|
| Mermaid `style` directive | ADO 的 Mermaid 版本可能會忽略 inline 樣式。維持原樣（只是外觀）。 |
| Mermaid 粗箭頭 `==>` | 可能可以用。維持原樣。 |
| Mermaid 虛線箭頭 `-.->` | 可能可以用。維持原樣。 |
| Subgraph 連結 | 不支援連到/來自 subgraph 的連結，但 subgraph 裡面的 node 運作正常。 |

### 不是問題（直接相容）

- ✅ 標準的 markdown 表格、blockquote、水平線
- ✅ Unicode emoji、帶語言標記的 fenced code block
- ✅ 同目錄的相對連結（`./other-page.md`）
- ✅ 外部 HTTP/HTTPS 連結
- ✅ 粗體、斜體、刪除線、行內 code
- ✅ 清單（有序、無序、巢狀）、1 到 6 級標題
- ✅ 用相對路徑的圖片

## ADO Wiki 支援的 Mermaid 圖表類型

截至 2025 年：
- ✅ `sequenceDiagram`、`gantt`、`graph`（**不是** `flowchart`）、`classDiagram`
- ✅ `stateDiagram`、`stateDiagram-v2`、`journey`、`pie`、`erDiagram`
- ✅ `requirementDiagram`、`gitGraph`、`timeline`
- ❌ `mindmap`、`sankey`、`quadrantChart`、`xychart`、`block`

## Build Script 結構

產生的 script 應該是 **Node.js ESM module**（`scripts/build-ado-wiki.js`），只用內建的 Node.js module（`node:fs/promises`、`node:path`、`node:url`）。沒有外部相依。

### 轉換函式

#### 1. 移除 YAML Front Matter

移除檔案開頭用 `---` 包起來的 YAML 區塊。ADO 會把它們渲染成看得到的文字。

```javascript
function stripFrontMatter(content) {
  if (!content.startsWith('---')) return content;
  const endIndex = content.indexOf('\n---', 3);
  if (endIndex === -1) return content;
  let rest = content.slice(endIndex + 4);
  if (rest.startsWith('\n')) rest = rest.slice(1);
  return rest;
}
```

#### 2. 轉換 Mermaid 區塊

逐行處理，追蹤 mermaid 區塊的狀態。修正**只**套用在 mermaid 區塊裡面：

- 開頭：` ```mermaid ` → `::: mermaid`
- 結尾：` ``` ` → `:::`
- `flowchart` → `graph`（保留方向：TD、LR、TB、RL、BT）
- 移除 `<br>`、`<br/>`、`<br />`（換成空格）
- 把長箭頭（`---->`，4 個以上的連字號）換成 `-->`

```javascript
function convertMermaidBlocks(content) {
  const lines = content.split('\n');
  const result = [];
  let inMermaid = false;

  for (const line of lines) {
    const trimmed = line.trimEnd();

    if (!inMermaid && /^```mermaid\s*$/.test(trimmed)) {
      result.push('::: mermaid');
      inMermaid = true;
      continue;
    }

    if (inMermaid && /^```\s*$/.test(trimmed)) {
      result.push(':::');
      inMermaid = false;
      continue;
    }

    if (inMermaid) {
      let fixed = line;
      fixed = fixed.replace(/^(\s*)flowchart(\s+)/, '$1graph$2');
      fixed = fixed.replace(/<br\s*\/?>/gi, ' ');
      fixed = fixed.replace(/-{4,}>/g, '-->');
      result.push(fixed);
    } else {
      result.push(line);
    }
  }

  return result.join('\n');
}
```

#### 3. 轉換往上層的相對原始碼連結

把 `[text](../path)` 轉成純文字。同目錄的 `.md` 連結和外部 URL 會保留。

```javascript
function convertSourceLinks(content) {
  return content.replace(
    /\[([^\]]*)\]\(\.\.\/[^)]*\)/g,
    (match, linkText) => linkText
  );
}
```

#### 4. 轉換 VitePress Container Directive（選用）

把 `::: tip` / `::: warning` / `::: danger` 轉成 ADO 的 alert blockquote：

```javascript
function convertContainerDirectives(content) {
  // ::: tip → > [!TIP]
  // ::: warning → > [!WARNING]
  // ::: danger → > [!CAUTION]
  // ::: info → > [!NOTE]
  // closing ::: → (blank line)
}
```

### Script 主流程

```javascript
async function main() {
  const files = await collectMarkdownFiles(ROOT);
  const stats = { frontMatter: 0, mermaid: 0, sourceLinks: 0, containers: 0 };

  for (const filePath of files) {
    let content = await readFile(filePath, 'utf-8');
    content = stripFrontMatter(content);
    content = convertMermaidBlocks(content);
    content = convertSourceLinks(content);

    const outPath = join(OUTPUT, relative(ROOT, filePath));
    await mkdir(dirname(outPath), { recursive: true });
    await writeFile(outPath, content, 'utf-8');
  }

  // Print transformation statistics
}
```

### 跳過的目錄

Script 應該跳過：`node_modules`、`.vitepress`、`.git`、`dist`、`build`、`out`、`target`，以及任何非文件的目錄。

### npm Script 整合

```json
{
  "scripts": {
    "build:ado": "node scripts/build-ado-wiki.js"
  }
}
```

## 驗證檢查清單

Script 跑完之後，驗證：
1. `dist/ado-wiki/` 的檔案數量和來源相符（扣掉跳過的目錄）
2. 剩下 0 個 ` ```mermaid ` fence，全部都轉成 `::: mermaid`
3. 剩下 0 個 `flowchart` 關鍵字，全部都轉成 `graph`
4. 輸出檔案裡沒有 YAML front matter
5. 往上層的相對連結已經轉成純文字
6. 同目錄的 `.md` 連結有保留
7. 目錄結構有保留
8. 非 markdown 檔案（圖片等）原樣複製
9. 根目錄的 `index.md` 是正確的 wiki 首頁（**不是** placeholder）

## 首頁產生（關鍵）

ADO Wiki 的 `index.md` **一定要是正確的 wiki 登陸頁**，不能是帶有「TODO」文字的通用 placeholder。

### 邏輯

1. **如果 VitePress 來源有 `index.md`**：轉換它（移除 front matter、移除 VitePress 的 hero/features 區塊）。如果還有實質內容，就用它。
2. **如果沒有實質內容了**（移除後是空的，或只剩 VitePress 的 hero 標記）：產生一個正確的登陸頁，包含：
   - 專案標題當作 `# heading`
   - 概觀段落（來自 README 或 wiki 概觀頁面）
   - 快速導覽表格（Section、Description 欄位，連到 wiki 各章節）
   - 如果有 onboarding 指南，附上連結
3. **絕對不要留下 placeholder**：如果 `index.md` 含有「TODO:」、「Give a short introduction」或類似的 placeholder 文字，要**整個換掉**

### ADO Wiki 的 `.order` 檔案

在每個目錄產生 `.order` 檔案來控制側邊欄順序：
- 先放 onboarding 指南，再放編號的章節
- 列出不含 `.md` 副檔名的頁面名稱，一行一個

## 引用與圖表的保留

轉換後的 ADO wiki 必須維持同樣的品質標準：

- **帶連結的引用**（`[file:line](URL)`）是標準 markdown，原樣保留
- Mermaid 圖表後面的 **`<!-- Sources: ... -->` 註解區塊**：保留（HTML 註解在 ADO 可以用）
- **帶「Source」欄的表格**：原樣保留（標準 markdown 表格）
- **Mermaid 圖表**：只轉換 fence，圖表的內容、類型和結構都保留
- ADO 支援的所有 Mermaid 圖表類型（graph、sequenceDiagram、classDiagram、stateDiagram、erDiagram 等）都原樣通過

## 重要備註

- **絕對不會修改來源檔案**，只動 `dist/ado-wiki/` 裡的副本
- **圖片也要複製**：如果來源有圖片，用相同的相對路徑複製
- Script 應該能用於**任何 VitePress wiki**，不只這個特定的
- 結尾要印出統計，顯示每種轉換類型的數量
- Script 零外部相依，只用 Node.js 內建模組
