---
name: automation-audit-ops
description: 以證據為先的 ECC 自動化盤點與重疊稽核工作流程。使用者想在動手修之前，先搞清楚哪些 job、hook、connector、MCP server 或 wrapper 是運作中、壞掉、多餘或缺少的時候使用。
metadata:
  origin: ECC
---

# Automation Audit Ops

當使用者問哪些自動化正在運作、哪些 job 壞了、哪裡有重疊，或哪些工具和 connector 目前真的有在做有用的事時，用這個 skill。

這是一個稽核優先的操作員 skill。工作是在重寫任何東西之前，先產出有證據支撐的盤點，以及「保留 / 合併 / 砍掉 / 下一個修」的建議清單。

## Skill 組合

相關的時候，把這些 ECC 原生的 skill 拉進工作流程：

- `workspace-surface-audit`：盤點 connector、MCP、hook 和 app
- `knowledge-ops`：稽核需要把 repo 的即時實況跟持久的 context 對帳時用
- `github-ops`：答案取決於 CI、排程的 workflow、issue 或 PR 自動化時用
- `ecc-tools-cost-audit`：真正的問題是 webhook 扇出、排隊的 job，或姊妹 app repo 的帳單燒太快時用
- `research-ops`：本地盤點需要跟目前平台支援或公開文件比對時用
- `verification-loop`：用來證明修復後的狀態，不要靠假設已經恢復

## 何時使用

- 使用者問「我有哪些自動化」「哪些是運作中的」「哪些壞了」或「哪些重疊」
- 任務橫跨 cron job、GitHub Actions、本機 hook、MCP server、connector、wrapper 或 app 整合
- 使用者想知道從別的 agent 系統移植過來了什麼，還有什麼需要在 ECC 裡重建
- 工作區累積了好幾種做同一件事的方式，使用者想要一條標準路線

## 護欄

- 除非使用者明確要求修復，否則一開始先維持唯讀
- 分開標示：
  - 已設定
  - 已驗證身分
  - 最近驗證過
  - 過時或壞掉
  - 完全缺少
- 不要只因為某個 skill 或設定有提到某個工具，就宣稱它在運作
- 證據表出現之前，不要合併或刪除重疊的部分

## 工作流程

### 1. 盤點真實的範圍

先讀目前實際運作的範圍，再去推論：

- repo 的 hook 和本機 hook script
- GitHub Actions 和排程的 workflow
- MCP 設定和已啟用的 server
- 由 connector 或 app 支撐的整合
- wrapper script 和 repo 專屬的自動化進入點

依範圍分組：

- 本機 runtime
- repo CI / 自動化
- 已連接的外部系統
- 訊息 / 通知
- 帳務 / 客戶營運
- 研究 / 監控

### 2. 依運作狀態替每個項目分類

對每個找到的自動化，標示：

- 已設定
- 已驗證身分
- 最近驗證過
- 過時或壞掉
- 缺少

然後分類問題類型：

- 目前正在壞
- 驗證中斷
- 狀態過時
- 重疊或冗餘
- 缺少的能力

### 3. 追蹤證明路徑

每個重要的主張，都要有具體的來源支撐：

- 檔案路徑
- workflow 執行紀錄
- hook log
- 設定項目
- 最近的指令輸出
- 確切的失敗特徵

如果目前的狀態不明確，就直接說，不要假裝稽核已經完成。

### 4. 以保留 / 合併 / 砍掉 / 下一個修收尾

對每個重疊或可疑的部分，給一個判斷：

- 保留（keep）
- 合併（merge）
- 砍掉（cut）
- 下一個修（fix next）

價值在於把吵雜的自動化收斂成一條標準的 ECC 路線，不是把每一條歷史路徑都保留下來。

## 輸出格式

```text
CURRENT SURFACE
- automation
- source
- live state
- proof

FINDINGS
- active breakage
- overlap
- stale status
- missing capability

RECOMMENDATION
- keep
- merge
- cut
- fix next

NEXT ECC MOVE
- exact skill / hook / workflow / app lane to strengthen
```

## 常見陷阱

- 即時盤點讀得到的時候，不要憑記憶回答
- 不要把「設定裡有」當成「有在運作」
- 在點名壞掉的高訊號路徑之前，不要先修價值較低的冗餘
- 使用者先要的是盤點，就不要把任務擴大成重寫整個 repo

## 驗證

- 重要的主張都引用了即時的證明路徑
- 每個找到的自動化都標上清楚的運作狀態類別
- 最後的建議有區分保留 / 合併 / 砍掉 / 下一個修
