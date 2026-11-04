---
name: bash-defensive-patterns
description: 掌握可上線等級 script 的防禦式 Bash 程式設計技巧。在撰寫穩健的 shell script、CI/CD pipeline，或需要容錯與安全的系統工具時使用。
---

# Bash 防禦式模式

用防禦式程式設計技巧、錯誤處理和安全最佳實務，撰寫可上線的 Bash script 的完整指引，用來避開常見陷阱並確保可靠性。

## 何時使用這個 Skill

- 撰寫正式環境的自動化 script
- 建構 CI/CD pipeline 的 script
- 建立系統管理的工具
- 開發有錯誤韌性的部署自動化
- 撰寫必須安全處理邊界情況的 script
- 建構好維護的 shell script 函式庫
- 實作完整的 logging 和監控
- 建立必須跨不同平台運作的 script

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。

## 最佳實務摘要

1. **一律使用 strict mode** - `set -Eeuo pipefail`
2. **所有變數都要加引號** - `"$variable"` 可以防止 word splitting
3. **用 [[]] 做條件判斷** - 比 [ ] 更穩健
4. **實作錯誤攔截** - 優雅地抓到並處理錯誤
5. **驗證所有輸入** - 檢查檔案是否存在、權限、格式
6. **用函式做重複使用** - 用有意義的名稱當前綴
7. **實作結構化的 logging** - 包含時間戳記和等級
8. **支援 dry-run 模式** - 讓使用者預覽變更
9. **安全地處理暫存檔** - 用 mktemp，並用 trap 清理
10. **設計成 idempotent** - script 重跑應該是安全的
11. **記錄需求** - 列出相依套件和最低版本
12. **測試錯誤路徑** - 確保錯誤處理確實能運作
13. **用 `command -v`** - 檢查執行檔時比 `which` 更安全
14. **優先用 printf，不要用 echo** - 跨系統的行為更可預測
