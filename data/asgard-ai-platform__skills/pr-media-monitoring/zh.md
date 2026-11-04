---
name: "pr-media-monitoring"
description: "建立並執行媒體監測，追蹤新聞、社群和網路管道上的品牌提及、情緒和聲量占比（share of voice）。使用者需要追蹤外界怎麼談論他們的品牌、監測競爭對手的媒體曝光、及早發現新興的公關議題，或衡量活動觸及時使用，就算他們說的是「大家怎麼說我們」、「監測我們的品牌提及」、「追蹤競爭對手的公關動態」或「設定媒體警示」也一樣。"
metadata:
  category: "WP-02 品牌公關"
  tags: ["pr", "media-monitoring", "brand", "reputation"]
---

# 媒體監測

## 框架

```
IRON LAW: Monitor for Action, Not Just Awareness

Media monitoring that produces weekly reports nobody reads is waste.
Every monitoring setup must have TRIGGER ACTIONS defined: if sentiment
drops below X, alert the PR team. If a competitor launches a campaign,
notify marketing within 24 hours. No triggers = no value.
```

### 監測面向

| 面向 | 追蹤什麼 | 工具 |
|-----------|-------------|-------|
| **聲量（Volume）** | 提及次數隨時間的變化 | Google Alerts、Mention、Meltwater |
| **情緒（Sentiment）** | 正面／中性／負面的比例 | Brandwatch、Talkwalker、人工編碼 |
| **聲量占比（Share of Voice）** | 你的提及數 vs 競爭對手的提及數 | 產業報告、自訂儀表板 |
| **來源（Source）** | 提及出現在哪裡（新聞、社群、論壇、部落格） | 平台分析、社群聆聽工具 |
| **影響者（Influencer）** | 誰在談論（觸及、權威度） | BuzzSumo、社群平台分析 |
| **主題（Topics）** | 哪些主題／關鍵字與你的品牌有關聯 | 關鍵字分群、主題模型 |

### 設定步驟

**Phase 1：定義關鍵字**
- 品牌名稱 + 常見的拼錯
- 產品名稱、CEO 姓名、主要高階主管
- 競爭對手的品牌名稱
- 產業關鍵字（作為脈絡）
- 用來排除不相關結果的否定關鍵字

**Phase 2：選擇管道**
- 新聞（傳統媒體、網路新聞）
- 社群媒體（Facebook、IG、X/Twitter，台灣要加 PTT、Dcard）
- 論壇與評論網站
- 影片（YouTube、TikTok）
- Podcast（新興管道，比較難監測）

**Phase 3：設定觸發條件**
| 觸發條件 | 門檻 | 行動 |
|---------|-----------|--------|
| 負面情緒暴增 | 24 小時內增加超過 20% | 立刻通知公關經理 |
| 競爭對手發表新產品 | 任何提及 | 通知行銷團隊 |
| 影響者提及（追蹤者超過 1 萬） | 任何提及 | 評估是否有互動的機會 |
| 偵測到危機關鍵字 | 「召回」、「訴訟」、「醜聞」+ 品牌 | 啟動危機程序 |

**Phase 4：報告節奏**
- 針對危機觸發條件的即時警示
- 給公關團隊的每日摘要
- 給行銷主管的每週摘要
- 給高階主管團隊的每月報告（聲量、情緒、聲量占比趨勢）

## 輸出格式

```markdown
# Media Monitoring Report: {Brand} — {Period}

## Summary
| Metric | Current | Prior Period | Change |
|--------|---------|-------------|--------|
| Total Mentions | {N} | {N} | {%} |
| Sentiment (Pos/Neu/Neg) | {%}/{%}/{%} | ... | ... |
| Share of Voice | {%} | {%} | {±%} |

## Top Mentions
| Date | Source | Headline/Summary | Sentiment | Reach |
|------|--------|-----------------|-----------|-------|
| {date} | {outlet} | {summary} | +/0/- | {est. reach} |

## Alerts Triggered
| Date | Trigger | Action Taken |
|------|---------|-------------|
| {date} | {what happened} | {response} |

## Competitor Activity
| Competitor | Mentions | Key Activity |
|-----------|----------|-------------|
| {name} | {N} | {what they did} |

## Recommendations
1. {action based on findings}
```

## 注意事項

- **情緒分析並不完美**：自動化工具會誤判諷刺、產業行話和依賴脈絡的語言。每週要人工檢查一個樣本來校準。
- **PTT／Dcard 在台灣很重要**：對台灣品牌來說，PTT 和 Dcard 是關鍵管道，很多國際監測工具涵蓋得不好。要考慮本地工具或人工監測。
- **聲量暴增 ≠ 危機**：一個正面提及你品牌的爆紅迷因，也會造成聲量暴增。不要慌，先看情緒再決定要不要升級。
- **監測競爭對手是合法且合乎倫理的**：追蹤競爭對手被公開提及的內容是標準做法。取得私人資料或冒充競爭對手則不是。

## 參考資料

- 危機升級程序請看 pr-crisis-response skill
- 台灣專屬的媒體生態請看 `references/taiwan-media.md`
