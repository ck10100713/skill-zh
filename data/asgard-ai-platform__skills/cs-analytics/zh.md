---
name: "cs-analytics"
description: "用 CSAT、NPS、CES、首次接觸解決率（First Contact Resolution）和客服工單文字探勘，衡量並最佳化客服績效。當使用者需要評估客服團隊表現、找出最主要的客訴原因、最佳化人力配置，或建立客服儀表板時使用。就算使用者只說「我們客服做得好嗎」、「客戶都在抱怨什麼」、「需要幾個客服」或「做一個客服 dashboard」也要用。"
metadata:
  category: "WP-06 Agent通訊+客服"
  tags: ["customer-service", "analytics", "nps", "csat"]
---

# 客服分析

## 框架

```
IRON LAW: Measure Satisfaction AND Efficiency — Never Just One

High CSAT with terrible resolution time = unsustainable (agents spend
too long per ticket). Fast resolution with low CSAT = cutting corners.
Both dimensions must be tracked and balanced.
```

### 關鍵指標

**滿意度指標**
| 指標 | 衡量什麼 | 如何蒐集 | 基準 |
|--------|-----------------|---------------|-----------|
| **CSAT** | 對特定互動的滿意度 | 互動後問卷（1-5 分） | > 4.0/5 |
| **NPS** | 推薦意願 | 「你有多可能推薦我們？」（0-10） | > 30 |
| **CES** | 解決問題所需的力氣 | 「解決這個問題有多容易？」（1-7） | > 5.0/7 |

**效率指標**
| 指標 | 公式 | 基準 |
|--------|---------|-----------|
| **首次接觸解決率（FCR）** | 首次接觸就解決的數量 / 總接觸數 | > 70% |
| **平均處理時間（AHT）** | 總處理時間 / 總接觸數 | 5-8 分鐘（依產業而異） |
| **平均回應時間** | 從工單建立到第一次回覆的時間 | < SLA 目標 |
| **積壓量（Backlog）** | 未結工單 / 每日處理量 | < 1 天 |
| **升級率** | 升級的工單 / 總工單 | < 20% |
| **重開率** | 重開的工單 / 已解決的工單 | < 5% |

**營運指標**
| 指標 | 公式 | 用途 |
|--------|---------|-----|
| **工單量** | 每日/每週/每月工單數 | 人力規劃 |
| **管道組成** | 各管道占比（email、聊天、電話、LINE） | 資源配置 |
| **尖峰時段** | 各小時的工單量 | 排班 |
| **類別分布** | 各問題類型占比 | 流程改善的優先順序 |

### 分析流程

**1. 主要來電原因分析**
- 把所有工單依原因分類（自動標籤或手動）
- 畫柏拉圖：前 5 大原因通常占 60-80% 的量
- 對每個主要原因：能不能自助解決？能不能自動化？能不能從源頭消除？

**2. 工單文字探勘**
- 從工單描述中擷取高頻關鍵字/片語
- 分群成主題（LDA、BERTopic，或簡單的 TF-IDF）
- 找出新興問題（最近幾週才冒出來的新主題）
- 對客戶訊息做情緒分析

**3. 人力最佳化**
```
Required Agents = Peak Hour Volume × AHT / (60 × Utilization Target)

Example: 50 tickets/hour × 8 min AHT / (60 × 0.75 utilization) = 8.9 → 9 agents
```

要再加上休息、會議和訓練的緩衝（約 15-20%）。

**4. 客服人員績效**
| 指標 | 比較 | 行動 |
|--------|---------|--------|
| 個人 CSAT vs 團隊平均 | 找出需要輔導的人 | 低於平均的人給予訓練 |
| 個人 AHT vs 團隊平均 | 找出效率落差 | 跟著高績效者學習 |
| 各人員的 FCR | 找出知識缺口 | 改善知識庫 |

### VOC（客戶之聲）追蹤

| 訊號 | 來源 | 頻率 |
|--------|--------|-----------|
| 新興客訴 | 工單文字探勘 | 每週 |
| 功能需求 | 標記過的工單 + 問卷 | 每月 |
| 流失訊號 | 「取消」意圖的工單、低 CSAT 模式 | 每週 |
| 讚美模式 | 高 CSAT + 正面評語 | 每月（與團隊分享） |

## 輸出格式

```markdown
# CS Analytics Report: {Period}

## Summary Dashboard
| Metric | Current | Prior | Target | Status |
|--------|---------|-------|--------|--------|
| CSAT | {X}/5 | {X}/5 | >4.0 | 🟢/🟡/🔴 |
| FCR | {%} | {%} | >70% | 🟢/🟡/🔴 |
| Avg Response Time | {hrs} | {hrs} | <{X}hrs | 🟢/🟡/🔴 |
| Ticket Volume | {N} | {N} | — | ↑/↓ |

## Top Contact Reasons (Pareto)
| # | Reason | Volume | % | Self-Servable? |
|---|--------|--------|---|---------------|
| 1 | {reason} | {N} | {%} | Y/N |

## Emerging Issues
{New topics detected in text mining this period}

## Staffing
- Current agents: {N}
- Required (based on volume): {N}
- Gap: {over/under-staffed by N}

## Recommendations
1. {highest-impact improvement}
```

## 常見陷阱

- **CSAT 的回應偏誤**：只有 10-20% 的客戶會回問卷，而且通常是非常滿意或非常不滿的人。沉默的大多數的體驗是未知的。要用行為資料（重複聯絡、流失）補充。
- **NPS 是策略層，CSAT 是戰術層**：NPS 衡量整體品牌忠誠度（長期），CSAT 衡量特定互動的品質（短期）。不要用 NPS 來評估個別客服人員。
- **最佳化 AHT 可能傷害品質**：要求降低 AHT 的壓力可能讓客服趕進度，反而拉低 FCR 和 CSAT。先最佳化 FCR，再看 AHT。
- **工單分類會漂移**：隨著產品演進，分類會過時。每季檢視並更新分類體系。
- **客服資料中相關不等於因果**：「用比較多範本的客服 CSAT 比較高」可能代表範本有幫助，也可能只是資深客服（剛好愛用範本）本來就比較強。

## 參考資料

- NPS 問卷設計，見 `references/nps-methodology.md`
- 客服工單的文字探勘，見 `references/ticket-text-mining.md`
