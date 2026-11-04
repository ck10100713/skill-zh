---
name: embedding-strategies
description: 為向量搜尋應用挑選並最佳化 embedding 模型的指南。適用於為 RAG 選 embedding 模型、最佳化 chunking 策略、針對特定領域 fine-tune embedding 的時候。
---

# Embedding 策略

為向量搜尋應用挑選並最佳化 embedding 模型的指南。

## 什麼時候用這個 Skill

- 為 RAG 挑選 embedding 模型
- 最佳化 chunking 策略
- 針對特定領域 fine-tune embedding
- 比較 embedding 模型的效能
- 降低 embedding 維度
- 處理多語言內容

## 核心概念

### 1. Embedding 模型比較（2026）

| 模型                       | 維度       | 最大 Token | 最適合                              |
| -------------------------- | ---------- | ---------- | ----------------------------------- |
| **voyage-3-large**         | 1024       | 32000      | Claude 應用（Anthropic 推薦）       |
| **voyage-3**               | 1024       | 32000      | Claude 應用，成本效益高             |
| **voyage-code-3**          | 1024       | 32000      | 程式碼搜尋                          |
| **voyage-finance-2**       | 1024       | 32000      | 金融文件                            |
| **voyage-law-2**           | 1024       | 32000      | 法律文件                            |
| **text-embedding-3-large** | 3072       | 8191       | OpenAI 應用，高準確度               |
| **text-embedding-3-small** | 1536       | 8191       | OpenAI 應用，成本效益高             |
| **bge-large-en-v1.5**      | 1024       | 512        | 開源、本機 deploy                   |
| **all-MiniLM-L6-v2**       | 384        | 256        | 快速、輕量                          |
| **multilingual-e5-large**  | 1024       | 512        | 多語言                              |

### 2. Embedding Pipeline

```
文件 → Chunking → 前處理 → Embedding 模型 → 向量
                ↓
        [Overlap, Size]  [Clean, Normalize]  [API/Local]
```

## 範本與詳細實作範例

完整的範本庫和詳細實作範例放在 `references/details.md`，需要具體範本的時候去讀那份檔案。

## 最佳實務

### 該做的

- **模型要配合使用情境**：程式碼、散文、多語言各有適合的
- **謹慎地 chunk**：保留語意邊界
- **正規化 embedding**：用於 cosine similarity 搜尋
- **批次送出請求**：比一筆一筆送更有效率
- **快取 embedding**：靜態內容避免重複計算
- **Claude 應用用 Voyage AI**：Anthropic 推薦

### 不該做的

- **不要忽略 token 上限**：截斷會遺失資訊
- **不要混用 embedding 模型**：向量空間不相容
- **不要跳過前處理**：垃圾進、垃圾出
- **不要切太碎**：會丟失重要的上下文
- **不要忘記 metadata**：過濾和除錯都需要
