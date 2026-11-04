---
name: "algo-social-sentiment"
description: "實作 VADER 情緒分析，替社群媒體文字評分。當使用者需要分析推文、評論或社群貼文的情緒、計算綜合情緒分數、或分類文字的正負面時使用，即使他們說的是「這是正面還是負面」、「這些留言的情緒」或「社群媒體的氛圍分析」也一樣。"
metadata:
  category: "WP-38 社群演算法"
  tags: ["social-media", "sentiment-analysis", "vader", "nlp"]
---

# VADER 情緒分析（VADER Sentiment Analysis）

## 概述

VADER（Valence Aware Dictionary and sEntiment Reasoner）是針對社群媒體最佳化、以詞典和規則為基礎的情緒工具。回傳綜合分數 compound，範圍 [-1, +1]，結合了正面、負面和中性的比例。每則文字的執行複雜度是 O(n)，n = 字數。不需要訓練。

## 何時使用

**觸發條件：**
- 要分析社群媒體貼文、推文或評論的情緒
- 要在不訓練 ML 模型的情況下，快速做情緒評分
- 要處理帶有俚語、表情符號和非正式用語的文字

**何時不要用：**
- 正式／學術文字（VADER 是針對社群媒體調校的）
- 領域專屬的情緒很重要時（例如金融情緒，用 FinBERT）
- 偵測反諷很關鍵時（VADER 偵測不到反諷）

## 演算法

```
鐵律：VADER 是為「社群媒體」文字設計的
它把俚語、表情符號、大小寫和標點，都當成情緒的修飾因子處理。
把它套用在正式文件（法律、學術、醫療）上，
產生的分數不可靠。領域專屬的文字，
要改用該領域訓練的模型。
```

### 階段 1：輸入驗證
把文字斷詞。要保留：大小寫（全大寫 = 強調）、標點（! 會放大）、表情符號／emoji。
**關卡：** 文字非空、編碼處理正確。

### 階段 2：核心演算法
1. 在 VADER 詞典中查每個 token（7,500 個以上帶情緒評分的詞彙）
2. 套用文法規則：否定（"not good" = 負面）、程度修飾詞（"very good" > "good"）、大小寫加成、標點放大
3. 計算正面、負面、中性比例的原始價數分數
4. 計算 compound 分數：用公式把所有價數分數的總和正規化：compound = sum / √(sum² + α)，其中 α = 15

### 階段 3：驗證
分類：compound ≥ 0.05 → 正面、≤ -0.05 → 負面，其餘為中性。抽查樣本結果。
**關卡：** 分類通過 10-20 個範例的人工抽查。

### 階段 4：輸出
回傳每則文字的 compound 分數和正負面分類。

## 輸出格式

```json
{
  "results": [{"text": "...", "compound": 0.76, "pos": 0.45, "neu": 0.55, "neg": 0.0, "label": "positive"}],
  "metadata": {"texts_analyzed": 500, "distribution": {"positive": 0.45, "neutral": 0.35, "negative": 0.20}}
}
```

## 範例

### 輸入輸出範例
**輸入：** "This product is AMAZING!!! 😍"
**預期：** compound ≈ 0.87（正面）。被這些加成：全大寫、!!!、😍 emoji。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| "Not bad at all" | 略微正面（約 0.2） | 雙重否定有被部分處理 |
| "😂😂😂" | 正面 | 詞典中有對應 emoji |
| 空字串 | Compound = 0，中性 | 沒有 token 可評分 |

## 常見陷阱

- **反諷看不出來**："Oh great, another meeting" 會被判成正面。VADER 沒有反諷偵測。
- **否定的視窗**：VADER 在 3 個字的視窗內套用否定。"I do not think this is bad" 可能會把否定鏈解析錯。
- **Emoji 涵蓋範圍**：VADER 的 emoji 詞典可能沒涵蓋較新的 emoji。視需要更新或補充。
- **語言限制**：VADER 只支援英文。中文／日文要用該語言專用的工具（例如中文用 SnowNLP）。
- **compound 門檻的敏感度**：0.05 這個界線是隨意定的。要依你的使用情境，以及對偽陽性的容忍度來調整門檻。

## 參考資料

- VADER 詞典與規則的文件，見 `references/vader-rules.md`
- 與 transformer 情緒模型的比較，見 `references/model-comparison.md`
