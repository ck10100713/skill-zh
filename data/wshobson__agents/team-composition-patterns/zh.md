---
name: team-composition-patterns
description: 設計最適合的 agent 團隊組成，包含人數估算準則、預設配置和 agent 類型選擇。當你要決定一個任務該開幾個 agent、要在 review 團隊、功能團隊或 debug 團隊之間選擇、要為每個角色挑對 subagent_type 讓 agent 拿到需要的工具、要為 CI 或本機環境設定顯示模式（tmux、iTerm2、in-process），或要為遷移、資安稽核這類非標準流程自訂團隊組成時，就用這個 skill。
version: 1.0.2
---

# Team Composition Patterns

為 Claude Code 的 Agent Teams 功能組多 agent 團隊、決定團隊人數、選擇 agent 類型、設定顯示模式的最佳實務。

## When to Use This Skill

- 決定一個任務要開幾個 teammate
- 在預設團隊配置之間做選擇
- 為每個角色選對 agent 類型（subagent_type）
- 設定 teammate 的顯示模式（tmux、iTerm2、in-process）
- 為非標準流程自訂團隊組成

## Team Sizing Heuristics

| Complexity   | Team Size | When to Use                                                 |
| ------------ | --------- | ----------------------------------------------------------- |
| Simple       | 1-2       | 單一面向的 review、獨立的 bug、小功能        |
| Moderate     | 2-3       | 多檔案修改、2-3 個關注點、中型功能       |
| Complex      | 3-4       | 橫切關注點、大型功能、深入的 debug      |
| Very Complex | 4-5       | 全端功能、全面性 review、系統性問題 |

**經驗法則**：從能涵蓋所有必要面向的最小團隊開始。每多一個 teammate，協調成本就會增加。

## Preset Team Compositions

### Review Team

- **Size**：3 個 reviewer
- **Agents**：3x `team-reviewer`
- **Default dimensions**：security、performance、architecture
- **Use when**：程式碼變更需要多面向的品質評估

### Debug Team

- **Size**：3 個調查員
- **Agents**：3x `team-debugger`
- **Default hypotheses**：3 個互相競爭的假設
- **Use when**：Bug 有多個可能的根本原因

### Feature Team

- **Size**：3（1 個 lead + 2 個 implementer）
- **Agents**：1x `team-lead` + 2x `team-implementer`
- **Use when**：功能可以拆成平行的工作流

### Fullstack Team

- **Size**：4（1 個 lead + 3 個 implementer）
- **Agents**：1x `team-lead` + 1x frontend `team-implementer` + 1x backend `team-implementer` + 1x test `team-implementer`
- **Use when**：功能橫跨前端、後端和測試層

### Research Team

- **Size**：3 個研究員
- **Agents**：3x `general-purpose`
- **Default areas**：每個人分配不同的研究問題、模組或主題
- **Capabilities**：程式碼搜尋（Grep、Glob、Read）、網路搜尋（WebSearch、WebFetch）
- **Use when**：需要理解 codebase、研究函式庫、比較不同做法，或平行從程式碼和網路來源收集資訊

### Security Team

- **Size**：4 個 reviewer
- **Agents**：4x `team-reviewer`
- **Default dimensions**：OWASP/弱點、認證/存取控制、相依套件/供應鏈、機密/設定
- **Use when**：要做涵蓋多個攻擊面的完整資安稽核

### Migration Team

- **Size**：4（1 個 lead + 2 個 implementer + 1 個 reviewer）
- **Agents**：1x `team-lead` + 2x `team-implementer` + 1x `team-reviewer`
- **Use when**：大型 codebase 遷移（框架升級、換語言、API 版本升級），需要平行作業又要驗證正確性

## Agent Type Selection

用 `Agent` 工具開 teammate 時，依 teammate 需要的工具來選 `subagent_type`：

| Agent Type                     | Tools Available                                      | Use For                                                    |
| ------------------------------ | ---------------------------------------------------- | ---------------------------------------------------------- |
| `general-purpose`              | 所有工具（Read、Write、Edit、Bash 等）            | 實作、debug、任何需要改檔案的任務 |
| `Explore`                      | 唯讀工具（Read、Grep、Glob）                   | 研究、程式碼探索、分析                       |
| `Plan`                         | 唯讀工具                                    | 架構規劃、任務拆解                  |
| `agent-teams:team-reviewer`    | Read/search/Bash 加上 TaskList/TaskGet/TaskUpdate/SendMessage | 產出結構化發現的 code review               |
| `agent-teams:team-debugger`    | Read/search/Bash 加上 TaskList/TaskGet/TaskUpdate/SendMessage | 假設導向的調查                    |
| `agent-teams:team-implementer` | Read/Write/Edit/search/Bash 加上 TaskList/TaskGet/TaskUpdate/SendMessage | 在檔案所有權範圍內開發功能 |
| `agent-teams:team-lead`        | Read/search/Bash 加上 Agent Teams 協調工具 | 團隊編排與協調                        |

**關鍵差異**：唯讀 agent（Explore、Plan）不能修改檔案。絕對不要把實作任務派給唯讀 agent。

## Display Mode Configuration

在 `~/.claude/settings.json` 設定：

```json
{
  "teammateMode": "tmux"
}
```

| Mode           | Behavior                       | Best For                                          |
| -------------- | ------------------------------ | ------------------------------------------------- |
| `"tmux"`       | 每個 teammate 在自己的 tmux pane   | 開發流程、同時監看多個 agent |
| `"iterm2"`     | 每個 teammate 在自己的 iTerm2 分頁 | 偏好 iTerm2 的 macOS 使用者                     |
| `"in-process"` | 所有 teammate 在同一個 process  | 簡單任務、CI/CD 環境                  |

## Custom Team Guidelines

自訂團隊時：

1. **每個團隊都需要協調者** — 要嘛指定一個 `team-lead`，要嘛由使用者直接協調
2. **角色對應到 agent 類型** — 有專門的 agent（reviewer、debugger、implementer）就用專門的
3. **避免重複的角色** — 兩個 agent 做同一件事是浪費資源
4. **事先劃清界線** — 每個 teammate 都要有明確負責的檔案或職責
5. **保持精簡** — 2-4 個 teammate 最剛好，5 個以上需要大量的協調成本

## Troubleshooting

**Teammate 被開成 `Explore`，但需要寫檔案。**
`Explore` 和 `Plan` 是唯讀 agent。把 `subagent_type` 改成 `general-purpose` 或合適的專門 agent 類型。絕對不要把實作任務派給唯讀 agent。

**團隊越來越大，協調拖慢了所有事情。**
每多一個 teammate 就多一份溝通成本。把角色合併：一個 agent 能不能兼顧兩個面向？4 個人做 6 個獨立任務，通常改成 3 個 agent 各負責 2 個任務會更好。

**tmux 模式沒有顯示 pane。**
開 teammate 之前，先確認 tmux 已安裝且已有一個 session 在跑。`in-process` 模式不需要 tmux，適合 CI 或腳本化的環境。

**兩個 reviewer 標出一樣的問題。**
Review 面向重疊了。重新定義每個 reviewer 的重點：一個看正確性/邏輯、一個看資安、一個看效能/擴展性。重疊的涵蓋範圍會浪費 token，還會產生重複的發現。

**`team-lead` 有開 teammate，但他們沒收到任務。**
確認 lead 是用 `Agent` 工具開 teammate，而且在 prompt 裡帶了完整的 context。Teammate 是從零開始，沒有先前的對話紀錄，所有相關資訊都要放在最初的 prompt 裡。

## Related Skills

- [parallel-feature-development](../parallel-feature-development/SKILL.md) — 團隊組好後，拆解工作流並分配檔案所有權
- [team-communication-protocols](../team-communication-protocols/SKILL.md) — 為組好的團隊建立訊息溝通規範和收尾流程
