---
name: cost-aware-llm-pipeline
description: LLM API 用量的成本優化模式，包含依任務複雜度做模型路由、預算追蹤、重試邏輯和 prompt caching。當 LLM 花費需要降下來，或要在不同模型等級與預算之間分配任務時使用。
metadata:
  origin: ECC
---

# 成本感知的 LLM Pipeline

在維持品質的前提下控制 LLM API 成本的一組模式。把模型路由、預算追蹤、重試邏輯和 prompt caching 組合成一條可以拼裝的 pipeline。

## 何時啟用

- 開發會呼叫 LLM API（Claude、GPT 等）的應用
- 批次處理複雜度不一的項目
- 需要把 API 花費控制在預算內
- 想省成本，但複雜任務的品質不能掉

## 核心概念

### 1. 依任務複雜度做模型路由

簡單任務自動選便宜的模型，貴的模型留給複雜任務。

```python
MODEL_SONNET = "claude-sonnet-5"
MODEL_HAIKU = "claude-haiku-4-5-20251001"

_SONNET_TEXT_THRESHOLD = 10_000  # chars
_SONNET_ITEM_THRESHOLD = 30     # items

def select_model(
    text_length: int,
    item_count: int,
    force_model: str | None = None,
) -> str:
    """Select model based on task complexity."""
    if force_model is not None:
        return force_model
    if text_length >= _SONNET_TEXT_THRESHOLD or item_count >= _SONNET_ITEM_THRESHOLD:
        return MODEL_SONNET  # Complex task
    return MODEL_HAIKU  # Simple task (3-4x cheaper)
```

### 2. 不可變的成本追蹤

用 frozen dataclass 追蹤累計花費。每次 API 呼叫都回傳一個新的 tracker，絕不修改原本的狀態。

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

@dataclass(frozen=True, slots=True)
class CostTracker:
    budget_limit: float = 1.00
    records: tuple[CostRecord, ...] = ()

    def add(self, record: CostRecord) -> "CostTracker":
        """Return new tracker with added record (never mutates self)."""
        return CostTracker(
            budget_limit=self.budget_limit,
            records=(*self.records, record),
        )

    @property
    def total_cost(self) -> float:
        return sum(r.cost_usd for r in self.records)

    @property
    def over_budget(self) -> bool:
        return self.total_cost > self.budget_limit
```

### 3. 範圍收窄的重試邏輯

只對暫時性錯誤重試。認證錯誤或 bad request 這類錯誤要直接失敗。

```python
from anthropic import (
    APIConnectionError,
    InternalServerError,
    RateLimitError,
)

_RETRYABLE_ERRORS = (APIConnectionError, RateLimitError, InternalServerError)
_MAX_RETRIES = 3

def call_with_retry(func, *, max_retries: int = _MAX_RETRIES):
    """Retry only on transient errors, fail fast on others."""
    for attempt in range(max_retries):
        try:
            return func()
        except _RETRYABLE_ERRORS:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    # AuthenticationError, BadRequestError etc. → raise immediately
```

### 4. Prompt Caching

把很長的 system prompt 快取起來，不用每次請求都重送一遍。

```python
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},  # Cache this
            },
            {
                "type": "text",
                "text": user_input,  # Variable part
            },
        ],
    }
]
```

## 組合起來

把四個技巧合在同一個 pipeline 函式裡：

```python
def process(text: str, config: Config, tracker: CostTracker) -> tuple[Result, CostTracker]:
    # 1. Route model
    model = select_model(len(text), estimated_items, config.force_model)

    # 2. Check budget
    if tracker.over_budget:
        raise BudgetExceededError(tracker.total_cost, tracker.budget_limit)

    # 3. Call with retry + caching
    response = call_with_retry(lambda: client.messages.create(
        model=model,
        messages=build_cached_messages(system_prompt, text),
    ))

    # 4. Track cost (immutable)
    record = CostRecord(model=model, input_tokens=..., output_tokens=..., cost_usd=...)
    tracker = tracker.add(record)

    return parse_result(response), tracker
```

## 價格參考（2026）

| 模型 | 輸入（$/1M tokens） | 輸出（$/1M tokens） | 相對成本 |
|-------|---------------------|----------------------|---------------|
| Haiku 3.5 (legacy) | $0.80 | $4.00 | 0.8x |
| Haiku 4.5 | $1.00 | $5.00 | 1x |
| Sonnet 5 | $2.00 | $10.00 | 2x |
| Sonnet 4.6 | $3.00 | $15.00 | 3x |
| Opus 4.8 | $5.00 | $25.00 | 5x |
| Fable 5 / Mythos 5 | $10.00 | $50.00 | 10x |
| Opus 4.0 / 4.1 (legacy) | $15.00 | $75.00 | 15x |

## 最佳實務

- **從最便宜的模型開始**，達到複雜度門檻才路由到貴的模型
- **處理批次前先設好明確的預算上限**，寧可早點失敗，也不要超支
- **記錄模型選擇的決策**，之後才能根據真實資料調整門檻
- **超過 1024 tokens 的 system prompt 要用 prompt caching**，成本和延遲都能省
- **認證或驗證錯誤絕對不要重試**，只有暫時性失敗（網路、rate limit、server error）才重試

## 要避免的反模式

- 不管複雜度，所有請求都用最貴的模型
- 所有錯誤都重試（永久性失敗只會白白燒預算）
- 修改成本追蹤的狀態（會讓除錯和稽核變困難）
- 在整個 codebase 到處寫死模型名稱（用常數或設定檔）
- 重複使用的 system prompt 卻不用 prompt caching

## 何時使用

- 任何會呼叫 Claude、OpenAI 或類似 LLM API 的應用
- 成本很快就會累積起來的批次處理 pipeline
- 需要智慧路由的多模型架構
- 需要預算護欄的 production 系統
