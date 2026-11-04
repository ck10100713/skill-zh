---
name: "grad-cognitive-load"
description: "運用認知負荷理論，在工作記憶的限制內管理內在、外在與增生負荷，最佳化教學設計。當使用者需要診斷學習者為什麼不堪負荷、為了更好的理解而重新設計訓練或文件、評估 UI/UX 資訊架構的認知負擔，或問到「為什麼這份教學讓人困惑」、「怎麼簡化複雜的說明」或「是什麼造成資訊過載」時使用。"
metadata:
  category: "WP-29 心理學理論"
  tags: ["cognitive-load-theory", "Sweller", "working-memory", "instructional-design", "intrinsic-load", "extraneous-load", "germane-load"]
---

# 認知負荷理論（CLT）

## 概述

認知負荷理論（Sweller, 1988）建立在人類認知的架構上：工作記憶的容量（7 +/- 2 個項目）和持續時間都嚴重受限，而長期記憶基本上是沒有上限的。有效的教學設計必須管理三種認知負荷：內在（任務複雜度）、外在（設計不良）和增生（schema 建構），讓總負荷不超過工作記憶的容量。

## 何時使用

- 診斷學習者為什麼無法理解或記住教材
- 為了降低認知負擔，重新設計文件、教學或訓練計畫
- 評估介面設計、儀表板或資訊顯示是否過載
- 為複雜的學習教材排序，搭起 schema 習得的鷹架

## 何時不要用

- 問題是動機而不是認知（學習者有能力處理，只是選擇不做）
- 對專家受眾，他們已經有 schema，適用專業反轉效應
- 簡化會犧牲任務必要的擬真度（有些任務本質上就是無法簡化的複雜）

## 假設

```
IRON LAW: Working memory capacity is FIXED and limited —
instructional design must minimize extraneous load to maximize
germane processing. Total load (intrinsic + extraneous + germane)
must not exceed working memory capacity.
```

關鍵假設：
1. 工作記憶處理新資訊；長期記憶儲存 schema，能繞過工作記憶的限制
2. 內在負荷由元素互動性決定，不改變任務就無法降低它
3. 外在負荷在設計者的掌控之下，永遠應該把它降到最低

## 方法論

### 步驟 1：分析元素互動性（內在負荷）

評估有多少資訊元素必須同時處理：
- **低互動性**：元素可以獨立學習（單字表）
- **高互動性**：元素必須整合起來才能理解（文法規則、電路設計）

### 步驟 2：找出外在負荷的來源

| 來源 | 說明 | 設計缺陷 |
|--------|-------------|-------------|
| 分散注意力（Split-attention） | 整合在空間/時間上分開的來源 | 文字離圖表很遠 |
| 冗餘（Redundancy） | 以多種格式處理相同的資訊 | 旁白重複螢幕上的文字 |
| 短暫資訊（Transient information） | 資訊在處理完成前就消失 | 快速的動畫沒有暫停 |
| 專業反轉（Expertise reversal） | 對新手有幫助、對專家卻有妨礙的鷹架 | 強迫進階使用者走一步一步的流程 |
| 誘人細節（Seductive details） | 有趣但無關的資訊 | 裝飾性的圖片、離題的故事 |

### 步驟 3：最佳化負荷的分配

管理總認知負荷的策略：
- **範例（Worked examples）**：藉由展示已解出的問題，降低新手的內在負荷
- **漸隱（Fading）**：從範例逐步過渡到獨立解題
- **形式效應（Modality effect）**：使用雙通道（視覺 + 聽覺）來擴大有效的工作記憶容量
- **分段（Segmenting）**：把複雜的教材拆成由學習者自己掌握節奏的片段
- **預先訓練（Pre-training）**：在介紹互動之前，先教組成元素
- **消除冗餘**：移除各通道之間重複的資訊

### 步驟 4：為增生負荷做設計

- 鼓勵自我解釋與精緻化
- 在練習題中使用變化，促進 schema 的抽象化
- 提供凸顯結構相似性的比較案例
- 把練習分散在不同時間（分散練習），以鞏固 schema

## 輸出格式

```markdown
## Cognitive Load Analysis: [Context]

### Intrinsic Load Assessment
- Element interactivity: [Low/Medium/High]
- Key interacting elements: [list]
- Learner expertise level: [Novice/Intermediate/Expert]

### Extraneous Load Audit
| Source | Present? | Severity | Fix |
|--------|----------|----------|-----|
| Split-attention | [Yes/No] | [High/Med/Low] | [solution] |
| Redundancy | [Yes/No] | [High/Med/Low] | [solution] |
| Transient info | [Yes/No] | [High/Med/Low] | [solution] |
| Seductive details | [Yes/No] | [High/Med/Low] | [solution] |

### Load Budget
- Estimated total load: [Within/Exceeding capacity]
- Extraneous reduction potential: [High/Medium/Low]

### Redesign Recommendations
1. [Primary extraneous load reduction]
2. [Segmenting or sequencing change]
3. [Germane load enhancement]
```

## 常見陷阱

- 專業反轉效應意味著，對新手最理想的設計會積極地傷害專家，所以需要適應性或分層的設計
- 「7 +/- 2」是粗略的經驗法則，對新的互動元素來說，有效的工作記憶容量可能低到只有 3-4 個組塊
- 增生負荷在近期的文獻中有爭議，有些研究者把它歸到內在負荷的管理之下，而不是當成獨立的一類
- 降低外在負荷永遠是有益的；降低內在負荷則可能過度簡化，阻礙深度學習
- 形式效應只有在視覺和聽覺通道傳遞的是互補（不是冗餘）的資訊時才適用
- 認知負荷很難直接衡量，各種替代指標（表現、主觀評分、次要任務）各有其限制

## 參考資料

- Sweller, J. (1988). Cognitive load during problem solving: effects on learning. *Cognitive Science*, 12(2), 257-285.
- Sweller, J., Ayres, P. & Kalyuga, S. (2011). *Cognitive load theory*. Springer.
- Paas, F., Renkl, A. & Sweller, J. (2003). Cognitive load theory and instructional design: recent developments. *Educational Psychologist*, 38(1), 1-4.
