---
name: "mfg-oee-analysis"
description: "把整體設備效率（OEE）拆成稼動率、性能率和良率來計算與診斷。使用者需要衡量產線效率、找出設備損失、對製造績效做標竿比較，或要為資本投資提出佐證時使用，就算他們說的是「為什麼我們的產出這麼低」、「機台稼動率報告」、「生產效率」或「我們損失了多少產能」也一樣。"
metadata:
  category: "WP-03 製造業"
  tags: ["manufacturing", "oee", "production-efficiency"]
---

# OEE 分析

## 框架

```
IRON LAW: OEE = Availability × Performance × Quality

OEE is a MULTIPLICATIVE metric. 90% × 90% × 90% = 72.9%, not 90%.
Each factor compounds the loss. World-class OEE is 85%+. Most plants
operate at 60-65%. Knowing the TOTAL is useless — you must decompose
to find which factor is dragging performance down.
```

### 三個因子

| 因子 | 公式 | 衡量的是 | 損失類別 |
|--------|---------|----------|----------------|
| **稼動率（Availability）** | 運轉時間 / 計畫生產時間 | 運轉時間 vs 停機時間 | 設備故障、換線、缺料 |
| **性能率（Performance）** | （理想週期時間 × 總產量）/ 運轉時間 | 實際速度 vs 設計速度 | 小停機、低速運轉、空轉 |
| **良率（Quality）** | 良品數 / 總產量 | 良率、一次通過的品質 | 瑕疵、重工、報廢、開機不良品 |

### 六大損失（對應到 OEE 因子）

| 損失 | OEE 因子 | 例子 |
|------|-----------|---------|
| 1. 設備故障 | 稼動率 | 機台故障、非計畫性維修 |
| 2. 設置與換線 | 稼動率 | 產品換線、換模、清潔 |
| 3. 空轉與小停機 | 性能率 | 感測器被擋住、清除卡料、小幅調整 |
| 4. 速度降低 | 性能率 | 因磨損或物料而低於額定速度運轉 |
| 5. 製程不良 | 良率 | 製程中的不良品、重工 |
| 6. 開機不良 | 良率 | 暖機期間的報廢、首件不合格 |

### 計算範例

```
Planned Production Time: 480 min (8-hour shift)
Downtime (breakdowns + changeover): 60 min
Run Time: 420 min

Ideal Cycle Time: 1 min/unit
Total Units Produced: 380

Good Units: 360
Defective Units: 20

Availability = 420 / 480 = 87.5%
Performance = (1 × 380) / 420 = 90.5%
Quality = 360 / 380 = 94.7%

OEE = 87.5% × 90.5% × 94.7% = 75.0%
```

### 診斷步驟

**Phase 1：計算 OEE**，每條產線／每台機器都算
**Phase 2：找出最弱的因子**（稼動率、性能率或良率）
**Phase 3：對該因子內的損失做柏拉圖分析**（哪一項具體損失最大？）
**Phase 4：對最大的損失做根因分析**（5 Whys、魚骨圖）
**Phase 5：改善**並重新量測

### 標竿

| OEE 水準 | 評等 | 典型情況 |
|-----------|--------|---------|
| > 85% | 世界級 | 頂尖製造商 |
| 60-85% | 一般 | 還有改善空間 |
| 40-60% | 偏低 | 損失很大，需要緊急處理 |
| < 40% | 危急 | 設備或製程根本壞掉 |

## 輸出格式

```markdown
# OEE Report: {Production Line}

## OEE Summary
| Factor | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| Availability | {%} | >90% | 🟢/🟡/🔴 |
| Performance | {%} | >95% | 🟢/🟡/🔴 |
| Quality | {%} | >99% | 🟢/🟡/🔴 |
| **OEE** | **{%}** | **>85%** | 🟢/🟡/🔴 |

## Loss Breakdown
| Loss | Minutes Lost | % of Total Loss | Priority |
|------|-------------|----------------|---------|
| {loss type} | {min} | {%} | 1/2/3 |

## Root Cause (Top Loss)
{5 Whys or fishbone analysis}

## Improvement Plan
| Action | Target Impact | Timeline | Owner |
|--------|-------------|----------|-------|
| {action} | +{X%} OEE | {weeks} | {who} |
```

## 注意事項

- **OEE 是以單一機台為單位，不是整廠**：整廠平均的 OEE 會藏住一個事實：一台是 95%、另一台是 45%，平均出來是 70%。要個別分析。
- **計畫性停機要排除**：OEE 衡量的是相對於「計畫」生產時間的損失。排定的保養、沒有生產的班次、計畫性停工，都要從分母排除。
- **100% OEE 不是目標**：那代表零換線、零瑕疵、100% 的時間都以最高速度運轉。追求 100% 反而可能推高成本（例如永遠不做預防保養）。關鍵產線的目標訂 85% 以上就好。
- **資料蒐集才是真正的挑戰**：人工追蹤 OEE 不準。要投資自動化的資料蒐集（感測器、MES 整合），才能量得可靠。

## 參考資料

- TPM（全面生產保養）方法論請看 `references/tpm.md`
- 自動化的 OEE 資料蒐集請看 `references/oee-automation.md`
