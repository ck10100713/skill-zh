---
name: "grad-ambidexterity"
description: "運用組織雙元性（ambidexterity）理論，在探索與開發活動之間取得平衡。當使用者需要診斷一個組織是過度開發還是過度探索、設計能同時支撐創新與效率的結構，或評估短期績效與長期更新之間的張力時使用。"
metadata:
  category: "WP-24 創新與國際化"
  tags: ["ambidexterity", "exploration-exploitation", "march-1991", "structural-ambidexterity", "contextual-ambidexterity", "organizational-design"]
---

# 組織雙元性：探索 vs 開發

## 概述

組織雙元性指的是企業同時追求探索（創新、實驗、新機會）與開發（效率、精進、執行既有能力）的能力。March（1991）證明，偏重其中一邊的企業都會面臨次佳的結果：過度開發會陷入能力陷阱，過度探索則會陷入失敗陷阱。

## 何時使用

**觸發條件：**
- 使用者問如何在不犧牲現有業務績效的情況下創新
- 使用者正在重組組織，要同時支撐研發與營運
- 使用者描述出能力陷阱（擅長的是錯誤的事）或失敗陷阱（實驗太多、沒有成果）的症狀
- 使用者提到「explore vs exploit」、「創新 vs 效率」或「雙元組織」

**何時不要用：**
- 分析外部新進者帶來的破壞 -> 用 grad-disruptive-innovation
- 透過策略聯盟取得創新 -> 用 grad-coopetition
- 國際化決策 -> 用 grad-oli 或 grad-uppsala

## 假設

```
IRON LAW: Over-Exploiting Kills Long-Term Innovation;
          Over-Exploring Kills Short-Term Revenue

Exploitation WITHOUT exploration leads to a COMPETENCY TRAP: the firm
becomes excellent at yesterday's business and is blindsided by change.

Exploration WITHOUT exploitation leads to a FAILURE TRAP: the firm
burns resources on experiments that never reach market scale.

There is no stable equilibrium — the balance must be actively managed.
```

- 探索和開發會競爭稀缺的資源（注意力、人才、預算）
- 最佳的平衡點會隨產業的動態程度與企業的生命週期階段而移動
- 高階領導層必須主動管理這個張力，它不會自己平衡

## 方法論

### 步驟 1：診斷目前的平衡

評估組織的探索與開發比例：

| 指標 | 偏重開發 | 平衡 | 偏重探索 |
|-----------|-------------------|----------|-------------------|
| 研發支出（占營收 %） | < 3% | 5-15% | > 20% |
| 新產品營收（占總營收 %） | < 10% | 20-40% | > 50% |
| 專案的時間範圍 | < 1 年 | 混合 | > 3 年 |
| 對失敗的容忍度 | 非常低 | 中等 | 非常高 |
| 流程的制式化程度 | 僵化 | 有適應性 | 混亂 |

### 步驟 2：找出雙元性的模式

選擇結構上的做法：
- **結構式雙元性（Structural ambidexterity）**（Tushman & O'Reilly）：把探索單位與開發單位分開，各有不同的文化、流程和指標。由高階領導層在頂端整合。
- **情境式雙元性（Contextual ambidexterity）**（Gibson & Birkinshaw）：個別員工依情境在探索與開發之間切換。需要支持性的文化（紀律 + 挑戰 + 信任 + 支持）。
- **循序式雙元性（Sequential ambidexterity）**：在探索期與開發期之間交替（較少見，適合較小的公司）。

### 步驟 3：設計整合機制

對結構式雙元性，要定義：
- 單位分隔的邊界（實體、文化、匯報線）
- 整合點（共同的高階團隊、知識傳遞的儀式）
- 資源分配規則（固定的探索預算 vs 動態分配）

對情境式雙元性，要定義：
- 行為上的期待（花在探索 vs 開發的時間比例）
- 文化上的促成條件（讓人敢實驗的心理安全感）
- 兩者都獎勵的指標（平衡計分卡的做法）

### 步驟 4：監控並重新平衡

建立檢視週期（每季檢視專案管線的健康度、每年檢視市場趨勢），以偵測是否往任何一個陷阱漂移。定義重新平衡的觸發條件。

## 輸出格式

```markdown
# Ambidexterity Assessment: {Organization}

## Current State Diagnosis
- Balance: Exploitation-heavy / Balanced / Exploration-heavy
- Evidence: {key indicators}
- Risk: Competency trap / Failure trap / None

## Recommended Ambidexterity Mode
- Mode: Structural / Contextual / Sequential
- Rationale: {why this mode fits}

## Design Recommendations
- Exploration unit: {scope, budget, metrics, reporting}
- Exploitation unit: {scope, budget, metrics, reporting}
- Integration mechanism: {how they connect}

## Rebalancing Triggers
- {Condition 1}: shift toward more exploration
- {Condition 2}: shift toward more exploitation
```

## 常見陷阱

- **只有結構分離、沒有整合，就只是分拆（spin-off）**：如果探索單位跟核心業務沒有連結，就會失去綜效。高階團隊「必須」做整合。
- **「創新劇場」不是探索**：從來不出產品的黑客松和實驗室只是浪費資源。探索必須有通往市場的路徑。
- **模式的選擇要看脈絡**：結構式雙元性適合有資源維持獨立單位的大公司。情境式適合每個人身兼多職的小公司。
- **平衡點會移動**：新創應該偏重探索。處於穩定產業的成熟企業可以偏重開發。沒有放諸四海皆準的比例。
- **指標不一致是第一殺手**：如果探索單位用開發的指標（季營收）來評斷，它們還沒能交出成果就會被關掉。

## 參考資料

- March（1991）的適應系統正式模型，見 `references/march-1991-model.md`
- Tushman & O'Reilly 的結構設計範本，見 `references/structural-ambidexterity-design.md`
