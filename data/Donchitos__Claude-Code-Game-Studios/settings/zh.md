---
name: settings
description: "檢視或修改專案設定：合併後的實際生效值，或是設在 project.local.yaml 的本機設定。"
argument-hint: "[key | key=value | --local key=value]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(bash "*/.claude/skills/settings/../../hooks/yaml-helper.sh" resolve_setting *), Bash(bash "*/.claude/skills/settings/../../hooks/yaml-helper.sh" get_yaml_key *), Bash(bash "*/.claude/skills/settings/../../hooks/yaml-helper.sh" validate_yaml_enum *), Bash(bash "*/.claude/skills/settings/../../hooks/yaml-helper.sh" validate_enum_value *), Bash(bash "*/.claude/skills/settings/../../hooks/yaml-helper.sh" is_locally_overridable *), Bash(bash .claude/scripts/config-set.sh *), Bash(grep -B14 '^> ### RESERVED' .claude/docs/effects-map.md), Bash(grep -E '^## ')
model: sonnet
---

# /settings — view or change project config

管理 `project.yaml`（全團隊共用的設定，會 commit）和 `project.local.yaml`
（每位開發者自己的覆寫，被 gitignore）。用這個 skill 來查看目前的
設定，或是修改設定，不用手動編輯 YAML。

**自動化模式**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。Phase 4 和
Phase 5 的核准關卡遵循 `.claude/docs/automation-modes.md` 裡的模式。**注意**：
寫入 `project.yaml` 屬於 `schema_changes` 決策（預設的
`automation_always_ask` 類別），所以即使在 `autonomous` 模式下，`/settings` 也會確認設定的寫入，
除非使用者已經把 `schema_changes` 從他們的一律詢問清單裡移除。

## Phase 0: Parse Arguments

判斷使用者呼叫的是四種形式中的哪一種：

| Form | Mode |
|------|------|
| `/settings` (no args) | **View-all** (Phase 2) |
| `/settings <key>` (single arg, no `=`) | **View-one** (Phase 3) |
| `/settings <key>=<value>` (single arg with `=`) | **Set-yaml** (Phase 4) |
| `/settings --local <key>=<value>` (`--local` prefix) | **Set-local** (Phase 5) |

對 Set-yaml 和 Set-local 來說，`<key>` 是用點分隔的 YAML 路徑（例如
`modes.review_mode`、`testing.strict.logic`），`<value>` 是新的值。

**空運算元驗證：** 把 `key=value` 運算元依 `=` 切開之後，
如果 `<key>` 或 `<value>` 任何一個是空的，就是格式錯誤，轉到
Phase 6（用法），不要嘗試寫入。這條規則在 Set-yaml 和 Set-local 的路由都適用：
對 `--local`，先去掉 `--local` token，再用同樣的方式檢查剩下的運算元（所以 `/settings --local =foo`
和 `/settings --local key=` 都會到 Phase 6）。

任何不符合上面四種形式的東西 → Phase 6（用法）。

## Phase 1: Load Helper

四個子指令都需要 `yaml-helper.sh`。每一次 helper 呼叫都當成獨立的
單純指令來跑：

```bash
bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" <helper call>
```

`<helper call>` 是下面各個 phase 點名的那個函式，例如
`resolve_setting modes.review_mode` 或 `validate_yaml_enum project.yaml`。
helper 會自己切到專案根目錄，所以當 session 是在子資料夾啟動時，那些 `project.yaml` 和
`project.local.yaml` 參數也能被解析，而且它會保留函式的結束狀態碼。`is_locally_overridable`
也會印出它的 `0` 或 `1`。要完全照範例的樣子執行：不要 `source`
那個檔案、不要包在 `cd ... &&` 裡，也不要加 `; echo $?`。這個 skill 只預先核准
單純的形式，複合指令每次都會問使用者。

如果 `.claude/hooks/yaml-helper.sh` 不存在，這就不是 CCGS 專案。
回報錯誤然後結束。

## Phase 1b: Reserved-setting detection

有些設定有完整的文件、也可以設定，但**沒有任何 skill
或 hook 會讀它們**：設了也沒有任何改變。**這個 skill 必須說出來。**
如果回傳一般的成功，會讓使用者合理地以為那個設定所描述的行為現在已經生效了，
促成這條規則的案例就是無障礙等級（accessibility tier）。
（這裡刻意不點名那個 key；見下面的註記。）
這個橫幅只存在於
`.claude/docs/effects-map.md`，
而正在設定專案的人永遠不會去開它。一個什麼都不做的設定，絕對不能長得
跟有效的設定一模一樣：見 `.claude/rules/skill-authoring.md` 的義務 3。

這個集合要推導出來，不要寫死（義務 5）：

```bash
grep -B14 '^> ### RESERVED' .claude/docs/effects-map.md | grep -E '^## '
```

**比對橫幅的標題（`> ### RESERVED`），絕對不要比對單純的 "RESERVED" 這個字。**
`platform.cert_tier` 那一節在文字說明裡*提到*這個橫幅，用來記錄它曾經
帶有這個橫幅、後來變成有效的設定。比對得太鬆，會把一個有效的
設定又回報成沒用的，這個方向會低估框架實際做的事，
也是為什麼 dead-settings 關卡兩個方向都要斷言。

標題可能用 " and " 連接**兩個 key**，要依這個分隔字串切開，
讓兩個都被抓到，否則第二個會悄悄漏出這個集合。把結果稱為
`RESERVED_SET`。

> 刻意不點名那些 key 的寫法。dead-settings 關卡會斷言
> 白名單上的設定**沒有**讀取者，而且任何一個拼出該 key 的 skill
> 檔案都會被它算成讀取者。為了舉例說明切分方式而在這裡點名它們，會讓
> `/settings` 被登記成兩個沒人讀的設定的讀取者，
> 關卡就會失敗，而且是正確地失敗。在解釋為什麼不要用某個已死路徑時把它拼出來，
> 會觸發同樣的警報。要改寫文字，不要加例外：
> 嚴格就是重點，所以不要為了讓例子更清楚而重新放回那些原本的名稱。

絕對不要拒絕寫入保留的 key。儲存使用者想要的值是正當的；
*默默地*儲存才是缺陷。

## Phase 2: View-all Mode

（沒有參數時）

1. 確認 `project.yaml` 存在。如果不存在，回報：
   > "No `project.yaml` found — run `/start` to create one."
   然後結束。

2. 檢查 `project.local.yaml` 是否存在。

3. 跑 `validate_yaml_enum project.yaml` 並擷取任何錯誤。
   如果 `project.local.yaml` 存在，也跑 `validate_yaml_enum project.local.yaml`。
   每個錯誤都標上來源檔案，讓使用者分得出它們。

4. **列舉葉節點。** 用 `Read` 工具把兩個 YAML 檔案都當文字讀進來。
   走過每個檔案的結構，把每個葉 key
   收集成一份去重複的點分隔路徑清單。葉節點是值不是空的
   `key: value` 那一行（純量或 inline array），不是引出巢狀 map
   的父區塊。每個檔案內維持出現順序；合併時，把 `project.local.yaml` 中
   `project.yaml` 沒有的葉節點接在後面。得到的清單
   就是要顯示的葉節點集合。

   **然後補上 rigor 家族**：`modes.rigor`、`modes.workflow`、
   `docs.density`、`qa.level`、`modes.story_granularity`、`modes.review_mode`、
   `team.size`，這七個裡面合併清單還沒有的都要補。這些通常不是任何一個檔案的葉節點：
   `modes.rigor` 有最終預設值，其他六個由 rigor 展開供應
   （`modes.review_mode` 和 `team.size` 在本機有設定時也可能是檔案的葉節點，但
   仍然必須補上，才能顯示它們*推導出來*的值）。如果只列舉
   檔案的葉節點，就會把使用者剛選的那些設定，藏在
   本來要顯示它們的那個檢視裡。

5. **對每個葉節點**，做三次讀取和一次檢查：
   - `resolve_setting <path>` → `<value>`、TAB、`<source>`。這會走完
     整條鏈（`project.local.yaml` → `project.yaml` → 舊檔案 →
     `rigor` 展開 → 預設值），所以它是唯一能回報
     推導值、或點名是誰供應的讀取方式。
   - `get_yaml_key project.yaml <path>` → 只有 yaml 的值（只有
     要顯示本機覆寫蓋掉了什麼時才需要）
   - `is_locally_overridable <path>` → 0（可覆寫）或 1（鎖定）

   依 `<source>` 計算**來源註記**：

   | `<source>` | Annotation |
   |---|---|
   | `project.local.yaml`, yaml-only value non-empty | `(LOCAL OVERRIDE — yaml has: <yamlvalue>)` |
   | `project.local.yaml`, yaml-only value empty | `(project.local.yaml)` |
   | `project.yaml` | `(project.yaml)` |
   | a legacy file path (e.g. `production/review-mode.txt`) | `(<path>, legacy)` |
   | `rigor:<level>` | `(derived from rigor: <level>)` |
   | `default` | `(default)` |
   | `unset` | skip the leaf (don't print unset keys) |

   當 `is_locally_overridable` 回傳 1 時，在註記後面加上 `, locked`。

   **當葉節點在 `RESERVED_SET`（Phase 1b）裡時，加上 `, reserved`**，並在區塊
   下面印出這行與圖例：

   ```
   reserved = stored, but nothing reads it. Setting it changes
   no behaviour today.
   ```

   > **四個階段都必須帶有 reserved 標記：view-one、view-all，
   > 以及兩條寫入路徑。** 如果標了 view-one 和寫入，卻讓 view-all
   > （**這個 skill 最常用的形式**）沒標，那麼設了保留 key 的使用者，
   > 會在大多數人實際會跑的那個檢視裡，看到它跟有效的設定並排列出，
   > 帶著一般的 `(project.yaml)` 註記。四個都要守住：view-one 和 view-all 是一對雙胞胎，
   > 就像兩條寫入路徑一樣。

6. **印出**，依頂層區段（`framework`、`modes`、
   `engine` 等）分組，順序是葉節點首次出現的順序。分組
   由點分隔的路徑決定，不是看葉節點來自哪個檔案
   ：例如 `modes.automation` 即使只有
   `project.local.yaml` 定義，也歸在 `modes:` 底下。每個區段內，葉節點
   縮排 2 個空格；子區塊（例如 `testing.strict.*`）再往內縮。
   輸出範例：

```
project.yaml: present
project.local.yaml: present

Schema validation: ok

Effective config:

framework:
  version: 1.2.0            (project.yaml, locked)

modes:
  review_mode: lean         (project.yaml)
  automation: autonomous    (LOCAL OVERRIDE — yaml has: collaborative)
  rigor: full               (project.yaml, locked)
  workflow: full            (derived from rigor: full, locked)
  story_granularity: fine   (derived from rigor: full, locked)

docs:
  density: terse            (project.yaml, locked)

qa:
  level: full               (derived from rigor: full, locked)

engine:
  name: Godot               (project.yaml, locked)
  version: 4.7              (project.yaml, locked)

testing:
  strict:
    logic: false            (LOCAL OVERRIDE — yaml has: true)
    integration: true       (project.yaml)

locked = cannot be overridden in project.local.yaml (project-wide setting).
It does NOT mean fixed: a derived value can still be set explicitly with
/settings <key>=<value>, and an explicit value wins over rigor.
```

只要任何一行被渲染出來帶有 `locked`，就要在設定區塊之後印出那兩行圖例。
沒有它，使用者會把 `locked` 讀成「不可變」，
然後推論 rigor 推導出來的設定沒辦法改，這跟
Phase 3 的 view-one 對同一個設定說的話相反（「明確的值會贏過
rigor」）。兩個檢視不能對同一個設定的可變性
留下互相矛盾的印象。

上面的 `docs.density` 那一行，就是把優先順序規則顯示出來：明確的 `project.yaml` 值
仍然會贏過 `rigor` 原本會推導出的等級，所以「完整但精簡」
是可以表達的。

如果有 schema 錯誤，在實際生效設定區塊之前，用這個格式印出：

```
Schema validation: ERRORS
  [project.yaml] modes.review_mode: 'chaotic' is not a valid value (expected: full|lean|solo)
  [project.local.yaml] engine.name: 'Pygame' is not a valid value (expected: Godot|Unity|Unreal)
```

## Phase 3: View-one Mode

（單一參數、沒有 `=` 時）

**如果 `<key>` 在 `RESERVED_SET` 裡，在值的區塊之前先印這段**：要放在上面，
不是下面。放在值下面的警語，讀起來像是對有效設定的註腳：

> **`<key>` is RESERVED — nothing reads it.** The value below is stored; it
> changes no behaviour today.

令 `<key>` 為參數。做四次讀取：

1. `resolve_setting <key>` → `<value>`、TAB、`<source>`（生效值加上來源）
2. `get_yaml_key project.yaml <key>` → 只有 yaml 的值
3. `get_yaml_key project.local.yaml <key>` → 只有本機的值（檔案不存在就跳過）
4. `is_locally_overridable <key>` → 0（可覆寫）或 1（鎖定）

從 `<source>` 判斷**來源**（跟 Phase 2 步驟 5 同一張表），
以及**是否被本機覆寫**的狀態：
- 本機獨有的值不是空的，就是 `yes`
- 否則是 `no`

印出：

```
<key>

  Effective value: <effective-value or "(not set)" if <source> is unset>
  Source: <project.yaml | project.local.yaml | project.local.yaml (overrides project.yaml) | derived from rigor: <level> | default>
  Locally overridden: <yes | no>
  Whitelist: <"can be locally overridden" if is_locally_overridable returned 0, else "locked — project-wide">
```

當兩個檔案都設了這個 key（LOCAL OVERRIDE 的情況），在 Source 底下
多加兩行：

```
  project.yaml value: <yamlvalue>
  project.local.yaml value: <localvalue>
```

當 `<source>` 是 `rigor:<level>` 時，在 Source 底下加一行，讓使用者
知道這個值可以設定，以及怎麼設：

```
  Set explicitly with: /settings <key>=<value>   (an explicit value wins over rigor)
```

當生效值是空的（這個 key 在任何地方都沒設），只印：

```
<key>

  Effective value: (not set)
  Locally overridden: no
  Whitelist: <"can be locally overridden" | "locked — project-wide">
```

## Phase 4: Set-yaml Mode

（`<key>=<value>`，沒有 `--local` 時）

1. **Schema 驗證**：呼叫 `validate_enum_value <key> <value>`。如果
   回傳 1，把 stderr 那一行原封不動顯示給使用者
   （`Invalid value '<value>' for '<key>'. Allowed: ...`），skill
   不寫入就結束。如果回傳 0，代表值是有效的，
   或是這個 key 沒有 enum 限制，繼續往下。

1b. **已知 key 檢查**：像 Phase 1 一樣從專案根目錄跑
   `bash .claude/scripts/config-set.sh <key> <value> --dry-run`，並讀它的
   `known` 那一列。如果寫 `yes`，繼續。如果寫 `no`，代表 CCGS 裡沒有任何東西
   會讀那個 key，所以寫入不會改變任何事；最常見的原因是打錯字。先不要
   寫：說明這點，並透過 `AskUserQuestion` 詢問，選項是
   `Use <nearest> instead`（只有當該列結尾是 `nearest: <key>` 時才有）、
   `Write <key> anyway`、`Cancel`。只有在使用者明確選擇之後才繼續；如果選
   `Use <nearest> instead`，就用那個 key 把這個 phase 重新開始。略過或
   空白的回答視為取消。

2. **Reserved 警告**：如果 `<key>` 在 `RESERVED_SET`（Phase 1b）裡，在
   核准提示之前印出：
   > "Note: `<key>` is RESERVED — no skill or hook reads it, so setting it will
   > not change any behaviour. Your value is stored either way."

   然後照常繼續到核准關卡。Phase 5 帶有一模一樣的
   警告。只在一條寫入路徑警告、另一條不警告，就留下一條
   通往同樣結果的靜默路徑，而這正是這個防護要避免的整個失敗。

3. **遮蔽警告**：讀 `get_yaml_key project.local.yaml <key>`。如果
   它回傳非空的值，在核准提示之前印出：
   > "Note: this setting is currently locally overridden in `project.local.yaml` (value: `<localvalue>`). Writing to `project.yaml` will not change your effective value."

4. **核准關卡**：使用 `AskUserQuestion`：
   - Prompt：``Set `<key>=<value>` in `project.yaml`?``
   - Options：`[A] Yes, write` / `[B] No, cancel`

5. **寫入**：使用 `Edit` 工具。編輯策略取決於
   `project.yaml` 裡已經有什麼：

   **Case A：key 已存在**：讀 `project.yaml`。找到
   `<lastsegment>: <oldvalue>` 那一行，以及緊鄰它上面、引出它父區塊的那一行
   （例如 `modes.review_mode` 的 `modes:`）。
   建構 `Edit`，讓 `old_string` 同時包含父區塊那一行和葉節點那一行，
   這樣即使 `<lastsegment>: <oldvalue>` 在別處也出現，比對仍然是唯一的。
   `modes.review_mode=full` 的範例：
   ```
   old_string:
     modes:
       review_mode: lean
   new_string:
     modes:
       review_mode: full
   ```

   **Case B：父區塊存在，葉節點不存在**：找到父區塊的最後一行。
   用 `Edit` 在正確的縮排下附加新的葉節點那一行，用
   最後一個既有的葉節點當作 `old_string` 的錨點。

   **Case C：父區塊不存在**：在檔案結尾附加一個新的頂層
   區塊（確定性做法：一律放在檔案結尾，絕對不放在區塊之間）。用 `Edit`，以
   檔案最後一個非空行當作 `old_string`，並把新區塊接在它後面。

   **Case D：檔案結構不尋常**（有同名的被註解掉的 key、
   巢狀結構不明確、YAML 格式有誤）：停下來，透過
   `AskUserQuestion` 詢問：
   > "Couldn't find a clean insertion point for `<key>` in `project.yaml`. Show me what to do."

6. 確認：``Set `<key>=<value>` in `project.yaml`.``

   **當 `<key>` 是 `modes.rigor` 時**，這次寫入也會連動另外六個
   設定，所以要印出它們現在解析成什麼：用 `resolve_setting` 重新讀取每一個，
   不要背誦展開表，因為它們任何一個都可能帶有仍然會勝出的明確值：

   ```
   Set modes.rigor=full in project.yaml. It now supplies:
     modes.workflow: full            (derived from rigor: full)
     docs.density: terse             (project.yaml — explicit, unchanged)
     qa.level: full                  (derived from rigor: full)
     modes.story_granularity: fine   (derived from rigor: full)
     modes.review_mode: full         (derived from rigor: full)
     team.size: studio               (derived from rigor: full)
   ```

## Phase 5: Set-local Mode

（`--local <key>=<value>` 時）

1. **白名單檢查**：呼叫 `is_locally_overridable <key>`。
   - 如果回傳 1（鎖定），印出一行：
     > ``<key> cannot be locally overridden — it's a project-wide setting. Use `/settings <key>=<value>` (no `--local`) to change it for the whole team.``
   - 不寫入就結束。

2. **Schema 驗證**：呼叫 `validate_enum_value <key> <value>`。如果
   回傳 1，原封不動顯示 stderr 訊息，不寫入就結束。

2a. **已知 key 檢查**：跟 Phase 4 步驟 1b 一樣，在
   `<key>` 前面加 `--local`：如果 `known` 那一列是 `no`，寫入前先問，如果該列有點名
   `nearest:` 的 key，就提供它。

2b. **Reserved 警告**：如果 `<key>` 在 `RESERVED_SET`（Phase 1b）裡，在
   核准提示之前印出：
   > "Note: `<key>` is RESERVED — no skill or hook reads it, so setting it will
   > not change any behaviour. Your value is stored either way."

   跟 Phase 4 步驟 2 一樣，而且是刻意的。兩條寫入路徑都通往
   使用者意圖的同一份紀錄檔；只警告其中一條，會讓
   `--local` 變成那條靜默的路徑。

3. **基底檢查**：如果 `project.yaml` 不存在：
   > "Cannot create `project.local.yaml` — `project.yaml` is missing. Run `/start` to create one first."
   結束。（依規格，本機覆寫需要有基底。）

4. **核准關卡**：使用 `AskUserQuestion`：
   - Prompt：``Set `<key>=<value>` in `project.local.yaml` (your personal override, gitignored)?``
   - Options：`[A] Yes, write` / `[B] No, cancel`

5. **寫入**：
   - 如果 `project.local.yaml` 不存在，用 `Write` 建立它，
     把新設定包在它的父區塊裡。`--local modes.automation=autonomous`
     的最小範例：
     ```yaml
     # project.local.yaml — per-developer overrides (gitignored)
     modes:
       automation: autonomous
     ```
   - 如果它存在，使用 `Edit`，採用 Phase 4 步驟 4 同樣的 Case A/B/C
     策略。

6. 確認：``Set `<key>=<value>` in `project.local.yaml` (your override).``

## Phase 6: Usage

當參數不符合四種有效形式中的任何一種（或運算元是空的）時，
印出：

```
Usage:
  /settings                          — view all effective config
  /settings <key>                    — view a single setting
  /settings <key>=<value>            — change a setting (project.yaml)
  /settings --local <key>=<value>    — change a setting locally
                                       (project.local.yaml, gitignored)

Examples:
  /settings modes.review_mode
  /settings modes.review_mode=full
  /settings --local modes.automation=autonomous
```

## Notes

- 所有 YAML 寫入都透過 `Edit`（既有的 key/區塊）或 `Write`
  （新檔案）。這個 skill 不依賴 `yq` 或任何外部的 YAML 函式庫。
- 白名單是在 `yaml-helper.sh` 裡強制執行的
  （`is_locally_overridable` 函式）。要擴充它，編輯
  `_yaml_helper_locally_overridable` 常數，不要在這裡重複列一份。
- **推導出來的值不會存在任何地方。** `modes.workflow`、`docs.density`、
  `qa.level`、`modes.story_granularity`、`modes.review_mode` 和 `team.size` 沒有
  最終預設值；當沒有任何檔案設定它們時，它們的值來自
  `yaml-helper.sh` 裡 `modes.rigor` 的展開
  （`_yaml_helper_rigor_expansion`）。要透過 `resolve_setting` 回報它們：
  用 `get_yaml_key` 讀會回傳空值，會把它們渲染成「(not set)」，
  但實際上每個 skill 都是依據一個真實的值在行動。
- schema 驗證的 enum 常數在 `yaml-helper.sh` 裡
  （`_yaml_helper_enums`）。`validate_enum_value` 是針對待寫入值的
  單一 key 驗證器；`validate_yaml_enum` 驗證整個
  檔案（`session-start.sh` 使用）。
- `project.local.yaml` 被 gitignore。這些
  覆寫永遠不會傳播給隊友。
- 要知道對特定遊戲類型或情況該**選哪個值**，以及什麼時候該
  建議改變某個值，見 `.claude/docs/settings-guidance.md`（建議性的預設組合
  加上改變的觸發條件）。`effects-map.md` 說明每個設定做什麼；那份文件說明
  該選哪一個。
