---
name: healthcare-phi-compliance
description: "醫療應用的受保護健康資訊（PHI）與 PII 合規模式：資料分類、列級存取控制、防竄改的稽核軌跡、schema 標記，以及常見的外洩管道，例如 log、URL 和瀏覽器儲存。程式碼會碰到病人或臨床人員資料、實作 HIPAA 或 GDPR 存取控制，或是稽核醫療系統的資料外洩風險時使用。"
metadata:
  version: "1.0.0"
  origin: Health1 Super Speciality Hospitals — contributed by Dr. Keyur Patel
---

# Healthcare PHI/PII Compliance Patterns

在醫療應用中保護病人資料、臨床人員資料和財務資料的模式。適用於 HIPAA（美國）、DISHA（印度）、GDPR（歐盟），以及一般的醫療資料保護。

## When to Use

- 建構任何會碰到病人紀錄的功能
- 為臨床系統實作存取控制或驗證
- 設計醫療資料的資料庫 schema
- 建構會回傳病人或臨床人員資料的 API
- 實作稽核軌跡或 logging
- review 程式碼有沒有資料外洩的弱點
- 為多租戶醫療系統設定 Row-Level Security（RLS）

## How It Works

醫療資料保護分三層運作：**分類**（什麼是敏感的）、**存取控制**（誰能看到）、**稽核**（誰真的看過）。

### Data Classification

**PHI（Protected Health Information）**：任何能識別病人、*而且*跟其健康有關的資料：病人姓名、出生日期、地址、電話、email、國民身分證字號（SSN、Aadhaar、NHS number）、病歷號、診斷、用藥、檢驗結果、影像、保險單和理賠細節、預約和住院紀錄，或是上述任意組合。

醫療系統中的 **PII（非病人的敏感資料）**：臨床人員/員工的個人資料、醫師的費用結構和撥款金額、員工薪資和銀行資料、廠商付款資訊。

### Access Control: Row-Level Security

```sql
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;

-- 依機構限定存取範圍
CREATE POLICY "staff_read_own_facility"
  ON patients FOR SELECT TO authenticated
  USING (facility_id IN (
    SELECT facility_id FROM staff_assignments
    WHERE user_id = auth.uid() AND role IN ('doctor','nurse','lab_tech','admin')
  ));

-- 稽核 log：只能新增（防竄改）
CREATE POLICY "audit_insert_only" ON audit_log FOR INSERT
  TO authenticated WITH CHECK (user_id = auth.uid());
CREATE POLICY "audit_no_modify" ON audit_log FOR UPDATE USING (false);
CREATE POLICY "audit_no_delete" ON audit_log FOR DELETE USING (false);
```

### Audit Trail

每一次 PHI 的存取或修改都必須記錄：

```typescript
interface AuditEntry {
  timestamp: string;
  user_id: string;
  patient_id: string;
  action: 'create' | 'read' | 'update' | 'delete' | 'print' | 'export';
  resource_type: string;
  resource_id: string;
  changes?: { before: object; after: object };
  ip_address: string;
  session_id: string;
}
```

### Common Leak Vectors

**錯誤訊息：** 丟給 client 的錯誤訊息裡，絕對不要包含能識別病人的資料。細節只在伺服器端記 log。

**Console 輸出：** 絕對不要記錄完整的病人物件。用不透明的內部紀錄 ID（UUID），不要用病歷號、國民身分證字號或姓名。

**URL 參數：** 絕對不要把能識別病人的資料放在可能出現在 log 或瀏覽器歷史紀錄中的 query string 或路徑片段。只用不透明的 UUID。

**瀏覽器儲存：** 絕對不要把 PHI 存在 localStorage 或 sessionStorage。PHI 只放在記憶體裡，要用時再抓。

**Service role key：** 絕對不要在 client 端程式碼使用 service_role key。一律使用 anon/publishable key，讓 RLS 來強制存取控制。

**Log 與監控：** 絕對不要記錄完整的病人紀錄。只用不透明的紀錄 ID（不要用病歷號）。把 stack trace 送到錯誤追蹤服務之前，要先清理過。

### Database Schema Tagging

在 schema 層級標記 PHI/PII 欄位：

```sql
COMMENT ON COLUMN patients.name IS 'PHI: patient_name';
COMMENT ON COLUMN patients.dob IS 'PHI: date_of_birth';
COMMENT ON COLUMN patients.aadhaar IS 'PHI: national_id';
COMMENT ON COLUMN doctor_payouts.amount IS 'PII: financial';
```

### Deployment Checklist

每次部署之前：
- 錯誤訊息或 stack trace 裡沒有 PHI
- console.log/console.error 裡沒有 PHI
- URL 參數裡沒有 PHI
- 瀏覽器儲存裡沒有 PHI
- client 端程式碼裡沒有 service_role key
- 所有 PHI/PII 資料表都啟用 RLS
- 所有資料修改都有稽核軌跡
- 已設定 session timeout
- 所有 PHI endpoint 都有 API 驗證
- 已驗證跨機構的資料隔離

## Examples

### Example 1: Safe vs Unsafe Error Handling

```typescript
// BAD：在錯誤裡洩漏 PHI
throw new Error(`Patient ${patient.name} not found in ${patient.facility}`);

// GOOD：通用的錯誤，細節只在伺服器端記 log，而且只用不透明的 ID
logger.error('Patient lookup failed', { recordId: patient.id, facilityId });
throw new Error('Record not found');
```

### Example 2: RLS Policy for Multi-Facility Isolation

```sql
-- A 機構的醫師看不到 B 機構的病人
CREATE POLICY "facility_isolation"
  ON patients FOR SELECT TO authenticated
  USING (facility_id IN (
    SELECT facility_id FROM staff_assignments WHERE user_id = auth.uid()
  ));

-- 測試：用 doctor-facility-a 登入，查詢 facility-b 的病人
-- 預期：回傳 0 筆
```

### Example 3: Safe Logging

```typescript
// BAD：記錄了可識別的病人資料
console.log('Processing patient:', patient);

// GOOD：只記錄不透明的內部紀錄 ID
console.log('Processing record:', patient.id);
// 注意：就連 patient.id 也應該是不透明的 UUID，不是病歷號
```
