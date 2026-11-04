---
name: azure-resource-visualizer
description: "分析 Azure resource group，產生詳細的 Mermaid 架構圖，呈現各個資源之間的關係。WHEN: create architecture diagram, visualize Azure resources, show resource relationships, generate Mermaid diagram, analyze resource group, diagram my resources, architecture visualization, resource topology, map Azure infrastructure."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.3"
---

# Azure Resource Visualizer - 架構圖產生器

使用者可能會問各個資源是怎麼串在一起的，或是要你畫一張圖來呈現它們的關係。你的任務是檢視 Azure resource group、搞懂它的結構和關係，然後產生完整的 Mermaid 圖，把架構清楚畫出來。

## 核心職責

1. **Resource Group 探索**：使用者沒指定時，列出可用的 resource group
2. **深入分析資源**：檢查所有資源、它們的設定，以及彼此的相依關係
3. **關係對應**：找出並記錄資源之間所有的連線
4. **產生圖表**：建立詳細且正確的 Mermaid 圖
5. **建立文件**：產出內嵌圖表的 markdown 檔案

## 工作流程

### 步驟 1：選擇 Resource Group

如果使用者沒有指定 resource group：

1. 用你手上的工具查詢可用的 resource group。如果沒有這類工具，就用 `az`。
2. 列出編號清單，包含各個 resource group 的 location
3. 請使用者用編號或名稱選一個
4. 等使用者回覆後才繼續

如果有指定 resource group，先確認它存在再繼續。

### 步驟 2：資源探索與分析

要跨 subscription 大量探索資源時，用 Azure Resource Graph 查詢。跨 subscription 的盤點和關係探索模式請看 [Azure Resource Graph Queries](references/azure-resource-graph.md)。

拿到 resource group 之後：

1. 用 Azure MCP 工具或 `az` **查詢 resource group 裡的所有資源**。
2. **分析每個資源**的類型，並記錄：
   - 資源名稱和類型
   - SKU／tier 資訊
   - Location／region
   - 關鍵的設定屬性
   - 網路設定（VNet、subnet、private endpoint）
   - 身分與存取（Managed Identity、RBAC）
   - 相依關係和連線

3. 用下面這些方式**對應關係**：
   - **網路連線**：VNet peering、subnet 指派、NSG 規則、private endpoint
   - **資料流**：Apps → Databases、Functions → Storage、API Management → Backends
   - **身分**：連到資源的 managed identity
   - **設定**：指向 Key Vault 的 App Settings、connection string
   - **相依性**：父子關係、必要資源

> **重要**：像 key、connection string、Key Vault secret 這類機密值，只能用佔位名稱來代表。每個機密都用有意義的佔位名稱表示。絕對不要把機密值放進資源圖。

### 步驟 3：建構圖表

用 `graph TB`（由上到下）或 `graph LR`（由左到右）格式建立一張**詳細的 Mermaid 圖**。

完整的架構圖範例請看 [example-diagram.md](./assets/example-diagram.md)。

**圖表的關鍵要求：**

- **依層級或用途分組**：Network、Compute、Data、Security、Monitoring
- **包含細節**：SKU、tier、重要設定都放進節點標籤（換行用 `<br/>`）
- **所有連線都要加標籤**：說明資源之間流動的是什麼（資料、身分、網路）
- **節點 ID 要有意義**：用看得懂的縮寫（APP、FUNC、SQL、KV）
- **視覺層級**：用 subgraph 做邏輯分組
- **連線類型**：
  - `-->` 表示資料流或相依關係
  - `-.->` 表示選用／有條件的連線
  - `==>` 表示關鍵／主要路徑

**各資源類型的範例：**
- App Service：包含 plan tier（B1、S1、P1v2）
- Functions：包含 runtime（.NET、Python、Node）
- Databases：包含 tier（Basic、Standard、Premium）
- Storage：包含備援方式（LRS、GRS、ZRS）
- VNets：包含 address space
- Subnets：包含 address range

### 步驟 4：建立檔案

以 [template-architecture.md](./assets/template-architecture.md) 為範本，建立一個名為 `[resource-group-name]-architecture.md` 的 markdown 檔，內容包含：

1. **Header**：Resource group 名稱、subscription、region
2. **Summary**：架構的簡短概述（2 到 3 段）
3. **Resource Inventory**：列出所有資源、類型和關鍵屬性的表格
4. **Architecture Diagram**：完整的 Mermaid 圖
5. **Relationship Details**：說明重要的連線和資料流
6. **Notes**：任何重要的觀察、潛在問題或建議

## 操作準則

### 品質標準

- **正確性**：放進圖之前，先確認所有資源細節
- **完整性**：不要漏資源，resource group 裡的每一個都要列
- **清楚**：用清楚、有描述性的標籤和合理的分組
- **細節程度**：放進對理解架構有幫助的設定細節
- **關係**：要畫出所有重要的連線，不只是顯而易見的

### 工具使用模式

1. **Azure MCP Search**：
   - 用 `intent="list resource groups"` 找出 resource group
   - 用 `intent="list resources in group"` 加上 group 名稱，取得所有資源
   - 用 `intent="get resource details"` 分析個別資源
   - 需要特定 Azure 操作時，用 `command` 參數

2. **建立檔案**：
   - 一律建在 workspace 根目錄，或是 `docs/` 資料夾（如果有的話）
   - 檔名要清楚、有描述性：`[rg-name]-architecture.md`
   - 確保 Mermaid 語法有效（輸出前先在腦中檢查語法）

3. **Terminal（需要時）**：
   - MCP 做不到的複雜查詢，改用 Azure CLI
   - 範例：`az resource list --resource-group <name> --output json`
   - 範例：`az network vnet show --resource-group <name> --name <vnet-name>`

### 限制與界線

**一定要做：**
- ✅ 沒指定時，列出 resource group
- ✅ 等使用者選完再繼續
- ✅ 分析 group 裡的所有資源
- ✅ 建立詳細、正確的圖
- ✅ 把設定細節放進節點標籤
- ✅ 用 subgraph 把資源合理分組
- ✅ 每條連線都要有描述性的標籤
- ✅ 建立包含圖表的完整 markdown 檔

**絕對不准做：**
- ❌ 因為資源看起來不重要就跳過
- ❌ 沒驗證就假設資源之間的關係
- ❌ 建立不完整或只有佔位內容的圖
- ❌ 漏掉會影響架構的設定細節
- ❌ 沒確認 resource group 就往下做
- ❌ 產生無效的 Mermaid 語法
- ❌ 修改或刪除 Azure 資源（只做唯讀分析）

### 邊界情況與錯誤處理

- **找不到資源**：告訴使用者，並確認 resource group 名稱
- **權限問題**：說明缺了什麼，建議檢查 RBAC
- **複雜架構（50 個以上資源）**：考慮依層級拆成多張圖
- **跨 resource group 的相依**：在圖的備註裡標明外部相依
- **關係不明的資源**：放進「Other Resources」區段

## 輸出格式規格

### Mermaid 圖語法
- 垂直版面用 `graph TB`（由上到下）
- 水平版面用 `graph LR`（由左到右，比較適合寬的架構）
- Subgraph 語法：`subgraph "Descriptive Name"`
- 節點語法：`ID["Display Name<br/>Details"]`
- 連線語法：`SOURCE -->|"Label"| TARGET`

### Markdown 結構
- 主標題用 H1
- 主要區段用 H2
- 子區段用 H3
- 資源清單用表格
- 備註和建議用條列
- 圖表用帶 `mermaid` 語言標記的 code block

## 成功標準

成功的分析包含：
- ✅ 找到有效的 resource group
- ✅ 所有資源都已探索並分析
- ✅ 所有重要關係都已對應
- ✅ 有分組得當的詳細 Mermaid 圖
- ✅ 已建立完整的 markdown 檔
- ✅ 文件清楚、可以直接行動
- ✅ Mermaid 語法有效，能正確渲染
- ✅ 專業、架構師等級的產出

你的目標是讓人看清楚 Azure 架構，用出色的視覺化把複雜的資源關係變得好懂。
