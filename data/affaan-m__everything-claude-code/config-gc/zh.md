---
name: config-gc
description: 為你的 Claude Code 設定做垃圾回收。定期掃描 ~/.claude（skill、記憶、hook、權限、MCP 伺服器、快取）裡多餘、過期、孤立或低價值的項目，然後帶使用者逐項確認刪除。適用於使用者說「clean up my config」、「config GC」、「too many skills」、「audit my setup」、「my .claude is bloated」，或要求定期設定檢視時。
metadata:
  origin: ECC
---

# Config GC — Garbage Collection for Claude Code Setups

借用 runtime 垃圾回收的概念：定期掃描不再被引用、重複、過期或低價值的物件，並回收空間。關鍵差別：**這裡的回收需要人在迴圈中。絕對不准自己決定刪除。**

## When to Activate

- 使用者要求清理、稽核或精簡他們的 Claude Code 設定
- 使用者抱怨 skill 太多、hook 太吵，或 session 啟動很慢
- 每月/定期的設定檢視到期了
- 安裝了大型 skill 包（例如這個 repo）之後，用來整理跟既有設定重疊的部分

**不要**在這些情況啟用：清理專案原始碼（那是重構）、清除對話記錄，或是解除安裝 Claude Code 本身。

## Design Philosophy

1. **只增不減的設定會漏。** Skill、記憶檔案、hook 和權限項目只會一直新增。沒有定期檢視，就會悄悄腐爛。
2. **定期稽核勝過一次性大掃除。** 大約每 30 天掃一次，每次提出一小批候選項目。
3. **每個管道有自己的策略。** 每一種累積類型（skill、hook、權限……）都有自己的過期訊號，不要到處套用同一條規則。
4. **先做軟刪除。** 改名成 `.disabled` > 移到 `~/.claude/_gc_trash/` > 真正刪除。永遠保留復原路徑。
5. **強制人在迴圈中。** 每個候選項目都有自己的 `[y/n/skip]` 確認。沒有「全部同意」的捷徑。
6. **留紀錄。** 每次 GC 都會附加到 `~/.claude/gc_log.md`：動了什麼、為什麼、怎麼復原。

## Scan Channels

| # | Channel | Path | Staleness / redundancy signals |
|---|---------|------|--------------------------------|
| 1 | Skills | `~/.claude/skills/*/` | 名稱高度重疊；最近的對話記錄裡從沒被觸發過；領域跟使用者實際工作不符；SKILL.md 損壞或是空的 |
| 2 | Memory | `~/.claude/**/memory/*.md` + 它的索引 | 同一個主題有多個索引項目；內容跟較新的項目矛盾；日期已經過了；沒列在索引裡的孤立檔案；少於 100 字、應該合併的片段 |
| 3 | Hooks | `~/.claude/hooks/` + settings | 磁碟上有、但沒有任何 hook 設定引用的 script；被重寫版本取代的舊版本 |
| 4 | Permissions | `settings.json` / `settings.local.json` 裡的 `permissions.allow` | 重複的項目；已經被萬用字元涵蓋的具體項目（例如允許 `Bash(*)` 時的 `Bash(git push)`）；過去實驗留下的一次性授權 |
| 5 | MCP servers | `~/.claude.json` 或專案的 `.mcp.json` | 連不上的伺服器；功能重複的；很久沒用的 |
| 6 | Scheduled reminders / jobs | 使用者存放它們的任何地方 | 已觸發超過 30 天的一次性任務；目標 script 已不存在的工作 |
| 7 | Project history | `~/.claude/projects/*/` | 過期的交接快照；被較新狀態取代的 session 紀錄 |
| 8 | Runtime caches | `cache/`、`file-history/`、`logs/`、`shell-snapshots/` | 依大小和 mtime 排序；提出超過 30 天且很大的項目 |

## Workflow

1. **掃描**所有管道（或使用者指名的子集）。收集候選項目，附上：路徑、管道、標記它的訊號、大小、最後修改時間。
2. **排序**依信心程度（損壞/孤立 = 高；只是舊 = 低），以編號表格呈現。每次最多約 20 個候選項目，GC 是定期做的，不是窮盡式的。
3. **逐一確認。** 對每個候選項目顯示證據，然後問 `[y/n/skip]`。使用者隨時可以停。
4. **軟刪除已確認的項目**：skill/hook 優先改名成 `.disabled`，檔案則移到 `_gc_trash/<date>/`。權限項目存在 JSON 裡（不能寫註解）：先備份 settings 檔案，把每個被移除的項目原封不動記到 `gc_log.md`，再用 `jq` 從 `allow` 陣列移除。只有使用者明確要求時才硬刪除。
5. **記錄**這次執行到 `~/.claude/gc_log.md`：時間戳記、處理的項目、復原指示。
6. **回報**：回收的大小、仍然健康的管道、建議的下次檢視日期。

## Example Scan Commands

孤立的 hook script（管道 3）：磁碟上有、但沒有 hook 設定引用的 script：

```bash
for f in ~/.claude/hooks/*; do
  name=$(basename "$f")
  grep -rq "$name" ~/.claude/settings.json ~/.claude/settings.local.json 2>/dev/null \
    || echo "ORPHAN: $f"
done
```

多餘的權限項目（管道 4）：重複的，以及被萬用字元蓋掉的具體授權：

```bash
jq -r '.permissions.allow[]' ~/.claude/settings.local.json | sort | uniq -d
if jq -e '.permissions.allow | index("Bash(*)")' ~/.claude/settings.local.json >/dev/null; then
  jq -r '.permissions.allow[]' ~/.claude/settings.local.json \
    | grep '^Bash(' | grep -vF 'Bash(*)'
fi
```

最大的過期快取（管道 8）：用 `du -k`，不用只有 GNU 才有的 `find -printf`，所以 macOS/BSD 也能跑：

```bash
find ~/.claude/file-history ~/.claude/shell-snapshots -type f -mtime +30 \
  -exec du -k {} + 2>/dev/null | sort -rn | head -20
```

帶復原路徑的軟刪除（日期只取一次，這樣紀錄才不會跟目錄對不起來）：

```bash
gc_date=$(date +%Y-%m-%d)
mkdir -p ~/.claude/_gc_trash/$gc_date
mv ~/.claude/skills/dead-skill ~/.claude/_gc_trash/$gc_date/
echo "$(date -Iseconds) moved skills/dead-skill -> _gc_trash/$gc_date/ (undo: mv back)" >> ~/.claude/gc_log.md
```

移除已確認多餘的權限項目（JSON 不能寫註解，所以先備份、記錄，再編輯）：

```bash
cp ~/.claude/settings.local.json ~/.claude/settings.local.json.bak
echo "$(date -Iseconds) removed permission entry: Bash(git push) (undo: restore from .bak or re-add)" >> ~/.claude/gc_log.md
jq '.permissions.allow -= ["Bash(git push)"]' ~/.claude/settings.local.json.bak \
  > ~/.claude/settings.local.json
```

## Anti-Patterns

- **整批核准。** 問「刪除全部 15 個？[y/n]」就違背設計了。一個項目，一個決定。
- **第一輪就硬刪除。** 如果沒有 `_gc_trash/` 的副本或 `.disabled` 改名，就是做錯了。
- **把「舊」當成「死」。** 60 天沒碰的 skill 可能是季節性的（報稅季、季度檢討）。年齡是訊號，不是判決，所以才要人來確認。
- **用截斷的方式清理記憶。** 合併兩個互相矛盾的記憶檔案，要先讀完兩個、保留較新的事實，不是刪掉比較長的那個。
- **動 `~/.claude`（或專案的 `.claude/`）以外的任何東西。** Config GC 絕對不會跑進原始碼目錄。

## Best Practices

- 大量新增之後就跑，不要只照日曆：裝了一個 50 個 skill 的包，正是跟既有 skill 重疊出現的時候。
- 兩個 skill 重疊時，優先停用觸發描述比較弱的那個，它多半本來就從沒被觸發過。
- 權限清理是每分鐘價值最高的管道：多餘的 allow 項目會讓安全審查更困難。
- `gc_log.md` 要永遠留著。它很小，而「我什麼時候停用那個 hook、為什麼」這種問題，比你想的更常出現。

## Related Skills

- `skill-stocktake`：稽核 skill 的*品質*；config-gc 稽核 skill 的*存在*。對撐過 GC 的 skill 再跑 stocktake。
- `workspace-surface-audit`：加法的對應物，建議該裝什麼。config-gc 是同一個生命週期中減法的那一半。
- `configure-ecc`：用它安裝完 skill 之後，執行 config-gc 來整理跟你原有設定重疊的地方。
- `continuous-learning`：產生這個 skill 之後會稽核的記憶檔案。
- `security-review`：很適合搭配權限管道使用。
