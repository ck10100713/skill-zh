---
name: "soc-innovation-diffusion"
description: "運用 Rogers 的創新擴散理論，分析新產品、新想法或新技術如何在人群中擴散。使用者需要規劃採用策略、為採用者分群、跨越從早期採用者到主流市場的鴻溝，或預測採用曲線時使用，就算他們說的是「我們怎麼讓更多人用這個」、「為什麼我們的產品起不來」或「我們怎麼觸及主流市場」也一樣。"
metadata:
  category: "WP-18 社會科學院"
  tags: ["social-science", "innovation-diffusion", "adoption"]
---

# 創新擴散

## 概述

Rogers 的理論描述創新如何以可預測的 S 曲線模式在人群中擴散，並分出五類採用者，各自需要不同的策略。Moore 的《跨越鴻溝》（Crossing the Chasm）進一步延伸，指出早期採用者和早期大眾之間那道關鍵的缺口。

## 框架

```
IRON LAW: The Chasm Is Real — Early Adopters ≠ Mainstream

Visionaries (early adopters) buy because it's NEW and they can tolerate
imperfections. Pragmatists (early majority) buy because it WORKS and
others already use it. These are fundamentally different buyer psychologies.

Success with early adopters does NOT predict mainstream success.
The strategy that wins innovators will FAIL with the majority.
```

### 五類採用者

| 類別 | 占人口比例 | 動機 | 策略 |
|----------|----------------|-----------|----------|
| **創新者（Innovators）** | 2.5% | 技術愛好者，追求新鮮的刺激 | 技術規格、搶先體驗、「成為第一個」 |
| **早期採用者（Early Adopters）** | 13.5% | 有遠見的人，追求策略優勢 | 願景契合、潛在 ROI、案例研究 |
| **早期大眾（Early Majority）** | 34% | 務實派，想要經過驗證的解決方案 | 參考對象、完整解決方案、低風險 |
| **晚期大眾（Late Majority）** | 34% | 保守派，跟隨群體 | 產業標準、同儕壓力、簡單 |
| **落後者（Laggards）** | 16% | 懷疑者，受傳統約束 | 必要性、沒有替代方案、與必要產品綑綁 |

### 鴻溝（Moore）

早期採用者（16%）和早期大眾（34%）之間的缺口，是大多數創新死掉的地方。要跨越：

1. **選一個灘頭陣地區隔**：早期大眾當中「一個」特定的利基
2. **交付完整產品（whole product）**：不只是核心產品，而是包含支援、整合、文件的完整解決方案
3. **徹底拿下這個區隔**：成為該利基中事實上的標準
4. **把這場勝利當作參考**：務實派買的是其他務實派在用的東西
5. **擴展到相鄰的區隔**：保齡球瓶策略，每拿下一個利基，就讓下一個更容易

### 影響採用速度的五個因素

| 因素 | 定義 | 在什麼情況下採用更快… |
|--------|-----------|----------------------|
| **相對優勢（Relative advantage）** | 比目前的解決方案好多少 | 好很多、明顯的改進 |
| **相容性（Compatibility）** | 與既有價值觀、做法、基礎設施的契合度 | 需要的改變最小 |
| **複雜度（Complexity）** | 理解與使用的難易度 | 容易掌握和使用 |
| **可試用性（Trialability）** | 投入前可以先試嗎？ | 有免費試用、freemium、試行方案 |
| **可觀察性（Observability）** | 別人看得到成果嗎？ | 成果看得見、可分享 |

## 輸出格式

```markdown
# Diffusion Analysis: {Innovation}

## Innovation Profile
| Factor | Assessment | Implication |
|--------|-----------|------------|
| Relative advantage | H/M/L | {detail} |
| Compatibility | H/M/L | {detail} |
| Complexity | H/M/L (lower = better) | {detail} |
| Trialability | H/M/L | {detail} |
| Observability | H/M/L | {detail} |

## Current Adoption Stage
- Estimated penetration: {X%}
- Current adopter category: {Innovators / Early Adopters / Chasm / Early Majority / etc.}

## Chasm Strategy (if applicable)
- Beachhead segment: {specific niche}
- Whole product gaps: {what's missing for a complete solution}
- Reference strategy: {how to get pragmatist references}

## Adoption Acceleration Plan
1. {action to improve weakest adoption factor}
```

## 範例

### 正確的應用
**情境：** 一個新的 AI 程式碼審查工具的採用分析
- **目前階段**：約 500 位用戶，大多是開發者網紅和技術主管 → 早期採用者
- **鴻溝風險**：高。早期採用者喜歡 AI 的建議，但工程經理（早期大眾）擔心誤報和安全性
- **灘頭陣地**：中型金融科技公司（程式碼審查負擔重、重視安全、願意採用經過驗證的工具）
- **完整產品的缺口**：缺少 SOC 2 合規文件、沒有 JIRA 整合、沒有團隊管理儀表板 → 沒有這些，早期大眾不會採用 ✓

### 錯誤的應用
- 「我們有 500 位熱情的用戶，所以我們準備好進入主流了」→ 500 位早期採用者，不代表這個產品已經準備好面對務實派。鴻溝需要完全不同的策略。違反鐵律。

## 注意事項

- **早期採用者的產品市場適配（product-market fit）≠ 主流市場的 product-market fit**：讓早期採用者興奮的功能（可客製化、尖端技術），可能會讓大眾（想要簡單和可靠）招架不住。
- **保齡球瓶策略**：拿下灘頭陣地之後，擴展到會參考第一場勝利的相鄰利基。不要跳到完全不同的區隔。
- **網路效應會加速擴散**：有網路效應的產品（通訊工具、平台），一旦越過臨界點，會走更陡的 S 曲線。
- **有可能倒退**：採用可能逆轉（Google Glass、Segway）。要維持採用，就必須持續交付價值。
- **B2B 的擴散比較慢**：組織層級的採用涉及多位決策者、採購流程和整合需求。要規劃更長的時程。

## 參考資料

- 跨越鴻溝的做法請看 `references/chasm-strategy.md`
