---
name: scientific-thinking-literature-review
description: 針對學術、生物醫學、技術與科學主題的系統性文獻回顧工作流程，包含搜尋規劃、來源篩選、綜合整理、引用檢查和證據紀錄。任務是尋找、篩選、綜合並引用一批學術或技術文獻時使用。
metadata:
  origin: community
---

# 文獻回顧

任務是尋找、篩選、綜合並引用一批學術或技術文獻時，使用這個 skill。

## 何時使用

- 建立系統性、範圍性或敘述性的文獻回顧。
- 綜合某個研究問題的現況（state of the art）。
- 找出缺口、矛盾或未來研究方向。
- 為論文或報告準備有引用佐證的背景段落。
- 比較同儕審查論文、預印本、專利和技術報告之間的證據。

## 回顧類型

- **敘述性回顧**：廣泛的綜合整理，適合用來建立方向感。
- **範圍性回顧**：描繪概念、方法和證據缺口。
- **系統性回顧**：預先定義的流程、可重現的搜尋、明確的篩選與排除。
- **統合分析（meta-analysis）**：系統性回顧，再加上效果量的量化彙整。

問使用者需要哪種嚴謹程度。沒指定的話，探索性工作預設用範圍性回顧，要發表或做臨床主張就用系統性回顧。

## 工作流程

### 1. 定義問題

把提示轉成可以搜尋的研究問題。

臨床或生物醫學工作用 PICO：

- Population（族群）
- Intervention or exposure（介入或暴露）
- Comparator（對照）
- Outcome（結果）

技術工作則用：

- 系統或領域
- 方法或介入
- 比較基準
- 評估指標

### 2. 規劃搜尋

蒐集來源之前，先建立搜尋流程：

- 要搜尋的資料庫
- 日期範圍
- 語言
- 出版類型
- 納入條件
- 排除條件
- 精確的搜尋字串

最少需要的實用資料庫組合：

- PubMed：生物醫學與生命科學文獻。
- arXiv：CS、數學、物理、量化生物學和預印本。
- Semantic Scholar 或 Crossref：廣泛的學術探索。
- 相關時再加領域專屬來源，例如臨床試驗登記、專利資料庫、標準機構或官方技術文件。

### 3. 搜尋並記錄證據

維護一份搜尋紀錄，讓回顧可以重現：

```markdown
| Database | Date searched | Query | Filters | Results | Export |
| --- | --- | --- | --- | ---: | --- |
| PubMed | 2026-05-11 | `("CRISPR"[tiab] OR "Cas9"[tiab]) AND "sickle cell"[tiab]` | 2020:2026, English | 86 | PMID list |
| arXiv | 2026-05-11 | `CRISPR sickle cell gene editing` | q-bio, 2020:2026 | 9 | BibTeX |
```

原始的 ID、URL、DOI、摘要和筆記，要跟最後的文字分開存放。

### 4. 去重

依這個順序去重：

1. DOI
2. PMID 或 arXiv ID
3. 完全相同的標題
4. 標準化後的標題加第一作者和年份

記錄移除了多少重複。

### 5. 篩選來源

分階段篩選：

1. 標題
2. 摘要
3. 全文

做系統性工作時，要記錄排除原因：

- 族群不對
- 介入不對
- 結果不對
- 不是原始研究
- 重複
- 取不到全文
- 超出日期範圍

### 6. 擷取資料

用結構化的擷取表：

```markdown
| Study | Design | Population/Data | Method | Comparator | Outcome | Key finding | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Author Year | RCT/cohort/review/etc. | sample or corpus | method | baseline | measured outcome | result | caveat |
```

技術論文要包含資料集、benchmark、指標、baseline 和可重現性備註。

### 7. 綜合整理

依主題歸納證據，不要一篇一篇摘要論文。

好用的綜合視角：

- 最強的證據
- 互相衝突的證據
- 方法上的弱點
- 族群或資料集的限制
- 時效與重複驗證
- 實務上的意涵
- 尚未回答的問題

依信心程度區分主張：

- **高信心**：跨來源重複驗證過的高品質證據。
- **中信心**：合理，但受限於樣本、方法或時效。
- **低信心**：早期、推測性、單一來源，或衡量薄弱。

### 8. 驗證引用

定稿之前：

- 驗證 DOI、PMID、arXiv ID 或官方 URL
- 檢查作者姓名和出版年份
- 不要為一篇論文沒有提出的主張引用它
- 預印本要標示為預印本
- 區分回顧文獻和原始證據

## 輸出範本

```markdown
# Literature Review: <Topic>

Generated: <date>
Review type: <narrative | scoping | systematic | meta-analysis>
Search window: <dates>
Databases: <list>

## Research Question

## Search Strategy

## Inclusion and Exclusion Criteria

## Evidence Summary

## Thematic Synthesis

## Gaps and Limitations

## References

## Search Log
```

## 常見陷阱

- 不要把搜尋結果的摘要片段當成證據。
- 不要把預印本、回顧文獻和原始研究混在一起卻不標示。
- 不要漏掉負面或互相衝突的發現。
- 沒有可重現的流程，就不要宣稱有系統性回顧的嚴謹度。
- 除非範圍明確限定在那個資料庫，否則不要只用單一資料庫就下廣泛的結論。
