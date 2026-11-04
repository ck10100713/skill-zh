---
name: skillopt-sleep
description: SkillOpt-Sleep 的 OpenClaw 改編版，僅供參考。拿來研究或移植別人貢獻的 DeepSeek wrapper，不是能直接執行的安裝版本。
---

# SkillOpt-Sleep OpenClaw 參考改編版

這個目錄是別人貢獻的**參考範例**，不是受支援、可直接插上就用的 OpenClaw 整合。它示範一種做法：把共用的 `skillopt_sleep` 週期，接到自訂的 DeepSeek Chat Completions backend，以及一組跟特定環境綁定的任務 fixture。

不要原封不動地執行或排程這些檔案。有幾個 script 和範例設定保留了貢獻者原本那台機器上的假設，而且 wrapper 有部分還沒移植到目前共用引擎的介面。先看這個目錄的 [README.md](README.md)，它才是權威的狀態說明和改編指南。

## 包含的內容

- `skillopt_sleep_openclaw.py`：貢獻者寫的 DeepSeek backend 原型。裡面還有一個 Ollama embedding helper，但那個 helper 沒有接到目前共用的 sleep 週期。
- `run_sleep.py`：自訂的週期 wrapper，含有跟環境綁定的路徑，以及一個 backend 註冊的 shim。
- `slash_sleep.py`：實驗性的指令 helper，是針對舊版 staging manifest 的格式寫的。
- `run_sleep_cron.sh`：跟特定機器綁定的分類執行器，不是可攜的 cron 安裝程式。
- `config.json`：範例設定，不是有保證或強制執行的 runtime 限制。
- `tests/*.json`：來自某一個環境的範例任務 fixture，不是通用的 OpenClaw benchmark。

## 已知的移植缺口

在把它當成整合之前，維護者至少要：

1. 把每一個絕對路徑（workspace、repository、state、skill、log、任務）都換成明確的使用者設定。
2. 更新自訂 backend 的 factory，符合目前 `get_backend` 的呼叫契約（包含專案目錄），並把 backend 的方法和 edit record 更新成目前的協定。
3. 把實驗性的採用邏輯，換成目前的 staging manifest 和 `skillopt_sleep.staging.adopt` 的行為。目前的 staging 產物是 `proposed_SKILL.md` / `proposed_CLAUDE.md`、`manifest.json` 和報告檔；它們不再提供舊的 `manifest.proposed_skill` 欄位。
4. 決定怎麼把真實的 OpenClaw transcript 轉成受支援的 session 格式。把 `claude_home` 指向任意的 agent 目錄，並不會讓裡面的檔案自動變成 Claude Code 相容的 JSONL。
5. 圍繞改編過的 wrapper 建立排程。共用的 scheduler 啟動的是共用的 CLI；它不會自動保留這個自訂 backend 或它的分類任務檔流程。
6. 加上獨立的端對端測試，涵蓋 dry-run、接受/拒絕的關卡、staging、採用與備份、憑證失敗，以及排程執行。

在這些缺口解決之前，要測試 SkillOpt-Sleep 本身，請使用受支援的共用 `python -m skillopt_sleep` CLI 搭配 `--backend mock`，並且只把這個目錄當成未來 OpenClaw 移植的原始素材。

## 共用引擎的功能不等於 wrapper 的功能

在這個版本，受支援的共用 CLI backend 有 `mock`、`claude`、`codex`、`copilot`、`handoff` 和 `azure_openai`；[plugin 整合參考](../README.md#supported-cli-surface)是權威的清單。共用引擎可以整合選定的 skill 和專案的 `CLAUDE.md` 記憶（由 `evolve_skill` 和 `evolve_memory` 控制），它的 `schedule` / `unschedule` 動作會管理共用引擎的 cron 項目。這些能力**不會**讓自訂的 OpenClaw wrapper 變得可攜：共用的 scheduler 不會去呼叫這個原型 backend 或它的分類 fixture。這些功能請看共用文件，不要看這份參考用的 SKILL.md。

## 資料與憑證的界線

原型的 DeepSeek backend 會把任務、skill、記憶、回應、rubric 和反思的內容，送到它所設定的 Chat Completions endpoint。它的原始碼裡還有一個 helper，如果未來的移植版把那個 helper 接進週期，就可以把文字送到 Ollama 服務。這兩條路徑，都不應該假設已經去除了所有的 secret 或私人細節。

在任何移植版用真實資料測試之前：

- 使用獨立的、合成的，或經過明確審查的任務檔；
- 替換範例裡的商家名稱、個人參照、URL 和機器路徑；
- 透過操作者的 secret 管理機制載入憑證；
- 對每個遠端 endpoint 驗證 TLS 和資料保留政策；
- 採用之前，檢查所有 staging 的產物。

附帶的 fixture 只是範例。它們的分數和任何舊的成本估算，都不能證明在其他 OpenClaw 部署上的成效、安全性，或穩定的每晚價格。

## 更多資訊

- [OpenClaw README](README.md)：目前的參考狀態和改編檢查清單
- [plugin 整合參考](../README.md)：受支援的共用引擎 CLI 範圍與資料界線
- [SkillOpt-Sleep 文件](../../docs/sleep/README.md)：概念、結果與限制

想把這份參考變成可攜整合的貢獻，應該加上測試，並同步更新這三份文件。
