---
name: inherit-legacy-style
description: 在舊專案上防止 AI 的風格漂移：掃描程式碼庫找出隱含的慣例，跟操作者一次一個地解決衝突，然後寫出可執行的 .ai-style-rules.md（Golden Files、命名規則、DONTs），並可選擇加上 CLAUDE.md hook。要讓 AI agent 接手手寫的舊程式碼庫，或要抽出專案沒寫下來的程式規則時使用。
metadata:
  origin: community
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, AskUserQuestion
---

# Inherit Legacy Style

在舊專案中防止 AI 程式碼風格漂移：沿著 4 個元架構維度掃描程式碼庫，找出隱含的慣例，跟使用者一次一個地解決衝突，再把共識固化成可執行的 `.ai-style-rules.md`。完全不限語言和框架。

## When to Activate

- 使用者輸入 `/inherit-legacy-style`
- 使用者提到要讓 AI 接手手寫的舊專案
- 使用者擔心 AI 產生的程式碼會「漂移」，偏離既有的專案慣例
- 使用者想把專案隱含的程式規則抽出來並明文化

## When to Use

需要保留舊專案風格、防止 AI 產生的風格漂移時用這個 skill。觸發條件見上面的 **When to Activate**。

## Prerequisites

- Git（建議；沒有 Git 的專案，增量模式會退回用檔案時間戳）
- 對專案根目錄有讀寫權限（會產生 `.ai-style-rules.md`，也可能產生 `CLAUDE.md`）

## Workflow

### Step 0 — Auto-Detect Mode

安靜地檢查專案根目錄有沒有 `.ai-style-rules.md`：

| 檔案存在嗎？ | 模式 |
|---|---|
| No | **Branch A — First-time Full-Scan** |
| Yes | **Branch B — Incremental Sniff** |

用一行話宣告模式然後繼續，絕對不要叫使用者來選。

### Branch A — First-time Full-Scan

**1. Measure scale, pick a scanning tier**

```bash
git ls-files | grep -cE '\.(js|ts|jsx|tsx|vue|py|go|rs|java|kt|rb|php|cs|swift|c|cpp|h)$'
```

| 層級 | 原始碼檔案數 | 策略 |
|---|---|---|
| Small | ≲ 50 | 每個原始檔都完整細讀 |
| Medium | 50–500 | 基礎設施層完整讀；商業邏輯層每個維度抽樣 2–3 個 |
| Large | ≳ 500 | 嚴格抽樣加預算上限；先看 `--stat` 摘要，再針對性閱讀 |

**2. Scan along 4 dimensions**

1. **File Anatomy** — 檔案內的宣告順序（imports → types → main logic → helpers → export）
2. **State & Control Flow** — 非同步狀態、分頁、flag 的命名慣例
3. **Infrastructure** — 橫切用的工具放在哪（interceptor、formatter、middleware）
4. **Error Handling** — try/catch、全域 interceptor 還是回傳 Result；null 檢查的習慣

**3. Apply signal-threshold noise reduction**

打斷使用者之前，先評估訊號強度：

- **弱訊號** → 自動壓下：少數派 <5% 而且數量 <10 → 多數派勝出，少數派進 DONTs
- **強訊號** → 拷問：分布接近對半，或在核心維度上有語意分歧
- **小專案例外**：原始碼 ≲50 個時，「3 比 2」不算多數 → 要拿來拷問

**4. Resolve conflicts one at a time (Grilling Protocol)**

每個強訊號衝突，只提出一個問題，附 4 個選項：

> Evidence: `pathA` uses style X, `pathB` uses style Y
> WARNING: Risk: mixing both fractures the project style
> Choose: `1` follow X  `2` follow Y  `3` this is evolution, update rules  `4` I have a new rule

停下來等使用者回答，再處理下一個衝突。絕對不要一次堆好幾個問題。

**5. Generate `.ai-style-rules.md`**，必須包含三個區段：
- **[Golden Files]** — 真實的範例路徑，並註明各自示範了什麼
- **[Naming & State-Control Rules]** — 具體、可檢查的慣例
- **[DONTs]** — 不能擴散出去的反模式

**6. Install the persistent hook**

問使用者要多強的執行力道（用 `AskUserQuestion`）：

| 選項 | 機制 |
|---|---|
| **1** Soft hook（建議） | 在專案的 `CLAUDE.md` 寫入 `@.ai-style-rules.md` 引用 |
| **2** Hard hook | Soft hook 再加上 `settings.json` 裡的 `PreToolUse[Write\|Edit\|MultiEdit]` Hook |
| **3** No hook | 保留規則檔，使用者自己手動引用 |

### Branch B — Incremental Sniff

1. 讀既有的 `.ai-style-rules.md`；如果裡面有 commit 指紋，用 `git diff <last_hash> HEAD --stat` 找出差異範圍
2. 讀最近的 Git 變更（`git log -3 --stat` → 視需要檢查可疑的檔案）
3. diff 太大（上百個檔案以上）時：只看 `--stat` 摘要，並抽樣變動最大的部分
4. 把新程式碼對照已記錄的規則 → 有衝突就走 Grilling Protocol
5. 在 `.ai-style-rules.md` 結尾追加演進紀錄（絕對不要覆蓋舊規則）

### Per-Turn Enforcement

當 `.ai-style-rules.md` 在 context 裡（透過 CLAUDE.md 載入），每個寫程式的任務都必須在推理過程一開頭先做一份**合規聲明**，說明要跟隨哪個範例，以及要避開哪些 DONTs。

## How It Works

這個 skill 會依 `.ai-style-rules.md` 有沒有存在，自動判斷是第一次執行還是增量執行：

- **First-time（Branch A）** — 衡量專案規模，沿著 4 個元架構維度（File Anatomy、State & Control Flow、Infrastructure、Error Handling）掃描程式碼庫，用訊號門檻降噪壓掉弱衝突，跟使用者一次一個地解決強訊號衝突，產生包含 Golden Files / Naming Rules / DONTs 的 `.ai-style-rules.md`，並提供可選的強制執行 hook。
- **Incremental（Branch B）** — 讀既有規則，檢查最近的 Git diff 有沒有新的或衝突的樣式，對找到的任何衝突跑同一套一次一個的拷問流程，並追加演進紀錄，不覆蓋既有規則。
- **Per-Turn Enforcement** — 透過 `CLAUDE.md` 掛上 hook 之後，每個寫程式的任務都以一份合規聲明開頭，說明跟隨的範例和避開的 DONTs。

## Output Specification

- 專案根目錄的 `.ai-style-rules.md`（標頭有 commit 指紋和規模層級）
- 可選：帶有 `@.ai-style-rules.md` 引用的 `CLAUDE.md`
- 演進紀錄以 `### [YYYY-MM-DD] Style Evolution Log` 條目的形式追加

## Anti-Patterns

- FAIL: 不准跳過規模衡量這一步，30 個檔案的專案用抽樣會「餓死」，5,000 個檔案的 repo 全掃會爆掉
- FAIL: 不准一次堆好幾個衝突問題，拷問一定是一次一個
- FAIL: 增量模式下不准覆蓋舊規則，一律追加演進紀錄
- FAIL: 不准沒問就預設用「hard hook」，執行力道由使用者決定
- FAIL: 不准評斷語法或技術棧的好壞，這個 skill 只對齊元架構
- FAIL: 不准照抄範例檔案裡的 bug，要重用結構，並標出缺陷

## Best Practices

- 掃描之前，用一行話宣告偵測到的模式（第一次 vs 增量）和規模層級
- 大專案先讀 `--stat` 摘要，再對可疑的檔案做針對性的 `Read`
- 讓訊號門檻去處理雜訊，843 比 8 的命名分歧應該自動解決，不用打斷使用者
- 對訊號強度拿不準時，傾向於問
- CLAUDE.md 的 soft hook（`@.ai-style-rules.md`）通常就夠了；只有使用者想要機械式強制執行時才用 hard hook

## Related Skills

- `init` — 初始化新的 CLAUDE.md，附上程式碼庫文件
- `code-review` — 檢查 diff 的正確性與風格問題
- `simplify` — 檢查程式碼有沒有可重用和簡化的地方

## Examples

1. **First-time onboarding**
   - 使用者：「幫我讓 AI 接手這個舊程式碼庫，但不要改它的風格。」
   - 動作：跑 Branch A 全掃 → 衡量規模 → 掃 4 個維度 → 拷問衝突 → 產生 `.ai-style-rules.md` → 提供 hook 強度選項（soft/hard/none）。

2. **Incremental update after team changes**
   - 使用者：「我們加了一個新模組，現有的風格規則要保持不變。」
   - 動作：跑 Branch B 增量偵測 → 把 Git 差異對照已記錄的規則 → 拷問任何新衝突 → 追加演進紀錄，不覆蓋。

3. **Enforcing DONTs via CLAUDE.md**
   - 使用者：「確保所有新程式碼都跟專案的規則保持一致。」
   - 動作：安裝 soft hook → `.ai-style-rules.md` 每個 session 自動載入 → 每個寫程式的任務都以合規聲明開頭，重用範例的樣式並避開 DONTs。
