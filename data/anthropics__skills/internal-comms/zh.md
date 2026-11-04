---
name: internal-comms
description: 一套協助我撰寫各種內部溝通文件的資源，使用我的公司慣用的格式。只要被要求寫任何內部溝通（狀態報告、主管更新、3P 更新、公司電子報、FAQ、事故報告、專案更新等），Claude 都應該使用這個 skill。
license: Complete terms in LICENSE.txt
---

## 什麼時候用這個 skill
要寫內部溝通文件時，這個 skill 適用於：
- 3P 更新（Progress、Plans、Problems，進度、計畫、問題）
- 公司電子報
- FAQ 回覆
- 狀態報告
- 主管更新
- 專案更新
- 事故報告

## 怎麼用這個 skill

要寫任何內部溝通文件：

1. **從需求判斷溝通類型**
2. **從 `examples/` 目錄載入對應的指引檔**：
    - `examples/3p-updates.md` - 給 Progress/Plans/Problems 團隊更新
    - `examples/company-newsletter.md` - 給全公司電子報
    - `examples/faq-answers.md` - 回答常見問題
    - `examples/general-comms.md` - 其他不明確符合上述任何一類的情況
3. **照那個檔案裡的具體指示**處理格式、語氣和內容蒐集

如果溝通類型跟現有的指引都對不上，就問使用者想要的格式，或請他們補充更多背景。

## 關鍵字
3P updates, company newsletter, company comms, weekly update, faqs, common questions, updates, internal comms
