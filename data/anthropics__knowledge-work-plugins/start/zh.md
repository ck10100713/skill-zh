---
name: start
description: 設定你的生物研究環境並探索可用的工具。適用於第一次熟悉這個 plugin、檢查已連接哪些文獻、藥物開發或視覺化的 MCP server，或在開始新專案前先盤點可用的分析 skill。
---

# Bio-Research 起手式

> 如果看到不熟悉的佔位符，或需要確認哪些工具已連接，請見 [CONNECTORS.md](../../CONNECTORS.md)。

你正在協助一位生物研究人員熟悉 bio-research plugin。依序走過以下步驟。

## 步驟 1：歡迎

顯示這段歡迎訊息：

```
Bio-Research Plugin

Your AI-powered research assistant for the life sciences. This plugin brings
together literature search, data analysis pipelines,
and scientific strategy — all in one place.
```

## 步驟 2：檢查可用的 MCP Server

列出可用的工具，測試哪些 MCP server 已連接。把結果分組：

**文獻與資料來源：**
- ~~literature database — 生物醫學文獻搜尋
- ~~literature database — 預印本存取（生物與醫學）
- ~~journal access — 學術出版品
- ~~data repository — 協作研究資料（Sage Bionetworks）

**藥物開發與臨床：**
- ~~chemical database — 生物活性化合物資料庫
- ~~drug target database — 藥物標靶探索平台
- ClinicalTrials.gov — 臨床試驗登錄系統
- ~~clinical data platform — 臨床試驗場址排名和平台協助

**視覺化與 AI：**
- ~~scientific illustration — 製作科學圖表和示意圖
- ~~AI research platform — 生物領域的 AI（組織病理學、藥物開發）

回報哪些 server 已連接、哪些還沒設定。

## 步驟 3：盤點可用的 Skill

列出這個 plugin 裡可用的分析 skill：

| Skill | What It Does |
|-------|-------------|
| **Single-Cell RNA QC** | 用 MAD 過濾對 scRNA-seq 資料做品質控制 |
| **scvi-tools** | 單細胞多體學的深度學習（scVI、scANVI、totalVI、PeakVI 等） |
| **Nextflow Pipelines** | 執行 nf-core 流程（RNA-seq、WGS/WES、ATAC-seq） |
| **Instrument Data Converter** | 把實驗儀器輸出轉成 Allotrope ASM 格式 |
| **Scientific Problem Selection** | 選擇研究問題的系統性框架 |

## 步驟 4：選用設定，二進位 MCP Server

說明另外有兩個 MCP server 需要單獨安裝：

- **~~genomics platform**：存取雲端分析資料和工作流程
  安裝：從 https://github.com/10XGenomics/txg-mcp/releases 下載 `txg-node.mcpb`
- **~~tool database**（Harvard MIMS）：科學發現用的 AI 工具
  安裝：從 https://github.com/mims-harvard/ToolUniverse/releases 下載 `tooluniverse.mcpb`

這兩個需要下載二進位檔，屬於選用。

## 步驟 5：問要怎麼幫忙

問研究人員今天在做什麼。依常見的工作流程建議起點：

1. **文獻回顧**：「Search ~~literature database for recent papers on [topic]」
2. **分析定序資料**：「Run QC on my single-cell data」或「Set up an RNA-seq pipeline」
3. **藥物開發**：「Search ~~chemical database for compounds targeting [protein]」或「Find drug targets for [disease]」
4. **資料標準化**：「Convert my instrument data to Allotrope format」
5. **研究策略**：「Help me evaluate a new project idea」

等使用者回應，再引導他們使用合適的工具和 skill。
