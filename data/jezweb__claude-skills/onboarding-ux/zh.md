---
name: onboarding-ux
description: "稽核並產生 app 內的使用者引導：onboarding 流程、空狀態、tooltip、功能導覽、情境式說明、預設值和行內提示。會瀏覽 app 找出新使用者會卡住的地方，再產出實際的內容和程式碼來修正。搭配 ux-audit：audit 找問題，這個 skill 做解法。觸發詞：'onboarding'、'help content'、'empty states'、'user guidance'、'first run experience'、'feature tour'、'app is confusing'、'new user experience'、'make the app welcoming'。"
compatibility: claude-code-only
---

# Onboarding UX

稽核 web app 的 onboarding 缺口，再產生 app 內的引導內容去補齊。目標是：新使用者永遠不會對著空白畫面發呆、不知道該做什麼。

## 這個 skill 解決什麼問題

你把功能都做好了，也都能用。但新使用者第一次登入時，看到的是：
- 只有欄位標題、什麼都沒有的空表格
- 側邊欄滿滿都是他們還看不懂的標籤
- 沒有任何提示告訴他從哪裡開始、這個 app 是拿來做什麼的
- 有些功能他根本不知道存在，因為沒有任何東西指向它們

這個 skill 會找出這些缺口，並產出內容和程式碼去補上。

## 偵測瀏覽器工具

和 ux-audit 一樣：偵測 Chrome MCP、Playwright MCP 或 playwright-cli。需要的話看 ux-audit 的 browser-tools.md 參考檔。

## URL 判定

和 ux-audit 一樣：優先用已部署/正式的 URL，不要用 localhost。檢查 wrangler.jsonc、CLAUDE.md，或正在跑的 dev server。

## 工作流程

### 階段 1：稽核，找出缺口

用全新使用者的身分瀏覽 app。每個頁面都要評估：

#### 空狀態
走訪每個列表/表格/集合頁面。對每一個檢查：

| 檢查項目 | 好 | 壞 |
|-------|------|-----|
| 零資料的頁面顯示什麼？ | "No clients yet. Add your first client to get started." + CTA 按鈕 | 只有欄位標題的空表格，或一片空白 |
| 有沒有明確的動作？ | 按鈕："Add your first [thing]" | 什麼都沒有，使用者得自己在導覽列或選單裡找 |
| 有沒有解釋這個功能？ | "Clients are the people and businesses you work with. Add one to start tracking your relationships." | 只是個空容器 |
| 空狀態有設計過嗎？ | 插圖或圖示、有幫助的文案、明顯的 CTA | 跟有資料時的畫面一模一樣，只是少了資料 |

#### 第一印象
用新使用者的身分登入（或清除狀態來模擬）。評估：

| 檢查項目 | 要看什麼 |
|-------|-----------------|
| **著陸頁** | 儀表板/首頁顯示有用的東西，還是空的？ |
| **定位感** | 10 秒內，我知道這個 app 在做什麼、該從哪裡開始嗎？ |
| **第一個動作** | 我該做的第一件事是不是很明顯、很突出？ |
| **認知負荷** | 有多少選單項目、按鈕和選項在爭奪注意力？ |
| **歡迎內容** | 有歡迎訊息、導覽或入門指南嗎？還是只有原始的 app？ |

#### 功能可發現性
針對 app 裡的每個功能：

| 檢查項目 | 要看什麼 |
|-------|-----------------|
| **找得到嗎？** | 在導覽列看得到，還是埋在選單/子選單裡？ |
| **知道它做什麼嗎？** | 標籤本身有說明，還是要點進去才知道？ |
| **鍵盤快捷鍵** | 有快捷鍵嗎？能被發現嗎（tooltip、說明面板）？ |
| **進階功能** | 篩選、批次動作、搜尋，這些看得到還是被藏起來？ |
| **設定與組態** | 找得到設定嗎？知道每個設定在做什麼嗎？ |

#### 情境式說明的缺口
在每個頁面：

| 檢查項目 | 要看什麼 |
|-------|-----------------|
| **表單欄位** | 複雜的欄位有說明文字或 tooltip 嗎？ |
| **行話** | 有沒有非專家看不懂的標籤？ |
| **後果** | 破壞性或不可逆的動作，有說明會發生什麼嗎？ |
| **驗證** | 我犯錯時，錯誤訊息有告訴我怎麼修嗎？ |

#### 產出稽核報告

寫到 `.jez/artifacts/onboarding/audit.md`：

```markdown
# Onboarding Audit: [App Name]
**Date**: YYYY-MM-DD
**URL**: [app url]

## First Impression Score
[1-5] — Can a new user figure out what to do within 30 seconds?

## Empty States Found
| Page | Current state | Recommendation |
|------|--------------|----------------|
| /clients | Empty table, no guidance | Add empty state with CTA |

## Missing Guidance
| Location | Gap | Priority |
|----------|-----|----------|
| Dashboard | No welcome or getting started | High |
| Settings | No descriptions on settings | Medium |

## Feature Discovery Issues
| Feature | Problem | Fix |
|---------|---------|-----|
| Keyboard shortcuts | No way to discover them | Add help panel |

## Quick Wins
[Top 5 changes that would have the biggest impact on new user experience]
```

---

### 階段 2：產生，做出解法

稽核之後，產生實際的內容和程式碼。先讀專案的 codebase，配合既有的技術堆疊和元件模式。

#### 1. 空狀態元件

對稽核中找出的每個空狀態，產生一個元件：

```tsx
// Pattern — adapt to the project's component library
function EmptyState({ icon, title, description, actionLabel, onAction }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="text-muted-foreground mb-4">{icon}</div>
      <h3 className="text-lg font-medium mb-2">{title}</h3>
      <p className="text-muted-foreground mb-6 max-w-md">{description}</p>
      <Button onClick={onAction}>{actionLabel}</Button>
    </div>
  );
}
```

為每個頁面寫專屬的文案：
- **標題**：這個功能是什麼（"Clients"）
- **描述**：為什麼重要，一句話（"Track the people and businesses you work with"）
- **動作**：下一步要做什麼（"Add your first client"）

文案要寫得像有幫助的同事，不要像說明書。

#### 2. 歡迎 / 首次執行體驗

依 app 的複雜度，產生下列其中一種模式：

**簡單的 app（3-5 個功能）**：儀表板上的歡迎橫幅
```tsx
// Dismissable welcome banner — shown until user closes it or completes first action
function WelcomeBanner({ onDismiss }) {
  return (
    <div className="rounded-lg border bg-card p-6 mb-6">
      <h2 className="text-xl font-semibold mb-2">Welcome to [App Name]</h2>
      <p className="text-muted-foreground mb-4">Here's how to get started:</p>
      <ol className="space-y-2 mb-4">
        <li>1. Add your first client</li>
        <li>2. Create a policy for them</li>
        <li>3. Check your dashboard for what needs attention</li>
      </ol>
      <Button variant="outline" size="sm" onClick={onDismiss}>Got it</Button>
    </div>
  );
}
```

**複雜的 app（6 個以上功能）**：清單式的 onboarding
```tsx
// Persistent getting-started checklist — tracks progress
function OnboardingChecklist({ steps, completedSteps }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Getting Started</CardTitle>
        <p className="text-sm text-muted-foreground">
          {completedSteps.length} of {steps.length} complete
        </p>
      </CardHeader>
      <CardContent>
        {steps.map(step => (
          <div key={step.id} className="flex items-center gap-3 py-2">
            <Checkbox checked={completedSteps.includes(step.id)} disabled />
            <span>{step.label}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
```

#### 3. 功能導覽

為 react-joyride（或同類工具）產生導覽設定：

```tsx
const tourSteps = [
  {
    target: '[data-tour="sidebar-clients"]',
    content: 'Your clients live here. Add people and businesses you work with.',
    placement: 'right',
  },
  {
    target: '[data-tour="create-button"]',
    content: 'Click here to create something new — a client, policy, or email.',
    placement: 'bottom',
  },
  {
    target: '[data-tour="search"]',
    content: 'Use search to find anything fast. Try Cmd+K for the quick switcher.',
    placement: 'bottom',
  },
];
```

同時產生需要加到既有元件上的 `data-tour` 屬性。

#### 4. Tooltip 與說明內容

對每個複雜的 UI 元素，產生 tooltip 文案：

```tsx
// Pattern for info tooltips
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <InfoIcon className="h-4 w-4 text-muted-foreground" />
    </TooltipTrigger>
    <TooltipContent>
      <p>Significance shows how important this client is to your business.
      5 = critical (your biggest client), 1 = minimal (one-off interaction).</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

為每個需要解釋的欄位，產生內容對照表：`{ fieldName: tooltipText }`。

#### 5. 情境式提示

為使用者可能不會發現的功能，產生行內提示：

```tsx
// Shown once, dismissable, stored in localStorage
function ContextualHint({ id, children }) {
  const [dismissed, setDismissed] = useState(
    () => localStorage.getItem(`hint-${id}`) === 'dismissed'
  );
  if (dismissed) return null;
  return (
    <div className="text-sm text-muted-foreground bg-muted/50 rounded-md px-3 py-2 mb-3 flex items-center justify-between">
      <span>{children}</span>
      <button onClick={() => { localStorage.setItem(`hint-${id}`, 'dismissed'); setDismissed(true); }}>
        <XIcon className="h-3 w-3" />
      </button>
    </div>
  );
}

// Usage
<ContextualHint id="keyboard-shortcuts">
  Tip: Press Cmd+K to quickly jump to any page or record.
</ContextualHint>
```

#### 6. 會教人的種子資料

產生能示範 app 功能的範例紀錄：

- 一個資料寫實的範例客戶（不是 "Test Client"）
- 每種狀態各一筆範例紀錄（草稿、啟用、完成、封存）
- 能呈現關聯的紀錄（客戶 → 聯絡人 → 保單 → email）

種子 script 要寫成 **onboarding 等級的資料**：這些紀錄要能教使用者什麼是好的資料。

#### 7. 說明頁內容

根據 app 實際內容，產生說明/FAQ 頁面的內容：

```markdown
## Frequently Asked Questions

### How do I add a new client?
1. Click "Clients" in the sidebar
2. Click "Add Client" in the top right
3. Fill in the name and domain — everything else is optional
4. Click "Save"

### What does "significance" mean?
Significance is a 1-5 rating of how important a client is...

### Can I undo a deletion?
Deletions are permanent. You'll always see a confirmation before...
```

## 輸出

所有產生的內容都放到 `.jez/artifacts/onboarding/`：

```
.jez/artifacts/onboarding/
├── audit.md                    # The gap analysis report
├── empty-states.tsx            # Empty state components with copy
├── welcome-banner.tsx          # First-run welcome component
├── onboarding-checklist.tsx    # Getting-started checklist (if complex app)
├── tour-steps.ts               # Feature tour configuration
├── tooltip-content.ts          # Tooltip copy map
├── contextual-hints.tsx        # Inline hint component + content
├── seed-data.ts                # Onboarding seed records
└── help-content.md             # FAQ / help page content
```

告訴使用者產生了哪些檔案，以及該整合到哪裡。每個檔案都要給具體說明，例如：「客戶清單是空的時候，把這個元件加到你的 /clients 頁面。」

## 小提醒

- 產生之前先讀專案既有的元件模式，配合它的風格，不要引進新的模式
- 如果專案有用 shadcn/ui，就用 shadcn/ui 元件
- 文案要寫得像有幫助的同事，不要像說明書
- 空狀態是影響最大的單一改動，先做這個
- 功能導覽太長會很煩人，最多 5 步
- 情境式提示要可以關閉，而且只顯示一次
- 範例資料要看起來像真的，用寫實的澳洲姓名、網域和細節
- 說明頁的內容可以從 ux-audit 的「向同事解釋」輸出產生

## 搭配其他 Skill

| 如果你也跑了…… | 這個 skill 會補上…… |
|--------------------|--------------------|
| `ux-audit`（thorough） | 把稽核發現當輸入，修正找到的問題 |
| `app-docs` | 說明頁的內容可以餵給使用者指南 |
| `product-showcase` | 空狀態和歡迎流程讓示範截圖看起來更好 |
