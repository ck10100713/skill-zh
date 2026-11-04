---
name: "grad-ai-ethics"
description: "運用 AI 倫理框架（公平、課責、透明、隱私）評估 AI 系統的演算法偏誤、可解釋性缺口與價值對齊失敗。當使用者需要稽核 AI 系統的倫理風險、設計公平性限制、評估可解釋性需求，或問到「這個 AI 系統公平嗎」、「怎麼偵測演算法偏誤」、「這個 AI 部署有什麼倫理影響」或「怎麼讓這個模型能向利害關係人解釋」時使用。"
metadata:
  category: "WP-34 跨學科/新興"
  tags: ["AI-ethics", "fairness", "accountability", "transparency", "algorithmic-bias", "XAI", "explainable-AI", "FATE"]
---

# AI 倫理

## 概述

AI 倫理檢視人工智慧系統的道德面向，以四大支柱為核心：公平（fairness）、課責（accountability）、透明（transparency）和隱私（privacy），簡稱 FATE。隨著 AI 系統越來越常做出影響重大的決定，它們會繼承並放大訓練資料與設計選擇中內嵌的偏誤。合乎倫理的 AI 需要主動找出偏誤、建立可解釋性機制、釐清課責結構，並保護隱私。

## 何時使用

- 在 AI 系統部署前或部署後稽核公平性
- 為機器學習管線設計偏誤緩解策略
- 針對不同的利害關係人受眾，評估可解釋性的需求
- 評估法規遵循（EU AI Act、GDPR、特定產業的要求）

## 何時不要用

- 問題純粹是模型效能，沒有倫理面向
- 分析的是非 AI 的自動化，或完全透明的規則式系統
- 焦點是 AI 的技術架構，沒有部署情境

## 假設

```
IRON LAW: AI systems encode the VALUES of their designers and training
data — there is no value-neutral AI, and "optimizing for accuracy"
without fairness constraints reproduces existing inequalities.
```

關鍵假設：
1. 所有資料集都反映了歷史上的決策和偏誤，「ground truth（真值）」是社會建構出來的
2. 公平有多種在數學上互相不相容的定義，選擇其中一種是價值判斷
3. 透明與可解釋性不是同一件事，一個系統可以是透明的（程式碼公開），但無法解釋（沒人了解它為什麼做出 X 這個決定）
4. 課責需要從開發者、部署者到受影響者之間，有清楚的責任鏈

## 方法論

### 步驟 1：描繪 AI 系統與利害關係人

找出 AI 系統的功能、決策領域、受影響的族群，以及系統營運者與被系統對待者之間的權力不對稱。

### 步驟 2：評估公平性

用多種公平性定義來評估：

| 公平性指標 | 定義 | 張力 |
|----------------|------------|---------|
| **人口統計均等（Demographic parity）** | 各群體的正面結果比率相等 | 可能與準確度衝突 |
| **均等化勝率（Equalized odds）** | 各群體的真陽性率和偽陽性率相等 | 可能與校準衝突 |
| **個體公平（Individual fairness）** | 相似的個體得到相似的結果 | 需要定義「相似」 |
| **校準（Calibration）** | 預測機率與各群體的實際結果相符 | 可能與均等化勝率衝突 |

### 步驟 3：評估透明度與可解釋性

評估解釋是否適合各個利害關係人：受影響的個人（以救濟為導向）、監管機關（以合規為導向）、開發者（以除錯為導向）和一般大眾（以信任為導向）。

### 步驟 4：設計課責與緩解措施

定義責任鏈、偏誤緩解的介入（前處理、處理中、後處理）、持續的監控，以及申訴救濟的機制。

## 輸出格式

```markdown
## AI Ethics Assessment: [System/Context]

### System Profile
- Function: [what the AI system does]
- Decision domain: [what decisions it makes or supports]
- Affected populations: [who is impacted]
- Power asymmetry: [who controls vs who is subject to the system]

### Fairness Assessment
| Dimension | Status | Evidence | Risk Level |
|-----------|--------|----------|------------|
| Demographic parity | [met/unmet/unknown] | [data] | [high/medium/low] |
| Equalized odds | [met/unmet/unknown] | [data] | [high/medium/low] |
| Individual fairness | [met/unmet/unknown] | [data] | [high/medium/low] |

### Transparency and Explainability
| Stakeholder | Explanation Needed | Currently Provided | Gap |
|-------------|-------------------|-------------------|-----|
| [affected individuals] | [what they need] | [what exists] | [gap] |
| [regulators] | [what they need] | [what exists] | [gap] |

### Accountability Structure
- Developer responsibility: [scope]
- Deployer responsibility: [scope]
- Redress mechanism: [how affected parties can contest decisions]

### Mitigation Recommendations
1. [Pre-processing intervention]
2. [In-processing intervention]
3. [Post-processing intervention]
4. [Monitoring and ongoing audit plan]
```

## 常見陷阱

- 公平性指標在數學上互不相容（Chouldechova, 2017），你「必須」選擇要優先考慮哪一個，而這是政治性的決定
- 「移除受保護屬性」並不會移除偏誤，相關的代理變數會讓歧視延續
- 可解釋性方法（LIME、SHAP）解釋的是模型的行為，不是模型的推理，它們是事後的合理化
- 隱私與公平可能衝突：公平性稽核需要人口統計資料，而隱私保護限制了這類資料
- AI 倫理不是檢查清單，它需要持續投入，不是一次性的認證
- 小心「倫理漂白（ethics washing）」，也就是只做表面功夫的倫理流程，提供掩護卻沒有實質的改變

## 參考資料

- Barocas, S., Hardt, M., & Narayanan, A. (2023). *Fairness and Machine Learning: Limitations and Opportunities*. MIT Press.
- Jobin, A., Ienca, M., & Vayena, E. (2019). The global landscape of AI ethics guidelines. *Nature Machine Intelligence*, 1(9), 389-399.
- Selbst, A. D., Boyd, D., Friedler, S. A., Venkatasubramanian, S., & Vertesi, J. (2019). Fairness and abstraction in sociotechnical systems. *Proceedings of FAT* 2019*, 59-68.
