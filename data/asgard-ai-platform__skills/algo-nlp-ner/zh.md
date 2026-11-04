---
name: "algo-nlp-ner"
description: "實作具名實體辨識（NER），辨識並分類文字中的實體。當使用者需要從文件中抽出人物、組織、地點、日期或自訂實體時使用，即使他們說的是『extract names from text』『find companies mentioned』或『entity extraction』。"
metadata:
  category: "WP-45 NLP 演算法"
  tags: ["nlp", "ner", "entity-extraction", "information-extraction"]
---

# 具名實體辨識

## 概述

NER 辨識文字中的具名實體，並分類到預先定義的類別（人物、組織、地點、日期、金額等）。做法有：規則式（regex、gazetteer）、統計式（CRF）、神經網路式（BiLSTM-CRF、transformer 類）。現代 NER 使用 spaCy 或 Hugging Face 模型，F1 分數 85-95%。

## 何時使用

**觸發條件：**
- 從非結構化文字抽出結構化實體
- 從文件建立知識圖譜
- 為資訊檢索或問答做前處理

**不該使用的情況：**
- 文字分類（替整份文件分類，而不是抽出實體）
- 實體之間的關係抽取（需要額外的 RE 模型）

## 演算法

```
IRON LAW: NER Performance Depends on DOMAIN Match
A model trained on news text (OntoNotes) performs poorly on medical
records or legal documents. Domain-specific entities (drug names,
legal citations, product SKUs) require domain-specific training data
or fine-tuning. Always evaluate on YOUR domain's data.
```

### 階段 1：輸入驗證
確定：目標實體類型（標準：PER、ORG、LOC、DATE、MONEY，或自訂）、輸入語言、領域。選擇合適的預訓練模型，或準備訓練資料。
**關卡：** 實體類型已定義，有模型或訓練資料。

### 階段 2：核心演算法
**預訓練模型做法：**
1. 載入模型（spaCy、Hugging Face NER pipeline）
2. 讓文字通過 pipeline
3. 抽出實體片段，附上類型標籤和信心分數

**Fine-tuning 做法：**
1. 用 BIO 格式標註 200 筆以上的領域專屬範例
2. 用標註資料 fine-tune transformer 模型（BERT、RoBERTa）
3. 在保留的測試集上評估

### 階段 3：驗證
評估：每個實體類型的 precision、recall、F1。檢查：邊界偵測（片段完全比對）和類型分類的準確度。
**關卡：** 在領域相關的測試資料上，每個實體類型的 F1 > 0.80。

### 階段 4：輸出
回傳抽出的實體，附上類型、位置和信心。

## 輸出格式

```json
{
  "entities": [{"text": "Apple Inc.", "type": "ORG", "start": 0, "end": 10, "confidence": 0.95}],
  "metadata": {"model": "en_core_web_trf", "entities_found": 15, "types": {"PER": 5, "ORG": 6, "LOC": 4}}
}
```

## 範例

### 輸入輸出範例
**輸入：** "Tim Cook announced that Apple will open a new store in Taipei on March 15."
**預期：** [Tim Cook/PER, Apple/ORG, Taipei/LOC, March 15/DATE]

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 「Apple」（沒有上下文） | 有歧義（水果還是公司） | 實體類型取決於上下文 |
| 巢狀實體 | 看標註方案而定 | 「Bank of America」= ORG，其中的「America」= LOC |
| 拼錯的實體 | 可能漏掉 | 「Appel」不在訓練資料裡 |

## 注意事項

- **邊界錯誤**：NER 常常類型對了但片段錯了（「New」vs「New York City」）。要同時用完全比對和部分比對的指標來評估。
- **歧義**：「Jordan」可能是人名、國家或品牌。依上下文消歧很難；有些模型只輸出最可能的類型。
- **中文 / 日文 NER**：沒有空白可以斷詞，邊界偵測更難。要用該語言專用的斷詞器（中文用 jieba）。
- **標註一致性**：訓練資料的品質至關重要。標註不一致（有時把「Dr.」當成名字的一部分，有時不當）會讓模型表現變差。
- **實體連結**：NER 辨識提及的字詞；實體連結則是把它們對應到知識庫條目。「Apple」→ Apple Inc. (Q312) 或蘋果（水果）。這是兩個不同的任務。

## 參考資料

- BIO 標註格式與指引，見 `references/bio-annotation.md`
- 用 transformer fine-tune NER，見 `references/transformer-ner.md`
