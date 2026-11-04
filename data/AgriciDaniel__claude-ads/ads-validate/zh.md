---
name: ads-validate
description: "驗證 Claude Ads 的契約、評分輸入、run bundle、capability、來源新鮮度、安全、安裝、解除安裝或發布就緒度。適用於 ads validate、ads status、ads next、成熟度檢查、依所有權 manifest 解除安裝、保留無關的 ads-* skill、checksum 驗證、preflight、QA 或發布稽核。"
---

# 驗證 Claude Ads

挑最窄的驗證目標：

- 契約或 bundle：用確定性的核心驗證器。
- 分數：驗證控制項、findings、分類權重和涵蓋率。
- Run：驗證 manifest 的完整性、來源脈絡、隱私、worker 狀態和輸出 artifact。
- Capability：要求有實作、fixture、測試、來源和誠實的模式。
- Repository：執行確定性、路由、安全、installer、輸出、證據、打包和新鮮度的關卡。
- Release：派出一個全新 context 的發布驗證者。

回傳機器可讀的通過/失敗結果、最高優先的阻礙、確切的證據和復原步驟。絕對不要因為文件寫得漂亮，或先前的 release 通過了，就把成熟度往上調。過期的證據和被跳過的遠端 CI，都會讓就緒度降級。

重新驗證或降級的決定，歸 `ads-research` 管。如果過期的說法因為來源或檔案系統存取不可用而無法重新驗證，就回傳一個失敗的最新證據檢查，把該說法在這次 run 中降級，並在去要缺少的存取權之前，先擋下依賴它的 release-current 主張。

## 安裝與解除安裝的驗證

解除安裝只能移除對應的 Claude Ads 所有權 manifest 裡的確切路徑。在刪除任何東西之前，先驗證整份 manifest 和設定的根目錄邊界。如果 manifest 不存在、無效、不相符或不安全，就在刪除任何東西之前停下來，要求人工審查。絕對不要用 `ads-*` 的 glob 去找目標；像 `ads-weather` 這種無關的 skill 必須原封不動。

拒絕 pipe 進 shell 的安裝指示。安全的安裝要用 host 原生的 installer，或經過本機檢查的 checkout/壓縮檔；壓縮檔在執行之前，要先用可信的 release 管道驗證 SHA-256 checksum。
