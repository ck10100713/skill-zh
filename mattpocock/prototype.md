---
layout: "default"
skill: "prototype"
author: "Matt Pocock"
category: "設計與前端"
summary: "做用完即丟的 prototype 回答設計問題"
source: "https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: prototype
description: 做一個用完即丟的 prototype 來回答設計問題。當使用者想確認某個狀態模型或邏輯感覺對不對，或想探索 UI 該長什麼樣子時使用。
---

# Prototype

prototype 是**用來回答一個問題的用完即丟程式碼**。問題決定它的形狀。

## 選一條分支

從使用者的 prompt、周圍的程式碼來判斷正在回答哪個問題，使用者在的話也可以直接問：

- **「這個邏輯 / 狀態模型感覺對嗎？」** → [LOGIC.md](LOGIC.md)。做一個可分享的單一 HTML 檔（自由操作的按鈕加上分頁式的引導導覽），把 state machine 推過那些光靠紙上推演很難想清楚的情況，而且非開發者也能自己操作。
- **「這個該長什麼樣子？」** → [UI.md](UI.md)。在單一路由上產生好幾個截然不同的 UI 變體，用 URL search param 和浮動的底部工具列來切換。

兩條分支產出的東西差很多，選錯會讓整個 prototype 白做。如果問題真的有歧義、又聯絡不到使用者，就預設選比較符合周圍程式碼的那條分支（後端 module → 邏輯；頁面或 component → UI），並在 prototype 最上面寫明這個假設。

## 兩條分支都適用的規則

1. **一開始就是用完即丟，而且清楚標示。** prototype 的程式碼放在靠近實際會用到的地方（在它正在做 prototype 的那個 module 或頁面旁邊），讓 context 一目了然，但命名要讓隨便看一眼的人就知道這是 prototype，不是 production。用完即丟的 UI 路由，遵守專案既有的路由慣例；不要發明新的頂層結構。
2. **跑起來要很簡單。** UI prototype 從專案的 task runner 一個指令就能啟動：`pnpm <name>`、`python <path>`、`bun <path>` 等等。邏輯 demo 是使用者雙擊就能開的單一 HTML 檔。不管哪種，都不需要動腦就能啟動。
3. **預設不做 persistence。** 狀態放在記憶體。persistence 是 prototype 要_檢驗_的東西，不是它該依賴的東西。如果問題明確牽涉到資料庫，就用一個暫時的 DB 或本地檔案，名字要清楚標示「PROTOTYPE, wipe me」。
4. **跳過潤飾。** 不寫測試，除了讓 prototype _能跑_ 之外不做錯誤處理，不做抽象。重點是快速學到東西。
5. **把狀態亮出來。** 每個動作之後（邏輯）或每次切換變體時（UI），印出或渲染完整的相關狀態，讓使用者看得到什麼變了。
6. **做完要留存。** 把驗證過的決策併進真正的程式碼，然後把 prototype 本身留存成**第一手來源**：commit 到一個用完即丟的 branch，不要進 main，並在實作的 issue 上留一個指向那個 branch 的 context 指標。答案也要留存（結論，以及它解決的問題），放在 issue 或 commit 裡。main branch 只留下驗證過的決策。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered, using the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file (free-play buttons plus tabbed guided walkthroughs) that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

The two branches produce very different artifacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious, but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner: `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file the user double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE, wipe me" name.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Capture it when done.** Fold any validated decision into the real code, then capture the prototype itself as a **primary source**: commit it to a throwaway branch, out of main, and leave a context pointer to that branch on the implementation issue. Capture the answer too (the verdict and the question it settled) in the issue or a commit. The main branch keeps only the validated decision.
~~~~~
{% endraw %}

</section>
</div>
