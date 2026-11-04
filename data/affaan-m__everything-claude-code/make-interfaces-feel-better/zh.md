---
name: make-interfaces-feel-better
description: 套用具體的設計工程細節，讓介面感覺更精緻。在 review 或改善 UI 的間距、字體排印、邊框、陰影、動態、點擊區域、圖示、文字換行與互動狀態時使用。
metadata:
  origin: community
---

# 讓介面感覺更好

用這個 skill 處理那些細小的設計工程細節，它們累積起來會讓
介面更精緻。

來源：從 `linus707` 已過期的社群 PR #1659 搶救而來。

## 何時使用

- 使用者說 UI 感覺怪怪的、平淡、很通用、擁擠、跳動或沒做完。
- 你正在建構控制項、卡片、清單、dashboard、導覽、表單或
  工具列。
- 元件需要 hover、active、focus、進場、退場、載入或空狀態。
- 前端 review 需要具體的前後對照建議。

## 核心原則

### 同心圓角（Concentric Radius）

對於相鄰的巢狀圓角表面：

```text
outer radius = inner radius + padding
```

如果 padding 很大，就把各層當成獨立的表面，不要硬套算式。
重點是視覺上的一致，不是迷信公式。

### 光學對齊（Optical Alignment）

幾何置中不一定是視覺置中。圖示按鈕、播放三角形、箭頭、星星與不對稱的圖示
常常需要一點位移。能修 SVG 就修 SVG，否則用像素等級的 margin 或 padding
調整。

### 陰影與邊框

用邊框做分隔與 focus ring。當卡片、
按鈕、下拉選單或 popover 需要深度時，用多層陰影。陰影應該是透明的，而且
夠細緻，能在各種背景上都適用。

### 文字換行

- 標題與短標題用 `text-wrap: balance`。
- 短到中等長度的內文、說明文字、描述
  與清單項目用 `text-wrap: pretty`。
- 長篇文章、程式碼與預先排版的內容兩者都不要用。
- 計數器、計時器、價格、表格
  與其他會更新的數字，用 `font-variant-numeric: tabular-nums`。

### 字體平滑

在 macOS 上，如果專案還沒做，
就在根版面套用 antialiased 字體平滑：

```css
html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### 圖片外框

圖片常常需要一圈細微的內縮外框，讓邊緣不會跟
背景糊在一起。

```css
img {
  outline: 1px solid rgba(0, 0, 0, 0.1);
  outline-offset: -1px;
}

@media (prefers-color-scheme: dark) {
  img {
    outline-color: rgba(255, 255, 255, 0.1);
  }
}
```

使用中性的黑或白 alpha 外框。不要用品牌色調
去染圖片外框。

### 動態

互動狀態的變化用 CSS transition，因為使用者在動作中途改變意圖時，
它可以重新指向新的目標。keyframe 保留給分階段的
一次性進場或載入序列。

好的動態預設值：

- 進場：結合 opacity、小幅 `translateY`，可選擇性加上 blur。
- 退場：比進場更短、更安靜，通常 150ms。
- 按下：有觸感的按鈕用 `scale(0.96)`，而且要有辦法在
  位移造成干擾時關掉。
- 圖示切換：用 opacity、scale 與 blur 做 cross-fade，
  不要瞬間切換顯示。

### Transition 範圍

絕對不要用 `transition: all`。明確指定會變動的屬性：

```css
.button {
  transition-property: transform, background-color, box-shadow;
  transition-duration: 150ms;
  transition-timing-function: ease-out;
}
```

`will-change` 只用在 compositor 友善屬性（例如 `transform`、`opacity` 與 `filter`）上第一幀的卡頓。
絕對不要用
`will-change: all`。

### 點擊區域

互動控制項至少要有 40x40px 的點擊區域，版面允許的話最好 44x44px。
當可見的圖示比較小時，用 pseudo-element 擴大，
但不要讓擴大後的點擊區域互相重疊。

## Review 輸出

review UI 打磨的過程時，用前後對照的列來回報具體變更：

| 原則 | 之前 | 之後 |
| --- | --- | --- |
| 同心圓角 | 父層與子層用同樣的圓角 | 父層圓角把 padding 算進去 |
| 等寬數字 | 數字變動時計數器會位移 | 計數器使用 `tabular-nums` |
| Transition 範圍 | `transition: all` | 明確指定 transition 屬性 |

當檔案路徑與屬性從程式碼片段看不出來時，要一併附上。
略過你檢查過但沒有改的原則。

## 檢查清單

- 巢狀圓角元素在視覺上一致。
- 圖示在視覺上置中。
- 按鈕、卡片與 popover 是基於正確的理由使用邊框或陰影。
- 標題與短文字避免尷尬的換行。
- 動態數字使用等寬數字。
- 需要的圖片有中性的外框。
- 進場與退場動畫分開處理、細緻，並在
  適當時可被中斷。
- 按鈕有觸感的 active 狀態，但動作不誇張。
- 沒有 `transition: all` 與 `will-change: all`。
- 小型控制項仍然有可用的點擊區域。
