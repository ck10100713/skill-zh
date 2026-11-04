---
name: "algo-nlp-summarization"
description: "用抽取式與生成式兩種方法實作文字摘要。當使用者需要濃縮長文件、建立自動摘要流程，或比較摘要策略時使用，即使他們說的是『summarize this document』『TLDR』或『key points extraction』。"
metadata:
  category: "WP-45 NLP 演算法"
  tags: ["nlp", "summarization", "extractive", "abstractive"]
---

# 文字摘要

## 概述

文字摘要在保留關鍵資訊的前提下濃縮文件。抽取式：從原文挑出重要的句子串接起來。生成式：生成改寫內容的新文字。抽取式比較簡單、也更忠於原文；生成式比較流暢，但可能產生幻覺。

## 何時使用

**觸發條件：**
- 濃縮長文件、報告或文章集合
- 為內容策展建立自動摘要流程
- 針對某個使用情境比較抽取式與生成式

**不該使用的情況：**
- 需要完整理解整份文件時（摘要會損失細節）
- 結構化資料抽取（用 NER 或資訊抽取）

## 演算法

```
IRON LAW: Abstractive Summarization Can HALLUCINATE
Abstractive models may generate fluent text containing facts NOT in
the source. Always verify key claims in abstractive summaries against
the original document. For high-stakes use cases (legal, medical),
prefer extractive or use abstractive with factual consistency checking.
```

### 階段 1：輸入驗證
確定：輸入長度、目標摘要長度（比例或字數）、單文件 vs 多文件、領域。
**關卡：** 有輸入文字，已定義目標長度。

### 階段 2：核心演算法
**抽取式（TextRank/LexRank）：**
1. 把文件切成句子
2. 建立相似度圖（句子為節點，cosine 相似度為邊）
3. 在句子圖上跑 PageRank
4. 依排名選出前 k 個句子，再依原始位置重新排序

**生成式（transformer 類）：**
1. 使用預訓練模型（BART、T5、Pegasus）
2. 編碼輸入文件（有長度限制時，視需要做分塊處理）
3. 用 beam search 生成摘要
4. 後處理：檢查有沒有重複、事實一致性

### 階段 3：驗證
評估：對參考摘要算 ROUGE 分數（ROUGE-1、ROUGE-2、ROUGE-L）。人工檢查事實準確度和連貫性。
**關卡：** ROUGE 分數對這個領域來說合理，抽樣檢查沒有幻覺。

### 階段 4：輸出
回傳摘要與 metadata。

## 輸出格式

```json
{
  "summary": "The company reported Q4 revenue of...",
  "method": "extractive_textrank",
  "metadata": {"input_words": 2000, "summary_words": 200, "compression_ratio": 0.10, "sentences_selected": 5}
}
```

## 範例

### 輸入輸出範例
**輸入：** 一篇 2000 字、關於季度財報的新聞文章
**預期：** 200 字的摘要，涵蓋：營收、獲利、財測、重點亮點。抽取式：挑 5-6 個句子。生成式：一段連貫的文字。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 非常短的輸入（< 100 字） | 原樣回傳或稍微精簡 | 本來就夠精簡了 |
| 多個互相矛盾的段落 | 摘要可能漏掉細微差異 | 摘要偏向主導的主題 |
| 專業術語 | 抽取式會保留，生成式可能簡化 | 領域專業會影響品質 |

## 注意事項

- **ROUGE ≠ 品質**：ROUGE 衡量的是和參考摘要的 n-gram 重疊度。ROUGE 高的摘要可能不連貫，ROUGE 低的摘要用詞不同，也可能非常好。
- **輸入長度限制**：Transformer 模型有最大 token 限制（512-4096）。長文件需要分塊策略（先分塊再摘要，或階層式摘要）。
- **重複**：生成式模型有時會重複片語。生成時要用重複懲罰（no_repeat_ngram_size）。
- **位置偏誤**：新聞文字的重要資訊都在前面（倒金字塔）。單純「取前 N 句」是很強的抽取式基準。
- **多文件摘要**：摘要多份相關文件時，需要處理跨來源的冗餘和矛盾。

## 參考資料

- TextRank/LexRank 的實作細節，見 `references/graph-based-extraction.md`
- 事實一致性檢查，見 `references/factual-consistency.md`
