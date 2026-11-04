---
name: codex-review
description: "用 headless 模式的 OpenAI Codex CLI 做獨立的 code review。針對最近的改動、PR、commit 或整個 app，從不同模型家族（目前的 Codex 模型）取得第二意見，涵蓋 bug、迴歸、安全、資料一致性、UX/state bug、效能風險和測試缺口。把依嚴重程度排序的報告存到 .jez/reviews/。觸發詞：'codex review', 'review with codex', 'independent code review', 'what does codex think', 'get codex to review'。"
compatibility: Designed for Claude Code (or similar products)
---

# Codex Review

透過 OpenAI Codex CLI（`codex review`）做獨立的 code review。價值在於拿到跟寫這份程式碼的模型**不同模型家族**的第二意見，Codex 能抓到 Claude 因為作者偏見而漏掉的東西。

跟 `brains-trust`（通用的多模型意見）互補。這個 skill 比較專門：認得 git、用調校過的 review prompt、把輸出存成結構化的報告。

## 什麼時候用

- 有意義的改動之後、commit 或上線之前
- 開 PR 之前，找一個獨立的 reviewer 自我 review
- 覺得哪裡怪怪的，但說不出來是什麼
- 對積極開發中的專案，定期做整個 app 的 review
- 使用者明確要求「獨立」或「第二意見」的 review 時

**不要用在：**
- 瑣碎的改動（錯字、一行修正）
- 研究問題或架構討論：改用 `brains-trust`
- 自動修問題：這只是建議性質

## 前置檢查

1. 確認有安裝 Codex CLI：
   ```bash
   which codex
   ```
   沒有的話：告訴使用者去安裝（macOS 用 `brew install codex`，或見 https://github.com/openai/codex），然後停下來，不要繼續。

2. 確認驗證：第一次呼叫 `codex review` 時，沒登入就會明確失敗。發生這種情況，指示使用者執行 `codex login`，然後停下來。

## 決定範圍

依使用者要求的內容選範圍參數：

| 使用者意圖 | 參數 |
|---|---|
| 「codex review」/「review the app」/「full review」/ 預設 | 不加參數（review 目前 HEAD 的整個 app） |
| 「review my changes」/「review what I just did」/「review uncommitted」 | `--uncommitted` |
| 「review this branch vs main」/「review the PR」 | `--base main`（或他們指定的 branch） |
| 「review commit abc123」 | `--commit abc123` |

**預設是整個 app 的 review。**單純說「codex review」沒有任何限定詞，就是 review HEAD 的整個 codebase，不只是未 commit 的改動。只有在使用者明確提到他們最近/未 commit 的工作時，才用 `--uncommitted`。

不明確就問一次。commit 或 branch 不要用猜的。

## 執行 review

標準的 review prompt 放在這個 skill 旁邊的 `prompt.md`。用 stdin 傳進去，避免 shell 跳脫的問題：

```bash
mkdir -p .jez/reviews
TS=$(date +%Y-%m-%d-%H%M)
OUT=".jez/reviews/codex-${TS}.md"
SKILL_DIR="$(dirname "$0")"  # or use the skill's absolute path

# Example: uncommitted changes
cat "${SKILL_DIR}/prompt.md" | codex review --uncommitted - 2>&1 | tee "$OUT"
```

其他範圍：

```bash
# Vs base branch
cat prompt.md | codex review --base main - 2>&1 | tee "$OUT"

# Specific commit
cat prompt.md | codex review --commit abc123 - 2>&1 | tee "$OUT"

# Current HEAD (no scope flag)
cat prompt.md | codex review - 2>&1 | tee "$OUT"
```

diff 很大的話，`codex review` 可能要跑好幾分鐘。讓它跑完。

## 替使用者整理摘要

Codex 跑完之後：

1. 印出輸出路徑：`Report saved to .jez/reviews/codex-<timestamp>.md`
2. 讀存下來的報告，抽出最重要的發現（**Critical** 和 **High** 底下的所有項目）
3. 直接顯示在對話裡，保留 file:line 的參照
4. 主動提議處理特定的發現：「要我修 `auth.ts:42` 的 SQL injection 嗎？」

## 規則

- **只是建議。**絕對不要自動套用 Codex 的建議。讀過發現、跟使用者討論，經過他們同意再修。
- **不要把 Claude 的推理洩漏進 prompt。**`prompt.md` 刻意保持中立，Codex review 的是程式碼，不是 Claude 對程式碼的描述。獨立性就是重點。
- **存到 `.jez/reviews/`**，絕對不要存到 `.claude/`（受保護的目錄）。
- **每次執行一份報告。**不要覆寫，時間戳記讓每次執行都是獨一無二的，使用者可以拿來比較。
- **如實報告 Codex 真正發現的東西。**不要淡化、不要加評論、不要跳過你不同意的發現。你認為 Codex 有哪裡錯了，先顯示 Codex 說了什麼，再以你自己的意見說出來。

## 驗證

這個 skill 有在運作的標準：
- 前置檢查能正確偵測缺少 `codex` 執行檔
- 依使用者意圖選對範圍參數
- 報告檔出現在 `.jez/reviews/`，時間戳記合理
- 檔案包含依嚴重程度排序、附 file:line 參照的發現
- Claude 把最重要的發現呈現出來，而不是自動修掉
