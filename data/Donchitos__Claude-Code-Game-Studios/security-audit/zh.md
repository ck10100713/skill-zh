---
name: security-audit
description: "安全稽核：存檔竄改、作弊途徑、網路漏洞、資料外洩、輸入驗證。公開發布或多人遊戲上線之前使用。"
argument-hint: "[full | network | save | input | quick]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Agent, Bash(bash "*/.claude/skills/security-audit/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow`

**自動化模式**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次寫檔，都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
屬於 `automation_always_ask` 的類別一律要詢問）。

**`workflow`**（上面已解析）只決定 Phase 7 對發布關卡要告訴你什麼：
在 `standard` 和 `full` 時，發布關卡需要這份報告；在 `minimal` 時
不需要。稽核本身在每個等級都一樣地跑。

# Security Audit

安全對任何要出貨的遊戲都不是選配。就算是單機遊戲，也有
存檔竄改的途徑。多人遊戲有作弊的攻擊面、資料外洩
風險，以及阻斷服務攻擊的可能。這個 skill 會有系統地稽核
程式碼庫中最常見的遊戲安全問題，並產出一份依優先順序排列的
修補計畫。

**什麼時候跑這個 skill：**
- 任何公開發布之前（在 `workflow: standard` 和 `full` 時，Polish → Release 關卡需要它）
- 啟用任何線上/多人功能之前
- 實作任何會從磁碟或網路讀取資料的系統之後
- 有人回報安全相關的 bug 時

**輸出：** `production/security/security-audit-[date]-[scope].md`：名稱裡
帶 scope，是為了避免同一天跑的 `quick` 或 `save` 把發布關卡要讀的
`full` 報告蓋掉。

---

## Phase 1: Parse Arguments and Scope

**模式：**
- `full`：所有類別（發布前建議用）
- `network`：只看網路/多人
- `save`：只看存檔和序列化
- `input`：只看輸入驗證和注入
- `quick`：只做高嚴重度的檢查（最快，適合反覆執行）
- 沒有參數：跑 `full`

讀 `project.yaml` 來決定下列項目，當某個 key 不存在或是空的時候，引擎/語言/平台退而用 `.claude/docs/technical-preferences.md`：
- `engine.name` 和 `engine.language`：**關鍵依據：它們決定要用 Phase 3 的
  哪一組 pattern，而如果某個引擎在某個類別沒有有來源依據的 pattern 組，那個
  類別就是 `NOT ASSESSED`。** 如果 `engine.name` 不存在或是空的，要在
  報告裡說明，並把每個 grep 類別都當作 `NOT ASSESSED`；不要退回去用
  Godot 的清單，只因為它們是完整寫出來的那一組
- `platform.targets`（影響哪些攻擊面適用）
- `platform.multiplayer` 和 `platform.online`：多人/網路功能是否
  在範圍內。`technical-preferences.md` 沒有對應的欄位，所以舊版的
  fallback 無法提供這兩個值。

  > **不存在不代表 `false`。** 這些 key 有讀取者，
  > 就是這個 skill，卻**在設定流程中沒有寫入者**：`/setup-engine` 和 `/start`
  > 都不會輸出 `platform:` 區塊，只有 `/settings`
  > 會設定它們，而且是在有人去跑它的時候，所以在大多數 CCGS 專案裡這兩個 key
  > 都不存在。如果把它們預設成 `false`，就會在**每一個專案上都跳過 Category 2（Network and
  > Multiplayer Security），包括真正的多人遊戲**：一個安全類別在沒有任何東西會設定的值上
  > 自動放行。
  >
  > 當任一個 key 不存在或是空的：**不要假設是單機，也不要
  > 跳過 Category 2。** 問使用者遊戲有沒有多人或線上功能。如果
  > 沒辦法問，就照樣跑 Category 2，並標成
  > `NOT ASSESSED — multiplayer scope unconfirmed (platform.multiplayer unset —
  > set it with /settings)`，依 Phase 5，這會讓 `CLEAR TO SHIP` 無法達成。
  > 在範圍未確認期間，嚴重度要按多人遊戲評：未解決的 HIGH
  > 就是 DO NOT SHIP，並且要在報告中說明這個評級假設是多人，
  > `security-engineer` 也是這樣做。
  > 多掃一個單機遊戲只花幾分鐘；少掃一個
  > 多人遊戲，等於把這個類別沒跑就出貨。
  >
  > 用 `/settings platform.multiplayer=true` 明確設定它們（它們是
  > 專案層級的，所以 `--local` 會被拒絕）。把它記錄在 `project.yaml`
  > 才是根本解法；這條規則是在有人去做之前的防護。

---

## Phase 2: Spawn Security Engineer

用 `Agent` 生成 `security-engineer`：稽核就是它的工作，所以不要在
這個 session 裡自己跑那些類別。如果無法生成，說明原因、在這裡跑掃描，
並讓報告的 **Audited by** 那行把這點寫清楚。

**送出這份固定的 brief 範本。** 只填 `{…}` 的欄位，資料來自
`project.yaml`（沒有的話用 technical preferences）、依
`.claude/docs/code-root-resolution.md` 解析出來的程式碼根目錄，以及 Phase 3 原封不動複製的文字。
不要加任何別的東西：不要對遊戲類型表示看法，不要預設嚴重度，不要對
任何發現發表意見。你自己加的一句話，就是預先評級滲進去的地方。

```text
Run a security audit of this project for /security-audit.

Scope: {full | network | save | input | quick}
Engine: {engine.name} {engine.version}, language {engine.language}
platform.multiplayer: {true | false | unset}    platform.online: {true | false | unset}    Phase 1 answer: {multiplayer | single-player | not asked}
Code root: {the resolved code root, or "unresolved"}
Also scan: {assets/data/ and the config files that exist, or "none"}
Categories to run, with their checks and grep patterns for this engine:
{each Phase 3 category this scope runs, copied as written, with the table's row for this engine}
NOT SOURCEABLE on this engine: {categories, or "none"} — report each NOT ASSESSED; never call it reviewed, verified safe or passed
Skipped, with reason: {e.g. "Category 2 — platform.multiplayer and platform.online are false", or "none"}
Report: production/security/security-audit-{date}-{scope}.md — return the report as text; /security-audit writes the file after asking

Severity (rate every finding yourself, against this table only):
- CRITICAL: Remote code execution, data breach, or trivially-exploitable cheat that breaks multiplayer integrity
- HIGH: Save tampering that bypasses progression, credential exposure, or server-side authority bypass
- MEDIUM: Client-side cheat enablement, information disclosure, or input validation gap with limited impact
- LOW: Defence-in-depth improvement — hardening that reduces attack surface but no direct exploit exists
Nothing in this brief sets or suggests a severity. The game's type never lowers a rating: a single-player game is rated on the same table. The one adjustment is upward — when the game is multiplayer, or its scope is unconfirmed (unset and not answered), a HIGH counts as CRITICAL; say so where it applies.
Report each finding as SEC-NNN with category, file:line, description, attack scenario, remediation and effort, grouped by severity.
```

這個範本本身就帶有評級規則，所以沒有什麼要重述的：
表格已經把繞過進度的存檔竄改評為 HIGH，agent 會依它
評每個發現，Phase 5 再把多人規則套用到
建議上。

如果程式碼根目錄無法解析，不要傳一個猜的進去：每個會掃描程式碼的類別
都是 `NOT ASSESSED — code root unresolved`，報告也要這樣說。
空的程式碼根目錄就是 Phase 5 裡「實作不足」的情況，每個
會掃描程式碼的類別寫 `NOT ASSESSED — no source under <root>`，而不是零個
發現。兩種情況都絕對不能報告成乾淨。

security-engineer 會針對 6 個類別跑稽核（見 Phase 3）。要收齊它們完整的發現之後才繼續。

---

## Phase 3: Audit Categories

security-engineer 會評估下面每一項。跳過不適用於專案範圍的類別，
並在 Executive Summary 裡點名每個被跳過的類別和原因
（`Category 2 — skipped: platform.multiplayer and
platform.online are false`）。

### Engine pattern sets：看下面任何一個 Category 之前，先讀這一段

**Categories 1–3 裡的每份 pattern 清單都是為 Godot 寫的。** 在 Unity 或
Unreal 專案上它們什麼都比對不到，而零命中的掃描會讓報告看起來是乾淨的，
「對安全稽核來說最危險的失敗」。請使用 Phase 1 解析出的
`engine.name` 對應的那張表。

| Category | Godot | Unity | Unreal |
|---|---|---|---|
| 1 — Save / serialization | the Godot list below | **NOT SOURCEABLE** | **NOT SOURCEABLE** |
| 2 — Network / multiplayer | the Godot list below | `ServerRpc`, `ClientRpc`, `NetworkVariable`, `NetworkObject`, `NetworkManager`, `NetworkBehaviour`, `IsServer`, `IsOwner` | `UFUNCTION`, `Server`, `Client`, `NetMulticast`, `Replicated`, `DOREPLIFETIME`, `GetLifetimeReplicatedProps`, `HasAuthority` |
| 3 — Input | the Godot list below | `InputSystem`, `PlayerInput`, `ReadValue`, `InputValue` | `EnhancedInput`, `UInputAction`, `InputMappingContext`, `BindAction`, `FInputActionValue` |
| 4 — Data exposure | engine-agnostic — the list below applies to all three | | |
| 5, 6 | judgement and manifests, not greps — no engine set needed | | |

上面 Unity 和 Unreal 的名稱是**取自這個 repo 固定的參考文件**
（`docs/engine-reference/unity/modules/{networking,input}.md`、
`docs/engine-reference/unreal/modules/{networking,input}.md`），不是憑記憶寫的。
使用前先對照固定版本驗證，並補上參考文件裡有記載、而這張表
漏掉的名稱，這張表只是下限，不是完整的集合。

> **`NOT SOURCEABLE` 是一個結論，不是要憑記憶去填的缺口。** 兩棵參考文件樹都
> 沒有序列化/存檔模組，所以 Unity 和 Unreal 的存檔 API 名稱
> 在這裡無法確認。**不要憑訓練資料寫下來。**
> 一份信心滿滿但錯誤的 pattern 清單，在這個 skill 裡比在任何其他地方都更糟：
> 它會產生一次看起來很徹底、什麼都沒找到、讀起來像通過的掃描。
> 表格寫 NOT SOURCEABLE 的地方，那個類別對這個引擎就是 **`NOT ASSESSED`**，
> 見 Phase 5。要正確補上它，請在 `docs/engine-reference/<engine>/modules/`
> 加一個存檔/序列化模組，來源要像其他模組一樣可追溯；
> 有了之後，從裡面取得該類別的 pattern 名稱，在報告裡引用它，
> 這個類別就可以跑了。


### Category 1: Save File and Serialization Security
- 存檔載入前有驗證嗎？（不要盲目 deserialize）
- 存檔路徑是用使用者輸入組出來的嗎？（路徑穿越風險）
- 存檔有做 checksum 或簽章嗎？（偵測竄改）
- 遊戲有沒有在沒檢查範圍的情況下，直接信任存檔裡的數值？
- 存檔載入附近有沒有任何 eval() 或動態程式碼執行的呼叫？

Grep patterns：**信任這份清單之前，先查固定版本的引擎參考文件**
（見下面的 API 名稱警告）：`FileAccess`、`File.open`、`open(`、`load`、
`deserialize`、`parse`、`parse_string`、`from_json`、`read_file`、`get_var`、
`bytes_to_var`，逐一檢查它們有沒有驗證。

> **API 名稱是跟版本綁定的，而且這份清單只是起點，不是
> 完整的集合。** `File.open` 是 **Godot 3.x**；Godot 4 把這個類別改名為
> `FileAccess`（`docs/engine-reference/godot/breaking-changes.md`）。依賴
> 這些 pattern 之前，先讀這個專案固定版本對應的 `docs/engine-reference/<engine>/`，
> 並補上它記載的名稱。grep 一個已經不存在的類別會回傳零命中，而且
> **這個類別零命中會讓報告看起來是乾淨的**，這是對安全稽核
> 最危險的失敗。
> 對 Godot 4 專案只搜 `File.open` 什麼都找不到，並對一個沒人檢查過的程式碼庫
> 回報 CLEAR TO SHIP。如果你無法確認固定版本的正確
> 名稱，就在報告裡說明，不要把零命中的掃描當成通過呈現。

### Category 2: Network and Multiplayer Security (skip if single-player only)
- 遊戲狀態是以伺服器為準，還是由客戶端決定結果？
- 收到的網路封包有驗證大小、類型和數值範圍嗎？
- 玩家位置和狀態變化有在伺服器端驗證嗎？
- 任何網路呼叫有做 rate limiting 嗎？
- 認證 token 的處理正確嗎（絕對不能用明文傳送）？
- 遊戲在 release build 裡有沒有暴露任何 debug 端點？

Grep：`recv`、`receive`、`PacketPeer`、`socket`、`MultiplayerPeer`、
`ENetMultiplayerPeer`、`NetworkedMultiplayerPeer`、`rpc`、`rpc_id`、
`@rpc`，逐一檢查每個呼叫點有沒有驗證。

> 跟 Category 1 一樣有版本的但書。`NetworkedMultiplayerPeer` 是 **Godot 3.x**；
> Godot 4 用的是 `ENetMultiplayerPeer`
> （`docs/engine-reference/godot/modules/networking.md`）。單純的子字串
> `MultiplayerPeer` 兩個都比對得到，是比較安全的探測方式。

### Category 3: Input Validation
- 有沒有任何玩家提供的字串被用在檔案路徑裡？（路徑穿越）
- 有沒有任何玩家提供的字串在沒清理的情況下被寫進 log？（log injection）
- 數值輸入（例如道具數量、角色屬性）在使用前有檢查範圍嗎？
- 成就/統計值在寫入任何後端之前有檢查嗎？

Grep：`get_input`、`Input.get_`、`input_map`、面向使用者的文字欄位，檢查驗證。

### Category 4: Data Exposure
- 程式碼根目錄或 `assets/` 裡有沒有寫死任何 API key、憑證或 secret？
- release build 裡有沒有包含 debug 符號或冗長的錯誤訊息？
- 遊戲有沒有把敏感的玩家資料記錄到磁碟或 console？
- 有沒有任何內部檔案路徑或系統資訊暴露給玩家？

在面向 release 的程式碼中不分大小寫地 grep：`api[_-]?key`、`secret`、
`password`、`token`、`private[_-]?key`、`sk_live`、`BEGIN PRIVATE KEY`、`DEBUG`，
以及引擎的 print 呼叫（Godot 是 `print(`，Unity 是 `Debug.Log`，Unreal 是 `UE_LOG`）。

### Category 5: Cheat and Anti-Tamper Vectors
- 對遊戲玩法關鍵的數值，是不是只存在記憶體裡，而不是容易編輯的檔案？
- 任何關鍵的遊戲進度旗標（例如「已購買 DLC」）有在伺服器端驗證嗎？
- 多人遊戲有沒有任何防護，可以對付記憶體編輯工具（Cheat Engine 等）？
- 排行榜/分數提交在接受之前有驗證嗎？

註：客戶端的反作弊基本上沒辦法強制執行。對於任何競技或有營利的內容，重點放在伺服器端驗證。

### Category 6: Dependency and Supply Chain
- 有用到任何第三方 plugin 或函式庫嗎？把它們列出來。
- 使用中的版本有任何 plugin 有已知的 CVE 嗎？
- plugin 的來源有驗證過嗎（官方 marketplace、審查過的 repo）？

Glob：`addons/`、`plugins/`、`third_party/`、`vendor/`，列出所有外部依賴。

---

## Phase 4: Classify Findings

對每個發現，指定：

**嚴重度：**
| Level | Definition |
|-------|-----------|
| **CRITICAL** | Remote code execution, data breach, or trivially-exploitable cheat that breaks multiplayer integrity |
| **HIGH** | Save tampering that bypasses progression, credential exposure, or server-side authority bypass |
| **MEDIUM** | Client-side cheat enablement, information disclosure, or input validation gap with limited impact |
| **LOW** | Defence-in-depth improvement — hardening that reduces attack surface but no direct exploit exists |

**狀態：** Open / Accepted Risk / Out of Scope

---

## Phase 5: Generate Report

```markdown
# Security Audit Report

**Date**: [date]
**Scope**: [full | network | save | input | quick]
**Engine**: [engine + version]
**Audited by**: [security-engineer via /security-audit | this session — security-engineer not spawned: reason]
**Files scanned**: [N source files, N config files]

---

## Executive Summary

| Severity | Count | Must Fix Before Release |
|----------|-------|------------------------|
| CRITICAL | [N] | Yes — all |
| HIGH | [N] | Yes — all |
| MEDIUM | [N] | Recommended |
| LOW | [N] | Optional |

**Release recommendation**: [NOT ASSESSED — INSUFFICIENT IMPLEMENTATION / CLEAR TO SHIP / FIX BEFORE SHIPPING / DO NOT SHIP]

Choose it by the open findings, first match wins:
- **DO NOT SHIP** — any open CRITICAL finding (in a multiplayer game, any open HIGH
  counts as CRITICAL)
- **FIX BEFORE SHIPPING** — open HIGH findings and no CRITICAL; the Polish → Release
  gate needs zero open HIGH (at `standard` and `full`)
- **NOT ASSESSED** — per the rule below, when the scan could not cover the surface.
  It ranks below both failure values — a known finding is more actionable than an
  unscanned category, and still has to be fixed — and above CLEAR TO SHIP
- **CLEAR TO SHIP** — no open CRITICAL or HIGH (MEDIUM and LOW may remain)

> **`NOT ASSESSED` is required when there was not enough implemented surface to
> audit**, or when the API names for the pinned engine version could not be
> confirmed — **in place of CLEAR TO SHIP, never of a failure value.** An open
> CRITICAL or HIGH still decides the recommendation (first match above): a run
> with an unscanned category and an open HIGH is FIX BEFORE SHIPPING, and names
> the unscanned category beside it. A zero-finding scan over two files of source is not a clean bill of
> health, and `CLEAR TO SHIP` must never be reachable by having nothing to look
> at. Name what was missing and which skill produces it.
>
> **The engine axis is part of that rule, not a separate one.** If
> the Phase 3 table marks a category `NOT SOURCEABLE` for this project's
> `engine.name`, that category is `NOT ASSESSED` — state it by name in the
> Executive Summary, and **`CLEAR TO SHIP` is unreachable for the run**. The
> category reads `NOT ASSESSED — <category> has no sourced pattern set for
> <engine>`; the release recommendation is still the first match above, so it is
> NOT ASSESSED only where the run would otherwise have been CLEAR TO SHIP. Never
> report the category as reviewed by other means: files it covers may still be
> read for another category, and a finding that read turns up is reported, but
> the category stays NOT ASSESSED — never "reviewed", "verified safe" or passed.
> A scan that could not look is not a scan that found nothing, and only the
> report can tell the reader which of the two happened.

---

## CRITICAL Findings

### SEC-001: [Title]
**Category**: [Save / Network / Input / Data / Cheat / Dependency]
**File**: `[path]` line [N]
**Description**: [What the vulnerability is]
**Attack scenario**: [How a malicious user would exploit it]
**Remediation**: [Specific code change or pattern to apply]
**Effort**: [Low / Medium / High]

[repeat per finding]

---

## HIGH Findings

[same format]

---

## MEDIUM Findings

[same format]

---

## LOW Findings

[same format]

---

## Accepted Risk

[Any findings explicitly accepted by the team with rationale]

---

## Dependency Inventory

| Plugin / Library | Version | Source | Known CVEs |
|-----------------|---------|--------|------------|
| [name] | [version] | [source] | [none / CVE-XXXX-NNNN] |

---

## Remediation Priority Order

1. [SEC-NNN] — [1-line description] — Est. effort: [Low/Medium/High]
2. ...

---

## Re-Audit Trigger

Run `/security-audit` again after remediating any CRITICAL or HIGH findings.
At `workflow: standard` and `full`, the Polish → Release gate requires this report with no open CRITICAL or HIGH items.
```

---

## Phase 6: Write Report

在對話中呈現報告摘要（只有 executive summary 加上 CRITICAL/HIGH 的發現）。

詢問："May I write the full security audit report to `production/security/security-audit-[date]-[scope].md`?"

核准後才寫。

---

## Phase 7: Gate Integration

在 `workflow: standard` 和 `full` 時，這份報告是 **Polish → Release 關卡**的必要產出物；`minimal` 的關卡除了 smoke 和 S1 bug 之外全部省略，也包括它。依上面解析出的 `workflow`，說明這個專案適用哪一種。

修補完發現之後，重跑：`/security-audit quick`，在跑 `/gate-check release` 之前確認 CRITICAL/HIGH 項目都已解決。

依發布建議分支，不要只看發現的數量：

如果是 **DO NOT SHIP**（有未解決的 CRITICAL，或多人遊戲中有未解決的 HIGH）：
> "⛔ CRITICAL security findings must be resolved before any public release. Do not proceed to `/launch-checklist` until these are addressed."

如果是 **FIX BEFORE SHIPPING**（有未解決的 HIGH 發現、沒有 CRITICAL、單機遊戲）：
> At `workflow: standard`/`full`: "⚠️ [N] HIGH finding(s) are open. The Polish → Release gate's security audit item requires none — fix them and re-run `/security-audit quick` before `/gate-check release`."
>
> At `minimal`: "⚠️ [N] HIGH finding(s) are open — fix them and re-run `/security-audit quick` before you ship. The `minimal` release gate does not read this report; the open HIGH still makes the recommendation FIX BEFORE SHIPPING."

如果是 **NOT ASSESSED**：
> "Security audit NOT ASSESSED — [each category not assessed, and why]. The report is
> written. [At `workflow: standard`/`full`:] `/gate-check release` will report its
> security item NOT ASSESSED until [the missing input] is supplied and the audit
> re-run. [At `minimal`:] The `minimal` release gate does not read this report,
> but those categories stay unscanned until [the missing input] is supplied."
>
> 要為每個類別點名缺少的輸入：`engine.name`、程式碼根目錄、
> 多人範圍（`/settings platform.multiplayer=…`），或者，對 Phase 3 的表格
> 在這個引擎上標為 NOT SOURCEABLE 的類別（Unity 和 Unreal 上常見的原因），
> 就是 `docs/engine-reference/<engine>/modules/` 裡的存檔/序列化模組
> （Phase 3），並點名那個類別。

如果是 **CLEAR TO SHIP**：
> "✅ No blocking security findings. Report written to `production/security/`. Include this path when running `/gate-check release`."

---

## Collaborative Protocol

- **絕對不要假設某個 pattern 是安全的**：標出來，讓使用者決定
- **接受風險是有效的結果**：對單人團隊來說，有些 LOW 的發現是可以接受的取捨；要記錄這個決定
- **多人遊戲的標準更高**：多人情境下的任何 HIGH 發現都應該當成 CRITICAL
- **這不是滲透測試**：這個稽核涵蓋的是常見的 pattern；在任何競技或有營利的多人遊戲上線之前，建議找真正的資安專業人員做一次滲透測試
