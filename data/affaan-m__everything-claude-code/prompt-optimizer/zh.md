---
name: prompt-optimizer
description: 分析草稿 prompt、偵測意圖和缺少的 context、對應到 ECC 的 command、skill 和 agent，並輸出可直接貼上的最佳化 prompt，附上診斷和理由。只提供建議，絕對不會執行任務。使用者說 'optimize prompt'、'improve my prompt'、'rewrite this prompt'、'help me prompt'、优化prompt、改进prompt、怎么写prompt 或 帮我优化这个指令 時使用；不適用於最佳化程式碼或效能的請求。
metadata:
  origin: community
  author: YannJY02
  version: "1.0.0"
---

# Prompt Optimizer

分析一份草稿 prompt、批評它、把它對應到 ECC 生態系的元件，並輸出一份使用者可以直接貼上執行的完整最佳化 prompt。

## 何時使用

- 使用者說「optimize this prompt」、「improve my prompt」、「rewrite this prompt」
- 使用者說「help me write a better prompt for...」
- 使用者說「what's the best way to ask Claude Code to...」
- 使用者說「优化prompt」、「改进prompt」、「怎么写prompt」、「帮我优化这个指令」
- 使用者貼上一份草稿 prompt，要求回饋或改進
- 使用者說「I don't know how to prompt for this」
- 使用者說「how should I use ECC for...」
- 使用者明確呼叫 `/prompt-optimize`

### 何時不要使用

- 使用者要的是直接把任務做完（直接執行就好）
- 使用者說「优化代码」、「优化性能」、「optimize this code」、「optimize performance」，這些是重構任務，不是 prompt 最佳化
- 使用者問的是 ECC 設定（改用 `configure-ecc`）
- 使用者想要 skill 清單（改用 `skill-stocktake`）
- 使用者說「just do it」或「直接做」

## 運作方式

**只提供建議，不要執行使用者的任務。**

絕對不要寫程式碼、建立檔案、執行指令，或採取任何實作動作。你唯一的輸出是一份分析加上一份最佳化的 prompt。

如果使用者說「just do it」、「直接做」或「don't optimize, just execute」，不要在這個 skill 裡切換成實作模式。告訴使用者這個 skill 只會產出最佳化的 prompt，並請他們如果想要執行，就另外提出一般的任務請求。

依序執行這個 6 階段的流程。用下面的輸出格式呈現結果。

### 分析流程

### Phase 0：專案偵測

分析 prompt 之前，先偵測目前的專案背景：

1. 檢查工作目錄裡有沒有 `CLAUDE.md`，有的話讀取它，了解專案慣例
2. 從專案檔案偵測技術堆疊：
   - `package.json` → Node.js / TypeScript / React / Next.js
   - `go.mod` → Go
   - `pyproject.toml` / `requirements.txt` → Python
   - `Cargo.toml` → Rust
   - `build.gradle` / `pom.xml` → Java / Kotlin（接著檢查 build 檔案裡有沒有 `quarkus` → Quarkus，或 `spring-boot` → Spring Boot）
   - `Package.swift` → Swift
   - `Gemfile` → Ruby
   - `composer.json` → PHP
   - `*.csproj` / `*.sln` → .NET
   - `Makefile` / `CMakeLists.txt` → C / C++
   - `cpanfile` / `Makefile.PL` → Perl
3. 記下偵測到的技術堆疊，供 Phase 3 和 Phase 4 使用

如果找不到任何專案檔案（例如 prompt 很抽象，或是給新專案用的），就跳過偵測，並在 Phase 4 標記「tech stack unknown」。

### Phase 1：意圖偵測

把使用者的任務分到一個或多個類別：

| 類別 | 訊號詞 | 範例 |
|----------|-------------|---------|
| New Feature | build, create, add, implement, 创建, 实现, 添加 | "Build a login page" |
| Bug Fix | fix, broken, not working, error, 修复, 报错 | "Fix the auth flow" |
| Refactor | refactor, clean up, restructure, 重构, 整理 | "Refactor the API layer" |
| Research | how to, what is, explore, investigate, 怎么, 如何 | "How to add SSO" |
| Testing | test, coverage, verify, 测试, 覆盖率 | "Add tests for the cart" |
| Review | review, audit, check, 审查, 检查 | "Review my PR" |
| Documentation | document, update docs, 文档 | "Update the API docs" |
| Infrastructure | deploy, CI, docker, database, 部署, 数据库 | "Set up CI/CD pipeline" |
| Design | design, architecture, plan, 设计, 架构 | "Design the data model" |

### Phase 2：範圍評估

如果 Phase 0 偵測到專案，就用程式碼庫的大小當作訊號。否則，單從 prompt 的描述來估計，並把這個估計標記為不確定。

| 範圍 | 判斷依據 | 編排方式 |
|-------|-----------|---------------|
| TRIVIAL | 單一檔案，< 50 行 | 直接執行 |
| LOW | 單一元件或模組 | 單一 command 或 skill |
| MEDIUM | 多個元件，同一領域 | Command 鏈 + /verify |
| HIGH | 跨領域，5 個以上檔案 | 先 /plan，再分階段執行 |
| EPIC | 跨多個 session、多個 PR、架構轉變 | 用 blueprint skill 做多 session 計畫 |

### Phase 3：ECC 元件對應

把意圖 + 範圍 + 技術堆疊（來自 Phase 0）對應到特定的 ECC 元件。

#### 依意圖類型

| 意圖 | Commands | Skills | Agents |
|--------|----------|--------|--------|
| New Feature | /plan, /tdd, /code-review, /verify | tdd-workflow, verification-loop | planner, tdd-guide, code-reviewer |
| Bug Fix | /tdd, /build-fix, /verify | tdd-workflow | tdd-guide, build-error-resolver |
| Refactor | /refactor-clean, /code-review, /verify | verification-loop | refactor-cleaner, code-reviewer |
| Research | /plan | search-first, iterative-retrieval | — |
| Testing | /tdd, /e2e, /test-coverage | tdd-workflow, e2e-testing | tdd-guide, e2e-runner |
| Review | /code-review | security-review | code-reviewer, security-reviewer |
| Documentation | /update-docs, /update-codemaps | — | doc-updater |
| Infrastructure | /plan, /verify | docker-patterns, deployment-patterns, database-migrations | architect |
| Design (MEDIUM-HIGH) | /plan | — | planner, architect |
| Design (EPIC) | — | blueprint (invoke as skill) | planner, architect |

#### 依技術堆疊

| 技術堆疊 | 要加的 Skills | Agent |
|------------|--------------|-------|
| Python / Django | django-patterns, django-tdd, django-security, django-verification, python-patterns, python-testing | python-reviewer |
| Go | golang-patterns, golang-testing | go-reviewer, go-build-resolver |
| Spring Boot / Java | springboot-patterns, springboot-tdd, springboot-security, springboot-verification, java-coding-standards, jpa-patterns | java-reviewer |
| Quarkus / Java | quarkus-patterns, quarkus-tdd, quarkus-security, quarkus-verification, java-coding-standards, jpa-patterns | java-reviewer |
| Kotlin / Android | kotlin-coroutines-flows, compose-multiplatform-patterns, android-clean-architecture | kotlin-reviewer |
| TypeScript / React | frontend-patterns, backend-patterns, coding-standards | code-reviewer |
| Swift / iOS | swiftui-patterns, swift-concurrency-6-2, swift-actor-persistence, swift-protocol-di-testing | code-reviewer |
| PostgreSQL | postgres-patterns, database-migrations | database-reviewer |
| Perl | perl-patterns, perl-testing, perl-security | code-reviewer |
| C++ | cpp-coding-standards, cpp-testing | code-reviewer |
| Other / Unlisted | coding-standards (universal) | code-reviewer |

### Phase 4：缺少的 Context 偵測

掃描 prompt 缺少哪些關鍵資訊。逐項檢查，並標記這是 Phase 0 自動偵測到的，還是使用者必須提供的：

- [ ] **Tech stack**：Phase 0 偵測到了，還是必須請使用者指定？
- [ ] **Target scope**：有提到檔案、目錄或模組嗎？
- [ ] **Acceptance criteria**：怎麼知道任務完成了？
- [ ] **Error handling**：有處理邊界情況和失敗模式嗎？
- [ ] **Security requirements**：認證、輸入驗證、secret？
- [ ] **Testing expectations**：單元、整合、E2E？
- [ ] **Performance constraints**：負載、延遲、資源上限？
- [ ] **UI/UX requirements**：設計規格、響應式、a11y？（如果是前端）
- [ ] **Database changes**：schema、migration、索引？（如果牽涉資料層）
- [ ] **Existing patterns**：要參考的檔案或要遵循的慣例？
- [ ] **Scope boundaries**：什麼事不要做？

**如果有 3 個以上的關鍵項目缺少**，在產生最佳化 prompt 之前，最多問使用者 3 個釐清問題。然後把答案整合進最佳化的 prompt。

### Phase 5：工作流程與模型建議

判斷這份 prompt 位在開發生命週期的哪個位置：

```
Research → Plan → Implement (TDD) → Review → Verify → Commit
```

MEDIUM 以上的任務，一律從 /plan 開始。EPIC 任務則用 blueprint skill。

**模型建議**（要放進輸出）：

| 範圍 | 建議的模型 | 理由 |
|-------|------------------|-----------|
| TRIVIAL-LOW | Sonnet 5 | 簡單任務用起來快、又省成本 |
| MEDIUM | Sonnet 5 | 一般工作最好的寫程式模型 |
| HIGH | Sonnet 5（主要）+ Opus 5（規劃） | 架構用 Opus，實作用 Sonnet |
| EPIC | Opus 5（blueprint）+ Sonnet 5（執行） | 多 session 規劃需要深度推理 |

**拆成多份 prompt**（針對 HIGH/EPIC 範圍）：

超過單一 session 能完成的任務，要拆成依序執行的多份 prompt：
- Prompt 1：研究 + 規劃（用 search-first skill，再用 /plan）
- Prompt 2-N：每份 prompt 實作一個階段（每份都以 /verify 結尾）
- 最後一份 Prompt：整合測試 + 對所有階段做 /code-review
- 用 /save-session 和 /resume-session 在 session 之間保留 context

---

## 輸出格式

用這個確切的結構呈現你的分析。回應要使用跟使用者輸入相同的語言。

### Section 1：Prompt 診斷

**優點：** 列出原本的 prompt 做得好的地方。

**問題：**

| 問題 | 影響 | 建議的修正 |
|-------|--------|---------------|
| (問題) | (後果) | (怎麼修) |

**需要釐清：** 用編號清單列出使用者應該回答的問題。如果 Phase 0 已經自動偵測到答案，就直接寫出來，不要再問。

### Section 2：建議的 ECC 元件

| 類型 | 元件 | 用途 |
|------|-----------|---------|
| Command | /plan | 寫程式之前先規劃架構 |
| Skill | tdd-workflow | TDD 方法論指引 |
| Agent | code-reviewer | 實作完成後的 review |
| Model | Sonnet 5 | 建議用於這個範圍 |

### Section 3：最佳化的 Prompt：完整版

把完整的最佳化 prompt 放在單一個 fenced code block 裡。這份 prompt 必須自成一體，可以直接複製貼上。要包含：
- 附帶背景的清楚任務描述
- 技術堆疊（偵測到的或指定的）
- 在正確的工作流程階段呼叫 /command
- 驗收標準
- 驗證步驟
- 範圍邊界（什麼事不要做）

提到 blueprint 的項目，要寫成：「Use the blueprint skill to...」（不要寫成 `/blueprint`，因為 blueprint 是 skill，不是 command）。

### Section 4：最佳化的 Prompt：快速版

給有經驗的 ECC 使用者用的精簡版本。依意圖類型而有所不同：

| 意圖 | 快速模式 |
|--------|--------------|
| New Feature | `/plan [feature]. /tdd to implement. /code-review. /verify.` |
| Bug Fix | `/tdd — write failing test for [bug]. Fix to green. /verify.` |
| Refactor | `/refactor-clean [scope]. /code-review. /verify.` |
| Research | `Use search-first skill for [topic]. /plan based on findings.` |
| Testing | `/tdd [module]. /e2e for critical flows. /test-coverage.` |
| Review | `/code-review. Then use security-reviewer agent.` |
| Docs | `/update-docs. /update-codemaps.` |
| EPIC | `Use blueprint skill for "[objective]". Execute phases with /verify gates.` |

### Section 5：強化的理由

| 強化項目 | 原因 |
|-------------|--------|
| (加了什麼) | (為什麼重要) |

### 結尾

> 不是你要的嗎？告訴我要調整什麼；如果你想要的是執行，而不是 prompt 最佳化，就另外提出一般的任務請求。

---

## 範例

### 觸發範例

- "Optimize this prompt for ECC"
- "Rewrite this prompt so Claude Code uses the right commands"
- "帮我优化这个指令"
- "How should I prompt ECC for this task?"

### 範例 1：模糊的中文 Prompt（偵測到專案）

**使用者輸入：**
```
帮我写一个用户登录页面
```

**Phase 0 偵測到：** `package.json` 含 Next.js 15、TypeScript、Tailwind CSS

**最佳化的 Prompt（完整版）：**
```
使用项目现有技术栈（Next.js 15 + TypeScript + Tailwind CSS）实现用户登录页面。

技术要求：
- 沿用项目现有的组件结构和路由约定
- 表单验证使用项目中已有的验证方案（检查是否已用 Zod/Yup/其他）
- 认证方式：沿用项目现有认证方案（如无，默认 JWT）
- 包含：邮箱/密码登录表单、表单验证、错误提示、加载状态、响应式布局

工作流：
1. /plan 先规划组件结构和认证流程，参考现有页面的模式
2. /tdd 测试先行：编写登录表单的单元测试和认证流程的集成测试
3. 实现登录页面和认证逻辑
4. /code-review 审查实现
5. /verify 验证所有测试通过且页面正常渲染

安全要求：
- 密码不明文传输
- 防止暴力破解（rate limiting）
- XSS 防护
- CSRF token

验收标准：
- 所有测试通过，覆盖率 80%+
- 页面在移动端和桌面端正常渲染
- 登录成功跳转到 dashboard，失败显示错误信息

不要做：
- 不要实现注册页面
- 不要实现忘记密码功能
- 不要修改现有的路由结构
```

### 範例 2：中等程度的英文 Prompt

**使用者輸入：**
```
Add a REST API endpoint for user profile updates with validation
```

**Phase 0 偵測到：** `go.mod` 含 Go 1.22、Chi router

**最佳化的 Prompt（完整版）：**
```
Add a REST API endpoint for user profile updates (PATCH /api/users/:id).

Tech stack: Go 1.22 + Chi router (detected from project)

Requirements:
- PATCH /api/users/:id — partial update of user profile
- Input validation for fields: name, email, avatar_url, bio
- Auth: require valid token, users can only update own profile
- Return 200 with updated user on success
- Return 400 with validation errors on invalid input
- Return 401/403 for auth failures
- Follow existing API patterns in the codebase

Workflow:
1. /plan the endpoint structure, middleware chain, and validation logic
2. /tdd — write table-driven tests for success, validation failure, auth failure, not-found
3. Implement following existing handler patterns
4. /go-review
5. /verify — run full test suite, confirm no regressions

Do not:
- Modify existing endpoints
- Change the database schema (use existing user table)
- Add new dependencies without checking existing ones first (use search-first skill)
```

### 範例 3：EPIC 專案

**使用者輸入：**
```
Migrate our monolith to microservices
```

**最佳化的 Prompt（完整版）：**
```
Use the blueprint skill to plan: "Migrate monolith to microservices architecture"

Before executing, answer these questions in the blueprint:
1. Which domain boundaries exist in the current monolith?
2. Which service should be extracted first (lowest coupling)?
3. Communication pattern: REST APIs, gRPC, or event-driven (Kafka/RabbitMQ)?
4. Database strategy: shared DB initially or database-per-service from start?
5. Deployment target: Kubernetes, Docker Compose, or serverless?

The blueprint should produce phases like:
- Phase 1: Identify service boundaries and create domain map
- Phase 2: Set up infrastructure (API gateway, service mesh, CI/CD per service)
- Phase 3: Extract first service (strangler fig pattern)
- Phase 4: Verify with integration tests, then extract next service
- Phase N: Decommission monolith

Each phase = 1 PR, with /verify gates between phases.
Use /save-session between phases. Use /resume-session to continue.
Use git worktrees for parallel service extraction when dependencies allow.

Recommended: Opus 5 for blueprint planning, Sonnet 5 for phase execution.
```

---

## 相關元件

| 元件 | 何時參考 |
|-----------|------------------|
| `configure-ecc` | 使用者還沒設定 ECC |
| `skill-stocktake` | 稽核已安裝哪些元件（用它，不要用寫死的目錄） |
| `search-first` | 最佳化 prompt 中的研究階段 |
| `blueprint` | EPIC 範圍的最佳化 prompt（當成 skill 呼叫，不要當成 command） |
| `strategic-compact` | 長 session 的 context 管理 |
| `cost-aware-llm-pipeline` | Token 最佳化的建議 |
