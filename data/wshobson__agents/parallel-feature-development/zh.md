---
name: parallel-feature-development
description: 協調平行的功能開發，涵蓋檔案所有權策略、避免衝突規則，以及多 agent 實作的整合模式。在把大型功能拆成獨立工作流、兩個以上 agent 需要同時實作同一系統的不同層、為在共用程式碼庫中避免 merge conflict 而建立檔案所有權、設計介面契約讓平行的實作者能在對方 API 完成前就先針對它開發，或決定全端功能要用垂直切片還是水平分層時使用。
version: 1.0.2
---

# Parallel Feature Development

把功能拆成平行工作流、建立檔案所有權邊界、避免衝突，並整合多個 implementer agent 的成果的策略。

## When to Use This Skill

- 把功能拆解成可平行實作的部分
- 在 agent 之間建立檔案所有權邊界
- 設計平行工作流之間的介面契約
- 選擇整合策略（垂直切片 vs 水平分層）
- 管理平行開發的 branch 與 merge 流程

## File Ownership Strategies

### By Directory

把特定目錄的所有權指派給各個 implementer：

```
implementer-1: src/components/auth/
implementer-2: src/api/auth/
implementer-3: tests/auth/
```

**最適合**：目錄邊界清楚、組織良好的程式碼庫。

### By Module

指派邏輯模組的所有權（可能橫跨多個目錄）：

```
implementer-1: Authentication module (login, register, logout)
implementer-2: Authorization module (roles, permissions, guards)
```

**最適合**：以功能為導向的架構、領域驅動設計。

### By Layer

指派架構分層的所有權：

```
implementer-1: UI layer (components, styles, layouts)
implementer-2: Business logic layer (services, validators)
implementer-3: Data layer (models, repositories, migrations)
```

**最適合**：傳統的 MVC/分層架構。

## Conflict Avoidance Rules

### The Cardinal Rule

**每個檔案只能有一個擁有者。** 不應該有任何檔案被指派給多個 implementer。

### When Files Must Be Shared

如果某個檔案確實需要多個 implementer 修改：

1. **指定單一擁有者**：由一個 implementer 擁有這個檔案
2. **其他 implementer 提出修改請求**：把具體的修改需求傳訊息給擁有者
3. **擁有者依序套用修改**：避免 merge conflict
4. **替代方案：抽出介面**：建立一個獨立的介面檔，非擁有者可以 import，不用修改它

### Interface Contracts

當 implementer 需要在邊界上協調時：

```typescript
// src/types/auth-contract.ts (owned by team-lead, read-only for implementers)
export interface AuthResponse {
  token: string;
  user: UserProfile;
  expiresAt: number;
}

export interface AuthService {
  login(email: string, password: string): Promise<AuthResponse>;
  register(data: RegisterData): Promise<AuthResponse>;
}
```

兩個 implementer 都從契約檔 import，但誰都不修改它。

## Integration Patterns

### Vertical Slice

每個 implementer 建構一個完整的功能切片（UI + API + 測試）：

```
implementer-1: Login feature (login form + login API + login tests)
implementer-2: Register feature (register form + register API + register tests)
```

**優點**：每個切片都能獨立測試，需要的整合很少。
**缺點**：共用的工具函式可能重複，在高度耦合的功能上比較難做。

### Horizontal Layer

每個 implementer 負責跨所有功能的一個分層：

```
implementer-1: All UI components (login form, register form, profile page)
implementer-2: All API endpoints (login, register, profile)
implementer-3: All tests (unit, integration, e2e)
```

**優點**：每一層內部的模式一致，分工自然。
**缺點**：整合點比較多，第 3 層依賴第 1 層和第 2 層。

### Hybrid

依耦合程度混用垂直與水平：

```
implementer-1: Login feature (vertical slice — UI + API + tests)
implementer-2: Shared auth infrastructure (horizontal — middleware, JWT utils, types)
```

**最適合**：大多數帶有一些共用基礎設施的真實功能。

## Branch Management

### Single Branch Strategy

所有 implementer 都在同一個 feature branch 上工作：

- 設定簡單，沒有 merge 的額外負擔
- 需要嚴格的檔案所有權才能避免衝突
- 最適合：小團隊（2 到 3 人）、邊界定義清楚

### Multi-Branch Strategy

每個 implementer 在一個 sub-branch 上工作：

```
feature/auth
  ├── feature/auth-login      (implementer-1)
  ├── feature/auth-register    (implementer-2)
  └── feature/auth-tests       (implementer-3)
```

- 隔離性更好，merge 點明確
- 額外負擔較高，共用檔案仍然可能有 merge conflict
- 最適合：較大的團隊（4 人以上）、複雜的功能

## Troubleshooting

**Implementer 因為等共用的程式碼而互相卡住。**
把共用的部分抽成獨立的介面契約檔，由 team-lead 擁有，讓 implementer 從它 import。兩邊都不修改契約，只針對它實作。

**即使有明確的所有權規則，還是出現 merge conflict。**
可能是有個檔案被指派給兩個 agent，或是有個自動 import 所有東西的 config/index 檔案（例如 `index.ts`、`__init__.py`）被兩邊都改了。指定一個擁有者負責所有 barrel/index 檔案，或讓 lead 在最後再合併。

**Implementer 提早完成，但整合步驟被卡住。**
使用暫時的介面：做完的 implementer 為下游的相依項目寫一個 stub 或 mock，讓另一個 implementer 可以繼續工作。到整合的時候再換成真正的實作。

**功能拆解做到一半才發現拆錯了。**
停止新的工作，讓 lead 重新分配檔案，並用廣播傳達這個變更。已經寫了一半的程式碼算是沉沒成本，可以接受，繼續用錯誤的切法做下去更糟。

**某個 implementer 寫的測試，對另一個 implementer 寫的程式碼會失敗。**
介面契約飄移了：擁有 API 的 implementer 改了簽章，卻沒通知寫測試的 implementer。要強制執行一條規則：修改契約檔之前必須先廣播。

## Related Skills

- [team-composition-patterns](../team-composition-patterns/SKILL.md) — 在拆解工作之前，先選對團隊規模與 agent 類型
- [team-communication-protocols](../team-communication-protocols/SKILL.md) — 協調 implementer 之間的整合交接與計畫核准
