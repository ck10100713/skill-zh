---
name: intent-driven-development
description: 在實作之前或同時，把含糊或影響重大的產品與工程變更，轉成範圍明確、可驗證的驗收條件。使用者要釐清功能、定義驗收條件、為安全/資料/migration/整合類變更降低風險、替另一個 agent 準備實作需求，或讓複雜需求可以測試時使用。瑣碎的編輯、直接了當的修正、進行中的除錯、code review，以及驗收條件已經很清楚的實作需求，都不要觸發，除非使用者明確呼叫這個 skill。
---

# Intent-Driven Development

產出有用的驗收條件，但不要把寫規格變成一場儀式。先檢視
手邊有的 context，點出真正的含糊之處，並選擇符合工作內容和風險的驗證方式。

## When to Activate

- 使用者要求在實作之前釐清功能、定義驗收條件，或降低變更風險
- 需求涉及安全、認證、持久化資料、migration、外部 API 或法遵
- 使用者想為另一個 agent 或團隊準備交接文件
- 需求含糊到預期結果還無法被觀察或測試
- 使用者用 `/intent-driven-development` 明確呼叫這個 skill

瑣碎的編輯、直接了當的一行修正、進行中的除錯、
code review 需求，或驗收條件已經很清楚的實作需求，都不要啟用。

## How It Works

1. **Inspect context first** — 在問任何問題之前，先讀 repo、文件、schema 和測試基礎設施，取得技術事實；產品/商業限制則視為只有使用者或產品文件才能提供的東西
2. **Choose depth** — 依風險輪廓選擇 Quick Capture（3-7 條條件，低/中風險）或 Full Acceptance Brief（安全、資料、migration、跨系統變更）
3. **Ask minimally** — 只問那些無法推論、而且會實質改變範圍或行為的問題
4. **Write observable criteria** — 每條 AC-NNN 都要描述起始條件、觸發動作、預期結果、禁止的副作用、驗證方式和優先級；沒有佐證就不准用「正確地」或「安全地」這種模糊字眼
5. **Proceed or hand off** — 需求清楚而且沒有阻礙性風險時，記下條件就繼續做；有風險的變更則列出阻礙，等待確認
6. **Handle revision** — 如果某條 AC 在實作中途因為架構限制而無法達成，就標記為 `[revised]`，更新範圍或驗證方式，把修訂版號加一，並且只重新呈現有變動的條件

## Examples

**Quick Capture — "Add CSV export to the dashboard"**

```
Goal: Authenticated users can download dashboard data as a CSV file.
In scope: Export of currently filtered rows; filename includes date.
Out of scope: Scheduled exports, email delivery, Excel format.
Assumptions: Max row count is under 10k; no PII in exported fields.

AC-001: Export generates file with correct headers
- Scenario: authenticated user, at least one data row visible
- Action: click "Export CSV"
- Expected: browser downloads file with columns [id, name, created_at]
- Must not: expose internal fields or rows belonging to other users
- Verification: automated integration test + manual schema spot-check
- Priority: Required
```

**Full Acceptance Brief 的觸發情境 — "Migrate user auth to OAuth"**

認證變更加上外部依賴加上既有的 session 資料 → 走 Full Brief，附上 Risk Review 表格、
針對 session 失效策略的阻礙性決策，以及明確的 rollback AC。

**Existing spec review — user pastes a PRD**

Skill 會檢查它有沒有缺少範圍邊界、無法驗證的需求（「系統要很快」）
和沒說出口的假設，然後回傳修正過或補充的條件，不用重新從頭做 discovery。

## Operating Rules

1. 對於在本地就能找到的技術事實，要先檢視手邊的 repo、文件、issue、設計和測試 context，
   再去問人。
2. 不要從程式碼推論產品或商業限制。商業規則、法遵與
   法規義務、合約的 SLA、定價、資料保存政策、優先順序，
   和目標使用者，都不是從 repo 讀得出來的。在使用者提供，或權威的產品文件（PRD、合約、政策文件）寫明之前，
   一律視為未知。把它們記成要請人確認的假設，絕對不要當成發現的事實。
   Repo 只會告訴你系統現在怎麼運作，不會告訴你商業上要求它做什麼。
3. 只問那些答案是必要、而且無法安全推論的問題。如果能省下不必要的來回，就把簡短、
   相關的問題合在一起問。
4. 預設不要擋住實作。當使用者要求實作一個夠清楚的變更時，簡短記下關鍵假設和驗收條件，
   然後繼續做，或交給實作工作流程。
5. 只有在某個未解決的決定可能造成重大的資安暴露、資料遺失、不可逆的 migration、
   合約/API 破壞、可觀的成本，或具破壞性的外部動作時，才要求使用者明確確認後再繼續。
6. 除非使用者要求，或目前 repo 的工作流程明確規定，否則不要把驗收文件寫進 repo、修改專案檔案、建立 branch、
   commit，或呼叫其他 skill。
7. 把自動化測試當成證據，不是真理。可靠而且合比例時優先用自動化；
   自動化無法確立結果的地方，允許用人工做 UX、無障礙、安全、法律或營運面的驗證。
8. 絕對不要在驗收條件、fixture、範例或存下來的產物裡放真實的 secret、憑證、token、私鑰、個資，
   或敏感的正式環境 payload。要用遮蔽過或合成的值。
9. 沒有明確授權，而且沒有指定安全環境，就不要執行破壞性測試、migration、資安探測、
   壓力測試、付費的外部呼叫，或針對正式環境/真實資料的操作。
10. 當某條驗收條件因為實作中發現的架構、平台或外部限制而無法滿足時，不要默默丟掉或繞過它。
   更新受影響的條件（標記為 `[revised]`，說明限制，並調整範圍或
   驗證方式），把修訂版號加一，並且在繼續之前，只向使用者重新呈現有變動的條件。
   只有當修訂改變了某個阻礙性決策，或實質降低安全性或正確性保證時，才需要明確確認。

## Choose The Depth

用最小的有用輸出。

### Quick Capture

用在清楚但不瑣碎、風險低或中等的變更。產出：

- Goal
- In scope / out of scope
- Assumptions
- 3-7 條附驗證方式的驗收條件
- 阻礙性問題（如果有）

除非 Operating Rules 裡有阻礙性風險，或使用者明確要求先給規格，
否則不要為了等核准而延後實作。

### Full Acceptance Brief

用在含糊、跨系統、對安全敏感、會改資料、migration、法遵，
或高成本的變更，或使用者要求交接文件時。產出下面完整的範本，
並在有風險的實作開始之前，針對未解決的阻礙性決策要求確認。

### Existing Specification Review

當使用者已經提供 PRD、issue、計畫或驗收條件時：

1. 直接檢查它，不要重新從頭做 discovery。
2. 找出缺少的範圍邊界、不安全的假設、互相矛盾的地方，和無法驗證的
   需求。
3. 回傳修正過或補充的條件。

## Workflow

### 1. Establish Goal And Risk

擷取或詢問：

- 使用者或系統可觀察到的結果。
- 受影響的角色。
- 主要的失敗後果。
- 真正適用的風險維度：安全/隱私、持久化資料、相容性/API、
  migration、外部依賴、成本、並行、效能、可用性/無障礙。

不要問跟不相關風險有關的泛泛問題。

### 2. Discover Context

當有本地或已連接的資料可用時，只檢視需要的部分：

- 既有行為，以及直接相關的檔案或介面。
- Repo 的慣例、產品文件、API 契約、資料 schema 或 migration 歷史。
- 既有的驗證基礎設施，以及實際可跑的指令。
- 外部依賴，以及它們能不能單獨測試。

把發現的事實跟使用者提供的假設分開記錄。如果無法檢視 context，
就說明哪些是未知，並問聚焦的問題。

Repo 透露的是技術事實，也就是系統現在怎麼運作、它的慣例和
它的契約。它不會透露產品或商業限制：商業規則、法遵
與法規義務、合約的 SLA、定價、資料保存政策、優先順序，
和目標使用者。絕對不要從程式碼或命名去重建這些東西。只能從使用者
或權威的產品文件取得，在那之前，把它們列為要確認的假設。

### 3. Define Scope

說明：

- Goal：用一句話描述預期的結果。
- In scope：這次變更必須交付的行為。
- Out of scope：明確排除的、很誘人的相鄰工作。
- Assumptions：還沒被證實的說法。
- Blocking decisions：會實質影響安全或行為、尚未解決的選擇。

### 4. Write Acceptance Criteria

用 `AC-001`、`AC-002` 這樣編號。每條條件都必須描述可觀察的行為，以及
合適的驗證方式；條件和測試不必一對一對應。

每條適用的條件都要包含：

- 情境或起始條件。
- 動作或觸發。
- 預期可觀察的行為。
- 有意義時，要寫禁止的副作用。
- 驗證方式：自動化測試、整合檢查、人工 UX 檢查、無障礙
  檢查、安全審查、營運檢查，或利害關係人驗收。
- 當驗證可能影響資料、服務、成本或 secret 時，要寫環境/安全限制。
- 優先級：required、important 或 optional。

不要使用「正確地」、「安全地」、「快」、「直覺」或「穩健」這類字眼，
除非定義了可觀察的佐證，或把它們記成需要人工判斷的項目。

### 5. Cover Only Relevant Boundaries

可以參考這些類別，但只納入適用的類別：

| 類別 | 納入時機 | 典型佐證 |
| --- | --- | --- |
| Happy path | 新增或改變了使用者看得到的行為 | 成功的流程或狀態轉換 |
| Validation | 變更會接受輸入 | 格式錯誤或邊界值被拒絕，而且沒有變動任何資料 |
| Authorization/privacy | 資料或動作有存取邊界 | 存取被拒絕，而且沒有敏感資訊外洩 |
| Persistence/migration | 儲存的資料或 schema 有變 | 向下相容讀取、migration、rollback 或備份行為 |
| Compatibility | 公開 API、檔案、事件或 client 可能被破壞 | 既有契約或 fixture 仍然有效 |
| Failure recovery | 存在網路、服務或非同步失敗 | 沒有部分狀態，或有明確的重試/降級行為 |
| Idempotency/concurrency | 可能重複或同時寫入 | 沒有重複的副作用，也沒有無效的最終狀態 |
| Performance | 使用者或服務有門檻要求 | 定義好的量測條件和門檻 |
| UX/accessibility | 有人要跟成果互動 | 鍵盤操作、回饋、錯誤復原、視覺/人工檢查 |

### 6. Present And Continue

- 如果是釐清/規格需求，就呈現 brief，並且只針對列出的阻礙項目請對方做決定。
- 如果是沒有阻礙的實作需求，就把精簡的條件摘要當成工作的一部分呈現，
  然後繼續實作。
- 如果是交接給另一個 agent 或團隊，要附上足夠的 context 和驗證細節，
  讓他們不用自己編需求就能動手。
- 只有在被要求時才把 brief 存成檔案。有 repo 核准的路徑就用那個路徑；
  否則在寫入之前，先詢問或說明選定的位置。

## Output Template

Full Acceptance Brief 用這個範本。Quick Capture 可以省略不相關的區段。

```markdown
# Acceptance Brief: <Change Name>

**Status:** Draft | Approved | Implemented | Verified
**Revision:** <number>
**Prepared for:** <user/team/agent, when known>
**Approval required before risky work:** Yes | No - <reason>

## Revision Log

| Rev | Date | Changed criteria | Reason |
| --- | --- | --- | --- |
| 1 | <date> | — | Initial draft |

## Goal

<One observable outcome sentence.>

## Scope

**In scope**
- <behavior included>

**Out of scope**
- <adjacent work excluded>

## Context

**Discovered facts** (technical, verified from repository or artifact)
- <how the system behaves today, conventions, contracts>

**Product/business constraints** (supplied by user or product artifact, never inferred from code)
- <business rule, compliance/SLA obligation, retention policy, priority, target user — or "none supplied yet">

**Assumptions**
- <unverified claim to confirm or validate>

**Dependencies and constraints**
- <external service, local convention, compatibility obligation, environment limit>

## Risk Review

| Risk area | Applies? | Required handling |
| --- | --- | --- |
| Security/privacy | Yes/No | <redaction, authorization, review, etc.> |
| Persistent data/migration | Yes/No | <compatibility, backup, rollback, etc.> |
| External effects/cost | Yes/No | <sandbox/test environment/authorization> |
| Compatibility/API | Yes/No | <contract to preserve or version> |
| UX/accessibility | Yes/No | <manual or automated evidence> |

## Acceptance Criteria

### AC-001: <observable behavior>
- **Scenario:** <starting condition>
- **Action:** <single trigger>
- **Expected:** <observable result>
- **Must not:** <prohibited side effect, if applicable>
- **Verification:** <method and intended evidence>
- **Environment/safety:** <constraints, if applicable>
- **Priority:** Required | Important | Optional

## Blocking Decisions

- [ ] <only decisions that prevent safe or correct progress>

## Verification Plan

| Criterion | Verification evidence | Status |
| --- | --- | --- |
| AC-001 | <test/check/review command or evidence type> | Pending |
```

## Pass/Fail Examples

用這些來判斷這個 skill 到底有沒有產出可驗證的 brief，而不是只有規劃的空話。

**A failing acceptance criterion**

```
AC-001: The export works correctly and is secure.
```

不及格：「works correctly」和「secure」都無法觀察，沒有情境、觸發動作、
預期結果或驗證方式，也沒有說明什麼事不能發生。讀的人
無法判斷實作有沒有滿足它。

**A passing acceptance criterion**

```
AC-001: Export generates file with correct headers
- Scenario: authenticated user, at least one data row visible
- Action: click "Export CSV"
- Expected: browser downloads file with columns [id, name, created_at]
- Must not: expose internal fields or rows belonging to other users
- Verification: automated integration test + manual schema spot-check
- Priority: Required
```

及格：有具體可觀察的結果、禁止的副作用，以及明確的驗證
方式。兩個人對它有沒有達成會得到同樣的判斷。

**A failing context entry**

```
Discovered facts: Users on the free tier are limited to 100 exports per month.
```

不及格：每個方案的上限是商業規則。它不能出現在「從程式碼推論出來的 discovered facts」下面；
它應該放在使用者提供的 Product/business constraints，或是列為
要確認的假設。

### Pass/Fail Rubric

只有每個答案都是「是」，brief 才算及格。任何一個「否」，都要先修訂再回傳。

- [ ] 每條 required 條件都有情境、可觀察的預期結果，和明確的驗證方式嗎？
- [ ] 所有模糊字眼（「correctly」、「secure」、「fast」、「robust」）都已換成可觀察的佐證，或標記為人工判斷了嗎？
- [ ] 產品/商業限制都列為使用者提供/假設，沒有任何一條是默默從程式碼推論出來的嗎？
- [ ] 範圍明確，而且點名了 out-of-scope 的項目嗎？
- [ ] 阻礙性決策只限於真正影響安全或正確性的選擇，而不是個人偏好嗎？

## Quality Check

回傳 brief 之前，檢查：

- Goal 描述的是結果，而不是實作選擇。
- 範圍邊界和假設都寫明了。
- 每條 required 條件都是可觀察的，或明確標記為需要人工判斷。
- 安全、隱私、資料、相容性、外部影響和 UX 的風險，都只在相關的地方被考慮，
  而且沒有被默默忽略。
- 驗證方式對有風險的操作指明了安全的環境。
- 沒有把 secret 或正式環境的敏感資訊複製進輸出。
- 沒有在缺乏理由或要求的情況下，強加 repo 異動或實作區塊。

## Handoff

如果有其他規劃或實作工作流程可用，就把驗收 brief 或
條件 ID 交給它。如果沒有專用的工作流程，就直接把 brief 當成
實作參考。不要假設任何特定名稱的 skill 或工具已經安裝。
