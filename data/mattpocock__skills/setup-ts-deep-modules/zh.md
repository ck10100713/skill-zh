---
name: setup-ts-deep-modules
description: 把 dependency-cruiser 接進 TypeScript repo，讓每個 package 都是深模組：實作藏在子資料夾，只能透過入口檔案存取。由使用者主動呼叫。
disable-model-invocation: true
---

# 設定 TS 深模組

讓這個 repo 的每個 package 都成為**深模組**：小小的介面背後藏著大量行為。package 的公開表面是它的**入口檔案（entry points）**（package 根目錄的檔案），子資料夾裡的一切都是隱藏的。這個 skill 會安裝 [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) 和那些讓入口檔案成為唯一入口的規則，然後證明這些規則真的擋得住東西。

詞彙（deep module、interface、seam、depth）的部分，用 Skill 工具呼叫 "codebase-design"，全程使用它的語言。

## 這會強制執行的形狀

```
src/packages/
  <name>/
    index.ts        ← 入口檔案（公開）。從外面 import 這個。
    client.ts       ← 另一個入口檔案。package 可以暴露多個。
    lib/            ← 實作：對外隱藏，裡面可以互相自由 import。
    tests/          ← 放在一起的測試 + fixture（是子資料夾，所以是私有的）。
```

公開表面是 package 的**根目錄檔案**，不是某個指定的 `index.ts`。依慣例，實作放在 `lib/`，測試放在 `tests/`，讓每個 package 都是同樣的兩個資料夾形狀。不過規則本身是通用的：*任何*子資料夾裡的*任何東西*都是私有的，所以你永遠不需要為了新增資料夾而擴充設定。

四條規則，全部是 `error`：

1. **入口檔案邊界**：package 外面的程式碼（app 程式碼或其他 package）只能 import 那個 package 的入口檔案（它的根目錄檔案），絕對不能 import 子資料夾裡的任何東西。
2. **package 內部自由**：package 自己的檔案之間可以自由互相 import。
3. **測試透過入口檔案**：`<pkg>/tests/` 底下的檔案可以 import 任何 package 的入口檔案和它們自己的 `tests/` fixture，但絕對不能 import 任何 package 的子資料夾內部（連自己的也不行）。跨 package 的整合測試沒問題；深層 import 不行。
4. **不能有循環**：不能有依賴循環。

**是入口檔案，不是 barrel。** 因為公開表面是*每一個*根目錄檔案，package 可以暴露好幾個小的入口檔案（`index.ts`、`client.ts`、`server.ts`），而不是把所有東西都塞進一個巨大的 `index.ts`。不鼓勵用 barrel 檔案去 re-export 整棵子樹；入口檔案要保持小，把實作藏在子資料夾裡。

分層（哪些 package 可以依賴哪些）是*另一個*問題，在設定裡只留一個註解掉的樁，讓這個 repo 自己去填。

## 步驟

### 1. 偵測環境

- **套件管理器**：`pnpm-lock.yaml` → pnpm、`yarn.lock` → yarn、`bun.lockb` → bun，否則用 npm。下面所有指令都用它（`pnpm`/`yarn`/`npm run`/`bunx`）。
- **Packages 根目錄**：如果有 `src/` 就用 `src/packages`，否則用 `packages`。如果 repo 已經有另一個明顯的慣例，就跟使用者確認這個選擇。
- **既有設定**：檢查有沒有 `.dependency-cruiser.*` 檔。如果有，**不要**覆蓋它：把這四條規則和選項合併進去，並告訴使用者你加了什麼。

**完成的標準：** 套件管理器、packages 根目錄、既有設定的狀態都已經知道。

### 2. 安裝 dependency-cruiser

用偵測到的套件管理器，把 `dependency-cruiser` 安裝成 devDependency。

**完成的標準：** `dependency-cruiser` 在 `devDependencies` 裡。

### 3. 寫設定檔

把 [`dependency-cruiser.config.cjs`](./dependency-cruiser.config.cjs) 複製到 repo 根目錄，命名為 `.dependency-cruiser.cjs`。把 `PACKAGES_ROOT` 設成第 1 步偵測到的根目錄。這些規則是依路徑深度判斷、與副檔名無關，所以其他東西都不需要調整。

**完成的標準：** `.dependency-cruiser.cjs` 存在、`PACKAGES_ROOT` 正確，而且四條 forbidden 規則都在。

### 4. 接進檢查流程

- 加一個 `lint:boundaries` 腳本：`depcruise <packages-root>`（或 `depcruise src`）。
- 把它併進 repo 的總括檢查指令，也就是已經在跑 typecheck 的那個（例如 `check` / `ci` / `validate` 腳本）。**不要**動 `tsconfig` 或加 path alias。
- 如果沒有總括腳本，就加上 `lint:boundaries`，並告訴使用者把它加進 CI。

**完成的標準：** `lint:boundaries` 存在，而且跟 typecheck 在同一個指令裡執行。

### 5. 建立範例 package

建立一個要 commit 的 `<packages-root>/example/`，當作可以直接複製的範本：

- `index.ts` 是入口檔案。匯出一個委派給內部檔案的函式（讓這個 package 明顯是*深*的，不是 pass-through）。
- `lib/impl.ts`：在**子資料夾**裡的內部檔案，由 `index.ts` import，從外面碰不到。
- `tests/example.test.ts` **只** import `../index`（入口檔案），並對公開函式做 assert。

告訴使用者這是個起手式範本，可以複製或刪掉。

**完成的標準：** 範例 package 存在，透過根目錄的入口檔案暴露它的行為，並把 `impl` 藏在子資料夾裡。

### 6. 證明規則擋得住

這是整個 skill 的完成標準：遇到違規卻不會失敗的設定毫無價值。

1. 跑 `lint:boundaries`。在乾淨的範例上它一定要**通過**。
2. 暫時在 `tests/example.test.ts` 加一個深層 import（例如 `import { thing } from "../lib/impl"`）。再跑一次 `lint:boundaries`；它一定要**失敗**，並出現 `tests-through-entrypoints`。
3. 還原那個深層 import。再跑一次，它一定要**通過**。

**完成的標準：** 你親眼看到通過、然後在深層 import 上失敗、然後又通過。如果第 2 步沒有失敗，代表規則沒接對，結束前先修好。

### 7. 把慣例寫成文件

在 packages 資料夾裡寫一份 `README.md`（`<packages-root>/README.md`，放在它所管轄的 package 旁邊），涵蓋：`src/packages/<name>/` 的版面（入口檔案在根目錄、`lib/` 放實作、`tests/` 放測試）、「只能透過 package 的入口檔案（它的根目錄檔案）來 import」，以及怎麼跑 `lint:boundaries`。要明確**不鼓勵 barrel 檔案**：暴露好幾個小的入口檔案，而不是用一個 index 去 re-export 整棵子樹。內容限縮在可以直接複製的片段，加上四條規則各一段。

然後從 repo 的 agent 指示檔加一個指向它的 **context 指標**（有 `CLAUDE.md` 就用它，否則用 `AGENTS.md`，兩者都沒有就建立 `AGENTS.md`）。一行就夠，例如 `Packages are deep modules: see [src/packages/README.md](./src/packages/README.md) before adding or importing one.`。這樣 agent 才會主動發現邊界規則，而不是撞到才知道。

**完成的標準：** `<packages-root>/README.md` 存在且不鼓勵 barrel，而且 repo 的 `CLAUDE.md`/`AGENTS.md` 連到它。

## 備註

- 設定裡的 `$1` 反向參照（dependency-cruiser 的群組比對）正是讓 package 能碰到自己的內部、外人卻碰不到的關鍵。不要把它們攤平成每個 package 各自一條的規則。
- 公開或私有是由**深度**決定的：package 的根目錄檔案是入口檔案；子資料夾裡的任何東西都是私有的。慣例上的子資料夾是 `lib/`（實作）和 `tests/`，但規則並沒有把它們寫死：任何子資料夾都是私有的，所以新資料夾永遠不需要改設定。新增入口檔案就只是新增一個根目錄檔案（不用 barrel）。
- Package 是**扁平**的：根目錄底下只有一層直接的子項。package 的內部可以巢狀到你想要的深度；但 package 裡不能包含另一個 package。
- 用 `.cjs`（不是 `.js`），這樣設定檔的 `module.exports` 在 `"type": "module"` 的 repo 裡也能運作。
