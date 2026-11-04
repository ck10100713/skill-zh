---
name: vendor-check
description: 跨所有已連線的系統（CLM、CRM、email、文件儲存）檢查與供應商的現有合約狀態，附缺口分析和即將到來的期限。在供應商 onboarding 或續約、需要彙整已簽和缺少的文件（MSA、DPA、SOW），或檢查即將到期的合約和存續義務時使用。
argument-hint: "[供應商名稱]"
---

# /vendor-check -- 供應商合約狀態

> 如果看到不認識的 placeholder，或想確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

跨所有已連線的系統，檢查與供應商的現有合約狀態。提供這段法律關係的彙整檢視。

**重要**：這個指令協助法務工作流程，但不提供法律意見。合約狀態報告應由合格的法律專業人員對照原始文件驗證。

## 呼叫方式

```
/vendor-check [vendor name]
```

如果沒有提供供應商名稱，請使用者指定要檢查哪一家供應商。

## 工作流程

### 步驟 1：辨識供應商

從使用者接收供應商名稱。處理常見的名稱變體：
- 法定全名 vs. 商業名稱（例如「Alphabet Inc.」vs.「Google」）
- 縮寫（例如「AWS」vs.「Amazon Web Services」）
- 母公司/子公司關係

如果供應商名稱有歧義，請使用者釐清。

### 步驟 2：搜尋已連線的系統

依優先順序，在所有可用的已連線系統中搜尋該供應商：

#### CLM（合約生命週期管理）-- 有連線的話
搜尋涉及該供應商的所有合約：
- 有效的合約
- 已到期的合約（最近 3 年）
- 協商中或等待簽署的合約
- 修訂和附件

#### CRM -- 有連線的話
搜尋供應商/帳號的 record：
- 帳號狀態和關係類型
- 相關的 opportunity 或 deal
- 供應商法務/合約團隊的聯絡資訊

#### Email -- 有連線的話
搜尋最近的相關往來信件：
- 與合約相關的 email（最近 6 個月）
- NDA 或合約附件
- 協商的 thread

#### 文件（例如 Box、Egnyte、SharePoint）-- 有連線的話
搜尋：
- 已簽署的合約
- Redline 和草稿
- 盡職調查資料

#### 聊天（例如 Slack、Teams）-- 有連線的話
搜尋最近的提及：
- 涉及這家供應商的合約申請
- 關於這家供應商的法務問題
- 相關的團隊討論（最近 3 個月）

### 步驟 3：彙整合約狀態

對找到的每份合約，回報：

| 欄位 | 詳細內容 |
|-------|---------|
| **Agreement Type** | NDA、MSA、SOW、DPA、SLA、授權合約等 |
| **Status** | Active、Expired、In Negotiation、Pending Signature |
| **Effective Date** | 合約何時開始 |
| **Expiration Date** | 何時到期或續約 |
| **Auto-Renewal** | Yes/No，附續約期間和通知期 |
| **Key Terms** | 責任上限、準據法、終止條款 |
| **Amendments** | 已存檔的任何修訂或附件 |

### 步驟 4：缺口分析

找出哪些合約存在，以及可能缺少什麼：

```
## Agreement Coverage

[CHECK] NDA -- [status]
[CHECK/MISSING] MSA -- [status or "Not found"]
[CHECK/MISSING] DPA -- [status or "Not found"]
[CHECK/MISSING] SOW(s) -- [status or "Not found"]
[CHECK/MISSING] SLA -- [status or "Not found"]
[CHECK/MISSING] Insurance Certificate -- [status or "Not found"]
```

依關係類型，標記可能需要的任何缺口（例如有 MSA 但沒有 DPA，而供應商會處理個人資料）。

### 步驟 5：產出報告

輸出彙整報告：

```
## Vendor Agreement Status: [Vendor Name]

**Search Date**: [today's date]
**Sources Checked**: [list of systems searched]
**Sources Unavailable**: [list of systems not connected, if any]

## Relationship Overview

**Vendor**: [full legal name]
**Relationship Type**: [vendor/partner/customer/etc.]
**CRM Status**: [if available]

## Agreement Summary

### [Agreement Type 1] -- [Status]
- **Effective**: [date]
- **Expires**: [date] ([auto-renews / does not auto-renew])
- **Key Terms**: [summary of material terms]
- **Location**: [where the executed copy is stored]

### [Agreement Type 2] -- [Status]
[etc.]

## Gap Analysis

[What's in place vs. what may be needed]

## Upcoming Actions

- [Any approaching expirations or renewal deadlines]
- [Required agreements not yet in place]
- [Amendments or updates that may be needed]

## Notes

[Any relevant context from email/chat searches]
```

### 步驟 6：處理缺少的來源

如果關鍵系統沒有透過 MCP 連線：

- **沒有 CLM**：註明沒有連接 CLM。建議使用者手動查看自己的 CLM。回報在其他系統找到的內容。
- **沒有 CRM**：略過 CRM 的背景資訊。註明這個缺口。
- **沒有 Email**：註明沒有搜尋 email。建議使用者自己在 email 搜尋「[vendor name] agreement」或「[vendor name] NDA」。
- **沒有文件**：註明沒有搜尋文件儲存。

一定要清楚說明檢查了哪些來源、沒檢查哪些，讓使用者知道報告的完整程度。

## 備註

- 如果在任何已連線的系統都找不到合約，要清楚回報，並問使用者合約是不是存放在其他地方
- 對於供應商集團（例如有多家子公司的供應商），問使用者要檢查特定的實體還是整個集團
- 標記已到期、但可能仍有存續義務（保密、賠償等）的合約
- 如果合約即將到期（90 天內），要醒目地標出來
