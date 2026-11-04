---
name: context-driven-development
description: >-
  在 `conductor/` 目錄中建立並維護專案 context 的成品（product.md、tech-stack.md、workflow.md、tracks.md）。
  可以從零搭建新專案、從既有程式碼庫萃取 context、在實作之前驗證成品之間的一致性，
  並在專案演進時同步各份文件。設定專案、建立或更新產品文件、管理 tech stack 檔案、
  定義開發工作流程、追蹤工作單元、上手既有的程式碼庫，或進行專案鷹架搭建時使用。
version: 1.0.0
---

# Context-Driven Development

把 context 當成跟程式碼並列、被管理的成品來實作和維護的指南，透過結構化的專案文件，讓 AI 的互動前後一致，也讓團隊保持一致。

## 何時使用這個 Skill

- 用 Conductor 設定新專案
- 了解各個 context 成品之間的關係
- 在 AI 輔助的開發 session 之間維持一致性
- 讓團隊成員上手既有的 Conductor 專案
- 決定何時該更新 context 文件
- 管理 greenfield 和 brownfield 專案的 context

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。

## 最佳實務

1. **先讀 context**：開始工作前，一定要先讀相關的成品
2. **小幅更新**：對 context 做漸進式的修改，不要大幅重寫
3. **連結決策**：做實作選擇時，要引用 context
4. **替 context 做版本控制**：把 context 的變更跟程式碼的變更一起 commit
5. **審查 context**：把 context 成品的審查納入 code review
6. **定期驗證**：做重大工作之前，先跑 context 驗證檢查清單
7. **溝通變更**：context 成品有重大變動時，通知團隊
8. **保存歷史**：用 git 追蹤 context 隨時間的演進
9. **質疑過時**：如果 context 感覺不對，就去調查並更新
10. **保持可執行**：每個 context 項目都應該能影響某個決定或行為
