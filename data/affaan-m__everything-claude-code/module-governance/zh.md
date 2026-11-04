---
name: module-governance
description: >-
  實作新模組或變更其職責時，建立或維護某個業務模組的本地 agent 指示、領域 context 連結和介面所有權。重用專案層級的規則和既有的 ECC 流程；一般的 bug 修復、樣式調整和唯讀的設計討論，不會啟動模組文件的設置。
metadata:
  origin: ECC
---

# Module Governance

把模組層級的工作規則，接到既有的領域語言、合約和決策上。
這是一個統籌用的 skill，不是第二套 DDD 方法論，也不是自動產生文件的工具。

## When to Activate

- 使用者要求實作新的業務模組，不需要點名這個 skill。
- 使用者要求為既有模組寫文件，或維護一項已確認的職責變更。
- 已授權的模組變更，需要本地指示和權威知識的指標。

一般的 bug、樣式變更、邊界不變的內部重構，或只是單純沿用上層慣例的新目錄 / UI 元件，
都不要啟動設置。只是設計討論或單純稽核的話，檢查並回報就好，
不要建立檔案。依意圖選用 skill 不是背景 hook，
也不代表可以對不相關的程式碼、commit、push 或商業選擇有任何授權。

## How It Works

### 1. Discover the boundary before creating documents

讀適用的專案和上層 harness 指示、既有的地圖、需求、相關程式碼和合約。找出模組的職責、
非職責、狀態所有權和實際的使用者。光看目錄名稱
不足以確立一個 bounded context。有重大的模糊之處時要提出來，不要
自己發明商業規則。

對既有邊界的變更，先用 `change-impact`。它的唯讀和
授權限制仍然適用；不要跑不相關的開發流程。

### 2. Separate project-wide rules from local rules

專案層級的指示來源擁有全域限制、模組導覽
和跨模組協作。本地的 `AGENTS.md` 只擁有額外的模組
限制：職責、狀態所有權、公開介面的指標和
驗證的入口。本地規則不能豁免專案層級的限制。

重用既有的 `CLAUDE.md` 或其他正在使用的 harness 介面，不要
強迫改名或維護兩份副本。如果上層指示已經
涵蓋這個模組，而且沒有缺少任何本地規則，就連到那個來源，不要建立
多餘的本地檔案。遵守既有明確要求的本地入口點。
不要宣稱 harness 會自動載入每個巢狀的指示檔。

### 3. Reuse the existing knowledge owners

| 資訊 | 既有的 ECC 負責者 |
|---|---|
| 穩定的術語和概念關係 | `context-and-decisions`，使用既有的詞彙表或 context 角色 |
| 難以回頭的決策和理由 | `architecture-decision-records`，透過既有的 context 交接 |
| 跨邊界、可由機器檢查的介面 | `contract-first` |
| 文件導覽和生命週期 | `living-docs-governance` |
| 受影響的使用者和邊界變更的證據 | `change-impact` |

需要某個 skill 的工作時才載入它；不要在這裡重複它的方法。
術語放在相關的既有 `CONTEXT.md` 或同等檔案裡，
不要放在 AGENTS 裡。同一個業務 context 的前端和後端可以共用那份
詞彙表；UI 專屬的工作規則可以放在本地，不需要
每個頁面各建一份詞彙表。重用既有的合約和 ADR 時用參照，不要複製它們的內文。

### 4. Maintain only the authorized records

在使用者要求的模組工作範圍內，只更新最小的、缺少的本地規則
和已確認的 context 條目。受影響的導覽和生命週期更新用 `living-docs-governance`，
並保留它對新的頂層成品要求核准的規定。
不要為了湊「兩個檔案」的配額而建立空檔案。實作
還不存在時，把邊界標成「已確認的設計，程式碼尚未驗證」；
不要光憑文字就宣稱文件和程式碼一致。

### 5. Verify both meaning and links

把每個宣稱的負責者、介面和限制，拿去對照程式碼、權威
合約和可執行的證據。把矛盾回報給負責人去解決；
不要只為了配合某個偶然的實作就改寫規則。

相對連結要從**每份引用文件所在的目錄**解析，不是從終端機的
工作目錄。解析已安裝的 `docs-governance` skill 路徑，
並把它既有的唯讀連結檢查，當作雙方同意的驗證步驟來跑：

```bash
python3 <docs-governance-skill>/scripts/audit-docs.py --root <repository> --scope modules --module <module-directory>
```

確認稽核有掃到有變動的本地指示、context 和
導覽；檢查它的連結結果和 exit code。修好壞掉的參照後重跑，
不要建立空的目標檔。如果腳本不可用，或排除了某個目標，
就把那個目標回報為未驗證。商業測試通過不代表連結
正確，而同名的既有檔案也可能是錯誤的知識負責者。

## Examples

- **「實作庫存模組。」** 檢查既有的邊界；只為真正新增的限制加本地
  規則；重用領域詞彙表和 API
  合約；從既有的導覽連到它們；驗證程式碼和相對於來源的連結。
- **「付款應該拆成獨立模組嗎？」** 說明邊界的選項和
  證據，不要寫檔案，也不要把這場討論當成實作核准。
- **「修庫存徽章的顏色。」** 讀適用的指示，修好
  被要求的 UI 行為；不要產生 AGENTS、CONTEXT 或 ADR 文件。
- **「稽核模組文件。」** 用既有的唯讀稽核和語意
  審查；缺少本地檔案本身不代表可以建立。

## Anti-Patterns

- 每個目錄或前端頁面都強制要有一組 AGENTS/CONTEXT。
- 重複全域限制、詞彙表定義、合約或 ADR 的理由。
- 把文件檢查當成商業實作已完成的證明。
- 沒有真正的 harness 串接，就安裝 hook 或斷言會自動載入巢狀檔案。

## Delivery

回報權威紀錄的路徑、它們的專案/模組範圍、實際的變更、
驗證證據，以及尚未解決的所有權問題。模組治理
交付的是工作規則和知識入口，不是完整的 DDD 轉換。

## Related Skills

- `context-and-decisions`
- `architecture-decision-records`
- `contract-first`
- `change-impact`
- `living-docs-governance`
- `docs-governance`
