---
name: brand-review
description: 對照你的品牌語氣、風格指南和訊息支柱審查內容，依嚴重程度標出偏離之處，並附上具體的修改前／修改後建議。適用於內容發布前檢查草稿、稽核文案的語氣一致性和用詞，或篩檢未經證實的宣稱、缺少的免責聲明和其他法律警示。
argument-hint: "<content to review>"
---

# 品牌審查

> 如果看到不熟悉的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

對照品牌語氣、風格指南和訊息標準，審查行銷內容。標出偏離之處並提供具體的改善建議。

## 觸發

使用者執行 `/brand-review`，或要求對照品牌指南審閱、檢查或稽核內容。

## 輸入

1. **要審查的內容**：接受以下任何形式的內容：
   - 直接貼在對話中
   - 檔案路徑，或 ~~knowledge base 的參照（例如 Notion 頁面、共用文件）
   - 已發布頁面的 URL
   - 多份內容的批次審查

2. **品牌指南來源**（自動判斷）：
   - 如果本機設定中已設定品牌風格指南，就自動使用
   - 如果沒有設定，就問："Do you have a brand style guide or voice guidelines I should review against? You can paste them, share a file, or describe your brand voice. Otherwise, I'll do a general review for clarity, consistency, and professionalism."

## 審查流程

### 已設定品牌指南時

依下列每個面向評估內容：

#### 語氣與口吻（Voice and Tone）
- 內容符合定義的品牌語氣屬性嗎？
- 這個口吻適合這種內容類型和受眾嗎？
- 有沒有讓人覺得不一致的語氣轉變？
- 標出偏離的具體句子或片語，並說明為什麼

#### 用詞與語言
- 慣用的品牌用詞有被正確使用嗎？
- 有沒有出現任何「避免」的用詞或片語？
- 行話的程度適合目標受眾嗎？
- 產品名稱、功能名稱和品牌用詞有被正確使用嗎（大小寫、格式）？

#### 訊息支柱
- 內容有跟定義的訊息支柱或價值主張一致嗎？
- 宣稱跟核准的訊息一致嗎？
- 內容是在強化還是牴觸品牌定位？

#### 風格指南遵循
- 依風格指南的文法和標點（例如 Oxford comma、title case vs. sentence case）
- 格式慣例（標題、清單、強調）
- 數字格式、日期格式
- 縮寫用法（第一次使用時有定義嗎？）

### 沒有品牌指南時（通用審查）

評估內容的：

#### 清晰度
- 主要訊息在第一段內就清楚了嗎？
- 句子簡潔又容易理解嗎？
- 結構合乎邏輯又容易跟隨嗎？
- 有沒有含糊的陳述或不清楚的指涉？

#### 一致性
- 口吻從頭到尾一致嗎？
- 用詞一致嗎（同一個概念沒有在同義詞之間切換）？
- 格式一致嗎（標題、清單、大小寫）？

#### 專業度
- 內容沒有錯字、文法錯誤和彆扭的措辭嗎？
- 口吻適合預期的受眾嗎？
- 宣稱有支持或證實嗎？

### 法律與合規警示（一律檢查）

不論有沒有設定品牌指南，都要標出：
- **未經證實的宣稱**：沒有證據或限定條件的最高級詞（"best"、"fastest"、"only"）
- **缺少免責聲明**：可能需要法律免責聲明的財務宣稱、健康宣稱或保證
- **比較性宣稱**：可能被質疑的與競爭對手的比較
- **法規用語**：可能需要合規審查的內容（金融服務、醫療等）
- **推薦見證問題**：沒有署名或揭露的引述或背書
- **著作權疑慮**：看起來是從其他來源緊密改寫的內容

## 品牌語氣參考

使用這些框架來對照品牌標準評估內容，或協助使用者記錄他們的品牌語氣。

### 品牌語氣文件框架

完整的品牌語氣文件應涵蓋這些領域：

1. **品牌個性**：把品牌當成一個人來定義。範例："If our brand were a person, they would be a knowledgeable colleague who explains complex things simply, celebrates your wins genuinely, and never talks down to you."
2. **語氣屬性**：3-5 個定義品牌如何溝通的屬性，每個都要定義它在實務上代表什麼、它「不」代表什麼（避免誤解），以及一個範例。
3. **受眾意識**：品牌在對誰說話（主要和次要）、他們在意什麼、他們的專業程度，以及他們期待被怎麼稱呼。
4. **核心訊息支柱**：品牌持續傳達的 3-5 個關鍵主題、這些訊息的層次，以及每個支柱如何連結到受眾的需求。
5. **口吻光譜**：語氣如何隨情境調整，同時仍然讓人認得是同一個品牌。
6. **風格規則**：具體的文法、格式和語言規則。
7. **用詞**：慣用和避免的用詞。

### 語氣屬性光譜

定義或評估品牌語氣時，把屬性放在光譜上定位：

| 光譜 | 一端 | 另一端 |
|----------|---------|-----------|
| 正式程度 | 正式、制度化 | 隨性、口語 |
| 權威 | 專家、權威 | 同儕、協作 |
| 情感 | 溫暖、同理 | 直接、就事論事 |
| 複雜度 | 技術性、精確 | 簡單、易懂 |
| 能量 | 大膽、有活力 | 沉穩、節制 |
| 幽默 | 俏皮、機智 | 嚴肅、誠懇 |
| 創新 | 尖端、前瞻 | 成熟、經過驗證 |

對每個選定的屬性，用這個格式記錄：

**[Attribute name]**
- **We are**: [what this means in practice]
- **We are not**: [common misinterpretation to avoid]
- **This sounds like**: [example sentence demonstrating the attribute]
- **This does NOT sound like**: [example sentence violating the attribute]

範例：

**Approachable**
- **We are**: friendly, clear, jargon-free, welcoming to beginners and experts alike
- **We are not**: dumbed-down, overly casual, or lacking substance
- **This sounds like**: "Here's how to get started — it takes about five minutes."
- **This does NOT sound like**: "Yo! This is super easy, even a noob can do it lol."

### 跨管道和情境的口吻調整

品牌語氣保持一致，但口吻會隨情境調整。口吻是套用在語氣上的情緒抑揚。

#### 依管道區分的口吻

| 管道 | 口吻調整 | 範例 |
|---------|----------------|---------|
| 部落格 | 資訊豐富、口語、教育性 | "Let's walk through how this works and why it matters for your team." |
| 社群媒體（LinkedIn） | 專業、發人深省、簡潔 | "Three things we learned from running 50 campaigns this quarter." |
| 社群媒體（Twitter/X） | 簡短有力、直接、有時機智 | "Your landing page has 3 seconds. Make them count." |
| 電子郵件行銷 | 個人化、有幫助、以行動為導向 | "We put together something we think you'll find useful." |
| 銷售資料 | 有自信、以好處為導向、具體 | "Teams using our platform reduce reporting time by 40%." |
| 支援／說明文件 | 清楚、有耐心、逐步 | "If you see this error, here's how to fix it." |
| 新聞稿 | 正式、事實性、具新聞價值 | "The company today announced the launch of..." |
| 錯誤訊息 | 同理、有幫助、不責怪 | "Something went wrong on our end. We're looking into it." |

#### 依情境區分的口吻

| 情境 | 口吻調整 |
|-----------|----------------|
| 產品發表 | 興奮、有自信、前瞻 |
| 事件或服務中斷 | 透明、同理、負責 |
| 客戶成功案例 | 慶祝、具體、肯定客戶的功勞 |
| 思想領導力 | 權威、細膩、以證據為基礎 |
| 新手上路（Onboarding） | 歡迎、鼓勵、清楚 |
| 壞消息（漲價、功能淘汰） | 誠實、尊重、以解決方案為導向 |
| 競爭比較 | 有自信但公平、以事實為基礎、不貶低 |

#### 口吻調整規則
語氣屬性保持固定。口吻依情境把它們調高或調低。例如，如果一個品牌是 "bold and warm"：
- 在產品發表時，調高大膽
- 在事件回應時，調高溫暖
- 兩個屬性都不會消失；只是平衡改變了

### 風格指南的落實

#### 文法與寫作規範
記錄並一致地落實這些選擇：

| 規則 | 選項 | 範例 |
|------|---------|---------|
| Oxford comma | Yes / No | "fast, reliable, and secure" vs. "fast, reliable and secure" |
| 句首大寫 vs. 標題式大寫（標題） | Sentence / Title | "How to get started" vs. "How to Get Started" |
| 縮寫（Contractions） | Use / Avoid | "we're" vs. "we are" |
| 破折號（em dash）的空格 | No spaces / Spaces | "this—and more" vs. "this — and more" |
| 數字 | 1-9 拼出來、10 以上用數字 / 一律用數字 | "five features" vs. "5 features" |
| 百分比 | % / percent | "50%" vs. "50 percent" |
| 日期格式 | Month DD, YYYY / DD/MM/YYYY / 等 | "January 15, 2025" |
| 時間格式 | 12 小時制 / 24 小時制 | "3:00 PM" vs. "15:00" |
| 清單 | 句號／片語不加句號 | "Set up your account." vs. "Set up your account" |

#### 格式慣例
- 標題層級（何時使用 H1、H2、H3）
- 粗體和斜體的用法（粗體用於強調，斜體用於標題／術語）
- 連結文字（描述性 vs. "click here"，一律用描述性）
- 圖片替代文字的要求
- 程式碼格式（針對技術型品牌）
- 提示框或醒目標示框的用法

#### 標點與強調
- 驚嘆號政策（有限度使用，絕不超過一個）
- 刪節號的用法（在多數專業情境中避免）
- 全大寫政策（避免；改用粗體強調）
- 各管道的表情符號用法（專業管道：極少或不用；社群：適當時使用）

### 用詞管理

#### 慣用詞

維護一份慣用詞及其錯誤替代詞的清單：

| 用這個 | 不要用這個 | 備註 |
|----------|----------|-------|
| sign up (verb) | signup (verb) | "signup" 是名詞形式 |
| log in (verb) | login (verb) | "login" 是名詞／形容詞形式 |
| set up (verb) | setup (verb) | "setup" 是名詞／形容詞形式 |
| email | e-mail | 沒有連字號 |
| website | web site | 一個字 |
| data is (singular) | data are | 除非出版物要求用複數 |

#### 產品與功能名稱
- 產品名稱的官方大小寫
- 何時使用完整產品名稱 vs. 簡稱
- 產品名稱前要不要加 "the"
- 如何在文案中處理版本號
- 商標與註冊符號（何時需要、何時省略）

#### 包容性語言
- 使用性別中立的語言（對不特定的人用 they/them）
- 避免歧視身心障礙的用語（"crazy"、"blind spot"、"lame"）
- 適當時使用以人為先（person-first）的語言
- 避免可能無法翻譯的特定文化慣用語
- 用 "simple" 或 "straightforward" 而不是 "easy"（什麼叫容易因人而異）

#### 產業行話管理
- 定義受眾不用解釋就懂的技術用語
- 列出一律要定義或換成白話的行話
- 指定哪些縮寫在第一次使用時要拼出全名
- 針對對不同讀者意義不同的用語，建立受眾專屬的詞彙表

#### 競爭對手與品類用詞
- 如何稱呼你的產品品類（使用你偏好的框架）
- 如何稱呼競爭對手（用名稱或泛稱）
- 競爭對手創造出來、你應該避免使用的用語（避免強化他們的定位）
- 你偏好的差異化語言

## 輸出格式

審查結果依下列方式呈現：

### 摘要
- 整體評估：內容跟品牌標準（或一般品質）的契合程度
- 1-2 句話摘要最大的優點
- 1-2 句話摘要最重要的改善

### 詳細發現

每個發現的問題，都要提供：

| Issue | Location | Severity | Suggestion |
|-------|----------|----------|------------|

嚴重程度定義：
- **High**：牴觸品牌語氣、含有合規風險，或嚴重削弱訊息
- **Medium**：跟指南不一致，但沒有傷害
- **Low**：輕微的風格或偏好問題

### 修改後的段落

針對嚴重程度最高的前 3-5 個問題，提供修改前／修改後的對照，顯示原文和建議的修改。

### 法律／合規警示

另外列出任何法律或合規疑慮，並附上建議的處理行動。

## 審查之後

詢問："Would you like me to:
- Revise the full content with these suggestions applied?
- Focus on fixing just the high-severity issues?
- Review additional content against the same guidelines?
- Help you document your brand voice for future reviews?"
