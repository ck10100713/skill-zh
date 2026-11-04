---
name: "grad-servqual"
description: "運用 SERVQUAL 模型（Parasuraman、Zeithaml 與 Berry，1988），從五個構面衡量服務品質落差。當使用者需要診斷服務品質的缺口、拿顧客期望對照實際感受做 benchmark、設計服務改善方案，或問「我們的服務哪裡出問題」「顧客期待的和實際體驗的差在哪」「怎麼衡量服務品質」時使用。"
metadata:
  category: "WP-25 行銷理論"
  tags: ["SERVQUAL", "service-quality", "gap-model", "Parasuraman", "customer-expectations", "service-marketing"]
---

# SERVQUAL 模型

## 概述

SERVQUAL 把服務品質定義成顧客在五個構面上「期望」與「感受」之間的落差，這五個構面是：有形性（Tangibles）、可靠性（Reliability）、反應性（Responsiveness）、保證性（Assurance）、同理性（Empathy）。更大的 Gap Model 則指出導致服務品質失敗的五種組織層面落差。

## 何時使用

- 衡量服務品質並做 benchmark
- 找出哪些服務構面需要改善
- 診斷顧客不滿的根本原因
- 比較不同分店、競爭對手或不同時期的服務品質

## 何時不要使用

- 評估產品品質（改用 Garvin 的八個構面）
- 只需要單次交易層級的滿意度（改用 CSAT/NPS）
- 純自助式、沒有任何人員互動的數位產品

## 假設

```
鐵律：服務品質 = 感受 − 期望。兩邊「一定要」各自獨立衡量。
只量滿意度會把兩者混在一起，診斷用的洞察就藏起來了。
```

關鍵假設：
1. 顧客在接觸服務之前就已經形成期望
2. 品質是用比較的方式判斷的（感受 vs 期望）
3. 這五個構面在各服務產業都通用
4. 落差是累加的：多個小落差疊起來，就會變成整體品質不佳

## 方法

### 步驟 1：衡量期望與感受

每個構面用成對的 7 點 Likert 量表施測（共 22 題）：

| 構面 | 重點 | 範例題目 |
|-----------|-------|-------------|
| **有形性** | 實體設施、設備、外觀 | 「設備看起來很新穎」 |
| **可靠性** | 可靠地兌現承諾的服務 | 「在承諾的時間內提供服務」 |
| **反應性** | 願意幫忙、服務迅速 | 「員工提供迅速的服務」 |
| **保證性** | 專業知識、禮貌、信任 | 「員工讓人有信心」 |
| **同理性** | 關懷、個別化的關注 | 「了解個別需求」 |

### 步驟 2：計算落差分數

落差分數 = 感受分數 − 期望分數（負值代表未達期望）

### 步驟 3：診斷組織落差

| 落差 | 說明 | 根本原因 |
|-----|------------|------------|
| Gap 1 | 管理階層的認知 vs 顧客期望 | 市場研究做得不好 |
| Gap 2 | 服務品質規格 vs 管理階層的認知 | 標準不足 |
| Gap 3 | 服務傳遞 vs 規格 | 執行不佳 |
| Gap 4 | 對外溝通 vs 實際傳遞 | 過度承諾 |
| Gap 5 | 顧客感受 vs 期望 | Gap 1-4 的累積結果 |

### 步驟 4：排優先順序並介入

依照落差大小乘上重要性權重，替各構面排序。先處理負值最大的落差。

## 輸出格式

```markdown
## SERVQUAL 分析：[服務情境]

### 各構面落差分數
| 構面 | 期望 (E) | 感受 (P) | 落差 (P-E) | 優先順序 |
|-----------|----------------|-----------------|-----------|----------|
| 有形性 | | | | |
| 可靠性 | | | | |
| 反應性 | | | | |
| 保證性 | | | | |
| 同理性 | | | | |

### 組織落差診斷
- Gap 1（認知）：...
- Gap 2（標準）：...
- Gap 3（傳遞）：...
- Gap 4（溝通）：...

### 改善建議
1. [構面]：[具體行動]
2. ...
```

## 常見陷阱

- 期望分數常常集中在高分（天花板效應），壓縮了診斷用的變異
- 這 22 題的量表常被改編，任何修改都要記錄下來，才能談效度
- 各產業中，可靠性和反應性通常主導重要性權重
- 在「期望的服務」與「可接受的服務」之間存在容忍區間，兩者都量，洞察才更完整
- SERVPERF（Cronin & Taylor, 1992）主張只量感受就夠了，要知道這場爭論
- 文化規範會改變構面權重：集體主義文化會把同理性看得更重

## 參考資料

- Parasuraman, A., Zeithaml, V. A., & Berry, L. L. (1988). SERVQUAL: A multiple-item scale for measuring consumer perceptions of service quality. *Journal of Retailing*, 64(1), 12-40.
- Parasuraman, A., Zeithaml, V. A., & Berry, L. L. (1985). A conceptual model of service quality and its implications for future research. *Journal of Marketing*, 49(4), 41-50.
- Cronin, J. J., & Taylor, S. A. (1992). Measuring service quality: A reexamination and extension. *Journal of Marketing*, 56(3), 55-68.
