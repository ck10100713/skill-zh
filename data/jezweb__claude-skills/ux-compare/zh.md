---
name: ux-compare
description: "利用 ux-extract 產出的 pattern library，比較多個參考 app 的 UX 模式。讀取 2 份以上的 pattern-library.md，逐個類別走過，找出 app 在哪裡趨同（強烈訊號）、哪裡分歧（真正的設計選擇）、哪些是某個 app 獨有的，以及整組都缺少什麼。產出一份有立場的比較文件，並針對新的開發給建議。不需要瀏覽器，純 markdown 分析。觸發詞：'compare UX patterns'、'how do top apps handle X'、'ux comparison'、'pattern comparison across reference apps'。"
compatibility: claude-code-only
---

# UX Compare

讀 N 份由 `ux-extract` 產出的 pattern library，整合出一份比較。能回答像這樣的問題：

- *"Across claude.ai, Linear, Notion, Vercel, and Superhuman — how are empty states handled?"*
- *"Which apps use keyboard shortcuts, and what's the shared vocabulary?"*
- *"When we build our billing page, should we follow convention or deliberately break it?"*

單一份 extract 是一個參考點。多份 extract 是一個設計資料庫。比較則是一個*決策輔助*，它把資料庫變成「該怎麼做、為什麼」。

## 什麼時候用

- **開發之前**：針對你要做的那類功能比較 3–5 個參考，就能看出慣例和取捨
- **設計 review 期間**："這個模式在我們 extract 的 5 個參考裡都沒有，是故意的嗎？"
- **團隊對齊**：作為設計決策的共同參考
- **產出設計 brief**：趨同的模式變成基準線；分歧的模式變成討論的題目

## 輸入

### 可用的 library

首先，找出有哪些可用。Pattern library 放在：

- `docs/ux-extracts/<app-name>/pattern-library.md`
- `.jez/artifacts/ux-extracts/<app-name>/pattern-library.md`

列出你找到的所有 library。把清單連同每份的 extract 日期給使用者看，讓他們能看出哪些過時了：

```
Available pattern libraries:
- claude.ai      (extracted 2026-03-12)
- linear.app     (extracted 2026-02-28)
- notion.so      (extracted 2026-01-15) ← 3 months old
- superhuman     (extracted 2026-03-20)
```

如果只有一份 library，就停下來，建議先對更多 app 執行 `ux-extract`。只有一份 library 的「比較」就只是那份 library。

### 範圍 / 焦點

問使用者要比較什麼，或從他們的請求推斷：

- **整份 library**：比較每個 library 的每個類別（冗長但完整）
- **單一類別**：只比 empty state、只比鍵盤、只比 modal（更緊湊，對特定決策更有用）
- **一個功能領域**："這些 app 怎麼處理設定"，橫跨多個類別但保持聚焦
- **一個具體問題**："哪些 app 支援離線？"，也要搜尋 Notable Absences 區塊

範圍越窄，建議越銳利。預設要問：*"What feature or pattern do you want to compare?"*

### 要納入的 library

預設納入使用者提到的每一份 library，如果他們沒指定，就全部納入。讓他們可以排除：*"all except notion — their library is too stale"*。

## 比較流程

### 1. 讀每一份 library

對範圍內的每份 library，讀完整的 `pattern-library.md`。記下：
- Extract 日期
- Extract 的範圍（整個 app 還是部分）
- 任何 **Notable Absences** 區塊，這通常是比較時最有意思的資料

### 2. 逐個類別走過

對要求的範圍，走過任何一份 library 裡出現的每個模式類別。對每個類別：

1. **列出每個 app 怎麼做**：每個 app 一個條列，盡量具體、逐字引用
2. **找出趨同**：大多數或全部都一樣的是什麼？這是低風險的預設做法。
3. **找出分歧**：真正不同的地方在哪？這是設計決策。
4. **標出獨特做法**：只有一個 app 做 X。可能是創新，也可能是怪異，不管哪種都要點出來。
5. **標出覆蓋缺口**：如果某個 app 的 library 沒涵蓋這個類別，要說出來（不要默默把「library 裡沒有」當成「app 裡沒有」）。

### 3. 交叉比對缺少的東西

走完各類別之後，整理整組都缺少的東西。如果 5 個 app 裡有 4 個在破壞性動作上沒有 undo，那就是一個模式。如果 5 個 app 裡有 3 個沒有新增紀錄的鍵盤快捷鍵，那就是有人一再做出的決策。

### 4. 整合出建議

以有立場的指引收尾：
- **Safe default**：趨同的模式。照著做，使用者會覺得熟悉。
- **Deliberate choices**：分歧的模式，附上每個的取捨，讓使用者可以挑。
- **Avoid**：只有一個 app 獨有的模式，除非有明確的理由說明為什麼只有那個 app 這樣做。
- **Gaps worth filling**：令人意外的缺少，或你的使用者看到有處理會受益的缺少。

建議區塊就是要做這份比較的原因。沒有它，這份文件只是一堆條列。有了它，才是一個決策。

## 輸出

寫到 `docs/ux-comparisons/<topic>-YYYY-MM-DD.md`（如果 `.jez/artifacts/ux-comparisons/<topic>-YYYY-MM-DD.md` 這個路徑存在，就寫到那裡）。

Topic slug 取自範圍，例如 `empty-states`、`keyboard-shortcuts`、`onboarding`、`destructive-actions`。

完整的輸出格式見 [references/comparison-template.md](references/comparison-template.md)。

簡短版本：

```
# UX Comparison: Empty States

Compared: claude.ai, linear.app, notion.so, superhuman
Date: 2026-04-19
Scope: How these apps handle empty states across list views, onboarding, and zero-data dashboards.

## At a glance

[2-3 sentences: what converges, what diverges, what's missing across the set]

## Pattern-by-pattern

### Empty list state

- **claude.ai**: illustration + headline + description + primary CTA + 3 shortcut hints
- **linear**: headline only, small text, no CTA
- **notion**: template picker (unique — offers 12 templates)
- **superhuman**: empty state not reached in extract (all-data demo account)

Convergence: most show some form of guidance; none are fully blank.
Divergence: claude.ai guides toward keyboard workflow; notion guides toward templates.
Unique: notion's template-first empty state.
Coverage gap: superhuman not assessed.

### Empty search results
[...]

## Recommendations

- **Safe default**: illustration + one-line description + primary CTA. All convergent apps do this.
- **Consider**: shortcut hints (like claude.ai) if your power-user persona is strong. Tradeoff: adds visual noise that doesn't help first-time users.
- **Skip**: notion's template picker unless you have a templates feature.
- **Fill a gap**: none of the 4 apps explain *why* the list is empty. A one-liner ("No clients yet — add your first to get started") is convergent practice and worth preserving.

## Source libraries

- claude.ai — 2026-03-12
- linear.app — 2026-02-28
- notion.so — 2026-01-15 (stale, re-extract recommended)
- superhuman — 2026-03-20
```

## 自主權

- **直接做**：找出可用的 library、讀它們、寫比較文件、引用來源 library 裡的特定截圖或文案
- **先問**：使用者沒指定範圍時，問一個聚焦的問題，比寫一份漫無邊際的比較便宜
- **停下來確認**：如果可用的 library 少於 2 份，只有 1 份 library 就無法比較，建議先跑 `ux-extract`

## 參考檔案

| 時機 | 讀這個 |
|------|------|
| 撰寫比較文件 | [references/comparison-template.md](references/comparison-template.md) |

## 小技巧

- **不要把每份 library 的所有內容重新列一遍。** 比較的價值在於整合。如果你只是把 5 份 library 的條列複製過來，那就不是在比較。
- **趨同通常是最安全的選擇**，但不一定是最有意思的。要點出趨同可能只是互相抄襲，而不是好設計的地方。
- **引用來源 library 裡的截圖**，不要複製。"See claude.ai pattern library § Empty States, screenshot 502" 能讓 extract 保持是唯一的事實來源。
- **過時的 library 仍然有用**，只要註明日期。12 個月前的 library 是那個時間點的快照，不是什麼都沒有。
- **建議一定要有立場。** *"It depends"* 是最弱的輸出。表明一個立場，使用者可以不同意。
- **比較也會過期。** 底層的 extract 更新時，或有新的參考加入時，重新跑一次。

## 未來：超過 5 個 app

比較的規模是非線性成長的。3 個 app 很舒服；5 個是可讀性的上限；10 個就變成一個用文字無法整合的矩陣。如果比較超過 5 份 library，就分桶：

- Tier 1（最接近你的 app）：詳細條列
- Tier 2（同類的參考）：摘要條列
- Tier 3（離群值、新穎的做法）：例外時才提

或者做幾個範圍更窄的比較，而不是一個超大的比較。
