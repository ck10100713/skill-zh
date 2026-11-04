---
name: "stat-causal-inference"
description: "運用因果推論方法（反事實框架、工具變數、傾向分數配對、雙重差分）從觀察性資料估計因果效果。使用者需要從非實驗資料判斷 X 是否造成了 Y、在沒有隨機試驗的情況下評估方案／政策的影響，或要控制干擾因子時使用，就算他們說的是「這個改變有造成這項改善嗎」、「沒有實驗要怎麼衡量影響」或「這是相關還是因果」也一樣。"
metadata:
  category: "WP-21 設計/資訊/傳播/公衛"
  tags: ["statistics", "causal-inference", "econometrics"]
---

# 因果推論

## 框架

```
IRON LAW: Correlation Is Not Causation — But Causation Is Estimable

Observational data cannot prove causation through correlation alone.
BUT with the right methodology (matching, IV, DID, RDD), we CAN
estimate causal effects from observational data — IF the assumptions
of each method are satisfied and explicitly tested.

The key question is always: "What would have happened WITHOUT the treatment?"
(the counterfactual)
```

### 根本問題

我們觀察到：`Y_i(treated)`，也就是受處理的單位發生了什麼。
我們想知道：`Y_i(treated) - Y_i(untreated)`，也就是因果效果。
我們永遠觀察不到：同一個單位在同一時間的 `Y_i(untreated)`。

**所有因果推論方法估計的都是反事實**，也就是沒有處理的情況下會發生什麼。

### 方法選擇指南

| 方法 | 何時使用 | 關鍵假設 |
|--------|-----------|----------------|
| **RCT** | 你可以做隨機分派 | 隨機分派消除了干擾因子 |
| **傾向分數配對（PSM）** | 處理不是隨機的，但取決於可觀察的變數 | 沒有未觀察到的干擾因子（可觀察變數上的選擇） |
| **工具變數（IV）** | 存在未觀察到的干擾因子，但你有一個工具 | 工具會影響處理，但不會直接影響結果 |
| **雙重差分（DID）** | 政策／事件形成了天然的處理組／對照組 | 平行趨勢：沒有處理的話，兩組的趨勢會相似 |
| **斷點迴歸（RDD）** | 處理是由一個切點決定的 | 剛好在切點上下的觀察值是可比較的 |
| **合成控制（Synthetic Control）** | 一個處理單位、多個對照單位（彙總資料） | 合成出來的加權組合符合處理前的趨勢 |

### 分析步驟

1. **定義因果問題**：處理是什麼？結果是什麼？
2. **找出對效度的威脅**：哪些干擾因子可以解釋這個關聯？
3. **選擇方法**：依資料結構和可用的識別策略
4. **檢查假設**：每種方法都有可檢定和不可檢定的假設
5. **估計效果**：執行分析
6. **敏感度分析**：如果假設被部分違反，結果會改變多少？

## 輸出格式

```markdown
# Causal Analysis: {Treatment} → {Outcome}

## Causal Question
- Treatment: {what intervention/event}
- Outcome: {what we're measuring}
- Counterfactual: {what would have happened without treatment}

## Identification Strategy
- Method: {PSM / IV / DID / RDD / etc.}
- Rationale: {why this method fits}
- Key assumption: {stated explicitly}
- Assumption test: {how we check, or acknowledge if untestable}

## Results
- Estimated causal effect: {magnitude with CI}
- Robustness checks: {alternative specifications}

## Limitations
{What could still invalidate these results}
```

## 注意事項

- **「控制 X」不保證是因果**：在迴歸裡加入控制變數，只能減少「一部分」的干擾，處理不了未觀察到的干擾因子。如果處理不是隨機的，加了控制變數的 OLS 也不是因果。
- **平行趨勢無法檢定**：對 DID 來說，我們可以檢查處理前的平行趨勢，但沒辦法證明它們會持續下去。這是假設，不是事實。
- **弱工具變數會讓 IV 失效**：一個幾乎不影響處理的工具，會產生有偏誤的估計（常常比 OLS 還差）。要用第一階段的 F 統計量（> 10）檢驗工具的強度。
- **外部效度**：在某個情境下估計出來的因果效果，不一定能推廣。對切點附近的用戶估計出來的效果（RDD），不一定適用於整個母體。
- **因果推論需要領域知識**：光靠統計方法，沒辦法判斷什麼是干擾因子、什麼是中介變數、什麼是對撞因子（collider）。要先畫出因果圖（DAG）。

## 參考資料

- 有向無環圖（DAG）請看 `references/causal-dags.md`
- 用 Python/R 實作 DID 請看 `references/did-implementation.md`
