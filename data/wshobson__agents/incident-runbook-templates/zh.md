---
name: incident-runbook-templates
description: 建立結構化的事故應變 runbook，包含逐步程序、升級路徑與復原動作。適用於為付款處理系統建立服務中斷 runbook、建立涵蓋 connection pool 耗盡、複寫延遲和磁碟空間警報的資料庫事故程序、讓新的 on-call 工程師上手（需要寫給凌晨 3 點腦袋不清楚的人看的逐步復原指南），或在多個工程團隊之間標準化升級矩陣的時候。
---

# 事故 Runbook 範本

事故應變 runbook 的 production-ready 範本，涵蓋偵測、分流、緩解、解決與溝通。

## 什麼時候用這個 Skill

- 建立事故應變流程
- 建立特定服務的 runbook
- 設定升級路徑
- 記錄復原程序
- 回應正在發生的事故
- 讓 on-call 工程師上手

## 核心概念

### 1. 事故嚴重等級

| 嚴重等級 | 影響                       | 回應時間          | 範例                    |
| -------- | -------------------------- | ----------------- | ----------------------- |
| **SEV1** | 完全中斷、資料遺失         | 15 分鐘           | Production 掛掉         |
| **SEV2** | 嚴重劣化                   | 30 分鐘           | 關鍵功能壞掉            |
| **SEV3** | 輕微影響                   | 2 小時            | 非關鍵的 bug            |
| **SEV4** | 影響極小                   | 下一個工作日      | 外觀問題                |

### 2. Runbook 結構

```
1. 概述與影響
2. 偵測與警報
3. 初步分流
4. 緩解步驟
5. 根因調查
6. 解決程序
7. 驗證與 Rollback
8. 溝通範本
9. 升級矩陣
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務

### 該做的
- **保持 runbook 是最新的**：每次事故之後都要檢視
- **定期測試 runbook**：Game day、chaos engineering
- **包含 rollback 步驟**：永遠要有退路
- **記錄假設**：步驟要能運作，哪些條件必須成立
- **連到 dashboard**：壓力下能快速存取

### 不該做的
- **不要假設對方有相關知識**：要寫給凌晨 3 點腦袋不清楚的人看
- **不要跳過驗證**：確認每個步驟都有效
- **不要忘記溝通**：讓利害關係人隨時掌握狀況
- **不要單打獨鬥**：及早升級
- **不要跳過 postmortem**：從每次事故中學習

## 疑難排解

### Runbook 的步驟在 staging 有效，但真正發生事故時失敗

步驟常常假設了一些前提，在健康的環境中成立，但中斷期間不成立。對 runbook 中的每個指令，都加上前置條件檢查，以及一段「如果這個指令失敗該怎麼辦」的說明：

```bash
# 步驟：檢查 pod 狀態
kubectl get pods -n payments

# 前置條件：kubectl 已設定、kubeconfig 指向正確的 cluster
# 如果失敗：執行 `aws eks update-kubeconfig --name prod-cluster --region us-east-1`
# 預期輸出：pod 處於 Running 狀態
```

### On-call 工程師慌了，結果步驟做得亂七八糟

在 runbook 最上面加上一份編號的檢查表，對應各章節的編號，讓處理者在壓力下不用讀完整份文件，也能追蹤進度：

```markdown
## 快速檢查表
- [ ] 1. 宣告事故嚴重等級並開啟 war room
- [ ] 2. 檢查服務健康狀態（第 4.1 節）
- [ ] 3. 檢查最近的 deploy（第 4.1 節）
- [ ] 4. 如果懷疑是 deploy 造成的就 roll back（第 4.1 節）
- [ ] 5. 在 #payments-incidents 發出初步通知
- [ ] 6. 超過 15 分鐘還沒解決就升級
```

### Runbook 過時了：指令參照的是舊的 cluster 名稱或 endpoint

Runbook 會腐爛，因為它們是手動更新的。在最上面加上「最後驗證」日期和負責人，並加一個 CI 檢查，驗證所有 `curl` endpoint 和 `kubectl` context 名稱仍然有效：

```markdown
## Runbook 中繼資料
| 欄位 | 值 |
|---|---|
| 最後驗證 | 2024-11-15 |
| 負責人 | @platform-team |
| 檢視週期 | 每次 SEV1/SEV2 之後 |
```

### 工程師埋頭處理時，利害關係人的溝通被拖延

指派一個專門的事故溝通角色（獨立於事故指揮官），唯一的工作就是發布狀態更新。在溝通範本中加上固定的議程：

```
每 15 分鐘更新一次（即使沒有新資訊）：
- 目前狀態（調查中 / 緩解中 / 監控中）
- 影響（什麼壞了、誰受影響、流量百分比）
- 我們現在正在做什麼
- 下次更新：15 分鐘後
```

### 資料庫 runbook 的指令執行錯誤時，會造成額外的停機

在破壞性的 SQL 指令之前加上明確的警告，並要求在執行之前先檢查 dry-run 的輸出：

```sql
-- 警告：這會終止活躍的連線。請先確認數量。
-- DRY RUN（終止之前先檢查數量）：
SELECT count(*) FROM pg_stat_activity WHERE state = 'idle' AND query_start < now() - interval '10 minutes';

-- 只有在確認數量合理（< 50）之後才執行：
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'idle' AND query_start < now() - interval '10 minutes';
```

## 相關 Skill

- `postmortem-writing`：事故解決後，用 postmortem 範本記錄根因與預防措施
- `on-call-handoff-patterns`：安排換班交接的結構，讓接手的處理者完整掌握進行中事故的脈絡