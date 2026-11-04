---
layout: "default"
skill: "tdd"
author: "Matt Pocock"
category: "測試與驗證"
summary: "紅綠迴圈、只在講好的 seam 上測、三種測試反模式"
source: "https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: tdd
description: 測試驅動開發。當使用者想先寫測試再做功能或修 bug、提到「red-green-refactor」，或想要整合測試時使用。
---

# 測試驅動開發

TDD 就是 red → green 的迴圈。這份 skill 是讓這個迴圈產出「值得留下的測試」的參考：什麼是好測試、測試該放哪、有哪些反模式，以及迴圈的規則。每一節在每一輪都適用：在迴圈開始前和進行中參考它們，不是做完才看。

探索 codebase 時，如果有 `GLOSSARY.md` 就讀一下，讓測試名稱和介面用詞跟專案的領域語言一致；也要尊重你正在動的那一區的 ADR。

## 什麼是好測試

測試透過公開介面驗證行為，而不是驗證實作細節。程式碼可以整個換掉，測試不該跟著變。好的測試讀起來像規格：「使用者可以用有效的購物車結帳」清楚告訴你有什麼能力存在，而且它撐得過重構，因為它不在乎內部結構。

範例見 [tests.md](tests.md)，mock 的準則見 [mocking.md](mocking.md)。

## Seam：測試放在哪

**seam** 是你測試時站的那條公開邊界：在這個介面上你可以觀察行為，而不用把手伸進內部。測試住在 seam 上，絕不對著內部實作。

**只在事先講好的 seam 上測試。** 寫任何測試之前，先寫下要測的 seam，並跟使用者確認。沒確認過的 seam 不寫測試。你不可能什麼都測，所以事先對齊 seam，才能讓測試的心力落在關鍵路徑和複雜邏輯上，而不是每個 edge case。

這樣問：「公開介面是什麼？我們該測哪些 seam？」每個提議的 seam 都附一行說明：它能抓到什麼、會漏掉什麼。

如果介面本身的形狀還有疑問（模組該多深、seam 該放哪、介面該暴露什麼），就用 Skill 工具呼叫 "codebase-design" 拿詞彙。它是 module、interface、depth、seam、adapter、leverage、locality 這些術語的共用來源，是拿來查的參考，不是要跑的流程。

## 反模式

- **跟實作綁死**：mock 內部協作者、測 private method，或透過旁門驗證（直接查資料庫，而不是用介面）。徵兆：你重構了、行為沒變，測試卻壞了。
- **套套邏輯**：assertion 用跟程式碼一樣的方式重算預期值（`expect(add(a, b)).toBe(a + b)`、用同樣方法手推出來的 snapshot、一個常數斷言等於它自己），所以它天生就會過，永遠不可能跟程式碼意見不同。預期值必須來自獨立的真相來源：已知正確的字面值、手算的範例、規格。
- **水平切片**：先把所有測試寫完，再寫所有實作。大批寫出來的測試驗證的是_想像中的_行為：你測的是東西的_形狀_，不是使用者看得到的行為，測試會對真正的改動變得遲鈍，而且你在理解實作之前就先綁定了測試結構。改用**垂直切片**：一個測試 → 一段實作 → 重複，每個測試都是一發**曳光彈**，根據上一輪學到的東西調整。

## 迴圈的規則

- **先紅再綠。** 先寫會失敗的測試，然後只寫剛好能讓它通過的程式碼。不要預先為未來的測試鋪路，也不要加臆測出來的功能。
- **一次一片。** 每一輪：一個 seam、一個測試、一段最小實作。
- **重構不屬於這個迴圈。** 它屬於 review 階段（見 `code-review` skill），不屬於 red → green 的實作循環。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: tdd
description: Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.
---

# Test-Driven Development

TDD is the red → green loop. This skill is the reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle: consult them before and during the loop, not after.

When exploring the codebase, read `GLOSSARY.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification: "user can checkout with valid cart" tells you exactly what capability exists, and it survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. You can't test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?" Give each proposed seam a one-line note on what it catches and what it misses.

When the shape of that interface is itself in question (how deep the module is, where the seam belongs, what the interface should expose), call the Skill tool with "codebase-design" for the vocabulary. It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.

## Anti-patterns

- **Implementation-coupled**: mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological**: the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth: a known-good literal, a worked example, the spec.
- **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to the review stage (see the `code-review` skill), not the red → green implementation cycle.
~~~~~
{% endraw %}

</section>
</div>
