---
name: ecc-tools-cost-audit
description: 以證據為先的 ECC Tools 燒錢與計費稽核工作流。在調查 ECC Tools repo 中失控的 PR 建立、配額繞過、premium 模型外洩、重複 job，或 GitHub App 成本暴增時使用。
metadata:
  origin: ECC
---

# ECC Tools 成本稽核

當使用者懷疑 ECC Tools GitHub App 在燒成本、建立過多 PR、繞過用量限制，或把免費使用者導向 premium 分析路徑時，就用這個 skill。

這是針對兄弟 repo [ECC-Tools](../../ECC-Tools) 的聚焦操作者工作流。它不是通用的計費 skill，也不是整個 repo 的 code review。

## Skill 組合

相關時，把這些 ECC 原生 skill 拉進工作流：

- `autonomous-loops`：用於跨 webhook、queue、計費與重試的有界多步驟稽核
- `agentic-engineering`：把請求路徑追蹤成一個個可證明的獨立單元
- `customer-billing-ops`：repo 行為和客戶影響的計算必須清楚分開時
- `search-first`：在發明 helper 或重寫 repo 內既有工具之前
- `security-review`：動到 auth、用量 gate、entitlement 或 secret 時
- `verification-loop`：證明重跑安全與修復後的確切狀態
- `tdd-workflow`：修復需要在 worker、router 或計費路徑補 regression 覆蓋時

## 何時使用

- 使用者提到 ECC Tools 的燒錢速度、PR 遞迴、過度建立 PR、用量限制繞過，或 premium 模型外洩
- 任務在兄弟 repo `ECC-Tools` 裡，且取決於 webhook handler、queue worker、用量預留、PR 建立邏輯，或付費 gate 的執行
- 客戶回報 app 建了太多 PR、計費錯誤，或分析了程式碼卻沒有產出可用的結果

## 範圍護欄

- 在兄弟 repo `ECC-Tools` 裡工作，不要在 `ECC` 裡
- 除非使用者明確要求修復，否則先以唯讀方式開始
- 追蹤分析燒錢時，不要去動不相關的計費、結帳或 UI 流程
- 在證明不是之前，把 app 產生的 branch 和 app 產生的 PR 當成紅旗的遞迴路徑
- 明確分開三件事：
  - repo 端的燒錢根因
  - 面向客戶的計費影響
  - 需要排進 backlog 後續處理的產品或 entitlement 缺口

## 工作流

### 1. 凍結 repo 範圍

- 切換到兄弟 repo `ECC-Tools`
- 先檢查 branch 和本地 diff
- 找出稽核的確切範圍：
  - webhook router
  - queue producer
  - queue consumer
  - PR 建立路徑
  - 用量預留 / 計費路徑
  - 模型路由路徑

### 2. 先追蹤入口，再提出理論

- 先檢查 `src/index.*` 或主要的 entrypoint
- 在建議修復之前，先對應出每一條 enqueue 路徑
- 確認哪些 GitHub event 共用同一個 queue 類型
- 確認 push、pull_request、synchronize、comment 或手動重跑的 event，會不會匯集到同一條昂貴的路徑

### 3. 追蹤 worker 與副作用

- 檢查處理分析的 queue consumer 或排程 worker
- 確認排進 queue 的分析是不是一定會以下列結尾：
  - 建立 PR
  - 建立 branch
  - 更新檔案
  - 呼叫 premium 模型
  - 用量增加
- 如果分析會花掉 token，卻在輸出被保存之前失敗，就歸類為「燒錢但輸出壞掉」

### 4. 稽核高訊號的燒錢路徑

#### PR 倍增

- 檢查 PR helper 與 branch 命名
- 檢查去重、synchronize event 的處理，以及重用既有 PR
- 如果 app 產生的 branch 可以重新進入分析，就把它視為優先級 0 的遞迴風險

#### 配額繞過

- 檢查配額是在哪裡被檢查、用量又是在哪裡被預留或遞增
- 如果配額在 enqueue 之前檢查，但用量只在 worker 內才計費，就把前門同時放行當成真正的 race

#### Premium 模型外洩

- 檢查模型選擇、等級分支與 provider 路由
- 驗證有 premium key 時，免費或有上限的使用者是否仍能打到 premium 分析器

#### 重試燒錢

- 檢查重試 loop、重複的 queue job，以及確定性失敗的重跑
- 如果同一個非暫時性的錯誤能反覆花掉分析成本，要在改善品質之前先修這個

### 5. 依燒錢順序修復

如果使用者要求改程式碼，依下列順序排修復優先級：

1. 停止自動的 PR 倍增
2. 停止配額繞過
3. 停止 premium 外洩
4. 停止重複 job 的 fanout 與無意義的重試
5. 補上重跑/更新的安全缺口

除非同一個根因明顯橫跨多個檔案，否則這一輪只做一到三個直接的修復。

### 6. 用最小的證明步驟驗證

- 只重跑涵蓋被改動路徑的目標測試或整合切片
- 驗證燒錢路徑現在是：
  - 被擋下
  - 被去重
  - 降級成較便宜的分析
  - 或提早被拒絕
- 精確說明最終狀態：
  - 本地已修改
  - 本地已驗證
  - 已 push
  - 已 deploy
  - 仍然被卡住

## 高訊號的失敗模式

### 1. 所有觸發共用同一個 queue 類型

如果 push、PR sync 和手動稽核都排進同一種 job，而 worker 又一律建立 PR，分析就等於 PR 垃圾訊息。

### 2. enqueue 之後才預留用量

如果用量在前門檢查，卻只在 worker 內遞增，並行的請求可以全部通過 gate 並超出配額。

### 3. 免費層走到 premium 路徑

如果免費的排隊 job 在 key 存在時仍能路由到 Anthropic 或其他 premium provider，那就是真正的花費外洩，即使使用者從沒看到 premium 的結果。

### 4. App 產生的 branch 重新進入 webhook

如果 `pull_request.synchronize`、branch push 或 comment 觸發的執行在 app 自己的 branch 上被觸發，app 就會遞迴分析自己的輸出。

### 5. 在確保可持久化之前就做昂貴的工作

如果系統花掉 token 之後，卻在建立 PR、更新檔案或 branch 衝突時失敗，它就是在燒成本卻沒有交付價值。

## 常見陷阱

- 不要一開始就在 repo 裡亂逛；先釐清 webhook -> queue -> worker
- 不要把客戶計費的推論和有程式碼支撐的產品事實混在一起
- 在最高燒錢的路徑被控制住之前，不要先修價值較低的品質問題
- 在窄範圍的證明步驟重跑過之前，不要宣稱燒錢已修好
- 除非使用者要求，否則不要 push 或 deploy
- 如果不相關的 repo 本地變更已在進行中，不要去動它們

## 驗證

- 根因要引用確切的檔案路徑與程式碼區域
- 修復依燒錢影響排序，不是依程式碼整潔度
- 要寫出證明用的指令
- 最終狀態要區分本地修改、驗證、push 與 deploy
