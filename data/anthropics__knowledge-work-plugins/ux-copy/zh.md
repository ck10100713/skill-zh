---
name: ux-copy
description: 撰寫或審閱 UX 文案：microcopy、錯誤訊息、空狀態、CTA。用「write copy for」「what should this button say?」「review this error message」觸發，或在替 CTA 命名、寫確認對話框、填空狀態、寫 onboarding 文字時使用。
argument-hint: "<情境或要審閱的文案>"
---

# /ux-copy

> 如果看到不認識的 placeholder，或想確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

替任何介面情境撰寫或審閱 UX 文案。

## 用法

```
/ux-copy $ARGUMENTS
```

## 我需要你提供什麼

- **情境**：哪個畫面、流程或功能？
- **使用者狀態**：使用者想做什麼？心情如何？
- **語氣**：正式、友善、活潑、安心？
- **限制**：字數上限、平台規範？

## 原則

1. **清楚**：把意思講明白。不用行話，不要模稜兩可。
2. **簡潔**：用最少的字傳達完整的意思。
3. **一致**：同樣的東西到處都用同樣的詞。
4. **有用**：每個字都該幫使用者完成目標。
5. **有人味**：像一個樂於幫忙的人在寫，不是機器人。

## 文案模式

### CTA
- 以動詞開頭：「Start free trial」「Save changes」「Download report」
- 要具體：用「Create account」，不要用「Submit」
- 讓結果跟標籤對得上

### 錯誤訊息
結構：發生什麼事 + 為什麼 + 怎麼修
- "Payment declined. Your card was declined by your bank. Try a different card or contact your bank."

### 空狀態
結構：這是什麼 + 為什麼是空的 + 怎麼開始
- "No projects yet. Create your first project to start collaborating with your team."

### 確認對話框
- 把動作講清楚：用「Delete 3 files?」，不要用「Are you sure?」
- 說明後果：「This can't be undone」
- 按鈕用動作當標籤：「Delete files」/「Keep files」，不要用「OK」/「Cancel」

### Tooltip
- 簡潔、有幫助、絕不講廢話

### 載入狀態
- 設定預期，降低焦慮

### Onboarding
- 漸進式揭露，一次一個概念

## 聲音與語氣

依情境調整語氣：
- **成功**：慶祝，但不要過頭
- **錯誤**：有同理心又有幫助
- **警告**：清楚且可執行
- **中性**：資訊明確且簡潔

## 輸出

```markdown
## UX Copy: [Context]

### Recommended Copy
**[Element]**: [Copy]

### Alternatives
| Option | Copy | Tone | Best For |
|--------|------|------|----------|
| A | [Copy] | [Tone] | [When to use] |
| B | [Copy] | [Tone] | [When to use] |
| C | [Copy] | [Tone] | [When to use] |

### Rationale
[Why this copy works — user context, clarity, action-orientation]

### Localization Notes
[Anything translators should know — idioms to avoid, character expansion, cultural context]
```

## 如果有連接 Connector

如果有連接 **~~knowledge base**：
- 拉出你的品牌語氣指南和內容風格指南
- 檢查現有的文案模式和用語標準

如果有連接 **~~design tool**：
- 在 Figma 裡查看畫面情境，了解完整的使用者流程
- 從設計稿檢查字數上限和版面限制

## 小訣竅

1. **情境要具體**：「付款失敗時的錯誤訊息」比「錯誤訊息」好。
2. **分享你的品牌語氣**：「我們專業但溫暖」可以幫我對上你的語氣。
3. **考慮使用者的情緒狀態**：錯誤訊息需要同理心，成功訊息可以慶祝。
