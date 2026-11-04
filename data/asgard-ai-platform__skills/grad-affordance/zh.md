---
name: "grad-affordance"
description: "運用功能可供性理論（Affordance Theory，Gibson, 1979；Norman, 1988）分析人造物提供給行動者的行動可能性。當使用者需要從可供性的角度評估技術設計、找出使用者為什麼在介面上卡關、透過可供性實現（actualization）分析 IT 帶動的組織變革，或問到「這個技術提供了什麼可能性」、「為什麼使用者搞不懂這個功能」或「技術如何讓新的做法成為可能」時使用。"
metadata:
  category: "WP-30 資訊管理"
  tags: ["affordance", "Gibson", "Norman", "perceived-affordance", "actualization", "design", "HCI"]
---

# 功能可供性理論（Gibson / Norman）

## 概述

功能可供性理論解釋行動者如何感知並實現物件或環境所提供的行動可能性。Gibson 的生態觀點認為，可供性是存在於行動者與環境之間的關係性屬性，獨立於感知之外。Norman 把這個概念調整後用在設計上：被感知到的可供性會引導使用者的互動，而指示符（signifier）則傳達哪裡可以採取行動。在資訊系統（IS）研究中，可供性理論用來解釋技術如何讓組織行動成為可能（或受到限制）。

## 何時使用

- 分析使用者為什麼能或不能有效使用某項技術
- 設計能清楚傳達功能的介面
- 解釋為什麼同樣的技術在不同組織會產生不同的結果
- 彌合技術功能與組織實務之間的落差

## 何時不要用

- 預測採用的可能性（用 TAM/UTAUT）
- 量化衡量可用性指標（用 SUS 或啟發式評估）
- 焦點純粹是美學設計，沒有功能上的意涵

## 假設

```
IRON LAW: An affordance exists in the RELATION between actor and artifact —
it is neither a property of the object alone nor of the user alone.
```

關鍵假設：
1. 可供性是關係性的，取決於人造物的屬性和行動者的能力
2. 可供性的存在、可供性的感知、可供性的實現，是三件不同的事
3. 同一項技術對不同的行動者提供不同的行動（取決於角色、技能、目標）
4. 限制（constraint）是可供性的互補面，也就是人造物所阻止或不鼓勵的事

## 方法論

### 步驟 1：找出行動者與人造物

指明技術人造物和行動者群體。描述行動者的能力、目標和情境。同一個人造物對新手和專家提供的可能性不同。

### 步驟 2：列舉可供性

針對每一組行動者與人造物，找出：

| 可供性類型 | 說明 |
|----------------|-------------|
| 存在（Existence） | 這個關係中客觀上存在哪些行動可能性 |
| 感知（Perception） | 行動者實際感知到哪些可供性（Norman 的焦點） |
| 實現（Actualization） | 行動者對哪些被感知到的可供性採取了行動 |

除了可供性之外，也要列出限制（人造物所阻止的行動）。

### 步驟 3：分析落差

找出三個關鍵的落差：
- **感知落差**：存在但沒被感知到的可供性（設計/指示符的問題）
- **實現落差**：被感知到但沒有被實現的可供性（動機/技能/資源的問題）
- **假可供性（False affordance）**：被感知為可行，但實際上並不存在的行動

### 步驟 4：建議設計或組織層面的介入

針對感知落差：改善指示符、新手引導或文件。針對實現落差：提供訓練、資源，或移除組織上的障礙。針對假可供性：修正介面中誤導人的線索。

## 輸出格式

```markdown
## Affordance Analysis: [Artifact] x [Actor Group]

### Actor Profile
- Role: ...
- Capabilities: ...
- Goals: ...

### Affordance Map
| Affordance | Exists? | Perceived? | Actualized? | Gap Type |
|-----------|---------|------------|-------------|----------|
| | | | | |

### Constraints
- [constraint]: [effect on actor behavior]

### Gap Analysis
- Perception gaps: ...
- Actualization gaps: ...
- False affordances: ...

### Recommendations
1. [Gap type]: [intervention]
2. ...
```

## 常見陷阱

- 不要把 Gibson 的可供性（關係性的、客觀的）和 Norman 的被感知可供性（主觀的、以設計為重）混為一談，要說明你用的是哪一個視角
- 「功能（feature）」不是「可供性」，功能是人造物的屬性，可供性是從行動者與人造物的關係中浮現的
- 可供性理論是解釋性的，不是預測性的，它幫助詮釋為什麼會發生某些事，不是預測採用率
- 在 IS 研究中，可供性的實現取決於組織脈絡（規範、慣例、權力結構），不只是個人的感知
- 小心可供性蔓延：把所有想得到的行動可能性都列出來，卻沒有優先考慮跟研究問題相關的
- Norman 後來偏好用「指示符（signifier）」取代「被感知的可供性」以減少混淆，要用目前的術語

## 參考資料

- Gibson, J. J. (1979). *The Ecological Approach to Visual Perception*. Houghton Mifflin.
- Norman, D. A. (1988). *The Design of Everyday Things*. Basic Books.
- Markus, M. L., & Silver, M. S. (2008). A foundation for the study of IT effects: A new look at DeSanctis and Poole's concepts of structural features and spirit. *Journal of the AIS*, 9(10/11), 609-632.
- Volkoff, O., & Strong, D. M. (2013). Critical realism and affordances: Theorizing IT-associated organizational change processes. *MIS Quarterly*, 37(3), 819-834.
