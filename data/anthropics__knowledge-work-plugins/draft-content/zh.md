---
name: draft-content
description: 起草部落格文章、社群貼文、電子報、landing page、新聞稿和案例研究，附上各通路專屬的格式和 SEO 建議。寫任何行銷內容、需要標題或主旨行的多個選項，或要把訊息改編成適合特定平台、受眾和品牌語氣時使用。
argument-hint: "<content type and topic>"
---

# Draft Content

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

針對特定的內容類型、受眾和品牌語氣，產生行銷內容草稿。

## 觸發

使用者執行 `/draft-content`，或要求起草、撰寫或建立行銷內容。

## 輸入

向使用者蒐集以下資訊。沒有提供的話，先問再繼續：

1. **內容類型**：下列之一：
   - 部落格文章
   - 社群貼文（指定平台：LinkedIn、Twitter/X、Instagram、Facebook）
   - 電子報
   - Landing page 文案
   - 新聞稿
   - 案例研究

2. **主題**：內容的主旨或議題

3. **目標受眾**：這份內容是給誰看的（職務、產業、資歷、痛點）

4. **關鍵訊息**：2 到 4 個要傳達的主要重點或心得

5. **語氣**：例如權威、對話式、鼓舞人心、技術性、機智幽默（如果已設定品牌語氣，可不填）

6. **長度**：目標字數或格式限制（例如「1000 字」「280 字元」「3 段」）

## 品牌語氣

- 如果使用者的本機設定檔裡有設定品牌語氣，就自動套用。並告知使用者正在套用品牌語氣設定。
- 如果沒有設定品牌語氣，就問：「Do you have brand voice guidelines you'd like me to follow? If not, I'll use a neutral professional tone.」
- 整份草稿從頭到尾一致套用指定的語氣或預設語氣。

## 依類型產生內容

### 部落格文章
- 吸引人的標題（提供 2 到 3 個選項）
- 帶有 hook 的開頭（問句、統計數字、大膽的主張或故事）
- 3 到 5 個有條理的段落，搭配描述性的小標題
- 每個段落都有支撐論點、範例或資料引用
- 結尾附明確的 call to action
- SEO 考量：建議一個主關鍵字，放進標題和第一段，並在小標題使用相關關鍵字

### 社群貼文
- 符合平台的格式和長度
- 第一行就放 hook
- Hashtag 建議（3 到 5 個相關的 hashtag）
- Call to action 或互動引導
- 依品牌和平台適度使用 emoji
- 如果是 LinkedIn：專業的包裝，用分段讓文章好讀
- 如果是 Twitter/X：簡潔有力，控制在字元上限內
- 如果是 Instagram：以視覺為先的語言、故事導向、hashtag 區塊

### 電子報
- 主旨行（提供 2 到 3 個選項，並考量開信率）
- 預覽文字
- 開頭問候
- 層級清楚的內文段落
- Call to action 按鈕文字
- 結尾署名
- 提醒加上取消訂閱的說明

### Landing Page 文案
- 標題與副標題
- Hero 區塊文案
- 價值主張（3 到 4 個以效益為導向的重點或段落）
- 社會認證的佔位（建議放推薦語或數據的位置）
- 主要與次要 CTA
- FAQ 段落建議
- SEO：meta title 和 meta description 建議

### 新聞稿
- 符合新聞稿慣例的標題
- 發稿日期與地點（dateline）
- 導言段（who、what、when、where、why）
- 引述（提供佔位的撰寫指引）
- 公司簡介（boilerplate）佔位
- 媒體聯絡人佔位
- 標準的新聞稿格式

### 案例研究
- 強調成果的標題
- 客戶概況（產業、規模、挑戰）
- 挑戰段落
- 解決方案段落（實際導入了什麼）
- 附指標的成果段落（向使用者索取數據）
- 客戶引述佔位
- Call to action

## SEO 考量（針對網頁內容）

針對部落格文章、landing page 和其他面向網頁的內容：
- 依主題建議一個主關鍵字
- 建議關鍵字的擺放位置：標題、第一段、小標題、meta description
- 建議內部和外部連結的機會
- 建議一段 meta description（160 字元以內）
- 註明圖片 alt text 的機會

## 輸出

用清楚的格式呈現草稿。草稿之後附上：
- 簡短說明套用了哪種品牌語氣和調性
- 任何 SEO 建議（針對網頁內容）
- 後續步驟的建議（例如「跟團隊一起 review」「加入客戶引述」「搭配視覺素材」）

最後問：「Would you like me to revise any section, adjust the tone, or create a variation for a different channel?」
