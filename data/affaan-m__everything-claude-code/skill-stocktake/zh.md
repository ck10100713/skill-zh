---
name: skill-stocktake
description: "稽核 Claude skill 和指令的品質時使用。支援 Quick Scan（只看有變動的 skill）和 Full Stocktake 兩種模式，以依序執行的 subagent 分批評估。"
metadata:
  origin: ECC
---

# skill-stocktake

Slash command（`/skill-stocktake`），用品質檢查清單加上 AI 的整體判斷，稽核所有 Claude skill 和指令。支援兩種模式：針對最近有變動的 skill 做 Quick Scan，以及做完整檢視的 Full Stocktake。

## 範圍

這個指令的目標路徑**相對於執行它的目錄**：

| 路徑 | 說明 |
|------|-------------|
| `~/.claude/skills/` | 全域 skill（所有專案） |
| `{cwd}/.claude/skills/` | 專案層級 skill（目錄存在的話） |

**階段 1 一開始，指令會明確列出找到並掃描了哪些路徑。**

名為 `.trash` 的目錄在兩種掃描模式中都會被排除：已封存的 skill 不算現行清單的一部分。如果較舊的 `results.json` 裡有 `.trash` 項目，先用下面的快取初始化方式開始新的 Full Stocktake，再恢復 Quick Scan。一般的儲存只會合併項目，不會移除已封存的紀錄。

### 指定特定專案

要納入專案層級的 skill，從該專案的根目錄執行：

```bash
cd ~/path/to/my-project
/skill-stocktake
```

如果專案沒有 `.claude/skills/` 目錄，就只會評估全域的 skill 和指令。

## 模式

| 模式 | 觸發方式 | 耗時 |
|------|---------|---------|
| Quick Scan | `results.json` 存在（預設） | 5–10 分鐘 |
| Full Stocktake | `results.json` 不存在，或 `/skill-stocktake full` | 20–30 分鐘 |

這些 shell script 需要 `PATH` 上有 Bash、Node.js 和 `jq`。

**結果快取：** `~/.claude/skills/skill-stocktake/results.json`

## Quick Scan 流程

只重新評估上次執行後有變動的 skill（5–10 分鐘）。

1. 讀取 `~/.claude/skills/skill-stocktake/results.json`
2. 執行：`bash ~/.claude/skills/skill-stocktake/scripts/quick-diff.sh \
         ~/.claude/skills/skill-stocktake/results.json`
   （專案目錄會從 `$PWD/.claude/skills` 自動偵測；只有需要時才明確傳入）
3. 如果輸出是 `[]`：回報「No changes since last run.」然後停止
4. 只對那些有變動的檔案，用同樣的階段 2 準則重新評估
5. 沒有變動的 skill，沿用先前的結果
6. 只輸出差異
7. 執行：`bash ~/.claude/skills/skill-stocktake/scripts/save-results.sh \
         ~/.claude/skills/skill-stocktake/results.json <<< "$EVAL_RESULTS"`

## Full Stocktake 流程

### 階段 1：盤點

把這整個區塊放在**同一次 Bash 呼叫**中執行。它會印出給 agent 看的盤點結果，而且只有在沒有未完成的執行可以恢復時，才會初始化新的完整執行：

```bash
(
  set -euo pipefail
  SCAN_JSON=$(bash ~/.claude/skills/skill-stocktake/scripts/scan.sh)
  printf '%s\n' "$SCAN_JSON"
  RESULTS_JSON=~/.claude/skills/skill-stocktake/results.json

  CACHE_STATUS=""
  if [[ -f "$RESULTS_JSON" ]]; then
    CACHE_STATUS=$(jq -r '.batch_progress.status // ""' "$RESULTS_JSON")
  fi
  if [[ "$CACHE_STATUS" == "in_progress" ]]; then
    RESUMED_RESULTS=$(jq --slurpfile saved "$RESULTS_JSON" '
      . as $inventory | $saved[0]
      | .skills = (.skills | to_entries
        | map(.key = (.value.path // .key))
        | map(select(. as $entry
          | $entry.value.mtime != null
            and any($inventory.skills[];
              .path == $entry.key and .mtime == $entry.value.mtime)))
        | from_entries)
      | .mode = "full"
      | .batch_progress = {
          total: ($inventory.skills | length),
          evaluated: (.skills | length), status: "in_progress"
        }
    ' <<< "$SCAN_JSON")
    bash ~/.claude/skills/skill-stocktake/scripts/save-results.sh \
      "$RESULTS_JSON" --replace <<< "$RESUMED_RESULTS"
  else
    INITIAL_RESULTS=$(printf '%s\n' "$SCAN_JSON" | jq '{
      mode: "full", skills: {},
      batch_progress: {total: (.skills | length), evaluated: 0, status: "in_progress"}
    }')
    bash ~/.claude/skills/skill-stocktake/scripts/save-results.sh \
      "$RESULTS_JSON" --replace <<< "$INITIAL_RESULTS"
  fi
)
```

這支 script 會列舉 skill 檔案、擷取 frontmatter，並收集 UTC 的 mtime。專案目錄會從 `$PWD/.claude/skills` 自動偵測；只有需要時才明確傳入。把 script 輸出的掃描摘要和盤點表呈現出來：

```
Scanning:
  ✓ ~/.claude/skills/         (17 files)
  ✗ {cwd}/.claude/skills/    (not found — global skills only)
```

| Skill | 7d use | 30d use | Description |
|-------|--------|---------|-------------|

使用次數來自選用的 `~/.claude/observations.jsonl` 檔案（可用 `SKILL_STOCKTAKE_OBSERVATIONS` 覆寫），Claude Code 預設不會建立它。檔案不存在時，`use_7d` 和 `use_30d` 是 JSON `null`；在盤點表和摘要表中要顯示成 **unmeasured**。數值 `0` 表示檔案存在，但那段期間內沒有符合的 Read 觀測紀錄。缺少使用資料絕對不能當作淘汰 skill 的證據。

`--replace` 會寫入完整的快取快照。新的執行從空的評估開始；恢復的執行則只在某個路徑仍然有效、而且儲存的非 null mtime 跟最新盤點相符時，才保留儲存的評估。有變動的 skill 和沒有 mtime 的項目需要重新評估。它會移除已封存/已刪除的項目，而且即使沒有新的批次要跑，也會刷新進度計數。既有以名稱為 key 的項目，會依儲存的 `path` 正規化。恢復時絕對不要使用空的初始化 payload。後續的分段、完成更新和 Quick Scan 都必須省略 `--replace`，這樣才會合併進目前的執行，不會丟掉先前的結果。

### 階段 2：品質評估

啟動一個 Agent 工具的 subagent（**general-purpose agent**），把階段 1 實際輸出的 JSON 和下面的檢查清單交給它。要把盤點的值直接複製進 prompt 裡；shell 變數不會帶進 Agent 呼叫。要附上完整的盤點內容供重疊檢查用，並明確指出目前這一批要評估的路徑。不要送出字面上的盤點或檢查清單 placeholder。

Subagent 會讀取每個分配到的 skill、套用檢查清單，並回傳一個 JSON 物件，其中的 `skills` map 以盤點的路徑為 key。每個項目包含它的 `path`、掃描到的 `mtime`、`verdict` 和獨立完整的 `reason`。所有批次都要使用相同的路徑 key，這樣合併結果時才不會讓同名的不同 skill 互相覆蓋。

**分段建議：** 每次 subagent 呼叫處理約 20 個 skill，讓 context 維持在可管理的範圍。每個分段完成後，用 `mode: "full"` 和 `batch_progress: {total, evaluated, status: "in_progress"}` 把它回傳的 `skills` map 包起來。`total` 設為盤點的總數，`evaluated` 設為累計已評估的不重複路徑數，包含已儲存的批次。把這個 JSON 指派給 `CHUNK_RESULTS`，並在**與該指派相同的 Bash 呼叫**中執行下面的指令：

```bash
bash ~/.claude/skills/skill-stocktake/scripts/save-results.sh \
  ~/.claude/skills/skill-stocktake/results.json <<< "$CHUNK_RESULTS"
```

所有 skill 都評估完之後，進入階段 3 之前，先把完成狀態存下來：

```bash
(
  set -euo pipefail
  RESULTS_JSON=~/.claude/skills/skill-stocktake/results.json
  COMPLETED_RESULTS=$(jq -e '
    if (.skills | length) == .batch_progress.total then
      {skills: {}, mode: "full", batch_progress: (.batch_progress + {
        evaluated: (.skills | length), status: "completed"
      })}
    else error("Inventory still has unevaluated skills") end
  ' "$RESULTS_JSON")
  bash ~/.claude/skills/skill-stocktake/scripts/save-results.sh \
    "$RESULTS_JSON" <<< "$COMPLETED_RESULTS"
)
```

**恢復偵測：** 如果啟動時發現 `status: "in_progress"`，先執行階段 1，把儲存的結果跟最新盤點對帳，再只評估那些不在對帳後 `skills` map 裡的路徑。如果一個都不剩，就立刻存下完成狀態。已完成的評估只會保留給仍然存在、而且 mtime 相符且非 null 的路徑；新的或有變動的 skill，以及沒有 mtime 的項目，都需要評估。

每個 skill 都依這份檢查清單評估：

```
- [ ] Content overlap with other skills checked
- [ ] Overlap with MEMORY.md / CLAUDE.md checked
- [ ] Freshness of technical references verified (use WebSearch if tool names / CLI flags / APIs are present)
- [ ] Usage frequency considered when measured; missing observations marked unmeasured, not treated as zero
```

判定準則：

| Verdict | 意義 |
|---------|---------|
| Keep | 有用而且是最新的 |
| Improve | 值得保留，但需要具體的改進 |
| Update | 引用的技術已經過時（用 WebSearch 驗證） |
| Retire | 品質低、過時，或成本不對等 |
| Merge into [X] | 跟另一個 skill 有大量重疊；要指出合併的目標 |

評估是**整體的 AI 判斷**，不是數字評分表。指引的面向：
- **可執行性**：有程式碼範例、指令或步驟，讓你能立刻動手
- **範圍適配**：名稱、觸發條件和內容一致，不會太廣或太窄
- **獨特性**：價值無法被 MEMORY.md / CLAUDE.md / 另一個 skill 取代
- **時效性**：引用的技術在目前環境能用

**Reason 品質要求**：`reason` 欄位必須獨立完整，而且足以支撐決策：
- 絕對不要只寫「unchanged」，一定要重述核心證據
- 對於 **Retire**：說明（1）發現了什麼具體缺陷、（2）有什麼東西涵蓋了同樣的需求
  - 不好：`"Superseded"`
  - 好：`"disable-model-invocation: true already set; superseded by continuous-learning-v2 which covers all the same patterns plus confidence scoring. No unique content remains."`
- 對於 **Merge**：指出目標，並描述要整合哪些內容
  - 不好：`"Overlaps with X"`
  - 好：`"42-line thin content; Step 4 of chatlog-to-article already covers the same workflow. Integrate the 'article angle' tip as a note in that skill."`
- 對於 **Improve**：描述需要的具體變更（哪個段落、什麼動作、有需要的話寫目標大小）
  - 不好：`"Too long"`
  - 好：`"276 lines; Section 'Framework Comparison' (L80–140) duplicates ai-era-architecture-principles; delete it to reach ~150 lines."`
- 對於 **Keep**（Quick Scan 中只有 mtime 變動）：重述原本判定的理由，不要寫「unchanged」
  - 不好：`"Unchanged"`
  - 好：`"mtime updated but content unchanged. Unique Python reference explicitly imported by rules/python/; no overlap found."`

### 階段 3：摘要表

| Skill | 7d use | Verdict | Reason |
|-------|--------|---------|--------|

### 階段 4：整併

1. **Retire / Merge**：向使用者確認之前，針對每個檔案提出詳細的理由：
   - 發現了什麼具體問題（重疊、過時、參照損壞等）
   - 有什麼替代方案涵蓋同樣的功能（Retire：哪個現有的 skill/規則；Merge：目標檔案和要整合的內容）
   - 移除的影響（有哪些相依的 skill、MEMORY.md 參照或工作流程會受影響）
2. **Improve**：提出具體的改進建議並附上理由：
   - 要改什麼、為什麼（例如「從 430 行精簡到 200 行，因為 X/Y 段落跟 python-patterns 重複」）
   - 由使用者決定要不要動手
3. **Update**：呈現更新後的內容，並附上查證過的來源
4. 檢查 MEMORY.md 的行數；超過 100 行就提出壓縮建議

## 結果檔 Schema

`~/.claude/skills/skill-stocktake/results.json`：

**`evaluated_at`**：必須設為評估完成當下的實際 UTC 時間。用 Bash 取得：`date -u +%Y-%m-%dT%H:%M:%SZ`。絕對不要用 `T00:00:00Z` 這種只有日期的近似值。

```json
{
  "evaluated_at": "2026-02-21T10:00:00Z",
  "mode": "full",
  "batch_progress": {
    "total": 80,
    "evaluated": 80,
    "status": "completed"
  },
  "skills": {
    "~/.claude/skills/skill-name/SKILL.md": {
      "path": "~/.claude/skills/skill-name/SKILL.md",
      "verdict": "Keep",
      "reason": "Concrete, actionable, unique value for X workflow",
      "mtime": "2026-01-15T08:30:00Z"
    }
  }
}
```

## 備註

- 評估是盲測的：不論來源（ECC、自己寫的、自動擷取的），所有 skill 都套用同一份檢查清單
- 封存/刪除的操作一律需要使用者明確確認
- 不依 skill 的來源分流判定
