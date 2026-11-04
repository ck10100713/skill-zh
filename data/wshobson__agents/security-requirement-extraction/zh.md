---
name: security-requirement-extraction
description: 從威脅模型和商業脈絡推導出安全需求。在把威脅轉成可執行的需求、撰寫安全 user story 或建立安全測試案例時使用。
---

# Security Requirement Extraction

把威脅分析轉化成可執行的安全需求。

## When to Use This Skill

- 把威脅模型轉成需求
- 撰寫安全 user story
- 建立安全測試案例
- 建立安全驗收標準
- 對應合規需求
- 撰寫安全架構文件

## Core Concepts

### 1. Requirement Categories

```
Business Requirements → Security Requirements → Technical Controls
         ↓                       ↓                      ↓
  "Protect customer    "Encrypt PII at rest"   "AES-256 encryption
   data"                                        with KMS key rotation"
```

### 2. Security Requirement Types

| Type               | Focus                   | Example                               |
| ------------------ | ----------------------- | ------------------------------------- |
| **Functional**     | 系統必須做什麼     | "System must authenticate users"      |
| **Non-functional** | 系統必須表現得多好 | "Authentication must complete in <2s" |
| **Constraint**     | 被強加的限制     | "Must use approved crypto libraries"  |

### 3. Requirement Attributes

| Attribute        | Description                 |
| ---------------- | --------------------------- |
| **Traceability** | 連結到威脅/合規 |
| **Testability**  | 可以被驗證             |
| **Priority**     | 商業重要性         |
| **Risk Level**   | 沒滿足時的衝擊   |

## Templates and detailed worked examples

完整的範本庫放在 `references/details.md`。需要這個 skill 的具體範本時，再去讀那個檔案。

## Best Practices

### Do's

- **追溯到威脅** - 每條需求都應該對應到威脅
- **要具體** - 含糊的需求無法測試
- **包含驗收標準** - 定義什麼叫「完成」
- **考慮合規** - 及早對應到各框架
- **定期檢視** - 需求會隨著威脅演變

### Don'ts

- **不要太籠統** - 「要安全」不是需求
- **不要省略理由** - 說明為什麼重要
- **不要忽略優先順序** - 不是所有需求都一樣重要
- **不要忘了可測試性** - 測不了就驗證不了
- **不要閉門造車** - 讓利害關係人參與
