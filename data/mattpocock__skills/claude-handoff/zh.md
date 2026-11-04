---
name: claude-handoff
description: 把目前的對話交接給一個全新的背景 agent，讓它立刻接手工作。
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

寫一份交接摘要，總結目前的對話，讓全新的 agent 可以接著做下去。存到使用者作業系統的暫存目錄，然後啟動一個背景 agent，用這份摘要當它的 prompt：`claude --bg --name "<descriptive name>" -- "$(cat <summary file>)"`。傳檔案的方式可以避免 shell 去執行摘要裡的反引號或展開 `$`。它會在目前的工作目錄啟動並立刻返回；使用者用 `claude agents` 來管理它。

一定要帶 `-n`/`--name` 並取一個有描述性的名字（例如 `--name "Fix login bug"`）；它決定在工作清單、session 選擇器和終端機標題上顯示的名稱。

摘要裡要有一節「suggested skills」，列出下一個 agent 該用 Skill 工具呼叫哪些 skill。

其他產出物已經記錄過的內容（spec、計畫、ADR、issue、commit、diff）不要重複寫，用路徑或 URL 引用就好。

敏感資訊一律遮掉，例如 API key、密碼、個人可識別資訊，因為這份摘要會變成 agent 的 prompt。

如果使用者有帶參數，就把它當成下一個 session 要專注的事，並據此調整摘要內容。
