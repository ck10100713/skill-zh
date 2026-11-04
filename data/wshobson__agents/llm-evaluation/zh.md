---
name: llm-evaluation
description: 用自動化指標、人工回饋與 benchmark，為 LLM 應用實作完整的評估策略。在測試 LLM 效能、衡量 AI 應用品質或建立評估框架時使用。
---

# LLM Evaluation

精通 LLM 應用的完整評估策略，從自動化指標到人工評估與 A/B 測試。

## When to Use This Skill

- 有系統地衡量 LLM 應用的效能
- 比較不同的模型或 prompt
- 在部署前偵測效能退化
- 驗證 prompt 修改帶來的改進
- 對正式環境系統建立信心
- 建立基準線並長期追蹤進展
- 排查模型出現的非預期行為

## Core Evaluation Types

### 1. Automated Metrics

用計算出來的分數做評估，快速、可重複、可擴展。

**文字生成：**

- **BLEU**：N-gram 重疊度（翻譯）
- **ROUGE**：偏重召回率（摘要）
- **METEOR**：語意相似度
- **BERTScore**：以 embedding 為基礎的相似度
- **Perplexity**：語言模型的信心程度

**分類：**

- **Accuracy**：答對的百分比
- **Precision/Recall/F1**：各類別的表現
- **Confusion Matrix**：錯誤模式
- **AUC-ROC**：排序品質

**檢索（RAG）：**

- **MRR**：Mean Reciprocal Rank
- **NDCG**：Normalized Discounted Cumulative Gain
- **Precision@K**：前 K 筆中相關的比例
- **Recall@K**：前 K 筆的涵蓋率

### 2. Human Evaluation

針對難以自動化的品質面向，用人工評估。

**評估面向：**

- **Accuracy**：事實是否正確
- **Coherence**：邏輯是否通順
- **Relevance**：有沒有回答到問題
- **Fluency**：語言是否自然
- **Safety**：沒有有害內容
- **Helpfulness**：對使用者有沒有用

### 3. LLM-as-Judge

用比較強的 LLM 去評估較弱模型的輸出。

**做法：**

- **Pointwise**：替單一回應打分數
- **Pairwise**：比較兩個回應
- **Reference-based**：和標準答案比較
- **Reference-free**：沒有 ground truth 也能評判

## Quick Start

```python
from dataclasses import dataclass
from typing import Callable
import numpy as np

@dataclass
class Metric:
    name: str
    fn: Callable

    @staticmethod
    def accuracy():
        return Metric("accuracy", calculate_accuracy)

    @staticmethod
    def bleu():
        return Metric("bleu", calculate_bleu)

    @staticmethod
    def bertscore():
        return Metric("bertscore", calculate_bertscore)

    @staticmethod
    def custom(name: str, fn: Callable):
        return Metric(name, fn)

class EvaluationSuite:
    def __init__(self, metrics: list[Metric]):
        self.metrics = metrics

    async def evaluate(self, model, test_cases: list[dict]) -> dict:
        results = {m.name: [] for m in self.metrics}

        for test in test_cases:
            prediction = await model.predict(test["input"])

            for metric in self.metrics:
                score = metric.fn(
                    prediction=prediction,
                    reference=test.get("expected"),
                    context=test.get("context")
                )
                results[metric.name].append(score)

        return {
            "metrics": {k: np.mean(v) for k, v in results.items()},
            "raw_scores": results
        }

# Usage
suite = EvaluationSuite([
    Metric.accuracy(),
    Metric.bleu(),
    Metric.bertscore(),
    Metric.custom("groundedness", check_groundedness)
])

test_cases = [
    {
        "input": "What is the capital of France?",
        "expected": "Paris",
        "context": "France is a country in Europe. Paris is its capital."
    },
]

results = await suite.evaluate(model=your_model, test_cases=test_cases)
```

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

