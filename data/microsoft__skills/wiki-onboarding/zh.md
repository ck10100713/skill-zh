---
name: wiki-onboarding
description: 在 onboarding/ 資料夾產生四份針對不同對象的 onboarding 指南：Contributor、Staff Engineer、Executive 和 Product Manager。適用於使用者想要程式碼庫的 onboarding 文件時。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Wiki Onboarding 指南產生器

在 `onboarding/` 資料夾產生四份針對不同對象的 onboarding 文件，讓每位不同的利害關係人，都剛好得到他們需要的理解。

## 解析來源 Repository（一定要先做）

產生任何指南之前，你一定要先確定來源 repository 的背景：

1. **檢查 git remote**：執行 `git remote get-url origin` 偵測是否有 remote
2. **問使用者**：_"這是只在本機的 repository，還是你有來源 repository 的 URL（例如 GitHub、Azure DevOps）？"_
   - 有提供遠端 URL → 存成 `REPO_URL`，使用**帶連結的引用**：`[file:line](REPO_URL/blob/BRANCH/file#Lline)`
   - 只在本機 → 使用**本機引用**：`(file_path:line_number)`
3. **決定預設 branch**：執行 `git rev-parse --abbrev-ref HEAD`
4. 來源 repo 的背景沒解析清楚之前，**不准繼續**

## 什麼時候啟動

- 使用者要 onboarding 文件或 getting-started 指南
- 使用者執行 `/deep-wiki:onboard` 指令
- 使用者想幫助新的團隊成員理解程式碼庫

## 輸出結構

產生一個 `onboarding/` 資料夾，包含這些檔案：

```
onboarding/
├── index.md                    # Onboarding hub — links to all 4 guides with audience descriptions
├── contributor-guide.md        # For new contributors (assumes Python or JS background)
├── staff-engineer-guide.md     # For staff/principal engineers
├── executive-guide.md          # For VP/director-level engineering leaders
└── product-manager-guide.md    # For product managers and non-engineering stakeholders
```

### `index.md`：Onboarding Hub

一個登陸頁，包含：
- **一段專案摘要**
- **指南選擇表**：

| 指南 | 對象 | 你會學到什麼 | 時間 |
|-------|----------|-------------------|------|
| [Contributor Guide](./contributor-guide.md) | 有 Python/JS 經驗的新貢獻者 | 設定、第一個 PR、程式碼庫的模式 | 約 30 分鐘 |
| [Staff Engineer Guide](./staff-engineer-guide.md) | Staff/principal 工程師 | 架構、設計決策、系統邊界 | 約 45 分鐘 |
| [Executive Guide](./executive-guide.md) | VP/工程總監 | 能力、風險、團隊拓撲、投資論點 | 約 20 分鐘 |
| [Product Manager Guide](./product-manager-guide.md) | 產品經理 | 功能、使用者旅程、限制、資料模型 | 約 20 分鐘 |

## 語言偵測

掃描 repository 的 build 檔案，決定程式碼範例要用的主要語言：
- `package.json` / `tsconfig.json` → TypeScript/JavaScript
- `*.csproj` / `*.sln` → C# / .NET
- `Cargo.toml` → Rust
- `pyproject.toml` / `setup.py` / `requirements.txt` → Python
- `go.mod` → Go
- `pom.xml` / `build.gradle` → Java

---

## 指南 1：Contributor Guide

**檔案**：`onboarding/contributor-guide.md`
**對象**：加入專案的工程師。假設他精通 Python 或 JavaScript，並有一般的軟體工程經驗。
**長度**：1000 到 2500 行。循序漸進，每個段落都建立在前一段之上。

### 必要段落

**第一部分：基礎**（如果 repo 用的是 Python 或 JS 就跳過）
1. **給 Python/JS 工程師的 {Primary Language}**：語法比較表、async 模型、collection、型別系統、套件管理。要並排的具體程式碼，**不是**抽象的描述。
2. **{Primary Framework} 重點**：和對等的 Python/JS framework 比較（例如 FastAPI、Express）。Request pipeline、路由、DI、設定。

**第二部分：這個程式碼庫**
3. **這個專案做什麼**：2 到 3 句話的電梯簡報
4. **專案結構**：加上註解的目錄樹（什麼東西放哪裡、為什麼）。包含 `graph TB` 的架構概觀。
5. **核心概念**：領域專屬的術語，搭配程式碼範例說明。資料模型用 `erDiagram`。
6. **Request 生命週期**：用 `sequenceDiagram`（帶 `autonumber`）追蹤一個典型的 request 從頭到尾。
7. **關鍵模式**：「如果你想加 X，照這個模式」的範本，附上真實程式碼

**第三部分：開始上手**
8. **前置條件與設定**：表格：工具、版本、安裝指令。逐步說明，每一步都附上預期輸出。
9. **你的第一個任務**：從頭到尾示範加一個簡單的功能
10. **開發流程**：Branch 策略、commit 慣例、PR 流程。用 `flowchart` 圖表。
11. **執行測試**：全部測試、單一檔案、單一測試、coverage 的指令
12. **除錯指南**：常見問題表：症狀、原因、修法
13. **常見陷阱**：每個新貢獻者都會犯的錯，以及如何避免

**附錄**
- **詞彙表**（40 個以上術語）
- **關鍵檔案參考**：表格：路徑、用途、為什麼重要、來源
- **快速參考卡**：最常用指令和模式的小抄

### 規則
- 所有程式碼範例都用偵測到的主要語言
- 每個指令都必須能直接複製貼上，並附上預期輸出
- **至少 5 張 Mermaid 圖**（架構、ER、sequence、flowchart、state）
- 工作流程圖用 Mermaid（深色模式的顏色），並在每張圖後面加上 `<!-- Sources: ... -->` 註解區塊
- 所有論點都要以實際程式碼為依據，用帶連結的格式引用

---

## 指南 2：Staff Engineer Guide

**檔案**：`onboarding/staff-engineer-guide.md`
**對象**：需要知道每個決策「為什麼」的 staff/principal 工程師。有深厚的系統經驗，但可能不熟這個 repo 的語言。
**長度**：800 到 1200 行。內容密集、有立場、偏架構。

### 必要段落

1. **Executive Summary**：用一段密集的文字說明系統是什麼。它自己負責什麼、委派什麼。
2. **核心架構洞見**：**唯一**最重要的概念。要包含一段用和 repo **不同**語言寫的 pseudocode。
3. **系統架構**：完整的 Mermaid `graph TB` 圖。標出系統的「核心」。
4. **領域模型**：核心實體的 Mermaid `erDiagram`。資料不變量表：實體、不變量、由誰強制、來源。
5. **關鍵抽象與介面**：用 `classDiagram` 呈現承重的抽象。
6. **Request 生命週期**：用 `sequenceDiagram`（帶 `autonumber`）呈現典型 request 從進入到回應。
7. **狀態轉換**：對有重要生命週期狀態的實體，用 `stateDiagram-v2`。
8. **決策記錄**：表格：決策、考慮過的替代方案、理由、來源。
9. **相依套件的理由**：表格：相依套件、用途、取代了什麼、來源。
10. **資料流與狀態**：資料如何在系統中流動。儲存方式比較表。
11. **失敗模式與錯誤處理**：用 `flowchart` 呈現錯誤傳遞路徑。
12. **效能特性**：瓶頸、擴展上限、熱點路徑。
13. **安全模型**：驗證、授權、信任邊界、資料敏感度。
14. **測試策略**：測了什麼、沒測什麼、測試哲學。
15. **已知技術債**：表格：問題、風險等級、受影響的檔案、來源。
16. **要深入看哪裡**：建議的原始碼閱讀順序，以及 wiki 段落的連結。

### 規則
- 用**另一種語言的 pseudocode** 來解釋概念
- 用**比較表**對應不熟悉的概念（例如 `Task<T>` = `Awaitable[T]`）
- 用表格搭配密集的文字，**不要**用淺薄的條列
- 每個論點都要有帶連結的引用佐證
- **至少 5 張 Mermaid 圖**（架構、ER、class、sequence、state、flowchart）
- 每張圖後面都要加 `<!-- Sources: ... -->` 註解區塊
- **積極用表格**：決策、相依套件、技術債**全部**都要是帶 Source 欄的表格
- 重點放在決策**為什麼**這樣做，不只是**有什麼**

---

## 指南 3：Executive Guide

**檔案**：`onboarding/executive-guide.md`
**對象**：VP/工程總監。需要能力概觀、風險評估和投資背景，**不需要**程式碼層級的細節。
**長度**：400 到 800 行。策略性、簡潔、以決策為導向。

### 必要段落

1. **系統概觀**：它做什麼、誰在用、用 2 到 3 句話說明商業價值
2. **能力地圖**：表格：能力、狀態（Built/Partial/Planned）、成熟度、相依性。系統今天能做什麼、不能做什麼。
3. **架構一覽**：高層次的 Mermaid `graph LR` 圖。服務、資料儲存、外部整合，**不放**內部程式碼細節。聚焦在 deployment 單位和團隊邊界。
4. **團隊拓撲**：哪個團隊/人負責哪些元件。表格：元件、負責人、關鍵程度、Bus Factor。
5. **技術投資論點**：為什麼選這些技術。表格：技術、用途、考慮過的替代方案、風險等級。
6. **風險評估**：表格：風險、可能性、影響、緩解方式、負責人。涵蓋可靠性、安全、擴展性、合規。
7. **成本與擴展模型**：成本如何隨使用量成長。瓶頸是什麼。下一次擴展投資什麼時候需要。
8. **相依性地圖**：用 `graph TB` 呈現關鍵的外部相依。表格：相依、類型（Service/Library/Platform）、無法使用時的風險。
9. **關鍵指標與可觀測性**：量測了什麼、有哪些 dashboard、警報覆蓋率。表格：指標、目前的值、目標、來源。
10. **Roadmap 一致性**：把工程工作流對應到商業優先順序。進行中的、規劃中的、被卡住的。
11. **技術債摘要**：前 5 大債務項目及其商業影響。表格：問題、商業影響、修復工時、優先順序。
12. **建議**：下一季 3 到 5 項可執行的建議，依影響排序。

### 規則
- **不放程式碼片段**：這份指南是給工程主管看的，不是給寫程式的人
- **圖表停在服務/團隊層級**，不要到 class/function 層級
- **每個論點都要有證據佐證**：引用 wiki 段落、架構文件或原始檔案
- **至少 3 張 Mermaid 圖**（架構概觀、相依性地圖、能力/roadmap）
- 每個結構化的發現都用表格，這類讀者看的是表格，不是散文
- **用商業語言**：把技術概念翻成影響（可靠性、速度、成本、風險）

---

## 指南 4：Product Manager Guide

**檔案**：`onboarding/product-manager-guide.md`
**對象**：產品經理和非工程的利害關係人。需要理解系統做什麼、有哪些可能性、邊界在哪裡，**不需要**知道它怎麼建的。
**長度**：400 到 800 行。以使用者為中心、聚焦功能、注意限制。

### 必要段落

1. **這個系統做什麼**：用面向使用者的語言（不用術語）寫 2 到 3 句話的電梯簡報
2. **使用者旅程地圖**：用 Mermaid `graph LR` 或 `journey` 圖，呈現使用者在系統中的主要流程
3. **功能能力地圖**：表格：功能、狀態（Live/Beta/Planned/Not Possible）、面向使用者的行為、限制。做了什麼和沒做什麼的完整地圖。
4. **資料模型（產品視角）**：簡化的 Mermaid `erDiagram`，呈現使用者會接觸的實體。用商業語言解釋（例如「一個 Project 有很多 Document」，而不是「FK 關聯」）。
5. **設定與 Feature Flag**：表格：Flag/設定、控制什麼、預設值、誰可以改。哪些不需要工程介入就能切換。
6. **API 能力**：有哪些整合是可能的。表格：能力、Endpoint/方法、驗證方式、Rate limit。為整合夥伴而寫，不是為開發者。
7. **效能與 SLA**：回應時間、吞吐量上限、可用性目標。表格：操作、預期延遲、吞吐量上限、目前的 SLA。
8. **已知限制與約束**：誠實列出系統做不到或做得不好的事。表格：限制、對使用者的影響、替代做法、規劃中的修正。
9. **資料與隱私**：蒐集什麼資料、存在哪裡、保存政策、合規狀態。表格：資料類型、儲存位置、保存期限、合規。
10. **詞彙表**：用白話解釋領域術語（不用工程術語）
11. **FAQ**：10 個以上 PM 常問的問題，簡潔回答

### 規則
- **完全不用工程術語**：不要出現「middleware」、「dependency injection」、「ORM」。用白話。
- **以使用者為中心的敘述**：所有東西都用使用者體驗到什麼來描述，不是程式碼怎麼運作
- **至少 3 張 Mermaid 圖**（使用者旅程、資料模型、功能地圖/能力概觀）
- 每個結構化的發現都用表格，PM 看的是表格，不是散文
- 如果一定要提到技術概念，用一句話解釋（例如「Feature flag：讓我們不用 deploy 程式碼就能開關功能的開關」）
- 每個論點都要有證據佐證，引用 wiki 段落或原始檔案以供驗證

---

## Mermaid 圖表規則（所有指南）

所有圖表都必須用深色模式的顏色：
- Node 填色：`#2d333b`，邊框：`#6d5dfc`，文字：`#e6edf3`
- Subgraph 背景：`#161b22`，邊框：`#30363d`
- 線條：`#8b949e`
- 如果用 inline 的 `style` directive，要用深色填色並加上 `,color:#e6edf3`
- Mermaid label 裡**不要**用 `<br/>`（用 `<br>` 或換行）

## 驗證

每份指南產生之後，驗證：
- 提到的所有檔案路徑在 repo 裡確實存在
- 所有 class/method 名稱都正確（不是幻覺出來的）
- Mermaid 圖表能渲染（沒有語法錯誤）
- code fence 以外沒有裸露的類 HTML 標籤（像 `List<T>` 這樣的泛型），要用反引號包起來
- 每份指南都適合它的對象，Executive/PM 指南裡不能有程式碼
