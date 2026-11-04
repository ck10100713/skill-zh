---
name: incident-response
description: 執行事件應變流程：分級研判、對外溝通、撰寫 postmortem。當說「we have an incident」、「production is down」、有警報需要判斷嚴重程度、事件進行中要發狀態更新，或是事件解決後要寫無究責 postmortem 時觸發。
argument-hint: "<incident description or alert>"
---

# /incident-response

> 如果看到不認識的佔位符，或需要確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

從發現事件一路管理到 postmortem。

## 用法

```
/incident-response $ARGUMENTS
```

## 模式

```
/incident-response new [description]     # 開始一個新事件
/incident-response update [status]       # 發佈狀態更新
/incident-response postmortem            # 根據事件資料產生 postmortem
```

如果沒指定模式，就問事件目前在哪個階段。

## 運作方式

```
┌─────────────────────────────────────────────────────────────────┐
│                    INCIDENT RESPONSE                               │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: TRIAGE（分級研判）                                      │
│  ✓ 評估嚴重程度（SEV1-4）                                       │
│  ✓ 找出受影響的系統和使用者                                     │
│  ✓ 指派角色（IC、對外溝通、處理人員）                           │
│                                                                    │
│  Phase 2: COMMUNICATE（溝通）                                      │
│  ✓ 擬內部狀態更新                                                │
│  ✓ 擬客戶溝通內容（如有需要）                                   │
│  ✓ 建立 war room 並訂定更新頻率                                  │
│                                                                    │
│  Phase 3: MITIGATE（緩解）                                         │
│  ✓ 記錄已採取的緩解步驟                                          │
│  ✓ 追蹤事件時間軸                                                │
│  ✓ 確認已解決                                                    │
│                                                                    │
│  Phase 4: POSTMORTEM（事後檢討）                                   │
│  ✓ 無究責的 postmortem 文件                                      │
│  ✓ 重建時間軸                                                    │
│  ✓ 根本原因分析（5 whys）                                        │
│  ✓ 附負責人的行動項目                                            │
└─────────────────────────────────────────────────────────────────┘
```

## 嚴重程度分級

| 等級 | 標準 | 回應時間 |
|-------|----------|---------------|
| SEV1 | 服務掛了，所有使用者受影響 | 立即，全員投入 |
| SEV2 | 主要功能降級，許多使用者受影響 | 15 分鐘內 |
| SEV3 | 次要功能有問題，部分使用者受影響 | 1 小時內 |
| SEV4 | 外觀或低影響的問題 | 下一個工作日 |

## 溝通指引

定期提供清楚、以事實為主的更新。內容包括：現在發生什麼事、誰受影響、我們在做什麼、下次更新是什麼時候。

## 輸出：狀態更新

```markdown
## Incident Update: [標題]
**Severity:** SEV[1-4] | **Status:** Investigating | Identified | Monitoring | Resolved
**Impact:** [誰或什麼受到影響]
**Last Updated:** [時間戳]

### Current Status
[目前掌握的資訊]

### Actions Taken
- [動作 1]
- [動作 2]

### Next Steps
- [接下來要做什麼，以及預計時間]

### Timeline
| Time | Event |
|------|-------|
| [HH:MM] | [事件] |
```

## 輸出：Postmortem

```markdown
## Postmortem: [事件標題]
**Date:** [日期] | **Duration:** [X 小時] | **Severity:** SEV[X]
**Authors:** [姓名] | **Status:** Draft

### Summary
[2-3 句白話摘要]

### Impact
- [受影響的使用者]
- [影響持續時間]
- [如果能量化，寫對業務的影響]

### Timeline
| Time (UTC) | Event |
|------------|-------|
| [HH:MM] | [事件] |

### Root Cause
[詳細說明是什麼造成這次事件]

### 5 Whys
1. Why did [症狀]? → [因為……]
2. Why did [原因 1]? → [因為……]
3. Why did [原因 2]? → [因為……]
4. Why did [原因 3]? → [因為……]
5. Why did [原因 4]? → [根本原因]

### What Went Well
- [有效的做法]

### What Went Poorly
- [沒效的做法]

### Action Items
| Action | Owner | Priority | Due Date |
|--------|-------|----------|----------|
| [行動] | [負責人] | P0/P1/P2 | [日期] |

### Lessons Learned
[給團隊的重點心得]
```

## 如果有連上 Connector

如果有連上 **~~monitoring**：
- 拉警報細節和指標
- 顯示受影響指標的圖表

如果有連上 **~~incident management**：
- 在 PagerDuty/Opsgenie 建立或更新事件
- 呼叫值班的處理人員

如果有連上 **~~chat**：
- 把狀態更新發到事件頻道
- 建立 war room 頻道

## 小提醒

1. **馬上開始寫**：不要等資訊齊全，邊了解邊更新。
2. **更新只講事實**：我們知道什麼、做了什麼、接下來要做什麼。不要猜測。
3. **Postmortem 是無究責的**：焦點放在系統和流程，不是個人。
