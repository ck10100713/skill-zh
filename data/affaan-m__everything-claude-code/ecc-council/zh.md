---
name: ecc-council
description: 為含糊的決策、取捨與 go/no-go 判斷，召集四個聲音組成的 council。在有多條合理路徑、需要先有結構化的分歧再做選擇時使用。
metadata:
  origin: ECC
---

# Council

為含糊的決策召集四位顧問：
- context 內的 Claude 本人
- 一個 Skeptic subagent
- 一個 Pragmatist subagent
- 一個 Critic subagent

這是用來做**含糊情境下的決策**，不是用在 code review、實作規劃或架構設計。

## 何時使用

在下列情況使用 council：
- 一個決策有多條可信的路徑，沒有明顯的贏家
- 需要把取捨明確攤開
- 使用者要求第二意見、反方意見或多個觀點
- 對話造成的錨定效應是真實的風險
- go / no-go 判斷需要對抗式的挑戰

範例：
- monorepo vs polyrepo
- 現在就 ship vs 先等打磨完
- feature flag vs 完整 rollout
- 縮小範圍 vs 保留策略上的廣度

## 何時不要使用

| 不要用 council，改用 | 用 |
| --- | --- |
| 驗證輸出對不對 | `santa-method` |
| 把功能拆成實作步驟 | `planner` |
| 設計系統架構 | `architect` |
| review 程式碼找 bug 或安全問題 | `code-reviewer` 或 `santa-method` |
| 單純的事實問題 | 直接回答就好 |
| 明顯的執行任務 | 直接做就好 |

## 角色

| 聲音 | 視角 |
| --- | --- |
| Architect | 正確性、可維護性、長期影響 |
| Skeptic | 質疑前提、簡化、打破假設 |
| Pragmatist | 出貨速度、使用者影響、營運現實 |
| Critic | 邊界情況、下行風險、失敗模式 |

三個外部的聲音要當成全新的 subagent 啟動，**只給它們問題和相關 context**，不給完整的對話。這就是防錨定的機制。

## 工作流

### 1. 抽出真正的問題

把決策濃縮成一個明確的 prompt：
- 我們要決定什麼？
- 哪些限制很重要？
- 什麼算成功？

如果問題很模糊，召集 council 之前先問一個釐清問題。

### 2. 只蒐集必要的 context

如果決策跟 codebase 有關：
- 蒐集相關的檔案、片段、issue 內容或指標
- 保持精簡
- 只放做決策需要的 context

如果決策是策略性或通用的：
- 除非 repo 片段會實質改變答案，否則不要放

### 3. 先形成 Architect 的立場

在讀其他聲音之前，先寫下：
- 你一開始的立場
- 支持它的三個最強理由
- 你偏好的路徑裡最主要的風險

先做這件事，這樣最後的綜合才不會只是照抄外部的聲音。

### 4. 平行啟動三個獨立的聲音

每個 subagent 會拿到：
- 決策問題
- 需要的話，精簡的 context
- 嚴格的角色
- 沒有多餘的對話歷史

Prompt 形式：

```text
You are the [ROLE] on a four-voice decision council.

Question:
[decision question]

Context:
[only the relevant snippets or constraints]

Respond with:
1. Position — 1-2 sentences
2. Reasoning — 3 concise bullets
3. Risk — biggest risk in your recommendation
4. Surprise — one thing the other voices may miss

Be direct. No hedging. Keep it under 300 words.
```

角色重點：
- Skeptic：挑戰問題的框架、質疑假設、提出最簡單又可信的替代方案
- Pragmatist：以速度、簡單和真實世界的執行為優先
- Critic：揭露下行風險、邊界情況，以及計畫可能失敗的原因

### 5. 帶著偏見防護欄做綜合

你既是參與者也是綜合者，所以要遵守這些規則：
- 沒說明理由，就不要駁回外部的看法
- 如果外部的聲音改變了你的建議，要明講
- 一定要附上最強的反對意見，即使你不採納
- 如果兩個聲音都跟你一開始的立場相反，要把它當成真正的訊號
- 在給出結論之前，先把各方原始立場攤在眼前

### 6. 提出精簡的結論

用這個輸出格式：

```markdown
## Council: [short decision title]

**Architect:** [1-2 sentence position]
[1 line on why]

**Skeptic:** [1-2 sentence position]
[1 line on why]

**Pragmatist:** [1-2 sentence position]
[1 line on why]

**Critic:** [1-2 sentence position]
[1 line on why]

### Verdict
- **Consensus:** [where they align]
- **Strongest dissent:** [most important disagreement]
- **Premise check:** [did the Skeptic challenge the question itself?]
- **Recommendation:** [the synthesized path]
```

要讓手機螢幕也能一眼掃完。

## 持久化規則

**不要**用這個 skill 把臨時筆記寫到 `~/.claude/notes` 或其他影子路徑。

如果 council 實質改變了建議：
- 用 `knowledge-ops` 把教訓存到對的長期位置
- 或者結果屬於 session 記憶的話，用 `/save-session`
- 或者決策改變了正在進行的執行事實，就直接更新相關的 GitHub / Linear issue

只有決策改變了實際的東西，才把它持久化。

## 多輪追問

預設只跑一輪。

如果使用者想再來一輪：
- 新問題要聚焦
- 只在必要時才帶入前一輪的結論
- 讓 Skeptic 盡可能保持乾淨，才能保住防錨定的價值

## 反模式

- 把 council 用在 code review
- 任務只是實作工作時還用 council
- 把整段對話紀錄餵給 subagent
- 在最後結論裡把分歧藏起來
- 不管重要性，每個決策都存成筆記

## 相關 Skill

- `santa-method`：對抗式驗證
- `knowledge-ops`：正確地持久化決策的差異
- `search-first`：需要的話，在 council 之前先蒐集外部參考資料
- `architecture-decision-records`：決策變成長期的系統政策時，把結果正式化

## 範例

問題：

```text
Should we ship ECC 2.0 as alpha now, or hold until the control-plane UI is more complete?
```

council 可能的樣子：
- Architect 主張結構完整，避免讓介面變得混亂
- Skeptic 質疑 UI 是否真的是卡關的因素
- Pragmatist 問現在能 ship 什麼，又不傷害信任
- Critic 關注客服負擔、期待債與 rollout 的混亂

價值在於讓分歧在做選擇之前看得清楚，不用求大家意見一致。
