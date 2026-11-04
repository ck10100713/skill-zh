---
name: "tw-healthcare-regulations"
description: "摸清台灣的醫療法規，包括健保制度、醫療器材分級、藥品登記、遠距醫療規則和健康資料保護。當使用者要為台灣做健康科技產品、需要了解健保、評估醫療器材的法規路徑，或評估遠距醫療合規時使用這個 skill，就算他們說的是「在台灣賣醫療器材」、「健保怎麼運作」、「遠距醫療法規」或「台灣的健康資料隱私」也一樣。"
metadata:
  category: "WP-12 產業知識"
  tags: ["industry", "taiwan", "healthcare", "regulation"]
---

# 台灣醫療法規

## 框架

```
IRON LAW: NHI Shapes Everything in Taiwan Healthcare
（鐵律：在台灣醫療，健保決定一切）

台灣的全民健保涵蓋 99.9% 的人口。
台灣任何醫療產品或服務的策略，都必須把健保算進去：
要嘛取得健保給付（走量），要嘛定位成自費/高端（走毛利）。

忽略健保，就像忽略地心引力。
```

### 健保制度概覽

| 面向 | 細節 |
|--------|--------|
| 涵蓋率 | 99.9% 人口（2,300 萬人以上） |
| 單一保險人 | 衛生福利部中央健康保險署（NHIA） |
| 保費 | 投保薪資的 5.17%（分擔：雇主 60%、員工 30%、政府 10%） |
| 部分負擔 | 門診：NT$50-420。住院：5-30%（有上限） |
| 藥價 | NHIA 透過藥品費用目標（DET）訂定給付價格 |
| 年度預算 | 約 NT$800B 以上（每年成長 4-5%） |

### 醫療器材法規路徑

| 等級 | 風險 | 例子 | 核准路徑 | 時程 |
|-------|------|---------|-------------|---------|
| **第一等級** | 低 | 繃帶、壓舌板 | 登記（列冊） | 1-2 個月 |
| **第二等級** | 中 | 血壓計、手術手套 | 技術審查 | 6-12 個月 |
| **第三等級** | 高 | 植入物、AI 診斷軟體 | 完整臨床審查 | 12-24 個月 |
| **SaMD（軟體醫療器材）** | 依預期用途而定 | AI 診斷、臨床決策支援 | 依風險屬第二或第三等級 | 6-24 個月 |

**主管機關**：衛生福利部食品藥物管理署（TFDA）

### 數位健康法規概況

| 類別 | 法規狀態 | 關鍵規則 |
|----------|------------------|---------|
| **遠距醫療** | 疫情後擴大（通訊診察治療辦法） | 允許用於複診、慢性病、偏遠地區。多數情況下初診仍需親自到場。 |
| **AI 診斷** | 適用 SaMD 法規 | 如果 AI 做出/輔助臨床決策，就是醫療器材，需要 TFDA 核准 |
| **健康 app** | 只做保健則不受管 | 如果診斷、治療或監測某個醫療狀況，就跨進醫療器材的範圍 |
| **健康資料** | 個人資料保護法（PDPA）+ 醫療法 | 病歷的保護比一般個資更嚴格。使用資料需要病人同意。 |
| **電子病歷** | 醫療機構電子病歷製作及管理辦法 | 電子病歷系統必須符合衛福部標準。有條件允許雲端儲存。 |

### 數位健康產品的法規決策樹

```
Does your product diagnose, treat, or monitor a medical condition?
├── NO → Not a medical device. General consumer regulations apply.
└── YES → Medical device (SaMD)
    ├── Does it provide clinical decision support?
    │   ├── Autonomous (AI decides) → Class III
    │   └── Assistive (human decides) → Class II
    └── Does it monitor vital signs?
        ├── Clinical grade → Class II-III
        └── Wellness/fitness → Likely not regulated (but verify with TFDA)
```

## 輸出格式

```markdown
# Healthcare Regulatory Assessment: {Product}

## Product Classification
- Type: Medical device / Wellness / SaMD / Telemedicine
- Risk class: I / II / III
- Regulatory body: TFDA / NHIA / None

## Regulatory Pathway
| Step | Action | Timeline | Cost |
|------|--------|----------|------|
| 1 | {regulatory step} | {months} | NT${X} |

## NHI Strategy
- NHI reimbursement: Pursuing / Not pursuing
- If pursuing: {reimbursement category, pricing strategy}
- If not: {self-pay positioning, target market}

## Compliance Checklist
- [ ] TFDA classification confirmed
- [ ] Clinical data requirements identified
- [ ] Data privacy (PDPA + medical records) compliant
- [ ] NHI reimbursement strategy decided
```

## 常見陷阱

- **健保的價格壓力沒有止境**：健保以訂好的價格給付，而且會定期往下修。把事業建立在依賴健保給付上，就得接受毛利隨時間被侵蝕。
- **SaMD 法規快速演變**：TFDA 仍在發展 AI 型醫療器材的框架。今天不受管的，明天可能就需要核准。要積極關注法規變化。
- **可能需要臨床試驗**：第三等級器材和部分第二等級器材需要臨床證據。在台灣做臨床試驗，要預留 12-24 個月和 NT$5-20M 以上。
- **醫院採購靠關係**：台灣的大型醫院（台大、長庚、榮總）有採購委員會，但和醫界關鍵意見領袖（KOL）的關係，對推廣採用至關重要。
- **這是教育性質的指引，不是法規建議**：台灣的醫療法規很複雜，而且常常變動。具體的產品送件請直接諮詢 TFDA，或聘請法規事務顧問。

## 參考資料

- TFDA 送件程序，見 `references/tfda-submission.md`
- 健保給付申請流程，見 `references/nhi-reimbursement.md`
