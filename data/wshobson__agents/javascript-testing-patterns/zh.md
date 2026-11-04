---
name: javascript-testing-patterns
description: 用 Jest、Vitest 和 Testing Library 實作完整的測試策略，涵蓋單元測試、整合測試與端對端測試，包含 mock、fixture 與測試驅動開發。適用於撰寫 JavaScript/TypeScript 測試、建立測試基礎設施，或實作 TDD/BDD 流程的時候。
---

# JavaScript 測試模式

用現代的測試 framework 與最佳實務，在 JavaScript/TypeScript 應用中實作穩健測試策略的完整指南。

## 什麼時候用這個 Skill

- 為新專案建立測試基礎設施
- 為函式和類別撰寫單元測試
- 為 API 和服務建立整合測試
- 為使用者流程實作端對端測試
- Mock 外部相依與 API
- 測試 React、Vue 或其他前端元件
- 實作測試驅動開發（TDD）
- 在 CI/CD pipeline 中建立持續測試

## 測試 Framework

### Jest：功能完整的測試 Framework

**設定：**

```typescript
// jest.config.ts
import type { Config } from "jest";

const config: Config = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/src"],
  testMatch: ["**/__tests__/**/*.ts", "**/?(*.)+(spec|test).ts"],
  collectCoverageFrom: [
    "src/**/*.ts",
    "!src/**/*.d.ts",
    "!src/**/*.interface.ts",
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ["<rootDir>/src/test/setup.ts"],
};

export default config;
```

### Vitest：快速、Vite 原生的測試

**設定：**

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: ["**/*.d.ts", "**/*.config.ts", "**/dist/**"],
    },
    setupFiles: ["./src/test/setup.ts"],
  },
});
```

## 單元測試模式

### 模式 1：測試純函式

```typescript
// utils/calculator.ts
export function add(a: number, b: number): number {
  return a + b;
}

export function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("Division by zero");
  }
  return a / b;
}

// utils/calculator.test.ts
import { describe, it, expect } from "vitest";
import { add, divide } from "./calculator";

describe("Calculator", () => {
  describe("add", () => {
    it("should add two positive numbers", () => {
      expect(add(2, 3)).toBe(5);
    });

    it("should add negative numbers", () => {
      expect(add(-2, -3)).toBe(-5);
    });

    it("should handle zero", () => {
      expect(add(0, 5)).toBe(5);
      expect(add(5, 0)).toBe(5);
    });
  });

  describe("divide", () => {
    it("should divide two numbers", () => {
      expect(divide(10, 2)).toBe(5);
    });

    it("should handle decimal results", () => {
      expect(divide(5, 2)).toBe(2.5);
    });

    it("should throw error when dividing by zero", () => {
      expect(() => divide(10, 0)).toThrow("Division by zero");
    });
  });
});
```

### 模式 2：測試類別

```typescript
// services/user.service.ts
export class UserService {
  private users: Map<string, User> = new Map();

  create(user: User): User {
    if (this.users.has(user.id)) {
      throw new Error("User already exists");
    }
    this.users.set(user.id, user);
    return user;
  }

  findById(id: string): User | undefined {
    return this.users.get(id);
  }

  update(id: string, updates: Partial<User>): User {
    const user = this.users.get(id);
    if (!user) {
      throw new Error("User not found");
    }
    const updated = { ...user, ...updates };
    this.users.set(id, updated);
    return updated;
  }

  delete(id: string): boolean {
    return this.users.delete(id);
  }
}

// services/user.service.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { UserService } from "./user.service";

describe("UserService", () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  describe("create", () => {
    it("should create a new user", () => {
      const user = { id: "1", name: "John", email: "john@example.com" };
      const created = service.create(user);

      expect(created).toEqual(user);
      expect(service.findById("1")).toEqual(user);
    });

    it("should throw error if user already exists", () => {
      const user = { id: "1", name: "John", email: "john@example.com" };
      service.create(user);

      expect(() => service.create(user)).toThrow("User already exists");
    });
  });

  describe("update", () => {
    it("should update existing user", () => {
      const user = { id: "1", name: "John", email: "john@example.com" };
      service.create(user);

      const updated = service.update("1", { name: "Jane" });

      expect(updated.name).toBe("Jane");
      expect(updated.email).toBe("john@example.com");
    });

    it("should throw error if user not found", () => {
      expect(() => service.update("999", { name: "Jane" })).toThrow(
        "User not found",
      );
    });
  });
});
```

### 模式 3：測試非同步函式

```typescript
// services/api.service.ts
export class ApiService {
  async fetchUser(id: string): Promise<User> {
    const response = await fetch(`https://api.example.com/users/${id}`);
    if (!response.ok) {
      throw new Error("User not found");
    }
    return response.json();
  }

  async createUser(user: CreateUserDTO): Promise<User> {
    const response = await fetch("https://api.example.com/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(user),
    });
    return response.json();
  }
}

// services/api.service.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ApiService } from "./api.service";

// 全域 mock fetch
global.fetch = vi.fn();

describe("ApiService", () => {
  let service: ApiService;

  beforeEach(() => {
    service = new ApiService();
    vi.clearAllMocks();
  });

  describe("fetchUser", () => {
    it("should fetch user successfully", async () => {
      const mockUser = { id: "1", name: "John", email: "john@example.com" };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const user = await service.fetchUser("1");

      expect(user).toEqual(mockUser);
      expect(fetch).toHaveBeenCalledWith("https://api.example.com/users/1");
    });

    it("should throw error if user not found", async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: false,
      });

      await expect(service.fetchUser("999")).rejects.toThrow("User not found");
    });
  });

  describe("createUser", () => {
    it("should create user successfully", async () => {
      const newUser = { name: "John", email: "john@example.com" };
      const createdUser = { id: "1", ...newUser };

      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => createdUser,
      });

      const user = await service.createUser(newUser);

      expect(user).toEqual(createdUser);
      expect(fetch).toHaveBeenCalledWith(
        "https://api.example.com/users",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify(newUser),
        }),
      );
    });
  });
});
```

## Mock 模式

### 模式 1：Mock 模組

```typescript
// services/email.service.ts
import nodemailer from "nodemailer";

export class EmailService {
  private transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: 587,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  });

  async sendEmail(to: string, subject: string, html: string) {
    await this.transporter.sendMail({
      from: process.env.EMAIL_FROM,
      to,
      subject,
      html,
    });
  }
}

// services/email.service.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { EmailService } from "./email.service";

vi.mock("nodemailer", () => ({
  default: {
    createTransport: vi.fn(() => ({
      sendMail: vi.fn().mockResolvedValue({ messageId: "123" }),
    })),
  },
}));

describe("EmailService", () => {
  let service: EmailService;

  beforeEach(() => {
    service = new EmailService();
  });

  it("should send email successfully", async () => {
    await service.sendEmail(
      "test@example.com",
      "Test Subject",
      "<p>Test Body</p>",
    );

    expect(service["transporter"].sendMail).toHaveBeenCalledWith(
      expect.objectContaining({
        to: "test@example.com",
        subject: "Test Subject",
      }),
    );
  });
});
```

### 模式 2：為測試做 Dependency Injection

```typescript
// services/user.service.ts
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  create(user: User): Promise<User>;
}

export class UserService {
  constructor(private userRepository: IUserRepository) {}

  async getUser(id: string): Promise<User> {
    const user = await this.userRepository.findById(id);
    if (!user) {
      throw new Error("User not found");
    }
    return user;
  }

  async createUser(userData: CreateUserDTO): Promise<User> {
    // 商業邏輯放在這裡
    const user = { id: generateId(), ...userData };
    return this.userRepository.create(user);
  }
}

// services/user.service.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { UserService, IUserRepository } from "./user.service";

describe("UserService", () => {
  let service: UserService;
  let mockRepository: IUserRepository;

  beforeEach(() => {
    mockRepository = {
      findById: vi.fn(),
      create: vi.fn(),
    };
    service = new UserService(mockRepository);
  });

  describe("getUser", () => {
    it("should return user if found", async () => {
      const mockUser = { id: "1", name: "John", email: "john@example.com" };
      vi.mocked(mockRepository.findById).mockResolvedValue(mockUser);

      const user = await service.getUser("1");

      expect(user).toEqual(mockUser);
      expect(mockRepository.findById).toHaveBeenCalledWith("1");
    });

    it("should throw error if user not found", async () => {
      vi.mocked(mockRepository.findById).mockResolvedValue(null);

      await expect(service.getUser("999")).rejects.toThrow("User not found");
    });
  });

  describe("createUser", () => {
    it("should create user successfully", async () => {
      const userData = { name: "John", email: "john@example.com" };
      const createdUser = { id: "1", ...userData };

      vi.mocked(mockRepository.create).mockResolvedValue(createdUser);

      const user = await service.createUser(userData);

      expect(user).toEqual(createdUser);
      expect(mockRepository.create).toHaveBeenCalled();
    });
  });
});
```

### 模式 3：Spy 函式

```typescript
// utils/logger.ts
export const logger = {
  info: (message: string) => console.log(`INFO: ${message}`),
  error: (message: string) => console.error(`ERROR: ${message}`),
};

// services/order.service.ts
import { logger } from "../utils/logger";

export class OrderService {
  async processOrder(orderId: string): Promise<void> {
    logger.info(`Processing order ${orderId}`);
    // 處理訂單的邏輯
    logger.info(`Order ${orderId} processed successfully`);
  }
}

// services/order.service.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { OrderService } from "./order.service";
import { logger } from "../utils/logger";

describe("OrderService", () => {
  let service: OrderService;
  let loggerSpy: any;

  beforeEach(() => {
    service = new OrderService();
    loggerSpy = vi.spyOn(logger, "info");
  });

  afterEach(() => {
    loggerSpy.mockRestore();
  });

  it("should log order processing", async () => {
    await service.processOrder("123");

    expect(loggerSpy).toHaveBeenCalledWith("Processing order 123");
    expect(loggerSpy).toHaveBeenCalledWith("Order 123 processed successfully");
    expect(loggerSpy).toHaveBeenCalledTimes(2);
  });
});
```

## 整合測試

整合測試使用 `supertest` 和測試用資料庫實例，驗證真實的資料庫操作和 HTTP endpoint。一定要在 `beforeEach` 清空資料表，並在 `afterAll` 收尾。

完整的 API 整合測試範例（supertest + PostgreSQL）和資料庫 repository 整合測試，請見 [references/advanced-testing-patterns.md](references/advanced-testing-patterns.md)。

## 用 Testing Library 做前端測試

透過 render 來測試 React 元件，並用 role、placeholder 或 test ID 來查詢。用 `renderHook` + `act` 測試 hook。優先使用語意化的查詢（`getByRole`、`getByPlaceholderText`），而不是 `data-testid`。

完整的 React 元件測試範例（UserForm、搭配 `renderHook`/`act` 的 hook），請見 [references/advanced-testing-patterns.md](references/advanced-testing-patterns.md)。

## 測試 Fixture 與 Factory

用 `@faker-js/faker` 產生逼真的測試資料 factory。Factory 接受選用的 `overrides`，讓測試只需設定它們在意的欄位：

```typescript
// tests/fixtures/user.fixture.ts
import { faker } from "@faker-js/faker";

export function createUserFixture(overrides?: Partial<User>): User {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    createdAt: faker.date.past(),
    ...overrides,
  };
}
```

關於 snapshot 測試、coverage 設定、測試組織模式、promise 測試和 timer mock，請見 [references/advanced-testing-patterns.md](references/advanced-testing-patterns.md)。

## 最佳實務

1. **遵循 AAA 模式**：Arrange、Act、Assert
2. **每個測試一個斷言**：或邏輯上相關的斷言
3. **有描述性的測試名稱**：應該描述被測的是什麼
4. **使用 beforeEach/afterEach**：用於 setup 和 teardown
5. **Mock 外部相依**：讓測試保持隔離
6. **測試邊界案例**：不只是 happy path
7. **避免實作細節**：測行為，不要測實作
8. **使用測試 factory**：取得一致的測試資料
9. **讓測試保持快速**：Mock 慢的操作
10. **先寫測試（TDD）**：可以的話
11. **維持測試覆蓋率**：目標 80%+ 覆蓋率
12. **使用 TypeScript**：寫出型別安全的測試
13. **測試錯誤處理**：不只是成功的情況
14. **少用 data-testid**：優先用語意化的查詢
15. **測試後要清理**：避免測試之間互相污染
