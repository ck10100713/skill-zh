---
name: api-connector-builder
description: 完全比照目標 repo 既有的整合模式，建立新的 API connector 或 provider。想多加一個整合、又不想另外發明第二套架構時使用。
metadata:
  version: "1.0.0"
  origin: ECC direct-port adaptation
---

# API Connector Builder

當工作是要加上一個符合 repo 原生做法的整合介面，而不只是一個通用的 HTTP client 時用。

重點是比照宿主 repo 的模式：

- connector 的檔案配置
- 設定 schema
- 驗證模型
- 錯誤處理
- 測試風格
- 註冊/探索的接線

## 何時使用

- 「幫這個專案做一個 Jira connector」
- 「照現有的模式加一個 Slack provider」
- 「替這個 API 建一個新的整合」
- 「做一個符合 repo connector 風格的 plugin」

## 護欄

- repo 已經有整合架構時，不要另外發明新的
- 不要只從廠商文件開始；先從 repo 裡既有的 connector 開始
- repo 預期有 registry 接線、測試和文件時，不要只做到傳輸層的程式碼
- repo 有比較新的現行模式時，不要盲目照抄舊的 connector

## 工作流程

### 1. 學會這個 repo 的風格

至少檢視 2 個既有的 connector/provider，並整理出：

- 檔案配置
- 抽象邊界
- 設定模型
- 重試 / 分頁的慣例
- registry hook
- 測試 fixture 和命名

### 2. 縮小目標整合的範圍

只定義 repo 真正需要的介面：

- 驗證流程
- 關鍵實體
- 核心的讀寫操作
- 分頁和速率限制
- webhook 或輪詢模型

### 3. 以 repo 原生的分層建構

典型的切分：

- 設定/schema
- client/傳輸層
- 對應層
- connector/provider 進入點
- 註冊
- 測試

### 4. 對照來源模式驗證

新的 connector 在 codebase 裡看起來應該理所當然，而不是從另一個生態系移植過來的。

## 參考形狀

### Provider 風格

```text
providers/
  existing_provider/
    __init__.py
    provider.py
    config.py
```

### Connector 風格

```text
integrations/
  existing/
    client.py
    models.py
    connector.py
```

### TypeScript plugin 風格

```text
src/integrations/
  existing/
    index.ts
    client.ts
    types.ts
    test.ts
```

## 品質檢查表

- [ ] 符合 repo 裡既有的整合模式
- [ ] 有設定驗證
- [ ] 驗證和錯誤處理都是明確的
- [ ] 分頁/重試行為遵循 repo 的慣例
- [ ] registry/探索的接線完整
- [ ] 測試呼應宿主 repo 的風格
- [ ] repo 預期的話，文件/範例也已更新

## 相關 Skill

- `backend-patterns`
- `mcp-server-patterns`
- `github-ops`
