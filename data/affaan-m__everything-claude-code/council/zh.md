---
name: council
description: 為模稜兩可的決策、取捨和 go/no-go 判斷召集四個聲音的委員會。當有多條合理路徑、需要先有結構化的不同意見再做選擇時使用。
metadata:
  origin: ECC
---

# Council

為模稜兩可的決策召集四位顧問：
- 目前 context 裡的 Claude 本人
- 一個 Skeptic（懷疑者）subagent
- 一個 Pragmatist（務實者）subagent
- 一個 Critic（批評者）subagent

這是用在**模糊情境下的決策**，不是 code review、實作規劃或架構設計。

## 何時使用

在這些情況使用 council：
- 一個決策有多條可信的路徑，沒有明顯的贏家
- 需要把取捨明確攤開
- 使用者要第二意見、反對意見或多個觀點
- 對話的錨定效應（anchoring）確實是風險
- go / no-go 的判斷需要對抗式的挑戰

例子：
- monorepo 還是 polyrepo
- 現在就上線，還是等打磨完再上
- feature flag 還是全面 rollout
- 縮小範圍，還是保留策略上的廣度

## 何時不要用

| 不要用 council，改用 | 用這個 |
| --- | --- |
| 驗證輸出對不對 | `santa-method` |
| 把功能拆成實作步驟 | `planner` |
| 設計系統架構 | `architect` |
| 檢查程式碼有沒有 bug 或安全問題 | `code-reviewer` 或 `santa-method` |
| 單純的事實問題 | 直接回答 |
| 很明確的執行任務 | 直接做 |

## 角色

| 聲音 | 視角 |
| --- | --- |
| Architect | 正確性、可維護性、長期影響 |
| Skeptic | 質疑前提、簡化、打破假設 |
| Pragmatist | 出貨速度、對使用者的影響、營運現實 |
| Critic | 邊界情況、下行風險、失敗模式 |

三個外部聲音要用全新的 subagent 啟動，**只給它們問題和相關 context**，不要給完整的對話紀錄。這就是防止錨定的機制。

## 工作流程

### 1. 抽出真正的問題

把決策縮成一個明確的提問：
- 我們要決定什麼？
- 哪些限制條件重要？
- 什麼算成功？

如果問題太模糊，召集 council 之前先問一個釐清問題。

### 2. 只收集必要的 context

如果決策跟 codebase 有關：
- 收集相關的檔案、程式碼片段、issue 內容或指標
- 保持精簡
- 只放做決策需要的 context

如果決策是策略性或通用的：
- 除非 repo 的片段會實質影響答案，否則不要放

### 3. 先形成 Architect 的立場

在看其他聲音之前，先寫下：
- 你一開始的立場
- 支持它的三個最強理由
- 你偏好的路徑裡最主要的風險

要先做這步，這樣最後的綜合才不會只是照抄外部聲音。

### 4. 平行啟動三個獨立的聲音

每個 subagent 會拿到：
- 決策的問題
- 需要的話，附上精簡的 context
- 嚴格的角色設定
- 不要有不必要的對話歷史

prompt 的形狀：

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

各角色的側重：
- Skeptic：挑戰問題的框架、質疑假設、提出最簡單但可信的替代方案
- Pragmatist：以速度、簡單和實際執行為優先
- Critic：點出下行風險、邊界情況，以及計畫可能失敗的原因

### 5. 帶著偏見護欄做綜合

你既是參與者又是綜合者，所以要遵守這些規則：
- 沒說明理由就不要駁回外部的觀點
- 如果外部聲音改變了你的建議，要明說
- 一定要放進最強的反對意見，就算你不採納
- 如果有兩個聲音站在一起反對你一開始的立場，要把它當成真正的訊號
- 在下結論之前，先把各方的原始立場攤出來

### 6. 呈現精簡的結論

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

要讓人在手機螢幕上也能快速掃過。

## 持久化規則

**不要**從這個 skill 把臨時筆記寫到 `~/.claude/notes` 或其他影子路徑。

如果 council 實質改變了建議：
- 用 `knowledge-ops` 把這個教訓存到對的長期位置
- 或者，如果結果屬於 session 記憶，就用 `/save-session`
- 或者，如果決策改變了正在進行的執行事實，就直接更新相關的 GitHub / Linear issue

只有決策真的改變了什麼，才把它持久化。

## 多輪追問

預設只跑一輪。

如果使用者想再跑一輪：
- 新的問題要聚焦
- 只有必要時才附上上一輪的結論
- 盡量讓 Skeptic 保持乾淨，才能保住防錨定的價值

## 反模式

- 把 council 拿來做 code review
- 任務只是實作工作卻用 council
- 把整份對話紀錄餵給 subagent
- 在最後的結論裡把不同意見藏起來
- 不管重要性，每個決策都存成筆記

## 相關 Skills

- `santa-method` - 對抗式驗證
- `knowledge-ops` - 正確地持久化重要的決策變化
- `search-first` - 需要的話，在 council 之前先收集外部參考資料
- `architecture-decision-records` - 當決策變成長期的系統政策時，把結果正式化

## 範例

問題：

```text
Should we ship ECC 2.0 as alpha now, or hold until the control-plane UI is more complete?
```

可能的 council 樣貌：
- Architect 主張結構完整，避免讓使用者面對混亂的介面
- Skeptic 質疑 UI 是不是真的卡關的因素
- Pragmatist 問現在能出什麼，又不會傷害信任
- Critic 關注支援負擔、期待債務和 rollout 的混亂

價值不在於一致同意。價值在於先把分歧攤開看清楚，再做選擇。
