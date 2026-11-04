---
name: "biz-value-chain"
description: "用 Porter 價值鏈分析找出組織各項活動中的競爭優勢來源。當使用者需要找出營運中價值在哪裡創造或流失、依活動分析成本結構、最佳化內部流程，或找出適合外包的活動時使用。就算使用者只說「我們到底在哪裡賺錢」或「哪些活動該留在內部做」也要用。"
metadata:
  category: "WP-13 商學院—策略"
  tags: ["business-strategy", "value-chain", "operations"]
---

# 價值鏈分析

## 概述

價值鏈分析把組織拆成一個個具策略意義的活動，藉此了解競爭優勢從哪裡來。每個活動不是增加價值（客戶願意付的價格），就是增加成本。創造的總價值和總成本之間的差距就是利潤。

## 何時使用

**觸發條件：**
- 使用者想了解哪些活動驅動了競爭優勢
- 使用者在分析成本結構，想找出可以省錢的地方
- 使用者在決定哪些事情自己做、哪些外包
- 使用者問「我們在哪裡創造價值？」或「為什麼我們的毛利這麼低？」

**何時不要用：**
- 要做產業層級分析 → 用 Porter 五力
- 要做產品組合決策 → 用 BCG 矩陣
- 要掃描總體環境 → 用 PESTEL

## 框架

```
IRON LAW: Primary + Support Activities Are a Complete Set

Analyze ALL nine categories. Skipping support activities (like HR or
technology development) misses critical advantage sources. Amazon's
competitive advantage comes more from Technology Development (support)
than from any single primary activity.
```

### 步驟 1：盤點主要活動

主要活動直接為客戶創造並交付價值：

1. **進貨物流（Inbound Logistics）**：接收、儲存、分配投入的物料（倉庫、庫存、供應商排程）
2. **營運（Operations）**：把投入轉成最終產品（製造、組裝、包裝、測試）
3. **出貨物流（Outbound Logistics）**：蒐集、儲存、配送產品給買家（配送、訂單履行）
4. **行銷與銷售（Marketing & Sales）**：讓買家知道產品並促成購買（廣告、定價、通路管理）
5. **服務（Service）**：售後維持並提升產品價值（安裝、維修、訓練、支援）

### 步驟 2：盤點支援活動

支援活動讓主要活動得以運作並變得更好：

6. **企業基礎架構（Firm Infrastructure）**：一般管理、規劃、財務、會計、法務、政府事務
7. **人力資源管理（Human Resource Management）**：招募、聘僱、訓練、薪酬、文化
8. **技術發展（Technology Development）**：研發、產品設計、流程改善、IT 系統
9. **採購（Procurement）**：採購投入物料、與供應商談判、管理廠商關係

### 步驟 3：評估每個活動

這 9 個活動都要評估：
- **價值貢獻**：這個活動對客戶願意付的價格貢獻多少？
- **成本**：這個活動占總成本的百分之幾？
- **競爭比較**：這個活動做得比競爭對手好、一樣還是差？
- **連結**：這個活動是否關鍵地支撐其他活動，或依賴其他活動？

### 步驟 4：找出優勢來源

競爭優勢來自：
- **成本優勢**：做活動的成本比競爭對手低
- **差異化優勢**：做活動的方式能提高買家願意付的價格
- **連結優勢**：活動之間的協調比競爭對手好（例如營運和出貨物流緊密整合）

### 步驟 5：擬定建議

針對每個活動：
- 如果是優勢來源，就**強化**
- 如果是有改善空間的成本中心，就**最佳化**
- 如果競爭對手或專業廠商做得更好，而且它不是優勢來源，就**外包**
- 如果是可能替主要活動解鎖優勢的支援活動，就**投資**

## 輸出格式

```markdown
# Value Chain Analysis: {Company}

## Primary Activities

| Activity | Key Processes | Value Contribution | Cost % | vs Competitors |
|----------|-------------|-------------------|--------|----------------|
| Inbound Logistics | {processes} | High/Med/Low | X% | Better/Same/Worse |
| Operations | ... | ... | ... | ... |
| Outbound Logistics | ... | ... | ... | ... |
| Marketing & Sales | ... | ... | ... | ... |
| Service | ... | ... | ... | ... |

## Support Activities

| Activity | Key Processes | Value Contribution | Cost % | vs Competitors |
|----------|-------------|-------------------|--------|----------------|
| Infrastructure | {processes} | High/Med/Low | X% | Better/Same/Worse |
| HR Management | ... | ... | ... | ... |
| Technology Dev | ... | ... | ... | ... |
| Procurement | ... | ... | ... | ... |

## Advantage Sources
- **Cost advantage in**: {activities}
- **Differentiation advantage in**: {activities}
- **Key linkages**: {activity A ↔ activity B}

## Recommendations
1. **Strengthen**: {activity} — {why and how}
2. **Optimize**: {activity} — {specific improvement}
3. **Outsource**: {activity} — {rationale}
```

## 範例

### 正確的做法

**情境：** 一個台灣 DTC（直接面對消費者）保養品牌的價值鏈

| 活動 | 有優勢嗎？ | 分析 |
|----------|-----------|----------|
| 進貨物流 | 一般 | 標準的原料採購，向 OEM 供應商進貨 |
| 營運 | **差異化** ✓ | 與皮膚科醫師共同開發的專屬配方製程 |
| 出貨物流 | 一般 | 標準物流，走黑貓/宅配通 |
| 行銷與銷售 | **差異化** ✓ | 與 KOL 關係緊密，社群上有社群驅動的內容 |
| 服務 | 一般 | 標準客服 |
| 技術發展 | **差異化** ✓ | 用客戶回饋循環做資料驅動的產品開發 |
| 採購 | 成本優勢 ✓ | 與本地原料供應商簽長期合約，拿到量大折扣 |

**關鍵連結**：技術發展 ↔ 行銷與銷售，來自社群的客戶資料直接餵給產品研發。

### 錯誤的做法

**哪裡做錯了：**
- 只分析了營運和行銷，跳過其他 7 個活動 → 漏掉採購其實是關鍵的成本優勢來源。違反 Iron Law：必須是完整的一套。
- 把「品牌聲譽」列為主要活動 → 品牌聲譽是結果，不是活動。活動是動詞（採購、製造、配送），不是名詞。

## 常見陷阱

- **活動是動詞，不是資產**：「強大的品牌」不是活動。「投資 KOL 合作來建立品牌知名度」才是一個行銷與銷售活動。
- **支援活動常常是隱藏的優勢**：很多公司真正的競爭力在技術發展、人資或採購，不在主要活動。不要把支援活動當成純粹的管銷。
- **魔法發生在連結上**：活動之間的連結往往比單一活動更重要。ZARA 的優勢是設計（技術發展）→ 製造（營運）→ 配送到門市（出貨物流）之間的連結，不是任何單一活動。
- **服務業要調整**：對服務型企業來說，「營運」就是服務交付，「出貨物流」可能不適用。要依商業模式調整框架。

## 參考資料

- 與其他策略框架的比較，見 `references/framework-comparison.md`
