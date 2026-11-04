---
name: threat-mitigation-mapping
description: 把已找出的威脅對應到適當的安全控制與緩解措施。排定資安投資優先順序、制定修補計畫，或驗證控制措施有效性時使用。
---

# Threat Mitigation Mapping

把威脅和控制措施連起來，做有效的資安規劃。

## When to Use This Skill

- 排定資安投資的優先順序
- 制定修補路線圖
- 驗證控制措施的涵蓋範圍
- 設計縱深防禦
- 資安架構 review
- 風險處置規劃

## Core Concepts

### 1. Control Categories

```
Preventive ────► Stop attacks before they occur
   │              (Firewall, Input validation)
   │
Detective ─────► Identify attacks in progress
   │              (IDS, Log monitoring)
   │
Corrective ────► Respond and recover from attacks
                  (Incident response, Backup restore)
```

### 2. Control Layers

| Layer           | Examples                             |
| --------------- | ------------------------------------ |
| **Network**     | Firewall、WAF、DDoS 防護       |
| **Application** | 輸入驗證、認證     |
| **Data**        | 加密、存取控制          |
| **Endpoint**    | EDR、修補程式管理                |
| **Process**     | 資安訓練、事件應變 |

### 3. Defense in Depth

```
                    ┌──────────────────────┐
                    │      Perimeter       │ ← Firewall, WAF
                    │   ┌──────────────┐   │
                    │   │   Network    │   │ ← Segmentation, IDS
                    │   │  ┌────────┐  │   │
                    │   │  │  Host  │  │   │ ← EDR, Hardening
                    │   │  │ ┌────┐ │  │   │
                    │   │  │ │App │ │  │   │ ← Auth, Validation
                    │   │  │ │Data│ │  │   │ ← Encryption
                    │   │  │ └────┘ │  │   │
                    │   │  └────────┘  │   │
                    │   └──────────────┘   │
                    └──────────────────────┘
```

## Templates and detailed worked examples

完整的範本庫，以及詳細的緩解措施／控制措施對應，放在 `references/details.md`。需要以下這些具體範本時，再去讀那個檔案：Mitigation Model、Defense in Depth 評分、Executive Summary 骨架、Critical Gaps 報告、Recommendations、Implementation Roadmap、Results by Control。

## Best Practices

### Do's

- **Map all threats** - 不能有任何威脅沒被對應
- **Layer controls** - 縱深防禦是必要的
- **Mix control types** - 預防型、偵測型、矯正型都要有
- **Track effectiveness** - 量測並持續改善
- **Review regularly** - 控制措施會隨時間退化

### Don'ts

- **Don't rely on single controls** - 會有單點故障
- **Don't ignore cost** - ROI 很重要
- **Don't skip testing** - 沒測過的控制措施可能會失效
- **Don't set and forget** - 要持續改進
- **Don't ignore people/process** - 光靠技術是不夠的
