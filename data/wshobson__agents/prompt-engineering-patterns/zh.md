---
name: prompt-engineering-patterns
description: >-
  當使用者要求「優化 prompt」、「提升 prompt 效能」、「設計 prompt 範本」、「寫出更好的 prompt」、「除錯 prompt 問題」、「使用 chain-of-thought」、「結構化 prompting」、「few-shot prompting」，或想把進階的
  prompt engineering 模式套用到正式環境的 LLM 應用時，應使用這個 skill。
---

# Prompt Engineering Patterns

精通進階的 prompt engineering 技巧，讓 LLM 的效能、可靠度與可控性達到最大。

## When to Use This Skill

- 為正式環境的 LLM 應用設計複雜的 prompt
- 優化 prompt 的效能與一致性
- 實作結構化推理模式（chain-of-thought、tree-of-thought）
- 建構能動態挑選範例的 few-shot learning 系統
- 建立支援變數插值的可重用 prompt 範本
- 除錯並改善輸出不一致的 prompt
- 為專門的 AI 助理實作 system prompt
- 使用結構化輸出（JSON mode）做可靠的解析

## Core Capabilities

### 1. Few-Shot Learning

- 範例選擇策略（語意相似度、多樣性取樣）
- 在範例數量與 context window 限制之間取得平衡
- 用輸入輸出配對建構有效的示範
- 從知識庫動態檢索範例
- 透過策略性的範例選擇處理邊界案例

### 2. Chain-of-Thought Prompting

- 引導出逐步推理
- 用「Let's think step by step」做 zero-shot CoT
- 搭配推理軌跡的 few-shot CoT
- Self-consistency 技巧（取樣多條推理路徑）
- 驗證與確認步驟

### 3. Structured Outputs

- 用 JSON mode 做可靠的解析
- 用 Pydantic schema 強制格式
- 型別安全的回應處理
- 格式錯誤輸出的錯誤處理

### 4. Prompt Optimization

- 迭代式的改進流程
- 對 prompt 變體做 A/B 測試
- 衡量 prompt 的效能指標（準確度、一致性、延遲）
- 在維持品質的同時降低 token 用量
- 處理邊界案例與失效模式

### 5. Template Systems

- 變數插值與格式化
- 條件式的 prompt 段落
- 多輪對話範本
- 以角色為基礎的 prompt 組合
- 模組化的 prompt 元件

### 6. System Prompt Design

- 設定模型的行為與限制
- 定義輸出格式與結構
- 建立角色與專業領域
- 安全準則與內容政策
- 設定 context 與背景資訊

## Quick Start

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# Define structured output schema
class SQLQuery(BaseModel):
    query: str = Field(description="The SQL query")
    explanation: str = Field(description="Brief explanation of what the query does")
    tables_used: list[str] = Field(description="List of tables referenced")

# Initialize model with structured output
llm = ChatAnthropic(model="claude-sonnet-5")
structured_llm = llm.with_structured_output(SQLQuery)

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert SQL developer. Generate efficient, secure SQL queries.
    Always use parameterized queries to prevent SQL injection.
    Explain your reasoning briefly."""),
    ("user", "Convert this to SQL: {query}")
])

# Create chain
chain = prompt | structured_llm

# Use
result = await chain.ainvoke({
    "query": "Find all users who registered in the last 30 days"
})
print(result.query)
print(result.explanation)
```

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Best Practices

1. **要具體**：模糊的 prompt 會產出不一致的結果
2. **用示範，不要用說明**：範例比描述有效
3. **使用結構化輸出**：用 Pydantic 強制 schema，提高可靠度
4. **充分測試**：用多樣且具代表性的輸入來評估
5. **快速迭代**：小改動可能帶來大影響
6. **監控效能**：在正式環境追蹤指標
7. **版本控管**：把 prompt 當成程式碼，做好版本控管
8. **記錄意圖**：說明 prompt 為什麼要這樣組織

## Common Pitfalls

- **過度設計**：還沒試過簡單的 prompt 就先用複雜的
- **範例污染**：使用跟目標任務不符的範例
- **Context 溢位**：範例太多，超過 token 上限
- **指令模糊**：留下多種解讀的空間
- **忽略邊界案例**：沒有用不尋常或極端的輸入測試
- **沒有錯誤處理**：假設輸出一定格式正確
- **寫死的值**：沒有把 prompt 參數化以便重用

## Success Metrics

為你的 prompt 追蹤這些 KPI：

- **Accuracy**：輸出的正確性
- **Consistency**：相似輸入之間的可重現性
- **Latency**：回應時間（P50、P95、P99）
- **Token Usage**：每個請求的平均 token 數
- **Success Rate**：有效、可解析的輸出所占的百分比
- **User Satisfaction**：評分與回饋
