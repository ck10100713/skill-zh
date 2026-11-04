---
name: code-review
description: "以兩個面向 review 從某個固定點（commit、branch、tag 或 merge-base）以來的改動：Standards（程式碼有沒有遵守這個 repo 文件化的編碼標準？）和 Spec（程式碼有沒有符合原始 issue/spec 的要求？）。兩個 review 用平行的 sub-agent 同時跑，並排回報。當使用者想 review 一個 branch、一個 PR、進行中的改動，或說「review since X」時使用。"
---

對 `HEAD` 和使用者指定的固定點之間的 diff 做兩個面向的 review：

- **Standards**：程式碼有沒有符合這個 repo 文件化的編碼標準？
- **Spec**：程式碼有沒有忠實實作原始的 issue / spec？

兩個面向都用**平行的 sub-agent** 來跑，這樣它們不會污染彼此的 context，然後這個 skill 再彙整它們的發現。每個 sub-agent 都從全新的 context window 開始。

issue tracker 應該已經提供給你了。如果沒有，叫使用者去跑 `/setup-matt-pocock-skills`。

## 流程

### 1. 釘住固定點

使用者說的就是固定點（commit SHA、branch 名稱、tag、`main`、`HEAD~5` 等等）。如果他們沒指定，就問。

把 diff 指令記下來一次：`git diff <fixed-point>...HEAD`（三個點，這樣比較的對象是 merge-base）。同時用 `git log <fixed-point>..HEAD --oneline` 記下 commit 清單。

繼續之前，先確認固定點解析得出來（`git rev-parse <fixed-point>`），而且 diff 不是空的。錯誤的 ref 或空的 diff 應該在這裡就失敗，不要等到兩個平行的 sub-agent 裡才爆。

### 2. 找出 spec 來源

依下面順序尋找原始 spec：

1. commit message 裡的 issue 參照（`#123`、`Closes #45`、GitLab 的 `!67` 等等），照 tracker 文件裡的流程去抓。
2. 使用者當參數傳進來的路徑。
3. `docs/`、`specs/` 或 `.scratch/` 底下，跟 branch 名稱或功能對得上的 spec 檔。
4. 都找不到就問使用者 spec 在哪。如果他們說沒有，**Spec** sub-agent 就跳過，並回報「no spec available」。

### 3. 找出標準來源

在 repo 裡搜尋所有記載「程式碼該怎麼寫」的檔案。如果有 `CODING_STANDARDS.md` 或 `CONTRIBUTING.md`，一定要列進去。

除了 repo 文件化的東西之外，Standards 這個面向一律帶著下面的**壞味道基準（smell baseline）**：一組固定的 Fowler 程式碼壞味道（_Refactoring_ 第 3 章），就算 repo 什麼都沒文件化也適用。有兩條規則約束它：

- **repo 說了算。** repo 有文件化的標準就一律優先；基準會抓的東西如果標準明確認可，就不要報那個壞味道。
- **永遠是判斷題。** 每個壞味道都是有標籤的經驗法則（「possible Feature Envy」），絕不是硬性違規。跟這裡其他標準一樣，工具已經會強制檢查的就跳過。

每個壞味道的格式是*它是什麼* → *怎麼修*；拿它去比對 diff：

- **Mysterious Name**：函式、變數或型別的名字看不出它做什麼或裝什麼。→ 改名；想不出誠實的名字，代表設計本身就模糊。
- **Duplicated Code**：同樣的邏輯形狀在這次改動的多個 hunk 或檔案裡重複出現。→ 抽出共用的形狀，兩邊都呼叫它。
- **Feature Envy**：一個 method 伸手進別的物件拿資料，比用自己的還多。→ 把 method 搬到它眼紅的那份資料上。
- **Data Clumps**：同樣幾個欄位或參數老是一起出現（有個型別想誕生）。→ 打包成一個型別，傳那個型別。
- **Primitive Obsession**：用 primitive 或字串去代表一個值得有自己型別的領域概念。→ 給這個概念一個自己的小型別。
- **Repeated Switches**：對同一個型別的同一組 `switch`/`if` 連串判斷，在這次改動裡重複出現。→ 改用多型，或兩處共用一張 map。
- **Shotgun Surgery**：一個邏輯上的改動，逼你在 diff 裡的許多檔案到處改。→ 把會一起變動的東西收進同一個 module。
- **Divergent Change**：同一個檔案或 module 因為好幾個不相干的原因被修改。→ 拆開，讓每個 module 只因為一個原因而變。
- **Speculative Generality**：為了 spec 沒有的需求而加上的抽象、參數或 hook。→ 刪掉；inline 回去，直到真的出現需求。
- **Message Chains**：呼叫端不該依賴的長串 `a.b().c().d()` 導覽。→ 把這段走訪藏到第一個物件的單一 method 後面。
- **Middle Man**：一個 class 或函式大部分只是把事情轉手交出去。→ 砍掉，直接呼叫真正的目標。
- **Refused Bequest**：子類別或實作者忽略或覆寫了大部分繼承來的東西。→ 放棄繼承，改用組合。

### 4. 平行啟動兩個 sub-agent

兩個 sub-agent 的呼叫一起發出，在前景執行，然後彙整它們回傳的報告。

**Standards sub-agent 的 prompt** 要包含：

- 完整的 diff 指令和 commit 清單。
- 你在第 3 步找到的標準來源檔案清單，**加上第 3 步的壞味道基準**，整份貼進去（sub-agent 沒有其他方式拿到它）。
- 任務說明："Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent 的 prompt** 要包含：

- diff 指令和 commit 清單。
- spec 的路徑或抓下來的內容。
- 任務說明："Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

如果找不到 spec，就跳過 Spec sub-agent，並在最終報告裡註明。

### 5. 彙整

把兩份報告分別放在 `## Standards` 和 `## Spec` 標題底下，原文照放或稍微整理。**不要**合併或重新排名發現，因為兩個面向是刻意分開的（見 _為什麼分兩個面向_）。

最後用一句話總結：每個面向的發現總數，以及_各面向內_最嚴重的問題（如果有的話）。不要跨面向挑出單一贏家：那正是這個分離要防止的重新排名。

## 為什麼分兩個面向

一個改動可能過了其中一個面向、卻在另一個失敗：

- 每條標準都遵守、但做錯東西的程式碼 → **Standards 過，Spec 不過。**
- 完全照 issue 要求做、但違反專案慣例的程式碼 → **Spec 過，Standards 不過。**

分開回報，就不會讓一個面向蓋掉另一個。
