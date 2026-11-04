---
name: setup-zoom-oauth
description: 正確實作 Zoom 驗證。在設定 app 憑證、選擇 OAuth grant、申請 scope、處理 token refresh，或除錯驗證失敗時使用。
---

# /setup-zoom-oauth

當驗證是卡關點，或驗證的選擇會決定整個整合的樣貌時，使用這個 skill。

## 範圍

- App 類型選擇
- OAuth grant 選擇
- Scope 規劃
- Token 交換與 refresh
- 驗證除錯與環境假設

## 工作流程

1. 判斷 app 模型，以及是誰在授權給誰。
2. 選擇正確的 grant 流程。
3. 找出使用者流程所需的最小 scope。
4. 定義 token 的儲存與 refresh 行為。
5. 以上都清楚之後，才導向最深入的相關參考文件。

## 主要參考

- [oauth](../oauth/SKILL.md)
- [general](../general/SKILL.md)
- [rest-api](../rest-api/SKILL.md)

## 常見錯誤

- 在還沒釐清行為者和 tenant 模型之前就選了 grant
- 在確認確切的工作流程之前就申請範圍很廣的 scope
- 忘了 refresh token 的行為和 token 生命週期的處理
- refresh 成功之後，還繼續用舊的 refresh token，而不是存新回傳的那個
- 沒先檢查 app 設定，就把驗證失敗當成 API 失敗
