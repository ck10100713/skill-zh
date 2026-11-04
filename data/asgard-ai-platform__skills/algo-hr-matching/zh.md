---
name: "algo-hr-matching"
description: "實作 Gale-Shapley 穩定配對演算法，解決雙邊配對問題。當使用者需要把求職者配到職缺、把學生分配到學校，或解決任何雙邊偏好配對問題時使用，即使他們說的是『optimal job matching』『stable assignment』或『candidate-position pairing』。"
metadata:
  category: "WP-42 HR 演算法"
  tags: ["hr", "stable-matching", "gale-shapley", "assignment"]
---

# Gale-Shapley 穩定配對

## 概述

Gale-Shapley（延遲接受）在兩個大小相同的集合之間找出穩定配對，也就是沒有任何一對未配對的人，彼此比起目前的配對對象更喜歡對方。最壞情況複雜度 O(n²)。提案方最佳：提案的那一方能得到他們最好的穩定對象。

## 何時使用

**觸發條件：**
- 依雙方偏好把求職者配對到職缺
- 把學生分配到學校，或把住院醫師分配到醫院
- 任何需要穩定性（沒有 blocking pair）的雙邊配對

**不該使用的情況：**
- 單邊分配（用匈牙利演算法）
- 偏好是用分數而不是排名時（用最佳化）

## 演算法

```
IRON LAW: The Proposing Side Gets Their BEST Stable Partner
Gale-Shapley is proposer-optimal and reviewer-pessimal. If employers
propose, they get their best stable match; candidates get their worst.
The CHOICE of who proposes determines which stable matching is found.
```

### 階段 1：輸入驗證
收集：雙方的偏好排名。每個參與者要對另一邊的所有成員排序。
**關卡：** 偏好清單完整，兩邊人數相等（或用虛擬項目處理人數不等）。

### 階段 2：核心演算法
1. 所有提案方都是「自由」的（未配對）
2. 只要還有任何提案方是自由的，而且還沒向所有人提案過：
   - 自由的提案方向他排名最高、還沒提案過的接受方提案
   - 接受方如果還沒配對就接受；如果新的提案方更討喜，就換掉目前的配對對象
   - 被換掉的提案方再次變成自由
3. 所有提案方都配對完成時結束

### 階段 3：驗證
檢查穩定性：對每一對未配對的 (a,b)，確認他們至少有一方更喜歡目前的配對對象。沒有 blocking pair = 穩定。
**關卡：** 找到的 blocking pair 為零。

### 階段 4：輸出
回傳配對結果，並確認穩定性。

## 輸出格式

```json
{
  "matching": [{"proposer": "Candidate_A", "reviewer": "Company_X", "proposer_rank": 1, "reviewer_rank": 2}],
  "metadata": {"pairs": 10, "rounds": 23, "blocking_pairs": 0, "proposer_side": "candidates"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 3 位求職者、3 家公司，每個人都有完整的偏好排名
**預期：** 穩定配對，blocking pair 為零。由求職者提案會得到對求職者最佳的結果。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 所有人的第一志願都一樣 | 仍會終止，且穩定 | 被拒絕的提案方會往下一個選擇 |
| 偏好完全相同 | 唯一的穩定配對 | 只有一種可能 |
| 兩邊人數不等 | 較多的那邊有人沒配到 | 加虛擬項目，或用多對一的變體 |

## 注意事項

- **提案方優勢**：求職者提案的話，會比公司提案得到更好的配對。這是設計上的選擇，有公平性的影響。
- **偏好不完整**：如果參與者沒有對所有人排序，可能會有人沒配到。用可接受對象的門檻來處理。
- **多對一**：醫院與住院醫師的配對用的是多對一變體（每家醫院有多個名額）。要用 Roth-Peranson 延伸。
- **策略性操弄**：接受方「可以」靠謊報偏好（截短清單）獲益。提案方不行，對提案方來說誠實申報是優勢策略。
- **偏好的取得**：實務上很難拿到誠實又完整的排名。人們傾向挑到「夠好」就停，而不是把所有選項完整排序。

## 參考資料

- 多對一配對（醫院與住院醫師），見 `references/many-to-one.md`
- 策略行為分析，見 `references/strategic-manipulation.md`
