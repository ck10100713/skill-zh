---
name: agent-sort
description: 針對特定 repo 建立有證據支撐的 ECC 安裝計畫：用平行的、認得 repo 的審查流程，把 skill、command、rule、hook 和其他項目分進 DAILY 和 LIBRARY 兩個桶子。當 ECC 要修剪成專案真正需要的內容，而不是載入整包時使用。
metadata:
  origin: ECC
---

# Agent Sort

當 repo 需要一個專屬於專案的 ECC 範圍，而不是預設的完整安裝時，用這個 skill。

目標不是猜「感覺有用」的東西。目標是用實際 codebase 的證據，替 ECC 的元件分類。

## 何時使用

- 專案只需要 ECC 的一部分，完整安裝太吵
- Repo 的技術堆疊很明確，但沒人想一個一個手動挑 skill
- 團隊想要一個可重複的安裝決策，靠 grep 證據，不靠意見
- 你需要把「每次都載入的日常工作流程」跟「可搜尋的資料庫或參考資料」分開
- Repo 已經偏離，載入了錯的語言、rule 或 hook 組合，需要清理

## 不可妥協的規則

- 以目前的 repo 為準，不要用一般性的偏好
- 每個 DAILY 的決定都必須引用具體的 repo 證據
- LIBRARY 不是「刪除」，而是「保持可取用，但預設不載入」
- 不要安裝目前 repo 用不到的 hook、rule 或 script
- 優先用 ECC 原生的機制，不要引進第二套安裝系統

## 輸出

依序產出這些成品：

1. DAILY 清單
2. LIBRARY 清單
3. 安裝計畫
4. 驗證報告
5. 如果專案想要，再加一個選用的 `skill-library` router

## 分類模型

只用兩個桶子：

- `DAILY`
  - 這個 repo 每個 session 都該載入
  - 跟 repo 的語言、框架、工作流程或操作員介面高度吻合
- `LIBRARY`
  - 值得保留，但不值得預設載入
  - 應該能透過搜尋、router skill 或選擇性的手動使用找到

## 證據來源

分類之前，先用 repo 本地的證據：

- 副檔名
- 套件管理工具和 lockfile
- 框架設定檔
- CI 和 hook 設定
- build/test script
- import 和相依性清單
- 明確描述技術堆疊的 repo 文件

好用的指令：

```bash
rg --files
rg -n "typescript|react|next|supabase|django|spring|flutter|swift"
cat package.json
cat pyproject.toml
cat Cargo.toml
cat pubspec.yaml
cat go.mod
```

## 平行審查流程

如果能用平行的 subagent，就把審查拆成這幾輪：

1. Agents
   - 分類 `agents/*`
2. Skills
   - 分類 `skills/*`
3. Commands
   - 分類 `commands/*`
4. Rules
   - 分類 `rules/*`
5. Hooks 和 scripts
   - 分類 hook 介面、MCP 健康檢查、輔助 script 和作業系統相容性
6. Extras
   - 分類 context、範例、MCP 設定、範本和指引文件

如果沒有 subagent 可用，就依序跑同樣的幾輪。

## 核心工作流程

### 1. 讀 repo

分類任何東西之前，先確認真實的技術堆疊：

- 使用的語言
- 使用的框架
- 主要的套件管理工具
- 測試堆疊
- lint/format 堆疊
- 部署或 runtime 範圍
- 已經存在的操作員整合

### 2. 建立證據表

每個候選項目都要記錄：

- 元件路徑
- 元件類型
- 建議的桶子
- repo 證據
- 簡短理由

用這個格式：

```text
skills/frontend-patterns | skill | DAILY | 84 個 .tsx 檔案，有 next.config.ts | 核心前端堆疊
skills/django-patterns   | skill | LIBRARY | 沒有 .py 檔案，沒有 pyproject.toml       | 這個 repo 沒在用
rules/typescript/*       | rules | DAILY | package.json + tsconfig.json            | 使用中的 TS repo
rules/python/*           | rules | LIBRARY | 零個 Python 原始檔             | 只保持可取用
```

### 3. 決定 DAILY 還是 LIBRARY

符合以下情況就升為 `DAILY`：

- repo 明確使用對應的技術堆疊
- 元件夠通用，每個 session 都有幫助
- repo 本來就依賴對應的 runtime 或工作流程

符合以下情況就降為 `LIBRARY`：

- 元件不在技術堆疊內
- repo 以後可能會用到，但不是每天
- 它增加了 context 負擔，卻沒有立即的關聯

### 4. 建立安裝計畫

把分類結果轉成動作：

- DAILY skill -> 安裝或保留在 `.claude/skills/`
- DAILY command -> 只有仍然有用時，才保留成明確的 shim
- DAILY rule -> 只安裝對應語言的組合
- DAILY hook/script -> 只保留相容的
- LIBRARY 項目 -> 透過搜尋或 `skill-library` 保持可取用

如果 repo 已經在用選擇性安裝，就更新那份計畫，不要另建一套系統。

### 5. 建立選用的 library router

如果專案想要一個可搜尋的 library 介面，就建立：

- `.claude/skills/skill-library/SKILL.md`

那個 router 應該包含：

- 簡短說明 DAILY 和 LIBRARY 的差別
- 分組的觸發關鍵字
- library 參考資料放在哪裡

不要把每個 skill 的內容都複製進 router。

### 6. 驗證結果

計畫套用之後，驗證：

- 每個 DAILY 檔案都在預期的位置
- 過時的語言 rule 沒有繼續啟用
- 沒有安裝不相容的 hook
- 最後的安裝結果真的符合 repo 的技術堆疊

回傳一份精簡的報告，包含：

- DAILY 的數量
- LIBRARY 的數量
- 移除的過時項目
- 尚未解決的問題

## 交接

如果下一步是互動式安裝或修復，交接給：

- `configure-ecc`

如果下一步是清理重疊或審查目錄，交接給：

- `skill-stocktake`

如果下一步是更大範圍的 context 修剪，交接給：

- `strategic-compact`

## 輸出格式

依這個順序回傳結果：

```text
STACK
- 語言/框架/runtime 摘要

DAILY
- 一律載入的項目，附證據

LIBRARY
- 可搜尋或供參考的項目，附證據

INSTALL PLAN
- 該安裝、移除或轉由 router 處理的項目

VERIFICATION
- 執行過的檢查和尚存的缺口
```
