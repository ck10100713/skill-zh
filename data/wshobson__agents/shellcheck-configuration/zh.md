---
name: shellcheck-configuration
description: 精通 ShellCheck 靜態分析的設定與使用，提升 shell script 品質。在建立 lint 基礎設施、修正程式碼問題或確保腳本可攜性時使用。
---

# ShellCheck Configuration and Static Analysis

一份完整指引，教你設定並使用 ShellCheck 來提升 shell script 品質、抓出常見的陷阱，並透過靜態程式碼分析落實最佳實務。

## When to Use This Skill

- 在 CI/CD pipeline 裡為 shell script 設定 lint
- 分析既有的 shell script 找問題
- 理解 ShellCheck 的錯誤碼和警告
- 針對特定專案需求設定 ShellCheck
- 把 ShellCheck 整合進開發工作流程
- 抑制誤報並設定規則集
- 落實一致的程式碼品質標準
- 遷移腳本以通過品質關卡

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Best Practices

1. **在 CI/CD 跑 ShellCheck** - 在 merge 之前就抓出問題
2. **針對你的目標 shell 設定** - 不要把 bash 當成 sh 來分析
3. **把例外寫成文件** - 說明為什麼要抑制這些違規
4. **處理違規** - 不要只是把警告關掉
5. **啟用 strict mode** - 用 `--enable=all`，再小心地排除
6. **定期更新** - 保持 ShellCheck 最新，才有新的檢查
7. **用 pre-commit hook** - 在 push 之前先在本機抓出問題
8. **整合進編輯器** - 開發時取得即時回饋
