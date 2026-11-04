---
name: domain-modeling
description: 建立並磨利專案的領域模型。當討論 codebase 的術語、撰寫或編輯 GLOSSARY.md，或記錄或編輯 ADR 時使用。
---

# 領域建模

設計的同時，主動建立並磨利專案的領域模型。這是*主動*的紀律：挑戰用語、發明邊界情境，並且在詞彙和決策一成形時就寫下來。（只是*讀* `GLOSSARY.md` 來取得詞彙不算這個 skill：那是任何 skill 都能做的一行習慣。這個 skill 是用在你要改動模型的時候，不是單純拿來用而已。）

## 檔案結構

大部分的 repo 只有單一 context：

```
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

如果根目錄有 `GLOSSARY-MAP.md`，代表這個 repo 有多個 context。這份 map 會指出每一個 context 放在哪：

```
/
├── GLOSSARY-MAP.md
├── docs/
│   └── adr/                          ← 全系統的決策
├── src/
│   ├── ordering/
│   │   ├── GLOSSARY.md
│   │   └── docs/adr/                 ← 特定 context 的決策
│   └── billing/
│       ├── GLOSSARY.md
│       └── docs/adr/
```

檔案要延遲建立：有東西可寫才建。如果沒有 `GLOSSARY.md`，等第一個術語釐清時再建。如果沒有 `docs/adr/`，等第一份 ADR 需要時再建。

## session 進行中

### 對照詞彙表挑戰用語

當使用者用的術語跟 `GLOSSARY.md` 裡既有的語言衝突，馬上指出來。「你的詞彙表把『cancellation』定義成 X，但你好像是指 Y。到底是哪個？」

### 磨利模糊的語言

當使用者用了模糊或一詞多義的術語，就提出一個精確的標準用語。「你說的『account』：是指 Customer 還是 User？這兩個是不同的東西。」

### 討論具體情境

討論領域關係時，用具體情境去壓力測試。發明能戳到邊界情況的情境，逼使用者把概念之間的界線講精確。

### 跟程式碼對照

當使用者講某個東西怎麼運作，檢查程式碼是否同意。如果發現矛盾，就拿出來講：「你的程式碼會取消整張 Order，但你剛剛說可以部分取消。哪個才對？」

### 當場更新 GLOSSARY.md

術語一釐清，就在當下更新 `GLOSSARY.md`。不要攢著批次處理：發生時就記。格式照 [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md)。

`GLOSSARY.md` 要完全沒有實作細節。不要把 `GLOSSARY.md` 當成 spec、草稿紙，或實作決策的存放處。它就是詞彙表，沒有別的。

### 少提 ADR

只有在以下三點都成立時，才提議建立 ADR：

1. **難以回頭**：之後改變主意的成本很可觀
2. **沒有 context 會覺得意外**：未來的讀者會想「他們當初為什麼這樣做？」
3. **是真正取捨的結果**：確實有其他選項，而你是基於特定理由選了其中一個

三點缺任何一點，就跳過 ADR。格式照 [ADR-FORMAT.md](./ADR-FORMAT.md)。
