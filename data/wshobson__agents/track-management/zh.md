---
name: track-management
description: 建立、管理或處理 Conductor track（功能、bug 和重構的邏輯工作單位）時使用這個 skill。適用於 spec.md、plan.md 和 track 生命週期操作。
version: 1.0.0
---

# Track Management

建立、管理和完成 Conductor track 的指南。Track 是把功能、bug 和重構，依序經過規格、規劃和實作階段來組織的邏輯工作單位。

## When to Use This Skill

- 建立新的功能、bug 或重構 track
- 撰寫或 review spec.md 檔案
- 建立或更新 plan.md 檔案
- 管理 track 從建立到完成的生命週期
- 了解 track 的狀態標記與慣例
- 使用 tracks.md 登錄表
- 解讀或更新 track 的 metadata

## Detailed patterns and worked examples

詳細的模式說明放在 `references/details.md`。上面的導覽層不夠用的時候，再去讀那個檔案。

## Best Practices

1. **One track, one concern**：每個 track 只專注在單一的邏輯變更
2. **Small phases**：把工作切成每個 phase 最多 3-5 個任務
3. **Verification after phases**：一定要加入驗證任務
4. **Update markers immediately**：邊做邊標記任務狀態
5. **Record SHAs**：完成的任務一定要記下 commit SHA
6. **Review specs before planning**：建立 plan 之前，先確認 spec 完整
7. **Link dependencies**：明確標出 track 之間的相依關係
8. **Archive, don't delete**：保留已完成的 track 供日後參考
9. **Size appropriately**：每個 track 控制在 1-5 天的工作量
10. **Clear acceptance criteria**：每個需求都必須可測試
