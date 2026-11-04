---
name: "mfg-predictive-maintenance"
description: "用感測器資料、剩餘使用壽命（RUL）的機器學習模型和 P-F 曲線框架，設計預測性保養策略。使用者需要減少非計畫性停機、從事後維修轉向預測性保養、評估感測器／IoT 投資，或估算設備故障機率時使用，就算他們說的是「機器一直壞」、「這台設備什麼時候會壞」、「我們該不該投資 IoT 感測器」或「減少非計畫性停機」也一樣。"
metadata:
  category: "WP-03 製造業"
  tags: ["manufacturing", "predictive-maintenance", "iot", "reliability"]
---

# 預測性保養

## 框架

```
IRON LAW: Predictive > Preventive > Reactive (but each has its place)

Reactive (fix after failure): cheapest per-event, most expensive in downtime
Preventive (fix on schedule): prevents some failures, causes unnecessary maintenance
Predictive (fix based on condition): lowest total cost, requires sensor investment

Not ALL equipment justifies predictive maintenance. Apply to equipment where
unplanned downtime cost >> sensor investment cost.
```

### 保養策略比較

| 策略 | 何時保養 | 優點 | 缺點 | 最適合 |
|----------|-----------------|-----------|-------------|----------|
| **事後維修（Reactive）** | 故障之後 | 前期成本為零 | 停機時間最長、有安全風險 | 非關鍵、換起來便宜的設備 |
| **預防性保養（Preventive）** | 依排程（時間／週期數） | 可預期、簡單 | 過度保養（把還能用的零件換掉） | 磨損模式已知的設備 |
| **預測性保養（Predictive）** | 依狀態資料 | 同時把停機時間和保養成本降到最低 | 需要感測器、資料基礎建設、模型 | 關鍵、昂貴、故障會連鎖影響的設備 |

### P-F 曲線（潛在故障 → 功能故障）

```
Condition
  │
  │  ●─── P (Potential failure detected by sensor)
  │     ╲
  │      ╲  ← P-F Interval (time to act)
  │       ╲
  │        ● F (Functional failure — equipment stops)
  │
  └──────────────────── Time

The P-F interval is your window of opportunity. Detect at P, schedule
repair before F. The longer the P-F interval, the more planning time.
```

### 感測器資料類型

| 資料類型 | 能偵測什麼 | 設備 |
|-----------|----------------|-----------|
| **振動** | 軸承磨損、不平衡、不對中 | 旋轉機械（馬達、幫浦、渦輪） |
| **溫度** | 過熱、摩擦、電氣故障 | 馬達、變壓器、軸承 |
| **電流／功率** | 負載變化、電氣劣化 | 電動馬達、驅動器 |
| **聲學** | 洩漏、空蝕、微裂縫 | 壓力系統、管線、閥門 |
| **油品分析** | 磨耗顆粒、污染 | 齒輪箱、液壓系統 |

### 預測 RUL（剩餘使用壽命）的 ML 模型

| 做法 | 方法 | 需要的資料 |
|----------|--------|-------------|
| **統計式** | Weibull 分布、指數劣化 | 歷史故障時間 |
| **傳統 ML** | 對感測器特徵用 Random Forest、Gradient Boosting | 有標記的運轉到故障（run-to-failure）資料集 |
| **深度學習** | 對原始感測器時間序列用 LSTM、1D-CNN | 大量的感測器資料 |
| **異常偵測** | Isolation Forest、Autoencoder | 只需要正常運轉的資料（不需要故障標記） |

### 實施步驟

**Phase 1：選擇設備**（關鍵性分析）
- 哪些設備的停機成本最高？
- 哪些設備的故障會連鎖影響其他設備？
- 排優先順序：高成本 × 高頻率

**Phase 2：安裝感測器**
- 讓感測器類型對應到故障模式（見上表）
- 建立資料管線：感測器 → 邊緣／雲端 → 儲存

**Phase 3：建立基準線**
- 蒐集 3-6 個月的正常運轉資料
- 建立「健康」的模式

**Phase 4：開發模型**
- 從簡單的開始：以門檻值為基礎的警報（振動 > X = 警告）
- 資料累積之後，再升級到 ML 模型
- 如果故障案例很少或沒有，就用異常偵測

**Phase 5：落地營運**
- 把警報整合進保養工作流程（CMMS）
- 為每個警報等級定義處理程序
- 衡量：非計畫性停機的減少、保養成本的節省

### ROI 計算

```
Annual Savings = (Unplanned downtime hours reduced × Downtime cost/hour)
               + (Preventive maintenance events avoided × Cost per event)
               - (Sensor + infrastructure + model development cost)
```

## 輸出格式

```markdown
# Predictive Maintenance Plan: {Equipment/Line}

## Equipment Criticality
| Equipment | Downtime Cost/hr | Failure Frequency | Cascading? | Priority |
|-----------|-----------------|-------------------|-----------|---------|
| {name} | ${X} | {X/year} | Y/N | H/M/L |

## Sensor Plan
| Equipment | Failure Mode | Sensor Type | P-F Interval |
|-----------|-------------|-------------|-------------|
| {name} | {mode} | {sensor} | {est. hours/days} |

## Projected ROI
| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Unplanned downtime | {hrs/year} | {hrs/year} | ${X}/year |
| Maintenance cost | ${X}/year | ${X}/year | ${X}/year |
| Sensor investment | — | ${X} one-time | Payback: {months} |
```

## 注意事項

- **從振動監測開始**：它是最成熟、最被充分理解的預測技術。旋轉設備 80% 的故障，單靠振動分析就能預測。
- **資料品質 > 模型複雜度**：在乾淨的感測器資料上設一個簡單的門檻警報，會比在雜訊多、不完整的資料上跑精密的 ML 模型表現更好。先把資料品質修好。
- **誤報會殺死採用率**：如果模型太常狼來了，保養團隊就會直接無視。調整成高精確率（誤報少），就算早期漏掉一些偵測也要這樣。
- **文化改變比技術難**：要從「壞了才修」的文化轉型，需要管理階層支持，也要訓練保養團隊。光靠技術改變不了行為。

## 參考資料

- 依設備類型的感測器選擇指南請看 `references/sensor-guide.md`
- 以 LSTM 為基礎的 RUL 模型教學請看 `references/rul-tutorial.md`
