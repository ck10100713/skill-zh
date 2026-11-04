---
name: "tech-prompt-engineering"
description: "除錯並強化 production 的 LLM prompt：處理 prompt injection、輸出格式漂移、長 context 裡指令被遺忘，以及跨模型可攜性問題。當使用者已把 LLM 功能上線到 production，需要診斷輸出為什麼不一致、不安全，或在模型更新後退步時使用這個 skill，「不適用」於一般的「幫我把 prompt 寫好一點」這類問題。"
metadata:
  category: "WP-11 通用技術"
  tags: ["technology", "llm", "production", "debugging", "security"]
---

# Production Prompt Engineering

## 概述

這個 skill 處理的是「只會」在 production LLM 應用裡出現的失敗模式：prompt injection、輸出格式漂移、跨模型版本的無聲退步、長 context 裡的指令衰減，以及壓力下的幻覺。它「不是」few-shot 或 chain-of-thought 的教學，預設 agent 已經懂基本的 prompting 技巧。

## 何時使用

**觸發條件：**
- production 的 LLM 功能行為異常（不一致、不安全、格式漂移）
- 替多租戶應用設計 system prompt
- 強化 prompt，抵禦 injection 或 jailbreak 嘗試
- 診斷模型版本更新後的退步

**何時「不」使用：**
- 基本的「怎麼寫 prompt」，agent 本來就懂 few-shot、CoT、角色扮演
- 一次性的內容生成（直接寫 prompt 就好）
- RAG 架構設計（用 RAG 專用的 skill）

## 框架

```
IRON LAW: Treat User Input as Hostile by Default
（鐵律：預設把使用者輸入當成有敵意）

在 production 裡，使用者輸入「一定」會被拿來嘗試 prompt injection。
唯一可靠的防禦是結構性隔離：
1. System prompt 承載「所有」規則和行為（絕不信任使用者輸入能覆蓋它）
2. 使用者輸入「絕對不」直接串接進指令裡
3. 輸出在被下游使用「之前」，要先對照預期 schema 驗證
一個在 dev 用乾淨輸入跑得好好的 prompt，到了 production 碰上惡意輸入就會失敗。
```

## Production 失敗模式

| 失敗模式 | 可觀察的症狀 | 根本原因 | 解法 |
|--------------|-------------------|-----------|-----|
| **Prompt injection** | 使用者輸入覆蓋了 system 指令 | 指令和不受信任的輸入被串接在一起 | 結構性隔離：用 ChatML role；對 schema 驗證輸出；絕不使用容易被「ignore previous instructions」攻破的範本 |
| **格式漂移** | JSON 回應每 1000 次呼叫會壞 1 次 | 模型 temperature > 0 + 輸出沒有約束 | 約束式解碼（JSON mode、grammar）、schema 驗證 + 重試、調低 temperature |
| **指令衰減** | 規則一開始遵守，過了 N 輪就被忽略 | 長 context 把 system prompt 擠出注意力範圍 | 在「每一則」使用者訊息裡強化關鍵規則；用模型原生的 tool/system role；縮短 context |
| **無聲退步** | 同一個 prompt，模型更新後輸出變差 | 供應商更新了模型權重 | 鎖定模型版本；維護回歸測試集；滾動升級前先 A/B 測試 |
| **壓力下的幻覺** | 模型不確定時就捏造事實 | 沒有明確的「我不知道」退路 | 加上「If uncertain, respond with {null}. Do not guess.」+ 基於事實的約束 |
| **跨模型可攜性** | 在 GPT-4 上能跑，在 Claude/Gemini 上失敗 | 各模型專屬的 prompt 慣例 | 在所有目標模型上測試；避免用特定模型的 jailbreak；採用最大公約數的寫法 |

## 方法論

### 階段 1：重現失敗
收集：確切的輸入、確切的輸出、預期的輸出、模型 + 版本、temperature。在隔離環境（app 之外）重現，排除應用程式本身的 bug。
**關卡：** 失敗能在最小測試案例裡穩定重現。

### 階段 2：分類失敗模式
對照上面的表。多數 production 失敗都落在 6 個類別之一。不要用猜的，要找出是哪一種模式。
**關卡：** 失敗模式已分類，且有證據。

### 階段 3：套用針對性的修正
只修「那個特定」的失敗模式。不要整份 prompt 重寫，泛用式的重寫常常會帶出新的失敗模式。
**關卡：** 修正針對根本原因，不是症狀。

### 階段 4：建立回歸測試
把失敗案例加進回歸測試集。每次改 prompt 或更新模型版本前，都先跑一遍測試集。
**關卡：** 測試集能抓到原本的失敗，也能抓到之後的重蹈覆轍。

## 輸出格式

```markdown
# Prompt Debug Report: {Feature Name}

## Failure Reproduction
- Input: {exact input}
- Observed: {what happened}
- Expected: {what should have happened}
- Model: {name + version + temperature}

## Failure Mode
{One of: injection, format drift, instruction decay, silent regression, hallucination, cross-model}

## Root Cause
{Specific mechanism, not generic "prompt was bad"}

## Fix
{Targeted change with before/after prompt diff}

## Regression Test
{Test case added to prevent reintroduction}
```

## 常見陷阱

- **「Ignore previous instructions」只是開始**：現代的 injection 會用角色扮演（"Pretend you are DAN..."）、切換語言、Unicode 花招和編碼過的 payload。防禦需要輸入驗證「加上」輸出驗證，不是只靠指令的措辭。
- **Temperature 0 在多次呼叫間並不是確定性的**：就算 T=0，因為後端 GPU 的非確定性（batch 效應），不同次 API 呼叫的輸出還是可能不同。測試別依賴字串完全相等，改用語意或 schema 相等。
- **Few-shot 範例會蓋過你的指令**：如果範例給的是 500 字的回應，你卻說「要簡潔」，模型會照範例走。範例比指令「更強」。
- **System prompt 不是絕對的**：即使有 system prompt，夠惡意的使用者輸入還是能覆蓋行為。System prompt 是強烈的提示，不是安全邊界。要真正的安全，得靠輸出驗證和 sandbox。
- **供應商的模型更新是無聲的**：OpenAI 的 "gpt-4" 別名會在沒通知的情況下換權重。要鎖定有日期的版本（gpt-4-0613）才穩定，每次更新後都要重跑回歸測試。
- **Context window 大小 ≠ 有效 context**：128K context 的模型可能只對前 32K 和最後 4K 注意得好。關鍵指令要放在「開頭」和「結尾」，不要放中間（"lost in the middle" 效應）。

## 參考資料

- Prompt injection 攻擊模式，見 `references/injection-patterns.md`
- 回歸測試框架，見 `references/regression-testing.md`
- 跨模型的 prompt 可攜性，見 `references/cross-model-testing.md`
