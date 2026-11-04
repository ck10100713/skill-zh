---
name: click-path-audit
description: "把每個面向使用者的按鈕/觸點，從頭到尾追蹤它完整的狀態變更順序，找出那種各個函式單獨看都正常、但彼此互相抵銷、產生錯誤的最終狀態，或讓 UI 停在不一致狀態的 bug。適用於：系統化除錯沒找到 bug、但使用者回報按鈕壞掉，或是任何動到共用 state store 的大型重構之後。"
metadata:
  origin: community
---

# /click-path-audit — Behavioural Flow Audit

找出靜態讀程式碼會漏掉的 bug：state 互動的副作用、連續呼叫之間的 race condition，以及悄悄把彼此的效果抵銷掉的 handler。

## The Problem This Solves

傳統的除錯會檢查：
- 函式存在嗎？（少了接線）
- 會當掉嗎？（runtime 錯誤）
- 回傳的型別對嗎？（資料流）

但它**不會**檢查：
- **最終的 UI 狀態，跟按鈕標籤承諾的一樣嗎？**
- **函式 B 有沒有悄悄把函式 A 剛做的事還原？**
- **共用 state（Zustand/Redux/context）有沒有副作用，把原本要做的動作抵銷掉？**

真實的例子：「New Email」按鈕先呼叫 `setComposeMode(true)`，再呼叫 `selectThread(null)`。兩個各自都正常。但 `selectThread` 有個副作用，會把 `composeMode` 重設成 `false`。結果按鈕什麼都沒做。系統化除錯找到了 54 個 bug，這一個漏掉了。

---

## How It Works

對目標區域裡的**每一個**互動觸點：

```
1. IDENTIFY the handler (onClick, onSubmit, onChange, etc.)
2. TRACE every function call in the handler, IN ORDER
3. For EACH function call:
   a. What state does it READ?
   b. What state does it WRITE?
   c. Does it have SIDE EFFECTS on shared state?
   d. Does it reset/clear any state as a side effect?
4. CHECK: Does any later call UNDO a state change from an earlier call?
5. CHECK: Is the FINAL state what the user expects from the button label?
6. CHECK: Are there race conditions (async calls that resolve in wrong order)?
```

---

## Execution Steps

### Step 1: Map State Stores

在審查任何觸點之前，先為每一個 state store action 建立副作用地圖：

```
For each Zustand store / React context in scope:
  For each action/setter:
    - What fields does it set?
    - Does it RESET other fields as a side effect?
    - Document: actionName → {sets: [...], resets: [...]}
```

這是最關鍵的參考資料。不知道 `selectThread` 會重設 `composeMode` 的話，「New Email」的 bug 根本看不見。

**輸出格式：**
```
STORE: emailStore
  setComposeMode(bool) → sets: {composeMode}
  selectThread(thread|null) → sets: {selectedThread, selectedThreadId, messages, drafts, selectedDraft, summary} RESETS: {composeMode: false, composeData: null, redraftOpen: false}
  setDraftGenerating(bool) → sets: {draftGenerating}
  ...

DANGEROUS RESETS (actions that clear state they don't own):
  selectThread → resets composeMode (owned by setComposeMode)
  reset → resets everything
```

### Step 2: Audit Each Touchpoint

對目標區域裡每個按鈕/切換/表單送出：

```
TOUCHPOINT: [Button label] in [Component:line]
  HANDLER: onClick → {
    call 1: functionA() → sets {X: true}
    call 2: functionB() → sets {Y: null} RESETS {X: false}  ← CONFLICT
  }
  EXPECTED: User sees [description of what button label promises]
  ACTUAL: X is false because functionB reset it
  VERDICT: BUG — [description]
```

**逐一檢查這些 bug 模式：**

#### Pattern 1: Sequential Undo
```
handler() {
  setState_A(true)     // sets X = true
  setState_B(null)     // side effect: resets X = false
}
// Result: X is false. First call was pointless.
```

#### Pattern 2: Async Race
```
handler() {
  fetchA().then(() => setState({ loading: false }))
  fetchB().then(() => setState({ loading: true }))
}
// Result: final loading state depends on which resolves first
```

#### Pattern 3: Stale Closure
```
const [count, setCount] = useState(0)
const handler = useCallback(() => {
  setCount(count + 1)  // captures stale count
  setCount(count + 1)  // same stale count — increments by 1, not 2
}, [count])
```

#### Pattern 4: Missing State Transition
```
// Button says "Save" but handler only validates, never actually saves
// Button says "Delete" but handler sets a flag without calling the API
// Button says "Send" but the API endpoint is removed/broken
```

#### Pattern 5: Conditional Dead Path
```
handler() {
  if (someState) {        // someState is ALWAYS false at this point
    doTheActualThing()    // never reached
  }
}
```

#### Pattern 6: useEffect Interference
```
// Button sets stateX = true
// A useEffect watches stateX and resets it to false
// User sees nothing happen
```

### Step 3: Report

對每個找到的 bug：

```
CLICK-PATH-NNN: [severity: CRITICAL/HIGH/MEDIUM/LOW]
  Touchpoint: [Button label] in [file:line]
  Pattern: [Sequential Undo / Async Race / Stale Closure / Missing Transition / Dead Path / useEffect Interference]
  Handler: [function name or inline]
  Trace:
    1. [call] → sets {field: value}
    2. [call] → RESETS {field: value}  ← CONFLICT
  Expected: [what user expects]
  Actual: [what actually happens]
  Fix: [specific fix]
```

---

## Scope Control

這種稽核很花成本。要適當地控制範圍：

- **整個 app 的稽核：** 上線時或大型重構之後使用。每個頁面各派一個平行 agent。
- **單一頁面的稽核：** 建好新頁面之後，或使用者回報按鈕壞掉之後使用。
- **以 store 為主的稽核：** 修改 Zustand store 之後使用，稽核被改動的 action 的所有使用端。

### Recommended agent split for full app:

```
Agent 1: Map ALL state stores (Step 1) — this is shared context for all other agents
Agent 2: Dashboard (Tasks, Notes, Journal, Ideas)
Agent 3: Chat (DanteChatColumn, JustChatPage)
Agent 4: Emails (ThreadList, DraftArea, EmailsPage)
Agent 5: Projects (ProjectsPage, ProjectOverviewTab, NewProjectWizard)
Agent 6: CRM (all sub-tabs)
Agent 7: Profile, Settings, Vault, Notifications
Agent 8: Management Suite (all pages)
```

Agent 1 **一定**要先完成。它的輸出是所有其他 agent 的輸入。

---

## When to Use

- 系統化除錯找到「沒有 bug」、但使用者回報 UI 壞掉之後
- 修改任何 Zustand store action 之後（檢查所有呼叫端）
- 任何動到共用 state 的重構之後
- 發布之前，針對關鍵的使用者流程
- 當按鈕「什麼都沒做」時，這就是專門處理這種狀況的工具

## When NOT to Use

- API 層級的 bug（回應格式錯誤、缺少 endpoint），用 systematic-debugging
- 樣式/版面問題，用目視檢查
- 效能問題，用 profiling 工具

---

## Integration with Other Skills

- 在 `/superpowers:systematic-debugging` **之後**執行（它會找出其他 54 種 bug）
- 在 `/superpowers:verification-before-completion` **之前**執行（它會驗證修正有沒有用）
- 銜接 `/superpowers:test-driven-development`：這裡找到的每個 bug 都該補一個測試

---

## Example: The Bug That Inspired This Skill

**ThreadList.tsx 的「New Email」按鈕：**
```
onClick={() => {
  useEmailStore.getState().setComposeMode(true)   // ✓ sets composeMode = true
  useEmailStore.getState().selectThread(null)      // ✗ RESETS composeMode = false
}}
```

Store 的定義：
```
selectThread: (thread) => set({
  selectedThread: thread,
  selectedThreadId: thread?.id ?? null,
  messages: [],
  drafts: [],
  selectedDraft: null,
  summary: null,
  composeMode: false,     // ← THIS silent reset killed the button
  composeData: null,
  redraftOpen: false,
})
```

**系統化除錯漏掉它**，因為：
- 按鈕有 onClick handler（不是死的）
- 兩個函式都存在（沒有少接線）
- 兩個函式都不會當掉（沒有 runtime 錯誤）
- 資料型別是對的（沒有型別不符）

**Click-path 稽核抓得到它**，因為：
- Step 1 把 `selectThread` 會重設 `composeMode` 這件事標出來
- Step 2 追蹤 handler：第 1 個呼叫設成 true，第 2 個呼叫重設成 false
- 結論：Sequential Undo，最終狀態跟按鈕的意圖互相矛盾
