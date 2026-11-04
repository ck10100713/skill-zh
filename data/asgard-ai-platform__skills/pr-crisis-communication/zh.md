---
name: "pr-crisis-communication"
description: "用 SCCT 理論和危機聲明框架，管理預防、因應、復原三個階段的危機溝通。使用者面臨公關危機、需要擬定危機回應、規劃危機準備，或要處理負面的公眾關注時使用，就算他們說的是「我們上了負面新聞」、「這個醜聞我們該怎麼回應」、「擬一份公開聲明」或「為可能的反彈做準備」也一樣。"
metadata:
  category: "WP-21 設計/資訊/傳播/公衛"
  tags: ["communication", "crisis-management", "pr"]
---

# 危機溝通

## 框架

```
IRON LAW: Respond in the Golden Hour

The first public response must come within 1 hour of the crisis becoming
public. Silence creates a vacuum that others fill with speculation.
A holding statement ("We are aware and investigating") is better than
no statement. Perfection is the enemy of timeliness.
```

### 三個階段

**1. 預防**（危機之前）
- 找出潛在的危機（風險盤點）
- 準備暫時性聲明（holding statement）並訓練發言人
- 成立危機小組，角色分工明確
- 監控媒體與社群管道

**2. 因應**（危機期間）
- 啟動危機小組
- 立刻發出暫時性聲明
- 快速蒐集事實
- 用 3C 框架發出完整聲明：
  - **Concern（關切）**：對受影響的各方表達同理
  - **Commitment（承諾）**：說明你針對這件事做了什麼
  - **Control（掌控）**：展現你正在掌握局面

**3. 復原**（危機之後）
- 評估損害與學到的教訓
- 執行矯正措施
- 透過行動（不只是言語）重建利害關係人的信任
- 根據學到的教訓更新危機計畫

### SCCT（情境式危機溝通理論）

| 危機類型 | 責任歸屬 | 回應策略 |
|------------|---------------------|-------------------|
| **受害者型**（天災、謠言） | 低：組織同樣是受害者 | 否認／淡化 |
| **意外型**（技術錯誤、產品瑕疵） | 中：非故意 | 淡化／重建 |
| **可預防型**（人為失誤、組織失能） | 高：本來可以避免 | 重建（完整道歉 + 矯正行動） |

### 危機聲明範本

```
[關切] 我們對 [具體情況] 深感關切，我們的心與 [受影響的各方] 同在。

[事實] 以下是我們目前所知：[事實摘要，不做臆測]。

[承諾] 我們正在採取以下立即行動：
1. [行動 1]
2. [行動 2]

[掌控] 我們已啟動 [應變小組／流程]，並將以 [頻率與管道] 提供最新進展。

[聯絡] 如有疑問，請聯絡 [發言人、管道]。
```

## 輸出格式

```markdown
# Crisis Response Plan: {Situation}

## Crisis Assessment
- Type: Victim / Accidental / Preventable
- Severity: Low / Medium / High
- Stakeholders affected: {list}
- Media attention level: {current state}

## Immediate Response (< 1 hour)
- Holding statement: {draft}
- Spokesperson: {who}
- Internal notification: {who needs to know}

## Full Response (< 24 hours)
- Full statement: {draft using 3C framework}
- Key messages (3 max): ...
- Channel strategy: {where to publish}
- Q&A preparation: {anticipated questions + answers}

## Recovery Plan
- Corrective actions: ...
- Trust-rebuilding steps: ...
- Timeline: ...
```

## 注意事項

- **絕對不要說謊或臆測**：如果你不知道，就說「我們正在調查」。危機聲明裡寫錯一個事實，就會變成下一場危機。
- **社群媒體讓一切加速**：2010 年要花好幾天才會發展起來的危機，在 2025 年只要幾個小時。回應的速度必須跟得上擴散的速度。
- **先做內部溝通**：員工應該先從你這裡聽到，而不是從媒體聽到。內部聲明要在對外聲明之前，或同時發出。
- **道歉需要具體**：「如果有人覺得被冒犯，我們感到抱歉」不是道歉。「我們為 [具體行為] 造成的 [具體傷害] 道歉」才是。
- **法務與公關的拉扯**：法務團隊想什麼都不說（責任）。公關團隊想什麼都說（信任）。正確的答案通常是：承認事實、表達同理、承諾行動，同時不要過早承認法律責任。

## 參考資料

- 社群媒體危機應對手冊請看 `references/social-crisis.md`
