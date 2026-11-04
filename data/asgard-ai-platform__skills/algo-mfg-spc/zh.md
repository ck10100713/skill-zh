---
name: "algo-mfg-spc"
description: "實作統計製程管制（SPC）管制圖，監控生產製程的穩定性。當使用者需要偵測製程偏移、設定管制界限，或區分共同原因與特殊原因變異時使用，即使他們說的是『process monitoring』『control chart』或『is our process in control』。"
metadata:
  category: "WP-48 製造演算法"
  tags: ["manufacturing", "spc", "control-chart", "quality"]
---

# 統計製程管制

## 概述

SPC 用管制圖監控製程隨時間的穩定性。管制上限與下限（UCL/LCL）設在離製程平均 ±3σ 的位置。點落在界限內 = 共同原因變異（穩定）。點落在界限外或呈現特定模式 = 特殊原因變異（要調查）。主要的圖：X-bar/R、X-bar/S、I-MR、p-chart、c-chart。

## 何時使用

**觸發條件：**
- 監控生產製程的穩定性並偵測偏移
- 為品質指標設定以統計為基礎的管制界限
- 區分正常變異和可歸因的原因

**不該使用的情況：**
- 評估製程能力時（用 Cpk）
- 針對已知問題做根因分析時（用魚骨圖 / 5-why）

## 演算法

```
IRON LAW: Control Limits Are NOT Specification Limits
Control limits (±3σ) describe what the process IS doing.
Specification limits describe what the process SHOULD do.
A process can be in statistical control (stable) but still produce
out-of-spec products (incapable). Conversely, a capable process may
be out of control (drifting). Monitor control FIRST, then assess capability.
```

### 階段 1：輸入驗證
收集：25 組以上的量測子群組（X-bar/R 通常每組 5 個）。確認：量測系統足夠（gauge R&R < 10%）、資料依時間順序收集。
**關卡：** 子群組數足夠、資料依時間排序、量測系統已驗證。

### 階段 2：核心演算法
**X-bar/R 管制圖（子群組資料）：**
1. 計算各子群組的平均（X̄）和全距（R）
2. 計算總平均（X̄̄）和平均全距（R̄）
3. UCL_X̄ = X̄̄ + A₂×R̄，LCL_X̄ = X̄̄ - A₂×R̄（A₂ 依子群組大小查統計表）
4. UCL_R = D₄×R̄，LCL_R = D₃×R̄
5. 畫出各點，套用 Western Electric 規則找失控訊號

### 階段 3：驗證
檢查：點超出界限、連串（連續 7 點以上在同一側）、趨勢（連續 7 點以上上升 / 下降）、3 點中有 2 點超過 2σ、5 點中有 4 點超過 1σ。
**關卡：** 管制圖已建立，失控訊號已辨識。

### 階段 4：輸出
回傳管制圖資料，附上訊號與穩定性評估。

## 輸出格式

```json
{
  "chart": {"type": "xbar_r", "center_line": 50.2, "ucl": 52.1, "lcl": 48.3},
  "signals": [{"subgroup": 18, "rule": "point_beyond_ucl", "value": 52.8}],
  "stability": "out_of_control",
  "metadata": {"subgroups": 30, "subgroup_size": 5}
}
```

## 範例

### 輸入輸出範例
**輸入：** 25 個子群組，每組 5 筆量測值，全部落在 ±3σ 內，沒有任何模式
**預期：** 製程在管制中。沒有觸發任何訊號。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 一個點剛好超出 UCL | 有訊號，但可能是誤報 | 即使在管制中，每個點仍有約 0.27% 的機率 |
| 緩慢的上升趨勢 | 觸發趨勢規則 | 製程在漂移，要調查 |
| 所有點都靠近中心 | 可疑，檢查資料 | 可能代表資料被動過手腳或量測有問題 |

## 注意事項

- **合理的子群組劃分**：子群組必須在相似條件下收集（同一個班別、機台、操作員）。子群組劃分不好會墊高組內變異，讓界限太寬。
- **重新計算界限**：不要每新增一次資料就重算界限。用穩定的基準期建立界限，並固定不動，直到已知的製程變更發生。
- **管制圖類型的選擇**：計量資料（量測值）→ X-bar/R 或 I-MR。計數資料（個數 / 比例）→ p-chart、np-chart、c-chart、u-chart。圖選錯 = 界限算錯。
- **常態假設**：X-bar 圖對非常態相當穩健（中央極限定理）。個別值管制圖（I-MR）需要大致常態，要用直方圖檢查。
- **過度調整**：對每個小變動都做反應（tampering）會「增加」變異。只調查特殊原因的訊號，不要去處理共同原因的變異。

## 參考資料

- 管制圖常數表，見 `references/chart-constants.md`
- Western Electric 規則與模式偵測，見 `references/we-rules.md`
