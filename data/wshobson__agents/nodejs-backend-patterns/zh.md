---
name: nodejs-backend-patterns
description: 用 Express/Fastify 建構可上線的 Node.js 後端服務，實作 middleware 模式、錯誤處理、驗證授權、資料庫整合與 API 設計最佳實務。在建立 Node.js 伺服器、REST API、GraphQL 後端或 microservices 架構時使用。
---

# Node.js Backend Patterns

用現代框架、架構模式與最佳實務，建構可擴展、好維護、可上線的 Node.js 後端應用的完整指引。

## When to Use This Skill

- 建構 REST API 或 GraphQL 伺服器
- 用 Node.js 建立 microservices
- 實作驗證與授權
- 設計可擴展的後端架構
- 設定 middleware 與錯誤處理
- 整合資料庫（SQL 與 NoSQL）
- 用 WebSockets 建構即時應用
- 實作背景工作處理

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Best Practices

1. **使用 TypeScript**：型別安全能預防執行期錯誤
2. **實作適當的錯誤處理**：使用自訂的錯誤 class
3. **驗證輸入**：用 Zod 或 Joi 這類函式庫
4. **使用環境變數**：絕對不要把機密寫死在程式碼裡
5. **實作 logging**：使用結構化 logging（Pino、Winston）
6. **加上 rate limiting**：防止濫用
7. **使用 HTTPS**：正式環境一律要用
8. **正確實作 CORS**：正式環境不要用 `*`
9. **使用 dependency injection**：更好測試與維護
10. **寫測試**：單元、整合與 E2E 測試
11. **處理 graceful shutdown**：清理資源
12. **使用 connection pooling**：用於資料庫
13. **實作 health check**：用於監控
14. **使用壓縮**：縮小回應大小
15. **監控效能**：使用 APM 工具

## Testing Patterns

完整的測試指引請見 `javascript-testing-patterns` skill。
