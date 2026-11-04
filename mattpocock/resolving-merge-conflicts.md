---
layout: "default"
skill: "resolving-merge-conflicts"
author: "Matt Pocock"
category: "設定與維護"
summary: "解 merge/rebase 衝突，保留雙方意圖不准 abort"
source: "https://github.com/mattpocock/skills"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: resolving-merge-conflicts
description: "當你需要解決進行中的 git merge/rebase 衝突時使用。"
---

1. **看目前的狀態**：merge/rebase 進行到哪了。檢查 git 歷史和有衝突的檔案。

2. **找出每個衝突的第一手來源。** 深入理解每個改動為什麼這樣做、原本的意圖是什麼。讀 commit message、看 PR、看原始的 issue/ticket。

3. **逐個 hunk 解決。** 盡量讓兩邊的意圖都保留。兩邊不相容時，選擇符合這次 merge 目標的那一邊，並記下取捨。**不要**發明新的行為。一定要解決，絕對不准 `--abort`。

4. 找出專案的**自動化檢查**並跑起來，通常是先 typecheck，再跑測試，最後 format。merge 弄壞的東西都要修好。

5. **完成 merge/rebase。** 全部 stage 起來並 commit。如果是 rebase，就一直 continue 到所有 commit 都 rebase 完。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict."
---

1. **See the current state** of the merge/rebase. Check git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

4. Discover the project's **automated checks** and run them — typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge/rebase.** Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.
~~~~~
{% endraw %}

</section>
</div>
