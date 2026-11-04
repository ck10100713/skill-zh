---
name: "grad-dual-process"
description: "用雙歷程理論診斷判斷是來自快速直覺（System 1）還是緩慢分析（System 2）的處理，並找出由此產生的認知偏誤。當使用者需要解釋為什麼快速決策會出錯、設計考慮到認知預設值的選擇架構、稽核決策流程中的捷思錯誤，或問到「為什麼人會誤判機率」「怎麼減少直覺判斷的錯誤」「直覺什麼時候會失靈」時，就用這個 skill。"
metadata:
  category: "WP-29 心理學理論"
  tags: ["dual-process", "system-1", "system-2", "heuristics", "cognitive-bias", "Kahneman", "thinking-fast-and-slow"]
---

# Dual-Process Theory

## Overview

雙歷程理論（Kahneman，2011；Stanovich & West，2000）區分兩種認知處理模式：System 1（快速、自動、由捷思驅動）和 System 2（緩慢、審慎、基於規則）。大多數判斷預設走 System 1，它很有效率，但捷思失靈時容易產生系統性偏誤。

## When to Use

- 解釋為什麼利害關係人在時間壓力或複雜情境下，會出現可預測的判斷錯誤
- 設計能補償 System 1 預設值的決策環境（推力、檢查清單）
- 稽核現有流程，找出捷思捷徑在哪裡帶來風險
- 評估直覺專業什麼時候可靠、什麼時候會誤導

## When NOT to Use

- 決策本來就有結構化的演算法程序（偏誤已被工程化排除）
- 拿來當藉口，全盤否定直覺判斷：在高效度的環境中，專家直覺可以很準
- 問題出在動機，不是認知（人知道正確答案，卻選了別的）

## Assumptions

```
IRON LAW: System 1 operates by DEFAULT — System 2 engagement
requires cognitive effort and is easily depleted. Under time
pressure, cognitive load, or ego depletion, System 1 dominates
and heuristic biases amplify.
```

關鍵假設：
1. System 1 和 System 2 是處理模式的隱喻，不是腦中真正分離的系統
2. 捷思通常是適應性的，偏誤出現在邊界條件
3. System 2 可以推翻 System 1，但前提是有被提示，而且有足夠的認知資源

## Methodology

### Step 1 — Identify the Judgment or Decision Context

描述決策的特徵：時間壓力、複雜度、熟悉度、賭注大小、情緒投入程度。

### Step 2 — Classify Processing Mode

| Feature | System 1 | System 2 |
|---------|----------|----------|
| Speed | 快、自動 | 慢、費力 |
| Awareness | 無意識 | 有意識 |
| Capacity | 高（平行） | 低（序列） |
| Basis | 捷思、聯想 | 規則、邏輯 |
| Error type | 系統性偏誤 | 計算錯誤 |
| Triggered by | 預設、熟悉感 | 新奇、偵測到衝突 |

### Step 3 — Map Relevant Heuristics and Biases

常見的 System 1 捷思與其失靈模式：
- **Availability**：用回想的容易程度判斷頻率，會被顯著性和近期性帶偏
- **Representativeness**：用相似度判斷機率，忽略基本比率
- **Anchoring**：從初始值開始調整來估計，調整不足
- **Affect**：用情緒反應判斷風險與利益，忽略統計證據

### Step 4 — Design Intervention

- **De-bias**：放慢決策、要求明確說明理由、做 pre-mortem
- **Nudge**：重組選擇架構，讓 System 1 的預設值和期望結果一致
- **Leverage**：在高效度、回饋快速的領域，善用 System 1 的優勢（模式辨識）

## Output Format

```markdown
## Dual-Process Analysis: [Context]

### Decision Environment
- Time pressure: [High/Medium/Low]
- Complexity: [High/Medium/Low]
- Emotional involvement: [High/Medium/Low]
- Dominant processing: [System 1 / System 2 / Mixed]

### Heuristic-Bias Map
| Heuristic | Bias Triggered | Evidence | Risk Level |
|-----------|---------------|----------|------------|
| [heuristic] | [bias] | [observation] | [High/Med/Low] |

### Intervention Design
1. [De-biasing or nudge strategy]
2. [Process change]
3. [Environmental redesign]
```

## Gotchas

- System 1/System 2 是有用的隱喻，不是字面上的大腦架構，避免把這個區分實體化
- 在回饋明確、模式規律的領域（例如西洋棋、消防），專家直覺（System 1）非常準
- 去偏誤訓練的遷移效果很差，改變環境比訓練個人更有效
- 認知耗竭效應有爭議，不要假設有簡單的「意志力電池」模型
- System 2 本質上不是比較「好」，它比較慢、成本比較高，而且一樣會受動機性推理影響
- 人常把信心和準確度搞混，System 1 的高信心不代表正確

## References

- Kahneman, D. (2011). *Thinking, fast and slow*. Farrar, Straus and Giroux.
- Stanovich, K. E. & West, R. F. (2000). Individual differences in reasoning: implications for the rationality debate. *Behavioral and Brain Sciences*, 23(5), 645-665.
- Tversky, A. & Kahneman, D. (1974). Judgment under uncertainty: heuristics and biases. *Science*, 185(4157), 1124-1131.
