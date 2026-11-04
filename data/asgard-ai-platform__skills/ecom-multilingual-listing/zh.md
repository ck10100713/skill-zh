---
name: "ecom-multilingual-listing"
description: "最佳化跨國電商的多語言商品上架內容，包含 SEO 在地化、機器翻譯流程與文化調適。當使用者需要建立多語言商品頁、針對當地搜尋最佳化，或為不同市場調整行銷內容時使用。就算使用者只說「翻譯我們的商品頁」、「做當地 SEO」、「調整成適合日本市場」或「翻譯後的商品頁都沒有轉換」也要用。"
metadata:
  category: "WP-01 電商"
  tags: ["e-commerce", "localization", "seo", "multilingual"]
---

# 多語言商品頁最佳化

## 框架

```
IRON LAW: Localization ≠ Translation

Translating product listings word-for-word produces listings that are
grammatically correct but commercially ineffective. Localization adapts
the message for the TARGET MARKET's search behavior, cultural preferences,
and purchasing psychology.

"機能性飲料" doesn't translate to "functional beverage" for a US audience —
it translates to "energy drink" or "performance drink" because that's
what Americans search for.
```

### 在地化流程

**階段 1：關鍵字研究（每個市場各做一次）**
- 研究「當地」的搜尋詞（不是你的關鍵字的翻譯）
- 工具：Google Keyword Planner（設成目標國家）、Ahrefs、當地電商平台的搜尋建議
- 找出目標語言中：搜尋量高 + 競爭低的關鍵字

**階段 2：商品頁結構**
| 元素 | 在地化要求 |
|---------|------------------------|
| **標題** | 放入當地的主要關鍵字、遵守平台字數限制、重要的詞放前面 |
| **重點條列** | 強調「當地」消費者在乎的好處（可能跟母市場不同） |
| **商品描述** | 用有當地慣用語的自然語言，「不是」翻譯過來的官腔 |
| **圖片** | 當地的模特兒/場景、當地的度量單位（公分 vs 英吋）、當地的生活情境 |
| **搜尋詞** | 用當地語言填後台關鍵字，包含錯字和同義詞 |

**階段 3：文化調適**
- 顏色象徵（紅色在中國代表好運，在西方代表危險）
- 尺寸（亞洲 vs 西方的尺寸表，一定要提供換算）
- 信任訊號（各市場不同：美國看評價、日本看認證、東南亞看網紅背書）
- 價格顯示（含稅或未稅，各市場不同）

**階段 4：品質保證**
- 母語人士審閱（不只是雙語者，要是「目標」市場的母語人士）
- 對標題的各個版本做 A/B 測試，看點擊率
- 監控目標關鍵字的搜尋排名
- 查看目標市場競爭對手的商品頁，了解當地慣例

### 翻譯品質等級

| 等級 | 方法 | 成本 | 品質 | 使用情境 |
|------|--------|------|---------|----------|
| 機器翻譯 | AI（GPT、DeepL） | 最低 | 看得懂但常不自然 | 內部使用、草稿 |
| 機器翻譯 + 人工編修 | AI 草稿 → 母語編輯 | 中等 | 不錯 | B 類商品、大量 SKU |
| 專業在地化 | 具備市場專業的人工翻譯 | 最高 | 最好 | A 類商品、攸關品牌的內容 |
| 創譯（Transcreation） | 針對目標文化創意改寫 | 頂級 | 出色 | 標語、品牌故事、廣告 |

## 輸出格式

```markdown
# Listing Localization: {Product} → {Target Market}

## Keyword Research
| Local Keyword | Search Volume | Competition | Priority |
|-------------|-------------|------------|---------|
| {keyword} | {N/month} | H/M/L | 1/2/3 |

## Localized Listing
- **Title**: {optimized for local keywords}
- **Bullet Points**: {adapted for local benefits emphasis}
- **Description**: {localized, natural language}

## Cultural Adaptations
| Element | Home Market | Target Market | Change |
|---------|-----------|-------------|--------|
| {element} | {original} | {adapted} | {why} |

## QA Checklist
- [ ] Native speaker reviewed
- [ ] Keywords included in title/backend
- [ ] Sizing chart converted
- [ ] Images culturally appropriate
```

## 常見陷阱

- **Google 翻譯不是在地化**：它產出的商品頁文法正確，但在商業上是死的。「高品質的真皮皮夾」→「High quality genuine leather wallet」是翻譯。「Premium leather bifold wallet for men — RFID blocking」才是在地化（鎖定美國人實際搜尋的詞）。
- **每個平台的 SEO 規則都不同**：Amazon A9、蝦皮的演算法、樂天的排名，關鍵字擺放規則都不一樣。要研究各平台專屬的最佳實務。
- **不要翻譯評價**：評價應該來自當地客戶。翻譯過來的評價看起來很假，會侵蝕信任。
- **後台關鍵字很重要**：大多數電商平台都有隱藏的關鍵字欄位。用當地語言的同義詞、錯字和替代詞把它填滿。
- **日本市場要求完美**：日本消費者期待無瑕疵的語言、精確的規格和詳盡的商品描述。日本市場不能接受機器翻譯。

## 參考資料

- 各平台專屬的 SEO 指南，見 `references/marketplace-seo.md`
