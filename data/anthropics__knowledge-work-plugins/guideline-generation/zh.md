---
name: guideline-generation
description: >
  這個 skill 負責從素材來源產生、建立或打造品牌語氣指南。
  當使用者要求「generate brand guidelines」、
  「create a style guide」、「extract brand voice」、「create guidelines from calls」、
  「consolidate brand materials」、「analyze my sales calls for brand voice」、
  「build a brand playbook from documents」、「synthesize a voice and tone guide」，
  或上傳品牌文件、逐字稿或會議錄影來做品牌
  分析時使用。使用者手上有探索報告、想把它
  轉成可執行的指南時，也會觸發。
---

# Guideline Generation

從任何組合的來源：品牌文件、銷售通話逐字稿、探索報告或使用者直接輸入，產生完整、LLM 可直接使用的品牌語氣指南。把原始素材轉成結構化、可執行的指南，並附上信心分數和待釐清問題。

## 輸入

接受任何組合的：
- 來自 discover-brand skill 的**探索報告**（結構化、已預先篩選）
- **品牌文件**，上傳的或來自已連接的平台（PDF、PPTX、DOCX、MD、TXT）
- **對話逐字稿**，來自 Gong、Granola、手動上傳，或 Notion 會議筆記
- 使用者對自己品牌語氣和價值觀的**直接輸入**

有提供探索報告時，就把它當作主要輸入，因為來源已經篩選並排好名次。再視需要用額外的分析補充。

## 產生流程

### 1. 辨識並分類來源

判斷使用者提供了什麼。如果沒有可用的來源：
- 檢查先前執行 `/brand-voice:discover-brand` 有沒有留下探索報告
- 檢查 `.claude/brand-voice.local.md` 裡已知的品牌素材位置
- 建議先執行探索：`/brand-voice:discover-brand`

### 2. 處理來源

**針對文件：** 把繁重的解析工作委派給 document-analysis agent。擷取語氣屬性、訊息主題、術語、調性指引和範例。

**針對逐字稿：** 把模式辨識委派給 conversation-analysis agent。擷取隱含的語氣屬性、成功的用語模式、依情境的調性，以及反模式。

**針對探索報告：** 擷取已預先篩選的來源、衝突和缺口。直接使用排好名次的來源。

### 3. 整合成指南

把所有發現合併成一份統一的指南文件，依照 `references/guideline-template.md` 裡的範本。關鍵段落：

**「We Are / We Are Not」表**：品牌識別的核心錨點：

| We Are | We Are Not |
|--------|------------|
| [Attribute — e.g., "Confident"] | [Counter — e.g., "Arrogant"] |
| [Attribute — e.g., "Approachable"] | [Counter — e.g., "Casual or sloppy"] |

從各來源中最一致的模式推導屬性。每一列都應該有佐證。

**Voice 不變，Tone 彈性**：釐清什麼固定、什麼隨情境調整：
- **Voice** = 個性、價值觀、「We Are / We Are Not」，在所有內容中都不變
- **Tone** = 正式程度、能量、技術深度，隨情境彈性調整

**依情境的 Tone 矩陣：**

| Context | Formality | Energy | Technical Depth | Example |
|---------|-----------|--------|-----------------|---------|
| Cold outreach | Medium | High | Low | "[example phrase]" |
| Enterprise proposal | High | Medium | High | "[example phrase]" |
| Social media | Low | High | Low | "[example phrase]" |

### 4. 指派信心分數

依 `references/confidence-scoring.md` 裡的方法，為每個段落打分數：
- **High confidence**：3 個以上互相佐證的來源，找到明確的指引
- **Medium confidence**：1 到 2 個來源，或從模式推論出來
- **Low confidence**：單一來源、推論出來，或資料互相衝突

### 5. 浮現待釐清問題

對任何無法解決的模糊之處，產生待釐清問題：

```markdown
## Open Questions for Team Discussion

### High Priority (blocks guideline completion)
1. **[Question Title]**
   - What was found: [conflicting or incomplete info]
   - Agent recommendation: [suggested resolution with reasoning]
   - Need from you: [specific decision or confirmation needed]
```

每個待釐清問題都一定要附 agent 的建議。把模糊之處變成「確認或推翻」，絕對不要讓它變成死路。

### 6. 品質檢查

呈現之前，透過 quality-assurance agent（定義在 `agents/quality-assurance.md`）驗證：
- 所有主要段落都已填寫（來源足以支撐時，包含 Brand Personality 和 Content Examples）
- 至少 3 個有佐證的語氣屬性
- 「We Are / We Are Not」表有 4 列以上
- Tone 矩陣至少涵蓋 3 種情境
- 每個段落都指派了信心分數
- 所有擷取的元素都標明來源
- 沒有暴露 PII
- 待釐清問題都附有建議

### 7. 呈現並提供後續步驟

摘要關鍵發現：
- 產生的段落總數，附信心分數的分布
- 最強的語氣屬性和最有效的訊息
- 待釐清問題的數量（如果有的話）

### 8. 儲存供未來的 session 使用

預設的儲存位置是使用者工作資料夾內的 `.claude/brand-voice-guidelines.md`。

**重要：** agent 的工作目錄不一定是使用者的專案根目錄（尤其是在 Cowork，plugin 是從 plugin cache 目錄執行的）。一律要相對於使用者的工作資料夾來解析路徑，不要用目前的工作目錄。如果沒有設定工作資料夾，就跳過檔案儲存，並告訴使用者指南只會在這次對話中可用。

1. **解析儲存路徑。** 檔案一定要存到使用者工作資料夾內的 `.claude/brand-voice-guidelines.md`。寫入前先確認工作資料夾的路徑。
2. **檢查那個路徑下是否已有指南**
3. **如果已存在，就封存前一個版本：** 把現有的檔案在同一個目錄下改名為 `brand-voice-guidelines-YYYY-MM-DD.md`（用今天的日期）
4. **把新的指南儲存**到工作資料夾內的 `.claude/brand-voice-guidelines.md`
5. **用完整的絕對路徑跟使用者確認：**「Guidelines saved to `<full-path>`. `/brand-voice:enforce-voice` will find them automatically in future sessions.」

指南也存在於這次對話中，所以 `/brand-voice:enforce-voice` 可以立刻使用，不需要從檔案載入。

儲存之後，提供：
1. 逐段走過整份指南
2. 用 `/brand-voice:enforce-voice` 開始建立內容
3. 解決待釐清問題

## 隱私與安全

在整個產生流程中都要落實這些隱私限制，不是只在輸出時：
- 從所有範例中遮蔽客戶名稱和聯絡資訊
- 如果被要求，把逐字稿摘錄中的公司名稱匿名化
- 標記處理過程中偵測到的任何敏感資訊

## 參考檔案

- **`references/guideline-template.md`**：完整的輸出範本，包含所有段落、欄位定義和格式指引
- **`references/confidence-scoring.md`**：信心評分的方法、門檻和範例
