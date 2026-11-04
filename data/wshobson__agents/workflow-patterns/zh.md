---
name: workflow-patterns
description: 依照 Conductor 的 TDD 工作流程實作任務、處理 phase checkpoint、管理任務的 git commit，或了解驗證協定時，使用這個 skill。
version: 1.0.0
---

# Workflow Patterns

用 Conductor 的 TDD 工作流程實作任務、管理 phase checkpoint、處理 git commit，並執行驗證協定，確保整個實作過程的品質。

## When to Use This Skill

- 實作某個 track 的 plan.md 裡的任務
- 遵循 TDD 的 red-green-refactor 循環
- 完成 phase checkpoint
- 管理 git commit 和 note
- 了解品質保證關卡
- 處理驗證協定
- 在 plan 檔案中記錄進度

## Detailed patterns and worked examples

詳細的模式說明放在 `references/details.md`。上面的導覽層不夠用的時候，再去讀那個檔案。

## Best Practices

1. **Never skip RED**：一定要先寫會失敗的測試
2. **Small commits**：每個 commit 一個邏輯變更
3. **Immediate updates**：任務一完成就立刻更新 plan.md
4. **Wait for approval**：絕對不要跳過 checkpoint 驗證
5. **Rich git notes**：寫進有助於日後理解的 context
6. **Coverage discipline**：不接受低於目標的覆蓋率
7. **Quality gates**：標記完成前，先檢查所有關卡
8. **Sequential phases**：依序完成各個 phase
9. **Document deviations**：記下任何與原本計畫不同的變更
10. **Clean state**：每個 commit 之後，程式碼都要維持可運作狀態
11. **Fast feedback**：開發過程中經常跑相關的測試
12. **Clear blockers**：及早處理阻礙，不要繞過去
