---
name: ui-to-vue
description: 當使用者有 UI 截圖或設計匯出檔，需要批次轉換成 Vue 3 元件時使用，尤其是搭配 Vant、Element Plus 或 Ant Design Vue 的時候。
metadata:
  origin: community
---

# UI To Vue

把 UI 設計截圖批次轉換成 Vue 3 Composition API 的元件程式碼。

## 何時使用

- 使用者提供一個放設計截圖或設計匯出圖片的目錄。
- 目標應用程式是 Vue 3。
- 使用者想要頁面元件、共用元件和 router 串接的第一版。
- 使用者指定 Vant、Element Plus 或 Ant Design Vue 當元件庫。

## 何時不要使用

- 使用者只有一張截圖，想要客製化的元件。
- 目標專案不是 Vue。
- 設計需要詳細的互動邏輯、資料流或無障礙審查。
- 截圖含有不能送到外部模型 API 的私人客戶資料。

## 輸入

使用依模組和頁面狀態分組截圖的輸入目錄：

```text
screenshots/
|-- HomePage/
|   |-- List/
|   |   |-- HomePage-List-Default@3x.png
|   |   `-- cut-images/
|   |-- cut-images/
|   `-- HomePage-Default@3x.png
`-- cut-images/
```

支援的切圖目錄名稱包括 `assets`、`icons`、`sprites`、`cut`、`images` 和 `cut-images`。

## 轉換模型

- 頁面分組：當相關截圖代表列表、詳情、表單、載入中或空白狀態時，把它們合併成一個頁面元件。
- UI 元件庫對應：在可行的地方，把原生的視覺元素對應到 Vant、Element Plus 或 Ant Design Vue 的元件。
- 切圖優先順序：優先用頁面層級的素材，其次是模組層級的素材，最後是全域共用的素材。
- 元件抽取：重複的 UI 區域出現超過一次時，就抽成共用元件。

## CLI 用法

用 `npx` 執行轉換器，這樣文件記載的指令不用依賴全域安裝的執行檔就能跑：

```bash
export DASHSCOPE_API_KEY=your_key
npx ui-to-vue-converter@1.0.2 --input ./screenshots --ui vant --output ./src
```

桌面版的 UI 元件庫：

```bash
npx ui-to-vue-converter@1.0.2 --input ./designs --ui element-plus --output ./src
npx ui-to-vue-converter@1.0.2 --input ./designs --ui antd-vue --output ./src
```

如果套件是全域安裝的，可以直接用 `ui-to-vue` 執行檔：

```bash
npm install -g ui-to-vue-converter@1.0.2
ui-to-vue --input ./screenshots --ui vant --output ./src
```

## 選項

| 選項 | 說明 | 預設值 |
| --- | --- | --- |
| `--input` | 設計圖片目錄 | `./screenshots` |
| `--ui` | UI 元件庫：`vant`、`element-plus` 或 `antd-vue` | `vant` |
| `--output` | 輸出目錄 | `./src` |
| `--config` | 設定檔路徑 | `./.ui-to-vue.config.json` |

## API Key 處理

轉換器可以從設定檔或環境變數讀取 DashScope 憑證。在 repo 裡優先用環境變數：

```bash
export DASHSCOPE_API_KEY=your_key
```

如果一定要用本機設定檔，要讓它不進版本控制：

```json
{
  "apiKey": "your_dashscope_key",
  "input": "./designs",
  "ui": "vant",
  "output": "./src"
}
```

```gitignore
.ui-to-vue.config.json
```

## 安全與隱私

- 把設計截圖當成可能被送到外部模型 API 的原始素材。
- 沒有許可，不要對客戶私人的設計跑這個流程。
- 在可重複的工作流裡要釘住轉換器的版本，不要用 `@latest`。
- commit 之前，先 review 產生出來的 Vue 程式碼。
- 不要 commit `.ui-to-vue.config.json`、API key、產生出來的祕密，或客戶的截圖。

## 輸出 Review 檢查清單

- [ ] 頁面元件已產生在 `views/` 或選定的輸出目錄底下。
- [ ] 重複的 UI 區域只有在明確會重用時，才抽進 `components/`。
- [ ] router 輸出跟目標專案的 router 風格相容。
- [ ] 產生出來的元件一致地使用要求的 UI 元件庫。
- [ ] 產生出來的 CSS 單位符合設計基準。
- [ ] 程式碼通過專案的 formatter、linter、型別檢查和 build。
- [ ] commit 之前，已 review 佔位文案、mock 資料和產生出來的素材。

## 疑難排解

| 問題 | 檢查 |
| --- | --- |
| `401` 或認證錯誤 | 確認執行指令的 shell 裡有設定 `DASHSCOPE_API_KEY`。 |
| `command not found: ui-to-vue` | 改用 `npx ui-to-vue-converter@1.0.2` 的形式，或全域安裝套件。 |
| 切圖被忽略 | 確認素材目錄名稱有被支援，而且巢狀放在對應的頁面或模組底下。 |
| 元件沒有用要求的 UI 元件庫 | 用明確的 `--ui` 值重新執行，並檢查產生出來的 import。 |
| 產生出來的版面尺寸看起來不對 | 確認截圖匯出的寬度符合目標元件庫的基準。 |

## 參考資料

- npm 套件：`ui-to-vue-converter`
