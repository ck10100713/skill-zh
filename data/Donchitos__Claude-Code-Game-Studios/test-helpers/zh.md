---
name: test-helpers
description: "產生引擎專屬的測試 helper 函式庫：斷言工具、factory 函式、mock，放在引擎的測試資料夾裡，減少重複的樣板程式碼。"
argument-hint: "[system-name | all | scaffold]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/test-helpers/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和每一次檔案寫入，都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律要問 · guided 只問重大的 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 類別的一律要問）。

# Test Helpers

把常見的 setup、teardown 和斷言寫法抽成 helper，寫測試案例會更快、也更一致。這個 skill 會產生一套貼合專案實際引擎、語言和系統的 `tests/helpers/` 函式庫，讓每個開發者少寫一些樣板程式碼，多寫一些斷言。

**輸出：** 引擎專屬的 helper 檔案，放在引擎的 **helper root**，
那是它的測試執行器唯一會編譯到它們的地方（`.claude/docs/directory-structure.md`）：

| Engine | Helper root |
|---|---|
| Godot | `tests/helpers/` |
| Unity | `Assets/Tests/EditMode/Helpers/` — inside the `EditModeTests` assembly `/test-setup` creates. If PlayMode tests need the same helpers, ask before creating `Assets/Tests/Helpers/TestHelpers.asmdef` and referencing it from both test assemblies. |
| Unreal | `Source/<Module>/Private/Tests/Helpers/` |

下面的 `tests/helpers/` 指的是專案所用引擎的 helper root。

**什麼時候跑：**
- `/test-setup` 建好框架骨架之後（第一次）
- 多個測試檔案重複同樣的 setup 樣板時
- 開始為一個新系統寫測試時

---

## Assertions: use the project's test framework, never bare `assert()`

**產生的 helper 必須透過設定好的測試框架的斷言 API 來斷言**，由 `testing.framework` 解析出來，不能用 GDScript 內建的 `assert()`。

helper 裡用裸的 `assert()` 會出兩個問題，而且兩個都是悄悄發生的：

1. **它會中止整個執行，而不是讓測試失敗。** 框架的斷言會記錄失敗並繼續往下跑，所以一個壞掉的預期只會產生一個紅燈的測試。裸的 `assert()` 會讓執行停住，第一個失敗就把後面所有結果都藏起來。
2. **它在 release build 裡會被移除。** 一套建在 `assert()` 上的 helper 函式庫，會在你最想檢查的那個 build 裡完全停止斷言，而且沒有任何錯誤，測試還是「通過」。

**產生程式碼之前，先查好設定的框架的斷言形式。** 不要把這個檔案裡、或其他 skill 範例裡的寫法當成權威來抄，它們只是示意，而且已經不一致了（`assert_eq`、`assert_true` 和 `assert_that` 在整個 repo 裡都有出現）。如果你沒辦法確認專案框架的正確 API，就直說，而且不要產生 helper，不要用猜的。

**Helper 絕對不能繼承框架的 test-suite 基底類別。** `tests/helpers/` 裡一個繼承 suite 型別的檔案，會被執行器當成含有零個測試的測試 suite 發現。Helper 是普通的類別；只有真正的測試檔案才繼承 suite。

---

## 1. Parse Arguments

**模式：**
- `/test-helpers [system-name]` — 為特定系統產生 helper
  （例如 `/test-helpers combat`）
- `/test-helpers all` — 為所有有測試檔案的系統產生 helper
- `/test-helpers scaffold` — 只產生基礎 helper 函式庫（不含系統專屬的 helper）；第一次跑的時候用這個
- 沒有參數 — 如果還沒有 helper 就跑 `scaffold`，否則跑 `all`

---

## 2. Detect Engine and Language

先從 `project.yaml` 讀，對於任何缺少或是空的 key，退回去讀 `.claude/docs/technical-preferences.md`：
- `engine.name`（否則用 `Engine:` 的值）
- `engine.language`（否則用 `Language:` 的值）
- `testing.framework`（否則用 Testing 章節裡的 `Framework:`）

如果兩個來源都沒設定引擎：「Engine not configured. Run `/setup-engine` first.」

---

## 3. Load Existing Test Patterns

掃描引擎的測試根目錄，找已經在用的寫法（Godot `tests/`、Unity
`Assets/Tests/`、Unreal `Source/<Module>/Private/Tests/`）：

```
Glob pattern="tests/**/*_test.*"                  (Godot)
Glob pattern="Assets/Tests/**/*Tests.cs"          (Unity)
Glob pattern="Source/*/Private/Tests/**/*.cpp"    (Unreal)
```

挑一批具代表性的樣本（最多 5 個檔案），讀這些測試檔案並擷取：
- Setup 的寫法（`before_each` / `setUp` / fixture 是怎麼寫的）
- 常見的斷言寫法（最常斷言的是什麼）
- 物件建立的寫法（測試裡遊戲物件或場景是怎麼實例化的）
- Mock/stub 的寫法（依賴項是怎麼被替換的）

這樣可以確保產生的 helper 符合專案既有的風格，而不是一個通用模板。

也要讀：
- `design/gdd/systems-index.md` — 知道有哪些系統
- 範圍內的 GDD — 了解需要測試哪些資料型別和數值。要分段讀：先用 Grep 工具（pattern `^#`，content mode）找出需要的標題，再用 offset 和 limit 讀那些範圍。
- `docs/architecture/tr-registry.yaml` — 把需求對應到被測試的系統

---

## 4. Generate Engine-Specific Helpers

### Godot 4 (GDUnit4 / GDScript)

> **下面範例裡的 `FAIL_IF(...)` 是 PLACEHOLDER，不是 API。** 它標出在輸出任何這些程式碼之前，你必須依照 §2 的規則，從專案實際的測試框架解析出來的那一行。換成框架真正的失敗呼叫，也就是**向執行器登記一個失敗、並讓 suite 繼續往下跑**的那種形式，然後刪掉那行標記註解。
>
> **它刻意不寫成 `assert_that`、`assert_eq` 或 `assert_true`。** 這三個在 repo 裡的某處都有出現，而且彼此不一致，**GdUnit4 的 API 又不在 `docs/engine-reference/` 的涵蓋範圍內**，所以在這裡寫其中任何一個，就是在一個整個任務就是要阻止人這樣做的檔案裡，斷言一個這個 repo 沒辦法查證出處的 API。如果你沒辦法確認設定的框架的正確呼叫方式，§2 已經告訴你答案：**不要產生 helper。** 沒解決的 `FAIL_IF` 跑到磁碟上是 bug；缺少一個 helper 只是一件待辦。
>
> 範例也必須遵守 §2：這裡出現一個裸的 `assert()`，就會是 §2 禁止的那個確切形式，而且在 §2 禁止它之後六十行就出現。用文字寫下的規則，除非有人去強制，否則碰不到它自己的範例。

**基礎 helper**（`tests/helpers/game_assertions.gd`）：

```gdscript
## Game-specific assertion utilities for [Project Name] tests.
## Domain-specific helpers built on the project's test framework.
##
## Usage (static — no instance needed):
##   GameAssertions.assert_in_range(entity.health, 0, entity.max_health, "health")

class_name GameAssertions
extends RefCounted

## Assert a value is within the inclusive range [min_val, max_val].
## Use for any formula output that has defined bounds in a GDD.
static func assert_in_range(
    value: float,
    min_val: float,
    max_val: float,
    label: String = "value"
) -> void:
    # FRAMEWORK ASSERT — resolve per the rule above; do not emit `assert()`.
    FAIL_IF(
        not (value >= min_val and value <= max_val),
        "%s %.2f is outside expected range [%.2f, %.2f]" % [label, value, min_val, max_val]
    )

## Assert a signal was emitted during a callable block.
## Usage: assert_signal_emitted(entity, "health_changed", func(): entity.take_damage(10))
static func assert_signal_emitted(
    obj: Object,
    signal_name: String,
    action: Callable
) -> void:
    # A lambda captures a local by value: `emitted = true` inside it would set
    # the lambda's own copy. Mutate a Dictionary it shares instead. `...args`
    # (4.5+) accepts a signal with any number of arguments.
    var state := {"emitted": false}
    obj.connect(signal_name, func(...args): state.emitted = true)
    action.call()
    # FRAMEWORK ASSERT — resolve per the rule above; do not emit `assert()`.
    FAIL_IF(not state.emitted, "Expected signal '%s' to be emitted, but it was not." % signal_name)

## Assert that a callable does NOT emit a signal.
static func assert_signal_not_emitted(
    obj: Object,
    signal_name: String,
    action: Callable
) -> void:
    var state := {"emitted": false}  # a Dictionary, as above
    obj.connect(signal_name, func(...args): state.emitted = true)
    action.call()
    # FRAMEWORK ASSERT — resolve per the rule above; do not emit `assert()`.
    FAIL_IF(state.emitted, "Expected signal '%s' NOT to be emitted, but it was." % signal_name)

## Assert a node exists at path within a parent.
static func assert_node_exists(parent: Node, path: NodePath) -> void:
    # FRAMEWORK ASSERT — resolve per the rule above; do not emit `assert()`.
    FAIL_IF(
        not parent.has_node(path),
        "Expected node at path '%s' to exist." % str(path)
    )
```

**Factory helper**（`tests/helpers/game_factory.gd`）：

```gdscript
## Factory functions for creating test game objects.
## Returns minimal objects configured for unit testing (no scene tree required).
##
## Usage: var player = GameFactory.make_player(health: 100)

class_name GameFactory
extends RefCounted

## Create a minimal player-like object for testing.
## Override fields as needed.
static func make_player(health: int = 100) -> Node:
    var player = Node.new()
    player.set_meta("health", health)
    player.set_meta("max_health", health)
    return player
```

**Scene helper**（`tests/helpers/scene_runner_helper.gd`）：

```gdscript
## Utilities for scene-based integration tests. For input simulation and frame
## stepping, use gdUnit4's own `scene_runner()` from inside the suite.

class_name SceneRunnerHelper
extends RefCounted

## Load a scene under `host` — the calling test suite, which passes `self` —
## and wait one frame for _ready() to complete. A plain class, so the runner
## never discovers this file as a suite with zero tests.
static func load_scene_and_wait(host: Node, scene_path: String) -> Node:
    var scene: Node = load(scene_path).instantiate()
    host.add_child(scene)
    await host.get_tree().process_frame
    return scene
```

---

### Unity (NUnit / C#)

**基礎 helper**（`Assets/Tests/EditMode/Helpers/GameAssertions.cs`）：

```csharp
using NUnit.Framework;
using UnityEngine;

/// <summary>
/// Game-specific assertion utilities for [Project Name] tests.
/// Extends NUnit's Assert with domain-specific helpers.
/// </summary>
public static class GameAssertions
{
    /// <summary>
    /// Assert a value is within an inclusive range [min, max].
    /// Use for any formula output defined in GDD Formulas sections.
    /// </summary>
    public static void AssertInRange(float value, float min, float max, string label = "value")
    {
        Assert.That(value, Is.InRange(min, max),
            $"{label} ({value:F2}) is outside expected range [{min:F2}, {max:F2}]");
    }

    /// <summary>Assert a UnityEvent or C# event was raised during an action.</summary>
    public static void AssertEventRaised(ref bool wasCalled, System.Action action, string eventName)
    {
        wasCalled = false;
        action();
        Assert.IsTrue(wasCalled, $"Expected event '{eventName}' to be raised, but it was not.");
    }

    /// <summary>Assert a component exists on a GameObject.</summary>
    public static void AssertHasComponent<T>(GameObject obj) where T : Component
    {
        var component = obj.GetComponent<T>();
        Assert.IsNotNull(component,
            $"Expected GameObject '{obj.name}' to have component {typeof(T).Name}.");
    }
}
```

**Factory helper**（`Assets/Tests/EditMode/Helpers/GameFactory.cs`）：

```csharp
using UnityEngine;

/// <summary>
/// Factory methods for creating minimal test objects without loading scenes.
/// </summary>
public static class GameFactory
{
    /// <summary>Create a minimal GameObject with a named component for testing.</summary>
    public static GameObject MakeGameObject(string name = "TestObject")
    {
        var go = new GameObject(name);
        return go;
    }

    /// <summary>
    /// Create a ScriptableObject of type T for data-driven tests.
    /// Dispose with Object.DestroyImmediate after test.
    /// </summary>
    public static T MakeScriptableObject<T>() where T : ScriptableObject
    {
        return ScriptableObject.CreateInstance<T>();
    }
}
```

---

### Unreal Engine (C++)

**基礎 helper**（`Source/<Module>/Private/Tests/Helpers/GameTestHelpers.h`）：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"

/**
 * Game-specific assertion macros and helpers for [Project Name] automation tests.
 * Include in any test file that needs domain-specific assertions.
 *
 * Usage:
 *   GAME_TEST_ASSERT_IN_RANGE(TestName, DamageValue, 10.0f, 50.0f, TEXT("Damage"));
 */

// Assert a float value is within inclusive range [Min, Max]
#define GAME_TEST_ASSERT_IN_RANGE(TestName, Value, Min, Max, Label) \
    TestTrue( \
        FString::Printf(TEXT("%s (%.2f) in range [%.2f, %.2f]"), Label, Value, Min, Max), \
        (Value) >= (Min) && (Value) <= (Max) \
    )

// Assert a UObject pointer is valid (not null, not garbage collected)
#define GAME_TEST_ASSERT_VALID(TestName, Ptr, Label) \
    TestTrue( \
        FString::Printf(TEXT("%s is valid"), Label), \
        IsValid(Ptr) \
    )

// Assert an Actor is in the world (spawned successfully)
#define GAME_TEST_ASSERT_SPAWNED(TestName, ActorPtr, ClassName) \
    TestNotNull( \
        FString::Printf(TEXT("Spawned actor of class %s"), TEXT(#ClassName)), \
        ActorPtr \
    )

/**
 * Helper to create a minimal test world.
 * Remember to call World->DestroyWorld(false) in teardown.
 */
namespace GameTestHelpers
{
    inline UWorld* CreateTestWorld(const FString& WorldName = TEXT("TestWorld"))
    {
        UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
        FWorldContext& WorldContext = GEngine->CreateNewWorldContext(EWorldType::Game);
        WorldContext.SetCurrentWorld(World);
        return World;
    }
}
```

---

## 5. Generate System-Specific Helpers

對 `[system-name]` 或 `all` 模式，為每個系統產生一個 helper：

只讀這件事需要的 GDD 章節：`Grep pattern="^## ([0-9]+\. )?(Formulas|Edge Cases|Detailed Rules|Detailed Design)" path="design/gdd/[system].md" output_mode="content" -A 30`（那個可選的數字，是用來比對反向文件化 GDD 的 `## 4. Formulas`），不要整份讀（每個同類 skill 都是用 grep 抓 GDD 的章節；在 `all` 模式下，整份讀會在每個系統 400 多行的 GDD 上被放大好幾倍）。擷取：
- 資料型別（實體類型、component 名稱）
- 公式變數與它們的上下界
- Edge Cases 裡提到的常見測試情境

產生 `tests/helpers/[system]_factory.[ext]`，裡面是專屬於該系統物件的 factory 函式。

`combat` 系統的範例寫法（Godot/GDScript）：

```gdscript
## Factory and assertion helpers for Combat system tests.
## Generated by /test-helpers combat on [date].
## Based on: design/gdd/combat.md

class_name CombatTestFactory
extends RefCounted

const DAMAGE_MIN := 0
const DAMAGE_MAX := 999  # From GDD: damage formula upper bound

## Create a minimal attacker object for damage formula tests.
static func make_attacker(attack: float = 10.0, crit_chance: float = 0.0) -> Node:
    var attacker = Node.new()
    attacker.set_meta("attack", attack)
    attacker.set_meta("crit_chance", crit_chance)
    return attacker

## Create a minimal target object for damage receive tests.
static func make_target(defense: float = 0.0, health: float = 100.0) -> Node:
    var target = Node.new()
    target.set_meta("defense", defense)
    target.set_meta("health", health)
    target.set_meta("max_health", health)
    return target

## Assert damage output is within GDD-specified bounds.
static func assert_damage_in_bounds(damage: float) -> void:
    GameAssertions.assert_in_range(damage, DAMAGE_MIN, DAMAGE_MAX, "damage")
```

---

## 6. Write Output

呈現一份將要建立的東西的摘要：

```
## Test Helpers to Create

Base helpers (engine: [engine], helper root: [helper root]):
- [helper root]/game_assertions.[ext]
- [helper root]/game_factory.[ext]
[engine-specific extras]

System helpers ([mode]):
- [helper root]/[system]_factory.[ext]  ← from [system] GDD
```

問：「May I write these helper files to `[helper root]`?」

**絕對不要覆蓋既有檔案。** 如果檔案已經存在，就回報：
「Skipping `[path]` — already exists. Remove the file manually if you want it
regenerated.」

寫完之後：Verdict: **COMPLETE** — helper files created.

「Helper files created. To use them in a test:
- Godot: `class_name` is auto-imported — no explicit import needed
- Unity: Add `using` directive or reference the test assembly
- Unreal: `#include \"Tests/Helpers/GameTestHelpers.h\"` (from inside the module)」

---

## Collaborative Protocol

- **絕對不要覆蓋既有的 helper**：它們可能含有手寫的客製內容。只產生還不存在的新檔案
- **產生的程式碼只是起點**：產生的 factory 函式為了簡單用 metadata 的寫法；程式碼存在之後，再依實際的類別結構調整
- **Helper 應該反映 GDD**：helper 裡的上下界與常數，要能追溯到 GDD 的 Formulas 章節，不是自己編的數值
- **寫入前要先問**：在 `tests/` 底下建立檔案之前，一定要先確認

## Next Steps

- 如果測試框架還沒建好骨架，跑 `/test-setup`。
- 用 `/dev-story` 實作 story：helper 能減少新測試檔案的樣板程式碼。
- 跑 `/skill-test` 驗證其他可能需要 helper 涵蓋的 skill。
