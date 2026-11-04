---
name: "mfg-supplier-scorecard"
description: "用涵蓋品質、交期、價格、服務四個面向的加權計分卡來評估與管理供應商。使用者需要評估供應商績效、比較廠商來做選擇、設計供應商評等制度，或管理供應商發展時使用，就算他們說的是「我們該選哪家供應商」、「幫我們的廠商評分」、「這家供應商一直延遲交貨」或「建立廠商評鑑制度」也一樣。"
metadata:
  category: "WP-03 製造業"
  tags: ["manufacturing", "procurement", "supplier-management"]
---

# 供應商計分卡

## 框架

```
IRON LAW: Evaluate on QCDS (Quality, Cost, Delivery, Service) — Not Just Price

The cheapest supplier who delivers defective parts late with no support
is the most expensive supplier. Total Cost of Ownership (TCO) includes:
purchase price + incoming inspection + rework + downtime from defects +
expediting fees + management overhead.

NEVER select suppliers on price alone.
```

### 四個評估面向（QCDS）

| 面向 | 權重（典型） | KPI |
|-----------|-----------------|------|
| **品質（Quality）** | 30-40% | 不良率（PPM）、進料檢驗通過率、認證（ISO 9001）、矯正措施的回應速度 |
| **成本（Cost）** | 20-30% | 單價、總持有成本、價格穩定性、付款條件 |
| **交期（Delivery）** | 20-30% | 準時交貨率、前置時間、前置時間的變異、對急單的彈性 |
| **服務（Service）** | 10-20% | 回應速度、溝通品質、技術支援、願意合作做改善的意願 |

### 評分方法

1. **為每個面向定義 KPI**（每個面向 2-3 個）
2. **設定權重**（加起來必須是 100%）
3. **為每個 KPI 評分**：1-5 分，附明確的定義：
   - 5 = 優異（供應商中前 10%）
   - 4 = 良好（持續符合所有要求）
   - 3 = 可接受（符合大部分要求）
   - 2 = 低於預期（經常出問題）
   - 1 = 不可接受（有嚴重問題）
4. **計算加權總分**
5. **分級**：A（>4.0）、B（3.0-4.0）、C（2.0-3.0）、D（<2.0）

### 供應商分級與對應行動

| 等級 | 分數 | 策略 |
|-------|-------|---------|
| **A** | >4.0 | 優先供應商，增加業務量，共同開發 |
| **B** | 3.0-4.0 | 核可供應商，維持，針對性改善 |
| **C** | 2.0-3.0 | 有條件使用，90 天內要提出改善計畫 |
| **D** | <2.0 | 逐步淘汰，立刻開始找替代供應來源 |

### 風險評估

| 風險因子 | 問題 | 緩解措施 |
|-------------|---------|-----------|
| **單一來源** | 這家供應商是某個關鍵零組件的唯一來源嗎？ | 開發備援供應商 |
| **地理** | 供應商所在地區容易發生中斷嗎？ | 跨區域雙供應來源 |
| **財務** | 供應商財務穩定嗎？ | 監控信用，要求財務揭露 |
| **產能** | 供應商能跟著我們的成長擴大規模嗎？ | 產能承諾協議 |
| **智慧財產** | 供應商能接觸到我們的專有設計嗎？ | 合約中加入 NDA + 智財條款 |

### 供應商發展計畫（SDP）

針對值得留下的 C 級供應商：
1. **差距分析**：他們具體是哪裡不足？
2. **改善計畫**：具體、可衡量、有期限的目標
3. **支援**：提供訓練、分享最佳實務，必要時共同投資
4. **檢討**：每月檢查進度，90 天做正式的重新評估
5. **決定**：進步到 B 以上 → 繼續合作。仍是 C 或更差 → 淘汰。

## 輸出格式

```markdown
# Supplier Scorecard: {Supplier Name}

## Overall Score: {X.X} / 5.0 — Grade: {A/B/C/D}

## Detailed Scores
| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|---------|
| Quality | {%} | {X.X} | {X.XX} |
| Cost | {%} | {X.X} | {X.XX} |
| Delivery | {%} | {X.X} | {X.XX} |
| Service | {%} | {X.X} | {X.XX} |
| **Total** | **100%** | — | **{X.XX}** |

## KPI Details
| KPI | Target | Actual | Score |
|-----|--------|--------|-------|
| Defect rate | <500 PPM | {X} PPM | {1-5} |
| On-time delivery | >95% | {%} | {1-5} |
| ... | ... | ... | ... |

## Risk Assessment
| Risk | Level | Mitigation |
|------|-------|-----------|
| {risk} | H/M/L | {action} |

## Action Plan
{Based on grade: preferred/maintain/improve/phase out}
```

## 注意事項

- **權重應該反映「你」的優先順序**：醫療器材公司的品質權重應該 50% 以上。大宗物料的採購方可能把成本權重放 40%。不要用通用的權重。
- **分數膨脹**：採購團隊可能為了避免跟供應商進行困難的對話而灌高分數。每個分數都要求有資料佐證。
- **檢討頻率**：A 級每季、B/C 級每月、D 級每週，直到問題解決。
- **供應商關係很重要**：計分卡是改善的工具，不是懲罰。要把結果透明地分享給供應商，最好的供應商會想要回饋。
- **TCO 包含隱藏成本**：別忘了：進料檢驗的人力、為了應付不穩的交貨而備安全庫存所佔的倉儲空間、處理品質問題的工程時間、海外供應商的報關／物流。

## 參考資料

- TCO 計算方法請看 `references/tco-calculation.md`
- 供應商稽核檢查表請看 `references/supplier-audit.md`
