---
name: scientific-problem-selection
description: 當科學家需要協助選擇研究題目、發想專案、替卡關的專案排障，或做策略性的科學決策時，使用這個 skill。當使用者要提出新的研究點子、處理專案裡的問題、評估專案風險、規劃研究策略、走過決策樹，或需要協助選擇要做哪個科學問題時使用。典型的請求像是「I have an idea for a project」、「I'm stuck on my research」、「help me evaluate this project」、「what should I work on」或「I need strategic advice about my research」。
---

# 科學問題選擇 Skills

一個對話式的框架，用來系統性地選擇科學問題，根據 Fischbach 與 Walsh 的〈Problem choice and decision trees in science and engineering〉（Cell, 2024）。

## 開始

給使用者三個入口：

**1) 提出一個新專案的點子**：一起把它發展起來

**2) 分享目前專案裡的一個問題**：一起排除問題

**3) 問一個策略性的問題**：一起走過決策樹

這種對話式的入口，讓科學家從他們目前所在的位置開始，也建立起合作的氛圍。

---

## 選項 1：提出一個點子

### 起始提示
問：**「用簡短版本告訴我你的點子（1 到 2 句話）。」**

### 回應方式
使用者分享點子之後，回覆一段快速摘要（不超過一段），展現你理解了。點出大致的研究領域，並用凸顯點子核心的方式換句話說，顯示你們的理解一致、準備好深入細節。

### 後續提示
然後請他們提供更多細節：「現在多給我一些細節。你可以包含以下這些，簡短也沒關係，不確定的地方也可以直接說：
1. 你到底想做什麼
2. 你目前打算怎麼做
3. 如果成功了，為什麼會是一件大事
4. 你覺得主要的風險是什麼」

### 工作流程
從這裡開始，引導使用者走過問題選擇與評估的早期階段：
- **Skill 1：Intuition Pumps** - 精煉並強化點子
- **Skill 2：Risk Assessment** - 找出並管理專案風險
- **Skill 3：Optimization Function** - 定義成功指標
- **Skill 4：Parameter Strategy** - 決定哪些要固定、哪些保持彈性

詳細指引見 `references/01-intuition-pumps.md`、`references/02-risk-assessment.md`、`references/03-optimization-function.md` 和 `references/04-parameter-strategy.md`。

---

## 選項 2：排除問題

### 起始提示
問：**「用簡短版本告訴我你的問題（1 到 2 句話，或任何你覺得容易的方式）。」**

### 回應方式
使用者分享問題之後，回覆一段快速摘要（不超過一段），展現你理解了。點出問題發生的專案脈絡，並換句話說，凸顯問題的核心本質，讓使用者知道你理解了狀況。也要提出其他看起來重要、值得討論的問題。

### 後續提示
然後問：「現在多給我一些細節。你可以包含以下這些，簡短也沒關係：
1. 你專案的整體目標（如果我們之前還沒談過）
2. 到底是哪裡出了問題
3. 你目前想到的修正方式」

### 工作流程
從這裡開始，引導使用者進行排障和決策樹的導覽：
- **Skill 5：Decision Tree Navigation** - 規劃決策點，並在執行和策略思考之間切換
- **Skill 4：Parameter Strategy** - 一次只固定一個參數，讓其他的浮動
- **Skill 6：Adversity Response** - 把問題框架成成長的機會
- **Skill 7：Problem Inversion** - 繞過障礙的策略

一定要包含變通辦法，不論問題能不能輕易修好，這些變通辦法都可能有用。

詳細指引見 `references/05-decision-tree.md`、`references/06-adversity-planning.md`、`references/07-problem-inversion.md` 和 `references/04-parameter-strategy.md`。

---

## 選項 3：問一個策略性的問題

### 起始提示
問：**「用簡短版本告訴我你的問題（1 到 2 句話）。」**

### 回應方式
使用者分享問題之後，回覆一段快速摘要（不超過一段），展現你理解了。點出更廣的脈絡，並換句話說，凸顯問題的關鍵，確認和他們的想法一致。

### 後續提示
然後問：「現在多給我一些細節。你可以包含以下這些，簡短也沒關係：
1. 情境（也就是說，這是關於目前的專案還是未來的專案）
2. 你在想的內容，再多說一點細節」

### 工作流程
從這裡開始，從問題選擇框架中，挑選最適合這個問題的特定模組：
- **Skills 1-4**：用於未來專案的規劃（發想、風險、optimization、參數）
- **Skills 5-7**：用於目前專案的導覽（決策樹、逆境、反轉）
- **Skill 8**：用於溝通與綜合
- **Skill 9**：用於完整工作流程的統籌

完整的參考資料見 `references/` 資料夾。

---

## 核心框架概念

### 核心洞見
**Problem Choice >> Execution Quality**

就算把一個平庸的問題執行得很出色，也只會產生漸進式的影響。把一個重要的問題做好，會產生實質的影響。

### 時間悖論
科學家通常花：
- **幾天** 選擇問題
- **好幾年** 解決它

這種失衡限制了影響力。這些 skill 幫助你投入更多時間明智地選擇。

### 評估軸
**評估點子時：**
- **X 軸：** 成功的可能性
- **Y 軸：** 成功時的影響

這些 skill 幫助把點子往右移（更可行）、往上移（更有影響力）。

### 風險悖論
- 不要躲避風險，要和風險做朋友
- 沒有風險 = 漸進式的工作
- 但是：多重奇蹟 = 避開或修正
- **平衡：** 被理解、被量化、可管理的風險

### 參數悖論
- 固定太多 = 脆弱
- 固定太少 = 癱瘓
- **甜蜜點：** 只固定一個有意義的限制

### 逆境原則
- 危機無可避免（不要驚訝）
- 危機是機會（不要浪費）
- **策略：** 同時修好問題並升級專案

---

## 9 個 Skill 總覽

| Skill | 目的 | 產出 | 時間 |
|-------|---------|--------|------|
| 1. Intuition Pumps | 產生高品質的研究點子 | Problem Ideation Document | 約 1 週 |
| 2. Risk Assessment | 找出並管理專案風險 | Risk Assessment Matrix | 3-5 天 |
| 3. Optimization Function | 定義成功指標 | Impact Assessment Document | 2-3 天 |
| 4. Parameter Strategy | 決定哪些要固定、哪些保持彈性 | Parameter Strategy Document | 2-3 天 |
| 5. Decision Tree Navigation | 規劃決策點和 altitude dance | Decision Tree Map | 2 天 |
| 6. Adversity Response | 把危機當成機會做準備 | Adversity Playbook | 2 天 |
| 7. Problem Inversion | 繞過障礙 | Problem Inversion Analysis | 1 天 |
| 8. Integration & Synthesis | 綜合成連貫的計畫 | Project Communication Package | 3-5 天 |
| 9. Meta-Framework | 統籌完整的工作流程 | Complete Project Package | 1-6 週 |

---

## Skill 工作流程

```
SKILL 1: Intuition Pumps
         | (generates idea)
         v
SKILL 2: Risk Assessment
         | (evaluates feasibility)
         v
SKILL 3: Optimization Function
         | (defines success metrics)
         v
SKILL 4: Parameter Strategy
         | (determines flexibility)
         v
SKILL 5: Decision Tree
         | (plans execution and evaluation)
         v
SKILL 6: Adversity Planning
         | (prepares for failure modes)
         v
SKILL 7: Problem Inversion
         | (provides pivot strategies)
         v
SKILL 8: Integration & Communication
         | (synthesizes into coherent plan)
         v
SKILL 9: Meta-Skill
         (orchestrates complete workflow)
```

---

## 關鍵設計原則

1. **對話式入口**：用三個明確的起點，讓使用者從他們所在的位置開始
2. **用心的互動**：問釐清問題；信心低就請對方補充更多資訊
3. **整合文獻**：在關鍵的時間點使用 PubMed 搜尋來驗證
4. **具體的產出**：每個 skill 都產出具體的 1 到 2 頁文件
5. **逐步建立具體性**：透過有針對性的問題，逐漸浮現更多細節
6. **彈性**：Skill 可以獨立、依序或反覆地使用
7. **科學嚴謹**：關於普遍性和可行性的主張，應該要有證據支持

---

## 誰該使用這些 Skills

### 研究生（主要對象）
- **何時：** 選擇論文專案、資格考、委員會會議
- **重點：** Skills 1-3（發想、風險、影響）+ Skill 9（完整工作流程）
- **時程：** 完整規劃需要 2 到 4 週

### 博士後研究員
- **何時：** 開始新職位、規劃獨立專案、申請研究獎助
- **重點：** 所有 skill，強調獨立性和風險管理
- **時程：** 密集規劃 1 到 2 週

### 主持人（PI）
- **何時：** 新實驗室、新方向、指導學員、經費申請週期
- **重點：** Skills 1、3、4、6（發想、影響、參數、逆境）
- **時程：** 持續進行，融入實驗室文化

### 新創創辦人
- **何時：** 公司創立、轉向決策、向投資人簡報
- **重點：** Skills 1-4（從發想到參數）+ Skill 8（溝通）
- **時程：** 初期規劃 1 到 2 週，每季回顧

---

## 參考資料

詳細的 skill 文件放在 `references/` 資料夾：

| 檔案 | 內容 | 搜尋模式 |
|------|---------|-----------------|
| `01-intuition-pumps.md` | 產生研究點子 | `Intuition Pump #`, `Trap #`, `Phase [0-9]` |
| `02-risk-assessment.md` | 風險辨識 | `Risk.*1-5`, `go/no-go`, `assumption` |
| `03-optimization-function.md` | 成功指標 | `Generality.*Learning`, `optimization`, `impact` |
| `04-parameter-strategy.md` | 參數固定 | `fixed.*float`, `constraint`, `parameter` |
| `05-decision-tree.md` | 決策樹導覽 | `altitude`, `Level [0-9]`, `decision` |
| `06-adversity-planning.md` | 逆境應對 | `adversity`, `crisis`, `ensemble` |
| `07-problem-inversion.md` | 問題反轉策略 | `Strategy [0-9]`, `inversion`, `goal` |
| `08-integration-synthesis.md` | 整合與綜合 | `narrative`, `communication`, `story` |
| `09-meta-framework.md` | 完整工作流程 | `Phase`, `workflow`, `orchestrat` |

---

## 預期成果

### 立即（完成工作流程之後）
- 清楚的專案願景
- 誠實的風險評估
- 應變計畫
- 溝通資料準備就緒
- 對問題選擇有信心

### 6 個月
- 更快的決策（有框架了）
- 有成效的逆境處理
- 沒有存在危機（風險已被緩解）

### 2 年
- 發表成果或有扎實的進展
- 避開死胡同的專案
- 職涯與目標一致
- **時間花得值得**（終極的衡量標準）

---

## 基礎文獻

**Fischbach, M.A., & Walsh, C.T. (2024).** "Problem choice and decision trees in science and engineering." *Cell*, 187, 1828-1833.

根據在 Stanford University 開設的 BIOE 395 課程。
