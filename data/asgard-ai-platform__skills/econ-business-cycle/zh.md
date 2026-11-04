---
name: "econ-business-cycle"
description: "分析景氣循環的各個階段（擴張、高峰、收縮、谷底），以及對企業策略和政策回應的意涵。當使用者需要判斷目前所處的經濟階段、預判循環轉折點，或讓企業策略配合總體經濟循環時使用。就算使用者只說「我們是不是要進入衰退了」、「該怎麼為景氣下滑做準備」或「經濟什麼時候會復甦」也要用。"
metadata:
  category: "WP-17 經濟學院"
  tags: ["economics", "business-cycle", "macroeconomics"]
---

# 景氣循環分析

## 概述

景氣循環描述經濟活動反覆的波動：擴張 → 高峰 → 收縮 → 谷底 → 擴張。了解目前所處的階段，能幫企業抓準投資時機、管理庫存，並為下滑或復甦做準備。

## 框架

```
IRON LAW: Cycles Are Inevitable, Timing Is Not Predictable

Business cycles WILL happen — no economy grows forever. But predicting
EXACTLY when a peak or trough occurs is unreliable. Focus on identifying
the CURRENT phase and preparing for the NEXT one, not predicting exact
turning points.
```

### 四個階段

| 階段 | 特徵 | 關鍵指標 |
|-------|----------------|----------------|
| **擴張（Expansion）** | GDP 上升、失業率下降、獲利成長、資產價格上漲 | PMI > 50、殖利率曲線正常、消費者信心上升 |
| **高峰（Peak）** | 經濟處於最大產出、通膨加速、產能受限 | PMI 從高點下滑、通膨高於目標、央行緊縮 |
| **收縮（Contraction）** | GDP 下滑、失業率上升、獲利下降、信用緊縮 | PMI < 50、殖利率曲線可能倒掛、裁員增加 |
| **谷底（Trough）** | 經濟處於最低點、產能過剩、低通膨、悲觀情緒到頂 | PMI 趨穩、央行寬鬆、庫存去化完畢 |

### 階段判斷步驟

1. **檢查領先指標**：PMI、殖利率曲線、股市、消費者信心、建照核發
2. **檢查同時指標**：工業生產、零售銷售、就業
3. **檢查落後指標**：失業率、CPI、企業獲利、貸款違約
4. **找背離**：領先指標已經轉向，但落後指標仍然強勁 = 轉折點

### 各階段的策略因應

| 階段 | 企業策略 | 財務策略 |
|-------|------------------|-------------------|
| **擴張** | 投資產能、招募、推出新產品 | 鎖定固定利率債務、累積準備金 |
| **高峰** | 降低庫存、收緊信用條件、準備成本削減 | 降低槓桿、提高現金部位 |
| **收縮** | 削減成本、保留現金、收購陷入困境的資產 | 延長債務期限、與債權人協商 |
| **谷底** | 逆週期投資、用較低成本延攬人才 | 動用現金準備、買進被低估的資產 |

### 衰退指標

| 指標 | 訊號 |
|-----------|--------|
| 殖利率曲線倒掛 | 10 年期減 2 年期公債利差為負 → 12-18 個月內衰退（歷史上準確率約 80%） |
| Sahm 規則 | 失業率 3 個月平均較 12 個月低點上升 0.5% 以上 |
| 連續 2 季 GDP 為負 | 技術性衰退（落後的確認） |
| 美國諮商會領先指標（Conference Board Leading Index） | 連續 6 個月以上下滑 |

## 輸出格式

```markdown
# Business Cycle Assessment: {Country/Region}

## Current Phase: {Expansion / Peak / Contraction / Trough}

## Evidence
| Category | Indicator | Reading | Signal |
|----------|-----------|---------|--------|
| Leading | PMI | XX | {interpretation} |
| Leading | Yield curve | XX bps | {interpretation} |
| Coincident | Industrial production | X% YoY | {interpretation} |
| Lagging | Unemployment | X% | {interpretation} |

## Phase Progression
{Where we are in the cycle and directional signals}

## Strategic Implications
| Domain | Recommendation |
|--------|---------------|
| Investment | {expand/hold/cut} |
| Hiring | {hire/freeze/reduce} |
| Inventory | {build/maintain/liquidate} |
| Pricing | {raise/hold/discount} |
| Cash management | {deploy/conserve} |
```

## 範例

### 正確的做法
**情境：** 2025 年第 4 季的台灣經濟
- PMI：48.5（低於 50，連續 3 個月下滑）→ **領先指標：收縮訊號**
- 消費者信心：下滑 → **領先指標：支持收縮的判斷**
- GDP：年增 +3.2% → **落後指標：仍為正**
- 失業率：3.6% → **落後指標：仍低**

**診斷**：很可能處於**高峰**或剛過高峰，進入收縮初期。領先指標轉負，但落後指標還沒跟上，這是典型的轉折點 ✓

**策略**：降低庫存、收緊應收帳款、提高現金部位、延後非必要的資本支出。

### 錯誤的做法
- 「GDP 是 3.2%、失業率 3.6%，一切都很好」→ 只看落後指標，卻忽略發出下滑訊號的領先指標。就像只看後照鏡開車。違反 Iron Law：循環不可避免，要為下一個階段做準備。

## 常見陷阱

- **殖利率曲線倒掛**：歷史上最強的衰退預測指標（領先約 12-18 個月），但也出現過誤報。要把它當作眾多訊號之一，不能當成單獨的觸發條件。
- **政策回應會改變循環**：央行介入（QE、降息）可以縮短收縮期或延長擴張期。現代的循環不會完全照教科書的模式走。
- **各產業的循環不同**：科技、房地產、大宗商品和民生必需品，循環的時間和幅度都不一樣。你的產業可能在收縮，整體經濟卻在擴張。
- **全球連動**：台灣的循環深受美國需求、中國經濟和全球半導體循環影響。光看國內指標不夠。
- **逆週期機會**：最佳投資時機往往在收縮期（價格低、有人才可用、競爭對手變弱）。但這需要事先累積現金準備，也需要勇氣。

## 參考資料

- 總體經濟指標的解讀，見 econ-macro-indicators skill
- 台灣景氣循環的歷史資料，見 `references/taiwan-cycles.md`
