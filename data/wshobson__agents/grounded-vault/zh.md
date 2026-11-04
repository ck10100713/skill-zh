---
name: grounded-vault
description: 適用於維護由 agent 從來源編譯而成的持久 Markdown 知識庫、wiki 頁面中每個數字或引文都必須追溯到不可變來源，或編譯後的頁面需要低成本偵測與所描述程式碼之間的 drift 的時候。教你 raw/wiki/archive 的目錄配置、逐項主張的來源連結，以及用 git fingerprint 做零 token 的過期檢查。
---

# Grounded Vault

Grounded vault 是一個三層的 Markdown 儲存庫，其中每一項編譯出來的主張都能追溯回不可變的來源，而且每個頁面只要一個 `git diff` 就能檢查是否過期。
它只需要一個 git repository，不需要其他東西。這個慣例來自 `llm-wiki-loop` 專案，該專案是參考實作，不是相依套件；這個 skill 教的是這套模式，所以用純檔案和 session 裡的任何 agent 都能運作。

## 什麼時候用

- Agent 把筆記、論文、逐字稿、log 或程式碼編譯成 wiki 頁面，之後的 session 會依賴這些頁面。
- 頁面引用了數字、日期或引文，讀者必須能對照來源驗證每一項。
- 頁面描述的是程式碼，而每個 session 都重讀整個 codebase 來確認它們是否仍然成立，成本太高。
- 知識必須能修正，又不丟失歷史：被取代的頁面會被封存，絕不刪除。

Session 狀態、任務佇列和對話的連續性是另一個問題，那些請用 context-management 或 conductor plugin。這個 skill 談的是持久知識庫的來源追溯與 drift。

## 三層結構

| 層 | 內容 | 誰來寫 | 規則 |
|---|---|---|---|
| `raw/` | 來源資料：筆記、論文、逐字稿、log、匯出的資料 | 只有人和資料匯入流程 | 加入之後就不可變；agent 絕對不編輯 raw 檔案 |
| `wiki/` | 從 `raw/` 和程式碼編譯出來的頁面 | agent 和人 | 每個數字、日期和引文都連到它的來源 |
| `archive/` | 已經 drift 或被取代的頁面 | agent，在垃圾回收時 | 只移動，絕不刪除；header 會寫明原因 |

Vault 根目錄有兩個檔案。`index.md` 是每個現行頁面的地圖。`log.md` 是只能附加的紀錄，記錄什麼改了、為什麼改。兩者都跟它們所描述的頁面在同一個 commit 中變更。

## 頁面 Header 規範

每個 `wiki/` 頁面都以一個 header 區塊開頭：

```markdown
# Authentication architecture

> Raw: [raw/notes/auth-v1.md](../raw/notes/auth-v1.md), [raw/adr/0007-jwt.md](../raw/adr/0007-jwt.md)
> Fingerprint: git:5b237fa
> Monitored: src/auth/jwt.ts, src/auth/session.ts, package.json
> Status: Current
```

- `Raw:` 列出這個頁面是由哪些來源編譯而成的。行內的主張也要連到它各自特定的來源：`Tokens expire after 15 minutes ([raw/adr/0007-jwt.md](../raw/adr/0007-jwt.md)).`
- `Fingerprint:` 是這個頁面編譯時所對應的 commit 短 hash。
- `Monitored:` 列出這個頁面所描述的程式碼路徑。fingerprint 之後只要其中任何一個有變動，就代表這個頁面可能過期了。
- `Status:` 是 `Current`、`Outdated`（被監控的程式碼已經往前走了）或 `Disputed`（比較新的來源與這個頁面矛盾）。

## 依據規則（Grounding rule）

編譯出來的頁面只陳述來源所支持的內容，而且每個數字、日期或引文都要逐字出現在連結的來源中。綜合性的內容要自己說明它是綜合，並連到它的輸入。來源中的空缺要在頁面裡寫成空缺，不能靠猜測來補。

用機械的方式檢查：對每個有連結的主張，在連結的 raw 檔案裡搜尋那個確切的數字或引用的片語。找不到就是 grounding 錯誤，會擋住 commit。`references/details.md` 裡的腳本可以對整個 vault 做這件事。

## Drift 偵測

拿 fingerprint 跟目前的樹比較，不要重讀被監控的程式碼：

```bash
git diff --stat 5b237fa..HEAD -- src/auth/jwt.ts src/auth/session.ts package.json
```

輸出是空的，代表這個頁面仍然描述著它編譯時所對應的程式碼。有任何輸出，就要重新編譯：只重讀有變動的檔案、更新頁面，並蓋上新的 fingerprint。這個檢查在毫秒內完成，不花任何模型 token。

## 工作流程

1. **匯入（Ingest）。** 把新的資料放進 `raw/`，檔名要有日期或來源。絕對不要重寫既有的 raw 檔案；在旁邊新增一個。
2. **編譯（Compile）。** 寫入或更新 `wiki/` 頁面，要有 header 區塊、每項主張都附來源連結，以及讀取程式碼時所在 commit 的 fingerprint。
3. **檢查（Check）。** commit 之前先跑 grounding 檢查和 drift 檢查。錯誤要從來源修正；不要為了讓檢查通過而削弱主張。
4. **垃圾回收（Garbage collect）。** 出現 drift 或矛盾的來源，而這個頁面又沒有立刻重新編譯時，就改它的 status、把它移到 `archive/`，並記錄原因：

   ```markdown
   > Status: Outdated
   > Reason: src/auth/session.ts changed after git:5b237fa; see log.md 2026-09-01
   ```

5. **更新地圖。** 每次新增、移動或封存，都要在同一個 commit 中更新 `index.md`，並在 `log.md` 附加一行。

## Commit 關卡

從 pre-commit hook 或 CI 步驟執行這兩個檢查，這樣頁面就不可能帶著無法驗證的數字或過期的 fingerprint 進來：

```bash
python3 scripts/check_vault.py --strict   # 只要有任何 grounding 缺漏或 drift 的頁面就 exit 1
```

## 進一步內容

`references/details.md` 涵蓋：vault 檢查腳本、跨頁面批次執行 drift 檢查、`index.md` 和 `log.md` 的範本、被重新命名或刪除的被監控檔案、二進位或位於外部 URL 的來源，以及參考實作。
