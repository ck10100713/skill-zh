---
name: signature-request
description: 準備文件並送去電子簽署：跑簽署前檢查清單、設定簽署順序、送出執行。適用於合約定稿準備簽署、送出前核對實體名稱／附件／簽名欄，或設定循序或平行簽署人的 envelope。
argument-hint: "<document or contract to send>"
---

# /signature-request -- 電子簽署流程

> 如果看到不熟悉的佔位符，或需要確認哪些工具已連接，請見 [CONNECTORS.md](../../CONNECTORS.md)。

準備文件進行電子簽署：確認內容完整、設定簽署順序、送出執行。

**重要**：這個指令協助處理法務流程，但不提供法律意見。送簽前請先確認文件已是最終版本。

## 用法

```
/signature-request $ARGUMENTS
```

準備簽署：@$1

## 工作流程

### 步驟 1：接收文件

任何格式的文件都可以：
- **上傳檔案**：PDF、DOCX
- **URL**：~~cloud storage 或 ~~CLM 裡文件的連結
- **參照**：「我們昨天定稿的 Acme Corp MSA」

### 步驟 2：簽署前檢查清單

送簽前先確認：

```markdown
## Pre-Signature Checklist

- [ ] Document is in final, agreed form (no open redlines)
- [ ] All exhibits and schedules are attached
- [ ] Correct legal entity names on signature blocks
- [ ] Dates are correct or left blank for execution date
- [ ] Signature blocks match the authorized signers
- [ ] Any required internal approvals have been obtained
- [ ] Document has been reviewed by appropriate counsel
```

### 步驟 3：設定簽署

收集簽署細節：
- **簽署人**：誰要簽？（姓名、email、職稱）
- **簽署順序**：循序還是平行？
- **內部核准**：對方簽之前，有沒有人需要先核准？
- **副本收件人**：誰要收到完成簽署的文件副本？

### 步驟 4：送出簽署

**如果已連接 ~~e-signature：**
- 建立簽署 envelope／請求
- 設定簽署欄位和順序
- 加上需要的簽名縮寫或日期欄位
- 送出簽署

**如果沒有連接：**
- 產生簽署說明文件
- 提供適合手寫簽名或手動電子簽的文件格式
- 列出所有簽署人和聯絡資訊

## 輸出

```markdown
## Signature Request: [Document Title]

### Document Details
- **Type**: [MSA / NDA / SOW / Amendment / etc.]
- **Parties**: [Party A] and [Party B]
- **Pages**: [X]

### Pre-Signature Check: [PASS / ISSUES FOUND]
[List any issues that need attention before sending]

### Signing Configuration
| Order | Signer | Email | Role |
|-------|--------|-------|------|
| 1 | [Name] | [email] | [Party A Authorized Signatory] |
| 2 | [Name] | [email] | [Party B Authorized Signatory] |

### CC Recipients
- [Name] — [email]

### Status
[Sent for signature / Ready to send / Issues to resolve first]

### Next Steps
- [What to expect after sending]
- [Expected turnaround time]
- [Follow-up if not signed within X days]
```

## 小提醒

1. **仔細檢查實體名稱**：簽署最常見的錯誤就是法律實體名稱寫錯。
2. **確認簽署權限**：確保每位簽署人都有權代表所屬組織簽約。
3. **留一份副本**：簽署完成的副本要在簽完後馬上歸檔到 ~~cloud storage 或 ~~CLM。
