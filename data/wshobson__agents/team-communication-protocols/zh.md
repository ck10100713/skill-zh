---
name: team-communication-protocols
description: agent 團隊溝通用的結構化訊息協定，包含訊息類型的選擇、計畫核准、關閉流程，以及要避免的反模式。在為新建立的團隊訂定溝通規範、決定要傳直接訊息還是廣播、team-lead 需要在工作開始前審查並核准 implementer 的計畫、在所有任務完成後統籌優雅地關閉團隊，或除錯為什麼隊友在整合點沒有正確協調時使用這個 skill。
version: 1.0.2
---

# Team Communication Protocols

agent 隊友之間有效溝通的協定，包含訊息類型的選擇、計畫核准的工作流程、關閉流程，以及要避免的常見反模式。

## When to Use This Skill

- 為新團隊訂定溝通規範
- 在訊息類型之間做選擇（message、broadcast、shutdown_request）
- 處理計畫核准的工作流程
- 管理優雅的團隊關閉
- 找出隊友的身分和能力

## Message Type Selection

### `message` (Direct Message) — Default Choice

傳給單一特定的隊友：

```json
{
  "type": "message",
  "recipient": "implementer-1",
  "content": "Your API endpoint is ready. You can now build the frontend form.",
  "summary": "API endpoint ready for frontend"
}
```

**用於**：任務更新、協調、問題、整合通知。

### `broadcast` — Use Sparingly

同時傳給「所有」隊友：

```json
{
  "type": "broadcast",
  "content": "Critical: shared types file has been updated. Pull latest before continuing.",
  "summary": "Shared types updated"
}
```

**只用於**：影響所有人的關鍵阻礙、共享資源的重大變動。

**為什麼要少用？**：每次 broadcast 會送出 N 則獨立的訊息（每位隊友一則），消耗的 API 資源跟團隊大小成正比。

### `shutdown_request` — Graceful Termination

請求某位隊友關閉：

```json
{
  "type": "shutdown_request",
  "recipient": "reviewer-1",
  "content": "Review complete, shutting down team."
}
```

隊友會用 `shutdown_response` 回覆（核准，或附上理由拒絕）。

## Communication Anti-Patterns

| Anti-Pattern                            | Problem                                  | Better Approach                        |
| --------------------------------------- | ---------------------------------------- | -------------------------------------- |
| 廣播例行的更新            | 浪費資源、製造雜訊                  | 直接傳訊息給受影響的隊友    |
| 傳送 JSON 狀態訊息            | 不是為結構化資料設計的         | 用 TaskUpdate 更新任務狀態   |
| 在整合點不溝通 | 隊友照著過時的介面在開發 | 介面準備好時就發訊息   |
| 用訊息微管理              | 讓隊友喘不過氣、拖慢工作         | 在里程碑時關心一下，不是每一步都問 |
| 用 UUID 而不是名字            | 難讀、容易出錯                | 一律用隊友的名字              |
| 忽略閒置的隊友                 | 浪費產能                          | 分派新工作，或關閉他們           |

## Plan Approval Workflow

當隊友是以 `plan_mode_required` 建立的：

1. 隊友用唯讀的探索工具建立計畫
2. 隊友呼叫 `ExitPlanMode`，這會向 lead 送出 `plan_approval_request`
3. Lead 審查計畫
4. Lead 用 `plan_approval_response` 回應：

**核准**：

```json
{
  "type": "plan_approval_response",
  "request_id": "abc-123",
  "recipient": "implementer-1",
  "approve": true
}
```

**附上回饋並拒絕**：

```json
{
  "type": "plan_approval_response",
  "request_id": "abc-123",
  "recipient": "implementer-1",
  "approve": false,
  "content": "Please add error handling for the API calls"
}
```

## Shutdown Protocol

### Graceful Shutdown Sequence

1. **Lead 向每位隊友送出 shutdown_request**
2. **隊友收到請求**，是一則帶有 `type: "shutdown_request"` 的 JSON 訊息
3. **隊友用 `shutdown_response` 回應**：
   - `approve: true` — 隊友儲存狀態並結束
   - `approve: false` + 理由 — 隊友繼續工作
4. **Lead 處理拒絕** — 等隊友完成，再重試
5. **所有隊友都關閉之後** — 呼叫 `TeamDelete` 移除團隊資源

### Handling Rejections

如果隊友拒絕關閉：

- 檢查他們的理由（通常是「還在處理任務」）
- 等他們目前的任務完成
- 重試關閉請求
- 如果很緊急，使用者可以強制關閉

## Teammate Discovery

讀取設定檔來找出團隊成員：

**位置**：`~/.claude/teams/{team-name}/config.json`

**結構**：

```json
{
  "members": [
    {
      "name": "security-reviewer",
      "agentId": "uuid-here",
      "agentType": "team-reviewer"
    },
    {
      "name": "perf-reviewer",
      "agentId": "uuid-here",
      "agentType": "team-reviewer"
    }
  ]
}
```

**傳訊息和分派任務一律用 `name`**。絕對不要直接用 `agentId`、角色名稱或沒有後綴的別名。如果某位隊友是以 `team-lead-2` 建立的，就傳給 `team-lead-2`，不是 `team-lead`。

## Troubleshooting

**某位隊友沒有回應訊息。**
檢查這位隊友的任務狀態。如果是閒置，它可能已經完成任務，正在等著被分派新工作或被關閉。如果它還在運作，可能正在執行中途，等目前的操作結束後才會處理訊息。

**某位隊友說它看不到 SendMessage。**
檢查這位隊友 agent 的 `tools:` frontmatter。當 agent 使用受限的工具允許清單時，Agent Teams 的溝通工具，例如 `SendMessage`、`TaskList`、`TaskGet` 和 `TaskUpdate`，必須明確列出來。

**Lead 為了每個狀態更新都在發 broadcast。**
這是常見的反模式。Broadcast 很昂貴，每一次都會送出 N 則訊息。點對點的更新要用直接訊息（`type: "message"`）。Broadcast 只留給關鍵的共享資源變動，例如更新過的介面合約。

**某位隊友意外地拒絕了關閉請求。**
這位隊友還在工作。檢查 `shutdown_response` 的 content 欄位裡的拒絕理由，等工作完成，再重試。絕對不要強制終止一位有未儲存工作的隊友。

**收到了 plan_approval_request，但缺少 request_id。**
隊友在沒有必要的 request context 的情況下呼叫了 `ExitPlanMode`。讓隊友重新進入 plan mode、完成探索，再呼叫一次 `ExitPlanMode`。`request_id` 是由 plan mode 系統自動產生的。

**兩位隊友在互相等待，誰都沒有進展。**
這是死結（deadlock）：兩邊都被卡住，在等對方先完成。Lead 應該傳一則直接訊息給其中一位隊友，附上一個 stub 或部分結果，讓他能解除阻塞、繼續往下做。

## Related Skills

- [team-composition-patterns](../team-composition-patterns/SKILL.md) — 在訂定溝通規範之前，先選定 agent 類型和團隊規模
- [parallel-feature-development](../parallel-feature-development/SKILL.md) — 用溝通協定協調平行 implementer 之間的整合交接
