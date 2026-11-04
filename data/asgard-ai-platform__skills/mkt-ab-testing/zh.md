---
name: "mkt-ab-testing"
description: "為登陸頁、電子郵件活動、廣告素材和定價設計並執行行銷 A/B 測試，附上正確的測試設計與結果分析。使用者需要測試行銷版本的差異、透過實驗提升轉換率，或要在兩種活動做法之間做決定時使用，就算他們說的是「哪個版本表現比較好」、「測試這個登陸頁」、「A/B 測試我們的電子郵件主旨」或「我們該不該改 CTA」也一樣。"
metadata:
  category: "WP-09 數位行銷"
  tags: ["digital-marketing", "ab-testing", "conversion", "experimentation"]
---

# 行銷 A/B 測試

## 框架

```
IRON LAW: One Variable at a Time

If you change the headline AND the image AND the CTA simultaneously,
you cannot know which change caused the result. Test ONE variable per
experiment. If you need to test multiple changes, use sequential tests
or multivariate testing (MVT) with sufficient traffic.
```

### 該測什麼（依影響程度）

| 元素 | 預期提升 | 需要的流量 | 優先順序 |
|---------|-------------|---------------|---------|
| **優惠／定價** | 10-50% | 中 | 最高 |
| **標題／主旨** | 5-30% | 低 | 高 |
| **CTA（文字、顏色、位置）** | 5-20% | 低 | 高 |
| **頁面版面** | 5-15% | 中 | 中 |
| **圖片／影片** | 3-15% | 中 | 中 |
| **表單欄位** | 5-25%（減少欄位 = 轉換率更高） | 低 | 中 |
| **社會證明的位置** | 3-10% | 中 | 較低 |

### 測試設計

1. **假設**：「把 [變數] 從 [A] 改成 [B]，會讓 [指標] 提升 [X%]，因為 [理由]」
2. **主要指標**：「一個」決定勝負的指標（轉換率、每位訪客營收、註冊率）
3. **護欄指標**：絕對不能變差的指標（跳出率、頁面載入時間、每位用戶營收）
4. **流量分配**：對照組與變體組 50/50（標準做法）
5. **樣本數**：開始前先算好（公式請看 stat-ab-testing）
6. **期間**：至少 1-2 個完整的工作週（涵蓋星期幾的效應）

### 常見的行銷測試

| 測試 | 對照組（A） | 變體組（B） | 指標 |
|------|-----------|------------|--------|
| 電子郵件主旨 | "Your weekly update" | "3 trends you missed this week" | 開信率 |
| 登陸頁 CTA | "Sign Up" | "Start Free Trial" | 點擊率 |
| 定價頁 | 顯示 3 個方案 | 顯示 2 個方案 + 「最受歡迎」徽章 | 轉換率 |
| 廣告素材 | 產品照 | 帶有產品的生活風格照 | CTR → 轉換 |
| 表單長度 | 8 個欄位 | 4 個欄位 | 表單完成率 |

### 分析與決策

| 結果 | 決定 | 行動 |
|--------|---------|--------|
| B 勝出、p < 0.05、提升幅度有意義 | 上線 B | 部署變體，開始下一個測試 |
| B 勝出、p < 0.05、但提升很小（<1%） | 不上線 | 提升幅度不值得承擔改動的風險 |
| 沒有顯著差異 | 保留 A | A 是已知的基準；去測別的東西 |
| B 在主要指標勝出，但護欄指標輸了 | 調查 | 可能需要重新設計變體 |

## 輸出格式

```markdown
# A/B Test Plan: {Test Name}

## Hypothesis
Changing {variable} from {A} to {B} will increase {metric} by {X%} because {reasoning}.

## Design
- Primary metric: {metric}
- Guardrail: {metric(s)}
- Split: 50/50
- Sample size: {N per variant}
- Duration: {days/weeks}

## Results
| Metric | Control | Variant | Diff | CI (95%) | Significant? |
|--------|---------|---------|------|----------|-------------|
| {primary} | {value} | {value} | {±%} | [{lower}, {upper}] | Y/N |

## Decision
{Ship / Don't ship / Extend} — {rationale}
```

## 注意事項

- **不要因為「看起來不錯」就提早停止**：偷看結果、一看到顯著就停，會讓偽陽性率膨脹到 30% 以上。要跑到計畫的樣本數。
- **星期幾的效應**：週一的訪客和週六的訪客行為不同。測試一定要跑至少 1-2 個完整的週。
- **新奇效應**：新設計可能因為好奇而暫時提升。要等 2 週以上，看效果是否持續。
- **贏家的詛咒**：因為統計雜訊，測試估計出來的提升幅度常常比真實的提升大。部署後的實際影響要預期會比較小。
- **不要什麼都測，要測重要的**：花力氣跑 20 個按鈕顏色的小測試，卻忽略定價頁，是把精力放錯地方。先測影響大的元素。

## 腳本

| 腳本 | 說明 | 用法 |
|--------|-------------|-------|
| `scripts/ab_test.py` | 雙比例 z 檢定，附效果量與樣本數規劃 | `python scripts/ab_test.py --help` |

執行 `python scripts/ab_test.py --verify` 可以跑內建的健全性測試。

## 參考資料

- 統計方法論（樣本數、p 值）請看 stat-ab-testing skill
- 多變量測試設計請看 `references/mvt-design.md`
