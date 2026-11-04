---
name: ai-first-engineering
description: 給 AI agent 產出大量實作內容的團隊用的工程運作模型。替一個大部分由 agent 寫成的 codebase 制定團隊流程、review 關卡或擁有權規則時使用。
metadata:
  origin: ECC
---

# AI-First Engineering

替靠 AI 輔助程式碼生成來交付的團隊，設計流程、review 和架構時，用這個 skill。

## 流程上的轉變

1. 規劃的品質，比打字速度重要。
2. Eval 的覆蓋率，比憑感覺的信心重要。
3. Review 的重心，從語法轉到系統行為。

## 架構需求

偏好對 agent 友善的架構：
- 明確的邊界
- 穩定的契約
- 有型別的介面
- 確定性的測試

避免把隱含的行為散落在看不見的慣例裡。

## AI-First 團隊的 Code Review

Review 要看：
- 行為回歸
- 安全上的假設
- 資料完整性
- 失敗處理
- 上線安全性

自動化已經涵蓋的風格問題，盡量少花時間。

## 招募與評估訊號

強的 AI-first 工程師會：
- 乾淨地拆解模糊的工作
- 定義可衡量的驗收標準
- 寫出訊號量高的 prompt 和 eval
- 在交付壓力下仍堅持風險控管

## 測試標準

對產生出來的程式碼，把測試的標準拉高：
- 被動到的領域，必須有回歸覆蓋
- 明確的 edge case 斷言
- 介面邊界的整合檢查
