---
name: python-design-patterns
description: Python 設計模式，包含 KISS、關注點分離、單一職責與組合優於繼承。在從頭設計新的服務或元件並決定如何分層職責、重構長太大的 God class 或龐大函式、決定要新增抽象還是容忍重複、評估 pull request 是否有緊耦合或洩漏內部型別這類結構問題、為新的 class 階層選擇繼承或組合，或程式碼庫因為 I/O 與業務邏輯糾纏而越來越難測試時使用這個 skill。
---

# Python Design Patterns

用基本的設計原則撰寫好維護的 Python 程式碼。這些模式幫你打造容易理解、測試與修改的系統。

## When to Use This Skill

- 設計新的元件或服務
- 重構複雜或糾結的程式碼
- 決定要不要建立抽象
- 在繼承與組合之間做選擇
- 評估程式碼的複雜度與耦合
- 規劃模組化架構

## Core Concepts

### 1. KISS (Keep It Simple)

選擇行得通的最簡單解法。複雜度必須有具體的需求來證明它合理。

### 2. Single Responsibility (SRP)

每個單元應該只有一個改變的理由。把關注點分離到各自專注的元件。

### 3. Composition Over Inheritance

用組合物件來建立行為，不是擴充 class。

### 4. Rule of Three

等到有三個實例再去抽象。重複通常比過早的抽象好。

## Quick Start

```python
# Simple beats clever
# Instead of a factory/registry pattern:
FORMATTERS = {"json": JsonFormatter, "csv": CsvFormatter}

def get_formatter(name: str) -> Formatter:
    return FORMATTERS[name]()
```

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Best Practices Summary

1. **保持簡單** - 選擇行得通的最簡單解法
2. **單一職責** - 每個單元只有一個改變的理由
3. **分離關注點** - 用目的清楚的不同層級
4. **用組合，不要繼承** - 組合物件以獲得彈性
5. **三次法則** - 先等一等再抽象
6. **讓函式保持小** - 20 到 50 行（依複雜度而異），只做一件事
7. **注入相依** - 用 constructor injection 以利測試
8. **先刪除再抽象** - 先移除死碼，再考慮模式
9. **測試每一層** - 為每個關注點做獨立的測試
10. **明確勝過炫技** - 好讀的程式碼勝過優雅的程式碼

## Troubleshooting

**某個 class 越長越大，似乎有多個職責，但拆開又覺得不對。**
套用「改變的理由」測試：列出所有可能需要修改這個 class 的變更。如果清單裡的項目來自不同領域（例如 HTTP 解析、業務規則和格式化都有），就拆開。如果所有變更都出自同一個領域關注點，這個 class 的大小可能就是恰當的。

**把所有相依都透過 constructor 注入，結果 constructor 有 7 個以上的參數。**
這是一個 class 裡職責太多的徵兆，不是 dependency injection 本身的問題。先把 class 拆成更小的單元，每個 constructor 自然就會變小。

**組合產生了層層巢狀的 wrapper 物件，很難追蹤。**
讓組合保持淺層（2 到 3 層）。如果包裝是唯一的機制，考慮用基於 Protocol 的做法，或簡單的函式組合，會不會比一串 decorator 物件更乾淨。

**三次法則說還不要抽象，但重複造成了 bug，因為其中一份被更新了，另一份沒有。**
以危險的方式漸行漸遠的重複，應該更早抽象。三次法則是經驗法則，不是定律。如果這些副本已經以不正確的方式分歧了，就立刻抽出來，並加上一個測試來驗證共用的行為。

**Service 層從 API 層 import，破壞了相依的方向。**
這是違反分層的問題。Service 層不能從 handler import。引入一個兩邊都能 import 的共用 types/models 層，讓相依箭頭保持向下（API → Service → Repository）。

## Related Skills

- [python-testing-patterns](../python-testing-patterns/SKILL.md) — 利用這裡建立的 dependency injection 結構，獨立測試每一層
- [python-project-structure](../python-project-structure/SKILL.md) — 組織模組與目錄配置，讓層級邊界從一開始就很明確
