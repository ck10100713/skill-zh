---
name: balance-check
description: "找出公式和資料裡的平衡離群值、壞掉的成長曲線、退化策略、經濟失衡。「檢查遊戲平衡」。"
argument-hint: "[system-name|path-to-data-file]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(bash "*/.claude/skills/balance-check/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

# Balance Check



每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。

## 輸入不足：產出任何報告之前先檢查這個

**如果這個 skill 需要的輸入不存在，答案是「跑不了」，
不是一份填好的報告。** 先檢查，檢查不過就停。

1. 列出這個 skill 要讀的輸入（資料檔、先前的報告、profiler 輸出、
   測試結果、registry、原始碼）。
2. 每一項都記錄 `FOUND` 或 `ABSENT`，不是「假設存在」。
3. 如果某個章節需要的任何輸入是 ABSENT，那個章節就是
   **`NOT ASSESSED — NO DATA`**。不要估，不要從
   相鄰的產物推論，也不要留一個規定要填的格子讓下一個
   讀範本的人去填。
4. 如果**所有**需要的輸入都是 ABSENT，就停下來，把
   **`NOT ASSESSED — NO DATA`** 當作整份報告的 verdict 回報，並指出缺了什麼、
   哪個 skill 會產出它。

**`NOT ASSESSED` 的 verdict 是成功。** 沒有資料時，
它就是對「資料怎麼說？」最正確、最有用的答案。它要防的失敗模式
很明確：一份 verdict 列舉裡沒有「跑不了」狀態的報告，會產生
**假的乾淨通過**：一個沒有素材也沒有標準的專案，素材稽核卻回報 COMPLIANT；
或是一份效能分析，沒有任何 profiler 資料、也從沒設過預算，卻回報「對 16.67ms 預算有 >99% 的餘裕」。

**沒有證據，不代表沒有問題。** 因為沒有檔案可掃，所以掃不到任何東西，
這並沒有驗證任何事。要說清楚是這兩種情況的哪一種，
光看綠色結果，讀的人分不出來。

---

## Phase 1: 辨識平衡領域

從 `$ARGUMENTS` 判斷平衡領域，要用整個字串，因為資料檔路徑可能含空格：

- **Combat** → 武器／技能 DPS、time-to-kill、傷害類型之間的交互作用
- **Economy** → 資源的產出源與消耗口、取得速率、物品定價
- **Progression** → XP／戰力曲線、停滯區、戰力暴增點
- **Loot** → 稀有度分布、保底計時器、背包壓力
- **有給檔案路徑** → 直接載入那個檔案，從內容推斷領域

沒有參數的話，問使用者要檢查哪個系統。

---

## Phase 2: 讀取資料檔

針對辨識出的領域，讀 `assets/data/` 和 `design/balance/` 裡相關的檔案。
每個讀過的檔案都要記下來，它們會出現在報告的 Data Sources 章節。

---

## Phase 3: 讀取設計文件

**先看 registry。** 如果 `design/registry/entities.yaml` 存在，要在讀
GDD 之前先讀它。它的 `constants` 和 `formulas` 章節放著跨 GDD 的具名數值
和輸出範圍，也就是平衡目標，已經整理好了，每一項都有 `source:`
GDD 和任何 `revised:` 日期：
```
Grep pattern="^  - name:" path="design/registry/entities.yaml" output_mode="content" -A 6
```
registry 列出的任何常數或公式（`constants:` 和 `formulas:` 區塊），預期值就取 registry 的；
這些是權威的跨文件數字，GDD 不准跟它矛盾。**如果 `design/registry/entities.yaml` 不存在，或是沒有項目**
（在 `/design-system` 填入之前，它出貨時是個空的 stub），就跳過這步，只用 GDD。

然後從 `design/gdd/` 讀這個系統的 GDD，了解預期的設計
目標、調校參數，和預期的數值範圍，registry 沒提供的部分都看這裡。
這是判斷「正確」行為的基準。按章節讀：
用 Grep 工具（pattern `^#`、content mode）找出需要的標題，再用 offset 和 limit 讀那幾段範圍。

如果資料檔是 FOUND，但兩個來源都沒有給這個領域的目標，
那些要對照目標來判斷的章節（Outliers Detected，以及領域有曲線時的 Progression
Analysis）就是 `NOT ASSESSED — NO DATA`。每一個都要指出缺了什麼，也就是
它去 `design/gdd/` 找的那份 GDD，以及 registry 是不存在還是空的，
並點名 `/design-system`，它兩個都會寫。

---

## Phase 4: 進行分析

**每個領域：把每個值拿去跟它的目標比。** 資料檔裡每個具名的值，
目標都從 Phase 3 取，也就是 registry 常數的 `value`、registry
公式的 `output_range`，或是 GDD 寫明的範圍，然後比對。超出目標的值
就是 Outliers Detected 裡的一列（`player_damage_base` 是 140，
目標 90–110）。哪裡都找不到目標的值，既不算在範圍內也不算
離群：把它列在 Values That Need Attention 底下，標成 `no stated range — not judged`。

然後執行各領域的專屬檢查：

**Combat 平衡：**
- 計算每個戰力層級所有武器／技能的 DPS
- 檢查每個層級的 time-to-kill
- 找出任何壓過其他所有選項的選項（嚴格更好）
- 檢查防禦選項會不會造成殺不死的狀態
- 驗證傷害類型／抗性的交互作用是否平衡

**Economy 平衡：**
- 把所有資源的產出源和消耗口連同流量速率畫出來
- 推算資源隨時間的累積
- 檢查有沒有無限資源迴圈
- 驗證金幣消耗口有沒有隨金幣產出一起放大
- 檢查有沒有任何物品永遠不值得買

**Progression 平衡：**
- 畫出 XP 曲線和戰力曲線
- 檢查停滯區（太久沒有有意義的成長）
- 檢查戰力暴增點（能力突然大跳）
- 驗證內容門檻有沒有對上預期的玩家戰力
- 檢查跳關／刷等策略會不會破壞預期的節奏

**Loot 平衡：**
- 計算取得每個稀有度層級的預期時間
- 檢查保底計時器的算式
- 驗證沒有任何戰利品在任何階段是完全沒用的
- 檢查背包壓力 vs 取得速率

---

## Phase 5: 輸出分析

```
## Balance Check: [System Name]

### Data Sources Analyzed
- [List of files read]

### Health Summary: [NOT ASSESSED / HEALTHY / CONCERNS / CRITICAL ISSUES]

### Outliers Detected
| Item/Value | Expected Range | Actual | Issue |
|-----------|---------------|--------|-------|

### Degenerate Strategies Found
- [Strategy description and why it is problematic]

### Progression Analysis
[Graph description or table showing progression curve health]

### Recommendations
| Priority | Issue | Suggested Fix | Impact |
|----------|-------|--------------|--------|

### Values That Need Attention
[Specific values with suggested adjustments and rationale]
```

依最嚴重的發現選 Health Summary，先符合的先贏：
- **CRITICAL ISSUES**：有退化策略（某個選擇壓過所有
  替代方案）、成長卡死或無法完成，或是經濟
  迴圈沒有消耗口
- **CONCERNS**：調校一輪就能修的離群值或曲線問題，而且
  沒有嚴重等級的發現
- **NOT ASSESSED**：沒東西可分析（上面的沒資料路徑）、某個
  需要目標的章節是 `NOT ASSESSED — NO DATA`，或是有值沒有明列範圍
  可以拿來判斷；要點名是哪一個。它的順位低於那兩個有發現的 verdict，因為
  量到的問題比缺口更能立刻採取行動，同時又高於 HEALTHY
- **HEALTHY**：每個值都對照明列的目標判斷過、沒有離群值、沒有
  退化策略、成長都在明列的目標之內

---

## Phase 6: 修正與驗證循環

呈現完報告後，用 `AskUserQuestion`：
- Prompt: "Balance check complete. What would you like to do next?"
- 選項：
  - `[A] Fix highest-priority issue now — walk me through it`
  - `[B] Save report to design/balance/balance-check-[system]-[date].md`
  - `[C] Stop here — I'll review the findings manually`

**當成 subagent 跑？** `game-designer` 會預先載入這個 skill，而 subagent 沒有
`AskUserQuestion`。回覆的結尾把問題和這三個選項
用短清單列出來，然後停：呼叫你的那一方會去問使用者，再把
答案傳回來。

選 [A]：
- 問先處理哪個問題（依優先順序參照 Recommendations 表的列）
- 引導使用者更新 `assets/data/` 裡相關的資料檔，或 `design/balance/` 裡的公式
- 每次修正後，主動提議重跑相關的平衡檢查，確認沒有引入新的離群值
- 如果修正改到 GDD 裡定義、或是 ADR 有引用的調校參數，提醒使用者：
  > "This value is defined in a design document. Run `/propagate-design-change [path]` on the affected GDD to find downstream impacts before committing."

選 [B]：
- 把報告寫到 `design/balance/balance-check-[system]-[date].md`（需要的話建立目錄）。[date] 用目前日期，格式是 YYYY-MM-DD。
- 確認檔案寫好了，然後以這句收尾："Re-run `/balance-check` after fixes to verify."

選 [C]：
- 摘要未解決的問題，然後以這句收尾："Re-run `/balance-check` after fixes to verify."
