---
name: brand-voice-enforcement
description: >
  這個 skill 把品牌指南套用到內容創作上。當使用者要求「寫一封 email」「草擬提案」「做 pitch deck」
  「寫 LinkedIn 貼文」「草擬簡報」「寫 Slack 訊息」「草擬銷售內容」，或任何需要套用品牌語氣的內容創作請求時使用。
  也會在出現「on-brand」「brand voice」「enforce voice」「apply brand guidelines」「brand-aligned content」
  「write in our voice」「use our brand tone」「make this sound like us」「rewrite this in our tone」
  或「this doesn't sound on-brand」時觸發。不適用於從零產生指南（用 guideline-generation）
  或探索品牌素材（用 discover-brand）。
---

# Brand Voice Enforcement

把現有的品牌指南套用到所有銷售與行銷內容的產生上。載入使用者的品牌指南，把 voice constants 和 tone flexes 套到內容請求上，驗證輸出，並說明品牌上的選擇。

## 載入品牌指南

用下面的順序找使用者的品牌指南，找到就停：

1. **Session context** — 檢查這個 session 稍早是否已經產生過品牌指南（透過 `/brand-voice:generate-guidelines`）。如果有，它們已經在對話裡，直接用。session 裡產生的指南最新，也最能反映使用者最近的意圖。

2. **本地指南檔** — 檢查使用者工作資料夾裡有沒有 `.claude/brand-voice-guidelines.md`。不要用相對於 agent 目前工作目錄的相對路徑，因為在 Cowork 裡 agent 是從 plugin cache 目錄執行的，不是使用者的專案。要相對於使用者的工作資料夾解析路徑。如果沒有設定工作資料夾，就跳過這一步。

3. **問使用者** — 如果上面都沒找到指南，告訴使用者：
   「我找不到你的品牌指南。你可以：
   - 執行 `/brand-voice:discover-brand`，在你的各個平台上找品牌素材
   - 執行 `/brand-voice:generate-guidelines`，從文件或逐字稿建立指南
   - 直接把指南貼到這個對話，或告訴我檔案在哪」

   等使用者提供指南再繼續。

另外也要讀 `.claude/brand-voice.local.md` 取得執行強度的設定（就算指南是從別的地方來的）：
- `strictness`: strict | balanced | flexible
- `always-explain`: 是否永遠說明品牌上的選擇

## 執行流程

### 1. 分析內容請求

動筆之前先確認：
- **內容類型**：email、簡報、提案、社群貼文、訊息等
- **目標讀者**：角色、資歷、產業、公司階段
- **需要的關鍵訊息**：適用哪些 message pillar
- **特定要求**：長度、格式、語氣覆寫

### 2. 套用 Voice Constants

Voice 是品牌的個性，在所有內容裡都維持不變：
- 套用指南裡的「We Are / We Are Not」屬性
- 一致地使用品牌個性
- 採用核准的用語，拒絕禁用的詞
- 遵循訊息框架和價值主張

「voice constant, tone flexes」模型請參考 `references/voice-constant-tone-flexes.md`。

### 3. 依情境調整 Tone

Tone 會依內容類型和讀者調整。用指南裡的 tone-by-context 矩陣來設定：
- **正式度**：這份該多正式或多隨性？
- **能量**：要有多少急迫感或熱情？
- **技術深度**：要多詳細，或多好懂？

### 4. 產生內容

產出的內容要：
- 全程符合品牌 voice 屬性
- 遵循這個內容類型專屬的 tone 指引
- 自然地帶入關鍵訊息（不要硬塞）
- 使用偏好的用語
- 品質與風格要貼近指南裡的範例

複雜或長篇的內容，交給 content-generation agent（定義在 `agents/content-generation.md`）。
重要性高的內容，交給 quality-assurance agent（定義在 `agents/quality-assurance.md`）做驗證。

### 5. 驗證並說明

內容產生後：
- 簡短點出套用了哪些品牌指南
- 說明關鍵的 voice 與 tone 決定
- 註明有哪些地方為了情境而調整了指南
- 主動提議根據回饋再修

設定裡的 `always-explain` 為 true 時，每次回覆都要附上品牌套用說明。

## 處理衝突

使用者的請求跟品牌指南衝突時：
1. 清楚說明衝突在哪
2. 給出建議
3. 提供選項：嚴格遵循指南、依情境調整，或直接覆寫

預設是調整指南，並說明取捨。

## Open Questions 意識

Open questions 是產生指南時標記出來、還沒解決的品牌定位決策，存在指南的「Open Questions」段落裡。產生內容時，要檢查品牌指南有沒有 open questions：
- 如果內容碰到還沒解決的 open question，要註明
- 除非使用者另有指示，否則採用 agent 在該 open question 上的建議
- 如果該問題對內容影響很大，建議使用者把它解決掉

## 參考檔案

- **`references/voice-constant-tone-flexes.md`** — 「voice constant, tone flexes」心智模型、「We Are / We Are Not」表格結構，以及 tone-by-context 矩陣的說明
- **`references/before-after-examples.md`** — 各內容類型的前後對照範例，展示實際執行的樣子
