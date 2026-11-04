---
name: e2e-testing-patterns
description: 精通用 Playwright 和 Cypress 做端對端測試，建立可靠的測試套件，抓出 bug、提升信心並支援快速 deploy。適用於實作 E2E 測試、除錯不穩定的測試，或建立測試標準的時候。
---

# E2E 測試模式

建立可靠、快速又好維護的端對端測試套件，讓你有信心快速出貨，並在使用者之前抓到 regression。

## 什麼時候用這個 Skill

- 實作端對端測試自動化
- 除錯不穩定或不可靠的測試
- 測試關鍵的使用者流程
- 建立 CI/CD 測試 pipeline
- 跨多個瀏覽器測試
- 驗證無障礙需求
- 測試響應式設計
- 建立 E2E 測試標準

## 核心概念

### 1. E2E 測試基礎

**E2E 該測什麼：**

- 關鍵的使用者路徑（登入、結帳、註冊）
- 複雜的互動（拖放、多步驟表單）
- 跨瀏覽器相容性
- 真實的 API 整合
- 驗證流程

**E2E 不該測什麼：**

- 單元層級的邏輯（用單元測試）
- API 契約（用整合測試）
- 邊界案例（太慢）
- 內部實作細節

### 2. 測試哲學

**測試金字塔：**

```
        /\
       /E2E\         ← 少量，聚焦在關鍵路徑
      /─────\
     /Integr\        ← 較多，測試元件之間的互動
    /────────\
   /Unit Tests\      ← 大量、快速、隔離
  /────────────\
```

**最佳實務：**

- 測試使用者行為，不要測實作
- 讓測試彼此獨立
- 讓測試具有確定性
- 針對速度最佳化
- 用 data-testid，不要用 CSS selector

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務

1. **使用 Data Attribute**：用 `data-testid` 或 `data-cy` 取得穩定的 selector
2. **避免脆弱的 Selector**：不要依賴 CSS class 或 DOM 結構
3. **測試使用者行為**：點擊、輸入、看到結果，不是實作細節
4. **讓測試彼此獨立**：每個測試都應該能單獨執行
5. **清理測試資料**：每個測試都自己建立、自己銷毀測試資料
6. **使用 Page Object**：封裝頁面邏輯
7. **有意義的斷言**：檢查使用者實際看得到的行為
8. **針對速度最佳化**：能 mock 就 mock，平行執行

```typescript
// ❌ 不好的 selector
cy.get(".btn.btn-primary.submit-button").click();
cy.get("div > form > div:nth-child(2) > input").type("text");

// ✅ 好的 selector（findBy* 指令來自 @testing-library/cypress；
// 請在你的 Cypress support 檔案加上 `import "@testing-library/cypress/add-commands";`）
cy.findByRole("button", { name: "Submit" }).click();
cy.findByLabelText("Email address").type("user@example.com");
cy.get('[data-testid="email-input"]').type("user@example.com");
```

## 常見陷阱

- **不穩定的測試**：要用適當的 wait，不要用固定的 timeout
- **緩慢的測試**：mock 外部 API，使用平行執行
- **過度測試**：不要用 E2E 測每一個邊界案例
- **互相耦合的測試**：測試之間不該彼此依賴
- **糟糕的 selector**：避免 CSS class 和 nth-child
- **沒有清理**：每個測試之後都要清理測試資料
- **測到實作細節**：測使用者行為，不是內部細節

## 除錯失敗的測試

```typescript
// Playwright 除錯
// 1. 用 headed 模式執行
npx playwright test --headed

// 2. 用 debug 模式執行
npx playwright test --debug

// 3. 使用 trace viewer（在設定檔用 `use: { trace: 'on-first-retry' }` 來錄製）
npx playwright show-trace path/to/trace.zip
await page.screenshot({ path: 'screenshot.png' });

// 4. 加上 test.step 讓報告更清楚
test('checkout flow', async ({ page }) => {
    await test.step('Add item to cart', async () => {
        await page.goto('/products');
        await page.getByRole('button', { name: 'Add to Cart' }).click();
    });

    await test.step('Proceed to checkout', async () => {
        await page.goto('/cart');
        await page.getByRole('button', { name: 'Checkout' }).click();
    });
});

// 5. 檢查頁面狀態
await page.pause();  // 暫停執行，開啟 inspector
```
