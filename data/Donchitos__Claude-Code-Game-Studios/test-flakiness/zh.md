---
name: test-flakiness
description: "從 CI log 找出不穩定（flaky）的測試：彙整通過率、找出時好時壞的失敗，並建議隔離。要在跑過多次之後用。"
argument-hint: "[ci-log-path | scan | registry]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(ls -t *), Bash(bash "*/.claude/skills/test-flakiness/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和每一次檔案寫入，都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律要問 · guided 只問重大的 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 類別的一律要問）。

# Test Flakiness Detection

不穩定（flaky）的測試，指的是程式碼完全沒改，卻有時通過、有時失敗的測試。在某些方面，flaky 測試比沒有測試還糟：它們會訓練團隊無視紅燈的 CI，把真正的失敗給蓋住。這個 skill 負責找出它們、說明可能的原因，並針對每一個建議該隔離還是該修。

**輸出：** 更新後的 `tests/regression-suite.md` 隔離區段 + 選用的
`production/qa/flakiness-report-[date].md`

**什麼時候跑：**
- Polish 階段（測試已經跑過很多次；統計訊號才可靠）
- 開發者開始把 CI 失敗當成「大概是 flaky」而不理它的時候
- `/regression-suite` 找出需要診斷的被隔離測試之後

---

## 1. Parse Arguments

**模式：**
- `/test-flakiness [ci-log-path]` — 分析某個特定的 CI 執行 log 檔案
- `/test-flakiness scan` — 掃描 `.github/` 或標準 log 輸出目錄裡所有找得到的 CI log
- `/test-flakiness registry` — 讀現有 regression-suite.md 的隔離區段，並針對已知的 flaky 測試提供修復指引
- 沒有參數 — 自動偵測：CI log 拿得到就跑 `scan`，否則跑 `registry`

---

## 2. Locate CI Log Data

### Option A — GitHub Actions (preferred)

檢查有沒有測試結果產物：
```bash
ls -t .github/ 2>/dev/null
ls -t test-results/ 2>/dev/null
```

Godot 專案：GdUnit4 輸出跟 JUnit 格式相容的 XML 結果，
放在 `reports/` 底下（它預設的報告資料夾，`res://reports/`）。檢查 `reports/`，
以及任何你把執行結果存進去的 `test-results/`，找 `.xml` 檔案。

Unity 專案：game-ci 的測試執行器預設把 NUnit XML 輸出到 `test-results/`。

Unreal 專案：automation log 會放到 `Saved/Logs/`。用 grep 找
`Result={Success}` 和 `Result={Fail}`：每個測試都會印出
`Test Completed. Result={<status>}`
（`docs/engine-reference/unreal/current-best-practices.md`，「Command Line」）。

### Option B — Local log files

如果有給路徑參數，就直接讀那個檔案。

### Option C — No log data available

如果找不到任何 log：
> "No CI log data found. To detect flaky tests, this skill needs test result
> history from multiple runs. Options:
> 1. Run the test suite at least 3 times and collect the output logs
> 2. Check CI pipeline output and save a log to `test-results/`
> 3. Run `/test-flakiness registry` to review tests already flagged as flaky
>    in `tests/regression-suite.md`"

停下來，問使用者要走哪個選項。

---

## 3. Parse Test Results

對找到的每個 CI log 或結果檔案，解析：

**JUnit XML 格式**（GdUnit4）：
- 用 grep 找 `<testcase name=` 取得測試名稱
- 用 grep 找 `<failure` 或 `<error` 辨識失敗
- 解析 `classname` 和 `name` 屬性，得到完整的測試識別碼

**NUnit XML 格式**（Unity，也就是 `/smoke-check` 讀取的、含 `<test-run>` 元素的那個檔案）：
- 每個測試是一個 `<test-case` 元素；它的 `fullname` 屬性就是識別碼
- 它的 `result` 屬性是 `Passed`、`Failed`、`Inconclusive` 或 `Skipped`
  （`docs/engine-reference/unity/current-best-practices.md`，「Command Line」）；
  只有 `Passed` 和 `Failed` 會進入歷史紀錄

**純文字 log**：
- 用 grep 找通過／失敗的樣式：
  - Godot：測試名稱旁邊的 `PASSED` / `FAILED`
  - Unreal：`Result={Success}` / `Result={Fail}`
  - Unity：`Test passed` / `Test failed`

建立一張表：`test_id → [run1_result, run2_result, run3_result, ...]`

---

## 4. Identify Flaky Tests

一個測試如果在結果歷史中同時出現過 PASS 和 FAIL，而且那些執行之間沒有任何程式碼改動，它就是 **flaky**。

Flaky 程度的門檻：
- **High flakiness**：在 >25% 的執行中失敗，立刻隔離
- **Moderate flakiness**：在 5–25% 的執行中失敗，要調查並盡快修
- **Low/suspected flakiness**：在 1–5% 的執行中失敗，持續觀察；可能真的只是罕見的失敗

**執行次數少於 3 次時，每個發現都只是*疑似*，不管它的失敗率是多少。** 兩次執行失敗一次，看起來是 50%，但它只是一個資料點：不要隔離它，標成 suspected，並問有沒有更多執行資料可用。上面的各個層級，以及隔離，都是從 3 次執行起才適用。

對每個 flaky 測試，分類可能的原因：

### Cause classification

| Cause | Symptoms | Fix direction |
|-------|----------|---------------|
| **Timing / async** | Fails after awaiting signals or timers; pass rate correlates with system load | Add explicit await/synchronisation; avoid time-based delays |
| **Order dependency** | Fails when run after specific other tests; passes in isolation | Add proper setup/teardown; ensure test isolation |
| **Random seed** | Fails intermittently with no pattern; involves RNG | Pass explicit seed; don't use `randf()` in tests |
| **Resource leak** | Fails more often later in a test run | Fix cleanup in teardown; check orphan nodes (Godot) or object disposal (Unity) |
| **External state** | Fails when a file, scene, or global exists from a prior test | Isolate test from file system; use in-memory mocks |
| **Floating point** | Fails on comparisons like `== 0.5` | Use epsilon comparison (`is_equal_approx`, `Assert.AreApproximately`) |
| **Scene/prefab load race** | Fails when scenes are not yet ready | Await one frame after instantiation; use `await get_tree().process_frame` |

用 Grep 檢查測試檔案裡有沒有計時呼叫、randf、全域狀態存取，或對浮點數做的相等比較，來縮小原因的範圍。

---

## 5. Recommend Action

對每個 flaky 測試：

**隔離（High flakiness）：**
> "Quarantine this test immediately. Skip it with the engine's own mechanism,
> log it in the `tests/regression-suite.md` quarantine section, and fix the root
> cause before removing quarantine."

各引擎的跳過機制，只講專案所用引擎的那一個：
- **Godot (gdUnit4)，GDScript**：測試函式上的 skip 參數，
  `func test_x(_do_skip := true, _skip_reason := "flaky: [cause]")`。gdUnit4 讀的是參數名稱 `do_skip` 和 `skip_reason`（允許前面加 `_`），出自
  `addons/gdUnit4/src/core/GdUnitTestSuiteScanner.gd`，以 gdUnit4 6.2.2 為準；
  針對已安裝的版本，要到那裡確認。
- **Godot (gdUnit4)，C#**：**NOT SOURCEABLE**：gdUnit4 的 C# 測試 attribute 不在 `addons/gdUnit4/` 的原始碼裡，`docs/engine-reference/godot/` 也沒有涵蓋它們。記在隔離區段，並問使用者他們的 C# 測試是怎麼跳過的；不要自己發明一個 attribute。
- **Unity (NUnit)**：`[Ignore("flaky: [cause]")]`，NUnit 3 要求要寫理由
- **Unreal**：**NOT SOURCEABLE**：`docs/engine-reference/unreal/` 沒有記載任何跳過 automation 測試的方法。記在隔離區段，並問使用者他們的 CI 是怎麼排除一個測試的；不要自己發明一個 flag。

**調查並盡快修（Moderate）：**
> "This test is intermittently unreliable. Root cause appears to be [cause].
> Suggested fix: [specific fix based on cause classification]. Do not quarantine
> yet — fix the test directly."

**持續觀察（Low/suspected）：**
> "This test shows suspected flakiness. Collect more run data before
> quarantining. Note it as 'suspected' in the regression suite."

---

## 6. Generate Reports

### In-conversation summary

```
## Flakiness Detection Results

**Runs analysed**: [N]
**Tests tracked**: [N]

### Flaky Tests Found

| Test | System | Fail Rate | Confidence | Likely Cause | Recommendation |
|------|--------|-----------|------------|--------------|----------------|
| [test_name] | [system] | [N]% | confirmed | Timing | Quarantine + fix async |
| [test_name] | [system] | [N]% | confirmed | Float comparison | Fix: use epsilon compare |
| [test_name] | [system] | [N]% | suspected (fewer than 3 runs) | Order dependency | Collect more runs before acting |

### Clean Tests (no flakiness detected)

[N] tests ran across [N] runs with consistent results — no flakiness detected.

### Data Limitations

[Note if fewer than 5 runs were available — fewer runs = less statistical confidence]
```

---

## 7. Update Regression Suite + Optional Report File

問：「May I update the quarantine section of `tests/regression-suite.md`
with the flaky tests found?」

如果同意：用 `Edit` 把條目附加到 Quarantined Tests 表。
絕對不要移除既有的隔離條目，只能新增。

（另外）問：「May I write a full flakiness report to
`production/qa/flakiness-report-[date].md`?」

完整報告包含逐個測試的分析，附原因細節和引擎專屬的修正程式碼片段。

寫完之後：

- 對每個被隔離的測試：「Add the engine-specific skip annotation to
  disable this test in CI. Re-enable after the root cause is fixed.」
- 對適合直接修的測試：「The fix for [test] is straightforward —
  change the equality comparison on line [N] to use `is_equal_approx`.」
- 摘要：「Once all quarantine annotations are applied, CI should run green.
  Schedule fix work for the [N] quarantined tests before the release gate.」

---

## Collaborative Protocol

- **絕對不要刪除測試檔案**：隔離的意思是加註解並列入清單，不是移除
- **統計信心很重要**：少於 3 次執行時，把發現標成「suspected」，不是「confirmed」；並問有沒有更多執行資料可用
- **目標永遠是修好它**：隔離只是暫時的；即使建議隔離，也要講出修法的方向
- **寫入前要先問**：regression-suite 的更新和報告檔案都需要明確核准。寫入時：Verdict: **COMPLETE** — flakiness report written. 拒絕時：Verdict: **BLOCKED** — user declined write.
- **CI 的 flaky 是整個團隊的問題**：把清單和建議的動作清楚地講出來；不要在團隊不知情的情況下悄悄隔離
