---
name: stride-analysis-patterns
description: 套用 STRIDE 方法論來有系統地找出威脅。在分析系統安全、進行威脅建模討論，或建立安全文件時使用。
---

# STRIDE Analysis Patterns

用 STRIDE 方法論有系統地找出威脅。

## When to Use This Skill

- 開始新的威脅建模討論
- 分析既有的系統架構
- 檢視安全設計的決策
- 建立威脅文件
- 訓練團隊辨識威脅
- 合規與稽核準備

## Core Concepts

### 1. STRIDE Categories

```
S - Spoofing       → Authentication threats
T - Tampering      → Integrity threats
R - Repudiation    → Non-repudiation threats
I - Information    → Confidentiality threats
    Disclosure
D - Denial of      → Availability threats
    Service
E - Elevation of   → Authorization threats
    Privilege
```

### 2. Threat Analysis Matrix

| Category            | Question                                  | Control Family |
| ------------------- | ----------------------------------------- | -------------- |
| **Spoofing**        | 攻擊者能假冒別人嗎？  | Authentication |
| **Tampering**       | 攻擊者能修改傳輸中/靜態的資料嗎？ | Integrity      |
| **Repudiation**     | 攻擊者能否認自己做過的動作嗎？                | Logging/Audit  |
| **Info Disclosure** | 攻擊者能存取未授權的資料嗎？    | Encryption     |
| **DoS**             | 攻擊者能破壞可用性嗎？        | Rate limiting  |
| **Elevation**       | 攻擊者能取得更高的權限嗎？      | Authorization  |

## Templates and detailed worked examples

完整的範本庫放在 `references/details.md`。需要這個 skill 的具體範本時，再去讀那個檔案。

## Best Practices

### Do's

- **讓利害關係人參與** - 安全、開發和維運的觀點都要有
- **要有系統** - 涵蓋所有 STRIDE 類別
- **務實地排優先順序** - 專注在高衝擊的威脅
- **定期更新** - 威脅模型是活的文件
- **用視覺化輔助** - DFD 有助於溝通

### Don'ts

- **不要跳過任何類別** - 每一類都會揭露不同的威脅
- **不要假設是安全的** - 質疑每一個元件
- **不要閉門造車** - 協作式建模比較好
- **不要忽略低機率的威脅** - 高衝擊的威脅很重要
- **不要停在找出威脅** - 要接著做緩解措施
