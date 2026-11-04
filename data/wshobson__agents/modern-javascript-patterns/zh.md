---
name: modern-javascript-patterns
description: 精通 ES6+ 功能，包含 async/await、解構、spread 運算子、箭頭函式、promise、module、iterator、generator 與函式程式設計模式，寫出乾淨、有效率的 JavaScript。在重構舊程式碼、實作現代寫法或最佳化 JavaScript 應用時使用。
---

# Modern JavaScript Patterns

精通現代 JavaScript（ES6+）功能、函式程式設計模式與最佳實務的完整指南，用來寫出乾淨、好維護又有效能的程式碼。

## When to Use This Skill

- 把舊的 JavaScript 重構成現代語法
- 實作函式程式設計模式
- 最佳化 JavaScript 效能
- 撰寫好維護、好閱讀的程式碼
- 處理非同步操作
- 建構現代 web 應用
- 從 callback 遷移到 Promise/async-await
- 實作資料轉換 pipeline

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Best Practices

1. **預設用 const**：只有需要重新賦值時才用 let
2. **優先用箭頭函式**：尤其是 callback
3. **使用 template literal**：取代字串串接
4. **解構物件和陣列**：讓程式碼更乾淨
5. **使用 async/await**：取代 Promise 鏈
6. **避免修改資料**：用 spread 運算子和陣列方法
7. **使用 optional chaining**：避免「Cannot read property of undefined」
8. **使用 nullish coalescing**：處理預設值
9. **優先用陣列方法**：取代傳統迴圈
10. **使用 module**：讓程式碼組織更好
11. **寫 pure function**：更好測試、更好推理
12. **使用有意義的變數名稱**：程式碼本身就是文件
13. **讓函式保持小**：單一職責原則
14. **正確處理錯誤**：搭配 async/await 使用 try/catch
15. **使用 strict mode**：`'use strict'` 能更早抓到錯誤

常見的陷阱（this 綁定、promise 反模式、記憶體洩漏）請見 [references/advanced-patterns.md](references/advanced-patterns.md)。
