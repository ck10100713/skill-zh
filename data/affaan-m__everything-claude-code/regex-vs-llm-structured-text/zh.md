---
name: regex-vs-llm-structured-text
description: 用「regex 優先」的混合 pipeline 解析結構化文字（測驗題、表單、發票、收據、表格）的決策框架：regex 便宜地處理 95% 以上，信心評分器標出低信心項目，LLM 驗證器只修邊界案例。在 regex 與 LLM 之間選擇文字擷取方式、建置便宜的文件解析器，或最佳化擷取成本與準確度時使用。
metadata:
  origin: ECC
---

# 解析結構化文字：Regex 還是 LLM

解析結構化文字（測驗題、表單、發票、文件）的實用決策框架。關鍵洞察：regex 能便宜、確定地處理 95-98% 的情況。昂貴的 LLM 呼叫留給剩下的邊界案例。

## 何時啟用

- 解析有重複模式的結構化文字（題目、表單、表格）
- 在 regex 與 LLM 之間決定文字擷取的做法
- 建置結合兩種做法的混合 pipeline
- 最佳化文字處理的成本與準確度取捨

## 決策框架

```
文字格式是否一致而且重複？
├── 是（>90% 符合某個模式）→ 從 Regex 開始
│   ├── Regex 處理 95%+ → 完成，不需要 LLM
│   └── Regex 處理 <95% → 只針對邊界案例加上 LLM
└── 否（自由格式、變化很大）→ 直接用 LLM
```

## 架構模式

```
原始文字
    │
    ▼
[Regex Parser] ─── 擷取結構（95-98% 準確度）
    │
    ▼
[Text Cleaner] ─── 移除雜訊（標記、頁碼、殘留物）
    │
    ▼
[Confidence Scorer] ─── 標出低信心的擷取結果
    │
    ├── 高信心（≥0.95）→ 直接輸出
    │
    └── 低信心（<0.95）→ [LLM Validator] → 輸出
```

## 實作

### 1. Regex Parser（處理大多數）

```python
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class ParsedItem:
    id: str
    text: str
    choices: tuple[str, ...]
    answer: str
    confidence: float = 1.0

def parse_structured_text(content: str) -> list[ParsedItem]:
    """Parse structured text using regex patterns."""
    pattern = re.compile(
        r"(?P<id>\d+)\.\s*(?P<text>.+?)\n"
        r"(?P<choices>(?:[A-D]\..+?\n)+)"
        r"Answer:\s*(?P<answer>[A-D])",
        re.MULTILINE | re.DOTALL,
    )
    items = []
    for match in pattern.finditer(content):
        choices = tuple(
            c.strip() for c in re.findall(r"[A-D]\.\s*(.+)", match.group("choices"))
        )
        items.append(ParsedItem(
            id=match.group("id"),
            text=match.group("text").strip(),
            choices=choices,
            answer=match.group("answer"),
        ))
    return items
```

### 2. 信心評分

標出可能需要 LLM review 的項目：

```python
@dataclass(frozen=True)
class ConfidenceFlag:
    item_id: str
    score: float
    reasons: tuple[str, ...]

def score_confidence(item: ParsedItem) -> ConfidenceFlag:
    """Score extraction confidence and flag issues."""
    reasons = []
    score = 1.0

    if len(item.choices) < 3:
        reasons.append("few_choices")
        score -= 0.3

    if not item.answer:
        reasons.append("missing_answer")
        score -= 0.5

    if len(item.text) < 10:
        reasons.append("short_text")
        score -= 0.2

    return ConfidenceFlag(
        item_id=item.id,
        score=max(0.0, score),
        reasons=tuple(reasons),
    )

def identify_low_confidence(
    items: list[ParsedItem],
    threshold: float = 0.95,
) -> list[ConfidenceFlag]:
    """Return items below confidence threshold."""
    flags = [score_confidence(item) for item in items]
    return [f for f in flags if f.score < threshold]
```

### 3. LLM Validator（只處理邊界案例）

```python
def validate_with_llm(
    item: ParsedItem,
    original_text: str,
    client,
) -> ParsedItem:
    """Use LLM to fix low-confidence extractions."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # 驗證用最便宜的模型
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": (
                f"Extract the question, choices, and answer from this text.\n\n"
                f"Text: {original_text}\n\n"
                f"Current extraction: {item}\n\n"
                f"Return corrected JSON if needed, or 'CORRECT' if accurate."
            ),
        }],
    )
    # 解析 LLM 的回應並回傳修正後的項目...
    return corrected_item
```

### 4. 混合 Pipeline

```python
def process_document(
    content: str,
    *,
    llm_client=None,
    confidence_threshold: float = 0.95,
) -> list[ParsedItem]:
    """完整 pipeline：regex -> 信心檢查 -> 邊界案例交給 LLM。"""
    # 步驟 1：Regex 擷取（處理 95-98%）
    items = parse_structured_text(content)

    # 步驟 2：信心評分
    low_confidence = identify_low_confidence(items, confidence_threshold)

    if not low_confidence or llm_client is None:
        return items

    # 步驟 3：LLM 驗證（只針對被標出的項目）
    low_conf_ids = {f.item_id for f in low_confidence}
    result = []
    for item in items:
        if item.id in low_conf_ids:
            result.append(validate_with_llm(item, content, llm_client))
        else:
            result.append(item)

    return result
```

## 真實世界的指標

來自一個 production 測驗解析 pipeline（410 題）：

| 指標 | 數值 |
|--------|-------|
| Regex 成功率 | 98.0% |
| 低信心項目 | 8（2.0%） |
| 需要的 LLM 呼叫 | 約 5 次 |
| 相較全部用 LLM 省下的成本 | 約 95% |
| 測試覆蓋率 | 93% |

## 最佳實踐

- **從 regex 開始**：即使不完美的 regex，也給你一個可以改進的基準
- **用信心評分**，以程式方式找出哪些需要 LLM 幫忙
- 驗證用**最便宜的 LLM**（Haiku 等級的模型就夠了）
- **絕對不要修改**已解析的項目，在清理／驗證步驟中回傳新的實例
- 解析器**很適合 TDD**：先為已知的模式寫測試，再寫邊界案例
- **記錄指標**（regex 成功率、LLM 呼叫次數），追蹤 pipeline 的健康度

## 要避免的反模式

- regex 能處理 95% 以上的情況，卻把所有文字都送給 LLM（又貴又慢）
- 對自由格式、變化很大的文字用 regex（這種情況 LLM 比較好）
- 跳過信心評分，只希望 regex「自然會對」
- 在清理／驗證步驟中修改已解析的物件
- 沒測邊界案例（格式錯誤的輸入、缺少欄位、編碼問題）

## 何時使用

- 測驗／考試題目解析
- 表單資料擷取
- 發票／收據處理
- 文件結構解析（標題、章節、表格）
- 任何有重複模式、而且在意成本的結構化文字
