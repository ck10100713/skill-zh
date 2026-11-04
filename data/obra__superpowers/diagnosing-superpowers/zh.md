---
name: diagnosing-superpowers
description: 當 superpowers 的某個 session 出了問題而你的搭檔想知道原因時使用，例如重複做工、忽略計畫、跌跌撞撞、結果很差、某個 skill 沒觸發、「花太久了」、「為什麼這麼貴」、「它到底在幹嘛」；或想為 superpowers 維護者整理 bug 報告時使用，對象可以是目前的 session，也可以是用 id 或路徑指定的過去 session，任何 harness 都適用。
---

# Diagnosing Superpowers

## 概述

跟你的搭檔一起釐清某個 session 出了什麼問題，讀取磁碟上的 transcript，並用證據報告發生了什麼事。你只負責報告，不負責診斷 superpowers。要不要改 superpowers，由負責分流這份 bundle 或 issue 的人決定。

**核心原則：** 每個發現都要引用 `path:line`。沒有引用，就不算發現。每個數字都要來自 transcript 或你執行過的指令，絕對不能憑記憶。

## 工作流程

每個步驟建立一個 todo。步驟 5–7 只在它們說明的條件下才執行。

1. **問題受理。** 一次問一個問題，直到你能寫出一份陳述，裡面點名 session、已知的話寫出 turn 範圍、你的搭檔原本預期什麼、實際發生什麼，以及他們在意的可觀察指標（實際時間、token、重複的動作、某一個特定動作）。「花太久了」是抱怨，不是問題陳述。記下目標是不是要產出 superpowers 的 bug 報告。
2. **定位。** 用 `references/session-discovery.md`，把每個 session 解析成經過驗證的絕對檔案系統路徑。確認過去的 session 時，要引用它的第一個 prompt 和時間戳記，並列出你排除的每一個候選項及理由，沒有的話寫「none」。列舉出 subagent 的 transcript。建立 `~/.superpowers/diagnosing-superpowers/<session-id>/`，把路徑告訴你的搭檔，並在那裡填寫 `templates/case.md`，環境與 skill 觀察要遵守它的來源（provenance）規則。
3. **分流。** 自己讀報告問題前後的區段。接著平行派出一個分析用 subagent 負責一個面向，每個 subagent 都拿到案件檔案的路徑、`prompts/analyst-common.md`，以及 `prompts/` 底下的一個面向檔案：`skill-timeline.md`、
   `plan-adherence.md`、`repeated-work.md`、`stumbles.md`、
   `quality-evidence.md`、`request-conflicts.md`、`cost-and-time.md`。
   Transcript 很長時，依 turn 範圍拆分一個面向。回傳的發現沒有 `path:line` 的，一律丟掉。
4. **報告。** 依序填寫 `templates/report.md` 的每個段落，寫到工作區、顯示出來，並給出路徑。檢查被引用的內容實際上證明了什麼，並保留佐證的案件；symlink 別名不是多餘的副本。
5. **GitHub issue**：當報告 §7 說可能或很可能，或你的搭檔要求時。依 `references/github-issues.md` 搜尋已開啟和已關閉的 issue 有沒有這些症狀。顯示匹配的結果，並建議把報告加到最接近的那個。如果沒有任何匹配，就填寫 `templates/issue.md`，寫到工作區，顯示確切的文字，核准之後才建立 issue。`gh` 沒辦法附加檔案；如果有 bundle，就把它的路徑給你的搭檔，讓他們在瀏覽器附上。
6. **匯出**：只有在你的搭檔要求 bundle 時才做；絕對不要沒人要求就自己建立。如果受理時的目標是 bug 報告，就說一次可以應要求提供經過清理（scrub）的 bundle，然後等待。詢問遮蔽（redaction）等級，並說明每一級包含什麼：skeleton（沒有 tool result 的內文）、evidence（只有被引用事件的內文）、full。依 `templates/bundle-README.md` 建立 bundle，派出 `prompts/scrub.md`，再派出 `prompts/scrub-audit.md`，兩個都重複執行，直到稽核回傳 CLEAN。顯示最終的清理紀錄、檔案清單，以及隱私和證據的結果之前，先完成 bundle 範本裡的證據檢查與對帳。核准之後才封存（`zip -r` 或 `tar -czf`）。給出封存檔的路徑時，說明它包含什麼，指出清理紀錄裡有哪些替換，並說清理可能有漏網之魚：他們分享之前，一定要檢查每一個檔案。
7. **類似的 session**：被問到時才做。把已確認的發現變成一個特徵，依 mtime 和大小列出候選項，找出標記行的行號，對每個候選項平行派出 `prompts/similar-session.md`，並附加到報告 §9。

## 快速參考

七個分析員永遠全部都跑。這張表是告訴你步驟 3 要自己先讀哪個區段，以及判決時該把哪些發現放在最前面。

| 抱怨 | 先讀、先講 |
|---|---|
| 「花太久了」 | cost-and-time、stumbles |
| 「它為什麼多做這些事？」 | repeated-work、plan-adherence |
| 「為什麼這麼貴？」 | cost-and-time |
| 「它到底在幹什麼？」（還在跑） | skill-timeline；在覆蓋範圍裡註明進行中 |
| 「它無視計畫」 | plan-adherence，先看 compaction 的那些行 |
| 「Skill X 從來沒觸發」 | skill-timeline |

## 硬性規則

- **Context 安全。** 一行 transcript 可能就有一 MB 大。每次處理每個 session 檔案，都要遵守 `references/context-safety.md`。
- **唯讀。** 絕對不准修改、移動或刪除 session 檔案。
- **給 subagent 確切的路徑。** Subagent 的「目前 session」是它自己的。要傳絕對路徑和 id。
- **只看人類的 prompt。** Hook 輸出、system reminder 和 tool result 都不是你搭檔說的話。在 subagent 的 transcript 裡，「user」是上層的 agent。
- **不做 superpowers 診斷。** 報告 §7 只陳述有沒有牽涉，然後就停。絕對不要指出某個 skill 的缺陷或提議修改。你的搭檔逼你給修法，也不能豁免這條；指向 issue 那個步驟，並提到可以應要求提供 bundle。也不要給你的搭檔任何建議。
- **核准關卡。** 你的搭檔看過清理紀錄和檔案清單之前，不准封存。他們核准確切文字之前，不准開 issue 或留言，而且摘要是佔位符的也不准。
- **先受理再分析。** 你的搭檔回答之前，步驟 2–7 什麼都不准開始。如果他們不在，就把問題寫下來然後停住。你幫他們重建出來的陳述不算答案。已經限定範圍的請求（一個特定事件、現在正在跑的東西，或要執行的分析）本身就是陳述：回答它，然後再問。針對整個 session 的「為什麼」是抱怨。

## 警訊

| 想法 | 現實 |
|---------|---------|
| 「問題很明顯，跳過受理」 | 問題陳述決定所有東西的範圍。去問。 |
| 「他們不在，所以我來重建陳述」 | 你沒辦法重建他們想要什麼。把問題寫下來然後停住。 |
| 「我現在全部掃一遍，最後再問」 | 沒有限定範圍的掃描，會把他們的額度花在錯的問題上。先問。 |
| 「他們要 bug 報告，所以我現在就建 bundle」 | Bundle 就是他們的 session 資料打包起來。他們要求才建。 |
| 「很小的針對性修改，不需要重構」 | 不是你能決定的，不管多小。報告證據；由分流的人決定。 |
| 「每個 token 的價格是眾所周知的」 | 不是你從 transcript 算出來的數字，就是捏造的。要嘛引用，要嘛丟掉。 |
