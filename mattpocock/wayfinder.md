---
layout: "default"
skill: "wayfinder"
author: "Matt Pocock"
category: "規劃與釐清"
summary: "把大到一個 session 裝不下的工作畫成決策地圖"
source: "https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: wayfinder
description: 把一大塊工作（一個 agent session 裝不下的）規劃成 issue tracker 上由決策 ticket 組成的共享地圖，一次解決一張，直到通往目的地的路清楚為止。
disable-model-invocation: true
---

一個鬆散的想法來了，大到一個 agent session 裝不下，還被迷霧包著：從這裡到**目的地**的路還看不見。Wayfinding 的重點是找出那條路，不是衝向目的地。這個 skill 把路畫成 repo 的 issue tracker 上的**共享地圖**，然後一次處理一張**決策 ticket**（解決之後得到的是一個決策的問題，不是要執行的建置切片），直到路線清楚為止。

目的地依每次的投入而不同，替它命名是繪圖的第一個動作：它會塑造每一張 ticket。它可能是一份要交出去反覆修改的 spec、規劃開始前要鎖定的一個決策，或是像資料結構遷移那樣原地做出的改動。這張地圖不限領域：工程工作、課程內容，只要符合這個形狀都行。

## 規劃，不要做

Wayfinder 預設是**規劃**：每張 ticket 解決一個決策，當路清楚了、沒有任何東西需要在有人動手做之前決定時，地圖就完成了。想直接動手做的衝動，通常就是你已經走到地圖邊緣、該交接的訊號。某次投入可以在它的 **Notes** 裡覆寫這點，把執行也帶進地圖本身，但除非這樣，否則要產出決策，不要產出成品。

## 用名字稱呼

每張地圖和每張 ticket 都是一個 issue，所以都有**名字**：它的標題。在人類會讀的所有東西裡（敘述、地圖的 Decisions-so-far），都要用那個名字稱呼它，絕對不要只用單獨的 id、編號或 slug。一整排的 `#42, #43, #44` 看不懂；名字一眼就讀得出來。id 和 URL 並沒有消失；名字包著它的連結，但它們是放在名字_裡面_，絕不取代名字。

## 地圖

地圖是這個 repo 的 issue tracker 上的單一 issue，標上 `wayfinder:map` 標籤，是正式的產出物。它的 ticket 是地圖的子 issue。

地圖是**索引**，不是儲存處。它列出已做出的決策，並指向存放細節的 ticket；一個決策只存在一個地方，也就是它的 ticket，所以地圖絕不重述它，只摘要要點並附連結。

**地圖、它的子 ticket、blocking 和前線查詢實際上放在哪裡，取決於 tracker。** issue tracker 應該已經提供給你了。如果沒有，叫使用者去跑 `/setup-matt-pocock-skills`。查閱 tracker 文件的「Wayfinding operations」一節，了解_這個_ repo 怎麼表達它們。如果沒有提供 tracker，就預設用本地 markdown tracker。

### 地圖本文

整張地圖的低解析度版本，每個 session 載入一次。未解決的 ticket **不**列在這裡：它們是未關閉的子 issue，用查詢找出來。

```markdown
## Destination

<抵達這張地圖終點時是什麼樣子：這次投入正在找路前往的 spec、決策或改動。一到兩行；每個 session 在挑 ticket 之前都先對齊它。>

## Notes

<領域；每個 session 都該參考的 skill；這次投入的長期偏好>

## Decisions so far

<!-- 索引：每張已關閉的 ticket 一行，足夠判斷是否相關，再點開連結看 ticket 裡的細節 -->

- [<已關閉的 ticket 標題>](link): <答案的一句話摘要>

## Not yet specified

<!-- 見「戰爭迷霧」：範圍內但還沒辦法開成 ticket 的迷霧；隨著前線推進而升格 -->

## Out of scope

<!-- 見「範圍外」：被判定在目的地之外的工作；已關閉，永遠不會升格 -->
```

### Ticket

每張 ticket 是地圖的**子 issue**；tracker 的 issue id 就是它的身分。它的本文就是問題，大小要能放進一個 100K token 的 agent session：

```markdown
## Question

<這張 ticket 要解決的決策或調查>
```

每張 ticket 都帶有一個 `wayfinder:<type>` 標籤，是 `research`、`prototype`、`grilling`、`task` 其中之一（見 [Ticket 類型](#ticket-types)）。`wayfinder:` 標籤是地圖和它的 ticket 唯一會帶的標籤，絕不帶像 `ready-for-agent` 這種 triage 標籤：它們是決策，不是實作工作。

session 要**認領**一張 ticket，做法是把它指派給主導這張地圖的開發者，而且要**最先**做，在任何工作之前，這樣同時進行的 session 才會跳過它。那個被指派者_就是_認領：未關閉又沒有指派的 ticket 就是未被認領。

blocking 使用 tracker 的**原生**依賴關係：這很重要，因為它會在 tracker 自己的 UI 裡_視覺化_地顯示前線，人類不用打開地圖就能看到哪些可以接手。只有缺少原生 blocking 的 tracker，才退而使用本文慣例。當擋住一張 ticket 的每張 ticket 都已關閉，這張 ticket 就是**未被擋住**；**前線**就是未關閉、未被擋住、未被認領的子項，也就是已知世界的邊緣。

答案不屬於本文的一部分；它是在解決時記錄的（見[處理地圖](#work-through-the-map)）。解決 ticket 時產生的資產，用連結從 issue 連過去，不要貼進來。

## Ticket 類型

每張 ticket 不是 **HITL**（human in the loop，_跟_一個能為自己發言的人類一起處理），就是 **AFK**，由 agent 自己單獨推進。HITL ticket 只能透過那場即時的交流來解決；agent 絕不替人類那一方代答（一個 grilling agent 自問自答，就是破壞了這一點）。

- **Research**（AFK）：閱讀文件、第三方 API，或像知識庫這樣的本地資源，找出某個決策在等的事實。由呼叫 Skill 工具使用 "research" 的 subagent 解決。需要目前工作目錄以外的知識時使用。
- **Prototype**（HITL）：做一個便宜、粗糙、具體的東西讓大家有反應可以討論（大綱、粗略的版本、樁，或 UI/邏輯程式碼），藉此提高討論的擬真度，做法是呼叫 Skill 工具使用 "prototype"。把 prototype 當成資產連結起來。當「它該長什麼樣」或「它該怎麼運作」是關鍵問題時使用。
- **Grilling**（HITL）：對話。預設情況。一律用 Skill 工具呼叫兩次，分別是 "grilling" 和 "domain-modeling"。
- **Task**（HITL 或 AFK）：在能做出_決策_之前必須先完成的手動工作：沒有東西要決定、做 prototype 或研究，但討論被卡住，直到它做完。例如註冊一個服務才能評判它的 API、開通權限、搬移資料才看得出它的形狀。這是唯一一種真的去_做_、而不是去決定的類型，它之所以有存在的位置，是因為它能解開一個決策，不是因為它交付了目的地。agent 做得到的就自己單獨推進（AFK）；否則就交給人類一份精確的檢查清單（HITL）。工作做完就算解決；答案要記錄做了什麼，以及後續 ticket 所依賴的任何結果事實（憑證的位置、新的 URL、資料列數）。

## 戰爭迷霧

地圖是_刻意_不完整的：看不見的東西就不要畫。在有效的 ticket 之外是**戰爭迷霧**：你看得出會來、但還沒辦法釘死的決策和調查的模糊輪廓，因為它們懸在仍然未解的問題上。解決一張 ticket 會撥開它前方的迷霧，把現在可以明確寫出來的部分升格成新的 ticket，一次一張，直到通往目的地的路清楚、沒有任何 ticket 剩下。

地圖的 **Not yet specified** 一節就是寫下這個模糊輪廓的地方：猜測中的問題、之後要回頭看的區域。它是_通往_目的地的、尚未發現的前線：這裡的一切都在範圍內，只是還不夠清晰到可以開 ticket。能寫多鬆就寫多鬆、能寫多完整就寫多完整，視輪廓而定；它同時也是給協作者看的路標，讓他們知道這次投入的方向。

**是迷霧還是 ticket？** 判斷標準是你現在能不能精確地陳述這個問題，_不是_你現在能不能回答它。

- **開成 ticket 的時機**：問題已經很清晰，就算它被擋住、你現在還不能動手。
- **放進 Not yet specified 的時機**：你還沒辦法把它表述得那麼清晰。不要把迷霧預先切成 ticket 大小的碎片：它比 ticket 粗，一塊迷霧在前線推進到它那裡時，可能升格成好幾張 ticket，也可能一張都沒有。

**Not yet specified** 不包含已經決定的（Decisions so far）、已經是有效 ticket 的，以及範圍外的（下一節）。

## 範圍外

迷霧只會朝著目的地聚集。目的地決定了範圍，所以在它之外的工作是**範圍外**：它不是迷霧，也不屬於 **Not yet specified**。它在地圖上有自己的 **Out of scope** 一節：你已經有意識地排除在_這次_投入之外的工作。把它放到這裡的是範圍，不是清晰度。

範圍外的工作永遠不會升格（前線止於目的地），所以只有在目的地被重新劃定時它才會回來，而且是當作新的投入，不是接續。

把某件事判為範圍外是一個劃定範圍的動作，不是路線上的一步。當一張已經存在的 ticket 結果落在目的地之外（繪圖時範圍抓錯，或是某個解決結果讓它現形），就**把它關閉**（已關閉的 ticket 毫無疑問不在前線上），並在 **Out of scope** 一節留一行：要點加上為什麼它在範圍外，連結到已關閉的 ticket。它不放進 **Decisions so far**，那裡記錄的是實際走過的路線；範圍邊界不是路線上的一步。

## 呼叫方式

兩種模式。不管哪種，**一個 session 絕對不要解決超過一張 ticket**，research ticket 除外。

### 繪製地圖

使用者帶著一個鬆散的想法來呼叫。

1. **替目的地命名。** 用 Skill 工具呼叫兩次，分別是 "grilling" 和 "domain-modeling"，釘出這張地圖正在找路前往的東西：spec、決策或改動。目的地決定範圍，所以要先定下來。
2. **畫出前線。** 再 grill 一次，這次是**廣度優先**：在整個空間裡展開，而不是深入任何單一條線，找出未決的決策和現在就能接手的第一步。**如果這樣找不出任何迷霧**（通往目的地的路已經很清楚，整段旅程小到一個 session 就裝得下），你就不需要地圖。停下來，問使用者想怎麼進行。
3. **建立地圖**（標籤 `wayfinder:map`）：填好 Destination 和 Notes，Decisions-so-far 留空，把迷霧勾勒進 **Not yet specified**。
4. **把現在能明確寫出來的 ticket 建成**地圖的子 issue，然後在**第二輪**接上 blocking 關係（issue 要先有 id 才能互相參照）。交叉參照也在那一輪寫，用真正的 id：佔位用的 `#<n>` 會自動連到不相干的 issue。接線會把它們分成前線和被擋住的；所有你還不能明確寫出來的，都留在迷霧裡：**Not yet specified** 一節。
5. **啟動 research 的 subagent。** 對你剛建立的每張 `research` ticket，啟動一個有全新 context window 的 subagent，呼叫 Skill 工具使用 "research" 來平行解決它，把發現記錄在用完即丟的 `research/<name>` branch 上，並從 ticket 留一個 context 指標。推送 branch，但不要開 PR：它永遠不會被 merge。
6. 停：繪圖是一個 session 的工作；它不親手解決任何東西。

### 處理地圖

使用者帶著一張地圖（URL 或編號）來呼叫。ticket 是**選填**的：沒有指定時，由你挑下一個決策，不是使用者。

1. 載入**地圖**：低解析度的視圖，不是每張 ticket 的本文。
2. 選 ticket。如果使用者指定了一張，就用它。否則依序取前線的第一張 ticket。**認領它**：在任何工作之前先指派給自己。
3. 依它的 `wayfinder:<type>` 標籤所指的類型來解決它（見 [Ticket 類型](#ticket-types)）。要讀標籤，不只是本文：本文絕不會寫明類型。**需要時放大**：隨時抓取任何相關或已關閉 ticket 的完整本文；對 `## Notes` 區塊點名的 skill，用 Skill 工具呼叫它們。有疑問就用 Skill 工具呼叫兩次，分別是 "grilling" 和 "domain-modeling"。
4. 記錄解決結果：把答案發成**解決留言**、**關閉** issue，並**在地圖的 Decisions-so-far 附上一個 context 指標**。
5. 加入新浮現的 ticket（先建立再接線）；把答案讓它變得可以明確寫出來的迷霧升格，從 **Not yet specified** 清掉每塊升格的迷霧，讓它只以新的 ticket 存在。如果答案顯示某張 ticket（這一張或別張）落在目的地之外，就把它**判為範圍外**，而不是在路線上解決它。如果這個決策讓地圖的其他部分失效，就更新或刪掉那些 ticket。

使用者可能會平行執行未被擋住的 ticket，所以要預期其他 session 會同時在編輯 tracker。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: wayfinder
description: Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.
disable-model-invocation: true
---

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** on the repo's issue tracker, then works its **decision tickets** (questions whose resolution is a decision, not slices of a build to execute) one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting: it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic: engineering work, course content, whatever fits the shape.

## Plan, don't do

Wayfinder is **planning** by default: each ticket resolves a decision, and the map is done when the way is clear, with nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off. An effort can override this in its **Notes**, carrying execution into the map itself, but absent that, produce decisions, not deliverables.

## Refer by name

Every map and ticket is an issue, so it has a **name**: its title. In everything the human reads (narration, the map's Decisions-so-far), refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish; a name wraps its link, but they ride _inside_ the name, never stand in for it.

## The Map

The map is a single issue on this repo's issue tracker, labelled `wayfinder:map`, the canonical artifact. Its tickets are child issues of the map.

The map is an **index**, not a store. It lists the decisions made and points at the tickets that hold their detail; a decision lives in exactly one place, its ticket, so the map never restates it, only gists it and links.

**Where the map, its child tickets, blocking, and frontier queries physically live is tracker-specific.** The issue tracker should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`. Consult the tracker doc's "Wayfinding operations" section for how _this_ repo expresses them. If no tracker has been provided, default to the local-markdown tracker.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are **not** listed: they are open child issues, found by query.

```markdown
## Destination

<what reaching the end of this map looks like: the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a **child issue** of the map; the tracker's issue id is its identity. Its body is the question, sized to one 100K token agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

Each ticket carries a `wayfinder:<type>` label, one of `research`, `prototype`, `grilling`, `task` (see [Ticket Types](#ticket-types)). `wayfinder:` labels are the only labels a map and its tickets carry, never a triage label like `ready-for-agent`: they are decisions, not implementation work.

A session **claims** a ticket by assigning it to the dev driving the map, **first**, before any work, so concurrent sessions skip it. That assignee _is_ the claim: an open, unassigned ticket is unclaimed.

Blocking uses the tracker's **native** dependency relationship: essential because it renders the frontier _visually_ in the tracker's own UI, so the human sees what's takeable without opening the map. Only a tracker that lacks native blocking falls back to a body convention. A ticket is **unblocked** when every ticket blocking it is closed; the **frontier** is the open, unblocked, unclaimed children, the edge of the known.

The answer isn't part of the body; it's recorded on resolution (see [Work through the map](#work-through-the-map)). Assets created while resolving a ticket are linked from the issue, not pasted in.

## Ticket Types

Every ticket is either **HITL** (human in the loop, worked _with_ a human who speaks for themselves) or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).

- **Research** (AFK): Reading documentation, third-party APIs, or local resources like knowledge bases to surface a fact a decision waits on. Resolved by a subagent that calls the Skill tool with "research". Use when knowledge outside the current working directory is required.
- **Prototype** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to (an outline, a rough take, a stub, or UI/logic code) by calling the Skill tool with "prototype". Links the prototype as an asset. Use when "how should it look" or "how should it behave" is the key question.
- **Grilling** (HITL): Conversation. The default case. Always call the Skill tool twice, for "grilling" and "domain-modeling".
- **Task** (HITL or AFK): Manual work that must happen before a _decision_ can be made: nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that _does_ rather than decides, and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.

## Fog of war

The map is _deliberately_ incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war**: the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets, one at a time, until the way to the destination is clear and no tickets remain.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier _toward_ the destination: everything here is in scope, just not sharp enough to ticket. Write as loosely or as fully as the view allows; it doubles as a signpost for collaborators reading where the effort is headed.

**Fog or ticket?** The test is whether you can state the question precisely now, _not_ whether you can answer it now.

- **Ticket when** the question is already sharp, even if it's blocked and you can't act on it yet.
- **Not yet specified when** you can't yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces: it's coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

**Not yet specified** excludes what's already decided (Decisions so far), what's already a live ticket, and what's out of scope (the next section).

## Out of scope

Fog only ever gathers _toward_ the destination. The destination fixes the scope, so work beyond it is **out of scope**: it isn't fog, and it doesn't belong in **Not yet specified**. It gets its own **Out of scope** section on the map: work you've consciously ruled out of _this_ effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates (the frontier stops at the destination), so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination (mis-scoped in while charting, or exposed by a resolution), **close it** (a closed ticket is unambiguously off the frontier) and leave one line in the **Out of scope** section: the gist plus why it's out of scope, linking the closed ticket. It stays out of **Decisions so far**, which records the route actually walked; a scope boundary isn't a step on it.

## Invocation

Two modes. Either way, **never resolve more than one ticket per session**, with the exception of research tickets.

### Chart the map

User invokes with a loose idea.

1. **Name the destination.** Call the Skill tool twice, for "grilling" and "domain-modeling", to pin down what this map is finding its way to: the spec, decision, or change. The destination fixes the scope, so it's settled first.
2. **Map the frontier.** Grill again, **breadth-first** this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog** (the way to the destination is already clear, the whole journey small enough for one session), you don't need a map. Stop and ask the user how they'd like to proceed.
3. **Create the map** (label `wayfinder:map`): Destination and Notes filled in, Decisions-so-far empty, the fog sketched into **Not yet specified**.
4. **Create the tickets you can specify now** as child issues of the map, then wire blocking edges in a **second pass** (issues need ids before they can reference each other). Write cross-references in that pass too, with real ids: a placeholder `#<n>` auto-links to an unrelated issue. Wiring sorts them into the frontier and the blocked; everything you can't yet specify stays in the fog: the **Not yet specified** section.
5. **Fire the research subagents.** For each `research` ticket you just created, spin up a subagent with a fresh context window that calls the Skill tool with "research" to resolve it in parallel, capturing its findings on a throwaway `research/<name>` branch with a context pointer from the ticket. Push the branch but open no PR: it is never merged.
6. Stop: charting is one session's work; it hand-resolves nothing.

### Work through the map

User invokes with a map (URL or number). A ticket is **optional**: without one, you pick the next decision, not the user.

1. Load the **map**: the low-res view, not every ticket body.
2. Choose the ticket. If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it**: assign it to yourself before any work.
3. Resolve it as the type its `wayfinder:<type>` label names (see [Ticket Types](#ticket-types)). Read the label, not just the body: the body never states the type. **Zoom as needed**: fetch the full body of any related or closed ticket on demand; call the Skill tool for whichever skills the `## Notes` block names. If in doubt, call the Skill tool twice, for "grilling" and "domain-modeling".
4. Record the resolution: post the answer as a **resolution comment**, **close** the issue, and **append a context pointer** to the map's Decisions-so-far.
5. Add newly-surfaced tickets (create-then-wire); graduate any fog the answer has made specifiable, clearing each graduated patch from **Not yet specified** so it lives only as its new ticket. If the answer reveals that a ticket (this one or another) sits beyond the destination, **rule it out of scope** rather than resolving it on the route. If the decision invalidates other parts of the map, update or delete those tickets.

The user may run unblocked tickets in parallel, so expect other sessions to be editing the tracker concurrently.
~~~~~
{% endraw %}

</section>
</div>
