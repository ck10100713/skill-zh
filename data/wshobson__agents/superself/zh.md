---
name: superself
description: '當專案把狀態存放在 Superself（AGENTS.md 或 CLAUDE.md 裡有 `<!-- superself:begin` 區塊，或 `self setup` 把目錄解析到一個已註冊的專案）時使用：在 session 開始時讀取 `self context`、把工作掛到一個 work unit 上、附上證據來回報，並記錄已確認的決定，讓下一個 session 能從這個 session 結束的地方接續下去。'
---

# Superself

Superself 是一個 Apache-2.0 的 CLI（`npm install -g superself@0.6.1`，需要 Node 22.12+），把專案的狀態（目標、決定、work unit、報告）當成一份只能附加的事件 log，用版本控管的方式存在跟程式碼分開的 git repository 裡。狀態是在需要時才推導出來的，所以裡面沒有任何東西是手動維護的。這個 skill 告訴 agent 怎麼透過 `self` CLI 讀取和寫入那份狀態。它由 Superself 的作者維護：https://github.com/fxylabs/superself

## When this skill applies

- 專案的 `AGENTS.md` 或 `CLAUDE.md` 裡，在 `<!-- superself:begin` 和 `<!-- superself:end -->` 之間有一個區塊，或是 `self setup` 印出這個目錄解析到的 workspace、專案和 store。
- 如果 `self --version` 失敗，就跳過這個 skill：這個專案沒有使用 Superself，下面的任何東西都不該用手編造。這個 skill 是針對 `superself@0.6.1` 寫的；不同的 major 或 minor 版本，可能已經移動了某個動詞或旗標，所以在依賴它之前，先檢查 `self <command> --help`。

## Session start

1. 執行 `self context`，並把它的輸出當成目前的事實：目標、有效的決定和慣例、未完成的工作、最近的報告。它是從 log 摺疊出來的，絕對不是手寫的。
2. context 裡缺少的東西，是被刻意排除在顯示範圍之外的；`self search <query>` 可以找到 context 沒列出的有效紀錄，`self work show <id>` 會印出某個 unit 的完整簡介和報告歷史。

## While working

- 實質的工作要掛到一個 work unit 上。用 `self work add "<required outcome>"` 建立一個，outcome 是必須成真的事情，不是任務，然後用 `self work start <id>`。`start` 會讀取簡介，並記錄這個 session 接手了這個 unit；如果有另一個 session 持有它，CLI 會說是誰、從什麼時候開始，但不會拒絕。你自己判斷後繼續。
- commit 之後，回報進度：`self report <id> "<what happened>"`。目前 HEAD 的 commit 會自動附上當作證據；`--evidence <commit|note>` 可以附上別的東西，`--file <path>` 可以附上比較長的簡介。
- 記錄使用者確認過的決定：`self decide "<text>" --why "<reason>"`。使用者還沒確認的話，用 `--proposed`。一個事件一個決定。
- 被擋住了？`self work block <id> --on decision|dependency|external --why "..."`。被取代或被移走了？`self work retire <id> --why "..." [--successor <id>]`。絕對不要把這樣的 unit 標記成完成，也絕對不要讓它錯誤地維持在被擋住的狀態。
- 發現某個目標和目前狀態之間有落差？用 `self work propose` 和它的簡介來提議這項工作；使用者會接受或拒絕。
- 使用者核准了下一步或後續的延伸？馬上用 `self work add` 加上背後的 context 註冊起來。只存在於對話中的計畫，會在對話結束時消失。

## Closing

- `self work done <id>` 只有在某份報告帶有 commit 或 artifact，或是 done 本身說明了可驗證發生了什麼的時候，才會關閉一個 unit：`self work done <id> --report "<what verifiably happened>"`。光是空口宣稱會被拒絕，而已宣告的標準會把關，直到每一項都被涵蓋。
- 一筆紀錄的文字一旦確認就不可變。要更正，就用重新陳述的方式：在任何 add 動詞上使用 `--supersedes <id>`，會記錄新的措辭並保留血脈（lineage）。`retract` 則是撤回一筆紀錄，沒有任何東西取代它。

## Rules that keep the state trustworthy

- 紀錄（事件、決定、報告、慣例）都用英文寫，這樣下一個打開它們的人才讀得懂；回覆使用者則用他們自己的語言。
- 一個 branch 要透過 pull request 才能進到 main：PR review 和 CI 負責 merge 的控制。Superself 負責 context 和 work graph，不負責 merge 的關卡。
- 絕對不要手動編輯產生出來的狀態檔，或 `.superself/` 底下的任何東西。
- 在沒有 superself 區塊的專案裡，先執行 `self setup`。如果它把目錄解析到一個已註冊的專案，就問使用者一次，要不要執行 `self connect`，它會把受管理的區塊寫進 `AGENTS.md` 或 `CLAUDE.md`。如果它沒有解析出任何專案，就問一次要不要用 `self project init` 註冊。絕對不要自己註冊或連接專案。

## Going deeper

`self --help` 會列出每個動詞；`self <command> --help` 會印出某個指令的旗標，而且不會動到狀態。主題指南隨 CLI 一起提供：

- `self help agents` — session 如何從頭到尾驅動這個 CLI
- `self help context` — `self context` 會顯示什麼，以及為什麼有些東西不在裡面
- `self help records` — 每種紀錄種類背後共通的一個實體，以及紀錄如何被更正
- `self help placement` — scope、優先順序和曝光度，一筆紀錄如何爭取到在 context 裡的位置
- `self help work` — work graph：outcome、證據、標準和提案
- `self help goals` — 長期目標、objective、里程碑，以及要達成其中一個需要什麼
- `self help workspace` — store、其中的專案，以及在機器之間搬移它
