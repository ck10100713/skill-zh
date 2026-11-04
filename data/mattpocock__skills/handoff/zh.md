---
name: handoff
description: 把目前的對話壓縮成交接文件，讓另一個 agent 接手。
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

寫一份交接文件，總結目前的對話，讓全新的 agent 可以接著做下去。存到使用者作業系統的暫存目錄（`$TMPDIR`，沒有就用 `/tmp`；Windows 是 `%TEMP%`），不要存在目前的 workspace。

文件裡要有一節「suggested skills」，列出下一個 agent 該用 Skill 工具呼叫哪些 skill。

其他產出物已經記錄過的內容（spec、計畫、ADR、issue、commit、diff）不要重複寫，用路徑或 URL 引用就好。

敏感資訊一律遮掉，例如 API key、密碼、個人可識別資訊。

如果使用者有帶參數，就把它當成下一個 session 要專注的事，並據此調整文件內容。
