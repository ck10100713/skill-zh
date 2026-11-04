---
name: rag-implementation
description: 用向量資料庫和語意搜尋，為 LLM 應用建構 Retrieval-Augmented Generation（RAG）系統。在實作有知識依據的 AI、建構文件問答系統，或把 LLM 接上外部知識庫時使用。
---

# RAG Implementation

精通 Retrieval-Augmented Generation（RAG），打造能利用外部知識來源、給出準確且有依據回答的 LLM 應用。

## When to Use This Skill

- 針對私有文件建構問答系統
- 建立能提供最新、事實性資訊的聊天機器人
- 用自然語言查詢實作語意搜尋
- 用有依據的回答減少幻覺
- 讓 LLM 能存取特定領域的知識
- 建構文件助理
- 建立附帶來源引用的研究工具

## Core Components

### 1. Vector Databases

**用途**：有效率地儲存和檢索文件 embedding

**選項：**

- **Pinecone**：託管式、可擴展、serverless
- **Weaviate**：開源、混合搜尋、GraphQL
- **Milvus**：高效能、可地端部署
- **Chroma**：輕量、好上手、適合本機開發
- **Qdrant**：快速、支援過濾搜尋、用 Rust 寫的
- **pgvector**：PostgreSQL 擴充套件，可跟 SQL 整合

### 2. Embeddings

**用途**：把文字轉成數值向量，用來做相似度搜尋

**模型（2026）：**
| Model | Dimensions | Best For |
|-------|------------|----------|
| **voyage-3-large** | 1024 | Claude 應用（Anthropic 推薦） |
| **voyage-code-3** | 1024 | 程式碼搜尋 |
| **text-embedding-3-large** | 3072 | OpenAI 應用、高準確度 |
| **text-embedding-3-small** | 1536 | OpenAI 應用、高性價比 |
| **bge-large-en-v1.5** | 1024 | 開源、本機部署 |
| **multilingual-e5-large** | 1024 | 多語言支援 |

### 3. Retrieval Strategies

**做法：**

- **Dense Retrieval**：用 embedding 做語意相似度
- **Sparse Retrieval**：關鍵字比對（BM25、TF-IDF）
- **Hybrid Search**：用加權融合結合 dense + sparse
- **Multi-Query**：產生多種查詢變體
- **HyDE**：產生假設性文件來提升檢索效果

### 4. Reranking

**用途**：重新排序結果來提升檢索品質

**方法：**

- **Cross-Encoders**：以 BERT 為基礎的 rerank（ms-marco-MiniLM）
- **Cohere Rerank**：以 API 提供的 rerank
- **Maximal Marginal Relevance (MMR)**：兼顧多樣性和相關性
- **LLM-based**：用 LLM 為相關性打分

## Quick Start with LangGraph

```python
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_voyageai import VoyageAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import TypedDict, Annotated

class RAGState(TypedDict):
    question: str
    context: list[Document]
    answer: str

# Initialize components
llm = ChatAnthropic(model="claude-sonnet-5")
embeddings = VoyageAIEmbeddings(model="voyage-3-large")
vectorstore = PineconeVectorStore(index_name="docs", embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# RAG prompt
rag_prompt = ChatPromptTemplate.from_template(
    """Answer based on the context below. If you cannot answer, say so.

    Context:
    {context}

    Question: {question}

    Answer:"""
)

async def retrieve(state: RAGState) -> RAGState:
    """Retrieve relevant documents."""
    docs = await retriever.ainvoke(state["question"])
    return {"context": docs}

async def generate(state: RAGState) -> RAGState:
    """Generate answer from context."""
    context_text = "\n\n".join(doc.page_content for doc in state["context"])
    messages = rag_prompt.format_messages(
        context=context_text,
        question=state["question"]
    )
    response = await llm.ainvoke(messages)
    return {"answer": response.content}

# Build RAG graph
builder = StateGraph(RAGState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

rag_chain = builder.compile()

# Use
result = await rag_chain.ainvoke({"question": "What are the main features?"})
print(result["answer"])
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。
