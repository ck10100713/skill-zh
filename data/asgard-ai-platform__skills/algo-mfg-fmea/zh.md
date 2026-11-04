---
name: "algo-mfg-fmea"
description: "進行 FMEA，有系統地找出、排定優先順序並降低潛在的失效模式。當使用者需要評估產品或製程風險、排定矯正措施的優先順序，或建立風險登記表時使用，即使他們說的是『failure mode analysis』『risk assessment』『what could go wrong』或『RPN calculation』。"
metadata:
  category: "WP-48 製造演算法"
  tags: ["manufacturing", "fmea", "risk-analysis", "quality"]
---

# FMEA（Failure Mode and Effects Analysis，失效模式與效應分析）

## 概述

FMEA 有系統地找出潛在的失效模式、它們的效應、原因和現有的管制措施。每個失效以嚴重度（S）、發生度（O）、偵測度（D）各用 1-10 分評分。RPN = S × O × D 用來排定先處理哪些風險。AIAG-VDA FMEA（2019）用 Action Priority（AP）矩陣取代 RPN。

## 何時使用

**觸發條件：**
- 設計新產品 / 製程，並主動辨識風險
- 有系統地評估現有的失效模式，以排定優先順序
- 符合汽車（IATF 16949）或醫療器材（ISO 13485）的品質要求

**不該使用的情況：**
- 針對已知問題做根因分析時（用魚骨圖 / 5-why）
- 對不良資料做統計分析時（用 SPC 或柏拉圖）

## 演算法

```
IRON LAW: Severity Can NEVER Be Reduced by Design Changes
Severity is determined by the EFFECT on the customer. A brake failure
is always severity 10, regardless of how unlikely or detectable it is.
FMEA reduces risk by: lowering Occurrence (better design/process) or
improving Detection (better testing/inspection). NEVER inflate
Detection scores to lower RPN artificially.
```

### 階段 1：輸入驗證
定義範圍：設計 FMEA（DFMEA）或製程 FMEA（PFMEA）。組成跨部門團隊。準備：製程流程圖或系統方塊圖。
**關卡：** 範圍已定義、團隊已組成、有參考用的圖。

### 階段 2：核心演算法
1. 針對每個功能 / 製程步驟，列出所有潛在的失效模式
2. 每個失效模式都要找出：對客戶的效應、根本原因、現有的預防管制、現有的偵測管制
3. 評分：嚴重度（1-10）、發生度（1-10）、偵測度（1-10）
4. **經典 RPN：** RPN = S × O × D。優先處理高 RPN。
5. **AIAG-VDA AP：** 用 S-O-D 組合矩陣指派 Action Priority：High、Medium、Low。
6. 為 High 優先的項目定義建議措施，並指定負責人和目標日期

### 階段 3：驗證
審查：所有功能 / 步驟都涵蓋了嗎？嚴重度分數符合實際對客戶的影響嗎？偵測度分數實際嗎（不要過於樂觀）？
**關卡：** 涵蓋完整、評分實際、高優先項目都有指派措施。

### 階段 4：輸出
回傳 FMEA 登記表，附上排好優先順序的措施。

## 輸出格式

```json
{
  "fmea_items": [{"failure_mode": "seal leak", "effect": "water damage", "cause": "material degradation", "severity": 8, "occurrence": 4, "detection": 6, "rpn": 192, "ap": "high", "action": "add pressure test at final inspection"}],
  "summary": {"total_modes": 45, "high_priority": 8, "medium": 15, "low": 22},
  "metadata": {"type": "PFMEA", "scope": "assembly line 3"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 咖啡機沖煮模組，功能：「把水加熱到 93°C」
**預期：** 失效模式：過熱（S=7, O=3, D=4, RPN=84）、加熱不足（S=5, O=4, D=3, RPN=60）、完全不加熱（S=8, O=2, D=2, RPN=32）。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| S=10，不管 O 和 D | 一律高優先 | 攸關安全的失效不管 RPN 多少都要處理 |
| RPN=100 (S=10,O=1,D=10) vs (S=1,O=10,D=10) | RPN 相同，風險差很多 | 這就是 AIAG-VDA AP 要取代純 RPN 的原因 |
| 沒有現有管制 | D=10（無法偵測） | 誠實的評估才會推動改善 |

## 注意事項

- **RPN 會誤導**：S=10,O=1,D=10 算出的 RPN=100（災難性但罕見、無法偵測），和 S=1,O=10,D=10（無關緊要但頻繁）差很多。AIAG-VDA AP 矩陣就是處理這個缺陷。
- **評分的一致性**：沒有校準的話，不同的團隊成員打分會不一樣。要用附範例的評分標準，並由團隊一起校準。
- **偵測 ≠ 預防**：偵測度分數低（偵測得好）並不會防止失效，只是把它攔下來。降低發生度要比改善偵測度更優先。
- **活的文件**：設計 / 製程有變更、出現新的失效資料，或實施矯正措施時，FMEA 都必須更新。靜態的 FMEA 價值會遞減。
- **範圍蔓延**：想涵蓋所有東西的 FMEA 會變得無法管理。先專注在關鍵功能或風險最高的區域。

## 參考資料

- AIAG-VDA AP 矩陣與評分表，見 `references/aiag-vda-ap.md`
- S/O/D 評分標準，見 `references/scoring-rubrics.md`
