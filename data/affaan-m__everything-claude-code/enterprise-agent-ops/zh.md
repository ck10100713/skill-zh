---
name: enterprise-agent-ops
description: 長時間運行或雲端託管的 agent 系統的營運控制：runtime 生命週期（啟動、暫停、停止、重啟）、可觀測性（log、metric、trace）、最小權限的安全範圍與 kill switch，以及帶有稽核 log 與成功率/成本指標的 rollout/rollback 變更管理。在 PM2、systemd 或 container 上跑 production agent 叢集，需要監控、事件應變或部署 gate 時使用。
metadata:
  origin: ECC
---

# Enterprise Agent Ops

用在雲端託管或持續運行的 agent 系統，這類系統需要單一 CLI session 以外的營運控制。

## 營運面向

1. runtime 生命週期（啟動、暫停、停止、重啟）
2. 可觀測性（log、metric、trace）
3. 安全控制（範圍、權限、kill switch）
4. 變更管理（rollout、rollback、稽核）

## 基本控制

- 不可變的部署產物
- 最小權限的憑證
- 環境層級的 secret 注入
- 硬性的 timeout 與重試預算
- 高風險動作的稽核 log

## 要追蹤的指標

- 成功率
- 每個任務的平均重試次數
- 恢復時間
- 每個成功任務的成本
- 失敗類別分佈

## 事件處理模式

失敗暴增時：
1. 凍結新的 rollout
2. 擷取有代表性的 trace
3. 隔離出問題的路徑
4. 用最小的安全變更修補
5. 跑 regression 加安全檢查
6. 逐步恢復

## 部署整合

這個 skill 可以搭配：
- PM2 工作流
- systemd 服務
- container 編排器
- CI/CD gate
