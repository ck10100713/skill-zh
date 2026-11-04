---
name: database-migration
description: 跨 ORM 與平台執行資料庫 migration，涵蓋零停機策略、資料轉換和 rollback 流程。適用於搬移資料庫、修改 schema、做資料轉換，或實作零停機 deploy 策略的時候。
---

# 資料庫 Migration

精通跨 ORM（Sequelize、TypeORM、Prisma）的資料庫 schema 與資料 migration，包含 rollback 策略與零停機 deploy。

## 什麼時候用這個 Skill

- 在不同 ORM 之間做 migration
- 進行 schema 轉換
- 在資料庫之間搬資料
- 實作 rollback 流程
- 零停機 deploy
- 資料庫版本升級
- 資料模型重構

## ORM Migration

### Sequelize Migration

```javascript
// migrations/20231201-create-users.js
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.createTable("users", {
      id: {
        type: Sequelize.INTEGER,
        primaryKey: true,
        autoIncrement: true,
      },
      email: {
        type: Sequelize.STRING,
        unique: true,
        allowNull: false,
      },
      createdAt: Sequelize.DATE,
      updatedAt: Sequelize.DATE,
    });
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.dropTable("users");
  },
};

// 執行：npx sequelize-cli db:migrate
// Rollback：npx sequelize-cli db:migrate:undo
```

### TypeORM Migration

```typescript
// migrations/1701234567-CreateUsers.ts
import { MigrationInterface, QueryRunner, Table } from "typeorm";

export class CreateUsers1701234567 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.createTable(
      new Table({
        name: "users",
        columns: [
          {
            name: "id",
            type: "int",
            isPrimary: true,
            isGenerated: true,
            generationStrategy: "increment",
          },
          {
            name: "email",
            type: "varchar",
            isUnique: true,
          },
          {
            name: "created_at",
            type: "timestamp",
            default: "CURRENT_TIMESTAMP",
          },
        ],
      }),
    );
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.dropTable("users");
  }
}

// 執行：npm run typeorm migration:run
// Rollback：npm run typeorm migration:revert
```

### Prisma Migration

```prisma
// schema.prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  createdAt DateTime @default(now())
}

// 產生 migration：npx prisma migrate dev --name create_users
// 套用：npx prisma migrate deploy
```

## Schema 轉換

### 新增帶預設值的欄位

```javascript
// 安全的 migration：新增帶預設值的欄位
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.addColumn("users", "status", {
      type: Sequelize.STRING,
      defaultValue: "active",
      allowNull: false,
    });
  },

  down: async (queryInterface) => {
    await queryInterface.removeColumn("users", "status");
  },
};
```

### 重新命名欄位（零停機）

```javascript
// 步驟 1：新增欄位
module.exports = {
  up: async (queryInterface, Sequelize) => {
    await queryInterface.addColumn("users", "full_name", {
      type: Sequelize.STRING,
    });

    // 從舊欄位複製資料
    await queryInterface.sequelize.query("UPDATE users SET full_name = name");
  },

  down: async (queryInterface) => {
    await queryInterface.removeColumn("users", "full_name");
  },
};

// 步驟 2：更新應用程式改用新欄位

// 步驟 3：移除舊欄位
module.exports = {
  up: async (queryInterface) => {
    await queryInterface.removeColumn("users", "name");
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.addColumn("users", "name", {
      type: Sequelize.STRING,
    });
  },
};
```

### 變更欄位型別

```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    // 大型資料表要用多步驟做法

    // 1. 新增欄位
    await queryInterface.addColumn("users", "age_new", {
      type: Sequelize.INTEGER,
    });

    // 2. 複製並轉換資料
    await queryInterface.sequelize.query(`
      UPDATE users
      SET age_new = CAST(age AS INTEGER)
      WHERE age IS NOT NULL
    `);

    // 3. 刪除舊欄位
    await queryInterface.removeColumn("users", "age");

    // 4. 重新命名新欄位
    await queryInterface.renameColumn("users", "age_new", "age");
  },

  down: async (queryInterface, Sequelize) => {
    await queryInterface.changeColumn("users", "age", {
      type: Sequelize.STRING,
    });
  },
};
```

## 資料轉換

### 複雜的資料 Migration

```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    // 取得所有記錄
    const [users] = await queryInterface.sequelize.query(
      "SELECT id, address_string FROM users",
    );

    // 轉換每一筆記錄
    for (const user of users) {
      const addressParts = user.address_string.split(",");

      await queryInterface.sequelize.query(
        `UPDATE users
         SET street = :street,
             city = :city,
             state = :state
         WHERE id = :id`,
        {
          replacements: {
            id: user.id,
            street: addressParts[0]?.trim(),
            city: addressParts[1]?.trim(),
            state: addressParts[2]?.trim(),
          },
        },
      );
    }

    // 刪除舊欄位
    await queryInterface.removeColumn("users", "address_string");
  },

  down: async (queryInterface, Sequelize) => {
    // 重建原本的欄位
    await queryInterface.addColumn("users", "address_string", {
      type: Sequelize.STRING,
    });

    await queryInterface.sequelize.query(`
      UPDATE users
      SET address_string = CONCAT(street, ', ', city, ', ', state)
    `);

    await queryInterface.removeColumn("users", "street");
    await queryInterface.removeColumn("users", "city");
    await queryInterface.removeColumn("users", "state");
  },
};
```

## Rollback 策略

### 以 Transaction 為基礎的 Migration

```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    const transaction = await queryInterface.sequelize.transaction();

    try {
      await queryInterface.addColumn(
        "users",
        "verified",
        { type: Sequelize.BOOLEAN, defaultValue: false },
        { transaction },
      );

      await queryInterface.sequelize.query(
        "UPDATE users SET verified = true WHERE email_verified_at IS NOT NULL",
        { transaction },
      );

      await transaction.commit();
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  },

  down: async (queryInterface) => {
    await queryInterface.removeColumn("users", "verified");
  },
};
```

### 以 Checkpoint 為基礎的 Rollback

```javascript
module.exports = {
  up: async (queryInterface, Sequelize) => {
    // 建立備份資料表
    await queryInterface.sequelize.query(
      "CREATE TABLE users_backup AS SELECT * FROM users",
    );

    try {
      // 執行 migration
      await queryInterface.addColumn("users", "new_field", {
        type: Sequelize.STRING,
      });

      // 驗證 migration
      const [result] = await queryInterface.sequelize.query(
        "SELECT COUNT(*) as count FROM users WHERE new_field IS NULL",
      );

      if (result[0].count > 0) {
        throw new Error("Migration verification failed");
      }

      // 刪除備份
      await queryInterface.dropTable("users_backup");
    } catch (error) {
      // 從備份還原
      await queryInterface.sequelize.query("DROP TABLE users");
      await queryInterface.sequelize.query(
        "CREATE TABLE users AS SELECT * FROM users_backup",
      );
      await queryInterface.dropTable("users_backup");
      throw error;
    }
  },
};
```

## 其他模式與範本

更多詳細範本和實作範例放在 `references/details.md`，要完整的模式庫就去讀那份檔案。

