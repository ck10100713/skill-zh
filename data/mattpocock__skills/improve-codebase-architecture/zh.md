---
name: improve-codebase-architecture
description: 掃描 codebase 找出可以加深的機會，用視覺化的 HTML 報告呈現，再針對你選的那一項進行 grilling。
disable-model-invocation: true
---

# 改善 Codebase 架構

找出架構上的摩擦，並提出**加深的機會（deepening opportunities）**：把淺模組變成深模組的重構。目標是好測試、好讓 AI 導覽。

這個指令會參考專案的領域模型，並建立在共用的設計詞彙之上：

- 用 Skill 工具呼叫 "codebase-design" 取得架構詞彙（**module**、**interface**、**depth**、**seam**、**adapter**、**leverage**、**locality**）和它的原則（刪除測試、「介面就是測試表面」、「一個 adapter = 假設性的 seam，兩個才是真的」）。每一條建議都要照原意使用這些術語，不要滑到「component」「service」「API」或「boundary」。
- `GLOSSARY.md` 裡的領域語言會幫好的 seam 命名；`docs/adr/` 裡的 ADR 記錄了這個指令不該重新爭論的決策。

## 流程

### 1. 探索

**掃描之前先界定範圍：YAGNI。** 加深一個 module 的回報，是讓之後對它的改動更容易，所以要把比較多的注意力放在 codebase 近期有改動的部分。看之前先決定*要看哪裡*：

- 如果使用者指了方向（某個 module、某個子系統、某個痛點），就照做，跳過下面的推論。
- 否則，往回翻一大段 commit 歷史（`git log --oneline`）找 codebase 的熱點，也就是一直出現的檔案和區域，讓這些路徑先吸引你的注意。如果改動很分散、沒有明顯的熱點，就把網撒大一點。

先讀專案的領域詞彙表（`GLOSSARY.md`）和你要動的那一區的任何 ADR。

然後啟動一個有全新 context window 的 sub-agent 去走過 codebase。不要照僵硬的啟發法；自然地探索，並記下你在哪裡感到摩擦：

- 哪裡要理解一個概念，得在很多小 module 之間跳來跳去？
- 哪裡的 module 很**淺**，介面幾乎跟實作一樣複雜？
- 哪裡為了好測試而抽出了純函式，但真正的 bug 藏在它們怎麼被呼叫（沒有 **locality**）？
- 哪裡緊耦合的 module 越過了它們的 seam 而外洩？
- codebase 的哪些部分沒有測試，或是透過現在的介面很難測試？

對任何你懷疑很淺的東西套用**刪除測試**：刪掉它會讓複雜度集中，還是只是搬家？「會，集中了」就是你要的訊號。

### 2. 用 HTML 報告呈現候選項

把一個獨立（self-contained）的 HTML 檔寫到作業系統的暫存目錄，這樣 repo 裡不會多出東西。從 `$TMPDIR` 解析暫存目錄，沒有就退回 `/tmp`（Windows 是 `%TEMP%`），寫到 `<tmpdir>/architecture-review-<timestamp>.html`，讓每次執行都是新檔。幫使用者打開它（Linux 用 `xdg-open <path>`，macOS 用 `open <path>`，Windows 用 `start <path>`），並告訴他絕對路徑。

報告用 **Tailwind（透過 CDN）** 做版面和樣式，用 **Mermaid（透過 CDN）** 畫圖，適用在圖形/流程/時序能可靠傳達結構的地方。Mermaid 要跟手工做的 CSS/SVG 視覺搭配：關係是圖形狀的時候（呼叫圖、依賴、時序）用 Mermaid，想要更有編輯感的東西時（質量圖、剖面圖、塌縮動畫）就用手工的 div/SVG。每個候選項都要有**前後對照的視覺化**。要視覺化。

每個候選項都渲染成一張卡片，包含：

- **Files**：涉及哪些檔案/module
- **Problem**：為什麼現在的架構造成摩擦
- **Solution**：用白話描述會改什麼
- **Benefits**：用 locality 和 leverage 來解釋，並說明測試會怎麼改善
- **Before / After diagram**：並排、自己手繪，說明淺的狀況和加深的結果
- **Recommendation strength**：`Strong`、`Worth exploring`、`Speculative` 三選一，用徽章呈現

報告最後加一節 **Top recommendation**：你會先處理哪個候選項，以及為什麼。

**領域用 GLOSSARY.md 的詞彙，架構用 `/codebase-design` 的詞彙。** 如果 `GLOSSARY.md` 定義了「Order」，就說「Order intake module」，不要說「FooBarHandler」，也不要說「Order service」。

**ADR 衝突**：如果候選項跟既有的 ADR 矛盾，只有在摩擦嚴重到值得重新檢討那份 ADR 時才拿出來。在卡片上清楚標示（例如用警告 callout：_「contradicts ADR-0007, but worth reopening because…」_）。不要把 ADR 禁止的每一個理論上的重構都列出來。

完整的 HTML 骨架、圖表模式和樣式指引見 [HTML-REPORT.md](HTML-REPORT.md)。

現在**不要**提議介面。檔案寫好之後，問使用者：「Which of these would you like to explore?」

### 3. Grilling 迴圈

使用者選好候選項之後，用 Skill 工具呼叫 "grilling"，跟他一起走過決策樹：限制、依賴、加深後 module 的形狀、seam 後面放什麼、哪些測試可以留下來。

決策一成形，副作用就當場發生；用 Skill 工具呼叫 "domain-modeling"，隨時讓領域模型保持最新：

- **用 `GLOSSARY.md` 裡沒有的概念幫加深後的 module 命名？** 把這個術語加進 `GLOSSARY.md`。檔案不存在就延遲建立。
- **對話中磨利了一個模糊的術語？** 當場更新 `GLOSSARY.md`。
- **使用者用有承重作用的理由否決了候選項？** 提議寫 ADR，話術是：_「Want me to record this as an ADR so future architecture reviews don't re-suggest it?」_ 只有當未來的探索者真的需要這個理由來避免重複建議同一件事時才提；暫時性的理由（「現在不值得」）和不言自明的理由就跳過。
- **想探索加深後 module 的替代介面？** 用 Skill 工具呼叫 "codebase-design"，並使用它的 design-it-twice 平行 sub-agent 模式。
