---
name: healthcare-emr-patterns
description: 醫療應用的 EMR/EHR 開發模式。臨床安全、就診流程、處方產生、臨床決策支援整合，以及以無障礙為優先的醫療資料輸入 UI。建構 EMR 或 EHR 功能（例如就診流程、處方產生或臨床資料輸入 UI）時使用。
metadata:
  version: "1.0.0"
  origin: Health1 Super Speciality Hospitals — contributed by Dr. Keyur Patel
---

# Healthcare EMR Development Patterns

建構電子病歷（EMR）和電子健康紀錄（EHR）系統的模式。以病人安全、臨床準確度和醫護人員的效率為優先。

## When to Use

- 建構病人就診流程（主訴、檢查、診斷、處方）
- 實作臨床記錄（結構化 + 自由文字 + 語音轉文字）
- 設計附藥物交互作用檢查的處方/用藥模組
- 整合臨床決策支援系統（CDSS）
- 建構附參考範圍標示的檢驗結果顯示
- 為臨床資料實作稽核軌跡
- 設計對醫療人員無障礙的臨床資料輸入 UI

## How It Works

### Patient Safety First

每個設計決策都必須用這句話來檢驗：「這會傷害到病人嗎？」

- 藥物交互作用一定要發出警示，不可默默放行
- 異常的檢驗數值一定要用視覺標示
- 危急的生命徵象一定要觸發升級處置流程
- 沒有稽核軌跡，就不能修改任何臨床資料

### Single-Page Encounter Flow

臨床就診應該在單一頁面上垂直流動，不要切換分頁：

```
Patient Header (sticky — always visible)
├── Demographics, allergies, active medications
│
Encounter Flow (vertical scroll)
├── 1. Chief Complaint (structured templates + free text)
├── 2. History of Present Illness
├── 3. Physical Examination (system-wise)
├── 4. Vitals (auto-trigger clinical scoring)
├── 5. Diagnosis (ICD-10/SNOMED search)
├── 6. Medications (drug DB + interaction check)
├── 7. Investigations (lab/radiology orders)
├── 8. Plan & Follow-up
└── 9. Sign / Lock / Print
```

### Smart Template System

```typescript
interface ClinicalTemplate {
  id: string;
  name: string;             // 例如 "Chest Pain"
  chips: string[];          // 可點擊的症狀 chip
  requiredFields: string[]; // 必填的資料點
  redFlags: string[];       // 觸發無法關閉的警示
  icdSuggestions: string[]; // 事先對應好的診斷碼
}
```

任何範本裡的 red flag 都必須觸發看得見、無法關閉的警示，不是 toast 通知。

### Medication Safety Pattern

```
User selects drug
  → Check current medications for interactions
  → Check encounter medications for interactions
  → Check patient allergies
  → Validate dose against weight/age/renal function
  → If CRITICAL interaction: BLOCK prescribing entirely
  → Clinician must document override reason to proceed past a block
  → If MAJOR interaction: display warning, require acknowledgment
  → Log all alerts and override reasons in audit trail
```

Critical 交互作用**預設會擋下處方**。臨床人員必須明確覆寫，並附上記載在稽核軌跡裡的理由。系統絕不會默默放行 critical 交互作用。

### Locked Encounter Pattern

臨床就診一旦簽署：
- 不允許編輯，只能新增補充紀錄（addendum，一筆另外連結的紀錄）
- 原始紀錄和補充紀錄都會出現在病人的時間軸上
- 稽核軌跡會記錄是誰簽署、什麼時候簽署，以及任何補充紀錄

### UI Patterns for Clinical Data

**生命徵象顯示：** 目前數值搭配正常範圍標示（綠/黃/紅）、與前一次比較的趨勢箭頭、自動計算的臨床評分（NEWS2、qSOFA），以及行內的升級處置指引。

**檢驗結果顯示：** 正常範圍標示、與前一次數值的比較、危急值搭配無法關閉的警示、採檢/分析的時間戳記，以及附預期完成時間的待辦檢驗醫囑。

**處方 PDF：** 一鍵產生，包含病人基本資料、過敏、診斷、藥物細節（學名 + 商品名、劑量、途徑、頻率、療程）、臨床人員簽名欄。

### Accessibility for Healthcare

醫療 UI 的要求比一般網頁 app 更嚴格：
- 對比至少 4.5:1（WCAG AA）：臨床人員在各種光線下工作
- 大的觸控目標（至少 44x44px）：因應戴手套/匆忙的操作
- 鍵盤導覽：給快速輸入資料的進階使用者
- 不要只用顏色表示：永遠把顏色搭配文字/圖示（因為有色盲的臨床人員）
- 所有表單欄位都有螢幕閱讀器標籤
- 臨床警示不要用會自動消失的 toast：臨床人員必須主動確認

### Anti-Patterns

- 把臨床資料存在瀏覽器的 localStorage
- 藥物交互作用檢查默默失敗
- 對危急的臨床警示使用可關閉的 toast
- 用分頁式的就診 UI，把臨床工作流程切碎
- 允許編輯已簽署/已鎖定的就診紀錄
- 顯示臨床資料卻沒有稽核軌跡
- 臨床資料結構使用 `any` 型別

## Examples

### Example 1: Patient Encounter Flow

```
Doctor opens encounter for Patient #4521
  → Sticky header shows: "Rajesh M, 58M, Allergies: Penicillin, Active Meds: Metformin 500mg"
  → Chief Complaint: selects "Chest Pain" template
    → Clicks chips: "substernal", "radiating to left arm", "crushing"
    → Red flag "crushing substernal chest pain" triggers non-dismissable alert
  → Examination: CVS system — "S1 S2 normal, no murmur"
  → Vitals: HR 110, BP 90/60, SpO2 94%
    → NEWS2 auto-calculates: score 8, risk HIGH, escalation alert shown
  → Diagnosis: searches "ACS" → selects ICD-10 I21.9
  → Medications: selects Aspirin 300mg
    → CDSS checks against Metformin: no interaction
  → Signs encounter → locked, addendum-only from this point
```

### Example 2: Medication Safety Workflow

```
Doctor prescribes Warfarin for Patient #4521
  → CDSS detects: Warfarin + Aspirin = CRITICAL interaction
  → UI: red non-dismissable modal blocks prescribing
  → Doctor clicks "Override with reason"
  → Types: "Benefits outweigh risks — monitored INR protocol"
  → Override reason + alert stored in audit trail
  → Prescription proceeds with documented override
```

### Example 3: Locked Encounter + Addendum

```
Encounter #E-2024-0891 signed by Dr. Shah at 14:30
  → All fields locked — no edit buttons visible
  → "Add Addendum" button available
  → Dr. Shah clicks addendum, adds: "Lab results received — Troponin elevated"
  → New record E-2024-0891-A1 linked to original
  → Timeline shows both: original encounter + addendum with timestamps
```
