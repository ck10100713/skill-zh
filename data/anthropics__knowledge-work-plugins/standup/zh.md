---
name: standup
description: 依近期活動產生站會更新。適用於準備每日站會、彙整昨天的 commit、PR 和工單變動、把工作整理成 yesterday/today/blockers 格式，或把幾則粗略的筆記整理成可以分享的更新。
argument-hint: "[yesterday | today | blockers]"
---

# /standup

> 如果看到不熟悉的佔位符，或需要確認哪些工具已連接，請見 [CONNECTORS.md](../../CONNECTORS.md)。

彙整你各個工具裡的近期活動，產生站會更新。

## 運作方式

```
┌─────────────────────────────────────────────────────────────────┐
│                        STANDUP                                    │
├─────────────────────────────────────────────────────────────────┤
│  獨立運作（永遠可用）                                              │
│  ✓ 告訴我你做了什麼，我來整理                                     │
│  ✓ 整理成每日站會格式（yesterday / today / blockers）             │
│  ✓ 保持簡潔、以行動為導向                                         │
├─────────────────────────────────────────────────────────────────┤
│  加強版（連接工具之後）                                            │
│  + 原始碼管理：近期的 commit 和 PR                                │
│  + 專案追蹤工具：工單狀態變動                                     │
│  + 聊天：相關的討論和決策                                         │
│  + CI/CD：建置和部署狀態                                          │
└─────────────────────────────────────────────────────────────────┘
```

## 我需要你提供什麼

**選項 A：讓我去拉**
如果你的工具已連接，直接說 `/standup`，我會自動蒐集所有東西。

**選項 B：告訴我你做了什麼**
「Worked on the auth migration, reviewed 3 PRs, got blocked on the API rate limiting issue.」

## 輸出

```markdown
## Standup — [Date]

### Yesterday
- [Completed item with ticket reference if available]
- [Completed item]

### Today
- [Planned item with ticket reference]
- [Planned item]

### Blockers
- [Blocker with context and who can help]
```

## 有連接器時

如果已連接 **~~source control**：
- 拉近期的 commit 和 PR（開啟的、審查的、合併的）
- 在高層次摘要程式碼變更

如果已連接 **~~project tracker**：
- 拉移到「in progress」或「done」的工單
- 顯示即將到來的 sprint 項目

如果已連接 **~~chat**：
- 掃描相關的討論和決策
- 標出需要你回應的討論串

## 小提醒

1. **每天早上都跑**：養成習慣，就不用再臨時手忙腳亂找站會筆記。
2. **補充脈絡**：我產生之後，補上關於阻礙或優先順序的任何細節。
3. **分享格式**：請我調整成適合 Slack、email 或你們團隊站會工具的格式。
