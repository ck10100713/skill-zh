---
name: "cs-chatbot-design"
description: "設計對話式 AI 聊天機器人，包含意圖辨識、slot 填充、對話流程與回應生成。當使用者需要建立聊天機器人、設計對話流程、實作意圖分類，或提升機器人準確度時使用。就算使用者只說「做一個 chatbot」、「我們的機器人聽不懂使用者在說什麼」、「設計 FAQ 機器人」或「改善機器人的回覆」也要用。"
metadata:
  category: "WP-06 Agent通訊+客服"
  tags: ["chatbot", "conversational-ai", "nlu", "dialogue"]
---

# 聊天機器人設計

## 框架

```
IRON LAW: Intent First, Response Second

A chatbot must UNDERSTAND what the user wants (intent) before crafting
a response. Building response templates without intent classification
produces a keyword-matching FAQ, not a chatbot.

Flow: User message → Intent classification → Slot extraction → Response
```

### 核心 NLU 流程

| 階段 | 做什麼 | 範例 |
|-------|-------------|---------|
| **意圖分類（Intent Classification）** | 辨識使用者想做什麼 | 「你們幾點打烊？」→ intent: `check_hours` |
| **實體/Slot 擷取** | 從訊息中擷取關鍵資訊 | 「幫我訂週五 4 個人的位子」→ slots: {party_size: 4, date: Friday} |
| **對話管理（Dialogue Management）** | 決定下一步動作（補問缺少的資訊、確認、執行） | 缺少 slot `time` → 問「你想訂幾點？」 |
| **回應生成（Response Generation）** | 產生回覆 | 「已幫你訂好週五晚上 7 點 4 位的座位，到時候見！」 |

### 意圖設計

- **從 10 到 15 個核心意圖開始**，涵蓋 80% 的使用者問題
- 每個意圖需要 10 到 20 個訓練範例（不同說法）
- 加一個 `fallback` 意圖，處理辨識不出來的輸入
- 把相關意圖分組：`order_status`、`order_cancel`、`order_modify` 歸在「訂單管理」底下

### 對話流程模式

| 模式 | 何時使用 | 範例 |
|---------|-----------|---------|
| **單輪（Single-turn）** | 簡單問答，不需要上下文 | 「你們營業時間？」→ 直接回答 |
| **多輪（slot 填充）** | 需要多項資訊 | 「我要訂位」→ 問人數 → 問日期 → 問時間 → 確認 |
| **分支（Branching）** | 依使用者的回答走不同路徑 | 「你有帳號嗎？」→ 有：登入流程 / 沒有：註冊流程 |
| **確認（Confirmation）** | 執行動作之前 | 「我會取消訂單 #12345，這樣對嗎？」 |
| **轉接（Handoff）** | 機器人處理不了這個需求 | 「我幫你轉接真人客服」 |

### 回應設計原則

1. **先確認收到**：「了解，你想查詢訂單狀態。」
2. **簡潔**：回答問題就停，不要多加不必要的資訊。
3. **提供下一步**：「還有什麼我可以幫忙的嗎？」或建議相關操作。
4. **用快速回覆/按鈕**：減少打字、引導對話。
5. **個性**：定義一致的語氣（親切、專業、輕鬆），然後堅持下去。

### 指標

| 指標 | 定義 | 目標 |
|--------|-----------|--------|
| **意圖準確率** | 意圖分類正確的比例 | > 85% |
| **自助解決率（Containment rate）** | 不需轉真人就解決的比例 | > 60-70% |
| **CSAT** | 客戶滿意度分數 | > 4.0/5 |
| **Fallback 率** | 觸發 fallback/未知意圖的比例 | < 15% |
| **解決時間** | 平均解決時間 | < 2 分鐘 |

## 輸出格式

```markdown
# Chatbot Design: {Use Case}

## Intent Catalog
| Intent | Description | Example Utterances | Priority |
|--------|-----------|-------------------|---------|
| {intent} | {what it means} | "{example 1}", "{example 2}" | H/M/L |

## Dialogue Flows
### {Flow Name}
1. User: {trigger utterance}
2. Bot: {response + slot question if needed}
3. User: {provides info}
4. Bot: {confirmation or action}

## Fallback Strategy
- After 1 miss: rephrase + suggest options
- After 2 misses: offer human handoff

## Metrics Targets
| Metric | Target |
|--------|--------|
| Intent accuracy | > {X%} |
| Containment | > {X%} |
```

## 常見陷阱

- **使用者不會照你的流程走**：人們會用意想不到的方式打字、對話中途換話題、給不完整的資訊。要為混亂的情況設計，不要只顧順利路徑。
- **Fallback 是最重要的意圖**：好的 fallback（「我不太確定我理解對了，你是指 X、Y 還是 Z？」）比亂猜好。
- **用 LLM 的機器人還是需要護欄**：用 GPT/Claude 生成回應？第一層還是要加意圖分類來做路由和限制，避免幻覺和離題的回答。
- **要用真實使用者測試，不要只讓團隊成員測**：你的團隊知道機器人怎麼運作，講話也「講得對」。真實使用者不會。上線前至少找 10 位以上的真實使用者測試。
- **對話紀錄是金礦**：每週檢視對話紀錄。失敗的對話會暴露缺少的意圖、讓人困惑的流程，以及訓練資料的缺口。

## 參考資料

- NLU 訓練資料的最佳實務，見 `references/nlu-training.md`
- LINE/Messenger 平台整合，見 ecom-conversational skill
