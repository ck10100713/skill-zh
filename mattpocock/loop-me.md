---
layout: "default"
skill: "loop-me"
author: "Matt Pocock"
category: "規劃與釐清"
summary: "拷問你生活中的重複模式，寫成 workflow spec"
source: "https://github.com/mattpocock/skills/blob/main/skills/in-progress/loop-me/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: loop-me
description: 針對我想在這個 workspace 裡建立的 workflow 的 spec 來拷問我。
disable-model-invocation: true
argument-hint: "A workflow to design, or nothing to go find one"
---

進行一場有狀態的 `/grilling` session，唯一的產出是 **workflow** spec。沿用 grilling 的紀律（毫不留情、一次問一回合、每題附建議答案），目標和詞彙見下面。隨著 grilling 釐清事情，建立、編輯、刪除 spec。

## loop 的視角

**loop** 是使用者生活中反覆出現的模式：他的職涯、他的一週、他的早晨，或某個重複的單一活動。把生活看成 loop 套 loop，就會發現這些活動其實有多可預測，這也是它們值得**委派**的原因。用這個視角去找值得寫成 spec 的 loop，並提出使用者沒注意到的 loop。

**workflow** 是一個 loop 的 spec，把它落實。你在 loop 上執行一個 workflow：loop 就是它執行中的實例。workflow 放在 `workflows/*.md`，是唯一的事實來源。

## 詞彙

這是一套共用語言，只在 workflow 用得到的時候才拿出來用，絕對不是檢查清單。**不強制任何結構**：除非 grilling 顯示需要，否則 workflow 不需要 AI、不需要 checkpoint、也不需要排程。

- **Trigger**：每次執行由什麼觸發，可以是**事件**（新的 email、新的 issue）或**排程**（每天早上）。事件觸發通常比較有效率。
- **Checkpoint**：human-in-the-loop 的節點，請使用者驗證或做決定。有些 workflow 沒有 checkpoint，全自動跑；有些完全不用 AI。
- **Push right**：把 checkpoint 盡可能往後推。在找人類介入之前先做完最多的工作，讓他們只被問一次、問得晚、而且所有東西都已經備好。
- **Brief**：checkpoint 呈現的東西，是精簡、能直接拿來做決定的摘要（產出了什麼、為什麼、以及往下連到資產本身的連結），絕對不是原始輸出。使用者讀的是 brief，不是草稿。review 的速度是關鍵。

## 完成的定義

一份 workflow spec 完成的標準是：實作的 agent 可以一個問題都不用問就把它做出來。一直 grill 到那個程度；只要還有問題就不算完成。

## workspace

- `workflows/*.md`：每個 workflow 一份 spec。
- `NOTES.md`：關於使用者世界的原始筆記，包括他用的工具、他處理的管道，以及他對這兩者的專屬用語。內容是空的或太薄時，在寫任何 spec 之前先訪談他的世界。模糊的詞一浮現就釐清成標準用語，並記在這裡。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: loop-me
description: Grill me about specs for the workflows I want to build, within this workspace.
disable-model-invocation: true
argument-hint: "A workflow to design, or nothing to go find one"
---

Run a stateful `/grilling` session whose only output is **workflow** specs. Use the grilling discipline (relentless, a round of questions at a time, a recommended answer attached to each) aimed at the vocabulary and goal below. Create, edit, and delete specs as the grilling resolves things.

## The loop lens

A **loop** is a recurring pattern in the user's life: their career, their week, their morning, a single repeated activity. Picturing a life as loops within loops reveals how predictable its activities really are, which is what makes them worth **delegating**. Use the lens to find loops worth specifying, and propose ones the user hasn't noticed.

A **workflow** is the spec of one loop, made real. You run a workflow on a loop: the loop is its running instantiation. Workflows live in `workflows/*.md` and are the source of truth.

## Vocabulary

A shared language, reached for only when a workflow calls for it: never a checklist. **Mandate nothing structural**: a workflow needs no AI, no checkpoint, and no schedule unless the grilling shows it does.

- **Trigger**: what fires each run, an **event** (a new email, a new issue) or a **schedule** (every morning). Event-triggering is usually the more efficient.
- **Checkpoint**: a human-in-the-loop point where the user is asked to verify or decide. Some workflows have none and run autonomously; some use no AI at all.
- **Push right**: defer the checkpoint as far as it will go. Do maximal work before involving the human, so they are asked once, late, with everything prepared.
- **Brief**: what a checkpoint presents, a tight, decision-ready summary (what was produced, why, and a link down to the asset itself), never the raw output. The user reads a brief, not a draft. Speed of review is imperative.

## Definition of done

A workflow spec is done when an implementer agent could build it without asking a single question. Grill until then; nothing is done while a question remains.

## The workspace

- `workflows/*.md`: one spec per workflow.
- `NOTES.md`: raw notes on the user's world, the tools they use, the channels they process, and their own terminology for both. When it is empty or thin, interview them about their world before specifying anything. Sharpen fuzzy terms into canonical ones as they surface, and record them here.
~~~~~
{% endraw %}

</section>
</div>
