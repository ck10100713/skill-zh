---
name: "stat-ab-testing"
description: "用正確的統計方法設計並分析 A/B 測試，包含樣本數計算、隨機分派、頻率學派與貝氏方法，以及序貫檢定。使用者需要建立實驗、計算所需樣本數、解讀測試結果，或在不同測試方法之間做選擇時使用，就算他們說的是「我們該不該 A/B 測試這個」、「我們需要多少用戶」、「這個測試結果有定論嗎」或「我們可以提早停止測試嗎」也一樣。"
metadata:
  category: "WP-21 設計/資訊/傳播/公衛"
  tags: ["statistics", "ab-testing", "experimentation"]
---

# A/B 測試統計

## 框架

```
IRON LAW: Calculate Sample Size BEFORE Running the Test

Running a test without knowing the required sample size leads to two
failures: stopping too early (false positives) or running too long (waste).

Required inputs: baseline conversion rate, minimum detectable effect (MDE),
significance level (α), power (1-β). Calculate BEFORE starting.
```

### 樣本數公式（比例）

```
n per group ≈ (Z_α/2 + Z_β)² × [p₁(1-p₁) + p₂(1-p₂)] / (p₁ - p₂)²
```

速查表（α=0.05，檢定力=0.8）：
| 基準率 | MDE（相對值） | 每組 N |
|--------------|----------------|-------------|
| 5% | 10%（→5.5%） | ~58,000 |
| 5% | 20%（→6.0%） | ~15,000 |
| 10% | 10%（→11%） | ~15,000 |
| 10% | 20%（→12%） | ~4,000 |

### 測試方法

| 方法 | 運作方式 | 最適合 |
|----------|-------------|-----------|
| **頻率學派（固定期間）** | 設定樣本數，跑到完成，然後分析 | 標準做法，廣為人理解 |
| **貝氏** | 用資料更新信念，計算改善的機率 | 想要機率式的陳述（「B 有 90% 的機會比較好」） |
| **序貫檢定** | 以調整過的門檻在間隔期檢查結果 | 需要在有明顯贏家時提早停止，或限制下行風險 |

### 實驗設計檢查表

1. **假設**：你預期會發生什麼？為什麼？
2. **主要指標**：「一個」關鍵指標（轉換、營收、留存）
3. **護欄指標**：絕對不能變差的指標（頁面載入時間、錯誤率）
4. **隨機化單位**：使用者、session，還是裝置？
5. **樣本數**：從基準、MDE、α、檢定力算出來
6. **期間**：要涵蓋每週的循環（至少 1-2 個完整的週）
7. **停止規則**：事先定義好，不要偷看之後在沒有校正的情況下提早停止

### 分析步驟

1. 檢查隨機化的平衡（各組在處理前的指標上可以比較嗎？）
2. 計算觀察到的差異和信賴區間
3. 執行顯著性檢定（比例用 z 檢定，連續變數用 t 檢定）
4. 檢查護欄指標
5. 要同時考慮實務上的顯著性來詮釋

## 輸出格式

```markdown
# A/B Test Design: {Experiment Name}

## Hypothesis
- H₀: {no difference}
- H₁: {expected improvement}
- Primary metric: {metric}
- MDE: {X% relative}

## Sample Size
- Baseline rate: {X%}
- Required N per group: {N}
- Estimated duration: {days/weeks}

## Results (post-test)
| Metric | Control | Treatment | Diff | CI (95%) | p-value |
|--------|---------|-----------|------|----------|---------|
| {primary} | X% | X% | +X% | [X, X] | {value} |

## Decision
{Ship / Don't ship / Extend test} — {rationale}
```

## 注意事項

- **偷看會讓偽陽性膨脹**：每天檢查結果，一看到 p < 0.05 就停，可能產生 30% 以上的偽陽性率。如果需要偷看，就用序貫檢定的方法。
- **新奇效應**：新功能可能顯示出提升，但隨著使用者習慣之後就消退。測試要跑夠久（2 週以上）才會穩定。
- **辛普森悖論**：整體結果為正，可能在每個子群組裡都是負的（反之亦然）。要依關鍵維度做分群。
- **網路效應／干擾**：如果處理組的使用者和對照組的使用者互動（社交功能、市集），獨立性就被破壞了。要用整群隨機化（cluster randomization）。
- **統計顯著性門檻是任意的**：α=0.05 是慣例，不是真理。高風險的決策（定價、大幅度的 UX 變更），可以考慮 α=0.01。

## 參考資料

- 貝氏 A/B 測試方法論請看 `references/bayesian-ab.md`
- 多臂吃角子老虎機做法請看 `references/bandits.md`
