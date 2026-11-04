---
name: responsive-design
description: 用 container query、fluid typography、CSS Grid 和 mobile-first 斷點策略，實作現代響應式版面。在建構自適應介面、實作流動式版面，或建立元件層級的響應式行為時使用。
---

# Responsive Design

精通現代響應式設計技巧，打造能在所有螢幕尺寸和裝置情境下順暢適應的介面。

## When to Use This Skill

- 實作 mobile-first 的響應式版面
- 用 container query 做以元件為基礎的響應式
- 建立流動式的字級和間距比例
- 用 CSS Grid 和 Flexbox 建構複雜版面
- 為設計系統設計斷點策略
- 實作響應式圖片和媒體
- 建立自適應的 navigation 模式
- 建構響應式表格和資料呈現

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Best Practices

1. **Mobile-First**：先寫行動版樣式，再往大螢幕強化
2. **Content Breakpoints**：斷點依內容來設，不要依裝置
3. **Fluid Over Fixed**：字級和間距用流動式的值
4. **Container Queries**：用在元件層級的響應式
5. **Test Real Devices**：模擬器抓不到所有問題
6. **Performance**：優化圖片，螢幕外的內容用 lazy load
7. **Touch Targets**：行動版至少維持 44x44px
8. **Logical Properties**：為了國際化，用 inline/block

## Common Issues

- **Horizontal Overflow**：內容超出 viewport
- **Fixed Widths**：用 px 而不是相對單位
- **Viewport Height**：行動瀏覽器上的 100vh 問題
- **Font Size**：行動版文字太小
- **Touch Targets**：按鈕太小，很難點準
- **Aspect Ratio**：圖片被擠壓或拉伸
- **Z-Index Stacking**：overlay 在不同螢幕上壞掉
