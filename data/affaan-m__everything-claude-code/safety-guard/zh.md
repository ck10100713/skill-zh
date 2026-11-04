---
name: safety-guard
description: "用三種模式防範破壞性操作：Careful 攔下危險指令（rm -rf、git push --force、DROP TABLE）要求確認，Freeze 把寫入鎖在單一目錄，Guard 兩者合併。這只是建議性質：由 agent 自己套用這些規則，沒有附帶 hook。在正式環境作業、讓 agent 自主執行、限制只能編輯某個目錄，或進行 migration、deploy、資料變更時使用。"
metadata:
  origin: ECC
---

# Safety Guard：防止破壞性操作

## 何時使用

- 在正式環境作業時
- Agent 自主執行時（full-auto 模式）
- 想把編輯限制在特定目錄時
- 進行敏感操作時（migration、deploy、資料變更）

## 運作方式

三種保護模式。它們是 agent 要遵守的指示，不是強制攔截（見[強制執行](#強制執行)）。

### 模式 1：Careful 模式

執行破壞性指令之前，agent 會先停下來警告：

```
Watched patterns:
- rm -rf (especially /, ~, or project root)
- git push --force
- git reset --hard
- git checkout . (discard all changes)
- DROP TABLE / DROP DATABASE
- docker system prune
- kubectl delete
- chmod 777
- sudo rm
- npm publish (accidental publishes)
- Any command with --no-verify
```

偵測到時：說明這個指令會做什麼、請求確認、建議比較安全的替代做法。

### 模式 2：Freeze 模式

把檔案編輯鎖在特定的目錄樹，例如：「freeze edits to `src/components/`」。

Agent 不會在 `src/components/` 之外 Write/Edit，如果某個改動需要動到外面，會解釋原因。想讓 agent 專心處理一個區塊、不碰無關程式碼時很好用。

### 模式 3：Guard 模式（Careful + Freeze 合併）

兩種保護同時啟動，例如：「guard mode, write only to `src/api/`, read anything」。

Agent 什麼都能讀，但只會寫入 `src/api/`，而且執行任何破壞性指令前都會先問。

### 解除

告訴 agent 不要再套用這些規則。

## 強制執行

這個 skill 只是建議性質。ECC 沒有附 `/safety-guard` 指令，也沒有對應的 hook，所以違反這些規則的 tool call 不會被擋下來。想要不靠 agent 的強制攔截，請用 Claude Code 的[權限 deny 規則](https://code.claude.com/docs/en/permissions)（例如 `Bash(rm -rf *)`）或 [PreToolUse hook](https://code.claude.com/docs/en/hooks)。

## 整合

- `codex -a never` 的 session 預設啟用
- 搭配 ECC 2.0 的可觀測性風險評分一起使用
