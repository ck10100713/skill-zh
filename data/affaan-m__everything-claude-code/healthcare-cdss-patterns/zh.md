---
name: healthcare-cdss-patterns
description: 臨床決策支援系統（CDSS）的開發模式。藥物交互作用檢查、劑量驗證、臨床評分（NEWS2、qSOFA）、警示嚴重度分級，以及整合進 EMR 工作流程。建構臨床決策支援時使用：藥物交互作用檢查、劑量驗證、臨床評分或警示嚴重度。
metadata:
  version: "1.0.0"
  origin: Health1 Super Speciality Hospitals — contributed by Dr. Keyur Patel
---

# Healthcare CDSS Development Patterns

建構能整合進 EMR 工作流程的臨床決策支援系統（Clinical Decision Support System）的模式。CDSS 模組攸關病人安全，對漏報（false negative）零容忍。

## When to Use

- 實作藥物交互作用檢查
- 建構劑量驗證引擎
- 實作臨床評分系統（NEWS2、qSOFA、APACHE、GCS）
- 設計異常臨床數值的警示系統
- 建構內建安全檢查的用藥醫囑輸入
- 把檢驗結果的解讀跟臨床脈絡整合

## How It Works

CDSS 引擎是一個**零副作用的純函式函式庫**。輸入臨床資料，輸出警示。這樣它就能完全被測試。

三個主要模組：

1. **`checkInteractions(newDrug, currentMeds, allergies)`**：把新藥對照目前的用藥和已知過敏檢查。回傳依嚴重度排序的 `InteractionAlert[]`。使用 `DrugInteractionPair` 資料模型。
2. **`validateDose(drug, dose, route, weight, age, renalFunction)`**：依體重、年齡調整和腎功能調整的規則，驗證開立的劑量。回傳 `DoseValidationResult`。
3. **`calculateNEWS2(vitals)`**：用 `NEWS2Input` 算出 National Early Warning Score 2。回傳 `NEWS2Result`，包含總分、風險等級和升級處置指引。

```
EMR UI
  ↓ (user enters data)
CDSS Engine (pure functions, no side effects)
  ├── Drug Interaction Checker
  ├── Dose Validator
  ├── Clinical Scoring (NEWS2, qSOFA, etc.)
  └── Alert Classifier
  ↓ (returns alerts)
EMR UI (displays alerts inline, blocks if critical)
```

### Drug Interaction Checking

```typescript
interface DrugInteractionPair {
  drugA: string;           // 學名
  drugB: string;           // 學名
  severity: 'critical' | 'major' | 'minor';
  mechanism: string;
  clinicalEffect: string;
  recommendation: string;
}

function checkInteractions(
  newDrug: string,
  currentMedications: string[],
  allergyList: string[]
): InteractionAlert[] {
  if (!newDrug) return [];
  const alerts: InteractionAlert[] = [];
  for (const current of currentMedications) {
    const interaction = findInteraction(newDrug, current);
    if (interaction) {
      alerts.push({ severity: interaction.severity, pair: [newDrug, current],
        message: interaction.clinicalEffect, recommendation: interaction.recommendation });
    }
  }
  for (const allergy of allergyList) {
    if (isCrossReactive(newDrug, allergy)) {
      alerts.push({ severity: 'critical', pair: [newDrug, allergy],
        message: `Cross-reactivity with documented allergy: ${allergy}`,
        recommendation: 'Do not prescribe without allergy consultation' });
    }
  }
  return alerts.sort((a, b) => severityOrder(a.severity) - severityOrder(b.severity));
}
```

交互作用的配對必須是**雙向的**：如果藥物 A 會跟藥物 B 交互作用，那藥物 B 也會跟藥物 A 交互作用。

### Dose Validation

```typescript
interface DoseValidationResult {
  valid: boolean;
  message: string;
  suggestedRange: { min: number; max: number; unit: string } | null;
  factors: string[];
}

function validateDose(
  drug: string,
  dose: number,
  route: 'oral' | 'iv' | 'im' | 'sc' | 'topical',
  patientWeight?: number,
  patientAge?: number,
  renalFunction?: number
): DoseValidationResult {
  const rules = getDoseRules(drug, route);
  if (!rules) return { valid: true, message: 'No validation rules available', suggestedRange: null, factors: [] };
  const factors: string[] = [];

  // 安全：如果規則需要體重但體重缺失，就擋下（不要放行）
  if (rules.weightBased) {
    if (!patientWeight || patientWeight <= 0) {
      return { valid: false, message: `Weight required for ${drug} (mg/kg drug)`,
        suggestedRange: null, factors: ['weight_missing'] };
    }
    factors.push('weight');
    const maxDose = rules.maxPerKg * patientWeight;
    if (dose > maxDose) {
      return { valid: false, message: `Dose exceeds max for ${patientWeight}kg`,
        suggestedRange: { min: rules.minPerKg * patientWeight, max: maxDose, unit: rules.unit }, factors };
    }
  }

  // 依年齡調整（當規則定義了年齡區間，而且有提供年齡時）
  if (rules.ageAdjusted && patientAge !== undefined) {
    factors.push('age');
    const ageMax = rules.getAgeAdjustedMax(patientAge);
    if (dose > ageMax) {
      return { valid: false, message: `Exceeds age-adjusted max for ${patientAge}yr`,
        suggestedRange: { min: rules.typicalMin, max: ageMax, unit: rules.unit }, factors };
    }
  }

  // 依腎功能調整（當規則定義了 eGFR 區間，而且有提供 eGFR 時）
  if (rules.renalAdjusted && renalFunction !== undefined) {
    factors.push('renal');
    const renalMax = rules.getRenalAdjustedMax(renalFunction);
    if (dose > renalMax) {
      return { valid: false, message: `Exceeds renal-adjusted max for eGFR ${renalFunction}`,
        suggestedRange: { min: rules.typicalMin, max: renalMax, unit: rules.unit }, factors };
    }
  }

  // 絕對上限
  if (dose > rules.absoluteMax) {
    return { valid: false, message: `Exceeds absolute max ${rules.absoluteMax}${rules.unit}`,
      suggestedRange: { min: rules.typicalMin, max: rules.absoluteMax, unit: rules.unit },
      factors: [...factors, 'absolute_max'] };
  }
  return { valid: true, message: 'Within range',
    suggestedRange: { min: rules.typicalMin, max: rules.typicalMax, unit: rules.unit }, factors };
}
```

### Clinical Scoring: NEWS2

```typescript
interface NEWS2Input {
  respiratoryRate: number; oxygenSaturation: number; supplementalOxygen: boolean;
  temperature: number; systolicBP: number; heartRate: number;
  consciousness: 'alert' | 'voice' | 'pain' | 'unresponsive';
}
interface NEWS2Result {
  total: number;           // 0-20
  risk: 'low' | 'low-medium' | 'medium' | 'high';
  components: Record<string, number>;
  escalation: string;
}
```

評分表必須跟 Royal College of Physicians 的規格完全一致。

### Alert Severity and UI Behavior

| Severity | UI Behavior | Clinician Action Required |
|----------|-------------|--------------------------|
| Critical | 阻擋動作。無法關閉的 modal。紅色。 | 必須記錄覆寫原因才能繼續 |
| Major | 行內警示橫幅。橘色。 | 繼續之前必須確認 |
| Minor | 行內提示訊息。黃色。 | 只要知悉，不需採取行動 |

Critical 警示絕對不可以自動關閉，也不可以做成 toast 通知。覆寫原因必須存進稽核軌跡（audit trail）。

### Testing CDSS (Zero Tolerance for False Negatives)

```typescript
describe('CDSS — Patient Safety', () => {
  INTERACTION_PAIRS.forEach(({ drugA, drugB, severity }) => {
    it(`detects ${drugA} + ${drugB} (${severity})`, () => {
      const alerts = checkInteractions(drugA, [drugB], []);
      expect(alerts.length).toBeGreaterThan(0);
      expect(alerts[0].severity).toBe(severity);
    });
    it(`detects ${drugB} + ${drugA} (reverse)`, () => {
      const alerts = checkInteractions(drugB, [drugA], []);
      expect(alerts.length).toBeGreaterThan(0);
    });
  });
  it('blocks mg/kg drug when weight is missing', () => {
    const result = validateDose('gentamicin', 300, 'iv');
    expect(result.valid).toBe(false);
    expect(result.factors).toContain('weight_missing');
  });
  it('handles malformed drug data gracefully', () => {
    expect(() => checkInteractions('', [], [])).not.toThrow();
  });
});
```

通過標準：100%。漏掉任何一個交互作用，都是病人安全事件。

### Anti-Patterns

- 讓 CDSS 檢查變成可選的，或是沒有記錄理由就能跳過
- 把交互作用檢查做成 toast 通知
- 對藥物或臨床資料使用 `any` 型別
- 把交互作用配對寫死在程式碼裡，而不是用可維護的資料結構
- 在 CDSS 引擎裡默默吞掉錯誤（失敗必須大聲浮出來）
- 體重拿不到時就跳過依體重的驗證（必須擋下，不是放行）

## Examples

### Example 1: Drug Interaction Check

```typescript
const alerts = checkInteractions('warfarin', ['aspirin', 'metformin'], ['penicillin']);
// [{ severity: 'critical', pair: ['warfarin', 'aspirin'],
//    message: 'Increased bleeding risk', recommendation: 'Avoid combination' }]
```

### Example 2: Dose Validation

```typescript
const ok = validateDose('paracetamol', 1000, 'oral', 70, 45);
// { valid: true, suggestedRange: { min: 500, max: 4000, unit: 'mg' } }

const bad = validateDose('paracetamol', 5000, 'oral', 70, 45);
// { valid: false, message: 'Exceeds absolute max 4000mg' }

const noWeight = validateDose('gentamicin', 300, 'iv');
// { valid: false, factors: ['weight_missing'] }
```

### Example 3: NEWS2 Scoring

```typescript
const result = calculateNEWS2({
  respiratoryRate: 24, oxygenSaturation: 93, supplementalOxygen: true,
  temperature: 38.5, systolicBP: 100, heartRate: 110, consciousness: 'voice'
});
// { total: 13, risk: 'high', escalation: 'Urgent clinical review. Consider ICU.' }
```
