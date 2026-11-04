---
name: deploy-checklist
description: 上線前驗證檢查清單。要發 release、deploy 帶有資料庫 migration 或 feature flag 的變更、上 production 前確認 CI 狀態和核准，或事先記錄 rollback 觸發條件時使用。
argument-hint: "[service or release name]"
---

# /deploy-checklist

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

產生一份上線前檢查清單，在發布前確認準備就緒。

## 用法

```
/deploy-checklist $ARGUMENTS
```

## 輸出

```markdown
## Deploy Checklist: [Service/Release]
**Date:** [Date] | **Deployer:** [Name]

### Pre-Deploy
- [ ] All tests passing in CI
- [ ] Code reviewed and approved
- [ ] No known critical bugs in release
- [ ] Database migrations tested (if applicable)
- [ ] Feature flags configured (if applicable)
- [ ] Rollback plan documented
- [ ] On-call team notified

### Deploy
- [ ] Deploy to staging and verify
- [ ] Run smoke tests
- [ ] Deploy to production (canary if available)
- [ ] Monitor error rates and latency for 15 min
- [ ] Verify key user flows

### Post-Deploy
- [ ] Confirm metrics are nominal
- [ ] Update release notes / changelog
- [ ] Notify stakeholders
- [ ] Close related tickets

### Rollback Triggers
- Error rate exceeds [X]%
- P50 latency exceeds [X]ms
- [Critical user flow] fails
```

## 客製化

跟我說說你的 deploy 狀況，我會客製這份清單：
- 「我們有用 feature flag」→ 加上 flag 驗證步驟
- 「這次包含資料庫 migration」→ 加上 migration 專屬檢查
- 「這是會破壞相容性的 API 變更」→ 加上通知 API 使用方的步驟

## 如果有連接 connector

如果有連接 **~~source control**：
- 拉出 release 的 diff 和變更清單
- 確認所有 PR 都已核准並 merge

如果有連接 **~~CI/CD**：
- 自動檢查 build 和測試狀態
- deploy 前確認 pipeline 是綠的

如果有連接 **~~monitoring**：
- 依目前的基準線預先填好 rollback 觸發門檻
- 設定 deploy 後的指標監看

## 小提醒

1. **每次 deploy 前都跑一遍**：連例行的也要。清單可以避免「我忘了……」。
2. **客製一次，重複使用**：告訴我你的技術棧，我會記住你的 deploy 流程。
3. **把 rollback 標準寫進去**：要在 deploy 之前就決定什麼時候 rollback，不是 deploy 到一半才決定。
